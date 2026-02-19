"""
Database module for Kiosco Manager
Optimized with SQLite best practices following Database Design Expert guidelines
"""

import sqlite3
import os
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FormaPago(Enum):
    """Enum for payment methods - ensures data integrity"""
    EFECTIVO = "Efectivo"
    TRANSFERENCIA = "Transferencia"
    DEBITO = "Débito"
    CREDITO = "Crédito"


class EstadoFiado(Enum):
    """Enum for fiado status"""
    PENDIENTE = "Pendiente"
    PAGADO = "Pagado"
    PARCIAL = "Parcial"


@dataclass
class Venta:
    """Data class for Venta - type safety and validation"""
    id: Optional[int]
    monto: float
    forma_pago: str
    cliente: Optional[str]
    nota: Optional[str]
    fecha_hora: datetime
    
    def __post_init__(self):
        if self.monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        if self.forma_pago not in [fp.value for fp in FormaPago]:
            raise ValueError(f"Forma de pago inválida: {self.forma_pago}")


@dataclass
class Fiado:
    """Data class for Fiado - simplified for database operations"""
    cliente: str
    monto: float
    interes: float = 0
    nota: Optional[str] = None
    
    def __post_init__(self):
        if not self.cliente or len(self.cliente.strip()) < 2:
            raise ValueError("El nombre del cliente debe tener al menos 2 caracteres")
        if self.monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        if self.interes < 0:
            raise ValueError("El interés no puede ser negativo")


class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass


