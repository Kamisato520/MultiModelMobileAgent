from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, Base, engine
from .models import User, Task

app = FastAPI()

# 初始化数据库
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/create-user")
def create_user(name: str, email: str, db: Session = Depends(get_db)):
    new_user = User(name=name, email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/create-task")
def create_task(description: str, db: Session = Depends(get_db)):
    new_task = Task(description=description)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
