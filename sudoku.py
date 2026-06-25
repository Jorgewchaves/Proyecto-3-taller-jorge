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
        "elementos": "numeros"
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
        with open(archivo, "w") as f:
            json.dump([], f)
        return []
    
    with open(archivo, "r") as f:
        return json.load(f)

#E:list usuarios - Lista de usuarios a guardar
#S:None
#Funcion:Guarda la lista de usuarios en el archivo usuarios.json
def guardar_usuarios(usuarios):
    directorio = obtener_directorio_script()
    archivo = os.path.join(directorio, "usuarios.json")
    
    with open(archivo, "w") as f:
        json.dump(usuarios, f, indent=4)

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

#====================FUNCIONES DE GENERACION DE SUDOKU====================

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

#E:list tablero - Tablero de Sudoku resuelto
#E:str dificultad - Nivel de dificultad ("facil","intermedio","dificil")
#S:list - Tablero con celdas eliminadas según la dificultad
#Funcion:Elimina celdas del tablero según la dificultad (30,40,50 celdas respectivamente)
def eliminar_celdas(tablero, dificultad):
    copia = [fila[:] for fila in tablero]
    
    eliminaciones = {
        "facil": 30,
        "intermedio": 40,
        "dificil": 50
    }
    
    cantidad = eliminaciones.get(dificultad, 30)
    
    posiciones = [(f, c) for f in range(9) for c in range(9)]
    random.shuffle(posiciones)
    
    for i in range(cantidad):
        fila, columna = posiciones[i]
        copia[fila][columna] = 0
    
    return copia

#E:str dificultad - Nivel de dificultad ("facil","intermedio","dificil")
#S:tuple - (tablero_juego, tablero_solucion) ambos como listas 9x9
#Funcion:Genera una partida de Sudoku completa con el nivel de dificultad especificado
def generar_partida_sudoku(dificultad):
    tablero_resuelto = generar_sudoku_valido()
    tablero_juego = eliminar_celdas(tablero_resuelto, dificultad)
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
#S:tuple - (tablero_juego, tablero_solucion) partida única no repetida
#Funcion:Genera una partida única que no esté en el historial, con máximo 100 intentos
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
    
    #Si no se encuentra una única, permitir repetición
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
    
    #Lista de numeros romanos validos de 1 a 9
    numeros_romanos_validos = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
    
    for i, elem in enumerate(elementos):
        #Verificar si es un numero romano valido
        if elem in numeros_romanos_validos:
            continue  #Es un numero romano valido, pasar al siguiente
        
        #Si no es numero romano, aplicar las restricciones normales
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
    
    #Verificar que no haya duplicados
    if len(set(elementos)) != 9:
        return False, "Los elementos no pueden repetirse entre si"
    
    return True, "Elementos validos"

#====================FUNCIONES DE BITACORA Y TOP X====================

#E:str nombre_jugador - Nombre del jugador
#E:str dificultad - Nivel de dificultad
#E:int segundos - Tiempo en segundos que tardo
#E:str fecha_hora - Fecha y hora en formato ISO8601
#S:None
#Funcion:Guarda una partida completada en el archivo de bitacora
def guardar_partida_en_bitacora(nombre_jugador, dificultad, segundos, fecha_hora):
    directorio_script = obtener_directorio_script()
    nombre_archivo = os.path.join(directorio_script, "sudoku2026_bitacora_jugadas.json")
    
    datos_bitacora = {}
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, "r") as archivo:
            datos_bitacora = json.load(archivo)
    
    if nombre_jugador not in datos_bitacora:
        datos_bitacora[nombre_jugador] = []
    
    datos_bitacora[nombre_jugador].append({
        "dificultad": dificultad,
        "tiempo": segundos,
        "fecha_hora": fecha_hora
    })
    
    with open(nombre_archivo, "w") as archivo:
        json.dump(datos_bitacora, archivo, indent=4)

