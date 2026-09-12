from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import admin, auth, parking, payments, users

app = FastAPI(title="Society Parking Payment Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "https://society-parking-app-8op9.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(parking.router)
app.include_router(payments.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "society-parking-api"}


@app.get("/health")
def health():
    return {"status": "healthy"}
