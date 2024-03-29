from telegram import Update
import config
import cv2
import pytesseract
#from PIL import Image only needed to see image when debugging
import numpy as np
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
import translator as tr

def recognize_text (image_binary, preprocess_options):    
    image = np.asarray (image_binary, dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    
    # get grayscale image
    def get_grayscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # noise removal
    def remove_noise(image):
        return cv2.medianBlur(image,5)
    #thresholding
    def thresholding(image):
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    if preprocess_options == 1:    
        output = get_grayscale(image)
    elif preprocess_options == 2:
        output = get_grayscale(image)        
        output = remove_noise(output)
    elif preprocess_options == 3:
        output = get_grayscale(image)        
        output = remove_noise(output)
        output = thresholding(output)
    else:
        print("That's it man")
        return None
    
    #Image.fromarray(output).show() # to show image on server

    # Adding custom options
    custom_config = r'-l ces --oem 3 --psm 6'
    text = pytesseract.image_to_string(output, config=custom_config)
    
    return text

CHOICE, MORE = 0,1

#### Preparing UI ####
reply_keyboard = [
    ["Yes", "No, Try Again"],    
    ["Done"],
    ]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

more_keyboard = [
    ["More", "Done"],
]
more_markup = ReplyKeyboardMarkup(more_keyboard, one_time_keyboard=True)
#### ************ #####

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in config.SPECIAL_USERS:
        photo = await context.bot.get_file(update.message.photo[-1].file_id)  
        photo = await photo.download_as_bytearray() 
        context.user_data["photo"] = photo #storing photo in memory to come back again and try once more with pre-processing if any issues with OCR
        output_text = recognize_text(photo, 1)
        context.user_data["text_from_photo"] = {"preprocess":1,"text":[output_text]}                         
        await context.bot.send_message(
            chat_id = update.effective_chat.id,
            text = output_text + "\n" + "Is this what you wanted?",
            reply_markup = markup
        )
        return CHOICE

async def improve_photo (update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in config.SPECIAL_USERS:
        if update.message.text == "Yes":
            output_text = context.user_data["text_from_photo"]["text"][-1]

            # Translating text from Slovink.cz
            translation_routine = tr.Translator(output_text)            
            translated_text = translation_routine.get(0,6)    
            # update persistence
            translation_routine.update_persistence(update, context)

            print("UserID: {}, has requested {} and get response {}".format(update.effective_user.id, output_text, translated_text ))
            
            await context.bot.send_message(
                chat_id = update.effective_chat.id,
                #parse_mode= "Markdown",
                text = "You requested *{}* and here what I found for you: \n{}".format(output_text, translated_text),
                reply_markup = more_markup
            )

            #removing all temporary data
            context.user_data["text_from_photo"].clear()
            context.user_data["photo"] = ""
            return MORE

        elif update.message.text == "No, Try Again":            
            context.user_data["text_from_photo"]["preprocess"] = context.user_data["text_from_photo"]["preprocess"] + 1                      
            output_text = recognize_text(context.user_data["photo"],    context.user_data["text_from_photo"]["preprocess"])
            context.user_data["text_from_photo"]["text"].append(output_text)            

            if output_text == None:
                output_text = "Please re-take photo and start again"
                await context.bot.send_message(
                chat_id = update.effective_chat.id,
                text = output_text
                )
                #removing all temporary data
                context.user_data["text_from_photo"].clear()
                context.user_data["photo"] = ""
                return -1
            else:
                await context.bot.send_message(
                    chat_id = update.effective_chat.id,
                    text = output_text + "\n" + "Is it better?",
                    reply_markup=markup
                )
                return CHOICE

async def photo_more_translation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    temp_key_for_translation = context.user_data["temp_key_for_translation"]

    await context.bot.send_message(
            chat_id = update.effective_chat.id,
            parse_mode= "Markdown",
            text = "More fore *{}* : \n{}".format(temp_key_for_translation,   "\n".join(context.user_data["history"][temp_key_for_translation].split('\n')[6:])            )
            )
    return -1

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:    
    #removing all temporary data
    context.user_data["text_from_photo"].clear()
    context.user_data["photo"] = ""

    return -1 # handle done for now

#assembling conversation handler
photo_conv_handler = ConversationHandler(        
    entry_points=[MessageHandler(filters.PHOTO, photo)],
    states={
        CHOICE: [
            MessageHandler(filters.Regex("^(Yes|No, Try Again)$"), improve_photo)
        ],
        MORE: [
            MessageHandler(filters.Regex("^(More)$"), photo_more_translation)
        ]
    },
    fallbacks=[MessageHandler(filters.Regex("^(Done)$"), done)],
    name = "photo_conversation",
    persistent  =   True
)