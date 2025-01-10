from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

app = FastAPI()

TOKEN = '7015054463:AAHRjapJy3Rkbz3JTC_IjsjhklrzO1XBhb0'
bot = Bot(token=TOKEN)
application = Application.builder().bot(bot).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! This is a webhook demo bot.')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 获取用户发送的图片
    photo = update.message.photo[-1]  # 获取最高质量的图片版本
    # 直接将相同的图片发送回去
    await update.message.reply_photo(photo.file_id)

application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.bot.set_webhook(url="https://telegram-bot-zeta-azure.vercel.app/webhook")

@app.on_event("shutdown")
async def shutdown():
    await application.stop()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        json_data = await request.json()
        update = Update.de_json(json_data, bot)
        async with application:
            await application.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        print(f"Error processing update: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def index():
    return {"message": "Hello, this is the Telegram bot webhook!"}

