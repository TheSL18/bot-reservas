# Documentación del Bot de Reservas para UNIMINUTO

## Descripción

Este bot de Telegram automatiza el proceso de reserva de espacios dentro de UNIMINUTO, permitiendo a los usuarios reservar auditorios, plazoletas y salas de juntas. Los administradores pueden gestionar las reservas y ver estadísticas. El bot está construido en Python utilizando la biblioteca `pyTelegramBotAPI` y se conecta a una base de datos MariaDB para almacenar y recuperar datos de las reservas.

## Requisitos

- Python 3.x
- Biblioteca `pyTelegramBotAPI`
- Base de datos MariaDB
- Archivo `.env` con las credenciales del bot y de la base de datos

## Configuración

El bot utiliza variables de entorno para configurar el acceso a la base de datos y al token del bot de Telegram. Asegúrate de tener un archivo `.env` con el siguiente formato:

```bash
BOT_TOKEN=your_telegram_bot_token
DB_HOST=your_database_host
DB_USER=your_database_user
DB_PASSWD=your_database_password
DB_DB=your_database_name
```

## Comandos Disponibles

### `/start`
Este comando inicia la interacción con el bot y proporciona un mensaje de bienvenida, explicando las funciones básicas del bot.

### `/help`
Muestra los comandos disponibles y cómo utilizarlos.

### `/reservar`
Inicia el proceso de reserva de un espacio. El bot guía al usuario a través de los siguientes pasos:
1. Solicita el nombre del usuario.
2. Solicita el nombre del evento o reunión.
3. Solicita el correo electrónico (debe ser un correo institucional `@uniminuto.edu`).
4. Solicita la fecha de la reserva (DD/MM/AAAA).
5. Solicita la hora de inicio y fin de la reserva (formato 24 horas HH:MM).
6. Solicita información sobre montaje especial (si es necesario).
7. Solicita el departamento responsable.

### `/cancelar`
Permite al usuario cancelar una reserva existente.

### `/consultar`
Permite al usuario consultar los detalles de una reserva.

### `/ver`
Muestra una lista de categorías de espacios (auditorios, plazoletas, salas de juntas). Al seleccionar una categoría, el bot muestra las opciones disponibles y sus respectivas imágenes junto con una descripción detallada.

## Estructura de los Espacios

El bot tiene una estructura predefinida de categorías de espacios:

- **Auditorios**: 
  - Auditorio B205-C202
  - Auditorio Escalonado Grande
  - Auditorio Escalonado Pequeño
- **Plazoletas**: 
  - Plazoleta Jesus y Maria
  - Plazoleta RGH
  - Plazoleta de la Cruz
  - Plazoleta Verde
  - Plazoleta R Piso 9
  - Hall Torre B-C
- **Salas de Juntas**: 
  - Sala de Juntas
  - Sala de Juntas RGH
  - Sala de Juntas FCC
  - Sala de Juntas FCE
  - Sala de Juntas FING
  - Sala de Juntas FEDU
  - Sala de Juntas I+D
  - Sala de Juntas FCHS
  - Coworking 1
  - Coworking 2

## Proceso de Reserva

1. El usuario inicia una reserva usando `/reservar`.
2. El bot solicita la información necesaria (nombre, evento, fecha, hora, etc.).
3. Después de ingresar la información, el bot verifica la disponibilidad del espacio y confirma la reserva.

## Base de Datos

El bot se conecta a una base de datos MariaDB. Asegúrate de que los detalles de la conexión estén correctamente configurados en el archivo `.env`.

### Estructura de la Tabla `reservas`

```sql
CREATE TABLE reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255),
    nombre_evento VARCHAR(255),
    email VARCHAR(255),
    espacio VARCHAR(255),
    fecha DATE,
    hora_inicio TIME,
    hora_fin TIME,
    montaje_especial TEXT,
    departamento VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Instalación

1. Clona el repositorio del bot.
2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configura las variables de entorno en un archivo `.env` siguiendo el formato proporcionado.
4. Ejecuta el bot:
   ```bash
   python bot.py
   ```

## Funciones Administrativas

### Ver Estadísticas (solo admin)

El comando `/estadisticas` (solo disponible para el administrador) muestra estadísticas de uso del bot, como el número de reservas por espacio.

## Notas

- Asegúrate de que las imágenes de los espacios están correctamente ubicadas en la carpeta `img/`.
- El bot está configurado para funcionar solo con correos institucionales de UNIMINUTO (`@uniminuto.edu`).

## Mejoras Futuras

- Integración con Microsoft Calendar para sincronizar las reservas.
- Funcionalidad de notificaciones para recordar al usuario sobre sus reservas.
- Estadísticas más avanzadas para el administrador.
