from telegram.ext import Application, MessageHandler, CommandHandler, filters
from config import TELEGRAM_BOT_TOKEN

async def reply(update, context):
    print(context)
    await update.message.reply_text("Hello there!")

async def hello(update, context):
    print(context)
    await update.message.reply_text("你好!")

def main():
    """
    Handles the initial launch of the program (entry point).
    """
    token = TELEGRAM_BOT_TOKEN
    application = Application.builder().token(token).concurrent_updates(True).read_timeout(30).write_timeout(30).build()
    application.add_handler(MessageHandler(filters.TEXT, reply))
    application.add_handler(CommandHandler("hello", hello))
    application.add_handler(MessageHandler(filters.PHOTO, reply))
    print("Telegram Bot started!", flush=True)
    application.run_polling()


if __name__ == "__main__":
    main()

