import streamlit as st
import requests
import urllib.parse

# Настройка страницы
st.set_page_config(page_title="Тим Бёртон - Поиск новостей", layout="wide")

# Получаем Groq API ключ
API_KEY = "e9eac514f1cd4452b6f6a672b3c9cd2d"  # Ваш API ключ
GROQ_API_KEY = API_KEY if API_KEY else None

if not GROQ_API_KEY:
    st.error("Ключ API не найден.")

st.title("🦇 Автоматический поиск новостей о творческой вселенной Тима Бёртона")

def search_news(query):
    """Поиск информации через Groq API о творческой вселенной Тима Бёртона"""
    if not GROQ_API_KEY:
        return None, False
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Широкий промпт для всей творческой вселенной Бёртона
    prompt = f"""Ты - эксперт по творческой вселенной режиссера Тима Бёртона. 
Отвечай на вопросы о ВСЁМ, что связано с Тимом Бёртоном и его творчеством:

РАЗРЕШЕННЫЕ ТЕМЫ:
1. Все фильмы и проекты Тима Бёртона
2. Все актёры, которые снимались у Бёртона (Джонни Депп, Хелена Бонем Картер, Майкл Китон, Вайнона Райдер, Лиза Мэри и др.)
3. Композиторы (Дэнни Эльфман и другие)
4. Сценаристы, продюсеры, операторы, работавшие с Бёртоном
5. Анимационные и художественные работы Бёртона
6. Биография, награды, интервью Бёртона
7. Критика и анализ его творчества
8. Фанатская культура и сообщество
9. Влияние Бёртона на поп-культуру
10. Стиль, визуальные особенности его работ

ИНСТРУКЦИИ:
1. Если вопрос СВЯЗАН с Тимоти Бёртоном или его творческой вселенной - дай развернутый ответ.
2. Если вопрос НЕ связан с Бёртоном и его миром (например, погода, политика, другие режиссеры, общие темы), отвечай: "Этот вопрос не связан с творческой вселенной Тима Бёртона."
3. Отвечай на русском языке.
4. Предоставляй актуальную информацию (если доступна).
5. Формат: краткий, информативный ответ.

Вопрос пользователя: {query}

Ответ:"""
    
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "model": "llama-3.1-8b-instant",
        "temperature": 0.4,
        "max_tokens": 800
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            
            # Проверяем, является ли вопрос о вселенной Бёртона
            is_burton_universe = True
            rejection_phrases = [
                "не связан с творческой вселенной",
                "не связан с тимом бёртоном",
                "этот вопрос не связан",
                "не могу ответить на этот вопрос"
            ]
            
            # Также проверяем, не является ли ответ слишком общим/универсальным
            universal_answers = [
                "я не могу ответить",
                "я не знаю",
                "не имею информации",
                "модель не может"
            ]
            
            answer_lower = answer.lower()
            for phrase in rejection_phrases + universal_answers:
                if phrase in answer_lower and len(answer) < 150:  # Если короткий отказ
                    is_burton_universe = False
                    break
            
            return answer, is_burton_universe
        else:
            return f"Ошибка API: {response.status_code}", False
    except Exception as e:
        return f"Ошибка: {str(e)}", False

def create_google_search_link(query):
    """Создает ссылку для поиска в Google"""
    encoded_query = urllib.parse.quote(query)
    return f"https://www.google.com/search?q={encoded_query}"

# Интерфейс поиска
st.header("🔍 Поиск по вселенной Тима Бёртона")
st.markdown("### Ищите информацию о фильмах, актёрах, проектах и всем, что связано с Бёртоном")

col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input(
        "Введите ваш запрос:",
        placeholder="Например: Уэднесдэй 2 сезон, Джонни Депп, Дэнни Эльфман...",
        key="search_input"
    )

# Быстрые кнопки популярных запросов
st.markdown("### 🚀 Популярные запросы:")
quick_cols = st.columns(5)
with quick_cols[0]:
    if st.button("🎬 Уэднесдэй 2", use_container_width=True):
        st.session_state.search_query = "Уэднесдэй 2 сезон новости"
with quick_cols[1]:
    if st.button("👻 Битлджус 2", use_container_width=True):
        st.session_state.search_query = "Битлджус 2 новый фильм Тим Бёртон"
with quick_cols[2]:
    if st.button("🎭 Джонни Депп", use_container_width=True):
        st.session_state.search_query = "Джонни Депп и Тим Бёртон сотрудничество"
with quick_cols[3]:
    if st.button("🎵 Дэнни Эльфман", use_container_width=True):
        st.session_state.search_query = "Дэнни Эльфман музыка для фильмов Бёртона"
with quick_cols[4]:
    if st.button("📅 Новые проекты", use_container_width=True):
        st.session_state.search_query = "Новые проекты Тим Бёртон 2024"

