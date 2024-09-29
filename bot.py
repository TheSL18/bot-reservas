#!/usr/bin/env python

import os
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, BotCommand
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
from telebot import TeleBot, types

load_dotenv()

# Token del bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USER_ID = 592974024 # Reemplaza con tu ID de usuario

bot = telebot.TeleBot(BOT_TOKEN)

# Conexión a la base de datos MariaDB
def connect_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWD'),
        database=os.getenv('DB_DB'),
        charset='utf8mb4',
        collation='utf8mb4_general_ci'
    )

# Estructura de categorías y espacios
espacios = {
    "Auditorio": [
        "Auditorio B205-C202", 
        "Auditorio Escalonado Grande", 
        "Auditorio Escalonado Pequeño", 
    ],
    "Plazoleta": [
        "Plazoleta Jesus y Maria", 
        "Plazoleta RGH", 
        "Plazoleta de la Cruz", 
        "Plazoleta Verde", 
        "Plazoleta R Piso 9",
        "Hall Torre B-C",
    ],
    "Sala de Juntas": [
        "Sala de Juntas",
        "Sala de Juntas RGH",  
        "Sala de Juntas FCC",
        "Sala de Juntas FCE",
        "Sala de Juntas FING",
        "Sala de Juntas FEDU",
        "Sala de Juntas I+D",
        "Sala de Juntas FCHS",
        "Coworking 1", 
        "Coworking 2"
    ]
}

# Diccionario de imágenes asociadas
imagenes_espacios = {
    "Auditorio B205-C202": {
        "img_path": "img/b205.jpeg", 
        "descripcion": "Auditorio con capacidad para 125 personas, equipado con sistema de sonido, proyector y camara para reuniones en vivo."
    },
    "Auditorio Escalonado Grande": {
        "img_path": "img/escalonadogrande.jpg", 
        "descripcion": "Auditorio con asientos escalonados para hasta 49 personas."
    },
    "Auditorio Escalonado Pequeño": {
        "img_path": "img/auditoriopequeño.jpg", 
        "descripcion": "Auditorio con asientos escalonados para hasta 42 personas."
    },
    "Plazoleta Jesus y Maria": {
        "img_path": "img/plazoletajym.jpeg", 
        "descripcion": "Plazoleta bajo techo ideal para eventos al aire libre y actividades recreativas."
    },
    "Plazoleta RGH": {
        "img_path": "img/plazoletargh.jpeg", 
        "descripcion": "Área amplia en el campus RGH, perfecta para encuentros y actividades sociales."
    },
    "Plazoleta de la Cruz": {
        "img_path": "img/plazoletacruz.jpeg", 
        "descripcion": "Espacio al aire libre con ambiente tranquilo, Ubicada entre torres A y B."
    },
    "Plazoleta Verde": {
        "img_path": "img/plazoletaverde.jpeg", 
        "descripcion": "Plazoleta rodeada de vegetación, ideal para actividades al aire libre ubicada antes de los torniquetes de acceso a la universidad."
    },
    "Plazoleta R Piso 9": {
        "img_path": "img/plazoletar.jpeg", 
        "descripcion": "Área de encuentro VIP en el piso 9 del edificio C, con vistas panorámicas del campus a cielo abierto No se permite el ingreso a estudiantes."
    },
    "Hall Torre B-C": {
        "img_path": "img/hall.jpeg", 
        "descripcion": "Espacio principal en el corazon de las Torres B y C, ideal para exposiciones y recepciones con capacidad maxima de 30 personas."
    },
    "Sala de Juntas RGH": {
        "img_path": "img/rgh.jpeg", 
        "descripcion": "Sala de reuniones equipada con tecnología de video conferencia y capacidad para 20 personas."
    },
    "Sala de Juntas": {
        "img_path": "img/saladejuntasu.jpeg", 
        "descripcion": "Sala de reuniones pequeña, ideal para encuentros de equipo o sesiones de brainstorming."
    },
    "Sala de Juntas FCC": {
        "img_path": "img/fcc.jpeg", 
        "descripcion": "Espacio de reuniones flexible en el edificio FCC, Ubicada dentro de la facultad Piso 1 Torre B Calle 80 edificio DJC. Máximo 16 Personas."
    },
    "Sala de Juntas FCE": {
        "img_path": "img/fce.jpeg", 
        "descripcion": "Sala en el edificio FCE, Ubicada dentro de la facultad Piso 1 Torre C Calle 80 edificio DJC. Máximo 10 Personas."
    },
    "Sala de Juntas FING": {
        "img_path": "img/fing.jpeg", 
        "descripcion": "Espacio de reuniones en el edificio FING, Ubicada en Calle 81B No 73 Bis-65 Máximo 13 Personas."
    },
    "Sala de Juntas FEDU": {
        "img_path": "img/fedu.jpeg", 
        "descripcion": "Sala de reuniones en el edificio FEDU, Ubicada en DG 81c bis No 72c 46 Máximo 13 Personas."
    },
    "Sala de Juntas I+D": {
        "img_path": "img/i+d.jpeg", 
        "descripcion": "Ubicada en Calle 81bis # 72B-59 Edificio I+D Máximo 10 Personas"
    },
    "Sala de Juntas FCHS": {
        "img_path": "img/fchs.jpeg", 
        "descripcion": "Sala de reuniones en el edificio FCHS, Ubicado en Diag 81d # 72c 21 piso 2 Máximo 12 personas."
    },
    "Coworking 1": {
        "img_path": "img/coworking1.jpeg", 
        "descripcion": "Espacio de coworking abierto y flexible, ideal para trabajo colaborativo con capacidad maxima de 15 personas."
    },
    "Coworking 2": {
        "img_path": "img/c2.jpg", 
        "descripcion": "Área de coworking minimalista, perfecta para equipos de maximo 6 personas"
    },
}

