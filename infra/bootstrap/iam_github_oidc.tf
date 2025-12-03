resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]

  tags = {
    Project = var.project
    Stack   = "bootstrap"
  }
}

data "aws_iam_policy_document" "assume_role_infra" {
  statement {
    effect = "Allow"

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    actions = ["sts:AssumeRoleWithWebIdentity"]

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        "repo:${var.repo.owner}/${var.repo.name}:*"
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "oc_infra_deployer" {
  name               = var.repo.role_name
  assume_role_policy = data.aws_iam_policy_document.assume_role_infra.json

  tags = {
    Project = var.project
    Stack   = "bootstrap"
    Repo    = "${var.repo.owner}/${var.repo.name}"
    Purpose = "Terraform-OIDC-Infra"
  }
}
