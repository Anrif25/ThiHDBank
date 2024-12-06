import streamlit as st
import requests
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

def color_rows(row):
    if (row['muc_do_hai_long'] >= 5 ):
        return ['background-color: lightgreen'] * len(row)
    elif (row['muc_do_hai_long'] <= 4 or row['cam_xuc'] in ['tiêu cực']):
        return ['background-color: lightyellow'] * len(row)
    return [''] * len(row)

def fetch_data():
    try:
        response = requests.get("http://localhost:8000/api/chat-data/")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Lỗi khi lấy dữ liệu: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Lỗi kết nối tới server: {e}")
        return []

def process_data(data):
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.sort_values(by=["user_id", "timestamp"], ascending=[True, False], inplace=True)
        df = df.drop_duplicates(subset="user_id", keep="first")

    return df

def display_warnings(df, processed_user_ids):
    # Hiển thị cảnh báo cho những khách hàng chưa được xử lý
    for index, row in df.iterrows():
        if row['user_id'] not in processed_user_ids:
            if row['muc_do_hai_long'] <= 4 or row['cam_xuc'] == 'tiêu cực':
                st.warning(f"Khách hàng ở đoạn chat {row['user_id']} cần nhân viên hỗ trợ.")
                processed_user_ids.add(row['user_id'])  # Đánh dấu user_id đã được cảnh báo

def count_emotions(df):
    emotion_counts = df['cam_xuc'].value_counts()
    return emotion_counts

st.title("Quản lý thông tin mức độ hài lòng của khách hàng")

# Tạo hai cột ngang nhau cho checkbox và nút "Lấy dữ liệu mới"
col1, col2 = st.columns([1, 1])

# Đặt checkbox trong cột 1
with col1:
    auto_refresh = st.checkbox("Tự động làm mới", value=True)

# Nút "Lấy dữ liệu mới" chỉ hiển thị khi checkbox không được chọn
if not auto_refresh:
    with col2:
        load_data_button = st.button("Lấy dữ liệu mới")

refresh_rate = st.slider("Tốc độ làm mới (giây)", min_value=1, max_value=5, value=5)

# Tạo ba cột cho bảng dữ liệu, cảnh báo và biểu đồ cảm xúc
col1, col2, col3 = st.columns([1, 1, 1])

# Sử dụng một biến trạng thái cho key để tạo key duy nhất khi tải lại dữ liệu
if auto_refresh:
    with col1:
        st.header("Bảng Dữ Liệu Khách Hàng")
        data_placeholder = st.empty()
    
    with col2:
        st.header("Cảnh Báo")
        warning_placeholder = st.empty()
    
    with col3:
        st.header("Biểu Đồ Cảm Xúc")
        chart_placeholder = st.empty()

    processed_user_ids = set()  # Tạo một set để theo dõi các user_id đã được xử lý

    while True:
        raw_data = fetch_data()
        processed_data = process_data(raw_data)

        if not processed_data.empty:
            with col1:
                # Cập nhật bảng dữ liệu khách hàng
                column_config = {
                    "cam_xuc": st.column_config.TextColumn("Cảm Xúc", width="small"),
                    "muc_do_hai_long": st.column_config.NumberColumn("Mức Độ Hài Lòng", width="small"),
                    "user_id": st.column_config.TextColumn("ID Đoạn chat", width="medium"),
                    "ten_khach_hang": st.column_config.TextColumn("Tên Khách hàng", width="medium")
                }

                # Cập nhật bảng dữ liệu với thông tin mới
                styled_df = processed_data.style.apply(color_rows, axis=1)
                data_placeholder.dataframe(
                    styled_df, 
                    column_config=column_config,
                    use_container_width=True
                )

            with col2:
                # Cập nhật cảnh báo cho những khách hàng mới
                warning_placeholder.empty()
                display_warnings(processed_data, processed_user_ids)
            
            with col3:
                # Cập nhật biểu đồ cảm xúc với key duy nhất cho mỗi biểu đồ
                emotion_counts = count_emotions(processed_data)
                fig = px.bar(
                    x=emotion_counts.index, 
                    y=emotion_counts.values, 
                    labels={'x': 'Cảm Xúc', 'y': 'Số Lượng'},
                    title='Phân Bố Cảm Xúc Khách Hàng',
                    color=emotion_counts.index,
                    color_discrete_map={
                        'tích cực': 'green', 
                        'tiêu cực': 'red', 
                        'trung tính': 'gray'
                    }
                )
                fig.update_layout(
                    xaxis_title='Cảm Xúc', 
                    yaxis_title='Số Lượng Khách Hàng',
                    height=300
                )
                chart_placeholder.plotly_chart(fig, use_container_width=True, key=str(fig))  # Thêm key duy nhất
        
        else:
            with col1:
                data_placeholder.write("Chưa có dữ liệu!")
            with col2:
                warning_placeholder.empty()
            with col3:
                chart_placeholder.empty()

        time.sleep(refresh_rate)
        st.rerun()

else:
    with col1:
        st.header("Bảng Dữ Liệu Khách Hàng")
    
    with col2:
        st.header("Cảnh Báo")
    
    with col3:
        st.header("Biểu Đồ Cảm Xúc")
    
    raw_data = fetch_data()
    processed_data = process_data(raw_data)

    processed_user_ids = set()  # Tạo một set để theo dõi các user_id đã được xử lý

    if not processed_data.empty:
        with col1:
            # Cập nhật bảng dữ liệu khách hàng
            column_config = {
                "cam_xuc": st.column_config.TextColumn("Cảm Xúc", width="small"),
                "muc_do_hai_long": st.column_config.NumberColumn("Mức Độ Hài Lòng", width="small"),
                "user_id": st.column_config.TextColumn("ID đoạn chat", width="medium"),
                "ten_khach_hang": st.column_config.TextColumn("Tên Khách Hàng", width="medium")
            }

            styled_df = processed_data.style.apply(color_rows, axis=1)
            data_placeholder = st.empty()  # Placeholder cho bảng dữ liệu
            data_placeholder.dataframe(
                styled_df, 
                column_config=column_config,
                use_container_width=True
            )
        
        with col2:
            # Cập nhật cảnh báo cho những khách hàng mới
            display_warnings(processed_data, processed_user_ids)
        
        with col3:
            # Cập nhật biểu đồ cảm xúc
            emotion_counts = count_emotions(processed_data)
            fig = px.bar(
                x=emotion_counts.index, 
                y=emotion_counts.values, 
                labels={'x': 'Cảm Xúc', 'y': 'Số Lượng'},
                title='Phân Bố Cảm Xúc Khách Hàng',
                color=emotion_counts.index,
                color_discrete_map={
                    'tích cực': 'green', 
                    'tiêu cực': 'red', 
                    'trung tính': 'gray'
                }
            )
            fig.update_layout(
                xaxis_title='Cảm Xúc', 
                yaxis_title='Số Lượng Khách Hàng',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True, key=str(fig))  # Thêm key duy nhất

    else:
        with col1:
            st.write("Chưa có dữ liệu!")

    # Lấy dữ liệu mới khi nút "Lấy dữ liệu mới" được nhấn
    if load_data_button:
        raw_data = fetch_data()
        processed_data = process_data(raw_data)
