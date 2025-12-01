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
    }
    .google-btn {
        display: inline-block;
        background: linear-gradient(45deg, #4285f4, #34a853);
        color: white !important;
        padding: 12px 24px;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        font-size: 16px;
        margin: 10px 0;
        border: none;
        cursor: pointer;
        text-align: center;
    }
    .google-btn:hover {
        opacity: 0.9;
    }
    .back-btn {
        background: linear-gradient(45deg, #f0e68c, #ff6b6b);
        color: #0f0f1f !important;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        text-decoration: none;
        display: inline-block;
        margin: 10px 0;
    }
    .error-box {
        background-color: #332222;
        color: #ff9999;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #ff6b6b;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Константы ---
MAIN_PAGE_URL = "https://quixotic-shrimp-ea9.notion.site/9aabb68bd7004965819318e32d8ff06e?v=2b4a0ca7844a80d6aa8a000c6a7e5272"

# --- Проверка темы ---
def is_burton_related(query):
    """Проверяет, связан ли запрос с Тимом Бёртоном"""
    query_lower = query.lower()
    
    burton_keywords = [
        # Основное
        'буртон', 'burton', 'тим', 'tim', 'бёртон',
        
        # Фильмы
        'уэднесдэй', 'wednesday', 'уеднесдей', 'венсдей',
        'битлджус', 'beetlejuice', 'битлджуис',
        'эдвард', 'edward', 'ножницы', 'scissorhands',
        'кошмар', 'nightmare', 'рождество', 'christmas',
        'сонная', 'sleepy', 'лощина', 'hollow',
        'суини', 'sweeney', 'тодд', 'todd',
        'чарли', 'charlie', 'шоколад', 'chocolate',
        'алиса', 'alice', 'страна', 'wonderland',
        'франкенвини', 'frankenweenie',
        
        # Актеры
        'депп', 'depp', 'джонни', 'johnny',
        'хелена', 'helena', 'бонем', 'bonham',
        'вайнона', 'winona', 'райдер', 'ryder',
        'майкл', 'michael', 'китон', 'keaton',
        'лиза', 'lisa', 'мэри', 'mary',
        
        # Команда
        'эльфман', 'elfman', 'дэнни', 'danny',
        
        # Темы
        'режиссер', 'режиссёр', 'director',
        'готика', 'готический', 'gothic',
        'анимация', 'animation', 'кукольный',
        'стиль', 'style', 'выставка', 'exhibition',
        'проект', 'project', 'фильм', 'movie',
        'кино', 'cinema', 'сериал', 'series'
    ]
    
    return any(keyword in query_lower for keyword in burton_keywords)

# --- Получение статичных новостей (запасной вариант) ---
def get_static_burton_news():
    """Возвращает статичные новости о Бёртоне (если API недоступно)"""
    return [
        {
            'title': 'Тим Бёртон работает над новыми проектами',
            'snippet': 'Известный режиссер планирует несколько новых фильмов в своем уникальном готическом стиле.',
            'source': 'КиноПоиск',
            'date': '2024',
            'link': 'https://www.kinopoisk.ru/name/20414/'
        },
        {
            'title': 'Уэднесдэй 2 сезон в разработке',
            'snippet': 'Netflix подтвердил работу над вторым сезоном сериала "Уэднесдэй" от Тима Бёртона.',
            'source': 'Netflix News',
            'date': '2024',
            'link': 'https://www.netflix.com/title/81231974'
        },
        {
            'title': 'Битлджус 2: новые детали',
            'snippet': 'Продолжение культового фильма с участием Майкла Китона и Дженны Ортеги.',
            'source': 'IMDb',
            'date': '2024',
            'link': 'https://www.imdb.com/title/tt2049403/'
        },
        {
            'title': 'Выставка работ Тима Бёртона',
            'snippet': 'В музее современного искусства проходит выставка эскизов и работ режиссера.',
            'source': 'Арт-новости',
            'date': '2024',
            'link': 'https://ru.wikipedia.org/wiki/Бёртон,_Тим'
        }
    ]

# --- Поиск новостей с резервным вариантом ---
def search_burton_news_safe(query):
    """Безопасный поиск новостей с резервным вариантом"""
    try:
        # Пробуем получить реальные новости
        search_terms = f"Тим Бёртон {query}"
        search_url = f"https://news.google.com/rss/search?q={quote(search_terms)}&hl=ru&gl=RU&ceid=RU:ru"
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            articles = []
            for item in root.findall('.//item')[:10]:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else '#'
                
                # Фильтруем только про Бёртона
                article_text = f"{title}".lower()
                if any(word in article_text for word in ['буртон', 'burton', 'тим', 'tim']):
                    description = ''
                    if item.find('description') is not None:
                        desc_text = item.find('description').text or ''
                        description = re.sub('<[^<]+?>', '', desc_text)
                    
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'snippet': description[:200] + '...' if len(description) > 200 else description,
                        'source': 'Google News',
                        'date': pub_date
                    })
            
            if articles:
                return articles, True, None
            else:
                # Если нет результатов, возвращаем статичные новости
                return get_static_burton_news(), False, "Используются запасные данные"
                
    except Exception as e:
        # При любой ошибке возвращаем статичные новости
        return get_static_burton_news(), False, f"Ошибка: {str(e)}. Используются запасные данные."
    
    return get_static_burton_news(), False, "Используются запасные данные"

# === ИНТЕРФЕЙС ===
st.markdown('<h1 class="main-title">🦇 Новости вселенной Тима Бёртона</h1>', unsafe_allow_html=True)
st.write("Поиск информации о Тим Бёртоне, его фильмах и проектах")

# --- Быстрые кнопки вверху ---
st.header("🎬 Быстрый поиск")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📺 Уэднесдэй", use_container_width=True):
        st.session_state.search_query = "Уэднесдэй сериал"
with col2:
    if st.button("👻 Битлджус 2", use_container_width=True):
        st.session_state.search_query = "Битлджус 2"
with col3:
    if st.button("🎭 Джонни Депп", use_container_width=True):
        st.session_state.search_query = "Джонни Депп"
with col4:
    if st.button("🎨 Стиль Бёртона", use_container_width=True):
        st.session_state.search_query = "готический стиль"

# --- Основной поиск ---
st.header("🔍 Поиск новостей")

if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

search_query = st.text_input(
    "Введите запрос о Тим Бёртоне:",
    value=st.session_state.search_query,
    placeholder="Например: новые проекты, выставка, интервью...",
    label_visibility="collapsed"
)

# Кнопки в одной строке
col_search, col_back = st.columns([3, 1])

with col_search:
    search_clicked = st.button("🔍 Найти новости", type="primary", use_container_width=True)

with col_back:
    # ПРОСТАЯ КНОПКА "НА ГЛАВНУЮ" С ССЫЛКОЙ
    if st.button("🏠 На главную", use_container_width=True):
        # Используем markdown с прямой ссылкой
        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            <a href="{MAIN_PAGE_URL}" target="_blank" class="back-btn">
            ⬅️ Перейти на главную
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- Обработка поиска ---
if search_clicked and search_query:
    if not is_burton_related(search_query):
        st.markdown(f"""
        <div class="error-box">
            <h3>🦇 Этот запрос не связан с Тимом Бёртоном</h3>
            <p>Вы искали: <strong>"{search_query}"</strong></p>
            <p>Эта система ищет только информацию о Тим Бёртоне, его фильмах, актерах и проектах.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # ОДНА ссылка на Google
        google_url = f"https://www.google.com/search?q={quote(search_query)}"
        st.markdown(f"""
        <div style="text-align: center; margin: 30px 0;">
            <a href="{google_url}" target="_blank" class="google-btn">
            🔍 Поиск в Google: "{search_query}"
            </a>
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.spinner("🦇 Ищу новости..."):
            articles, is_real, message = search_burton_news_safe(search_query)
            
            if message:
                st.info(f"ℹ️ {message}")
            
            if articles:
                st.success(f"🎭 Найдено новостей: {len(articles)}")
                
                for article in articles:
                    with st.container():
                        st.markdown(f"""
                        <div class="news-card">
                            <h4 style="color: #f0e68c;">{article['title']}</h4>
                            <p style="color: #ccc; font-size: 0.9em;">
                            📰 <strong>{article['source']}</strong> | 
                            📅 {article['date']}
                            </p>
                            <p style="color: #e0e0e0;">{article['snippet']}</p>
                            <a href="{article['link']}" target="_blank" 
                               style="color: #ff6b6b; text-decoration: none; font-weight: bold;">
                            🔗 Читать подробнее
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("📭 Новостей не найдено")

# --- Боковая панель ---
with st.sidebar:
    st.markdown("### 🦇 О системе")
    st.markdown("""
    **Что мы ищем:**
    - Фильмы и проекты Бёртона
    - Актеры его команды
    - События и выставки
    - Интервью и новости
    
    **Примеры запросов:**
    - Уэднесдэй 2 сезон
    - Битлджус 2 фильм
    - Джонни Депп
    - Дэнни Эльфман
    - Выставка Бёртона
    """)
    
    st.markdown("---")
    st.markdown("### 🔗 Полезные ссылки")
    
    # Ссылки в сайдбаре
    links = [
        ("📖 Википедия", "https://ru.wikipedia.org/wiki/Бёртон,_Тим"),
        ("🎬 IMDb", "https://www.imdb.com/name/nm0000318/"),
        ("📺 Netflix", "https://www.netflix.com/title/81231974"),
    ]
    
    for icon, url in links:
        st.markdown(f'<a href="{url}" target="_blank" style="color: #f0e68c; text-decoration: none; display: block; margin: 5px 0;">{icon} {url.split("//")[-1].split("/")[0]}</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Кнопка "На главную" в сайдбаре
    if st.button("⬅️ Вернуться на главную", use_container_width=True, key="sidebar_back"):
        # Прямая ссылка в markdown
        st.markdown(f"""
        <div style="text-align: center; margin-top: 20px;">
            <a href="{MAIN_PAGE_URL}" target="_blank" 
               style="display: inline-block; padding: 10px 20px; background: #f0e68c; 
                      color: #0f0f1f; border-radius: 5px; text-decoration: none; font-weight: bold;">
            🏠 Открыть главную страницу
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- Информация внизу ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #888; padding: 20px;">
    <p>🦇 Система поиска новостей о Тим Бёртоне</p>
    <p>
        <a href="{MAIN_PAGE_URL}" target="_blank" style="color: #f0e68c; text-decoration: none;">
        🔗 Главная страница проекта
        </a>
    </p>
</div>
""", unsafe_allow_html=True)

# --- Дополнительная ссылка внизу для надежности ---
st.markdown(f"""
<div style="position: fixed; bottom: 10px; right: 10px; z-index: 1000;">
    <a href="{MAIN_PAGE_URL}" target="_blank" 
       style="background: #f0e68c; color: #0f0f1f; padding: 8px 15px; 
              border-radius: 20px; text-decoration: none; font-size: 12px;
              box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
       🏠 На главную
    </a>
</div>
""", unsafe_allow_html=True)
