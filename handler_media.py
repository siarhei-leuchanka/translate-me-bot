from telegram import Update
from telegram.ext import ContextTypes 
from google.cloud import speech
from bs4 import BeautifulSoup
import config

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

async def media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in config.SPECIAL_USERS:
        
        # Instantiates a client
        client = speech.SpeechClient()
        speach2text_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=48000,
        language_code="cs-CZ",
        )                
        raw_audio = await context.bot.get_file(file_id = update.message.voice.file_id)    
        bytes_audio = await raw_audio.download_as_bytearray()
        bytes_audio = bytes(bytes_audio)        
        audio =  speech.RecognitionAudio(content=bytes_audio)
        
        # Detects speech in the audio file
        response = client.recognize(config=speach2text_config, audio=audio)
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
        
        #### storing it in persistence layer to access later
        #checking for dictionary if it is there
        if 'history' not in context.user_data:
            context.user_data["history"] = {}
        context.user_data["history"][text_to_translate] = text_to_send

    else:
        await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text = "You entered incorrect password"
            )