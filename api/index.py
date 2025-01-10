from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler

app = FastAPI()

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

def start(update, context):
    update.message.reply_text('Hello! This is a webhook demo bot.')

dispatcher.add_handler(CommandHandler('start', start))

@app.post("/webhook")
async def webhook(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, bot)
    dispatcher.process_update(update)
    return "ok"

@app.get("/")
async def index():
    return {"message": "Hello, this is the Telegram bot webhook!"}