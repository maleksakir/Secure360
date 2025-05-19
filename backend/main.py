from fastapi import FastAPI
from routers import scanner, users
from database import init_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
init_db()
app.include_router(users.router)
app.include_router(scanner.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
