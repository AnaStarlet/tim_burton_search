import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup
import re

# Настройка страницы
st.set_page_config(
    page_title="Тим Бёртон - Поиск новостей", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧛 Реальный поиск новостей: Тим Бёртон")
st.markdown("### Поиск актуальных новостей из реальных источников в интернете")

# ========== СЛОВАРЬ ПЕРЕВОДА ==========
TRANSLATION_DICT = {
    # Русские названия → Английские названия
    "витиркус": "wednesday",
    "уоднесдэй": "wednesday",
    "уэднесдэй": "wednesday",
    "вэнсдэй": "wednesday",
    "битлджус": "beetlejuice",
    "битлджуз": "beetlejuice",
    "битлджуси": "beetlejuice",
    "битлджуси": "beetlejuice",
    "тим бёртон": "tim burton",
    "тим бертон": "tim burton",
    "джонни депп": "johnny depp",
    "дженна ортега": "jenna ortega",
    "монака беллуччи": "monica bellucci",
    "монака беллучи": "monica bellucci",
    "винна райдер": "winona ryder",
    "винона райдер": "winona ryder",
    "сезон": "season",
    "фильм": "movie",
    "кино": "film",
    "новый": "new",
    "проект": "project",
    "выставка": "exhibition",
    "интервью": "interview",
    "нетфликс": "netflix",
    "голливуд": "hollywood"
}

def translate_query_to_english(query):
    """Переводит русский запрос в английский для поиска"""
    query_lower = query.lower()
    
    # Заменяем все известные русские слова
    for rus, eng in TRANSLATION_DICT.items():
        query_lower = query_lower.replace(rus, eng)
    
    # Убираем лишние пробелы
    query_lower = re.sub(r'\s+', ' ', query_lower).strip()
    
    return query_lower

# ========== БОКОВАЯ ПАНЕЛЬ ==========
with st.sidebar:
    st.title("🎬 Тим Бёртон")
    st.markdown("---")
    
    # Настройки поиска
    st.header("⚙️ Источники новостей")
    st.write("Выберите, где искать новости:")
    
    sources = {
        "BBC News": st.checkbox("BBC News", value=True),
        "The Guardian": st.checkbox("The Guardian", value=True),
        "Variety": st.checkbox("Variety", value=True),
        "Deadline": st.checkbox("Deadline Hollywood", value=True),
        "Hollywood Reporter": st.checkbox("Hollywood Reporter", value=True),
        "IndieWire": st.checkbox("IndieWire", value=True),
        "Google News": st.checkbox("Google News", value=True),
    }
    
    st.markdown("---")
    
    # Фильтры
    st.header("⏳ Фильтры")
    time_filter = st.selectbox(
        "Период поиска:",
        ["Последние 7 дней", "Последний месяц", "Последние 3 месяца", "Все время"],
        index=3  # По умолчанию "Все время"
    )
    
    # Автоматический перевод
    st.header("🌐 Перевод запросов")
    auto_translate = st.checkbox("Автоматически переводить на английский", value=True)
    st.caption("При включении: 'Витиркус 2' → 'Wednesday 2'")
    
    st.markdown("---")
    
    # Быстрый поиск с ПРАВИЛЬНЫМИ запросами
    st.header("🚀 Быстрый поиск")
    
    quick_queries = {
        "Уоднесдэй 2 сезон": "Wednesday season 2",
        "Битлджус 2": "Beetlejuice 2", 
        "Тим Бёртон": "Tim Burton",
        "Джонни Депп": "Johnny Depp",
        "Дженна Ортега": "Jenna Ortega",
        "Моника Беллуччи": "Monica Bellucci",
        "Выставка Бёртона": "Tim Burton exhibition",
        "Новые проекты": "Tim Burton new projects"
    }
    
    for rus_query, eng_query in quick_queries.items():
        if st.button(f"🔍 {rus_query}", key=f"quick_{rus_query}", use_container_width=True):
            st.session_state.search_query = rus_query
            st.session_state.translated_query = eng_query
            st.rerun()
    
    st.markdown("---")
    
    # Информация
    st.header("ℹ️ Как правильно искать")
    st.info("""
    **ВАЖНО: Ищите на английском!**
    
    Правильно:
    • `Wednesday season 2` ✅
    • `Beetlejuice 2` ✅
    • `Tim Burton` ✅
    
    Неправильно:
    • `Витиркус 2` ❌
    • `Уоднесдэй` ❌
    • `Тим Бёртон` ❌ (без перевода)
    
    Включите "Автоматический перевод"!
    """)

# ========== ФУНКЦИИ ПОИСКА ==========
def get_date_from_entry(entry):
    """Извлекает дату из новостной записи"""
    try:
        if hasattr(entry, 'published_parsed'):
            return datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'published'):
            # Пробуем распарсить дату
            date_str = entry.published
            for fmt in ["%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%dT%H:%M:%SZ", "%a, %d %b %Y"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
    except:
        pass
    return datetime.now()

def search_news_rss(url, source_name, query):
    """Поиск новостей в RSS ленте"""
    try:
        feed = feedparser.parse(url)
        results = []
        
        for entry in feed.entries:
            # Собираем весь текст для поиска
            search_text = f"{entry.title} {entry.get('summary', '')}".lower()
            
            # Проверяем каждое слово запроса
            query_words = query.lower().split()
            match_found = False
            
            # Ищем хотя бы одно слово из запроса
            for word in query_words:
                if len(word) > 3 and word in search_text:  # Только слова длиннее 3 букв
                    match_found = True
                    break
            
            if match_found:
                # Форматируем дату
                date_obj = get_date_from_entry(entry)
                date_str = date_obj.strftime("%d.%m.%Y")
                
                # Получаем описание
                summary = entry.get('summary', '')
                if not summary or len(summary) < 50:
                    summary = entry.title
                
                results.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': source_name,
                    'date': date_obj,
                    'date_str': date_str,
                    'summary': summary[:300] + "..." if len(summary) > 300 else summary,
                    'relevance': len([w for w in query_words if w in search_text])
                })
        
        return results[:20]  # Ограничиваем 20 результатами на источник
    
    except Exception as e:
        st.sidebar.warning(f"Ошибка в {source_name}")
        return []

