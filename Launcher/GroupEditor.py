import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt

class GroupEditor(QDialog):
    # Добавили аргумент old_name=None, чтобы редактор понимал режим работы
    def __init__(self, parent=None, old_name=None):
        super().__init__(parent)
        self.old_name = old_name
        self.data_file = "games_data.json"
        
        # Определяем режим работы и заголовок
        if self.old_name:
            self.setWindowTitle("Редактировать группу")
        else:
            self.setWindowTitle("Создать группу")
            
        self.setFixedWidth(400)
        
        # Применяем темный стиль для всего окна
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; }
            QLabel { color: #e1e1e1; font-size: 15px; font-weight: bold; }
            QLineEdit { 
                background-color: #2d2d2d; border: 1px solid #3e3e42; 
                padding: 10px; border-radius: 6px; color: white; font-size: 14px; 
            }
            QPushButton { 
                background-color: #0e639c; color: white; border: none; 
                padding: 12px; border-radius: 6px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #1177bb; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Заголовок
        self.lbl = QLabel("Введите название группы:")
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("напишите название группы")
        
        # Если редактируем - вставляем текущее имя
        if self.old_name:
            self.name_edit.setText(self.old_name)
            
        layout.addWidget(self.name_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("СОХРАНИТЬ")
        self.save_btn.clicked.connect(self.save_group)
        cancel_btn = QPushButton("ОТМЕНА")
        cancel_btn.setStyleSheet("background-color: #444;")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_group(self):
        name = self.name_edit.text().strip()
        if not name: 
            QMessageBox.warning(self, "Ошибка", "Имя группы не может быть пустым!")
            return

        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except:
                    data = {"groups": {}, "standalone": [], "history": []}
        else:
            data = {"groups": {}, "standalone": [], "history": []}

        # Логика сохранения
        if self.old_name:
            # Режим редактирования
            if name != self.old_name:
                if name in data["groups"]:
                    QMessageBox.warning(self, "Ошибка", "Группа с таким именем уже существует!")
                    return
                # Переносим данные из старого ключа в новый
                data["groups"][name] = data["groups"].pop(self.old_name)
            # Если имя не изменилось, ничего делать не нужно, просто сохраняем текущее
        else:
            # Режим создания
            if name in data["groups"]:
                QMessageBox.warning(self, "Ошибка", "Такая группа уже существует!")
                return
            data["groups"][name] = []

        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = GroupEditor()
    editor.show()
    sys.exit(app.exec())