from fastapi import FastAPI, Request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from api.message import start_message, profile_message
app = FastAPI()

TOKEN = '8134329878:AAF-iYg-GOeUXWwIV2pOGbMu-AiKn5j_nBY'
bot = Bot(token=TOKEN)
application = Application.builder().bot(bot).build()

# 启动时显示菜单按钮
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 创建一个自定义的"菜单"按钮，放置在聊天框下方
    keyboard = [
        [
            KeyboardButton("💰 购买积分"),
            KeyboardButton("👤 个人资料"),
            KeyboardButton("⚙️ 偏好设定")
        ],
        [
            KeyboardButton("💡 提示"),
            KeyboardButton("📢 官方样本频道"),
            KeyboardButton("🔗 分享")
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)  # resize_keyboard=True，按钮大小自适应
    
    html_message = start_message.format(update.effective_chat.id)
    
    await update.message.reply_text(
        html_message,
        reply_markup=reply_markup,
        parse_mode='HTML'  # 启用 HTML 解析模式
    )

# 处理收到的图片
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 获取最高质量的图片（telegram会发送多个不同尺寸的版本）
    photo = update.message.photo[-1]  # 使用 -1 获取最大尺寸的图片
    
    # 获取图片文件对象
    file = await context.bot.get_file(photo.file_id)
    # 获取图片链接
    photo_url = file.file_path
    
    # 创建初始内联键盘按钮
    keyboard = [
        [
            InlineKeyboardButton("脱衣", callback_data='nude'),
            InlineKeyboardButton("换脸", callback_data='face_swap')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # 发送图片和按钮，同时打印图片链接
    await update.message.reply_photo(
        photo.file_id, 
        reply_markup=reply_markup,
        caption=f"图片链接: {photo_url}\nChat ID: {update.effective_chat.id}"
    )


# 处理按钮点击
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'nude':
        # 脱衣选项的子菜单
        keyboard = [
            [
                InlineKeyboardButton("test1", callback_data='test1'),
                InlineKeyboardButton("test2", callback_data='test2')
            ],
            [InlineKeyboardButton("返回", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_reply_markup(reply_markup=reply_markup)
    
    elif query.data == 'face_swap':
        # 换脸选项的子菜单
        keyboard = [
            [
                InlineKeyboardButton("test3", callback_data='test3'),
                InlineKeyboardButton("test4", callback_data='test4')
            ],
            [InlineKeyboardButton("返回", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_reply_markup(reply_markup=reply_markup)
    
    elif query.data == 'back':
        # 返回主菜单
        keyboard = [
            [
                InlineKeyboardButton("脱衣", callback_data='nude'),
                InlineKeyboardButton("换脸", callback_data='face_swap')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_reply_markup(reply_markup=reply_markup)
    
    # 处理测试按钮回调
    elif query.data in ['test1', 'test2', 'test3', 'test4']:
        # 这里替换为你想要发送的新图片
        new_photo_url = "https://m.media-amazon.com/images/I/61X4kXalXtL._AC_SX679_.jpg"  # 替换为实际的图片URL
        try:
            # 删除原始消息（包含旧图片和按钮）
            await query.message.delete()
            
            # 发送新图片，不带任何按钮
            await query.message.reply_photo(
                photo=new_photo_url,
                caption=f"这是{query.data}的结果"
            )
        except Exception as e:
            await query.message.reply_text(f"处理图片时出错：{str(e)}")

# 处理文本消息
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "👤 个人资料":
        formatted_profile = profile_message.format(
            update.effective_user.id, 
            update.effective_user.username or "未设置用户名"
        )

        await update.message.reply_text(
            formatted_profile,
            parse_mode='HTML'
        )

# 绑定处理程序
application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(MessageHandler(filters.TEXT, handle_message))
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

@app.post("/send_photo")
async def send_photo(chat_id: str, photo_url: str):
    try:
        async with bot:  # 添加这个上下文管理器
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo_url
            )
        return {"status": "success", "message": "Photo sent successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.post("/send_photo_with_url")
async def send_photo_with_url(chat_id: str, photo_url: str):
    try:
        async with bot:
            # 发送图片到对话
            message = await bot.send_photo(
                chat_id=chat_id,
                photo=photo_url
            )
            # 获取发送的图片文件ID
            file_id = message.photo[-1].file_id
            # 获取文件信息
            file_info = await bot.get_file(file_id)
            # 获取文件URL
            file_url = file_info.file_path
            # 构建完整的Telegram文件URL
            telegram_file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_url}"
            
            return {
                "status": "success", 
                "message": "Photo sent successfully",
                "file_url": telegram_file_url
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/")
async def index():
    return {"message": "Hello, this is the Telegram bot webhook!"}


