import httpx
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from app.core.config import settings
from app.services.generate_images import request_ai_image_generation

# Giả định URL AI Server, bạn nên đưa vào file .env
AI_SERVER_URL = f"{settings.AI_SERVER_URL}/analyze-trend"

logger = logging.getLogger(__name__)

async def call_ai_trend_analysis(request_id: str, db: AsyncIOMotorDatabase):
    """
    Hàm chạy ngầm: Lấy dữ liệu từ DB -> Gọi AI Server -> Cập nhật kết quả
    """
    try:
        # 1. Lấy thông tin chi tiết của Analysis Request
        # Giả sử bạn cần lấy thêm thông tin sản phẩm từ một collection khác (ví dụ 'products')
        analysis_req = await db["analysis_requests"].find_one({"_id": ObjectId(request_id)})
        if not analysis_req:
            return

        # 2. Cập nhật trạng thái sang ANALYZING_AI
        await db["analysis_requests"].update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "ANALYZING_AI", "updated_at": datetime.utcnow()}}
        )

        # 3. Chuẩn bị dữ liệu gửi đi (Mapping theo schema AI Server yêu cầu)
        # Lưu ý: Phần 'products' này bạn cần query dựa trên project_id hoặc category_name của request
        # products_cursor = db["products"].find({"project_id": analysis_req["project_id"]}).limit(20)
        products_cursor = [
            {
                "product_name": "Vest nam, Áo vets nam chất liệu KAKI thô dày dặn...", 
                "image_url": "https://img.lazcdn.com/g/ff/kf/S9a0617ab39034ee48328bc9fcb3b2514y.jpg",
                "reviews": [
                    "Chất liệu KAKI thô dày dặn",
                    "Ít nhăn, ít nhàu",
                    "Kiểu dáng tay lỡ trẻ trung"
                ],
                "scenario": "Normal",
                "sales_velocity": 78,
                "created_at": "2026-05-07T20:00:00Z"
            },
            {
                "product_name": "Elegant and Luxurious Middle-Aged Men's Vest", 
                "image_url": "https://img.lazcdn.com/g/p/1b03190a29f316afe88a6397088c41d1.jpg_720x720q80.jpg_.webp",
                "reviews": [
                    "Đáng đồng tiền bát gạo, shop làm ăn uy tín đấy, form dáng ok",
                    "Đóng gói kỹ xíu đi shop ơi bọc nilon mỏng dính, bù lại chất vải đẹp, đường may ok ko bị lỗi.",
                    "Shop làm ăn bố láo, nhắn tin xin đổi size mà seen không thèm rep, thái độ lồi lõm với khách."
                ],
                "scenario": "Normal",
                "sales_velocity": 60,
                "created_at": "2026-05-07T20:00:00Z"
            },
            {
                "product_name": "Middle-Aged Men's Suit Made of Tweed Material Imported from India", 
                "image_url": "https://img.lazcdn.com/g/p/0341cb412893306fb4645281b48532da.jpg_720x720q80.jpg_.webp",
                "reviews": [
                    "Sợ áo mỏng nhận về nặng trịch dầy dặn bất ngờ hehe.",
                    "Xỉu up xỉu down luôn á áo đỉnh vãi chưởng",
                    "Dm giao mẹ cái giẻ rách à áo rách toạc mà cũng ship tốn tiền"
                ],
                "scenario": "Normal",
                "sales_velocity": 86,
                "created_at": "2026-05-07T20:00:00Z"
            },
            {
                "product_name": "Charcoal Green Men's Suit with Tie, Groom's Suit, Men's Office Suit, Men's Suit Made of Beautiful Fabric, Wrinkle-Free, Not Ruffled.", 
                "image_url": "https://img.lazcdn.com/g/ff/kf/Sa364139c1aba47a5b2f979448fcdc2eeP.jpg_720x720q80.jpg_.webp",
                "reviews": [
                    "Shop làm ăn vcl nhắn ko rep áo thì chật cứng bực mình bồi thường đi",
                    "Mua cho chồng mặc đi đám cưới ai cũng khen đẹp, form lên vừa vặn lắm",
                    "Trúc xinh trúc mọc đầu đình, em xinh em đứng một mình cũng xinh. Áo đẹp lắm nha shop 10 sao"
                ],
                "scenario": "Normal",
                "sales_velocity": 76,
                "created_at": "2026-05-07T20:00:00Z"
            },
        ]
        products_data = []
        for p in products_cursor:
            created_at = p.get("created_at", datetime.utcnow())
            # Handle both string and datetime objects
            created_at_str = created_at if isinstance(created_at, str) else created_at.isoformat()
            
            products_data.append({
                "product_name": p.get("product_name", ""),  # Fix: use product_name, not name
                "image_url": p.get("image_url", ""),
                "reviews": p.get("reviews", []),
                "scenario": p.get("scenario", "fashion_trend"),
                "sales_velocity": p.get("sales_velocity", 0),
                "created_at": created_at_str
            })

        payload = {
            "request_id": str(request_id),
            "category_keyword": "Vest Nam", #analysis_req.get("category_name", ""),
            "products": products_data,
            "limit": 5
        }

        # 4. Gửi request tới AI Server
        logger.warning(f"Sending payload to AI server: {payload}")  # Debug: log payload
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(AI_SERVER_URL, json=payload)
            response.raise_for_status()
            ai_result = response.json()
        logger.warning("khfa")
        # 5. Xử lý kết quả trả về và lưu vào database
        # lưu kết quả vào collection 'trend_results'
        trends = ai_result.get("trends", [])
        if trends:
            await db["trend_results"].insert_many([
                {**trend, "analysis_request_id": ObjectId(request_id), "created_at": datetime.utcnow()}
                for trend in trends
            ])

            # Lấy trend có score cao nhất để làm mẫu tạo ảnh
            top_trend = max(trends, key=lambda x: x.get("trend_score", 0))

            # in ra top trend ra terminal
            logger.warning(f"Top trend from AI analysis: {top_trend}")
            
            # Tạo một prompt từ các keyword của trend
            style_prompt = "".join(top_trend.get("style_keywords", []))
            base_img = top_trend.get("source_image_url")

            # Kích hoạt luôn bước sinh ảnh
            # await request_ai_image_generation(
            #     request_id=request_id,
            #     db=db,
            #     # target_style_prompt=style_prompt,
            #     base_image_url=base_img
            # )

        # 6. Cập nhật trạng thái hoàn thành
        await db["analysis_requests"].update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {
                "status": "COMPLETED", 
                "updated_at": datetime.utcnow(),
                "result_images": [trend.get("source_image_url") for trend in trends]  # Lưu lại ảnh gốc của các trend để user xem
                }
            }
        )

    except Exception as e:
        logger.error(f"Error in background AI analysis for {request_id}: {str(e)}")
        # Cập nhật trạng thái lỗi để user biết
        await db["analysis_requests"].update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "FAILED", "updated_at": datetime.utcnow()}}
        )