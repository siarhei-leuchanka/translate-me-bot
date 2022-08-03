from telegram import Update
from telegram.ext import ContextTypes 
from google.cloud import speech
import config
import translator as tr

async def media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in config.SPECIAL_USERS:
        # getting audio that has been sent and converting it into bytes format
        raw_audio = await context.bot.get_file(file_id = update.message.voice.file_id)    
        bytes_audio = await raw_audio.download_as_bytearray() 
        bytes_audio = bytes(bytes_audio)  

        # Instantiates a client
        client = speech.SpeechClient()
        speach2text_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=48000,
            language_code="cs-CZ",
        )                      
        audio =  speech.RecognitionAudio(content=bytes_audio)
        
        # Detects speech in the audio file
        response = client.recognize(config=speach2text_config, audio=audio)                
        text_to_translate = " | ".join([result.alternatives[0].transcript for result in response.results])        
        
        # Translating text from Slovink.cz
        translated_text = tr.Translator(text_to_translate).get()
        
        print("UserID: {}, has requested {} and get response {}".format(update.effective_user.id, text_to_translate, translated_text )) #this requires some updates

        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            parse_mode= "Markdown",
            text = "You entered *{}* and here what I found for you: \n{}".format(text_to_translate, translated_text)
            )

        #### storing it in persistence layer to access later
        #checking for dictionary if it is there
        if 'history' not in context.user_data:
            context.user_data["history"] = {}
        context.user_data["history"][text_to_translate] = translated_text

    else:
        await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text = "You entered incorrect password"
            )