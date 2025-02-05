from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import List, Optional

SECRET_KEY = "c8d2b25c3645732fcd434750feba81ca6f44aaa04795a0c860fb0a0f9167e819"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_db = {
    "joe": {
        "username": "joe",
        "full_name": "Joe Coder",
        "email": "joecoder@gmail.com",
        "hashed_password": pwd_context.hash("password123"),
        "disabled": False
    }
}

tache_db = []

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    disabled: Optional[bool] = None

class UserCreate(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: str 

class UserInDB(User):
    hashed_password: str

class Tache(BaseModel):
    id: int
    title: str
    description: str
    owner: str

class TacheCreate(BaseModel):
    title: str
    description: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    user_data = db.get(username)
    if user_data:
        return UserInDB(**user_data)
    return None

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    
    user = get_user(fake_db, username=token_data.username)
    if user is None:
        raise credential_exception
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/")
async def welcome():
    return {"message": "Bienvenue dans l'API FastAPI !"}

@app.post("/token/", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/", response_model=List[User])
async def get_users(current_user: User = Depends(get_current_active_user)):
    return [
        User(
            username=u,
            full_name=d.get("full_name"),
            email=d.get("email"),
            disabled=d.get("disabled"),
        )
        for u, d in fake_db.items()
    ]

@app.post("/user/", response_model=User)
async def create_user(user: UserCreate):
    if user.username in fake_db:
        raise HTTPException(status_code=400, detail="username alreadY registerd")

    hashed_password = get_password_hash(user.password)

    fake_db[user.username]= {
    "username": user.username,
    "full_name": user.full_name,
    "email": user.email,
    "hashed_password": hashed_password,
    "disabled": False
}
    return User(username=user.username, full_name=user.full_name, email=user.email, disabled=False)

@app.post("/tache/", response_model=Tache)
async def create_tache(tache: TacheCreate, current_user: User = Depends(get_current_active_user)):
    tache_id = len(tache_db) + 1 
    new_tache = Tache(id=tache_id, title=tache.title, description=tache.description, owner=current_user.username)
    tache_db.append(new_tache)
    return new_tache

@app.get("/tache/", response_model=List[Tache])
async def get_my_tache(current_user: User = Depends(get_current_active_user)):
    user_tache = [tache for tache in tache_db if tache.owner == current_user.username]
    return user_tache

@app.delete("/tache/{tache_id}")
async def delete_tache(tache_id: int, current_user: User = Depends(get_current_active_user)):
    global tache_db
    tache = next((t for t in tache_db if t.id == tache_id and t.owner == current_user.username), None)
    if tache is None:
        raise HTTPException(status_code=404, detail="Tache not found or unauthorized")
    
    tache_db = [t for t in tache_db if t.id != tache_id]
    return {"message": "Tache deleted successfully"}
