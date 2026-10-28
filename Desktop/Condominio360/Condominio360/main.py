import os
import flet as ft
import pandas as pd
from connect_manager import ContactManager, FORMATO_FECHA
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class AppControl(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page

        self.color_primary = "#008080"
        self.bg_color = "#0F0F0F"

        self.data = ContactManager()
        self.selected_row = []          # IDs de las filas marcadas en la tabla
        self.editing_id = None          # ID del cliente que se esta editando
        self.fecha_inicio = None        # datetime elegido en el calendario
        self.estado = "NO DEFINIDO"
        self.dias_atrasados = "NO DEFINIDO"

        self.page.bgcolor = "black"
        self.page.window.prevent_close = True
        self.page.window.on_event = self.window_event

        # ---------------- Dialogos ----------------
        self.confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Por favor confirme", color=self.color_primary),
            content=ft.Text("¿Está seguro de que desea salir de la aplicación?"),
            actions=[
                ft.ElevatedButton("SI", bgcolor=self.color_primary, on_click=self.yes_click),
                ft.OutlinedButton("NO", style=ft.ButtonStyle(side=ft.BorderSide(2, self.color_primary)), on_click=self.no_click),
            ],
        )

        self.delete_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar borrado", color=self.color_primary),
            content=ft.Text("¿Desea borrar los clientes seleccionados?"),
            actions=[
                ft.ElevatedButton("SI", bgcolor=self.color_primary, on_click=self.confirmar_borrado),
                ft.OutlinedButton("NO", style=ft.ButtonStyle(side=ft.BorderSide(2, self.color_primary)),
                                  on_click=lambda e: self.page.close(self.delete_dialog)),
            ],
        )

        self.mensaje_aviso_error = ft.Text()
        self.alert_dialog = ft.AlertDialog(
            title=ft.Text("Aviso", color=self.color_primary),
            content=self.mensaje_aviso_error,
            actions=[
                ft.TextButton("OK", style=ft.ButtonStyle(bgcolor=self.color_primary, color="white"), on_click=lambda e: self.close_dialog())
            ],
        )

        self.table_detalles = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Fecha inicio")),
                ft.DataColumn(ft.Text("Dias retrasados")),
            ])
        self.scrollable_table = ft.Column(
            controls=[self.table_detalles],
            width=500,   # Ancho fijo
            height=300,  # Altura fija
            scroll="auto",
        )
        self.detalles_dialog = ft.AlertDialog(
            title=ft.Text("Pagos atrasados", color=self.color_primary),
            content=self.scrollable_table,
            actions=[
                ft.TextButton("Cerrar", style=ft.ButtonStyle(bgcolor=self.color_primary, color="white"),
                              on_click=lambda e: self.page.close(self.detalles_dialog))
            ],
        )

        self.date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2040, 12, 31),
            on_change=self.fecha_elegida,
        )

        # ---------------- Formulario ----------------
        self.txt_cliente = self.crear_campo("Nombre del Cliente")
        self.txt_correo = self.crear_campo("Correo electronico")
        self.txt_detalles = self.crear_campo("Detalles")
        self.txt_pago_mensual = self.crear_campo("Pago mensual", numerico=True)
        self.txt_pago_total = self.crear_campo("Pago Total", numerico=True)
        self.txt_instalacion = self.crear_campo("Pago de instalación", numerico=True)

        self.lbl_fecha = ft.Text("Fecha de inicio")
        self.btn_fecha = ft.ElevatedButton(
            "Elegir fecha de inicio",
            icon=ft.Icons.CALENDAR_MONTH,
            color="white",
            bgcolor="#1c2a2a",
            on_click=self.abrir_calendario,
        )

        panel_formulario = ft.Container(
            width=380,
            bgcolor=self.bg_color,
            border_radius=15,
            padding=20,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Ingrese sus datos", size=26, italic=True, color="white"),
                            ft.Row(controls=[
                                ft.IconButton(ft.Icons.REFRESH, tooltip="Limpiar formulario", on_click=self.limpiar),
                                ft.IconButton(ft.Icons.ATTACH_MONEY, tooltip="Ver pagos atrasados", on_click=self.ver_atrasados),
                            ]),
                        ],
                    ),
                    self.txt_cliente,
                    self.txt_correo,
                    self.txt_detalles,
                    ft.Container(
                        border=ft.border.all(1, self.color_primary),
                        border_radius=5,
                        padding=5,
                        content=ft.Row(controls=[self.btn_fecha, self.lbl_fecha]),
                    ),
                    self.txt_pago_mensual,
                    self.txt_pago_total,
                    self.txt_instalacion,
                ],
            ),
        )

       
        self.tabla = ft.DataTable(
            show_checkbox_column=True,
            column_spacing=30,
            columns=[
                self.crear_columna("CLIENTE"),
                self.crear_columna("CORREO"),
                self.crear_columna("DETALLES"),
                self.crear_columna("INICIO"),
                self.crear_columna("FIN"),
                self.crear_columna("ESTADO"),
                self.crear_columna("DÍAS ATRASADOS"),
            ],
            rows=[],
        )

        self.txt_buscar = ft.TextField(
            hint_text="Buscar por nombre",
            border=ft.InputBorder.NONE,
            width=220,
            on_change=self.buscar,
        )

        barra_botones = ft.Row(
            wrap=True,
            controls=[
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, color="white", bgcolor=self.color_primary, on_click=self.guardar),
                ft.ElevatedButton("Actualizar", icon=ft.Icons.UPDATE, color="white", bgcolor=self.color_primary, on_click=self.actualizar),
                ft.ElevatedButton("Borrar", icon=ft.Icons.DELETE, color="white", bgcolor=self.color_primary, on_click=self.pedir_borrado),
                ft.IconButton(ft.Icons.EDIT, tooltip="Editar el cliente seleccionado", on_click=self.editar),
                ft.IconButton(ft.Icons.DOWNLOAD, tooltip="Exportar a Excel", on_click=self.exportar),
                ft.IconButton(ft.Icons.HOME, tooltip="Mostrar todos", on_click=self.mostrar_todos),
                self.txt_buscar,
            ],
        )

        panel_tabla = ft.Container(
            expand=True,
            bgcolor=self.bg_color,
            border_radius=15,
            padding=20,
            content=ft.Column(
                expand=True,
                controls=[
                    barra_botones,
                    ft.Column(
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[ft.Row(controls=[self.tabla], scroll=ft.ScrollMode.AUTO)],
                    ),
                ],
            ),
        )

        self.content = ft.Row(expand=True, controls=[panel_formulario, panel_tabla])

        self.cargar_tabla(actualizar=False)

    def crear_campo(self, label, numerico=False):
        return ft.TextField(
            label=label,
            border_color=self.color_primary,
            focused_border_color=self.color_primary,
            max_length=4 if numerico else None,
            keyboard_type=ft.KeyboardType.NUMBER if numerico else ft.KeyboardType.TEXT,
            input_filter=ft.NumbersOnlyInputFilter() if numerico else None,
        )

    def crear_columna(self, titulo):
        return ft.DataColumn(ft.Text(titulo, color=self.color_primary, weight=ft.FontWeight.BOLD))

    def show_message(self, texto):
        self.mensaje_aviso_error.value = texto
        self.page.open(self.alert_dialog)

    def close_dialog(self):
        self.page.close(self.alert_dialog)

    
    def window_event(self, e):
        if e.data == "close":
            self.page.open(self.confirm_dialog)

    def yes_click(self, e):
        self.data.close_connection()
        self.page.window.destroy()

    def no_click(self, e):
        self.page.close(self.confirm_dialog)

    
    def abrir_calendario(self, e):
        self.page.open(self.date_picker)

    def fecha_elegida(self, e):
        self.fecha_inicio = e.control.value
        self.lbl_fecha.value = self.fecha_inicio.strftime(FORMATO_FECHA)
        self.page.update()

    
    def cargar_tabla(self, filtro="", actualizar=True):
        self.data.update_estados()
        self.selected_row = []
        self.tabla.rows = []

        for fila in self.data.get_clientes(filtro):
            # 0 ID, 1 CLIENTE, 2 CORREO, 3 DETALLES, 4 INICIO, 5 FIN, 6 ESTADO, 7 DIAS
            color_estado = "red" if fila[6] == "VENCIDO" else "green"
            self.tabla.rows.append(
                ft.DataRow(
                    selected=False,
                    on_select_changed=lambda e, rid=fila[0]: self.seleccionar(e, rid),
                    cells=[
                        ft.DataCell(ft.Text(fila[1])),
                        ft.DataCell(ft.Text(fila[2] or "")),
                        ft.DataCell(ft.Text(fila[3] or "")),
                        ft.DataCell(ft.Text(fila[4])),
                        ft.DataCell(ft.Text(fila[5])),
                        ft.DataCell(ft.Text(fila[6], color=color_estado)),
                        ft.DataCell(ft.Text(str(fila[7]))),
                    ],
                )
            )

        if actualizar:
            self.tabla.update()

    def seleccionar(self, e, row_id):
        e.control.selected = not e.control.selected
        if e.control.selected:
            self.selected_row.append(row_id)
        elif row_id in self.selected_row:
            self.selected_row.remove(row_id)
        e.control.update()

    def buscar(self, e):
        self.cargar_tabla(self.txt_buscar.value.strip())

    def mostrar_todos(self, e):
        self.txt_buscar.value = ""
        self.cargar_tabla()
        self.txt_buscar.update()

    
    def limpiar(self, e=None):
        for campo in (self.txt_cliente, self.txt_correo, self.txt_detalles,
                      self.txt_pago_mensual, self.txt_pago_total, self.txt_instalacion):
            campo.value = ""
        self.fecha_inicio = None
        self.editing_id = None
        self.lbl_fecha.value = "Fecha de inicio"
        self.page.update()

    def leer_formulario(self):
        """Valida el formulario y devuelve la tupla lista para guardar, o None si hay error."""
        cliente = self.txt_cliente.value.strip()
        correo = self.txt_correo.value.strip()
        detalles = self.txt_detalles.value.strip()

        if not cliente:
            self.show_message("Escriba el nombre del cliente.")
            return None
        if correo and "@" not in correo:
            self.show_message("El correo electrónico no es válido.")
            return None
        if self.fecha_inicio is None:
            self.show_message("Elija la fecha de inicio.")
            return None

        pago_mensual = int(self.txt_pago_mensual.value or 0)
        pago_total = int(self.txt_pago_total.value or 0)
        instalacion = int(self.txt_instalacion.value or 0)

        if pago_mensual <= 0 or pago_total <= 0:
            self.show_message("El pago mensual y el pago total deben ser mayores que 0.")
            return None

        # Numero de meses = pago total / pago mensual (cada mes = 30 dias)
        meses = max(1, round(pago_total / pago_mensual))
        fecha_fin = self.fecha_inicio + timedelta(days=30 * meses)
        fecha_fin_str = fecha_fin.strftime(FORMATO_FECHA)

        self.estado, self.dias_atrasados = ContactManager.calcular_estado(fecha_fin_str)

        return (cliente, correo, detalles,
                self.fecha_inicio.strftime(FORMATO_FECHA), fecha_fin_str,
                self.estado, self.dias_atrasados,
                pago_mensual, pago_total, instalacion)

   
    def guardar(self, e):
        datos = self.leer_formulario()
        if datos is None:
            return
        self.data.add_cliente(*datos)
        self.limpiar()
        self.cargar_tabla()
        self.show_message("Cliente guardado correctamente.")

    def editar(self, e):
        if len(self.selected_row) != 1:
            self.show_message("Marque un solo cliente para editarlo.")
            return
        fila = self.data.get_cliente(self.selected_row[0])
        if not fila:
            return

        self.editing_id = fila[0]
        self.txt_cliente.value = fila[1]
        self.txt_correo.value = fila[2] or ""
        self.txt_detalles.value = fila[3] or ""
        self.fecha_inicio = datetime.strptime(fila[4], FORMATO_FECHA)
        self.lbl_fecha.value = fila[4]
        self.txt_pago_mensual.value = f"{fila[8]:g}"
        self.txt_pago_total.value = f"{fila[9]:g}"
        self.txt_instalacion.value = f"{fila[10]:g}"
        self.page.update()

    def actualizar(self, e):
        if self.editing_id is None:
            self.show_message("Primero marque un cliente y pulse el lápiz para editarlo.")
            return
        datos = self.leer_formulario()
        if datos is None:
            return
        self.data.update_cliente(self.editing_id, *datos)
        self.limpiar()
        self.cargar_tabla()
        self.show_message("Cliente actualizado correctamente.")

    def pedir_borrado(self, e):
        if not self.selected_row:
            self.show_message("Marque al menos un cliente para borrar.")
            return
        self.page.open(self.delete_dialog)

    def confirmar_borrado(self, e):
        self.data.delete_clientes(self.selected_row)
        self.page.close(self.delete_dialog)
        self.limpiar()
        self.cargar_tabla()

    def ver_atrasados(self, e):
        self.data.update_estados()
        self.table_detalles.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(nombre)),
                ft.DataCell(ft.Text(inicio)),
                ft.DataCell(ft.Text(str(dias))),
            ])
            for nombre, inicio, dias in self.data.get_atrasados()
        ]
        self.page.open(self.detalles_dialog)

    def exportar(self, e):
        filas = self.data.get_clientes()
        if not filas:
            self.show_message("No hay datos para exportar.")
            return
        columnas = ["ID", "CLIENTE", "CORREO", "DETALLES", "FECHA_INICIO", "FECHA_FIN",
                    "ESTADO", "DIAS_ATRASADOS", "PAGO_MENSUAL", "PAGO_TOTAL", "INSTALACION"]
        nombre = f"clientes_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
        ruta = os.path.join(BASE_DIR, nombre)
        try:
            pd.DataFrame(filas, columns=columnas).to_excel(ruta, index=False)
            self.show_message(f"Archivo exportado:\n{ruta}")
        except Exception as ex:
            self.show_message(f"No se pudo exportar: {ex}")


def main(page: ft.Page):
    page.title = "Control de Pagos"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10
    page.window.width = 1200
    page.window.height = 700
    page.add(AppControl(page))


ft.app(target=main)