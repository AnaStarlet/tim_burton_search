import streamlit as st
import requests
import os
from datetime import datetime
from urllib.parse import quote
import json

# --- Настройки страницы ---
st.set_page_config(page_title="Новости о Тиме Бёртоне", page_icon="🦇", layout="wide")

# --- Стили для тёмной темы Бёртона ---
st.markdown("""
<style>
    .stApp { 
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        color: #e0e0e0;
    }
    .main-header {
        color: #f0e68c;
        text-align: center;
        font-family: 'Creepster', cursive;
        font-size: 3rem;
    }
    .section-header {
        color: #f0e68c;
        font-family: 'Irish Grover', cursive;
        border-bottom: 2px solid #f0e68c;
        padding-bottom: 10px;
    }
    .news-card {
        background: #2a2a2a;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #f0e68c;
        margin: 15px 0;
    }
    .news-title {
        color: #f0e68c;
        font-size: 1.3rem;
    }
    .news-source {
        color: #c0c0c0;
        font-style: italic;
    }
    .stTextInput>div>div>input {
        background: #3a3a3a;
        color: #f0e68c;
        border: 2px solid #f0e68c;
    }
    .stButton button {
        background: linear-gradient(45deg, #4a4a4a, #6a6a6a);
        color: #f0e68c;
        border: 2px solid #f0e68c;
        border-radius: 10px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# --- Функция для поиска новостей через Google (Serper.dev) ---
@st.cache_data(ttl=1800)  # Кэшируем результат на 30 минут
def fetch_google_news(search_query):
    """Ищет новости через Google News API от Serper.dev."""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return None, "Ключ SERPER_API_KEY не найден в секретах."

    url = "https://google.serper.dev/news"
    # Добавляем в запрос требование искать только за последнюю неделю для свежести
    payload = json.dumps({"q": search_query, "gl": "ru", "hl": "ru", "tbs": "qdr:w"})
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            results = response.json().get("news", [])
            return results, None
        else:
            return None, f"Ошибка API Serper. Статус: {response.status_code}, Ответ: {response.text}"
    except Exception as e:
        return None, f"Ошибка сети: {e}"


# === ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ===
st.markdown('<div class="main-header">🦇 Новости о Тиме Бёртоне</div>', unsafe_allow_html=True)
st.markdown("### Автоматический поиск самых актуальных новостей о творчестве, фильмах и проектах Тима Бёртона")
st.divider()

# --- Раздел "Последние актуальные новости" ---
st.markdown('<div class="section-header">🔥 Последние новости о Тим Бёртоне</div>', unsafe_allow_html=True)

# Ключевые слова для поиска новостей о Тиме Бёртоне
burton_keywords = (
    # Имя режиссера на разных языках
    '"Tim Burton" OR "Тим Бёртон" OR "Тим Бертон" OR '
    # Основные фильмы
    '"The Nightmare Before Christmas" OR "Кошмар перед Рождеством" OR '
    '"Edward Scissorhands" OR "Эдвард руки-ножницы" OR '
    '"Beetlejuice" OR "Битлджус" OR "Битлджуис" OR '
    '"Corpse Bride" OR "Труп невесты" OR '
    '"Alice in Wonderland" OR "Алиса в Стране чудес" OR '
    # Новые проекты
    '"Beetlejuice 2" OR "Битлджус 2" OR "Битлджус Битлджус" OR '
    '"Wednesday" OR "Уэнздей" OR '
    # Актёры-коллабораторы
    '"Johnny Depp" OR "Джонни Депп" OR '
    '"Helena Bonham Carter" OR "Хелена Бонем Картер" OR '
    '"Michael Keaton" OR "Майкл Китон" OR '
    # Стиль и творчество
    '"Burtonesque" OR "готическая эстетика" OR "стиль Бёртона"'
)

with st.spinner("🦇 Ищу свежие новости о Тиме Бёртоне..."):
    latest_articles, error = fetch_google_news(burton_keywords)

    if error:
        st.error(f"Ошибка при поиске новостей: {error}")
    elif latest_articles:
        st.success(f"Найдено свежих новостей: {len(latest_articles)}")

        for i, article in enumerate(latest_articles[:8]):  # Показываем до 8 новостей
            with st.container():
                st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">{article['title']}</div>
                    <div class="news-source">📰 {article['source']} | 🕐 {article.get('date', 'Дата неизвестна')}</div>
                    <p>{article.get('snippet', 'Описание отсутствует.')}</p>
                    <a href="{article['link']}" target="_blank" style="color: #f0e68c; text-decoration: none;">🔗 Читать полную статью</a>
                </div>
                """, unsafe_allow_html=True)

            if i < len(latest_articles[:8]) - 1:
                st.markdown("---")
    else:
        st.info("Не удалось найти свежих новостей о Тиме Бёртоне за последнюю неделю.")

# --- Раздел "Индивидуальный поиск" ---
st.markdown('<div class="section-header">🔍 Поиск по конкретным проектам</div>', unsafe_allow_html=True)

st.markdown("""
<div style="background: #2a2a2a; padding: 15px; border-radius: 10px; margin: 10px 0;">
    <strong>💡 Примеры запросов:</strong><br>
    • <em>Уэнздей 2 сезон</em> - новости о продолжении сериала<br>
    • <em>Битлджус Битлджус</em> - о новом фильме<br>
    • <em>Джонни Депп Тим Бёртон</em> - об их сотрудничестве<br>
    • <em>новые проекты Тим Бёртон 2024</em> - о будущих работах
</div>
""", unsafe_allow_html=True)

# Поле для поиска
search_term = st.text_input(
    "Введите ваш запрос для поиска:",
    placeholder="Например: Уэнздей 2 сезон или новые проекты Бёртона...",
    key="custom_search"
)

col1, col2 = st.columns([1, 4])
with col1:
    search_button = st.button("🔎 Найти новости", use_container_width=True)

if search_button:
    if not search_term:
        st.warning("Пожалуйста, введите запрос для поиска.")
    else:
        with st.spinner(f"Ищу новости по запросу '{search_term}'..."):
            articles, error = fetch_google_news(search_term)

            if error:
                st.error(f"Ошибка при поиске: {error}")
            elif not articles:
                st.info(f"📭 Новостей по запросу '{search_term}' не найдено.")
            else:
                st.success(f"🎯 Найдено результатов: {len(articles)}")

                for i, article in enumerate(articles[:10]):
                    with st.container():
                        st.markdown(f"""
                        <div class="news-card">
                            <div class="news-title">{article['title']}</div>
                            <div class="news-source">📰 {article['source']} | 🕐 {article.get('date', 'Дата неизвестна')}</div>
                            <p>{article.get('snippet', 'Описание отсутствует.')}</p>
                            <a href="{article['link']}" target="_blank" style="color: #f0e68c; text-decoration: none;">🔗 Читать полную статью</a>
                        </div>
                        """, unsafe_allow_html=True)

                    if i < len(articles[:10]) - 1:
                        st.markdown("---")

# --- Информация о приложении ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #c0c0c0;">
    <p>🦇 <strong>Tim Burton News Search</strong> • Автоматический сбор новостей из открытых источников</p>
    <p>🔍 Поиск через Google News API • Обновляется каждые 30 минут</p>
</div>
""", unsafe_allow_html=True)
