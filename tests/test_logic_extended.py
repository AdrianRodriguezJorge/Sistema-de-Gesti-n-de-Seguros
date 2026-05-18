# -*- coding: utf-8 -*-
import os
import sys

# Añadir el directorio raíz al path de Python para permitir ejecución directa
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.conexionDB import Database
from models.agencia import Agencia
from db.queries_agencia import CrudAgencia
from models.pago import Pago
from db.queries_pago import CrudPago
from models.reaseguradora import Reaseguradora
from db.queries_reaseguradora import CrudReaseguradora
from models.cliente import Cliente
from db.queries_cliente import CrudCliente
from models.poliza import Poliza
from db.queries_poliza import CrudPoliza

# Reconfigurar la salida estándar a UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def test_logic_extended():
    print("=" * 60)
    print("       🧪 EJECUTANDO PRUEBAS DE LÓGICA EXTENDIDA (AGENCIA, REASEGURADORA, PAGO)")
    print("=" * 60)
    
    try:
        with Database() as db:
            pais = db.fetch_one("SELECT idpais FROM pais LIMIT 1;")
            tipo_reaseguro = db.fetch_one("SELECT idtiporeaseguro FROM tipo_reaseguro LIMIT 1;")
            tipo_seguro = db.fetch_one("SELECT idtiposeguro FROM tipo_seguro LIMIT 1;")
            estado_poliza = db.fetch_one("SELECT idestadopoliza FROM estado_poliza LIMIT 1;")
            
            if not (pais and tipo_reaseguro and tipo_seguro and estado_poliza):
                print("❌ Faltan catálogos base.")
                return

            id_pais = pais["idpais"]
            id_tipo_reaseguro = tipo_reaseguro["idtiporeaseguro"]
            id_tipo_seguro = tipo_seguro["idtiposeguro"]
            id_estado_poliza = estado_poliza["idestadopoliza"]
        
        # --- TEST 1: CRUD AGENCIA ---
        print("➡️  Paso 1: Probando CRUD de Agencia...")
        crud_ag = CrudAgencia()
        nueva_ag = Agencia(nombre="Agencia Prueba", direccion="Dir 1", telefono="123", email="ag@ag.com", directorGeneral="Dir", jefeSeguros="Seg", jefeReclamaciones="Rec")
        ag_id = crud_ag.crear(nueva_ag)
        assert ag_id is not None, "Fallo al crear agencia"
        
        ag_ob = crud_ag.obtener(ag_id)
        assert ag_ob.nombre == "Agencia Prueba", "Nombre de agencia no coincide"
        
        ag_ob.nombre = "Agencia Modificada"
        crud_ag.actualizar(ag_ob)
        ag_ob_actualizada = crud_ag.obtener(ag_id)
        assert ag_ob_actualizada.nombre == "Agencia Modificada", "Fallo al actualizar agencia"
        
        # Como CrudAgencia no tiene eliminar(), borramos vía consulta directa
        with Database() as db:
            db.execute("DELETE FROM agencia WHERE idagencia=%s", (ag_id,))
        assert crud_ag.obtener(ag_id) is None, "Fallo al eliminar agencia"
        print("  🟢 CRUD de Agencia superado con éxito")
        
        # --- TEST 2: CRUD REASEGURADORA ---
        print("➡️  Paso 2: Probando CRUD de Reaseguradora...")
        crud_rea = CrudReaseguradora()
        nueva_rea = Reaseguradora(nombre="Rea Prueba", idPais=id_pais, idTipoReaseguro=id_tipo_reaseguro)
        rea_id = crud_rea.crear(nueva_rea)
        assert rea_id is not None, "Fallo al crear reaseguradora"
        
        rea_ob = crud_rea.obtener(rea_id)
        assert rea_ob.nombre == "Rea Prueba", "Nombre de reaseguradora no coincide"
        
        rea_ob.nombre = "Rea Mod"
        crud_rea.actualizar(rea_ob)
        assert crud_rea.obtener(rea_id).nombre == "Rea Mod", "Fallo al actualizar reaseguradora"
        
        # Eliminar a través del método que requiere el objeto
        crud_rea.eliminar(rea_ob)
        assert crud_rea.obtener(rea_id) is None, "Fallo al eliminar reaseguradora"
        print("  🟢 CRUD de Reaseguradora superado con éxito")
        
        # --- TEST 3: CRUD PAGO ---
        print("➡️  Paso 3: Probando CRUD de Pago...")
        # Setup: Crear cliente y póliza falsos
        crud_cli = CrudCliente()
        cli_id = crud_cli.crear(Cliente(nombre="Cli", apellidos="Test", noIdentificacion="T123", edad=30, sexo="M", idPais=id_pais, dirPostal="D", telefono="1", correo="cli_pago@test.com"))
        
        crud_pol = CrudPoliza()
        pol_id = crud_pol.crear(Poliza(idTipoSeguro=id_tipo_seguro, fechaInicio="2026-01-01", fechaFin="2027-01-01", primaMensual=10.0, idEstadoPoliza=id_estado_poliza, montoAsegurado=100.0, idCliente=cli_id))
        
        crud_pago = CrudPago()
        nuevo_pago = Pago(idPoliza=pol_id, fechaPago="2026-02-01", montoPagado=100.0)
        pago_id = crud_pago.crear(nuevo_pago)
        assert pago_id is not None, "Fallo al crear pago"
        
        pago_ob = crud_pago.obtener(pago_id)
        assert float(pago_ob.montoPagado) == 100.0, "Monto pagado no coincide"
        
        # Borrado de estructuras mediante eliminación en cascada de la póliza y el cliente
        crud_pol.eliminar(pol_id)
        crud_cli.eliminar(cli_id)
        
        # El pago debería haberse eliminado por cascade delete
        assert crud_pago.obtener(pago_id) is None, "El pago no se borró en cascada"
        print("  🟢 CRUD de Pago y Eliminación en Cascada superados con éxito")

        print("🎉 ¡TODO PERFECTO! Las pruebas lógicas extendidas pasaron al 100%.")

    except AssertionError as assert_err:
        print(f"❌ Fallo en prueba de aserción: {assert_err}")
        raise
    except Exception as e:
        print(f"❌ Error inesperado durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_logic_extended()
