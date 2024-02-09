from unittest import TestCase

from django.core.exceptions import ValidationError
from passwords import validators


class TestLengthValidatorTests(TestCase):

    def test_length_validator_explicit_minimum(self):
        lv = validators.LengthValidator(min_length=8, max_length=None)

        # these should all fail validation
        badstrings = "", "1", "1234567", "$%ǟ^&*("
        for bad in badstrings:
            with self.assertRaises(ValidationError):
                lv(bad)

        # these should all pass validation
        goodstrings = "12345678", "^@$%()ǟ^&$@%ǟ_(^$%@ǟ'')"
        for good in goodstrings:
            lv(good)

    def test_length_validator_zero_minimum(self):
        lv = validators.LengthValidator(min_length=0, max_length=None)
        lv("")

    def test_length_validator_no_minimum(self):
        lv = validators.LengthValidator(min_length=None, max_length=None)
        lv("")

    def test_length_validator_explicit_maximum(self):
        lv = validators.LengthValidator(min_length=None, max_length=8)

        # these should all pass validation
        goodstrings = "", "1", "1234567", "$%ǟ^&*("
        for good in goodstrings:
            lv(good)

        # these should all fail validation
        badstrings = "123456789", "^@$%()ǟ^&$@%ǟ_(^$%@ǟ'')"
        for bad in badstrings:
            with self.assertRaises(ValidationError):
                lv(bad)

    def test_length_validator_zero_maximum(self):
        lv = validators.LengthValidator(min_length=None, max_length=0)
        # no problems here
        lv("")

        with self.assertRaises(ValidationError):
            lv("longer than zero chars")

    def test_length_validator_no_maximum(self):
        lv = validators.LengthValidator(min_length=None, max_length=None)
        lv("any length is fine")


class ValidatorTestCase(TestCase):

    def assert_valid(self, validator, string):
        # we test validationerror isn't raised by just running the validation.
        validator(string)

    def assert_invalid(self, validator, string, exc_re=None):
        if exc_re is None:
            with self.assertRaises(ValidationError):
                validator(string)
        else:
            with self.assertRaisesRegex(ValidationError, exc_re):
                validator(string)


