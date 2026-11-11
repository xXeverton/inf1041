from pydantic import BaseModel


class ErrorSchema(BaseModel):
    message: str


def apresenta_erro(mensagem: str) -> ErrorSchema:
    return ErrorSchema(message=mensagem)
