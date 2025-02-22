from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from passwords.validators import ComplexityValidator as ComVal


class ComplexityValidator:
    """Wrapper for validators."""

    def __init__(self):
        self.validator = ComVal(settings.PASSWORD_COMPLEXITY)

    def get_help_text(self):
        return _("Your password fails to meet our complexity requirements.")

    def validate(self, value, user=None):
        return self.validator(value)
