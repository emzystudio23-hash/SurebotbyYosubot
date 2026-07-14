import logging
import asyncio
import random
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Lee el token automáticamente desde el panel de control de Railway
TOKEN_BOT = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

escanner_activo = False

async def obtener_datos_reales_de_api():
    partidos_mock = [
        {"home": "Real Madrid", "away": "Barcelona", "sport": "Fútbol - LaLiga"},
        {"home": "Carlos Alcaraz", "away": "Novak Djokovic", "sport": "Tenis - Wimbledon"},
        {"home": "Atlético de Madrid", "away": "Sevilla", "sport": "Fútbol - LaLiga"}
    ]
    casas_mock = ["Bet365", "Codere", "William Hill"]
    partido = random.choice(partidos_mock)
    casa1, casa2 = random.sample(casas_mock, 2)
    cuota_a = round(random.uniform(2.10, 2.40), 2)
    cuota_b = round(random.uniform(1.95, 2.20), 2)
    
    return {
        "evento": f"{partido['home']} vs {partido['away']}",
        "deporte": partido["sport"],
        "casa_a": casa1,
        "cuota_a": cuota_a,
        "casa_b": casa2,
        "cuota_b": cuota_b
    }

def calcular_surebet(cuota_1, cuota_2):
    probabilidad_inversa = (1 / cuota_1) + (1 / cuota_2)
    if probabilidad_inversa < 1.0:
        beneficio = (1 - probabilidad_inversa) * 100
        return True, beneficio
    return False, 0

async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Comando /start recibido.")
    usuario = update.effective_user.first_name
    texto = (
        f"👋 ¡Hola {usuario}! Bienvenido al **MVP de Arbitraje Deportivo**.\n\n"
        f"⚡ **Estado del Escáner:** {'🟢 ACTIVO' if escanner_activo else '🔴 APAGADO'}"
    )
    botones = [
        [
            InlineKeyboardButton("▶️ Iniciar Escáner", callback_data="iniciar"),
            InlineKeyboardButton("🛑 Detener Escáner", callback_data="detener")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(botones)
    await update.message.reply_text(texto, parse_mode="Markdown", reply_markup=reply_markup)

async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global escanner_activo
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if query.data == "iniciar":
        if not escanner_activo:
            escanner_activo = True
            await query.edit_message_text(
                "🟢 **Escáner Iniciado.** Recibirás Surebets aquí cada pocos segundos.",
                parse_mode="Markdown"
            )
            asyncio.create_task(bucle_escaneo(context, chat_id))
    elif query.data == "detener":
        escanner_activo = False
        await query.edit_message_text("🔴 **Escáner Detenido.**")

async def bucle_escaneo(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    global escanner_activo
    while escanner_activo:
        datos = await obtener_datos_reales_de_api()
        hay_oportunidad, beneficio = calcular_surebet(datos["cuota_a"], datos["cuota_b"])
        if hay_oportunidad:
            alerta_formateada = (
                f"⚡️ **¡SUREBET DETECTADA!** ⚡️\n"
                f"📈 **Beneficio Neto:** `{beneficio:.2f}%`\n"
                f"🏆 **Deporte:** {datos['deporte']}\n"
                f"⚽️ **Evento:** {datos['evento']}\n\n"
                f"1️⃣ **Opción A:** {datos['casa_a']} ➔ `{datos['cuota_a']}`\n"
                f"2️⃣ **Opción B:** {datos['casa_b']} ➔ `{datos['cuota_b']}`\n"
            )
            await context.bot.send_message(chat_id=chat_id, text=alerta_formateada, parse_mode="Markdown")
        await asyncio.sleep(4)

def main():
    logger.info("Iniciando aplicación del bot...")
    
    if not TOKEN_BOT:
        logger.error("❌ ERROR: La variable de entorno TELEGRAM_TOKEN no está configurada en Railway.")
        return

    application = Application.builder().token(TOKEN_BOT).build()
    application.add_handler(CommandHandler("start", comando_start))
    application.add_handler(CallbackQueryHandler(manejar_botones))
    
    logger.info("Bot listo. Iniciando polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
