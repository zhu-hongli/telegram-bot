from fastapi import FastAPI, Request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

app = FastAPI()

TOKEN = '7015054463:AAHRjapJy3Rkbz3JTC_IjsjhklrzO1XBhb0'
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
    
    html_message = """
<b>⭐️ 本机器人的使用条款和免责声明</b>

<i>基本说明：</i>
➡️ 本机器人是一个根据用户输入生成图像的机器人。

<i>免责声明：</i>
<code>➡️ 但是，该机器人不对用户使用它创建的任何特定图像负责。
➡️ 使用应该由用户自行全面认识和负责。
➡️ 用户在利用此机器人时必须对内容和行为承担全部责任。
➡️ 本机器人仅是一个工具，无法控制或对用户的使用方式负责。</code>

<i>重要提醒：</i>
<b>⭐️ 禁止用户使用机器人传播可能对个人或组织造成伤害的图像。</b>

<i>隐私声明：</i>
<code>⭐️ 不会存储用户提交的任何信息或图像，除了TelegramID，也没有权利将用户信息用于任何目的。</code>
"""
    
    await update.message.reply_text(
        html_message,
        reply_markup=reply_markup,
        parse_mode='HTML'  # 启用 HTML 解析模式
    )

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

# 处理文本消息
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "👤 个人资料":
        profile_message = """
<b>👤 用户个人资料</b>

<i>基本信息：</i>
🆔 用户ID：<code>{}</code>
👤 用户名：<code>{}</code>
📅 注册日期：2024-03-20

<i>账户状态：</i>
💰 剩余积分：500
⭐️ 会员等级：普通用户
🎯 使用次数：27次

<i>其他信息：</i>
🔥 连续使用天数：3天
🏆 特殊成就：新手上路
""".format(update.effective_user.id, update.effective_user.username or "未设置用户名")

        await update.message.reply_text(
            profile_message,
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

@app.get("/")
async def index():
    return {"message": "Hello, this is the Telegram bot webhook!"}