class ComplexityValidatorTests(ValidatorTestCase):

    def mkvalidator(self, **complexities):
        return validators.ComplexityValidator(complexities=complexities)

    def test_minimum_uppercase_count(self):
        cv = self.mkvalidator(UPPER=0)
        self.assert_valid(cv, "no uppercase")
        self.assert_valid(cv, "Some UpperCase")
        self.assert_valid(cv, "ALL UPPERCASE")

        cv = self.mkvalidator(UPPER=1)
        self.assert_invalid(cv, "no uppercase", "uppercase")
        self.assert_valid(cv, "Some UpperCase")
        self.assert_valid(cv, "ALL UPPERCASE")

        cv = self.mkvalidator(UPPER=100)
        self.assert_invalid(cv, "no uppercase", "uppercase")
        self.assert_invalid(cv, "Some UpperCase", "uppercase")
        self.assert_invalid(cv, "ALL UPPERCASE", "uppercase")

    def test_minimum_lowercase_count(self):
        cv = self.mkvalidator(LOWER=0)
        self.assert_valid(cv, "NO LOWERCASE")
        self.assert_valid(cv, "sOME lOWERCASE")
        self.assert_valid(cv, "all lowercase")

        cv = self.mkvalidator(LOWER=1)
        self.assert_invalid(cv, "NO LOWERCASE", "lowercase")
        self.assert_valid(cv, "sOME lOWERCASE")
        self.assert_valid(cv, "all lowercase")

        cv = self.mkvalidator(LOWER=100)
        self.assert_invalid(cv, "NO LOWERCASE", "lowercase")
        self.assert_invalid(cv, "sOME lOWERCASE", "lowercase")
        self.assert_invalid(cv, "all lowercase", "lowercase")

    def test_minimum_letter_count(self):
        cv = self.mkvalidator(LETTERS=0)
        self.assert_valid(cv, "1234. ?")
        self.assert_valid(cv, "soME 123")
        self.assert_valid(cv, "allletters")

        cv = self.mkvalidator(LETTERS=1)
        self.assert_invalid(cv, "1234. ?", "letter")
        self.assert_valid(cv, "soME 123")
        self.assert_valid(cv, "allletters")

        cv = self.mkvalidator(LETTERS=100)
        self.assert_invalid(cv, "1234. ?", "letter")
        self.assert_invalid(cv, "soME 123", "letter")
        self.assert_invalid(cv, "allletters", "letter")

    def test_minimum_digit_count(self):
        cv = self.mkvalidator(DIGITS=0)
        self.assert_valid(cv, "")
        self.assert_valid(cv, "0")
        self.assert_valid(cv, "1")
        self.assert_valid(cv, "11")
        self.assert_valid(cv, "one 1")

        cv = self.mkvalidator(DIGITS=1)
        self.assert_invalid(cv, "", "digits")
        self.assert_valid(cv, "0")
        self.assert_valid(cv, "1")
        self.assert_valid(cv, "11")
        self.assert_valid(cv, "one 1")

    def test_minimum_punctuation_count(self):
        none = "no punctuation"
        one = "ffs!"
        mixed = r"w@oo%lo(om!ol~oo&"
        # this is a copy of string.punctuation
        allpunc = r'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

        cv = self.mkvalidator(SPECIAL=0)
        self.assert_valid(cv, none)
        self.assert_valid(cv, one)
        self.assert_valid(cv, mixed)
        self.assert_valid(cv, allpunc)

        cv = self.mkvalidator(SPECIAL=1)
        self.assert_invalid(cv, none, "special")
        self.assert_valid(cv, one)
        self.assert_valid(cv, mixed)
        self.assert_valid(cv, allpunc)

        cv = self.mkvalidator(SPECIAL=100)
        self.assert_invalid(cv, none, "special")
        self.assert_invalid(cv, one, "special")
        self.assert_invalid(cv, mixed, "special")
        self.assert_invalid(cv, allpunc, "special")

    def test_minimum_nonascii_count(self):
        none = "regularchars and numbers 100"
        one = "\x00"  # null
        many = "\x00\x01\x02\x03\x04\x05\t\n\r"

        cv = self.mkvalidator(SPECIAL=0)
        self.assert_valid(cv, none)
        self.assert_valid(cv, one)
        self.assert_valid(cv, many)

        cv = self.mkvalidator(SPECIAL=1)
        self.assert_invalid(cv, none)
        self.assert_valid(cv, one)
        self.assert_valid(cv, many)

        cv = self.mkvalidator(SPECIAL=100)
        self.assert_invalid(cv, none)
        self.assert_invalid(cv, one)
        self.assert_invalid(cv, many)

    def test_minimum_words_count(self):
        none = ""
        one = "oneword"
        some = "one or two words"
        many = "a b c d e f g h i 1 2 3 4 5 6 7 8 9 { $ # ! )}"

        cv = self.mkvalidator(WORDS=0)
        self.assert_valid(cv, none)
        self.assert_valid(cv, one)
        self.assert_valid(cv, some)
        self.assert_valid(cv, many)

        cv = self.mkvalidator(WORDS=1)
        self.assert_invalid(cv, none, "unique words")
        self.assert_valid(cv, one)
        self.assert_valid(cv, some)
        self.assert_valid(cv, many)

        cv = self.mkvalidator(WORDS=10)
        self.assert_invalid(cv, none, "unique words")
        self.assert_invalid(cv, one, "unique words")
        self.assert_invalid(cv, some, "unique words")
        self.assert_valid(cv, many)

        cv = self.mkvalidator(WORDS=100)
        self.assert_invalid(cv, none, "unique words")
        self.assert_invalid(cv, one, "unique words")
        self.assert_invalid(cv, some, "unique words")
        self.assert_invalid(cv, many, "unique words")


class DictionaryValidator(ValidatorTestCase):

    different = "ljasdfkjhsdfkjhsiudfyisd"
    vsimilar = "uncommon"
    same = "words"

    def mkvalidator(self, words=None, dictionary_words=None, threshold=None):
        instance = validators.DictionaryValidator(words=words, threshold=threshold)
        if dictionary_words:
            instance.get_dictionary_words = lambda self, d: dictionary_words
        return instance

    def test_provide_words_but_no_dictionary(self):
        dv = self.mkvalidator(words=["common", "words"])
        self.assert_valid(dv, self.different)

    def test_provide_dictionary_but_no_words(self):
        dv = self.mkvalidator(dictionary_words="common\nwords")
        self.assert_valid(dv, self.different)

    def test_thresholds(self):
        dv = self.mkvalidator(words=["common", "words"], threshold=0.0)
        self.assert_invalid(dv, self.different, "dictionary word")
        self.assert_invalid(dv, self.vsimilar, "dictionary word")
        self.assert_invalid(dv, self.same, "dictionary word")

        dv = self.mkvalidator(words=["common", "words"], threshold=0.5)
        self.assert_valid(dv, self.different)
        self.assert_invalid(dv, self.vsimilar, "dictionary word")
        self.assert_invalid(dv, self.same, "dictionary word")

        dv = self.mkvalidator(words=["common", "words"], threshold=1.0)
        self.assert_valid(dv, self.different)
        self.assert_valid(dv, self.vsimilar)
        self.assert_invalid(dv, self.same, "dictionary word")
