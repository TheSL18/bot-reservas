import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Token del bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USER_ID = 592974024  # Reemplaza con tu ID de usuario

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

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
    "Auditorio B205-C202": {"img_path": "img/b205.jpeg", "descripcion": "Auditorio con capacidad para 125 personas, equipado con sistema de sonido, proyector y camara para reuniones en vivo."},
    "Auditorio Escalonado Grande": {"img_path": "img/escalonadogrande.jpg", "descripcion": "Auditorio con asientos escalonados para hasta 49 personas."},
    "Auditorio Escalonado Pequeño": {"img_path": "img/auditoriopequeño.jpg", "descripcion": "Auditorio con asientos escalonados para hasta 42 personas."},
    "Plazoleta Jesus y Maria": {"img_path": "img/plazoletajym.jpeg", "descripcion": "Plazoleta bajo techo ideal para eventos al aire libre y actividades recreativas."},
    "Plazoleta RGH": {"img_path": "img/plazoletargh.jpeg", "descripcion": "Área amplia en el campus RGH, perfecta para encuentros y actividades sociales."},
    "Plazoleta de la Cruz": {"img_path": "img/plazoletacruz.jpeg", "descripcion": "Espacio al aire libre con ambiente tranquilo, Ubicada entre torres A y B."},
    "Plazoleta Verde": {"img_path": "img/plazoletaverde.jpeg", "descripcion": "Plazoleta rodeada de vegetación, ideal para actividades al aire libre ubicada antes de los torniquetes de acceso a la universidad."},
    "Plazoleta R Piso 9": {"img_path": "img/plazoletar.jpeg", "descripcion": "Área de encuentro VIP en el piso 9 del edificio C, con vistas panorámicas del campus a cielo abierto No se permite el ingreso a estudiantes."},
    "Hall Torre B-C": {"img_path": "img/hall.jpeg", "descripcion": "Espacio principal en el corazon de las Torres B y C, ideal para exposiciones y recepciones con capacidad maxima de 30 personas."},
    "Sala de Juntas RGH": {"img_path": "img/rgh.jpeg", "descripcion": "Sala de reuniones equipada con tecnología de video conferencia y capacidad para 20 personas."},
    "Sala de Juntas": {"img_path": "img/saladejuntasu.jpeg", "descripcion": "Sala de reuniones pequeña, ideal para encuentros de equipo o sesiones de brainstorming."},
    "Sala de Juntas FCC": {"img_path": "img/fcc.jpeg", "descripcion": "Espacio de reuniones flexible en el edificio FCC, Ubicada dentro de la facultad Piso 1 Torre B Calle 80 edificio DJC. Máximo 16 Personas."},
    "Sala de Juntas FCE": {"img_path": "img/fce.jpeg", "descripcion": "Sala en el edificio FCE, Ubicada dentro de la facultad Piso 1 Torre C Calle 80 edificio DJC. Máximo 10 Personas."},
    "Sala de Juntas FING": {"img_path": "img/fing.jpeg", "descripcion": "Espacio de reuniones en el edificio FING, Ubicada en Calle 81B No 73 Bis-65 Máximo 13 Personas."},
    "Sala de Juntas FEDU": {"img_path": "img/fedu.jpeg", "descripcion": "Sala de reuniones en el edificio FEDU, Ubicada en DG 81c bis No 72c 46 Máximo 13 Personas."},
    "Sala de Juntas I+D": {"img_path": "img/i+d.jpeg", "descripcion": "Ubicada en Calle 81bis # 72B-59 Edificio I+D Máximo 10 Personas"},
    "Sala de Juntas FCHS": {"img_path": "img/fchs.jpeg", "descripcion": "Sala de reuniones en el edificio FCHS, Ubicado en Diag 81d # 72c 21 piso 2 Máximo 12 personas."},
    "Coworking 1": {"img_path": "img/coworking1.jpeg", "descripcion": "Espacio de coworking abierto y flexible, ideal para trabajo colaborativo con capacidad maxima de 15 personas."},
    "Coworking 2": {"img_path": "img/c2.jpg", "descripcion": "Área de coworking minimalista, perfecta para equipos de maximo 6 personas"},
}

async def set_bot_commands():
    commands = [
        BotCommand(command="/start", description="Iniciar el bot"),
        BotCommand(command="/help", description="Mostrar ayuda"),
        BotCommand(command="/reservar", description="Reservar un espacio"),
        BotCommand(command="/cancelar", description="Cancelar una reserva"),
        BotCommand(command="/consultar", description="Consultar detalles de una reserva"),
        BotCommand(command="/estadisticas", description="Ver estadísticas (solo admin)")
    ]
    await bot.set_my_commands(commands)

# Comando /start
@dp.message_handler(Command(commands=['start']))
async def start(message: types.Message):
    await message.reply("Hola! Soy Recon tu asistente para realizar solicitudes de reservas de los espacios en UNIMINUTO. Puedes realizar solicitudes de reservar salas, auditorios y plazoletas. Usa /reservar para empezar.")

# Comando /help
@dp.message_handler(Command(commands=['help']))
async def help(message: types.Message):
    await message.reply("Comandos disponibles:\n/reservar - Para hacer una reserva\n/cancelar - Para cancelar una reserva\n/estadisticas - Para ver estadísticas (solo admin)")

