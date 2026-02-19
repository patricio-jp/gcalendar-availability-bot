# Google Calendar Availability Bot 📅🤖

Este bot monitorea automáticamente una página pública de reserva de citas de Google Calendar y te notifica vía Telegram cuando detecta nuevos horarios disponibles.

## ✨ Características

- **Monitoreo Automático**: Revisa la página cada X minutos (intervalo aleatorio configurable).
- **Detección Inteligente**: Identifica fechas y horarios disponibles usando Selenium.
- **Notificaciones Instantáneas**: Envía un mensaje a tu Telegram con la lista detallada de citas disponibles (Fecha y Hora) y el enlace directo para reservar.
- **Anti-Bot**: Utiliza intervalos de espera aleatorios y un User-Agent real para simular comportamiento humano y evitar bloqueos.
- **Silencioso**: Si no hay citas nuevas, no envía mensajes molestos.

## 🛠️ Requisitos

- **Python 3.8+**
- **Google Chrome** instalado (el bot usa ChromeDriver automáticamente).
- Una cuenta de **Telegram** (para recibir alertas).

## 🚀 Instalación y Configuración Local

1.  **Clonar el repositorio**:

    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd gcalendar-availability-bot
    ```

2.  **Crear entorno virtual (Recomendado)**:

    ```bash
    python -m venv .venv
    # En Windows:
    .venv\Scripts\activate
    # En Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Instalar dependencias**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar Variables de Entorno**:
    - Copia el archivo de ejemplo (si no existe, crea uno llamado `.env`):
    - Edita `.env` con tus datos:

    ```env
    # URL pública de la página de citas de Google
    CALENDAR_URL="https://calendar.google.com/calendar/u/0/appointments/..."

    # Credenciales de Telegram
    # 1. Crea un bot con @BotFather para obtener el TOKEN
    # 2. Obtén tu ID numérico con @userinfobot
    TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
    TELEGRAM_CHAT_ID="12345678"

    # Intervalo de revisión en minutos (Mínimo y Máximo para aleatoriedad)
    CHECK_INTERVAL_MIN=5
    CHECK_INTERVAL_MAX=15
    ```

5.  **Ejecutar el Bot**:
    ```bash
    python main.py
    ```

## ☁️ Despliegue en Servidor (Oracle Cloud / VM Ubuntu)

Para mantener el bot corriendo 24/7 en una máquina virtual:

### Opción A: Usando `screen` (Más simple)

1.  Instala screen: `sudo apt install screen`
2.  Crea una sesión: `screen -S gcalbot`
3.  Activa el entorno y corre el bot:
    ```bash
    source .venv/bin/activate
    python main.py
    ```
4.  Desconéctate de la sesión manteniendo el bot corriendo: `Ctrl+A` seguido de `D`.
5.  Para volver a ver el log: `screen -r gcalbot`.

### Opción B: Usando `systemd` (Recomendado para producción)

Crea un servicio para que el bot arranque automáticamente si se reinicia el servidor.

1.  Crea el archivo de servicio:
    ```bash
    sudo nano /etc/systemd/system/gcalbot.service
    ```
2.  Pega el siguiente contenido (ajusta las rutas):

    ```ini
    [Unit]
    Description=Google Calendar Bot
    After=network.target

    [Service]
    User=ubuntu
    WorkingDirectory=/home/ubuntu/gcalendar-availability-bot
    ExecStart=/home/ubuntu/gcalendar-availability-bot/.venv/bin/python main.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

3.  Activa y arranca el servicio:
    ```bash
    sudo systemctl enable gcalbot
    sudo systemctl start gcalbot
    ```

> [!NOTE]
> En servidores Linux sin interfaz gráfica (headless), asegúrate de tener instalado Chrome o Chromium:
> `sudo apt install chromium-browser`

### Opción C: Usando Docker (🐳 Recomendado)

Docker es ideal porque empaqueta todo (incluyendo Chrome y sus dependencias) en un contenedor aislado, evitando problemas de configuración en tu VM.

1.  **Instalar Docker** en tu VM (si no lo tienes):

    ```bash
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    ```

2.  **Construir la imagen**:

    ```bash
    # Ejecuta esto dentro de la carpeta del proyecto
    docker build -t gcal-bot .
    ```

3.  **Correr el contenedor en segundo plano**:

    ```bash
    # Asegúrate de tener tu archivo .env listo
    docker run -d --name mi-bot --env-file .env --restart unless-stopped --shm-size=2g gcal-bot
    ```

4.  **Ver logs**:

    ```bash
    docker logs -f mi-bot
    ```

5.  **Detener**:
    ```bash
    docker stop mi-bot
    ```
