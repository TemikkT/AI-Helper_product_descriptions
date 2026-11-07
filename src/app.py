import json
import os
import streamlit as st
from pydantic import ValidationError
from src.models import ProductInput
from src.llm_service import generate_product_card

st.set_page_config(
    page_title="AI-помощник подготовки товарных описаний",
    layout="wide"
)

st.title("AI-помощник для подготовки товарных описаний (B2B)")
st.markdown("Прототип сервиса генерации карточек товаров по техническим данным контрольно-измерительных приборов.")

# Загрузка примеров
SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_products.json")
samples = []
if os.path.exists(SAMPLE_PATH):
    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        samples = json.load(f)

st.sidebar.header("Входные данные")
input_mode = st.sidebar.radio("Источник данных:", ["Готовые примеры из YML", "Ввести JSON вручную"])

selected_data = {}
if input_mode == "Готовые примеры из YML" and samples:
    sample_names = [s["name"] for s in samples]
    chosen_name = st.sidebar.selectbox("Выберите товар:", sample_names)
    selected_data = next((s for s in samples if s["name"] == chosen_name), samples[0])
    json_str = json.dumps(selected_data, ensure_ascii=False, indent=2)
    user_input_json = st.sidebar.text_area("JSON товара", value=json_str, height=300)
else:
    default_json = json.dumps(samples[0] if samples else {}, ensure_ascii=False, indent=2)
    user_input_json = st.sidebar.text_area("JSON товара", value=default_json, height=300)

if st.sidebar.button("Сгенерировать карточку товара", type="primary"):
    try:
        raw_dict = json.loads(user_input_json)
        product_input = ProductInput(**raw_dict)

        with st.spinner("Генерация карточки с помощью LLM..."):
            card = generate_product_card(product_input)

        st.success("Карточка успешно сгенерирована!")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("SEO и Запросы")
            st.markdown(f"**SEO-заголовок (до 70 символов):**\n`{card.seo_title}` ({len(card.seo_title)} симв.)")
            
            st.markdown("**SEO-описание (800–1200 символов):**")
            st.info(card.seo_description)
            st.caption(f"Длина описания: {len(card.seo_description)} символов")

            st.markdown("**Поисковые запросы (3–5 шт.):**")
            for q in card.search_queries:
                st.markdown(f"- {q}")

        with col2:
            st.subheader("Характеристики и Коммерческий блок")
            
            st.markdown("**Ключевые характеристики:**")
            for spec in card.key_specs:
                st.markdown(f"- {spec}")

            st.markdown("**Commercial-блок для менеджера:**")
            st.warning(card.commercial_block)

    except json.JSONDecodeError:
        st.error("Ошибка: Некорректный формат JSON. Проверьте синтаксис (кавычки, запятые).")
    except ValidationError as ve:
        st.error(f"Ошибка валидации данных: {ve}")
    except Exception as ex:
        st.error(f"Произошла ошибка: {ex}")