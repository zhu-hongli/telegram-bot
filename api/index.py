from fastapi import FastAPI, Request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

app = FastAPI()

TOKEN = '7015054463:AAHRjapJy3Rkbz3JTC_IjsjhklrzO1XBhb0'
bot = Bot(token=TOKEN)
application = Application.builder().bot(bot).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 创建菜单按钮
    keyboard = [
        [InlineKeyboardButton("📱 菜单", callback_data='show_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Hello! This is a webhook demo bot.', reply_markup=reply_markup)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 获取用户发送的图片
    photo = update.message.photo[-1]  # 获取最高质量的图片版本
    
    # 创建内联键盘按钮
    keyboard = [
        [
            InlineKeyboardButton("比基尼", callback_data='bikini'),
            InlineKeyboardButton("脱衣", callback_data='nude')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # 发送图片和按钮
    await update.message.reply_photo(photo.file_id, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # 响应回调查询
    
    if query.data == 'show_menu':
        # 创建展开的菜单选项
        keyboard = [
            [InlineKeyboardButton("💰 充值", callback_data='recharge')],
            [InlineKeyboardButton("🔍 Test1", callback_data='test1')],
            [InlineKeyboardButton("🔧 Test2", callback_data='test2')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("请选择以下选项：", reply_markup=reply_markup)
    elif query.data == 'recharge':
        await query.message.reply_text("您选择了充值选项")
    elif query.data == 'test1':
        await query.message.reply_text("您选择了Test1选项")
    elif query.data == 'test2':
        await query.message.reply_text("您选择了Test2选项")
    elif query.data == 'bikini':
        await query.message.reply_text("您选择了比基尼选项")
    elif query.data == 'nude':
        await query.message.reply_text("您选择了脱衣选项")

application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(CallbackQueryHandler(button_callback))

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

