from fastapi import APIRouter
from app.api.v2.endpoints import login, users, subscription_plans, analysis_requests, credit_transactions, generated_designs, projects, style_presets, trend_insights, billing

api_router = APIRouter()

# Đăng ký các router lẻ vào Big Router
api_router.include_router(login.router, prefix="/auth", tags=["Authentication V2"])
api_router.include_router(users.router, prefix="/users", tags=["Users V2"])
api_router.include_router(subscription_plans.router, prefix="/subscription_plans", tags=["Subscription Plans V2"])
api_router.include_router(analysis_requests.router, prefix="/analysis_requests", tags=["Analysis Requests V2"])
api_router.include_router(credit_transactions.router, prefix="/credit_transactions", tags=["Credit Transactions V2"])
api_router.include_router(generated_designs.router, prefix="/generated_designs", tags=["Generated Designs V2"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects V2"])
api_router.include_router(style_presets.router, prefix="/style_presets", tags=["Style Presets V2"])
api_router.include_router(trend_insights.router, prefix="/trend_insights", tags=["Trend Insights V2"])
api_router.include_router(billing.router, prefix="/billing", tags=["Billing V2"])