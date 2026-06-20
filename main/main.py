import flet as ft
from config import PCRRecipe
from exporter import PDFGenerator # Изменили ExcelGenerator на PDFGenerator

class PCRApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.recipe = PCRRecipe()  # Подключаем нашу базу

        # Настройки окна
        self.page.title = "ПЦР Калькулятор"
        self.page.window_width = 550
        self.page.window_height = 700
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.horizontal_alignment = "center"

        # Создаем элементы UI
        self.title = ft.Text("🧬 Калькулятор ПЦР", size=24, weight="bold")
        self.rxn_label = ft.Text("Количество реакций: 52", size=18, color="blue")

        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Реагент", weight="bold")),
                ft.DataColumn(ft.Text("На 1 rxn (µL)", weight="bold"), numeric=True),
                ft.DataColumn(ft.Text("Общий объем", weight="bold"), numeric=True),
            ],
            rows=[]
        )

        self.slider = ft.Slider(
            min=1, max=100, value=52, divisions=99, label="{value}",
            on_change=self.on_slider_change
        )

        self.export_btn = ft.ElevatedButton(
            "🖨 Создать PDF протокол",
            icon="picture_as_pdf",
            color="white",
            bgcolor="red",  # Сделали красной, как логотип PDF
            on_click=self.on_export
        )

        # Первая отрисовка
        self.update_table(52)
        self.build_ui()

    def update_table(self, rxn):
        self.table.rows.clear()

        # Получаем данные из класса config.py
        data = self.recipe.calculate(rxn)

        for row in data:
            self.table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(row[0]))),
                    ft.DataCell(ft.Text(str(row[1]))),
                    ft.DataCell(ft.Text(str(row[2])))
                ])
            )

        # Итоговая строка
        self.table.rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("Итого Mastermix", weight="bold", color="green")),
                ft.DataCell(ft.Text(str(self.recipe.mastermix), weight="bold", color="green")),
                ft.DataCell(ft.Text(f"{self.recipe.mastermix * rxn:.1f}", weight="bold", color="green"))
            ])
        )

    def on_slider_change(self, e):
        rxn = int(e.control.value)
        self.rxn_label.value = f"Количество реакций: {rxn}"
        self.update_table(rxn)
        self.page.update()

    def on_export(self, e):
        rxn = int(self.slider.value)
        data = self.recipe.calculate(rxn)

        # Теперь обращаемся к PDFGenerator
        success, msg = PDFGenerator.create_protocol(rxn, data, self.recipe.mastermix)

        color = "green" if success else "red"
        self.page.show_snack_bar(ft.SnackBar(ft.Text(msg), bgcolor=color, open=True))

    def build_ui(self):
        self.page.add(
            self.title, ft.Container(height=10),
            self.rxn_label, self.slider, self.export_btn,
            ft.Divider(), self.table
        )


# Точка входа в программу
def main(page: ft.Page):
    PCRApp(page)


ft.app(target=main)