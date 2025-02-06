from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mistralai import Mistral, UserMessage
import logging
import sys

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

MISTRAL_API_KEY = "mistral-api-token"  
TELEGRAM_TOKEN = "telegram-bot-token"  
MODEL_NAME = "mistral-large-latest"


client = Mistral(api_key=MISTRAL_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text("Hello! I'm your Mistral-powered bot. Send me a message!")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop command to stop the bot"""
    await update.message.reply_text("Stopping the bot...")
    context.application.stop() 
    sys.exit()
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process user messages"""
    try:
        user_input = update.message.text
        logging.info(f"Received message: {user_input}") 
        
        messages = [
            {"role": "user", "content": user_input}
        ]

        async_response = await client.chat.stream_async(model=MODEL_NAME, messages=messages)

        reply = ""
        async for chunk in async_response:
            reply += chunk.data.choices[0].delta.content
        
        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"Error in handle_message: {str(e)}", exc_info=True)
        await update.message.reply_text("Sorry, I encountered an error processing your request.")

if __name__ == "__main__":

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CommandHandler("stop", stop))
    
    logging.info("Starting bot polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
