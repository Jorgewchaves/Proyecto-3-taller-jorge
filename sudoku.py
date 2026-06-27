import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random
from datetime import datetime
import webbrowser
import hashlib
import re
import sys
import pickle
import subprocess

#intentar importar reportlab
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    import webbrowser
    REPORTLAB_DISPONIBLE = True
except ImportError:
    REPORTLAB_DISPONIBLE = False
    print("ADVERTENCIA: reportlab no está instalado. Instálelo con: pip install reportlab")

#====================CLASES PARA EL TOP X====================

class Partida:
    #E:str jugador - nombre del jugador, str dificultad - nivel, int tiempo - segundos, str fecha_hora - fecha ISO
    #S:None
    #Funcion:Constructor de la clase Partida, almacena todos los datos de una partida completada
    def __init__(self, jugador, dificultad, tiempo, fecha_hora):
        self.jugador = jugador
        self.dificultad = dificultad
        self.tiempo = tiempo
        self.fecha_hora = fecha_hora
    
    #E:ninguna
    #S:str - string formateado con los datos de la partida
    #Funcion:Retorna un string con los datos de la partida formateados para mostrar
    def get_partida(self):
        tiempo_formateado = self.formatear_tiempo(self.tiempo)
        fecha_formateada = self.formatear_fecha(self.fecha_hora)
        return f"{self.jugador} - {tiempo_formateado} - {fecha_formateada}"
    
    #E:int tiempo_segundos - tiempo en segundos
    #S:str - tiempo formateado HH:MM:SS
    #Funcion:Convierte segundos a formato HH:MM:SS
    def formatear_tiempo(self, tiempo_segundos):
        horas = tiempo_segundos // 3600
        minutos = (tiempo_segundos % 3600) // 60
        segundos = tiempo_segundos % 60
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    
    #E:str fecha_hora_iso - fecha en formato ISO8601
    #S:str - fecha formateada DD-MM-AAAA HH:MM:SS
    #Funcion:Convierte fecha ISO a formato legible
    def formatear_fecha(self, fecha_hora_iso):
        try:
            if "T" in fecha_hora_iso:
                fecha_parte = fecha_hora_iso.split("T")[0]
                hora_parte = fecha_hora_iso.split("T")[1]
                anio = fecha_parte[0:4]
                mes = fecha_parte[4:6]
                dia = fecha_parte[6:8]
                hora = hora_parte[0:2]
                minuto = hora_parte[2:4]
                segundo = hora_parte[4:6]
                return f"{dia}-{mes}-{anio} {hora}:{minuto}:{segundo}"
        except:
            pass
        return fecha_hora_iso

class NodoABB:
    #E:Partida partida - objeto Partida a almacenar
    #S:None
    #Funcion:Constructor del nodo del ABB, almacena una partida y referencias a hijos
    def __init__(self, partida):
        self.partida = partida
        self.izquierdo = None
        self.derecho = None

class ABB:
    #E:ninguna
    #S:None
    #Funcion:Constructor del Arbol Binario de Busqueda, inicializa raiz como None
    def __init__(self):
        self.raiz = None
    
    #E:Partida partida - objeto Partida a insertar
    #S:None
    #Funcion:Inserta un nodo en el ABB usando recursividad, ordena por tiempo
    def insertar_nodo(self, partida):
        if self.raiz is None:
            self.raiz = NodoABB(partida)
        else:
            self._insertar_recursivo(self.raiz, partida)
    
    #E:NodoABB nodo - nodo actual en la recursión, Partida partida - objeto a insertar
    #S:None
    #Funcion:Funcion recursiva auxiliar para insertar nodo en el ABB
    def _insertar_recursivo(self, nodo, partida):
        if partida.tiempo < nodo.partida.tiempo:
            if nodo.izquierdo is None:
                nodo.izquierdo = NodoABB(partida)
            else:
                self._insertar_recursivo(nodo.izquierdo, partida)
        else:
            if nodo.derecho is None:
                nodo.derecho = NodoABB(partida)
            else:
                self._insertar_recursivo(nodo.derecho, partida)
    
    #E:ninguna
    #S:list - lista de strings con los datos de las partidas en orden ascendente
    #Funcion:Recorre el ABB en orden (in-order) y retorna lista con datos de partidas
    def recorrer_arbol(self):
        resultado = []
        self._recorrer_recursivo(self.raiz, resultado)
        return resultado
    
    #E:NodoABB nodo - nodo actual en la recursión, list resultado - lista para almacenar datos
    #S:None
    #Funcion:Funcion recursiva auxiliar para recorrido in-order del ABB
    def _recorrer_recursivo(self, nodo, resultado):
        if nodo is not None:
            self._recorrer_recursivo(nodo.izquierdo, resultado)
            resultado.append(nodo.partida.get_partida())
            self._recorrer_recursivo(nodo.derecho, resultado)
    
    #E:ninguna
    #S:int - cantidad de nodos en el arbol
    #Funcion:Cuenta el numero de nodos en el ABB usando recursividad
    def contar_nodos(self):
        return self._contar_recursivo(self.raiz)
    
    #E:NodoABB nodo - nodo actual en la recursion
    #S:int - cantidad de nodos en el subarbol
    #Funcion:Funcion recursiva auxiliar para contar nodos
    def _contar_recursivo(self, nodo):
        if nodo is None:
            return 0
        return 1 + self._contar_recursivo(nodo.izquierdo) + self._contar_recursivo(nodo.derecho)
    
    #E:int limite - numero maximo de nodos a retornar (0=todos)
    #S:list - lista de strings con los datos de las primeras N partidas
    #Funcion:Retorna las primeras N partidas (las mas rapidas) del arbol
    def obtener_primeros_n(self, limite):
        todos = self.recorrer_arbol()
        if limite <= 0 or limite >= len(todos):
            return todos
        return todos[:limite]
    
    #E:str nombre_usuario - nombre del usuario a eliminar
    #S:bool - True si se elimino al menos un nodo
    #Funcion:Elimina todos los nodos que pertenezcan al usuario especificado
    def eliminar_usuario(self, nombre_usuario):
        eliminados = False
        self.raiz, eliminados = self._eliminar_recursivo(self.raiz, nombre_usuario)
        return eliminados
    
    #E:NodoABB nodo - nodo actual, str nombre_usuario - usuario a eliminar
    #S:tuple - (NodoABB nuevo_nodo, bool eliminado)
    #Funcion:Funcion recursiva para eliminar nodos de un usuario especifico
    def _eliminar_recursivo(self, nodo, nombre_usuario):
        if nodo is None:
            return None, False
        
        eliminado = False
        
        #Eliminar del subarbol izquierdo
        nodo.izquierdo, elim_izq = self._eliminar_recursivo(nodo.izquierdo, nombre_usuario)
        if elim_izq:
            eliminado = True
        
        #Eliminar del subarbol derecho
        nodo.derecho, elim_der = self._eliminar_recursivo(nodo.derecho, nombre_usuario)
        if elim_der:
            eliminado = True
        
        #Verificar si el nodo actual pertenece al usuario
        if nodo.partida.jugador == nombre_usuario:
            #Este nodo debe ser eliminado
            #Fusionar los subarboles izquierdo y derecho
            if nodo.izquierdo is None:
                return nodo.derecho, True
            if nodo.derecho is None:
                return nodo.izquierdo, True
            
            #Tiene ambos hijos: encontrar el minimo del subarbol derecho
            sucesor = self._encontrar_minimo(nodo.derecho)
            #Reemplazar la partida del nodo actual con la del sucesor
            nodo.partida = sucesor.partida
            #Eliminar el sucesor del subarbol derecho
            nodo.derecho = self._eliminar_nodo_especifico(nodo.derecho, sucesor)
            return nodo, True
        
        return nodo, eliminado
    
    #E:NodoABB nodo - nodo actual, NodoABB nodo_a_eliminar - nodo a eliminar por referencia
    #S:NodoABB - nuevo nodo raiz del subarbol
    #Funcion:Elimina un nodo especifico por referencia (no por nombre)
    def _eliminar_nodo_especifico(self, nodo, nodo_a_eliminar):
        if nodo is None:
            return None
        if nodo is nodo_a_eliminar:
            #Fusionar hijos
            if nodo.izquierdo is None:
                return nodo.derecho
            if nodo.derecho is None:
                return nodo.izquierdo
            #Tiene ambos hijos
            sucesor = self._encontrar_minimo(nodo.derecho)
            nodo.partida = sucesor.partida
            nodo.derecho = self._eliminar_nodo_especifico(nodo.derecho, sucesor)
            return nodo
        
        nodo.izquierdo = self._eliminar_nodo_especifico(nodo.izquierdo, nodo_a_eliminar)
        nodo.derecho = self._eliminar_nodo_especifico(nodo.derecho, nodo_a_eliminar)
        return nodo
    
    #E:NodoABB nodo - nodo actual
    #S:NodoABB - nodo con el valor minimo (mas a la izquierda)
    #Funcion:Encuentra el nodo con el valor minimo en el arbol (el mas a la izquierda)
    def _encontrar_minimo(self, nodo):
        while nodo.izquierdo is not None:
            nodo = nodo.izquierdo
        return nodo

#====================FUNCIONES BASICAS====================

#E:ninguna
#S:str - Ruta absoluta de la carpeta donde se encuentra este script
#Funcion:Obtiene el directorio donde está guardado el archivo .py actual
def obtener_directorio_script():
    return os.path.dirname(os.path.abspath(__file__))

#E:ninguna
#S:None
#Funcion:Abre el manual de usuario en formato PDF
def abrir_manual_usuario():
    directorio_script = obtener_directorio_script()
    nombre_manual = os.path.join(directorio_script, "manual_de_usuario_sudoku.pdf")
    
    if os.path.exists(nombre_manual):
        webbrowser.open(nombre_manual)
    else:
        messagebox.showerror("Error", f"No se encuentra el archivo del manual de usuario.\n\nSe esperaba en: {nombre_manual}")

#E:ninguna
#S:dict - Diccionario con la configuracion por defecto
#Funcion:Resetea el archivo de configuracion a los valores por defecto y los devuelve
def resetear_configuracion_a_default():
    directorio_script = obtener_directorio_script()
    archivo_config = os.path.join(directorio_script, "sudoku2026configuracion.json")
    
    configuracion_default = {
        "nivel": "facil",
        "reloj": "cronometro",
        "top_x": 0,
        "elementos": "numeros",
        "tiempos_multinivel": {
            "facil": {"horas": 0, "minutos": 0, "segundos": 0},
            "intermedio": {"horas": 0, "minutos": 0, "segundos": 0},
            "dificil": {"horas": 0, "minutos": 0, "segundos": 0}
        }
    }
    
    with open(archivo_config, "w") as archivo:
        json.dump(configuracion_default, archivo, indent=4)
    
    return configuracion_default

#====================FUNCIONES DE USUARIOS====================

#E:ninguna
#S:list - Lista de usuarios del archivo usuarios.json
#Funcion:Carga el archivo de usuarios o crea uno vacío si no existe
def cargar_usuarios():
    directorio = obtener_directorio_script()
    archivo = os.path.join(directorio, "usuarios.json")
    
    if not os.path.exists(archivo):
        with open(archivo, "w", encoding='utf-8') as f:
            json.dump([], f, indent=4)
        return []
    
    try:
        with open(archivo, "r", encoding='utf-8-sig') as f:
            contenido = f.read().strip()
            if not contenido:
                with open(archivo, "w", encoding='utf-8') as f2:
                    json.dump([], f2, indent=4)
                return []
            return json.loads(contenido)
    except json.JSONDecodeError as e:
        print(f"Error JSON en usuarios.json: {e}")
        try:
            with open(archivo, "r", encoding='utf-8') as f:
                contenido = f.read()
                import re
                contenido = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', contenido)
                if contenido.strip():
                    return json.loads(contenido)
        except:
            pass
        with open(archivo, "w", encoding='utf-8') as f:
            json.dump([], f, indent=4)
        return []
    except Exception as e:
        print(f"Error al cargar usuarios: {e}")
        return []

#E:list usuarios - Lista de usuarios a guardar
#S:None
#Funcion:Guarda la lista de usuarios en el archivo usuarios.json
def guardar_usuarios(usuarios):
    directorio = obtener_directorio_script()
    archivo = os.path.join(directorio, "usuarios.json")
    
    try:
        with open(archivo, "w", encoding='utf-8') as f:
            json.dump(usuarios if usuarios else [], f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar usuarios: {e}")

#E:str correo - Correo electrónico a validar
#S:bool - True si el correo tiene formato válido, False en caso contrario
#Funcion:Valida que el correo tenga formato correcto usando expresión regular
def validar_correo(correo):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, correo) is not None

#E:str nombre - Nombre de usuario a validar
#S:bool - True si el nombre es válido, False en caso contrario
#Funcion:Valida que el nombre tenga entre 1 y 30 caracteres y solo letras,números,espacios y guiones bajos
def validar_nombre(nombre):
    if len(nombre) < 1 or len(nombre) > 30:
        return False
    patron = r'^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s0-9_]+$'
    return re.match(patron, nombre) is not None

#E:ninguna
#S:str - Código de 6 dígitos como string
#Funcion:Genera un código de 6 dígitos aleatorio
def generar_codigo_ingreso():
    return f"{random.randint(0, 999999):06d}"

#E:str codigo - Código a hashear
#S:str - Hash SHA256 del código
#Funcion:Hashea el código usando SHA256 para almacenamiento seguro
def hashear_codigo(codigo):
    return hashlib.sha256(codigo.encode()).hexdigest()

#E:list usuarios - Lista de usuarios existentes
#S:int - Siguiente ID disponible
#Funcion:Obtiene el siguiente ID disponible incrementando el máximo actual en 1
def obtener_siguiente_id(usuarios):
    if not usuarios:
        return 1
    return max(u["id"] for u in usuarios) + 1

#E:list usuarios - Lista de usuarios existentes
#E:str correo - Correo a verificar
#S:bool - True si el correo ya existe, False en caso contrario
#Funcion:Verifica si un correo ya está registrado en la lista de usuarios
def usuario_existe_por_correo(usuarios, correo):
    return any(u["correo"].lower() == correo.lower() for u in usuarios)

#E:list usuarios - Lista de usuarios existentes
#E:str nombre - Nombre a verificar
#S:bool - True si el nombre ya existe, False en caso contrario
#Funcion:Verifica si un nombre ya está registrado en la lista de usuarios
def usuario_existe_por_nombre(usuarios, nombre):
    return any(u["nombre"].lower() == nombre.lower() for u in usuarios)

