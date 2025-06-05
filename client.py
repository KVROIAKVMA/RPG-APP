import socket
import threading

import sounddevice as sd
import numpy as np
import json
import threading
import base64

class VTTClient:
    def __init__(self, host="127.0.0.1", port=12345, on_message=None, notify_voice_rx=None):
        self.host = host
        self.port = port
        self.on_message = on_message
        self.notify_voice_rx = notify_voice_rx
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        threading.Thread(target=self.receive, daemon=True).start()
        self.voice_stream = None
        self.is_speaking = False
        self.fs = 16000  # Frecuencia de muestreo
        self.blocksize = 1024
        self.volume = 1.0  # Volumen de reproducción (1.0 = 100%)

    def set_volume(self, vol):
        self.volume = vol

    def send(self, data):
        self.client_socket.sendall(data)

    def start_voice(self):
        if self.is_speaking:
            return
        self.is_speaking = True
        def callback(indata, frames, time, status):
            if self.is_speaking:
                # Codifica el bloque de audio como base64 y lo manda
                audio_bytes = indata.tobytes()
                header = json.dumps({"type": "audio"}).encode() + b"\n"
                self.send(header + audio_bytes)
        self.voice_stream = sd.InputStream(samplerate=self.fs, channels=1, blocksize=self.blocksize, dtype='int16', callback=callback)
        self.voice_stream.start()

    def stop_voice(self):
        self.is_speaking = False
        if self.voice_stream:
            self.voice_stream.stop()
            self.voice_stream.close()
            self.voice_stream = None

    def receive(self):
        buffer = b""
        while True:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                buffer += data
                while b"\n" in buffer:
                    header, buffer = buffer.split(b"\n", 1)
                    try:
                        header_json = json.loads(header.decode())
                        if header_json.get("type") == "audio":
                            # Espera a tener suficiente audio
                            if len(buffer) >= self.blocksize * 2:
                                audio_bytes = buffer[:self.blocksize*2]
                                buffer = buffer[self.blocksize*2:]
                                self.handle_audio_message(audio_bytes)
                        else:
                            # Mensaje normal
                            if self.on_message:
                                self.on_message(header + b"\n" + buffer)
                                buffer = b""
                    except Exception as e:
                        # Si no es JSON, lo ignora
                        pass
            except:
                break

    def handle_audio_message(self, audio_bytes):
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
        audio_np *= self.volume
        audio_np = np.clip(audio_np, -32768, 32767).astype(np.int16)
        sd.play(audio_np, samplerate=self.fs)
        if self.notify_voice_rx:
            try:
                self.notify_voice_rx()
            except Exception:
                pass

if __name__ == "__main__":
    def print_message(msg):
        print("Mensaje recibido:", msg)
    client = VTTClient(on_message=print_message)
    while True:
        msg = input("Enviar mensaje: ").encode()
        client.send(msg)