def search_all_sources(query, enabled_sources):
    """Ищет новости по всем включенным источникам"""
    # RSS-ленты источников
    rss_feeds = {
        "BBC News": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
        "The Guardian": "https://www.theguardian.com/film/rss",
        "Variety": "https://variety.com/feed/",
        "Deadline": "https://deadline.com/feed/",
        "Hollywood Reporter": "https://www.hollywoodreporter.com/feed/",
        "IndieWire": "https://www.indiewire.com/feed/",
    }
    
    all_results = []
    progress_bar = st.progress(0)
    
    enabled_count = sum(1 for source, enabled in enabled_sources.items() if enabled)
    current_source = 0
    
    for source_name, url in rss_feeds.items():
        if enabled_sources.get(source_name, False):
            current_source += 1
            progress_bar.progress(current_source / enabled_count)
            
            with st.spinner(f"🔍 Ищем в {source_name}..."):
                results = search_news_rss(url, source_name, query)
                all_results.extend(results)
                time.sleep(0.3)
    
    progress_bar.empty()
    
    # Сортируем по релевантности и дате
    all_results.sort(key=lambda x: (-x['relevance'], -x['date'].timestamp()))
    
    # Убираем дубликаты
    seen_links = set()
    unique_results = []
    for result in all_results:
        if result['link'] not in seen_links:
            seen_links.add(result['link'])
            unique_results.append(result)
    
    return unique_results

# ========== ОСНОВНОЙ ИНТЕРФЕЙС ==========
# Поле поиска
col1, col2 = st.columns([3, 1])

with col1:
    st.header("🔍 Введите тему для поиска")
    
    # Инициализация session state
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'translated_query' not in st.session_state:
        st.session_state.translated_query = ""
    
    user_query = st.text_input(
        "", 
        value=st.session_state.search_query,
        placeholder="Например: Уоднесдэй 2, Битлджус 2, Тим Бёртон...",
        key="main_search_input"
    )

with col2:
    st.markdown("###")
    search_button = st.button("🔎 НАЧАТЬ ПОИСК", type="primary", use_container_width=True)

