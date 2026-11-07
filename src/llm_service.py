import os
import json
import httpx
from openai import OpenAI
from dotenv import load_dotenv
from src.models import ProductInput, ProductCardOutput

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")


def get_llm_client() -> OpenAI:
    if not OPENROUTER_API_KEY:
        raise ValueError("Не найден OPENROUTER_API_KEY в переменных окружения (.env)")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        http_client=httpx.Client(trust_env=False)
    )


SYSTEM_PROMPT = """Ты опытный SEO-специалист и контент-менеджер B2B интернет-магазина.
Создай черновик карточки товара.

ВЕРНИ СТРОГО JSON-объект со следующими ключами:
- "seo_title": строка (SEO-заголовок до 70 символов)
- "seo_description": строка (SEO-описание от 800 до 1200 символов)
- "key_specs": массив строк (список ключевых характеристик)
- "search_queries": массив строк (3-5 поисковых запросов)
- "commercial_block": строка (commercial-блок для менеджера)

ПРАВИЛА:
1. НЕ ВЫДУМЫВАЙ характеристики. Используй только переданные данные.
2. Если данных нет, укажи «данных нет».
"""


def generate_product_card(product: ProductInput) -> ProductCardOutput:
    client = get_llm_client()

    user_prompt = f"""Сформируй карточку товара на основе следующих данных:
                        Название: {product.name}
                        Производитель: {product.manufacturer}
                        Характеристики: {json.dumps(product.specs, ensure_ascii=False)}
                        Описание / Техпаспорт: {product.description}
                        """

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return ProductCardOutput(**data)

    except Exception as e:
        raise RuntimeError(f"Ошибка при обращении к LLM API: {str(e)}")