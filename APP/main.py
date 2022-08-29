from fileinput import filename
import logging
from multiprocessing import context
import config
from xml.sax.handler import feature_namespaces
from telegram import Update 
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, PicklePersistence, ContextTypes
from handler_unlock import unlock
from handler_start import start
import handlers_photo
import handler_media
from flask import Flask, request
import asyncio
import http
import config

async def main() -> None:
    ####### Setting up logging #######
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    
    # Creating a file to store data between requests
    my_persistence = PicklePersistence(filepath = 'file_persistence')

    # If webhook is True then we assume it is in container and it requires custom web server, thus we need custom UDATER, if not then run with built in UDPATER 
    application = ApplicationBuilder().token(config.TOKEN).updater(None).persistence(persistence=my_persistence).build()
    await application.update_queue.put(
            Update.de_json(data = request.get_json(force=True), bot=application.bot)
    )
    
    # adding handlers
    application.add_handler(handlers_photo.photo_conv_handler)
    application.add_handler(handler_media.media_conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Text(), unlock))
    
    # Start and run the application    
    async with application:
        await application.start()
        # when some shutdown mechanism is triggered:
        await application.stop()

##########################################
# custom web server when webhook is enabled
webserver = Flask(__name__)
@webserver.route("/", methods = ['GET', 'POST'])
def index():
    asyncio.run(main())    
    return "", http.HTTPStatus.NO_CONTENT

##########################################
# We ignore FLASK if Webhook is set up and starting in debug mode for local testing using getUdpates
# Checking Webhook parameter and starting application in getUpdates mode. 
if config.WEBHOOK == False:
       ####### Setting up logging #######
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    
    # Creating a file to store data between requests
    my_persistence = PicklePersistence(filepath = 'file_persistence')
    application = ApplicationBuilder().token(config.TOKEN).persistence(persistence=my_persistence).build()        
    
    # adding handlers
    application.add_handler(handlers_photo.photo_conv_handler)
    application.add_handler(handler_media.media_conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Text(), unlock))
    
    # Start and run the application using getUpdates mode. For local usage. 
    application.run_polling()