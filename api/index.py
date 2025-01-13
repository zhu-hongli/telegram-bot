from fastapi import FastAPI, Request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

app = FastAPI()

TOKEN = '7015054463:AAHRjapJy3Rkbz3JTC_IjsjhklrzO1XBhb0'
bot = Bot(token=TOKEN)
application = Application.builder().bot(bot).build()

# 启动时显示菜单按钮
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 创建一个自定义的“菜单”按钮，放置在聊天框下方
    keyboard = [
        [KeyboardButton("📱 菜单")]  # 这个按钮将出现在聊天框下方
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)  # resize_keyboard=True，按钮大小自适应
    await update.message.reply_text('Hello! This is a webhook demo bot. 点击“菜单”按钮展开更多操作选项。',
                                    reply_markup=reply_markup)

# 处理收到的图片
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

# 处理按钮点击
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'show_menu':
        # 创建展开的菜单选项
        keyboard = [
            [InlineKeyboardButton("🤖 启动机器人", callback_data='start')],
            [InlineKeyboardButton("⭐ 充值成为vip", callback_data='payment')],
            [InlineKeyboardButton("🎄 查询当前排队人数", callback_data='ck')],
            [InlineKeyboardButton("📖 禁止保存的频道/群组帖子", callback_data='zc')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # 编辑原消息以显示新的菜单
        await query.message.edit_text("请选择以下选项：", reply_markup=reply_markup)

    # 处理其他具体选项点击
    elif query.data == 'start':
        await query.message.reply_text("您选择了启动机器人选项")
    elif query.data == 'payment':
        await query.message.reply_text("您选择了充值选项")
    elif query.data == 'ck':
        await query.message.reply_text("您选择了查询排队人数选项")
    elif query.data == 'zc':
        await query.message.reply_text("您选择了禁止保存的频道/群组帖子选项")
    elif query.data == 'bikini':
        await query.message.reply_text("您选择了比基尼选项")
    elif query.data == 'nude':
        await query.message.reply_text("您选择了脱衣选项")

# 绑定处理程序
application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(CallbackQueryHandler(button_callback))

@app.on_event("startup")
async def startup():
    # 初始化时不再重复发送菜单按钮
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
