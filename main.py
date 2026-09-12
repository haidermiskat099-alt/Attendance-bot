import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Updated roster with actual names
ROSTER = {
    "01": "KOEL (MAY 02)",
    "02": "AURA (JAN 09)",
    "03": "HAIDER (JUL 15)",
    "04": "SAEED (AUG 27)",
    "05": "PRITHWI (JUL 22)",
    "06": "SUBHANKAR (OCT 09)"
}

active_session = {
    "active": False,
    "present": set(),
    "message_id": None,
    "chat_id": None
}

def build_keyboard():
    keyboard = []
    row = []
    for roll, name in ROSTER.items():
        is_present = roll in active_session["present"]
        status = "✅" if is_present else "❌"
        text = f"{status} {roll}. {name}"
        row.append(InlineKeyboardButton(text, callback_data=f"mark_{roll}"))
        
        if len(row) == 2:  # Displays 2 students per row
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
        
    keyboard.append([InlineKeyboardButton("🏁 End Attendance", callback_data="end_session")])
    return InlineKeyboardMarkup(keyboard)

async def start_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_session
    active_session = {
        "active": True,
        "present": set(),
        "chat_id": update.effective_chat.id
    }
    
    msg = await update.message.reply_text(
        "📋 **Attendance Session Started**\n\nTap your roll/name to mark present:",
        reply_markup=build_keyboard(),
        parse_mode="Markdown"
    )
    active_session["message_id"] = msg.message_id

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if not active_session["active"]:
        await query.answer("This session has ended.", show_alert=True)
        return

    data = query.data
    if data.startswith("mark_"):
        roll = data.split("_")[1]
        
        if roll in active_session["present"]:
            active_session["present"].remove(roll)
            await query.answer(f"Roll {roll} marked absent.")
        else:
            active_session["present"].add(roll)
            await query.answer(f"Roll {roll} marked present!")

        await query.edit_message_reply_markup(reply_markup=build_keyboard())

    elif data == "end_session":
        active_session["active"] = False
        
        present_list = sorted(list(active_session["present"]))
        absent_list = sorted([r for r in ROSTER.keys() if r not in active_session["present"]])

        present_str = "\n".join([f"• Roll {r}: {ROSTER[r]}" for r in present_list]) or "None"
        absent_str = "\n".join([f"• Roll {r}: {ROSTER[r]}" for r in absent_list]) or "None"

        summary = (
            "📊 **FINAL ATTENDANCE REPORT**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✅ **PRESENT ({len(present_list)}):**\n{present_str}\n\n"
            f"❌ **ABSENT ({len(absent_list)}):**\n{absent_str}\n"
        )
        await query.edit_message_text(summary, parse_mode="Markdown")

def main():
    token = "8606133927:AAEjxIemS0IFquD55YNeYkFWximqjL-u1UU"
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("attendance", start_attendance))
    app.add_handler(CallbackQueryHandler(handle_button))
    
    print("Bot is running... Press Ctrl+C in Pydroid to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
