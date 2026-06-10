# PBL5 Fashion Trend Analysis API

Dự án backend FastAPI cho hệ thống phân tích xu hướng thời trang và tạo thiết kế AI cho các doanh nghiệp thời trang.

## 📋 Tổng quan dự án

PBL5 là nền tảng giúp các doanh nghiệp thời trang:

- Phân tích xu hướng thời trang từ nhiều nguồn (TikTok, Instagram, Pinterest, v.v.)
- Nhận gợi ý sản phẩm dựa trên AI
- Tạo thiết kế sản phẩm thông qua API AI
- Quản lý project, gói đăng ký và credit

---

## 🏗️ Kiến trúc dự án

```text
app/
├── api/                  # API Router và Endpoints
│   ├── deps.py          # Dependencies chung
│   ├── v1/              # API Version 1
│   └── v2/              # API Version 2 (Recommended)
├── core/                # Cấu hình và helpers chung
│   ├── config.py        # Biến môi trường
│   ├── database.py      # MongoDB connection
│   ├── security.py      # JWT và mật khẩu
│   └── cloudinary.py    # Cloudinary config
├── models/              # Pydantic models cho DB
├── schemas/             # Pydantic schemas cho API request/response
├── repositories/        # Data access layer
├── services/            # Business logic
└── main.py             # FastAPI app entry point
```

---

## 📚 Chi tiết các module

Xem chi tiết mô tả từng layer:

- [API Layer](app/api/README.md) - Router, dependencies và endpoints
- [Core Layer](app/core/README.md) - Cấu hình, database, security, cloudinary
- [Models Layer](app/models/README.md) - Pydantic models cho MongoDB
- [Schemas Layer](app/schemas/README.md) - Pydantic schemas cho API
- [Repositories Layer](app/repositories/README.md) - Data access layer
- [Services Layer](app/services/README.md) - Business logic

---

## 🚀 Cách chạy dự án

### Yêu cầu

- Python 3.10+
- MongoDB (hoặc MongoDB Atlas)
- Cloudinary account
- AI Server (xem `.env`)

### Setup

1. Clone repository và vào thư mục

```bash
cd d:\PBL5_DA_CNPM\APIver1
```

1. Tạo virtual environment

```bash
python -m venv venv
```

1. Kích hoạt virtual environment

```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# hoặc Windows CMD
venv\Scripts\activate.bat
```

1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

1. Tạo file `.env`

```bash
# API Metadata
PROJECT_NAME=pbl5 fastapi app
API_V1_STR=/api
API_V2_STR=/api/v2

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# MongoDB
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=pbl5

# AI Server
AI_SERVER_URL=http://your_ai_server:port

# Backend
BACKEND_URL=http://localhost:8000

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
CLOUDINARY_URL=cloudinary://key:secret@cloud_name
```

1. Chạy ứng dụng

```bash
python -m uvicorn app.main:app --reload
```

Ứng dụng sẽ chạy tại `http://localhost:8000`

---

## 📖 API Documentation

Swagger UI: `http://localhost:8000/docs`

ReDoc: `http://localhost:8000/redoc`

---

## 🔐 Xác thực

Hệ thống sử dụng **JWT (JSON Web Tokens)** cho xác thực.

### Luồng đăng nhập

1. User gọi endpoint `/api/v2/auth/login` với email/password
2. Server trả về `access_token` (JWT)
3. Client gửi kèm token trong header: `Authorization: Bearer <token>`
4. Server xác thực token qua `get_current_user` dependency

---

## 💳 Hệ thống Credit

- User mặc định nhận **100 credits** khi tạo tài khoản
- Có thể nạp thêm credit qua gói đăng ký (`subscription_plans`)
- Mỗi lần sử dụng API tính lệ phí credit

---

## 📊 Endpoints chính

### API V2 (Recommended)

#### Authentication

- `POST /api/v2/auth/login` - Đăng nhập
- `POST /api/v2/auth/register` - Đăng ký

#### Users

- `GET /api/v2/users/me` - Lấy thông tin user hiện tại
- `PUT /api/v2/users/{user_id}` - Cập nhật thông tin user

#### Projects

- `GET /api/v2/projects` - Lấy danh sách project
- `POST /api/v2/projects` - Tạo project mới

#### Analysis Requests

- `POST /api/v2/analysis_requests` - Tạo phiên phân tích
- `GET /api/v2/analysis_requests/{request_id}` - Lấy chi tiết phiên phân tích

#### Generated Designs

- `GET /api/v2/generated_designs/{request_id}` - Lấy thiết kế AI

#### Admin

- `GET /api/v2/admin/stats` - Lấy thống kê hệ thống

---

## 🗂️ Database Schema (MongoDB)

### Collections chính

- `users` - Tài khoản người dùng
- `business_profiles` - Profile doanh nghiệp
- `projects` - Project của user
- `analysis_requests` - Phiên phân tích
- `generated_designs` - Thiết kế AI tạo
- `trend_insights` - Kết quả phân tích trend
- `fashion_trends` - Xu hướng thời trang
- `style_presets` - Phong cách thiết kế sẵn có
- `subscription_plans` - Gói đăng ký
- `credit_transactions` - Giao dịch credit

---

## 🔄 Luồng chính

### Phân tích xu hướng

1. User tạo project
2. User gọi `/analysis_requests` để bắt đầu phân tích
3. Backend gửi request tới AI Server
4. AI Server trả về kết quả
5. Backend lưu vào `generated_designs` và `trend_insights`
6. User nhận được gợi ý

---

## 🛠️ Công nghệ sử dụng

- **FastAPI** - Web framework
- **MongoDB + Motor** - Database async
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Cloudinary** - Image upload
- **Alembic** - Database migrations (nếu cần)

---

## 📝 Quy ước code

- Sử dụng snake_case cho tên biến, hàm, module
- Sử dụng PascalCase cho tên class
- Thêm type hints cho tất cả functions
- Viết docstring cho functions công cộng
- Validate dữ liệu qua Pydantic schemas

---

## 🐛 Troubleshooting

### Lỗi kết nối MongoDB

```text
MDB: connection error
```

**Giải pháp:**

- Kiểm tra `DATABASE_URL` trong `.env`
- Kiểm tra network connectivity
- Nếu dùng MongoDB Atlas, thêm IP của máy vào whitelist

### Lỗi Cloudinary

```text
Failed to configure Cloudinary
```

**Giải pháp:**

- Kiểm tra `CLOUDINARY_*` variables trong `.env`
- Nếu dùng `CLOUDINARY_URL`, đảm bảo format đúng

### Lỗi JWT

```text
Could not validate credentials
```

**Giải pháp:**

- Kiểm tra `SECRET_KEY` có đúng không
- Kiểm tra token chưa hết hạn

---

## 📞 Support

Nếu có bất kỳ câu hỏi hoặc vấn đề, vui lòng liên hệ team phát triển.

---

## 📄 Giấy phép

Project này được phát triển cho mục đích giáo dục.
