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

    def add_tab(self, nombre):
        tab = QWidget()
        tab_layout = QVBoxLayout()
        if nombre == "Mapa":
            tab_layout.addWidget(QLabel("Aquí irá el mapa (imagen, grid, tokens, etc.)", alignment=Qt.AlignCenter))
        elif nombre == "Chat":
            from PyQt5.QtWidgets import QListWidget, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QMessageBox
            self.chat_list = QListWidget()
            chat_input_layout = QHBoxLayout()
            self.chat_input = QLineEdit()
            self.chat_send = QPushButton("Enviar")
            chat_input_layout.addWidget(self.chat_input)
            chat_input_layout.addWidget(self.chat_send)
            tab_layout.addWidget(self.chat_list)
            tab_layout.addLayout(chat_input_layout)
            btns = QHBoxLayout()
            btn_save = QPushButton("Guardar chat")
            btn_load = QPushButton("Cargar chat")
            btns.addWidget(btn_save)
            btns.addWidget(btn_load)
            tab_layout.addLayout(btns)
            self.chat_send.clicked.connect(lambda: self.chat_list.addItem(self.chat_input.text()) or self.chat_input.clear())
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
        elif nombre == "Iniciativa":
            from PyQt5.QtWidgets import QListWidget, QPushButton, QHBoxLayout, QInputDialog, QMessageBox
            self.init_list = QListWidget()
            btn_add = QPushButton("Agregar")
            btn_del = QPushButton("Eliminar")
            btn_reset = QPushButton("Resetear")
            btn_next = QPushButton("Avanzar turno")
            btns = QHBoxLayout(); btns.addWidget(btn_add); btns.addWidget(btn_del); btns.addWidget(btn_reset); btns.addWidget(btn_next)
            tab_layout.addWidget(self.init_list)
            tab_layout.addLayout(btns)
            def add_initiative():
                text, ok = QInputDialog.getText(tab, "Agregar a iniciativa", "Nombre e iniciativa (ej: Gandalf 17):")
                if ok and text.strip():
                    try:
                        name, ini = text.rsplit(' ', 1)
                        ini = int(ini)
                        self.init_list.addItem(f"{name.strip()} [{ini}]")
                        sort_initiative()
                    except Exception:
                        QMessageBox.warning(tab, "Error", "Formato inválido. Usa: Nombre 17")
            def del_initiative():
                row = self.init_list.currentRow()
                if row >= 0:
                    self.init_list.takeItem(row)
            def reset_initiative():
                self.init_list.clear()
            def sort_initiative():
                items = [self.init_list.item(i).text() for i in range(self.init_list.count())]
                def extract_ini(txt):
                    try:
                        return int(txt.split('[')[-1].rstrip(']'))
                    except: return 0
                items.sort(key=extract_ini, reverse=True)
                self.init_list.clear()
                for it in items:
                    self.init_list.addItem(it)
            def next_turn():
                if self.init_list.count() > 1:
                    first = self.init_list.takeItem(0)
                    self.init_list.addItem(first)
            btn_add.clicked.connect(add_initiative)
            btn_del.clicked.connect(del_initiative)
            btn_reset.clicked.connect(reset_initiative)
            btn_next.clicked.connect(next_turn)
        elif nombre == "Plantillas":
            from PyQt5.QtWidgets import QListWidget, QPushButton, QHBoxLayout, QInputDialog, QFileDialog, QMessageBox
            import json
            self.templates_list = QListWidget()
            btn_add = QPushButton("Agregar")
            btn_del = QPushButton("Eliminar")
            btn_use = QPushButton("Usar")
            btn_save = QPushButton("Guardar")
            btn_load = QPushButton("Cargar")
            btns = QHBoxLayout(); btns.addWidget(btn_add); btns.addWidget(btn_del); btns.addWidget(btn_use); btns.addWidget(btn_save); btns.addWidget(btn_load)
            tab_layout.addWidget(self.templates_list)
            tab_layout.addLayout(btns)
            def add_template():
                dlg = QInputDialog(tab)
                dlg.setWindowTitle("Agregar plantilla")
                dlg.setLabelText("Nombre, Clase, Nivel (ej: Legolas,Ranger,7):")
                if dlg.exec_():
                    text = dlg.textValue()
                    parts = [p.strip() for p in text.split(',')]
                    if len(parts) == 3 and parts[2].isdigit():
                        nombre, clase, nivel = parts
                        self.templates_list.addItem(json.dumps({'nombre': nombre, 'clase': clase, 'nivel': int(nivel)}, ensure_ascii=False))
                    else:
                        QMessageBox.warning(tab, "Error", "Formato inválido. Usa: Nombre,Clase,Nivel")
            def del_template():
                row = self.templates_list.currentRow()
                if row >= 0:
                    self.templates_list.takeItem(row)
            def use_template():
                item = self.templates_list.currentItem()
                if item and hasattr(self, 'char_name'):
                    try:
                        data = json.loads(item.text())
                        self.char_name.setText(data.get('nombre', ''))
                        self.char_class.setText(data.get('clase', ''))
                        self.char_level.setText(str(data.get('nivel', '')))
                        QMessageBox.information(tab, "Plantilla usada", "Ficha rellenada con la plantilla seleccionada.")
                    except Exception as e:
                        QMessageBox.critical(tab, "Error", f"No se pudo usar la plantilla: {e}")
            def save_templates():
                path, _ = QFileDialog.getSaveFileName(tab, "Guardar plantillas", "", "Plantillas (*.json)")
                if path:
                    try:
                        data = [json.loads(self.templates_list.item(i).text()) for i in range(self.templates_list.count())]
                        with open(path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        QMessageBox.information(tab, "Plantillas guardadas", f"Plantillas guardadas en {path}")
                    except Exception as e:
                        QMessageBox.critical(tab, "Error", f"No se pudo guardar las plantillas: {e}")
            def load_templates():
                path, _ = QFileDialog.getOpenFileName(tab, "Cargar plantillas", "", "Plantillas (*.json)")
                if path:
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        self.templates_list.clear()
                        for tpl in data:
                            self.templates_list.addItem(json.dumps(tpl, ensure_ascii=False))
                        QMessageBox.information(tab, "Plantillas cargadas", f"Plantillas cargadas de {path}")
                    except Exception as e:
                        QMessageBox.critical(tab, "Error", f"No se pudo cargar las plantillas: {e}")
            btn_add.clicked.connect(add_template)
            btn_del.clicked.connect(del_template)
            btn_use.clicked.connect(use_template)
            btn_save.clicked.connect(save_templates)
            btn_load.clicked.connect(load_templates)
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
        elif nombre == "Historial":
            from PyQt5.QtWidgets import QListWidget
            self.history_list = QListWidget()
            tab_layout.addWidget(self.history_list)
        else:
            tab_layout.addWidget(QLabel(f"Aquí va el contenido de {nombre}"))
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
