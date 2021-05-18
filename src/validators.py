import re

from pydantic import BaseModel, validator


class LinkValidator(BaseModel):
    link: str

    @validator('link')
    def validate_link(cls,
                      link: str) -> str:
        pattern = re.compile(r'https?://.*')

        if pattern.search(link) is None:
            raise ValueError("Wrong link format")
        return link
