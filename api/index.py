from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

app = FastAPI()

TOKEN = '7015054463:AAHRjapJy3Rkbz3JTC_IjsjhklrzO1XBhb0'
bot = Bot(token=TOKEN)
application = Application.builder().bot(bot).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! This is a webhook demo bot.')

application.add_handler(CommandHandler('start', start))

@app.on_event("startup")
async def startup():
    await application.initialize()

@app.post("/webhook")
async def webhook(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, bot)
    await application.process_update(update)
    return "ok"

@app.get("/")
async def index():
    return {"message": "Hello, this is the Telegram bot webhook!"}

