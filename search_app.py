import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup

# Настройка страницы
st.set_page_config(
    page_title="Тим Бёртон - Поиск новостей", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧛 Реальный поиск новостей: Тим Бёртон")
st.markdown("### Поиск актуальных новостей из реальных источников в интернете")

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
        "Entertainment Weekly": st.checkbox("Entertainment Weekly", value=False)
    }
    
    st.markdown("---")
    
    # Фильтры
    st.header("⏳ Фильтры")
    time_filter = st.selectbox(
        "Показывать новости за:",
        ["Последние 7 дней", "Последний месяц", "Последние 3 месяца", "Последние 6 месяцев", "Все время"],
        index=0
    )
    
    # ВСЕГДА МАКСИМУМ
    st.info("ℹ️ Всегда показывается максимальное количество найденных новостей")
    
    st.markdown("---")
    
    # Быстрый поиск
    st.header("🚀 Быстрый поиск")
    st.write("Нажмите для быстрого поиска:")
    
    quick_queries = [
        "Wednesday season 2",
        "Beetlejuice 2",
        "Tim Burton",
        "Johnny Depp",
        "Monica Bellucci",
        "Burton exhibition",
        "New projects 2024",
        "Netflix Wednesday",
        "Jenna Ortega",
        "Winona Ryder"
    ]
    
    # Показываем кнопки в 2 колонки
    cols = st.columns(2)
    for idx, query in enumerate(quick_queries):
        col = cols[idx % 2]
        with col:
            if st.button(f"🔍 {query}", key=f"quick_{query}", use_container_width=True):
                st.session_state.search_query = query
                st.rerun()
    
    st.markdown("---")
    
    # Информация
    st.header("ℹ️ О поиске")
    st.info("""
    **Это реальный поиск новостей!**
    
    Приложение ищет в RSS-лентах:
    • BBC, Guardian, Variety
    • Deadline, Hollywood Reporter
    • Google News
    
    Все новости — реальные статьи
    со ссылками на источники.
    """)

# ========== ФУНКЦИИ ПОИСКА НОВОСТЕЙ ==========
def get_date_from_entry(entry):
    """Извлекает дату из новостной записи"""
    try:
        if hasattr(entry, 'published_parsed'):
            return datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed'):
            return datetime(*entry.updated_parsed[:6])
        elif hasattr(entry, 'published'):
            # Пробуем разные форматы дат
            date_str = entry.published
            formats = [
                "%a, %d %b %Y %H:%M:%S %Z",
                "%a, %d %b %Y %H:%M:%S %z",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S"
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
    except:
        pass
    return datetime.now()

def filter_by_time(news_list, time_period):
    """Фильтрует новости по времени"""
    now = datetime.now()
    
    if time_period == "Последние 7 дней":
        cutoff = now - timedelta(days=7)
    elif time_period == "Последний месяц":
        cutoff = now - timedelta(days=30)
    elif time_period == "Последние 3 месяца":
        cutoff = now - timedelta(days=90)
    elif time_period == "Последние 6 месяцев":
        cutoff = now - timedelta(days=180)
    else:
        return news_list
    
    return [news for news in news_list if news['date'] >= cutoff]

def search_bbc_news(query):
    """Поиск новостей на BBC"""
    try:
        url = "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"
        feed = feedparser.parse(url)
        
        results = []
        for entry in feed.entries:
            content = f"{entry.title} {entry.get('summary', '')}".lower()
            if query.lower() in content:
                results.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': 'BBC News',
                    'date': get_date_from_entry(entry),
                    'summary': entry.get('summary', '')[:250] + "..." if len(entry.get('summary', '')) > 250 else entry.get('summary', ''),
                    'full_text': entry.get('summary', '')
                })
        return results
    except Exception as e:
        return []

def search_guardian_news(query):
    """Поиск новостей в The Guardian"""
    try:
        url = "https://www.theguardian.com/film/rss"
        feed = feedparser.parse(url)
        
        results = []
        for entry in feed.entries:
            content = f"{entry.title} {entry.get('summary', '')}".lower()
            if query.lower() in content:
                try:
                    response = requests.get(entry.link, timeout=5)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Ищем основной текст статьи в The Guardian
                    article_body = soup.find('div', {'data-gu-name': 'body'})
                    if not article_body:
                        article_body = soup.find('div', class_='article-body')
                    if not article_body:
                        article_body = soup.find('article')
                    
                    full_text = article_body.get_text()[:500] + "..." if article_body else entry.get('summary', '')[:300] + "..."
                except:
                    full_text = entry.get('summary', '')[:300] + "..."
                
                results.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': 'The Guardian',
                    'date': get_date_from_entry(entry),
                    'summary': entry.get('summary', '')[:200] + "..." if len(entry.get('summary', '')) > 200 else entry.get('summary', ''),
                    'full_text': full_text
                })
        return results
    except Exception as e:
        return []

