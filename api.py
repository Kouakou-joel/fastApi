from fastapi import FastAPI,Query,Path,UploadFile,Form
from tensorflow.keras.models import load_model
import numpy as np
import io
from PIL import Image
from pydantic import BaseModel
from typing import Optional
from data import (get_all_teams_from_fake_db,
                   get_team_from_fake_db,create_team_in_fake_db
)

app = FastAPI()

@app.get("/")
def green():
    return {"message": "Bonjour"}

@app.get("/items")
def get_items():
    return[
        {"id":1 , "description": "items"},
        {"id":2 , "description": "items"},
        {"id":3 , "description": "items"},
        {"id":4 , "description": "items"}
    ]

class CoordIn(BaseModel):
    password: str
    lad: float
    long: float
    zom: Optional[int] = None
  
class CoordOut(BaseModel):
    lad: float
    long: float
    zom: Optional[int] = None
  


class Team(BaseModel):
    id: int
    name: str
    drivers: list[str]
    engime: str

#Request body
@app.post("/teams")
def create_team(team: Team):
    create_team_in_fake_db(team)

    return team

@app.get("/teams")
def get_teams(skip: int = Query (0, le=9, description="le nombre doit etre un entier"),
              limit:int = 10):
    teams =  get_all_teams_from_fake_db()
    return teams[skip:limit]

@app.get("/teams/{team}")
def get_teams(team: str = Path(..., min_length=4, description="minimum 4 caracters"),
             show_drivers: bool =True ):
    result = get_team_from_fake_db(team)
    
    if result is None:
        return f"la team {team} est incorrect"
    return result

@app.get("/teams/id/{id}")
def get_team_by_id(id):
    return {"id": id}
     

def load(): 
    model_path = "best_model.h5"
    try:
        model = load_model(model_path, compile=False)
        return model
    except Exception as e:
        print(f"Erreur lors du chargement du modèle : {e}")
        return None 

# Charger le modèle si la fonction existe
if "load" in globals():
    model = load()
else:
    model = None

# Fonction de prétraitement de l'image
def preprocess(img):
    img = img.resize((224, 224))  
    img = np.asarray(img) / 255.0 
    img = np.expand_dims(img, axis=0)  
    return img

# Route pour la prédiction
@app.post("/predict")
async def predict(file: UploadFile):
    if model is None:
        return {"error": "Le modèle n'a pas été chargé correctement."}

    image_data = await file.read()

    # ovrir l'image
    img = Image.open(io.BytesIO(image_data))

    # Prétraitement
    img_processed = preprocess(img)
    
    # Prédiction avec le modèle
    predictions = model.predict(img_processed)
    rec = predictions[0][0].tolist()  

    return {"predictions": rec}

@app.post("/position/", response_model=CoordOut)
async def make_position(coord: CoordIn):
    #db wrie completed
    return coord

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {username: username}
