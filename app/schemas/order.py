from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrderPublic(BaseModel):
    id: int
    user_id: int
    order_no: str
    product_id: str
    status: int
    amount: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
