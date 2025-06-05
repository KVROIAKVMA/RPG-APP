import sys
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox
from vtt_ui import VTTWindow
from server import VTTServer
from client import VTTClient

if __name__ == "__main__":
    app = QApplication(sys.argv)
    name, ok = QInputDialog.getText(None, "Nombre de jugador", "Ingresa tu nombre o apodo:")
    if not ok or not name.strip():
        sys.exit(0)
    player_name = name.strip()
    mode, ok = QInputDialog.getItem(None, "Modo de juego", "¿Servidor o Cliente?", ["Servidor", "Cliente"], 0, False)
    if not ok:
        sys.exit(0)
    if mode == "Servidor":
        port, ok = QInputDialog.getInt(None, "Puerto", "Puerto para escuchar:", 12345, 1024, 65535)
        if not ok:
            sys.exit(0)
        server = VTTServer(port=port)
        server.start()
        network = server
        is_server = True
        host = "localhost"
    else:
        host, ok = QInputDialog.getText(None, "Conectar a", "IP del servidor:", text="127.0.0.1")
        if not ok:
            sys.exit(0)
        port, ok = QInputDialog.getInt(None, "Puerto", "Puerto del servidor:", 12345, 1024, 65535)
        if not ok:
            sys.exit(0)
        try:
            client = VTTClient(host=host, port=port)
            network = client
            is_server = False
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo conectar: {e}")
            sys.exit(1)
    def notify_voice_rx():
        if is_server:
            server = VTTServer()
            threading.Thread(target=server.start, daemon=True).start()
            network = None
        else:
            # La ventana se creará después para pasarle notify_voice_rx
            network = None
    if not is_server:
        network = VTTClient(host=host, port=port, notify_voice_rx=notify_voice_rx)
    window = VTTWindow(network=network, is_server=is_server, host=host, player_name=player_name)
    window.show()
    sys.exit(app.exec_())
