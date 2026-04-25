from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app=FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeResponse(BaseModel):
    message: str
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_food(file:UploadFile=File(...), weight: float=Form(...)):
    return {"message":f"I got ur photo broski {file.filename} it weights {weight} gramms"}
