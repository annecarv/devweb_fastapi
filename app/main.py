from fastapi import FastAPI
from app.database import init_db
from app.routers import posts, comments, likes, categories

app = FastAPI(title="Backend EX3")


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(likes.router)
app.include_router(categories.router)
