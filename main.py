from fileinput import filename
import logging
from multiprocessing import context
import config
from xml.sax.handler import feature_namespaces
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, PicklePersistence
from handler_unlock import unlock
from handler_start import start
import handler_media

####### Setting up logging #######
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
####### ***************** #######

####### Importing Conversation handler for Photo processing #######
import handlers_photo


from telegram import Update 
from telegram.ext import ContextTypes 

my_persistence = PicklePersistence(filepath = 'my_file')

async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(context.user_data)
    print("Here am I!")

####### Starting the bot #######
if __name__ == '__main__':
    application = ApplicationBuilder().token(config.TOKEN).persistence(persistence=my_persistence).build()

    photo_conv_handler = ConversationHandler(        
        entry_points=[MessageHandler(filters.PHOTO, handlers_photo.photo)],
        states={
            handlers_photo.CHOICE: [
                MessageHandler(filters.Regex("^(Yes|No, Try Again)$"), handlers_photo.improve_photo)
            ],
            handlers_photo.MORE: [
                MessageHandler(filters.Regex("^(More)$"), handlers_photo.photo_more_translation)
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("^(Done)$"), handlers_photo.done)],
        name = "photo_conversation",
        persistent  =   True
    ) 

    #application.add_handler(MessageHandler(filters.VOICE, media))
    media_conv_handler = ConversationHandler(        
        entry_points=[MessageHandler(filters.VOICE, handler_media.media)],
        states={
            handler_media.CHOICE: [
                MessageHandler(filters.Regex("^(More)$"), handler_media.media_more)
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^(Done)$"), handler_media.media_done)],
        name = "voice_conversation",
        persistent  =   True
    )     

    application.add_handler(photo_conv_handler)
    application.add_handler(media_conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('debug', debug))    
    application.add_handler(MessageHandler(filters.Text(), unlock))

    
    application.run_polling()
####### ***************** #######