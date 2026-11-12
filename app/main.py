from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health
from app.api.datasets import router as datasets_router
from app.api.local_ai import router as local_ai_router

app = FastAPI(
    title="Financial AI Service",
    description="Service tạo dataset và huấn luyện mô hình AI tài chính",
    version="0.1.0",
)

# Frontend development server chạy ở port khác với FastAPI.
# Giới hạn origin vào các địa chỉ local cần dùng khi phát triển.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)

app.include_router(datasets_router)
app.include_router(local_ai_router)
