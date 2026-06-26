from fpdf import FPDF
import subprocess
from datetime import datetime
import os
import platform


class PDFGenerator:
    @staticmethod
    def create_protocol(rxn, data_rows, recipe, blocks_data, markers_list, programs_list, extra_rxn, all_amplifiers,
                        selected_amplifiers=None, filename="PCR_Protocol.pdf", auto_print=False):
        if selected_amplifiers is None:
            selected_amplifiers = []

        pdf = FPDF()
        pdf.add_page()

        font_path = "/Library/Fonts/Arial.ttf"
        if not os.path.exists(font_path):
            font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
        bold_font_path = font_path.replace("Arial.ttf", "Arial Bold.ttf")

        try:
            pdf.add_font("Arial", "", font_path)
            if os.path.exists(bold_font_path):
                pdf.add_font("Arial", "B", bold_font_path)
            else:
                pdf.add_font("Arial", "B", font_path)
            pdf.set_font("Arial", size=10)
        except Exception as e:
            return False, f"Ошибка шрифта: {e}"

        # 1. Шапка
        date_str = datetime.now().strftime("%d.%m.%y")
        pdf.set_font("Arial", "B", 10)
        pdf.cell(50, 6, "ВНИИР им. Н.И. Вавилова", border=1, align="C")
        pdf.cell(20, 6, "Date:", border=1, align="C")
        pdf.cell(30, 6, date_str, border=1, align="C")
        pdf.ln(8)

        # 2. Блоки
        pdf.set_font("Arial", "", 10)
        for block in blocks_data:
            if block['name'] or block['count'] > 0:
                pdf.cell(20, 6, "Блок:", border=1)
                pdf.cell(50, 6, block['name'], border=1, align="C")
                pdf.set_fill_color(255, 255, 153)
                pdf.cell(20, 6, str(block['count']) if block['count'] > 0 else "", border=1, align="C", fill=True)
                pdf.ln()

        pdf.cell(20, 6, "Доп-но:", border=1)
        pdf.cell(50, 6, "", border=1)
        pdf.set_fill_color(255, 255, 153)
        pdf.cell(20, 6, str(extra_rxn), border=1, align="C", fill=True)
        pdf.ln(8)

        # 3. PCR Setup
        pdf.set_font("Arial", "B", 11)
        total_vol = round(recipe.mastermix + 2.0, 1)

        pdf.cell(40, 6, "PCR-Setup [Final]", border=1, align="C")
        pdf.cell(30, 6, f"{total_vol} µL", border=1, align="C")
        pdf.cell(20, 6, str(rxn), border=1, align="C")
        pdf.cell(15, 6, "rxn", border=1, align="C")
        pdf.ln(8)

        # 4. Table
        col_widths = [60, 25, 30]
        pdf.set_font("Arial", "B", 10)
        for row in data_rows:
            pdf.cell(col_widths[0], 6, str(row[0]), border=1, align="R")
            pdf.cell(col_widths[1], 6, str(row[1]) + " µL", border=1, align="C")
            pdf.cell(col_widths[2], 6, str(row[2]) + " µL", border=1, align="C")
            pdf.ln()

        # Mastermix
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(220, 255, 220)
        pdf.cell(col_widths[0], 7, "Mastermix", border=1, align="R", fill=True)
        pdf.cell(col_widths[1], 7, f"{recipe.mastermix} µL", border=1, align="C", fill=True)
        pdf.cell(col_widths[2], 7, f"{round(recipe.mastermix * rxn, 1)} µL", border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_font("Arial", "", 10)
        pdf.cell(col_widths[0], 6, "ДНК (10 ng/µL)", border=1, align="R")
        pdf.cell(col_widths[1], 6, "2.0 µL", border=1, align="C")
        pdf.cell(col_widths[2], 6, "", border=1)
        pdf.ln()
        pdf.set_font("Arial", "B", 10)
        pdf.cell(col_widths[0], 6, "Конечный объем", border=1, align="R")
        pdf.cell(col_widths[1], 6, f"{total_vol} µL", border=1, align="C")
        pdf.cell(col_widths[2], 6, "", border=1)
        pdf.ln(10)

        # 5. Подвал
        y_start = pdf.get_y()

        # --- ЛЕВАЯ КОЛОНКА ---
        pdf.set_font("Arial", "", 10)
        pdf.cell(25, 6, "Праймер 1:", border=1)
        pdf.cell(55, 6, getattr(recipe, 'primer1_name', ''), border=1, align="C")
        pdf.ln()
        pdf.cell(25, 6, "Праймер 2:", border=1)
        pdf.cell(55, 6, getattr(recipe, 'primer2_name', ''), border=1, align="C")
        pdf.ln()

        # Если есть 3-й праймер, выводим его
        p3_name = getattr(recipe, 'primer3_name', '')
        if p3_name:
            pdf.cell(25, 6, "Праймер 3:", border=1)
            pdf.cell(55, 6, p3_name, border=1, align="C")
            pdf.ln()

        pdf.cell(25, 6, "Ann. Temp:", border=1)
        pdf.cell(55, 6, getattr(recipe, 'temp', ''), border=1, align="C")
        pdf.ln()

        if markers_list:
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(80, 6, "Используемые Маркеры:", border=1, align="C", fill=True)
            pdf.ln()
            for m in markers_list:
                pdf.set_text_color(0, 0, 200)
                pdf.cell(80, 6, m, border=1, align="C")
                pdf.set_text_color(0, 0, 0)
                pdf.ln()

        pdf.ln(2)
        pdf.cell(25, 6, "Remarks:", border=1)
        pdf.cell(55, 15, "", border=1)
        pdf.ln(17)
        pdf.cell(40, 6, "Work Carried Out By:", border=1)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(40, 6, "A.N.", border=1, align="C")

        # --- ПРАВАЯ КОЛОНКА ---
        pdf.set_y(y_start)
        pdf.set_font("Arial", "", 10)

        if programs_list:
            pdf.set_x(100)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(73, 6, "Программы амплификации:", border=1, align="C", fill=True)
            pdf.ln()
            for p in programs_list:
                pdf.set_x(100)
                pdf.set_font("Arial", "B", 10)
                pdf.cell(73, 6, p, border=1, align="C")
                pdf.set_font("Arial", "", 10)
                pdf.ln()

        pdf.ln(2)

        for amp in all_amplifiers:
            pdf.set_x(100)
            pdf.cell(30, 6, "Амплификатор:", border=1)

            checkmark = "X" if amp in selected_amplifiers else ""
            pdf.set_font("Arial", "B", 10)
            pdf.cell(8, 6, checkmark, border=1, align="C")

            pdf.set_font("Arial", "", 10)
            pdf.cell(35, 6, amp, border=1)
            pdf.ln()

        pdf.output(filename)

        try:
            current_os = platform.system()
            if auto_print:
                if current_os == "Windows":
                    os.startfile(filename, "print")
                    return True, "Windows: Отправлено на принтер!"
                elif current_os == "Darwin":
                    import time
                    abs_path = os.path.abspath(filename)
                    subprocess.run(["open", "-a", "Preview", abs_path])
                    time.sleep(0.5)
                    apple_script = '''
                    tell application "Preview" to activate
                    tell application "System Events"
                        tell process "Preview"
                            keystroke "p" using command down
                        end tell
                    end tell
                    '''
                    subprocess.run(["osascript", "-e", apple_script])
                    return True, "macOS: Открыто диалоговое окно печати!"
                else:
                    subprocess.run(["xdg-open", filename])
                    return True, "Linux: Файл открыт"
            else:
                if current_os == "Windows":
                    os.startfile(filename)
                elif current_os == "Darwin":
                    subprocess.run(["open", filename])
                else:
                    subprocess.run(["xdg-open", filename])
                return True, "PDF протокол открыт для просмотра!"
        except Exception as ex:
            return False, f"Ошибка ОС: {str(ex)}"