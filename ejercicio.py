import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt

# --- 1. INSPECCIÓN Y ANÁLISIS CON PANDAS ---
def analizar_datos(df):
    print("=" * 50)
    print("INSPECCIÓN INICIAL DE DATOS CON PANDAS")
    print("=" * 50)
    print("\n--> Estructura del DataFrame (Filas, Columnas):", df.shape)
    print("\n--> Tipos de datos por columna:\n", df.dtypes)
    print("\n--> Primeras filas del inventario:\n", df.head())
    print("\n--> Resumen estadístico del inventario:\n", df.describe())
    print("\n--> Conteo de productos por sucursal:\n", df['Sucursal'].value_counts())
    print("=" * 50)


# --- 2. INTERFAZ GRÁFICA CON PYQT5 Y MATPLOTLIB ---
class VentanaInventario(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Sistema de Gestión e Inspección de Inventario - UGB")
        self.setGeometry(100, 100, 1100, 700)

        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QHBoxLayout(widget_central)

        # Panel Izquierdo: Tabla de Datos
        layout_izquierdo = QVBoxLayout()
        label_tabla = QLabel("<b>Inventario Consolidado por Sucursales</b>")
        layout_izquierdo.addWidget(label_tabla)

        self.tabla = QTableWidget()
        self.cargar_tabla()
        layout_izquierdo.addWidget(self.tabla)

        btn_resumen = QPushButton("Mostrar Resumen Estadístico")
        btn_resumen.clicked.connect(self.mostrar_resumen)
        layout_izquierdo.addWidget(btn_resumen)

        layout_principal.addLayout(layout_izquierdo, stretch=1)

        # Panel Derecho: Gráficos con Matplotlib
        layout_derecho = QVBoxLayout()
        label_grafico = QLabel("<b>Visualización de Métricas del Inventario</b>")
        layout_derecho.addWidget(label_grafico)

        self.figura, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(6, 8))
        self.canvas = FigureCanvas(self.figura)
        layout_derecho.addWidget(self.canvas)

        self.generar_graficos()

        layout_principal.addLayout(layout_derecho, stretch=1)

    def cargar_tabla(self):
        self.tabla.setRowCount(len(self.df))
        self.tabla.setColumnCount(len(self.df.columns))
        self.tabla.setHorizontalHeaderLabels(self.df.columns)

        for i in range(len(self.df)):
            for j in range(len(self.df.columns)):
                item = QTableWidgetItem(str(self.df.iloc[i, j]))
                self.tabla.setItem(i, j, item)

        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def generar_graficos(self):
        self.ax1.clear()
        self.ax2.clear()

        # Gráfico 1: Total de Stock por Sucursal (Barras)
        stock_sucursal = self.df.groupby('Sucursal')['Cantidad_Stock'].sum()
        stock_sucursal.plot(kind='bar', ax=self.ax1, color='#2b5c8f')
        self.ax1.set_title('Cantidad Total en Stock por Sucursal')
        self.ax1.set_xlabel('Sucursal')
        self.ax1.set_ylabel('Unidades')
        self.ax1.tick_params(axis='x', rotation=30)

        # Gráfico 2: Valor Monetario por Categoría (Pie Chart)
        self.df['Valor_Total'] = self.df['Cantidad_Stock'] * self.df['Precio_Unitario']
        valor_categoria = self.df.groupby('Categoria')['Valor_Total'].sum()
        valor_categoria.plot(kind='pie', ax=self.ax2, autopct='%1.1f%%', startangle=90)
        self.ax2.set_title('Distribución del Valor Monetario por Categoria')
        self.ax2.set_ylabel('')

        self.figura.tight_layout()
        self.canvas.draw()

    def mostrar_resumen(self):
        total_unidades = self.df['Cantidad_Stock'].sum()
        valor_inventario = (self.df['Cantidad_Stock'] * self.df['Precio_Unitario']).sum()
        mensaje = (
            f"<b>Métricas Generales del Inventario:</b><br><br>"
            f"• <b>Total de Productos Registrados:</b> {len(self.df)}<br>"
            f"• <b>Total de Unidades en Stock:</b> {total_unidades:,} unidades<br>"
            f"• <b>Valor Total del Inventario:</b> ${valor_inventario:,.2f}<br>"
            f"• <b>Sucursales Monitoreadas:</b> 5 (San Salvador, Santa Ana, San Miguel, La Libertad, Sonsonate)"
        )
        QMessageBox.information(self, "Resumen Estadístico", mensaje)


# --- 3. EJECUCIÓN DEL PROGRAMA ---
if __name__ == '__main__':
    archivo_csv = 'datos.csv'

    if not os.path.exists(archivo_csv):
        print(f"Error: No se encontró el archivo {archivo_csv}. Asegúrate de crearlo en la misma carpeta.")
        sys.exit(1)

    # Carga de datos
    df_inventario = pd.read_csv(archivo_csv)

    # Inspección técnica en consola con Pandas
    analizar_datos(df_inventario)

    # Lanzamiento de la Interfaz PyQt5
    app = QApplication(sys.argv)
    ventana = VentanaInventario(df_inventario)
    ventana.show()
    sys.exit(app.exec_())