from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    price: int
    duration_seconds: int
    description: Optional[str] = ""
    status: Optional[int] = 1


class ProductCreate(ProductBase):
    sku_id: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    duration_seconds: Optional[int] = None
    description: Optional[str] = None
    status: Optional[int] = None


class ProductPublic(ProductBase):
    id: int
    sku_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
