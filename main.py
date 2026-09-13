import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# ----------------------------------------------------
# 1. BOT CONFIGURATION & CATEGORIZED ROSTER
# ----------------------------------------------------
BOT_TOKEN = "8606133927:AAHOVaafAKx17KpYnt6GsJlptRGA63Srhsk"

# Student Roster categorized for automated banter
BOYS = [
    "Abhinandan",
    "Aritra",
    "Classy",
    "Gnetlemxn",
    "Haider",
    "Ramit",
    "Ranbir",
    "Saeed",
    "Sayan",
    "Sushanta Basak",
    "Swarna",
]

GIRLS = [
    "Amina",
    "Anurima",
    "Atreyi",
    "Bidisha",
    "Koel",
    "Nasima",
    "Reshmi",
    "Saraiya",
    "Shreyoshree",
    "Sneha",
    "Sukanya Mondal",
]

# Attendance Tracking State
attendance_records = {}


# ----------------------------------------------------
# 2. START COMMAND WITH CUSTOM FUNNY OPENING
# ----------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global attendance_records
    attendance_records = {}  # Reset attendance for a new session

    opening_text = (
        "🔥 *কইরে henglu পেঙ্গলু er দল!!* 🔥\n\n"
        "সবাই নিজের অ্যাটেনডেন্স জানিয়ে দাও !! 🚀✨\n\n"
        "_Click your name button below to mark your presence:_"
    )

    all_students = sorted(BOYS + GIRLS)
    keyboard = []

    # Creating interactive buttons with 2 columns to keep it clean
    row = []
    for idx, name in enumerate(all_students, start=1):
        row.append(
            InlineKeyboardButton(
                f"⚡ {name} 🎯", callback_data=f"mark_{name}"
            )
        )
        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    # Add Finish button at the bottom
    keyboard.append(
        [
            InlineKeyboardButton(
                "🏁 Finish & Show Report 📊", callback_data="finish_attendance"
            )
        ]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        opening_text, reply_markup=reply_markup, parse_mode="Markdown"
    )


# ----------------------------------------------------
# 3. INTERACTIVE BUTTON HANDLER
# ----------------------------------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    # Marking individual presence with popup alerts
    if data.startswith("mark_"):
        student_name = data.split("_")[1]

        if student_name in attendance_records:
            await query.answer(
                text=f"⚠️ {student_name}, তুমি তো ইতিমধ্যেই Present দিয়ে ফেলেছো! 😅",
                show_alert=True,
            )
        else:
            attendance_records[student_name] = "Present"
            await query.answer(
                text=f"🎉 Boom! {student_name} is Present! 🟢", show_alert=False
            )

    # Finishing attendance and calculating stats
    elif data == "finish_attendance":
        await query.answer()
        await generate_final_report(query)


# ----------------------------------------------------
# 4. REPORT & BANTER GENERATION
# ----------------------------------------------------
async def generate_final_report(query):
    all_students = BOYS + GIRLS
    presents = list(attendance_records.keys())
    absents = [s for s in all_students if s not in presents]

    present_boys = sum(1 for s in presents if s in BOYS)
    present_girls = sum(1 for s in presents if s in GIRLS)

    report_text = "📊 *ATTENDANCE SUMMARY REPORT* 📊\n"
    report_text += "`" + "=" * 32 + "`\n\n"

    report_text += (
        f"🟢 *Present ({len(presents)}):*\n"
        + (", ".join(sorted(presents)) if presents else "None ❌")
        + "\n\n"
    )
    report_text += (
        f"🔴 *Absent ({len(absents)}):*\n"
        + (", ".join(sorted(absents)) if absents else "None 🎉")
        + "\n\n"
    )

    report_text += "`" + "-" * 32 + "`\n"

    # Gender comparison banter
    if present_girls > present_boys:
        report_text += "💃 *পেঙ্গলু গুলো আজকে বেশি আছে!* 💥\n"
    elif present_boys > present_girls:
        report_text += "🕺 *হেঙ্গলু গুলো আজকে বেশি আছে!* 💥\n"
    else:
        report_text += "⚖️ *আজকে হেঙ্গলু আর পেঙ্গলু একদম সমান সমান!* 🤝\n"

    report_text += "`" + "=" * 32 + "`\n\n"

    # Friendly closing greeting
    report_text += (
        "✨ *ধন্যবাদ সবাইকে! সবাই ভালোভাবে পড়াশোনা করো এবং সুস্থ থেকো!* 🙏❤️"
    )

    await query.edit_message_text(text=report_text, parse_mode="Markdown")


# ----------------------------------------------------
# MAIN ENGINE
# ----------------------------------------------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Attendance Bot Started...")
    app.run_polling()
    
