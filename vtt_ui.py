from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QApplication, QLabel
from PyQt5.QtCore import Qt
import sys

class VTTWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VTT - Virtual Tabletop")
        self.setGeometry(100, 100, 1100, 750)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.central_widget.setLayout(layout)

        # Tabs vacíos
        self.add_tab("Mapa")
        self.add_tab("Chat")
        
        
        
        self.add_tab("Fichas")
        self.add_tab("Iniciativa")
        self.add_tab("Plantillas")
        self.add_tab("Notas")
        self.add_tab("Macros")
        self.add_tab("Historial")
        self.add_tab("Agenda")
        self.add_tab("Audio")
        self.add_tab("Voz")

    def add_tab(self, nombre):
        from PyQt5.QtWidgets import QVBoxLayout
        tab = QWidget()
        tab_layout = QVBoxLayout()
        # --- Sistema de campaña: botones globales ---
        if not hasattr(self, '_campaign_buttons_added'):
            from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QMenuBar, QAction
            import json, base64, io
            from PyQt5.QtGui import QImage
            from PyQt5.QtCore import QByteArray
            btn_save_campaign = QPushButton("Guardar campaña")
            btn_load_campaign = QPushButton("Cargar campaña")
            # --- Modo DM/Jugador ---
            self._modo_dm = True  # Por defecto DM
            if not hasattr(self, '_menubar_added'):
                menubar = QMenuBar(self)
                modo_menu = menubar.addMenu("Modo")
                act_dm = QAction("DM", self, checkable=True)
                act_jugador = QAction("Jugador", self, checkable=True)
                act_dm.setChecked(True)
                modo_menu.addAction(act_dm)
                modo_menu.addAction(act_jugador)
                def set_dm():
                    self._modo_dm = True
                    act_dm.setChecked(True)
                    act_jugador.setChecked(False)
                    if hasattr(self, 'update_notes_ui'):
                        self.update_notes_ui()
                def set_jugador():
                    self._modo_dm = False
                    act_dm.setChecked(False)
                    act_jugador.setChecked(True)
                    if hasattr(self, 'update_notes_ui'):
                        self.update_notes_ui()
                act_dm.triggered.connect(set_dm)
                act_jugador.triggered.connect(set_jugador)
                if hasattr(self, 'setMenuBar'):
                    self.setMenuBar(menubar)
                else:
                    self.central_widget.layout().insertWidget(0, menubar)
                self._menubar_added = True
            def save_campaign():
                import datetime, os
                data = {}
                # Mapas y tokens
                if hasattr(self, 'map_scenes'):
                    mapdata = []
                    for scene in self.map_scenes:
                        # Niebla en base64
                        fog_bytes = QByteArray()
                        scene.fog.save(fog_bytes, 'PNG')
                        fog_b64 = base64.b64encode(fog_bytes.data()).decode('utf-8')
                        # Imagen de mapa incrustada
                        map_img_b64 = None
                        if os.path.exists(scene.image_path):
                            with open(scene.image_path, 'rb') as fimg:
                                map_img_b64 = base64.b64encode(fimg.read()).decode('utf-8')
                        tokens = []
                        for t in scene.tokens:
                            # Token img incrustada
                            token_img_b64 = None
                            img_path = getattr(t.pixmap, '_img_path', None)
                            if img_path and os.path.exists(img_path):
                                with open(img_path, 'rb') as ftok:
                                    token_img_b64 = base64.b64encode(ftok.read()).decode('utf-8')
                            tokens.append({
                                'x': t.pos.x(),
                                'y': t.pos.y(),
                                'estados': list(t.states),
                                'img': img_path or None,
                                'img_b64': token_img_b64
                            })
                        mapdata.append({
                            'name': scene.name,
                            'image_path': scene.image_path,
                            'image_b64': map_img_b64,
                            'fog': fog_b64,
                            'tokens': tokens,
                            'notes': [n if isinstance(n, dict) else {'texto': n, 'privada': False} for n in getattr(scene, 'notes', [])]
                        })
                    data['mapas'] = mapdata
                # Estados personalizados
                if hasattr(self.map_widget, '_custom_states'):
                    data['estados_personalizados'] = {k: v.name() for k,v in self.map_widget._custom_states.items()}
                # Fichas
                if hasattr(self, 'char_name'):
                    data['ficha'] = {
                        'nombre': self.char_name.text(),
                        'clase': self.char_class.text(),
                        'nivel': self.char_level.text()
                    }
                # Notas
                if hasattr(self, 'notas_list'):
                    data['notas'] = [self.notas_list.item(i).text() for i in range(self.notas_list.count())]
                # Chat
                if hasattr(self, 'chat_list'):
                    data['chat'] = [self.chat_list.item(i).text() for i in range(self.chat_list.count())]
                # Iniciativa
                if hasattr(self, 'init_list'):
                    data['iniciativa'] = [self.init_list.item(i).text() for i in range(self.init_list.count())]
                # Plantillas
                if hasattr(self, 'template_list'):
                    data['plantillas'] = [self.template_list.item(i).text() for i in range(self.template_list.count())]
                path, _ = QFileDialog.getSaveFileName(self, "Guardar campaña", "", "Campaña (*.json)")
                if path:
                    # Backup automático
                    if os.path.exists(path):
                        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        backup_path = f"{os.path.splitext(path)[0]}_backup_{now}.json"
                        import shutil
                        shutil.copy2(path, backup_path)
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    QMessageBox.information(self, "Campaña guardada", f"Campaña guardada en {path}")
                # Estados personalizados
                if hasattr(self.map_widget, '_custom_states'):
                    data['estados_personalizados'] = {k: v.name() for k,v in self.map_widget._custom_states.items()}
                # Fichas
                if hasattr(self, 'char_name'):
                    data['ficha'] = {
                        'nombre': self.char_name.text(),
                        'clase': self.char_class.text(),
                        'nivel': self.char_level.text()
                    }
                # Notas
                if hasattr(self, 'notas_list'):
                    data['notas'] = [self.notas_list.item(i).text() for i in range(self.notas_list.count())]
                # Chat
                if hasattr(self, 'chat_list'):
                    data['chat'] = [self.chat_list.item(i).text() for i in range(self.chat_list.count())]
                # Iniciativa
                if hasattr(self, 'init_list'):
                    data['iniciativa'] = [self.init_list.item(i).text() for i in range(self.init_list.count())]
                # Plantillas
                if hasattr(self, 'template_list'):
                    data['plantillas'] = [self.template_list.item(i).text() for i in range(self.template_list.count())]
                path, _ = QFileDialog.getSaveFileName(self, "Guardar campaña", "", "Campaña (*.json)")
                if path:
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    QMessageBox.information(self, "Campaña guardada", f"Campaña guardada en {path}")
            def load_campaign():
                path, _ = QFileDialog.getOpenFileName(self, "Cargar campaña", "", "Campaña (*.json)")
                if not path:
                    return
                import os
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Mapas
                if 'mapas' in data:
                    self.map_scenes.clear()
                    self.map_widget.set_scene(None)
                    map_selector = None
                    for w in self.findChildren(QComboBox):
                        if w.count()>0 and w.itemText(0).endswith(('.png','.jpg','.jpeg','.bmp')):
                            map_selector = w
                            break
                    if map_selector:
                        map_selector.clear()
                    for m in data['mapas']:
                        import tempfile
                        map_img_path = m['image_path']
                        use_temp = False
                        if not os.path.exists(map_img_path) and m.get('image_b64'):
                            # Crear archivo temporal desde base64
                            img_bytes = base64.b64decode(m['image_b64'])
                            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(map_img_path)[-1])
                            tmp.write(img_bytes)
                            tmp.close()
                            map_img_path = tmp.name
                            use_temp = True
                        if not os.path.exists(map_img_path):
                            QMessageBox.warning(self, "Imagen faltante", f"No se encontró la imagen {m['image_path']} para el mapa {m['name']}")
                            continue
                        scene = type(self.map_scenes[0] if self.map_scenes else self.map_widget.scene)(m['name'], map_img_path)
                        # Niebla
                        fog_bytes = base64.b64decode(m['fog'])
                        img = QImage()
                        img.loadFromData(fog_bytes, 'PNG')
                        scene.fog = QPixmap.fromImage(img)
                        # Tokens
                        scene.tokens.clear()
                        for t in m['tokens']:
                            token_img_path = t['img']
                            if token_img_path and os.path.exists(token_img_path):
                                pix = QPixmap(token_img_path)
                                pix = pix.scaled(64,64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                pix._img_path = token_img_path
                            elif t.get('img_b64'):
                                img_bytes = base64.b64decode(t['img_b64'])
                                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                                tmp.write(img_bytes)
                                tmp.close()
                                pix = QPixmap(tmp.name)
                                pix = pix.scaled(64,64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                pix._img_path = None
                            else:
                                pix = QPixmap(64,64)
                                pix.fill(Qt.red)
                                pix._img_path = None
                            token = type(scene.tokens[0] if scene.tokens else Token)(pix, QPoint(t['x'], t['y']))
                            token.states = set(t.get('estados',[]))
                            scene.tokens.append(token)
                        # Notas
                        scene.notes = m.get('notes',[])
                        # Compatibilidad retro: si alguna nota es str, convertir a dict
                        for i, n in enumerate(scene.notes):
                            if isinstance(n, str):
                                scene.notes[i] = {'texto': n, 'privada': False}
                        self.map_scenes.append(scene)
                        if map_selector:
                            map_selector.addItem(m['name'])
                    if self.map_scenes:
                        self.map_widget.set_scene(self.map_scenes[0])
                        if map_selector:
                            map_selector.setCurrentIndex(0)
                # Estados personalizados
                if 'estados_personalizados' in data and hasattr(self.map_widget, '_custom_states'):
                    from PyQt5.QtGui import QColor
                    self.map_widget._custom_states.clear()
                    for k,v in data['estados_personalizados'].items():
                        self.map_widget._custom_states[k] = QColor(v)
                # Fichas
                if 'ficha' in data and hasattr(self, 'char_name'):
                    self.char_name.setText(data['ficha'].get('nombre',''))
                    self.char_class.setText(data['ficha'].get('clase',''))
                    self.char_level.setText(data['ficha'].get('nivel',''))
                # Notas
                if 'notas' in data and hasattr(self, 'notas_list'):
                    self.notas_list.clear()
                    for n in data['notas']:
                        self.notas_list.addItem(n)
                # Chat
                if 'chat' in data and hasattr(self, 'chat_list'):
                    self.chat_list.clear()
                    for c in data['chat']:
                        self.chat_list.addItem(c)
                # Iniciativa
                if 'iniciativa' in data and hasattr(self, 'init_list'):
                    self.init_list.clear()
                    ini_data = data['iniciativa']
                    if isinstance(ini_data, dict):
                        lista = ini_data.get('lista', [])
                        turno = ini_data.get('turno', 0)
                    else:
                        lista = ini_data
                        turno = 0
                    for i in lista:
                        self.init_list.addItem(i)
                    self._initiative_turn = turno
                    # Refresca el UI si la función existe
                    if hasattr(self, 'init_list') and hasattr(self, '_initiative_turn'):
                        def refresh_initiative():
                            for i in range(self.init_list.count()):
                                item = self.init_list.item(i)
                                txt = item.text()
                                if txt.startswith("▶ "):
                                    txt = txt[2:]
                                item.setText(txt)
                            if self.init_list.count():
                                idx = self._initiative_turn % self.init_list.count()
                                item = self.init_list.item(idx)
                                item.setText("▶ " + item.text())
                                self.init_list.setCurrentRow(idx)
                        refresh_initiative()
                # Agenda
                if 'agenda' in data and hasattr(self, 'events_by_date'):
                    self.events_by_date = data['agenda']
                    if hasattr(self, 'calendar') and hasattr(self, 'event_list'):
                        def refresh_events():
                            date = self.calendar.selectedDate().toString("yyyy-MM-dd")
                            self.event_list.clear()
                            for ev in self.events_by_date.get(date, []):
                                self.event_list.addItem(ev)
                        refresh_events()
                if 'agenda_audio' in data and hasattr(self, 'event_audio_by_date'):
                    self.event_audio_by_date = data['agenda_audio']
                # Voz/Discord
                if 'discord_url' in data:
                    self._discord_url_cache = data['discord_url']
                # Plantillas
                if 'plantillas' in data and hasattr(self, 'template_list'):
                    self.template_list.clear()
                    for t in data['plantillas']:
                        self.template_list.addItem(t)
                QMessageBox.information(self, "Campaña cargada", f"Campaña cargada de {path}")

            if not hasattr(self, '_campaign_bar'):
                self._campaign_bar = QHBoxLayout()
                self._campaign_bar.addWidget(btn_save_campaign)
                self._campaign_bar.addWidget(btn_load_campaign)
                if hasattr(self, 'central_widget'):
                    self.central_widget.layout().insertLayout(0, self._campaign_bar)
                else:
                    tab_layout.addLayout(self._campaign_bar)
            btn_save_campaign.clicked.connect(save_campaign)
            btn_load_campaign.clicked.connect(load_campaign)
            self._campaign_buttons_added = True
        if nombre == "Mapa":
            from PyQt5.QtWidgets import QPushButton, QFileDialog, QHBoxLayout, QMessageBox, QSlider, QLabel, QComboBox, QListWidget, QLineEdit
            from PyQt5.QtGui import QPixmap, QPainter, QColor
            from PyQt5.QtCore import Qt, QPoint, QRect
            import os

            class Token:
                def __init__(self, pixmap, pos):
                    self.pixmap = pixmap
                    self.pos = pos
                    self.selected = False
                    self.states = set()  # Estados activos
                def rect(self):
                    return QRect(self.pos, self.pixmap.size())

            class MapScene:
                def __init__(self, name, image_path):
                    self.name = name
                    self.image_path = image_path
                    self.map_image = QPixmap(image_path)
                    self.fog = QPixmap(self.map_image.size())
                    self.fog.fill(QColor(0,0,0,220))
                    self.tokens = []
                def clear_fog(self):
                    self.fog = QPixmap(self.map_image.size())
                    self.fog.fill(QColor(0,0,0,220))
                def add_token(self, pixmap):
                    pix = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    x = (self.map_image.width() - pix.width()) // 2
                    y = (self.map_image.height() - pix.height()) // 2
                    self.tokens.append(Token(pix, QPoint(x, y)))

            class MapWidget(QWidget):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.setMinimumSize(600, 400)
                    self.scene = None
                    self.drawing = False
                    self.brush_radius = 40
                    self.last_pos = None
                    self.drag_token = None
                    self.drag_offset = QPoint(0,0)
                def set_scene(self, scene):
                    self.scene = scene
                    self.update()
                def paintEvent(self, event):
                    painter = QPainter(self)
                    if self.scene and self.scene.map_image:
                        scaled_map = self.scene.map_image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        painter.drawPixmap(0,0, scaled_map)
                        # Dibujar tokens
                        if self.scene.tokens:
                            sx = scaled_map.width() / self.scene.map_image.width()
                            sy = scaled_map.height() / self.scene.map_image.height()
                            for tok in self.scene.tokens:
                                tx = int(tok.pos.x() * sx)
                                ty = int(tok.pos.y() * sy)
                                tw = int(tok.pixmap.width() * sx)
                                th = int(tok.pixmap.height() * sy)
                                painter.drawPixmap(tx, ty, tw, th, tok.pixmap)
                                # Estados visuales
                                estado_colores = {
                                    'Envenenado': QColor(0,200,0),
                                    'Caído': QColor(200,0,0),
                                    'Inspirado': QColor(0,100,255),
                                    'Marcado': QColor(220,220,0),
                                    'Muerto': QColor(20,20,20),
                                    'Aturdido': QColor(160,32,240),
                                    'Invisible': QColor(120,120,120),
                                    'Bendecido': QColor(150,200,255),
                                    'Maldito': QColor(128,0,128),
                                    'Protegido': QColor(255,255,255),
                                    'Acorazado': QColor(255,140,0),
                                    'Sordo': QColor(139,69,19),
                                    'Cegado': QColor(60,60,60),
                                    'Paralizado': QColor(0,0,100)
                                }
                                if hasattr(self, '_custom_states'):
                                    for k, v in self._custom_states.items():
                                        estado_colores[k] = v
                                estado_letras = {
                                    'Envenenado': 'E',
                                    'Caído': 'C',
                                    'Inspirado': 'I',
                                    'Marcado': 'M',
                                    'Muerto': 'X',
                                    'Aturdido': 'A',
                                    'Invisible': 'V',
                                    'Bendecido': 'B',
                                    'Maldito': 'D',
                                    'Protegido': 'P',
                                    'Acorazado': 'Z',
                                    'Sordo': 'S',
                                    'Cegado': 'G',
                                    'Paralizado': 'L'
                                }
                                r = 12  # radio del circulito de estado
                                offset = 0
                                for estado in sorted(tok.states):
                                    color = estado_colores.get(estado, QColor(128,128,128))
                                    letra = estado_letras.get(estado, estado[0])
                                    painter.setBrush(color)
                                    painter.setPen(Qt.black)
                                    painter.drawEllipse(tx+tw-r-2, ty+2+offset, r, r)
                                    painter.setPen(Qt.white)
                                    painter.setFont(painter.font())
                                    painter.drawText(tx+tw-r-2, ty+2+offset, r, r, Qt.AlignCenter, letra)
                                    offset += r+2
                                if tok.selected:
                                    painter.setPen(QColor(255,255,0))
                                    painter.drawRect(tx, ty, tw, th)
                        if self.scene.fog:
                            scaled_fog = self.scene.fog.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            painter.drawPixmap(0,0, scaled_fog)
                    else:
                        painter.fillRect(self.rect(), Qt.darkGray)
                def mousePressEvent(self, event):
                    if not self.scene:
                        return
                    if event.button() == Qt.LeftButton:
                        # ¿Token seleccionado?
                        if self.scene.tokens and self.scene.map_image:
                            sx = self.width() / self.scene.map_image.width()
                            sy = self.height() / self.scene.map_image.height()
                            for tok in reversed(self.scene.tokens):
                                tx = int(tok.pos.x() * sx)
                                ty = int(tok.pos.y() * sy)
                                tw = int(tok.pixmap.width() * sx)
                                th = int(tok.pixmap.height() * sy)
                                rect = QRect(tx, ty, tw, th)
                                if rect.contains(event.pos()):
                                    self.drag_token = tok
                                    self.drag_offset = event.pos() - QPoint(tx, ty)
                                    tok.selected = True
                                    self.update()
                                    return
                        # Si no, modo fog
                        if self.scene.fog:
                            self.drawing = True
                            self.last_pos = event.pos()
                            self.erase_fog(event.pos())
                    elif event.button() == Qt.RightButton:
                        # Menú contextual para eliminar token y estados
                        if self.scene.tokens and self.scene.map_image:
                            sx = self.width() / self.scene.map_image.width()
                            sy = self.height() / self.scene.map_image.height()
                            for i, tok in enumerate(reversed(self.scene.tokens)):
                                tx = int(tok.pos.x() * sx)
                                ty = int(tok.pos.y() * sy)
                                tw = int(tok.pixmap.width() * sx)
                                th = int(tok.pixmap.height() * sy)
                                rect = QRect(tx, ty, tw, th)
                                if rect.contains(event.pos()):
                                    from PyQt5.QtWidgets import QMenu
                                    menu = QMenu(self)
                                    action_del = menu.addAction("Eliminar token")
                                    # Submenú de estados
                                    estados = [
                                        "Envenenado", "Caído", "Inspirado", "Marcado", "Muerto", "Aturdido", "Invisible", "Bendecido", "Maldito", "Protegido", "Acorazado", "Sordo", "Cegado", "Paralizado"
                                    ]
                                    submenu = menu.addMenu("Estados")
                                    estado_actions = {}
                                    # Estados personalizados globales para la sesión
                                    if not hasattr(self, '_custom_states'):
                                        self._custom_states = {}  # nombre: QColor
                                    custom_states = self._custom_states
                                    for est in estados + list(custom_states.keys()):
                                        act = submenu.addAction(est)
                                        act.setCheckable(True)
                                        act.setChecked(est in tok.states)
                                        estado_actions[act] = est
                                    submenu.addSeparator()
                                    action_add_custom = submenu.addAction("Agregar estado personalizado...")
                                    action_res = menu.exec_(self.mapToGlobal(event.pos()))
                                    if action_res == action_del:
                                        idx = len(self.scene.tokens) - 1 - i
                                        self.scene.tokens.pop(idx)
                                        self.update()
                                        return
                                    elif action_res in estado_actions:
                                        est = estado_actions[action_res]
                                        if est in tok.states:
                                            tok.states.remove(est)
                                        else:
                                            tok.states.add(est)
                                        self.update()
                                        return
                                    elif action_res == action_add_custom:
                                        from PyQt5.QtWidgets import QInputDialog, QColorDialog
                                        text, ok = QInputDialog.getText(self, "Estado personalizado", "Nombre del estado:")
                                        if ok and text:
                                            color = QColorDialog.getColor(QColor(128,128,128), self, f"Color para {text}")
                                            if color.isValid():
                                                custom_states[text] = color
                                                tok.states.add(text)
                                                self.update()
                                        return
                        for tok in self.scene.tokens:
                            tok.selected = False
                        self.update()
                def mouseMoveEvent(self, event):
                    if not self.scene:
                        return
                    if self.drag_token and self.scene.map_image:
                        sx = self.width() / self.scene.map_image.width()
                        sy = self.height() / self.scene.map_image.height()
                        x = int((event.pos().x() - self.drag_offset.x()) / sx)
                        y = int((event.pos().y() - self.drag_offset.y()) / sy)
                        self.drag_token.pos = QPoint(x, y)
                        self.update()
                    elif self.drawing and self.scene.fog:
                        self.erase_fog(event.pos())
                def mouseReleaseEvent(self, event):
                    self.drawing = False
                    self.drag_token = None
                def erase_fog(self, pos):
                    if not self.scene or not self.scene.fog:
                        return
                    w, h = self.width(), self.height()
                    fw, fh = self.scene.fog.width(), self.scene.fog.height()
                    x = int(pos.x() * fw / w)
                    y = int(pos.y() * fh / h)
                    painter = QPainter(self.scene.fog)
                    painter.setCompositionMode(QPainter.CompositionMode_Clear)
                    painter.setBrush(Qt.transparent)
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(QPoint(x, y), self.brush_radius, self.brush_radius)
                    painter.end()
                    self.update()
            self.map_scenes = []
            self.map_widget = MapWidget()
            map_selector = QComboBox()
            btn_add_map = QPushButton("Agregar mapa")
            btn_del_map = QPushButton("Eliminar mapa")
            btn_fog = QPushButton("Cubrir todo (niebla)")
            btn_token = QPushButton("Cargar token")
            brush_label = QLabel("Tamaño pincel: 40")
            brush_slider = QSlider(Qt.Horizontal)
            brush_slider.setMinimum(10)
            brush_slider.setMaximum(100)
            brush_slider.setValue(40)
            def on_brush(val):
                self.map_widget.brush_radius = val
                brush_label.setText(f"Tamaño pincel: {val}")
            brush_slider.valueChanged.connect(on_brush)
            def add_map():
                path, _ = QFileDialog.getOpenFileName(tab, "Cargar mapa", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)")
                if path:
                    name = os.path.basename(path)
                    scene = MapScene(name, path)
                    self.map_scenes.append(scene)
                    map_selector.addItem(name)
                    map_selector.setCurrentIndex(len(self.map_scenes)-1)
                    self.map_widget.set_scene(scene)
            def del_map():
                idx = map_selector.currentIndex()
                if idx >= 0 and len(self.map_scenes) > 0:
                    self.map_scenes.pop(idx)
                    map_selector.removeItem(idx)
                    if self.map_scenes:
                        new_idx = max(0, idx-1)
                        map_selector.setCurrentIndex(new_idx)
                        self.map_widget.set_scene(self.map_scenes[new_idx])
                    else:
                        self.map_widget.set_scene(None)
            def select_map(idx):
                if 0 <= idx < len(self.map_scenes):
                    self.map_widget.set_scene(self.map_scenes[idx])
            def cover_all():
                scene = self.map_widget.scene
                if scene:
                    scene.clear_fog()
                    self.map_widget.update()
            def load_token():
                scene = self.map_widget.scene
                if not scene:
                    return
                path, _ = QFileDialog.getOpenFileName(tab, "Cargar token", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)")
                if path:
                    pix = QPixmap(path)
                    scene.add_token(pix)
                    self.map_widget.update()
            map_selector.currentIndexChanged.connect(select_map)
            btn_add_map.clicked.connect(add_map)
            btn_del_map.clicked.connect(del_map)
            btn_fog.clicked.connect(cover_all)
            btn_token.clicked.connect(load_token)
            controls = QHBoxLayout()
            controls.addWidget(map_selector)
            controls.addWidget(btn_add_map)
            controls.addWidget(btn_del_map)
            controls.addWidget(btn_fog)
            controls.addWidget(btn_token)
            controls.addWidget(brush_label)
            controls.addWidget(brush_slider)
            tab_layout.addLayout(controls)
            tab_layout.addWidget(self.map_widget)
        elif nombre == "Chat":
            from PyQt5.QtWidgets import QListWidget, QLineEdit, QPushButton, QHBoxLayout, QColorDialog
            from PyQt5.QtGui import QColor
            import re, random
            self.chat_list = QListWidget()
            chat_input = QLineEdit()
            chat_send = QPushButton("Enviar")
            chat_bar = QHBoxLayout(); chat_bar.addWidget(chat_input); chat_bar.addWidget(chat_send)
            tab_layout.addWidget(self.chat_list)
            tab_layout.addLayout(chat_bar)

            # Botones guardar/cargar chat
            btns = QHBoxLayout()
            btn_save = QPushButton("Guardar chat")
            btn_load = QPushButton("Cargar chat")
            btns.addWidget(btn_save)
            btns.addWidget(btn_load)
            tab_layout.addLayout(btns)

            # Macros en memoria de sesión
            if not hasattr(self, '_chat_macros'):
                self._chat_macros = {}

            def roll_dice(expr):
                # Soporta expresiones tipo 2d6+3, d20, 1d8-1, d100, etc.
                m = re.fullmatch(r"(\d*)d(\d+)([+-]\d+)?", expr.replace(' ',''))
                if not m:
                    return None
                n, die, mod = m.groups()
                n = int(n) if n else 1
                die = int(die)
                mod = int(mod) if mod else 0
                rolls = [random.randint(1, die) for _ in range(n)]
                total = sum(rolls) + mod
                return f"[{expr}] → {rolls} {'+'+str(mod) if mod else ''} = {total}"

            def send_chat():
                txt = chat_input.text().strip()
                if not txt:
                    return
                # --- Macros ---
                if txt.startswith("/macro "):
                    # /macro saludo=/w Gandalf Hola!
                    try:
                        name, cmd = txt[7:].split('=',1)
                        name = name.strip()
                        self._chat_macros[name] = cmd.strip()
                        self.chat_list.addItem(f"Macro '{name}' guardada.")
                    except Exception:
                        self.chat_list.addItem("Error de macro. Usa: /macro nombre=comando")
                    chat_input.clear()
                    return
                if txt.startswith("/") and not txt.startswith("/w ") and not txt.startswith("/macro "):
                    macro = txt[1:].split(' ')[0]
                    if macro in self._chat_macros:
                        txt = self._chat_macros[macro]
                # --- Dados ---
                if txt.startswith("/d") or re.match(r"/\d*d\d+", txt):
                    expr = txt[1:] if txt.startswith("/d") else txt[1:]
                    res = roll_dice(expr)
                    if res:
                        item = self.chat_list.addItem(f"🎲 {res}")
                    else:
                        self.chat_list.addItem("Comando de dado inválido.")
                    chat_input.clear()
                    return
                # --- Whispers ---
                if txt.startswith("/w "):
                    # /w Gandalf Hola!
                    parts = txt.split(' ',2)
                    if len(parts)>=3:
                        target, msg = parts[1], parts[2]
                        modo_dm = getattr(self, '_modo_dm', True)
                        if modo_dm or (hasattr(self, 'char_name') and self.char_name.text()==target):
                            self.chat_list.addItem(f"(whisper a {target}): {msg}")
                        else:
                            self.chat_list.addItem("No tienes permiso para enviar/ver este whisper.")
                    else:
                        self.chat_list.addItem("Uso: /w <nombre> <mensaje>")
                    chat_input.clear()
                    return
                # Normal
                self.chat_list.addItem(txt)
                chat_input.clear()
            chat_send.clicked.connect(send_chat)
            chat_input.returnPressed.connect(send_chat)
            def save_chat():
                from PyQt5.QtWidgets import QFileDialog, QMessageBox
                path, _ = QFileDialog.getSaveFileName(tab, "Guardar chat", "", "Chat (*.txt)")
                if path:
                    with open(path, 'w', encoding='utf-8') as f:
                        for i in range(self.chat_list.count()):
                            f.write(self.chat_list.item(i).text() + '\n')
                    QMessageBox.information(tab, "Chat guardado", f"Chat guardado en {path}")
            def load_chat():
                from PyQt5.QtWidgets import QFileDialog, QMessageBox
                path, _ = QFileDialog.getOpenFileName(tab, "Cargar chat", "", "Chat (*.txt)")
                if path:
                    with open(path, 'r', encoding='utf-8') as f:
                        self.chat_list.clear()
                        for line in f:
                            self.chat_list.addItem(line.rstrip('\n'))
                    QMessageBox.information(tab, "Chat cargado", f"Chat cargado de {path}")
            btn_save.clicked.connect(save_chat)
            btn_load.clicked.connect(load_chat)
            def save_chat():
                path, _ = QFileDialog.getSaveFileName(tab, "Guardar chat", "", "Chat (*.txt)")
                if path:
                    try:
                        with open(path, 'w', encoding='utf-8') as f:
                            for i in range(self.chat_list.count()):
                                f.write(self.chat_list.item(i).text() + '\n')
                        QMessageBox.information(tab, "Chat guardado", f"Chat guardado en {path}")
                    except Exception as e:
                        QMessageBox.critical(tab, "Error", f"No se pudo guardar el chat: {e}")
            def load_chat():
                path, _ = QFileDialog.getOpenFileName(tab, "Cargar chat", "", "Chat (*.txt)")
                if path:
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            self.chat_list.clear()
                            for line in f:
                                self.chat_list.addItem(line.rstrip())
                        QMessageBox.information(tab, "Chat cargado", f"Chat cargado de {path}")
                    except Exception as e:
                        QMessageBox.critical(tab, "Error", f"No se pudo cargar el chat: {e}")
            btn_save.clicked.connect(save_chat)
            btn_load.clicked.connect(load_chat)
        elif nombre == "Dados":
            from PyQt5.QtWidgets import QPushButton, QListWidget, QHBoxLayout, QComboBox, QSpinBox
            import random
            self.dice_history = QListWidget()
            dice_layout = QHBoxLayout()
            dice_type = QComboBox(); dice_type.addItems(["d4", "d6", "d8", "d10", "d12", "d20", "d100"])
            dice_qty = QSpinBox(); dice_qty.setRange(1, 20); dice_qty.setValue(1)
            dice_btn = QPushButton("Lanzar")
            dice_layout.addWidget(QLabel("Tipo:"))
            dice_layout.addWidget(dice_type)
            dice_layout.addWidget(QLabel("Cantidad:"))
            dice_layout.addWidget(dice_qty)
            dice_layout.addWidget(dice_btn)
            tab_layout.addLayout(dice_layout)
            tab_layout.addWidget(self.dice_history)
            def lanzar_dados():
                tipo = int(dice_type.currentText()[1:])
                qty = dice_qty.value()
                resultados = [random.randint(1, tipo) for _ in range(qty)]
                total = sum(resultados)
                self.dice_history.addItem(f"Tirada {qty}x d{tipo}: {resultados} (Total: {total})")
            dice_btn.clicked.connect(lanzar_dados)
        elif nombre == "Fichas":
            from PyQt5.QtWidgets import QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QMessageBox
            import json
            form = QFormLayout()
            self.char_name = QLineEdit()
            self.char_class = QLineEdit()
            self.char_level = QLineEdit()
            form.addRow("Nombre", self.char_name)
            form.addRow("Clase", self.char_class)
            form.addRow("Nivel", self.char_level)
            tab_layout.addLayout(form)
            btns = QHBoxLayout()
            btn_save = QPushButton("Guardar ficha")
            btn_load = QPushButton("Cargar ficha")
            btns.addWidget(btn_save)
            btns.addWidget(btn_load)
            tab_layout.addLayout(btns)
            def save_ficha():
                data = {
                    'nombre': self.char_name.text(),
                    'clase': self.char_class.text(),
                    'nivel': self.char_level.text()
                }
                path, _ = QFileDialog.getSaveFileName(tab, "Guardar ficha", "", "Ficha (*.json)")
                if path:
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    QMessageBox.information(tab, "Ficha guardada", f"Ficha guardada en {path}")
            def load_ficha():
                path, _ = QFileDialog.getOpenFileName(tab, "Cargar ficha", "", "Ficha (*.json)")
                if path:
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        self.char_name.setText(data.get('nombre', ''))
                        self.char_class.setText(data.get('clase', ''))
                        self.char_level.setText(str(data.get('nivel', '')))
                        QMessageBox.information(tab, "Ficha cargada", f"Ficha cargada de {path}")
                    except Exception as e:
                        QMessageBox.critical(tab, "Error", f"No se pudo cargar la ficha: {e}")
            btn_save.clicked.connect(save_ficha)
            btn_load.clicked.connect(load_ficha)
            from PyQt5.QtWidgets import QLabel, QListWidget, QLineEdit, QPushButton
            notes_label = QLabel("Notas de este mapa:")
            notes_list = QListWidget()
            notes_input = QLineEdit()
            notes_input.setPlaceholderText("Agregar nota...")
            notes_add_btn = QPushButton("+")
            notes_del_btn = QPushButton("-")
            notes_priv_chk = QPushButton("🔒 Pública")
            notes_priv_chk.setCheckable(True)
            notes_priv_chk.setChecked(False)
            notes_bar = QHBoxLayout()
            notes_bar.addWidget(notes_input)
            notes_bar.addWidget(notes_add_btn)
            notes_bar.addWidget(notes_del_btn)
            notes_bar.addWidget(notes_priv_chk)
            tab_layout.addWidget(notes_label)
            tab_layout.addWidget(notes_list)
            tab_layout.addLayout(notes_bar)

            # --- Sincroniza notas con el mapa activo y el modo ---
            def update_notes():
                notes_list.clear()
                scene = self.map_widget.scene
                modo_dm = getattr(self, '_modo_dm', True)
                if scene:
                    for n in getattr(scene, 'notes', []):
                        txt = n['texto'] if isinstance(n, dict) else n
                        priv = n.get('privada', False) if isinstance(n, dict) else False
                        if priv and not modo_dm:
                            continue  # Solo DM ve privadas
                        if priv:
                            notes_list.addItem("🔒 " + txt)
                        else:
                            notes_list.addItem(txt)
                # UI: solo DM puede marcar privadas
                notes_priv_chk.setEnabled(modo_dm)
                if not modo_dm:
                    notes_priv_chk.setChecked(False)
                    notes_priv_chk.setText("🔓 Pública")
        elif nombre == "Notas":
            from PyQt5.QtWidgets import QListWidget, QPushButton, QHBoxLayout, QInputDialog, QFileDialog, QMessageBox
            self.notes_list = QListWidget()
            btn_add = QPushButton("Agregar")
            btn_edit = QPushButton("Editar")
            btn_del = QPushButton("Eliminar")
            btn_save = QPushButton("Guardar notas")
            btn_load = QPushButton("Cargar notas")
            btns = QHBoxLayout(); btns.addWidget(btn_add); btns.addWidget(btn_edit); btns.addWidget(btn_del); btns.addWidget(btn_save); btns.addWidget(btn_load)
            tab_layout.addWidget(self.notes_list)
            tab_layout.addLayout(btns)
            def add_note():
                text, ok = QInputDialog.getText(tab, "Agregar nota", "Contenido de la nota:")
                if ok and text.strip():
                    self.notes_list.addItem(text.strip())
            def edit_note():
                item = self.notes_list.currentItem()
                if item:
                    text, ok = QInputDialog.getText(tab, "Editar nota", "Contenido de la nota:", text=item.text())
                    if ok and text.strip():
                        item.setText(text.strip())
            def del_note():
                row = self.notes_list.currentRow()
                if row >= 0:
                    self.notes_list.takeItem(row)
            def save_notes():
                path, _ = QFileDialog.getSaveFileName(tab, "Guardar notas", "", "Notas (*.txt)")
                if path:
                    try:
                        with open(path, 'w', encoding='utf-8') as f:
                            for i in range(self.notes_list.count()):
                                f.write(self.notes_list.item(i).text() + '\n')
                        QMessageBox.information(tab, "Notas guardadas", f"Notas guardadas en {path}")
                    except Exception as e:
                        QMessageBox.critical(tab, "Error", f"No se pudo guardar las notas: {e}")
            def load_notes():
                path, _ = QFileDialog.getOpenFileName(tab, "Cargar notas", "", "Notas (*.txt)")
                if path:
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            self.notes_list.clear()
                            for line in f:
                                self.notes_list.addItem(line.rstrip())
                        QMessageBox.information(tab, "Notas cargadas", f"Notas cargadas de {path}")
                    except Exception as e:
                        QMessageBox.critical(tab, "Error", f"No se pudo cargar las notas: {e}")
            btn_add.clicked.connect(add_note)
            btn_edit.clicked.connect(edit_note)
            btn_del.clicked.connect(del_note)
            btn_save.clicked.connect(save_notes)
            btn_load.clicked.connect(load_notes)
        elif nombre == "Macros":
            from PyQt5.QtWidgets import QListWidget, QPushButton, QHBoxLayout
            self.macros_list = QListWidget()
            btn_add = QPushButton("Agregar")
            btn_del = QPushButton("Eliminar")
            btn_run = QPushButton("Ejecutar")
            btns = QHBoxLayout(); btns.addWidget(btn_add); btns.addWidget(btn_del); btns.addWidget(btn_run)
            tab_layout.addWidget(self.macros_list)
            tab_layout.addLayout(btns)
        elif nombre == "Iniciativa":
            from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QListWidget, QLineEdit, QInputDialog, QMessageBox, QLabel, QSpinBox
            import random
            self.init_list = QListWidget()
            self.init_list.setSelectionMode(QListWidget.SingleSelection)
            tab_layout.addWidget(QLabel("Iniciativa - Orden de Turnos"))
            tab_layout.addWidget(self.init_list)
            # --- Controles ---
            controls = QHBoxLayout()
            name_input = QLineEdit(); name_input.setPlaceholderText("Nombre")
            ini_input = QSpinBox(); ini_input.setRange(1, 99); ini_input.setPrefix("Ini: ")
            roll_btn = QPushButton("Tirar d20")
            add_btn = QPushButton("Añadir")
            del_btn = QPushButton("Eliminar")
            up_btn = QPushButton("↑")
            down_btn = QPushButton("↓")
            next_btn = QPushButton("Siguiente")
            prev_btn = QPushButton("Anterior")
            restart_btn = QPushButton("Reiniciar")
            announce_btn = QPushButton("Anunciar turno")
            controls.addWidget(name_input)
            controls.addWidget(ini_input)
            controls.addWidget(roll_btn)
            controls.addWidget(add_btn)
            controls.addWidget(del_btn)
            controls.addWidget(up_btn)
            controls.addWidget(down_btn)
            controls.addWidget(next_btn)
            controls.addWidget(prev_btn)
            controls.addWidget(restart_btn)
            controls.addWidget(announce_btn)
            tab_layout.addLayout(controls)

            # --- Estado de turno actual ---
            self._initiative_turn = 0
            def refresh_initiative():
                for i in range(self.init_list.count()):
                    item = self.init_list.item(i)
                    txt = item.text()
                    # Limpia iconos previos
                    if txt.startswith("▶ "):
                        txt = txt[2:]
                    # Iconos por tipo
                    if "(PJ)" in txt or "(Jugador)" in txt:
                        txt_icon = "🎲 " + txt
                    elif "(Enemigo)" in txt or "(NPC)" in txt:
                        txt_icon = "👹 " + txt
                    else:
                        txt_icon = txt
                    item.setText(txt_icon)
                    item.setForeground(Qt.white)
                    font = item.font(); font.setBold(False); item.setFont(font)
                    item.setBackground(Qt.transparent)
                if self.init_list.count():
                    idx = self._initiative_turn % self.init_list.count()
                    item = self.init_list.item(idx)
                    txt = item.text()
                    # Evita duplicar ▶
                    if not txt.startswith("▶ "):
                        item.setText("▶ " + txt)
                    item.setForeground(Qt.darkGreen)
                    font = item.font(); font.setBold(True); item.setFont(font)
                    item.setBackground(Qt.green)
                    self.init_list.setCurrentRow(idx)
            def add_entry():
                name = name_input.text().strip()
                ini = ini_input.value()
                if not name:
                    QMessageBox.warning(tab, "Falta nombre", "Introduce un nombre.")
                    return
                self.init_list.addItem(f"{name} ({ini})")
                sort_initiative()
                name_input.clear()
            def roll_initiative():
                name = name_input.text().strip()
                ini = random.randint(1,20)
                ini_input.setValue(ini)
                if name:
                    self.init_list.addItem(f"{name} ({ini})")
                    sort_initiative()
                    name_input.clear()
            def del_entry():
                row = self.init_list.currentRow()
                if row >= 0:
                    self.init_list.takeItem(row)
                    if self.init_list.count()==0:
                        self._initiative_turn = 0
                    else:
                        self._initiative_turn %= self.init_list.count()
                    refresh_initiative()
            def move_up():
                row = self.init_list.currentRow()
                if row > 0:
                    item = self.init_list.takeItem(row)
                    self.init_list.insertItem(row-1, item)
                    self.init_list.setCurrentRow(row-1)
                    refresh_initiative()
            def move_down():
                row = self.init_list.currentRow()
                if row < self.init_list.count()-1:
                    item = self.init_list.takeItem(row)
                    self.init_list.insertItem(row+1, item)
                    self.init_list.setCurrentRow(row+1)
                    refresh_initiative()
            def next_turn():
                if self.init_list.count()==0:
                    return
                self._initiative_turn = (self._initiative_turn+1) % self.init_list.count()
                refresh_initiative()
            def prev_turn():
                if self.init_list.count()==0:
                    return
                self._initiative_turn = (self._initiative_turn-1) % self.init_list.count()
                refresh_initiative()
            def restart():
                self._initiative_turn = 0
                refresh_initiative()
            def sort_initiative():
                # Ordena por iniciativa (número entre paréntesis, descendente)
                items = [self.init_list.item(i).text() for i in range(self.init_list.count())]
                items = sorted(items, key=lambda x: int(x.split('(')[-1].split(')')[0]), reverse=True)
                self.init_list.clear()
                for it in items:
                    self.init_list.addItem(it)
                self._initiative_turn = 0
                refresh_initiative()
            def announce_turn():
                if self.init_list.count()==0:
                    return
                idx = self._initiative_turn % self.init_list.count()
                item = self.init_list.item(idx)
                msg = f"Turno de: {item.text().replace('▶ ','')}"
                if hasattr(self, 'chat_list'):
                    self.chat_list.addItem(f"🛎️ {msg}")
                else:
                    QMessageBox.information(tab, "Turno", msg)
            add_btn.clicked.connect(add_entry)
            roll_btn.clicked.connect(roll_initiative)
            del_btn.clicked.connect(del_entry)
            up_btn.clicked.connect(move_up)
            down_btn.clicked.connect(move_down)
            next_btn.clicked.connect(next_turn)
            prev_btn.clicked.connect(prev_turn)
            restart_btn.clicked.connect(restart)
            announce_btn.clicked.connect(announce_turn)
            def on_initiative_double_click(item):
                name = item.text()
                # Limpia iconos y prefijos
                for prefix in ["▶ ", "🎲 ", "👹 "]:
                    if name.startswith(prefix):
                        name = name[len(prefix):]
                name = name.strip()
                # Buscar token en todos los mapas
                token_found = False
                if hasattr(self, 'map_scenes') and hasattr(self, 'map_widget'):
                    for idx, scene in enumerate(self.map_scenes):
                        for tok in getattr(scene, 'tokens', []):
                            # Puede ser dict o clase Token
                            tname = tok['name'] if isinstance(tok, dict) else getattr(tok, 'name', None)
                            if tname == name:
                                # Cambia de mapa si es necesario
                                if hasattr(self, 'map_widget') and hasattr(self.map_widget, 'set_scene'):
                                    self.map_widget.set_scene(scene)
                                # Centra el mapa en el token
                                if hasattr(self.map_widget, 'pan') and hasattr(self.map_widget, 'update'):
                                    # Suponemos que el token tiene 'x' y 'y' (dict) o pos (QPoint)
                                    if isinstance(tok, dict):
                                        x, y = tok.get('x', 0), tok.get('y', 0)
                                    else:
                                        pos = getattr(tok, 'pos', None)
                                        x, y = pos.x(), pos.y() if pos else (0, 0)
                                    # Centra el mapa
                                    self.map_widget.pan = QPoint(-x + self.map_widget.width()//2, -y + self.map_widget.height()//2)
                                    self.map_widget.update()
                                token_found = True
                                break
                        if token_found:
                            break
                next_turn()
                announce_turn()
            self.init_list.itemDoubleClicked.connect(on_initiative_double_click)
            refresh_initiative()
        elif nombre == "Historial":
            from PyQt5.QtWidgets import QListWidget
            self.history_list = QListWidget()
            tab_layout.addWidget(self.history_list)
        elif nombre == "Agenda":
            from PyQt5.QtWidgets import QCalendarWidget, QListWidget, QPushButton, QHBoxLayout, QVBoxLayout, QInputDialog, QMessageBox
            from PyQt5.QtCore import QDate, Qt
            self.calendar = QCalendarWidget()
            self.event_list = QListWidget()
            self.events_by_date = {}  # {QDate.toString(): [str, ...]}
            self.event_audio_by_date = {}  # {date: [audio_path or None, ...]}
            btn_play_event_audio = QPushButton("Reproducir audio del evento")
            btn_play_event_audio.setEnabled(False)
            def add_event():
                text, ok = QInputDialog.getText(tab, "Nuevo Evento", "Descripción del evento:")
                if ok and text.strip():
                    date = self.calendar.selectedDate().toString("yyyy-MM-dd")
                    self.events_by_date.setdefault(date, []).append(text.strip())
                    # Pregunta si quiere asociar audio
                    audio_path = None
                    resp = QMessageBox.question(tab, "¿Asociar audio?", "¿Quieres asociar un audio a este evento?", QMessageBox.Yes | QMessageBox.No)
                    if resp == QMessageBox.Yes:
                        files, _ = QFileDialog.getOpenFileNames(tab, "Selecciona archivo de audio", "", "Audio (*.wav)")
                        if files:
                            audio_path = files[0]
                    self.event_audio_by_date.setdefault(date, []).append(audio_path)
                    refresh_events()
            def edit_event():
                row = self.event_list.currentRow()
                if row < 0:
                    return
                date = self.calendar.selectedDate().toString("yyyy-MM-dd")
                old = self.events_by_date.get(date, [])[row]
                text, ok = QInputDialog.getText(tab, "Editar Evento", "Descripción:", text=old)
                if ok and text.strip():
                    self.events_by_date[date][row] = text.strip()
                    # Permite cambiar audio asociado
                    audio_path = self.event_audio_by_date.get(date, [None]*len(self.events_by_date[date]))[row]
                    resp = QMessageBox.question(tab, "¿Cambiar audio?", "¿Quieres cambiar el audio asociado?", QMessageBox.Yes | QMessageBox.No)
                    if resp == QMessageBox.Yes:
                        files, _ = QFileDialog.getOpenFileNames(tab, "Selecciona archivo de audio", "", "Audio (*.wav)")
                        if files:
                            audio_path = files[0]
                        else:
                            audio_path = None
                        self.event_audio_by_date[date][row] = audio_path
                    refresh_events()
            def del_event():
                row = self.event_list.currentRow()
                if row < 0:
                    return
                date = self.calendar.selectedDate().toString("yyyy-MM-dd")
                del self.events_by_date[date][row]
                if date in self.event_audio_by_date and len(self.event_audio_by_date[date]) > row:
                    del self.event_audio_by_date[date][row]
                    if not self.event_audio_by_date[date]:
                        del self.event_audio_by_date[date]
                if not self.events_by_date[date]:
                    del self.events_by_date[date]
                refresh_events()
            btns = QHBoxLayout()
            add_btn = QPushButton("Añadir")
            edit_btn = QPushButton("Editar")
            del_btn = QPushButton("Eliminar")
            btns.addWidget(add_btn)
            btns.addWidget(edit_btn)
            btns.addWidget(del_btn)
            vbox = QVBoxLayout()
            vbox.addWidget(self.calendar)
            vbox.addWidget(self.event_list)
            vbox.addLayout(btns)
            tab_layout.addLayout(vbox)
            def highlight_event_days():
                fmt_event = self.calendar.dateTextFormat(self.calendar.selectedDate())
                fmt_event.setBackground(Qt.yellow)
                fmt_event.setForeground(Qt.black)
                fmt_normal = self.calendar.dateTextFormat(self.calendar.selectedDate())
                fmt_normal.setBackground(Qt.transparent)
                fmt_normal.setForeground(Qt.white)
                # Limpia todos
                for y in range(1970, 2100):
                    for m in range(1,13):
                        for d in range(1,32):
                            try:
                                date = QDate(y,m,d)
                                self.calendar.setDateTextFormat(date, fmt_normal)
                            except:
                                pass
                # Resalta días con eventos
                for key in self.events_by_date.keys():
                    date = QDate.fromString(key, "yyyy-MM-dd")
                    if date.isValid():
                        self.calendar.setDateTextFormat(date, fmt_event)

            self._agenda_reminder_dates = set()
            def refresh_events():
                date = self.calendar.selectedDate().toString("yyyy-MM-dd")
                self.event_list.clear()
                audios = self.event_audio_by_date.get(date, [])
                for idx, ev in enumerate(self.events_by_date.get(date, [])):
                    label = "📅 " + ev
                    if idx < len(audios) and audios[idx]:
                        label += " 🎵"
                    self.event_list.addItem(label)
                highlight_event_days()
                # Recordatorio automático en chat solo una vez por fecha/sesión
                if hasattr(self, 'chat_list') and self.events_by_date.get(date) and date not in self._agenda_reminder_dates:
                    msg = f"📅 Recordatorio: eventos para {date}: " + ", ".join(self.events_by_date[date])
                    if any(audios):
                        msg += " (con audio)"
                    self.chat_list.addItem(msg)
                    self._agenda_reminder_dates.add(date)
                btn_play_event_audio.setEnabled(False)

            def on_event_selected():
                row = self.event_list.currentRow()
                date = self.calendar.selectedDate().toString("yyyy-MM-dd")
                audios = self.event_audio_by_date.get(date, [])
                if row >= 0 and row < len(audios) and audios[row]:
                    btn_play_event_audio.setEnabled(True)
                else:
                    btn_play_event_audio.setEnabled(False)

            def play_event_audio():
                row = self.event_list.currentRow()
                date = self.calendar.selectedDate().toString("yyyy-MM-dd")
                audios = self.event_audio_by_date.get(date, [])
                if row >= 0 and row < len(audios) and audios[row]:
                    try:
                        import threading, sounddevice as sd, numpy as np, wave
                        fname = audios[row]
                        def _play():
                            try:
                                wf = wave.open(fname, 'rb')
                                samplerate = wf.getframerate()
                                data = wf.readframes(wf.getnframes())
                                audio = np.frombuffer(data, dtype=np.int16)
                                audio = audio.astype(np.float32) / 32768.0
                                sd.play(audio, samplerate=samplerate)
                                sd.wait()
                            except Exception as e:
                                QMessageBox.warning(tab, "Error audio", str(e))
                        threading.Thread(target=_play, daemon=True).start()
                    except Exception as e:
                        QMessageBox.warning(tab, "Error audio", str(e))

            self.event_list.currentRowChanged.connect(on_event_selected)
            btn_play_event_audio.clicked.connect(play_event_audio)
            self.calendar.selectionChanged.connect(refresh_events)
            add_btn.clicked.connect(add_event)
            edit_btn.clicked.connect(edit_event)
            del_btn.clicked.connect(del_event)
            vbox.addWidget(btn_play_event_audio)
            refresh_events()
        elif nombre == "Audio":
            from PyQt5.QtWidgets import QPushButton, QLabel, QSlider, QFileDialog, QListWidget, QHBoxLayout, QVBoxLayout
            from PyQt5.QtCore import Qt
            import os
            self.audio_files = []
            self.audio_list = QListWidget()
            self.audio_player_label = QLabel("Ningún audio seleccionado")
            self.audio_volume = QSlider(Qt.Horizontal)
            self.audio_volume.setRange(0, 100)
            self.audio_volume.setValue(80)
            btn_load = QPushButton("Cargar audio")
            btn_play = QPushButton("Reproducir")
            btn_pause = QPushButton("Pausar")
            btn_stop = QPushButton("Detener")
            hbtns = QHBoxLayout()
            hbtns.addWidget(btn_load)
            hbtns.addWidget(btn_play)
            hbtns.addWidget(btn_pause)
            hbtns.addWidget(btn_stop)
            vbox = QVBoxLayout()
            vbox.addWidget(QLabel("Lista de audios (mp3/wav)"))
            vbox.addWidget(self.audio_list)
            vbox.addLayout(hbtns)
            vbox.addWidget(QLabel("Volumen"))
            vbox.addWidget(self.audio_volume)
            vbox.addWidget(self.audio_player_label)
            tab_layout.addLayout(vbox)
            # --- Lógica de audio ---
            import threading
            import sounddevice as sd
            import numpy as np
            import wave
            import sys
            self._audio_stream = None
            self._audio_data = None
            self._audio_samplerate = 44100
            self._audio_playing = False
            def load_audio():
                files, _ = QFileDialog.getOpenFileNames(tab, "Selecciona archivos de audio", "", "Audio (*.wav)")
                for f in files:
                    if f not in self.audio_files:
                        self.audio_files.append(f)
                        self.audio_list.addItem(os.path.basename(f))
            def play_audio():
                row = self.audio_list.currentRow()
                if row < 0 or row >= len(self.audio_files):
                    return
                fname = self.audio_files[row]
                self.audio_player_label.setText(f"Reproduciendo: {os.path.basename(fname)}")
                def _play():
                    try:
                        wf = wave.open(fname, 'rb')
                        self._audio_samplerate = wf.getframerate()
                        data = wf.readframes(wf.getnframes())
                        audio = np.frombuffer(data, dtype=np.int16)
                        audio = audio.astype(np.float32) / 32768.0
                        vol = self.audio_volume.value() / 100.0
                        audio = audio * vol
                        self._audio_playing = True
                        sd.play(audio, samplerate=self._audio_samplerate)
                        sd.wait()
                        self._audio_playing = False
                    except Exception as e:
                        self.audio_player_label.setText(f"Error: {e}")
                threading.Thread(target=_play, daemon=True).start()
            def pause_audio():
                try:
                    sd.stop()
                    self._audio_playing = False
                except Exception:
                    pass
            def stop_audio():
                try:
                    sd.stop()
                    self._audio_playing = False
                    self.audio_player_label.setText("Ningún audio seleccionado")
                except Exception:
                    pass
            btn_load.clicked.connect(load_audio)
            btn_play.clicked.connect(play_audio)
            btn_pause.clicked.connect(pause_audio)
            btn_stop.clicked.connect(stop_audio)
            self.audio_volume.valueChanged.connect(lambda v: None)
        elif nombre == "Voz":
            from PyQt5.QtWidgets import QLineEdit, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QMessageBox
            import webbrowser
            self.discord_url = ""
            label = QLabel("Pega aquí la invitación/canal de Discord (https://discord.gg/... o https://discord.com/channels/...) :")
            url_input = QLineEdit()
            url_input.setPlaceholderText("URL de Discord")
            btn_join = QPushButton("Unirse al canal de voz")
            status = QLabel()
            def update_status():
                if url_input.text().strip():
                    status.setText("🟢 Enlace configurado")
                else:
                    status.setText("🔴 Sin enlace")
            def join_discord():
                url = url_input.text().strip()
                if url.startswith("http"):
                    webbrowser.open(url)
                else:
                    QMessageBox.warning(tab, "URL inválida", "Por favor, pega una URL válida de Discord.")
            def save_url():
                self.discord_url = url_input.text().strip()
                update_status()
            url_input.textChanged.connect(save_url)
            btn_join.clicked.connect(join_discord)
            update_status()
            vbox = QVBoxLayout()
            vbox.addWidget(label)
            vbox.addWidget(url_input)
            vbox.addWidget(btn_join)
            vbox.addWidget(status)
            tab_layout.addLayout(vbox)
            # Al cargar campaña, restaurar url
            if hasattr(self, '_discord_url_cache'):
                url_input.setText(self._discord_url_cache)
        tab.setLayout(tab_layout)
        self.tabs.addTab(tab, nombre)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VTTWindow()
    window.show()
    sys.exit(app.exec_())


    def load_template(self):
        print("load_template llamado (stub)")
        # Aquí se implementará la carga de plantillas

    def remove_template(self):
        print("remove_template llamado (stub)")
        # Aquí se implementará la eliminación de plantillas

    def use_template(self):
        print("use_template llamado (stub)")
        # Aquí se implementará el uso de plantillas

    def add_note(self):
        print("add_note llamado (stub)")
        # Aquí se implementará agregar nota

    def remove_note(self):
        print("remove_note llamado (stub)")
        # Aquí se implementará eliminar nota

    def edit_note(self):
        print("edit_note llamado (stub)")
        # Aquí se implementará editar nota

    def add_macro(self):
        print("add_macro llamado (stub)")
        # Aquí se implementará agregar macro

    def remove_macro(self):
        print("remove_macro llamado (stub)")
        # Aquí se implementará eliminar macro

    def run_macro(self):
        print("run_macro llamado (stub)")
        # Aquí se implementará ejecutar macro

    def save_campaign(self):
        print("save_campaign llamado (stub)")
        # Aquí se implementará guardar campaña

    def load_campaign(self):
        print("load_campaign llamado (stub)")
        # Aquí se implementará cargar campaña

    def on_initiative_reordered(self, *args, **kwargs):
        pass
    def _initiative_drag_start(self, *args, **kwargs):
        pass
    def add_initiative_entry_vtt(self, *args, **kwargs):
        pass
    def remove_initiative_entry(self, *args, **kwargs):
        pass
    def advance_initiative(self, *args, **kwargs):
        pass
    def __init__(self, network=None, is_server=False, host="localhost", player_name="Jugador"):
        super().__init__()
        try:
            # ...
            # (resto del código)
            # --- DRAG&DROP ORDEN INICIATIVA ---
            self._initiative_drag_from = None
            self.setWindowTitle("VTT - Virtual Tabletop")
            self.setGeometry(100, 100, 1100, 750)
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.layout = QVBoxLayout()
            self.setStyleSheet("""
                QWidget {
                    background-color: #232629;
                    color: #f0f0f0;
                    font-family: Segoe UI, Arial, sans-serif;
                    font-size: 15px;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: #232629;
                    border-radius: 8px;
                    padding: 12px 28px;
                    font-size: 18px;
                    font-weight: bold;
                    border: 2px solid #232629;
                }
                QPushButton:hover {
                    background-color: #232629;
                    color: #f0f0f0;
                    border: 2px solid #f0f0f0;
                }
                QLineEdit, QTextEdit, QListWidget {
                    background-color: #292c31;
                    color: #f0f0f0;
                    border-radius: 4px;
                }
                QTabWidget::pane {
                    border: 1px solid #333;
                    border-radius: 10px;
                    background: #232629;
                }
                QTabBar::tab {
                    background: #232629;
                    color: #f0f0f0;
                    font-size: 19px;
                    font-weight: bold;
                    min-width: 120px;
                    min-height: 36px;
                    padding: 10px 28px;
                    border: 2px solid #444857;
                    border-bottom: none;
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background: #f0f0f0;
                    color: #232629;
                    border: 2px solid #f0f0f0;
                    border-bottom: 2px solid #232629;
                }
                QTabBar::tab:hover {
                    background: #555a6a;
                    color: #fff;
                }
            """)
            self.network = network
            self.is_server = is_server
            self.host = host
            self.player_name = player_name or "Jugador"
            self.user_colors = {}
            self.macros = []
            self.map_widget = None
            # if self.network:
            #     self.start_network_listener()

            # Tabs principales
            self.tabs = QTabWidget()
            self.tabs.setMinimumSize(400, 400)
            map_layout = QVBoxLayout()
            map_controls = QHBoxLayout()
            btn_zoom_in = QPushButton("+")
            btn_zoom_out = QPushButton("–")
            btn_grid = QPushButton("Rejilla")
            grid_type_combo = QComboBox(); grid_type_combo.addItems(["Cuadrícula", "Hexágonos"])
            grid_size_spin = QSpinBox(); grid_size_spin.setRange(20, 200); grid_size_spin.setValue(50)
            btn_fog = QPushButton("Niebla")
            fog_mode_combo = QComboBox(); fog_mode_combo.addItems(["Revelar", "Ocultar"])
            fog_brush_spin = QSpinBox(); fog_brush_spin.setRange(10, 100); fog_brush_spin.setValue(40)
            self.map_widget = MapWidget()
            map_controls.addWidget(btn_zoom_in)
            map_controls.addWidget(btn_zoom_out)
            map_controls.addWidget(btn_grid)
            map_controls.addWidget(grid_type_combo)
            map_controls.addWidget(grid_size_spin)
            map_controls.addWidget(btn_fog)
            map_controls.addWidget(fog_mode_combo)
            map_controls.addWidget(fog_brush_spin)
            map_layout.addLayout(map_controls)
            # Conexiones
            btn_zoom_in.clicked.connect(self.map_widget.zoom_in)
            btn_zoom_out.clicked.connect(self.map_widget.zoom_out)
            btn_grid.clicked.connect(self.map_widget.toggle_grid)
            grid_type_combo.currentTextChanged.connect(lambda t: self.map_widget.set_grid_type('cuadricula' if t=="Cuadrícula" else 'hex'))
            map_layout.addWidget(self.map_widget)

            map_tab = QWidget()
            map_tab.setLayout(map_layout)
            self.tabs.addTab(map_tab, "Mapa")

            # --- TAB CHAT ---
            chat_tab = QWidget()
            chat_layout = QVBoxLayout()
            self.chat_box = QListWidget()
            self.chat_box.setFont(QFont("Segoe UI", 12))
            chat_layout.addWidget(self.chat_box)
            chat_input_layout = QHBoxLayout()
            self.chat_input = QLineEdit()
            self.chat_input.setPlaceholderText("Escribe un mensaje...")
            chat_input_layout.addWidget(self.chat_input)
            self.send_btn = QPushButton("Enviar")
            chat_input_layout.addWidget(self.send_btn)

            chat_layout.addLayout(chat_input_layout)
            chat_tab.setLayout(chat_layout)
            self.tabs.addTab(chat_tab, "Chat")
            

            # --- TAB DADOS ---
            dice_tab = QWidget()
            dice_layout = QVBoxLayout()
            dice_btns = QHBoxLayout()
            self.dice_types = [4, 6, 8, 10, 12, 20, 100]
            self.dice_buttons = {}
            for d in self.dice_types:
                btn = QPushButton(f"d{d}")
                btn.clicked.connect(lambda _, dd=d: self.roll_dice(dd))
                self.dice_buttons[d] = btn
                dice_btns.addWidget(btn)
            dice_layout.addLayout(dice_btns)
            self.dice_history = QListWidget()
            dice_layout.addWidget(QLabel("Historial de tiradas:"))
            dice_layout.addWidget(self.dice_history)
            dice_tab.setLayout(dice_layout)
            self.tabs.addTab(dice_tab, "Dados")
            

            # --- TAB FICHAS ---
            sheet_tab = QTabWidget()
            # Vampiro
            vampiro_widget = self.map_widget.make_vampiro_sheet()
            sheet_tab.addTab(vampiro_widget, "Vampiro")
            # D&D
            dnd_widget = self.map_widget.make_dnd_sheet()
            sheet_tab.addTab(dnd_widget, "D&D")
            self.tabs.addTab(sheet_tab, "Fichas")
            

            # --- TAB FICHAS COMPARTIDAS ---
            self.shared_sheets_tab = QTabWidget()
            self.tabs.addTab(self.shared_sheets_tab, "Fichas compartidas")
            

            # --- TAB INICIATIVA ---
            self.initiative_tab = QWidget()
            self.initiative_layout = QVBoxLayout()
            self.initiative_list = QListWidget()
            self.initiative_list.setDragDropMode(QListWidget.InternalMove)
            self.initiative_list.model().rowsMoved.connect(self.on_initiative_reordered)
            self.initiative_list.pressed.connect(self._initiative_drag_start)
            self.initiative_controls = QHBoxLayout()
            self.add_init_btn = QPushButton("Añadir")
            self.del_init_btn = QPushButton("Eliminar")
            self.next_init_btn = QPushButton("Siguiente turno")
            self.initiative_controls.addWidget(self.add_init_btn)
            self.initiative_controls.addWidget(self.del_init_btn)
            self.initiative_controls.addWidget(self.next_init_btn)
            self.initiative_layout.addLayout(self.initiative_controls)
            self.initiative_layout.addWidget(self.initiative_list)
            self.initiative_tab.setLayout(self.initiative_layout)
            self.tabs.addTab(self.initiative_tab, "Iniciativa")
            self.initiative_data = []  # [{nombre, iniciativa, pv, activo}]
            self.initiative_index = 0
            self.add_init_btn.clicked.connect(self.add_initiative_entry_vtt)
            self.del_init_btn.clicked.connect(self.remove_initiative_entry)
            self.next_init_btn.clicked.connect(self.advance_initiative)
            

            # --- TAB PLANTILLAS ---
            self.templates_tab = QWidget()
            self.templates_layout = QVBoxLayout()
            self.templates_list = QListWidget()
            self.templates_controls = QHBoxLayout()
            self.load_template_btn = QPushButton("Cargar plantilla")
            self.del_template_btn = QPushButton("Eliminar plantilla")
            self.use_template_btn = QPushButton("Crear ficha desde plantilla")
            self.templates_controls.addWidget(self.load_template_btn)
            self.templates_controls.addWidget(self.del_template_btn)
            self.templates_controls.addWidget(self.use_template_btn)
            self.templates_layout.addLayout(self.templates_controls)
            self.templates_layout.addWidget(self.templates_list)
            self.templates_tab.setLayout(self.templates_layout)
            self.tabs.addTab(self.templates_tab, "Plantillas")
            self.templates = []  # [{nombre, campos: [{etiqueta, tipo, clave}]}]
            self.load_template_btn.clicked.connect(self.load_template)
            self.del_template_btn.clicked.connect(self.remove_template)
            self.use_template_btn.clicked.connect(self.use_template)
            

            # --- TAB NOTAS ---
            self.notes_tab = QWidget()
            self.notes_layout = QVBoxLayout()
            self.notes_list = QListWidget()
            self.notes_controls = QHBoxLayout()
            self.add_note_btn = QPushButton("Añadir nota")
            self.edit_note_btn = QPushButton("Editar")
            self.del_note_btn = QPushButton("Eliminar")
            self.notes_controls.addWidget(self.add_note_btn)
            self.notes_controls.addWidget(self.edit_note_btn)
            self.notes_controls.addWidget(self.del_note_btn)
            self.notes_layout.addLayout(self.notes_controls)
            self.notes_layout.addWidget(self.notes_list)
            self.notes_tab.setLayout(self.notes_layout)
            self.tabs.addTab(self.notes_tab, "Notas")
            self.notes = []  # [{titulo, texto, tipo, destinatario, autor}]
            self.add_note_btn.clicked.connect(self.add_note)
            self.edit_note_btn.clicked.connect(self.edit_note)
            self.del_note_btn.clicked.connect(self.remove_note)
            

            # --- TAB MACROS ---
            self.macros_tab = QWidget()
            self.macros_layout = QVBoxLayout()
            self.macros_list = QListWidget()
            self.macros_controls = QHBoxLayout()
            self.add_macro_btn = QPushButton("Añadir macro")
            self.del_macro_btn = QPushButton("Eliminar macro")
            self.run_macro_btn = QPushButton("Ejecutar macro")
            self.macros_controls.addWidget(self.add_macro_btn)
            self.macros_controls.addWidget(self.del_macro_btn)
            self.macros_controls.addWidget(self.run_macro_btn)
            self.macros_layout.addLayout(self.macros_controls)
            self.macros_layout.addWidget(self.macros_list)
            self.macros_tab.setLayout(self.macros_layout)
            self.tabs.addTab(self.macros_tab, "Macros")
            self.add_macro_btn.clicked.connect(self.add_macro)
            self.del_macro_btn.clicked.connect(self.remove_macro)
            self.run_macro_btn.clicked.connect(self.run_macro)
            

            # --- TAB HISTORIAL ---
            self.history_list = QListWidget()
            self.tabs.addTab(self.history_list, "Historial")
            

            # --- GUARDAR/CARGAR CAMPAÑA ---
            self.save_campaign_btn = QPushButton("Guardar campaña")
            self.load_campaign_btn = QPushButton("Cargar campaña")
            self.layout.addWidget(self.save_campaign_btn)
            self.layout.addWidget(self.load_campaign_btn)
            self.save_campaign_btn.clicked.connect(self.save_campaign)
            self.load_campaign_btn.clicked.connect(self.load_campaign)

            
        except Exception as e:
            import traceback
            print("[ERROR en constructor VTTWindow]:", e)
            traceback.print_exc()

# ---
# El siguiente bloque corresponde a la lógica de dibujo del mapa y tokens. Debe estar dentro de un método paintEvent de un widget, por ejemplo MapWidget.
# Si MapWidget no existe como clase, créala como un QWidget.

class MapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_type = 'cuadricula'
        self.grid_size = 50
        self.show_fog = False
        self.fog_mask = None
        self.tokens = {}
        self.zoom = 1.0
        self.pan = QPoint(0, 0)
        self.fog_brush_radius = 40
        # ... otros atributos necesarios ...

    def zoom_in(self):
        self.zoom *= 1.2
        self.update()

    def zoom_out(self):
        self.zoom /= 1.2
        self.update()

    def toggle_grid(self):
        self.grid_type = 'hex' if self.grid_type == 'cuadricula' else 'cuadricula'
        self.update()

    def set_grid_type(self, tipo):
        self.grid_type = tipo
        self.update()

    def set_grid_size(self, size):
        self.grid_size = int(size)
        self.update()

    def toggle_fog(self):
        self.show_fog = not self.show_fog
        self.update()

    def set_fog_mode(self, modo):
        self.fog_mode = modo
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Suponiendo que hay una imagen de fondo llamada self.background
        if hasattr(self, 'background') and self.background:
            scaled = self.background.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(0, 0, scaled)
        else:
            scaled = self
        if self.grid_type == 'cuadricula':
            w, h = scaled.width(), scaled.height()
            for x in range(0, w, self.grid_size):
                painter.drawLine(x, 0, x, h)
            for y in range(0, h, self.grid_size):
                painter.drawLine(0, y, w, y)
        elif self.grid_type == 'hex':
            w, h = scaled.width(), scaled.height()
            size = self.grid_size
            dx = size * 3//2
            dy = int(size * (3**0.5))
            for y in range(0, h+dy, dy):
                shift = (y//dy)%2 * (size*3//4)
                for x in range(-size, w+dx, dx):
                    points = []
                    for i in range(6):
                        angle = 3.14159/3 * i
                        px = x + shift + size * 0.5 + size * 0.5 * (1 + 0.866 * (i%2)) * (1 if i<3 else -1)
                        py = y + size * 0.5 + size * 0.866 * (i-1 if i>0 else 0)
                        points.append(QPoint(int(px), int(py)))
                    painter.drawPolygon(*points)
        # Niebla de guerra
        if self.show_fog and self.fog_mask:
            painter.setOpacity(0.75)
            painter.drawPixmap(0, 0, self.fog_mask.scaled(self.size()))
            painter.setOpacity(1.0)
        # Tokens
        for token_id, token in self.tokens.items():
            tx = int(token['x'] * self.zoom + self.pan.x())
            ty = int(token['y'] * self.zoom + self.pan.y())
            # Imagen
            if token['img']:
                pix = token['img'].scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.drawPixmap(tx-20, ty-20, pix)
            else:
                painter.setBrush(QColor(200, 50, 50, 200))
                painter.setPen(QColor(0,0,0,180))
                painter.drawEllipse(QRect(tx-15, ty-15, 30, 30))
            # Nombre y PV
            painter.setFont(QFont('Segoe UI', 10, QFont.Bold))
            painter.setPen(QColor(255,255,255))
            painter.drawText(tx-40, ty-25, 80, 20, Qt.AlignCenter, f"{token['name']} ({token['pv']})")
            # Estado
            if token['estado']:
                painter.setFont(QFont('Segoe UI', 8))
                painter.setPen(QColor(230,230,80))
                painter.drawText(tx-40, ty+22, 80, 16, Qt.AlignCenter, token['estado'])
        painter.restore()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton or (event.button() == Qt.LeftButton and (event.modifiers() & Qt.ShiftModifier)):
            self.last_pan = event.pos()
        elif self.show_fog and event.button() == Qt.LeftButton and self.fog_mode in ('revelar','ocultar'):
            self.editing_fog = True
            self.edit_fog(event.pos(), self.fog_mode)
        else:
            pos = self.map_to_img(event.pos())
            for token_id, token in self.tokens.items():
                if (QPoint(token['x'], token['y']) - pos).manhattanLength() < 20:
                    self.selected_token = token_id
                    self.offset = pos - QPoint(token['x'], token['y'])
                    if event.type() == event.MouseButtonDblClick:
                        # Permitir edición solo si GM o token no bloqueado
                        if not token.get('bloqueado', False) or self.is_gm:
                            self.edit_token_dialog(token_id)
                    break

    def mouseMoveEvent(self, event):
        if self.last_pan is not None:
            delta = event.pos() - self.last_pan
            self.pan += delta
            self.last_pan = event.pos()
            self.update()
        elif self.editing_fog and self.show_fog:
            self.edit_fog(event.pos(), self.fog_mode)
        elif self.selected_token:
            # Solo GM o token no bloqueado
            token = self.tokens[self.selected_token]
            if not token.get('bloqueado', False) or self.is_gm:
                pos = self.map_to_img(event.pos() - self.offset)
                token['x'], token['y'] = pos.x(), pos.y()
                self.update()

    def mouseReleaseEvent(self, event):
        if self.last_pan is not None:
            self.last_pan = None
        if self.editing_fog:
            self.editing_fog = False
        if self.selected_token:
            token = self.tokens[self.selected_token]
            self.token_moved.emit(self.selected_token, token['x'], token['y'])
            self.selected_token = None

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        factor = 1.2 if angle > 0 else 1/1.2
        self.set_zoom(self.zoom * factor)

    def map_to_img(self, pos):
        # Convierte coordenadas widget a coordenadas de imagen
        x = int((pos.x() - self.pan.x()) / self.zoom)
        y = int((pos.y() - self.pan.y()) / self.zoom)
        return QPoint(x, y)

    def edit_fog(self, pos, mode):
        if not self.fog_mask:
            return
        img_pos = self.map_to_img(pos)
        painter = QPainter(self.fog_mask)
        if mode == 'revelar':
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
        else:
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.setBrush(QColor(0,0,0,220))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(img_pos, self.fog_brush_radius, self.fog_brush_radius)
        painter.end()
        self.update()

# --- Fichas de personaje ---
    
    # Vampiro: La Mascarada
    
    def make_vampiro_sheet(self):
        widget = QWidget()
        layout = QFormLayout()
        fields = {}
        def add_row(label, widget_field):
            layout.addRow(QLabel(label), widget_field)
            fields[label] = widget_field
        add_row("Nombre", QLineEdit())
        add_row("Clan", QLineEdit())
        add_row("Generación", QSpinBox())
        add_row("Sire", QLineEdit())
        add_row("Naturaleza", QLineEdit())
        add_row("Conducta", QLineEdit())
        add_row("Concepto", QLineEdit())
        add_row("Fuerza", QSpinBox())
        add_row("Destreza", QSpinBox())
        add_row("Resistencia", QSpinBox())
        add_row("Carisma", QSpinBox())
        add_row("Manipulación", QSpinBox())
        add_row("Apariencia", QSpinBox())
        add_row("Percepción", QSpinBox())
        add_row("Inteligencia", QSpinBox())
        add_row("Astucia", QSpinBox())
        add_row("Salud", QSpinBox())
        add_row("Fuerza de Voluntad", QSpinBox())
        add_row("Disciplinas", QLineEdit())
        add_row("Notas", QTextEdit())
        # Botones guardar/cargar/compartir
        btns = QHBoxLayout()
        save_btn = QPushButton("Guardar ficha")
        load_btn = QPushButton("Cargar ficha")
        share_btn = QPushButton("Compartir ficha")
        btns.addWidget(save_btn)
        btns.addWidget(load_btn)
        btns.addWidget(share_btn)
        layout.addRow(btns)
        widget.setLayout(layout)
        # Lógica guardar/cargar
        def save_sheet():
            data = {}
            for k, w in fields.items():
                if isinstance(w, QLineEdit):
                    data[k] = w.text()
                elif isinstance(w, QSpinBox):
                    data[k] = w.value()
                elif isinstance(w, QTextEdit):
                    data[k] = w.toPlainText()
            fname, _ = QFileDialog.getSaveFileName(widget, "Guardar ficha", "ficha_vampiro.json", "JSON (*.json)")
            if fname:
                with open(fname, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        def load_sheet():
            fname, _ = QFileDialog.getOpenFileName(widget, "Cargar ficha", "", "JSON (*.json)")
            if fname:
                with open(fname, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for k, w in fields.items():
                    if k in data:
                        if isinstance(w, QLineEdit):
                            w.setText(str(data[k]))
                        elif isinstance(w, QSpinBox):
                            w.setValue(int(data[k]))
                        elif isinstance(w, QTextEdit):
                            w.setPlainText(str(data[k]))
        def share_sheet():
            if self.network:
                data = {}
                for k, w in fields.items():
                    if isinstance(w, QLineEdit):
                        data[k] = w.text()
                    elif isinstance(w, QSpinBox):
                        data[k] = w.value()
                    elif isinstance(w, QTextEdit):
                        data[k] = w.toPlainText()
                send_msg = json.dumps({"type": "share_sheet", "game": "vampiro", "user": self.player_name, "sheet": data}).encode()
                try:
                    self.network.send(send_msg)
                except Exception as e:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(widget, "Error", f"No se pudo compartir: {e}")
        save_btn.clicked.connect(save_sheet)
        load_btn.clicked.connect(load_sheet)
        share_btn.clicked.connect(share_sheet)
        return widget

    # D&D 5e
    def make_dnd_sheet(self):
        widget = QWidget()
        layout = QFormLayout()
        fields = {}
        def add_row(label, widget_field):
            layout.addRow(QLabel(label), widget_field)
            fields[label] = widget_field
        add_row("Nombre", QLineEdit())
        add_row("Clase", QLineEdit())
        add_row("Raza", QLineEdit())
        add_row("Nivel", QSpinBox())
        add_row("Experiencia", QSpinBox())
        add_row("Puntos de Golpe (HP)", QSpinBox())
        add_row("Fuerza", QSpinBox())
        add_row("Destreza", QSpinBox())
        add_row("Constitución", QSpinBox())
        add_row("Inteligencia", QSpinBox())
        add_row("Sabiduría", QSpinBox())
        add_row("Carisma", QSpinBox())
        add_row("CA (Clase de Armadura)", QSpinBox())
        add_row("Iniciativa", QSpinBox())
        add_row("Velocidad", QSpinBox())
        add_row("Notas", QTextEdit())
        # Botones guardar/cargar/compartir
        btns = QHBoxLayout()
        save_btn = QPushButton("Guardar ficha")
        load_btn = QPushButton("Cargar ficha")
        share_btn = QPushButton("Compartir ficha")
        btns.addWidget(save_btn)
        btns.addWidget(load_btn)
        btns.addWidget(share_btn)
        layout.addRow(btns)
        widget.setLayout(layout)
        # Lógica guardar/cargar
        def save_sheet():
            data = {}
            for k, w in fields.items():
                if isinstance(w, QLineEdit):
                    data[k] = w.text()
                elif isinstance(w, QSpinBox):
                    data[k] = w.value()
                elif isinstance(w, QTextEdit):
                    data[k] = w.toPlainText()
            fname, _ = QFileDialog.getSaveFileName(widget, "Guardar ficha", "ficha_dnd.json", "JSON (*.json)")
            if fname:
                with open(fname, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        def load_sheet():
            fname, _ = QFileDialog.getOpenFileName(widget, "Cargar ficha", "", "JSON (*.json)")
            if fname:
                with open(fname, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for k, w in fields.items():
                    if k in data:
                        if isinstance(w, QLineEdit):
                            w.setText(str(data[k]))
                        elif isinstance(w, QSpinBox):
                            w.setValue(int(data[k]))
                        elif isinstance(w, QTextEdit):
                            w.setPlainText(str(data[k]))
        def share_sheet():
            if self.network:
                data = {}
                for k, w in fields.items():
                    if isinstance(w, QLineEdit):
                        data[k] = w.text()
                    elif isinstance(w, QSpinBox):
                        data[k] = w.value()
                    elif isinstance(w, QTextEdit):
                        data[k] = w.toPlainText()
                send_msg = json.dumps({"type": "share_sheet", "game": "dnd", "user": self.player_name, "sheet": data}).encode()
                try:
                    self.network.send(send_msg)
                except Exception as e:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(widget, "Error", f"No se pudo compartir: {e}")
        save_btn.clicked.connect(save_sheet)
        load_btn.clicked.connect(load_sheet)
        share_btn.clicked.connect(share_sheet)
        return widget
