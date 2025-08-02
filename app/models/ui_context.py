from pydantic import BaseModel
from typing import List, Optional

class Product(BaseModel):
    name: str
    price: Optional[float] = None

class UiContext(BaseModel):
    view: str
    cartItems: List[str]
    visibleProducts: List[Product]
