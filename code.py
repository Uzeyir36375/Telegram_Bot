import logging
import requests
import json
import base64
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Telegram bot API key
TELEGRAM_BOT_API_KEY = '7151600512:AAG23UiUgR8lwbLkO-t4GQwYhws4LBgHhvI'  # Replace with your actual Telegram bot API key

# Relevance AI details
RELEVANCE_REGION = 'f1db6c'
RELEVANCE_PROJECT_ID = '33ac7d2d8648-43fb-ba5c-c3f6d391baed'
RELEVANCE_AGENT_ID = '74abae77-ae58-4368-bbb8-9c5dec6f3962'
RELEVANCE_API_KEY = 'sk-ZjMxNTRiNmUtYTViYi00NGEwLWIwMzktNzgwMDY0YmRhNTE5'  # Replace with the new API key

# Construct the authorization token
AUTHORIZATION_TOKEN = f"{RELEVANCE_PROJECT_ID}:{RELEVANCE_API_KEY}"

# Endpoint URL
RELEVANCE_AI_API_ENDPOINT = f'https://api-{RELEVANCE_REGION}.stack.tryrelevance.com/latest/agents/trigger'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hi! Send me a text and a file, and I will process them.')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    context.user_data['text'] = text
    await update.message.reply_text('Text received. Now, please send me a file.')

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'text' not in context.user_data:
        await update.message.reply_text('Please send the text first.')
        return
    
    file = update.message.document
    file_id = file.file_id
    new_file = await context.bot.get_file(file_id)
    file_path = new_file.file_path
    
    # Download the file
    file_response = requests.get(file_path)
    file_content = file_response.content
    
    # Convert file content to base64
    file_content_base64 = base64.b64encode(file_content).decode('utf-8')
    
    text = context.user_data['text']
    
    # Prepare the payload for the API
    payload = {
        "message": {
            "role": "user",
            "content": text
        },
        "agent_id": RELEVANCE_AGENT_ID,
        "file": file_content_base64
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {AUTHORIZATION_TOKEN}'
    }
    
    # Log the payload and headers for debugging
    logger.info(f'Sending payload: {json.dumps(payload, indent=2)}')
    logger.info(f'Headers: {headers}')

    response = requests.post(RELEVANCE_AI_API_ENDPOINT, headers=headers, data=json.dumps(payload))
    
    # Log the response for debugging
    logger.info(f'API response status code: {response.status_code}')
    logger.info(f'API response content: {response.content.decode()}')

    if response.status_code == 200:
        response_data = response.json()
        await update.message.reply_text(f'Response from API: {response_data}')
    else:
        await update.message.reply_text(f'Failed to get a response from the API. Status code: {response.status_code}. Response: {response.content.decode()}')
    
    # Clear the user data
    context.user_data.clear()

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    application.run_polling()

if __name__ == "__main__":
    main()
