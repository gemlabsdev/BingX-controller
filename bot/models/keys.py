import uuid
from pydantic import BaseModel, Field


class Key(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    exchange: str = Field(...)
    public: str = Field(...)
    private: str = Field(...)

    def __repr__(self):
        return f'<Keys "{self.exchange.upper()}">'
