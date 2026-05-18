DROP TABLE IF EXISTS reporte_generado CASCADE;
DROP TABLE IF EXISTS reclamacion_rechazada CASCADE;
DROP TABLE IF EXISTS poliza_cancelada CASCADE;
DROP TABLE IF EXISTS participacion_reaseguro CASCADE;
DROP TABLE IF EXISTS reaseguradora CASCADE;
DROP TABLE IF EXISTS reclamacion CASCADE;
DROP TABLE IF EXISTS pago CASCADE;
DROP TABLE IF EXISTS poliza_cobertura CASCADE;
DROP TABLE IF EXISTS cobertura CASCADE;
DROP TABLE IF EXISTS poliza CASCADE;
DROP TABLE IF EXISTS cliente CASCADE;
DROP TABLE IF EXISTS agencia CASCADE;
DROP TABLE IF EXISTS tipo_reaseguro CASCADE;
DROP TABLE IF EXISTS estado_reclamacion CASCADE;
DROP TABLE IF EXISTS tipo_siniestro CASCADE;
DROP TABLE IF EXISTS estado_poliza CASCADE;
DROP TABLE IF EXISTS tipo_seguro CASCADE;
DROP TABLE IF EXISTS pais CASCADE;

CREATE TABLE pais (
    idpais SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE tipo_seguro (
    idtiposeguro SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE estado_poliza (
    idestadopoliza SERIAL PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL
);

CREATE TABLE tipo_siniestro (
    idtiposiniestro SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE estado_reclamacion (
    idestadoreclamacion SERIAL PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL
);

CREATE TABLE tipo_reaseguro (
    idtiporeaseguro SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE agencia (
    idagencia SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    director_general VARCHAR(100) NOT NULL,
    jefe_seguros VARCHAR(100) NOT NULL,
    jefe_reclamaciones VARCHAR(100) NOT NULL
);

CREATE TABLE cliente (
    idcliente SERIAL PRIMARY KEY,
    no_identificacion VARCHAR(50) NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    edad INTEGER CHECK (edad >= 0 AND edad <= 120),
    sexo CHAR(1) CHECK (sexo IN ('M', 'F')),
    dir_postal VARCHAR(150),
    telefono VARCHAR(20),
    correo VARCHAR(100) UNIQUE,
    idpais INTEGER NOT NULL,
    FOREIGN KEY (idpais) REFERENCES pais(idpais)
);

CREATE TABLE poliza (
    idpoliza SERIAL PRIMARY KEY,
    idtiposeguro INTEGER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    prima_mensual DECIMAL(12,2) NOT NULL CHECK (prima_mensual > 0),
    idestadopoliza INTEGER NOT NULL,
    monto_asegurado DECIMAL(15,2) NOT NULL CHECK (monto_asegurado > 0),
    idcliente INTEGER NOT NULL,
    FOREIGN KEY (idtiposeguro) REFERENCES tipo_seguro(idtiposeguro),
    FOREIGN KEY (idestadopoliza) REFERENCES estado_poliza(idestadopoliza),
    FOREIGN KEY (idcliente) REFERENCES cliente(idcliente)
);

CREATE TABLE cobertura (
    idcobertura SERIAL PRIMARY KEY,
    descripcion VARCHAR(200) NOT NULL
);

CREATE TABLE poliza_cobertura (
    idpoliza INTEGER NOT NULL,
    idcobertura INTEGER NOT NULL,
    monto DECIMAL(15,2) NOT NULL CHECK (monto > 0),
    PRIMARY KEY (idpoliza, idcobertura),
    FOREIGN KEY (idpoliza) REFERENCES poliza(idpoliza),
    FOREIGN KEY (idcobertura) REFERENCES cobertura(idcobertura)
);

CREATE TABLE pago (
    idpago SERIAL PRIMARY KEY,
    idpoliza INTEGER NOT NULL,
    fecha_pago DATE NOT NULL,
    monto_pagado DECIMAL(12,2) NOT NULL CHECK (monto_pagado > 0),
    FOREIGN KEY (idpoliza) REFERENCES poliza(idpoliza)
);

CREATE TABLE reclamacion (
    idreclamacion SERIAL PRIMARY KEY,
    idtiposiniestro INTEGER NOT NULL,
    fecha_siniestro DATE NOT NULL,
    monto_reclamado DECIMAL(15,2) NOT NULL CHECK (monto_reclamado > 0),
    idestadoreclamacion INTEGER NOT NULL,
    monto_indemnizado DECIMAL(15,2) DEFAULT 0,
    idpoliza INTEGER NOT NULL,
    FOREIGN KEY (idtiposiniestro) REFERENCES tipo_siniestro(idtiposiniestro),
    FOREIGN KEY (idestadoreclamacion) REFERENCES estado_reclamacion(idestadoreclamacion),
    FOREIGN KEY (idpoliza) REFERENCES poliza(idpoliza),
    CHECK (monto_indemnizado <= monto_reclamado)
);

CREATE TABLE reaseguradora (
    idreaseguradora SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    idpais INTEGER NOT NULL,
    idtiporeaseguro INTEGER NOT NULL,
    FOREIGN KEY (idpais) REFERENCES pais(idpais),
    FOREIGN KEY (idtiporeaseguro) REFERENCES tipo_reaseguro(idtiporeaseguro)
);

CREATE TABLE participacion_reaseguro (
    idreaseguradora INTEGER NOT NULL,
    idtiposeguro INTEGER NOT NULL,
    porcentaje DECIMAL(5,2) NOT NULL CHECK (porcentaje >= 0 AND porcentaje <= 100),
    PRIMARY KEY (idreaseguradora, idtiposeguro),
    FOREIGN KEY (idreaseguradora) REFERENCES reaseguradora(idreaseguradora),
    FOREIGN KEY (idtiposeguro) REFERENCES tipo_seguro(idtiposeguro)
);

CREATE TABLE poliza_cancelada (
    idpolizacancelada SERIAL PRIMARY KEY,
    motivo VARCHAR(200) NOT NULL,
    idpoliza INTEGER NOT NULL,
    FOREIGN KEY (idpoliza) REFERENCES poliza(idpoliza)
);

CREATE TABLE reclamacion_rechazada (
    idreclamacionrechazada SERIAL PRIMARY KEY,
    motivo VARCHAR(200) NOT NULL,
    idreclamacion INTEGER NOT NULL,
    FOREIGN KEY (idreclamacion) REFERENCES reclamacion(idreclamacion)
);

CREATE TABLE reporte_generado (
    id_reporte SERIAL PRIMARY KEY,
    nombre_reporte VARCHAR(150) NOT NULL,
    fecha_creacion DATE DEFAULT CURRENT_DATE,
    datos_reporte JSONB NOT NULL
);

COMMENT ON TABLE reporte_generado IS 'Histórico de reportes generados con persistencia de datos y timestamps.';


-- ==========================================
-- INSERCIÓN DE CATÁLOGOS BÁSICOS
-- ==========================================

INSERT INTO pais (idpais, nombre) VALUES 
(1, 'República Dominicana'),
(2, 'España'),
(3, 'México'),
(4, 'Estados Unidos');

INSERT INTO tipo_seguro (idtiposeguro, nombre) VALUES 
(1, 'Vida'),
(2, 'Automóvil'),
(3, 'Hogar'),
(4, 'Salud');

INSERT INTO estado_poliza (idestadopoliza, nombre) VALUES 
(1, 'Activa'),
(2, 'Vencida'),
(3, 'Cancelada');

INSERT INTO tipo_siniestro (idtiposiniestro, nombre) VALUES 
(1, 'Accidente de tráfico'),
(2, 'Robo'),
(3, 'Incendio'),
(4, 'Inundación'),
(5, 'Enfermedad');

INSERT INTO estado_reclamacion (idestadoreclamacion, nombre) VALUES 
(1, 'En proceso'),
(2, 'Aprobada'),
(3, 'Rechazada');

INSERT INTO tipo_reaseguro (idtiporeaseguro, nombre) VALUES 
(1, 'Cuota Parte'),
(2, 'Excedente'),
(3, 'Stop Loss');

-- Ajustar las secuencias de los catálogos para evitar conflictos futuros
SELECT SETVAL('pais_idpais_seq', (SELECT MAX(idpais) FROM pais));
SELECT SETVAL('tipo_seguro_idtiposeguro_seq', (SELECT MAX(idtiposeguro) FROM tipo_seguro));
SELECT SETVAL('estado_poliza_idestadopoliza_seq', (SELECT MAX(idestadopoliza) FROM estado_poliza));
SELECT SETVAL('tipo_siniestro_idtiposiniestro_seq', (SELECT MAX(idtiposiniestro) FROM tipo_siniestro));
SELECT SETVAL('estado_reclamacion_idestadoreclamacion_seq', (SELECT MAX(idestadoreclamacion) FROM estado_reclamacion));
SELECT SETVAL('tipo_reaseguro_idtiporeaseguro_seq', (SELECT MAX(idtiporeaseguro) FROM tipo_reaseguro));


-- ==========================================
-- INSERCIÓN DE DATOS DE PRUEBA (CLIENTES, PÓLIZAS, PAGOS, RECLAMACIONES)
-- ==========================================

-- Insertar 10 clientes
INSERT INTO cliente (idcliente, no_identificacion, nombre, apellidos, edad, sexo, dir_postal, telefono, correo, idpais) VALUES
(1, 'ID001', 'Juan', 'Perez', 30, 'M', '01001', '555-0001', 'juan@email.com', 1),
(2, 'ID002', 'Maria', 'Lopez', 25, 'F', '01002', '555-0002', 'maria@email.com', 1),
(3, 'ID003', 'Carlos', 'Gomez', 40, 'M', '01003', '555-0003', 'carlos@email.com', 2),
(4, 'ID004', 'Ana', 'Martinez', 35, 'F', '01004', '555-0004', 'ana@email.com', 1),
(5, 'ID005', 'Luis', 'Rodriguez', 28, 'M', '01005', '555-0005', 'luis@email.com', 1),
(6, 'ID006', 'Sofia', 'Hernandez', 45, 'F', '01006', '555-0006', 'sofia@email.com', 2),
(7, 'ID007', 'Pedro', 'Sanchez', 50, 'M', '01007', '555-0007', 'pedro@email.com', 1),
(8, 'ID008', 'Laura', 'Torres', 32, 'F', '01008', '555-0008', 'laura@email.com', 1),
(9, 'ID009', 'Miguel', 'Ramirez', 38, 'M', '01009', '555-0009', 'miguel@email.com', 2),
(10, 'ID010', 'Carmen', 'Flores', 29, 'F', '01010', '555-0010', 'carmen@email.com', 1);

-- Insertar pólizas (1-2 por cliente)
INSERT INTO poliza (idpoliza, idtiposeguro, fecha_inicio, fecha_fin, prima_mensual, idestadopoliza, monto_asegurado, idcliente) VALUES
(1, 1, '2025-01-01', '2026-01-01', 500.00, 1, 100000.00, 1),
(2, 2, '2025-02-01', '2026-02-01', 300.00, 1, 50000.00, 1),
(3, 1, '2025-03-01', '2026-03-01', 600.00, 1, 120000.00, 2),
(4, 2, '2025-04-01', '2026-04-01', 350.00, 1, 60000.00, 3),
(5, 3, '2025-05-01', '2026-05-01', 400.00, 1, 80000.00, 3),
(6, 1, '2025-06-01', '2026-06-01', 550.00, 1, 110000.00, 4),
(7, 2, '2025-07-01', '2026-07-01', 320.00, 1, 55000.00, 5),
(8, 3, '2025-08-01', '2026-08-01', 450.00, 1, 90000.00, 5),
(9, 2, '2025-09-01', '2026-09-01', 380.00, 1, 65000.00, 6),
(10, 1, '2025-10-01', '2026-10-01', 700.00, 1, 140000.00, 7),
(11, 3, '2025-11-01', '2026-11-01', 500.00, 1, 100000.00, 7),
(12, 1, '2025-12-01', '2026-12-01', 650.00, 1, 130000.00, 8),
(13, 2, '2026-01-01', '2027-01-01', 360.00, 1, 70000.00, 9),
(14, 1, '2026-02-01', '2027-02-01', 800.00, 1, 160000.00, 9),
(15, 3, '2026-03-01', '2027-03-01', 420.00, 1, 85000.00, 10);

-- Insertar coberturas
INSERT INTO cobertura (idcobertura, descripcion) VALUES
(1, 'Robo total'), (2, 'Daños a terceros'), (3, 'Incendio'), (4, 'Muerte accidental'), (5, 'Gastos medicos');

-- Asignar coberturas a pólizas (poliza_cobertura)
INSERT INTO poliza_cobertura (idpoliza, idcobertura, monto) VALUES
(1, 4, 50000.00), (1, 5, 30000.00), (2, 1, 20000.00), (2, 2, 15000.00),
(3, 4, 60000.00), (4, 1, 25000.00), (4, 2, 20000.00), (5, 3, 30000.00),
(6, 4, 55000.00), (7, 1, 22000.00), (7, 2, 18000.00), (8, 3, 35000.00),
(9, 1, 28000.00), (9, 2, 22000.00), (10, 4, 70000.00), (10, 5, 40000.00),
(11, 3, 45000.00), (12, 4, 65000.00), (12, 5, 35000.00), (13, 1, 30000.00),
(13, 2, 25000.00), (14, 4, 80000.00), (14, 5, 50000.00), (15, 3, 40000.00);

-- Insertar pagos (2-3 por póliza)
INSERT INTO pago (idpago, idpoliza, fecha_pago, monto_pagado) VALUES
(1, 1, '2025-01-05', 500.00), (2, 1, '2025-02-05', 500.00), (3, 1, '2025-03-05', 500.00),
(4, 2, '2025-02-05', 300.00), (5, 2, '2025-03-05', 300.00),
(6, 3, '2025-03-05', 600.00), (7, 3, '2025-04-05', 600.00), (8, 3, '2025-05-05', 600.00),
(9, 4, '2025-04-05', 350.00), (10, 4, '2025-05-05', 350.00),
(11, 5, '2025-05-05', 400.00), (12, 5, '2025-06-05', 400.00),
(13, 6, '2025-06-05', 550.00), (14, 6, '2025-07-05', 550.00), (15, 6, '2025-08-05', 550.00),
(16, 7, '2025-07-05', 320.00), (17, 7, '2025-08-05', 320.00),
(18, 8, '2025-08-05', 450.00), (19, 8, '2025-09-05', 450.00),
(20, 9, '2025-09-05', 380.00), (21, 9, '2025-10-05', 380.00), (22, 9, '2025-11-05', 380.00),
(23, 10, '2025-10-05', 700.00), (24, 10, '2025-11-05', 700.00),
(25, 11, '2025-11-05', 500.00), (26, 11, '2025-12-05', 500.00),
(27, 12, '2025-12-05', 650.00), (28, 12, '2026-01-05', 650.00), (29, 12, '2026-02-05', 650.00),
(30, 13, '2026-01-05', 360.00), (31, 13, '2026-02-05', 360.00),
(32, 14, '2026-02-05', 800.00), (33, 14, '2026-03-05', 800.00),
(34, 15, '2026-03-05', 420.00), (35, 15, '2026-04-05', 420.00);

-- Insertar reclamaciones (algunas pólizas)
INSERT INTO reclamacion (idreclamacion, idtiposiniestro, fecha_siniestro, monto_reclamado, idestadoreclamacion, monto_indemnizado, idpoliza) VALUES
(1, 1, '2025-02-15', 15000.00, 2, 12000.00, 1),
(2, 2, '2025-03-20', 8000.00, 1, 0.00, 2),
(3, 1, '2025-05-10', 12000.00, 2, 10000.00, 4),
(4, 2, '2025-08-15', 5000.00, 3, 0.00, 7),
(5, 1, '2025-11-20', 20000.00, 2, 18000.00, 10),
(6, 3, '2025-12-10', 10000.00, 1, 0.00, 10),
(7, 1, '2026-03-15', 25000.00, 2, 22000.00, 14);

-- Insertar reaseguradoras de prueba
INSERT INTO reaseguradora (idreaseguradora, nombre, idpais, idtiporeaseguro) VALUES
(1, 'Reaseguradora Universal', 1, 1),
(2, 'Mapfre Reaseguros', 2, 2);

-- Insertar participaciones de reaseguro de prueba
INSERT INTO participacion_reaseguro (idreaseguradora, idtiposeguro, porcentaje) VALUES
(1, 1, 30.00),
(1, 2, 20.00),
(2, 3, 50.00);

-- Inserción de Agencia de prueba por defecto si no existe
INSERT INTO agencia (idagencia, nombre, direccion, telefono, email, director_general, jefe_seguros, jefe_reclamaciones) VALUES
(1, 'Seguros La Confianza S.A.', 'Av. Winston Churchill 101, Santo Domingo', '809-555-1234', 'info@laconfianza.com.do', 'Lic. Alejandro Castro', 'Ing. Marcos Ruiz', 'Dra. Elena Medina')
ON CONFLICT DO NOTHING;

-- Ajustar las secuencias de las tablas de datos de prueba
SELECT SETVAL('cliente_idcliente_seq', (SELECT MAX(idcliente) FROM cliente));
SELECT SETVAL('poliza_idpoliza_seq', (SELECT MAX(idpoliza) FROM poliza));
SELECT SETVAL('cobertura_idcobertura_seq', (SELECT MAX(idcobertura) FROM cobertura));
SELECT SETVAL('pago_idpago_seq', (SELECT MAX(idpago) FROM pago));
SELECT SETVAL('reclamacion_idreclamacion_seq', (SELECT MAX(idreclamacion) FROM reclamacion));
SELECT SETVAL('reaseguradora_idreaseguradora_seq', (SELECT MAX(idreaseguradora) FROM reaseguradora));
SELECT SETVAL('agencia_idagencia_seq', (SELECT MAX(idagencia) FROM agencia));


-- ==========================================
-- CREACIÓN DE ÍNDICES DE BÚSQUEDA (Req. Rendimiento)
-- ==========================================
CREATE INDEX IF NOT EXISTS idx_cliente_no_identificacion ON cliente(no_identificacion);
CREATE INDEX IF NOT EXISTS idx_poliza_idcliente ON poliza(idcliente);
CREATE INDEX IF NOT EXISTS idx_reclamacion_idpoliza ON reclamacion(idpoliza);
CREATE INDEX IF NOT EXISTS idx_pago_idpoliza ON pago(idpoliza);


-- ==========================================
-- CREACIÓN DE DISPARADORES Y FUNCIONES (Triggers)
-- ==========================================

-- 1. Trigger de validación de vigencia de fechas en pólizas (fecha_fin > fecha_inicio)
CREATE OR REPLACE FUNCTION fn_validar_fechas_poliza()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.fecha_fin <= NEW.fecha_inicio THEN
        RAISE EXCEPTION 'La fecha de fin de la póliza (%s) debe ser posterior a la fecha de inicio (%s)', NEW.fecha_fin, NEW.fecha_inicio;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validar_fechas_poliza ON poliza;
CREATE TRIGGER trg_validar_fechas_poliza
BEFORE INSERT OR UPDATE ON poliza
FOR EACH ROW
EXECUTE FUNCTION fn_validar_fechas_poliza();


-- 2. Trigger de validación de reclamaciones (póliza activa y fecha del siniestro válida)
CREATE OR REPLACE FUNCTION fn_validar_creacion_reclamacion()
RETURNS TRIGGER AS $$
DECLARE
    poliza_estado VARCHAR(30);
    poliza_inicio DATE;
    poliza_fin DATE;
BEGIN
    -- Obtener datos de la póliza
    SELECT ep.nombre, p.fecha_inicio, p.fecha_fin
    INTO poliza_estado, poliza_inicio, poliza_fin
    FROM poliza p
    JOIN estado_poliza ep ON p.idestadopoliza = ep.idestadopoliza
    WHERE p.idpoliza = NEW.idpoliza;

    IF poliza_estado != 'Activa' THEN
        RAISE EXCEPTION 'No se pueden crear reclamaciones sobre pólizas con estado ''%''. La póliza debe estar activa.', poliza_estado;
    END IF;

    IF NEW.fecha_siniestro < poliza_inicio OR NEW.fecha_siniestro > poliza_fin THEN
        RAISE EXCEPTION 'La fecha del siniestro (%s) debe estar comprendida dentro de la vigencia de la póliza (%s al %s)', NEW.fecha_siniestro, poliza_inicio, poliza_fin;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validar_creacion_reclamacion ON reclamacion;
CREATE TRIGGER trg_validar_creacion_reclamacion
BEFORE INSERT OR UPDATE ON reclamacion
FOR EACH ROW
EXECUTE FUNCTION fn_validar_creacion_reclamacion();


-- 3. Trigger para validar que el porcentaje total de participación en reaseguro para un tipo de seguro no exceda el 100%
CREATE OR REPLACE FUNCTION fn_validar_porcentaje_participacion()
RETURNS TRIGGER AS $$
DECLARE
    total_porcentaje DECIMAL(5,2);
BEGIN
    -- Sumar los porcentajes de participación existentes, excluyendo la reaseguradora actual si es UPDATE
    SELECT COALESCE(SUM(porcentaje), 0)
    INTO total_porcentaje
    FROM participacion_reaseguro
    WHERE idtiposeguro = NEW.idtiposeguro AND idreaseguradora != NEW.idreaseguradora;

    IF (total_porcentaje + NEW.porcentaje) > 100.00 THEN
        RAISE EXCEPTION 'El porcentaje total de participación de reaseguro para este tipo de seguro no puede exceder el 100%% (Total acumulado: %s%%, Intentado agregar: %s%%)', total_porcentaje, NEW.porcentaje;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validar_porcentaje_participacion ON participacion_reaseguro;
CREATE TRIGGER trg_validar_porcentaje_participacion
BEFORE INSERT OR UPDATE ON participacion_reaseguro
FOR EACH ROW
EXECUTE FUNCTION fn_validar_porcentaje_participacion();
