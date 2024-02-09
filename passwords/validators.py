import re

from pathlib import Path

from django.core.exceptions import ValidationError
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _

from passwords.settings import pwd_settings


DICT_CACHE = []
DICT_FILESIZE = -1
DICT_MAX_CACHE = 1000000


class LengthValidator:
    message = _("Invalid Length (%s)")
    code = "length"

    def __init__(self, min_length=None, max_length=None):
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, value):
        err = None
        if self.min_length is not None and len(value) < self.min_length:
            err = _("Must be %s characters or more") % self.min_length
        elif self.max_length is not None and len(value) > self.max_length:
            err = _("Must be %s characters or less") % self.max_length

        if err is not None:
            raise ValidationError(self.message % err, code=self.code)


class ComplexityValidator:
    message = _("Must be more complex (%s)")
    code = "complexity"

    def __init__(self, complexities):
        self.complexities = complexities

    def __call__(self, value):
        if self.complexities is None:
            return

        uppercase, lowercase, letters = set(), set(), set()
        digits, special = set(), set()

        for character in value:
            if character.isupper():
                uppercase.add(character)
                letters.add(character)
            elif character.islower():
                lowercase.add(character)
                letters.add(character)
            elif character.isdigit():
                digits.add(character)
            elif not character.isspace():
                special.add(character)

        words = set(re.findall(r"\b\w+", value, re.UNICODE))

        errors = []
        if len(uppercase) < self.complexities.get("UPPER", 0):
            errors.append(
                _("%(UPPER)s or more unique uppercase characters") % self.complexities
            )
        if len(lowercase) < self.complexities.get("LOWER", 0):
            errors.append(
                _("%(LOWER)s or more unique lowercase characters") % self.complexities
            )
        if len(letters) < self.complexities.get("LETTERS", 0):
            errors.append(_("%(LETTERS)s or more unique letters") % self.complexities)
        if len(digits) < self.complexities.get("DIGITS", 0):
            errors.append(_("%(DIGITS)s or more unique digits") % self.complexities)
        if len(special) < self.complexities.get("SPECIAL", 0):
            errors.append(
                _("%(SPECIAL)s or more non unique special characters")
                % self.complexities
            )
        if len(words) < self.complexities.get("WORDS", 0):
            errors.append(_("%(WORDS)s or more unique words") % self.complexities)

        if errors:
            raise ValidationError(
                self.message % (_("must contain ") + ", ".join(errors),), code=self.code
            )


class BaseSimilarityValidator:
    message = _("Too Similar to [%(haystacks)s]")
    code = "similarity"

    def __init__(self, haystacks=None, threshold=None):
        self.haystacks = haystacks if haystacks else []
        if threshold is None:
            self.threshold = pwd_settings.PASSWORD_MATCH_THRESHOLD
        else:
            self.threshold = threshold

    def fuzzy_substring(self, needle, haystack):
        needle, haystack = needle.lower(), haystack.lower()
        m, n = len(needle), len(haystack)

        if m == 1 and needle not in haystack:
            return -1
        if n == 0:
            return m

        row1 = [0] * (n + 1)
        for i in range(m):
            row2 = [i + 1]
            for j in range(n):
                cost = 1 if needle[i] != haystack[j] else 0
                row2.append(min(row1[j + 1] + 1, row2[j] + 1, row1[j] + cost))
            row1 = row2
        return min(row1)

    def __call__(self, value):
        for haystack in self.haystacks:
            distance = self.fuzzy_substring(value, haystack)
            longest = max(len(value), len(haystack))
            similarity = (longest - distance) / longest
            if similarity >= self.threshold:
                raise ValidationError(
                    self.message % {"haystacks": ", ".join(self.haystacks)},
                    code=self.code,
                )


class DictionaryValidator(BaseSimilarityValidator):
    message = _("Based on a dictionary word")
    code = "dictionary_word"

    def __init__(self, words=None, dictionary=None, threshold=None):
        haystacks = []
        if dictionary:
            words = self.get_dictionary_words(dictionary)
        if words:
            haystacks.extend(words)
        super().__init__(haystacks=haystacks, threshold=threshold)

    def get_dictionary_words(self, dictionary):
        if DICT_CACHE:
            return DICT_CACHE
        if DICT_FILESIZE == -1:  # noqa: F823
            with Path.open(dictionary) as f:
                f.seek(0, 2)
                DICT_FILESIZE = f.tell()  # noqa: N806

            if DICT_FILESIZE < 1000000:
                with Path.open(dictionary) as dictionary:
                    return [smart_str(x.strip()) for x in dictionary.readlines()]
        with Path.open(dictionary) as dictionary:
            return [smart_str(x.strip()) for x in dictionary.readlines()]


class CommonSequenceValidator(BaseSimilarityValidator):
    message = _("Based on a common sequence of characters")
    code = "common_sequence"


validate_length = LengthValidator(
    pwd_settings.PASSWORD_MIN_LENGTH, pwd_settings.PASSWORD_MAX_LENGTH
)
complexity = ComplexityValidator(pwd_settings.PASSWORD_COMPLEXITY)
dictionary_words = DictionaryValidator(dictionary=pwd_settings.PASSWORD_DICTIONARY)
common_sequences = CommonSequenceValidator(pwd_settings.PASSWORD_COMMON_SEQUENCES)
