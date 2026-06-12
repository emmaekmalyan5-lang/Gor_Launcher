import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QLineEdit, 
                             QPushButton, QHBoxLayout, QLabel, QFileDialog, 
                             QCheckBox, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class GameEditor(QDialog):
    def __init__(self, parent=None, game_data=None, groups=None, current_group=None):
        super().__init__(parent)
        self.data_file = "games_data.json"
        self.setWindowTitle("Настройка игры GOR")
        self.setFixedWidth(600)
        
        # Загружаем структуру данных
        self.all_data = self.load_json()
        self.groups = groups or list(self.all_data.get("groups", {}).keys())
        
        # Сохраняем оригинальное имя для проверки при редактировании
        self.original_name = game_data['name'] if game_data else None
        
        self.game_data = game_data or {
            "name": "", "path": "", "icon": "", 
            "group": "Без группы", "args": "", 
            "playtime_seconds": 0, "favorite": False
        }
        self.current_group = current_group or "Без группы"
        
        self.init_ui()

    def load_json(self):
        if not os.path.exists(self.data_file):
            default_data = {"groups": {}, "standalone": [], "history": []}
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=4)
            return default_data
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_json(self, data):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setStyleSheet("background-color: #1e1e1e; color: #e1e1e1; font-size: 14px;")

        # --- НАЗВАНИЕ ---
        layout.addWidget(QLabel("Название мода/игры:"))
        self.name_edit = QLineEdit(self.game_data['name'])
        self.name_edit.setStyleSheet("background-color: #2d2d2d; border: 1px solid #3e3e42; padding: 8px; border-radius: 4px;")
        layout.addWidget(self.name_edit)

        # --- ПУТЬ К ФАЙЛУ ---
        layout.addWidget(QLabel("Файл запуска (любой тип файла):"))
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(self.game_data['path'])
        self.path_edit.setStyleSheet("background-color: #2d2d2d; border: 1px solid #3e3e42; padding: 8px; border-radius: 4px;")
        self.path_btn = QPushButton("📁 Обзор")
        self.path_btn.clicked.connect(self.select_path)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.path_btn)
        layout.addLayout(path_layout)

        # --- АРГУМЕНТЫ ---
        layout.addWidget(QLabel("Аргументы запуска:"))
        self.args_edit = QLineEdit(self.game_data.get('args', ''))
        self.args_edit.setPlaceholderText("-game folder_name")
        self.args_edit.setStyleSheet("background-color: #2d2d2d; border: 1px solid #007acc; padding: 8px; border-radius: 4px;")
        layout.addWidget(self.args_edit)

        # --- ОБЛОЖКА ---
        layout.addWidget(QLabel("Обложка (PNG/JPG):"))
        icon_layout = QHBoxLayout()
        self.icon_edit = QLineEdit(self.game_data['icon'])
        self.icon_edit.setStyleSheet("background-color: #2d2d2d; border: 1px solid #3e3e42; padding: 8px; border-radius: 4px;")
        self.icon_btn = QPushButton("🖼️ Фото")
        self.icon_btn.clicked.connect(self.select_icon)
        icon_layout.addWidget(self.icon_edit)
        icon_layout.addWidget(self.icon_btn)
        layout.addLayout(icon_layout)

        preview_box = QHBoxLayout()
        self.preview_label = QLabel("Нет фото")
        self.preview_label.setFixedSize(200, 260)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 2px dashed #444; background: #121212; border-radius: 10px;")
        
        self.fav_check = QCheckBox("⭐️ ДОБАВИТЬ В ИЗБРАННОЕ")
        self.fav_check.setChecked(self.game_data.get('favorite', False))
        self.fav_check.setStyleSheet("font-weight: bold; color: #ffcc00; margin-left: 10px;")
        
        preview_box.addWidget(self.preview_label)
        preview_box.addWidget(self.fav_check)
        preview_box.addStretch()
        layout.addLayout(preview_box)
        
        if self.game_data['icon']: self.update_preview()

        # --- ВЫБОР ГРУППЫ ---
        layout.addWidget(QLabel("Назначить в группу:"))
        self.group_box = QComboBox()
        self.group_box.addItem("Без группы")
        self.group_box.addItems(self.groups)
        self.group_box.setCurrentText(self.current_group)
        self.group_box.setStyleSheet("background-color: #2d2d2d; color: white; padding: 8px; border-radius: 4px;")
        layout.addWidget(self.group_box)

        # --- КНОПКИ ---
        btns = QHBoxLayout()
        save_btn = QPushButton("СОХРАНИТЬ")
        save_btn.setStyleSheet("background-color: #0e639c; font-weight: bold; padding: 15px; border-radius: 8px; margin-top: 10px;")
        save_btn.clicked.connect(self.save_and_accept)
        cancel_btn = QPushButton("ОТМЕНА")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def save_and_accept(self):
        # 1. Удаляем старую версию, если она была (ищем по оригинальному имени)
        if self.original_name:
            # Ищем в standalone
            for i, g in enumerate(self.all_data["standalone"]):
                if g["name"] == self.original_name:
                    self.all_data["standalone"].pop(i); break
            # Ищем в группах
            for g_name in self.all_data["groups"]:
                for i, g in enumerate(self.all_data["groups"][g_name]):
                    if g["name"] == self.original_name:
                        self.all_data["groups"][g_name].pop(i); break

        # 2. Собираем новые данные
        new_data = self.get_data()
        target_group = new_data.pop('group')
        
        # 3. Добавляем в нужную категорию
        if target_group == "Без группы":
            self.all_data["standalone"].append(new_data)
        else:
            if target_group not in self.all_data["groups"]:
                self.all_data["groups"][target_group] = []
            self.all_data["groups"][target_group].append(new_data)
        
        self.save_json(self.all_data)
        self.accept()

    def select_path(self):
        # Разрешаем выбор любого файла, чтобы универсальный лаунчер мог открыть всё
        file, _ = QFileDialog.getOpenFileName(self, "Выбрать файл запуска", "", "Все файлы (*.*)")
        if file: self.path_edit.setText(file)

    def select_icon(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выбрать обложку", "", "Images (*.png *.jpg *.jpeg)")
        if file: 
            self.icon_edit.setText(file)
            self.update_preview()

    def update_preview(self):
        path = self.icon_edit.text()
        if os.path.exists(path):
            pix = QPixmap(path)
            self.preview_label.setPixmap(pix.scaled(200, 260, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.preview_label.setText("Файл не найден")

    def get_data(self):
        data = {
            "name": self.name_edit.text(), 
            "path": self.path_edit.text(), 
            "icon": self.icon_edit.text(), 
            "group": self.group_box.currentText(),
            "args": self.args_edit.text(),
            "favorite": self.fav_check.isChecked()
        }
        data['playtime_seconds'] = self.game_data.get('playtime_seconds', 0)
        return data

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = GameEditor()
    editor.show()
    sys.exit(app.exec())