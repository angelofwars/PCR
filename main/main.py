import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import flet as ft
from config import ProtocolDatabase, SettingsManager
from exporter import PDFGenerator
from sheets_exporter import GoogleSheetsLogger


class PCRApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = ProtocolDatabase()
        self.settings = SettingsManager()
        self.google_logger = GoogleSheetsLogger()
        self.current_recipe = self.db.get_recipe(self.db.get_all_names()[0])

        self.page.title = "ПЦР Калькулятор"
        self.page.window_width = 750
        self.page.window_height = 950
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.scroll = "auto"
        self.page.horizontal_alignment = "center"

        self.tab_calc_btn = ft.ElevatedButton("🧬 Калькулятор", on_click=lambda e: self.switch_tab("calc"),
                                              color="white", bgcolor="blue")
        self.tab_set_btn = ft.ElevatedButton("⚙️ Настройки", on_click=lambda e: self.switch_tab("set"), color="white",
                                             bgcolor="grey")
        self.custom_tabs_row = ft.Row([self.tab_calc_btn, self.tab_set_btn], alignment=ft.MainAxisAlignment.CENTER)

        self.calc_view = self.build_calc_tab()
        self.set_view = self.build_settings_tab()
        self.set_view.visible = False

        self.page.add(
            ft.Container(height=10),
            self.custom_tabs_row,
            ft.Divider(),
            self.calc_view,
            self.set_view
        )
        self.update_table(self.current_rxn)

    def switch_tab(self, tab_name):
        if tab_name == "calc":
            self.calc_view.visible = True
            self.set_view.visible = False
            self.tab_calc_btn.bgcolor = "blue"
            self.tab_set_btn.bgcolor = "grey"
        else:
            self.calc_view.visible = False
            self.set_view.visible = True
            self.tab_calc_btn.bgcolor = "grey"
            self.tab_set_btn.bgcolor = "blue"
        self.page.update()

    def build_calc_tab(self):
        self.recipe_dropdown = ft.Dropdown(
            width=400,
            options=[ft.dropdown.Option(name) for name in self.db.get_all_names()],
            value=self.current_recipe.name,
            on_change=self.on_recipe_change
        )

        self.edit_btn = ft.IconButton(icon="edit", tooltip="Изменить", icon_color="blue",
                                      on_click=lambda e: self.open_editor(is_new=False))
        self.new_btn = ft.IconButton(icon="add_box", tooltip="Создать", icon_color="green",
                                     on_click=lambda e: self.open_editor(is_new=True))
        self.menu_row = ft.Row([self.recipe_dropdown, self.edit_btn, self.new_btn],
                               alignment=ft.MainAxisAlignment.CENTER)

        self.marker_inputs = []
        self.markers_list_ui = ft.Column([], horizontal_alignment="center")
        self.add_marker_btn = ft.IconButton(icon="add_circle", icon_color="blue", icon_size=30,
                                            on_click=self.add_marker)
        self.rm_marker_btn = ft.IconButton(icon="remove_circle", icon_color="red", icon_size=30,
                                           on_click=self.remove_marker)
        self.marker_controls_row = ft.Row(
            [ft.Text("Маркеры:", size=16, weight="bold"), self.add_marker_btn, self.rm_marker_btn],
            alignment=ft.MainAxisAlignment.CENTER)
        self.add_marker(update_ui=False)
        self.markers_wrapper = ft.Column([self.marker_controls_row, self.markers_list_ui],
                                         horizontal_alignment="center")

        self.program_inputs = []
        self.programs_list_ui = ft.Column([], horizontal_alignment="center")
        self.add_prog_btn = ft.IconButton(icon="add_circle", icon_color="purple", icon_size=30,
                                          on_click=self.add_program)
        self.rm_prog_btn = ft.IconButton(icon="remove_circle", icon_color="red", icon_size=30,
                                         on_click=self.remove_program)
        self.prog_controls_row = ft.Row(
            [ft.Text("Программы:", size=16, weight="bold"), self.add_prog_btn, self.rm_prog_btn],
            alignment=ft.MainAxisAlignment.CENTER)
        self.add_program(update_ui=False)
        self.program_inputs[0].value = getattr(self.current_recipe, 'program', '')
        self.programs_wrapper = ft.Column([self.prog_controls_row, self.programs_list_ui],
                                          horizontal_alignment="center")

        self.block_inputs = []
        self.blocks_list_ui = ft.Column([], horizontal_alignment="center")
        self.add_btn = ft.IconButton(icon="add_circle", icon_color="green", icon_size=30, on_click=self.add_block)
        self.rm_btn = ft.IconButton(icon="remove_circle", icon_color="red", icon_size=30, on_click=self.remove_block)
        self.block_controls_row = ft.Row([ft.Text("Блоки плашек:", size=16, weight="bold"), self.add_btn, self.rm_btn],
                                         alignment=ft.MainAxisAlignment.CENTER)
        self.add_block(update_ui=False)

        self.extra_rxn = ft.TextField(label="Доп. реакции", width=120, value="8", text_align="center",
                                      on_change=self.calculate_total)
        self.total_rxn_label = ft.Text("Итого реакций: 8", size=22, weight="bold", color="green")
        self.current_rxn = 8

        self.blocks_wrapper = ft.Column([
            self.block_controls_row, self.blocks_list_ui,
            ft.Row([ft.Text("Дополнительно:", size=16), self.extra_rxn], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=5), self.total_rxn_label
        ], horizontal_alignment="center")

        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Реагент", weight="bold")),
                ft.DataColumn(ft.Text("На 1 rxn", weight="bold"), numeric=True),
                ft.DataColumn(ft.Text("Общий объем", weight="bold"), numeric=True)
            ],
            rows=[]
        )

        self.amp_checkboxes_row = ft.Row([], wrap=True, alignment=ft.MainAxisAlignment.CENTER)
        self.amps_wrapper = ft.Column([
            ft.Text("Где ставим? (можно выбрать несколько):", size=16, weight="bold", color="blue"),
            self.amp_checkboxes_row
        ], horizontal_alignment="center")
        self.refresh_amp_checkboxes()

        self.view_btn = ft.ElevatedButton("👀 PDF", icon="remove_red_eye", color="white", bgcolor="blue",
                                          on_click=self.on_view_click)
        self.print_btn = ft.ElevatedButton("🖨 Печать", icon="print", color="white", bgcolor="green",
                                           on_click=self.on_print_click)
        self.google_btn = ft.ElevatedButton("☁️ В Журнал", icon="cloud_upload", color="white", bgcolor="orange",
                                            on_click=self.on_google_click)
        self.buttons_row = ft.Row(controls=[self.view_btn, self.print_btn, self.google_btn],
                                  alignment=ft.MainAxisAlignment.CENTER)

        dynamic_inputs_row = ft.Row([self.markers_wrapper, ft.VerticalDivider(), self.programs_wrapper],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    vertical_alignment=ft.CrossAxisAlignment.START)

        return ft.Column([
            self.menu_row, ft.Divider(),
            dynamic_inputs_row, ft.Divider(),
            self.blocks_wrapper, ft.Divider(),
            self.amps_wrapper, ft.Container(height=5),
            self.buttons_row, ft.Divider(),
            ft.Row([self.table], alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment="center")

    def build_settings_tab(self):
        title = ft.Text("⚙️ Настройки Амплификаторов", size=24, weight="bold")

        self.new_amp_input = ft.TextField(label="Название нового амплификатора", width=300)
        add_btn = ft.ElevatedButton("Добавить", icon="add", color="white", bgcolor="green",
                                    on_click=self.on_add_amp_click)

        self.amps_list_ui = ft.Column([], horizontal_alignment="center")
        self.refresh_settings_list()

        return ft.Column([
            ft.Container(height=20),
            ft.Row([title], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(),
            ft.Row([self.new_amp_input, add_btn], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            self.amps_list_ui
        ], horizontal_alignment="center")

    def refresh_settings_list(self):
        self.amps_list_ui.controls.clear()
        for amp in self.settings.amplifiers:
            self.amps_list_ui.controls.append(
                ft.Row([
                    ft.Text(amp, size=16, width=200),
                    ft.IconButton(icon="delete", icon_color="red", tooltip="Удалить",
                                  on_click=lambda e, a=amp: self.on_delete_amp_click(a))
                ], alignment=ft.MainAxisAlignment.CENTER)
            )
        self.page.update()

    def refresh_amp_checkboxes(self):
        self.amp_checkboxes = {amp: ft.Checkbox(label=amp, value=False) for amp in self.settings.amplifiers}
        self.amp_checkboxes_row.controls = list(self.amp_checkboxes.values())
        self.page.update()

    def on_add_amp_click(self, e):
        val = self.new_amp_input.value.strip()
        if val:
            self.settings.add_amplifier(val)
            self.new_amp_input.value = ""
            self.refresh_settings_list()
            self.refresh_amp_checkboxes()

    def on_delete_amp_click(self, amp_name):
        self.settings.remove_amplifier(amp_name)
        self.refresh_settings_list()
        self.refresh_amp_checkboxes()

    def add_marker(self, e=None, update_ui=True):
        i = len(self.marker_inputs) + 1
        m_f = ft.TextField(label=f"Маркер {i}", width=300)
        self.marker_inputs.append(m_f)
        self.markers_list_ui.controls = [ft.Row([m], alignment=ft.MainAxisAlignment.CENTER) for m in self.marker_inputs]
        if update_ui: self.page.update()

    def remove_marker(self, e=None):
        if len(self.marker_inputs) > 1:
            self.marker_inputs.pop()
            self.markers_list_ui.controls = [ft.Row([m], alignment=ft.MainAxisAlignment.CENTER) for m in
                                             self.marker_inputs]
            self.page.update()

    def add_program(self, e=None, update_ui=True):
        i = len(self.program_inputs) + 1
        p_f = ft.TextField(label=f"Программа {i}", width=300)
        self.program_inputs.append(p_f)
        self.programs_list_ui.controls = [ft.Row([p], alignment=ft.MainAxisAlignment.CENTER) for p in
                                          self.program_inputs]
        if update_ui: self.page.update()

    def remove_program(self, e=None):
        if len(self.program_inputs) > 1:
            self.program_inputs.pop()
            self.programs_list_ui.controls = [ft.Row([p], alignment=ft.MainAxisAlignment.CENTER) for p in
                                              self.program_inputs]
            self.page.update()

    def add_block(self, e=None, update_ui=True):
        i = len(self.block_inputs) + 1
        name_f = ft.TextField(label=f"Блок {i}", width=200, on_change=self.calculate_total)
        count_f = ft.TextField(label="Шт", width=80, value="", text_align="center", on_change=self.calculate_total)
        self.block_inputs.append({"name": name_f, "count": count_f})
        self.blocks_list_ui.controls = [ft.Row([b["name"], b["count"]], alignment=ft.MainAxisAlignment.CENTER) for b in
                                        self.block_inputs]
        if update_ui: self.page.update()

    def remove_block(self, e=None):
        if len(self.block_inputs) > 1:
            self.block_inputs.pop()
            self.blocks_list_ui.controls = [ft.Row([b["name"], b["count"]], alignment=ft.MainAxisAlignment.CENTER) for b
                                            in self.block_inputs]
            self.calculate_total()

    def calculate_total(self, e=None):
        total = sum([int(b["count"].value.strip()) for b in self.block_inputs if b["count"].value.strip().isdigit()])
        if self.extra_rxn.value.strip().isdigit(): total += int(self.extra_rxn.value.strip())
        self.current_rxn = total if total > 0 else 1
        self.total_rxn_label.value = f"Итого реакций: {self.current_rxn}"
        self.update_table(self.current_rxn)
        self.page.update()

    def on_recipe_change(self, e):
        self.current_recipe = self.db.get_recipe(self.recipe_dropdown.value)
        if self.program_inputs: self.program_inputs[0].value = getattr(self.current_recipe, 'program', '')
        self.update_table(self.current_rxn)
        self.page.update()

    def update_table(self, rxn):
        self.table.rows.clear()
        data = self.current_recipe.calculate(rxn)
        for row in data:
            self.table.rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(row[0]))),
                    ft.DataCell(ft.Text(str(row[1]))),
                    ft.DataCell(ft.Text(str(row[2])))
                ]))
        self.table.rows.append(ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("Итого Mastermix", weight="bold", color="green")),
                ft.DataCell(ft.Text(str(self.current_recipe.mastermix), weight="bold", color="green")),
                ft.DataCell(ft.Text(f"{self.current_recipe.mastermix * rxn:.1f}", weight="bold", color="green"))
            ]))

    def open_editor(self, is_new=False):
        r = self.current_recipe
        if is_new:
            from config import PCRRecipe
            r = PCRRecipe("Новый протокол", 2.0, 2.0, 0.6, 0.1, 0.1, 13.05, 0.15)

        name_f = ft.TextField(label="Название протокола", value=r.name if not is_new else "", expand=True)
        buf_f = ft.TextField(label="Буфер", value=str(r.buffer), width=80)
        mg_f = ft.TextField(label="MgCl2", value=str(r.mgcl2), width=80)
        dntp_f = ft.TextField(label="dNTPs", value=str(r.dntps), width=80)
        taq_f = ft.TextField(label="Taq", value=str(r.taq), width=80)

        prf_f = ft.TextField(label="Пр. F", value=str(r.primer_f), width=80)
        prr_f = ft.TextField(label="Пр. R", value=str(r.primer_r), width=80)
        pr3_f = ft.TextField(label="Пр. 3", value=str(getattr(r, 'primer_3', 0.0)), width=80)
        h2o_f = ft.TextField(label="H2O", value=str(r.h2o), width=80)

        p1n_f = ft.TextField(label="Праймер 1", value=r.primer1_name, expand=True)
        p2n_f = ft.TextField(label="Праймер 2", value=r.primer2_name, expand=True)
        p3n_f = ft.TextField(label="Праймер 3", value=getattr(r, 'primer3_name', ""), expand=True)

        prog_f = ft.TextField(label="Программа по умолч.", value=getattr(r, 'program', ''), expand=True)
        temp_f = ft.TextField(label="Температура", value=getattr(r, 'temp', ''), width=150)

        def save_click(e):
            try:
                from config import PCRRecipe
                p3_val = float(pr3_f.value.replace(',', '.')) if pr3_f.value.strip() else 0.0

                new_recipe = PCRRecipe(
                    name=name_f.value,
                    buffer=float(buf_f.value.replace(',', '.')),
                    mgcl2=float(mg_f.value.replace(',', '.')),
                    dntps=float(dntp_f.value.replace(',', '.')),
                    primer_f=float(prf_f.value.replace(',', '.')),
                    primer_r=float(prr_f.value.replace(',', '.')),
                    h2o=float(h2o_f.value.replace(',', '.')),
                    taq=float(taq_f.value.replace(',', '.')),
                    primer1_name=p1n_f.value,
                    primer2_name=p2n_f.value,
                    program=prog_f.value,
                    temp=temp_f.value,
                    primer_3=p3_val,
                    primer3_name=p3n_f.value
                )
                self.db.add_or_update(new_recipe)
                self.recipe_dropdown.options = [ft.dropdown.Option(n) for n in self.db.get_all_names()]
                self.recipe_dropdown.value = new_recipe.name
                self.current_recipe = new_recipe
                if self.program_inputs: self.program_inputs[0].value = getattr(new_recipe, 'program', '')
                self.update_table(self.current_rxn)
                self.page.close(dialog)
                self.page.update()
                self.page.open(ft.SnackBar(ft.Text("✅ Сохранено!"), bgcolor="green"))
            except ValueError:
                self.page.open(ft.SnackBar(ft.Text("❌ Ошибка: Числа пишите через точку!"), bgcolor="red"))

        dialog = ft.AlertDialog(
            title=ft.Text("✏️ Редактор"),
            content=ft.Column([
                name_f,
                ft.Row([buf_f, mg_f, dntp_f, taq_f]),
                ft.Row([prf_f, prr_f, pr3_f, h2o_f]),
                ft.Row([p1n_f, p2n_f, p3n_f]),
                ft.Row([prog_f, temp_f])
            ], tight=True),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton("Сохранить", on_click=save_click, color="white", bgcolor="green")
            ]
        )
        self.page.open(dialog)

    def on_view_click(self, e):
        self.generate_document(auto_print=False)

    def on_print_click(self, e):
        self.generate_document(auto_print=True)

    def on_google_click(self, e):
        active_markers = ", ".join([m.value.strip() for m in self.marker_inputs if m.value.strip()])
        active_programs = ", ".join([p.value.strip() for p in self.program_inputs if p.value.strip()])
        total_mm = round(self.current_recipe.mastermix * self.current_rxn, 1)

        selected_amps = [name for name, cb in self.amp_checkboxes.items() if cb.value]
        amp_str = ", ".join(selected_amps) if selected_amps else "Не указан"

        success, msg = self.google_logger.log_experiment(
            protocol_name=self.current_recipe.name,
            markers=active_markers,
            programs=active_programs,
            rxn_count=self.current_rxn,
            mastermix_vol=total_mm,
            amplifier=amp_str
        )

        color = "green" if success else "red"
        self.page.open(ft.SnackBar(ft.Text(msg), bgcolor=color))

    def generate_document(self, auto_print):
        rxn = self.current_rxn
        data = self.current_recipe.calculate(rxn)
        active_markers = [m.value.strip() for m in self.marker_inputs if m.value.strip()]
        active_programs = [p.value.strip() for p in self.program_inputs if p.value.strip()]

        blocks_data = [{"name": b["name"].value,
                        "count": int(b["count"].value.strip()) if b["count"].value.strip().isdigit() else 0} for b in
                       self.block_inputs]
        extra = int(self.extra_rxn.value.strip()) if self.extra_rxn.value.strip().isdigit() else 0

        selected_amps = [name for name, cb in self.amp_checkboxes.items() if cb.value]

        success, msg = PDFGenerator.create_protocol(
            rxn=rxn,
            data_rows=data,
            recipe=self.current_recipe,
            blocks_data=blocks_data,
            markers_list=active_markers,
            programs_list=active_programs,
            extra_rxn=extra,
            all_amplifiers=self.settings.amplifiers,
            selected_amplifiers=selected_amps,
            auto_print=auto_print
        )

        color = "green" if success else "red"
        self.page.open(ft.SnackBar(ft.Text(msg), bgcolor=color))


def main(page: ft.Page):
    PCRApp(page)


ft.app(target=main)