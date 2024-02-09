from django.conf import settings
from django.core.signals import setting_changed


COMMON_SEQUENCES: list = [
    "0123456789",
    "`1234567890-=",
    "~!@#$%^&*()_+",
    "abcdefghijklmnopqrstuvwxyz",
    "qwertyuiop[]\\asdfghjkl;'zxcvbnm,./",
    'qwertyuiop{}|asdfghjkl;"zxcvbnm<>?',
    "qwertyuiopasdfghjklzxcvbnm",
    "1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik,9ol.0p;/-['=]\\",
    "qazwsxedcrfvtgbyhnujmikolp",
    "qwertzuiopü+asdfghjklöä#<yxcvbnm,.-",
    "qwertzuiopü*asdfghjklöä'>yxcvbnm;:_",
    "qaywsxedcrfvtgbzhnujmikolp",
]

DEFAULTS: dict = {
    "PASSWORD_MIN_LENGTH": 6,
    "PASSWORD_MAX_LENGTH": None,
    "PASSWORD_DICTIONARY": None,
    "PASSWORD_MATCH_THRESHOLD": 0.9,
    "PASSWORD_COMMON_SEQUENCES": COMMON_SEQUENCES,
    "PASSWORD_COMPLEXITY": None,
}


class PasswordSettings:

    def __init__(self, user_settings=None, defaults=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "PWD_VALIDATOR", {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid Password setting: '%s'" % attr)
        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        setattr(self, attr, val)
        return val

    def reload(self):
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


pwd_settings = PasswordSettings(None, DEFAULTS)


def reload_pwd_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "PWD_VALIDATOR":
        pwd_settings.reload()


setting_changed.connect(reload_pwd_settings)
