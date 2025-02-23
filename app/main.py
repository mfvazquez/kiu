from fastapi import FastAPI
from dotenv import load_dotenv
from app.routers.journey import router as journey_router


load_dotenv()

app = FastAPI()

app.include_router(journey_router)
