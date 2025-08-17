import logging
import httpx  # Use httpx for asynchronous requests
import re  # Import the regular expression module
import urllib.parse  # Import the URL parsing module
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --------------------------
# CONFIGURATION
# --------------------------
TELEGRAM_BOT_TOKEN = "8282591633:AAEccCRWwvAEOBnVGBcBmwrDqQynVerblrE"
FLOWISE_API_URL = "https://determined-brandise-11indrajith-312be074.koyeb.app/api/v1/prediction/95309642-184f-439f-afae-957a848e51cc"

# --------------------------
# LOGGING
# --------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --------------------------
# START COMMAND
# --------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello 👋 I'm your AI assistant powered by Flowise! Ask me anything.")

# --------------------------
# HANDLE MESSAGES
# --------------------------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id
    logger.info(f"Received message from {chat_id}: {user_message}")

    await context.bot.send_chat_action(chat_id=chat_id, action='typing')

    payload = {"question": user_message}
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            flowise_response = await client.post(FLOWISE_API_URL, json=payload)  # ✅ renamed to flowise_response

        if flowise_response.status_code == 200:
            data = flowise_response.json()
            response_text = data.get("text") or data.get("output") or str(data)
        else:
            logger.error(f"Flowise API Error: {flowise_response.status_code} - {flowise_response.text}")
            response_text = "⚠️ I encountered an error while processing your request. Please try again later."

    except httpx.RequestError as e:
        logger.error(f"Could not connect to Flowise API: {e}")
        response_text = "⚠️ I'm having trouble connecting to my brain right now. Please make sure the Flowise server is running."

    # --------------------------
    # CLEAN RESPONSE
    # --------------------------
    phrases_to_remove = [
        r'^Based on the provided data,?\s*',
        r'^Based on the information provided,?\s*',
        r'^Here are some laptops suitable,?\s*',
        r'^Important Note:?\s*',
        r'The provided text gives specifications for various laptops, but '
    ]
    cleaned_response = response_text
    for phrase in phrases_to_remove:
        cleaned_response = re.sub(phrase, '', cleaned_response, flags=re.IGNORECASE).strip()

    cleaned_response = re.sub(r'[*_`]', '', cleaned_response)

    laptop_pattern = r'\b(ASUS|Lenovo|HP|DELL|MSI)\s+[\w\s-]+(?= Core i| Ryzen| Athlon| Octa Core| Dual Core|\:)'
    laptop_names = re.findall(laptop_pattern, cleaned_response, re.IGNORECASE)
    
    for name in set(laptop_names):
        search_query = urllib.parse.quote_plus(name + " laptop price")
        search_url = f"https://www.google.com/search?q={search_query}"
        cleaned_response = cleaned_response.replace(name, f'<a href="{search_url}">{name}</a>')

    if cleaned_response:
        cleaned_response = cleaned_response[0].upper() + cleaned_response[1:]

    await update.message.reply_text(cleaned_response, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

# --------------------------
# MAIN FUNCTION
# --------------------------
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("✅ Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
