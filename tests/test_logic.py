# -*- coding: utf-8 -*-
import os
import sys

# Añadir el directorio raíz al path de Python para permitir ejecución directa
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.conexionDB import Database
from models.cobertura import Cobertura
from db.queries_cobertura import CrudCobertura
from models.cliente import Cliente
from db.queries_cliente import CrudCliente
from models.poliza import Poliza
from db.queries_poliza import CrudPoliza
from models.reclamacion import Reclamacion
from db.queries_reclamacion import CrudReclamacion

# Reconfigurar la salida estándar a UTF-8 para evitar errores de codificación
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def run_tests():
    print("=" * 60)
    print("       🧪 EJECUTANDO PRUEBAS DE INTEGRIDAD Y LÓGICA DE NEGOCIO")
    print("=" * 60)
    
    # Obtener llaves foráneas válidas dinámicamente para evitar fallos de integridad por datos inexistentes
    try:
        with Database() as db:
            pais = db.fetch_one("SELECT idpais FROM pais LIMIT 1;")
            tipo_seguro = db.fetch_one("SELECT idtiposeguro FROM tipo_seguro LIMIT 1;")
            estado_poliza = db.fetch_one("SELECT idestadopoliza FROM estado_poliza LIMIT 1;")
            tipo_siniestro = db.fetch_one("SELECT idtiposiniestro FROM tipo_siniestro LIMIT 1;")
            estado_reclamacion = db.fetch_one("SELECT idestadoreclamacion FROM estado_reclamacion LIMIT 1;")
            
            if not (pais and tipo_seguro and estado_poliza and tipo_siniestro and estado_reclamacion):
                print("❌ Error: Faltan catálogos base en la base de datos. Por favor ejecuta el SQL primero.")
                return
                
            id_pais = pais["idpais"]
            id_tipo_seguro = tipo_seguro["idtiposeguro"]
            id_estado_poliza = estado_poliza["idestadopoliza"]
            id_tipo_siniestro = tipo_siniestro["idtiposiniestro"]
            id_estado_reclamacion = estado_reclamacion["idestadoreclamacion"]
            
        print("✅ Catálogos base detectados correctamente.")
        # Limpiar registros previos de pruebas truncadas para evitar conflictos de unicidad (correo)
        with Database() as db:
            db.execute("DELETE FROM pago WHERE idpoliza IN (SELECT idpoliza FROM poliza WHERE idcliente IN (SELECT idcliente FROM cliente WHERE correo IN ('prueba@test.com', 'prueba_mod@test.com')));")
            db.execute("DELETE FROM poliza_cobertura WHERE idpoliza IN (SELECT idpoliza FROM poliza WHERE idcliente IN (SELECT idcliente FROM cliente WHERE correo IN ('prueba@test.com', 'prueba_mod@test.com')));")
            db.execute("DELETE FROM reclamacion_rechazada WHERE idreclamacion IN (SELECT idreclamacion FROM reclamacion WHERE idpoliza IN (SELECT idpoliza FROM poliza WHERE idcliente IN (SELECT idcliente FROM cliente WHERE correo IN ('prueba@test.com', 'prueba_mod@test.com'))));")
            db.execute("DELETE FROM reclamacion WHERE idpoliza IN (SELECT idpoliza FROM poliza WHERE idcliente IN (SELECT idcliente FROM cliente WHERE correo IN ('prueba@test.com', 'prueba_mod@test.com')));")
            db.execute("DELETE FROM poliza_cancelada WHERE idpoliza IN (SELECT idpoliza FROM poliza WHERE idcliente IN (SELECT idcliente FROM cliente WHERE correo IN ('prueba@test.com', 'prueba_mod@test.com')));")
            db.execute("DELETE FROM poliza WHERE idcliente IN (SELECT idcliente FROM cliente WHERE correo IN ('prueba@test.com', 'prueba_mod@test.com'));")
            db.execute("DELETE FROM cliente WHERE correo IN ('prueba@test.com', 'prueba_mod@test.com');")
        print("✅ Estado de prueba limpio garantizado.")
        print("-" * 60)
        
        # --- TEST 1: CRUD COBERTURA ---
        print("➡️  Paso 1: Probando CRUD de Cobertura...")
        crud_cob = CrudCobertura()
        nueva_cob = Cobertura(descripcion="Cobertura de Prueba Temporal")
        cob_id = crud_cob.crear(nueva_cob)
        assert cob_id is not None, "Error al crear cobertura"
        print(f"  🟢 Cobertura creada con ID: {cob_id}")
        
        cob_obtenida = crud_cob.obtener(cob_id)
        assert cob_obtenida is not None, "Error al obtener cobertura"
        assert cob_obtenida.descripcion == "Cobertura de Prueba Temporal", "Descripción no coincide"
        print("  🟢 Cobertura leída correctamente")
        
        crud_cob.actualizar(Cobertura(descripcion="Cobertura de Prueba Actualizada", idCobertura=cob_id))
        cob_actualizada = crud_cob.obtener(cob_id)
        assert cob_actualizada.descripcion == "Cobertura de Prueba Actualizada", "Actualización fallida"
        print("  🟢 Cobertura actualizada correctamente")
        
        crud_cob.eliminar(cob_id)
        assert crud_cob.obtener(cob_id) is None, "Error al eliminar cobertura"
        print("  🟢 Cobertura eliminada correctamente")
        print("-" * 60)
        
        # --- TEST 2: CRUD CLIENTE ---
        print("➡️  Paso 2: Probando CRUD de Cliente...")
        crud_cli = CrudCliente()
        nuevo_cli = Cliente(
            nombre="Usuario",
            apellidos="Prueba",
            noIdentificacion="TEST-12345",
            edad=25,
            sexo="M",
            idPais=id_pais,
            dirPostal="Dirección de Prueba",
            telefono="12345678",
            correo="prueba@test.com"
        )
        cli_id = crud_cli.crear(nuevo_cli)
        assert cli_id is not None, "Error al crear cliente"
        print(f"  🟢 Cliente creado con ID: {cli_id}")
        
        cli_obtenido = crud_cli.obtener(cli_id)
        assert cli_obtenido is not None, "Error al obtener cliente"
        assert cli_obtenido.nombre == "Usuario" and cli_obtenido.apellidos == "Prueba", "Datos no coinciden"
        print("  🟢 Cliente leído correctamente")
        
        crud_cli.actualizar(Cliente(
            nombre="Usuario Mod",
            apellidos="Prueba Mod",
            noIdentificacion="TEST-12345",
            edad=26,
            sexo="M",
            idPais=id_pais,
            dirPostal="Dirección de Prueba Mod",
            telefono="87654321",
            correo="prueba_mod@test.com",
            idCliente=cli_id
        ))
        cli_actualizado = crud_cli.obtener(cli_id)
        assert cli_actualizado.nombre == "Usuario Mod" and cli_actualizado.edad == 26, "Actualización fallida"
        print("  🟢 Cliente actualizado correctamente")
        print("-" * 60)
        
        # --- TEST 3: CRUD PÓLIZA Y CASCADE DELETION ---
        print("➡️  Paso 3: Probando CRUD de Póliza y Eliminación en Cascada...")
        crud_pol = CrudPoliza()
        nueva_pol = Poliza(
            idTipoSeguro=id_tipo_seguro,
            fechaInicio="2026-01-01",
            fechaFin="2027-01-01",
            primaMensual=150.0,
            idEstadoPoliza=id_estado_poliza,
            montoAsegurado=75000.0,
            idCliente=cli_id
        )
        pol_id = crud_pol.crear(nueva_pol)
        assert pol_id is not None, "Error al crear póliza"
        print(f"  🟢 Póliza creada con ID: {pol_id}")
        
        # Añadir dependencias de póliza para forzar fallos de FK y probar nuestro cascade
        with Database() as db:
            # 1. Pago
            db.execute("INSERT INTO pago (idpoliza, fecha_pago, monto_pagado) VALUES (%s, CURRENT_DATE, 150.0);", (pol_id,))
            # 2. Cobertura asignada
            # Obtener una cobertura de catálogo existente
            cob_cat = db.fetch_one("SELECT idcobertura FROM cobertura LIMIT 1;")
            if cob_cat:
                db.execute("INSERT INTO poliza_cobertura (idpoliza, idcobertura, monto) VALUES (%s, %s, 5000.0);", (pol_id, cob_cat["idcobertura"]))
            # 3. Póliza cancelada
            db.execute("INSERT INTO poliza_cancelada (idpoliza, motivo) VALUES (%s, 'Cancelación de test');", (pol_id,))
            
        print("  🟢 Elementos dependientes vinculados con éxito (pago, cobertura, cancelación).")
        
        # Probar lectura y actualización
        pol_obtenida = crud_pol.obtener(pol_id)
        assert pol_obtenida is not None, "Error al obtener póliza"
        assert float(pol_obtenida.primaMensual) == 150.0, "Prima no coincide"
        
        crud_pol.actualizar(Poliza(
            idTipoSeguro=id_tipo_seguro,
            fechaInicio="2026-01-01",
            fechaFin="2027-01-01",
            primaMensual=175.0,
            idEstadoPoliza=id_estado_poliza,
            montoAsegurado=75000.0,
            idCliente=cli_id,
            idPoliza=pol_id
        ))
        pol_actualizada = crud_pol.obtener(pol_id)
        assert float(pol_actualizada.primaMensual) == 175.0, "Actualización de prima fallida"
        print("  🟢 Póliza leída y actualizada correctamente")
        
        # Ejecutar eliminación en cascada de la póliza
        crud_pol.eliminar(pol_id)
        assert crud_pol.obtener(pol_id) is None, "Error: La póliza no se eliminó"
        print("  🟢 ¡ELIMINACIÓN EN CASCADA COMPLETA! Póliza y sus elementos dependientes borrados con éxito.")
        print("-" * 60)
        
        # --- TEST 4: CRUD RECLAMACIÓN Y CASCADE DELETION ---
        print("➡️  Paso 4: Probando CRUD de Reclamación y Eliminación en Cascada...")
        # Volvemos a crear una póliza para poder vincular la reclamación
        pol_id_nueva = crud_pol.crear(Poliza(
            idTipoSeguro=id_tipo_seguro,
            fechaInicio="2026-01-01",
            fechaFin="2027-01-01",
            primaMensual=150.0,
            idEstadoPoliza=id_estado_poliza,
            montoAsegurado=75000.0,
            idCliente=cli_id
        ))
        
        crud_rec = CrudReclamacion()
        nueva_rec = Reclamacion(
            idTipoSiniestro=id_tipo_siniestro,
            fechaSiniestro="2026-06-01",
            montoReclamado=5000.0,
            idEstadoReclamacion=id_estado_reclamacion,
            montoIndemnizado=0.0,
            idPoliza=pol_id_nueva
        )
        rec_id = crud_rec.crear(nueva_rec)
        assert rec_id is not None, "Error al crear reclamación"
        print(f"  🟢 Reclamación creada con ID: {rec_id}")
        
        # Vincular rechazo de reclamación para forzar FK en cascada
        with Database() as db:
            db.execute("INSERT INTO reclamacion_rechazada (idreclamacion, motivo) VALUES (%s, 'Rechazo de test');", (rec_id,))
        print("  🟢 Historial de rechazo vinculado con éxito.")
        
        # Probar lectura y actualización
        rec_obtenida = crud_rec.obtener(rec_id)
        assert rec_obtenida is not None, "Error al obtener reclamación"
        assert float(rec_obtenida.montoReclamado) == 5000.0, "Monto reclamado no coincide"
        
        crud_rec.actualizar(Reclamacion(
            idTipoSiniestro=id_tipo_siniestro,
            fechaSiniestro="2026-06-01",
            montoReclamado=6000.0,
            idEstadoReclamacion=id_estado_reclamacion,
            montoIndemnizado=2000.0,
            idPoliza=pol_id_nueva,
            idReclamacion=rec_id
        ))
        rec_actualizada = crud_rec.obtener(rec_id)
        assert float(rec_actualizada.montoReclamado) == 6000.0 and float(rec_actualizada.montoIndemnizado) == 2000.0, "Actualización fallida"
        print("  🟢 Reclamación leída y actualizada correctamente")
        
        # Eliminar reclamación
        crud_rec.eliminar(rec_id)
        assert crud_rec.obtener(rec_id) is None, "Error al eliminar reclamación"
        print("  🟢 ¡ELIMINACIÓN EN CASCADA COMPLETA! Reclamación e historial de rechazos eliminados exitosamente.")
        
        # Limpiar póliza nueva y cliente de prueba
        crud_pol.eliminar(pol_id_nueva)
        crud_cli.eliminar(cli_id)
        print("  🟢 Limpieza de registros temporales completada con éxito.")
        print("-" * 60)
        
        print("🎉 ¡TODO EXCELENTE! Las pruebas lógicas y de integridad pasaron al 100% sin ningún error.")
        
    except AssertionError as assert_err:
        print(f"❌ Fallo en prueba de aserción: {assert_err}")
    except Exception as e:
        print(f"❌ Error inesperado durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
