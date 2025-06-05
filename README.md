# VTT para Juegos de Rol

Esta aplicación es un Virtual Tabletop (VTT) para jugar juegos de rol en red local. Permite cargar mapas, mover tokens, chatear y tirar dados virtuales.

## Instalación

1. Instala Python 3.8 o superior.
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Ejecuta `main.py` para iniciar como anfitrión (server) o jugador (cliente).

## Funcionalidades
- Cargar mapas (imágenes)
- Mover tokens
- Chat integrado
- Tiradas de dados
- Multiusuario en red local

## Archivos principales
- `main.py`: Lanzador de la app
- `server.py`: Lógica del servidor
- `client.py`: Lógica del cliente
- `vtt_ui.py`: Interfaz gráfica
