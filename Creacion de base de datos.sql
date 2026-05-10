-- 1. CONFIGURACIÓN DE USUARIO Y PERMISOS
ALTER SESSION SET CONTAINER = FREEPDB1;

-- Limpieza previa de tablas (Primero la hija, luego la madre)
DROP TABLE ESTUDIO CASCADE CONSTRAINTS;
DROP TABLE PACIENTE CASCADE CONSTRAINTS;

-- 2. CREACIÓN DEL USUARIO (Omitir si ya está creado y configurado)
-- CREATE USER CMAMA_DB_USR IDENTIFIED BY root;
-- GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE SEQUENCE, CREATE PROCEDURE TO CMAMA_DB_USR;
-- ALTER USER CMAMA_DB_USR QUOTA UNLIMITED ON USERS;

-- 3. CREACIÓN DE LA ESTRUCTURA DE DATOS

-- TABLA PACIENTE
-- Mapeada con la clase Paciente(id, edad, espesor_mama_actual)
CREATE TABLE PACIENTE (
    id_paciente          VARCHAR2(50) PRIMARY KEY, -- ID / DNI
    edad                 NUMBER(3),
    espesor_mama_actual  NUMBER(10, 2)             -- Espesor registrado del paciente
);

-- TABLA ESTUDIO
-- Mapeada con la clase Estudio y sus cálculos de lateralidad
CREATE TABLE ESTUDIO (
    id_estudio              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_paciente             VARCHAR2(50) NOT NULL,
    tipo_actividad          VARCHAR2(100),
    prestacion_realizada    VARCHAR2(200),
    hora_adquisicion        VARCHAR2(20),  -- Almacenamos HH:MM:SS
    fecha_realizacion       DATE,
    lateralidad             VARCHAR2(20),
    proyeccion              VARCHAR2(50),
    fuerza_compresion       VARCHAR2(50),
    tension_tubo            NUMBER(10),
    espesor_mama_estudio    NUMBER(10, 2),
    corriente_tubo          NUMBER(10),
    carga                   NUMBER(12, 4),
    tiempo_exposicion       NUMBER(12, 4),
    filtro                  VARCHAR2(50),
    kerma_entrada           NUMBER(12, 4),
    dosis_glandular         NUMBER(12, 4),
    
    -- Campos calculados por la clase Estudio (Atributos discriminados)
    dosis_der               NUMBER(12, 4),
    dosis_izq               NUMBER(12, 4),
    espesor_der             NUMBER(10, 2),
    espesor_izq             NUMBER(10, 2),
    dosis_efectiva          NUMBER(12, 4),
    
    -- Datos de geometría y entorno
    distancia_foco_paciente NUMBER(12, 4),
    distancia_foco_mama     VARCHAR2(50),
    factor_magnificacion    NUMBER(10, 4),
    rejilla                 VARCHAR2(50),
    temperatura             NUMBER(10, 2),
    grupo_espesor           VARCHAR2(50),

    -- Relación: Si se borra un paciente, se borran sus estudios automáticamente
    CONSTRAINT fk_estudio_paciente 
        FOREIGN KEY (id_paciente) 
        REFERENCES PACIENTE(id_paciente)
        ON DELETE CASCADE
);