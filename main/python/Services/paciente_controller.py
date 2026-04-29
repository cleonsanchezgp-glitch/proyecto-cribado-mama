import pandas as pd
from datetime import datetime
import os
import importlib.util

from main.python.Models.Estudio import Estudio
from main.python.Models.Paciente import Paciente
from main.python.Services import data_cleaner



class paciente_controller:




    def __init__(self, ruta_archivo: str):
        self.ruta_archivo = ruta_archivo
        self.pacientes: list[Paciente] = []


    def ejecutar(self):
        print(f"Cargando datos desde: {self.ruta_archivo}...")
        try:
            #self._limpiar_datos() #Limpiamos los datos del archivo antes de leerlos 
            datos = self._leer_archivo() #Leemos el archivo ya limpio
            self.pacientes = self._procesar_datos(datos) # Creamos los objetos Paciente y Estudio con los datos 
            self._mostrar_resumen()
        except Exception as e:
            print(f"Error durante la ejecución: {e}")
            raise


    def _limpiar_datos(self):
        """
        Lee el archivo original, lo limpia y guarda una versión limpia.
        Actualiza self.ruta_archivo para que _leer_archivo() use el archivo limpio.
        """
        print(f"Iniciando limpieza del archivo: {self.ruta_archivo}")
        try:
            if self.ruta_archivo.lower().endswith('.csv'):
                try:
                    df = pd.read_csv(self.ruta_archivo, header=2)
                except:
                    df = pd.read_csv(self.ruta_archivo, sep=';', header=2)
            else:
                df = pd.read_excel(self.ruta_archivo, header=2)

            print(f"Archivo cargado para limpieza. Filas iniciales: {len(df)}")

            # Eliminar duplicados 
            df.drop_duplicates(inplace=True)
            df.dropna(inplace=True)

            print(f"Filas tras limpieza: {len(df)}")

            # Guardar el archivo limpio en la misma carpeta que el original
            directorio = os.path.dirname(self.ruta_archivo)
            ruta_salida = os.path.join(directorio, "datos_ris_limpios.xlsx")


            df.to_excel(ruta_salida, index=False)
            print(f"Archivo limpio guardado en: {ruta_salida}")

            #Actualizamos la ruta para que _leer_archivo()
            # trabaje sobre el archivo limpio y no el original
            self.ruta_archivo = ruta_salida

        except Exception as e:
            print(f"Error al limpiar los datos: {e}")
            raise



#--------------------------------------------------------------------------------------------------------



#En este metodo realizamos la extracción de datos del archivo (excel, csv, xslv)
#Leemos el archivo y lo convertimos en una lista
    def _leer_archivo(self):
        _, extension = os.path.splitext(self.ruta_archivo)

        #Realizamos una conversión a minusculas para evitar posibles errores al momento de escribir la extensión del archivo
        #ya sea porque se escribio XsLv, CSV, etc ..
        extension = extension.lower()

        #Explicamos que si la extension es csv utilice Pandas para leer el archivo
        #
        if extension == '.csv':
            df = pd.read_csv(self.ruta_archivo, header=2)
        elif extension in ['.xlsx', '.xls']:
            df = pd.read_excel(self.ruta_archivo, header=0)
        else:
            raise ValueError(f"Formato de archivo no soportado: {extension}")

        print(f"Filas cargadas: {len(df)} | Columnas: {list(df.columns)}")  
        return df.to_dict(orient='records')



    def _parsear_hora(self, valor):
        if isinstance(valor, str):
            return datetime.strptime(valor.strip(), "%H:%M:%S").time()
        elif hasattr(valor, 'time'):
            return valor.time()
        else:
            return valor

    def _parsear_fecha(self, valor):
        if isinstance(valor, str):
            return datetime.strptime(valor.strip(), "%d/%m/%Y %H:%M:%S").date()
        elif hasattr(valor, 'date'):
            return valor.date()
        else:
            return valor

    def _parsear_float(self, valor):
        if isinstance(valor, str):
            valor = valor.strip()
        # Caso español: '1.188,0' -> miles con punto, decimal con coma
            if ',' in valor:
                valor = valor.replace('.', '').replace(',', '.')
            # Caso: '1.188.0' -> dos puntos, quitamos el primero
            elif valor.count('.') > 1:
                partes = valor.rsplit('.', 1)   # separa por el último punto
                valor = partes[0].replace('.', '') + '.' + partes[1]
            return float(valor)
        return float(valor) if valor is not None else 0.0

    def _procesar_datos(self, lista_filas):
        pacientes_temp = {}

        for fila in lista_filas:
            clave = (
                fila['Nº de Estudio'],
                fila['Edad']
            )

            if clave not in pacientes_temp:
                pacientes_temp[clave] = Paciente(
                    nombre       = str(fila['Nº de Estudio']),
                    edad         = int(fila['Edad']),
                    espesor_mama = int(fila['Espesor de Mama Comprimida (mm)'])
                )

            estudio = Estudio(
                tipo_actividad          = str(fila['Tipo de Actividad']).strip(),
                prestacion_realizada    = str(fila['Prestación Realizada']).strip(),
                hora_adquisicion        = self._parsear_hora(fila['Hora de Adquisición']),
                fecha_realizacion       = self._parsear_fecha(fila['Fecha de Realización']),
                lateralidad             = str(fila['Lateralidad']).strip(),
                proyeccion              = str(fila['Proyección']).strip(),
                fuerza_compresion       = str(fila['Fuerza de Compresión (N)']).strip(),
                tension_tubo            = int(self._parsear_float(fila['Tensión del Tubo (kVp)'])),
                corriente_tubo          = int(self._parsear_float(fila['Corriente del Tubo (mA)'])),
                carga                   = self._parsear_float(fila['Carga (mAs)']),
                tiempo_exposicion       = self._parsear_float(fila['Tiempo Exposición (ms)']),
                filtro                  = str(fila['Filtro']).strip(),
                kerma_entrada           = self._parsear_float(fila['Kerma a la Entrada (mGy)']),
                dosis_glandular         = self._parsear_float(fila['Dosis Glandular (mGy)']),
                distancia_foco_paciente = self._parsear_float(fila['Distancia Foco a Paciente']),
                distancia_foco_mama     = str(fila['Distancia Foco Entrada de la Mama (mm)']).strip(),
                factor_magnificacion    = self._parsear_float(fila['Factor de magnificación']),
                rejilla                 = str(fila['Rejilla']).strip(),
                temperatura             = self._parsear_float(fila['Temperatura Detector (ºC)']),
                grupo_espesor           = str(fila['Grupo por Espesor']).strip()
            )

            pacientes_temp[clave].agregar_estudio(estudio)

        return list(pacientes_temp.values())

    def _mostrar_resumen(self):
        print(f"\n{'='*60}")
        print(f"Total pacientes únicos: {len(self.pacientes)}")
        print(f"{'='*60}")
        for p in self.pacientes:
            print(f"\n{p}")
            for i, e in enumerate(p.estudios, start=1):
                print(f"  Estudio {i}: {e}")

# --- INICIO DEL PROGRAMA ---
if __name__ == "__main__":
    app = paciente_controller(r"C:\Users\User\Downloads\imagenes mam jul_dic26 (2).xlsx")
    app.ejecutar()