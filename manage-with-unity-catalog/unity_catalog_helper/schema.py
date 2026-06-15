from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class Permissions(BaseModel):
    readers: List[str] = []
    writers: List[str] = []

class Catalog(BaseModel):
    name: str
    path: Optional[str] = None
    permissions: Optional[Permissions] = Permissions()

class Table(BaseModel):
    name: str
    path: str
    catalog: str
    permissions: Optional[Permissions] = Permissions()

class ConfigSchema(BaseModel):
    catalogs: List[Catalog] = Field(alias="schemas", default=[])
    tables: List[Table] = Field(alias="tables", default=[])
