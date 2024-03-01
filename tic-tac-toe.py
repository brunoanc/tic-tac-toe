import collections
import copy
import textwrap
import random
import time
import csv
from IPython.display import Markdown, display
from google.colab import drive

# Contiene el tablero y las estrategias para la IA
class Tablero:
  # Inicializa el tablero vacío con los íconos seleccionados por el usuario
  def __init__(self, icono_jugador: str, icono_ai: str):
    self.tablero = {
      "A1": " ",
      "A2": " ",
      "A3": " ",
      "B1": " ",
      "B2": " ",
      "B3": " ",
      "C1": " ",
      "C2": " ",
      "C3": " ",
    }

    self.turno = 0
    self.jugador = icono_jugador
    self.ai = icono_ai

  # Imprime el tablero en forma de cuadrícula con la guía de letras
  def imprimir(self):
    print(textwrap.dedent(f"""
        1   2   3

    A   {self.tablero["A1"]} | {self.tablero["A2"]} | {self.tablero["A3"]}
       -----------
    B   {self.tablero["B1"]} | {self.tablero["B2"]} | {self.tablero["B3"]}
       -----------
    C   {self.tablero["C1"]} | {self.tablero["C2"]} | {self.tablero["C3"]}
    """))

  # Obtiene los valores de la columna especificada
  def __columna(self, num: int):
    return [self.tablero[f"A{num}"], self.tablero[f"B{num}"], self.tablero[f"C{num}"]]

  # Obtiene los valores de la fila especificada
  def __fila(self, letra: str):
    return [self.tablero[f"{letra}1"], self.tablero[f"{letra}2"], self.tablero[f"{letra}3"]]

  # Obtiene los valores de la diagonal especificada
  def __diagonal(self, num: int):
    if num == 1:
      return [self.tablero["A1"], self.tablero["B2"], self.tablero["C3"]]
    elif num == 2:
      return [self.tablero["A3"], self.tablero["B2"], self.tablero["C1"]]

  # Obtiene el ganador si ya existe, si no, regresa None
  def ganador(self):
    # Checa por tres en línea horizontal
    for c in ["A", "B", "C"]:
      fila = self.__fila(c)
      if fila == [self.ai, self.ai, self.ai]:
        return self.ai
      elif fila == [self.jugador, self.jugador, self.jugador]:
        return self.jugador

    # Checa por tres en línea vertical
    for n in range(1, 4):
      columna = self.__columna(n)
      if columna == [self.ai, self.ai, self.ai]:
        return self.ai
      elif columna == [self.jugador, self.jugador, self.jugador]:
        return self.jugador

    # Checa por tres en línea diagonal
    for n in range(1, 3):
      diagonal = self.__diagonal(n)
      if diagonal == [self.ai, self.ai, self.ai]:
        return self.ai
      elif diagonal == [self.jugador, self.jugador, self.jugador]:
        return self.jugador

    # Si nadie ganó pero no hay lugares vacíos, es empate
    if sum(1 for k, v in self.tablero.items() if v == " ") == 0:
      return "empate"

    # La partida aún no ha terminado
    return None

  # Movimiento de la IA: Completa tres en línea para ganar
  def __ganar(self):
    # Checa por dos en línea horizontal
    for c in ["A", "B", "C"]:
      fila = self.__fila(c)
      if fila == [" ", self.ai, self.ai]:
        self.tablero[f"{c}1"] = self.ai
        return True
      elif fila == [self.ai, " ", self.ai]:
        self.tablero[f"{c}2"] = self.ai
        return True
      elif fila == [self.ai, self.ai, " "]:
        self.tablero[f"{c}3"] = self.ai
        return True

    # Checa por dos en línea vertical
    for n in range(1, 4):
      columna = self.__columna(n)
      if columna == [" ", self.ai, self.ai]:
        self.tablero[f"A{n}"] = self.ai
        return True
      elif columna == [self.ai, " ", self.ai]:
        self.tablero[f"B{n}"] = self.ai
        return True
      elif columna == [self.ai, self.ai, " "]:
        self.tablero[f"C{n}"] = self.ai
        return True

    # Checa por dos en línea diagonal
    for n in range(1, 3):
      diagonal = self.__diagonal(n)
      if diagonal == [" ", self.ai, self.ai]:
        self.tablero[f"A{2 * n - 1}"] = self.ai
        return True
      elif diagonal == [self.ai, " ", self.ai]:
        self.tablero["B2"] = self.ai
        return True
      elif diagonal == [self.ai, self.ai, " "]:
        self.tablero[f"C{-2 * n + 5}"] = self.ai
        return True

  # Movimiento de la IA: Bloquea dos en línea del oponente
  def __bloquear(self):
    # Checa por dos en línea horizontal
    for c in ["A", "B", "C"]:
      fila = self.__fila(c)
      if fila == [" ", self.jugador, self.jugador]:
        self.tablero[f"{c}1"] = self.ai
        return True
      elif fila == [self.jugador, " ", self.jugador]:
        self.tablero[f"{c}2"] = self.ai
        return True
      elif fila == [self.jugador, self.jugador, " "]:
        self.tablero[f"{c}3"] = self.ai
        return True

    # Checa por dos en línea vertical
    for n in range(1, 4):
      columna = self.__columna(n)
      if columna == [" ", self.jugador, self.jugador]:
        self.tablero[f"A{n}"] = self.ai
        return True
      elif columna == [self.jugador, " ", self.jugador]:
        self.tablero[f"B{n}"] = self.ai
        return True
      elif columna == [self.jugador, self.jugador, " "]:
        self.tablero[f"C{n}"] = self.ai
        return True

    # Checa por dos en línea diagonal
    for n in range(1, 3):
      diagonal = self.__diagonal(n)
      if diagonal == [" ", self.jugador, self.jugador]:
        self.tablero[f"A{2 * n - 1}"] = self.ai
        return True
      elif diagonal == [self.jugador, " ", self.jugador]:
        self.tablero["B2"] = self.ai
        return True
      elif diagonal == [self.jugador, self.jugador, " "]:
        self.tablero[f"C{-2 * n + 5}"] = self.ai
        return True

  # Checa si un jugador (persona o IA) tiene dos o más posibilidades de ganar en el turno
  def __checar_bifurcacion(self, j: str):
    contador_ganar = 0

    # Horizontal
    for c in ["A", "B", "C"]:
      fila = self.__fila(c)
      if collections.Counter(fila) == collections.Counter([j, j, " "]):
        contador_ganar += 1

    # Vertical
    for n in range(1, 4):
      columna = self.__columna(n)
      if collections.Counter(columna) == collections.Counter([j, j, " "]):
        contador_ganar += 1

    # Diagonal
    for n in range(1, 3):
      diagonal = self.__diagonal(n)
      if collections.Counter(diagonal) == collections.Counter([j, j, " "]):
        contador_ganar += 1

    return contador_ganar > 1

  # Movimiento de la IA: Genera dos oportunidades de ganar al mismo tiempo, dos parejas de dos en línea
  def __bifurcar(self):
    for k, v in self.tablero.items():
      if v != " ":
        continue

      # Reemplaza y verifica las oportunidades creadas
      self.tablero[k] = self.ai
      if self.__checar_bifurcacion(self.ai):
        return True
      else:
        self.tablero[k] = " "

  # Movimiento de la IA: Bloquea la generación de dobles oportunidades para el contrincante
  def __bloquear_bifurcacion(self):
    posibles_forks = set()
    for k, v in self.tablero.items():
      if v != " ":
        continue

      # Reemplaza y verifica las oportunidades creadas
      self.tablero[k] = self.jugador
      if self.__checar_bifurcacion(self.jugador):
        posibles_forks.add(k)
      self.tablero[k] = " "

    # Si solo se necesita bloquear una posición, lo hacemos
    if len(posibles_forks) == 0:
      return
    elif len(posibles_forks) == 1:
      self.tablero[posibles_forks[0]] == self.ai
      return True

    # Subcaso 1: intentaremos bloquear todas las oportunidades, aprovechando para juntar dos en línea
    for pos in posibles_forks:
      copia_tab = copy.deepcopy(self)
      copia_tab.tablero = copy.deepcopy(self.tablero)
      copia_tab.tablero[pos] = self.ai

      # Checa que pasaría si el contrincante bloquea los dos en línea: si se genera una doble oportunidad para él, no nos sirve
      copia_tab.ai, copia_tab.jugador = copia_tab.jugador, copia_tab.ai
      if copia_tab.__bloquear() and not copia_tab.__checar_bifurcacion(self.jugador):
        self.tablero[pos] = self.ai
        return True

    # Subcaso 2: Juntamos dos en línea para forzar al contrincante a bloquearnos y abandonar su estrategia
    for pos in set(self.tablero.keys()).difference(posibles_forks):
      copia_tab = copy.deepcopy(self)
      copia_tab.tablero = copy.deepcopy(self.tablero)
      copia_tab.tablero[pos] = self.ai

      copia_tab.ai, copia_tab.jugador = copia_tab.jugador, copia_tab.ai
      # Checa que pasaría si el contrincante bloquea los dos en línea
      if copia_tab.__bloquear() and not copia_tab.__checar_bifurcacion(self.jugador):
        self.tablero[pos] = self.ai
        return True

  # Movimiento de la IA: Pone en el centro
  def __centro(self):
    if self.tablero["B2"] == " ":
      self.tablero["B2"] = self.ai
      return True

  # Movimiento de la IA: Pone en la esquina opuesta al contrincante
  def __esquina_opuesta(self):
    esquinas = ["A1", "A3", "C3", "C1"]
    for i in range(len(esquinas)):
      esq = esquinas[i]
      esq_opuesta = esquinas[(i + 2) % 4]
      if self.tablero[esq] == " " and self.tablero[esq_opuesta] == self.jugador:
        self.tablero[esq] = self.ai
        return True

  # Movimiento de la IA: Pone en una esquina vacía
  def __esquina_vacia(self):
    esquinas = ["A1", "A3", "C3", "C1"]
    for esq in esquinas:
      if self.tablero[esq] == " ":
        self.tablero[esq] = self.ai
        return True

  # Movimiento de la IA: Pone en una arista vacía
  def __lado_vacio(self):
    lados = ["A2", "B3", "C2", "B1"]
    for l in lados:
      if self.tablero[l] == " ":
        self.tablero[l] = self.ai
        return True

  # Dificultad fácil de la IA: Hace movimientos aleatorios
  def turno_ai_facil(self):
    vacios = [k for k, v in self.tablero.items() if v == " "]
    seleccion = random.choice(vacios)
    self.tablero[seleccion] = self.ai

  # Dificultad intermedia de la IA: Sabe ganar, bloquear y utiliza el centro estratégicamente
  def turno_ai_intermedio(self):
    if self.__ganar():
      return
    elif self.__bloquear():
      return
    elif self.__centro():
      return
    else:
      self.turno_ai_facil()

  # Dificultad difícil de la IA: Utiliza las posiciones estratégicamente y con jerarquía
  def turno_ai_dificil(self):
    if self.__ganar():
      return
    elif self.__bloquear():
      return
    elif self.__centro():
      return
    elif self.__esquina_opuesta():
      return
    elif self.__esquina_vacia():
      return
    elif self.__lado_vacio():
      return

  # Dificultad imposible de la IA: Puede evitar dobles oportunidades, haciendo imposible ganar
  def turno_ai_imposible(self):
    if self.__ganar():
      return
    elif self.__bloquear():
      return
    elif self.__bifurcar():
      return
    elif self.__bloquear_bifurcacion():
      return
    elif self.__centro():
      return
    elif self.__esquina_opuesta():
      return
    elif self.__esquina_vacia():
      return
    elif self.__lado_vacio():
      return

