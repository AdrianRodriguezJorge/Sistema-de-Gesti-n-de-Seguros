-- SISTEMA DE GESTION DE SEGUROS
-- Autores: 
-- Kevin de la Cruz Perez
-- Victor M. Moreno Iglesias
-- Xavier Ramirez Fernandez

-- TABLA PAIS
CREATE TABLE PAIS (
    idPais VARCHAR(3) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- TABLA TIPO_SEGURO
CREATE TABLE TIPO_SEGURO (
    idTipoSeguro INTEGER PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- TABLA ESTADO_POLIZA
CREATE TABLE ESTADO_POLIZA (
    idEstadoPoliza INTEGER PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL
);

-- TABLA TIPO_SINIESTRO
CREATE TABLE TIPO_SINIESTRO (
    idTipoSiniestro INTEGER PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- TABLA ESTADO_RECLAMACION
CREATE TABLE ESTADO_RECLAMACION (
    idEstadoReclamacion INTEGER PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL
);

-- TABLA TIPO_REASEGURO
CREATE TABLE TIPO_REASEGURO (
    idTipoReaseguro INTEGER PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- TABLA AGENCIA
CREATE TABLE AGENCIA (
    idAgencia INTEGER PRIMARY KEY CHECK (idAgencia = 1),
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    directorGeneral VARCHAR(100) NOT NULL,
    jefeSeguros VARCHAR(100) NOT NULL,
    jefeReclamaciones VARCHAR(100) NOT NULL
);

-- TABLA CLIENTE
CREATE TABLE CLIENTE (
    idCliente VARCHAR(15) PRIMARY KEY,
    noIdentificacion VARCHAR(15) NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    edad INTEGER CHECK (edad >= 0 AND edad <= 120),
    sexo CHAR(1) CHECK (sexo IN ('M', 'F')),
    dirPostal VARCHAR(150),
    telefono VARCHAR(20),
    correo VARCHAR(100) UNIQUE,
    idPais VARCHAR(3) NOT NULL,
    FOREIGN KEY (idPais) REFERENCES PAIS(idPais)
);

-- TABLA POLIZA
CREATE TABLE POLIZA (
    idPoliza VARCHAR(20) PRIMARY KEY,
    idTipoSeguro INTEGER NOT NULL,
    fechaInicio DATE NOT NULL,
    fechaFin DATE NOT NULL,
    primaMensual DECIMAL(12,2) NOT NULL CHECK (primaMensual > 0),
    idEstadoPoliza INTEGER NOT NULL,
    montoAsegurado DECIMAL(15,2) NOT NULL CHECK (montoAsegurado > 0),
    idCliente VARCHAR(15) NOT NULL,
    FOREIGN KEY (idTipoSeguro) REFERENCES TIPO_SEGURO(idTipoSeguro),
    FOREIGN KEY (idEstadoPoliza) REFERENCES ESTADO_POLIZA(idEstadoPoliza),
    FOREIGN KEY (idCliente) REFERENCES CLIENTE(idCliente)
);

-- TABLA COBERTURA
CREATE TABLE COBERTURA (
    idCobertura INTEGER PRIMARY KEY,
    descripcion VARCHAR(200) NOT NULL
);

-- TABLA POLIZA_COBERTURA
CREATE TABLE POLIZA_COBERTURA (
    idPoliza VARCHAR(20) NOT NULL,
    idCobertura INTEGER NOT NULL,
    monto DECIMAL(15,2) NOT NULL CHECK (monto > 0),
    PRIMARY KEY (idPoliza, idCobertura),
    FOREIGN KEY (idPoliza) REFERENCES POLIZA(idPoliza),
    FOREIGN KEY (idCobertura) REFERENCES COBERTURA(idCobertura)
);

-- TABLA PAGO
CREATE TABLE PAGO (
    idPago INTEGER PRIMARY KEY,
    idPoliza VARCHAR(20) NOT NULL,
    fechaPago DATE NOT NULL,
    montoPagado DECIMAL(12,2) NOT NULL CHECK (montoPagado > 0),
    FOREIGN KEY (idPoliza) REFERENCES POLIZA(idPoliza)
);

-- TABLA RECLAMACION
CREATE TABLE RECLAMACION (
    idReclamacion VARCHAR(20) PRIMARY KEY,
    idTipoSiniestro INTEGER NOT NULL,
    fechaSiniestro DATE NOT NULL,
    montoReclamado DECIMAL(15,2) NOT NULL CHECK (montoReclamado > 0),
    idEstadoReclamacion INTEGER NOT NULL,
    montoIndemnizado DECIMAL(15,2) DEFAULT 0,
    idPoliza VARCHAR(20) NOT NULL,
    FOREIGN KEY (idTipoSiniestro) REFERENCES TIPO_SINIESTRO(idTipoSiniestro),
    FOREIGN KEY (idEstadoReclamacion) REFERENCES ESTADO_RECLAMACION(idEstadoReclamacion),
    FOREIGN KEY (idPoliza) REFERENCES POLIZA(idPoliza),
    CHECK (montoIndemnizado <= montoReclamado)
);

-- TABLA REASEGURADORA
CREATE TABLE REASEGURADORA (
    idReaseguradora VARCHAR(15) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    idPais VARCHAR(3) NOT NULL,
    idTipoReaseguro INTEGER NOT NULL,
    FOREIGN KEY (idPais) REFERENCES PAIS(idPais),
    FOREIGN KEY (idTipoReaseguro) REFERENCES TIPO_REASEGURO(idTipoReaseguro)
);

-- TABLA PARTICIPACION_REASEGURO
CREATE TABLE PARTICIPACION_REASEGURO (
    idReaseguradora VARCHAR(15) NOT NULL,
    idTipoSeguro INTEGER NOT NULL,
    porcentaje DECIMAL(5,2) NOT NULL CHECK (porcentaje >= 0 AND porcentaje <= 100),
    PRIMARY KEY (idReaseguradora, idTipoSeguro),
    FOREIGN KEY (idReaseguradora) REFERENCES REASEGURADORA(idReaseguradora),
    FOREIGN KEY (idTipoSeguro) REFERENCES TIPO_SEGURO(idTipoSeguro)
);

-- TABLA POLIZA_CANCELADA
CREATE TABLE POLIZA_CANCELADA (
    idPolizaCancelada VARCHAR(20) PRIMARY KEY,
    motivo VARCHAR(200) NOT NULL,
    idPoliza VARCHAR(20) NOT NULL,
    FOREIGN KEY (idPoliza) REFERENCES POLIZA(idPoliza)
);

-- TABLA RECLAMACION_RECHAZADA
CREATE TABLE RECLAMACION_RECHAZADA (
    idReclamacionRechazada VARCHAR(20) PRIMARY KEY,
    motivo VARCHAR(200) NOT NULL,
    idReclamacion VARCHAR(20) NOT NULL,
    FOREIGN KEY (idReclamacion) REFERENCES RECLAMACION(idReclamacion)
);