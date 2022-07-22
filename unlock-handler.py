




async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):    
    if update.effective_user.id not in SPECIAL_USERS:
        if update.message.text == PASS:    
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text = "Success. Send me voice message with a word you want to translate from CZ"        
                )
            SPECIAL_USERS.append(update.effective_user.id)
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
