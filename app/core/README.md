# Core Layer

Thư mục `app/core` chứa cấu hình chung và các tiện ích cơ bản cho ứng dụng.
Các module ở đây hỗ trợ:

- Cấu hình môi trường và biến setting.
- Kết nối đến MongoDB bằng Motor.
- Bảo mật JWT và mã hóa mật khẩu.
- Cấu hình Cloudinary để upload ảnh.

## File trong `app/core`

- `cloudinary.py`
- `config.py`
- `database.py`
- `security.py`

---

## config.py

### Chức năng của config.py

Định nghĩa lớp `Settings` dùng `pydantic_settings` để đọc cấu hình từ:

- Biến môi trường
- File `.env`

### Các thiết lập chính của config.py

- `PROJECT_NAME`
- `API_V1_STR` và `API_V2_STR`
- `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- `MONGO_DETAILS`, `DATABASE_NAME`
- `AI_SERVER_URL`, `BACKEND_URL`
- `CLOUDINARY_*`

---

## database.py

### Chức năng của database.py

Quản lý kết nối MongoDB và index khi ứng dụng khởi chạy.

### Các hàm chính của database.py

- `connect_to_mongo()`
- `setup_indexes()`
- `close_mongo_connection()`
- `get_database()`

---

## security.py

### Chức năng của security.py

Cung cấp các helper bảo mật JWT và mật khẩu cho toàn bộ Backend.

### Các hàm chính của security.py

- `create_access_token(subject, expires_delta)`
- `verify_password(plain_password, hashed_password)`
- `get_password_hash(password)`
- `get_current_user(token, db)`

---

## cloudinary.py

### Chức năng của cloudinary.py

Cấu hình `cloudinary` dựa trên biến môi trường.

### Các hành vi chính của cloudinary.py

- Mask thông tin nhạy cảm khi log config
- Cấu hình cloudinary từ `CLOUDINARY_URL` nếu có
- Nếu không, cấu hình từ `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY` và `CLOUDINARY_API_SECRET`
- Log lỗi khi cấu hình thất bại
