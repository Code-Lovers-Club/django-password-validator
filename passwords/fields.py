import typing

from django.forms import CharField
from django.forms import PasswordInput
from django.utils.translation import gettext_lazy as _

from passwords.settings import pwd_settings
from passwords.validators import common_sequences
from passwords.validators import complexity
from passwords.validators import dictionary_words
from passwords.validators import validate_length


class PasswordField(CharField):

    default_validators: typing.ClassVar[list] = [
        validate_length,
        common_sequences,
        dictionary_words,
        complexity,
    ]

    def __init__(self, *args, **kwargs):
        if "widget" not in kwargs:
            attrs = {}

            # 'minlength' is poorly supported, so use 'pattern' instead.
            # See http://stackoverflow.com/a/10294291/25507,
            # http://caniuse.com/#feat=input-minlength.
            if pwd_settings.PASSWORD_MIN_LENGTH and pwd_settings.PASSWORD_MAX_LENGTH:
                attrs["pattern"] = ".{%i,%i}" % (
                    pwd_settings.PASSWORD_MIN_LENGTH,
                    pwd_settings.PASSWORD_MAX_LENGTH,
                )
                attrs["title"] = _("%i to %i characters") % (
                    pwd_settings.PASSWORD_MIN_LENGTH,
                    pwd_settings.PASSWORD_MAX_LENGTH,
                )
            elif pwd_settings.PASSWORD_MIN_LENGTH:
                attrs["pattern"] = ".{%i,}" % pwd_settings.PASSWORD_MIN_LENGTH
                attrs["title"] = (
                    _("%i characters minimum") % pwd_settings.PASSWORD_MIN_LENGTH
                )

            if pwd_settings.PASSWORD_MAX_LENGTH:
                attrs["maxlength"] = pwd_settings.PASSWORD_MAX_LENGTH

            kwargs["widget"] = PasswordInput(render_value=False, attrs=attrs)

        super().__init__(*args, **kwargs)