# Clase para manejar las estadísticas en el archivo CSV
class Estadisticas:
  # Inicializa el diccionario leyendo del Drive
  def __init__(self):
    self.estadisticas = {
        1: [0, 0, 0],
        2: [0, 0, 0],
        3: [0, 0, 0],
        4: [0, 0, 0],
        -1: [0, 0, 0]
    }

    # Monta y lee el archivo del drive para obtener las estadísticas previas
    drive.mount('/mnt/drive')
    with open('/mnt/drive/MyDrive/Teresiano/Semestre 5/estadisticas_semestral.csv', newline='') as csvf:
      for fila in csv.reader(csvf, delimiter=','):
        self.estadisticas[int(fila[0])] = [int(n) for n in fila[1:4]]

  # Guarda las estadísticas actualizadas en Drive
  def guardar(self):
    with open('/mnt/drive/MyDrive/Teresiano/Semestre 5/estadisticas_semestral.csv', 'w', newline='') as csvf:
      escritor = csv.writer(csvf, delimiter=",")
      for k, v in self.estadisticas.items():
        escritor.writerow([k] + v)

# Main
if __name__ == "__main__":
  estadisticas = Estadisticas()

  # Íconos por defecto, se pueden cambiar
  icono_jugador = "X"
  icono_ai = "O"

  while True:
    tablero = Tablero(icono_jugador, icono_ai)

    # Menú principal
    display(Markdown(textwrap.dedent("""
    ### ¡Gato! 🐈

    **Por Bruno Ancona**

    <br/>

    **[1] Jugar contra la computadora**

    **[2] Jugar contra un amigo**

    **[3] Estadísticas**

    **[4] Ajustes**

    **[5] Salir**

    <br/>
    """)), clear = True)

    # Selección del usuario
    opcion_str = input("Elige una opción: ")

    try:
      opcion = int(opcion_str)
      if opcion not in range(1, 6):
        raise IndexError()
    except:
      print("Opción invalida, intenta de nuevo.")
      time.sleep(1)
      continue

    match opcion:
      case 1: # Contra la computadora
        # Selecciona la dificultad
        display(Markdown(textwrap.dedent("""
        ### Jugar 🎮

        <br/>

        **Opciones de dificultad:**

        <br/>

        **[1] Fácil**

        **[2] Intermedio**

        **[3] Difícil**

        **[4] Imposible**

        **[5] Regresar**

        <br/>
        """)), clear = True)

        dif_str = input("Elige una opción: ")

        try:
          dificultad = int(dif_str)
          if dificultad not in range(1, 6):
            raise IndexError()
        except:
          print("Opción invalida, intenta de nuevo.")
          time.sleep(1)
          continue

        if dificultad == 5:
          continue

        # Empezar juego
        while (ganador := tablero.ganador()) is None:
          time.sleep(1)
          if tablero.turno >= 9:
            break
          elif tablero.turno % 2 == 0:
            # Turno del jugador
            display(Markdown("**Turno: Jugador** <br/>"), clear = True)
            tablero.imprimir()

            # Preguntarle al usuario por la casilla
            casilla = input("Elige una casilla (ejemplo: B2): ").upper()
            if casilla not in ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]:
              print("Casilla invalida, intenta de nuevo.")
              continue
            elif tablero.tablero[casilla] != " ":
              print("Casilla ya usada, elige otra.")
              continue
            else:
              tablero.tablero[casilla] = tablero.jugador
              tablero.turno += 1
          else:
            # Turno de la IA
            display(Markdown("**Turno: Computadora** <br/>"), clear = True)
            tablero.imprimir()

            # Usar estrategia de acuerdo a la dificultad
            match dificultad:
              case 1: tablero.turno_ai_facil()
              case 2: tablero.turno_ai_intermedio()
              case 3: tablero.turno_ai_dificil()
              case 4: tablero.turno_ai_imposible()
            tablero.turno += 1
            time.sleep(1.5)

        # Revelar ganador
        if ganador == tablero.ai:
          display(Markdown("**Ganador: Computadora** <br/>"), clear = True)
          estadisticas.estadisticas[dificultad][2] += 1
        elif ganador == tablero.jugador:
          display(Markdown("**Ganador: Jugador** <br/>"), clear = True)
          estadisticas.estadisticas[dificultad][0] += 1
        elif ganador == "empate":
          display(Markdown("**Empate** <br/>"), clear = True)
          estadisticas.estadisticas[dificultad][1] += 1
        tablero.imprimir()
        time.sleep(5)
      case 2: # Dos jugadores
        # Empezar el juego
        while (ganador := tablero.ganador()) is None:
          time.sleep(1)
          if tablero.turno >= 9:
            break

          # Verificar de quién es el turno
          if tablero.turno % 2 == 0:
            num_jugador = 1
            icon_jugador = tablero.jugador
          else:
            num_jugador = 2
            icon_jugador = tablero.ai

          display(Markdown(f"**Turno: Jugador {num_jugador}** <br/>"), clear = True)
          tablero.imprimir()

          # Solicitar casilla al usuario
          casilla = input("Elige una casilla (ejemplo: B2): ").upper()
          if casilla not in ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]:
            print("Casilla invalida, intenta de nuevo.")
            continue
          elif tablero.tablero[casilla] != " ":
            print("Casilla ya usada, elige otra.")
            continue
          else:
            tablero.tablero[casilla] = icon_jugador
            tablero.turno += 1

        # Revelar ganador
        if ganador == tablero.ai:
          display(Markdown("**Ganador: Jugador 2** <br/>"), clear = True)
          estadisticas.estadisticas[-1][2] += 1
        elif ganador == tablero.jugador:
          display(Markdown("**Ganador: Jugador 1** <br/>"), clear = True)
          estadisticas.estadisticas[-1][0] += 1
        elif ganador == "empate":
          display(Markdown(textwrap.dedent("**Empate** <br/>")), clear = True)
          estadisticas.estadisticas[-1][1] += 1
        tablero.imprimir()
        time.sleep(5)
      case 3: # Estadísticas
        # Mostrar estadísticas en tablas de Markdown
        display(Markdown(textwrap.dedent(f"""
        ### Estadísticas 📈

        <br/>

        #### Contra la computadora

        |            |            Victorias            |             Empates             |             Derrotas            |
        |:----------:|:-------------------------------:|:-------------------------------:|:-------------------------------:|
        |    Fácil   |{estadisticas.estadisticas[1][0]}|{estadisticas.estadisticas[1][1]}|{estadisticas.estadisticas[1][2]}|
        | Intermedio |{estadisticas.estadisticas[2][0]}|{estadisticas.estadisticas[2][1]}|{estadisticas.estadisticas[2][2]}|
        |   Difícil  |{estadisticas.estadisticas[3][0]}|{estadisticas.estadisticas[3][1]}|{estadisticas.estadisticas[3][2]}|
        |  Imposible |{estadisticas.estadisticas[4][0]}|{estadisticas.estadisticas[4][1]}|{estadisticas.estadisticas[4][2]}|

        <br/>

        #### Contra tus amigos

        |             Victorias            |              Empates             |             Derrotas             |
        |:--------------------------------:|:--------------------------------:|:--------------------------------:|
        |{estadisticas.estadisticas[-1][0]}|{estadisticas.estadisticas[-1][1]}|{estadisticas.estadisticas[-1][2]}|

        <br/>
        """)), clear = True)

        input("Presiona ENTER para regresar.")
      case 4: # Ajustes
        display(Markdown("### Opciones ⚙️"), clear = True)

        # Permite al usuario seleccionar otros íconos
        icono_jugador = (input(f"Introduzca el símbolo para el jugador 1 (default: {tablero.jugador}):") or tablero.jugador)[0]
        icono_ai = (input(f"Introduzca el símbolo para la IA / jugador 2 (default: {tablero.ai}):") or tablero.ai)[0]
        print("Ajustes guardados.")

        time.sleep(1)
        continue
      case 5:
        break

  # Guardar estadísticas actualizadas
    estadisticas.guardar()
