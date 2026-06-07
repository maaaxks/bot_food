# bot_food

Telegram-bot for automatic food recognition and nutritional value estimation from photos.

## Overview

The system classifies food photos using a two-model cascade architecture based on ResNet18 with ImageNet transfer learning.

Model 1 classifies 15 dish types. If confidence is below threshold (< 0.9), Model 2 identifies individual ingredients from a set of 16. If confidence is very low (< 0.2), the image is considered non-food.

Nutritional value (calories, protein, fat, carbs) is calculated proportionally to the portion weight specified by the user.

## Project structure

```
bot_food/
├── app/
│   ├── main.py            # FastAPI application, POST /analyze endpoint
│   ├── inference.py       # Inference logic for dish classification model
│   └── inference_2.py     # Inference logic for ingredient classification model
├── bot/
│   ├── telegram_bot.py    # Telegram bot (python-telegram-bot)
│   └── .env               # Bot token (not committed)
├── models/
│   ├── model_1/
│   │   ├── data_clean/    # Training images organized by class folder
│   │   ├── model_1.pth    # Trained dish classifier weights
│   │   ├── class_names.json
│   │   ├── nutrition_db.json
│   │   └── Untitled.ipynb # Training notebook
│   └── model_2/
│       ├── data/          # Ingredient images (single + mixed subfolders)
│       ├── ingredient_model_C.pth  # Best ingredient model weights (scenario C)
│       ├── ingredient_mapping.json
│       ├── labels.json    # Multi-hot labels for mixed images
│       ├── nutrition_db_2.json
│       └── model_2.ipynb  # Training notebook with scenario comparison
└── requirements.txt
```

## Requirements

- Python 3.9+
- PyTorch 2.x
- torchvision
- FastAPI
- uvicorn
- python-telegram-bot
- Pillow
- python-dotenv

Install dependencies:

```bash
pip install -r requirements.txt
```

## Setup

1. Clone the repository.

2. Create `bot/.env` with your Telegram bot token:

```
BOT_TOKEN=your_token_here
```

3. Make sure model weights are present:
   - `models/model_1/model_1.pth`
   - `models/model_2/ingredient_model_C.pth`

## Running

Start the backend server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Start the Telegram bot (in a separate terminal):

```bash
python bot/telegram_bot.py
```

## How it works

The user sends a photo to the bot and optionally specifies portion weight in grams (default: 100 g).

The bot sends the image to the backend via POST /analyze.

The backend applies the following cascade logic:

- If dish model confidence >= 0.9: return dish name and nutritional value from dish database.
- If 0.2 <= confidence < 0.9: run ingredient model, return detected ingredients and aggregated nutritional value.
- If confidence < 0.2: return a message that no food was detected.

## Supported dishes (model 1)

borsh, caesar_salad, carbonara, croissant, donut, french_fried_potato, fried_eggs, pancakes, pelmeni, pizza_pepperoni, plov, pork_chop, rice, shashlik, vinegret

## Supported ingredients (model 2)

avocado, bread, carrot, cheese, chicken, corn, cucumber, egg_boiled, egg_fried, lettuce, oatmeal_porridge, pasta, potato, sausage_boiled, smoked_salmon_slices, tomato

## Model training

Both models use ResNet18 with pretrained ImageNet weights (full fine-tuning). Training notebooks are located in the respective model directories.

Three training scenarios for the ingredient model were compared. Training on combined single and mixed images (scenario C) achieved the best results: micro F1-score 0.77 vs 0.60 for mixed-only and 0.59 for sequential training.

The dish model achieved 96% accuracy and macro F1-score 0.96 on the validation set (304 images, 15 classes).