# Используем состояние для автоматического заполнения
if 'search_query' in st.session_state and st.session_state.search_query:
    search_query = st.session_state.search_query

if search_query:
    with st.spinner("🔮 Погружаюсь в мир Бёртона..."):
        results, is_burton_universe = search_news(search_query)
        
        if results:
            if is_burton_universe:
                st.subheader("🎭 Результаты поиска:")
                st.markdown(f"**Запрос:** `{search_query}`")
                st.markdown("---")
                
                # Красивое оформление ответа
                st.markdown(f"""
                <div style='background-color: #2b2b2b; padding: 20px; border-radius: 10px; border-left: 5px solid #f0e68c;'>
                {results.replace('\n', '<br>')}
                </div>
                """, unsafe_allow_html=True)
                
                # Дополнительные ссылки
                st.markdown("---")
                col_info, col_google = st.columns(2)
                with col_info:
                    st.markdown("""
                    **📚 Дополнительно:**
                    - [Википедия: Тим Бёртон](https://ru.wikipedia.org/wiki/Бёртон,_Тим)
                    - [IMDb фильмография](https://www.imdb.com/name/nm0000318/)
                    """)
                with col_google:
                    google_link = create_google_search_link(f"Тим Бёртон {search_query}")
                    st.markdown(f"""
                    **🔍 Больше информации:**
                    [Поиск в Google]({google_link})
                    """)
                    
            else:
                # Если вопрос не о вселенной Бёртона
                st.warning("⚠️ Этот запрос не связан с творческой вселенной Тима Бёртона")
                st.markdown("---")
                
                # Предлагаем поискать в Google с вариантами
                st.subheader("🔎 Попробуйте один из вариантов:")
                
                google_link = create_google_search_link(search_query)
                burton_google_link = create_google_search_link(f"Тим Бёртон {search_query}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div style='background-color: #f0f8ff; padding: 15px; border-radius: 10px; border: 2px solid #4da6ff; text-align: center;'>
                        <h4 style='color: #0066cc;'>Общий поиск</h4>
                        <a href='{google_link}' 
                           target='_blank' 
                           style='color: #0066cc; text-decoration: none; font-weight: bold;'>
                           🔍 "{search_query}"
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='background-color: #fff0f0; padding: 15px; border-radius: 10px; border: 2px solid #ff6b6b; text-align: center;'>
                        <h4 style='color: #cc0000;'>Поиск с Бёртоном</h4>
                        <a href='{burton_google_link}' 
                           target='_blank' 
                           style='color: #cc0000; text-decoration: none; font-weight: bold;'>
                           🦇 "Тим Бёртон {search_query}"
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Быстрые запросы по Бёртону
                st.markdown("---")
                st.markdown("### 🎬 Или попробуйте эти запросы о Бёртоне:")
                
                quick_buttons = st.columns(4)
                burtons_queries = [
                    "Фильмы Тима Бёртона",
                    "Актёры Бёртона",
                    "Стиль Бёртона",
                    "Новости Бёртона"
                ]
                
                for idx, query in enumerate(burtons_queries):
                    with quick_buttons[idx]:
                        if st.button(query, use_container_width=True):
                            st.session_state.search_query = query
                            st.rerun()
        else:
            st.error("❌ Не удалось выполнить поиск. Попробуйте позже.")

# Боковая панель с информацией
with st.sidebar:
    st.markdown("### 🦇 О системе поиска")
    st.markdown("""
    **Ищем ВСЁ о творческой вселенной Тима Бёртона:**
    
    ✅ **Фильмы и проекты:**
    - Уэднесдэй (сериал)
    - Битлджус, Битлджус 2
    - Эдвард Руки-ножницы
    - Кошмар перед Рождеством
    - И все другие фильмы
    
    ✅ **Актёры и команда:**
    - Джонни Депп
    - Хелена Бонем Картер
    - Майкл Китон
    - Вайнона Райдер
    - Дэнни Эльфман (композитор)
    - И многие другие
    
    ✅ **Темы и стиль:**
    - Готический стиль Бёртона
    - Анимационные работы
    - Биография и интервью
    - Награды и признание
    - Культурное влияние
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Статистика")
    if search_query and results:
        st.metric("Длина ответа", f"{len(results)} символов")
        st.metric("Тема запроса", "Бёртон" if is_burton_universe else "Другое")

# Кнопка "Назад" внизу
st.markdown("---")
col_back, col_space = st.columns([1, 3])
with col_back:
    if st.button("⬅️ На главную", use_container_width=True, type="secondary"):
        st.markdown("""
        <script>
            window.open('https://quixotic-shrimp-ea9.notion.site/9aabb68bd7004965819318e32d8ff06e?v=2b4a0ca7844a80d6aa8a000c6a7e5272', '_blank');
        </script>
        """, unsafe_allow_html=True)
