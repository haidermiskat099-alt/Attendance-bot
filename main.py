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

# Tracking State: maps student_name -> telegram_user_id
attendance_records = {}


# ----------------------------------------------------
# 2. ATTENDANCE COMMAND
# ----------------------------------------------------
async def attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global attendance_records
    attendance_records = {}  # Reset session

    opening_text = (
        "🔥 *কইরে henglu পেঙ্গলু er দল!!* 🔥\n\n"
        "সবাই নিজের অ্যাটেনডেন্স জানিয়ে দাও !! 🚀✨\n\n"
        "_Click YOUR own name button below to mark your presence:_"
    )

    all_students = sorted(BOYS + GIRLS)
    keyboard = []

    row = []
    for name in all_students:
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
# 3. INTERACTIVE BUTTON HANDLER (LOCKED TO USER ID)
# ----------------------------------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data.startswith("mark_"):
        student_name = data.split("_")[1]

        # Check 1: Has anyone already claimed this name?
        if student_name in attendance_records:
            if attendance_records[student_name] == user_id:
                await query.answer(
                    text=f"⚠️ {student_name}, তুমি তো ইতিমধ্যেই Present দিয়ে ফেলেছো! 😅",
                    show_alert=True,
                )
            else:
                await query.answer(
                    text=f"❌ {student_name}-এর অ্যাটেনডেন্স অন্য কেউ দিয়ে দিয়েছে! তুমি শুধু তোমার নিজের নামের বাটন চাপতে পারবে।",
                    show_alert=True,
                )
            return

        # Check 2: Has this Telegram user already claimed a DIFFERENT name?
        if user_id in attendance_records.values():
            await query.answer(
                text="⚠️ তুমি তো ইতিমধ্যেই অন্য নামে Present দিয়ে দিয়েছো! একজন একবারই অ্যাটেনডেন্স দিতে পারবে। 😅",
                show_alert=True,
            )
            return

        # Success: Lock the name to this Telegram user ID
        attendance_records[student_name] = user_id
        await query.answer(
            text=f"🎉 Boom! {student_name} is Present! 🟢", show_alert=False
        )

    elif data == "finish_attendance":
        await query.answer()
        await generate_final_report(query)


# ----------------------------------------------------
# 4. REPORT GENERATION
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

    if present_girls > present_boys:
        report_text += "💃 *পেঙ্গলু গুলো আজকে বেশি আছে!* 💥\n"
    elif present_boys > present_girls:
        report_text += "🕺 *হেঙ্গলু গুলো আজকে বেশি আছে!* 💥\n"
    else:
        report_text += "⚖️ *আজকে হেঙ্গলু আর পেঙ্গলু একদম সমান সমান!* 🤝\n"

    report_text += "`" + "=" * 32 + "`\n\n"
    report_text += (
        "✨ *ধন্যবাদ সবাইকে! সবাই ভালোভাবে পড়াশোনা করো এবং সুস্থ থেকো!* 🙏❤️"
    )

    await query.edit_message_text(text=report_text, parse_mode="Markdown")


# ----------------------------------------------------
# MAIN ENGINE
# ----------------------------------------------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Changed command to /attendance
    app.add_handler(CommandHandler("attendance", attendance))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Attendance Bot Started...")
    app.run_polling()
