from pydantic import BaseModel


class CredentialsRequest(BaseModel):
    da: str
    password: str


class ClassItem(BaseModel):
    nom: str
    description: str
    dateDepart: str 
    dureeHeures: float
