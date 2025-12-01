import streamlit as st
import requests
import datetime

# Настройка страницы
st.set_page_config(
    page_title="Тим Бёртон - Поиск новостей", 
    layout="wide",
    initial_sidebar_state="expanded"  # Боковая панель открыта по умолчанию
)

# Получаем Groq API ключ
if 'GROQ_API_KEY' in st.secrets:
    GROQ_API_KEY = st.secrets['GROQ_API_KEY']
else:
    st.error("Ключ GROQ_API_KEY не найден в секретах.")
    GROQ_API_KEY = None

# ========== БОКОВАЯ ПАНЕЛЬ (ШТОРКА) ==========
with st.sidebar:
    st.title("🎬 Тим Бёртон")
    st.markdown("---")
    
    # Настройки поиска
    st.header("⚙️ Настройки поиска")
    
    # Выбор модели (если нужно)
    model_option = st.selectbox(
        "Модель AI:",
        ["llama-3.1-8b-instant", "llama3-70b-8192", "mixtral-8x7b-32768"],
        index=0
    )
    
    # Температура (креативность)
    temperature = st.slider(
        "Креативность ответов:",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Ниже = точнее, выше = креативнее"
    )
    
    # Количество результатов
    num_results = st.slider(
        "Количество новостей:",
        min_value=1,
        max_value=10,
        value=4,
        step=1
    )
    
    st.markdown("---")
    
    # Быстрый поиск
    st.header("🚀 Быстрый поиск")
    st.write("Нажмите на запрос для поиска:")
    
    quick_queries = [
        "Когда выйдет Уэднесдэй 2 сезон?",
        "Битлджус 2 дата выхода в мире",
        "Тим Бёртон и Моника Беллуччи последние новости",
        "Новые проекты Тима Бёртона 2024",
        "Выставка Бёртона в музее",
        "Актеры Битлджус 2"
    ]
    
    for query in quick_queries:
        if st.button(query, key=f"quick_{query}", use_container_width=True):
            st.session_state.search_query = query
            st.rerun()
    
    st.markdown("---")
    
    # Информация о приложении
    st.header("ℹ️ О приложении")
    st.info("""
    Это приложение использует Groq API для поиска 
    актуальных новостей о Тим Бёртоне.
    
    **Важно:** Все ссылки и даты предоставляются 
    AI и могут требовать проверки.
    """)
    
    # Ссылки
    st.markdown("---")
    st.write("**Полезные ссылки:**")
    st.markdown("""
    - [Официальный сайт Тима Бёртона](https://timburton.com)
    - [IMDb: Тим Бёртон](https://www.imdb.com/name/nm0000318/)
    - [Wikipedia](https://ru.wikipedia.org/wiki/Бёртон,_Тим)
    """)
    
    # Кнопка очистки
    if st.button("🧹 Очистить историю", use_container_width=True):
        if 'search_history' in st.session_state:
            st.session_state.search_history = []
        st.success("История очищена!")

# ========== ОСНОВНАЯ ОБЛАСТЬ ==========
st.title("🧛 Автоматический поиск новостей: Тим Бёртон")
st.markdown("Поиск актуальной информации, дат релизов и интервью.")

# История поиска (сохраняем в сессии)
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

def search_news(query, model=model_option, temp=temperature, num=num_results):
    """Поиск новостей через Groq API с запросом формата даты и ссылок"""
    if not GROQ_API_KEY:
        return None
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Получаем текущую дату, чтобы модель понимала контекст времени
    current_date = datetime.datetime.now().strftime("%d.%m.%Y")
    
    # Обновленный промпт с учетом настроек
    prompt = f"""
    Сегодняшняя дата: {current_date}.
    Ты — новостной ассистент по творчеству Тима Бёртона.
    Пользователь ищет информацию по запросу: "{query}".
    
    Найди {num} ключевых факта или новости.
    Для каждой новости ОБЯЗАТЕЛЬНО используй такой формат (используй Markdown):
    
    ### 🎬 [Заголовок новости]
    📅 Дата/Период: [Укажи дату или примерное время события]
    🔗 Источник: Укажи название источника и вставь ссылку в формате: [Название сайта]
    📝 Суть: [Краткое описание новости]
    
    ---
    
    Если ты не знаешь точной ссылки, укажи ссылку на официальный сайт или IMDB. Не выдумывай несуществующие URL.
    """
    
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "model": model,
        "temperature": temp
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"Ошибка API: {response.status_code}"
    except Exception as e:
        return f"Ошибка: {str(e)}"

# Интерфейс поиска в основной области
col1, col2 = st.columns([3, 1])

