import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class HacklabUsernameValidator(validators.RegexValidator):
    regex = r"^[A-Za-z][A-Za-z0-9_.-]{1,31}\Z"
    message = _(
        "Enter a valid username of 2 to 32 characters. This value may contain only unaccented lowercase a-z "
        "and uppercase A-Z letters, numbers, and ./-/_ characters. It must begin with a letter."
    )
    flags = re.ASCII


custom_username_validators = [HacklabUsernameValidator()]
