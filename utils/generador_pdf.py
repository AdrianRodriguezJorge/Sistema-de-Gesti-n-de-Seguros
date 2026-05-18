import io
from datetime import datetime
from fpdf import FPDF

def clean_txt(text):
    """
    Enables safe encoding to Latin-1/cp1252 for core PDF fonts.
    Replaces unsupported characters safely so Spanish accents and 'ñ' work perfectly.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        return str(text)
    # Standard Latin-1 characters like á, é, í, ó, ú, ñ, Á, É, Í, Ó, Ú, Ñ, etc. are supported.
    return text.encode('latin-1', errors='replace').decode('latin-1')

class PDFReporte(FPDF):
    def __init__(self, titulo_reporte="Reporte de Seguros"):
        super().__init__()
        self.titulo_reporte = clean_txt(titulo_reporte)
        self.fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Primary Colors (Navy Blue and Teal)
        self.c_primary_r = 29
        self.c_primary_g = 53
        self.c_primary_b = 87
        
        self.c_sec_r = 69
        self.c_sec_g = 123
        self.c_sec_b = 157
        
        self.c_bg_r = 241
        self.c_bg_g = 250
        self.c_bg_b = 238
        
        self.c_text_r = 50
        self.c_text_g = 50
        self.c_text_b = 50

        self.set_margins(15, 15, 15)
        self.alias_nb_pages()

    def header(self):
        # Draw top colored bar
        self.set_fill_color(self.c_primary_r, self.c_primary_g, self.c_primary_b)
        self.rect(0, 0, 210, 8, 'F')
        
        # Title block
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(self.c_primary_r, self.c_primary_g, self.c_primary_b)
        self.cell(0, 10, clean_txt("SISTEMA DE GESTIÓN DE SEGUROS"), ln=True, align='L')
        
        # Subtitle or current report name
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(120, 120, 120)
        self.cell(120, 5, self.titulo_reporte, align='L')
        self.cell(0, 5, clean_txt(f"Generado el: {self.fecha_generacion}"), ln=True, align='R')
        
        # Divider line
        self.set_draw_color(self.c_sec_r, self.c_sec_g, self.c_sec_b)
        self.set_line_width(0.5)
        self.line(15, 31.5, 195, 31.5)
        self.ln(6)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.line(15, 282, 195, 282)
        
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(120, 10, clean_txt("Sistema de Gestión de Seguros - Reportes Oficiales"), align='L')
        self.cell(0, 10, clean_txt(f"Página {self.page_no()}/{{nb}}"), align='R')

    def agregar_titulo_documento(self, titulo):
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(self.c_primary_r, self.c_primary_g, self.c_primary_b)
        self.cell(0, 12, clean_txt(titulo), ln=True, align='L')
        self.ln(2)

    def agregar_subtitulo(self, texto):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(self.c_sec_r, self.c_sec_g, self.c_sec_b)
        self.cell(0, 8, clean_txt(texto), ln=True, align='L')
        self.ln(1)

    def agregar_metrica_box(self, label, valor, width=60):
        # Render a nice gray metric block
        x_pos = self.get_x()
        y_pos = self.get_y()
        
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(220, 220, 220)
        self.set_line_width(0.3)
        self.rect(x_pos, y_pos, width, 18, 'DF')
        
        self.set_y(y_pos + 2)
        self.set_x(x_pos + 2)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(100, 100, 100)
        self.cell(width - 4, 4, clean_txt(label), ln=True, align='C')
        
        self.set_x(x_pos + 2)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(self.c_primary_r, self.c_primary_g, self.c_primary_b)
        self.cell(width - 4, 8, clean_txt(valor), ln=True, align='C')
        
        self.set_y(y_pos)
        self.set_x(x_pos + width + 5)

    def agregar_seccion_divider(self):
        self.ln(4)
        self.set_draw_color(230, 230, 230)
        self.set_line_width(0.3)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(4)

    def agregar_campo_valor(self, campo, valor, col_width_campo=50):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(self.c_primary_r, self.c_primary_g, self.c_primary_b)
        self.cell(col_width_campo, 6, clean_txt(f"{campo}:"), align='L')
        
        self.set_font('Helvetica', '', 9)
        self.set_text_color(self.c_text_r, self.c_text_g, self.c_text_b)
        self.cell(0, 6, clean_txt(str(valor)), ln=True, align='L')

    def agregar_tabla(self, headers, rows, col_widths):
        # Header row
        self.set_fill_color(self.c_primary_r, self.c_primary_g, self.c_primary_b)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 9)
        
        # Print headers
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, clean_txt(header), border=1, align='C', fill=True)
        self.ln()
        
        # Rows
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(self.c_text_r, self.c_text_g, self.c_text_b)
        
        alt_row = False
        for row in rows:
            # Check for page overflow
            if self.get_y() > 260:
                self.add_page()
                # Print headers again
                self.set_fill_color(self.c_primary_r, self.c_primary_g, self.c_primary_b)
                self.set_text_color(255, 255, 255)
                self.set_font('Helvetica', 'B', 9)
                for i, header in enumerate(headers):
                    self.cell(col_widths[i], 8, clean_txt(header), border=1, align='C', fill=True)
                self.ln()
                self.set_font('Helvetica', '', 8.5)
                self.set_text_color(self.c_text_r, self.c_text_g, self.c_text_b)

            if alt_row:
                self.set_fill_color(self.c_bg_r, self.c_bg_g, self.c_bg_b)
            else:
                self.set_fill_color(255, 255, 255)
                
            for i, val in enumerate(row):
                align_mode = 'C'
                if isinstance(val, float) or (isinstance(val, str) and (val.startswith('$') or val.endswith('%'))):
                    align_mode = 'R'
                elif i == 1 and len(headers) > 3: # Client name usually
                    align_mode = 'L'
                self.cell(col_widths[i], 7, clean_txt(str(val)), border=1, align=align_mode, fill=True)
            self.ln()
            alt_row = not alt_row
        self.ln(2)


class GeneradorPDF:
    @staticmethod
    def generar_pdf_ingresos_mensuales(datos):
        año = datos.get('año', datetime.now().year)
        total_anual = datos.get('total_anual', 0)
        ingresos = datos.get('ingresos', [])
        
        pdf = PDFReporte(f"Reporte de Ingresos Mensuales - Año {año}")
        pdf.add_page()
        
        pdf.agregar_titulo_documento(f"Reporte de Ingresos Mensuales")
        pdf.agregar_subtitulo(f"Periodo Fiscal: {año}")
        pdf.ln(2)
        
        # Metrics Row
        total_meses = len(ingresos)
        promedio = total_anual / total_meses if total_meses > 0 else 0
        
        pdf.agregar_metrica_box("Ingreso Total Anual", f"${total_anual:,.2f}", 55)
        pdf.agregar_metrica_box("Meses con Ingresos", str(total_meses), 55)
        pdf.agregar_metrica_box("Promedio Mensual", f"${promedio:,.2f}", 55)
        pdf.ln(24)
        
        # Table
        pdf.agregar_subtitulo("Desglose Mensual")
        headers = ["Mes", "Ingreso Registrado ($)"]
        rows = [[i.get('mes'), f"${i.get('ingreso', 0):,.2f}"] for i in ingresos]
        col_widths = [90, 90]
        
        pdf.agregar_tabla(headers, rows, col_widths)
        
        # Generate raw bytes
        return bytes(pdf.output())

    @staticmethod
    def generar_pdf_ficha_agencia(datos):
        pdf = PDFReporte("Ficha de la Agencia de Seguros")
        pdf.add_page()
        
        pdf.agregar_titulo_documento("Ficha Tecnica de la Agencia")
        pdf.ln(2)
        
        pdf.agregar_subtitulo("Datos Generales de la Agencia")
        pdf.agregar_campo_valor("Nombre de la Agencia", datos.get('nombre'))
        pdf.agregar_campo_valor("Direccion Postal", datos.get('direccion'))
        pdf.agregar_campo_valor("Telefono de Contacto", datos.get('telefono'))
        pdf.agregar_campo_valor("Email Principal", datos.get('email'))
        
        pdf.agregar_seccion_divider()
        
        pdf.agregar_subtitulo("Equipo Directivo de la Agencia")
        pdf.agregar_campo_valor("Director General", datos.get('director_general'))
        pdf.agregar_campo_valor("Jefe de Seguros", datos.get('jefe_seguros'))
        pdf.agregar_campo_valor("Jefe de Reclamaciones", datos.get('jefe_reclamaciones'))
        
        return bytes(pdf.output())

    @staticmethod
    def generar_pdf_ficha_cliente(datos):
        cliente = datos.get('cliente', {})
        nombre_completo = f"{cliente.get('nombre', '')} {cliente.get('apellidos', '')}"
        
        pdf = PDFReporte(f"Ficha de Cliente: {nombre_completo}")
        pdf.add_page()
        
        pdf.agregar_titulo_documento("Ficha Informativa de Cliente")
        pdf.ln(2)
        
        # Profile Columns (Left text, Right metrics)
        pdf.agregar_subtitulo("Informacion del Cliente")
        pdf.agregar_campo_valor("Nombre Completo", nombre_completo)
        pdf.agregar_campo_valor("Numero Identificacion", cliente.get('identificacion'))
        pdf.agregar_campo_valor("Telefono", cliente.get('telefono'))
        pdf.agregar_campo_valor("Correo Electronico", cliente.get('correo'))
        pdf.agregar_campo_valor("Pais de Origen", cliente.get('pais'))
        
        pdf.agregar_seccion_divider()
        
        pdf.agregar_subtitulo("Resumen Financiero y de Servicios")
        pdf.agregar_metrica_box("Polizas Activas", str(datos.get('polizas_activas', 0)), 55)
        pdf.agregar_metrica_box("Primas Pagadas", f"${datos.get('total_primas', 0):,.2f}", 55)
        pdf.agregar_metrica_box("Reclamaciones Realizadas", str(datos.get('reclamaciones', 0)), 55)
        pdf.ln(24)
        
        return bytes(pdf.output())

    @staticmethod
    def generar_pdf_ficha_reaseguradora(datos):
        nombre = datos.get('nombre', '')
        
        pdf = PDFReporte(f"Ficha de Reaseguradora: {nombre}")
        pdf.add_page()
        
        pdf.agregar_titulo_documento("Ficha Tecnica de Reaseguradora")
        pdf.ln(2)
        
        pdf.agregar_subtitulo("Datos de Identificacion")
        pdf.agregar_campo_valor("Nombre de Empresa", nombre)
        pdf.agregar_campo_valor("Pais de Procedencia", datos.get('pais'))
        pdf.agregar_campo_valor("Tipo de Reaseguro", datos.get('tipo_reaseguro'))
        
        pdf.agregar_seccion_divider()
        
        # Table of shares
        pdf.agregar_subtitulo("Participacion en Ramos de Seguros")
        participaciones = datos.get('participaciones', [])
        
        if participaciones:
            headers = ["Tipo de Seguro", "Porcentaje de Participacion (%)"]
            rows = [[p.get('tipo_seguro'), f"{p.get('porcentaje', 0):.1f}%"] for p in participaciones]
            col_widths = [110, 70]
            pdf.agregar_tabla(headers, rows, col_widths)
        else:
            pdf.set_font('Helvetica', 'I', 9)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 6, clean_txt("No se registran participaciones activas para esta reaseguradora."), ln=True)
            
        return bytes(pdf.output())

    @staticmethod
    def generar_pdf_polizas_periodo(datos):
        f_inicio = datos.get('fecha_inicio', '')
        f_fin = datos.get('fecha_fin', '')
        
        pdf = PDFReporte(f"Reporte de Polizas por Periodo")
        pdf.add_page()
        
        pdf.agregar_titulo_documento("Polizas Emitidas en el Periodo")
        pdf.agregar_subtitulo(f"Rango de Fechas: {f_inicio} al {f_fin}")
        pdf.ln(2)
        
        polizas = datos.get('polizas', [])
        
        if polizas:
            headers = ["No.", "Cliente", "Tipo Seguro", "F. Inicio", "F. Fin", "Prima Mens."]
            rows = [[
                str(p.get('id')),
                p.get('cliente', ''),
                p.get('tipo_seguro', ''),
                p.get('fecha_inicio', ''),
                p.get('fecha_fin', ''),
                f"${p.get('prima', 0):,.2f}"
            ] for p in polizas]
            
            col_widths = [15, 55, 35, 25, 25, 25]
            pdf.agregar_tabla(headers, rows, col_widths)
            pdf.ln(2)
            
            # Print total count metric
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(pdf.c_primary_r, pdf.c_primary_g, pdf.c_primary_b)
            pdf.cell(0, 6, clean_txt(f"Total de polizas emitidas en el periodo: {len(polizas)}"), ln=True, align='R')
        else:
            pdf.set_font('Helvetica', 'I', 9)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 6, clean_txt("No se registraron emisiones de polizas en el periodo seleccionado."), ln=True)
            
        return bytes(pdf.output())

    @staticmethod
    def generar_pdf_estado_reclamaciones(datos):
        f_inicio = datos.get('fecha_inicio', '')
        f_fin = datos.get('fecha_fin', '')
        
        pdf = PDFReporte("Reporte de Estado de Reclamaciones")
        pdf.add_page()
        
        pdf.agregar_titulo_documento("Estado de las Reclamaciones")
        pdf.agregar_subtitulo(f"Rango de Siniestros: {f_inicio} al {f_fin}")
        pdf.ln(2)
        
        reclamaciones = datos.get('reclamaciones', [])
        
        if reclamaciones:
            headers = ["ID", "Cliente", "Monto Reclamado", "Monto Indemnizado", "Estado"]
            rows = [[
                str(r.get('id')),
                r.get('cliente', ''),
                f"${r.get('monto_reclamado', 0):,.2f}",
                f"${r.get('monto_indemnizado', 0):,.2f}",
                r.get('estado', '')
            ] for r in reclamaciones]
            
            col_widths = [15, 65, 35, 35, 30]
            pdf.agregar_tabla(headers, rows, col_widths)
            pdf.ln(2)
            
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(pdf.c_primary_r, pdf.c_primary_g, pdf.c_primary_b)
            pdf.cell(0, 6, clean_txt(f"Total de reclamaciones analizadas: {len(reclamaciones)}"), ln=True, align='R')
        else:
            pdf.set_font('Helvetica', 'I', 9)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 6, clean_txt("No se encontraron reclamaciones para el periodo de siniestro seleccionado."), ln=True)
            
        return bytes(pdf.output())

    @staticmethod
    def generar(nombre_reporte, datos):
        """
        Main routing function to generate PDF bytes according to the report name.
        """
        if 'Ingresos Mensuales' in nombre_reporte:
            return GeneradorPDF.generar_pdf_ingresos_mensuales(datos)
        elif 'Ficha Agencia' in nombre_reporte:
            return GeneradorPDF.generar_pdf_ficha_agencia(datos)
        elif 'Ficha Cliente' in nombre_reporte:
            return GeneradorPDF.generar_pdf_ficha_cliente(datos)
        elif 'Ficha Reaseguradora' in nombre_reporte:
            return GeneradorPDF.generar_pdf_ficha_reaseguradora(datos)
        elif 'Pólizas por Período' in nombre_reporte:
            return GeneradorPDF.generar_pdf_polizas_periodo(datos)
        elif 'Estado Reclamaciones' in nombre_reporte:
            return GeneradorPDF.generar_pdf_estado_reclamaciones(datos)
        else:
            # Generic fallback
            pdf = PDFReporte(nombre_reporte)
            pdf.add_page()
            pdf.agregar_titulo_documento(nombre_reporte)
            pdf.ln(5)
            pdf.agregar_subtitulo("Datos del Reporte")
            for k, v in datos.items():
                if isinstance(v, (dict, list)):
                    continue
                pdf.agregar_campo_valor(k.capitalize(), str(v))
            return bytes(pdf.output())
