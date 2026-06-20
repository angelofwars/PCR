from fpdf import FPDF
import subprocess
from datetime import datetime
import os


class PDFGenerator:
    @staticmethod
    def create_protocol(rxn, data_rows, mastermix_total, filename="PCR_Protocol.pdf"):
        pdf = FPDF()
        pdf.add_page()

        # Находим стандартный системный шрифт Arial на macOS для поддержки кириллицы
        font_path = "/Library/Fonts/Arial.ttf"
        if not os.path.exists(font_path):
            font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"

        bold_font_path = font_path.replace("Arial.ttf", "Arial Bold.ttf")

        try:
            pdf.add_font("Arial", "", font_path)
            # Добавляем жирный шрифт (если он есть в системе)
            if os.path.exists(bold_font_path):
                pdf.add_font("Arial", "B", bold_font_path)
            else:
                pdf.add_font("Arial", "B", font_path)

            pdf.set_font("Arial", size=12)
        except Exception as e:
            return False, f"Ошибка шрифта: {e}"

        # 1. Шапка документа
        date_str = datetime.now().strftime("%d.%m.%Y")
        pdf.set_font("Arial", "B", 14)
        pdf.cell(100, 10, "ВНИИР им. Н.И. Вавилова", ln=0)

        pdf.set_font("Arial", "", 12)
        pdf.cell(90, 10, f"Date: {date_str}", ln=1, align="R")

        pdf.ln(5)  # Отступ вниз
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"PCR-Setup [Final] 20 µL, {rxn} rxn", ln=1)
        pdf.ln(5)

        # 2. Отрисовка таблицы
        pdf.set_font("Arial", "B", 11)
        col_widths = [70, 40, 40]
        headers = ["Реагент", "На 1 rxn (µL)", f"На {rxn} rxn (µL)"]

        # Заголовки таблицы
        for i in range(3):
            pdf.cell(col_widths[i], 10, headers[i], border=1, align="C")
        pdf.ln()

        # Данные таблицы
        pdf.set_font("Arial", "", 11)
        for row in data_rows:
            pdf.cell(col_widths[0], 10, str(row[0]), border=1)
            pdf.cell(col_widths[1], 10, str(row[1]), border=1, align="C")
            pdf.cell(col_widths[2], 10, str(row[2]), border=1, align="C")
            pdf.ln()

        # Итоговая строка (Мастер-микс)
        pdf.set_font("Arial", "B", 11)
        pdf.set_text_color(34, 139, 34)  # Зеленый цвет для мастер-микса
        pdf.cell(col_widths[0], 10, "Mastermix", border=1)
        pdf.cell(col_widths[1], 10, str(mastermix_total), border=1, align="C")
        pdf.cell(col_widths[2], 10, str(round(mastermix_total * rxn, 1)), border=1, align="C")
        pdf.ln()
        pdf.set_text_color(0, 0, 0)  # Возвращаем черный цвет

        # 3. Подвал с параметрами амплификации
        pdf.ln(15)
        pdf.set_font("Arial", "", 11)
        pdf.cell(60, 8, "ДНК (10 ng/µL):   2.0 µL", ln=1)
        pdf.cell(60, 8, "Конечный объем:   20.0 µL", ln=1)

        pdf.ln(10)
        # Создаем две колонки для записей от руки
        pdf.cell(90, 8, "Праймер 1:  ______________________")
        pdf.cell(90, 8, "Амплификатор:  ___________________", ln=1)
        pdf.cell(90, 8, "Праймер 2:  ______________________")
        pdf.cell(90, 8, "Annaeling Temp.:  ________________", ln=1)
        pdf.cell(90, 8, "Программа:  ______________________")
        pdf.cell(90, 8, "Work Carried Out By:  A.N.", ln=1)

        # Сохранение файла
        pdf.output(filename)

        try:
            # Открываем файл средствами macOS
            subprocess.run(["open", filename])
            return True, f"PDF протокол {filename} создан!"
        except Exception as ex:
            return False, str(ex)