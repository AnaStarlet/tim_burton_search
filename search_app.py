import streamlit as st
import requests
from urllib.parse import quote
import json
import re
import time

# --- Настройки страницы ---
st.set_page_config(page_title="Новости Вселенной Тима Бёртона", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0f0f1f; }
    .main-title { color: #f0e68c; text-align: center; margin-bottom: 30px; font-family: 'Courier New', monospace; }
    .news-card {
        background-color: #1a1a2e;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #f0e68c;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(240, 230, 140, 0.1);
    }
    .static-news {
        background-color: #2b2b2b;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff6b6b;
        margin: 10px 0;
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
        text-align: center;
        transition: transform 0.3s;
    }
    .google-btn:hover {
        transform: scale(1.05);
    }
    .back-btn {
        background: linear-gradient(45deg, #f0e68c, #d4af37);
        color: #0f0f1f !important;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        text-decoration: none;
        display: inline-block;
        margin: 10px 0;
        border: none;
        cursor: pointer;
    }
    .warning-box {
        background-color: #332222;
        color: #ff9999;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ff6b6b;
        margin: 15px 0;
    }
    .success-box {
        background-color: #223322;
        color: #99ff99;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #34a853;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Константы ---
MAIN_PAGE_URL = "https://quixotic-shrimp-ea9.notion.site/9aabb68bd7004965819318e32d8ff06e?v=2b4a0ca7844a80d6aa8a000c6a7e5272"

# --- База знаний о Бёртоне ---
BURTON_KNOWLEDGE = {
    "фильмы": [
        "Уэднесдэй (Wednesday) - сериал Netflix",
        "Битлджус (Beetlejuice) - 1988, продолжение в 2024",
        "Эдвард Руки-ножницы (Edward Scissorhands) - 1990",
        "Кошмар перед Рождеством (The Nightmare Before Christmas) - 1993",
        "Сонная Лощина (Sleepy Hollow) - 1999",
        "Суини Тодд (Sweeney Todd) - 2007",
        "Алиса в Стране чудес (Alice in Wonderland) - 2010",
        "Темные тени (Dark Shadows) - 2012",
        "Франкенвини (Frankenweenie) - 2012",
        "Дом странных детей (Miss Peregrine's Home for Peculiar Children) - 2016",
        "Дамбо (Dumbo) - 2019"
    ],
    "актеры": [
        "Джонни Депп (Johnny Depp) - многократный сотрудник",
        "Хелена Бонем Картер (Helena Bonham Carter) - актриса и бывшая партнер",
        "Майкл Китон (Michael Keaton) - Битлджус",
        "Вайнона Райдер (Winona Ryder) - Эдвард Руки-ножницы, Дракула",
        "Лиза Мэри (Lisa Marie) - актриса и бывшая муза",
        "Дэнни ДеВито (Danny DeVito) - Бэтмен возвращается",
        "Кристофер Ли (Christopher Lee) - несколько фильмов",
        "Ева Грин (Eva Green) - Темные тени, Дом странных детей"
    ],
    "проекты": [
        "Уэднесдэй 2 сезон - в разработке (2024)",
        "Битлджус 2 - ожидается в 2024",
        "Новый анимационный проект - в планах",
        "Сериал по мотивам ранних работ - обсуждается"
    ],
    "команда": [
        "Дэнни Эльфман (Danny Elfman) - постоянный композитор",
        "Колин Этвуд (Colleen Atwood) - художник по костюмам",
        "Алекс Макдауэлл (Alex McDowell) - художник-постановщик"
    ],
    "стиль": [
        "Готическая эстетика",
        "Черно-белая цветовая гамма",
        "Полосы и узоры",
        "Кукольная анимация (stop-motion)",
        "Темный юмор",
        "Винтажные элементы"
    ]
}

# --- Проверка темы ---
def is_burton_related(query):
    """Проверяет, связан ли запрос с Тимом Бёртоном"""
    query_lower = query.lower()
    
    burton_keywords = [
        'буртон', 'burton', 'тим', 'tim', 'бёртон',
        'уэднесдэй', 'wednesday', 'уеднесдей', 'венсдей',
        'битлджус', 'beetlejuice', 'битлджуис',
        'эдвард', 'edward', 'ножницы', 'scissorhands',
        'кошмар', 'nightmare', 'рождество', 'christmas',
        'сонная', 'sleepy', 'лощина', 'hollow',
        'суини', 'sweeney', 'тодд', 'todd',
        'чарли', 'charlie', 'шоколад', 'chocolate',
        'алиса', 'alice', 'страна', 'wonderland',
        'франкенвини', 'frankenweenie', 'дом странных',
        'дамбо', 'dumbo', 'темные тени', 'dark shadows',
        'депп', 'depp', 'джонни', 'johnny',
        'хелена', 'helena', 'бонем', 'bonham',
        'вайнона', 'winona', 'райдер', 'ryder',
        'майкл', 'michael', 'китон', 'keaton',
        'лиза', 'lisa', 'мэри', 'mary',
        'эльфман', 'elfman', 'дэнни', 'danny',
        'режиссер', 'режиссёр', 'director',
        'готика', 'готический', 'gothic',
        'анимация', 'animation', 'кукольный',
        'стиль', 'style', 'выставка', 'exhibition',
        'проект', 'project', 'фильм', 'movie',
        'кино', 'cinema', 'сериал', 'series'
    ]
    
    return any(keyword in query_lower for keyword in burton_keywords)

# --- Получение статичных новостей ---
def get_static_news_by_topic(query):
    """Возвращает релевантные статичные новости по теме"""
    query_lower = query.lower()
    
    # Более умный подбор новостей по теме
    news_items = []
    
    if any(word in query_lower for word in ['уэднесдэй', 'wednesday', 'сериал', 'netflix']):
        news_items.extend([
            {
                'title': 'Уэднесдэй 2 сезон подтвержден',
                'snippet': 'Netflix официально объявил о работе над вторым сезоном сериала "Уэднесдэй".',
                'source': 'Netflix',
                'date': '2024',
                'link': 'https://www.netflix.com/title/81231974',
                'type': 'Сериал'
            },
            {
                'title': 'Дженна Ортега вернется в роли Уэднесдэй',
                'snippet': 'Актриса подтвердила свое участие во втором сезоне культового сериала.',
                'source': 'Variety',
                'date': '2024',
                'link': 'https://variety.com',
                'type': 'Кастинг'
            }
        ])
    
    if any(word in query_lower for word in ['битлджус', 'beetlejuice', 'битлджуис']):
        news_items.extend([
            {
                'title': 'Битлджус 2: съемки завершены',
                'snippet': 'Продолжение культового фильма с Майклом Китоном и Дженной Ортегой готово к выходу.',
                'source': 'Warner Bros.',
                'date': '2024',
                'link': 'https://www.warnerbros.com',
                'type': 'Фильм'
            },
            {
                'title': 'Майкл Китон о возвращении в роли Битлджуса',
                'snippet': 'Актер поделился впечатлениями от съемок в сиквеле через 35 лет.',
                'source': 'Hollywood Reporter',
                'date': '2024',
                'link': 'https://www.hollywoodreporter.com',
                'type': 'Интервью'
            }
        ])
    
    if any(word in query_lower for word in ['депп', 'depp', 'джонни']):
        news_items.extend([
            {
                'title': 'Джонни Депп и Тим Бёртон: история сотрудничества',
                'snippet': 'От "Эдварда Руки-ножницы" до "Суини Тодда" - 30 лет творческого тандема.',
                'source': 'КиноПоиск',
                'date': '2024',
                'link': 'https://www.kinopoisk.ru/name/20414/',
                'type': 'Статья'
            }
        ])
    
    if any(word in query_lower for word in ['проект', 'project', 'новый', 'будущий']):
        news_items.extend([
            {
                'title': 'Новые проекты Тим Бёртона',
                'snippet': 'Режиссер работает над несколькими анимационными и игровыми проектами.',
                'source': 'Deadline',
                'date': '2024',
                'link': 'https://deadline.com',
                'type': 'Новости'
            },
            {
                'title': 'Тим Бёртон планирует возвращение к stop-motion',
                'snippet': 'Режиссер хочет снять новый анимационный фильм в своей фирменной технике.',
                'source': 'Animation Magazine',
                'date': '2024',
                'link': 'https://www.animationmagazine.net',
                'type': 'Анимация'
            }
        ])
    
    # Если нет специфичных новостей, возвращаем общие
    if not news_items:
        news_items = [
            {
                'title': 'Тим Бёртон: готический гений кино',
                'snippet': 'Обзор карьеры одного из самых узнаваемых режиссеров современности.',
                'source': 'Википедия',
                'date': '2024',
                'link': 'https://ru.wikipedia.org/wiki/Бёртон,_Тим',
                'type': 'Биография'
            },
            {
                'title': 'Выставка работ Бёртона в Лос-Анджелесе',
                'snippet': 'Экспозиция включает эскизы, костюмы и реквизит из фильмов режиссера.',
                'source': 'LACMA',
                'date': '2024',
                'link': 'https://www.lacma.org',
                'type': 'Выставка'
            }
        ]
    
    return news_items

# --- Поиск новостей с улучшенной обработкой ---
def search_news_safe(query, timeout=8):
    """Безопасный поиск новостей"""
    try:
        # Пробуем получить реальные новости с увеличенным таймаутом
        search_terms = f"Тим Бёртон {query}"
        search_url = f"https://news.google.com/rss/search?q={quote(search_terms)}&hl=ru&gl=RU&ceid=RU:ru"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(search_url, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            articles = []
            for item in root.findall('.//item')[:8]:  # Берем меньше результатов для скорости
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else '#'
                
                # Быстрая проверка на релевантность
                if 'буртон' in title.lower() or 'burton' in title.lower():
                    description = ''
                    if item.find('description') is not None:
                        desc_text = item.find('description').text or ''
                        description = re.sub('<[^<]+?>', '', desc_text)[:150]
                    
                    pub_date = item.find('pubDate').text[:16] if item.find('pubDate') is not None else '2024'
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'snippet': description,
                        'source': 'Google News',
                        'date': pub_date,
                        'type': 'Новость'
                    })
            
            if articles:
                return articles, True, "Реальные новости"
            else:
                # Если нет результатов в RSS, используем статические
                return get_static_news_by_topic(query), False, "Используются данные из базы знаний"
                
    except requests.exceptions.Timeout:
        return get_static_news_by_topic(query), False, "Таймаут соединения. Используются данные из базы знаний"
    except Exception as e:
        return get_static_news_by_topic(query), False, f"Используются данные из базы знаний"
    
    return get_static_news_by_topic(query), False, "Используются данные из базы знаний"

# === ИНТЕРФЕЙС ===
st.markdown('<h1 class="main-title">🦇 Тим Бёртон: База знаний и новости</h1>', unsafe_allow_html=True)
st.write("Поиск информации о творчестве, фильмах и проектах Тима Бёртона")

# --- Быстрые кнопки ---
st.markdown("### 🚀 Быстрый доступ")
cols = st.columns(5)
with cols[0]:
    if st.button("🎬 Фильмы", use_container_width=True):
        st.session_state.search_query = "фильмы"
with cols[1]:
    if st.button("🎭 Актеры", use_container_width=True):
        st.session_state.search_query = "актеры"
with cols[2]:
    if st.button("📺 Уэднесдэй", use_container_width=True):
        st.session_state.search_query = "Уэднесдэй"
with cols[3]:
    if st.button("👻 Битлджус", use_container_width=True):
        st.session_state.search_query = "Битлджус"
with cols[4]:
    if st.button("🎨 Проекты", use_container_width=True):
        st.session_state.search_query = "новые проекты"

# --- Поисковая строка ---
st.markdown("### 🔍 Поиск информации")

if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

search_query = st.text_input(
    "Введите запрос о Тим Бёртоне:",
    value=st.session_state.search_query,
    placeholder="Например: готический стиль, Дэнни Эльфман, выставка...",
    label_visibility="collapsed"
)

# Кнопки действий
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    search_clicked = st.button("🔎 Найти информацию", type="primary", use_container_width=True)
with col2:
    if st.button("🏠 На главную", use_container_width=True):
        # Прямая ссылка
        st.markdown(f'<a href="{MAIN_PAGE_URL}" target="_blank" style="display: none;">Главная</a>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="success-box">
            <p>📎 Ссылка на главную страницу:</p>
            <a href="{MAIN_PAGE_URL}" target="_blank" class="back-btn">
            ⬅️ Открыть главную
            </a>
        </div>
        """, unsafe_allow_html=True)
with col3:
    if st.button("ℹ️ О системе", use_container_width=True):
        st.session_state.show_info = True

# --- Обработка поиска ---
if search_clicked and search_query:
    if not is_burton_related(search_query):
        st.markdown(f"""
        <div class="warning-box">
            <h4>⚠️ Запрос не связан с Тимом Бёртоном</h4>
            <p>Вы искали: <strong>"{search_query}"</strong></p>
            <p>Эта система содержит информацию только о творчестве Тима Бёртона.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Одна ссылка на Google
        google_url = f"https://www.google.com/search?q={quote(search_query)}"
        st.markdown(f"""
        <div style="text-align: center; margin: 25px 0;">
            <a href="{google_url}" target="_blank" class="google-btn">
            🔍 Поиск в Google
            </a>
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.spinner("🦇 Ищу информацию..."):
            # Небольшая задержка для UX
            time.sleep(0.5)
            
            articles, is_real, message = search_news_safe(search_query, timeout=10)
            
            # Показываем информацию о источнике данных
            if message:
                st.info(f"📋 {message}")
            
            if articles:
                st.success(f"📚 Найдено материалов: {len(articles)}")
                
                # Показываем информацию из базы знаний для некоторых запросов
                query_lower = search_query.lower()
                for category, items in BURTON_KNOWLEDGE.items():
                    if category in query_lower:
                        with st.expander(f"📖 Информация из базы знаний: {category.capitalize()}", expanded=True):
                            for item in items[:5]:  # Показываем первые 5 пунктов
                                st.write(f"• {item}")
                
                # Показываем новости/статьи
                st.markdown("### 📰 Материалы по теме:")
                for article in articles:
                    with st.container():
                        st.markdown(f"""
                        <div class="news-card">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <h4 style="color: #f0e68c; margin: 0; flex: 1;">{article['title']}</h4>
                                <span style="background: #444; color: #ccc; padding: 3px 8px; border-radius: 10px; font-size: 0.8em;">
                                    {article.get('type', 'Статья')}
                                </span>
                            </div>
                            <p style="color: #aaa; font-size: 0.9em; margin: 5px 0;">
                                📰 <strong>{article['source']}</strong> | 📅 {article['date']}
                            </p>
                            <p style="color: #e0e0e0; margin: 10px 0;">{article['snippet']}</p>
                            <a href="{article['link']}" target="_blank" 
                               style="color: #ff6b6b; text-decoration: none; font-weight: bold;">
                            🔗 Открыть источник
                            </a>
                        </div>
                        """, unsafe_allow_html=True)

# --- Информация о системе ---
if st.session_state.get('show_info', False):
    st.markdown("### ℹ️ О системе поиска")
    st.markdown("""
    **База знаний содержит информацию о:**
    
    🎬 **Фильмы:** Полная фильмография с описаниями  
    🎭 **Актеры:** Постоянные участники команды Бёртона  
    📺 **Проекты:** Текущие и будущие работы  
    🎨 **Стиль:** Особенности визуального языка  
    🎵 **Команда:** Композиторы, художники, сценаристы  
    
    **Источники данных:**
    1. База знаний системы (основной источник)
    2. Новостные агрегаторы (дополнительно)
    3. Проверенные ресурсы о кино
    
    **Примечание:** При проблемах с интернет-соединением система использует локальную базу знаний.
    """)
    if st.button("Скрыть информацию", key="hide_info"):
        st.session_state.show_info = False

# --- Сайдбар ---
with st.sidebar:
    st.markdown("### 🦇 Навигация")
    
    # Категории базы знаний
    st.markdown("**База знаний:**")
    for category in BURTON_KNOWLEDGE.keys():
        if st.button(f"📁 {category.capitalize()}", key=f"cat_{category}"):
            st.session_state.search_query = category
            st.rerun()
    
    st.markdown("---")
    st.markdown("**🔗 Полезные ссылки:**")
    
    links = [
        ("📖 Википедия", "https://ru.wikipedia.org/wiki/Бёртон,_Тим"),
        ("🎬 IMDb", "https://www.imdb.com/name/nm0000318/"),
        ("📺 Netflix", "https://www.netflix.com/title/81231974"),
        ("🎵 Danny Elfman", "https://www.dannyelfman.com/"),
    ]
    
    for icon, url in links:
        st.markdown(f'<a href="{url}" target="_blank" style="color: #f0e68c; text-decoration: none; display: block; margin: 8px 0; padding: 5px 10px; background: #222; border-radius: 5px;">{icon} {url.split("//")[-1].split("/")[0]}</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Кнопка на главную в сайдбаре
    st.markdown(f"""
    <div style="text-align: center; margin-top: 20px;">
        <a href="{MAIN_PAGE_URL}" target="_blank" 
           style="display: inline-block; padding: 10px 20px; background: linear-gradient(45deg, #f0e68c, #d4af37); 
                  color: #0f0f1f; border-radius: 5px; text-decoration: none; font-weight: bold; font-size: 14px;">
        🏠 Открыть главную страницу
        </a>
    </div>
    """, unsafe_allow_html=True)

# --- Футер ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #888; padding: 20px; font-size: 0.9em;">
    <p>🦇 Система базы знаний о Тим Бёртоне • Обновляется регулярно</p>
    <p>
        <a href="{MAIN_PAGE_URL}" target="_blank" style="color: #f0e68c; text-decoration: none; font-weight: bold;">
        🔗 Перейти на главную страницу проекта
        </a>
    </p>
</div>
""", unsafe_allow_html=True)
