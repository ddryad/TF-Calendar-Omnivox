from pydantic import BaseModel


class CredentialsRequest(BaseModel):
    da: str
    password: str


class ClassItem(BaseModel):
    titre: str
    date: str
    heure: str
    local: str
    categorie: str