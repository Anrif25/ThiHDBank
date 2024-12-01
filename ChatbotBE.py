from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

# Danh sách lưu trữ dữ liệu chat (ví dụ sử dụng bộ nhớ tạm thời)
chat_data = []

# Định nghĩa mô hình dữ liệu
class ChatData(BaseModel):
    user_id: str
    ten_khach_hang: str
    muc_do_hai_long: int
    cam_xuc: str

@app.post("/api/chat-data/")
async def create_chat_data(chat_data_entry: ChatData):
    # Tìm và xóa bản ghi cũ với user_id trùng nhau
    global chat_data
    chat_data = [entry for entry in chat_data if entry['user_id'] != chat_data_entry.dict()['user_id']]
    
    # Thêm bản ghi mới
    chat_data.append(chat_data_entry.dict())
    
    return {"message": "Dữ liệu đã được lưu thành công!"}

@app.get("/api/chat-data/")
async def get_chat_data():
    # Trả về dữ liệu đã lưu
    return chat_data