def search_variety_news(query):
    """Поиск новостей в Variety"""
    try:
        url = "https://variety.com/feed/"
        feed = feedparser.parse(url)
        
        results = []
        for entry in feed.entries:
            content = f"{entry.title} {entry.get('summary', '')}".lower()
            if query.lower() in content:
                results.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': 'Variety',
                    'date': get_date_from_entry(entry),
                    'summary': entry.get('summary', '')[:250] + "..." if len(entry.get('summary', '')) > 250 else entry.get('summary', ''),
                    'full_text': entry.get('summary', '')
                })
        return results
    except:
        return []

def search_deadline_news(query):
    """Поиск новостей в Deadline"""
    try:
        url = "https://deadline.com/feed/"
        feed = feedparser.parse(url)
        
        results = []
        for entry in feed.entries:
            content = f"{entry.title} {entry.get('summary', '')}".lower()
            if query.lower() in content:
                results.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': 'Deadline Hollywood',
                    'date': get_date_from_entry(entry),
                    'summary': entry.get('summary', '')[:250] + "..." if len(entry.get('summary', '')) > 250 else entry.get('summary', ''),
                    'full_text': entry.get('summary', '')
                })
        return results
    except:
        return []

def search_hollywood_reporter(query):
    """Поиск новостей в Hollywood Reporter"""
    try:
        url = "https://www.hollywoodreporter.com/feed/"
        feed = feedparser.parse(url)
        
        results = []
        for entry in feed.entries:
            content = f"{entry.title} {entry.get('summary', '')}".lower()
            if query.lower() in content:
                results.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': 'Hollywood Reporter',
                    'date': get_date_from_entry(entry),
                    'summary': entry.get('summary', '')[:250] + "..." if len(entry.get('summary', '')) > 250 else entry.get('summary', ''),
                    'full_text': entry.get('summary', '')
                })
        return results
    except:
        return []

def search_indiewire(query):
    """Поиск новостей в IndieWire"""
    try:
        url = "https://www.indiewire.com/feed/"
        feed = feedparser.parse(url)
        
        results = []
        for entry in feed.entries:
            content = f"{entry.title} {entry.get('summary', '')}".lower()
            if query.lower() in content:
                results.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': 'IndieWire',
                    'date': get_date_from_entry(entry),
                    'summary': entry.get('summary', '')[:250] + "..." if len(entry.get('summary', '')) > 250 else entry.get('summary', ''),
                    'full_text': entry.get('summary', '')
                })
        return results
    except:
        return []

def search_google_news(query):
    """Поиск через Google News RSS"""
    try:
        search_query = query.replace(' ', '+')
        url = f"https://news.google.com/rss/search?q={search_query}+film+movie+Hollywood&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(url)
        
        results = []
        for entry in feed.entries:
            results.append({
                'title': entry.title,
                'link': entry.link,
                'source': entry.source.title if hasattr(entry, 'source') else 'Google News',
                'date': get_date_from_entry(entry),
                'summary': entry.title[:150] + "..." if len(entry.title) > 150 else entry.title,
                'full_text': entry.title
            })
        return results
    except:
        return []