#E:str nombre - Nombre del jugador a verificar
#S:bool - True si el nombre ya existe en la bitacora, False en caso contrario
#Funcion:Verifica si un nombre de jugador ya existe en el archivo de bitacora
def nombre_existe_en_bitacora(nombre):
    directorio_script = obtener_directorio_script()
    archivo_bitacora = os.path.join(directorio_script, "sudoku2026_bitacora_jugadas.json")
    
    if not os.path.exists(archivo_bitacora):
        return False
    
    with open(archivo_bitacora, "r") as archivo:
        datos_bitacora = json.load(archivo)
    
    return nombre in datos_bitacora

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
#Funcion:Genera un archivo PDF o TXT con el TOP X de mejores tiempos
def generar_top_x():
    directorio_script = obtener_directorio_script()
    archivo_bitacora = os.path.join(directorio_script, "sudoku2026_bitacora_jugadas.json")
    archivo_config = os.path.join(directorio_script, "sudoku2026configuracion.json")
    
    top_x = 0
    if os.path.exists(archivo_config):
        with open(archivo_config, "r") as archivo:
            config = json.load(archivo)
            top_x = config.get("top_x", 0)
    
    if not os.path.exists(archivo_bitacora):
        messagebox.showinfo("TOP X", "No hay partidas registradas en la bitacora.")
        return False
    
    with open(archivo_bitacora, "r") as archivo:
        datos_bitacora = json.load(archivo)
    
    partidas_por_nivel = {
        "facil": [],
        "intermedio": [],
        "dificil": []
    }
    
    for jugador, partidas in datos_bitacora.items():
        for partida in partidas:
            nivel = partida.get("dificultad", "").lower()
            if nivel in partidas_por_nivel:
                partidas_por_nivel[nivel].append({
                    "jugador": jugador,
                    "tiempo": partida.get("tiempo", 0),
                    "fecha_hora": partida.get("fecha_hora", "")
                })
    
    for nivel in partidas_por_nivel:
        partidas_por_nivel[nivel].sort(key=lambda x: x["tiempo"])
    
    for nivel in partidas_por_nivel:
        if top_x > 0 and len(partidas_por_nivel[nivel]) > top_x:
            partidas_por_nivel[nivel] = partidas_por_nivel[nivel][:top_x]
    
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
                    for i, partida in enumerate(partidas, 1):
                        tiempo_formateado = formatear_tiempo(partida["tiempo"])
                        fecha_formateada = formatear_fecha(partida["fecha_hora"])
                        f.write(f"{i}. {partida['jugador']} - {tiempo_formateado} - {fecha_formateada}\n")
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
            for i, partida in enumerate(partidas, 1):
                tiempo_formateado = formatear_tiempo(partida["tiempo"])
                fecha_formateada = formatear_fecha(partida["fecha_hora"])
                tabla_datos.append([str(i), partida["jugador"], tiempo_formateado, fecha_formateada])
            
            tabla = Table(tabla_datos, colWidths=[0.5*inch, 2*inch, 1.2*inch, 1.8*inch])
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
#S:None
#Funcion:Crea y muestra la ventana de juego con el usuario autenticado
def crear_ventana_juego(ventana_principal, usuario):
    directorio_script = obtener_directorio_script()
    archivo_config = os.path.join(directorio_script, "sudoku2026configuracion.json")
    archivo_partidas_guardadas = os.path.join(directorio_script, "sudoku2026juegoactual.json")
    
    with open(archivo_config, "r") as archivo:
        configuracion_actual = json.load(archivo)
    
    nivel_actual = configuracion_actual.get("nivel", "facil")
    tipo_elementos = configuracion_actual.get("elementos", "numeros")
    elementos_personalizados = configuracion_actual.get("elementos_personalizados", [])
    tipo_reloj_actual = configuracion_actual.get("reloj", "cronometro")
    tiempo_inicial = configuracion_actual.get("tiempo_inicial", {"horas": 0, "minutos": 0, "segundos": 0})
    
    #GENERAR PARTIDA EN TIEMPO REAL
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
    
    def elemento_a_numero(elemento):
        if elemento == "":
            return 0
        if tipo_elementos == "numeros":
            return int(elemento)
        elif tipo_elementos == "letras":
            return ord(elemento) - ord('A') + 1
        else:  #personalizados
            try:
                return elementos_personalizados.index(elemento) + 1
            except ValueError:
                return 0
    
    def numero_a_elemento(numero):
        if tipo_elementos == "numeros":
            return str(numero)
        elif tipo_elementos == "letras":
            return chr(ord('A') + numero - 1)
        else:  #personalizados
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
    
    #El nombre del jugador se toma del usuario autenticado
    nombre_jugador = usuario.get("nombre", "")
    
    #Si el usuario no tiene nombre, pedirlo
    if not nombre_jugador:
        ventana_nombre = tk.Toplevel(ventana_principal)
        ventana_nombre.title("Nombre de usuario")
        ventana_nombre.geometry("400x200")
        ventana_nombre.resizable(False, False)
        ventana_nombre.transient(ventana_principal)
        ventana_nombre.grab_set()
        
        ventana_nombre.update_idletasks()
        x = (ventana_nombre.winfo_screenwidth() // 2) - (400 // 2)
        y = (ventana_nombre.winfo_screenheight() // 2) - (200 // 2)
        ventana_nombre.geometry(f"+{x}+{y}")
        
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
                crear_ventana_juego(ventana_principal, usuario)
            else:
                label_estado_nombre.config(text="Error al guardar el nombre")
        
        boton_guardar_nombre = tk.Button(frame_nombre, text="GUARDAR", command=guardar_nombre, width=20, height=2)
        boton_guardar_nombre.pack(pady=10)
        
        entrada_nombre.bind("<Return>", lambda e: guardar_nombre())
        entrada_nombre.focus()
        
        ventana_principal.withdraw()
        return
    
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
                    crear_ventana_juego(ventana_principal, usuario)
    
    def verificar_finalizacion():
        for fila in range(9):
            for columna in range(9):
                if matriz_valores_actuales[fila][columna] == "":
                    return False
        return True
    
    def finalizar_juego():
        nonlocal juego_iniciado
        
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
        
        ventana_juego.withdraw()
        messagebox.showinfo("¡EXCELENTE!", "¡JUEGO COMPLETADO!")
        ventana_juego.deiconify()
        
        ventana_juego.destroy()
        crear_ventana_juego(ventana_principal, usuario)
    
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
        crear_ventana_juego(ventana_principal, usuario)
    
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
        
        if tipo_reloj_actual == "timer":
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
        if tipo_reloj_actual == "timer":
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
        
        if tipo_reloj_actual == "timer":
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

#====================VENTANA DE CONFIGURACION====================

#E:tk.Tk ventana_principal - Ventana principal del menu
#S:None
#Funcion:Crea y muestra la ventana de configuracion
def crear_ventana_configuracion(ventana_principal):
    ventana_configuracion = tk.Toplevel(ventana_principal)
    ventana_configuracion.title("Sudoku - Configuracion")
    ventana_configuracion.geometry("550x750")
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
    
    frame_nivel = tk.LabelFrame(frame_scrollable, text="NIVEL", font=("Arial", 12, "bold"))
    frame_nivel.pack(fill=tk.X, padx=20, pady=10)
    
    directorio_script = obtener_directorio_script()
    archivo_config = os.path.join(directorio_script, "sudoku2026configuracion.json")
    with open(archivo_config, "r") as archivo:
        config_actual = json.load(archivo)
    
    variable_nivel = tk.StringVar(value=config_actual.get("nivel", "facil"))
    
    opcion_facil = tk.Radiobutton(frame_nivel, text="Facil", variable=variable_nivel, value="facil")
    opcion_facil.pack(anchor=tk.W, padx=20, pady=5)
    
    opcion_intermedio = tk.Radiobutton(frame_nivel, text="Intermedio", variable=variable_nivel, value="intermedio")
    opcion_intermedio.pack(anchor=tk.W, padx=20, pady=5)
    
    opcion_dificil = tk.Radiobutton(frame_nivel, text="Dificil", variable=variable_nivel, value="dificil")
    opcion_dificil.pack(anchor=tk.W, padx=20, pady=5)
    
    frame_reloj = tk.LabelFrame(frame_scrollable, text="RELOJ", font=("Arial", 12, "bold"))
    frame_reloj.pack(fill=tk.X, padx=20, pady=10)
    
    variable_reloj = tk.StringVar(value=config_actual.get("reloj", "cronometro"))
    
    opcion_cronometro = tk.Radiobutton(frame_reloj, text="Cronometro", variable=variable_reloj, value="cronometro")
    opcion_cronometro.pack(anchor=tk.W, padx=20, pady=5)
    
    opcion_timer = tk.Radiobutton(frame_reloj, text="Timer", variable=variable_reloj, value="timer")
    opcion_timer.pack(anchor=tk.W, padx=20, pady=5)
    
    opcion_no_reloj = tk.Radiobutton(frame_reloj, text="No usar reloj", variable=variable_reloj, value="no_reloj")
    opcion_no_reloj.pack(anchor=tk.W, padx=20, pady=5)
    
    frame_timer_valores = tk.LabelFrame(frame_scrollable, text="VALORES PARA TIMER", font=("Arial", 10, "bold"))
    frame_timer_valores.pack(fill=tk.X, padx=20, pady=10)
    
    frame_horas = tk.Frame(frame_timer_valores)
    frame_horas.pack(side=tk.LEFT, expand=True, padx=10, pady=5)
    
    etiqueta_horas = tk.Label(frame_horas, text="Horas (0-4)")
    etiqueta_horas.pack()
    
    entrada_horas = tk.Entry(frame_horas, width=10, justify="center")
    entrada_horas.insert(0, str(config_actual.get("tiempo_inicial", {}).get("horas", 0)))
    entrada_horas.pack()
    
    frame_minutos = tk.Frame(frame_timer_valores)
    frame_minutos.pack(side=tk.LEFT, expand=True, padx=10, pady=5)
    
    etiqueta_minutos = tk.Label(frame_minutos, text="Minutos (0-59)")
    etiqueta_minutos.pack()
    
    entrada_minutos = tk.Entry(frame_minutos, width=10, justify="center")
    entrada_minutos.insert(0, str(config_actual.get("tiempo_inicial", {}).get("minutos", 0)))
    entrada_minutos.pack()
    
    frame_segundos = tk.Frame(frame_timer_valores)
    frame_segundos.pack(side=tk.LEFT, expand=True, padx=10, pady=5)
    
    etiqueta_segundos = tk.Label(frame_segundos, text="Segundos (0-59)")
    etiqueta_segundos.pack()
    
    entrada_segundos = tk.Entry(frame_segundos, width=10, justify="center")
    entrada_segundos.insert(0, str(config_actual.get("tiempo_inicial", {}).get("segundos", 0)))
    entrada_segundos.pack()
    
    frame_top_x = tk.LabelFrame(frame_scrollable, text="TOP X", font=("Arial", 12, "bold"))
    frame_top_x.pack(fill=tk.X, padx=20, pady=10)
    
    frame_top_x_valor = tk.Frame(frame_top_x)
    frame_top_x_valor.pack(pady=10)
    
    etiqueta_top_x = tk.Label(frame_top_x_valor, text="Cantidad (0-10, 0=todas):")
    etiqueta_top_x.pack(side=tk.LEFT, padx=5)
    
    entrada_top_x = tk.Entry(frame_top_x_valor, width=5, justify="center")
    entrada_top_x.insert(0, str(config_actual.get("top_x", 0)))
    entrada_top_x.pack(side=tk.LEFT, padx=5)
    
    #====================PANEL DE ELEMENTOS====================
    frame_elementos = tk.LabelFrame(frame_scrollable, text="ELEMENTOS", font=("Arial", 12, "bold"))
    frame_elementos.pack(fill=tk.X, padx=20, pady=10)
    
    variable_elementos = tk.StringVar(value=config_actual.get("elementos", "numeros"))
    
    #Tabla de equivalencias
    frame_tabla_equivalencias = tk.Frame(frame_elementos)
    frame_tabla_equivalencias.pack(pady=10)
    
    etiqueta_numeros = tk.Label(frame_tabla_equivalencias, text="Numeros", font=("Arial", 10, "bold"))
    etiqueta_numeros.grid(row=0, column=0, padx=20)
    
    etiqueta_letras = tk.Label(frame_tabla_equivalencias, text="Letras", font=("Arial", 10, "bold"))
    etiqueta_letras.grid(row=0, column=1, padx=20)
    
    etiqueta_personalizados = tk.Label(frame_tabla_equivalencias, text="Personalizados", font=("Arial", 10, "bold"))
    etiqueta_personalizados.grid(row=0, column=2, padx=20)
    
    #Crear entradas para elementos personalizados
    elementos_personalizados_guardados = config_actual.get("elementos_personalizados", [])
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
    
    #Radio buttons
    opcion_numeros = tk.Radiobutton(frame_elementos, text="Usar Numeros (1-9)", variable=variable_elementos, value="numeros")
    opcion_numeros.pack(anchor=tk.W, padx=20, pady=5)
    
    opcion_letras = tk.Radiobutton(frame_elementos, text="Usar Letras (A-I)", variable=variable_elementos, value="letras")
    opcion_letras.pack(anchor=tk.W, padx=20, pady=5)
    
    opcion_personalizados = tk.Radiobutton(frame_elementos, text="Definido por el jugador", variable=variable_elementos, value="personalizados")
    opcion_personalizados.pack(anchor=tk.W, padx=20, pady=5)
    
    #Funcion para habilitar/deshabilitar entradas
    def actualizar_estado_entradas(*args):
        if variable_elementos.get() == "personalizados":
            for entrada in entradas_personalizados:
                entrada.config(state="normal", bg="white")
        else:
            for entrada in entradas_personalizados:
                entrada.config(state="disabled", bg="#f0f0f0")
    
    variable_elementos.trace('w', actualizar_estado_entradas)
    actualizar_estado_entradas()
    
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
    
    def accion_boton_jugar():
        crear_ventana_juego(ventana_principal, usuario)
    
    def accion_boton_configurar():
        crear_ventana_configuracion(ventana_principal)
    
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

#====================MAIN====================

#E:ninguna
#S:None
#Funcion:Inicia la aplicacion
def main():
    resetear_configuracion_a_default()
    
    #Vaciar el historial de partidas al iniciar el programa
    vaciar_historial_partidas()
    
    #Crear ventana principal oculta
    ventana_principal = tk.Tk()
    ventana_principal.withdraw()
    
    #Mostrar login
    mostrar_login(ventana_principal)
    
    tk.mainloop()

if __name__ == "__main__":
    main()