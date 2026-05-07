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

<<<<<<< HEAD
-- TABLA CLIENTE
CREATE TABLE CLIENTE (
    idCliente VARCHAR(15) PRIMARY KEY,
    noIdentificacion VARCHAR(15) NOT NULL,
=======
CREATE TABLE cliente (
    idcliente SERIAL PRIMARY KEY,
    no_identificacion VARCHAR(50) NOT NULL,
>>>>>>> 73161b5 (mis cambios)
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
