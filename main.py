import logging
import config
from tracemalloc import BaseFilter
from xml.sax.handler import feature_namespaces
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, Application, CallbackContext
from google.cloud import speech
from bs4 import BeautifulSoup

TOKEN = config.TOKEN
PASS = config.PASS
SPECIAL_USERS = config.SPECIAL_USERS

HELLO_TEXT = "Greeting. The bot will try to translate audio you sent to the selected language.  This is the DEMO version and functionality is password protected. Please enter a password to proceed:"

def get_translation_from_slovnik (key):
    import requests

    url = " https://www.slovnik.cz/bin/mld.fpl"
    payload = {"vcb": key ,"trn": "přeložit", "dictdir": "encz.cz", "lines": 15, "js": 1}

    r = requests.get(url, payload)
    
    return r.text

def parse_response(html):
    translation_dict = []
    soup = BeautifulSoup(  html, 'html.parser' )

    for item in soup.find_all(class_ = "pair"):        
        translation_dict.append((item.find(class_ = "l").get_text(), item.find(class_ = "r").get_text()))
    
    return translation_dict

# Instantiates a client
client = speech.SpeechClient()
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
    sample_rate_hertz=48000,
    language_code="cs-CZ",
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text = HELLO_TEXT
        )

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

async def media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in SPECIAL_USERS:
        raw_audio = await context.bot.get_file(file_id = update.message.voice.file_id)    
        bytes_audio = await raw_audio.download_as_bytearray()
        bytes_audio = bytes(bytes_audio)        
        audio =  speech.RecognitionAudio(content=bytes_audio)
        
        # Detects speech in the audio file
        response = client.recognize(config=config, audio=audio)
        text_to_translate = " | ".join([result.alternatives[0].transcript for result in response.results])
        translated_text = parse_response(get_translation_from_slovnik(text_to_translate))
        print("UserID: {}, has requested {} and get response {}".format(update.effective_user.id, text_to_translate, translated_text ))
        
        text_to_send = ""
        for i,y in translated_text:
            text_to_send += i + " - " + y + "\n"


        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            parse_mode= "Markdown",
            text = "You entered *{}* and here what I found for you: \n{}".format(text_to_translate,text_to_send)
            )
    else:
        await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text = "You entered incorrect password"
            )

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))    
    application.add_handler(MessageHandler(filters.Text(), unlock))
    application.add_handler(MessageHandler(filters.VOICE, media))
    
    application.run_polling()