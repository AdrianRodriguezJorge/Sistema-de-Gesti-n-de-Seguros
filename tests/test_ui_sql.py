# -*- coding: utf-8 -*-
import os
import sys
import ast

# Reconfigurar la salida estándar a UTF-8 para evitar errores de codificación en Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Añadir el directorio raíz al path de Python para permitir imports locales
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.conexionDB import Database

def extract_sql_queries(filepath):
    """
    Parsea de forma estática el AST de un archivo Python para extraer todas las
    cadenas literales que se asemejan a consultas SQL (SELECT, INSERT, UPDATE, DELETE).
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"❌ Error de sintaxis de Python al parsear {os.path.basename(filepath)}: {e}")
        return []
        
    sql_queries = []
    sql_keywords = {'select', 'insert', 'update', 'delete', 'explain'}
    tables = {
        'cliente', 'poliza', 'reclamacion', 'agencia', 'pago', 
        'cobertura', 'poliza_cobertura', 'reaseguradora', 
        'participacion_reaseguro', 'poliza_cancelada', 'reclamacion_rechazada',
        'reporte_generado', 'pais', 'tipo_seguro', 'estado_poliza',
        'tipo_siniestro', 'estado_reclamacion', 'tipo_reaseguro'
    }
    
    for node in ast.walk(tree):
        val = None
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value
        elif hasattr(ast, 'Str') and isinstance(node, ast.Str):
            val = node.s
            
        if val:
            val_clean = val.strip().lower()
            # Verificar si contiene expresiones SQL válidas y al menos una tabla conocida
            sql_expressions = ['select ', 'insert into ', 'update ', 'delete from ', 'explain ']
            has_sql_kw = any(expr in val_clean for expr in sql_expressions)
            has_table = any(table in val_clean for table in tables)
            
            if has_sql_kw and has_table:
                lineno = getattr(node, 'lineno', 'Desconocida')
                sql_queries.append((lineno, val))
                
    return sql_queries

def test_ui_queries():
    print("=" * 75)
    print("   🔍 VERIFICACIÓN ESTÁTICA Y EXPLAIN DE CONSULTAS SQL EN LA CAPA UI")
    print("=" * 75)
    
    ui_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui'))
    py_files = [os.path.join(ui_dir, f) for f in os.listdir(ui_dir) if f.endswith('.py') and f.startswith('ui_')]
    
    failures = 0
    checked_queries = 0
    
    with Database() as db:
        for filepath in py_files:
            filename = os.path.basename(filepath)
            print(f"\n📂 Analizando archivo: {filename}...")
            queries = extract_sql_queries(filepath)
            
            if not queries:
                print("  ✨ Sin consultas SQL embebidas.")
                continue
                
            print(f"  📝 Detectadas {len(queries)} consultas SQL. Validando...")
            for lineno, sql in queries:
                checked_queries += 1
                sql_clean = sql.strip()
                
                # Reemplazar placeholders %s con NULL para que el analizador de PostgreSQL los valide
                sql_prepared = sql_clean
                while '%s' in sql_prepared:
                    sql_prepared = sql_prepared.replace('%s', 'NULL')
                
                # Quitar punto y coma al final si existe para añadir EXPLAIN
                sql_prepared = sql_prepared.rstrip(';')
                
                # Si no empieza con EXPLAIN, agregarlo
                if not sql_prepared.lower().startswith('explain'):
                    explain_query = f"EXPLAIN {sql_prepared}"
                else:
                    explain_query = sql_prepared
                
                try:
                    # Ejecutar el EXPLAIN
                    db.execute(explain_query)
                    print(f"  🟢 [Línea {lineno}]: Válida.")
                except Exception as e:
                    failures += 1
                    print(f"  🔴 [Línea {lineno}]: CONSULTA ERRÓNEA O DESALINEADA CON LA BD!")
                    print(f"     SQL Original:\n{sql_clean}")
                    print(f"     Error de BD: {e}")
                    # Limpiar el estado de la transacción fallida en PostgreSQL para continuar con las demás consultas
                    try:
                        db.conn.rollback()
                    except Exception:
                        pass

    print("\n" + "=" * 75)
    print("📋 RESUMEN DE LA AUDITORÍA DE CONSULTAS:")
    print(f"   - Consultas totales revisadas: {checked_queries}")
    print(f"   - Consultas exitosas: {checked_queries - failures}")
    print(f"   - Consultas fallidas/erróneas: {failures}")
    print("=" * 75)
    
    if failures > 0:
        print("❌ ¡ALERTA! Se encontraron consultas SQL rotas o desalineadas en la capa UI.")
        sys.exit(1)
    else:
        print("🎉 ¡TODO PERFECTO! Todas las consultas SQL en los archivos de la interfaz son 100% correctas.")
        sys.exit(0)

if __name__ == "__main__":
    test_ui_queries()
