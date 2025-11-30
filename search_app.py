import streamlit as st
import requests
import json

# Настройка страницы
st.set_page_config(page_title="Тим Бёртон - Поиск новостей", layout="wide")

# Получаем Groq API ключ
if 'GROQ_API_KEY' in st.secrets:
    GROQ_API_KEY = st.secrets['GROQ_API_KEY']
else:
    st.error("Ключ GROQ_API_KEY не найден в секретах.")
    GROQ_API_KEY = None

st.title("Автоматический поиск самых актуальных новостей о творчестве, фильмах и проектах Тима Бёртона")

def search_news(query):
    """Поиск новостей через Groq API"""
    if not GROQ_API_KEY:
        return None
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Найди самые актуальные новости и информацию по запросу: {query}
    Верни ответ в формате:
    - Новость 1
    - Новость 2
    - Новость 3"""
    
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "model": "llama-3.1-8b-instant",
        "temperature": 0.7
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

# Интерфейс поиска
st.header("Поиск новостей о Тим Бёртоне")
search_query = st.text_input("Введите ваш запрос:", placeholder="Уэднесдэй 2 сезон или новые проекты Бёртона...")

if search_query:
    with st.spinner("Ищем новости..."):
        results = search_news(search_query)
        if results:
            st.subheader("Результаты поиска:")
            st.write(results)
        else:
            st.error("Не удалось выполнить поиск")

st.header("Примеры запросов:")
st.markdown("""
- **Уэднесдэй 2 сезон** - новости о продолжении сериала
- **Битлджус Битлджус 2** - о новом фильме  
- **Джонни Депп Тим Бёртон** - об их сотрудничестве
- **Новые проекты Тим Бёртон 2024** - о будущих работах
""")

# Кнопка "Назад" - ИСПРАВЛЕННАЯ ВЕРСИЯ
st.markdown("---")
if st.button("⬅️ Назад", use_container_width=True, key="back_news"):
    # Создаем ссылку, которую пользователь может скопировать или открыть в новой вкладке
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