def search_all_news(query, enabled_sources):
    """Ищет новости по всем выбранным источникам - ВСЕГДА МАКСИМУМ"""
    all_results = []
    
    # Прогресс бар
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    sources_funcs = [
        ("BBC News", search_bbc_news, enabled_sources.get("BBC News", False)),
        ("The Guardian", search_guardian_news, enabled_sources.get("The Guardian", False)),
        ("Variety", search_variety_news, enabled_sources.get("Variety", False)),
        ("Deadline", search_deadline_news, enabled_sources.get("Deadline", False)),
        ("Hollywood Reporter", search_hollywood_reporter, enabled_sources.get("Hollywood Reporter", False)),
        ("IndieWire", search_indiewire, enabled_sources.get("IndieWire", False)),
        ("Google News", search_google_news, enabled_sources.get("Google News", False)),
        ("Entertainment Weekly", search_google_news, enabled_sources.get("Entertainment Weekly", False))  # заглушка
    ]
    
    total_sources = sum(1 for _, _, enabled in sources_funcs if enabled)
    current_source = 0
    
    for source_name, func, enabled in sources_funcs:
        if enabled:
            current_source += 1
            progress = current_source / total_sources
            progress_bar.progress(progress)
            status_text.text(f"🔍 Ищем в {source_name}...")
            
            try:
                results = func(query)
                all_results.extend(results)
                time.sleep(0.2)  # Небольшая пауза
            except Exception as e:
                st.sidebar.warning(f"Ошибка в {source_name}")
    
    progress_bar.empty()
    status_text.empty()
    
    # Убираем дубликаты
    seen_titles = set()
    unique_results = []
    for result in all_results:
        if result['title'] not in seen_titles:
            seen_titles.add(result['title'])
            unique_results.append(result)
    
    # Сортируем по дате (свежие сначала)
    unique_results.sort(key=lambda x: x['date'], reverse=True)
    
    return unique_results  # ВОЗВРАЩАЕМ ВСЕ НАЙДЕННЫЕ НОВОСТИ

# ========== ОСНОВНОЙ ИНТЕРФЕЙС ==========
# Поле поиска в основной области
col1, col2 = st.columns([3, 1])

with col1:
    st.header("🔍 Введите тему для поиска")
    
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    
    search_query = st.text_input(
        "", 
        value=st.session_state.search_query,
        placeholder="Например: Tim Burton new movie, Wednesday season 2, Beetlejuice sequel...",
        key="main_search_input"
    )

with col2:
    st.markdown("###")
    search_button = st.button("🔎 НАЧАТЬ ПОИСК НОВОСТЕЙ", type="primary", use_container_width=True)

# Если нажата кнопка поиска
if search_button and search_query:
    with st.spinner(f"🔍 Ищу все новости по запросу: '{search_query}'..."):
        # Ищем новости
        results = search_all_news(search_query, sources)
        
        if results:
            # Фильтруем по времени
            filtered_results = filter_by_time(results, time_filter)
            
            st.success(f"✅ НАЙДЕНО: {len(filtered_results)} РЕАЛЬНЫХ НОВОСТЕЙ!")
            
            # Показываем источники
            sources_used = set(r['source'] for r in filtered_results)
            st.caption(f"**Источники:** {', '.join(sources_used)} | **Период:** {time_filter} | **Найдено всего:** {len(results)}")
            
            st.markdown("---")
            
            # Отображаем ВСЕ новости
            for i, news in enumerate(filtered_results):
                # Определяем иконку для источника
                icon = "📰"
                if "BBC" in news['source']:
                    icon = "🇬🇧"
                elif "Guardian" in news['source']:
                    icon = "🗞️"
                elif "Variety" in news['source']:
                    icon = "🎬"
                elif "Deadline" in news['source']:
                    icon = "⏰"
                elif "Hollywood" in news['source']:
                    icon = "⭐"
                elif "Google" in news['source']:
                    icon = "🔍"
                elif "IndieWire" in news['source']:
                    icon = "🎥"
                
                # Карточка новости
                with st.expander(f"{icon} **{news['title']}**", expanded=(i < 5)):  # Первые 5 открыты
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        st.markdown(f"**Источник:** `{news['source']}`")
                        st.markdown(f"**Дата:** `{news['date'].strftime('%d.%m.%Y %H:%M')}`")
                        
                        if news['summary'] and len(news['summary']) > 50:
                            st.markdown("**Описание:**")
                            st.write(news['summary'])
                    
                    with col_b:
                        st.markdown("")
                        st.markdown("")
                        st.markdown(f"[📖 ОТКРЫТЬ СТАТЬЮ]({news['link']})", unsafe_allow_html=True)
                    
                    # Полный текст (если есть)
                    if news.get('full_text') and len(news['full_text']) > 100:
                        with st.expander("📄 Показать больше текста"):
                            st.write(news['full_text'][:1500] + "..." if len(news['full_text']) > 1500 else news['full_text'])
                
                st.markdown("---")
            
            # Статистика
            st.info(f"""
            **📊 СТАТИСТИКА ПОИСКА:**
            - Всего найдено новостей: **{len(results)}**
            - После фильтра по времени: **{len(filtered_results)}**
            - Самые свежие новости: **{filtered_results[0]['date'].strftime('%d.%m.%Y') if filtered_results else 'нет'}**
            - Количество источников: **{len(sources_used)}**
            - Самое старое: **{filtered_results[-1]['date'].strftime('%d.%m.%Y') if len(filtered_results) > 1 else 'нет'}**
            """)
            
        else:
            st.error("😞 НЕ НАЙДЕНО НОВОСТЕЙ ПО ЗАПРОСУ.")
            st.info("""
            **💡 СОВЕТЫ ДЛЯ ЛУЧШЕГО ПОИСКА:**
            1. **Используйте английские названия** - `"Tim Burton"` вместо `"Тим Бёртон"`
            2. **Попробуйте разные формулировки** - `"Wednesday Netflix"`, `"Wednesday season 2"`, `"Wednesday Addams"`
            3. **Убедитесь, что выбраны источники** в боковой панели
            4. **Расширьте период поиска** - выберите "Все время"
            5. **Попробуйте поискать позже** - новости появляются постоянно
            
            **Лучшие запросы:**
            • Wednesday season 2 Netflix
            • Beetlejuice 2 release date
            • Tim Burton exhibition 2024
            • Johnny Depp Burton collaboration
            • Monica Bellucci Tim Burton
            """)

