import streamlit as st
import google.generativeai as genai
import requests
import uuid

# Kiểm tra trạng thái nhập tên người dùng
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "name_confirmed" not in st.session_state:
    st.session_state.name_confirmed = False

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4()) 

# Nếu chưa có tên hoặc chưa xác nhận, yêu cầu người dùng nhập và bấm nút xác nhận
if not st.session_state.name_confirmed:
    st.title("Chào mừng đến với Chatbot EmoWatch!")
    user_name_input = st.text_input("Vui lòng nhập tên của bạn:")

    # Nút xác nhận
    confirm_button = st.button("Xác nhận")

    # Khi người dùng bấm nút xác nhận
    if confirm_button:
        if user_name_input.strip():  # Kiểm tra xem tên đã được nhập chưa
            st.session_state.user_name = user_name_input.strip()
            st.session_state.name_confirmed = True
            st.success(f"{st.session_state.user_name} là tên của bạn? Vui lòng bấm xác nhận bắt đầu trò chuyện.")
        else:
            st.error("Vui lòng nhập tên trước khi xác nhận.")
else:
    # Hiển thị giao diện chat sau khi nhập tên và xác nhận
    st.title(f"Chào mừng, {st.session_state.user_name}!")

    # Cấu hình API
    genai.configure(api_key=st.secrets["Gemini_API_Key"])

    # Cấu hình mô hình generative
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    # Chuyển đổi vai trò từ mô hình sang Streamlit
    def translate_role(user_role):
        return "assistant" if user_role == "model" else user_role

    # Khởi tạo lịch sử hội thoại nếu chưa có
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = model.start_chat(history=[])

    # Hiển thị lịch sử chat
    for message in st.session_state.chat_history.history:
        if message.parts[0].text != "feedback_prompt" and not message.parts[0].text.startswith('Đọc câu sau'):
            with st.chat_message(translate_role(message.role)):
                st.markdown(message.parts[0].text)

    def send_data_to_management(user_id, user_name, emotion_score, emotion_type):
        """Gửi thông tin đến trang quản lý qua API."""
        api_url = "http://localhost:8000/api/chat-data/"  # URL API backend
        data = {
            "user_id": user_id, 
            "ten_khach_hang": user_name,
            "muc_do_hai_long": emotion_score,
            "cam_xuc": emotion_type
        }
        try:
            response = requests.post(api_url, json=data, timeout=5)
            if response.status_code == 200:
                st.success("Dữ liệu đã được gửi thành công!")
            else:
                st.error(f"Lỗi khi gửi dữ liệu: {response.status_code}")
        except requests.ConnectionError:
            st.error("Không thể kết nối tới server. Vui lòng kiểm tra server backend.")
        except requests.Timeout:
            st.error("Kết nối tới server bị quá thời gian chờ.")
        except Exception as e:
            st.error(f"Lỗi không xác định: {e}")

    def handle_user_input(prompt):
        if not prompt:
            return

        # Hiển thị câu hỏi của người dùng
        st.chat_message("user").markdown(prompt)

        # Gửi câu hỏi đến mô hình và nhận phản hồi
        gemini_response = st.session_state.chat_history.send_message(prompt)

        # Hiển thị phản hồi từ mô hình
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)

        # Phân tích cảm xúc 
        EmotionScore, EmotionType = handle_feedback(prompt)

        # Gửi dữ liệu tới server quản lý
        send_data_to_management(st.session_state.user_id, st.session_state.user_name, EmotionScore, EmotionType)

    def handle_feedback(prompt):
        feedback_prompt = (
            f'Đọc câu sau: "{prompt}". '
            "Đánh giá theo 2 tiêu chí: mức độ hài lòng trên thang điểm 1-10 và cảm xúc (tích cực/tiêu cực/trung tính). "
            "Nếu câu trên là một trường hợp khẩn cấp có ảnh hưởng xấu thì hãy trả về điểm 1 và cảm xúc tiêu cực"
            "Trả lời ngắn gọn, chỉ cung cấp điểm số và cảm xúc."
        )

        # Tạo một đối tượng tạm thời không ảnh hưởng đến lịch sử chính
        temp_chat = model.start_chat(history=[])
        feedback_response = temp_chat.send_message(feedback_prompt)
        

        # Tách dữ liệu từ phản hồi
        feedback_text = feedback_response.text
        print(feedback_text)
        try:
            parts = feedback_text.split(", ")
            EmotionScore = int(parts[0])
            EmotionType = parts[1]
        except (IndexError, ValueError):
            EmotionScore = 4
            EmotionType = "trung tính"

        return EmotionScore, EmotionType

    # Nhận đầu vào từ người dùng
    user_input = st.chat_input("Ask EmoWatch")
    if user_input:
        handle_user_input(user_input)
