from pydantic import AfterValidator
from schema.enums import Roles,Levels,AssignmentRole
from typing import Annotated
import re

def check_email(value:str):
    EMAIL_REGEX = re.compile(
    r"^[a-zA-Z][a-zA-Z0-9_.+-]*@gmail\.com$"
    )
    ALLOWED_DOMAIN="gmail.com"
    ans=value
    value = value.strip().lower()

    if not EMAIL_REGEX.match(value):
        raise ValueError(
            f"Email must be a valid {ALLOWED_DOMAIN} address"
        )

    domain = value.split("@")[-1]
    if domain != ALLOWED_DOMAIN:
        raise ValueError(f"Only {ALLOWED_DOMAIN} email addresses are allowed")
    return ans


def check_password(value: str) -> str:
    MIN_LENGTH = 8

    if not (MIN_LENGTH <= len(value)):
        raise ValueError(
            f"Password must be longer than 8 Charecters"
        )

    if not re.search(r"[a-z]", value):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r"\d", value):
        raise ValueError("Password must contain at least one number")

    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", value):
        raise ValueError("Password must contain at least one special character")

    if re.search(r"\s", value):
        raise ValueError("Password must not contain whitespace")

    return value

def check_non_empty_value(value: str) -> str:
    if not value.strip():
        raise ValueError("Cannot accept empty string")
    return value

email_value=Annotated[str,AfterValidator(check_email)]
password_value=Annotated[str,AfterValidator(check_password)]
non_empty_value=Annotated[str,AfterValidator(check_non_empty_value)]
