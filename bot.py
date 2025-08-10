import os
import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

# ⚙ Configuración desde variables de entorno (seguro)
TOKEN = os.getenv("TOKEN")
USUARIO_ADMIN = int(os.getenv("USUARIO_ADMIN", "0"))
ARCHIVO = "respuestas.json"

# Crear archivo de respuestas si no existe
if not os.path.exists(ARCHIVO):
    with open(ARCHIVO, "w") as f:
        json.dump({}, f)

def cargar_respuestas():
    with open(ARCHIVO, "r") as f:
        return json.load(f)

def guardar_respuestas(respuestas):
    with open(ARCHIVO, "w") as f:
        json.dump(respuestas, f)

# 📌 Comando para agregar respuesta (solo admin)
async def agregar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USUARIO_ADMIN:
        await update.message.reply_text("⛔ No tienes permiso para usar este comando.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /agregar <pregunta> <respuesta>")
        return
    pregunta = context.args[0].lower()
    respuesta = " ".join(context.args[1:])
    respuestas = cargar_respuestas()
    respuestas[pregunta] = respuesta
    guardar_respuestas(respuestas)
    await update.message.reply_text(f"✅ Respuesta agregada para: {pregunta}")

# 📌 Comando para borrar respuesta (solo admin)
async def borrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USUARIO_ADMIN:
        await update.message.reply_text("⛔ No tienes permiso para usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /borrar <pregunta>")
        return
    pregunta = context.args[0].lower()
    respuestas = cargar_respuestas()
    if pregunta in respuestas:
        del respuestas[pregunta]
        guardar_respuestas(respuestas)
        await update.message.reply_text(f"🗑 Respuesta borrada para: {pregunta}")
    else:
        await update.message.reply_text("❌ No existe esa pregunta.")

# 📌 Responder mensajes
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text.lower()
    respuestas = cargar_respuestas()
    if mensaje in respuestas:
        await update.message.reply_text(respuestas[mensaje])

# 📌 Iniciar bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot activo y listo.")

# 🚀 Arrancar bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("agregar", agregar))
    app.add_handler(CommandHandler("borrar", borrar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    print("🟢 Bot iniciado...")
    app.run_polling()