#E:str correo - Correo del nuevo usuario
#E:str codigo - Código de ingreso inicial
#S:tuple - (dict usuario_creado o None, str mensaje)
#Funcion:Crea un nuevo usuario con correo y código (sin nombre aún)
def crear_usuario_sin_nombre(correo, codigo):
    usuarios = cargar_usuarios()
    
    if usuario_existe_por_correo(usuarios, correo):
        return None, "El correo ya está registrado"
    
    nuevo_usuario = {
        "id": obtener_siguiente_id(usuarios),
        "correo": correo.lower(),
        "codigo_ingreso": hashear_codigo(codigo),
        "nombre": "",
        "fecha_creacion": datetime.now().isoformat()
    }
    
    usuarios.append(nuevo_usuario)
    guardar_usuarios(usuarios)
    
    return nuevo_usuario, "Usuario creado exitosamente"

#E:str correo - Correo del usuario a buscar
#S:dict - Diccionario del usuario o None si no existe
#Funcion:Obtiene un usuario por su correo electrónico
def obtener_usuario_por_correo(correo):
    usuarios = cargar_usuarios()
    for usuario in usuarios:
        if usuario["correo"].lower() == correo.lower():
            return usuario
    return None

#E:str correo - Correo del usuario
#E:str nombre - Nuevo nombre a asignar
#S:bool - True si se actualizó correctamente, False en caso contrario
#Funcion:Actualiza el nombre de un usuario (se guarda inmediatamente al ingresarlo)
def actualizar_nombre_usuario(correo, nombre):
    usuarios = cargar_usuarios()
    for usuario in usuarios:
        if usuario["correo"].lower() == correo.lower():
            usuario["nombre"] = nombre
            guardar_usuarios(usuarios)
            return True
    return False

#E:str correo - Correo del usuario a eliminar
#S:bool - True si se elimino correctamente, False en caso contrario
#Funcion:Elimina un usuario del archivo usuarios.json por su correo
def eliminar_usuario_por_correo(correo):
    try:
        usuarios = cargar_usuarios()
        for i, usuario in enumerate(usuarios):
            if usuario["correo"].lower() == correo.lower():
                del usuarios[i]
                guardar_usuarios(usuarios)
                return True
        return False
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        return False

#E:str nombre - Nombre del usuario a eliminar de la bitacora
#S:bool - True si se elimino al menos una partida
#Funcion:Elimina todas las partidas de un usuario de los arboles ABB
def eliminar_usuario_de_bitacora(nombre):
    try:
        abb_facil, abb_intermedio, abb_dificil = cargar_arboles_bitacora()
        
        eliminados_facil = abb_facil.eliminar_usuario(nombre)
        eliminados_intermedio = abb_intermedio.eliminar_usuario(nombre)
        eliminados_dificil = abb_dificil.eliminar_usuario(nombre)
        
        guardar_arboles_bitacora(abb_facil, abb_intermedio, abb_dificil)
        
        return eliminados_facil or eliminados_intermedio or eliminados_dificil
    except Exception as e:
        print(f"Error al eliminar usuario de bitacora: {e}")
        return False

#====================FUNCIONES DE GENERACION DE SUDOKU CON SOLUCION UNICA====================

