import flet as ft
import pandas as pd
from datetime import datetime, timedelta
from connect_manager import ConnectManager

class AppControl(ft.Container):
    def __init__(self, page: ft.Page):
        super()._init_(expand=True)
        self.page = page
        
        # Colores principales del tema del video
        self.color_primary = "#008080"
        self.bgcolor = "#0F0F0F"
        
        # Conexión a la base de datos
        self.db = ConnectManager()
        self.selected_row = []
        self.estado = "NO DEFINIDO"
        self.dias_atrasados = "NO DEFINIDO"

        self.bgcolor = "black"
        self.page.window.prevent_close = True
        self.page.window.on_event = self.window_event

        self.confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Por favor confirme", color = self.color_primary),
            content=ft.Text("¿Estás seguro de querer cerrar la aplicación?"),
            actions=[
                ft.ElevatedButton("SI", bgcolor=self.color_primary, on_click=self.yes_click),
                ft.OutlinedButton("NO", style=ft.ButtonStyle(side=ft.BorderSide(2, self.color_primary)), on_click=self.no_click)
            ]
        )
        self.mensaje_aviso_error = ft.Text()
        self.alert_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error", color=self.color_primary),
            content=self.mensaje_aviso_error,
            actions=[
                ft.ElevatedButton("OK", bgcolor=self.color_primary, on_click=self.ok_click)
            ]
        )

        # CAMPOS DE TEXTO DEL FORMULARIO
        self.txt_cliente = ft.TextField(label="Nombre del Cliente", border_color=self.color_primary)
        self.txt_correo = ft.TextField(label="Correo Electrónico", border_color=self.color_primary)
        self.txt_detalles = ft.TextField(label="Detalles", border_color=self.color_primary)
        self.txt_fecha_inicio = ft.TextField(label="Fecha Inicio (YYYY-MM-DD)", border_color=self.color_primary)
        self.txt_pago_mensual = ft.TextField(label="Pago Mensual", border_color=self.color_primary)
        self.txt_pago_total = ft.TextField(label="Pago Total", border_color=self.color_primary)
        self.txt_instalacion = ft.TextField(label="Pago Instalación", border_color=self.color_primary)

        # TABLA DE DATOS
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Correo")),
                ft.DataColumn(ft.Text("Inicio")),
                ft.DataColumn(ft.Text("Fin")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Días")),
                ft.DataColumn(ft.Text("Mensual")),
                ft.DataColumn(ft.Text("Total")),
                ft.DataColumn(ft.Text("Instalación")),
            ],
            rows=[]
        )

        # BOTONES
        btn_guardar = ft.ElevatedButton("Guardar", on_click=self.guardar_datos, bgcolor=self.color_primary, color="white")
        btn_borrar = ft.ElevatedButton("Borrar", on_click=self.borrar_datos, bgcolor="red", color="white")
        btn_excel = ft.ElevatedButton("Exportar Excel", on_click=self.exportar_excel)

        # ESTRUCTURA DE LA INTERFAZ
        form_container = ft.Column([
            self.txt_cliente,
            self.txt_correo,
            self.txt_detalles,
            self.txt_fecha_inicio,
            self.txt_pago_mensual,
            self.txt_pago_total,
            self.txt_instalacion,
            ft.Row([btn_guardar, btn_borrar, btn_excel])
        ], width=300)

        self.content = ft.Row([
            form_container,
            ft.Column([self.table], scroll=ft.ScrollMode.ALWAYS, expand=True)
        ])

        self.cargar_tabla()

    def calcular_fechas(self, fecha_str, mensual, total):
        try:
            f_inicio = datetime.strptime(fecha_str, "%Y-%m-%d")
            meses = int(float(total) // float(mensual)) if float(mensual) > 0 else 1
            f_fin = f_inicio + timedelta(days=30 * meses)
            
            hoy = datetime.now()
            if hoy > f_fin:
                estado = "Debe"
                dias = (hoy - f_fin).days
            else:
                estado = "Al día"
                dias = 0
            return f_fin.strftime("%Y-%m-%d"), estado, str(dias)
        except Exception:
            return fecha_str, "Al día", "0"

    def guardar_datos(self, e):
        if not self.txt_cliente.value or not self.txt_pago_mensual.value:
            return

        f_fin, estado, dias = self.calcular_fechas(
            self.txt_fecha_inicio.value,
            self.txt_pago_mensual.value,
            self.txt_pago_total.value
        )

        self.db.add_client(
            self.txt_cliente.value,
            self.txt_correo.value,
            self.txt_detalles.value,
            self.txt_fecha_inicio.value,
            f_fin,
            estado,
            dias,
            self.txt_pago_mensual.value,
            self.txt_pago_total.value,
            self.txt_instalacion.value
        )
        self.limpiar_campos()
        self.cargar_tabla()

    def cargar_tabla(self):
        self.table.rows.clear()
        registros = self.db.get_clients()
        for r in registros:
            self.table.rows.append(
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text(str(val))) for val in r]
                )
            )
        self.page.update()

    def borrar_datos(self, e):
        if self.txt_cliente.value:
            self.db.delete_client(self.txt_cliente.value)
            self.limpiar_campos()
            self.cargar_tabla()

    def exportar_excel(self, e):
        registros = self.db.get_clients()
        cols = ["ID", "Cliente", "Correo", "Detalles", "Inicio", "Fin", "Estado", "Días", "Mensual", "Total", "Instalación"]
        df = pd.DataFrame(registros, columns=cols)
        df.to_excel("reporte_pagos.xlsx", index=False)

    def limpiar_campos(self):
        self.txt_cliente.value = ""
        self.txt_correo.value = ""
        self.txt_detalles.value = ""
        self.txt_fecha_inicio.value = ""
        self.txt_pago_mensual.value = ""
        self.txt_pago_total.value = ""
        self.txt_instalacion.value = ""

def main(page: ft.Page):
    page.title = "Control de Pagos"
    page.bgcolor = "#0F0F0F"
    app = AppControl(page)
    page.add(app)

ft.app(target=main)