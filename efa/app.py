import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder
import io

# --- Расширенные HTML-стили ---
st.set_page_config(
    page_title="DataPlayground Pro",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    body { background-color: #f4f6f9; }
    .stCard {
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Сессионное состояние
if 'dataframes' not in st.session_state:
    st.session_state.dataframes = {}
if 'current_df' not in st.session_state:
    st.session_state.current_df = None

def load_data(uploaded_file):
    file_extension = Path(uploaded_file.name).suffix.lower()
    try:
        if file_extension == '.csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension == '.parquet':
            df = pd.read_parquet(uploaded_file)
        else:
            st.error("Неподдерживаемый формат файла")
            return None
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки: {e}")
        return None

def advanced_filtering(df):
    st.markdown("<div class='stCard'>", unsafe_allow_html=True)
    st.header("🔍 Расширенная Фильтрация")
    
    selected_columns = st.multiselect(
        "Выберите колонки для отображения",
        df.columns.tolist(),
        default=df.columns.tolist()
    )
    
    filter_type = st.radio("Тип фильтрации", ["Числовая", "Текстовая", "Категориальная"])
    
    if filter_type == "Числовая":
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        filter_col = st.selectbox("Колонка для фильтрации", numeric_columns)
        
        min_val, max_val = float(df[filter_col].min()), float(df[filter_col].max())
        filter_range = st.slider(
            f"Диапазон для {filter_col}", 
            min_val, max_val, 
            (min_val, max_val)
        )
        
        filtered_df = df[
            (df[filter_col] >= filter_range[0]) & 
            (df[filter_col] <= filter_range[1])
        ]
    
    elif filter_type == "Текстовая":
        text_columns = df.select_dtypes(include=['object']).columns
        filter_col = st.selectbox("Колонка для фильтрации", text_columns)
        
        filter_text = st.text_input(f"Поиск в колонке {filter_col}")
        filtered_df = df[df[filter_col].str.contains(filter_text, case=False, na=False)]
    
    else:  # Категориальная
        cat_columns = df.select_dtypes(include=['category', 'object']).columns
        filter_col = st.selectbox("Колонка для фильтрации", cat_columns)
        
        unique_values = df[filter_col].unique()
        selected_values = st.multiselect("Выберите значения", unique_values)
        
        filtered_df = df[df[filter_col].isin(selected_values)] if selected_values else df
    
    sort_col = st.selectbox("Сортировка по колонке", filtered_df.columns)
    sort_ascending = st.checkbox("По возрастанию", True)
    
    result_df = filtered_df[selected_columns].sort_values(
        by=sort_col, 
        ascending=sort_ascending
    )
    
    st.subheader(f"Результат: {len(result_df)} строк")
    st.dataframe(result_df)
    
    if st.button("💾 Экспортировать отфильтрованные данные"):
        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Скачать CSV",
            data=csv,
            file_name='filtered_data.csv',
            mime='text/csv'
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

def advanced_grouping(df):
    st.markdown("<div class='stCard'>", unsafe_allow_html=True)
    st.header("📊 Продвинутая Группировка")
    
    group_cols = st.multiselect(
        "Колонки для группировки",
        df.columns.tolist()
    )
    
    if group_cols:
        agg_cols = st.multiselect(
            "Колонки для агрегации",
            [col for col in df.columns if col not in group_cols]
        )
        
        if agg_cols:
            agg_funcs = st.multiselect(
                "Функции агрегации",
                ['count', 'sum', 'mean', 'min', 'max', 'median', 'std'],
                default=['count']
            )
            
            agg_dict = {col: agg_funcs for col in agg_cols}
            
            grouped_df = df.groupby(group_cols).agg(agg_dict).reset_index()
            
            st.subheader("Результат группировки")
            st.dataframe(grouped_df)
            
            if len(group_cols) == 1 and len(agg_cols) == 1:
                group_col = group_cols[0]
                agg_col = agg_cols[0]
                agg_func = agg_funcs[0]
                
                fig = px.bar(
                    grouped_df, 
                    x=group_col, 
                    y=f"{agg_col}_{agg_func}",
                    title=f"{agg_func.capitalize()} {agg_col} по {group_col}"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            if st.button("💾 Экспортировать сгруппированные данные"):
                csv = grouped_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Скачать CSV",
                    data=csv,
                    file_name='grouped_data.csv',
                    mime='text/csv'
                )
    
    st.markdown("</div>", unsafe_allow_html=True)

def advanced_join(st_session_state):
    st.markdown("<div class='stCard'>", unsafe_allow_html=True)
    st.header("🔗 Расширенное Объединение Таблиц")
    
    if len(st_session_state.dataframes) < 2:
        st.warning("Загрузите минимум 2 таблицы для объединения")
        return
    
    table_names = list(st_session_state.dataframes.keys())
    
    left_table = st.selectbox("Левая таблица", table_names)
    right_table = st.selectbox("Правая таблица", 
        [name for name in table_names if name != left_table])
    
    left_df = st_session_state.dataframes[left_table]
    right_df = st_session_state.dataframes[right_table]
    
    left_join_cols = st.multiselect(
        f"Колонки для объединения из {left_table}", 
        left_df.columns.tolist()
    )
    right_join_cols = st.multiselect(
        f"Колонки для объединения из {right_table}", 
        right_df.columns.tolist()
    )
    
    join_type = st.selectbox(
        "Тип объединения", 
        ["inner", "left", "right", "outer"]
    )
    
    if st.button("🔍 Выполнить объединение") and left_join_cols and right_join_cols:
        try:
            result_df = pd.merge(
                left_df, 
                right_df, 
                left_on=left_join_cols, 
                right_on=right_join_cols, 
                how=join_type
            )
            
            st.subheader("Результат объединения")
            st.dataframe(result_df)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Левая таблица", len(left_df))
            col2.metric("Правая таблица", len(right_df))
            col3.metric("Результат", len(result_df))
            
            if st.button("💾 Сохранить результат"):
                new_table_name = f"{left_table}_join_{right_table}"
                st_session_state.dataframes[new_table_name] = result_df
                st.success(f"Таблица '{new_table_name}' сохранена")
        
        except Exception as e:
            st.error(f"Ошибка при объединении: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    st.title("DataPlayground 📊")
    st.write("Анализируйте данные без программирования")

    with st.sidebar:
        st.header("Загрузка Данных")
        uploaded_file = st.file_uploader(
            "Выберите CSV или Parquet файл",
            type=['csv', 'parquet'],
            key='file_uploader'
        )

        if uploaded_file:
            table_name = Path(uploaded_file.name).stem
            if table_name not in st.session_state.dataframes:
                df = load_data(uploaded_file)
                if df is not None:
                    st.session_state.dataframes[table_name] = df
                    st.session_state.current_df = table_name

        if st.session_state.dataframes:
            st.header("Доступные Таблицы")
            selected_table = st.selectbox(
                "Выберите таблицу",
                list(st.session_state.dataframes.keys()),
                key='table_selector'
            )
            st.session_state.current_df = selected_table

    if st.session_state.current_df:
        df = st.session_state.dataframes[st.session_state.current_df]
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Обзор", 
            "Фильтрация", 
            "Группировка", 
            "Объединение",
            "Визуализация"
        ])

        with tab1:
            st.write("### Информация о Данных")
            st.write(f"Строки: {df.shape[0]}")
            st.write(f"Колонки: {df.shape[1]}")
            st.dataframe(df.head())

        with tab2:
            advanced_filtering(df)

        with tab3:
            advanced_grouping(df)

        with tab4:
            advanced_join(st.session_state)

        with tab5:
            st.write("Здесь будет визуализация")

if __name__ == "__main__":
    main()