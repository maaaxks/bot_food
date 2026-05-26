import json
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision import models


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


MODEL_PATH = "../models/model_2/ingredient_model_C.pth"
MAPPING_PATH = "../models/model_2/ingredient_mapping.json"
NUTRITION_PATH = "../models/model_2/nutrition_db_2.json"


with open(MAPPING_PATH, "r") as f:
    ingredient_mapping = json.load(f)

with open(NUTRITION_PATH, "r") as f:
    nutrition_db_2 = json.load(f)


NUM_CLASSES = len(ingredient_mapping)


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


model_2=models.resnet18(weights=None)

in_features=model_2.fc.in_features

model_2.fc=nn.Linear(in_features,NUM_CLASSES)
model_2.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model_2=model_2.to(DEVICE)

model_2.eval()

def predict_ingredients(image_path, threshold=0.35):
    image=Image.open(image_path).convert("RGB")
    image_tensor=transform(image)
    image_tensor=image_tensor.unsqueeze(0)
    image_tensor=image_tensor.to(DEVICE)

    with torch.no_grad():
        outputs=model_2(image_tensor)
        probs=torch.sigmoid(outputs)[0]

    predictions=[]
    for i, prob in enumerate(probs):
        prob=float(prob)
        if prob>=threshold:
            ingredient_name= ingredient_mapping[str(i + 1)]
            predictions.append({
                "ingredient": ingredient_name,
                "confidence": round(prob, 3)
            })

    predictions.sort(key=lambda x: x["confidence"], reverse=True)
    return predictions

def calculate_ingredients_nutrition(predictions, weight):
    total_calories=0
    total_protein=0
    total_fat=0
    total_carbs=0

    if len(predictions)==0:
        return {
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "carbs": 0
        }

    weight_per_ingredient=weight/len(predictions)
    for item in predictions:
        ingredient_name=item["ingredient"]
        if ingredient_name not in nutrition_db_2:
            continue

        nutrition=nutrition_db_2[ingredient_name]
        factor=weight_per_ingredient / 100
        total_calories+=nutrition["calories"] * factor
        total_protein+=nutrition["protein"] * factor
        total_fat+=nutrition["fat"] * factor
        total_carbs+=nutrition["carbs"] * factor

    return {
        "calories": round(total_calories, 1),
        "protein": round(total_protein, 1),
        "fat": round(total_fat, 1),
        "carbs": round(total_carbs, 1)
    }