bot.set_my_commands([
    BotCommand("start", "Iniciar el bot"),
    BotCommand("help", "Mostrar ayuda"),
    BotCommand("reservar", "Reservar un espacio"),
    BotCommand("cancelar", "Cancelar una reserva"),
    BotCommand("consultar", "Consultar detalles de una reserva"),
    # BotCommand("estadisticas", "Ver estadísticas (solo admin)")
])

# Comando /start
@bot.message_handler(commands=['start'])
def start(message: Message):
    bot.reply_to(message, "Hola! Soy Recon tu asistente para realizar solicitudes de reservas de los espacios en UNIMINUTO. Puedes realizar solicitudes de reservar salas, auditorios y plazoletas. Usa /reservar para empezar.")

# Comando /help
@bot.message_handler(commands=['help'])
def help(message: Message):
    bot.reply_to(message, "Comandos disponibles:\n/reservar - Para hacer una reserva\n/cancelar - Para cancelar una reserva\n/estadisticas - Para ver estadísticas (solo admin)")

# Comando /ver para ver imágenes 360°
@bot.message_handler(commands=['ver'])
def ver(message: Message):
    markup = InlineKeyboardMarkup()
    for espacio_tipo in espacios.keys():
        markup.add(InlineKeyboardButton(text=espacio_tipo, callback_data=f"tipo_{espacio_tipo}"))
    bot.send_message(message.chat.id, "Selecciona el tipo de espacio para ver las opciones disponibles:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('tipo_'))
def mostrar_opciones_espacio(call: CallbackQuery):
    espacio_tipo = call.data.split('_')[1]
    opciones = espacios.get(espacio_tipo, [])

    if opciones:
        markup = InlineKeyboardMarkup()
        for opcion in opciones:
            markup.add(InlineKeyboardButton(text=opcion, callback_data=f"opcion_{opcion}"))
        bot.send_message(call.message.chat.id, f"Seleccione un {espacio_tipo}:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "No hay opciones disponibles en esta categoría.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('opcion_'))
def mostrar_imagen_espacio(call: CallbackQuery):
    espacio_seleccionado = call.data.split('_')[1]
    user_data['espacio'] = espacio_seleccionado  # Guardar la selección de espacio en user_data

    espacio_info = imagenes_espacios.get(espacio_seleccionado, None)
    
    if espacio_info:
        image_path = espacio_info.get("img_path")
        descripcion = espacio_info.get("descripcion", "Descripción no disponible.")

        if image_path:
            # Mostrar la imagen del espacio con la descripción
            with open(image_path, 'rb') as img:
                bot.send_photo(call.message.chat.id, img, caption=f"{espacio_seleccionado}\n\n{descripcion}")

            # Mostrar botones de acción
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Reservar este Espacio", callback_data="reservar_espacio"))
            markup.add(InlineKeyboardButton("Seleccionar Otro Espacio", callback_data="cambiar_espacio"))
            bot.send_message(call.message.chat.id, "¿Qué te gustaría hacer a continuación?", reply_markup=markup)
        else:
            bot.reply_to(call.message, f"No se encontró la imagen para {espacio_seleccionado}. {descripcion}")
    else:
        bot.reply_to(call.message, "No se encontró la información para el espacio seleccionado.")

@bot.callback_query_handler(func=lambda call: call.data == 'reservar_espacio')
def continuar_con_reserva(call: CallbackQuery):
    msg = bot.send_message(call.message.chat.id, "Proporciona la fecha de la reserva (DD/MM/AAAA):")
    bot.register_next_step_handler(msg, fecha)  # Continuar con el proceso de reserva

@bot.callback_query_handler(func=lambda call: call.data == 'cambiar_espacio')
def cambiar_espacio(call: CallbackQuery):
    # Volver a mostrar la selección de categorías de espacios
    markup = InlineKeyboardMarkup()
    for espacio_tipo in espacios.keys():
        markup.add(InlineKeyboardButton(text=espacio_tipo, callback_data=f"tipo_{espacio_tipo}"))
    bot.send_message(call.message.chat.id, "Selecciona un tipo de espacio para ver las opciones disponibles:", reply_markup=markup)

# Proceso de reserva
user_data = {}

@bot.message_handler(commands=['reservar'])
def reservar(message: Message):
    msg = bot.reply_to(message, "Por favor, proporciona tu nombre:")
    bot.register_next_step_handler(msg, nombre)

def nombre(message: Message):
    user_data['nombre'] = message.text
    msg = bot.reply_to(message, "Proporciona el nombre del evento o reunión:")
    bot.register_next_step_handler(msg, nombre_evento)

def nombre_evento(message: Message):
    user_data['nombre_evento'] = message.text
    msg = bot.reply_to(message, "Proporciona tu correo electrónico:")
    bot.register_next_step_handler(msg, email)

def email(message: Message):
    email_text = message.text.strip().lower()
    
    if not email_text.endswith('@uniminuto.edu'):
        bot.reply_to(message, "Lo siento, solo se permiten correos uniminuto.edu. Cancelando solicitud...")
        return
    
    user_data['email'] = email_text
    
    markup = InlineKeyboardMarkup()
    for espacio_tipo in espacios.keys():
        markup.add(InlineKeyboardButton(espacio_tipo, callback_data=f"tipo_{espacio_tipo}"))
    bot.send_message(message.chat.id, "Selecciona el tipo de espacio a reservar:", reply_markup=markup)

def espacio(message: Message):
    user_data['espacio'] = message.text  # Corregido: usar message.text para obtener la respuesta del usuario
    msg = bot.reply_to(message, "Proporciona la fecha de la solicitud reserva (DD/MM/AAAA):")
    bot.register_next_step_handler(msg, fecha)

def fecha(message: Message):
    try:
        # Validar la fecha proporcionada
        fecha_reserva = datetime.strptime(message.text, "%d/%m/%Y").date()
        user_data['fecha'] = fecha_reserva
        msg = bot.reply_to(message, "Proporciona la hora de inicio de la solicitud de reserva en formato 24 horas (HH:MM):")
        bot.register_next_step_handler(msg, hora_inicio)
    except ValueError:
        # Si el formato de la fecha no es válido, solicitar nuevamente
        msg = bot.reply_to(message, "Formato de fecha inválido. Por favor, proporciona la fecha en el formato DD/MM/AAAA:")
        bot.register_next_step_handler(msg, fecha)

def hora_inicio(message: Message):
    try:
        # Validar el formato de la hora de inicio (24 horas)
        hora_inicio_reserva = datetime.strptime(message.text, "%H:%M").time()
        user_data['hora_inicio'] = hora_inicio_reserva
        msg = bot.reply_to(message, "Proporciona la hora de finalización de la reserva en formato 24 horas (HH:MM):")
        bot.register_next_step_handler(msg, hora_fin)
    except ValueError:
        # Si el formato de la hora no es válido, solicitar nuevamente
        msg = bot.reply_to(message, "Formato de hora inválido. Por favor, proporciona la hora de inicio en formato 24 horas (HH:MM):")
        bot.register_next_step_handler(msg, hora_inicio)

def hora_fin(message: Message):
    try:
        # Validar el formato de la hora de finalización (24 horas)
        hora_fin_reserva = datetime.strptime(message.text, "%H:%M").time()

        # Asegurarse de que la hora de finalización sea posterior a la de inicio
        if hora_fin_reserva <= user_data['hora_inicio']:
            raise ValueError("La hora de finalización debe ser posterior a la hora de inicio.")

        user_data['hora_fin'] = hora_fin_reserva
        msg = bot.reply_to(message, "¿Requiere algún montaje especial? (Si (Comenta tu montaje o arreglo)/ No)")
        bot.register_next_step_handler(msg, montaje)
    except ValueError:
        # Si el formato de la hora no es válido, o la hora de finalización no es posterior a la de inicio
        msg = bot.reply_to(message, "Formato de hora inválido o la hora de finalización no es posterior a la de inicio. Proporciona la hora de finalización en formato 24 horas (HH:MM):")
        bot.register_next_step_handler(msg, hora_fin)

def montaje(message: Message):
    user_data['montaje_especial'] = message.text
    msg = bot.reply_to(message, "Por último, proporciona tu departamento o dependencia:")
    bot.register_next_step_handler(msg, departamento)

def departamento(message: Message):
    user_data['departamento'] = message.text
    id_reserva = reservar_espacio(user_data)
    bot.reply_to(message, f"Solicitud de reserva confirmada! Tu ID de solicitud es {id_reserva}, este proceso no representa tener una reserva oficial, esta sujeto a disponibilidad y puede ser modificado o cancelado en cualquier momento.")

def reservar_espacio(datos):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reservas (nombre, nombre_evento, email, espacio, fecha, hora_inicio, hora_fin, montaje_especial, departamento, estado) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'activa')
    """, (datos['nombre'], datos['nombre_evento'], datos['email'], datos['espacio'], datos['fecha'], datos['hora_inicio'], datos['hora_fin'], datos['montaje_especial'], datos['departamento']))
    conn.commit()
    id_reserva = cursor.lastrowid
    datos['id_reserva'] = id_reserva

    # Actualizar la tabla de usuarios
    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (datos['email'],))
    usuario = cursor.fetchone()
    if usuario:
        cursor.execute("UPDATE usuarios SET reservas = reservas + 1 WHERE id = %s", (usuario[0],))
    else:
        cursor.execute("INSERT INTO usuarios (nombre, email, departamento, reservas, canceladas) VALUES (%s, %s, %s, 1, 0)",
                       (datos['nombre'], datos['email'], datos['departamento']))
    conn.commit()
    cursor.close()
    conn.close()
    return id_reserva

# Comando para cancelar
@bot.message_handler(commands=['cancelar'])
def cancelar(message: Message):
    bot.send_message(message.chat.id, "Por favor, proporciona el ID de la reserva que deseas cancelar:")
    bot.register_next_step_handler(message, procesar_cancelacion)

def procesar_cancelacion(message: Message):
    try:
        id_reserva = int(message.text.strip())
        if cancelar_reserva(id_reserva):
            bot.reply_to(message, f"La reserva con ID {id_reserva} ha sido cancelada exitosamente.")
        else:
            bot.reply_to(message, f"No se pudo cancelar la reserva con ID {id_reserva}. Por favor, verifica que el ID sea correcto y que la reserva esté activa.")
    except ValueError:
        bot.reply_to(message, "Por favor, proporciona un ID de reserva válido.")

def cancelar_reserva(id_reserva):
    conn = connect_db()
    cursor = conn.cursor()
    
    # Obtener la información de la reserva antes de actualizar el estado
    cursor.execute("SELECT email FROM reservas WHERE id = %s AND estado = 'activa'", (id_reserva,))
    reserva = cursor.fetchone()

    if reserva:
        email_usuario = reserva[0]

        # Actualizar el estado de la reserva a 'cancelada'
        cursor.execute("UPDATE reservas SET estado = 'cancelada' WHERE id = %s", (id_reserva,))
        filas_afectadas = cursor.rowcount

        if filas_afectadas > 0:
            # Incrementar el contador de canceladas en la tabla de usuarios
            cursor.execute("UPDATE usuarios SET canceladas = canceladas + 1 WHERE email = %s", (email_usuario,))
            conn.commit()

        cursor.close()
        conn.close()
        return filas_afectadas > 0
    
    cursor.close()
    conn.close()
    return False

# Comando para estadísticas
@bot.message_handler(commands=['estadisticas'])
def estadisticas(message: Message):
    if message.from_user.id !=  ADMIN_USER_ID:
        bot.reply_to(message, "No tienes permiso para acceder a esta información.")
        return

    conn = connect_db()
    cursor = conn.cursor()

    # Total de reservas activas
    cursor.execute("SELECT COUNT(*) FROM reservas WHERE estado = 'activa'")
    total_reservas_activas = cursor.fetchone()[0]

    # Total de reservas canceladas
    cursor.execute("SELECT COUNT(*) FROM reservas WHERE estado = 'cancelada'")
    total_reservas_canceladas = cursor.fetchone()[0]

    # Espacio más reservado
    cursor.execute("SELECT espacio, COUNT(*) as cantidad FROM reservas WHERE estado = 'activa' GROUP BY espacio ORDER BY cantidad DESC LIMIT 1")
    espacio_mas_reservado = cursor.fetchone()
    if espacio_mas_reservado:
        espacio_mas_reservado_text = f"{espacio_mas_reservado[0]} con {espacio_mas_reservado[1]} reservas activas"
    else:
        espacio_mas_reservado_text = "No hay reservas activas registradas."

    # Usuario con más reservas activas
    cursor.execute("SELECT nombre, email, COUNT(*) as cantidad FROM reservas WHERE estado = 'activa' GROUP BY email, nombre ORDER BY cantidad DESC LIMIT 1")
    usuario_mas_reservas_activas = cursor.fetchone()
    if usuario_mas_reservas_activas:
        usuario_mas_reservas_activas_text = f"{usuario_mas_reservas_activas[0]} ({usuario_mas_reservas_activas[1]} reservas activas)"
    else:
        usuario_mas_reservas_activas_text = "No hay reservas activas registradas."

    # Usuario con más reservas canceladas
    cursor.execute("SELECT nombre, email, canceladas FROM usuarios ORDER BY canceladas DESC LIMIT 1")
    usuario_mas_cancelaciones = cursor.fetchone()
    if usuario_mas_cancelaciones:
        usuario_mas_cancelaciones_text = f"{usuario_mas_cancelaciones[0]} con {usuario_mas_cancelaciones[2]} reservas canceladas"
    else:
        usuario_mas_cancelaciones_text = "No hay cancelaciones registradas."

    # Formatear el mensaje de estadísticas
    mensaje = (f"Estadísticas de Reservas:\n\n"
               f"Total de reservas activas: {total_reservas_activas}\n"
               f"Total de reservas canceladas: {total_reservas_canceladas}\n"
               f"Espacio más reservado: {espacio_mas_reservado_text}\n"
               f"Usuario con más reservas activas: {usuario_mas_reservas_activas_text}\n"
               f"Usuario con más reservas canceladas: {usuario_mas_cancelaciones_text}")

    bot.reply_to(message, mensaje)

    cursor.close()
    conn.close()

# Comando para consultar reserva
@bot.message_handler(commands=['consultar'])
def consultar(message: types.Message):
    msg = bot.reply_to(message, "Proporciona tu nombre o correo electrónico:")
    bot.register_next_step_handler(msg, recibir_datos)

def recibir_datos(message: types.Message):
    user_data['identificador'] = message.text
    msg = bot.reply_to(message, "Proporciona el ID de tu solicitud de reserva:")
    bot.register_next_step_handler(msg, id_reserva)

def id_reserva(message: types.Message):
    user_data['id_reserva'] = message.text
    consultar_reserva(user_data, message)

def consultar_reserva(datos, message):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nombre, espacio, fecha, hora_inicio, hora_fin, montaje_especial, departamento, espacio_asignado, estado FROM reservas WHERE id = %s AND (nombre = %s OR email = %s)",
        (datos['id_reserva'], datos['identificador'], datos['identificador'])
    )
    reserva = cursor.fetchone()
    if reserva:
        nombre, espacio, fecha, hora_inicio, hora_fin, montaje_especial, departamento, espacio_asignado, estado = reserva
        if estado == 'cancelada':
            reserva_msg = (
                f"Detalles de la solicitud de reserva (ID: {datos['id_reserva']}):\n"
                f"La reserva ha sido cancelada."
            )
        else:
            if not espacio_asignado or espacio_asignado.strip().lower() in ["none", "null"]:
                espacio_asignado = " La asignación de espacios se efectúa 24 horas después de la solicitud. Por favor, intenta realizar la consulta nuevamente más tarde "
            reserva_msg = (
                f"Detalles de la solicitud de reserva (ID: {datos['id_reserva']}):\n"
                f"Nombre del reservante: {nombre}\n"
                f"Espacio reservado: {espacio}\n"
                f"Fecha de reserva: {fecha.strftime('%d/%m/%Y')}\n"
                f"Hora de inicio: {hora_inicio}\n"
                f"Hora de fin: {hora_fin}\n"
                f"Montaje especial: {montaje_especial}\n"
                f"Departamento: {departamento}\n"
                f"Espacio asignado: *{espacio_asignado}*"
            )
        bot.reply_to(message, reserva_msg, parse_mode='Markdown')
    else:
        bot.reply_to(message, "No se encontró ninguna solicitud de reserva con la información proporcionada.")
    cursor.close()
    conn.close()

# Inicia el bot
bot.polling()
