# API Layer

Thư mục `app/api` chứa các router, dependencies và định nghĩa endpoint cho FastAPI.

Nó được chia thành:

- `deps.py`: dependency chung cho các router (ví dụ: xác thực người dùng)
- `v1/`: API version 1
- `v2/`: API version 2

## File trong `app/api`

- `deps.py`
- `v1/router.py`
- `v2/router.py`

---

## deps.py

### Chức năng của deps.py

Cung cấp dependency chung cho API version 1, bao gồm:

- `get_current_user(token)`
- `get_current_active_user(current_user)`

### Nội dung chính của deps.py

- Xử lý giải mã JWT token
- Kiểm tra token hợp lệ
- Kiểm tra trạng thái active của người dùng

---

## v1/router.py

### Chức năng của v1/router.py

Đăng ký các router endpoint cho API version 1.

### Các router chính trong v1

- `users` với prefix `/users`
- `categories` với prefix `/categories`
- `business_profiles` với prefix `/business-profile`
- `businesses` với prefix `/businesses`
- `login` với prefix `/auth`

---

## v2/router.py

### Chức năng của v2/router.py

Đăng ký các router endpoint cho API version 2.

### Các router chính trong v2

- `auth` với prefix `/auth`
- `users` với prefix `/users`
- `subscription_plans` với prefix `/subscription_plans`
- `analysis_requests` với prefix `/analysis_requests`
- `credit_transactions` với prefix `/credit_transactions`
- `generated_designs` với prefix `/generated_designs`
- `projects` với prefix `/projects`
- `style_presets` với prefix `/style_presets`
- `trend_insights` với prefix `/trend_insights`
- `billing` với prefix `/billing`
- `trend_result` với prefix `/trend-results`
- `admin` với prefix `/admin`

---

## Gợi ý tổ chức

- `v1` nên giữ các tính năng cơ bản và cũ.
- `v2` nên chứa các endpoint mới, phân tách tường minh và hỗ trợ các route admin, billing, trend insights.
- Các endpoint nên chứa các schema request/response cụ thể để đảm bảo validate đầu vào.
