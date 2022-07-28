from telegram import Update
from telegram.ext import ContextTypes 


HELLO_TEXT = "Greeting. The bot will try to translate audio you sent to the selected language.  This is the DEMO version and functionality is password protected. Please enter a password to proceed:"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text = HELLO_TEXT
        )
