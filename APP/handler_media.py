from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes 
from google.cloud import speech
import config
import translator as tr 

CHOICE = 0
#### Preparing UI ####
reply_keyboard = [
    ["More", "Done"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


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
        translation_routine = tr.Translator(text_to_translate)
        translated_text = translation_routine.get(0,6)    
        # update persistence
        translation_routine.update_persistence(update, context)

        print("UserID: {}, has requested {} and get response {}".format(update.effective_user.id, text_to_translate, translated_text )) #this requires some updates

        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            parse_mode= "Markdown",
            text = "You entered *{}* and here what I found for you: \n{}".format(text_to_translate, translated_text),
            reply_markup = markup
            )
        return CHOICE

    else:
        await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text = "You entered incorrect password"
            )

async def media_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    temp_key_for_translation = context.user_data["temp_key_for_translation"]

    await context.bot.send_message(
            chat_id = update.effective_chat.id,
            parse_mode= "Markdown",
            text = "More fore *{}* : \n{}".format(temp_key_for_translation,   "\n".join(context.user_data["history"][temp_key_for_translation].split('\n')[6:])            )
            )
    return -1

async def media_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    return -1
