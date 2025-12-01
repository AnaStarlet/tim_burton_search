import streamlit as st
import requests
from urllib.parse import quote
import json

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
    .error-card {
        background-color: #2b2222;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff6b6b;
        margin: 20px 0;
    }
    .not-related-card {
        background-color: #22222b;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #4285f4;
        margin: 20px 0;
        text-align: center;
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
    }
    .back-btn {
        background: linear-gradient(45deg, #f0e68c, #d4af37);
        color: #0f0f1f !important;
        padding: 12px 24px;
        border-radius: 5px;
        font-weight: bold;
        text-decoration: none;
        display: inline-block;
        margin: 20px auto;
        border: none;
        cursor: pointer;
        text-align: center;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- Константы ---
MAIN_PAGE_URL = "https://quixotic-shrimp-ea9.notion.site/9aabb68bd7004965819318e32d8ff06e?v=2b4a0ca7844a80d6aa8a000c6a7e5272"

# --- Проверка темы запроса ---
def is_burton_related(query):
    """Проверяет, связан ли запрос с Тимом Бёртоном"""
    query_lower = query.lower()
    
    burton_keywords = [
        # Имена
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

# --- Статические данные (на случай ошибки API) ---
def get_static_burton_data():
    """Возвращает статические данные о Бёртоне"""
    return [
        {
            'title': 'Тим Бёртон и Джонни Депп: 30 лет сотрудничества',
            'snippet': 'От "Эдварда Руки-ножницы" до "Суини Тодда" - история творческого тандема длиной в три десятилетия.',
            'source': 'КиноПоиск',
            'date': '2024',
            'link': 'https://www.kinopoisk.ru/name/20414/'
        },
        {
            'title': 'Уэднесдэй 2 сезон: что известно',
            'snippet': 'Netflix работает над вторым сезоном сериала "Уэднесдэй" режиссера Тима Бёртона.',
            'source': 'Netflix News',
            'date': '2024',
            'link': 'https://www.netflix.com/title/81231974'
        },
        {
            'title': 'Битлджус 2: детали сиквела',
            'snippet': 'Майкл Китон возвращается в роли Битлджуса через 35 лет в сиквеле культового фильма.',
            'source': 'IMDb',
            'date': '2024',
            'link': 'https://www.imdb.com/title/tt0094721/'
        },
        {
            'title': 'Готический стиль Бёртона',
            'snippet': 'Уникальный визуальный язык режиссера: от черно-белой эстетики до кукольной анимации.',
            'source': 'Арт-обзор',
            'date': '2024',
            'link': 'https://ru.wikipedia.org/wiki/Бёртон,_Тим'
        }
    ]

# --- Поиск новостей (с резервным вариантом) ---
def search_burton_info(query):
    """Поиск информации о Бёртоне с резервными данными"""
    # Сначала проверяем тему
    if not is_burton_related(query):
        return None, "not_related"
    
    # Пробуем получить данные из API
    try:
        # Формируем URL для RSS Google News (бесплатный метод)
        search_url = f"https://news.google.com/rss/search?q={quote('Тим Бёртон ' + query)}&hl=ru&gl=RU&ceid=RU:ru"
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(search_url, timeout=5)
        
        if response.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            articles = []
            for item in root.findall('.//item')[:5]:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else '#'
                
                # Фильтруем только статьи про Бёртона
                if 'буртон' in title.lower() or 'burton' in title.lower():
                    import re
                    description = ''
                    if item.find('description') is not None:
                        desc_text = item.find('description').text or ''
                        description = re.sub('<[^<]+?>', '', desc_text)
                    
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else '2024'
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'snippet': description[:200] + '...' if len(description) > 200 else description,
                        'source': 'Google News',
                        'date': pub_date[:16]
                    })
            
            if articles:
                return articles, "success"
            else:
                # Если нет результатов в RSS, возвращаем статические данные
                return get_static_burton_data(), "static_data"
                
    except Exception:
        # При любой ошибке возвращаем статические данные
        return get_static_burton_data(), "static_data"
    
    return get_static_burton_data(), "static_data"

# === ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ===
st.markdown('<h1 class="main-title">🦇 Поиск информации о Тим Бёртоне</h1>', unsafe_allow_html=True)
st.write("Найдите информацию о фильмах, актерах и проектах Тима Бёртона")

# --- Быстрые запросы ---
st.header("🎬 Быстрые запросы")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Уэднесдэй", use_container_width=True):
        st.session_state.search_query = "Уэднесдэй"
with col2:
    if st.button("Битлджус 2", use_container_width=True):
        st.session_state.search_query = "Битлджус"
with col3:
    if st.button("Джонни Депп", use_container_width=True):
        st.session_state.search_query = "Джонни Депп"
with col4:
    if st.button("Готический стиль", use_container_width=True):
        st.session_state.search_query = "готический стиль"

# --- Поисковая строка ---
st.header("🔍 Поиск информации")

if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

search_query = st.text_input(
    "Введите запрос о Тим Бёртоне:",
    value=st.session_state.search_query,
    placeholder="Например: сотрудничество с Джонни Деппом, новые проекты...",
    label_visibility="collapsed"
)

# --- Обработка поиска ---
if st.button("🔎 Найти", type="primary", use_container_width=True):
    if not search_query:
        st.warning("Пожалуйста, введите запрос")
    else:
        st.session_state.search_query = search_query
        
        # Проверяем тему
        if not is_burton_related(search_query):
            # Запрос не по теме
            st.markdown(f"""
            <div class="not-related-card">
                <h3 style="color: #4285f4;">⚠️ Этот запрос не связан с Тимом Бёртоном</h3>
                <p>Вы искали: <strong>"{search_query}"</strong></p>
                <p>Эта система ищет только информацию о Тим Бёртоне и его творчестве.</p>
                
                <a href="https://www.google.com/search?q={quote(search_query)}" 
                   target="_blank" 
                   class="google-btn">
                🔍 Поиск в Google
                </a>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Запрос по теме - ищем информацию
            with st.spinner("🦇 Ищу информацию..."):
                articles, status = search_burton_info(search_query)
                
                if status == "not_related":
                    st.error("Запрос не связан с Тимом Бёртоном")
                elif articles:
                    if status == "static_data":
                        st.info("ℹ️ Используются данные из базы знаний")
                    
                    st.success(f"🎭 Найдено материалов: {len(articles)}")
                    
                    for article in articles:
                        with st.container():
                            st.markdown(f"""
                            <div class="news-card">
                                <h4 style="color: #f0e68c;">{article['title']}</h4>
                                <p style="color: #ccc; font-size: 0.9em;">
                                📰 <strong>{article['source']}</strong> | 📅 {article['date']}
                                </p>
                                <p style="color: #e0e0e0;">{article['snippet']}</p>
                                <a href="{article['link']}" target="_blank" 
                                   style="color: #ff6b6b; text-decoration: none; font-weight: bold;">
                                🔗 Читать подробнее
                                </a>
                            </div>
                            """, unsafe_allow_html=True)

# --- Информация о системе ---
with st.expander("ℹ️ О системе", expanded=False):
    st.markdown("""
    **Эта система ищет информацию о:**
    
    ✅ **Тим Бёртон:**
    - Все фильмы и проекты
    - Актеры и команда
    - Стиль и творчество
    - Выставки и события
    
    ✅ **Примеры запросов:**
    - Уэднесдэй 2 сезон
    - Битлджус 2 фильм
    - Джонни Депп сотрудничество
    - Дэнни Эльфман музыка
    - Готический стиль Бёртона
    
    
    """)

# --- ОДНА кнопка "Назад" внизу ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 20px;">
    <a href="{MAIN_PAGE_URL}" target="_blank" class="back-btn">
    ⬅️ Вернуться на главную страницу
    </a>
</div>
""", unsafe_allow_html=True)

# --- Футер ---
st.markdown("""
<div style='text-align: center; color: #888; padding: 10px; font-size: 0.9em;'>
    <p>🦇 Система поиска информации о Тим Бёртоне</p>
</div>
""", unsafe_allow_html=True)
