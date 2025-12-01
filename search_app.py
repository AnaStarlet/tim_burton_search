import streamlit as st
import requests
from urllib.parse import quote
import json
import re

# --- Настройки страницы ---
st.set_page_config(page_title="Новости Вселенной Тима Бёртона", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0f0f1f; }
    .main-title { color: #f0e68c; text-align: center; margin-bottom: 30px; }
    .news-card {
        background-color: #2b2b2b;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #f0e68c;
        margin-bottom: 20px;
        transition: transform 0.3s;
    }
    .not-related-box {
        background-color: #2b2b2b;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff6b6b;
        margin: 20px 0;
    }
    .warning-message {
        background-color: #332222;
        color: #ff9999;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ff6b6b;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Проверка темы запроса ---
def is_burton_related(query):
    """Проверяет, связан ли запрос с Тимом Бёртоном"""
    query_lower = query.lower()
    
    # Ключевые слова Бёртона
    burton_keywords = [
        # Имена и фамилии
        'буртон', 'burton', 'тим', 'tim',
        # Фильмы
        'уэднесдэй', 'wednesday', 'битлджус', 'beetlejuice',
        'эдвард', 'edward', 'ножницы', 'scissorhands',
        'кошмар', 'nightmare', 'рождество', 'christmas',
        'сонная', 'sleepy', 'лощина', 'hollow',
        'суини', 'sweeney', 'тодд', 'todd',
        'чарли', 'charlie', 'шоколад', 'chocolate',
        'планета', 'planet', 'обезьян', 'apes',
        'алиса', 'alice', 'страна', 'wonderland',
        # Актеры
        'депп', 'depp', 'джонни', 'johnny',
        'хелена', 'helena', 'бонем', 'bonham',
        'вайнона', 'winona', 'райдер', 'ryder',
        'майкл', 'michael', 'китон', 'keaton',
        'лиза', 'lisa', 'мэри', 'mary',
        # Команда
        'эльфман', 'elfman', 'дэнни', 'danny',
        # Общие темы
        'режиссер', 'режиссёр', 'director',
        'готика', 'готический', 'gothic',
        'анимация', 'animation', 'кукольный',
        'стиль', 'style', 'выставка', 'exhibition',
        'проект', 'project', 'фильм', 'movie',
        'кино', 'cinema', 'сериал', 'series'
    ]
    
    # Проверяем наличие хотя бы одного ключевого слова
    for keyword in burton_keywords:
        if keyword in query_lower:
            return True
    
    return False

# --- Создание Google ссылки ---
def create_google_link(query):
    """Создает ссылку для поиска в Google"""
    encoded_query = quote(f"{query}")
    return f"https://www.google.com/search?q={encoded_query}"

# --- Поиск новостей (только по Бёртону) ---
@st.cache_data(ttl=3600)
def search_burton_news(query):
    """Поиск новостей только по тематике Бёртона"""
    if not is_burton_related(query):
        return None, "not_related"
    
    try:
        # Пытаемся получить RSS из Google News
        search_url = f"https://news.google.com/rss/search?q={quote(f'Тим Бёртон {query}')}&hl=ru&gl=RU&ceid=RU:ru"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            articles = []
            for item in root.findall('.//item')[:10]:
                title = item.find('title').text if item.find('title') is not None else 'Без названия'
                link = item.find('link').text if item.find('link') is not None else '#'
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else 'Дата неизвестна'
                
                # Получаем описание
                description = ''
                if item.find('description') is not None:
                    desc_text = item.find('description').text or ''
                    description = re.sub('<[^<]+?>', '', desc_text)
                
                # Фильтруем статьи, не связанные с Бёртоном
                article_text = f"{title} {description}".lower()
                if any(keyword in article_text for keyword in ['буртон', 'burton', 'тим', 'tim']):
                    articles.append({
                        'title': title,
                        'link': link,
                        'snippet': description[:200] + '...' if len(description) > 200 else description,
                        'source': 'Google News',
                        'date': pub_date
                    })
            
            if articles:
                return articles, None
            else:
                return None, "no_results"
        else:
            return None, f"error_{response.status_code}"
            
    except Exception as e:
        return None, f"error_{str(e)}"

# === ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ===
st.markdown('<h1 class="main-title">🦇 Новости вселенной Тима Бёртона</h1>', unsafe_allow_html=True)
st.write("Ищите только новости, связанные с Тимом Бёртоном, его фильмами и проектами")
st.divider()

# --- Быстрые запросы ---
st.header("🎬 Быстрые запросы о Бёртоне")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Уэднесдэй 2", use_container_width=True):
        st.session_state.search_query = "Уэднесдэй 2 сезон"
with col2:
    if st.button("Битлджус 2", use_container_width=True):
        st.session_state.search_query = "Битлджус 2 фильм"
with col3:
    if st.button("Джонни Депп", use_container_width=True):
        st.session_state.search_query = "Джонни Депп Бёртон"
with col4:
    if st.button("Новые проекты", use_container_width=True):
        st.session_state.search_query = "новые проекты Тим Бёртон"

# --- Поле поиска ---
st.header("🔍 Поиск новостей")
st.write("Введите запрос, связанный с Тимом Бёртоном:")

if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

search_query = st.text_input(
    "Ваш запрос:",
    value=st.session_state.search_query,
    placeholder="Например: выставка Бёртона, интервью Тим Бёртон, готический стиль...",
    label_visibility="collapsed"
)

# --- Обработка поиска ---
if st.button("🔍 Найти новости", type="primary", use_container_width=True):
    if not search_query:
        st.warning("⚠️ Пожалуйста, введите запрос")
    else:
        st.session_state.search_query = search_query
        
        # Проверяем, связан ли запрос с Бёртоном
        if not is_burton_related(search_query):
            st.markdown(f"""
            <div class="warning-message">
                <h3>🦇 Этот запрос не связан с Тимом Бёртоном</h3>
                <p>Вы искали: <strong>{search_query}</strong></p>
                <p>Эта система ищет только информацию, связанную с Тимом Бёртоном, его фильмами, актерами и проектами.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Предлагаем поиск в Google
            google_url = create_google_link(search_query)
            st.markdown(f"""
            <div class="not-related-box">
                <h3 style="color: #ff6b6b;">🔍 Попробуйте поискать в Google:</h3>
                <a href="{google_url}" target="_blank" style="
                    display: inline-block;
                    background: linear-gradient(45deg, #4285f4, #34a853);
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 16px;
                    margin-top: 10px;
                ">
                🔎 Поиск "{search_query}" в Google
                </a>
                <p style="color: #ccc; margin-top: 10px; font-size: 14px;">
                Ссылка откроется в новой вкладке
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Показываем примеры запросов по Бёртону
            st.markdown("---")
            st.subheader("💡 Примеры запросов о Бёртоне:")
            
            examples = [
                "Тим Бёртон интервью 2024",
                "Выставка работ Бёртона",
                "Готический стиль в фильмах",
                "Дэнни Эльфман музыка",
                "Хелена Бонем Картер"
            ]
            
            cols = st.columns(3)
            for i, example in enumerate(examples):
                with cols[i % 3]:
                    if st.button(example, use_container_width=True):
                        st.session_state.search_query = example
                        st.rerun()
        else:
            # Если запрос связан с Бёртоном, ищем новости
            with st.spinner(f"🦇 Ищу новости по теме '{search_query}'..."):
                articles, error = search_burton_news(search_query)
                
                if error == "not_related":
                    st.error("Этот запрос не связан с Тимом Бёртоном")
                elif error == "no_results":
                    st.info(f"📭 По запросу '{search_query}' не найдено новостей о Бёртоне")
                    
                    # Предлагаем альтернативные запросы
                    st.markdown("### 💡 Попробуйте:")
                    alt_queries = [
                        "Тим Бёртон",
                        "Burton films",
                        "Проекты Бёртона"
                    ]
                    
                    for alt in alt_queries:
                        if st.button(f"🔍 {alt}", key=f"alt_{alt}"):
                            st.session_state.search_query = alt
                            st.rerun()
                elif error and error.startswith("error"):
                    st.error(f"Ошибка при поиске: {error}")
                    
                    # Все равно предлагаем Google поиск
                    google_url = create_google_link(f"Тим Бёртон {search_query}")
                    st.markdown(f"""
                    <div style="background-color: #2b2b2b; padding: 15px; border-radius: 10px; margin: 20px 0;">
                        <p>Вы можете попробовать поискать напрямую:</p>
                        <a href="{google_url}" target="_blank" style="color: #4285f4; font-weight: bold;">
                        🔍 Поиск "Тим Бёртон {search_query}" в Google
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                elif articles:
                    st.success(f"🎭 Найдено новостей: {len(articles)}")
                    
                    for idx, article in enumerate(articles):
                        with st.container():
                            st.markdown(f"""
                            <div class="news-card">
                                <h4 style="color: #f0e68c; margin: 0;">{article['title']}</h4>
                                <p style="color: #ccc; font-size: 0.85em; margin: 5px 0;">
                                📰 {article.get('source', 'Источник')} | 📅 {article.get('date', '')}
                                </p>
                                <p style="color: #e0e0e0; margin: 10px 0;">{article.get('snippet', '')}</p>
                                <a href="{article['link']}" target="_blank" style="color: #ff6b6b; text-decoration: none;">
                                🔗 Открыть статью
                                </a>
                            </div>
                            """, unsafe_allow_html=True)

# --- Информация в сайдбаре ---
with st.sidebar:
    st.markdown("### 🦇 О системе поиска")
    st.markdown("""
    **Ищем только информацию о:**
    
    ✅ **Тим Бёртон:**
    - Фильмы и проекты
    - Актеры команды
    - Композиторы и команда
    - Выставки и события
    - Интервью и новости
    
    ✅ **Примеры запросов:**
    - "Уэднесдэй 2 сезон"
    - "Битлджус 2 фильм"
    - "Стиль Бёртона"
    - "Дэнни Эльфман"
    - "Выставка Бёртона"
    
    """)
    
    st.markdown("---")
    st.markdown("### 🔙 Навигация")
    if st.button("⬅️ На главную страницу", use_container_width=True):
        st.markdown("""
        <script>
            window.open('https://quixotic-shrimp-ea9.notion.site/9aabb68bd7004965819318e32d8ff06e?v=2b4a0ca7844a80d6aa8a000c6a7e5272', '_blank');
        </script>
        """, unsafe_allow_html=True)

# --- Футер ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px; font-size: 0.9em;'>
    <p>🦇 Поиск новостей вселенной Тима Бёртона • Только релевантная информация</p>
    <p><small>Запросы фильтруются по тематике Бёртона</small></p>
</div>
""", unsafe_allow_html=True)
