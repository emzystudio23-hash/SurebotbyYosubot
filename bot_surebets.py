import logging
import asyncio
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 1. CONFIGURACIÓN INICIAL
# Reemplaza con el Token que te dé @BotFather en Telegram
TOKEN_BOT = "TU_TELEGRAM_BOT_TOKEN_AQUÍ"

# Configuración de logs para ver errores en consola
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Variable global temporal para controlar el estado del escáner
escanner_activo = False

# ==========================================
# 2. SECCIÓN MODULAR: AQUÍ IRÁ TU API MÁS TARDE
# ==========================================
async def obtener_datos_reales_de_api():
    """
    [ZONA DE RESERVA] 
    Cuando tengas tus API Keys (de las casas de apuestas o un proveedor como The Odds API),
    reemplazarás este diccionario estático con una petición web real (usando httpx o requests).
    """
    # Lista de ejemplos que simulan datos crudos del mercado español
    partidos_mock = [
        {"home": "Real Madrid", "away": "Barcelona", "sport": "Fútbol - LaLiga"},
        {"home": "Carlos Alcaraz", "away": "Novak Djokovic", "sport": "Tenis - Wimbledon"},
        {"home": "Atlético de Madrid", "away": "Sevilla", "sport": "Fútbol - LaLiga"},
        {"home": "Baskonia", "away": "Real Madrid Basket", "sport": "Baloncesto - ACB"}
    ]
    
    casas_mock = ["Bet365", "Codere", "William Hill", "888Sport", "Bwin", "Luckia"]
    
    # Generamos un partido aleatorio simulado
    partido = random.choice(partidos_mock)
    casa1, casa2 = random.sample(casas_mock, 2)
    
    # Generamos cuotas que matemáticamente fuercen una surebet aleatoria para el MVP
    cuota_a = round(random.uniform(2.10, 2.40), 2)
    cuota_b = round(random.uniform(1.95, 2.20), 2)
    
    return {
        "evento": f"{partido['home']} vs {partido['away']}",
        "deporte": partido["sport"],
        "mercado": "Ganador del Partido (12)",
        "casa_a": casa1,
        "cuota_a": cuota_a,
        "casa_b": casa2,
        "cuota_b": cuota_b
    }

# ==========================================
# 3. LÓGICA DE ARBITRAJE MATEMÁTICO
# ==========================================
def calcular_surebet(cuota_1, cuota_2):
    """
    Aplica el algoritmo de arbitraje para mercados binarios.
    Retorna (HaySurebet, PorcentajeBeneficio)
    """
    probabilidad_inversa = (1 / cuota_1) + (1 / cuota_2)
    if probabilidad_inversa < 1.0:
        beneficio = (1 - probabilidad_inversa) * 100
        return True, beneficio
    return False, 0

# ==========================================
# 4. COMANDOS Y MENÚ DEL BOT EN TELEGRAM (ESPAÑOL)
# ==========================================
async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra el panel de control principal al usuario."""
    usuario = update.effective_user.first_name
    texto = (
        f"👋 ¡Hola {usuario}! Bienvenido al **MVP de Arbitraje Deportivo**.\n\n"
        f"Este bot está diseñado al estilo de BetBurger para escanear cuotas en "
        f"casas de apuestas de España y enviarte Surebets garantizadas.\n\n"
        f"⚡ **Estado del Escáner:** {'🟢 ACTIVO' if escanner_activo else '🔴 APAGADO'}"
    )
    
    # Botones interactivos bajo el mensaje
    botones = [
        [
            InlineKeyboardButton("▶️ Iniciar Escáner", callback_data="iniciar"),
            InlineKeyboardButton("🛑 Detener Escáner", callback_data="detener")
        ],
        [
            InlineKeyboardButton("📊 Ver Estado", callback_data="estado")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(botones)
    
    await update.message.reply_text(texto, parse_mode="Markdown", reply_markup=reply_markup)

async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Administra las acciones de los botones interactivos."""
    global escanner_activo
    query = update.callback_query
    await query.answer() # Evita el reloj de arena en Telegram
    
    chat_id = query.message.chat_id

    if query.data == "iniciar":
        if not escanner_activo:
            escanner_activo = True
            await query.edit_message_text(
                "🟢 **Escáner Iniciado.** Empezarás a recibir Surebets en este chat cada pocos segundos.",
                parse_mode="Markdown"
            )
            # Lanzamos el bucle del escáner en segundo plano
            asyncio.create_task(bucle_escaneo(context, chat_id))
        else:
            await query.edit_message_text("⚠️ El escáner ya está corriendo actualmente.")
            
    elif query.data == "detener":
        escanner_activo = False
        await query.edit_message_text("🔴 **Escáner Detenido.** Ya no se enviarán más alertas.")
        
    elif query.data == "estado":
        estado = "🟢 Ejecutándose y buscando cuotas..." if escanner_activo else "🔴 Pausado."
        await query.message.reply_text(f"ℹ️ **Estado actual:** {estado}", parse_mode="Markdown")

# ==========================================
# 5. EL ESCÁNER AUTOMÁTICO (EL MOTOR)
# ==========================================
async def bucle_escaneo(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Bucle asíncrono que corre en segundo plano buscando arbitrajes."""
    global escanner_activo
    print("[INFO] Bucle de escaneo activado en segundo plano.")
    
    while escanner_activo:
        # 1. Consumimos la función modular (ahora simulada, mañana real)
        datos = await obtener_datos_reales_de_api()
        
        # 2. Procesamos con el algoritmo matemático
        hay_oportunidad, beneficio = calcular_surebet(datos["cuota_a"], datos["cuota_b"])
        
        # 3. Si hay beneficio, armamos la alerta limpia idéntica a BetBurger_Spain
        if hay_oportunidad:
            alerta_formateada = (
                f"⚡️ **¡SUREBET DETECTADA!** ⚡️\n"
                f"📈 **Beneficio Neto:** `{beneficio:.2f}%`\n"
                f"🏆 **Deporte:** {datos['deporte']}\n"
                f"⚽️ **Evento:** {datos['evento']}\n"
                f"📊 **Mercado:** {datos['mercado']}\n\n"
                f"1️⃣ **Opción A:** {datos['casa_a']} ➔ `{datos['cuota_a']}`\n"
                f"2️⃣ **Opción B:** {datos['casa_b']} ➔ `{datos['cuota_b']}`\n\n"
                f"📱 _Las cuotas deportivas cambian rápido. Revisa antes de apostar._"
            )
            
            await context.bot.send_message(chat_id=chat_id, text=alerta_formateada, parse_mode="Markdown")
        
        # Espera de 4 segundos antes de volver a escanear un bloque de cuotas
        await asyncio.sleep(4)

# ==========================================
# 6. INICIALIZACIÓN PRINCIPAL
# ==========================================
def main():
    """Arranca el bot de Telegram."""
    # Crear la aplicación e inyectar el Token
    application = Application.builder().token(TOKEN_BOT).build()

    # Registrar los manejadores (handlers) de comandos y botones
    application.add_handler(CommandHandler("start", comando_start))
    application.add_handler(CallbackQueryHandler(manejar_botones))

    # Iniciar el bot en modo polling (escucha constante)
    print("Bot MVP iniciado. Presiona Ctrl+C en tu terminal para detenerlo.")
    application.run_polling()

if __name__ == "__main__":
    main()
