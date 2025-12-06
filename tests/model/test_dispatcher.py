# tests/model/test_dispatcher.py

import importlib
import sys
from typing import Any

import pytest

import src.model.dispatcher as dispatcher


def reload_dispatcher() -> Any:
    """
    Helper para recarregar o módulo entre testes, caso necessário.

    (Hoje não há lógica em import-time dependente de env, mas deixo
    o helper pronto caso o dispatcher evolua.)
    """
    return importlib.reload(dispatcher)


def test_resolve_step_name_uses_cli_argument_first(monkeypatch):
    """
    Deve priorizar o primeiro argumento de linha de comando, mesmo que
    STEP_NAME esteja setado na env.

    Contrato atual do código:
    - step_name = sys.argv[1]
    Então simulamos algo como:
      ["dispatcher", "train"]
    """
    # STEP_NAME no ambiente (que deve ser ignorado)
    monkeypatch.setenv("STEP_NAME", "evaluate")

    # CLI: dispatcher train
    monkeypatch.setattr(sys, "argv", ["dispatcher", "train"], raising=False)

    reload_dispatcher()
    step_name = dispatcher.resolve_step_name()

    assert step_name == "train"


def test_resolve_step_name_uses_env_when_no_cli(monkeypatch):
    """
    Quando não há argumento de CLI, deve usar STEP_NAME do ambiente.

    Aqui simulamos:
      sys.argv = ["dispatcher"]
      STEP_NAME = "ingest"
    """
    monkeypatch.delenv("STEP_NAME", raising=False)
    monkeypatch.setenv("STEP_NAME", "ingest")

    # Sem arg extra
    monkeypatch.setattr(sys, "argv", ["dispatcher"], raising=False)

    reload_dispatcher()
    step_name = dispatcher.resolve_step_name()

    assert step_name == "ingest"


def test_resolve_step_name_exits_when_missing(monkeypatch, capsys):
    """
    Quando não há CLI arg nem STEP_NAME na env, deve imprimir mensagem
    de ajuda e encerrar com código 1.
    """
    monkeypatch.delenv("STEP_NAME", raising=False)
    monkeypatch.setattr(sys, "argv", ["dispatcher"], raising=False)

    reload_dispatcher()

    with pytest.raises(SystemExit) as excinfo:
        dispatcher.resolve_step_name()

    assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert "ERROR: STEP_NAME not provided" in captured.out
    assert "Use CLI arg or set STEP_NAME env var" in captured.out
    assert "STEP_NAME=ingest python -m src.model.pipeline.dispatcher" in captured.out


@pytest.mark.parametrize(
    "step_name,expected_module",
    [
        ("ingest", "src.model.data.ingest"),
        ("split_batches", "src.model.data.split_batches"),
        ("preprocess_batch", "src.model.pipeline.preprocess_batch"),
        ("train", "src.model.pipeline.train"),
        ("evaluate", "src.model.pipeline.evaluate"),
    ],
)
def test_get_module_for_step_returns_expected_module(step_name, expected_module):
    """
    Para cada STEP_NAME conhecido, deve retornar o módulo Python correto.
    """
    reload_dispatcher()
    module = dispatcher.get_module_for_step(step_name)
    assert module == expected_module


def test_get_module_for_step_exits_on_unknown_step(capsys):
    """
    Para STEP_NAME desconhecido, deve imprimir erro com os valores válidos
    e encerrar com código 1.
    """
    reload_dispatcher()

    with pytest.raises(SystemExit) as excinfo:
        dispatcher.get_module_for_step("unknown_step")

    assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert "Unknown STEP_NAME='unknown_step'" in captured.out
    # Garante que lista de válidos foi exibida
    for valid in sorted(dispatcher.STEP_TO_MODULE.keys()):
        assert valid in captured.out


