"""
Test Suite Completo - Kiosco Manager
Prueba TODAS las funcionalidades del sistema
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Asegurar que podemos importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database, DatabaseError, FormaPago, EstadoFiado

class TestColors:
    OK = '[OK]'
    FAIL = '[FAIL]'
    WARNING = '[WARN]'
    INFO = '[INFO]'
    END = ''

class KioscoTester:
    def __init__(self):
        self.db = None
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        # Generar nombres únicos para cada ejecución
        self.test_suffix = str(random.randint(1000, 9999))
        
    def setup(self):
        """Inicializar base de datos de prueba"""
        print(f"{TestColors.INFO} Inicializando base de datos...")
        try:
            self.db = Database()
            print(f"{TestColors.OK} Base de datos inicializada (suffix: {self.test_suffix})")
            return True
        except Exception as e:
            print(f"{TestColors.FAIL} Error al inicializar BD: {e}")
            return False
    
    def run_test(self, test_name, test_func):
        """Ejecutar un test individual"""
        try:
            print(f"{TestColors.INFO} Test: {test_name}")
            test_func()
            self.tests_passed += 1
            self.test_results.append((test_name, True, None))
            print(f"{TestColors.OK}  PASSED")
            return True
        except Exception as e:
            self.tests_failed += 1
            self.test_results.append((test_name, False, str(e)))
            print(f"{TestColors.FAIL}  FAILED: {e}")
            return False
    
    # ==========================================
    # TESTS DE VENTAS
    # ==========================================
    def test_crear_venta(self):
        """Test: Crear una venta básica"""
        venta_id = self.db.agregar_venta(
            monto=1500.50,
            forma_pago="Efectivo",
            cliente="Test Cliente",
            nota="Venta de prueba"
        )
        assert venta_id is not None, "No se retornó ID de venta"
        assert venta_id > 0, f"ID de venta inválido: {venta_id}"
        self.test_venta_id = venta_id
        
    def test_crear_venta_sin_cliente(self):
        """Test: Crear venta sin cliente (opcional)"""
        venta_id = self.db.agregar_venta(
            monto=500,
            forma_pago="Transferencia",
            cliente="",
            nota=""
        )
        assert venta_id is not None, "No se retornó ID de venta"
        
    def test_crear_venta_monto_invalido(self):
        """Test: Intentar crear venta con monto inválido"""
        try:
            self.db.agregar_venta(monto=-100, forma_pago="Efectivo")
            assert False, "Debería haber fallado con monto negativo"
        except (ValueError, DatabaseError):
            pass  # Expected
            
    def test_obtener_ventas_hoy(self):
        """Test: Obtener ventas del día"""
        datos = self.db.obtener_resumen_diario()
        assert 'ventas' in datos, "No se encontró key 'ventas'"
        assert 'total' in datos, "No se encontró key 'total'"
        assert 'cantidad' in datos, "No se encontró key 'cantidad'"
        assert 'por_forma_pago' in datos, "No se encontró key 'por_forma_pago'"
        assert datos['cantidad'] >= 2, f"Se esperaban al menos 2 ventas, hay {datos['cantidad']}"
        
    def test_obtener_ventas_por_fecha(self):
        """Test: Obtener ventas de fecha específica"""
        hoy = datetime.now().strftime('%Y-%m-%d')
        datos = self.db.obtener_ventas_por_fecha(hoy)
        assert 'ventas' in datos
        assert len(datos['ventas']) >= 2
        
    def test_resumen_mensual(self):
        """Test: Obtener resumen mensual"""
        hoy = datetime.now()
        datos = self.db.obtener_resumen_mensual(hoy.year, hoy.month)
        assert 'total' in datos
        assert 'cantidad' in datos
        assert 'por_forma_pago' in datos
        assert 'por_dia' in datos
        
    # ==========================================
    # TESTS DE CLIENTES
    # ==========================================
    def test_crear_cliente(self):
        """Test: Crear un cliente nuevo"""
        cliente_id = self.db.agregar_cliente(
            nombre=f"Juan Pérez {self.test_suffix}",
            telefono="1234567890",
            email="juan@test.com",
            direccion="Calle Test 123",
            notas="Cliente de prueba"
        )
        assert cliente_id is not None, "No se retornó ID de cliente"
        assert cliente_id > 0, f"ID de cliente inválido: {cliente_id}"
        self.test_cliente_id = cliente_id
        
    def test_crear_cliente_duplicado(self):
        """Test: Intentar crear cliente duplicado"""
        try:
            self.db.agregar_cliente(nombre=f"Juan Pérez {self.test_suffix}")
            assert False, "Debería fallar con cliente duplicado"
        except (ValueError, DatabaseError):
            pass  # Expected
            
    def test_obtener_clientes(self):
        """Test: Obtener lista de clientes"""
        clientes = self.db.obtener_clientes()
        assert len(clientes) > 0, "No se encontraron clientes"
        assert any(c['nombre'] == f"Juan Pérez {self.test_suffix}" for c in clientes), "No se encontró cliente de prueba"
        
    def test_buscar_cliente_por_nombre(self):
        """Test: Buscar cliente por nombre"""
        cliente = self.db.buscar_cliente_por_nombre(f"Juan Pérez {self.test_suffix}")
        assert cliente is not None, "No se encontró cliente"
        assert cliente['nombre'] == f"Juan Pérez {self.test_suffix}"
        
    # ==========================================
    # TESTS DE FIADOS
    # ==========================================
    def test_crear_fiado(self):
        """Test: Crear un fiado"""
        # Primero crear un cliente para el fiado
        cliente_id = self.db.agregar_cliente(
            nombre=f"María García {self.test_suffix}", 
            telefono="0987654321"
        )
        self.test_cliente_fiado_id = cliente_id
        
        fiado_id = self.db.agregar_fiado(
            cliente_id=cliente_id,
            cliente_nombre=f"María García {self.test_suffix}",
            monto=3500,
            interes=10,
            nota="Fiado de prueba"
        )
        assert fiado_id is not None, "No se retornó ID de fiado"
        assert fiado_id > 0, f"ID de fiado inválido: {fiado_id}"
        self.test_fiado_id = fiado_id
        
        # Verificar que se calculó correctamente
        fiados = self.db.obtener_fiados()
        fiado = next((f for f in fiados if f['id'] == fiado_id), None)
        assert fiado is not None, "No se encontró fiado creado"
        assert fiado['monto_total'] == 3850.00, f"Monto total incorrecto: {fiado['monto_total']} (esperado: 3850.00)"
        assert fiado['estado'] == 'Pendiente', f"Estado incorrecto: {fiado['estado']}"
        
    def test_pago_parcial_fiado(self):
        """Test: Registrar pago parcial de fiado"""
        # Pagar $1000 de $3850
        resultado = self.db.registrar_pago_fiado(self.test_fiado_id, 1000)
        assert resultado['completado'] == False, "No debería estar completado"
        assert resultado['estado'] == 'Parcial', f"Estado incorrecto: {resultado['estado']}"
        assert resultado['saldo_restante'] == 2850.00, f"Saldo incorrecto: {resultado['saldo_restante']}"
        
    def test_pago_completo_fiado(self):
        """Test: Completar pago de fiado"""
        # Pagar los $2850 restantes
        resultado = self.db.registrar_pago_fiado(self.test_fiado_id, 2850)
        assert resultado['completado'] == True, "Debería estar completado"
        assert resultado['estado'] == 'Pagado', f"Estado incorrecto: {resultado['estado']}"
        assert resultado['saldo_restante'] == 0.00, f"Saldo debería ser 0.00: {resultado['saldo_restante']}"
        
    def test_obtener_fiados(self):
        """Test: Obtener lista de fiados"""
        fiados = self.db.obtener_fiados()
        assert len(fiados) > 0, "No se encontraron fiados"
        
    def test_obtener_fiados_por_estado(self):
        """Test: Filtrar fiados por estado"""
        fiados_pagados = self.db.obtener_fiados(estado='Pagado')
        assert len(fiados_pagados) > 0, "No se encontraron fiados pagados"
        
    def test_historial_pagos_fiado(self):
        """Test: Obtener historial de pagos de un fiado"""
        historial = self.db.obtener_historial_fiado(self.test_fiado_id)
        assert len(historial) == 2, f"Se esperaban 2 pagos, hay {len(historial)}"
        
    def test_estadisticas_fiados(self):
        """Test: Obtener estadísticas de fiados"""
        stats = self.db.obtener_estadisticas_fiados()
        assert 'total' in stats
        assert 'pagados' in stats
        assert 'saldo_pendiente' in stats
        assert stats['total'] > 0
        
    # ==========================================
    # TESTS DE RESUMENES Y REPORTES
    # ==========================================
    def test_exportar_datos(self):
        """Test: Exportar datos a JSON"""
        datos = self.db.exportar_a_json()
        assert 'ventas' in datos
        assert 'fiados' in datos
        assert 'exportado_el' in datos
        assert len(datos['ventas']) >= 2
        
    # ==========================================
    # RUN ALL TESTS
    # ==========================================
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("\n" + "="*70)
        print("   TEST SUITE COMPLETO - KIOSCO MANAGER")
        print("="*70 + "\n")
        
        if not self.setup():
            return False
        
        # TESTS DE VENTAS
        print("[SECCION] TESTS DE VENTAS")
        print("-" * 70)
        
        self.run_test("Crear venta basica", self.test_crear_venta)
        self.run_test("Crear venta sin cliente", self.test_crear_venta_sin_cliente)
        self.run_test("Validar monto invalido", self.test_crear_venta_monto_invalido)
        self.run_test("Obtener ventas de hoy", self.test_obtener_ventas_hoy)
        self.run_test("Obtener ventas por fecha", self.test_obtener_ventas_por_fecha)
        self.run_test("Resumen mensual", self.test_resumen_mensual)
        
        # TESTS DE CLIENTES
        print("\n[SECCION] TESTS DE CLIENTES")
        print("-" * 70)
        
        self.run_test("Crear cliente", self.test_crear_cliente)
        self.run_test("Validar cliente duplicado", self.test_crear_cliente_duplicado)
        self.run_test("Obtener clientes", self.test_obtener_clientes)
        self.run_test("Buscar cliente por nombre", self.test_buscar_cliente_por_nombre)
        
        # TESTS DE FIADOS
        print("\n[SECCION] TESTS DE FIADOS")
        print("-" * 70)
        
        self.run_test("Crear fiado", self.test_crear_fiado)
        self.run_test("Pago parcial de fiado", self.test_pago_parcial_fiado)
        self.run_test("Pago completo de fiado", self.test_pago_completo_fiado)
        self.run_test("Obtener fiados", self.test_obtener_fiados)
        self.run_test("Filtrar fiados por estado", self.test_obtener_fiados_por_estado)
        self.run_test("Historial de pagos", self.test_historial_pagos_fiado)
        self.run_test("Estadisticas de fiados", self.test_estadisticas_fiados)
        
        # TESTS DE REPORTES
        print("\n[SECCION] TESTS DE REPORTES")
        print("-" * 70)
        
        self.run_test("Exportar datos", self.test_exportar_datos)
        
        # RESULTADOS
        self.print_results()
        
        return self.tests_failed == 0
    
    def print_results(self):
        """Imprimir resultados finales"""
        print("\n" + "="*70)
        print("   RESULTADOS DE PRUEBAS")
        print("="*70 + "\n")
        
        total = self.tests_passed + self.tests_failed
        print(f"Total de tests: {total}")
        print(f"{TestColors.OK} Pasados: {self.tests_passed}")
        print(f"{TestColors.FAIL} Fallidos: {self.tests_failed}")
        print(f"Tasa de exito: {(self.tests_passed/total)*100:.1f}%\n")
        
        if self.tests_failed > 0:
            print(f"{TestColors.FAIL} Tests fallidos:")
            for name, passed, error in self.test_results:
                if not passed:
                    print(f"  - {name}: {error}")
            print()
        
        if self.tests_failed == 0:
            print(f"{TestColors.OK} TODOS LOS TESTS PASARON EXITOSAMENTE")
        else:
            print(f"{TestColors.WARNING} ALGUNOS TESTS FALLARON - REVISAR")
        
        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    tester = KioscoTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
