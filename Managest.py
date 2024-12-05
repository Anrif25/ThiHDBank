import streamlit as st
import requests
import pandas as pd
import time

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

def display_warnings(df):
    """
    Hiển thị cảnh báo cho các hàng có điều kiện thỏa mãn.
    """
    for index, row in df.iterrows():
        if row['muc_do_hai_long'] <= 4 or row['cam_xuc'] == 'tiêu cực':
            st.warning(f"Khách hàng ở đoạn chat {row['user_id']} cần nhân viên hỗ trợ.")

st.title("Quản lý thông tin mức độ hài lòng của khách hàng")

auto_refresh = st.checkbox("Tự động làm mới", value=True)
refresh_rate = st.slider("Tốc độ làm mới (giây)", min_value=1, max_value=5, value=5)

# Tạo hai cột với kích thước phù hợp
col1, col2 = st.columns([1, 1])  # Cột bên trái rộng hơn



# Nếu tự động làm mới được bật
if auto_refresh:
    # Sử dụng st.empty() cho mỗi cột
    with col1:
        st.header("Bảng Dữ Liệu Khách Hàng")
        data_placeholder = st.empty()
    
    with col2:
        st.header("Cảnh Báo")
        warning_placeholder = st.empty()
    
    while True:
        # Lấy dữ liệu mới
        raw_data = fetch_data()
        processed_data = process_data(raw_data)

        if not processed_data.empty:
            # Hiển thị dữ liệu và cảnh báo
            with col1:
                # Cấu hình độ rộng cột
                column_config = {
                    "cam_xuc": st.column_config.TextColumn(
                        "Cảm Xúc", 
                        width="small"
                    ),
                    "muc_do_hai_long": st.column_config.NumberColumn(
                        "Mức Độ Hài Lòng", 
                        width="small"
                    ),
                    "user_id": st.column_config.TextColumn(
                        "ID Đoạn chat", 
                        width="medium"
                    ),
                    "ten_khach_hang": st.column_config.TextColumn(
                        "Tên Khách hàng", 
                        width="medium"
                    )
                }
                
                styled_df = processed_data.style.apply(color_rows, axis=1)
                # Sử dụng use_container_width=True để hiển thị đầy đủ
                data_placeholder.dataframe(
                    styled_df, 
                    column_config=column_config,
                    use_container_width=True
                )
            
            # Xóa các cảnh báo cũ và hiển thị cảnh báo mới
            with col2:
                warning_placeholder.empty()
                with warning_placeholder.container():
                    display_warnings(processed_data)
        else:
            with col1:
                data_placeholder.write("Chưa có dữ liệu!")
            with col2:
                warning_placeholder.empty()

        # Chờ theo tốc độ làm mới
        time.sleep(refresh_rate)
        
        # Làm mới trang
        st.rerun()

else:
    # Nếu tắt tự động làm mới
    with col1:
        st.header("Bảng Dữ Liệu Khách Hàng")
    
    with col2:
        st.header("Cảnh Báo")
    
    raw_data = fetch_data()
    processed_data = process_data(raw_data)

    if not processed_data.empty:
        # Hiển thị dữ liệu ở cột bên trái
        with col1:
            # Cấu hình độ rộng cột
            column_config = {
                "cam_xuc": st.column_config.TextColumn(
                    "Cảm Xúc", 
                    width="small"
                ),
                "muc_do_hai_long": st.column_config.NumberColumn(
                    "Mức Độ Hài Lòng", 
                    width="small"
                ),
                "user_id": st.column_config.TextColumn(
                    "ID đoạn chat", 
                    width="medium"
                ),
                "ten_khach_hang": st.column_config.TextColumn(
                    "Tên Khách Hàng", 
                    width="medium"
                )
            }
            
            styled_df = processed_data.style.apply(color_rows, axis=1)
            # Sử dụng use_container_width=True để hiển thị đầy đủ
            st.dataframe(
                styled_df, 
                column_config=column_config,
                use_container_width=True
            )
        
        # Hiển thị cảnh báo ở cột bên phải
        with col2:
            display_warnings(processed_data)
    else:
        with col1:
            st.write("Chưa có dữ liệu!")