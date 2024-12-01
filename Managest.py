import streamlit as st
import requests
import pandas as pd
import time  # Thêm import time để điều khiển tốc độ làm mới

def color_rows(row):
    if (row['muc_do_hai_long'] >= 5 and row['cam_xuc'] in ['tích cực', 'trung tính']):
        return ['background-color: lightgreen'] * len(row)
    elif (row['muc_do_hai_long'] <= 4 and row['cam_xuc'] in ['tiêu cực', 'trung tính']):
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

# Thiết lập giao diện Streamlit
st.title("Quản lý thông tin khách hàng")

# Thêm nút và slider để điều chỉnh tốc độ làm mới
auto_refresh = st.checkbox("Tự động làm mới", value=True)
refresh_rate = st.slider("Tốc độ làm mới (giây)", min_value=1, max_value=60, value=5)

# Nếu tự động làm mới được bật
if auto_refresh:
    # Sử dụng st.empty() để tạo placeholder
    data_placeholder = st.empty()
    
    while True:
        # Lấy dữ liệu mới
        raw_data = fetch_data()
        processed_data = process_data(raw_data)

        if not processed_data.empty:
            # Áp dụng style cho dataframe
            styled_df = processed_data.style.apply(color_rows, axis=1)
            data_placeholder.dataframe(styled_df)
        else:
            data_placeholder.write("Chưa có dữ liệu!")

        # Chờ theo tốc độ làm mới
        time.sleep(refresh_rate)
        
        # Làm mới trang
        st.rerun()

else:
    # Nếu tắt tự động làm mới
    raw_data = fetch_data()
    processed_data = process_data(raw_data)

    if not processed_data.empty:
        # Áp dụng style cho dataframe
        styled_df = processed_data.style.apply(color_rows, axis=1)
        st.dataframe(styled_df)
    else:
        st.write("Chưa có dữ liệu!")