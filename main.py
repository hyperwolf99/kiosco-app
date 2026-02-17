"""
Kiosco Manager - Main Application
Optimized UI/UX following accessibility guidelines (WCAG)
Simple, clear, and intuitive interface for non-technical users
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime, timedelta
import json
import logging
from typing import Optional
from pathlib import Path

from database import Database, DatabaseError, FormaPago, EstadoFiado

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Color scheme - Paleta atractiva en modo claro
class Colors:
    """Esquema de colores atractivo y profesional"""
    # Colores principales
    PRIMARY = "#3B82F6"           # Azul vibrante
    PRIMARY_DARK = "#1D4ED8"      # Azul oscuro para hover
    PRIMARY_LIGHT = "#DBEAFE"     # Azul claro para fondos
    
    # Colores de éxito/positivos
    SUCCESS = "#10B981"           # Verde esmeralda
    SUCCESS_DARK = "#059669"      # Verde oscuro
    SUCCESS_LIGHT = "#D1FAE5"     # Verde claro
    
    # Colores de peligro/negativos
    DANGER = "#EF4444"            # Rojo coral
    DANGER_DARK = "#DC2626"       # Rojo oscuro
    DANGER_LIGHT = "#FEE2E2"      # Rojo claro
    
    # Colores de advertencia
    WARNING = "#F59E0B"           # Ámbar
    WARNING_DARK = "#D97706"      # Ámbar oscuro
    WARNING_LIGHT = "#FEF3C7"     # Ámbar claro
    
    # Colores de información
    INFO = "#8B5CF6"              # Púrpura
    INFO_DARK = "#7C3AED"         # Púrpura oscuro
    INFO_LIGHT = "#EDE9FE"        # Púrpura claro
    
    # Colores de fondo
    BACKGROUND = "#F1F5F9"        # Gris azulado muy claro
    CARD_BG = "#FFFFFF"           # Blanco puro para tarjetas
    CARD_BG_ALT = "#F8FAFC"       # Gris muy claro alternativo
    
    # Colores de texto
    TEXT_PRIMARY = "#1E293B"      # Gris oscuro casi negro
    TEXT_SECONDARY = "#64748B"    # Gris medio
    TEXT_MUTED = "#94A3B8"        # Gris claro
    
    # Colores de borde
    BORDER = "#CBD5E1"            # Gris azulado
    BORDER_LIGHT = "#E2E8F0"      # Gris muy claro
    
    # Colores especiales
    ACCENT = "#EC4899"            # Rosa para acentos
    ACCENT_LIGHT = "#FCE7F3"      # Rosa claro


class KioscoApp:
    """
    Main application class with optimized UI/UX
    Following accessibility guidelines for elderly and non-technical users
    """
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🏪 Kiosco Manager - Control de Ventas")
        self.root.geometry("1200x800")
        self.root.configure(bg=Colors.BACKGROUND)
        
        # Configure fonts for readability
        self.setup_fonts()
        
        # Initialize database
        try:
            self.db = Database()
        except DatabaseError as e:
            messagebox.showerror(
                "Error de Base de Datos",
                f"No se pudo iniciar la base de datos:\n{str(e)}\n\n"
                "Contacte soporte técnico."
            )
            self.root.quit()
            return
        
        # Initialize variables
        self.init_variables()
        
        # Create UI
        self.create_ui()
        
        # Load initial data
        self.load_initial_data()
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        logger.info("Kiosco Manager iniciado correctamente")
    
    def setup_fonts(self):
        """Setup accessible fonts following WCAG guidelines - EXTRA LARGE for readability"""
        # Main font - extra large for elderly users
        self.font_title = ("Segoe UI", 32, "bold")
        self.font_header = ("Segoe UI", 20, "bold")
        self.font_large = ("Segoe UI", 18)
        self.font_medium = ("Segoe UI", 16)
        self.font_normal = ("Segoe UI", 14)
        self.font_small = ("Segoe UI", 12)
        
        # Extra large fonts for tables (important for visibility)
        self.font_table_header = ("Segoe UI", 14, "bold")
        self.font_table_row = ("Segoe UI", 14)
        
        # Configure ttk styles for larger fonts in treeviews
        style = ttk.Style()
        style.configure("Treeview", font=self.font_table_row, rowheight=35)
        style.configure("Treeview.Heading", font=self.font_table_header)
        style.configure("TNotebook.Tab", font=self.font_medium)
    
    def init_variables(self):
        """Initialize Tkinter variables"""
        # Venta variables
        self.var_monto = tk.StringVar()
        self.var_cliente = tk.StringVar()
        self.var_nota = tk.StringVar()
        self.var_forma_pago = tk.StringVar(value=FormaPago.EFECTIVO.value)
        
        # Fiado variables
        self.var_fiado_cliente_id = tk.IntVar(value=0)
        self.var_fiado_cliente_nombre = tk.StringVar()
        self.var_fiado_monto = tk.StringVar()
        self.var_fiado_interes = tk.StringVar(value="0")
        self.var_fiado_nota = tk.StringVar()
        
        # Nuevo cliente variables
        self.var_nuevo_cliente_nombre = tk.StringVar()
        self.var_nuevo_cliente_telefono = tk.StringVar()
        
        # Historial variables
        self.var_historial_cliente_id = tk.IntVar(value=0)
        
        # Search variables
        self.var_buscar_fecha = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
    
    def create_ui(self):
        """Create main user interface"""
        # Main container with padding
        self.main_container = tk.Frame(self.root, bg=Colors.BACKGROUND)
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        self.create_header()
        
        # Navigation tabs
        self.create_tabs()
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create application header with title"""
        self.header_frame = tk.Frame(self.main_container, bg=Colors.PRIMARY, padx=20, pady=15)
        self.header_frame.pack(fill='x', pady=(0, 20))
        
        title = tk.Label(
            self.header_frame,
            text="🏪 KIOSCO MANAGER",
            font=self.font_title,
            bg=Colors.PRIMARY,
            fg="white"
        )
        title.pack(side='left')
        
        # Date display
        date_label = tk.Label(
            self.header_frame,
            text=datetime.now().strftime('%d/%m/%Y %H:%M'),
            font=self.font_medium,
            bg=Colors.PRIMARY,
            fg="white"
        )
        date_label.pack(side='right')
        
        # Update time every minute
        self.update_time(date_label)
    
    def update_time(self, label):
        """Update time display every minute"""
        label.config(text=datetime.now().strftime('%d/%m/%Y %H:%M'))
        self.root.after(60000, lambda: self.update_time(label))
    
    def create_tabs(self):
        """Create tabbed interface"""
        # Style configuration for tabs
        style = ttk.Style()
        style.configure('TNotebook', background=Colors.BACKGROUND)
        style.configure('TNotebook.Tab', font=self.font_medium, padding=[20, 10])
        
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Tab 1: Register Sale
        self.tab_ventas = tk.Frame(self.notebook, bg=Colors.BACKGROUND)
        self.notebook.add(self.tab_ventas, text="💰  REGISTRAR VENTA")
        self.create_tab_ventas()
        
        # Tab 2: Reports
        self.tab_reportes = tk.Frame(self.notebook, bg=Colors.BACKGROUND)
        self.notebook.add(self.tab_reportes, text="📊  REPORTES")
        self.create_tab_reportes()
        
        # Tab 3: Fiados
        self.tab_fiados = tk.Frame(self.notebook, bg=Colors.BACKGROUND)
        self.notebook.add(self.tab_fiados, text="📒  FIADOS")
        self.create_tab_fiados()
    
    def create_tab_ventas(self):
        """Create sales registration tab"""
        # Left panel - Form
        form_panel = tk.Frame(self.tab_ventas, bg=Colors.CARD_BG, padx=30, pady=30)
        form_panel.pack(side='left', fill='both', expand=False, padx=(0, 10))
        
        # Form title
        tk.Label(
            form_panel,
            text="Nueva Venta",
            font=self.font_header,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 20))
        
        # Amount input
        self.create_form_field(
            form_panel, "Monto ($):", self.var_monto,
            is_number=True, is_large=True
        )
        
        # Payment method selection
        self.create_payment_method_selector(form_panel)
        
        # Client name (optional)
        self.create_form_field(
            form_panel, "Cliente (opcional):", self.var_cliente
        )
        
        # Note (optional)
        self.create_form_field(
            form_panel, "Nota (opcional):", self.var_nota
        )
        
        # Save button - LARGE and GREEN
        save_btn = tk.Button(
            form_panel,
            text="✅  GUARDAR VENTA",
            font=("Segoe UI", 18, "bold"),
            bg=Colors.SUCCESS,
            fg="white",
            activebackground=Colors.SUCCESS_DARK,
            activeforeground="white",
            cursor="hand2",
            padx=40,
            pady=15,
            command=self.guardar_venta
        )
        save_btn.pack(pady=(30, 0))
        
        # Tooltip
        self.create_tooltip(save_btn, "Presione Enter para guardar rápido")
        
        # Right panel - Today's sales
        sales_panel = tk.Frame(self.tab_ventas, bg=Colors.CARD_BG, padx=20, pady=20)
        sales_panel.pack(side='left', fill='both', expand=True)
        
        # Panel title
        tk.Label(
            sales_panel,
            text="Ventas de Hoy",
            font=self.font_header,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 10))
        
        # Sales treeview
        self.create_sales_treeview(sales_panel)
    
    def create_form_field(self, parent, label_text, variable, is_number=False, is_large=False):
        """Create a labeled form field"""
        frame = tk.Frame(parent, bg=Colors.CARD_BG)
        frame.pack(fill='x', pady=10)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=self.font_medium if not is_large else self.font_large,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        )
        label.pack(anchor='w')
        
        entry = tk.Entry(
            frame,
            textvariable=variable,
            font=self.font_large if is_large else self.font_medium,
            width=25 if is_large else 30,
            relief='solid',
            bd=2
        )
        entry.pack(fill='x', pady=(5, 0))
        
        if is_number:
            # Validation for numbers
            vcmd = (parent.register(self.validate_number), '%P')
            entry.config(validate='key', validatecommand=vcmd)
        
        return entry
    
    def validate_number(self, value):
        """Validate numeric input"""
        if value == "":
            return True
        try:
            float(value.replace(',', '.'))
            return True
        except ValueError:
            return False
    
    def create_payment_method_selector(self, parent):
        """Create payment method buttons"""
        frame = tk.Frame(parent, bg=Colors.CARD_BG)
        frame.pack(fill='x', pady=15)
        
        tk.Label(
            frame,
            text="Forma de Pago:",
            font=self.font_medium,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor='w')
        
        # Button container
        btn_frame = tk.Frame(frame, bg=Colors.CARD_BG)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        self.payment_buttons = {}
        
        # Emojis para cada forma de pago
        payment_emojis = {
            'Efectivo': '💵',
            'Transferencia': '📱',
            'Débito': '💳',
            'Crédito': '💎'
        }
        
        for i, forma_pago in enumerate(FormaPago):
            emoji = payment_emojis.get(forma_pago.value, '💵')
            btn_text = f"{emoji} {forma_pago.value}"
            
            btn = tk.Button(
                btn_frame,
                text=btn_text,
                font=self.font_medium,
                width=14,
                bg=Colors.PRIMARY if i == 0 else Colors.BACKGROUND,
                fg="white" if i == 0 else Colors.TEXT_PRIMARY,
                activebackground=Colors.PRIMARY_DARK,
                activeforeground="white",
                relief='solid',
                bd=3 if i == 0 else 2,
                highlightbackground=Colors.BORDER,
                highlightthickness=2,
                cursor="hand2",
                command=lambda fp=forma_pago.value: self.select_payment_method(fp)
            )
            btn.pack(side='left', padx=5)
            self.payment_buttons[forma_pago.value] = btn
    
    def select_payment_method(self, forma_pago):
        """Handle payment method selection"""
        self.var_forma_pago.set(forma_pago)
        
        # Update button styles
        for fp, btn in self.payment_buttons.items():
            if fp == forma_pago:
                btn.config(
                    bg=Colors.PRIMARY,
                    fg="white",
                    relief='solid',
                    bd=2
                )
            else:
                btn.config(
                    bg=Colors.BACKGROUND,
                    fg=Colors.TEXT_PRIMARY,
                    relief='solid',
                    bd=2
                )
    
    def create_sales_treeview(self, parent):
        """Create treeview for displaying sales"""
        # Create frame for treeview
        tree_frame = tk.Frame(parent, bg=Colors.CARD_BG)
        tree_frame.pack(fill='both', expand=True)
        
        # Define columns
        columns = ('hora', 'monto', 'pago', 'cliente', 'nota')
        self.tree_ventas = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        # Configure columns
        self.tree_ventas.heading('hora', text='Hora')
        self.tree_ventas.heading('monto', text='Monto')
        self.tree_ventas.heading('pago', text='Pago')
        self.tree_ventas.heading('cliente', text='Cliente')
        self.tree_ventas.heading('nota', text='Nota')
        
        self.tree_ventas.column('hora', width=80, anchor='center')
        self.tree_ventas.column('monto', width=100, anchor='e')
        self.tree_ventas.column('pago', width=120, anchor='center')
        self.tree_ventas.column('cliente', width=150)
        self.tree_ventas.column('nota', width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree_ventas.yview)
        self.tree_ventas.configure(yscrollcommand=scrollbar.set)
        
        self.tree_ventas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def create_tab_reportes(self):
        """Create reports tab"""
        # Notebook for sub-tabs
        report_notebook = ttk.Notebook(self.tab_reportes)
        report_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Daily report
        daily_frame = tk.Frame(report_notebook, bg=Colors.BACKGROUND, padx=20, pady=20)
        report_notebook.add(daily_frame, text="📅 Hoy")
        self.create_daily_report(daily_frame)
        
        # Monthly report
        monthly_frame = tk.Frame(report_notebook, bg=Colors.BACKGROUND, padx=20, pady=20)
        report_notebook.add(monthly_frame, text="📆 Este Mes")
        self.create_monthly_report(monthly_frame)
        
        # Date search
        search_frame = tk.Frame(report_notebook, bg=Colors.BACKGROUND, padx=20, pady=20)
        report_notebook.add(search_frame, text="🔍 Buscar Fecha")
        self.create_date_search(search_frame)
    
    def create_daily_report(self, parent):
        """Create daily report view"""
        # Summary cards
        summary_frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        summary_frame.pack(fill='x', pady=(0, 20))
        
        # Total card
        self.daily_total_card, self.daily_total_label = self.create_summary_card(
            summary_frame, "TOTAL HOY", "$0.00", Colors.PRIMARY
        )
        self.daily_total_card.pack(side='left', padx=(0, 10))
        
        # Sales count card
        self.daily_count_card, self.daily_count_label = self.create_summary_card(
            summary_frame, "CANTIDAD", "0 ventas", Colors.SUCCESS
        )
        self.daily_count_card.pack(side='left', padx=(0, 10))
        
        # Payment method breakdown
        self.daily_pagos_frame = tk.Frame(parent, bg=Colors.CARD_BG, padx=20, pady=15)
        self.daily_pagos_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            self.daily_pagos_frame,
            text="Desglose por Forma de Pago",
            font=self.font_header,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 10))
        
        # Sales detail treeview
        self.create_report_treeview(parent, 'daily')
    
    def create_monthly_report(self, parent):
        """Create monthly report view"""
        # Summary
        summary_frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        summary_frame.pack(fill='x', pady=(0, 20))
        
        self.monthly_total_card, self.monthly_total_label = self.create_summary_card(
            summary_frame, "TOTAL MES", "$0.00", Colors.PRIMARY
        )
        self.monthly_total_card.pack(side='left', padx=(0, 10))
        
        # Daily breakdown treeview
        columns = ('fecha', 'total', 'efectivo', 'transferencia', 'debito', 'credito')
        self.tree_mensual = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_mensual.heading(col, text=col.capitalize())
            self.tree_mensual.column(col, width=100, anchor='center' if col != 'fecha' else 'w')
        
        self.tree_mensual.column('fecha', width=120)
        
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.tree_mensual.yview)
        self.tree_mensual.configure(yscrollcommand=scrollbar.set)
        
        self.tree_mensual.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Export button
        export_btn = tk.Button(
            parent,
            text="📥 Exportar Mes",
            font=self.font_medium,
            bg=Colors.WARNING,
            fg="white",
            cursor="hand2",
            command=self.exportar_mes
        )
        export_btn.pack(pady=(10, 0))
    
    def create_date_search(self, parent):
        """Create date search interface with day, month and year options"""
        # Notebook for search types
        search_notebook = ttk.Notebook(parent)
        search_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Buscar por Fecha (día específico)
        tab_fecha = tk.Frame(search_notebook, bg=Colors.BACKGROUND)
        search_notebook.add(tab_fecha, text="📅 Por Fecha")
        self._create_search_by_date(tab_fecha)
        
        # Tab 2: Buscar por Mes
        tab_mes = tk.Frame(search_notebook, bg=Colors.BACKGROUND)
        search_notebook.add(tab_mes, text="📆 Por Mes")
        self._create_search_by_month(tab_mes)
        
        # Tab 3: Buscar por Año
        tab_anio = tk.Frame(search_notebook, bg=Colors.BACKGROUND)
        search_notebook.add(tab_anio, text="📊 Por Año")
        self._create_search_by_year(tab_anio)
    
    def _create_search_by_date(self, parent):
        """Create search by specific date"""
        # Search controls
        search_frame = tk.Frame(parent, bg=Colors.CARD_BG, padx=20, pady=15)
        search_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            search_frame,
            text="Fecha (AAAA-MM-DD):",
            font=self.font_medium,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(side='left')
        
        entry = tk.Entry(
            search_frame,
            textvariable=self.var_buscar_fecha,
            font=self.font_medium,
            width=15,
            relief='solid',
            bd=2
        )
        entry.pack(side='left', padx=10)
        
        search_btn = tk.Button(
            search_frame,
            text="🔍 Buscar",
            font=self.font_medium,
            bg=Colors.PRIMARY,
            fg="white",
            cursor="hand2",
            command=self.buscar_fecha
        )
        search_btn.pack(side='left')
        
        # Results
        self.search_result_frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        self.search_result_frame.pack(fill='both', expand=True)
    
    def _create_search_by_month(self, parent):
        """Create search by month interface"""
        # Variables para mes y año
        self.var_buscar_mes = tk.StringVar(value=str(datetime.now().month))
        self.var_buscar_mes_anio = tk.StringVar(value=str(datetime.now().year))
        
        # Search controls
        search_frame = tk.Frame(parent, bg=Colors.CARD_BG, padx=20, pady=15)
        search_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            search_frame,
            text="Mes:",
            font=self.font_medium,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(side='left')
        
        # Meses del año
        meses = [
            ("Enero", "01"), ("Febrero", "02"), ("Marzo", "03"),
            ("Abril", "04"), ("Mayo", "05"), ("Junio", "06"),
            ("Julio", "07"), ("Agosto", "08"), ("Septiembre", "09"),
            ("Octubre", "10"), ("Noviembre", "11"), ("Diciembre", "12")
        ]
        self.meses_dict = {nombre: num for nombre, num in meses}
        
        combo_mes = ttk.Combobox(
            search_frame,
            values=[m[0] for m in meses],
            font=self.font_medium,
            width=15,
            state='readonly'
        )
        combo_mes.set([m[0] for m in meses][datetime.now().month - 1])
        combo_mes.pack(side='left', padx=10)
        self.combo_mes_busqueda = combo_mes
        
        tk.Label(
            search_frame,
            text="Año:",
            font=self.font_medium,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(side='left', padx=(20, 5))
        
        entry_anio = tk.Entry(
            search_frame,
            textvariable=self.var_buscar_mes_anio,
            font=self.font_medium,
            width=8,
            relief='solid',
            bd=2
        )
        entry_anio.pack(side='left', padx=5)
        
        search_btn = tk.Button(
            search_frame,
            text="🔍 Buscar Mes",
            font=self.font_medium,
            bg=Colors.PRIMARY,
            fg="white",
            cursor="hand2",
            command=self.buscar_por_mes
        )
        search_btn.pack(side='left', padx=20)
        
        # Results frame
        self.search_mes_result_frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        self.search_mes_result_frame.pack(fill='both', expand=True)
    
    def _create_search_by_year(self, parent):
        """Create search by year interface"""
        self.var_buscar_anio = tk.StringVar(value=str(datetime.now().year))
        
        # Search controls
        search_frame = tk.Frame(parent, bg=Colors.CARD_BG, padx=20, pady=15)
        search_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            search_frame,
            text="Año:",
            font=self.font_medium,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(side='left')
        
        entry_anio = tk.Entry(
            search_frame,
            textvariable=self.var_buscar_anio,
            font=self.font_medium,
            width=10,
            relief='solid',
            bd=2
        )
        entry_anio.pack(side='left', padx=10)
        
        search_btn = tk.Button(
            search_frame,
            text="🔍 Buscar Año",
            font=self.font_medium,
            bg=Colors.PRIMARY,
            fg="white",
            cursor="hand2",
            command=self.buscar_por_anio
        )
        search_btn.pack(side='left', padx=20)
        
        # Results frame
        self.search_anio_result_frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        self.search_anio_result_frame.pack(fill='both', expand=True)
    
    def create_tab_fiados(self):
        """Create fiados management tab"""
        # Create notebook for fiados sub-tabs
        self.fiados_notebook = ttk.Notebook(self.tab_fiados)
        self.fiados_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Nuevo Fiado
        tab_nuevo = tk.Frame(self.fiados_notebook, bg=Colors.BACKGROUND)
        self.fiados_notebook.add(tab_nuevo, text="➕ Nuevo Fiado")
        self.create_tab_nuevo_fiado(tab_nuevo)
        
        # Tab 2: Lista de Fiados
        tab_lista = tk.Frame(self.fiados_notebook, bg=Colors.BACKGROUND)
        self.fiados_notebook.add(tab_lista, text="📋 Lista de Fiados")
        self.create_tab_lista_fiados(tab_lista)
        
        # Tab 3: Historial de Pagos
        tab_historial = tk.Frame(self.fiados_notebook, bg=Colors.BACKGROUND)
        self.fiados_notebook.add(tab_historial, text="📜 Historial de Pagos")
        self.create_tab_historial_pagos(tab_historial)
        
        # Evento cuando se cambia de pestaña en fiados
        self.fiados_notebook.bind('<<NotebookTabChanged>>', self.on_fiados_tab_changed)
    
    def on_fiados_tab_changed(self, event=None):
        """Handle tab change in fiados notebook"""
        try:
            current_tab = self.fiados_notebook.select()
            tab_text = self.fiados_notebook.tab(current_tab, "text")
            
            if tab_text == "➕ Nuevo Fiado":
                # Actualizar saldo del cliente seleccionado
                cliente_id = self.var_fiado_cliente_id.get()
                if cliente_id:
                    self.actualizar_saldo_cliente(cliente_id)
        except Exception as e:
            logger.error(f"Error al cambiar pestaña: {e}")
    
    def create_fiados_treeview(self, parent):
        """Create treeview for fiados"""
        columns = ('id', 'fecha', 'cliente', 'monto', 'interes', 'pagado', 'estado', 'nota')
        self.tree_fiados = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        display_columns = {
            'fecha': 'Fecha',
            'cliente': 'Cliente',
            'monto': 'Monto Total',
            'interes': 'Interés',
            'pagado': 'Pagado',
            'estado': 'Estado',
            'nota': 'Nota'
        }
        
        self.tree_fiados['displaycolumns'] = ('fecha', 'cliente', 'monto', 'interes', 'pagado', 'estado', 'nota')
        
        for col, header in display_columns.items():
            self.tree_fiados.heading(col, text=header)
            self.tree_fiados.column(col, width=100, anchor='center' if col != 'cliente' else 'w')
        
        self.tree_fiados.column('cliente', width=150)
        self.tree_fiados.column('nota', width=200)
        
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.tree_fiados.yview)
        self.tree_fiados.configure(yscrollcommand=scrollbar.set)
        
        self.tree_fiados.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Context menu
        self.tree_fiados.bind('<Button-3>', self.show_fiado_context_menu)
    
    def show_fiado_context_menu(self, event):
        """Show context menu for fiado actions"""
        item = self.tree_fiados.identify_row(event.y)
        if item:
            self.tree_fiados.selection_set(item)
            
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="✅ Registrar Pago", command=self.registrar_pago_fiado)
            menu.add_command(label="📋 Ver Historial", command=self.ver_historial_fiado)
            menu.add_separator()
            menu.add_command(label="❌ Cancelar")
            
            menu.post(event.x_root, event.y_root)
    
    def create_summary_card(self, parent, title, value, color):
        """Create a summary card widget - returns (frame, value_label) tuple"""
        card = tk.Frame(parent, bg=color, padx=30, pady=20)
        
        tk.Label(
            card,
            text=title,
            font=self.font_medium,
            bg=color,
            fg="white"
        ).pack()
        
        value_label = tk.Label(
            card,
            text=value,
            font=("Segoe UI", 24, "bold"),
            bg=color,
            fg="white"
        )
        value_label.pack()
        
        return card, value_label
    
    def create_tab_nuevo_fiado(self, parent):
        """Create new fiado tab with client selection"""
        # Left panel - Client Selection
        left_panel = tk.Frame(parent, bg=Colors.CARD_BG, padx=30, pady=30)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        
        tk.Label(
            left_panel,
            text="Seleccionar Cliente",
            font=self.font_header,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 20))
        
        # Client dropdown
        tk.Label(
            left_panel,
            text="Cliente:",
            font=self.font_medium,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor='w')
        
        self.combo_clientes = ttk.Combobox(
            left_panel,
            textvariable=self.var_fiado_cliente_nombre,
            font=self.font_medium,
            width=30,
            state='readonly'
        )
        self.combo_clientes.pack(fill='x', pady=(5, 20))
        self.combo_clientes.bind('<<ComboboxSelected>>', self.on_cliente_selected)
        
        # Refresh button
        tk.Button(
            left_panel,
            text="🔄 Actualizar Lista",
            font=self.font_normal,
            command=self.cargar_clientes_en_combo
        ).pack(fill='x', pady=(0, 30))
        
        # Or add new client
        separator = tk.Frame(left_panel, bg=Colors.BORDER, height=2)
        separator.pack(fill='x', pady=20)
        
        tk.Label(
            left_panel,
            text="¿Cliente nuevo?",
            font=self.font_header,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 10))
        
        self.create_form_field(left_panel, "Nombre:", self.var_nuevo_cliente_nombre)
        self.create_form_field(left_panel, "Teléfono (opcional):", self.var_nuevo_cliente_telefono)
        
        tk.Button(
            left_panel,
            text="➕ Agregar Cliente",
            font=self.font_medium,
            bg=Colors.PRIMARY,
            fg="white",
            cursor="hand2",
            command=self.agregar_nuevo_cliente
        ).pack(fill='x', pady=(10, 0))
        
        # Right panel - Fiado Form
        right_panel = tk.Frame(parent, bg=Colors.CARD_BG, padx=30, pady=30)
        right_panel.pack(side='left', fill='both', expand=True)
        
        tk.Label(
            right_panel,
            text="Datos del Fiado",
            font=self.font_header,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor='w', pady=(0, 20))
        
        # Selected client display
        self.lbl_cliente_seleccionado = tk.Label(
            right_panel,
            text="Cliente: Ninguno seleccionado",
            font=self.font_large,
            bg=Colors.CARD_BG,
            fg=Colors.DANGER
        )
        self.lbl_cliente_seleccionado.pack(anchor='w', pady=(0, 20))
        
        # Total pending for selected client
        self.lbl_saldo_cliente = tk.Label(
            right_panel,
            text="Saldo pendiente: $0.00",
            font=self.font_medium,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY
        )
        self.lbl_saldo_cliente.pack(anchor='w', pady=(0, 20))
        
        self.create_form_field(right_panel, "Monto del fiado ($):", self.var_fiado_monto, is_number=True)
        self.create_form_field(right_panel, "Interés (%):", self.var_fiado_interes, is_number=True)
        self.create_form_field(right_panel, "Nota:", self.var_fiado_nota)
        
        save_btn = tk.Button(
            right_panel,
            text="💾 GUARDAR FIADO",
            font=("Segoe UI", 18, "bold"),
            bg=Colors.DANGER,
            fg="white",
            activebackground=Colors.DANGER_DARK,
            cursor="hand2",
            padx=40,
            pady=15,
            command=self.guardar_fiado
        )
        save_btn.pack(pady=(30, 0))
        
        # Load initial clients
        self.cargar_clientes_en_combo()
        
        # Initialize client filter for fiados
        self.cargar_clientes_en_combo_fiados()
        self.filtro_cliente_id_actual = None
    
    def create_tab_lista_fiados(self, parent):
        """Create fiados list tab"""
        # Top panel with client filter
        top_frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        top_frame.pack(fill='x', pady=(0, 10))
        
        # Client filter
        filter_client_frame = tk.Frame(top_frame, bg=Colors.CARD_BG, padx=15, pady=10)
        filter_client_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            filter_client_frame,
            text="Filtrar por Cliente:",
            font=self.font_medium,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(side='left', padx=(0, 10))
        
        self.combo_filtro_cliente_fiados = ttk.Combobox(
            filter_client_frame,
            font=self.font_medium,
            width=30,
            state='readonly'
        )
        self.combo_filtro_cliente_fiados.pack(side='left', padx=(0, 10))
        self.combo_filtro_cliente_fiados.bind('<<ComboboxSelected>>', self.on_filtro_cliente_fiados_changed)
        
        tk.Button(
            filter_client_frame,
            text="🔄 Actualizar Lista",
            font=self.font_normal,
            bg=Colors.PRIMARY,
            fg="white",
            cursor="hand2",
            command=self.actualizar_lista_fiados_con_filtro
        ).pack(side='left', padx=5)
        
        tk.Button(
            filter_client_frame,
            text="❌ Limpiar Filtro",
            font=self.font_normal,
            command=self.limpiar_filtro_cliente_fiados
        ).pack(side='left', padx=5)
        
        # Filter buttons for status
        filter_frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Button(
            filter_frame,
            text="Todos",
            font=self.font_normal,
            command=lambda: self.cargar_fiados_filtrados(None)
        ).pack(side='left', padx=2)
        
        tk.Button(
            filter_frame,
            text="Pendientes",
            font=self.font_normal,
            bg=Colors.DANGER,
            fg="white",
            command=self.cargar_fiados_pendientes_y_parciales
        ).pack(side='left', padx=2)
        
        tk.Button(
            filter_frame,
            text="Pagados",
            font=self.font_normal,
            bg=Colors.SUCCESS,
            fg="white",
            command=lambda: self.cargar_fiados_filtrados(EstadoFiado.PAGADO.value)
        ).pack(side='left', padx=2)
        
        # Action buttons for selected client
        action_frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        action_frame.pack(fill='x', pady=(0, 10))
        
        self.lbl_cliente_seleccionado_fiados = tk.Label(
            action_frame,
            text="Ningún cliente seleccionado",
            font=self.font_medium,
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT_SECONDARY
        )
        self.lbl_cliente_seleccionado_fiados.pack(side='left', padx=(0, 20))
        
        self.btn_aplicar_interes = tk.Button(
            action_frame,
            text="📈 Aplicar Interés %",
            font=self.font_normal,
            bg=Colors.WARNING,
            fg="white",
            cursor="hand2",
            state='disabled',
            command=self.aplicar_interes_masivo
        )
        self.btn_aplicar_interes.pack(side='left', padx=5)
        
        self.btn_pagar_todo = tk.Button(
            action_frame,
            text="💰 Pagar Todo",
            font=self.font_normal,
            bg=Colors.SUCCESS,
            fg="white",
            cursor="hand2",
            state='disabled',
            command=self.pagar_todos_fiados_cliente
        )
        self.btn_pagar_todo.pack(side='left', padx=5)
        
        # Total pending
        self.lbl_total_fiados = tk.Label(
            parent,
            text="Total Pendiente General: $0.00",
            font=self.font_header,
            bg=Colors.BACKGROUND,
            fg=Colors.DANGER
        )
        self.lbl_total_fiados.pack(anchor='w', pady=10)
        
        # Fiados treeview - EXTRA LARGE FONT
        columns = ('id', 'fecha', 'cliente', 'monto_total', 'interes', 'pagado', 'saldo', 'estado', 'nota')
        self.tree_fiados = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        display_columns = {
            'fecha': 'Fecha',
            'cliente': 'Cliente',
            'monto_total': 'Monto Total',
            'interes': 'Int. %',
            'pagado': 'Pagado',
            'saldo': 'Saldo',
            'estado': 'Estado',
            'nota': 'Nota'
        }
        
        self.tree_fiados['displaycolumns'] = ('fecha', 'cliente', 'monto_total', 'interes', 'pagado', 'saldo', 'estado', 'nota')
        
        for col, header in display_columns.items():
            self.tree_fiados.heading(col, text=header)
            self.tree_fiados.column(col, width=120, anchor='center' if col != 'cliente' else 'w')
        
        self.tree_fiados.column('cliente', width=180)
        self.tree_fiados.column('nota', width=200)
        self.tree_fiados.column('monto_total', width=130)
        self.tree_fiados.column('saldo', width=130)
        
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.tree_fiados.yview)
        self.tree_fiados.configure(yscrollcommand=scrollbar.set)
        
        self.tree_fiados.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Context menu
        self.tree_fiados.bind('<Button-3>', self.show_fiado_context_menu)
        
        # Buttons frame
        btn_frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        btn_frame.pack(fill='x', pady=10)
        
        tk.Button(
            btn_frame,
            text="💵 Registrar Pago",
            font=self.font_medium,
            bg=Colors.SUCCESS,
            fg="white",
            cursor="hand2",
            command=self.registrar_pago_fiado
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="📋 Ver Detalle",
            font=self.font_medium,
            bg=Colors.PRIMARY,
            fg="white",
            cursor="hand2",
            command=self.ver_detalle_fiado
        ).pack(side='left', padx=5)
    
    def create_tab_historial_pagos(self, parent):
        """Create payment history tab"""
        # Top panel - Client selection
        top_panel = tk.Frame(parent, bg=Colors.CARD_BG, padx=20, pady=15)
        top_panel.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            top_panel,
            text="Ver historial de:",
            font=self.font_medium,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        ).pack(side='left', padx=(0, 10))
        
        self.combo_historial_cliente = ttk.Combobox(
            top_panel,
            font=self.font_medium,
            width=35,
            state='readonly'
        )
        self.combo_historial_cliente.pack(side='left', padx=(0, 10))
        self.combo_historial_cliente.bind('<<ComboboxSelected>>', self.cargar_historial_cliente)
        
        tk.Button(
            top_panel,
            text="🔍 Ver Historial",
            font=self.font_normal,
            bg=Colors.PRIMARY,
            fg="white",
            cursor="hand2",
            command=self.cargar_historial_cliente
        ).pack(side='left', padx=5)
        
        # Summary panel
        self.historial_summary = tk.Frame(parent, bg=Colors.CARD_BG, padx=20, pady=15)
        self.historial_summary.pack(fill='x', pady=(0, 10))
        
        self.lbl_historial_cliente = tk.Label(
            self.historial_summary,
            text="Seleccione un cliente para ver su historial",
            font=self.font_header,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY
        )
        self.lbl_historial_cliente.pack(anchor='w')
        
        self.lbl_historial_totales = tk.Label(
            self.historial_summary,
            text="",
            font=self.font_medium,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY
        )
        self.lbl_historial_totales.pack(anchor='w', pady=(5, 0))
        
        # Payments treeview - EXTRA LARGE FONT
        columns = ('fecha', 'fiado', 'monto', 'nota')
        self.tree_historial = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        headers = {'fecha': 'Fecha y Hora', 'fiado': 'Fiado #', 'monto': 'Monto Pagado', 'nota': 'Nota'}
        
        for col, header in headers.items():
            self.tree_historial.heading(col, text=header)
            self.tree_historial.column(col, width=150, anchor='center' if col != 'nota' else 'w')
        
        self.tree_historial.column('fecha', width=180)
        self.tree_historial.column('monto', width=150)
        self.tree_historial.column('nota', width=300)
        
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.tree_historial.yview)
        self.tree_historial.configure(yscrollcommand=scrollbar.set)
        
        self.tree_historial.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load clients
        self.cargar_clientes_en_combo_historial()
    
    def cargar_clientes_en_combo(self):
        """Load clients into combobox"""
        try:
            clientes = self.db.obtener_clientes()
            self.clientes_dict = {c['nombre']: c['id'] for c in clientes}
            self.combo_clientes['values'] = list(self.clientes_dict.keys())
            # También cargar en el filtro de fiados
            self.cargar_clientes_en_combo_fiados()
        except Exception as e:
            logger.error(f"Error al cargar clientes: {e}")
    
    def cargar_clientes_en_combo_historial(self):
        """Load clients into history combobox"""
        try:
            clientes = self.db.obtener_clientes()
            self.historial_clientes_dict = {c['nombre']: c['id'] for c in clientes}
            self.combo_historial_cliente['values'] = list(self.historial_clientes_dict.keys())
        except Exception as e:
            logger.error(f"Error al cargar clientes: {e}")
    
    def on_cliente_selected(self, event=None):
        """Handle client selection"""
        nombre = self.var_fiado_cliente_nombre.get()
        if nombre in self.clientes_dict:
            cliente_id = self.clientes_dict[nombre]
            self.var_fiado_cliente_id.set(cliente_id)
            self.lbl_cliente_seleccionado.config(
                text=f"Cliente: {nombre}",
                fg=Colors.SUCCESS
            )
            # Show pending balance
            self.actualizar_saldo_cliente(cliente_id)
    
    def actualizar_saldo_cliente(self, cliente_id):
        """Update client balance display"""
        try:
            resumen = self.db.obtener_resumen_fiados_cliente(cliente_id)
            saldo = resumen['resumen_fiados']['saldo_pendiente']
            self.lbl_saldo_cliente.config(
                text=f"Saldo pendiente total: ${saldo:.2f}"
            )
        except Exception as e:
            self.lbl_saldo_cliente.config(text="Saldo pendiente: $0.00")
    
    def agregar_nuevo_cliente(self):
        """Add new client"""
        nombre = self.var_nuevo_cliente_nombre.get().strip()
        telefono = self.var_nuevo_cliente_telefono.get().strip()
        
        if not nombre:
            messagebox.showwarning("⚠️ Atención", "Por favor ingrese el nombre del cliente")
            return
        
        try:
            cliente_id = self.db.agregar_cliente(nombre, telefono)
            if cliente_id:
                messagebox.showinfo("✅ Éxito", f"Cliente '{nombre}' agregado correctamente")
                self.var_nuevo_cliente_nombre.set('')
                self.var_nuevo_cliente_telefono.set('')
                self.cargar_clientes_en_combo()
                self.cargar_clientes_en_combo_historial()
                # Select the new client
                self.var_fiado_cliente_nombre.set(nombre)
                self.on_cliente_selected()
        except ValueError as e:
            messagebox.showwarning("⚠️ Atención", str(e))
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo agregar el cliente: {e}")
    
    def create_report_treeview(self, parent, report_type):
        """Create treeview for reports"""
        columns = ('hora', 'monto', 'pago', 'cliente', 'nota')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=100)
        
        tree.column('hora', width=80)
        tree.column('monto', width=100)
        tree.column('pago', width=120)
        tree.column('cliente', width=150)
        
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        if report_type == 'daily':
            self.tree_daily_report = tree
        else:
            self.tree_search_report = tree
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = tk.Frame(self.main_container, bg=Colors.PRIMARY, padx=20, pady=10)
        self.status_bar.pack(fill='x', pady=(20, 0))
        
        self.lbl_status = tk.Label(
            self.status_bar,
            text="Listo",
            font=self.font_normal,
            bg=Colors.PRIMARY,
            fg="white"
        )
        self.lbl_status.pack(side='left')
        
        self.lbl_totals = tk.Label(
            self.status_bar,
            text="💰 Hoy: $0.00  |  📒 Fiados: $0.00",
            font=self.font_normal,
            bg=Colors.PRIMARY,
            fg="white"
        )
        self.lbl_totals.pack(side='right')
    
    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip,
                text=text,
                font=self.font_small,
                bg='#FFFFCC',
                relief='solid',
                bd=1
            )
            label.pack()
            
            widget.tooltip = tooltip
        
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for power users"""
        self.root.bind('<Return>', lambda e: self.guardar_venta())
        self.root.bind('<F1>', lambda e: self.notebook.select(0))
        self.root.bind('<F2>', lambda e: self.notebook.select(1))
        self.root.bind('<F3>', lambda e: self.notebook.select(2))
        self.root.bind('<F5>', lambda e: self.refresh_all())
    
    def guardar_venta(self):
        """Save a new sale"""
        try:
            # Validate amount
            monto_str = self.var_monto.get().strip()
            if not monto_str:
                messagebox.showwarning("⚠️ Atención", "Por favor ingrese el monto")
                return
            
            try:
                monto = float(monto_str.replace(',', '.'))
                if monto <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("❌ Error", "El monto debe ser un número mayor a 0")
                return
            
            # Get other values
            forma_pago = self.var_forma_pago.get()
            cliente = self.var_cliente.get().strip()
            nota = self.var_nota.get().strip()
            
            # Save to database
            venta_id = self.db.agregar_venta(monto, forma_pago, cliente, nota)
            
            if venta_id:
                # Clear form
                self.var_monto.set('')
                self.var_cliente.set('')
                self.var_nota.set('')
                self.var_forma_pago.set(FormaPago.EFECTIVO.value)
                self.select_payment_method(FormaPago.EFECTIVO.value)
                
                # Refresh data
                self.refresh_all()
                
                # Show success
                messagebox.showinfo(
                    "✅ Éxito",
                    f"Venta registrada:\nMonto: ${monto:.2f}\nPago: {forma_pago}"
                )
                
                logger.info(f"Venta guardada: ID={venta_id}, Monto=${monto}")
            
        except DatabaseError as e:
            messagebox.showerror("❌ Error", str(e))
            logger.error(f"Error al guardar venta: {e}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error inesperado: {str(e)}")
            logger.error(f"Error inesperado: {e}")
    
    def guardar_fiado(self):
        """Save a new fiado with client ID"""
        try:
            # Validate client selection
            cliente_id = self.var_fiado_cliente_id.get()
            cliente_nombre = self.var_fiado_cliente_nombre.get()
            
            if not cliente_id or not cliente_nombre:
                messagebox.showwarning("⚠️ Atención", "Por favor seleccione un cliente de la lista")
                return
            
            # Validate amount
            monto_str = self.var_fiado_monto.get().strip()
            if not monto_str:
                messagebox.showwarning("⚠️ Atención", "Por favor ingrese el monto")
                return
            
            try:
                monto = float(monto_str.replace(',', '.'))
                if monto <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("❌ Error", "El monto debe ser un número mayor a 0")
                return
            
            # Get interest
            try:
                interes = float(self.var_fiado_interes.get().replace(',', '.') or 0)
                if interes < 0:
                    interes = 0
            except ValueError:
                interes = 0
            
            nota = self.var_fiado_nota.get().strip()
            
            # Save to database
            fiado_id = self.db.agregar_fiado(cliente_id, cliente_nombre, monto, interes, nota)
            
            if fiado_id:
                # Clear form
                self.var_fiado_monto.set('')
                self.var_fiado_interes.set('0')
                self.var_fiado_nota.set('')
                
                # Refresh data
                self.cargar_fiados()
                self.actualizar_saldo_cliente(cliente_id)
                self.update_status_bar()
                
                # Show success
                monto_total = monto * (1 + interes / 100)
                messagebox.showinfo(
                    "✅ Éxito",
                    f"Fiado registrado:\nCliente: {cliente_nombre}\nMonto Total: ${monto_total:.2f}"
                )
                
                logger.info(f"Fiado guardado: ID={fiado_id}, Cliente={cliente_nombre}")
            
        except DatabaseError as e:
            messagebox.showerror("❌ Error", str(e))
            logger.error(f"Error al guardar fiado: {e}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error inesperado: {str(e)}")
            logger.error(f"Error inesperado: {e}")
    
    def registrar_pago_fiado(self):
        """Register payment for selected fiado with partial payment support"""
        selection = self.tree_fiados.selection()
        if not selection:
            messagebox.showwarning("⚠️ Atención", "Por favor seleccione un fiado de la lista")
            return
        
        item = self.tree_fiados.item(selection[0])
        fiado_id = int(item['values'][0])
        cliente_nombre = item['values'][2]
        saldo_actual = float(item['values'][6].replace('$', '').replace(',', ''))
        
        # Get client info from database to find client_id
        try:
            # Search for client by name to get ID
            clientes = self.db.obtener_clientes()
            cliente_id = None
            for c in clientes:
                if c['nombre'] == cliente_nombre:
                    cliente_id = c['id']
                    break
        except:
            cliente_id = None
        
        # Show dialog with current balance
        msg = f"Cliente: {cliente_nombre}\nSaldo pendiente: ${saldo_actual:.2f}\n\nIngrese el monto a pagar:"
        monto = simpledialog.askfloat(
            "Registrar Pago",
            msg,
            minvalue=0.01,
            maxvalue=saldo_actual
        )
        
        if monto:
            try:
                resultado = self.db.registrar_pago_fiado(fiado_id, monto)
                
                if resultado:
                    # Build success message
                    msg = f"✅ Pago registrado exitosamente!\n\n"
                    msg += f"Monto pagado: ${resultado['monto_pagado']:.2f}\n"
                    msg += f"Total pagado: ${resultado['total_pagado']:.2f}\n"
                    msg += f"Saldo anterior: ${resultado['saldo_anterior']:.2f}\n"
                    msg += f"Saldo restante: ${resultado['saldo_restante']:.2f}\n"
                    msg += f"Estado: {resultado['estado']}"
                    
                    if resultado['completado']:
                        msg += "\n\n🎉 ¡FIADO COMPLETAMENTE PAGADO!"
                    
                    messagebox.showinfo("✅ Pago Registrado", msg)
                    
                    # Ask if user wants to register as sale
                    if messagebox.askyesno(
                        "Registrar como Venta",
                        "¿Desea registrar este pago como una venta también?"
                    ):
                        self.db.agregar_venta(
                            monto,
                            FormaPago.EFECTIVO.value,
                            cliente_nombre,
                            f"Pago de fiado #{fiado_id}"
                        )
                        self.refresh_all()
                    else:
                        # Recargar SIN filtro para mostrar el estado actualizado
                        self.cargar_fiados()  # Sin parámetro = mostrar todos
                        self.update_status_bar()
                    
                    # IMPORTANTE: Actualizar saldo del cliente en pestaña "Nuevo Fiado"
                    if cliente_id:
                        self.actualizar_saldo_cliente(cliente_id)
                        # Si el cliente está seleccionado en el combo, refrescar
                        if self.var_fiado_cliente_id.get() == cliente_id:
                            self.lbl_saldo_cliente.config(
                                text=f"Saldo actualizado - pendiente: ${resultado['saldo_restante']:.2f}"
                            )
                    
                    logger.info(f"Pago registrado: Fiado ID={fiado_id}, Monto=${monto}, Saldo=${resultado['saldo_restante']}")
            
            except Exception as e:
                messagebox.showerror("❌ Error", str(e))
                logger.error(f"Error al registrar pago: {e}")
    
    def ver_historial_fiado(self):
        """Show payment history for selected fiado"""
        selection = self.tree_fiados.selection()
        if not selection:
            return
        
        item = self.tree_fiados.item(selection[0])
        fiado_id = int(item['values'][0])
        cliente = item['values'][2]
        
        historial = self.db.obtener_historial_fiado(fiado_id)
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(f"Historial de Pagos - {cliente}")
        popup.geometry("500x400")
        
        tk.Label(
            popup,
            text=f"Historial de Pagos: {cliente}",
            font=self.font_header
        ).pack(pady=10)
        
        # Treeview for payments
        tree = ttk.Treeview(popup, columns=('fecha', 'monto', 'nota'), show='headings', height=10)
        tree.heading('fecha', text='Fecha')
        tree.heading('monto', text='Monto')
        tree.heading('nota', text='Nota')
        
        for pago in historial:
            tree.insert('', 'end', values=(
                pago['fecha_pago'],
                f"${pago['monto']:.2f}",
                pago['nota'] or '-'
            ))
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Button(
            popup,
            text="Cerrar",
            command=popup.destroy,
            font=self.font_medium
        ).pack(pady=10)
    
    def buscar_fecha(self):
        """Search sales by date"""
        try:
            fecha_str = self.var_buscar_fecha.get()
            datetime.strptime(fecha_str, '%Y-%m-%d')
            
            datos = self.db.obtener_resumen_diario(fecha_str)
            
            # Clear previous results
            for widget in self.search_result_frame.winfo_children():
                widget.destroy()
            
            # Show results
            tk.Label(
                self.search_result_frame,
                text=f"Resultados para: {fecha_str}",
                font=self.font_header,
                bg=Colors.BACKGROUND,
                fg=Colors.TEXT_PRIMARY
            ).pack(anchor='w', pady=(0, 10))
            
            # Summary
            summary = tk.Frame(self.search_result_frame, bg=Colors.CARD_BG, padx=20, pady=15)
            summary.pack(fill='x', pady=(0, 10))
            
            tk.Label(
                summary,
                text=f"Total: ${datos['total']:.2f}  |  Ventas: {datos['cantidad']}",
                font=self.font_large,
                bg=Colors.CARD_BG,
                fg=Colors.TEXT_PRIMARY
            ).pack()
            
            # Payment breakdown
            for forma_pago, info in datos['por_forma_pago'].items():
                tk.Label(
                    summary,
                    text=f"{forma_pago}: ${info['total']:.2f} ({info['cantidad']} ventas)",
                    font=self.font_normal,
                    bg=Colors.CARD_BG,
                    fg=Colors.TEXT_SECONDARY
                ).pack(anchor='w')
            
            # Sales list
            self.create_report_treeview(self.search_result_frame, 'search')
            
            for venta in datos['ventas']:
                hora = venta['fecha_hora'].split()[1] if venta['fecha_hora'] else ''
                self.tree_search_report.insert('', 'end', values=(
                    hora,
                    f"${venta['monto']:.2f}",
                    venta['forma_pago'],
                    venta['cliente'] or '-',
                    venta['nota'] or '-'
                ))
            
        except ValueError:
            messagebox.showerror("❌ Error", "Formato de fecha inválido. Use: AAAA-MM-DD")
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
            logger.error(f"Error al buscar fecha: {e}")
    
    def buscar_por_mes(self):
        """Search sales by month"""
        try:
            mes_nombre = self.combo_mes_busqueda.get()
            mes_num = self.meses_dict.get(mes_nombre, '01')
            anio = self.var_buscar_mes_anio.get()
            
            # Validate year
            if not anio.isdigit() or len(anio) != 4:
                raise ValueError("Año inválido")
            
            datos = self.db.obtener_resumen_mensual(int(anio), int(mes_num))
            
            # Clear previous results
            for widget in self.search_mes_result_frame.winfo_children():
                widget.destroy()
            
            # Show results
            tk.Label(
                self.search_mes_result_frame,
                text=f"Resultados para: {mes_nombre} {anio}",
                font=self.font_header,
                bg=Colors.BACKGROUND,
                fg=Colors.TEXT_PRIMARY
            ).pack(anchor='w', pady=(0, 10))
            
            # Summary
            summary = tk.Frame(self.search_mes_result_frame, bg=Colors.CARD_BG, padx=20, pady=15)
            summary.pack(fill='x', pady=(0, 10))
            
            tk.Label(
                summary,
                text=f"Total del Mes: ${datos['total']:.2f}  |  Promedio: ${datos['promedio']:.2f}  |  Ventas: {datos['cantidad']}",
                font=self.font_large,
                bg=Colors.CARD_BG,
                fg=Colors.TEXT_PRIMARY
            ).pack()
            
            # Payment breakdown
            for forma_pago, info in datos['por_forma_pago'].items():
                tk.Label(
                    summary,
                    text=f"{forma_pago}: ${info['total']:.2f} ({info['cantidad']} ventas)",
                    font=self.font_normal,
                    bg=Colors.CARD_BG,
                    fg=Colors.TEXT_SECONDARY
                ).pack(anchor='w')
            
            # Daily breakdown treeview
            tk.Label(
                self.search_mes_result_frame,
                text="Detalle por Día:",
                font=self.font_medium,
                bg=Colors.BACKGROUND,
                fg=Colors.TEXT_PRIMARY
            ).pack(anchor='w', pady=(10, 5))
            
            columns = ('fecha', 'total', 'efectivo', 'transferencia', 'debito', 'credito')
            tree = ttk.Treeview(self.search_mes_result_frame, columns=columns, show='headings', height=12)
            
            headers = {'fecha': 'Fecha', 'total': 'Total', 'efectivo': 'Efectivo', 
                      'transferencia': 'Transf.', 'debito': 'Débito', 'credito': 'Crédito'}
            
            for col, header in headers.items():
                tree.heading(col, text=header)
                tree.column(col, width=100, anchor='center' if col != 'fecha' else 'w')
            
            tree.column('fecha', width=120)
            
            scrollbar = ttk.Scrollbar(self.search_mes_result_frame, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            for dia in datos['por_dia']:
                tree.insert('', 'end', values=(
                    dia['dia'],
                    f"${dia['total']:.2f}",
                    f"${dia['efectivo']:.2f}",
                    f"${dia['transferencia']:.2f}",
                    f"${dia['debito']:.2f}",
                    f"${dia['credito']:.2f}"
                ))
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al buscar: {str(e)}")
            logger.error(f"Error al buscar por mes: {e}")
    
    def buscar_por_anio(self):
        """Search sales by year"""
        try:
            anio = self.var_buscar_anio.get()
            
            # Validate year
            if not anio.isdigit() or len(anio) != 4:
                raise ValueError("Año inválido. Use formato: AAAA")
            
            anio_int = int(anio)
            
            # Get data for all months
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        strftime('%m', fecha_hora) as mes,
                        COUNT(*) as cantidad,
                        SUM(monto) as total,
                        SUM(CASE WHEN forma_pago = 'Efectivo' THEN monto ELSE 0 END) as efectivo,
                        SUM(CASE WHEN forma_pago = 'Transferencia' THEN monto ELSE 0 END) as transferencia,
                        SUM(CASE WHEN forma_pago = 'Débito' THEN monto ELSE 0 END) as debito,
                        SUM(CASE WHEN forma_pago = 'Crédito' THEN monto ELSE 0 END) as credito
                    FROM ventas 
                    WHERE strftime('%Y', fecha_hora) = ?
                    GROUP BY mes
                    ORDER BY mes
                ''', (anio,))
                
                meses_data = cursor.fetchall()
                
                # Get total for year
                cursor.execute('''
                    SELECT COUNT(*), SUM(monto), AVG(monto)
                    FROM ventas 
                    WHERE strftime('%Y', fecha_hora) = ?
                ''', (anio,))
                
                total_year = cursor.fetchone()
            
            # Clear previous results
            for widget in self.search_anio_result_frame.winfo_children():
                widget.destroy()
            
            # Show results
            tk.Label(
                self.search_anio_result_frame,
                text=f"Resultados para el Año: {anio}",
                font=self.font_header,
                bg=Colors.BACKGROUND,
                fg=Colors.TEXT_PRIMARY
            ).pack(anchor='w', pady=(0, 10))
            
            # Summary
            summary = tk.Frame(self.search_anio_result_frame, bg=Colors.CARD_BG, padx=20, pady=15)
            summary.pack(fill='x', pady=(0, 10))
            
            total_ventas = total_year['SUM(monto)'] or 0
            cantidad_ventas = total_year['COUNT(*)'] or 0
            promedio_ventas = total_year['AVG(monto)'] or 0
            
            tk.Label(
                summary,
                text=f"Total del Año: ${total_ventas:.2f}  |  Total Ventas: {cantidad_ventas}  |  Promedio: ${promedio_ventas:.2f}",
                font=self.font_large,
                bg=Colors.CARD_BG,
                fg=Colors.TEXT_PRIMARY
            ).pack()
            
            # Monthly breakdown treeview
            tk.Label(
                self.search_anio_result_frame,
                text="Resumen por Mes:",
                font=self.font_medium,
                bg=Colors.BACKGROUND,
                fg=Colors.TEXT_PRIMARY
            ).pack(anchor='w', pady=(10, 5))
            
            columns = ('mes', 'cantidad', 'total', 'efectivo', 'transferencia', 'debito', 'credito')
            tree = ttk.Treeview(self.search_anio_result_frame, columns=columns, show='headings', height=12)
            
            nombres_meses = {
                '01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril',
                '05': 'Mayo', '06': 'Junio', '07': 'Julio', '08': 'Agosto',
                '09': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
            }
            
            headers = {'mes': 'Mes', 'cantidad': 'Ventas', 'total': 'Total', 
                      'efectivo': 'Efectivo', 'transferencia': 'Transf.', 'debito': 'Débito', 'credito': 'Crédito'}
            
            for col, header in headers.items():
                tree.heading(col, text=header)
                tree.column(col, width=100, anchor='center' if col != 'mes' else 'w')
            
            tree.column('mes', width=120)
            
            scrollbar = ttk.Scrollbar(self.search_anio_result_frame, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            for mes_data in meses_data:
                tree.insert('', 'end', values=(
                    nombres_meses.get(mes_data['mes'], mes_data['mes']),
                    mes_data['cantidad'],
                    f"${mes_data['total']:.2f}",
                    f"${mes_data['efectivo']:.2f}",
                    f"${mes_data['transferencia']:.2f}",
                    f"${mes_data['debito']:.2f}",
                    f"${mes_data['credito']:.2f}"
                ))
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al buscar: {str(e)}")
            logger.error(f"Error al buscar por año: {e}")
    
    def exportar_mes(self):
        """Export monthly report"""
        try:
            archivo = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")],
                initialfile=f"resumen_{datetime.now().strftime('%Y%m')}.json"
            )
            
            if archivo:
                datos = self.db.exportar_a_json()
                
                with open(archivo, 'w', encoding='utf-8') as f:
                    json.dump(datos, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("✅ Éxito", f"Datos exportados a:\n{archivo}")
                logger.info(f"Datos exportados: {archivo}")
        
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al exportar: {str(e)}")
            logger.error(f"Error al exportar: {e}")
    
    def load_initial_data(self):
        """Load initial data when app starts"""
        self.refresh_all()
    
    def refresh_all(self):
        """Refresh all data displays"""
        try:
            self.cargar_ventas_hoy()
            self.update_daily_report()
            self.update_monthly_report()
            self.cargar_fiados()
            self.cargar_clientes_en_combo_fiados()  # Refresh client filter
            self.update_status_bar()
            self.lbl_status.config(text="Datos actualizados")
            logger.info("Datos refrescados")
        except Exception as e:
            logger.error(f"Error al refrescar datos: {e}")
    
    def cargar_ventas_hoy(self):
        """Load today's sales"""
        # Clear treeview
        for item in self.tree_ventas.get_children():
            self.tree_ventas.delete(item)
        
        # Get data
        datos = self.db.obtener_resumen_diario()
        
        # Populate treeview
        for venta in datos['ventas']:
            hora = venta['fecha_hora'].split()[1] if venta['fecha_hora'] else ''
            self.tree_ventas.insert('', 'end', values=(
                hora,
                f"${venta['monto']:.2f}",
                venta['forma_pago'],
                venta['cliente'] or '-',
                venta['nota'] or '-'
            ))
    
    def update_daily_report(self):
        """Update daily report view"""
        datos = self.db.obtener_resumen_diario()
        
        # Update cards
        if hasattr(self, 'daily_total_label'):
            self.daily_total_label.config(text=f"${datos['total']:.2f}")
        
        if hasattr(self, 'daily_count_label'):
            self.daily_count_label.config(text=f"{datos['cantidad']} ventas")
        
        # Update payment breakdown
        if hasattr(self, 'daily_pagos_frame'):
            for widget in self.daily_pagos_frame.winfo_children()[1:]:  # Keep title
                widget.destroy()
            
            for forma_pago, info in datos['por_forma_pago'].items():
                tk.Label(
                    self.daily_pagos_frame,
                    text=f"{forma_pago}: ${info['total']:.2f} ({info['cantidad']} ventas)",
                    font=self.font_normal,
                    bg=Colors.CARD_BG,
                    fg=Colors.TEXT_SECONDARY
                ).pack(anchor='w', pady=2)
        
        # Update treeview
        if hasattr(self, 'tree_daily_report'):
            for item in self.tree_daily_report.get_children():
                self.tree_daily_report.delete(item)
            
            for venta in datos['ventas']:
                hora = venta['fecha_hora'].split()[1] if venta['fecha_hora'] else ''
                self.tree_daily_report.insert('', 'end', values=(
                    hora,
                    f"${venta['monto']:.2f}",
                    venta['forma_pago'],
                    venta['cliente'] or '-',
                    venta['nota'] or '-'
                ))
    
    def update_monthly_report(self):
        """Update monthly report view"""
        datos = self.db.obtener_resumen_mensual()
        
        # Update total card
        if hasattr(self, 'monthly_total_label'):
            self.monthly_total_label.config(
                text=f"${datos['total']:.2f}"
            )
        
        # Update treeview
        if hasattr(self, 'tree_mensual'):
            for item in self.tree_mensual.get_children():
                self.tree_mensual.delete(item)
            
            for dia in datos['por_dia']:
                self.tree_mensual.insert('', 'end', values=(
                    dia['dia'],
                    f"${dia['total']:.2f}",
                    f"${dia['efectivo']:.2f}",
                    f"${dia['transferencia']:.2f}",
                    f"${dia['debito']:.2f}",
                    f"${dia['credito']:.2f}"
                ))
    
    def cargar_fiados(self, estado=None):
        """Load fiados list with saldo pendiente"""
        # Clear treeview
        for item in self.tree_fiados.get_children():
            self.tree_fiados.delete(item)
        
        # Get data
        fiados = self.db.obtener_fiados(estado)
        stats = self.db.obtener_estadisticas_fiados()
        
        # Update total label
        if hasattr(self, 'lbl_total_fiados'):
            self.lbl_total_fiados.config(
                text=f"Total Pendiente General: ${stats['saldo_pendiente']:.2f}"
            )
        
        # Populate treeview with saldo
        for fiado in fiados:
            fecha = fiado['fecha_creacion'].split()[0] if fiado['fecha_creacion'] else ''
            
            # Calculate color tag based on status
            tag = ''
            if fiado['estado'] == EstadoFiado.PAGADO.value:
                tag = 'pagado'
            elif fiado['estado'] == EstadoFiado.PARCIAL.value:
                tag = 'parcial'
            
            item = self.tree_fiados.insert('', 'end', values=(
                fiado['id'],
                fecha,
                fiado['cliente_nombre'],
                f"${fiado['monto_total']:.2f}",
                f"{fiado['interes_porcentaje']}%",
                f"${fiado['monto_pagado']:.2f}",
                f"${fiado['saldo_pendiente']:.2f}",
                fiado['estado'],
                fiado['nota'] or '-'
            ), tags=(tag,))
        
        # Configure tags
        self.tree_fiados.tag_configure('pagado', foreground=Colors.SUCCESS)
        self.tree_fiados.tag_configure('parcial', foreground=Colors.WARNING)
    
    def cargar_fiados_filtrados(self, estado=None):
        """Load fiados with client filter applied"""
        cliente_nombre = self.combo_filtro_cliente_fiados.get()
        
        if cliente_nombre and cliente_nombre in self.clientes_dict_fiados:
            cliente_id = self.clientes_dict_fiados[cliente_nombre]
            self.filtro_cliente_id_actual = cliente_id
            
            # Update label
            self.lbl_cliente_seleccionado_fiados.config(
                text=f"Cliente: {cliente_nombre}",
                fg=Colors.PRIMARY
            )
            
            # Enable action buttons
            self.btn_aplicar_interes.config(state='normal')
            self.btn_pagar_todo.config(state='normal')
            
            # Load fiados for this client
            self.cargar_fiados_por_cliente(cliente_id, estado)
        else:
            self.filtro_cliente_id_actual = None
            self.lbl_cliente_seleccionado_fiados.config(
                text="Ningún cliente seleccionado",
                fg=Colors.TEXT_SECONDARY
            )
            self.btn_aplicar_interes.config(state='disabled')
            self.btn_pagar_todo.config(state='disabled')
            self.cargar_fiados(estado)
    
    def cargar_fiados_por_cliente(self, cliente_id, estado=None):
        """Load fiados for specific client"""
        # Clear treeview
        for item in self.tree_fiados.get_children():
            self.tree_fiados.delete(item)
        
        # Get data
        fiados = self.db.obtener_fiados(estado, cliente_id)
        
        # Calculate total for this client
        total_pendiente = sum(f['saldo_pendiente'] for f in fiados if f['estado'] in ['Pendiente', 'Parcial'])
        
        # Update total label
        if hasattr(self, 'lbl_total_fiados'):
            self.lbl_total_fiados.config(
                text=f"Total Pendiente del Cliente: ${total_pendiente:.2f}"
            )
        
        # Populate treeview
        for fiado in fiados:
            fecha = fiado['fecha_creacion'].split()[0] if fiado['fecha_creacion'] else ''
            
            tag = ''
            if fiado['estado'] == EstadoFiado.PAGADO.value:
                tag = 'pagado'
            elif fiado['estado'] == EstadoFiado.PARCIAL.value:
                tag = 'parcial'
            
            item = self.tree_fiados.insert('', 'end', values=(
                fiado['id'],
                fecha,
                fiado['cliente_nombre'],
                f"${fiado['monto_total']:.2f}",
                f"{fiado['interes_porcentaje']}%",
                f"${fiado['monto_pagado']:.2f}",
                f"${fiado['saldo_pendiente']:.2f}",
                fiado['estado'],
                fiado['nota'] or '-'
            ), tags=(tag,))
        
        # Configure tags
        self.tree_fiados.tag_configure('pagado', foreground=Colors.SUCCESS)
        self.tree_fiados.tag_configure('parcial', foreground=Colors.WARNING)
    
    def cargar_fiados_pendientes_y_parciales(self):
        """Load fiados with 'Pendiente' or 'Parcial' status"""
        # Clear treeview
        for item in self.tree_fiados.get_children():
            self.tree_fiados.delete(item)
        
        # Get client filter if applied
        cliente_id = None
        if hasattr(self, 'filtro_cliente_id_actual') and self.filtro_cliente_id_actual:
            cliente_id = self.filtro_cliente_id_actual
        
        # Get data - both Pendiente and Parcial
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT 
                    f.*,
                    CASE 
                        WHEN f.monto_pagado > 0 THEN ROUND((f.monto_pagado / f.monto_total) * 100, 1)
                        ELSE 0 
                    END as porcentaje_pagado
                FROM fiados f
                WHERE f.estado IN ('Pendiente', 'Parcial')
            '''
            params = []
            
            if cliente_id:
                query += " AND f.cliente_id = ?"
                params.append(cliente_id)
            
            query += " ORDER BY f.fecha_creacion DESC"
            
            cursor.execute(query, params)
            fiados = cursor.fetchall()
            
            # Calculate total
            if cliente_id:
                cursor.execute('''
                    SELECT SUM(saldo_pendiente) 
                    FROM fiados 
                    WHERE cliente_id = ? AND estado IN ('Pendiente', 'Parcial')
                ''', (cliente_id,))
            else:
                cursor.execute('''
                    SELECT SUM(saldo_pendiente) 
                    FROM fiados 
                    WHERE estado IN ('Pendiente', 'Parcial')
                ''')
            
            total_pendiente = cursor.fetchone()[0] or 0
        
        # Update label
        if hasattr(self, 'lbl_total_fiados'):
            if cliente_id:
                self.lbl_total_fiados.config(
                    text=f"Total Pendiente del Cliente: ${total_pendiente:.2f}",
                    fg=Colors.DANGER
                )
            else:
                self.lbl_total_fiados.config(
                    text=f"Total Pendiente General: ${total_pendiente:.2f}",
                    fg=Colors.DANGER
                )
        
        # Populate treeview
        for fiado in fiados:
            fecha = fiado['fecha_creacion'].split()[0] if fiado['fecha_creacion'] else ''
            
            tag = ''
            if fiado['estado'] == EstadoFiado.PAGADO.value:
                tag = 'pagado'
            elif fiado['estado'] == EstadoFiado.PARCIAL.value:
                tag = 'parcial'
            
            item = self.tree_fiados.insert('', 'end', values=(
                fiado['id'],
                fecha,
                fiado['cliente_nombre'],
                f"${fiado['monto_total']:.2f}",
                f"{fiado['interes_porcentaje']}%",
                f"${fiado['monto_pagado']:.2f}",
                f"${fiado['saldo_pendiente']:.2f}",
                fiado['estado'],
                fiado['nota'] or '-'
            ), tags=(tag,))
        
        # Configure tags
        self.tree_fiados.tag_configure('pagado', foreground=Colors.SUCCESS)
        self.tree_fiados.tag_configure('parcial', foreground=Colors.WARNING)
    
    def on_filtro_cliente_fiados_changed(self, event=None):
        """Handle client filter selection change"""
        self.cargar_fiados_filtrados(None)
    
    def actualizar_lista_fiados_con_filtro(self):
        """Update fiados list with current filter"""
        self.cargar_clientes_en_combo_fiados()
        self.cargar_fiados_filtrados(None)
    
    def limpiar_filtro_cliente_fiados(self):
        """Clear client filter"""
        self.combo_filtro_cliente_fiados.set('')
        self.filtro_cliente_id_actual = None
        self.lbl_cliente_seleccionado_fiados.config(
            text="Ningún cliente seleccionado",
            fg=Colors.TEXT_SECONDARY
        )
        self.btn_aplicar_interes.config(state='disabled')
        self.btn_pagar_todo.config(state='disabled')
        self.cargar_fiados()
    
    def cargar_clientes_en_combo_fiados(self):
        """Load clients into fiados filter combobox"""
        try:
            clientes = self.db.obtener_clientes()
            self.clientes_dict_fiados = {c['nombre']: c['id'] for c in clientes}
            self.combo_filtro_cliente_fiados['values'] = list(self.clientes_dict_fiados.keys())
        except Exception as e:
            logger.error(f"Error al cargar clientes en filtro: {e}")
    
    def aplicar_interes_masivo(self):
        """Apply interest to all pending/partial fiados of selected client"""
        if not hasattr(self, 'filtro_cliente_id_actual') or not self.filtro_cliente_id_actual:
            messagebox.showwarning("⚠️ Atención", "Por favor seleccione un cliente primero")
            return
        
        # Ask for interest percentage
        porcentaje = simpledialog.askfloat(
            "Aplicar Interés",
            "Ingrese el porcentaje de interés a aplicar:",
            minvalue=0.1,
            maxvalue=100
        )
        
        if porcentaje:
            try:
                resultado = self.db.aplicar_interes_fiados_cliente(
                    self.filtro_cliente_id_actual, 
                    porcentaje
                )
                
                msg = f"✅ Interés aplicado exitosamente!\n\n"
                msg += f"Porcentaje aplicado: {porcentaje}%\n"
                msg += f"Fiados actualizados: {resultado['fiados_actualizados']}\n"
                msg += f"Total de interés: ${resultado['total_interes_monto']:.2f}"
                
                messagebox.showinfo("✅ Éxito", msg)
                
                # Refresh views
                self.cargar_fiados_filtrados(None)
                
                # Refresh client balance in "Nuevo Fiado" tab if same client is selected
                if self.var_fiado_cliente_id.get() == self.filtro_cliente_id_actual:
                    self.actualizar_saldo_cliente(self.filtro_cliente_id_actual)
                
                logger.info(f"Interés aplicado: Cliente={self.filtro_cliente_id_actual}, {resultado['fiados_actualizados']} fiados")
                
            except Exception as e:
                messagebox.showerror("❌ Error", str(e))
                logger.error(f"Error al aplicar interés: {e}")
    
    def pagar_todos_fiados_cliente(self):
        """Pay all pending/partial fiados of selected client"""
        if not hasattr(self, 'filtro_cliente_id_actual') or not self.filtro_cliente_id_actual:
            messagebox.showwarning("⚠️ Atención", "Por favor seleccione un cliente primero")
            return
        
        # Get pending amount
        try:
            resumen = self.db.obtener_resumen_fiados_cliente(self.filtro_cliente_id_actual)
            saldo_pendiente = resumen['resumen_fiados']['saldo_pendiente']
            
            if saldo_pendiente <= 0:
                messagebox.showinfo("ℹ️ Información", "El cliente no tiene saldo pendiente")
                return
            
            # Ask for confirmation and amount
            monto = simpledialog.askfloat(
                "Pagar Todos los Fiados",
                f"El cliente tiene un saldo total pendiente de: ${saldo_pendiente:.2f}\n\n"
                f"Ingrese el monto total a pagar:",
                minvalue=saldo_pendiente - 0.01,
                maxvalue=saldo_pendiente + 0.01,
                initialvalue=saldo_pendiente
            )
            
            if monto:
                resultado = self.db.pagar_todos_fiados_cliente(
                    self.filtro_cliente_id_actual,
                    monto,
                    "Pago total de todos los fiados"
                )
                
                msg = f"✅ Pagos registrados exitosamente!\n\n"
                msg += f"Cliente: {resultado['cliente_nombre']}\n"
                msg += f"Total pagado: ${resultado['total_pagado']:.2f}\n"
                msg += f"Fiados pagados: {resultado['cantidad_fiados']}"
                
                messagebox.showinfo("✅ Éxito", msg)
                
                # Refresh views - mantener filtro del cliente
                self.cargar_fiados_filtrados(None)
                self.update_status_bar()
                
                # Refresh client balance in "Nuevo Fiado" tab
                if self.var_fiado_cliente_id.get() == self.filtro_cliente_id_actual:
                    self.actualizar_saldo_cliente(self.filtro_cliente_id_actual)
                
                # Mostrar mensaje si el cliente ya no tiene fiados pendientes
                # pero mantener el filtro activo para que vea el historial
                self.lbl_total_fiados.config(
                    text=f"✅ Cliente al día - Sin fiados pendientes",
                    fg=Colors.SUCCESS
                )
                
                logger.info(f"Pago masivo: Cliente={resultado['cliente_nombre']}, ${resultado['total_pagado']}, {resultado['cantidad_fiados']} fiados")
                
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
            logger.error(f"Error al pagar fiados: {e}")
    
    def ver_detalle_fiado(self):
        """Show fiado details with payment history"""
        selection = self.tree_fiados.selection()
        if not selection:
            messagebox.showwarning("⚠️ Atención", "Por favor seleccione un fiado")
            return
        
        item = self.tree_fiados.item(selection[0])
        fiado_id = int(item['values'][0])
        cliente = item['values'][2]
        monto_total = item['values'][3]
        pagado = item['values'][5]
        saldo = item['values'][6]
        estado = item['values'][7]
        
        # Create popup
        popup = tk.Toplevel(self.root)
        popup.title(f"Detalle de Fiado - {cliente}")
        popup.geometry("600x500")
        
        # Summary
        tk.Label(
            popup,
            text=f"Cliente: {cliente}",
            font=self.font_header
        ).pack(pady=5)
        
        tk.Label(
            popup,
            text=f"Monto Total: {monto_total}  |  Pagado: {pagado}  |  Saldo: {saldo}",
            font=self.font_large
        ).pack(pady=5)
        
        tk.Label(
            popup,
            text=f"Estado: {estado}",
            font=self.font_medium,
            fg=Colors.SUCCESS if estado == 'Pagado' else Colors.DANGER if estado == 'Pendiente' else Colors.WARNING
        ).pack(pady=5)
        
        # Payment history
        tk.Label(
            popup,
            text="Historial de Pagos:",
            font=self.font_medium
        ).pack(anchor='w', padx=20, pady=(20, 10))
        
        historial = self.db.obtener_historial_fiado(fiado_id)
        
        tree = ttk.Treeview(popup, columns=('fecha', 'monto', 'nota'), show='headings', height=10)
        tree.heading('fecha', text='Fecha y Hora')
        tree.heading('monto', text='Monto')
        tree.heading('nota', text='Nota')
        tree.column('fecha', width=150)
        tree.column('monto', width=100)
        tree.column('nota', width=300)
        
        total_pagos = 0
        for pago in historial:
            tree.insert('', 'end', values=(
                pago['fecha_pago'],
                f"${pago['monto']:.2f}",
                pago['nota'] or '-'
            ))
            total_pagos += pago['monto']
        
        tree.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Total payments
        tk.Label(
            popup,
            text=f"Total de pagos realizados: ${total_pagos:.2f} ({len(historial)} pagos)",
            font=self.font_medium,
            fg=Colors.PRIMARY
        ).pack(pady=10)
        
        tk.Button(
            popup,
            text="Cerrar",
            command=popup.destroy,
            font=self.font_medium
        ).pack(pady=10)
    
    def cargar_historial_cliente(self, event=None):
        """Load payment history for selected client"""
        nombre = self.combo_historial_cliente.get()
        if not nombre or nombre not in self.historial_clientes_dict:
            return
        
        cliente_id = self.historial_clientes_dict[nombre]
        
        try:
            # Clear treeview
            for item in self.tree_historial.get_children():
                self.tree_historial.delete(item)
            
            # Get data
            historial = self.db.obtener_historial_pagos_cliente(cliente_id)
            
            # Update summary
            self.lbl_historial_cliente.config(text=f"Cliente: {historial['cliente_nombre']}")
            
            total_pagado = historial['total_pagado_general']
            cantidad_pagos = historial['total_pagos_realizados']
            
            resumen_text = f"Total de fiados: {historial['total_fiados']}  |  "
            resumen_text += f"Pagos realizados: {cantidad_pagos}  |  "
            resumen_text += f"Monto total pagado: ${total_pagado:.2f}"
            
            self.lbl_historial_totales.config(text=resumen_text)
            
            # Populate treeview
            for fiado in historial['fiados']:
                for pago in fiado['pagos']:
                    self.tree_historial.insert('', 'end', values=(
                        pago['fecha_pago'],
                        f"#{fiado['fiado_id']}",
                        f"${pago['monto']:.2f}",
                        pago['nota'] or '-'
                    ))
            
            logger.info(f"Historial cargado: Cliente={nombre}, Pagos={cantidad_pagos}")
            
        except Exception as e:
            logger.error(f"Error al cargar historial: {e}")
            messagebox.showerror("❌ Error", f"No se pudo cargar el historial: {e}")
    
    def update_status_bar(self):
        """Update status bar with totals"""
        try:
            ventas_hoy = self.db.obtener_resumen_diario()
            stats_fiados = self.db.obtener_estadisticas_fiados()
            
            self.lbl_totals.config(
                text=f"💰 Hoy: ${ventas_hoy['total']:.2f}  |  "
                     f"📒 Fiados pendientes: ${stats_fiados['saldo_pendiente']:.2f}"
            )
        except Exception as e:
            logger.error(f"Error al actualizar barra de estado: {e}")


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set DPI awareness for Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = KioscoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
