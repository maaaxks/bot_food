import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://127.0.0.1:8000/analyze"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a photo of your meal with weight in caption (grams)."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f"temp_{update.message.from_user.id}.jpg"
    await photo_file.download_to_drive(photo_path)

    weight_text = update.message.caption
    if weight_text:
        try:
            weight = float(weight_text)
        except ValueError:
            weight = 100.0
    else:
        weight = 100.0

    with open(photo_path, "rb") as f:
        files={"file": (photo_path, f, "image/jpeg")}
        data = {"weight": weight}
        try:
            resp = requests.post(API_URL, files=files, data=data)
            result=resp.json()
            predicted_class = result["dish"]
            confidence = result["confidence"]
            weight = result["weight"]
            calories = result["calories"]
            protein = result["protein"]
            fat = result["fat"]
            carbs = result["carbs"]
            message = (
                f"Dish: {predicted_class}\n"
                f"Confidence: {confidence}\n"
                f"Weight: {weight} g\n\n"

                f"Calories: {calories} kcal\n"
                f"Protein: {protein} g\n"
                f"Fat: {fat} g\n"
                f"Carbs: {carbs} g"
            )
        except Exception as e:
            print(resp.text)
            message = f"Error: {e}"

    os.remove(photo_path)
    await update.message.reply_text(message)

if __name__ == "__main__":
    TOKEN=os.getenv('BOT_TOKEN')
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot engine start...")
    app.run_polling()

