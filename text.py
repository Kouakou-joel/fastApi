from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import databases
import sqlalchemy

DATABASE_URL = "sqlite:///./test.db"

metadata = sqlalchemy.MetaData()

database = databases.Database(DATABASE_URL)

register = sqlalchemy.Table(
    "register",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(500)),
    sqlalchemy.Column("email", sqlalchemy.String(225)),
    sqlalchemy.Column("password", sqlalchemy.String(225)),
    sqlalchemy.Column("date_created", sqlalchemy.DateTime())
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata.create_all(engine)

app = FastAPI()

@app.on_event("startup")
async def connect():
    await database.connect()

@app.on_event("shutdown")
async def disconnect():
    await database.disconnect()

class Register(BaseModel):
    id: int
    name: str
    email: str
    password: str
    date_created: datetime

class RegisterIn(BaseModel):
    name: str
    email: str
    password: str

@app.get("/")
def home():
    return {"message": "bienvenue"}

#voir la liste des utilisateur
@app.get("/register/", response_model=List[Register])
async def get_all():
    query = register.select()
    all_get = await database.fetch_all(query)
    return all_get

#voir un uuilisateur via son id
@app.get("/register/{id}", response_model=Register)
async def get_one(id: int):
    query = register.select().where(register.c.id == id)
    user = await database.fetch_one(query)
    if user:
        return user
    return {"error": "User not found"}
    

    #creer un utilisatteur
@app.post("/register/", response_model=Register)
async def create(r: RegisterIn):
    query = register.insert().values(
        name=r.name,
        email=r.email,
        password=r.password,
        date_created=datetime.utcnow()
    )
    record_id = await database.execute(query)
    query = register.select().where(register.c.id == record_id)
    row = await database.fetch_one(query)
    return row

#modif d utilisateur
@app.put("/register/{id}")
async def update(id: int, r: RegisterIn):
    query = register.update().where(register.c.id == id).values(
        name=r.name,
        email=r.email,
        password=r.password,
        date_created=datetime.utcnow()
    )
    await database.execute(query)
    query = register.select().where(register.c.id == id)
    row = await database.fetch_one(query)
    if row:
        return row
    return {"error": "User not found"}

#supression d utilisateur
@app.delete("/register/{id}")
async def delete(id: int):
    query = register.select().where(register.c.id == id)
    row = await database.fetch_one(query)
    if row:
        delete_query = register.delete().where(register.c.id == id)
        await database.execute(delete_query)
        return {"message": "User deleted successfully"}
    return {"error": "User not found"}
