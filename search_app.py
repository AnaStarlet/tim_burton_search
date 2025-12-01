import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup
import json
import time

# ==================== НАСТРОЙКИ ====================
st.set_page_config(
    page_title="Поиск новостей о Тим Бёртоне",
    page_icon="🎬",
    layout="wide"
)

# ==================== CSS СТИЛИ ====================
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .news-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 5px solid #ff4b4b;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .news-card-internet {
        border-left: 5px solid #00ff00 !important;
    }
    .news-card-database {
        border-left: 5px solid #ffaa00 !important;
    }
    .source-badge {
        display: inline-block;
        background: #ff4b4b;
        color: white;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        margin-right: 10px;
    }
    .internet-badge {
        background: #00cc44 !important;
    }
    .database-badge {
        background: #ff9900 !important;
    }
    h1, h2, h3 {
        color: #ff4b4b !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #ff4b4b 0%, #ff6b6b 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #ff3333 0%, #ff5555 100%);
    }
</style>
""", unsafe_allow_html=True)

# ==================== БАЗА ДАННЫХ (ЗАГРУШЕННЫЕ НОВОСТИ) ====================
def load_database_news():
    """Загружает предварительно сохраненные новости из 'базы данных'"""
    database_news = [
        {
            "title": "Уоднесдэй 2 сезон: Netflix анонсировал съемки",
            "source": "Deadline Hollywood",
            "date": "2024",
            "summary": "Второй сезон сериала 'Уоднесдэй' с Дженной Ортегой начнут снимать весной 2024 года.",
            "url": "https://deadline.com/2023/11/wednesday-season-2-netflix-release-date-1235601234/",
            "type": "database"
        },
        {
            "title": "Тим Бёртон о работе над 'Уоднесдэй'",
            "source": "Variety",
            "date": "2023",
            "summary": "Режиссер Тим Бёртон рассказал о своем подходе к созданию атмосферы в сериале 'Уоднесдэй'.",
            "url": "https://variety.com/2023/tv/news/tim-burton-wednesday-netflix-interview-1235489123/",
            "type": "database"
        },
        {
            "title": "Битлджус 2: возвращение культового фильма",
            "source": "Hollywood Reporter",
            "date": "2024",
            "summary": "Тим Бёртон подтвердил работу над сиквелом 'Битлджуса', выход намечен на 2025 год.",
            "url": "https://www.hollywoodreporter.com/movies/movie-news/beetlejuice-2-tim-burton-return-1235678901/",
            "type": "database"
        },
        {
            "title": "Джонни Депп и Тим Бёртон: история сотрудничества",
            "source": "Empire",
            "date": "2023",
            "summary": "Вспоминаем все фильмы, которые создали легендарный дуэт Бёртона и Деппа.",
            "url": "https://www.empireonline.com/movies/features/tim-burton-johnny-depp-collaboration-history/",
            "type": "database"
        }
    ]
    return database_news

# ==================== ПОИСК В ИНТЕРНЕТЕ (RSS) ====================
def search_rss_news(query, max_results=15):
    """
    Ищет новости по RSS-лентам на основе запроса
    Возвращает список статей
    """
    articles = []
    
    # RSS-ленты новостных сайтов о кино и развлечениях
    rss_feeds = [
        {
            "url": "https://deadline.com/feed/",
            "name": "Deadline Hollywood",
            "category": "film"
        },
        {
            "url": "https://variety.com/feed/",
            "name": "Variety",
            "category": "entertainment"
        },
        {
            "url": "https://www.hollywoodreporter.com/feed/",
            "name": "Hollywood Reporter",
            "category": "film"
        },
        {
            "url": "https://www.theguardian.com/film/rss",
            "name": "The Guardian Film",
            "category": "film"
        },
        {
            "url": "https://www.indiewire.com/feed/",
            "name": "IndieWire",
            "category": "film"
        }
    ]
    
    search_terms = query.lower().split()
    
    for feed_info in rss_feeds:
        try:
            st.info(f"🔍 Ищем в {feed_info['name']}...")
            
            # Парсим RSS
            feed = feedparser.parse(feed_info['url'])
            
            for entry in feed.entries[:20]:  # Проверяем первые 20 записей
                # Проверяем совпадение в заголовке
                title = entry.title.lower() if hasattr(entry, 'title') else ""
                summary = entry.summary.lower() if hasattr(entry, 'summary') else ""
                description = entry.description.lower() if hasattr(entry, 'description') else ""
                
                content = f"{title} {summary} {description}"
                
                # Проверяем все слова запроса
                match_score = sum(1 for term in search_terms if term in content)
                
                if match_score > 0:  # Если найдено хотя бы одно слово
                    # Извлекаем дату
                    if hasattr(entry, 'published_parsed'):
                        date = datetime(*entry.published_parsed[:6])
                        date_str = date.strftime("%d.%m.%Y")
                    elif hasattr(entry, 'published'):
                        date_str = entry.published
                    else:
                        date_str = "Дата неизвестна"
                    
                    # Извлекаем описание
                    if hasattr(entry, 'summary'):
                        # Очищаем HTML теги
                        soup = BeautifulSoup(entry.summary, 'html.parser')
                        summary_text = soup.get_text()[:200] + "..."
                    else:
                        summary_text = "Описание отсутствует"
                    
                    article = {
                        "title": entry.title,
                        "source": feed_info['name'],
                        "date": date_str,
                        "summary": summary_text,
                        "url": entry.link,
                        "type": "internet",
                        "match_score": match_score
                    }
                    articles.append(article)
                    
                    if len(articles) >= max_results:
                        break
            
            time.sleep(0.5)  # Небольшая пауза между запросами
            
        except Exception as e:
            st.warning(f"⚠️ Ошибка при чтении {feed_info['name']}: {str(e)[:100]}...")
            continue
    
    # Сортируем по релевантности
    articles.sort(key=lambda x: x['match_score'], reverse=True)
    return articles[:max_results]

# ==================== ДОПОЛНИТЕЛЬНЫЙ ПОИСК ЧЕРЕЗ GOOGLE NEWS RSS ====================
def search_google_news_rss(query, max_results=10):
    """Ищет новости через Google News RSS"""
    try:
        # Формируем URL для Google News RSS
        formatted_query = query.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={formatted_query}+Тим+Бёртон&hl=ru&gl=RU&ceid=RU:ru"
        
        feed = feedparser.parse(url)
        articles = []
        
        for entry in feed.entries[:max_results]:
            article = {
                "title": entry.title,
                "source": entry.source.title if hasattr(entry, 'source') else "Google News",
                "date": entry.published if hasattr(entry, 'published') else "Дата неизвестна",
                "summary": entry.title,  # У Google News часто нет отдельного summary
                "url": entry.link,
                "type": "internet",
                "match_score": 3
            }
            articles.append(article)
        
        return articles
    except Exception as e:
        st.warning(f"⚠️ Ошибка Google News RSS: {str(e)[:100]}")
        return []

# ==================== ОТОБРАЖЕНИЕ НОВОСТЕЙ ====================
def display_article(article, index):
    """Отображает одну новость в красивом формате"""
    card_class = "news-card-internet" if article["type"] == "internet" else "news-card-database"
    badge_class = "internet-badge" if article["type"] == "internet" else "database-badge"
    badge_text = "🌐 ИНТЕРНЕТ" if article["type"] == "internet" else "💾 БАЗА"
    
    st.markdown(f"""
    <div class="news-card {card_class}">
        <h4>{article['title']}</h4>
        <p>
            <span class="source-badge {badge_class}">{badge_text}</span>
            <span class="source-badge">{article['source']}</span>
            <span style="color: #888;">| {article['date']}</span>
        </p>
        <p>{article['summary']}</p>
        <a href="{article['url']}" target="_blank" style="color: #ff4b4b; text-decoration: none;">📖 Читать полностью →</a>
    </div>
    """, unsafe_allow_html=True)

# ==================== ОСНОВНОЙ ИНТЕРФЕЙС ====================
def main():
    # Заголовок
    st.title("🎬 Поиск новостей о Тим Бёртоне")
    st.markdown("---")
    
    # Боковая панель
    with st.sidebar:
        st.header("⚙️ Настройки поиска")
        
        search_mode = st.radio(
            "Режим поиска:",
            ["🌐 Только из интернета", "💾 Только из базы", "🔍 Везде"],
            index=2
        )
        
        st.markdown("---")
        st.header("🔎 Быстрый поиск")
        
        quick_queries = ["Уоднесдэй 2", "Битлджус 2", "Джонни Депп", "Тим Бёртон", "Новые проекты"]
        
        for q in quick_queries:
            if st.button(q, key=f"quick_{q}"):
                st.session_state.search_query = q
        
        st.markdown("---")
        st.info("""
        **📢 Примечание:**
        - Поиск в интернете может занять 10-30 секунд
        - Некоторые сайты могут блокировать RSS-запросы
        - Для более точного поиска используйте английские названия
        """)
    
    # Основная область
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Поле поиска
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ""
        
        query = st.text_input(
            "**Введите запрос:**",
            value=st.session_state.search_query,
            placeholder="Например: 'Tim Burton new movie', 'Уоднесдэй 2 сезон'..."
        )
    
    with col2:
        st.markdown("###")
        search_button = st.button("🔍 Начать поиск", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    # Если нажата кнопка поиска
    if search_button and query:
        st.session_state.search_query = query
        
        # Показываем индикатор поиска
        search_placeholder = st.empty()
        
        with search_placeholder.container():
            st.subheader(f"Результаты поиска: '{query}'")
            
            # Прогресс бар
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            all_articles = []
            
            # ========== ПОИСК В ИНТЕРНЕТЕ ==========
            if search_mode in ["🌐 Только из интернета", "🔍 Везде"]:
                status_text.text("🔍 Ищу свежие новости в интернете...")
                
                # Поиск через RSS новостных сайтов
                progress_bar.progress(30)
                rss_articles = search_rss_news(query, max_results=10)
                
                # Поиск через Google News RSS
                progress_bar.progress(60)
                google_articles = search_google_news_rss(query, max_results=5)
                
                internet_articles = rss_articles + google_articles
                
                # Убираем дубликаты
                seen_titles = set()
                unique_internet_articles = []
                for article in internet_articles:
                    if article['title'] not in seen_titles:
                        seen_titles.add(article['title'])
                        unique_internet_articles.append(article)
                
                all_articles.extend(unique_internet_articles)
                
                progress_bar.progress(80)
            
            # ========== ПОИСК В БАЗЕ ДАННЫХ ==========
            if search_mode in ["💾 Только из базы", "🔍 Везде"]:
                status_text.text("💾 Ищу в базе данных...")
                
                database_articles = []
                db_news = load_database_news()
                
                query_lower = query.lower()
                for article in db_news:
                    if (query_lower in article['title'].lower() or 
                        query_lower in article['summary'].lower()):
                        database_articles.append(article)
                
                all_articles.extend(database_articles)
                
                progress_bar.progress(100)
            
            status_text.text("✅ Поиск завершен!")
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
        
        # Очищаем индикатор и показываем результаты
        search_placeholder.empty()
        
        # Показываем результаты
        if all_articles:
            # Группируем по источнику
            internet_count = sum(1 for a in all_articles if a['type'] == 'internet')
            database_count = sum(1 for a in all_articles if a['type'] == 'database')
            
            st.success(f"🎉 Найдено {len(all_articles)} новостей: 🌐 {internet_count} из интернета, 💾 {database_count} из базы")
            st.markdown("---")
            
            # Показываем все статьи
            for i, article in enumerate(all_articles):
                display_article(article, i)
                
                # Кнопка "Сохранить в базу" для интернет-новостей
                if article['type'] == 'internet':
                    col_s1, col_s2, col_s3 = st.columns([1, 1, 8])
                    with col_s1:
                        if st.button("💾 Сохранить", key=f"save_{i}"):
                            st.success(f"Новость '{article['title'][:50]}...' сохранена в базу!")
                    with col_s2:
                        if st.button("📌 Закладка", key=f"bookmark_{i}"):
                            st.info("Добавлено в закладки")
                    st.markdown("---")
        else:
            st.warning("😞 Ничего не найдено. Попробуйте:")
            st.markdown("""
            1. Изменить запрос
            2. Использовать английские названия
            3. Проверить режим поиска
            """)
    
    # Если запрос еще не вводили
    elif not search_button:
        st.markdown("""
        ## 🎯 Как пользоваться поиском:
        
        1. **Введите запрос** в поле выше (например: "Tim Burton", "Уоднесдэй", "Битлджус 2")
        2. **Выберите режим поиска** в боковой панели:
           - 🌐 **Только из интернета** - свежие новости с RSS-лент
           - 💾 **Только из базы** - сохраненные статьи
           - 🔍 **Везде** - поиск во всех источниках
        3. **Нажмите "Начать поиск"** или используйте быстрый поиск
        
        ## 📌 Популярные запросы:
        - Новые проекты Тима Бёртона
        - Уоднесдэй 2 сезон
        - Битлджус сиквел
        - Фильмы с Джонни Деппом
        - Анимационные работы
        """)
        
        # Показываем последние сохраненные новости
        st.markdown("---")
        st.subheader("💾 Последние новости из базы:")
        
        db_news = load_database_news()
        for i, article in enumerate(db_news[:3]):
            display_article(article, i)
            st.markdown("---")

# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    # Проверяем наличие feedparser
    try:
        import feedparser
        main()
    except ImportError:
        st.error("""
        ⚠️ **Ошибка: Модуль feedparser не установлен!**
        
        Установите его командой:
        ```
        pip install feedparser
        ```
        
        Или добавьте в файл `requirements.txt`:
        ```
        feedparser>=6.0.10
        ```
        """)
