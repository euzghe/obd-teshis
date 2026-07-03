"""FastAPI uygulama giriş noktası."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.api.routes import router

app = FastAPI(
    title="OBD-II Akıllı Araç Teşhis Asistanı",
    description="Arıza kodlarını okuyup AI ile sade Türkçe açıklayan, gerçek zamanlı araç verisi gösteren API.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root() -> dict:
    return {"name": "OBD-II Akıllı Araç Teşhis Asistanı", "mock_mode": config.OBD_MOCK_MODE}