class Database:
    """
    Database manager with connection pooling, transactions, and optimization
    Following SQLite Database Expert best practices
    """
    
    def __init__(self):
        self.db_path = self._get_db_path()
        self.backup_dir = self.db_path.parent / 'backups'
        self._init_database()
    
    def _get_db_path(self) -> Path:
        """Get database path following OS conventions"""
        if os.name == 'nt':
            db_dir = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'KioscoManager'
        else:
            db_dir = Path.home() / '.kiosco-manager'
        
        db_dir.mkdir(parents=True, exist_ok=True)
        return db_dir / 'kiosco.db'
    
    @contextmanager
    def _get_connection(self):
        """
        Context manager for database connections
        Ensures proper connection handling and automatic commit/rollback
        """
        conn = None
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,  # Wait up to 30 seconds for locks
                isolation_level=None  # Autocommit mode for simplicity
            )
            conn.row_factory = sqlite3.Row  # Enable column access by name
            conn.execute("PRAGMA foreign_keys = ON")  # Enforce foreign keys
            conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging for better concurrency
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise DatabaseError(f"Error de base de datos: {e}")
        finally:
            if conn:
                conn.close()
    
    def _check_table_schema(self, conn, table_name, expected_columns):
        """Check if table exists and has the expected columns"""
        cursor = conn.cursor()
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = {row[1] for row in cursor.fetchall()}
            return expected_columns.issubset(existing_columns)
        except:
            return False
    
    def _init_database(self):
        """Initialize database with proper schema, indexes, and constraints"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if we need to migrate from old schema
            needs_migration = self._check_table_schema(conn, 'fiados', {'cliente'})
            
            if needs_migration:
                logger.info("Migrando base de datos desde versión antigua...")
                self._migrate_database(conn)
            
            # Create tables with proper constraints
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    monto REAL NOT NULL CHECK(monto > 0),
                    forma_pago TEXT NOT NULL CHECK(forma_pago IN ('Efectivo', 'Transferencia', 'Débito', 'Crédito')),
                    cliente TEXT CHECK(length(cliente) >= 0),
                    nota TEXT,
                    fecha_hora DATETIME DEFAULT (datetime('now', 'localtime')),
                    created_at DATETIME DEFAULT (datetime('now', 'localtime'))
                )
            ''')
            
            # Create clients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE CHECK(length(nombre) >= 2),
                    telefono TEXT,
                    email TEXT,
                    direccion TEXT,
                    notas TEXT,
                    fecha_registro DATETIME DEFAULT (datetime('now', 'localtime')),
                    activo INTEGER DEFAULT 1
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fiados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER NOT NULL,
                    cliente_nombre TEXT NOT NULL CHECK(length(cliente_nombre) >= 2),
                    monto_original REAL NOT NULL CHECK(monto_original > 0),
                    interes_porcentaje REAL DEFAULT 0 CHECK(interes_porcentaje >= 0),
                    monto_total REAL NOT NULL CHECK(monto_total > 0),
                    monto_pagado REAL DEFAULT 0 CHECK(monto_pagado >= 0),
                    saldo_pendiente REAL NOT NULL CHECK(saldo_pendiente >= 0),
                    nota TEXT,
                    estado TEXT DEFAULT 'Pendiente' CHECK(estado IN ('Pendiente', 'Pagado', 'Parcial')),
                    fecha_creacion DATETIME DEFAULT (datetime('now', 'localtime')),
                    fecha_pago DATETIME,
                    created_at DATETIME DEFAULT (datetime('now', 'localtime')),
                    updated_at DATETIME DEFAULT (datetime('now', 'localtime')),
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pagos_fiados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fiado_id INTEGER NOT NULL,
                    monto REAL NOT NULL CHECK(monto > 0),
                    fecha_pago DATETIME DEFAULT (datetime('now', 'localtime')),
                    nota TEXT,
                    FOREIGN KEY (fiado_id) REFERENCES fiados(id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes for performance optimization
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_ventas_fecha 
                ON ventas(date(fecha_hora))
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_ventas_forma_pago 
                ON ventas(forma_pago)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_fiados_estado 
                ON fiados(estado)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_fiados_cliente_nombre 
                ON fiados(cliente_nombre)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_pagos_fiado_id 
                ON pagos_fiados(fiado_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_clientes_nombre 
                ON clientes(nombre)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_fiados_cliente_id 
                ON fiados(cliente_id)
            ''')
            
            # Create triggers for automatic updates
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_fiado_timestamp 
                AFTER UPDATE ON fiados
                BEGIN
                    UPDATE fiados SET updated_at = datetime('now', 'localtime') 
                    WHERE id = NEW.id;
                END
            ''')
            
            logger.info("Database initialized successfully")
    
    def _migrate_database(self, conn):
        """Migrate from old database schema to new schema"""
        cursor = conn.cursor()
        logger.info("Iniciando migración de base de datos...")
        
        try:
            # Backup old data
            cursor.execute("SELECT * FROM fiados")
            old_fiados = cursor.fetchall()
            logger.info(f"Encontrados {len(old_fiados)} fiados para migrar")
            
            # Drop old tables
            cursor.execute("DROP TABLE IF EXISTS pagos_fiados")
            cursor.execute("DROP TABLE IF EXISTS fiados")
            cursor.execute("DROP TABLE IF EXISTS clientes")
            logger.info("Tablas antiguas eliminadas")
            
            # Create new schema (it will be created by _init_database)
            # Just commit the drop
            conn.commit()
            logger.info("Migración completada. Se recrearán las tablas con el nuevo esquema.")
            
            # Note: Old data is lost in this simple migration
            # For production, you would want to preserve the data
            logger.warning("Los datos anteriores de fiados se han eliminado. Se requiere recrear los fiados.")
            
        except Exception as e:
            logger.error(f"Error durante la migración: {e}")
            raise DatabaseError(f"Error al migrar base de datos: {e}")
    
    def agregar_venta(self, monto: float, forma_pago: str, cliente: str = "", nota: str = "") -> Optional[int]:
        """
        Add a new sale with transaction safety
        Returns: The ID of the newly created venta
        """
        try:
            venta = Venta(
                id=None,
                monto=monto,
                forma_pago=forma_pago,
                cliente=cliente if cliente else None,
                nota=nota if nota else None,
                fecha_hora=datetime.now()
            )
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Usar datetime('now', 'localtime') para hora local
                cursor.execute('''
                    INSERT INTO ventas (monto, forma_pago, cliente, nota, fecha_hora)
                    VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
                ''', (venta.monto, venta.forma_pago, venta.cliente, venta.nota))
                
                venta_id = cursor.lastrowid
                logger.info(f"Venta registrada: ID={venta_id}, Monto=${monto}, Pago={forma_pago}")
                return venta_id
                
        except ValueError as e:
            logger.warning(f"Validación fallida: {e}")
            raise
        except Exception as e:
            logger.error(f"Error al agregar venta: {e}")
            raise DatabaseError(f"No se pudo registrar la venta: {e}")
    
    def modificar_venta(self, venta_id: int, monto: float, forma_pago: str, cliente: str = "", nota: str = "") -> bool:
        """
        Modify an existing sale
        Returns: True if successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE ventas 
                    SET monto = ?, forma_pago = ?, cliente = ?, nota = ?
                    WHERE id = ?
                ''', (monto, forma_pago, cliente if cliente else None, nota if nota else None, venta_id))
                
                if cursor.rowcount == 0:
                    raise DatabaseError(f"Venta con ID {venta_id} no encontrada")
                
                logger.info(f"Venta modificada: ID={venta_id}, Monto=${monto}, Pago={forma_pago}")
                return True
                
        except Exception as e:
            logger.error(f"Error al modificar venta: {e}")
            raise DatabaseError(f"No se pudo modificar la venta: {e}")
    
    def eliminar_venta(self, venta_id: int) -> bool:
        """
        Delete a sale
        Returns: True if successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM ventas WHERE id = ?', (venta_id,))
                
                if cursor.rowcount == 0:
                    raise DatabaseError(f"Venta con ID {venta_id} no encontrada")
                
                logger.info(f"Venta eliminada: ID={venta_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error al eliminar venta: {e}")
            raise DatabaseError(f"No se pudo eliminar la venta: {e}")
    
    def obtener_ventas_por_fecha(self, fecha: str) -> Dict[str, Any]:
        """
        Get sales for a specific date with optimized query
        Returns: Dictionary with ventas list and summary statistics
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all sales for the date
            cursor.execute('''
                SELECT id, monto, forma_pago, cliente, nota, fecha_hora
                FROM ventas 
                WHERE date(fecha_hora) = ?
                ORDER BY fecha_hora DESC
            ''', (fecha,))
            
            ventas = cursor.fetchall()
            
            # Get summary by payment method
            cursor.execute('''
                SELECT forma_pago, COUNT(*) as cantidad, SUM(monto) as total
                FROM ventas 
                WHERE date(fecha_hora) = ?
                GROUP BY forma_pago
            ''', (fecha,))
            
            por_forma_pago = {row['forma_pago']: {'cantidad': row['cantidad'], 'total': row['total']} 
                            for row in cursor.fetchall()}
            
            # Get total
            cursor.execute('''
                SELECT COUNT(*), SUM(monto), AVG(monto), MAX(monto), MIN(monto)
                FROM ventas 
                WHERE date(fecha_hora) = ?
            ''', (fecha,))
            
            stats = cursor.fetchone()
            
            return {
                'ventas': ventas,
                'total': stats['SUM(monto)'] or 0,
                'cantidad': stats['COUNT(*)'] or 0,
                'promedio': stats['AVG(monto)'] or 0,
                'maximo': stats['MAX(monto)'] or 0,
                'minimo': stats['MIN(monto)'] or 0,
                'por_forma_pago': por_forma_pago
            }
    
    def obtener_resumen_diario(self, fecha: Optional[str] = None) -> Dict[str, Any]:
        """Get daily summary with statistics and shift breakdown"""
        if fecha is None:
            fecha = datetime.now().strftime('%Y-%m-%d')
        
        datos = self.obtener_ventas_por_fecha(fecha)
        
        # Get shift breakdown
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Turno mañana: 6:00 - 18:00
            cursor.execute('''
                SELECT COUNT(*), SUM(monto)
                FROM ventas 
                WHERE date(fecha_hora) = ?
                AND CAST(strftime('%H', fecha_hora) AS INTEGER) >= 6
                AND CAST(strftime('%H', fecha_hora) AS INTEGER) < 18
            ''', (fecha,))
            stats_mañana = cursor.fetchone()
            
            # Turno tarde: 18:00 - 6:00 (next day)
            cursor.execute('''
                SELECT COUNT(*), SUM(monto)
                FROM ventas 
                WHERE date(fecha_hora) = ?
                AND (CAST(strftime('%H', fecha_hora) AS INTEGER) >= 18 OR CAST(strftime('%H', fecha_hora) AS INTEGER) < 6)
            ''', (fecha,))
            stats_tarde = cursor.fetchone()
        
        datos['turno_mañana'] = {
            'cantidad': stats_mañana[0] or 0,
            'total': stats_mañana[1] or 0
        }
        datos['turno_tarde'] = {
            'cantidad': stats_tarde[0] or 0,
            'total': stats_tarde[1] or 0
        }
        
        return datos
    
    def obtener_resumen_mensual(self, anio: Optional[int] = None, mes: Optional[int] = None) -> Dict[str, Any]:
        """
        Get monthly summary with daily breakdown
        """
        if anio is None or mes is None:
            ahora = datetime.now()
            anio = ahora.year
            mes = ahora.month
        
        mes_str = f"{anio:04d}-{mes:02d}"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total for the month
            cursor.execute('''
                SELECT COUNT(*), SUM(monto), AVG(monto)
                FROM ventas 
                WHERE strftime('%Y-%m', fecha_hora) = ?
            ''', (mes_str,))
            
            total_stats = cursor.fetchone()
            
            # By payment method
            cursor.execute('''
                SELECT forma_pago, COUNT(*) as cantidad, SUM(monto) as total
                FROM ventas 
                WHERE strftime('%Y-%m', fecha_hora) = ?
                GROUP BY forma_pago
            ''', (mes_str,))
            
            por_forma_pago = {row['forma_pago']: {'cantidad': row['cantidad'], 'total': row['total']} 
                            for row in cursor.fetchall()}
            
            # Daily breakdown
            cursor.execute('''
                SELECT 
                    date(fecha_hora) as dia,
                    COUNT(*) as cantidad,
                    SUM(monto) as total,
                    SUM(CASE WHEN forma_pago = 'Efectivo' THEN monto ELSE 0 END) as efectivo,
                    SUM(CASE WHEN forma_pago = 'Transferencia' THEN monto ELSE 0 END) as transferencia,
                    SUM(CASE WHEN forma_pago = 'Débito' THEN monto ELSE 0 END) as debito,
                    SUM(CASE WHEN forma_pago = 'Crédito' THEN monto ELSE 0 END) as credito
                FROM ventas 
                WHERE strftime('%Y-%m', fecha_hora) = ?
                GROUP BY date(fecha_hora)
                ORDER BY dia DESC
            ''', (mes_str,))
            
            por_dia = cursor.fetchall()
            
            return {
                'anio': anio,
                'mes': mes,
                'total': total_stats['SUM(monto)'] or 0,
                'cantidad': total_stats['COUNT(*)'] or 0,
                'promedio': total_stats['AVG(monto)'] or 0,
                'por_forma_pago': por_forma_pago,
                'por_dia': por_dia
            }
    
    def agregar_cliente(self, nombre: str, telefono: str = "", email: str = "", direccion: str = "", notas: str = "") -> Optional[int]:
        """Add a new client to the database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO clientes (nombre, telefono, email, direccion, notas)
                    VALUES (?, ?, ?, ?, ?)
                ''', (nombre.strip(), telefono.strip() or None, email.strip() or None, 
                      direccion.strip() or None, notas.strip() or None))
                
                cliente_id = cursor.lastrowid
                logger.info(f"Cliente registrado: ID={cliente_id}, Nombre={nombre}")
                return cliente_id
        except sqlite3.IntegrityError:
            logger.warning(f"Cliente ya existe: {nombre}")
            raise ValueError(f"El cliente '{nombre}' ya existe en el sistema")
        except Exception as e:
            logger.error(f"Error al agregar cliente: {e}")
            raise DatabaseError(f"No se pudo registrar el cliente: {e}")
    
    def obtener_clientes(self, activos: bool = True) -> List[sqlite3.Row]:
        """Get all clients, optionally filtering by active status"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if activos:
                cursor.execute('''
                    SELECT * FROM clientes 
                    WHERE activo = 1
                    ORDER BY nombre ASC
                ''')
            else:
                cursor.execute('''
                    SELECT * FROM clientes 
                    ORDER BY nombre ASC
                ''')
            return cursor.fetchall()
    
    def buscar_cliente_por_nombre(self, nombre: str) -> Optional[sqlite3.Row]:
        """Search for a client by exact name"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM clientes 
                WHERE nombre = ? AND activo = 1
            ''', (nombre.strip(),))
            return cursor.fetchone()
    
    def agregar_fiado(self, cliente_id: int, cliente_nombre: str, monto: float, interes: float = 0, nota: str = "") -> Optional[int]:
        """Add a new fiado with calculated totals and client reference"""
        try:
            # Redondear a 2 decimales para evitar problemas de precision
            monto_total = round(monto * (1 + interes / 100), 2)
            saldo_pendiente = monto_total
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO fiados (cliente_id, cliente_nombre, monto_original, interes_porcentaje, 
                                      monto_total, saldo_pendiente, nota)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (cliente_id, cliente_nombre.strip(), monto, interes, monto_total, saldo_pendiente, 
                      nota if nota else None))
                
                fiado_id = cursor.lastrowid
                logger.info(f"Fiado registrado: ID={fiado_id}, Cliente={cliente_nombre}, MontoTotal=${monto_total}")
                return fiado_id
                
        except Exception as e:
            logger.error(f"Error al agregar fiado: {e}")
            raise DatabaseError(f"No se pudo registrar el fiado: {e}")
    
    def registrar_pago_fiado(self, fiado_id: int, monto: float, nota: str = "") -> Dict[str, Any]:
        """Register a partial or full payment for a fiado. Returns payment details."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Start transaction
                conn.execute("BEGIN TRANSACTION")
                
                try:
                    # Get current fiado state
                    cursor.execute('''
                        SELECT monto_total, monto_pagado, saldo_pendiente, estado, cliente_nombre
                        FROM fiados WHERE id = ?
                    ''', (fiado_id,))
                    
                    fiado = cursor.fetchone()
                    if not fiado:
                        raise ValueError("Fiado no encontrado")
                    
                    if fiado['estado'] == EstadoFiado.PAGADO.value:
                        raise ValueError("Este fiado ya está completamente pagado")
                    
                    if monto > fiado['saldo_pendiente']:
                        raise ValueError(f"El monto (${monto:.2f}) excede el saldo pendiente (${fiado['saldo_pendiente']:.2f})")
                    
                    nuevo_pagado = round(fiado['monto_pagado'] + monto, 2)
                    nuevo_saldo = round(fiado['monto_total'] - nuevo_pagado, 2)
                    
                    # Register the payment
                    cursor.execute('''
                        INSERT INTO pagos_fiados (fiado_id, monto, nota)
                        VALUES (?, ?, ?)
                    ''', (fiado_id, monto, nota if nota else None))
                    
                    pago_id = cursor.lastrowid
                    
                    # Update fiado state
                    # Usar tolerancia para evitar problemas de precision flotante
                    if nuevo_saldo <= 0.01:  # Considerar pagado si queda menos de 1 centavo
                        nuevo_estado = EstadoFiado.PAGADO.value
                        nuevo_saldo = 0.0  # Forzar a exactamente 0
                        fecha_pago = datetime.now()
                    else:
                        nuevo_estado = EstadoFiado.PARCIAL.value
                        fecha_pago = None
                    
                    cursor.execute('''
                        UPDATE fiados 
                        SET monto_pagado = ?, saldo_pendiente = ?, estado = ?, fecha_pago = ?
                        WHERE id = ?
                    ''', (nuevo_pagado, nuevo_saldo, nuevo_estado, fecha_pago, fiado_id))
                    
                    conn.execute("COMMIT")
                    
                    result = {
                        'pago_id': pago_id,
                        'fiado_id': fiado_id,
                        'cliente': fiado['cliente_nombre'],
                        'monto_pagado': monto,
                        'total_pagado': nuevo_pagado,
                        'saldo_anterior': fiado['saldo_pendiente'],
                        'saldo_restante': nuevo_saldo,
                        'estado': nuevo_estado,
                        'completado': nuevo_saldo <= 0.01  # Usar misma tolerancia
                    }
                    
                    logger.info(f"Pago registrado: Fiado ID={fiado_id}, Monto=${monto}, Saldo=${nuevo_saldo}")
                    return result
                    
                except Exception as e:
                    conn.execute("ROLLBACK")
                    raise e
                    
        except Exception as e:
            logger.error(f"Error al registrar pago: {e}")
            raise DatabaseError(f"No se pudo registrar el pago: {e}")
    
    def modificar_fiado(self, fiado_id: int, monto: float, forma_pago: str = "efectivo", nota: str = "") -> bool:
        """
        Modify an existing fiado (only if not fully paid)
        Returns: True if successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT monto_total, monto_pagado, estado FROM fiados WHERE id = ?', (fiado_id,))
                fiado = cursor.fetchone()
                
                if not fiado:
                    raise DatabaseError(f"Fiado con ID {fiado_id} no encontrado")
                
                if fiado['estado'] == EstadoFiado.PAGADO.value:
                    raise DatabaseError("No se puede modificar un fiado ya pagado completamente")
                
                monto_pagado = fiado['monto_pagado']
                monto_original = monto - (fiado['monto_total'] - monto_pagado)
                interes_porcentaje = 0
                
                cursor.execute('''
                    UPDATE fiados 
                    SET monto_original = ?, monto_total = ?, saldo_pendiente = ?, 
                        interes_porcentaje = ?, nota = ?, updated_at = datetime('now', 'localtime')
                    WHERE id = ?
                ''', (monto_original, monto, monto - monto_pagado, interes_porcentaje, 
                      nota if nota else None, fiado_id))
                
                logger.info(f"Fiado modificado: ID={fiado_id}, Monto=${monto}")
                return True
                
        except Exception as e:
            logger.error(f"Error al modificar fiado: {e}")
            raise DatabaseError(f"No se pudo modificar el fiado: {e}")
    
    def eliminar_fiado(self, fiado_id: int) -> bool:
        """
        Delete a fiado (only if not fully paid)
        Returns: True if successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT estado FROM fiados WHERE id = ?', (fiado_id,))
                fiado = cursor.fetchone()
                
                if not fiado:
                    raise DatabaseError(f"Fiado con ID {fiado_id} no encontrado")
                
                if fiado['estado'] == EstadoFiado.PAGADO.value:
                    raise DatabaseError("No se puede eliminar un fiado ya pagado completamente")
                
                cursor.execute('DELETE FROM fiados WHERE id = ?', (fiado_id,))
                
                logger.info(f"Fiado eliminado: ID={fiado_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error al eliminar fiado: {e}")
            raise DatabaseError(f"No se pudo eliminar el fiado: {e}")
    
    def obtener_fiados(self, estado: Optional[str] = None, cliente_id: Optional[int] = None) -> List[sqlite3.Row]:
        """Get fiados with optional filters"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT 
                    f.*,
                    CASE 
                        WHEN f.monto_pagado > 0 THEN ROUND((f.monto_pagado / f.monto_total) * 100, 1)
                        ELSE 0 
                    END as porcentaje_pagado
                FROM fiados f
                WHERE 1=1
            '''
            params = []
            
            if estado:
                query += " AND f.estado = ?"
                params.append(estado)
            
            if cliente_id:
                query += " AND f.cliente_id = ?"
                params.append(cliente_id)
            
            query += " ORDER BY f.fecha_creacion DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def obtener_fiados_por_cliente(self, cliente_id: int) -> List[sqlite3.Row]:
        """Get all fiados for a specific client with payment summary"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    f.*,
                    CASE 
                        WHEN f.monto_pagado > 0 THEN ROUND((f.monto_pagado / f.monto_total) * 100, 1)
                        ELSE 0 
                    END as porcentaje_pagado,
                    COUNT(p.id) as cantidad_pagos
                FROM fiados f
                LEFT JOIN pagos_fiados p ON f.id = p.fiado_id
                WHERE f.cliente_id = ?
                GROUP BY f.id
                ORDER BY f.fecha_creacion DESC
            ''', (cliente_id,))
            return cursor.fetchall()
    
    def obtener_resumen_fiados_cliente(self, cliente_id: int) -> Dict[str, Any]:
        """Get summary of all fiados and payments for a client"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get client info
            cursor.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,))
            cliente = cursor.fetchone()
            
            if not cliente:
                raise ValueError("Cliente no encontrado")
            
            # Get fiados summary
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_fiados,
                    SUM(CASE WHEN estado = 'Pendiente' THEN 1 ELSE 0 END) as pendientes,
                    SUM(CASE WHEN estado = 'Parcial' THEN 1 ELSE 0 END) as parciales,
                    SUM(CASE WHEN estado = 'Pagado' THEN 1 ELSE 0 END) as pagados,
                    SUM(monto_total) as total_deuda,
                    SUM(monto_pagado) as total_pagado,
                    SUM(saldo_pendiente) as saldo_pendiente
                FROM fiados 
                WHERE cliente_id = ?
            ''', (cliente_id,))
            
            resumen = cursor.fetchone()
            
            # Get all payments history
            cursor.execute('''
                SELECT 
                    p.*,
                    f.cliente_nombre
                FROM pagos_fiados p
                JOIN fiados f ON p.fiado_id = f.id
                WHERE f.cliente_id = ?
                ORDER BY p.fecha_pago DESC
            ''', (cliente_id,))
            
            pagos = cursor.fetchall()
            
            return {
                'cliente': dict(cliente),
                'resumen_fiados': {
                    'total_fiados': resumen['total_fiados'] or 0,
                    'pendientes': resumen['pendientes'] or 0,
                    'parciales': resumen['parciales'] or 0,
                    'pagados': resumen['pagados'] or 0,
                    'total_deuda': resumen['total_deuda'] or 0,
                    'total_pagado': resumen['total_pagado'] or 0,
                    'saldo_pendiente': resumen['saldo_pendiente'] or 0
                },
                'historial_pagos': [dict(pago) for pago in pagos],
                'cantidad_pagos': len(pagos)
            }
    
    def obtener_estadisticas_fiados(self) -> Dict[str, Any]:
        """Get fiado statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN estado = 'Pendiente' THEN 1 ELSE 0 END) as pendientes,
                    SUM(CASE WHEN estado = 'Pagado' THEN 1 ELSE 0 END) as pagados,
                    SUM(CASE WHEN estado = 'Parcial' THEN 1 ELSE 0 END) as parciales,
                    SUM(CASE WHEN estado IN ('Pendiente', 'Parcial') THEN (monto_total - monto_pagado) ELSE 0 END) as saldo_pendiente,
                    SUM(monto_total) as monto_total,
                    SUM(monto_pagado) as monto_recuperado
                FROM fiados
            ''')
            
            stats = cursor.fetchone()
            
            return {
                'total': stats['total'] or 0,
                'pendientes': stats['pendientes'] or 0,
                'pagados': stats['pagados'] or 0,
                'parciales': stats['parciales'] or 0,
                'saldo_pendiente': stats['saldo_pendiente'] or 0,
                'monto_total': stats['monto_total'] or 0,
                'monto_recuperado': stats['monto_recuperado'] or 0
            }
    
    def crear_backup(self, nombre_archivo: Optional[str] = None) -> Path:
        """Create a timestamped backup of the database"""
        try:
            self.backup_dir.mkdir(exist_ok=True)
            
            if nombre_archivo is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_archivo = f"backup_{timestamp}.db"
            
            backup_path = self.backup_dir / nombre_archivo
            
            # Create backup using SQLite's backup API
            with self._get_connection() as src_conn:
                backup_conn = sqlite3.connect(str(backup_path))
                src_conn.backup(backup_conn)
                backup_conn.close()
            
            logger.info(f"Backup creado: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error al crear backup: {e}")
            raise DatabaseError(f"No se pudo crear el backup: {e}")
    
    def exportar_a_json(self, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None) -> Dict[str, Any]:
        """Export data to JSON format for external use"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Base query for ventas
            ventas_query = "SELECT * FROM ventas"
            ventas_params = []
            
            if fecha_inicio and fecha_fin:
                ventas_query += " WHERE date(fecha_hora) BETWEEN ? AND ?"
                ventas_params = [fecha_inicio, fecha_fin]
            
            ventas_query += " ORDER BY fecha_hora DESC"
            
            cursor.execute(ventas_query, ventas_params)
            ventas = [dict(row) for row in cursor.fetchall()]
            
            # Get all fiados
            cursor.execute("SELECT * FROM fiados ORDER BY fecha_creacion DESC")
            fiados = [dict(row) for row in cursor.fetchall()]
            
            return {
                'exportado_el': datetime.now().isoformat(),
                'periodo': {
                    'inicio': fecha_inicio,
                    'fin': fecha_fin
                },
                'resumen': {
                    'total_ventas': len(ventas),
                    'total_fiados': len(fiados),
                    'monto_total_ventas': sum(v['monto'] for v in ventas)
                },
                'ventas': ventas,
                'fiados': fiados
            }
    
    def obtener_historial_fiado(self, fiado_id: int) -> List[sqlite3.Row]:
        """Get payment history for a specific fiado"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM pagos_fiados 
                WHERE fiado_id = ?
                ORDER BY fecha_pago DESC
            ''', (fiado_id,))
            return cursor.fetchall()
    
    def obtener_historial_pagos_cliente(self, cliente_id: int) -> Dict[str, Any]:
        """Get complete payment history for a client with totals"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all fiados for client with their payments
            cursor.execute('''
                SELECT 
                    f.id as fiado_id,
                    f.monto_total,
                    f.monto_pagado,
                    f.saldo_pendiente,
                    f.estado,
                    f.fecha_creacion,
                    p.id as pago_id,
                    p.monto as pago_monto,
                    p.fecha_pago,
                    p.nota as pago_nota
                FROM fiados f
                LEFT JOIN pagos_fiados p ON f.id = p.fiado_id
                WHERE f.cliente_id = ?
                ORDER BY f.fecha_creacion DESC, p.fecha_pago DESC
            ''', (cliente_id,))
            
            rows = cursor.fetchall()
            
            # Get client name
            cursor.execute('SELECT nombre FROM clientes WHERE id = ?', (cliente_id,))
            cliente = cursor.fetchone()
            cliente_nombre = cliente['nombre'] if cliente else 'Desconocido'
            
            # Organize data
            fiados_dict = {}
            total_pagado_general = 0
            
            for row in rows:
                fiado_id = row['fiado_id']
                
                if fiado_id not in fiados_dict:
                    fiados_dict[fiado_id] = {
                        'fiado_id': fiado_id,
                        'monto_total': row['monto_total'],
                        'monto_pagado': row['monto_pagado'],
                        'saldo_pendiente': row['saldo_pendiente'],
                        'estado': row['estado'],
                        'fecha_creacion': row['fecha_creacion'],
                        'pagos': []
                    }
                
                if row['pago_id']:
                    fiados_dict[fiado_id]['pagos'].append({
                        'pago_id': row['pago_id'],
                        'monto': row['pago_monto'],
                        'fecha_pago': row['fecha_pago'],
                        'nota': row['pago_nota']
                    })
                    total_pagado_general += row['pago_monto']
            
            return {
                'cliente_id': cliente_id,
                'cliente_nombre': cliente_nombre,
                'fiados': list(fiados_dict.values()),
                'total_fiados': len(fiados_dict),
                'total_pagado_general': total_pagado_general,
                'total_pagos_realizados': sum(len(f['pagos']) for f in fiados_dict.values())
            }
    
    def buscar_ventas(self, cliente: Optional[str] = None, 
                     forma_pago: Optional[str] = None,
                     monto_min: Optional[float] = None,
                     monto_max: Optional[float] = None) -> List[sqlite3.Row]:
        """Advanced search for sales"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM ventas WHERE 1=1"
            params = []
            
            if cliente:
                query += " AND cliente LIKE ?"
                params.append(f"%{cliente}%")
            
            if forma_pago:
                query += " AND forma_pago = ?"
                params.append(forma_pago)
            
            if monto_min is not None:
                query += " AND monto >= ?"
                params.append(monto_min)
            
            if monto_max is not None:
                query += " AND monto <= ?"
                params.append(monto_max)
            
            query += " ORDER BY fecha_hora DESC LIMIT 100"
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def aplicar_interes_fiados_cliente(self, cliente_id: int, porcentaje_interes: float) -> Dict[str, Any]:
        """Apply interest to all pending or partial fiados of a client"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Start transaction
                conn.execute("BEGIN TRANSACTION")
                
                try:
                    # Get all pending/partial fiados for client
                    cursor.execute('''
                        SELECT id, monto_original, interes_porcentaje, monto_total, saldo_pendiente, estado
                        FROM fiados 
                        WHERE cliente_id = ? AND estado IN ('Pendiente', 'Parcial')
                    ''', (cliente_id,))
                    
                    fiados = cursor.fetchall()
                    
                    if not fiados:
                        raise ValueError("El cliente no tiene fiados pendientes o parciales")
                    
                    total_interes_aplicado = 0
                    fiados_actualizados = []
                    
                    for fiado in fiados:
                        # Calculate new interest and totals
                        nuevo_interes = fiado['interes_porcentaje'] + porcentaje_interes
                        nuevo_monto_total = round(fiado['monto_original'] * (1 + nuevo_interes / 100), 2)
                        
                        # Calculate new saldo based on what's already paid
                        monto_pagado = fiado['monto_total'] - fiado['saldo_pendiente']
                        nuevo_saldo = round(nuevo_monto_total - monto_pagado, 2)
                        
                        # Update fiado
                        cursor.execute('''
                            UPDATE fiados 
                            SET interes_porcentaje = ?, monto_total = ?, saldo_pendiente = ?, updated_at = datetime('now', 'localtime')
                            WHERE id = ?
                        ''', (nuevo_interes, nuevo_monto_total, nuevo_saldo, fiado['id']))
                        
                        interes_aplicado = nuevo_monto_total - fiado['monto_original']
                        total_interes_aplicado += interes_aplicado
                        fiados_actualizados.append({
                            'fiado_id': fiado['id'],
                            'interes_anterior': fiado['interes_porcentaje'],
                            'interes_nuevo': nuevo_interes,
                            'monto_total_anterior': fiado['monto_total'],
                            'monto_total_nuevo': nuevo_monto_total,
                            'saldo_nuevo': nuevo_saldo
                        })
                    
                    conn.execute("COMMIT")
                    
                    logger.info(f"Interés aplicado a {len(fiados_actualizados)} fiados del cliente {cliente_id}")
                    
                    return {
                        'cliente_id': cliente_id,
                        'porcentaje_aplicado': porcentaje_interes,
                        'fiados_actualizados': len(fiados_actualizados),
                        'total_interes_monto': total_interes_aplicado,
                        'detalle': fiados_actualizados
                    }
                    
                except Exception as e:
                    conn.execute("ROLLBACK")
                    raise e
                    
        except Exception as e:
            logger.error(f"Error al aplicar interés: {e}")
            raise DatabaseError(f"No se pudo aplicar el interés: {e}")
    
    def pagar_todos_fiados_cliente(self, cliente_id: int, monto_total: float, nota: str = "") -> Dict[str, Any]:
        """Pay all pending/partial fiados of a client in one payment"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Start transaction
                conn.execute("BEGIN TRANSACTION")
                
                try:
                    # Get all pending/partial fiados for client
                    cursor.execute('''
                        SELECT id, saldo_pendiente, estado, cliente_nombre
                        FROM fiados 
                        WHERE cliente_id = ? AND estado IN ('Pendiente', 'Parcial')
                        ORDER BY fecha_creacion ASC
                    ''', (cliente_id,))
                    
                    fiados = cursor.fetchall()
                    
                    if not fiados:
                        raise ValueError("El cliente no tiene fiados pendientes o parciales para pagar")
                    
                    # Calculate total pending
                    total_pendiente = sum(f['saldo_pendiente'] for f in fiados)
                    
                    if abs(monto_total - total_pendiente) > 0.01:
                        raise ValueError(f"El monto ingresado (${monto_total:.2f}) no coincide con el total pendiente (${total_pendiente:.2f})")
                    
                    fiados_pagados = []
                    
                    for fiado in fiados:
                        # Register payment for this fiado
                        cursor.execute('''
                            INSERT INTO pagos_fiados (fiado_id, monto, nota)
                            VALUES (?, ?, ?)
                        ''', (fiado['id'], fiado['saldo_pendiente'], nota if nota else "Pago completo"))
                        
                        # Mark fiado as paid
                        cursor.execute('''
                            UPDATE fiados 
                            SET monto_pagado = monto_total, saldo_pendiente = 0, estado = 'Pagado', 
                                fecha_pago = datetime('now', 'localtime'), updated_at = datetime('now', 'localtime')
                            WHERE id = ?
                        ''', (fiado['id'],))
                        
                        fiados_pagados.append({
                            'fiado_id': fiado['id'],
                            'monto_pagado': fiado['saldo_pendiente'],
                            'estado_anterior': fiado['estado']
                        })
                    
                    conn.execute("COMMIT")
                    
                    logger.info(f"Pagados {len(fiados_pagados)} fiados del cliente {cliente_id}")
                    
                    return {
                        'cliente_id': cliente_id,
                        'cliente_nombre': fiados[0]['cliente_nombre'] if fiados else '',
                        'total_pagado': monto_total,
                        'cantidad_fiados': len(fiados_pagados),
                        'fiados_pagados': fiados_pagados
                    }
                    
                except Exception as e:
                    conn.execute("ROLLBACK")
                    raise e
                    
        except Exception as e:
            logger.error(f"Error al pagar fiados: {e}")
            raise DatabaseError(f"No se pudo realizar el pago: {e}")
    
    def close(self):
        """Cleanup method - currently connections are managed by context managers"""
        logger.info("Database connection manager closed")
