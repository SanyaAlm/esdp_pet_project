from pydantic import BaseModel, Field


class SendSmsDto(BaseModel):
    from_: str = Field(alias='from')
    to: str
    text: str
