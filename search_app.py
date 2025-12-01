import streamlit as st
import requests
import os
from datetime import datetime
from urllib.parse import quote
import json

# --- Настройки страницы ---
st.set_page_config(page_title="Новости Вселенной Тима Бёртона", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0f0f1f; }
    body, p, .st-emotion-cache-16txtl3, .st-emotion-cache-1629p8f p, .st-emotion-cache-1xarl3l, h1, h2, h3, h4, h5, h6 {
        color: #f0e68c !important;
    }
    .st-emotion-cache-16txtl3 { padding-top: 2rem; }
    .news-card {
        background-color: #2b2b2b;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #f0e68c;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- Ваш API ключ Serper.dev ---
SERPER_API_KEY = "e9eac514f1cd4452b6f6a672b3c9cd2d"

# --- Функция для поиска новостей через Google (Serper.dev) ---
@st.cache_data(ttl=1800) # Кэшируем результат на 30 минут
def fetch_google_news(search_query):
    """Ищет новости через Google News API от Serper.dev."""
    if not SERPER_API_KEY:
        return None, "API ключ не настроен."

    url = "https://google.serper.dev/news"
    # Добавляем в запрос требование искать только за последнюю неделю для свежести
    payload = json.dumps({"q": search_query, "gl": "ru", "hl": "ru", "tbs": "qdr:w"})
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            results = response.json().get("news", [])
            return results, None
        else:
            return None, f"Ошибка API. Статус: {response.status_code}"
    except Exception as e:
        return None, f"Ошибка сети: {e}"

# === ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ===
st.title("🦇 Дайджест новостей вселенной Тима Бёртона")
st.write("Автоматический поиск самых актуальных новостей о Тим Бёртоне, его фильмах, проектах и команде.")
st.divider()

# --- Раздел "Последние актуальные новости" ---
st.header("🔥 Последние релевантные новости")

# Ключевые слова для поиска новостей о Тиме Бёртоне
relevant_keywords = (
    # Основное
    '"Tim Burton" OR "Тим Бёртон" OR "Тима Бёртона" OR '
    # Фильмы и проекты
    '"Wednesday" OR "Уэднесдэй" OR "Уэнсдэй" OR '
    '"Beetlejuice" OR "Битлджус" OR "Битлджуис" OR '
    '"Edward Scissorhands" OR "Эдвард Руки-ножницы" OR '
    '"The Nightmare Before Christmas" OR "Кошмар перед Рождеством" OR '
    '"Sleepy Hollow" OR "Сонная Лощина" OR '
    # Актеры и команда
    '"Johnny Depp" OR "Джонни Депп" OR '
    '"Helena Bonham Carter" OR "Хелена Бонем Картер" OR '
    '"Danny Elfman" OR "Дэнни Эльфман" OR '
    '"Winona Ryder" OR "Вайнона Райдер" OR '
    '"Michael Keaton" OR "Майкл Китон" OR '
    # Компании
    '"Burton Productions" OR "Tim Burton Productions" OR '
    # События
    '"Burton exhibition" OR "выставка Бёртона" OR '
    '"Burton style" OR "стиль Бёртона" OR "готический стиль"'
)

with st.spinner("Загружаю самые релевантные новости о Тим Бёртоне за последнюю неделю..."):
    latest_articles, error = fetch_google_news(relevant_keywords)

    if error:
        st.error(error)
    elif latest_articles:
        st.success(f"Найдено свежих новостей: {len(latest_articles)}")
        for article in latest_articles[:10]: # Показываем до 10 новостей
            with st.container():
                st.markdown(f"""
                <div class="news-card">
                    <h3 style="color: #f0e68c;">{article['title']}</h3>
                    <p style="color: #ccc; font-size: 0.9em;">
                    📰 <strong>Источник:</strong> {article['source']} | 
                    📅 <strong>Опубликовано:</strong> {article.get('date', 'Дата неизвестна')}
                    </p>
                    <p style="color: #e0e0e0;">{article.get('snippet', 'Описание отсутствует.')}</p>
                    <a href="{article['link']}" target="_blank" style="color: #ff6b6b; text-decoration: none;">
                    🔗 Читать полную статью
                    </a>
                </div>
                """, unsafe_allow_html=True)
                
                if latest_articles.index(article) < 9:  # Добавляем разделитель между новостями
                    st.markdown("<hr style='border: 1px solid #444;'>", unsafe_allow_html=True)
    else:
        st.info("Не удалось найти свежих новостей о Тим Бёртоне за последнюю неделю.")

# --- Раздел "Индивидуальный поиск" ---
st.header("🔍 Индивидуальный поиск")
st.write("Ищите информацию о конкретных фильмах, актерах или событиях связанных с Тим Бёртоном.")

# Примеры для пользователя
st.info('Примеры запросов: Уэднесдэй 2 сезон, Битлджус 2, Джонни Депп, готический стиль')

search_term = st.text_input("Введите ваш точный запрос для поиска:", "")

if st.button("Найти"):
    if not search_term:
        st.warning("Пожалуйста, введите запрос для поиска.")
    else:
        with st.spinner(f"Ищу в Google News по запросу '{search_term}'..."):
            articles, error = fetch_google_news(search_term)

            if error:
                st.error(error)
            elif not articles:
                st.info(f"Новостей по запросу '{search_term}' не найдено.")
            else:
                st.success(f"Найдено результатов: {len(articles)}")
                for article in articles[:15]:
                    with st.container():
                        st.markdown(f"""
                        <div class="news-card">
                            <h3 style="color: #f0e68c;">{article['title']}</h3>
                            <p style="color: #ccc; font-size: 0.9em;">
                            📰 <strong>Источник:</strong> {article['source']} | 
                            📅 <strong>Опубликовано:</strong> {article.get('date', 'Дата неизвестна')}
                            </p>
                            <p style="color: #e0e0e0;">{article.get('snippet', 'Описание отсутствует.')}</p>
                            <a href="{article['link']}" target="_blank" style="color: #ff6b6b; text-decoration: none;">
                            🔗 Читать полную статью
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if articles.index(article) < 14:  # Добавляем разделитель
                            st.markdown("<hr style='border: 1px solid #444;'>", unsafe_allow_html=True)

# --- Сайдбар с дополнительной информацией ---
with st.sidebar:
    st.markdown("### 🦇 О системе поиска")
    st.markdown("""
    **Поиск по темам:**
    - Фильмы и проекты Бёртона
    - Актеры и команда
    - Выставки и события
    - Интервью и новости
    - Стиль и творчество
    
    **Использует:** Google News API
    **Период:** Последняя неделя
    **Язык:** Русский
    """)
    
    st.markdown("---")
    
    # Кнопка "Назад" с прямой ссылкой
    if st.button("⬅️ На главную", use_container_width=True):
        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            <a href="https://quixotic-shrimp-ea9.notion.site/9aabb68bd7004965819318e32d8ff06e?v=2b4a0ca7844a80d6aa8a000c6a7e5272" 
               target="_blank" 
               style="display: inline-block; padding: 10px 20px; background: #f0e68c; color: #0f0f1f; 
                      border-radius: 5px; text-decoration: none; font-weight: bold;">
            🏠 Открыть главную страницу
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- Футер ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p>🦇 Система поиска новостей вселенной Тима Бёртона</p>
    <p><small>Использует Google News API для поиска актуальной информации</small></p>
</div>
""", unsafe_allow_html=True)
