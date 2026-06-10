# Services Layer

Thư mục `app/services` chứa các module xử lý logic nghiệp vụ liên quan đến AI, sinh ảnh và upload ảnh.

## File

- `analyze_trend.py`
- `generate_images.py`
- `uploadImgtoCloudinary.py`

---

## analyze_trend.py

### Mục đích của analyze_trend.py

Xử lý luồng phân tích xu hướng AI cho một `Analysis Request`.

### Chức năng chính của analyze_trend.py

- `call_ai_trend_analysis(request_id: str, db: AsyncIOMotorDatabase)`
  - Tải `Analysis Request` từ MongoDB.
  - Cập nhật trạng thái sang `ANALYZING_AI`.
  - Đọc dữ liệu sản phẩm từ file JSON `src_img/formatted_products_reviews.json`.
  - Chuẩn hóa dữ liệu sản phẩm và tạo payload gửi tới AI Server.
  - Gọi endpoint AI Server ở `settings.AI_SERVER_URL`.
  - Lưu kết quả vào collection `trend_results`.
  - Cập nhật trạng thái `analysis_requests` thành `COMPLETED` hoặc `FAILED`.

### Ghi chú cho analyze_trend.py

- Dữ liệu sản phẩm hiện lấy từ file cứng `src_img/formatted_products_reviews.json`.
- Nếu file không tồn tại hoặc JSON không hợp lệ, hàm sẽ ghi thông báo lỗi và đánh dấu request `FAILED`.
- Kết quả AI được lưu dưới dạng bản ghi `trend_results` cùng với `analysis_request_id`.
- Đã có logic để chọn `top_trend`, nhưng phần gọi `request_ai_image_generation` đang bị comment.

---

## generate_images.py

### Mục đích của generate_images.py

Quản lý yêu cầu sinh ảnh AI và đồng bộ kết quả từ AI Server về hệ thống.

### Chức năng chính của generate_images.py

- `request_ai_image_generation(db: AsyncIOMotorDatabase, request_id: str, target_style_prompt: str, base_image_url: str, target_season: str = "Spring", target_audience: str = "General", target_weather: str = "Rainy", num_images: int = 3, seed: int = 42, canny_low_threshold: int = 155, canny_high_threshold: int = 255)`
  - Cập nhật `analysis_requests` sang trạng thái `GENERATING_IMAGES`.
  - Gửi payload tới AI Server để tạo job.
  - Lưu `job_id` nhận được về request.
  - Gọi `sync_ai_design_results` để lấy và lưu kết quả thiết kế.

- `sync_ai_design_results(request_id: str, job_id: str, db: AsyncIOMotorDatabase)`
  - Lấy chi tiết job từ AI Server.
  - Kiểm tra danh sách thiết kế được generate.
  - Lưu từng thiết kế vào nội bộ qua route POST tới `INTERNAL_DESIGN_POST_URL`.
  - Hiện comment phần cập nhật trạng thái request sau khi sync.

### Ghi chú cho generate_images.py

- Có log debug giúp theo dõi trạng thái và payload gửi tới AI.
- `ai_metadata` được lưu lại để chứa tất cả dữ liệu gốc từ AI Server.
- `sync_ai_design_results` hiện đang POST lại kết quả vào endpoint nội bộ thay vì chèn trực tiếp vào DB.

---

## uploadImgtoCloudinary.py

### Mục đích của uploadImgtoCloudinary.py

Upload ảnh từ URL lên Cloudinary và trả về thông tin file đã upload.

### Chức năng chính của uploadImgtoCloudinary.py

- `upload_image_to_cloudinary(folder_name: str, image_url: str, generated_design_id: str) -> Dict[str, Any]`
  - Tải ảnh từ `image_url` bằng `httpx`.
  - Cấu hình Cloudinary thông qua `settings`.
  - Upload ảnh bằng `cloudinary.uploader.upload` trong `asyncio.to_thread`.
  - Trả về `cloudinary_url`, `public_id`, `design_id`, và raw response.
  - Nếu upload thất bại, trả về object chứa `error` thay vì raise.

### Ghi chú cho uploadImgtoCloudinary.py

- SDK Cloudinary là blocking, nên được chạy trong thread worker.
- Có nhiều bước cấu hình dự phòng: dùng `settings.CLOUDINARY_URL` nếu có, nếu không thì định nghĩa trực tiếp các biến config.
- Nếu tải ảnh không thành công, hàm vẫn trả về cấu trúc lỗi rõ ràng.

---

## Tổng quan kiến trúc

- `analyze_trend.py` xử lý luồng phân tích xu hướng và tạo payload dữ liệu sản phẩm cho AI.
- `generate_images.py` điều phối việc gọi AI image generation và đồng bộ kết quả thiết kế vào hệ thống.
- `uploadImgtoCloudinary.py` xử lý upload ảnh đã tạo lên Cloudinary.

## Đề xuất cải thiện

- Tách file `src_img/formatted_products_reviews.json` thành nguồn dữ liệu riêng hoặc collection DB để tránh hardcode dữ liệu trong service.
- Bổ sung `settings.INTERNAL_API_TOKEN` nếu endpoint nội bộ yêu cầu bảo mật.
- Hoàn thiện phần gọi `request_ai_image_generation` trong `analyze_trend.py` nếu muốn tự động chạy bước sinh ảnh sau khi phân tích trend.
- Thêm unit test cho từng service để kiểm tra behavior khi mất file JSON, lỗi AI Server, upload ảnh thất bại.
