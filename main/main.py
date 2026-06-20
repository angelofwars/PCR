import flet as ft

def main(page: ft.Page):
    # Настройки окна
    page.title = "ПЦР Калькулятор"
    page.window_width = 550
    page.window_height = 650
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = "center"

    # Базовые объемы на 1 реакцию
    vol_buffer = 2.0
    vol_mgcl2 = 2.0
    vol_dntps = 0.6
    vol_primer_f = 0.1
    vol_primer_r = 0.1
    vol_h2o = 13.05
    vol_taq = 0.15
    vol_mastermix = 18.0

    # Элементы интерфейса (используем простые названия цветов)
    title = ft.Text("🧬 Калькулятор ПЦР-смеси", size=24, weight="bold")
    rxn_label = ft.Text("Количество реакций: 52", size=18, color="blue")

    # Создаем пустую таблицу с заголовками колонок
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Реагент", weight="bold")),
            ft.DataColumn(ft.Text("На 1 rxn (µL)", weight="bold"), numeric=True),
            ft.DataColumn(ft.Text("Общий объем (µL)", weight="bold"), numeric=True),
        ],
        rows=[]
    )

    # Функция, которая генерирует строки таблицы
    def update_table(rxn):
        table.rows = [
            ft.DataRow(cells=[ft.DataCell(ft.Text("10x-буфер синтол")), ft.DataCell(ft.Text(f"{vol_buffer}")), ft.DataCell(ft.Text(f"{vol_buffer * rxn:.1f}"))]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("MgCl2 25 mM")), ft.DataCell(ft.Text(f"{vol_mgcl2}")), ft.DataCell(ft.Text(f"{vol_mgcl2 * rxn:.1f}"))]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("10mM dNTPs (Евроген)")), ft.DataCell(ft.Text(f"{vol_dntps}")), ft.DataCell(ft.Text(f"{vol_dntps * rxn:.1f}"))]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("Праймер_F (100 µM)")), ft.DataCell(ft.Text(f"{vol_primer_f}")), ft.DataCell(ft.Text(f"{vol_primer_f * rxn:.1f}"))]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("Праймер_R (100 µM)")), ft.DataCell(ft.Text(f"{vol_primer_r}")), ft.DataCell(ft.Text(f"{vol_primer_r * rxn:.1f}"))]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("H2O")), ft.DataCell(ft.Text(f"{vol_h2o}")), ft.DataCell(ft.Text(f"{vol_h2o * rxn:.1f}"))]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("HS-Taq-Полимераза")), ft.DataCell(ft.Text(f"{vol_taq}")), ft.DataCell(ft.Text(f"{vol_taq * rxn:.2f}"))]),
            # Выделяем итоговую строку зеленым цветом (color="green")
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("Итого Mastermix", weight="bold", color="green")),
                ft.DataCell(ft.Text(f"{vol_mastermix}", weight="bold", color="green")),
                ft.DataCell(ft.Text(f"{vol_mastermix * rxn:.1f}", weight="bold", color="green"))
            ]),
        ]

    # Заполняем таблицу стартовыми значениями
    update_table(52)

    # Функция для ползунка
    def slider_changed(e):
        rxn_count = int(e.control.value)
        rxn_label.value = f"Количество реакций: {rxn_count}"
        update_table(rxn_count)
        page.update()

    slider = ft.Slider(
        min=1, max=100, value=52, divisions=99, label="{value}", on_change=slider_changed
    )

    # Собираем все элементы на странице
    page.add(
        title,
        ft.Container(height=10),
        rxn_label,
        slider,
        ft.Divider(),
        table
    )

# Запуск приложения
ft.app(target=main)