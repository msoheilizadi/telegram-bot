import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

TOKEN = "7276512374:AAF0_T8syIAh4j67q0KIVdHkJtAWSMaIwZ4"

# Database setup
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_user_language(user_id, language):
    """Save or update the user's selected language in the database."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, language) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET language=?", (user_id, language, language))
    conn.commit()
    conn.close()

def get_user_language(user_id):
    """Retrieve the user's language from the database."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

async def start(update: Update, context: CallbackContext):
    """Ask user to choose a language if not already saved."""
    user_id = update.message.chat.id
    saved_language = get_user_language(user_id)

    if saved_language:
        await send_main_menu(update, saved_language)  # Show main menu in saved language
    else:
        # Language Selection Buttons
        language_keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa")]
        ]
        language_markup = InlineKeyboardMarkup(language_keyboard)

        await update.message.reply_text("🌍 Please choose your language:\n\n🇬🇧 Select English\n🇮🇷 زبان فارسی را انتخاب کنید", reply_markup=language_markup)

async def set_language(update: Update, context: CallbackContext):
    """Store selected language and show corresponding buttons."""
    query = update.callback_query
    user_id = query.message.chat.id

    language = "en" if query.data == "lang_en" else "fa"
    save_user_language(user_id, language)  # Save language to DB

    await query.answer()
    await send_main_menu(update, language)

async def send_main_menu(update: Update, language):
    """Send the main menu with buttons in the selected language."""
    reply_keyboard_en = [
        [KeyboardButton("📌 Services"), KeyboardButton("📞 Contact Support")],
        [KeyboardButton("ℹ️ About Us")]
    ]
    reply_keyboard_fa = [
        [KeyboardButton("📌 خدمات"), KeyboardButton("📞 پشتیبانی")],
        [KeyboardButton("ℹ️ درباره ما")]
    ]

    reply_markup = ReplyKeyboardMarkup(reply_keyboard_en if language == "en" else reply_keyboard_fa, resize_keyboard=True)

    await update.callback_query.message.reply_text(
        "✅ Language set to English." if language == "en" else "✅ زبان فارسی انتخاب شد.",
        reply_markup=reply_markup
    )

async def handle_text(update: Update, context: CallbackContext):
    """Handle user messages based on selected language."""
    user_id = update.message.chat.id
    lang = get_user_language(user_id) or "en"

    text = update.message.text

    responses = {
        "en": {
            "📌 Services": "Here are our services:\n- Service 1\n- Service 2",
            "📞 Contact Support": "📩 Contact us at: support@example.com",
            "ℹ️ About Us": "We are BAM Intelligence, providing smart solutions!"
        },
        "fa": {
            "📌 خدمات": "🔹 خدمات ما:\n- سرویس ۱\n- سرویس ۲",
            "📞 پشتیبانی": "📩 تماس با ما: support@example.com",
            "ℹ️ درباره ما": "ما BAM Intelligence هستیم، ارائه‌دهنده راهکارهای هوشمند!"
        }
    }

    reply = responses[lang].get(text, "❓ Invalid command." if lang == "en" else "❓ دستور نامعتبر است.")
    await update.message.reply_text(reply)

def main():
    init_db()  # Initialize the database

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()
