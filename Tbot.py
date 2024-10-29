import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Dictionary to store expenses
expenses = {}

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Add Expense", callback_data='add')],
        [InlineKeyboardButton("Show Expenses", callback_data='show')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome! Please choose an option:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if query.data == 'add':
        query.edit_message_text(text="Please send the expense in the format: amount category")
        context.user_data['awaiting_expense'] = True
    elif query.data == 'show':
        show_expenses(query, context)

def add_expense(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('awaiting_expense'):
        try:
            amount, category = update.message.text.split()
            amount = float(amount)
            if category not in expenses:
                expenses[category] = 0
            expenses[category] += amount
            update.message.reply_text(f'Added: {amount} to category {category}')
        except (ValueError, IndexError):
            update.message.reply_text('Please use the format: amount category')
        finally:
            context.user_data['awaiting_expense'] = False

def show_expenses(update: Update, context: CallbackContext) -> None:
    if not expenses:
        update.message.reply_text('No expenses recorded.')
        return
    message = 'Your expenses:\n'
    for category, amount in expenses.items():
        message += f'{category}: {amount}\n'
    update.message.reply_text(message)

def main() -> None:
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, add_expense))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()