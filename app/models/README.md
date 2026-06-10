# Models Layer

Thư mục `app/models` chứa các lớp Pydantic model dùng để chuẩn hóa dữ liệu khi lưu vào MongoDB và truyền qua repository.

Model bên đây thường khai báo các field, giá trị mặc định, ràng buộc validation và cấu hình `populate_by_name`.

## File trong `app/models`

- `analysis_request.py`
- `business_product.py`
- `business_profile.py`
- `category.py`
- `credit_transaction.py`
- `fashion_trend.py`
- `generated_design.py`
- `project.py`
- `raw_trend_data.py`
- `recommendation.py`
- `style_preset.py`
- `subscription_plan.py`
- `trend_insight.py`
- `user.py`

---

## analysis_request.py

### Chức năng của analysis_request.py

Định nghĩa model cho phiên phân tích AI và trạng thái request.

### Các field chính của analysis_request.py

- `project_id`
- `category_name`
- `status`
- `created_at`
- `updated_at`

---

## business_product.py

### Chức năng của business_product.py

Định nghĩa model sản phẩm thuộc business để lưu trữ và truy vấn.

### Các field chính của business_product.py

- `business_id`
- `name`
- `description`
- `price`
- `image_url`
- `created_at`

---

## business_profile.py

### Chức năng của business_profile.py

Định nghĩa model profile doanh nghiệp và sở thích thời trang.

### Các field chính của business_profile.py

- `user_id`
- `company_name`
- `target_market`
- `business_scale`
- `interest_categories`
- `updated_at`

---

## category.py

### Chức năng của category.py

Định nghĩa model category với parent-child và thời gian tạo.

### Các field chính của category.py

- `name`
- `description`
- `parent_id`
- `created_at`

---

## credit_transaction.py

### Chức năng của credit_transaction.py

Định nghĩa model giao dịch credit gồm nạp và tiêu dùng.

### Các field chính của credit_transaction.py

- `user_id`
- `transaction_type`
- `amount`
- `related_request_id`
- `created_at`

---

## fashion_trend.py

### Chức năng của fashion_trend.py

Định nghĩa model xu hướng thời trang với thông tin category và độ hot.

### Các field chính của fashion_trend.py

- `category_id`
- `trend_name`
- `color_code`
- `material`
- `style`
- `popularity_score`
- `season`
- `created_at`

---

## generated_design.py

### Chức năng của generated_design.py

Định nghĩa model thiết kế AI cùng metadata, URL ảnh và rating người dùng.

### Các field chính của generated_design.py

- `request_id`
- `ai_job_id`
- `ai_metadata`
- `design_image_url`
- `status`
- `updated_at`
- `user_rating`

---

## project.py

### Chức năng của project.py

Định nghĩa model project của người dùng.

### Các field chính của project.py

- `user_id`
- `project_name`
- `description`
- `created_at`

---

## raw_trend_data.py

### Chức năng của raw_trend_data.py

Định nghĩa model dữ liệu thô từ nguồn trend để phân tích sau.

### Các field chính của raw_trend_data.py

- `trend_id`
- `source_type`
- `content_type`
- `raw_payload`
- `collected_at`

---

## recommendation.py

### Chức năng của recommendation.py

Định nghĩa model gợi ý business-trend với action và độ tin cậy.

### Các field chính của recommendation.py

- `business_id`
- `trend_id`
- `action`
- `confidence_score`
- `created_at`

---

## style_preset.py

### Chức năng của style_preset.py

Định nghĩa model style preset dùng để gửi prompt tới AI.

### Các field chính của style_preset.py

- `display_name`
- `ai_prompt_text`
- `thumbnail_url`
- `created_at`

---

## subscription_plan.py

### Chức năng của subscription_plan.py

Định nghĩa model gói đăng ký, credit và tính năng đi kèm.

### Các field chính của subscription_plan.py

- `plan_name`
- `price_per_month`
- `credits_per_month`
- `description`
- `is_popular`
- `features`
- `created_at`

---

## trend_insight.py

### Chức năng của trend_insight.py

Định nghĩa model insight kết quả phân tích trend.

### Các field chính của trend_insight.py

- `request_id`
- `product_name`
- `source_image_url`
- `positive_rate`
- `total_reviews`
- `created_at`

---

## user.py

### Chức năng của user.py

Định nghĩa model người dùng với thông tin đăng nhập và credit.

### Các field chính của user.py

- `username`
- `email`
- `password_hash`
- `role`
- `available_credits`
- `created_at`
