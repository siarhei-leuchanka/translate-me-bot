from telegram import Update
from telegram.ext import ContextTypes 
import config

HELLO_TEXT = "Greeting. The bot will try to translate audio you sent to the selected language.  This is the DEMO version and functionality is password protected. Please enter a password to proceed:"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text = HELLO_TEXT
        )

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):    
    if update.effective_user.id not in config.SPECIAL_USERS:
        if update.message.text == config.PASS:    
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text = "Success. Send me voice message with a word you want to translate from CZ \n Or you can send me a picture!"        
                )
            config.SPECIAL_USERS.append(update.effective_user.id)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text = "You entered incorrect password"
            )
    else:
        await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text = "Send me voice message with a word you want to translate from CZ"        
                )
