import sys
import json
import os
import subprocess
import time
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLineEdit, QLabel, QMessageBox, QHBoxLayout,
                             QGroupBox)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class SunshineControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sunshine Control Center")
        self.setFixedSize(450, 520)
        
        self.base_dir = os.getcwd()
        self.sunshine_dir = os.path.join(self.base_dir, "Sunshine")
        self.assets_dir = os.path.join(self.sunshine_dir, "assets")
        self.apps_json_path = os.path.join(self.sunshine_dir, "config", "apps.json")
        self.games_data_path = os.path.join(self.base_dir, "games_data.json")

        self.init_ui()

    def init_ui(self):
        # --- СТИЛИ ОСТАЛИСЬ ПРЕЖНИМИ ДЛЯ СОХРАНЕНИЯ ВИЗУАЛА ---
        style_sheet = """
            QMainWindow { background-color: #0a0a0a; }
            #CentralWidget { background-color: #0a0a0a; }
            QLabel { color: #f0f0f0; font-size: 14px; font-weight: bold; background: transparent; }
            QGroupBox { 
                color: #007acc; font-size: 16px; font-weight: bold; 
                border: 1px solid #333; border-radius: 12px; 
                margin-top: 18px; padding: 20px 10px 10px 10px; background-color: #141414;
            }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; background-color: #0a0a0a; }
            QLineEdit { background: #1a1a1a; border-radius: 8px; padding: 8px; border: 1px solid #333; color: white; font-size: 14px; }
            QLineEdit:focus { border: 1px solid #007acc; background: #222; }
            QPushButton { background-color: #1a1a1a; border-radius: 8px; padding: 10px 20px; color: white; border: 1px solid #333; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background-color: #007acc; border: 1px solid #005f9e; }
            QPushButton:pressed { background-color: #005f9e; }
            QPushButton#StopBtn { background-color: #550000; border: 1px solid #8b0000; }
            QPushButton#StopBtn:hover { background-color: #8b0000; }
        """
        self.setStyleSheet(style_sheet)

        central = QWidget()
        central.setObjectName("CentralWidget")
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title = QLabel("SUNSHINE CONTROL")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # --- БЛОК 1: СИНХРОНИЗАЦИЯ И УПРАВЛЕНИЕ ---
        sync_group = QGroupBox("🎮 Управление")
        sync_layout = QVBoxLayout(sync_group)
        
        self.btn_sync = QPushButton("🔄 ЗОПУСК И СИНХРОНИЗИРОВАТЬ SUNSHINE")
        self.btn_sync.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sync.clicked.connect(self.sync_games)
        sync_layout.addWidget(self.btn_sync)
        
        self.btn_stop = QPushButton("🛑 ПРИНУДИТЕЛЬНО ОСТАНОВИТЬ SUNSHINE")
        self.btn_stop.setObjectName("StopBtn")
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.clicked.connect(self.stop_sunshine)
        sync_layout.addWidget(self.btn_stop)
        
        main_layout.addWidget(sync_group)

        # --- БЛОК 2: АВТОРИЗАЦИЯ ---
        auth_group = QGroupBox("🔐 Авторизация")
        auth_layout = QVBoxLayout(auth_group)
        auth_layout.setSpacing(8)

        auth_layout.addWidget(QLabel("Новый логин:"))
        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("Введите логин...")
        auth_layout.addWidget(self.user_edit)

        auth_layout.addWidget(QLabel("Новый пароль:"))
        self.pass_edit = QLineEdit()
        self.pass_edit.setPlaceholderText("Введите пароль...")
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        auth_layout.addWidget(self.pass_edit)

        self.btn_creds = QPushButton("СОХРАНИТЬ ДАННЫЕ")
        self.btn_creds.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_creds.clicked.connect(self.apply_creds)
        auth_layout.addWidget(self.btn_creds)

        main_layout.addWidget(auth_group)
        self.setCentralWidget(central)

    def sync_games(self):
        if not os.path.exists(self.games_data_path):
            QMessageBox.critical(self, "Ошибка", "games_data.json не найден!")
            return
        with open(self.games_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_games = data.get("standalone", [])
        for grp in data.get("groups", {}).values():
            all_games.extend(grp)
        os.makedirs(self.assets_dir, exist_ok=True)
        sunshine_apps = []
        if os.path.exists(self.apps_json_path):
            try:
                with open(self.apps_json_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    for app in existing_data.get("apps", []):
                        if app.get("name") in ["Desktop", "Steam Big Picture"]:
                            sunshine_apps.append(app)
            except Exception as e: print(f"Ошибка чтения apps.json: {e}")
        for g in all_games:
            raw_icon = g.get("icon", "")
            final_icon_path = ""
            if raw_icon and os.path.exists(raw_icon):
                if not raw_icon.lower().endswith('.png'):
                    try:
                        safe_name = "".join([c for c in g["name"] if c.isalnum() or c in (' ', '_', '-')]).strip()
                        new_icon_path = os.path.join(self.assets_dir, f"{safe_name}.png")
                        pixmap = QPixmap(raw_icon)
                        if not pixmap.isNull():
                            pixmap.save(new_icon_path, "PNG")
                            final_icon_path = new_icon_path
                        else: final_icon_path = raw_icon
                    except Exception as e: print(f"Ошибка конвертации: {e}"); final_icon_path = raw_icon
                else:
                    try:
                        filename = os.path.basename(raw_icon)
                        dest_path = os.path.join(self.assets_dir, filename)
                        shutil.copy2(raw_icon, dest_path)
                        final_icon_path = dest_path
                    except Exception as e: print(f"Ошибка копирования: {e}"); final_icon_path = raw_icon
                if final_icon_path: final_icon_path = os.path.normpath(final_icon_path).replace("\\", "/")
            app_entry = {
                "name": g["name"],
                "cmd": os.path.normpath(g["path"]).replace("\\", "/"),
                "working-dir": os.path.normpath(os.path.dirname(g["path"])).replace("\\", "/"),
                "auto-detach": True,
                "wait-all": True,
                "image-path": final_icon_path
            }
            sunshine_apps.append(app_entry)
        os.makedirs(os.path.dirname(self.apps_json_path), exist_ok=True)
        with open(self.apps_json_path, 'w', encoding='utf-8') as f:
            json.dump({"env": {}, "apps": sunshine_apps}, f, indent=4, ensure_ascii=False)
        
        # Перезапуск после успешной синхронизации
        self.restart_sunshine()
        QMessageBox.information(self, "Успех", "Конфигурация обновлена и Sunshine перезапущен!")

    def stop_sunshine(self):
        os.system("taskkill /f /im sunshine.exe")
        QMessageBox.information(self, "Статус", "Процесс Sunshine завершен.")

    def apply_creds(self):
        user = self.user_edit.text()
        pwd = self.pass_edit.text()
        if not user or not pwd: return
        os.system("taskkill /f /im sunshine.exe")
        time.sleep(1.5)
        exe = os.path.join(self.sunshine_dir, "sunshine.exe")
        subprocess.run([exe, "--creds", user, pwd], cwd=self.sunshine_dir)
        subprocess.Popen([exe], cwd=self.sunshine_dir)
        QMessageBox.information(self, "Готово", "Данные авторизации применены и процесс запущен.")

    def restart_sunshine(self):
        os.system("taskkill /f /im sunshine.exe")
        time.sleep(1.5)
        exe = os.path.join(self.sunshine_dir, "sunshine.exe")
        subprocess.Popen([exe], cwd=self.sunshine_dir)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ex = SunshineControlApp()
    ex.show()
    sys.exit(app.exec())