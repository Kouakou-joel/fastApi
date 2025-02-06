from fastapi import FastAPI, HTTPException
from models import Todo, Todo_pydantic, TodoIn_pydantic
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise
from pydantic import BaseModel
from typing import List

class Messa(BaseModel):
    message: str

app = FastAPI()

@app.get("/")
def default():
    return {"message": "Bonjour todo"}

@app.post("/todo", response_model=Todo_pydantic)
async def create(todo = TodoIn_pydantic):  
    obj = await Todo.create(**todo.dict(exclude_unset=True))
    return await Todo_pydantic.from_tortoise_orm(obj)


@app.get("/todo/{id}", response_model=TodoIn_pydantic, responses= {404: {"model": HTTPNotFoundError}})
async def get_todo(id: int):
     return await Todo_pydantic.from_queryset_single(Todo.get(id=id))

@app.put("/todo/{id}", response_model=Todo_pydantic)
async def update_todo(id: int, todo = TodoIn_pydantic):
    updated_count = await Todo.filter(id=id).update(**todo.dict(exclude_unset=True))
    if not updated_count:
        raise HTTPException(status_code=404, detail="Todo non trouvé")
    return await Todo_pydantic.from_queryset_single(Todo.get(id=id))

@app.delete("/todo/{id}", response_model=Messa)
async def delete_todo(id: int):
    deleted_count = await Todo.filter(id=id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail="Todo non trouvé")
    return Messa(message="Supprimé avec succès")

@app.get("/todos/", response_model=List[Todo_pydantic])
async def get_todos():
    return await Todo_pydantic.from_queryset(Todo.all())



register_tortoise(
    app,
    db_url="sqlite://store.db",
    modules={"models": ["models"]}, 
    generate_schemas=True,
    add_exception_handlers=True
)