import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from inference import predict_food
from inference import calculate_nutrition
from inference_2 import predict_ingredients
from inference_2 import calculate_ingredients_nutrition


app=FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/analyze")
async def analyze_food(file:UploadFile=File(...), weight: float=Form(...)):
    temp_filename=os.path.join(UPLOAD_DIR, f"temp_{uuid.uuid4()}.jpg")
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    predicted_class, confidence=predict_food(temp_filename)
    THRESHOLD=0.99
    if confidence>=THRESHOLD:
        nutrition=calculate_nutrition(predicted_class, weight)
        os.remove(temp_filename)

        return {

            "type": "dish",

            "dish": predicted_class,

            "confidence": round(confidence, 3),

            "weight": weight,

            "calories": nutrition["calories"],

            "protein": nutrition["protein"],

            "fat": nutrition["fat"],

            "carbs": nutrition["carbs"]
            }
    elif confidence<=0.2:
        return{
            "type": "not food",
            "message": "Your photo is not food",
            "confidence": round(confidence, 3)
        }
    else:
        ingredients=predict_ingredients(temp_filename)
        nutrition=calculate_ingredients_nutrition(ingredients, weight)
        os.remove(temp_filename)

        return {

            "type": "ingredients",

            "ingredients": ingredients,

            "dish_confidence": round(confidence, 3),

            "weight": weight,

            "calories": nutrition["calories"],
            "protein": nutrition["protein"],
            "fat": nutrition["fat"],
            "carbs": nutrition["carbs"]
            }
