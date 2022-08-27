from fileinput import filename
import logging
from multiprocessing import context
import config
from xml.sax.handler import feature_namespaces
from telegram import Update 
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, PicklePersistence, ContextTypes
from handler_unlock import unlock
from handler_start import start
import handler_media
from flask import Flask, request
import asyncio
import http

async def main() -> None:
    ####### Setting up logging #######
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    ####### ***************** #######    

    my_persistence = PicklePersistence(filepath = 'file_persistence')
    application = ApplicationBuilder().token(config.TOKEN).updater(None).persistence(persistence=my_persistence).build()

    await application.update_queue.put(
            Update.de_json(data = request.get_json(force=True), bot=application.bot)
        )        
 
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

    # adding handlers
    application.add_handler(media_conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Text(), unlock))
            
    # Start and run the application    
    async with application:
        await application.start()
        # when some shutdown mechanism is triggered:
        await application.stop()

webserver = Flask(__name__)

@webserver.route("/", methods = ['GET', 'POST'])
def index():
    asyncio.run(main())    
    return "", http.HTTPStatus.NO_CONTENT
