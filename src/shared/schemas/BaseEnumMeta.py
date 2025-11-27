from enum import EnumMeta


class BaseEnumMeta(EnumMeta):
    def __call__(cls, value, *args, **kwargs):
        try:
            return super().__call__(value, *args, **kwargs)
        except ValueError:
            return cls.UNKNOWN
