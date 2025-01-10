import logging
import random
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN

app = FastAPI()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "欢迎使用我的Telegram机器人！\n"
        "可用命令:\n"
        "/start - 显示欢迎信息\n"
        "/help - 查看帮助\n"
        "/joke - 讲个笑话\n"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "机器人功能:\n"
        "1. /start - 启动机器人\n"
        "2. /help - 显示帮助信息\n"
        "3. /joke - 随机讲个笑话\n"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = [
        "为什么程序员喜欢使用黑暗模式？因为光线太亮会闪瞎代码！",
        "程序员的浪漫：我们的爱情，就像调试代码，需要耐心和理解。",
        "为什么Python如此受欢迎？因为它很蟒蛇！"
    ]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(jokes))

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"你说：{update.message.text}")

# 注册命令处理器
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('help', help_command))
application.add_handler(CommandHandler('joke', joke_command))

# 注册消息处理器
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.post("/webhook")
async def webhook(request: Request):
    update = Update.de_json(await request.json(), application.bot)
    await application.update_queue.put(update)
    return {"status": "ok"}

@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.start()
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path=TELEGRAM_BOT_TOKEN,
        webhook_url=f"https://your-vercel-domain.vercel.app/{TELEGRAM_BOT_TOKEN}"
    )

@app.on_event("shutdown")
async def shutdown():
    await application.updater.stop()
    await application.stop()
    await application.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=10000)
