import os
import threading
from datetime import datetime
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- Web Server for Render.com (Health Check) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Chef Gari Bot is active! Let's cook!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Bot Content (Recipes & Malaysian Culinary Knowledge) ---

LEARNING_CONTENT = [
    # Day 1: Nasi Lemak
    "🍳 *Day 1: Nasi Lemak (Malaysia's National Pride)*\n\n"
    "Nasi Lemak is our national dish! The secret lies in the rich coconut rice and a well-balanced sambal.\n\n"
    "*Main Ingredients:*\n"
    "- Rice, Coconut Milk, Pandan Leaves, Ginger.\n"
    "- Anchovies, Peanuts, Boiled Egg, Cucumber.\n\n"
    "*Simple Method:*\n"
    "1. Cook the rice with coconut milk, a pinch of salt, ginger, and pandan leaves.\n"
    "2. Sauté blended chilies with onions, garlic, and tamarind juice until the oil separates for the sambal.\n"
    "3. Serve with garnishes and your favorite side dishes!",

    # Day 2: Chicken Satay
    "🍢 *Day 2: Chicken Satay & Peanut Sauce*\n\n"
    "Satay is known for its charcoal-grilled aroma and aromatic spice marinade.\n\n"
    "*Marinade Secrets:*\n"
    "- Turmeric (for that golden yellow color).\n"
    "- Lemongrass, Galangal, and Cumin.\n\n"
    "*Chef's Tips:*\n"
    "Use a stalk of lemongrass to brush oil onto the satay while grilling to keep the meat moist and fragrant!",

    # Day 3: Malaysian Laksa
    "🍜 *Day 3: The Diversity of Laksa*\n\n"
    "Malaysia has various types of laksa depending on the state!\n"
    "- *Northern Laksa:* Sour fish-based broth (Asam Laksa).\n"
    "- *Sarawak Laksa:* Spiced coconut broth with shrimp.\n"
    "- *Laksam:* Rolled rice noodles with a thick white coconut gravy.\n\n"
    "Which one is your favorite? All of them use fresh herbs like Vietnamese coriander (daun kesum) and ginger torch bud (bunga kantan)."
]

QUIZ_DATA = [
    {
        "question": "Which main ingredient provides the fragrant aroma to Nasi Lemak?",
        "options": ["Pandan Leaves", "Cinnamon", "Black Pepper"],
        "correct": 0
    },
    {
        "question": "Which spice gives the yellow color to the Satay marinade?",
        "options": ["Chili", "Turmeric", "Cumin"],
        "correct": 1
    },
    {
        "question": "Which leaf is often used in Laksa broth for its unique aroma?",
        "options": ["Curry Leaf", "Soup Leaf (Celery/Parsley)", "Vietnamese Coriander (Kesum)"],
        "correct": 2
    }
]

# --- Bot Logic ---
user_progress = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_progress:
        user_progress[user_id] = {"day": 0, "quiz_day": 0, "last_learned_date": None}
    
    # Menu in English
    keyboard = [
        ["Start Learning to Cook 🍳", "Cooking Quiz 🧠"],
        ["Take a Break ☕"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        f"Welcome to *Chef Gari Bot*! 👨‍🍳🇲🇾\n\n"
        "I will teach you the secrets of Malaysia's best dishes step-by-step.\n"
        "Please select a menu below to begin."
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in user_progress:
        user_progress[user_id] = {"day": 0, "quiz_day": 0, "last_learned_date": None}

    if text == "Start Learning to Cook 🍳":
        current_day = user_progress[user_id]["day"]
        today = str(datetime.now().date())
        
        if user_progress[user_id]["last_learned_date"] == today:
            await update.message.reply_text("You have already learned today's recipe! See you tomorrow for a new menu. ✨")
            return

        if current_day < len(LEARNING_CONTENT):
            await update.message.reply_text(LEARNING_CONTENT[current_day], parse_mode='Markdown')
            user_progress[user_id]["day"] += 1
            user_progress[user_id]["last_learned_date"] = today
        else:
            await update.message.reply_text("Congratulations! You have learned all the basic recipes. Stay tuned for further updates!")

    elif text == "Cooking Quiz 🧠":
        current_quiz_idx = user_progress[user_id]["quiz_day"]
        
        if current_quiz_idx < len(QUIZ_DATA):
            q = QUIZ_DATA[current_quiz_idx]
            buttons = [[InlineKeyboardButton(opt, callback_data=f"quiz_{idx}")] for idx, opt in enumerate(q["options"])]
            reply_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(f"Quiz Question:\n\n{q['question']}", reply_markup=reply_markup)
        else:
            await update.message.reply_text("You have answered all the quizzes! You are truly a cooking expert! 🌟")

    elif text == "Take a Break ☕":
        await update.message.reply_text("Alright, go grab a coffee! I'll be waiting here for your next cooking session. 👨‍🍳")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    current_quiz_idx = user_progress[user_id]["quiz_day"]
    if current_quiz_idx >= len(QUIZ_DATA):
        return

    selected_option = int(query.data.split("_")[1])
    if selected_option == QUIZ_DATA[current_quiz_idx]["correct"]:
        feedback = "Correct! Spot on! ✅\n\n"
    else:
        feedback = "Ouch, that's wrong! Good try though.\n\n"
    
    feedback += "Keep learning to become a great Chef! See you again! 🌟"
    user_progress[user_id]["quiz_day"] += 1
    await query.edit_message_text(text=feedback)

if __name__ == '__main__':
    # Run Flask in a separate thread
    threading.Thread(target=run_flask, daemon=True).start()
    
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    if not TOKEN:
        print("CRITICAL ERROR: TELEGRAM_TOKEN environment variable not found.")
        exit(1)
    
    print("Starting Chef Gari Bot (Malaysian Edition)...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    application.run_polling()
