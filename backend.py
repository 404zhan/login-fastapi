import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import jwt, datetime
from dotenv import load_dotenv

ROLES = ["dealer", "factory", "service", "management", "r&d", "admin"]

# Load .env file
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Use local SQLite DB for testing if DATABASE_URL not set
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
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
    role = Column(String, default="dealer")

Base.metadata.create_all(bind=engine)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()

def hash_password(password: str) -> str:
    password_bytes = password[:72].encode()  # truncate to 72 chars
    return pwd_context.hash(password_bytes)

def verify_password(plain: str, hashed: str) -> bool:
    plain_bytes = plain[:72].encode()
    return pwd_context.verify(plain_bytes, hashed)

def create_access_token(data: dict):
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.username == payload["sub"]).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def role_required(required_roles: list[str]):
    def wrapper(user: User = Depends(get_current_user)):
        if user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    return wrapper

# ---------------- Routes ----------------
@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    user = User(username=username, password=hash_password(password), role="dealer")
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"msg": "User registered", "username": user.username, "role": user.role}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}

@app.post("/assignrole")
def assign_role(username: str, new_role: str, current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can assign roles")
    if new_role.lower() not in ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = new_role
    db.commit()
    return {"msg": f"Role updated for {username}", "new_role": new_role}

@app.get("/admin-dashboard")
def admin_dashboard(user: User = Depends(role_required(["admin"]))):
    return {"msg": "Welcome Admin"}

# ---------------- Seed Admin ----------------
def seed_admin():
    db = SessionLocal()
    if not db.query(User).filter(User.username == "admin").first():
        admin = User(username="admin", password=hash_password("admin123"), role="admin")
        db.add(admin)
        db.commit()
    db.close()

seed_admin()