# Если запрос не введен
elif not search_query or not search_button:
    st.markdown("---")
    
    # Инструкция
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        with st.expander("📋 КАК ПОЛЬЗОВАТЬСЯ", expanded=True):
            st.markdown("""
            ### 🔍 **ЭТО РЕАЛЬНЫЙ ПОИСК НОВОСТЕЙ**
            
            **Как работает:**
            1. **Введите запрос** на английском языке
            2. **Выберите источники** в боковой панели
            3. **Нажмите "НАЧАТЬ ПОИСК"**
            4. **Получите все найденные новости**
            
            **Всегда показываются ВСЕ найденные новости!**
            
            **Лучшие источники:**
            • BBC News - международные новости
            • The Guardian - качественные статьи
            • Variety - профессиональная индустрия
            • Deadline - последние новости Голливуда
            """)
    
    with col_info2:
        with st.expander("🎯 ЛУЧШИЕ ЗАПРОСЫ", expanded=True):
            st.markdown("""
            ### **Проверенные запросы:**
            
            **Для фильмов:**
            • `Wednesday season 2`
            • `Beetlejuice 2`
            • `Tim Burton new movie`
            • `Burton Netflix project`
            
            **Для актеров:**
            • `Johnny Depp Burton`
            • `Jenna Ortega Wednesday`
            • `Winona Ryder Beetlejuice`
            • `Monica Bellucci Tim`
            
            **Для выставок и новостей:**
            • `Tim Burton exhibition`
            • `Burton art show 2024`
            • `Burton interview 2024`
            • `New projects 2024`
            """)
    
    # Последние новости (пример)
    st.markdown("---")
    st.subheader("🔥 ЧТО СЕЙЧАС ИЩУТ:")
    
    trending = [
        "🔍 Wednesday season 2 Netflix",
        "🔍 Beetlejuice 2 release date", 
        "🔍 Tim Burton exhibition London",
        "🔍 Johnny Depp new movie",
        "🔍 Monica Bellucci Tim Burton"
    ]
    
    for trend in trending:
        st.markdown(f"- {trend}")

# Кнопка "На главную"
st.markdown("---")
if st.button("🏠 НА ГЛАВНУЮ СТРАНИЦУ", use_container_width=True, type="secondary"):
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 10px;'>
        <h4 style='color: #f0e68c;'>ПЕРЕЙТИ НА ГЛАВНУЮ СТРАНИЦУ ПРОЕКТА</h4>
        <a href='https://quixotic-shrimp-ea9.notion.site/9aabb68bd7004965819318e32d8ff06e?v=2b4a0ca7844a80d6aa8a000c6a7e5272' 
           target='_blank' 
           style='color: #ff6b6b; text-decoration: none; font-weight: bold; font-size: 18px; background: #0f3460; padding: 10px 20px; border-radius: 5px; display: inline-block; margin: 10px;'>
           🚀 ОТКРЫТЬ ГЛАВНУЮ
        </a>
    </div>
    """, unsafe_allow_html=True)

# Футер
st.markdown("---")
st.caption(f"🎬 РЕАЛЬНЫЙ ПОИСК НОВОСТЕЙ | ОБНОВЛЕНО: {datetime.now().strftime('%d.%m.%Y %H:%M')} | ВСЕГДА МАКСИМАЛЬНОЕ КОЛИЧЕСТВО РЕЗУЛЬТАТОВ")
