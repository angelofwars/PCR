import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os


class GoogleSheetsLogger:
    def __init__(self, credentials_file='credentials.json'):
        # ID вашей таблицы, который мы взяли из ссылки
        self.sheet_id = '1KiDR31j3wgwoOTvS6IYC4zgoJ-Qiuezaqil8iNzOCuM'
        self.credentials_file = credentials_file
        self.client = None
        self.sheet = None

    def connect(self):
        if not os.path.exists(self.credentials_file):
            return False, f"Ключ {self.credentials_file} не найден в папке проекта!"
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
            self.client = gspread.authorize(creds)
            # Открываем таблицу по ID и берем первый лист
            self.sheet = self.client.open_by_key(self.sheet_id).sheet1
            return True, "Подключено!"
        except Exception as e:
            return False, f"Ошибка подключения: {str(e)}"

    def log_experiment(self, protocol_name, markers, programs, rxn_count, mastermix_vol, amplifier, user="A.N."):
        if not self.sheet:
            success, msg = self.connect()
            if not success:
                return False, msg

        current_date = datetime.now().strftime("%d.%m.%Y %H:%M")

        # Формируем строку, которая запишется в таблицу
        row = [
            current_date,  # A: Дата
            user,  # B: Исполнитель
            protocol_name,  # C: Протокол
            markers,  # D: Маркеры
            programs,  # E: Программы
            rxn_count,  # F: Кол-во rxn
            mastermix_vol,  # G: Потраченный Mastermix (µL)
            amplifier  # H: Амплификатор
        ]

        try:
            self.sheet.append_row(row)
            return True, "☁️ Данные успешно записаны в Google Таблицу!"
        except Exception as e:
            return False, f"Ошибка записи: {str(e)}"