# Comando /ver para ver imágenes 360°
@dp.message_handler(Command(commands=['ver']))
async def ver(message: types.Message):
    markup = InlineKeyboardMarkup()
    for espacio_tipo in espacios.keys():
        markup.add(InlineKeyboardButton(text=espacio_tipo, callback_data=f"tipo_{espacio_tipo}"))
    await message.reply("Selecciona el tipo de espacio para ver las opciones disponibles:", reply_markup=markup)

@dp.callback_query_handler(Text(startswith='tipo_'))
async def mostrar_opciones_espacio(call: types.CallbackQuery, state: FSMContext):
    espacio_tipo = call.data.split('_')[1]
    opciones = espacios.get(espacio_tipo, [])

    if opciones:
        markup = InlineKeyboardMarkup()
        for opcion in opciones:
            markup.add(InlineKeyboardButton(text=opcion, callback_data=f"opcion_{opcion}"))
        await call.message.reply(f"Seleccione un {espacio_tipo}:", reply_markup=markup)
    else:
        await call.message.reply("No hay opciones disponibles en esta categoría.")

@dp.callback_query_handler(Text(startswith='opcion_'))
async def mostrar_imagen_espacio(call: types.CallbackQuery, state: FSMContext):
    espacio_seleccionado = call.data.split('_')[1]
    await state.update_data(espacio=espacio_seleccionado)  # Guardar la selección de espacio en el estado

    espacio_info = imagenes_espacios.get(espacio_seleccionado, None)

    if espacio_info:
        image_path = espacio_info.get("img_path")
        descripcion = espacio_info.get("descripcion", "Descripción no disponible")

        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                await call.message.reply_photo(photo, caption=descripcion)
            # Mostrar botones de reserva o cancelación
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("Reservar", callback_data="reservar_espacio"),
                InlineKeyboardButton("Cancelar", callback_data="cancelar_reserva"))
            await call.message.reply("Selecciona una acción:", reply_markup=markup)
        else:
            await call.message.reply("No se encontró la imagen del espacio seleccionado.")
    else:
        await call.message.reply("No se encontró información sobre el espacio seleccionado.")

# Comando /reservar
@dp.message_handler(Command(commands=['reservar']))
async def reservar(message: types.Message):
    markup = InlineKeyboardMarkup()
    for espacio_tipo in espacios.keys():
        markup.add(InlineKeyboardButton(text=espacio_tipo, callback_data=f"tipo_{espacio_tipo}"))
    await message.reply("Selecciona el tipo de espacio que deseas reservar:", reply_markup=markup)

# Cancelar reserva
@dp.callback_query_handler(Text(equals="cancelar_reserva"))
async def cancelar_reserva(call: types.CallbackQuery):
    await call.message.reply("Has cancelado la reserva.")

# Reservar espacio
@dp.callback_query_handler(Text(equals="reservar_espacio"))
async def realizar_reserva(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    espacio_seleccionado = data.get('espacio')  # Recuperar la selección de espacio guardada en user_data

    if espacio_seleccionado:
        # Conectarse a la base de datos y guardar la reserva
        db = connect_db()
        cursor = db.cursor()
        user_id = call.from_user.id
        query = "INSERT INTO reservas (user_id, espacio, fecha_reserva) VALUES (%s, %s, %s)"
        values = (user_id, espacio_seleccionado, datetime.now())
        cursor.execute(query, values)
        db.commit()
        cursor.close()
        db.close()

        await call.message.reply(f"Has reservado {espacio_seleccionado} exitosamente.")
    else:
        await call.message.reply("No se encontró la información del espacio para realizar la reserva.")

# Comando /cancelar
@dp.message_handler(Command(commands=['cancelar']))
async def cancelar(message: types.Message):
    user_id = message.from_user.id

    # Conectarse a la base de datos y eliminar la reserva
    db = connect_db()
    cursor = db.cursor()
    query = "DELETE FROM reservas WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    db.commit()
    cursor.close()
    db.close()

    await message.reply("Tu reserva ha sido cancelada.")

# Comando /consultar
@dp.message_handler(Command(commands=['consultar']))
async def consultar(message: types.Message):
    user_id = message.from_user.id

    # Conectarse a la base de datos y consultar la reserva
    db = connect_db()
    cursor = db.cursor()
    query = "SELECT espacio, fecha_reserva FROM reservas WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    reserva = cursor.fetchone()
    cursor.close()
    db.close()

    if reserva:
        espacio, fecha_reserva = reserva
        await message.reply(f"Tienes reservada el {espacio} en la fecha {fecha_reserva}.")
    else:
        await message.reply("No tienes ninguna reserva activa.")

# Comando /estadisticas (solo admin)
@dp.message_handler(Command(commands=['estadisticas']))
async def estadisticas(message: types.Message):
    if message.from_user.id == ADMIN_USER_ID:
        # Conectarse a la base de datos y consultar las estadísticas
        db = connect_db()
        cursor = db.cursor()
        query = "SELECT espacio, COUNT(*) FROM reservas GROUP BY espacio"
        cursor.execute(query)
        estadisticas = cursor.fetchall()
        cursor.close()
        db.close()

        if estadisticas:
            respuesta = "Estadísticas de reservas:\n\n"
            for espacio, count in estadisticas:
                respuesta += f"{espacio}: {count} reservas\n"
            await message.reply(respuesta)
        else:
            await message.reply("No hay estadísticas disponibles.")
    else:
        await message.reply("No tienes permiso para ver las estadísticas.")

async def main():
    await set_bot_commands()
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

