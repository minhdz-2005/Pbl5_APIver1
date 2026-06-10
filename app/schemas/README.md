# Schemas Layer

Thư mục `app/schemas` định nghĩa các schema Pydantic dùng để validate, serialize và deserialize dữ liệu giữa API và ứng dụng.

## Mục đích chung

- Định nghĩa request/response payload cho các endpoint.
- Kiểm tra kiểu dữ liệu, giá trị hợp lệ và alias cho ObjectId.
- Tăng tính nhất quán giữa model lưu trữ và API.

## File trong `app/schemas`

- `analysis_request.py`
- `auth.py`
- `business_product.py`
- `business_profile.py`
- `category.py`
- `credit_transaction.py`
- `fashion_trend.py`
- `generated_design.py`
- `project.py`
- `raw_trend_data.py`
- `recommendation.py`
- `recommendation_repository.py`
- `style_preset.py`
- `subscription_plan.py`
- `token.py`
- `trend_insight.py`
- `trend_result.py`
- `user.py`

---

## analysis_request.py

### Chức năng của analysis_request.py

Định nghĩa schema cho các request phân tích, callback AI image và các trạng thái của analysis request.

### Các schema chính của analysis_request.py

- `RequestStatus`: enum trạng thái của request.
- `AnalysisRequestBase`: base schema cho `project_id` và `category_name`.
- `AnalysisRequestCreate`: schema tạo request.
- `ImageGenerationRequest`: payload gửi tới AI image generation.
- `AIImageCallbackData`: callback dữ liệu từ AI server.
- `AnalysisRequestUpdate`: schema cập nhật trạng thái và selected trend.
- `AnalysisRequestRead`: schema đọc request với `id`, `status`, `created_at`, `updated_at`.

---

## auth.py

### Chức năng của auth.py

Định nghĩa schema cho đăng nhập, đăng ký, thay đổi mật khẩu và response token người dùng.

### Các schema chính của auth.py

- `LoginRequest`
- `UserResponse`
- `LoginResponse`
- `RegisterRequest`
- `RegisterResponse`
- `ChangePasswordRequest`
- `ChangePasswordResponse`

---

## business_product.py

### Chức năng của business_product.py

Định nghĩa các schema CRUD cho business product.

### Các schema chính của business_product.py

- `BusinessProductBase`
- `BusinessProductCreate`
- `BusinessProductUpdate`
- `BusinessProductRead`

---

## business_profile.py

### Chức năng của business_profile.py

Định nghĩa schema cho business profile và quan hệ với categories.

### Các schema chính của business_profile.py

- `BusinessProfileBase`
- `BusinessProfileCreate`
- `BusinessProfileUpdate`
- `BusinessProfileRead`
- `BusinessInterestsUpdate`
- `BusinessInterestsRead`

---

## category.py

### Chức năng của category.py

Định nghĩa schema category với khả năng tạo cây phân cấp.

### Các schema chính của category.py

- `CategoryBase`
- `CategoryCreate`
- `CategoryUpdate`
- `CategoryRead`
- `CategoryTree`

---

## credit_transaction.py

### Chức năng của credit_transaction.py

Định nghĩa schema cho giao dịch nạp/xài credit.

### Các schema chính của credit_transaction.py

- `TransactionType`: enum `TOP_UP`/`USAGE`.
- `CreditTransactionBase`
- `CreditTransactionCreate`
- `CreditTransactionRead`

---

## fashion_trend.py

### Chức năng của fashion_trend.py

Định nghĩa schema cho xu hướng thời trang.

### Các schema chính của fashion_trend.py

- `FashionTrendBase`
- `FashionTrendCreate`
- `FashionTrendUpdate`
- `FashionTrendRead`

---

## generated_design.py

### Chức năng của generated_design.py

Định nghĩa schema cho các thiết kế AI đã tạo.

### Các schema chính của generated_design.py

- `GeneratedDesignBase`
- `GeneratedDesignCreate`
- `GeneratedDesignUpdate`
- `GeneratedDesignRead`

---

## project.py

### Chức năng của project.py

Định nghĩa schema cho dự án người dùng.

### Các schema chính của project.py

- `ProjectBase`
- `ProjectCreate`
- `ProjectUpdate`
- `ProjectRead`

---

## raw_trend_data.py

### Chức năng của raw_trend_data.py

Định nghĩa schema cho dữ liệu thô thu thập từ nguồn trending.

### Các schema chính của raw_trend_data.py

- `RawTrendDataBase`
- `RawTrendDataCreate`
- `RawTrendDataRead`
- `RawTrendDataUpdate`

---

## recommendation.py

### Chức năng của recommendation.py

Định nghĩa schema cho đề xuất (recommendation) giữa business và trend.

### Các schema chính của recommendation.py

- `ActionEnum`
- `RecommendationBase`
- `RecommendationCreate`
- `RecommendationRead`

---

## recommendation_repository.py

### Ghi chú cho recommendation_repository.py

File này nằm trong thư mục `app/schemas` nhưng thực chất định nghĩa một repository chứ không phải một schema. Nếu cần, có thể chuyển sang `app/repositories` để đúng kiến trúc.

---

## style_preset.py

### Chức năng của style_preset.py

Định nghĩa schema cho style preset và prompt AI.

### Các schema chính của style_preset.py

- `StylePresetBase`
- `StylePresetCreate`
- `StylePresetUpdate`
- `StylePresetRead`

---

## subscription_plan.py

### Chức năng của subscription_plan.py

Định nghĩa schema cho gói đăng ký, giá, credit và tính năng.

### Các schema chính của subscription_plan.py

- `SubscriptionPlanBase`
- `SubscriptionPlanCreate`
- `SubscriptionPlanUpdate`
- `SubscriptionPlanRead`

---

## token.py

### Chức năng của token.py

Định nghĩa schema token JWT và payload.

### Các schema chính của token.py

- `Token`
- `TokenPayload`

---

## trend_insight.py

### Chức năng của trend_insight.py

Định nghĩa schema cho báo cáo insight từ trend.

### Các schema chính của trend_insight.py

- `TrendInsightBase`
- `TrendInsightCreate`
- `TrendInsightRead`

---

## trend_result.py

### Chức năng của trend_result.py

Định nghĩa schema cho kết quả phân tích trend AI.

### Các schema chính của trend_result.py

- `ScoringSignals`
- `TrendResultBase`
- `TrendResultCreate`
- `TrendResultUpdate`
- `TrendResultRead`

---

## user.py

### Chức năng của user.py

Định nghĩa schema người dùng gồm tạo, đọc và cập nhật tài khoản.

### Các schema chính của user.py

- `UserRole`
- `UserBase`
- `UserCreate`
- `UserRead`
- `UserUpdate`

---

## Gợi ý cải thiện

- `recommendation_repository.py` nên được chuyển về `app/repositories` vì đó là repository implementation, không phải schema.
- Các schema `Read` hiện dùng `Field(..., alias="_id")` để map ObjectId từ MongoDB.
- Nếu muốn chuẩn hóa, có thể thêm schema `BaseResponse` hoặc dùng `ConfigDict` chung cho tất cả `Read` schema.