# Если нажата кнопка поиска
if search_button and user_query:
    st.session_state.search_query = user_query
    
    # Определяем запрос для поиска
    if auto_translate:
        search_query = translate_query_to_english(user_query)
        st.session_state.translated_query = search_query
    else:
        search_query = user_query.lower()
    
    # Показываем, что ищем
    if auto_translate and user_query.lower() != search_query:
        st.info(f"🔤 **Поисковый запрос:** '{user_query}' → '{search_query}'")
    
    with st.spinner(f"🔍 Ищем новости по запросу: '{search_query}'..."):
        results = search_all_sources(search_query, sources)
        
        if results:
            # Фильтруем по времени если нужно
            if time_filter != "Все время":
                cutoff_days = {
                    "Последние 7 дней": 7,
                    "Последний месяц": 30,
                    "Последние 3 месяца": 90
                }.get(time_filter, 365)
                
                cutoff_date = datetime.now() - timedelta(days=cutoff_days)
                results = [r for r in results if r['date'] >= cutoff_date]
            
            st.success(f"✅ НАЙДЕНО {len(results)} НОВОСТЕЙ!")
            
            # Группируем по источникам
            sources_found = {}
            for result in results:
                source = result['source']
                if source not in sources_found:
                    sources_found[source] = []
                sources_found[source].append(result)
            
            # Показываем результаты
            for source, source_results in sources_found.items():
                with st.expander(f"📰 {source} ({len(source_results)} новостей)", expanded=True):
                    for i, news in enumerate(source_results):
                        st.markdown(f"### {news['title']}")
                        st.caption(f"📅 {news['date_str']} | 🔗 [Открыть статью]({news['link']})")
                        st.write(news['summary'])
                        
                        if i < len(source_results) - 1:
                            st.markdown("---")
            
            # Статистика
            st.info(f"""
            **📊 СТАТИСТИКА:**
            • Всего новостей: **{len(results)}**
            • Источников: **{len(sources_found)}**
            • Самые свежие: **{results[0]['date_str'] if results else 'нет'}**
            • Период поиска: **{time_filter}**
            """)
            
        else:
            st.error("😞 НЕ НАЙДЕНО НОВОСТЕЙ ПО ЗАПРОСУ.")
            
            # Подсказки
            with st.expander("💡 КАК НАЙТИ НОВОСТИ?", expanded=True):
                st.markdown("""
                ### **ПРАВИЛЬНЫЕ ЗАПРОСЫ:**
                
                **Для Уоднесдэй:**
                • `Wednesday` ✅
                • `Wednesday season 2` ✅
                • `Wednesday Netflix` ✅
                • `Jenna Ortega Wednesday` ✅
                
                **Для Битлджуса:**
                • `Beetlejuice` ✅
                • `Beetlejuice 2` ✅
                • `Beetlejuice sequel` ✅
                • `Winona Ryder Beetlejuice` ✅
                
                **Для Тима Бёртона:**
                • `Tim Burton` ✅
                • `Tim Burton movie` ✅
                • `Tim Burton exhibition` ✅
                • `Tim Burton interview` ✅
                
                **НЕПРАВИЛЬНО:**
                • `Витиркус` ❌
                • `Уоднесдэй` ❌ (без перевода)
                • `Битлджус` ❌
                """)
                
                # Автоматически предлагаем правильный запрос
                if "витиркус" in user_query.lower() or "уоднесдэй" in user_query.lower():
                    st.warning("⚠️ **Вероятно, вы ищете 'Wednesday'**")
                    if st.button("🔍 Попробовать 'Wednesday season 2'"):
                        st.session_state.search_query = "Wednesday season 2"
                        st.rerun()
                
                elif "битлджус" in user_query.lower():
                    st.warning("⚠️ **Вероятно, вы ищете 'Beetlejuice'**")
                    if st.button("🔍 Попробовать 'Beetlejuice 2'"):
                        st.session_state.search_query = "Beetlejuice 2"
                        st.rerun()

# Если ничего не искали
else:
    st.markdown("---")
    
    # Примеры работающих запросов
    col_ex1, col_ex2 = st.columns(2)
    
    with col_ex1:
        st.subheader("🎯 **РАБОЧИЕ ЗАПРОСЫ:**")
        st.code("Wednesday season 2")
        st.code("Beetlejuice 2 release date")
        st.code("Tim Burton exhibition 2024")
        st.code("Johnny Depp Burton movie")
    
    with col_ex2:
        st.subheader("📰 **ЧТО НАЙДЕТСЯ:**")
        st.success("• Новости о втором сезоне Уоднесдэй")
        st.success("• Даты выхода Битлджус 2")
        st.success("• Интервью с Тимом Бёртоном")
        st.success("• Информация о новых проектах")

# Футер
st.markdown("---")
st.caption(f"🎬 РЕАЛЬНЫЙ ПОИСК НОВОСТЕЙ | Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')} | АВТОПЕРЕВОД ВКЛЮЧЕН: {'✅' if auto_translate else '❌'}")
