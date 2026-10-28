import os
import sqlite3
from datetime import datetime, date

FORMATO_FECHA = "%d/%m/%Y"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DB_PATH = os.path.join(ASSETS_DIR, "data.db")


class ContactManager:
    def __init__(self) -> None:
        # Crea la carpeta assets y la base de datos si no existen
        os.makedirs(ASSETS_DIR, exist_ok=True)
        self.connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_table()

    def create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS datos (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CLIENTE TEXT NOT NULL,
            CORREO TEXT,
            DETALLES TEXT,
            FECHA_INICIO TEXT,
            FECHA_FIN TEXT,
            ESTADO TEXT,
            DIAS_ATRASADOS INTEGER DEFAULT 0,
            PAGO_MENSUAL REAL DEFAULT 0,
            PAGO_TOTAL REAL DEFAULT 0,
            INSTALACION REAL DEFAULT 0
        )
        '''
        self.connection.execute(query)
        self.connection.commit()

    @staticmethod
    def calcular_estado(fecha_fin_str):
        """Devuelve (estado, dias_atrasados) segun la fecha de fin."""
        try:
            fin = datetime.strptime(fecha_fin_str, FORMATO_FECHA).date()
        except (ValueError, TypeError):
            return "NO DEFINIDO", 0
        hoy = date.today()
        if hoy > fin:
            return "VENCIDO", (hoy - fin).days
        return "AL DÍA", 0

    def add_cliente(self, cliente, correo, detalles, fecha_inicio, fecha_fin,
                    estado, dias_atrasados, pago_mensual, pago_total, instalacion):
        query = '''
        INSERT INTO datos (CLIENTE, CORREO, DETALLES, FECHA_INICIO, FECHA_FIN,
                           ESTADO, DIAS_ATRASADOS, PAGO_MENSUAL, PAGO_TOTAL, INSTALACION)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.connection.execute(query, (cliente, correo, detalles, fecha_inicio, fecha_fin,
                                        estado, dias_atrasados, pago_mensual, pago_total, instalacion))
        self.connection.commit()

    def get_clientes(self, filtro=""):
        cursor = self.connection.cursor()
        if filtro:
            cursor.execute("SELECT * FROM datos WHERE CLIENTE LIKE ? ORDER BY ID", (f"%{filtro}%",))
        else:
            cursor.execute("SELECT * FROM datos ORDER BY ID")
        return cursor.fetchall()

    def get_cliente(self, cliente_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM datos WHERE ID = ?", (cliente_id,))
        return cursor.fetchone()

    def get_atrasados(self):
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT CLIENTE, FECHA_INICIO, DIAS_ATRASADOS FROM datos "
            "WHERE DIAS_ATRASADOS > 0 ORDER BY DIAS_ATRASADOS DESC"
        )
        return cursor.fetchall()

    def delete_clientes(self, ids):
        self.connection.executemany("DELETE FROM datos WHERE ID = ?", [(i,) for i in ids])
        self.connection.commit()

    def update_cliente(self, cliente_id, cliente, correo, detalles, fecha_inicio, fecha_fin,
                       estado, dias_atrasados, pago_mensual, pago_total, instalacion):
        query = '''
        UPDATE datos
        SET CLIENTE = ?, CORREO = ?, DETALLES = ?, FECHA_INICIO = ?, FECHA_FIN = ?,
            ESTADO = ?, DIAS_ATRASADOS = ?, PAGO_MENSUAL = ?, PAGO_TOTAL = ?, INSTALACION = ?
        WHERE ID = ?
        '''
        self.connection.execute(query, (cliente, correo, detalles, fecha_inicio, fecha_fin,
                                        estado, dias_atrasados, pago_mensual, pago_total,
                                        instalacion, cliente_id))
        self.connection.commit()

    def update_estados(self):
        """Recalcula ESTADO y DIAS_ATRASADOS de todos los clientes con la fecha de hoy."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT ID, FECHA_FIN FROM datos")
        for cliente_id, fecha_fin in cursor.fetchall():
            estado, dias = self.calcular_estado(fecha_fin)
            self.connection.execute(
                "UPDATE datos SET ESTADO = ?, DIAS_ATRASADOS = ? WHERE ID = ?",
                (estado, dias, cliente_id),
            )
        self.connection.commit()

    def close_connection(self):
        self.connection.close()