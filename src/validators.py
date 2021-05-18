import re

from pydantic import BaseModel, validator


class LinkValidator(BaseModel):
    link: str

    @validator('link')
    def validate_link(cls,
                      link: bytes) -> str:
        pattern = re.compile(r'https?://.*')
        link = link.decode('utf-8')

        if pattern.search(link) is None:
            raise ValueError("Wrong link format")
        return link