#E:ninguna
#S:list - Tablero 9x9 con Sudoku resuelto
#Funcion:Genera un Sudoku completamente resuelto usando backtracking con valores aleatorios
def generar_sudoku_valido():
    tablero = [[0 for _ in range(9)] for _ in range(9)]
    
    def es_valido(tablero, fila, columna, numero):
        for c in range(9):
            if tablero[fila][c] == numero:
                return False
        for r in range(9):
            if tablero[r][columna] == numero:
                return False
        caja_fila = (fila // 3) * 3
        caja_columna = (columna // 3) * 3
        for r in range(caja_fila, caja_fila + 3):
            for c in range(caja_columna, caja_columna + 3):
                if tablero[r][c] == numero:
                    return False
        return True
    
    def resolver(tablero):
        for fila in range(9):
            for columna in range(9):
                if tablero[fila][columna] == 0:
                    numeros = list(range(1, 10))
                    random.shuffle(numeros)
                    for numero in numeros:
                        if es_valido(tablero, fila, columna, numero):
                            tablero[fila][columna] = numero
                            if resolver(tablero):
                                return True
                            tablero[fila][columna] = 0
                    return False
        return True
    
    resolver(tablero)
    return tablero

#E:list tablero - Tablero de Sudoku para contar soluciones
#S:int - Numero de soluciones (maximo 2 para eficiencia)
#Funcion:Cuenta cuantas soluciones tiene un tablero, limitando a 2
def contar_soluciones(tablero):
    soluciones = [0]
    
    def es_valido(tablero, fila, columna, numero):
        for c in range(9):
            if tablero[fila][c] == numero:
                return False
        for r in range(9):
            if tablero[r][columna] == numero:
                return False
        caja_fila = (fila // 3) * 3
        caja_columna = (columna // 3) * 3
        for r in range(caja_fila, caja_fila + 3):
            for c in range(caja_columna, caja_columna + 3):
                if tablero[r][c] == numero:
                    return False
        return True
    
    def resolver_contar(tablero):
        if soluciones[0] >= 2:
            return True
        for fila in range(9):
            for columna in range(9):
                if tablero[fila][columna] == 0:
                    for numero in range(1, 10):
                        if es_valido(tablero, fila, columna, numero):
                            tablero[fila][columna] = numero
                            if resolver_contar(tablero):
                                return True
                            tablero[fila][columna] = 0
                    return False
        soluciones[0] += 1
        return False
    
    copia = [fila[:] for fila in tablero]
    resolver_contar(copia)
    return soluciones[0]

#E:list tablero - Tablero de Sudoku resuelto
#E:int cantidad - Numero de celdas a eliminar
#S:list - Tablero con celdas eliminadas y solucion unica
#Funcion:Elimina celdas del tablero asegurando que solo tenga una solucion
def eliminar_celdas_con_solucion_unica(tablero, cantidad):
    copia = [fila[:] for fila in tablero]
    
    posiciones = [(f, c) for f in range(9) for c in range(9)]
    random.shuffle(posiciones)
    
    celdas_eliminadas = 0
    posiciones_idx = 0
    intentos_fallidos = 0
    max_intentos = 300
    
    while celdas_eliminadas < cantidad and posiciones_idx < len(posiciones) and intentos_fallidos < max_intentos:
        fila, columna = posiciones[posiciones_idx]
        posiciones_idx += 1
        
        if copia[fila][columna] == 0:
            continue
        
        valor_guardado = copia[fila][columna]
        copia[fila][columna] = 0
        
        soluciones = contar_soluciones(copia)
        
        if soluciones == 1:
            celdas_eliminadas += 1
            intentos_fallidos = 0
        else:
            copia[fila][columna] = valor_guardado
            intentos_fallidos += 1
        
        if intentos_fallidos > 50 and celdas_eliminadas < cantidad:
            posiciones_restantes = [(f, c) for f in range(9) for c in range(9) if copia[f][c] != 0]
            random.shuffle(posiciones_restantes)
            posiciones = posiciones + posiciones_restantes
            intentos_fallidos = 0
    
    if celdas_eliminadas < cantidad:
        for fila in range(9):
            for columna in range(9):
                if celdas_eliminadas >= cantidad:
                    break
                if copia[fila][columna] != 0:
                    valor_guardado = copia[fila][columna]
                    copia[fila][columna] = 0
                    soluciones = contar_soluciones(copia)
                    if soluciones == 1:
                        celdas_eliminadas += 1
                    else:
                        copia[fila][columna] = valor_guardado
            if celdas_eliminadas >= cantidad:
                break
    
    return copia

#E:str dificultad - Nivel de dificultad ("facil","intermedio","dificil")
#S:tuple - (tablero_juego, tablero_solucion) ambos como listas 9x9
#Funcion:Genera una partida de Sudoku con solucion unica
def generar_partida_sudoku(dificultad):
    tablero_resuelto = generar_sudoku_valido()
    
    eliminaciones = {
        "facil": 25,
        "intermedio": 30,
        "dificil": 35
    }
    cantidad = eliminaciones.get(dificultad, 15)
    
    tablero_juego = eliminar_celdas_con_solucion_unica(tablero_resuelto, cantidad)
    
    return tablero_juego, tablero_resuelto

#E:list tablero - Tablero 9x9 de Sudoku
#S:dict - Diccionario con posiciones "fila,columna": valor para celdas no vacías
#Funcion:Convierte un tablero en un diccionario de posiciones con valores
def partida_a_diccionario(tablero):
    resultado = {}
    for fila in range(9):
        for columna in range(9):
            if tablero[fila][columna] != 0:
                resultado[f"{fila},{columna}"] = tablero[fila][columna]
    return resultado

#E:ninguna
#S:dict - Historial de partidas por nivel {"facil":[],"intermedio":[],"dificil":[]}
#Funcion:Carga el historial de partidas generadas desde historial_partidas.json
def cargar_historial_partidas():
    directorio = obtener_directorio_script()
    archivo = os.path.join(directorio, "historial_partidas.json")
    
    if not os.path.exists(archivo):
        historial = {"facil": [], "intermedio": [], "dificil": []}
        with open(archivo, "w") as f:
            json.dump(historial, f, indent=4)
        return historial
    
    with open(archivo, "r") as f:
        return json.load(f)

#E:dict historial - Historial de partidas
#S:None
#Funcion:Guarda el historial de partidas generadas en historial_partidas.json
def guardar_historial_partidas(historial):
    directorio = obtener_directorio_script()
    archivo = os.path.join(directorio, "historial_partidas.json")
    
    with open(archivo, "w") as f:
        json.dump(historial, f, indent=4)

#E:None
#S:None
#Funcion:Vacia el historial de partidas al iniciar el programa
def vaciar_historial_partidas():
    historial = {"facil": [], "intermedio": [], "dificil": []}
    guardar_historial_partidas(historial)

#E:dict historial - Historial de partidas
#E:str nivel - Nivel de dificultad
#E:str partida - Partida en formato JSON string
#S:bool - True si la partida ya está en el historial, False en caso contrario
#Funcion:Verifica si una partida ya está en el historial del nivel especificado
def partida_en_historial(historial, nivel, partida):
    return partida in historial[nivel]

#E:dict historial - Historial de partidas
#E:str nivel - Nivel de dificultad
#E:str partida - Partida en formato JSON string
#S:None
#Funcion:Agrega una partida al historial manteniendo máximo 50 partidas por nivel
def agregar_partida_historial(historial, nivel, partida):
    if partida not in historial[nivel]:
        historial[nivel].append(partida)
        if len(historial[nivel]) > 50:
            historial[nivel].pop(0)
        guardar_historial_partidas(historial)

#E:str nivel - Nivel de dificultad
#S:tuple - (tablero_juego, tablero_solucion) partida única no repetida con solucion unica
#Funcion:Genera una partida única que no esté en el historial
def generar_partida_unica(nivel):
    historial = cargar_historial_partidas()
    intentos = 0
    max_intentos = 100
    
    while intentos < max_intentos:
        tablero_juego, tablero_solucion = generar_partida_sudoku(nivel)
        partida_dict = partida_a_diccionario(tablero_juego)
        partida_str = json.dumps(partida_dict, sort_keys=True)
        
        if not partida_en_historial(historial, nivel, partida_str):
            agregar_partida_historial(historial, nivel, partida_str)
            return tablero_juego, tablero_solucion
        
        intentos += 1
    
    tablero_juego, tablero_solucion = generar_partida_sudoku(nivel)
    return tablero_juego, tablero_solucion

#====================FUNCION PARA VALIDAR ELEMENTOS PERSONALIZADOS====================

#E:list elementos - Lista de 9 elementos ingresados por el usuario
#S:tuple - (bool es_valido, str mensaje_error)
#Funcion:Valida que los elementos personalizados cumplan con las restricciones
#Permite numeros romanos (I, II, III, IV, V, VI, VII, VIII, IX) como excepcion
#Todos los elementos deben ser diferentes entre si
def validar_elementos_personalizados(elementos):
    if len(elementos) != 9:
        return False, "Debe ingresar exactamente 9 elementos"
    
    numeros_romanos_validos = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
    
    for i, elem in enumerate(elementos):
        if elem in numeros_romanos_validos:
            continue
        
        if len(elem) != 1:
            return False, f"El elemento {i+1} debe ser un solo caracter (a menos que sea un numero romano valido)"
        if elem.isspace():
            return False, f"El elemento {i+1} no puede ser un espacio en blanco"
        if ord(elem) < 33 or ord(elem) > 126:
            return False, f"El elemento {i+1} no es un caracter imprimible"
        if elem.isdigit():
            return False, "Los elementos no pueden ser numeros (0-9)"
        if elem.isupper():
            return False, f"El elemento {i+1} no puede ser una letra mayuscula (excepto numeros romanos)"
    
    if len(set(elementos)) != 9:
        return False, "Los elementos no pueden repetirse entre si"
    
    return True, "Elementos validos"

#====================FUNCIONES DE BITACORA Y TOP X====================

#E:str nombre_jugador - Nombre del jugador
#E:str dificultad - Nivel de dificultad
#E:int segundos - Tiempo en segundos que tardo
#E:str fecha_hora - Fecha y hora en formato ISO8601
#S:None
#Funcion:Guarda una partida completada en el archivo binario de bitacora usando ABB
def guardar_partida_en_bitacora(nombre_jugador, dificultad, segundos, fecha_hora):
    directorio_script = obtener_directorio_script()
    nombre_archivo = os.path.join(directorio_script, "sudoku2026_bitacora_jugadas.pkl")
    
    abb_facil, abb_intermedio, abb_dificil = cargar_arboles_bitacora()
    
    partida = Partida(nombre_jugador, dificultad, segundos, fecha_hora)
    
    if dificultad == "facil":
        abb_facil.insertar_nodo(partida)
    elif dificultad == "intermedio":
        abb_intermedio.insertar_nodo(partida)
    elif dificultad == "dificil":
        abb_dificil.insertar_nodo(partida)
    else:
        return
    
    guardar_arboles_bitacora(abb_facil, abb_intermedio, abb_dificil)

#E:ninguna
#S:tuple - (ABB, ABB, ABB) tres arboles para facil, intermedio y dificil
#Funcion:Carga los tres ABB desde el archivo binario, si no existe crea arboles vacios
def cargar_arboles_bitacora():
    directorio_script = obtener_directorio_script()
    nombre_archivo = os.path.join(directorio_script, "sudoku2026_bitacora_jugadas.pkl")
    
    if not os.path.exists(nombre_archivo):
        return ABB(), ABB(), ABB()
    
    try:
        with open(nombre_archivo, "rb") as archivo:
            datos = pickle.load(archivo)
            if isinstance(datos, tuple) and len(datos) == 3:
                return datos[0], datos[1], datos[2]
            else:
                return ABB(), ABB(), ABB()
    except:
        return ABB(), ABB(), ABB()

#E:ABB abb_facil - Arbol para nivel facil
#E:ABB abb_intermedio - Arbol para nivel intermedio
#E:ABB abb_dificil - Arbol para nivel dificil
#S:None
#Funcion:Guarda los tres ABB en el archivo binario usando pickle
def guardar_arboles_bitacora(abb_facil, abb_intermedio, abb_dificil):
    directorio_script = obtener_directorio_script()
    nombre_archivo = os.path.join(directorio_script, "sudoku2026_bitacora_jugadas.pkl")
    
    with open(nombre_archivo, "wb") as archivo:
        pickle.dump((abb_facil, abb_intermedio, abb_dificil), archivo)

#E:str nombre - Nombre del jugador a verificar
#S:bool - True si el nombre ya existe en la bitacora, False en caso contrario
#Funcion:Verifica si un nombre de jugador ya existe en el archivo de bitacora
def nombre_existe_en_bitacora(nombre):
    abb_facil, abb_intermedio, abb_dificil = cargar_arboles_bitacora()
    
    def buscar_nombre_en_arbol(arbol, nombre_buscar):
        def recorrer_busqueda(nodo):
            if nodo is None:
                return False
            if nodo.partida.jugador == nombre_buscar:
                return True
            return recorrer_busqueda(nodo.izquierdo) or recorrer_busqueda(nodo.derecho)
        return recorrer_busqueda(arbol.raiz)
    
    return (buscar_nombre_en_arbol(abb_facil, nombre) or
            buscar_nombre_en_arbol(abb_intermedio, nombre) or
            buscar_nombre_en_arbol(abb_dificil, nombre))

#E:str tiempo_segundos - Tiempo en segundos
#S:str - Tiempo formateado como HH:MM:SS
#Funcion:Convierte segundos a formato HH:MM:SS
def formatear_tiempo(tiempo_segundos):
    horas = tiempo_segundos // 3600
    minutos = (tiempo_segundos % 3600) // 60
    segundos = tiempo_segundos % 60
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

#E:str fecha_hora_iso - Fecha en formato ISO8601 (YYYYMMDDTHHMMSS)
#S:str - Fecha formateada como DD-MM-AAAA HH:MM:SS
#Funcion:Convierte fecha ISO8601 a formato legible DD-MM-AAAA HH:MM:SS
def formatear_fecha(fecha_hora_iso):
    try:
        if "T" in fecha_hora_iso:
            fecha_parte = fecha_hora_iso.split("T")[0]
            hora_parte = fecha_hora_iso.split("T")[1]
            anio = fecha_parte[0:4]
            mes = fecha_parte[4:6]
            dia = fecha_parte[6:8]
            hora = hora_parte[0:2]
            minuto = hora_parte[2:4]
            segundo = hora_parte[4:6]
            return f"{dia}-{mes}-{anio} {hora}:{minuto}:{segundo}"
    except:
        pass
    return fecha_hora_iso

#E:ninguna
#S:bool - True si se genero el TOP X, False en caso contrario
#Funcion:Genera un archivo PDF o TXT con el TOP X de mejores tiempos usando los ABB
def generar_top_x():
    directorio_script = obtener_directorio_script()
    archivo_config = os.path.join(directorio_script, "sudoku2026configuracion.json")
    
    top_x = 0
    if os.path.exists(archivo_config):
        with open(archivo_config, "r") as archivo:
            config = json.load(archivo)
            top_x = config.get("top_x", 0)
    
    abb_facil, abb_intermedio, abb_dificil = cargar_arboles_bitacora()
    
    total_nodos = abb_facil.contar_nodos() + abb_intermedio.contar_nodos() + abb_dificil.contar_nodos()
    if total_nodos == 0:
        messagebox.showinfo("TOP X", "No hay partidas registradas en la bitacora.")
        return False
    
    datos_facil = abb_facil.obtener_primeros_n(top_x)
    datos_intermedio = abb_intermedio.obtener_primeros_n(top_x)
    datos_dificil = abb_dificil.obtener_primeros_n(top_x)
    
    partidas_por_nivel = {
        "facil": datos_facil,
        "intermedio": datos_intermedio,
        "dificil": datos_dificil
    }
    
    hay_datos = False
    for nivel in partidas_por_nivel:
        if partidas_por_nivel[nivel]:
            hay_datos = True
            break
    
    if not hay_datos:
        messagebox.showinfo("TOP X", "No hay partidas completadas en la bitacora.")
        return False
    
    if not REPORTLAB_DISPONIBLE:
        nombre_txt = os.path.join(directorio_script, "sudoku2026_top_x.txt")
        with open(nombre_txt, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("TOP X - MEJORES TIEMPOS\n")
            f.write("=" * 60 + "\n\n")
            
            if top_x > 0:
                f.write(f"Mostrando las mejores {top_x} partidas por nivel\n\n")
            else:
                f.write("Mostrando todas las partidas registradas\n\n")
            
            nombres_nivel = {
                "facil": "NIVEL FACIL",
                "intermedio": "NIVEL INTERMEDIO",
                "dificil": "NIVEL DIFICIL"
            }
            
            for nivel, partidas in partidas_por_nivel.items():
                f.write(f"\n{nombres_nivel[nivel]}\n")
                f.write("-" * 40 + "\n")
                if partidas:
                    for i, partida_str in enumerate(partidas, 1):
                        f.write(f"{i}. {partida_str}\n")
                else:
                    f.write("No hay partidas registradas\n")
        
        os.startfile(nombre_txt)
        return True
    
    nombre_pdf = os.path.join(directorio_script, "sudoku2026_top_x.pdf")
    doc = SimpleDocTemplate(nombre_pdf, pagesize=letter, 
                            topMargin=0.5*inch, bottomMargin=0.5*inch,
                            leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=1,
        spaceAfter=20
    )
    nivel_style = ParagraphStyle(
        'Nivel',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.blue,
        spaceBefore=15,
        spaceAfter=10
    )
    
    elementos = []
    
    titulo = Paragraph("TOP X - MEJORES TIEMPOS", titulo_style)
    elementos.append(titulo)
    elementos.append(Spacer(1, 0.2*inch))
    
    if top_x > 0:
        info = Paragraph(f"Mostrando las mejores {top_x} partidas por nivel", styles['Normal'])
    else:
        info = Paragraph("Mostrando todas las partidas registradas", styles['Normal'])
    elementos.append(info)
    elementos.append(Spacer(1, 0.3*inch))
    
    nombres_nivel = {
        "facil": "NIVEL FACIL",
        "intermedio": "NIVEL INTERMEDIO",
        "dificil": "NIVEL DIFICIL"
    }
    
    for nivel, partidas in partidas_por_nivel.items():
        if partidas:
            elementos.append(Paragraph(nombres_nivel[nivel], nivel_style))
            
            tabla_datos = [["#", "JUGADOR", "TIEMPO", "FECHA"]]
            for i, partida_str in enumerate(partidas, 1):
                partes = partida_str.split(" - ")
                if len(partes) == 3:
                    jugador = partes[0]
                    tiempo = partes[1]
                    fecha = partes[2]
                else:
                    jugador = partida_str
                    tiempo = ""
                    fecha = ""
                tabla_datos.append([str(i), jugador, tiempo, fecha])
            
            tabla = Table(tabla_datos, colWidths=[0.5*inch, 2.5*inch, 1.2*inch, 2.0*inch])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elementos.append(tabla)
            elementos.append(Spacer(1, 0.2*inch))
        else:
            elementos.append(Paragraph(f"{nombres_nivel[nivel]}: No hay partidas registradas", styles['Normal']))
            elementos.append(Spacer(1, 0.1*inch))
    
    doc.build(elementos)
    webbrowser.open(nombre_pdf)
    
    return True

#E:ninguna
#S:None
#Funcion:Muestra la ventana "Acerca de" con informacion del programa
def mostrar_acerca_de():
    ventana_acerca = tk.Toplevel()
    ventana_acerca.title("Acerca de")
    ventana_acerca.geometry("300x200")
    ventana_acerca.resizable(False, False)
    ventana_acerca.grab_set()
    
    ventana_acerca.update_idletasks()
    x = (ventana_acerca.winfo_screenwidth() // 2) - (300 // 2)
    y = (ventana_acerca.winfo_screenheight() // 2) - (200 // 2)
    ventana_acerca.geometry(f"+{x}+{y}")
    
    frame_principal = tk.Frame(ventana_acerca, padx=20, pady=20)
    frame_principal.pack(fill=tk.BOTH, expand=True)
    
    titulo = tk.Label(frame_principal, text="Juego Sudoku", font=("Arial", 16, "bold"))
    titulo.pack(pady=(0, 10))
    
    version = tk.Label(frame_principal, text="Version: 4.0", font=("Arial", 10))
    version.pack()
    
    fecha = tk.Label(frame_principal, text="Fecha de creacion: 17 de mayo", font=("Arial", 10))
    fecha.pack()
    
    autor = tk.Label(frame_principal, text="Autor: Jorge William Chaves Osorio", font=("Arial", 10))
    autor.pack()
    
    boton_cerrar = tk.Button(frame_principal, text="Cerrar", command=ventana_acerca.destroy, width=15)
    boton_cerrar.pack(pady=15)

#====================VENTANA DE LOGIN====================

#E:tk.Tk ventana_principal - Ventana principal del programa
#S:None
#Funcion:Muestra la ventana de inicio de sesión y al autenticar, crea la ventana principal
def mostrar_login(ventana_principal):
    ventana_principal.withdraw()
    
    ventana_login = tk.Toplevel(ventana_principal)
    ventana_login.title("Sudoku - Inicio de Sesión")
    ventana_login.geometry("450x400")
    ventana_login.resizable(False, False)
    
    ventana_login.update_idletasks()
    x = (ventana_login.winfo_screenwidth() // 2) - (450 // 2)
    y = (ventana_login.winfo_screenheight() // 2) - (400 // 2)
    ventana_login.geometry(f"+{x}+{y}")
    
    frame_principal = tk.Frame(ventana_login, padx=30, pady=30)
    frame_principal.pack(fill=tk.BOTH, expand=True)
    
    titulo = tk.Label(frame_principal, text="SUDOKU 2026", font=("Arial", 20, "bold"))
    titulo.pack(pady=(0, 10))
    
    subtitulo = tk.Label(frame_principal, text="Inicio de Sesion", font=("Arial", 14))
    subtitulo.pack(pady=(0, 20))
    
    frame_entrada = tk.Frame(frame_principal)
    frame_entrada.pack(fill=tk.X, pady=10)
    
    label_correo = tk.Label(frame_entrada, text="Correo electronico:", font=("Arial", 10))
    label_correo.pack(anchor=tk.W, pady=(0, 5))
    
    entrada_correo = tk.Entry(frame_entrada, font=("Arial", 12), width=40)
    entrada_correo.pack(fill=tk.X, pady=(0, 10))
    
    label_codigo = tk.Label(frame_entrada, text="Codigo de ingreso (6 digitos):", font=("Arial", 10))
    label_codigo.pack(anchor=tk.W, pady=(0, 5))
    
    entrada_codigo = tk.Entry(frame_entrada, font=("Arial", 12), width=40, show="*")
    entrada_codigo.pack(fill=tk.X, pady=(0, 15))
    
    label_estado = tk.Label(frame_entrada, text="", font=("Arial", 9), fg="red")
    label_estado.pack(pady=(0, 10))
    
    def manejar_ingreso():
        correo = entrada_correo.get().strip()
        codigo = entrada_codigo.get().strip()
        
        if not correo:
            label_estado.config(text="Debe ingresar un correo electronico", fg="red")
            entrada_correo.focus()
            return
        
        if not validar_correo(correo):
            label_estado.config(text="El formato del correo no es valido", fg="red")
            entrada_correo.delete(0, tk.END)
            entrada_correo.focus()
            return
        
        usuario = obtener_usuario_por_correo(correo)
        
        if not usuario:
            respuesta = messagebox.askyesno(
                "Usuario no registrado",
                f"El correo '{correo}' no esta registrado.\n\n¿Desea crear un nuevo usuario?"
            )
            if respuesta:
                codigo_nuevo = generar_codigo_ingreso()
                usuario_nuevo, mensaje = crear_usuario_sin_nombre(correo, codigo_nuevo)
                
                if usuario_nuevo:
                    messagebox.showinfo(
                        "Usuario creado",
                        f"Usuario creado exitosamente para: {correo}\n\n"
                        f"Su codigo de ingreso es: {codigo_nuevo}\n\n"
                        f"Guarde este codigo para ingresar al sistema."
                    )
                    label_estado.config(text="Usuario creado. Ingrese su codigo de 6 digitos", fg="green")
                    entrada_codigo.delete(0, tk.END)
                    entrada_codigo.focus()
                else:
                    label_estado.config(text=mensaje, fg="red")
                    entrada_correo.delete(0, tk.END)
                    entrada_correo.focus()
            else:
                entrada_correo.delete(0, tk.END)
                entrada_correo.focus()
                label_estado.config(text="", fg="red")
            return
        
        if not codigo:
            label_estado.config(text="Ingrese el codigo de ingreso", fg="red")
            entrada_codigo.focus()
            return
        
        if len(codigo) != 6 or not codigo.isdigit():
            label_estado.config(text="El codigo debe tener 6 digitos", fg="red")
            entrada_codigo.delete(0, tk.END)
            entrada_codigo.focus()
            return
        
        usuario_verificar = obtener_usuario_por_correo(correo)
        if not usuario_verificar:
            label_estado.config(text="Correo no registrado", fg="red")
            entrada_correo.delete(0, tk.END)
            entrada_correo.focus()
            return
        
        codigo_hash = hashear_codigo(codigo)
        if usuario_verificar["codigo_ingreso"] == codigo_hash:
            ventana_login.destroy()
            ventana_principal.deiconify()
            crear_ventana_principal(ventana_principal, usuario_verificar)
        else:
            label_estado.config(text="Codigo incorrecto. Intente nuevamente", fg="red")
            entrada_codigo.delete(0, tk.END)
            entrada_codigo.focus()
    
    def limpiar_estado(event=None):
        label_estado.config(text="")
        entrada_codigo.delete(0, tk.END)
    
    def cerrar_login():
        ventana_login.destroy()
        ventana_principal.destroy()
    
    frame_botones = tk.Frame(frame_entrada)
    frame_botones.pack(fill=tk.X, pady=10)
    
    boton_ingresar = tk.Button(frame_botones, text="INGRESAR", command=manejar_ingreso, width=20, height=2, bg="lightgreen")
    boton_ingresar.pack(pady=5)
    
    entrada_correo.bind("<Return>", lambda e: manejar_ingreso())
    entrada_codigo.bind("<Return>", lambda e: manejar_ingreso())
    entrada_correo.bind("<FocusIn>", limpiar_estado)
    
    ventana_login.protocol("WM_DELETE_WINDOW", cerrar_login)
    
    entrada_correo.focus()

#====================VENTANA DE JUEGO====================

#E:tk.Tk ventana_principal - Ventana principal del menu
#E:dict usuario - Diccionario con datos del usuario autenticado
#E:str nivel_inicial - Nivel inicial (por defecto "facil")
#S:None
#Funcion:Crea y muestra la ventana de juego con el usuario autenticado y nivel especificado
def crear_ventana_juego(ventana_principal, usuario, nivel_inicial="facil"):
    try:
        directorio_script = obtener_directorio_script()
        archivo_config = os.path.join(directorio_script, "sudoku2026configuracion.json")
        archivo_partidas_guardadas = os.path.join(directorio_script, "sudoku2026juegoactual.json")
        
        #Leer configuracion
        with open(archivo_config, "r") as archivo:
            configuracion_actual = json.load(archivo)
        
        nivel_actual = nivel_inicial
        tipo_elementos = configuracion_actual.get("elementos", "numeros")
        elementos_personalizados = configuracion_actual.get("elementos_personalizados", [])
        tipo_reloj_actual = configuracion_actual.get("reloj", "cronometro")
        es_multinivel = configuracion_actual.get("nivel", "facil") == "multinivel"
        
        tiempos_multinivel = configuracion_actual.get("tiempos_multinivel", {})
        
        tiempo_inicial = {"horas": 0, "minutos": 0, "segundos": 0}
        
        if es_multinivel:
            nivel_tiempo = tiempos_multinivel.get(nivel_actual, {})
            tiempo_inicial = {
                "horas": nivel_tiempo.get("horas", 0),
                "minutos": nivel_tiempo.get("minutos", 0),
                "segundos": nivel_tiempo.get("segundos", 0)
            }
        else:
            tiempo_inicial = configuracion_actual.get("tiempo_inicial", {"horas": 0, "minutos": 0, "segundos": 0})
        
        #Verificar si el usuario tiene nombre ANTES de generar el tablero y crear la ventana
        nombre_jugador = usuario.get("nombre", "")
        
        #Si el usuario no tiene nombre, mostrar ventana para ingresarlo y SALIR
        if not nombre_jugador or nombre_jugador == "":
            ventana_nombre = tk.Tk()
            ventana_nombre.title("Nombre de usuario")
            ventana_nombre.geometry("400x200")
            ventana_nombre.resizable(False, False)
            
            ventana_nombre.update_idletasks()
            x = (ventana_nombre.winfo_screenwidth() // 2) - (400 // 2)
            y = (ventana_nombre.winfo_screenheight() // 2) - (200 // 2)
            ventana_nombre.geometry(f"+{x}+{y}")
            
            ventana_nombre.lift()
            ventana_nombre.focus_force()
            
            frame_nombre = tk.Frame(ventana_nombre, padx=30, pady=30)
            frame_nombre.pack(fill=tk.BOTH, expand=True)
            
            label_info = tk.Label(frame_nombre, text="Ingresa tu nombre de usuario:", font=("Arial", 12))
            label_info.pack(pady=(0, 10))
            
            entrada_nombre = tk.Entry(frame_nombre, font=("Arial", 12), width=30)
            entrada_nombre.pack(pady=10)
            
            label_estado_nombre = tk.Label(frame_nombre, text="", font=("Arial", 9), fg="red")
            label_estado_nombre.pack(pady=5)
            
            def guardar_nombre():
                nombre = entrada_nombre.get().strip()
                if not validar_nombre(nombre):
                    label_estado_nombre.config(text="El nombre debe tener 1-30 caracteres (letras, numeros y espacios)")
                    return
                
                if usuario_existe_por_nombre(cargar_usuarios(), nombre):
                    label_estado_nombre.config(text="El nombre ya esta registrado")
                    return
                
                if actualizar_nombre_usuario(usuario["correo"], nombre):
                    usuario["nombre"] = nombre
                    ventana_nombre.destroy()
                    crear_ventana_juego(ventana_principal, usuario, nivel_actual)
                else:
                    label_estado_nombre.config(text="Error al guardar el nombre")
            
            boton_guardar_nombre = tk.Button(frame_nombre, text="GUARDAR", command=guardar_nombre, width=20, height=2)
            boton_guardar_nombre.pack(pady=10)
            
            entrada_nombre.bind("<Return>", lambda e: guardar_nombre())
            entrada_nombre.focus()
            
            ventana_nombre.mainloop()
            return
        
        #============================================
        #A PARTIR DE AQUI EL USUARIO TIENE NOMBRE
        #============================================
        
        #Generar la partida SOLO si el usuario tiene nombre
        tablero_juego, tablero_solucion = generar_partida_unica(nivel_actual)
        
        partida_cargada = {}
        for fila in range(9):
            for columna in range(9):
                if tablero_juego[fila][columna] != 0:
                    partida_cargada[f"{fila},{columna}"] = tablero_juego[fila][columna]
        
        elemento_seleccionado = None
        boton_seleccionado = None
        juego_iniciado = False
        tiempo_inicial_segundos = tiempo_inicial["horas"] * 3600 + tiempo_inicial["minutos"] * 60 + tiempo_inicial["segundos"]
        tiempo_restante = tiempo_inicial_segundos
        tiempo_transcurrido = 0
        temporizador_activo = None
        fecha_hora_inicio = None
        tipo_reloj = tipo_reloj_actual
        timer_se_convirtio_a_cronometro = False
        tiempo_acumulado_al_convertir = 0
        
        pila_jugadas_realizadas = []
        pila_jugadas_eliminadas = []
        
        matriz_valores_iniciales = [["" for _ in range(9)] for _ in range(9)]
        matriz_fijos = [[False for _ in range(9)] for _ in range(9)]
        matriz_valores_actuales = [["" for _ in range(9)] for _ in range(9)]
        
        lista_botones_numericos = []
        lista_botones_accion = []
        lista_celdas_tablero = []
        
        niveles_orden = ["facil", "intermedio", "dificil"]
        nivel_actual_idx = niveles_orden.index(nivel_actual)
        
        def elemento_a_numero(elemento):
            if elemento == "":
                return 0
            if tipo_elementos == "numeros":
                return int(elemento)
            elif tipo_elementos == "letras":
                return ord(elemento) - ord('A') + 1
            else:
                try:
                    return elementos_personalizados.index(elemento) + 1
                except ValueError:
                    return 0
        
        def numero_a_elemento(numero):
            if tipo_elementos == "numeros":
                return str(numero)
            elif tipo_elementos == "letras":
                return chr(ord('A') + numero - 1)
            else:
                if 1 <= numero <= len(elementos_personalizados):
                    return elementos_personalizados[numero - 1]
                return ""
        
        for posicion, valor in partida_cargada.items():
            partes = posicion.split(",")
            fila = int(partes[0])
            columna = int(partes[1])
            elemento_mostrar = numero_a_elemento(valor)
            matriz_valores_iniciales[fila][columna] = elemento_mostrar
            matriz_valores_actuales[fila][columna] = elemento_mostrar
            matriz_fijos[fila][columna] = True
        
        #Crear la ventana de juego
        ventana_juego = tk.Toplevel(ventana_principal)
        ventana_juego.title("Sudoku - Juego")
        ventana_juego.geometry("950x800")
        ventana_juego.resizable(False, False)
        
        def pausar_temporizador():
            nonlocal temporizador_activo
            if temporizador_activo:
                ventana_juego.after_cancel(temporizador_activo)
                temporizador_activo = None
        
        def reanudar_temporizador():
            nonlocal temporizador_activo
            if juego_iniciado and temporizador_activo is None and tipo_reloj != "no_reloj":
                temporizador_activo = ventana_juego.after(1000, actualizar_temporizador)
        
        def actualizar_temporizador_display():
            if tipo_reloj == "no_reloj":
                return
            if tipo_reloj == "cronometro":
                horas = tiempo_transcurrido // 3600
                minutos = (tiempo_transcurrido % 3600) // 60
                segundos = tiempo_transcurrido % 60
                etiqueta_horas.config(text=f"Horas: {horas:02d}")
                etiqueta_minutos.config(text=f"Minutos: {minutos:02d}")
                etiqueta_segundos.config(text=f"Segundos: {segundos:02d}")
            else:
                horas = tiempo_restante // 3600
                minutos = (tiempo_restante % 3600) // 60
                segundos = tiempo_restante % 60
                etiqueta_horas.config(text=f"Horas: {horas:02d}")
                etiqueta_minutos.config(text=f"Minutos: {minutos:02d}")
                etiqueta_segundos.config(text=f"Segundos: {segundos:02d}")
        
        def actualizar_temporizador():
            nonlocal tiempo_transcurrido, tiempo_restante, temporizador_activo, juego_iniciado, tipo_reloj, timer_se_convirtio_a_cronometro, tiempo_acumulado_al_convertir
            
            if not juego_iniciado:
                return
            
            if tipo_reloj == "cronometro":
                tiempo_transcurrido += 1
                actualizar_temporizador_display()
                temporizador_activo = ventana_juego.after(1000, actualizar_temporizador)
            elif tipo_reloj == "timer":
                if tiempo_restante > 0:
                    tiempo_restante -= 1
                    actualizar_temporizador_display()
                    temporizador_activo = ventana_juego.after(1000, actualizar_temporizador)
                else:
                    pausar_temporizador()
                    juego_iniciado = False
                    respuesta = mostrar_error_general_simple("TIEMPO EXPIRADO. ¿DESEA CONTINUAR EL MISMO JUEGO?", "TIEMPO EXPIRADO", yesno=True)
                    if respuesta:
                        tiempo_acumulado_al_convertir = tiempo_inicial_segundos
                        timer_se_convirtio_a_cronometro = True
                        tipo_reloj = "cronometro"
                        tiempo_transcurrido = tiempo_inicial_segundos
                        actualizar_temporizador_display()
                        juego_iniciado = True
                        reanudar_temporizador()
                    else:
                        ventana_juego.destroy()
                        crear_ventana_juego(ventana_principal, usuario, nivel_actual)
        
        def verificar_finalizacion():
            for fila in range(9):
                for columna in range(9):
                    if matriz_valores_actuales[fila][columna] == "":
                        return False
            return True
        
        def finalizar_juego():
            nonlocal juego_iniciado, nivel_actual, nivel_actual_idx
            
            pausar_temporizador()
            juego_iniciado = False
            
            if tipo_reloj_actual == "cronometro":
                duracion = tiempo_transcurrido
            else:
                if timer_se_convirtio_a_cronometro:
                    duracion = tiempo_transcurrido
                else:
                    duracion = tiempo_inicial_segundos - tiempo_restante
            
            fecha_hora_actual = datetime.now().strftime("%Y%m%dT%H%M%S")
            guardar_partida_en_bitacora(nombre_jugador, nivel_actual, duracion, fecha_hora_actual)
            
            if es_multinivel:
                siguiente_idx = (nivel_actual_idx + 1) % len(niveles_orden)
                siguiente_nivel = niveles_orden[siguiente_idx]
                
                ventana_juego.withdraw()
                messagebox.showinfo("¡NIVEL COMPLETADO!", 
                                  f"¡Excelente! Has completado el nivel {nivel_actual.upper()}.\n\n"
                                  f"Avanzando al nivel: {siguiente_nivel.upper()}")
                ventana_juego.deiconify()
                
                ventana_juego.destroy()
                crear_ventana_juego(ventana_principal, usuario, siguiente_nivel)
            else:
                ventana_juego.withdraw()
                messagebox.showinfo("¡EXCELENTE!", "¡JUEGO COMPLETADO!")
                ventana_juego.deiconify()
                
                ventana_juego.destroy()
                ventana_principal.deiconify()
        
        def guardar_juego():
            nonlocal juego_iniciado, nombre_jugador, nivel_actual, tipo_elementos, tipo_reloj_actual
            nonlocal tiempo_inicial_segundos, tiempo_transcurrido, tiempo_restante, tipo_reloj
            nonlocal timer_se_convirtio_a_cronometro, tiempo_acumulado_al_convertir
            nonlocal matriz_valores_actuales, matriz_fijos
            nonlocal pila_jugadas_realizadas, pila_jugadas_eliminadas            
            if not juego_iniciado:
                mostrar_error_general_simple("NO SE HA INICIADO EL JUEGO")
                return
            
            pausar_temporizador()
            
            clave = f"{nombre_jugador}_{nivel_actual}"
            
            datos_guardados = {}
            if os.path.exists(archivo_partidas_guardadas):
                with open(archivo_partidas_guardadas, "r") as archivo:
                    datos_guardados = json.load(archivo)
            
            datos_guardados[clave] = {
                "nombre_jugador": nombre_jugador,
                "nivel": nivel_actual,
                "tipo_elementos": tipo_elementos,
                "tipo_reloj": tipo_reloj_actual,
                "tiempo_inicial_segundos": tiempo_inicial_segundos,
                "tiempo_transcurrido": tiempo_transcurrido,
                "tiempo_restante": tiempo_restante,
                "tipo_reloj_actual": tipo_reloj,
                "timer_se_convirtio_a_cronometro": timer_se_convirtio_a_cronometro,
                "tiempo_acumulado_al_convertir": tiempo_acumulado_al_convertir,
                "matriz_valores_actuales": matriz_valores_actuales,
                "matriz_fijos": matriz_fijos,
                "pila_jugadas_realizadas": pila_jugadas_realizadas,
                "pila_jugadas_eliminadas": pila_jugadas_eliminadas
            }
            
            with open(archivo_partidas_guardadas, "w") as archivo:
                json.dump(datos_guardados, archivo, indent=4)
            
            mostrar_error_general_simple(f"Juego guardado correctamente para {nombre_jugador} (nivel {nivel_actual})", "Juego Guardado", yesno=False)
            
            reanudar_temporizador()
        
        def cargar_juego():
            nonlocal partida_cargada, nombre_jugador, nivel_actual, tipo_elementos
            nonlocal tipo_reloj_actual, tiempo_inicial_segundos, tiempo_transcurrido, tiempo_restante
            nonlocal tipo_reloj, timer_se_convirtio_a_cronometro, tiempo_acumulado_al_convertir
            nonlocal matriz_valores_actuales, matriz_fijos, pila_jugadas_realizadas, pila_jugadas_eliminadas
            nonlocal matriz_valores_iniciales, elemento_seleccionado, boton_seleccionado, juego_iniciado
            
            if juego_iniciado:
                mostrar_error_general_simple("No se puede cargar un juego mientras hay una partida en curso. Termine o borre el juego actual primero.")
                return
            
            nombre_temporal = nombre_jugador
            
            if os.path.exists(archivo_partidas_guardadas):
                with open(archivo_partidas_guardadas, "r") as archivo:
                    datos_guardados = json.load(archivo)
                
                clave = f"{nombre_temporal}_{nivel_actual}"
                if clave in datos_guardados:
                    juego = datos_guardados[clave]
                    
                    nombre_jugador = juego.get("nombre_jugador", nombre_temporal)
                    nivel_actual = juego.get("nivel", nivel_actual)
                    tipo_elementos = juego.get("tipo_elementos", tipo_elementos)
                    tipo_reloj_actual = juego.get("tipo_reloj", tipo_reloj_actual)
                    tiempo_inicial_segundos = juego.get("tiempo_inicial_segundos", tiempo_inicial_segundos)
                    tiempo_transcurrido = juego.get("tiempo_transcurrido", 0)
                    tiempo_restante = juego.get("tiempo_restante", tiempo_inicial_segundos)
                    tipo_reloj = juego.get("tipo_reloj_actual", tipo_reloj_actual)
                    timer_se_convirtio_a_cronometro = juego.get("timer_se_convirtio_a_cronometro", False)
                    tiempo_acumulado_al_convertir = juego.get("tiempo_acumulado_al_convertir", 0)
                    matriz_valores_actuales_cargada = juego.get("matriz_valores_actuales", None)
                    matriz_fijos_cargada = juego.get("matriz_fijos", None)
                    pila_jugadas_realizadas = juego.get("pila_jugadas_realizadas", [])
                    pila_jugadas_eliminadas = juego.get("pila_jugadas_eliminadas", [])
                    
                    if matriz_valores_actuales_cargada and matriz_fijos_cargada:
                        matriz_valores_actuales = matriz_valores_actuales_cargada
                        matriz_fijos = matriz_fijos_cargada
                        
                        for fila in range(9):
                            for columna in range(9):
                                matriz_valores_iniciales[fila][columna] = matriz_valores_actuales[fila][columna] if matriz_fijos[fila][columna] else ""
                        
                        for fila in range(9):
                            for columna in range(9):
                                color_fondo = "#d9d9d9" if matriz_fijos[fila][columna] else "white"
                                celda = lista_celdas_tablero[fila][columna]
                                celda.configure(state="normal", bg=color_fondo, readonlybackground=color_fondo)
                                celda.delete(0, tk.END)
                                if matriz_valores_actuales[fila][columna]:
                                    celda.insert(0, matriz_valores_actuales[fila][columna])
                                celda.configure(state="readonly")
                        
                        nivel_texto = nivel_actual.capitalize()
                        etiqueta_nivel_valor.config(text=nivel_texto)
                        
                        if tipo_elementos == "numeros":
                            elementos_texto = "Numeros (1-9)"
                        elif tipo_elementos == "letras":
                            elementos_texto = "Letras (A-I)"
                        else:
                            elementos_texto = "Personalizados"
                        etiqueta_elementos_valor.config(text=elementos_texto)
                        
                        actualizar_temporizador_display()
                        
                        for widget in frame_panel_numeros.winfo_children():
                            widget.destroy()
                        lista_botones_numericos.clear()
                        
                        if tipo_elementos == "numeros":
                            for i in range(1, 10):
                                texto_boton = str(i)
                                boton_numero = tk.Button(frame_panel_numeros, text=texto_boton, width=3, height=1, font=("Arial", 12))
                                boton_numero.grid(row=(i-1)//3, column=(i-1)%3, padx=2, pady=2)
                                boton_numero.configure(command=lambda e=texto_boton, b=boton_numero: seleccionar_elemento(e, b))
                                lista_botones_numericos.append(boton_numero)
                        elif tipo_elementos == "letras":
                            for i in range(1, 10):
                                texto_boton = chr(ord('A') + i - 1)
                                boton_numero = tk.Button(frame_panel_numeros, text=texto_boton, width=3, height=1, font=("Arial", 12))
                                boton_numero.grid(row=(i-1)//3, column=(i-1)%3, padx=2, pady=2)
                                boton_numero.configure(command=lambda e=texto_boton, b=boton_numero: seleccionar_elemento(e, b))
                                lista_botones_numericos.append(boton_numero)
                        else:
                            for i, elem in enumerate(elementos_personalizados, 1):
                                boton_numero = tk.Button(frame_panel_numeros, text=elem, width=3, height=1, font=("Arial", 12))
                                boton_numero.grid(row=(i-1)//3, column=(i-1)%3, padx=2, pady=2)
                                boton_numero.configure(command=lambda e=elem, b=boton_numero: seleccionar_elemento(e, b))
                                lista_botones_numericos.append(boton_numero)
                        
                        mostrar_error_general_simple(f"Juego cargado correctamente para {nombre_jugador}. Presione INICIAR JUEGO para continuar.", "Juego Cargado", yesno=False)
                        return
                
                mostrar_error_general_simple(f"NO TIENE UN JUEGO GUARDADO CON ESTA DIFICULTAD ({nivel_actual}) para el jugador {nombre_temporal}")
            else:
                mostrar_error_general_simple("No hay juegos guardados.")
        
        def mostrar_error_general_simple(mensaje, titulo="Error", yesno=False):
            pausar_temporizador()
            ventana_juego.withdraw()
            
            if yesno:
                resultado = messagebox.askyesno(titulo, mensaje)
            else:
                messagebox.showinfo(titulo, mensaje)
                resultado = None
            
            ventana_juego.deiconify()
            reanudar_temporizador()
            
            return resultado
        
        def mostrar_ventana_error(mensaje, fila_error=None, columna_error=None):
            nonlocal juego_iniciado
            
            pausar_temporizador()
            juego_estaba_iniciado = juego_iniciado
            juego_iniciado = False
            
            ventana_error = tk.Toplevel(ventana_juego)
            ventana_error.title("Error en la jugada")
            ventana_error.geometry("600x550")
            ventana_error.resizable(False, False)
            ventana_error.transient(ventana_juego)
            ventana_error.grab_set()
            
            frame_mensaje = tk.Frame(ventana_error)
            frame_mensaje.pack(pady=20)
            
            etiqueta_error = tk.Label(frame_mensaje, text=mensaje, font=("Arial", 12, "bold"), fg="red")
            etiqueta_error.pack()
            
            frame_tablero_error = tk.Frame(ventana_error)
            frame_tablero_error.pack(pady=10)
            
            for caja_fila in range(3):
                for caja_columna in range(3):
                    frame_caja = tk.LabelFrame(frame_tablero_error, bd=2, relief=tk.SOLID)
                    frame_caja.grid(row=caja_fila, column=caja_columna, padx=1, pady=1)
                    
                    for celda_fila in range(3):
                        for celda_columna in range(3):
                            fila_global = caja_fila * 3 + celda_fila
                            columna_global = caja_columna * 3 + celda_columna
                            
                            color_fondo = "#d9d9d9" if matriz_fijos[fila_global][columna_global] else "white"
                            
                            if fila_global == fila_error and columna_global == columna_error:
                                color_fondo = "red"
                            
                            valor = matriz_valores_actuales[fila_global][columna_global]
                            
                            celda = tk.Label(frame_caja, text=valor if valor else "", width=3, height=1,
                                             font=("Arial", 18), relief=tk.SOLID, bd=1,
                                             bg=color_fondo, anchor="center")
                            celda.grid(row=celda_fila, column=celda_columna, padx=1, pady=1)
            
            def cerrar_ventana_error():
                ventana_error.destroy()
                nonlocal juego_iniciado
                juego_iniciado = juego_estaba_iniciado
                reanudar_temporizador()
            
            boton_aceptar = tk.Button(ventana_error, text="ACEPTAR", command=cerrar_ventana_error, width=20, height=2)
            boton_aceptar.pack(pady=20)
            
            boton_aceptar.focus_set()
            
            ventana_juego.wait_window(ventana_error)
        
        def validar_jugada(fila, columna, elemento):
            if elemento == "":
                return True
            
            numero_elemento = elemento_a_numero(elemento)
            
            if matriz_fijos[fila][columna]:
                mostrar_ventana_error("JUGADA NO ES VALIDA PORQUE ESTE ES UN ELEMENTO FIJO", fila, columna)
                return False
            
            for c in range(9):
                if c != columna and matriz_valores_actuales[fila][c] != "":
                    if elemento_a_numero(matriz_valores_actuales[fila][c]) == numero_elemento:
                        mostrar_ventana_error("JUGADA NO ES VALIDA PORQUE EL ELEMENTO YA ESTA EN LA FILA", fila, c)
                        return False
            
            for r in range(9):
                if r != fila and matriz_valores_actuales[r][columna] != "":
                    if elemento_a_numero(matriz_valores_actuales[r][columna]) == numero_elemento:
                        mostrar_ventana_error("JUGADA NO ES VALIDA PORQUE EL ELEMENTO YA ESTA EN LA COLUMNA", r, columna)
                        return False
            
            caja_fila = fila // 3
            caja_columna = columna // 3
            for r in range(caja_fila * 3, caja_fila * 3 + 3):
                for c in range(caja_columna * 3, caja_columna * 3 + 3):
                    if (r != fila or c != columna) and matriz_valores_actuales[r][c] != "":
                        if elemento_a_numero(matriz_valores_actuales[r][c]) == numero_elemento:
                            mostrar_ventana_error("JUGADA NO ES VALIDA PORQUE EL ELEMENTO YA ESTA EN LA CUADRÍCULA", r, c)
                            return False
            
            return True
        
        def deshacer_jugada():
            nonlocal juego_iniciado
            if not juego_iniciado:
                mostrar_error_general_simple("NO SE HA INICIADO EL JUEGO")
                return
            
            if len(pila_jugadas_realizadas) == 0:
                mostrar_error_general_simple("NO HAY JUGADAS PARA DESHACER")
                return
            
            fila, columna, valor_anterior, valor_nuevo = pila_jugadas_realizadas.pop()
            pila_jugadas_eliminadas.append((fila, columna, valor_anterior, valor_nuevo))
            
            matriz_valores_actuales[fila][columna] = valor_anterior
            celda = lista_celdas_tablero[fila][columna]
            celda.configure(state="normal")
            celda.delete(0, tk.END)
            if valor_anterior:
                celda.insert(0, valor_anterior)
            celda.configure(state="readonly")
        
        def rehacer_jugada():
            nonlocal juego_iniciado
            if not juego_iniciado:
                mostrar_error_general_simple("NO SE HA INICIADO EL JUEGO")
                return
            
            if len(pila_jugadas_eliminadas) == 0:
                mostrar_error_general_simple("NO HAY JUGADAS PARA REHACER")
                return
            
            fila, columna, valor_que_habia, valor_que_se_quito = pila_jugadas_eliminadas.pop()
            
            if not validar_jugada(fila, columna, valor_que_se_quito):
                return
            
            valor_actual = matriz_valores_actuales[fila][columna]
            pila_jugadas_realizadas.append((fila, columna, valor_actual, valor_que_se_quito))
            
            matriz_valores_actuales[fila][columna] = valor_que_se_quito
            celda = lista_celdas_tablero[fila][columna]
            celda.configure(state="normal")
            celda.delete(0, tk.END)
            if valor_que_se_quito:
                celda.insert(0, valor_que_se_quito)
            celda.configure(state="readonly")
            
            if verificar_finalizacion():
                finalizar_juego()
        
        def colocar_elemento(fila, columna):
            nonlocal elemento_seleccionado, boton_seleccionado, juego_iniciado
            
            if not juego_iniciado:
                mostrar_error_general_simple("El juego no ha iniciado. Presione INICIAR JUEGO primero.")
                return
            if elemento_seleccionado is None:
                mostrar_error_general_simple("FALTA SELECCIONAR UN ELEMENTO")
                return
            
            pausar_temporizador()
            
            if validar_jugada(fila, columna, elemento_seleccionado):
                pila_jugadas_eliminadas.clear()
                
                valor_anterior = matriz_valores_actuales[fila][columna]
                pila_jugadas_realizadas.append((fila, columna, valor_anterior, elemento_seleccionado))
                
                matriz_valores_actuales[fila][columna] = elemento_seleccionado
                celda = lista_celdas_tablero[fila][columna]
                celda.configure(state="normal")
                celda.delete(0, tk.END)
                celda.insert(0, elemento_seleccionado)
                celda.configure(state="readonly")
                
                reanudar_temporizador()
                
                if verificar_finalizacion():
                    finalizar_juego()
            else:
                reanudar_temporizador()
        
        def borrar_juego():
            nonlocal juego_iniciado, pila_jugadas_realizadas, pila_jugadas_eliminadas, tiempo_transcurrido, tiempo_restante, tipo_reloj, timer_se_convirtio_a_cronometro, tiempo_acumulado_al_convertir
            
            if not juego_iniciado:
                mostrar_error_general_simple("NO SE HA INICIADO EL JUEGO")
                return
            
            respuesta = mostrar_error_general_simple("¿ESTA SEGURO DE BORRAR EL JUEGO?", "BORRAR JUEGO", yesno=True)
            if not respuesta:
                return
            
            pila_jugadas_realizadas.clear()
            pila_jugadas_eliminadas.clear()
            
            for fila in range(9):
                for columna in range(9):
                    if matriz_fijos[fila][columna]:
                        matriz_valores_actuales[fila][columna] = matriz_valores_iniciales[fila][columna]
                        celda = lista_celdas_tablero[fila][columna]
                        celda.configure(state="normal")
                        celda.delete(0, tk.END)
                        celda.insert(0, matriz_valores_iniciales[fila][columna])
                        celda.configure(state="readonly")
                    else:
                        matriz_valores_actuales[fila][columna] = ""
                        celda = lista_celdas_tablero[fila][columna]
                        celda.configure(state="normal")
                        celda.delete(0, tk.END)
                        celda.configure(state="readonly")
            
            if tipo_reloj_actual == "cronometro":
                tiempo_transcurrido = 0
            elif tipo_reloj_actual == "timer":
                tiempo_restante = tiempo_inicial_segundos
                tipo_reloj = "timer"
                timer_se_convirtio_a_cronometro = False
                tiempo_acumulado_al_convertir = 0
            actualizar_temporizador_display()
        
        def terminar_juego():
            nonlocal juego_iniciado
            
            if not juego_iniciado:
                mostrar_error_general_simple("NO SE HA INICIADO EL JUEGO")
                return
            
            respuesta = mostrar_error_general_simple("¿ESTA SEGURO DE TERMINAR EL JUEGO?", "TERMINAR JUEGO", yesno=True)
            if not respuesta:
                return
            
            ventana_juego.destroy()
            ventana_principal.deiconify()
        
        def top_x():
            pausar_temporizador()
            ventana_juego.withdraw()
            
            exito = generar_top_x()
            
            if not exito:
                messagebox.showinfo("TOP X", "No se pudo generar el TOP X o no hay datos.")
            
            ventana_juego.deiconify()
            reanudar_temporizador()
        
        def seleccionar_elemento(elemento, boton):
            nonlocal elemento_seleccionado, boton_seleccionado
            if boton_seleccionado:
                boton_seleccionado.configure(bg="SystemButtonFace")
            elemento_seleccionado = elemento
            boton_seleccionado = boton
            boton_seleccionado.configure(bg="lightgreen")
        
        def iniciar_juego():
            nonlocal juego_iniciado, fecha_hora_inicio, nombre_jugador, tiempo_restante, tipo_reloj, tiempo_inicial_segundos, pila_jugadas_realizadas, pila_jugadas_eliminadas, tiempo_transcurrido, timer_se_convirtio_a_cronometro, tiempo_acumulado_al_convertir
            
            if nombre_existe_en_bitacora(nombre_jugador):
                respuesta = mostrar_error_general_simple(f"El nombre '{nombre_jugador}' ya existe en el TOP. ¿Desea usarlo?", "Nombre existente", yesno=True)
                if not respuesta:
                    return
            
            if tipo_reloj_actual == "timer" and not es_multinivel:
                try:
                    horas_timer = int(entrada_timer_horas.get())
                    minutos_timer = int(entrada_timer_minutos.get())
                    segundos_timer = int(entrada_timer_segundos.get())
                    if horas_timer < 0 or horas_timer > 4 or minutos_timer < 0 or minutos_timer > 59 or segundos_timer < 0 or segundos_timer > 59:
                        mostrar_error_general_simple("Valores de timer invalidos")
                        return
                    if horas_timer == 0 and minutos_timer == 0 and segundos_timer == 0:
                        mostrar_error_general_simple("El timer debe tener al menos un valor mayor a cero")
                        return
                    tiempo_inicial_segundos = horas_timer * 3600 + minutos_timer * 60 + segundos_timer
                    tiempo_restante = tiempo_inicial_segundos
                    actualizar_temporizador_display()
                except ValueError:
                    mostrar_error_general_simple("Los valores del timer deben ser numeros enteros")
                    return
            
            timer_se_convirtio_a_cronometro = False
            tiempo_acumulado_al_convertir = 0
            
            pila_jugadas_realizadas.clear()
            pila_jugadas_eliminadas.clear()
            
            juego_iniciado = True
            fecha_hora_inicio = datetime.now()
            boton_iniciar_juego.config(state=tk.DISABLED)
            if tipo_reloj_actual == "timer" and not es_multinivel:
                entrada_timer_horas.config(state=tk.DISABLED)
                entrada_timer_minutos.config(state=tk.DISABLED)
                entrada_timer_segundos.config(state=tk.DISABLED)
            actualizar_temporizador_display()
            reanudar_temporizador()
        
        def on_cerrar_juego():
            pausar_temporizador()
            ventana_juego.destroy()
            ventana_principal.deiconify()
        
        ventana_juego.protocol("WM_DELETE_WINDOW", on_cerrar_juego)
        
        #interfaz grafica
        etiqueta_titulo = tk.Label(ventana_juego, text="S U D O K U", font=("Arial", 24, "bold"))
        etiqueta_titulo.pack(pady=10)
        
        frame_nivel_visible = tk.Frame(ventana_juego)
        frame_nivel_visible.pack(fill=tk.X, padx=20, pady=5)
        
        nivel_texto = nivel_actual.capitalize()
        etiqueta_nivel_titulo = tk.Label(frame_nivel_visible, text="Dificultad:", font=("Arial", 12, "bold"))
        etiqueta_nivel_titulo.pack(side=tk.LEFT, padx=5)
        
        etiqueta_nivel_valor = tk.Label(frame_nivel_visible, text=nivel_texto, font=("Arial", 12), fg="blue")
        etiqueta_nivel_valor.pack(side=tk.LEFT, padx=5)
        
        if es_multinivel:
            etiqueta_modo_titulo = tk.Label(frame_nivel_visible, text="Modo:", font=("Arial", 12, "bold"))
            etiqueta_modo_titulo.pack(side=tk.LEFT, padx=(20,5))
            
            etiqueta_modo_valor = tk.Label(frame_nivel_visible, text="MULTINIVEL", font=("Arial", 12), fg="red")
            etiqueta_modo_valor.pack(side=tk.LEFT, padx=5)
        
        if tipo_elementos == "numeros":
            elementos_texto = "Numeros (1-9)"
        elif tipo_elementos == "letras":
            elementos_texto = "Letras (A-I)"
        else:
            elementos_texto = "Personalizados"
        etiqueta_elementos_titulo = tk.Label(frame_nivel_visible, text="Elementos:", font=("Arial", 12, "bold"))
        etiqueta_elementos_titulo.pack(side=tk.LEFT, padx=(20,5))
        
        etiqueta_elementos_valor = tk.Label(frame_nivel_visible, text=elementos_texto, font=("Arial", 12), fg="green")
        etiqueta_elementos_valor.pack(side=tk.LEFT, padx=5)
        
        etiqueta_jugador_titulo = tk.Label(frame_nivel_visible, text="Jugador:", font=("Arial", 12, "bold"))
        etiqueta_jugador_titulo.pack(side=tk.LEFT, padx=(20,5))
        
        etiqueta_jugador_valor = tk.Label(frame_nivel_visible, text=nombre_jugador, font=("Arial", 12), fg="purple")
        etiqueta_jugador_valor.pack(side=tk.LEFT, padx=5)
        
        frame_principal = tk.Frame(ventana_juego)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        frame_columna_izquierda = tk.Frame(frame_principal)
        frame_columna_izquierda.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        frame_jugador = tk.Frame(frame_columna_izquierda)
        frame_jugador.pack(fill=tk.X, pady=(0,15))
        
        etiqueta_jugador_info = tk.Label(frame_jugador, text=f"Jugando como: {nombre_jugador}", font=("Arial", 12, "bold"), fg="purple")
        etiqueta_jugador_info.pack(side=tk.LEFT, padx=(0,10))
        
        frame_contenedor_tablero = tk.Frame(frame_columna_izquierda)
        frame_contenedor_tablero.pack(pady=10)
        
        for caja_fila in range(3):
            for caja_columna in range(3):
                frame_caja = tk.LabelFrame(frame_contenedor_tablero, bd=2, relief=tk.SOLID)
                frame_caja.grid(row=caja_fila, column=caja_columna, padx=1, pady=1)
                
                for celda_fila in range(3):
                    for celda_columna in range(3):
                        fila_global = caja_fila * 3 + celda_fila
                        columna_global = caja_columna * 3 + celda_columna
                        
                        color_fondo = "#d9d9d9" if matriz_fijos[fila_global][columna_global] else "white"
                        
                        celda_tablero = tk.Entry(frame_caja, width=3, font=("Arial", 18), justify="center",
                                                  bd=1, relief=tk.SOLID, state="readonly",
                                                  readonlybackground=color_fondo, bg=color_fondo)
                        
                        if matriz_valores_actuales[fila_global][columna_global]:
                            celda_tablero.configure(state="normal")
                            celda_tablero.insert(0, matriz_valores_actuales[fila_global][columna_global])
                            celda_tablero.configure(state="readonly")
                        
                        celda_tablero.grid(row=celda_fila, column=celda_columna, padx=1, pady=1)
                        celda_tablero.bind("<Button-1>", lambda e, f=fila_global, c=columna_global: colocar_elemento(f, c))
                        
                        if len(lista_celdas_tablero) <= fila_global:
                            lista_celdas_tablero.append([])
                        lista_celdas_tablero[fila_global].append(celda_tablero)
        
        frame_panel_numeros = tk.Frame(frame_columna_izquierda)
        frame_panel_numeros.pack(pady=10)
        
        if tipo_elementos == "numeros":
            for i in range(1, 10):
                texto_boton = str(i)
                boton_numero = tk.Button(frame_panel_numeros, text=texto_boton, width=3, height=1, font=("Arial", 12))
                boton_numero.grid(row=(i-1)//3, column=(i-1)%3, padx=2, pady=2)
                boton_numero.configure(command=lambda e=texto_boton, b=boton_numero: seleccionar_elemento(e, b))
                lista_botones_numericos.append(boton_numero)
        elif tipo_elementos == "letras":
            for i in range(1, 10):
                texto_boton = chr(ord('A') + i - 1)
                boton_numero = tk.Button(frame_panel_numeros, text=texto_boton, width=3, height=1, font=("Arial", 12))
                boton_numero.grid(row=(i-1)//3, column=(i-1)%3, padx=2, pady=2)
                boton_numero.configure(command=lambda e=texto_boton, b=boton_numero: seleccionar_elemento(e, b))
                lista_botones_numericos.append(boton_numero)
        else:
            for i, elem in enumerate(elementos_personalizados, 1):
                boton_numero = tk.Button(frame_panel_numeros, text=elem, width=3, height=1, font=("Arial", 12))
                boton_numero.grid(row=(i-1)//3, column=(i-1)%3, padx=2, pady=2)
                boton_numero.configure(command=lambda e=elem, b=boton_numero: seleccionar_elemento(e, b))
                lista_botones_numericos.append(boton_numero)
        
        frame_columna_derecha = tk.Frame(frame_principal, width=250)
        frame_columna_derecha.pack(side=tk.RIGHT, fill=tk.Y, padx=(20,0))
        frame_columna_derecha.pack_propagate(False)
        
        canvas_derecha = tk.Canvas(frame_columna_derecha, width=250, height=600)
        scrollbar_derecha = tk.Scrollbar(frame_columna_derecha, orient="vertical", command=canvas_derecha.yview)
        frame_botones_scrollable = tk.Frame(canvas_derecha)
        
        frame_botones_scrollable.bind("<Configure>", lambda e: canvas_derecha.configure(scrollregion=canvas_derecha.bbox("all")))
        canvas_derecha.create_window((0,0), window=frame_botones_scrollable, anchor="nw", width=230)
        canvas_derecha.configure(yscrollcommand=scrollbar_derecha.set)
        
        canvas_derecha.pack(side="left", fill="both", expand=True)
        scrollbar_derecha.pack(side="right", fill="y")
        
        boton_iniciar_juego = tk.Button(frame_botones_scrollable, text="INICIAR JUEGO", command=iniciar_juego, width=20, height=2)
        boton_iniciar_juego.pack(pady=10)
        lista_botones_accion.append(boton_iniciar_juego)
        
        if tipo_reloj_actual != "no_reloj":
            frame_temporizador = tk.LabelFrame(frame_botones_scrollable, text="TIEMPO", font=("Arial", 10, "bold"))
            frame_temporizador.pack(fill=tk.X, pady=10, padx=10)
            
            etiqueta_horas = tk.Label(frame_temporizador, text="Horas: 00")
            etiqueta_horas.pack(anchor=tk.W, padx=10, pady=2)
            
            etiqueta_minutos = tk.Label(frame_temporizador, text="Minutos: 00")
            etiqueta_minutos.pack(anchor=tk.W, padx=10, pady=2)
            
            etiqueta_segundos = tk.Label(frame_temporizador, text="Segundos: 00")
            etiqueta_segundos.pack(anchor=tk.W, padx=10, pady=2)
            
            if tipo_reloj_actual == "timer" and not es_multinivel:
                frame_timer_input = tk.LabelFrame(frame_botones_scrollable, text="MODIFICAR TIMER", font=("Arial", 10, "bold"))
                frame_timer_input.pack(fill=tk.X, pady=10, padx=10)
                
                frame_input_horas = tk.Frame(frame_timer_input)
                frame_input_horas.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
                label_horas = tk.Label(frame_input_horas, text="Horas")
                label_horas.pack()
                entrada_timer_horas = tk.Entry(frame_input_horas, width=5, justify="center")
                entrada_timer_horas.insert(0, str(tiempo_inicial["horas"]))
                entrada_timer_horas.pack()
                
                frame_input_minutos = tk.Frame(frame_timer_input)
                frame_input_minutos.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
                label_minutos = tk.Label(frame_input_minutos, text="Minutos")
                label_minutos.pack()
                entrada_timer_minutos = tk.Entry(frame_input_minutos, width=5, justify="center")
                entrada_timer_minutos.insert(0, str(tiempo_inicial["minutos"]))
                entrada_timer_minutos.pack()
                
                frame_input_segundos = tk.Frame(frame_timer_input)
                frame_input_segundos.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
                label_segundos = tk.Label(frame_input_segundos, text="Segundos")
                label_segundos.pack()
                entrada_timer_segundos = tk.Entry(frame_input_segundos, width=5, justify="center")
                entrada_timer_segundos.insert(0, str(tiempo_inicial["segundos"]))
                entrada_timer_segundos.pack()
            else:
                entrada_timer_horas = None
                entrada_timer_minutos = None
                entrada_timer_segundos = None
                
                if es_multinivel and tipo_reloj_actual == "timer":
                    tiempo_mostrar = tiempos_multinivel.get(nivel_actual, {})
                    horas = tiempo_mostrar.get("horas", 0)
                    minutos = tiempo_mostrar.get("minutos", 0)
                    segundos = tiempo_mostrar.get("segundos", 0)
                    etiqueta_horas.config(text=f"Horas: {horas:02d}")
                    etiqueta_minutos.config(text=f"Minutos: {minutos:02d}")
                    etiqueta_segundos.config(text=f"Segundos: {segundos:02d}")
        else:
            etiqueta_horas = None
            etiqueta_minutos = None
            etiqueta_segundos = None
            entrada_timer_horas = None
            entrada_timer_minutos = None
            entrada_timer_segundos = None
        
        boton_guardar_juego = tk.Button(frame_botones_scrollable, text="GUARDAR JUEGO", command=guardar_juego, width=20, height=2)
        boton_guardar_juego.pack(pady=10)
        lista_botones_accion.append(boton_guardar_juego)
        
        boton_cargar_juego = tk.Button(frame_botones_scrollable, text="CARGAR JUEGO", command=cargar_juego, width=20, height=2)
        boton_cargar_juego.pack(pady=10)
        lista_botones_accion.append(boton_cargar_juego)
        
        boton_deshacer_jugada = tk.Button(frame_botones_scrollable, text="DESHACER JUGADA", command=deshacer_jugada, width=20, height=2)
        boton_deshacer_jugada.pack(pady=10)
        lista_botones_accion.append(boton_deshacer_jugada)
        
        boton_rehacer_jugada = tk.Button(frame_botones_scrollable, text="REHACER JUGADA", command=rehacer_jugada, width=20, height=2)
        boton_rehacer_jugada.pack(pady=10)
        lista_botones_accion.append(boton_rehacer_jugada)
        
        boton_borrar_juego = tk.Button(frame_botones_scrollable, text="BORRAR JUEGO", command=borrar_juego, width=20, height=2)
        boton_borrar_juego.pack(pady=10)
        lista_botones_accion.append(boton_borrar_juego)
        
        boton_terminar_juego = tk.Button(frame_botones_scrollable, text="TERMINAR JUEGO", command=terminar_juego, width=20, height=2)
        boton_terminar_juego.pack(pady=10)
        lista_botones_accion.append(boton_terminar_juego)
        
        boton_top_x = tk.Button(frame_botones_scrollable, text="TOP X", command=top_x, width=20, height=2)
        boton_top_x.pack(pady=10)
        lista_botones_accion.append(boton_top_x)
        
        ventana_principal.withdraw()
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        messagebox.showerror("Error", f"Error al crear la ventana de juego:\n{str(e)}")

#====================VENTANA DE CONFIGURACION====================

#E:tk.Tk ventana_principal - Ventana principal del menu
#E:dict usuario_actual - Usuario actual autenticado (opcional)
#S:None
#Funcion:Crea y muestra la ventana de configuracion
def crear_ventana_configuracion(ventana_principal, usuario_actual=None):
    ventana_configuracion = tk.Toplevel(ventana_principal)
    ventana_configuracion.title("Sudoku - Configuracion")
    ventana_configuracion.geometry("600x900")
    ventana_configuracion.resizable(False, False)
    
    def on_cerrar_configuracion():
        ventana_configuracion.destroy()
        ventana_principal.deiconify()
    
    ventana_configuracion.protocol("WM_DELETE_WINDOW", on_cerrar_configuracion)
    
    canvas_configuracion = tk.Canvas(ventana_configuracion)
    scrollbar_vertical = tk.Scrollbar(ventana_configuracion, orient="vertical", command=canvas_configuracion.yview)
    frame_scrollable = tk.Frame(canvas_configuracion)
    
    frame_scrollable.bind("<Configure>", lambda evento: canvas_configuracion.configure(scrollregion=canvas_configuracion.bbox("all")))
    canvas_configuracion.create_window((0,0), window=frame_scrollable, anchor="nw")
    canvas_configuracion.configure(yscrollcommand=scrollbar_vertical.set)
    
    canvas_configuracion.pack(side="left", fill="both", expand=True)
    scrollbar_vertical.pack(side="right", fill="y")
    
    etiqueta_titulo = tk.Label(frame_scrollable, text="CONFIGURACION", font=("Arial", 18, "bold"))
    etiqueta_titulo.pack(pady=10)
    
    #Leer configuracion
    directorio_script = obtener_directorio_script()
    archivo_config = os.path.join(directorio_script, "sudoku2026configuracion.json")
    with open(archivo_config, "r") as archivo:
        config_actual = json.load(archivo)
    
    #Valores por defecto
    nivel_default = config_actual.get("nivel", "facil")
    reloj_default = config_actual.get("reloj", "cronometro")
    top_x_default = config_actual.get("top_x", 0)
    elementos_default = config_actual.get("elementos", "numeros")
    elementos_personalizados_guardados = config_actual.get("elementos_personalizados", [])
    tiempo_inicial_default = config_actual.get("tiempo_inicial", {"horas": 0, "minutos": 0, "segundos": 0})
    tiempos_multinivel = config_actual.get("tiempos_multinivel", {
        "facil": {"horas": 0, "minutos": 0, "segundos": 0},
        "intermedio": {"horas": 0, "minutos": 0, "segundos": 0},
        "dificil": {"horas": 0, "minutos": 0, "segundos": 0}
    })
    
    #====================NIVEL====================
    frame_nivel = tk.LabelFrame(frame_scrollable, text="NIVEL", font=("Arial", 12, "bold"))
    frame_nivel.pack(fill=tk.X, padx=20, pady=10)
    
    variable_nivel = tk.StringVar(value=nivel_default)
    
    opcion_facil = tk.Radiobutton(frame_nivel, text="Facil", variable=variable_nivel, value="facil")
    opcion_facil.pack(anchor=tk.W, padx=20, pady=5)
    
    opcion_intermedio = tk.Radiobutton(frame_nivel, text="Intermedio", variable=variable_nivel, value="intermedio")
    opcion_intermedio.pack(anchor=tk.W, padx=20, pady=5)
    
    opcion_dificil = tk.Radiobutton(frame_nivel, text="Dificil", variable=variable_nivel, value="dificil")
    opcion_dificil.pack(anchor=tk.W, padx=20, pady=5)
    
    opcion_multinivel = tk.Radiobutton(frame_nivel, text="Multinivel", variable=variable_nivel, value="multinivel")
    opcion_multinivel.pack(anchor=tk.W, padx=20, pady=5)
    
    #====================RELOJ====================
    frame_reloj = tk.LabelFrame(frame_scrollable, text="RELOJ", font=("Arial", 12, "bold"))
    frame_reloj.pack(fill=tk.X, padx=20, pady=10)
    
    variable_reloj = tk.StringVar(value=reloj_default)
    
    opcion_cronometro = tk.Radiobutton(frame_reloj, text="Cronometro", variable=variable_reloj, value="cronometro")
    opcion_cronometro.pack(anchor=tk.W, padx=20, pady=5)
    
    opcion_timer = tk.Radiobutton(frame_reloj, text="Timer", variable=variable_reloj, value="timer")
    opcion_timer.pack(anchor=tk.W, padx=20, pady=5)
    
    opcion_no_reloj = tk.Radiobutton(frame_reloj, text="No usar reloj", variable=variable_reloj, value="no_reloj")
    opcion_no_reloj.pack(anchor=tk.W, padx=20, pady=5)
    
    #Funcion para habilitar/deshabilitar campos de timer multinivel
    def actualizar_estado_timer_multinivel(*args):
        es_multinivel = variable_nivel.get() == "multinivel"
        es_timer = variable_reloj.get() == "timer"
        
        #Habilitar/deshabilitar campos de timer multinivel
        estado_multinivel = "normal" if (es_multinivel and es_timer) else "disabled"
        fondo_multinivel = "white" if (es_multinivel and es_timer) else "#f0f0f0"
        
        #Campos del nivel Facil
        entrada_facil_horas.config(state=estado_multinivel, bg=fondo_multinivel)
        entrada_facil_minutos.config(state=estado_multinivel, bg=fondo_multinivel)
        entrada_facil_segundos.config(state=estado_multinivel, bg=fondo_multinivel)
        
        #Campos del nivel Intermedio
        entrada_intermedio_horas.config(state=estado_multinivel, bg=fondo_multinivel)
        entrada_intermedio_minutos.config(state=estado_multinivel, bg=fondo_multinivel)
        entrada_intermedio_segundos.config(state=estado_multinivel, bg=fondo_multinivel)
        
        #Campos del nivel Dificil
        entrada_dificil_horas.config(state=estado_multinivel, bg=fondo_multinivel)
        entrada_dificil_minutos.config(state=estado_multinivel, bg=fondo_multinivel)
        entrada_dificil_segundos.config(state=estado_multinivel, bg=fondo_multinivel)
        
        #Habilitar/deshabilitar campos de timer normal
        estado_normal = "disabled" if es_multinivel else ("normal" if es_timer else "disabled")
        fondo_normal = "#f0f0f0" if es_multinivel else ("white" if es_timer else "#f0f0f0")
        
        entrada_horas.config(state=estado_normal, bg=fondo_normal)
        entrada_minutos.config(state=estado_normal, bg=fondo_normal)
        entrada_segundos.config(state=estado_normal, bg=fondo_normal)
    
    #====================VALORES PARA TIMER (MODO NORMAL)====================
    frame_timer_valores = tk.LabelFrame(frame_scrollable, text="VALORES PARA TIMER (MODO NORMAL)", font=("Arial", 10, "bold"))
    frame_timer_valores.pack(fill=tk.X, padx=20, pady=10)
    
    frame_horas = tk.Frame(frame_timer_valores)
    frame_horas.pack(side=tk.LEFT, expand=True, padx=10, pady=5)
    
    etiqueta_horas = tk.Label(frame_horas, text="Horas (0-4)")
    etiqueta_horas.pack()
    
    entrada_horas = tk.Entry(frame_horas, width=10, justify="center")
    entrada_horas.insert(0, str(tiempo_inicial_default.get("horas", 0)))
    entrada_horas.pack()
    
    frame_minutos = tk.Frame(frame_timer_valores)
    frame_minutos.pack(side=tk.LEFT, expand=True, padx=10, pady=5)
    
    etiqueta_minutos = tk.Label(frame_minutos, text="Minutos (0-59)")
    etiqueta_minutos.pack()
    
    entrada_minutos = tk.Entry(frame_minutos, width=10, justify="center")
    entrada_minutos.insert(0, str(tiempo_inicial_default.get("minutos", 0)))
    entrada_minutos.pack()
    
    frame_segundos = tk.Frame(frame_timer_valores)
    frame_segundos.pack(side=tk.LEFT, expand=True, padx=10, pady=5)
    
    etiqueta_segundos = tk.Label(frame_segundos, text="Segundos (0-59)")
    etiqueta_segundos.pack()
    
    entrada_segundos = tk.Entry(frame_segundos, width=10, justify="center")
    entrada_segundos.insert(0, str(tiempo_inicial_default.get("segundos", 0)))
    entrada_segundos.pack()
    
    #====================VALORES PARA TIMER MULTINIVEL====================
    frame_timer_multinivel = tk.LabelFrame(frame_scrollable, text="VALORES PARA TIMER MULTINIVEL", font=("Arial", 10, "bold"))
    frame_timer_multinivel.pack(fill=tk.X, padx=20, pady=10)
    
    #Nivel Facil
    frame_facil = tk.LabelFrame(frame_timer_multinivel, text="Nivel Facil", font=("Arial", 9, "bold"))
    frame_facil.pack(fill=tk.X, padx=10, pady=5)
    
    frame_facil_horas = tk.Frame(frame_facil)
    frame_facil_horas.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
    label_facil_horas = tk.Label(frame_facil_horas, text="Horas")
    label_facil_horas.pack()
    entrada_facil_horas = tk.Entry(frame_facil_horas, width=8, justify="center")
    entrada_facil_horas.insert(0, str(tiempos_multinivel.get("facil", {}).get("horas", 0)))
    entrada_facil_horas.pack()
    
    frame_facil_minutos = tk.Frame(frame_facil)
    frame_facil_minutos.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
    label_facil_minutos = tk.Label(frame_facil_minutos, text="Minutos")
    label_facil_minutos.pack()
    entrada_facil_minutos = tk.Entry(frame_facil_minutos, width=8, justify="center")
    entrada_facil_minutos.insert(0, str(tiempos_multinivel.get("facil", {}).get("minutos", 0)))
    entrada_facil_minutos.pack()
    
    frame_facil_segundos = tk.Frame(frame_facil)
    frame_facil_segundos.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
    label_facil_segundos = tk.Label(frame_facil_segundos, text="Segundos")
    label_facil_segundos.pack()
    entrada_facil_segundos = tk.Entry(frame_facil_segundos, width=8, justify="center")
    entrada_facil_segundos.insert(0, str(tiempos_multinivel.get("facil", {}).get("segundos", 0)))
    entrada_facil_segundos.pack()
    
    #Nivel Intermedio
    frame_intermedio = tk.LabelFrame(frame_timer_multinivel, text="Nivel Intermedio", font=("Arial", 9, "bold"))
    frame_intermedio.pack(fill=tk.X, padx=10, pady=5)
    
    frame_intermedio_horas = tk.Frame(frame_intermedio)
    frame_intermedio_horas.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
    label_intermedio_horas = tk.Label(frame_intermedio_horas, text="Horas")
    label_intermedio_horas.pack()
    entrada_intermedio_horas = tk.Entry(frame_intermedio_horas, width=8, justify="center")
    entrada_intermedio_horas.insert(0, str(tiempos_multinivel.get("intermedio", {}).get("horas", 0)))
    entrada_intermedio_horas.pack()
    
    frame_intermedio_minutos = tk.Frame(frame_intermedio)
    frame_intermedio_minutos.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
    label_intermedio_minutos = tk.Label(frame_intermedio_minutos, text="Minutos")
    label_intermedio_minutos.pack()
    entrada_intermedio_minutos = tk.Entry(frame_intermedio_minutos, width=8, justify="center")
    entrada_intermedio_minutos.insert(0, str(tiempos_multinivel.get("intermedio", {}).get("minutos", 0)))
    entrada_intermedio_minutos.pack()
    
    frame_intermedio_segundos = tk.Frame(frame_intermedio)
    frame_intermedio_segundos.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
    label_intermedio_segundos = tk.Label(frame_intermedio_segundos, text="Segundos")
    label_intermedio_segundos.pack()
    entrada_intermedio_segundos = tk.Entry(frame_intermedio_segundos, width=8, justify="center")
    entrada_intermedio_segundos.insert(0, str(tiempos_multinivel.get("intermedio", {}).get("segundos", 0)))
    entrada_intermedio_segundos.pack()
    
    #Nivel Dificil
    frame_dificil = tk.LabelFrame(frame_timer_multinivel, text="Nivel Dificil", font=("Arial", 9, "bold"))
    frame_dificil.pack(fill=tk.X, padx=10, pady=5)
    
    frame_dificil_horas = tk.Frame(frame_dificil)
    frame_dificil_horas.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
    label_dificil_horas = tk.Label(frame_dificil_horas, text="Horas")
    label_dificil_horas.pack()
    entrada_dificil_horas = tk.Entry(frame_dificil_horas, width=8, justify="center")
    entrada_dificil_horas.insert(0, str(tiempos_multinivel.get("dificil", {}).get("horas", 0)))
    entrada_dificil_horas.pack()
    
    frame_dificil_minutos = tk.Frame(frame_dificil)
    frame_dificil_minutos.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
    label_dificil_minutos = tk.Label(frame_dificil_minutos, text="Minutos")
    label_dificil_minutos.pack()
    entrada_dificil_minutos = tk.Entry(frame_dificil_minutos, width=8, justify="center")
    entrada_dificil_minutos.insert(0, str(tiempos_multinivel.get("dificil", {}).get("minutos", 0)))
    entrada_dificil_minutos.pack()
    
    frame_dificil_segundos = tk.Frame(frame_dificil)
    frame_dificil_segundos.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
    label_dificil_segundos = tk.Label(frame_dificil_segundos, text="Segundos")
    label_dificil_segundos.pack()
    entrada_dificil_segundos = tk.Entry(frame_dificil_segundos, width=8, justify="center")
    entrada_dificil_segundos.insert(0, str(tiempos_multinivel.get("dificil", {}).get("segundos", 0)))
    entrada_dificil_segundos.pack()
    
    #Aplicar estado inicial de los campos
    actualizar_estado_timer_multinivel()
    
    #Asignar trace a las variables de nivel y reloj
    variable_nivel.trace('w', actualizar_estado_timer_multinivel)
    variable_reloj.trace('w', actualizar_estado_timer_multinivel)
    
    #====================TOP X====================
    frame_top_x = tk.LabelFrame(frame_scrollable, text="TOP X", font=("Arial", 12, "bold"))
    frame_top_x.pack(fill=tk.X, padx=20, pady=10)
    
    frame_top_x_valor = tk.Frame(frame_top_x)
    frame_top_x_valor.pack(pady=10)
    
    etiqueta_top_x = tk.Label(frame_top_x_valor, text="Cantidad (0-10, 0=todas):")
    etiqueta_top_x.pack(side=tk.LEFT, padx=5)
    
    entrada_top_x = tk.Entry(frame_top_x_valor, width=5, justify="center")
    entrada_top_x.insert(0, str(top_x_default))
    entrada_top_x.pack(side=tk.LEFT, padx=5)
    
    #====================PANEL DE ELEMENTOS====================
    frame_elementos = tk.LabelFrame(frame_scrollable, text="ELEMENTOS", font=("Arial", 12, "bold"))
    frame_elementos.pack(fill=tk.X, padx=20, pady=10)
    
    variable_elementos = tk.StringVar(value=elementos_default)
    
    frame_tabla_equivalencias = tk.Frame(frame_elementos)
    frame_tabla_equivalencias.pack(pady=10)
    
    etiqueta_numeros = tk.Label(frame_tabla_equivalencias, text="Numeros", font=("Arial", 10, "bold"))
    etiqueta_numeros.grid(row=0, column=0, padx=20)
    
    etiqueta_letras = tk.Label(frame_tabla_equivalencias, text="Letras", font=("Arial", 10, "bold"))
    etiqueta_letras.grid(row=0, column=1, padx=20)
    
    etiqueta_personalizados = tk.Label(frame_tabla_equivalencias, text="Personalizados", font=("Arial", 10, "bold"))
    etiqueta_personalizados.grid(row=0, column=2, padx=20)
    
    entradas_personalizados = []
    for i in range(1, 10):
        etiqueta_numero = tk.Label(frame_tabla_equivalencias, text=str(i))
        etiqueta_numero.grid(row=i, column=0, padx=20)
        
        letra_correspondiente = chr(ord('A') + i - 1)
        etiqueta_letra = tk.Label(frame_tabla_equivalencias, text=letra_correspondiente)
        etiqueta_letra.grid(row=i, column=1, padx=20)
        
        entrada_pers = tk.Entry(frame_tabla_equivalencias, width=3, justify="center", font=("Arial", 12))
        entrada_pers.grid(row=i, column=2, padx=20, pady=2)
        if i <= len(elementos_personalizados_guardados):
            entrada_pers.insert(0, elementos_personalizados_guardados[i-1])
        entradas_personalizados.append(entrada_pers)
    
    opcion_numeros = tk.Radiobutton(frame_elementos, text="Usar Numeros (1-9)", variable=variable_elementos, value="numeros")
    opcion_numeros.pack(anchor=tk.W, padx=20, pady=5)
    
    opcion_letras = tk.Radiobutton(frame_elementos, text="Usar Letras (A-I)", variable=variable_elementos, value="letras")
    opcion_letras.pack(anchor=tk.W, padx=20, pady=5)
    
    opcion_personalizados = tk.Radiobutton(frame_elementos, text="Definido por el jugador", variable=variable_elementos, value="personalizados")
    opcion_personalizados.pack(anchor=tk.W, padx=20, pady=5)
    
    def actualizar_estado_entradas(*args):
        if variable_elementos.get() == "personalizados":
            for entrada in entradas_personalizados:
                entrada.config(state="normal", bg="white")
        else:
            for entrada in entradas_personalizados:
                entrada.config(state="disabled", bg="#f0f0f0")
    
    variable_elementos.trace('w', actualizar_estado_entradas)
    actualizar_estado_entradas()
    
    #====================ELIMINAR HISTORIAL DE USUARIO====================
    if usuario_actual is not None:
        nombre_usuario = usuario_actual.get("nombre", "")
        if nombre_usuario and nombre_usuario != "":
            frame_eliminar = tk.LabelFrame(frame_scrollable, text="ELIMINAR HISTORIAL", font=("Arial", 12, "bold"))
            frame_eliminar.pack(fill=tk.X, padx=20, pady=10)
            
            label_eliminar_info = tk.Label(frame_eliminar, 
                text=f"Esto eliminara permanentemente al usuario '{nombre_usuario}'\n"
                     f"y todas sus partidas registradas en el TOP X.\n"
                     f"El programa se reiniciara automaticamente.",
                font=("Arial", 10), fg="red", justify="center")
            label_eliminar_info.pack(pady=10)
            
            def eliminar_historial_usuario():
                #Confirmacion
                respuesta = messagebox.askyesno(
                    "Confirmar eliminacion",
                    f"¿Esta seguro de eliminar al usuario '{nombre_usuario}' y todo su historial?\n\n"
                    "Esta accion no se puede deshacer.",
                    icon='warning'
                )
                if not respuesta:
                    return
                
                #Segunda confirmacion
                respuesta2 = messagebox.askyesno(
                    "Ultima confirmacion",
                    f"¿Realmente desea eliminar a '{nombre_usuario}'?\n\n"
                    "Todas sus partidas en el TOP X seran eliminadas.",
                    icon='warning'
                )
                if not respuesta2:
                    return
                
                #Eliminar usuario de usuarios.json
                correo_usuario = usuario_actual.get("correo", "")
                if not eliminar_usuario_por_correo(correo_usuario):
                    messagebox.showerror("Error", "No se pudo eliminar el usuario de la base de datos.")
                    return
                
                #Eliminar partidas del usuario de los arboles ABB
                if not eliminar_usuario_de_bitacora(nombre_usuario):
                    messagebox.showinfo("Informacion", "El usuario no tenia partidas registradas en el TOP X.")
                else:
                    messagebox.showinfo("Exito", f"Se eliminaron todas las partidas de '{nombre_usuario}' del TOP X.")
                
                #Cerrar ventana de configuracion
                ventana_configuracion.destroy()
                ventana_principal.destroy()
                
                #Reiniciar el programa
                messagebox.showinfo("Reiniciando", "El programa se reiniciara para aplicar los cambios.")
                reiniciar_programa()
            
            boton_eliminar_historial = tk.Button(frame_eliminar, 
                text="ELIMINAR HISTORIAL DE USUARIO", 
                command=eliminar_historial_usuario,
                width=30, height=2, bg="red", fg="white")
            boton_eliminar_historial.pack(pady=10)
    
    #====================BOTONES GUARDAR/CANCELAR====================
    frame_botones = tk.Frame(frame_scrollable)
    frame_botones.pack(pady=20)
    
    def guardar_configuracion():
        nivel_seleccionado = variable_nivel.get()
        reloj_seleccionado = variable_reloj.get()
        elementos_seleccionados = variable_elementos.get()
        
        try:
            top_x_valor = int(entrada_top_x.get())
            if top_x_valor < 0 or top_x_valor > 10:
                messagebox.showerror("Error", "TOP X debe ser un entero entre 0 y 10")
                return
        except ValueError:
            messagebox.showerror("Error", "TOP X debe ser un numero entero")
            return
        
        if reloj_seleccionado == "timer":
            if nivel_seleccionado == "multinivel":
                #Validar timer multinivel
                try:
                    #Facil
                    f_h = int(entrada_facil_horas.get())
                    f_m = int(entrada_facil_minutos.get())
                    f_s = int(entrada_facil_segundos.get())
                    if f_h < 0 or f_h > 4 or f_m < 0 or f_m > 59 or f_s < 0 or f_s > 59:
                        messagebox.showerror("Error", "Valores invalidos para nivel Facil (Horas:0-4, Min:0-59, Seg:0-59)")
                        return
                    if f_h == 0 and f_m == 0 and f_s == 0:
                        messagebox.showerror("Error", "El timer para nivel Facil debe tener al menos un valor mayor a cero")
                        return
                    
                    #Intermedio
                    i_h = int(entrada_intermedio_horas.get())
                    i_m = int(entrada_intermedio_minutos.get())
                    i_s = int(entrada_intermedio_segundos.get())
                    if i_h < 0 or i_h > 4 or i_m < 0 or i_m > 59 or i_s < 0 or i_s > 59:
                        messagebox.showerror("Error", "Valores invalidos para nivel Intermedio (Horas:0-4, Min:0-59, Seg:0-59)")
                        return
                    if i_h == 0 and i_m == 0 and i_s == 0:
                        messagebox.showerror("Error", "El timer para nivel Intermedio debe tener al menos un valor mayor a cero")
                        return
                    
                    #Dificil
                    d_h = int(entrada_dificil_horas.get())
                    d_m = int(entrada_dificil_minutos.get())
                    d_s = int(entrada_dificil_segundos.get())
                    if d_h < 0 or d_h > 4 or d_m < 0 or d_m > 59 or d_s < 0 or d_s > 59:
                        messagebox.showerror("Error", "Valores invalidos para nivel Dificil (Horas:0-4, Min:0-59, Seg:0-59)")
                        return
                    if d_h == 0 and d_m == 0 and d_s == 0:
                        messagebox.showerror("Error", "El timer para nivel Dificil debe tener al menos un valor mayor a cero")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Todos los valores del timer multinivel deben ser numeros enteros")
                    return
            else:
                #Validar timer normal (solo si NO es multinivel)
                try:
                    horas_timer = int(entrada_horas.get())
                    minutos_timer = int(entrada_minutos.get())
                    segundos_timer = int(entrada_segundos.get())
                    
                    if horas_timer < 0 or horas_timer > 4:
                        messagebox.showerror("Error", "Las horas deben estar entre 0 y 4")
                        return
                    if minutos_timer < 0 or minutos_timer > 59:
                        messagebox.showerror("Error", "Los minutos deben estar entre 0 y 59")
                        return
                    if segundos_timer < 0 or segundos_timer > 59:
                        messagebox.showerror("Error", "Los segundos deben estar entre 0 y 59")
                        return
                    if horas_timer == 0 and minutos_timer == 0 and segundos_timer == 0:
                        messagebox.showerror("Error", "El timer debe tener al menos un valor mayor a cero")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Horas, minutos y segundos deben ser numeros enteros")
                    return
        
        #Validar elementos personalizados si están seleccionados
        elementos_personalizados = []
        if elementos_seleccionados == "personalizados":
            for entrada in entradas_personalizados:
                valor = entrada.get().strip()
                if not valor:
                    messagebox.showerror("Error", "Debe ingresar los 9 elementos personalizados")
                    return
                elementos_personalizados.append(valor)
            
            es_valido, mensaje = validar_elementos_personalizados(elementos_personalizados)
            if not es_valido:
                messagebox.showerror("Error", mensaje)
                return
        
        datos_configuracion = {
            "nivel": nivel_seleccionado,
            "reloj": reloj_seleccionado,
            "top_x": top_x_valor,
            "elementos": elementos_seleccionados
        }
        
        if elementos_seleccionados == "personalizados":
            datos_configuracion["elementos_personalizados"] = elementos_personalizados
        
        if reloj_seleccionado == "timer":
            if nivel_seleccionado == "multinivel":
                datos_configuracion["tiempos_multinivel"] = {
                    "facil": {
                        "horas": int(entrada_facil_horas.get()),
                        "minutos": int(entrada_facil_minutos.get()),
                        "segundos": int(entrada_facil_segundos.get())
                    },
                    "intermedio": {
                        "horas": int(entrada_intermedio_horas.get()),
                        "minutos": int(entrada_intermedio_minutos.get()),
                        "segundos": int(entrada_intermedio_segundos.get())
                    },
                    "dificil": {
                        "horas": int(entrada_dificil_horas.get()),
                        "minutos": int(entrada_dificil_minutos.get()),
                        "segundos": int(entrada_dificil_segundos.get())
                    }
                }
            else:
                datos_configuracion["tiempo_inicial"] = {
                    "horas": int(entrada_horas.get()),
                    "minutos": int(entrada_minutos.get()),
                    "segundos": int(entrada_segundos.get())
                }
        
        directorio_script = obtener_directorio_script()
        nombre_archivo = os.path.join(directorio_script, "sudoku2026configuracion.json")
        with open(nombre_archivo, "w") as archivo:
            json.dump(datos_configuracion, archivo, indent=4)
        
        messagebox.showinfo("Exito", "Configuracion guardada.")
        ventana_configuracion.destroy()
        ventana_principal.deiconify()
    
    def cancelar_configuracion():
        ventana_configuracion.destroy()
        ventana_principal.deiconify()
    
    boton_guardar = tk.Button(frame_botones, text="GUARDAR", command=guardar_configuracion, width=15, height=1)
    boton_guardar.pack(side=tk.LEFT, padx=10)
    
    boton_cancelar = tk.Button(frame_botones, text="CANCELAR", command=cancelar_configuracion, width=15, height=1)
    boton_cancelar.pack(side=tk.LEFT, padx=10)
    
    ventana_principal.withdraw()

#====================VENTANA PRINCIPAL====================

#E:tk.Tk ventana_principal - Ventana principal del programa
#E:dict usuario - Diccionario con datos del usuario autenticado
#S:None
#Funcion:Crea la ventana principal del menu con el nombre del usuario autenticado
def crear_ventana_principal(ventana_principal, usuario):
    ventana_principal.title("Sudoku")
    ventana_principal.geometry("400x350")
    ventana_principal.resizable(False, False)
    
    frame_usuario = tk.Frame(ventana_principal)
    frame_usuario.pack(pady=10)
    
    label_correo = tk.Label(frame_usuario, text=f"Correo: {usuario['correo']}", font=("Arial", 12, "bold"), fg="purple")
    label_correo.pack()
    
    nombre_mostrar = usuario.get("nombre", "Sin nombre")
    label_nombre = tk.Label(frame_usuario, text=f"Usuario: {nombre_mostrar}", font=("Arial", 10), fg="blue")
    label_nombre.pack()
    
    def accion_boton_jugar():
        directorio_script = obtener_directorio_script()
        archivo_config = os.path.join(directorio_script, "sudoku2026configuracion.json")
        with open(archivo_config, "r") as archivo:
            config_actual = json.load(archivo)
        
        nivel_inicial = config_actual.get("nivel", "facil")
        if nivel_inicial == "multinivel":
            nivel_inicial = "facil"
        
        crear_ventana_juego(ventana_principal, usuario, nivel_inicial)
    
    def accion_boton_configurar():
        crear_ventana_configuracion(ventana_principal, usuario)
    
    def accion_boton_acerca_de():
        mostrar_acerca_de()
    
    def accion_boton_ayuda():
        abrir_manual_usuario()
    
    def accion_boton_salir():
        ventana_principal.destroy()
    
    boton_jugar = tk.Button(ventana_principal, text="JUGAR", command=accion_boton_jugar, width=20, height=2)
    boton_jugar.pack(pady=5)
    
    boton_configurar = tk.Button(ventana_principal, text="CONFIGURAR", command=accion_boton_configurar, width=20, height=2)
    boton_configurar.pack(pady=5)
    
    boton_acerca_de = tk.Button(ventana_principal, text="ACERCA DE", command=accion_boton_acerca_de, width=20, height=2)
    boton_acerca_de.pack(pady=5)
    
    boton_ayuda = tk.Button(ventana_principal, text="AYUDA", command=accion_boton_ayuda, width=20, height=2)
    boton_ayuda.pack(pady=5)
    
    boton_salir = tk.Button(ventana_principal, text="SALIR", command=accion_boton_salir, width=20, height=2)
    boton_salir.pack(pady=5)

#====================FUNCION PARA REINICIAR EL PROGRAMA====================

#E:ninguna
#S:None
#Funcion:Reinicia el programa cerrando la instancia actual y ejecutando una nueva
def reiniciar_programa():
    script_path = os.path.abspath(__file__)
    
    try:
        sys.stdout.flush()
        subprocess.Popen([sys.executable, script_path])
        sys.exit(0)
    except Exception as e:
        print(f"Error al reiniciar: {e}")
        sys.exit(0)

#====================MAIN====================

#E:ninguna
#S:None
#Funcion:Inicia la aplicacion
def main():
    resetear_configuracion_a_default()
    vaciar_historial_partidas()
    
    ventana_principal = tk.Tk()
    ventana_principal.withdraw()
    
    mostrar_login(ventana_principal)
    
    tk.mainloop()

if __name__ == "__main__":
    main()