from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import Base, User, Task
from schemas import UserCreate, User as UserSchema, Token, TaskCreate, TaskUpdate, Task as TaskSchema
from auth import ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash, create_access_token, get_current_active_user, authenticate_user, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# User registration endpoint
@app.post("/register/", response_model=UserSchema)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# User login endpoint to obtain JWT token
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoint to get the current user
@app.get("/users/me/", response_model=UserSchema)
async def current_user(current_user: UserSchema = Depends(get_current_active_user)):
    return current_user

# Task Management Endpoints
@app.post("/tasks/", response_model=TaskSchema)
async def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_active_user)):
    new_task = Task(**task.dict(), user_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/tasks/", response_model=list[TaskSchema])
async def read_tasks(db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_active_user)):
    if current_user.role == "admin":
        return db.query(Task).all()
    else:
        return db.query(Task).filter(Task.user_id == current_user.id).all()

@app.put("/tasks/{task_id}", response_model=TaskSchema)
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_active_user)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user.role != "admin" and db_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    for key, value in task.dict().items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}", response_model=TaskSchema)
async def delete_task(task_id: int, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_active_user)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user.role != "admin" and db_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    db.delete(db_task)
    db.commit()
    return db_task

@app.put("/tasks/{task_id}/complete", response_model=TaskSchema)
async def mark_task_completed(task_id: int, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_active_user)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user.role != "admin" and db_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to complete this task")
    db_task.completed = True
    db.commit()
    db.refresh(db_task)
    return db_task

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
