from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel

app = FastAPI(title="Todo API", version="v1")

# Modèle de données pour un Todo
class Todo(BaseModel):
    id: int
    name: str
    description: str
    due_date: str

# Liste pour stocker les Todos
store_todo: List[Todo] = []

print(store_todo)

@app.get("/")
def default():
    return {"message": "Bonjour todo"}

#  Récupérer tous les Todos
@app.get("/todos/", response_model=List[Todo])
async def get_all_todos():
    return store_todo

#  Récupérer un Todo par ID
@app.get("/todos/{id}", response_model=Todo)
async def get_todo(id: int):
    if id < 0 or id >= len(store_todo):
        raise HTTPException(status_code=404, detail="Todo non trouvé")
    return store_todo[id]

#  Créer un Todo
@app.post("/todo/", response_model=Todo)
async def create_todo(todo: Todo):
    store_todo.append(todo)
    return todo

# Mettre a jour un Todo
@app.put("/todo/{id}", response_model=Todo)
async def update_todo(id: int, new_todo: Todo):
    if id < 0 or id >= len(store_todo):
        raise HTTPException(status_code=404, detail="Todo non trouvé")
    store_todo[id] = new_todo
    return store_todo[id]

# Supprimer un Todo
@app.delete("/todo/{id}", response_model=Todo)
async def delete_todo(id: int):
    if id < 0 or id >= len(store_todo):
        raise HTTPException(status_code=404, detail="Todo non trouvé")
    return store_todo.pop(id)
