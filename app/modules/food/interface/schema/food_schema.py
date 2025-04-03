from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, Field

class Food_Data(BaseModel):
    label: Optional[int] = 0
    name: Optional[str] = "음식명"
    size: Optional[float] = 0.0
    calorie: Optional[float] = 0.0
    carb: Optional[float] = 0.0
    sugar: Optional[float] = 0.0
    fat: Optional[float] = 0.0
    protein: Optional[float] = 0.0
    calcium: Optional[float] = 0.0
    phosphorus: Optional[float] = 0.0
    sodium: Optional[float] = 0.0
    magnesium: Optional[float] = 0.0
    iron: Optional[float] = 0.0
    zinc: Optional[float] = 0.0
    cholesterol: Optional[float] = 0.0
    trans_fat: Optional[float] = 0.0
