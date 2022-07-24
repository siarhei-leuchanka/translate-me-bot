import logging
from multiprocessing import context
import config
from xml.sax.handler import feature_namespaces
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters

from handler_unlock import unlock
from handler_start import start
from handler_media import media

####### Setting up logging #######
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
####### ***************** #######

####### Importing Conversation handler for Photo processing #######
import handlers_photo


####### Starting the bot #######
if __name__ == '__main__':
    application = ApplicationBuilder().token(config.TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.PHOTO, handlers_photo.photo)],
        states={
            handlers_photo.CHOICE: [
                MessageHandler(filters.Regex("^(Yes|No, Try Again)$"), handlers_photo.improve_photo)
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^(Done)$"), handlers_photo.done)],
    ) 
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))    
    application.add_handler(MessageHandler(filters.Text(), unlock))
    application.add_handler(MessageHandler(filters.VOICE, media))
        
    
    application.run_polling()
####### ***************** #######   