def test_run_module_calls_subprocess_without_extra_args(monkeypatch, capsys):
    """
    Deve chamar subprocess.run com 'python -m <module>' quando não há
    argumentos extras após o STEP_NAME.
    """
    calls: list[dict[str, Any]] = []

    def fake_run(cmd, check):
        calls.append({"cmd": cmd, "check": check})

    # sys.argv com apenas script + STEP_NAME (sem args adicionais)
    monkeypatch.setattr(sys, "argv", ["dispatcher", "ingest"], raising=False)
    monkeypatch.setattr(dispatcher.subprocess, "run", fake_run)

    reload_dispatcher()
    dispatcher.run_module("src.model.data.ingest")

    # Verifica prints
    captured = capsys.readouterr()
    assert "[dispatcher] Running module: src.model.data.ingest" in captured.out
    assert "[dispatcher] Command: python -m src.model.data.ingest" in captured.out

    # Verifica chamada ao subprocess.run
    assert len(calls) == 1
    assert calls[0]["cmd"] == ["python", "-m", "src.model.data.ingest"]
    assert calls[0]["check"] is True


def test_run_module_forwards_extra_args(monkeypatch, capsys):
    """
    Deve repassar corretamente os argumentos extras após o STEP_NAME
    para o comando python -m <module>.
    """
    calls: list[dict[str, Any]] = []

    def fake_run(cmd, check):
        calls.append({"cmd": cmd, "check": check})

    # CLI simulada:
    # dispatcher ingest --batches 0 --foo bar
    monkeypatch.setattr(
        sys,
        "argv",
        ["dispatcher", "ingest", "--batches", "0", "--foo", "bar"],
        raising=False,
    )
    monkeypatch.setattr(dispatcher.subprocess, "run", fake_run)

    reload_dispatcher()
    dispatcher.run_module("src.model.pipeline.preprocess_batch")

    captured = capsys.readouterr()
    assert (
        "[dispatcher] Running module: src.model.pipeline.preprocess_batch"
        in captured.out
    )
    assert (
        "[dispatcher] Command: python -m src.model.pipeline.preprocess_batch "
        "--batches 0 --foo bar" in captured.out
    )

    assert len(calls) == 1
    assert calls[0]["cmd"] == [
        "python",
        "-m",
        "src.model.pipeline.preprocess_batch",
        "--batches",
        "0",
        "--foo",
        "bar",
    ]
    assert calls[0]["check"] is True


def test_main_happy_path_uses_cli_and_dispatches_to_correct_module(monkeypatch):
    """
    Cenário de integração feliz:
    - STEP_NAME passado por CLI
    - dispatcher resolve o step, mapeia para módulo e chama subprocess.run
      com o comando correto.
    """
    calls: list[list[str]] = []

    def fake_run(cmd, check):
        calls.append(cmd)

    # CLI: dispatcher ingest --foo bar
    monkeypatch.setattr(
        sys,
        "argv",
        ["dispatcher", "ingest", "--foo", "bar"],
        raising=False,
    )
    # Garante que env não vai interferir
    monkeypatch.delenv("STEP_NAME", raising=False)
    monkeypatch.setattr(dispatcher.subprocess, "run", fake_run)

    reload_dispatcher()
    dispatcher.main()

    # Deve ter mapeado "ingest" -> "src.model.data.ingest"
    assert len(calls) == 1
    assert calls[0] == ["python", "-m", "src.model.data.ingest", "--foo", "bar"]


def test_main_uses_env_when_cli_missing(monkeypatch):
    """
    Cenário de integração onde não há CLI arg, e o STEP_NAME vem da env.
    """
    calls: list[list[str]] = []

    def fake_run(cmd, check):
        calls.append(cmd)

    # Sem STEP_NAME em argv
    monkeypatch.setattr(
        sys,
        "argv",
        ["dispatcher"],  # só o script
        raising=False,
    )
    monkeypatch.setenv("STEP_NAME", "evaluate")
    monkeypatch.setattr(dispatcher.subprocess, "run", fake_run)

    reload_dispatcher()
    dispatcher.main()

    # STEP_NAME = "evaluate" -> "src.model.pipeline.evaluate"
    assert len(calls) == 1
    assert calls[0] == ["python", "-m", "src.model.pipeline.evaluate"]
