# Repositories Layer

Thư mục `app/repositories` chứa các lớp truy cập dữ liệu (repository) cho từng collection MongoDB.
Các class ở đây chịu trách nhiệm:

- Tương tác với database Motor/MongoDB.
- Chuyển đổi dữ liệu giữa schema và document.
- Thực hiện truy vấn, update, delete và các logic truy xuất nâng cao.

## File trong `app/repositories`

- `analysis_repository.py`
- `business_repository.py`
- `category_repository.py`
- `design_repository.py`
- `insight_repository.py`
- `product_repository.py`
- `project_repository.py`
- `raw_trend_repository.py`
- `style_repository.py`
- `subscription_repository.py`
- `transaction_repository.py`
- `trend_repository.py`
- `trend_result_repository.py`
- `user_repository.py`

---

## analysis_repository.py

### Chức năng của analysis_repository.py

Quản lý truy vấn cho collection `analysis_requests`.

### Các phương thức chính của analysis_repository.py

- `create(req_in: AnalysisRequestCreate)`
- `get_by_project(project_id: str)`
- `get_by_id(req_id: str)`
- `update_status(req_id: str, status: str)`
- `delete(req_id: str)`

---

## business_repository.py

### Chức năng của business_repository.py

Quản lý business profile và các thao tác CRUD theo `user_id`.

### Các phương thức chính của business_repository.py

- `create(profile_in: BusinessProfileCreate)`
- `get_by_user_id(user_id: str)`
- `get_by_id(profile_id: str)`
- `update_by_user_id(user_id: str, profile_in: BusinessProfileUpdate)`
- `delete_by_user_id(user_id: str)`

---

## category_repository.py

### Chức năng của category_repository.py

Quản lý category tree, danh mục gốc, danh mục con và cập nhật danh mục.

### Các phương thức chính của category_repository.py

- `create(cat_in: CategoryCreate)`
- `get_all_roots()`
- `get_children(parent_id: str)`
- `get_by_id(cat_id: str)`
- `update(cat_id: str, cat_in: CategoryUpdate)`
- `delete(cat_id: str)`

---

## design_repository.py

### Chức năng của design_repository.py

Quản lý generated design, cập nhật rating và thống kê trạng thái thiết kế AI.

### Các phương thức chính của design_repository.py

- `create(design_in: GeneratedDesignCreate)`
- `get_by_request(request_id: str)`
- `update_rating(design_id: str, rating: int)`
- `get_by_id(design_id: str)`
- `get_success_rate()`
- `count_active_generations()`

---

## insight_repository.py

### Chức năng của insight_repository.py

Lưu và truy vấn trend insights biết kết quả phân tích.

### Các phương thức chính của insight_repository.py

- `create(insight_in: TrendInsightCreate)`
- `create_many(insights_in: List[TrendInsightCreate])`
- `get_by_request(request_id: str)`
- `get_by_id(insight_id: str)`
- `delete_by_request(request_id: str)`

---

## product_repository.py

### Chức năng của product_repository.py

Quản lý sản phẩm thuộc business, bao gồm CRUD theo `business_id`.

### Các phương thức chính của product_repository.py

- `create(product_in: BusinessProductCreate)`
- `get_by_business(business_id: str)`
- `get_by_id(product_id: str)`
- `update(product_id: str, product_in: BusinessProductUpdate)`
- `delete(product_id: str)`

---

## project_repository.py

### Chức năng của project_repository.py

Quản lý project người dùng và các truy vấn liên quan đến `user_id`.

### Các phương thức chính của project_repository.py

- `create(user_id: str, project_in: ProjectCreate)`
- `get_by_user(user_id: str)`
- `get_by_id(project_id: str)`
- `update(project_id: str, project_in: ProjectUpdate)`
- `delete(project_id: str)`

---

## raw_trend_repository.py

### Chức năng của raw_trend_repository.py

Lưu và truy vấn dữ liệu thô thu thập từ nguồn trend.

### Các phương thức chính của raw_trend_repository.py

- `create(raw_in: RawTrendDataCreate)`
- `create_many(items_in: List[RawTrendDataCreate])`
- `get_by_source(source: str, limit: int = 100)`
- `get_by_id(raw_id: str)`
- `assign_trend(raw_id: str, trend_id: str)`
- `delete_old_data(days: int = 30)`

---

## style_repository.py

### Chức năng của style_repository.py

Quản lý style preset để người dùng chọn phong cách thiết kế.

### Các phương thức chính của style_repository.py

- `create(style_in: StylePresetCreate)`
- `get_all()`
- `get_by_id(style_id: str)`
- `update(style_id: str, style_in: StylePresetUpdate)`
- `delete(style_id: str)`

---

## subscription_repository.py

### Chức năng của subscription_repository.py

Quản lý gói đăng ký và các thao tác CRUD tương ứng.

### Các phương thức chính của subscription_repository.py

- `create(...)`
- `get_all()`
- `get_by_id(...)`
- `update(...)`
- `delete(...)`

---

## transaction_repository.py

### Chức năng của transaction_repository.py

Quản lý giao dịch credit, lịch sử và thống kê tổng credits đã bán.

### Các phương thức chính của transaction_repository.py

- `create_transaction(tx_in: CreditTransactionCreate)`
- `get_history_by_user(user_id: str, limit: int = 50)`
- `get_all_transactions(limit: int | None = None)`
- `get_total_credits_sold()`
- `get_by_id(tx_id: str)`

---

## trend_repository.py

### Chức năng của trend_repository.py

Quản lý xu hướng thời trang và truy vấn trend theo category.

### Các phương thức chính của trend_repository.py

- `create(trend_in: FashionTrendCreate)`
- `get_by_id(trend_id: str)`
- `get_trends_by_category(category_id: str)`
- `get_top_trends(limit: int = 10)`
- `update(trend_id: str, trend_in: FashionTrendUpdate)`
- `delete(trend_id: str)`

---

## trend_result_repository.py

### Chức năng của trend_result_repository.py

Quản lý kết quả phân tích trend, bao gồm truy vấn theo request và cập nhật result.

### Các phương thức chính của trend_result_repository.py

- `get_by_request_id(request_id: str)`
- `get_one(trend_id: str)`
- `delete(trend_id: str)`
- `update(trend_id: str, data: dict)`

---

## user_repository.py

### Chức năng của user_repository.py

Quản lý người dùng, bao gồm đăng ký, kiểm tra email/username, cập nhật, nạp credit và analytics.

### Các phương thức chính của user_repository.py

- `hash_password(password: str)`
- `check_email_exists(email: str)`
- `check_username_exists(username: str)`
- `create(user_in: UserCreate)`
- `get_by_id(user_id: str)`
- `get_by_email(email: str)`
- `get_all()`
- `update(user_id: str, user_in: UserUpdate)`
- `delete(user_id: str)`
- `topup_credit(user_id: str, amount: int)`
- `count_users()`
- `get_user_growth_by_month()`