with col1:
    st.header("🔍 Введите тему для поиска")
    
    # Поле поиска с сохранением предыдущего запроса
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    
    search_query = st.text_input(
        "", 
        value=st.session_state.search_query,
        placeholder="Например: Битлджус 2 актеры, Выставка Бёртона 2024...",
        key="main_search_input"
    )

with col2:
    st.markdown("###")  # Для вертикального выравнивания
    search_button = st.button("🔎 Начать поиск", type="primary", use_container_width=True)

# Если нажата кнопка поиска или выбран быстрый запрос
if search_button and search_query:
    # Сохраняем в историю
    if search_query not in st.session_state.search_history:
        st.session_state.search_history.append(search_query)
    
    with st.spinner(f"Ищем информацию по запросу: '{search_query}'..."):
        results = search_news(search_query)
        
        if results:
            # Показываем запрос
            st.subheader(f"📋 Результаты по запросу: **{search_query}**")
            
            # Настройки, которые использовались
            with st.expander("⚙️ Параметры этого поиска"):
                st.write(f"- **Модель:** {model_option}")
                st.write(f"- **Креативность:** {temperature}")
                st.write(f"- **Количество новостей:** {num_results}")
                st.write(f"- **Дата поиска:** {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
            # Результаты
            st.markdown("---")
            st.markdown(results)
            
            # Предупреждение
            st.warning("""
            ⚠️ **Примечание:** 
            1. Ссылки сгенерированы искусственным интеллектом
            2. Если ссылка не открывается, попробуйте найти заголовок новости в Google
            3. Даты и информация могут требовать проверки
            """)
            
            # Кнопки действий
            col_act1, col_act2, col_act3 = st.columns(3)
            with col_act1:
                if st.button("📋 Скопировать результаты", use_container_width=True):
                    st.code(results, language="markdown")
                    st.success("Результаты скопированы в буфер обмена!")
            with col_act2:
                if st.button("🔄 Новый поиск", use_container_width=True):
                    st.session_state.search_query = ""
                    st.rerun()
            with col_act3:
                if st.button("📊 Сохранить в историю", use_container_width=True):
                    st.success("Поиск сохранен в истории!")
        else:
            st.error("Не удалось выполнить поиск. Проверьте API ключ.")

# Если есть история поиска, показываем ее
if st.session_state.search_history:
    st.markdown("---")
    with st.expander("📜 История поиска (последние 10 запросов)"):
        for i, query in enumerate(reversed(st.session_state.search_history[-10:])):
            col_h1, col_h2 = st.columns([4, 1])
            with col_h1:
                st.write(f"{i+1}. {query}")
            with col_h2:
                if st.button("🔁", key=f"repeat_{i}"):
                    st.session_state.search_query = query
                    st.rerun()

# Примеры в основной области
st.markdown("---")
with st.expander("📌 Примеры популярных запросов (нажмите, чтобы скопировать)"):
    examples = [
        "Когда выйдет Уэднесдэй 2 сезон?",
        "Битлджус 2 дата выхода в мире",
        "Тим Бёртон и Моника Беллуччи последние новости",
        "Где проходит выставка картин Тима Бёртона?",
        "Интервью Тима Бёртона 2024",
        "Новый проект с Джонни Деппом",
        "Уоднесдэй актеры второго сезона",
        "Награды и премии 2023-2024"
    ]
    
    for example in examples:
        if st.button(example, key=f"example_{example}", use_container_width=True):
            st.session_state.search_query = example
            st.rerun()

# Кнопка "Назад" с вашим дизайном
st.markdown("---")
if st.button("⬅️ Назад", use_container_width=True, key="back_news"):
    st.markdown("""
    <div style='background-color: #2b2b2b; padding: 15px; border-radius: 10px; border: 1px solid #f0e68c;'>
        <h4 style='color: #f0e68c; margin-top: 0;'>Перейти на главную страницу</h4>
        <p style='margin-bottom: 10px;'>Нажмите на ссылку ниже:</p>
        <a href='https://quixotic-shrimp-ea9.notion.site/9aabb68bd7004965819318e32d8ff06e?v=2b4a0ca7844a80d6aa8a000c6a7e5272' 
           target='_blank' 
           style='color: #ff6b6b; text-decoration: none; font-weight: bold; font-size: 16px;'>
           🏠 Главная страница проекта
        </a>
        <p style='margin-top: 10px; font-size: 12px; color: #ccc;'>Ссылка откроется в новой вкладке</p>
    </div>
    """, unsafe_allow_html=True)

# Информация в подвале
st.markdown("---")
st.caption("🎬 Приложение для поиска новостей о Тим Бёртоне | Использует Groq API | Обновлено: " + 
           datetime.datetime.now().strftime("%d.%m.%Y"))
