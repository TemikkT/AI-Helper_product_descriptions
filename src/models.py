from typing import Dict, List, Optional
from pydantic import BaseModel, Field

"""
Класс для продукта который мы будем подавать в LLM
"""
class ProductInput(BaseModel):
    name: str = Field(..., description="Название товара")
    manufacturer: str = Field(..., description="Производитель")
    specs: Dict[str, str] = Field(default_factory=dict, description="Краткие характеристики")
    description: Optional[str] = Field(default="", description="Текстовое описание или техпаспорт")


"""
Класс для продукта который мы будем просить возвращать LLM
"""
class ProductCardOutput(BaseModel):
    seo_title: str = Field(..., description="SEO-заголовок до 70 символов")
    seo_description: str = Field(..., description="SEO-описание объемом 800-1200 символов")
    key_specs: List[str] = Field(..., description="Структурированный список ключевых характеристик")
    search_queries: List[str] = Field(..., description="3-5 поисковых запросов для SEO")
    commercial_block: str = Field(..., description="Commercial-блок: кому подходит прибор и какие задачи решает")