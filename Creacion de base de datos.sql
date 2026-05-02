
-- CREACION DEL USUARIO PRINCIPAL PARA LA BASE DE DATOS


-- base de datos "FreePDB1"
ALTER SESSION SET CONTAINER = FREEPDB1;

-- Crear el usuario
CREATE USER CMAMA_DB_USR IDENTIFIED BY root;

-- Otorgar permiso para conectar
GRANT CREATE SESSION TO CMAMA_DB_USR;

-- Otorgar permiso para crear sus propias cosas (tablas, vistas, etc.)
GRANT CREATE TABLE, CREATE VIEW, CREATE SEQUENCE, CREATE PROCEDURE TO CMAMA_DB_USR;

-- IMPORTANTE: Darle espacio ilimitado en su propio almacenamiento (tablespace)
-- Sin esto, podrá crear la tabla pero no insertar datos.
ALTER USER CMAMA_DB_USR QUOTA UNLIMITED ON USERS;

--CRACION  DE LA ESTRUCTURA DE BASE DE DATOS

-- TABLA PACIENTE

-- TABLA PACIENTE
CREATE TABLE PACIENTE (
    id_paciente      VARCHAR2(20) PRIMARY KEY, -- DNI
    nombre           VARCHAR2(100) NOT NULL,
    edad             NUMBER(3),
    espesor_mama     NUMBER(10)
);

-- TABLA ESTUDIO
CREATE TABLE ESTUDIO (
    id_estudio              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_paciente             VARCHAR2(20) NOT NULL,
    tipo_actividad          VARCHAR2(100),
    prestacion_realizada    VARCHAR2(200),
    hora_adquisicion        TIMESTAMP,
    fecha_realizacion       DATE,
    lateralidad             VARCHAR2(50),
    proyeccion              VARCHAR2(50),
    fuerza_compresion       VARCHAR2(50),
    tension_tubo            NUMBER(10),
    corriente_tubo          NUMBER(10),
    carga                   BINARY_DOUBLE,
    tiempo_exposicion       BINARY_DOUBLE,
    filtro                  VARCHAR2(50),
    kerma_entrada           BINARY_DOUBLE,
    dosis_glandular         BINARY_DOUBLE,
    distancia_foco_paciente VARCHAR2(50),
    distancia_foco_mama     VARCHAR2(50),
    factor_magnificacion    BINARY_DOUBLE,
    rejilla                 VARCHAR2(50),
    temperatura             BINARY_DOUBLE,
    grupo_espesor           VARCHAR2(50),

    CONSTRAINT fk_estudio_paciente 
        FOREIGN KEY (id_paciente) 
        REFERENCES PACIENTE(id_paciente)
        ON DELETE CASCADE
);