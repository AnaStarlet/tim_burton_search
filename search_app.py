import streamlit as st
import requests
from urllib.parse import quote
import json
import time

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
    .news-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(240, 230, 140, 0.2);
    }
    .search-button {
        background: linear-gradient(45deg, #f0e68c, #ff6b6b);
        color: #0f0f1f;
        font-weight: bold;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- Ваш API ключ Serper.dev ---
SERPER_API_KEY = "e9eac514f1cd4452b6f6a672b3c9cd2d"  # Ваш API ключ

# --- Альтернативный метод поиска через Bing News API ---
def search_bing_news(query, count=15):
    """Альтернативный поиск новостей (используем Bing News в случае проблем с Serper)"""
    try:
        # Создаем заголовки для имитации браузера
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # Формируем URL для поиска в Google News (публичный доступ)
        search_url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ru&gl=RU&ceid=RU:ru"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Парсим RSS
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            articles = []
            for item in root.findall('.//item')[:count]:
                title = item.find('title').text if item.find('title') is not None else 'Без названия'
                link = item.find('link').text if item.find('link') is not None else '#'
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else 'Дата неизвестна'
                source = 'Google News'
                
                # Получаем описание из содержимого
                description = ''
                if item.find('description') is not None:
                    desc_text = item.find('description').text or ''
                    # Очищаем HTML теги
                    import re
                    description = re.sub('<[^<]+?>', '', desc_text)
                
                articles.append({
                    'title': title,
                    'link': link,
                    'snippet': description[:200] + '...' if len(description) > 200 else description,
                    'source': source,
                    'date': pub_date
                })
            
            return articles, None
        else:
            return None, f"Ошибка при получении RSS: {response.status_code}"
            
    except Exception as e:
        return None, f"Ошибка: {str(e)}"

# --- Основная функция поиска ---
@st.cache_data(ttl=3600)  # Кэшируем на 1 час
def search_news(query, use_backup=True):
    """Главная функция поиска новостей"""
    # Сначала пробуем через Serper API
    if SERPER_API_KEY:
        try:
            url = "https://google.serper.dev/news"
            payload = json.dumps({"q": query, "gl": "ru", "hl": "ru", "tbs": "qdr:w", "num": 20})
            headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
            
            response = requests.post(url, headers=headers, data=payload, timeout=15)
            
            if response.status_code == 200:
                results = response.json().get("news", [])
                if results:
                    return results, None
                else:
                    if use_backup:
                        return search_bing_news(query)
                    else:
                        return [], "Нет результатов через Serper API"
            else:
                # Если Serper вернул ошибку, используем альтернативный метод
                if use_backup:
                    st.warning(f"Serper API вернул ошибку {response.status_code}. Использую альтернативный поиск...")
                    return search_bing_news(query)
                else:
                    return None, f"Ошибка Serper API: {response.status_code}"
                    
        except Exception as serper_error:
            if use_backup:
                st.warning(f"Ошибка Serper: {serper_error}. Переключаюсь на альтернативный поиск...")
                return search_bing_news(query)
            else:
                return None, f"Ошибка Serper API: {serper_error}"
    else:
        # Если нет API ключа, сразу используем альтернативный метод
        return search_bing_news(query)

# === ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ===
st.markdown('<h1 class="main-title">🦇 Дайджест новостей вселенной Тима Бёртона</h1>', unsafe_allow_html=True)
st.write("Поиск самых актуальных новостей о Тим Бёртоне, его фильмах, проектах и команде.")
st.divider()

# --- Боковая панель с информацией ---
with st.sidebar:
    st.markdown("### 📋 Быстрые запросы")
    
    quick_queries = [
        "🎬 Уэднесдэй 2 сезон",
        "👻 Битлджус 2 фильм",
        "🎭 Джонни Депп Бёртон",
        "🎵 Дэнни Эльфман",
        "🏛️ Выставка Бёртона",
        "🎨 Готический стиль",
        "📅 Новые проекты 2024",
        "🎥 Фильмография Бёртона"
    ]
    
    for query in quick_queries:
        if st.button(query, use_container_width=True):
            st.session_state.search_query = query.replace("🎬 ", "").replace("👻 ", "").replace("🎭 ", "").replace("🎵 ", "").replace("🏛️ ", "").replace("🎨 ", "").replace("📅 ", "").replace("🎥 ", "")
    
    st.markdown("---")
    st.markdown("### ℹ️ О системе")
    st.markdown("""
    **Поиск по:**
    - 🎬 Фильмы Бёртона
    - 🎭 Актеры команды
    - 🏛️ События и выставки
    - 🎨 Стиль и творчество
    - 📅 Актуальные новости
    
    **Обновление:** Каждый час
    """)
    
    # Кнопка назад
    if st.button("⬅️ На главную", use_container_width=True, type="secondary"):
        st.markdown('<meta http-equiv="refresh" content="0; url=https://quixotic-shrimp-ea9.notion.site/9aabb68bd7004965819318e32d8ff06e?v=2b4a0ca7844a80d6aa8a000c6a7e5272">', unsafe_allow_html=True)

# --- Раздел "Автоматические новости" ---
st.header("🔥 Автоматический поиск новостей")

auto_queries = [
    "Тим Бёртон новости 2024",
    "Wednesday season 2 Netflix",
    "Beetlejuice 2 release date",
    "Tim Burton exhibition"
]

selected_auto = st.selectbox(
    "Выберите тему для автоматического поиска:",
    auto_queries,
    index=0
)

if st.button("🔍 Найти по выбранной теме", type="primary", use_container_width=True, key="auto_search"):
    with st.spinner(f"🦇 Ищу новости по теме: {selected_auto}..."):
        articles, error = search_news(selected_auto)
        
        if error:
            st.error(f"Ошибка: {error}")
            st.info("Попробуйте использовать поиск вручную ниже")
        elif articles:
            st.success(f"🎭 Найдено новостей: {len(articles)}")
            
            for idx, article in enumerate(articles):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        <div class="news-card">
                            <h4 style="color: #f0e68c; margin: 0;">{article['title']}</h4>
                            <p style="color: #ccc; font-size: 0.85em; margin: 5px 0;">
                            📰 {article.get('source', 'Неизвестный источник')} | 
                            📅 {article.get('date', 'Дата не указана')}
                            </p>
                            <p style="color: #e0e0e0; margin: 10px 0;">{article.get('snippet', '')}</p>
                            <a href="{article['link']}" target="_blank" style="color: #ff6b6b; text-decoration: none; font-weight: bold;">
                            🔗 Открыть статью
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if st.button("📋 Копировать", key=f"copy_{idx}", use_container_width=True):
                            st.write(f"Скопировано: {article['title'][:50]}...")
        else:
            st.info("📭 Новостей не найдено. Попробуйте другой запрос.")

# --- Раздел "Ручной поиск" ---
st.header("🔎 Персональный поиск")
st.write("Введите точный запрос для поиска:")

# Инициализация состояния
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# Поле ввода с возможностью выбора из быстрых запросов
col_input, col_btn = st.columns([3, 1])
with col_input:
    manual_query = st.text_input(
        "Ваш запрос:",
        value=st.session_state.search_query,
        placeholder="Например: Тим Бёртон интервью 2024, выставка работ Бёртона...",
        label_visibility="collapsed"
    )

with col_btn:
    search_clicked = st.button("🔍 Поиск", type="primary", use_container_width=True)

if search_clicked and manual_query:
    st.session_state.search_query = manual_query
    with st.spinner(f"🦇 Ищу по запросу: {manual_query}..."):
        time.sleep(1)  # Небольшая задержка для UX
        
        articles, error = search_news(manual_query)
        
        if error:
            st.error(f"Ошибка поиска: {error}")
            
            # Предлагаем простой поиск через Google
            google_url = f"https://www.google.com/search?q={quote(manual_query)}"
            st.markdown(f"""
            <div style='background-color: #2b2b2b; padding: 15px; border-radius: 10px; margin: 20px 0;'>
                <h4 style='color: #f0e68c;'>💡 Попробуйте поискать напрямую в Google:</h4>
                <a href="{google_url}" target="_blank" style="color: #ff6b6b; text-decoration: none; font-size: 16px;">
                🔍 Поиск в Google: "{manual_query}"
                </a>
            </div>
            """, unsafe_allow_html=True)
            
        elif articles:
            st.success(f"🎭 Найдено результатов: {len(articles)}")
            
            # Показать первые 10 результатов
            for idx, article in enumerate(articles[:10]):
                with st.expander(f"{idx+1}. {article['title'][:80]}...", expanded=idx==0):
                    st.markdown(f"""
                    **📰 Источник:** {article.get('source', 'Неизвестно')}  
                    **📅 Дата:** {article.get('date', 'Не указана')}  
                    
                    **Описание:**  
                    {article.get('snippet', 'Описание отсутствует')}
                    
                    [🔗 Открыть полную статью]({article['link']})
                    """)
        else:
            st.info("📭 По вашему запросу ничего не найдено.")
            
            # Предлагаем варианты
            st.markdown("### 💡 Попробуйте эти запросы:")
            suggest_cols = st.columns(4)
            suggestions = [
                ("🎬", "Уэднесдэй"),
                ("👻", "Битлджус"),
                ("🎭", "Джонни Депп"),
                ("🏛️", "Бёртон выставка")
            ]
            
            for i, (icon, query) in enumerate(suggestions):
                with suggest_cols[i]:
                    if st.button(f"{icon} {query}", use_container_width=True):
                        st.session_state.search_query = f"Тим Бёртон {query}"
                        st.rerun()

# --- Информация о статусе API ---
with st.expander("ℹ️ Статус системы"):
    if SERPER_API_KEY:
        st.success("✅ API ключ Serper настроен")
        st.code(f"Ключ: {SERPER_API_KEY[:10]}...{SERPER_API_KEY[-6:]}", language="text")
    else:
        st.warning("⚠️ API ключ Serper не настроен")
        st.info("Используется альтернативный метод поиска")
    
    st.markdown("""
    **Методы поиска:**
    1. **Serper.dev API** (основной) - быстрый и точный
    2. **Альтернативный RSS** (резервный) - если основной не работает
    
    **Обновление данных:** Каждый час
    **Язык поиска:** Русский
    **Период:** Последняя неделя
    """)

# --- Футер ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px; font-size: 0.9em;'>
    <p>🦇 Система поиска новостей вселенной Тима Бёртона • Использует открытые источники новостей</p>
    <p><small>Информация обновляется автоматически • © 2024</small></p>
</div>
""", unsafe_allow_html=True)
