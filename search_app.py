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
SERPER_API_KEY = "e9eac514f1cd4452b6f6a672b3c9cd2d"  # Ваш API ключ

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
st.header("🔥 Последние новости о Бёртоне")

# Ключевые слова для поиска новостей о Тиме Бёртоне
burton_keywords = (
    # Основные запросы
    '"Tim Burton" OR "Тим Бёртон" OR "Тима Бёртона" OR '
    # Проекты и фильмы
    '"Wednesday" OR "Уэднесдэй" OR "Уэнсдэй" OR '
    '"Beetlejuice 2" OR "Битлджус 2" OR "Битрлджус" OR '
    '"The Nightmare Before Christmas" OR "Кошмар перед Рождеством" OR '
    '"Edward Scissorhands" OR "Эдвард Руки-ножницы" OR '
    # Актеры и команда
    '"Johnny Depp" OR "Джонни Депп" OR '
    '"Helena Bonham Carter" OR "Хелена Бонем Картер" OR '
    '"Danny Elfman" OR "Дэнни Эльфман" OR '
    '"Winona Ryder" OR "Вайнона Райдер" OR '
    # Компании и студии
    '"Burton Productions" OR "Tim Burton Productions" OR '
    # События и награды
    '"Burton exhibition" OR "выставка Бёртона" OR '
    '"Burton style" OR "стиль Бёртона"'
)

with st.spinner("🦇 Ищу последние новости о Тим Бёртоне..."):
    latest_articles, error = fetch_google_news(burton_keywords)

    if error:
        st.error(f"Ошибка при поиске: {error}")
    elif latest_articles:
        st.success(f"🎭 Найдено свежих новостей: {len(latest_articles)}")
        
        for idx, article in enumerate(latest_articles[:15]): # Показываем до 15 новостей
            with st.container():
                st.markdown(f"""
                <div class="news-card">
                    <h3 style="color: #f0e68c;">{article['title']}</h3>
                    <p style="color: #ccc; font-size: 0.9em;">
                    📰 <strong>Источник:</strong> {article['source']} | 
                    📅 <strong>Дата:</strong> {article.get('date', 'Неизвестно')}
                    </p>
                    <p style="color: #e0e0e0;">{article.get('snippet', 'Описание отсутствует.')}</p>
                    <a href="{article['link']}" target="_blank" style="color: #ff6b6b; text-decoration: none;">
                    🔗 Читать полную статью
                    </a>
                </div>
                """, unsafe_allow_html=True)
                
                if idx < len(latest_articles[:15]) - 1:
                    st.markdown("<hr style='border: 1px solid #444;'>", unsafe_allow_html=True)
    else:
        st.info("📭 Не удалось найти свежих новостей о Тим Бёртоне за последнюю неделю.")

# --- Раздел "Индивидуальный поиск" ---
st.header("🔍 Персональный поиск по вселенной Бёртона")
st.write("Ищите информацию о конкретных фильмах, актерах или событиях связанных с Тим Бёртоном.")

# Быстрые кнопки поиска
st.markdown("### 🚀 Популярные запросы:")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🎬 Уэднесдэй 2", use_container_width=True):
        st.session_state.custom_search = "Уэднесдэй 2 сезон новости Тим Бёртон"
with col2:
    if st.button("👻 Битлджус 2", use_container_width=True):
        st.session_state.custom_search = "Beetlejuice 2 новости 2024"
with col3:
    if st.button("🎭 Джонни Депп", use_container_width=True):
        st.session_state.custom_search = "Джонни Депп Тим Бёртон сотрудничество"
with col4:
    if st.button("🎵 Дэнни Эльфман", use_container_width=True):
        st.session_state.custom_search = "Дэнни Эльфман музыка Бёртона"

# Поле для ввода запроса
if 'custom_search' in st.session_state:
    default_search = st.session_state.custom_search
else:
    default_search = ""

search_term = st.text_input(
    "Введите ваш запрос о Тим Бёртоне:", 
    value=default_search,
    placeholder="Например: Тим Бёртон выставка, новые проекты 2024, готический стиль..."
)

