# backend.py
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import jwt, datetime
from dotenv import load_dotenv


# Load .env file
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")  # fallback for local dev
ALGORITHM = os.getenv("ALGORITHM", "HS256")


DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")

Base.metadata.create_all(bind=engine)

# ---- Security ----
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ---- FastAPI App ----
app = FastAPI()


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def hash_password(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# ---- Routes ----
@app.post("/register")
def register(username: str, password: str, role: str = "user", db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    user = User(username=username, password=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    print("Using DB:", DATABASE_URL)
    return {"msg": "User registered", "username": user.username, "role": user.role}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def get_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"username": payload["sub"], "role": payload["role"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ---- Seed Admin Only ----
def seed_admin():
    db = SessionLocal()
    if not db.query(User).filter(User.username == "admin").first():
        admin = User(username="admin", password=hash_password("admin123"), role="admin")
        db.add(admin)
        db.commit()
    db.close()

seed_admin()
