from pydantic import BaseModel, Field
from decimal import Decimal
from typing import List, Optional

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price_at_addition: Decimal

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    user_id: int
    status: str
    items: List[CartItemResponse] = []

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    message: str