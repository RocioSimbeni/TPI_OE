import telebot
import json
import os


TOKEN = "8616300510:AAHDpBILl6dByVx-TZrmfRzHZGJ3JJksYGc"
bot = telebot.TeleBot(TOKEN)

ARCHIVO_BD = "base_datos.json"

estados_usuarios = {}


def cargar_base_datos():
    if not os.path.exists(ARCHIVO_BD):
        datos = {
            "1001": {"nombre": "Ana Gomez", "dias_disponibles": 14},
            "1002": {"nombre": "Carlos Perez", "dias_disponibles": 5},
            "1003": {"nombre": "Lucia Fernandez", "dias_disponibles": 0}
        }
        guardar_base_datos(datos)
        return datos
    with open(ARCHIVO_BD, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_base_datos(datos):
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)


@bot.message_handler(commands=['start', 'help'])
def enviar_bienvenida(message):
    chat_id = message.chat.id

    estados_usuarios[chat_id] = {"estado": "INICIO", "empleado_id": None}
    
    texto_bienvenida = (
        "*Asistente Virtual de RRHH*\n"
        "=========================\n"
        "¡Hola! Bienvenido al sistema automatizado de gestión de licencias.\n\n"
        "Por favor, para comenzar, *ingresá tu ID de empleado* (Ej: 1001):"
    )
    bot.send_message(chat_id, texto_bienvenida, parse_mode="Markdown")



@bot.message_handler(func=lambda message: True)
def procesar_flujo(message):
    chat_id = message.chat.id
    texto_usuario = message.text.strip()
    bd = cargar_base_datos()


    if chat_id not in estados_usuarios:
        estados_usuarios[chat_id] = {"estado": "INICIO", "empleado_id": None}
        bot.send_message(chat_id, "Por favor, inicia el proceso escribiendo /start")
        return

    estado_actual = estados_usuarios[chat_id]["estado"]


    if estado_actual == "INICIO":

        if texto_usuario in bd:
            estados_usuarios[chat_id]["empleado_id"] = texto_usuario
            estados_usuarios[chat_id]["estado"] = "ESPERANDO_DIAS" 
            
            nombre = bd[texto_usuario]["nombre"]
            dias = bd[texto_usuario]["dias_disponibles"]
            
            respuesta = (
                f"*Autenticación Exitosa*\n"
                f"Empleado: {nombre}\n"
                f"Días de vacaciones disponibles: *{dias}* días.\n\n"
                f"Por favor, ingresá la *cantidad de días* que te querés tomar:"
            )
            bot.send_message(chat_id, respuesta, parse_mode="Markdown")
        else:

            bot.send_message(chat_id, "*Error:* El ID ingresado no existe en los registros.\nPor favor, intentalo de nuevo:")

    elif estado_actual == "ESPERANDO_DIAS":

        if not texto_usuario.isdigit():
            bot.send_message(chat_id, "*Error de formato:* Por favor, ingresá únicamente números enteros (Ej: 5):")
            return

        dias_solicitados = int(texto_usuario)
        emp_id = estados_usuarios[chat_id]["empleado_id"]
        dias_totales = bd[emp_id]["dias_disponibles"]


        if dias_solicitados <= 0:
            bot.send_message(chat_id, "La cantidad de días debe ser mayor a 0. Ingresá otro valor:")
        
        elif dias_solicitados <= dias_totales:

            bd[emp_id]["dias_disponibles"] -= dias_solicitados
            guardar_base_datos(bd)
            
            respuesta_final = (
                f"*¡SOLICITUD APROBADA!*\n"
                f"Se han descontado {dias_solicitados} días de tu saldo.\n"
                f"Tu nuevo saldo disponible es: *{bd[emp_id]['dias_disponibles']}* días.\n\n"
                f"El proceso ha finalizado con éxito. ¡Que disfrutes tus vacaciones!"
            )
            bot.send_message(chat_id, respuesta_final, parse_mode="Markdown")
            estados_usuarios[chat_id]["estado"] = "FIN" 
        
        else:

            bot.send_message(
                chat_id, 
                f"*Solicitud Rechazada*\n"
                f"No tenés días suficientes. Solicitaste {dias_solicitados} pero tu saldo es de {dias_totales}.\n"
                f"Por favor, ingresá una cantidad menor:"
            )


    elif estado_actual == "FIN":
        bot.send_message(chat_id, "El trámite ya terminó. Si querés realizar otra solicitud, escribí /start")



if __name__ == "__main__":
    print("El bot de Telegram está corriendo... Presiona Ctrl+C para apagarlo.")
    bot.infinity_polling()