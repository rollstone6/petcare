"""宠物宝 (PetCare) — FastAPI 入口"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import engine, Base
from app.routers import products, ingredients, brands, categories, breeds, users, favorites, ai, records, schedules, reviews, health, pets

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# CORS: 仅允许配置的来源
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# 全局异常处理: 不泄露内部信息
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()  # 服务端日志
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None},
    )

app.include_router(products.router, prefix="/api")
app.include_router(ingredients.router, prefix="/api")
app.include_router(brands.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(breeds.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(favorites.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(records.router, prefix="/api")
app.include_router(schedules.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(pets.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "宠物宝 PetCare API", "version": "0.1.0"}