# Примеры запросов
with st.expander("📋 Примеры запросов"):
    st.markdown("""
    - **Фильмы:** "Кошмар перед Рождеством новости", "Эдвард Руки-ножницы ремастер"
    - **Актеры:** "Майкл Китон Битлджус", "Ева Грин Бёртон", "Кристофер Ли"
    - **Стиль:** "Готический стиль Бёртона", "визуальные эффекты Бёртона"
    - **События:** "Выставка Бёртона в музее", "интервью Тим Бёртон 2024"
    - **Проекты:** "Новые проекты Бёртона", "анимационные работы Бёртона"
    """)

if st.button("🔎 Найти новости", type="primary", use_container_width=True):
    if not search_term:
        st.warning("⚠️ Пожалуйста, введите запрос для поиска.")
    else:
        with st.spinner(f"🦇 Ищу новости по запросу '{search_term}'..."):
            articles, error = fetch_google_news(search_term)

            if error:
                st.error(f"Ошибка: {error}")
            elif not articles:
                st.info(f"📭 Новостей по запросу '{search_term}' не найдено.")
                
                # Предлагаем альтернативные варианты
                st.markdown("### 💡 Попробуйте другие запросы:")
                alt_cols = st.columns(3)
                alt_queries = [
                    "Тим Бёртон",
                    "Tim Burton новости",
                    "Бёртон проекты"
                ]
                
                for i, query in enumerate(alt_queries):
                    with alt_cols[i]:
                        if st.button(query, use_container_width=True):
                            st.session_state.custom_search = query
                            st.rerun()
            else:
                st.success(f"🎭 Найдено результатов: {len(articles)}")
                
                for idx, article in enumerate(articles[:20]): # Показываем до 20 результатов
                    with st.container():
                        st.markdown(f"""
                        <div class="news-card">
                            <h3 style="color: #f0e68c;">{article['title']}</h3>
                            <p style="color: #ccc; font-size: 0.9em;">
                            📰 <strong>Источник:</strong> {article['source']} | 
                            📅 <strong>Дата:</strong> {article.get('date', 'Неизвестно')}
                            </p>
                            <p style="color: #e0e0e0;">{article.get('snippet', 'Описание отсутствует.')}</p>
                            <a href="{article['link']}" target="_blank" style="color: #ff6b6b; text-decoration: none;">
                            🔗 Читать полную статью
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if idx < len(articles[:20]) - 1:
                            st.markdown("<hr style='border: 1px solid #444;'>", unsafe_allow_html=True)

# --- Раздел "Статистика" ---
st.sidebar.header("📊 Статистика поиска")
st.sidebar.markdown("""
**Поиск по ключевым темам:**
- 🎬 Фильмы и проекты
- 🎭 Актеры и команда  
- 🏛️ Выставки и события
- 🎨 Стиль и творчество
- 📅 Новости 2023-2024
""")

if latest_articles:
    st.sidebar.metric("📈 Найдено новостей", len(latest_articles))
    sources = list(set([article['source'] for article in latest_articles[:10]]))
    st.sidebar.markdown(f"**📰 Источники:** {', '.join(sources[:5])}")

# --- Кнопка "Назад" ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔙 Навигация")
if st.sidebar.button("⬅️ Вернуться на главную", use_container_width=True):
    st.markdown("""
    <script>
        window.open('https://quixotic-shrimp-ea9.notion.site/9aabb68bd7004965819318e32d8ff06e?v=2b4a0ca7844a80d6aa8a000c6a7e5272', '_blank');
    </script>
    """, unsafe_allow_html=True)

# --- Информация о системе ---
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ О системе")
st.sidebar.markdown("""
**Технологии:**
- 🐍 Python + Streamlit
- 🔍 Google News API (Serper.dev)
- 🕐 Поиск за последнюю неделю
- 🇷🇺 Русскоязычные источники

**Обновляется:** Каждые 30 минут
""")

# --- Футер ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p>🦇 Система поиска новостей вселенной Тима Бёртона</p>
    <p><small>Использует Google News API для поиска актуальной информации</small></p>
</div>
""", unsafe_allow_html=True)
