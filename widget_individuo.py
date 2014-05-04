#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import traceback
from PySide import QtGui, QtCore
from db import ManagerBase, Fotografo, Zona


def export_csv(table):
  file = QtCore.QFile("export.csv")
  if file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Truncate):
    data = QtCore.QTextStream(file)
    str_list = []
    for i in xrange(table.columnCount()):
      str_list.append("\""+table.horizontalHeaderItem(i).data(QtCore.Qt.DisplayRole)+"\"")
    data << ";".join(str_list) << "\n"
    for r in xrange(table.rowCount()):
      str_list = []
      for c in xrange(table.columnCount()):
        #item = table.item(r, c)
        #if (not item or not item.text()):
          #self.setItem(r, c, QtGui.QTableWidgetItem("0"))
        str_list.append("\""+table.item(r, c).text()+"\"")
      data << ";".join(str_list) << "\n"
    file.close()

sexo = ["Masculino", "Femenino", "No determinado"]

class WidgetAgregarZona(QtGui.QWidget):
  def __init__(self, parent=None, widget_extend = None):
    super(WidgetAgregarZona, self).__init__(parent)
    self.setLayout(self.iniciar_ui())
    self.show()
    self.widget_extend = widget_extend

  def guardar(self):
    db_man = ManagerBase()
    n = self.name_input.text()
    ln = self.lastname_input.text()
    em = self.email_input.text()
    if (n and ln and em):
      zona = db_man.nueva_zona(n, ln, em)
      self.close()
      if self.widget_extend != None:
        self.widget_extend.extend(zona)

  def iniciar_ui(self):
    #labels, inputs y boton guardar
    self.name_label = QtGui.QLabel("Nombre")
    self.name_input = QtGui.QLineEdit()
    self.lastname_label = QtGui.QLabel("Latitud")
    self.lastname_input = QtGui.QLineEdit()
    self.email_label = QtGui.QLabel("Longitud")
    self.email_input = QtGui.QLineEdit()
    save_button = QtGui.QPushButton("Guardar")
    save_button.clicked.connect(self.guardar)

    #layout
    lay = QtGui.QGridLayout()
    lay.addWidget(self.name_label, 0, 0)
    lay.addWidget(self.name_input, 0, 1)
    lay.addWidget(self.lastname_label, 1, 0)
    lay.addWidget(self.lastname_input, 1, 1)
    lay.addWidget(self.email_label, 2, 0)
    lay.addWidget(self.email_input, 2, 1)
    lay.addWidget(save_button, 3, 1)
    return lay


class WidgetAgregarFotografo(QtGui.QWidget):
  def __init__(self, parent=None, widget_extend = None):
    super(WidgetAgregarFotografo, self).__init__(parent)
    self.setLayout(self.iniciar_ui())
    self.show()
    self.widget_extend = widget_extend

  def guardar(self):
    db_man = ManagerBase()
    n = self.name_input.text()
    ln = self.lastname_input.text()
    em = self.email_input.text()
    if (n and ln and em):
      fotografo = db_man.nuevo_fotografo(n, ln, em)
      self.close()
      if self.widget_extend != None:
        self.widget_extend.extend(fotografo)

  def iniciar_ui(self):
    #labels, inputs y boton guardar
    self.name_label = QtGui.QLabel("Nombre")
    self.name_input = QtGui.QLineEdit()
    self.lastname_label = QtGui.QLabel("Apellido")
    self.lastname_input = QtGui.QLineEdit()
    self.email_label = QtGui.QLabel("e-mail")
    self.email_input = QtGui.QLineEdit()
    save_button = QtGui.QPushButton("Guardar")
    save_button.clicked.connect(self.guardar)

    #layout
    lay = QtGui.QGridLayout()
    lay.addWidget(self.name_label, 0, 0)
    lay.addWidget(self.name_input, 0, 1)
    lay.addWidget(self.lastname_label, 1, 0)
    lay.addWidget(self.lastname_input, 1, 1)
    lay.addWidget(self.email_label, 2, 0)
    lay.addWidget(self.email_input, 2, 1)
    lay.addWidget(save_button, 3, 1)
    return lay

class WidgetIndividuoConCapturas(QtGui.QWidget):
  """
  Widget que contiene una imagen del individuo con sus respectivas capturas
  las capturas se encuentran dentro de una tabla
  """
  def __init__(self, individuo, parent=None):
    super(WidgetIndividuoConCapturas, self).__init__(parent, QtCore.Qt.Window)
    self.parent = parent
    self.id_individuo = individuo.id
    self.setLayout(self.iniciar_ui(individuo))
    self.show()

  def iniciar_ui(self, individuo):

    self.id = QtGui.QLabel("id")
    self.id_input = QtGui.QLabel(str(individuo.id))
    self.sexo = QtGui.QLabel("sexo")
    self.sexo_input = ComboBoxSexo()
    self.sexo_input.setDisabled(True)
    self.sexo_input.setCurrentIndex(sexo.index(individuo.sexo))
    self.observaciones = QtGui.QLabel("Observaciones")
    self.observaciones_input = QtGui.QTextEdit(individuo.observaciones)
    self.observaciones_input.setDisabled(True)

    self.table = WidgetTableCapturas(capturas=individuo.capturas)
    self.vbox = QtGui.QVBoxLayout()

    #layout
    lay = QtGui.QGridLayout()
    lay.addWidget(self.id, 0, 0)
    lay.addWidget(self.id_input, 0, 1)
    lay.addWidget(self.sexo, 1, 0)
    lay.addWidget(self.sexo_input, 1, 1)
    lay.addWidget(self.observaciones, 2, 0)
    lay.addWidget(self.observaciones_input, 2, 1)
    #lay.addWidget(save_button, 3, # 1)

    self.vbox.addLayout(lay)
    self.vbox.addWidget(self.table)
    return self.vbox

  def closeEvent(self, a):
    del self.parent.opened_windows[unicode(self.id_individuo)]


class WidgetIndividuo(QtGui.QWidget):
  """
  Widget compuesto de un WidgetDatos y un WidgetGaleria.
  Sirve para mostrar los datos de un individuo, y las capturas de este individuo.
  lista_imagenes: lista de imagenes para la galeria. Esta lista se muestra en
  WidgetGaleria.
  datos: diccionario con los datos del individuo, que se van a mostrar en el
  WidgetDatos.
  """

  def __init__(self, lista_imagenes, datos_individuo, parent=None):
    super(WidgetIndividuo, self).__init__(parent)
    self.iniciar_ui(lista_imagenes, datos_individuo)

  def iniciar_ui(self, lista_imagenes, datos_individuo):
    self.setWindowFlags(QtCore.Qt.Window)
    #self.setGeometry(300, 300, 600, 400)
    self.setWindowTitle("Galeria de imagenes para un individuo")
    self.crear_layout(lista_imagenes, datos_individuo)
    self.show()

  def crear_layout(self, lista_imagenes, datos_individuo):
    vertical_lay = QtGui.QVBoxLayout()
    vertical_lay.addWidget(WidgetDatos(datos_individuo))

    horizontal_lay = QtGui.QHBoxLayout()
    horizontal_lay.addWidget(WidgetGaleria(lista_imagenes))
    horizontal_lay.addLayout(vertical_lay)

    self.setLayout(horizontal_lay)

class WidgetBotonesAtrasAdelante(QtGui.QWidget):
  """
  Este widget muestra un par de botones tipo adelante/atras
  """
  def __init__(self, parent=None):
    super(WidgetBotonesAtrasAdelante, self).__init__(parent)
    self.iniciar_ui()

  def iniciar_ui(self):
    #Botones
    self.boton_atras = QtGui.QPushButton('Atras', self)
    self.boton_adelante = QtGui.QPushButton('Adelante', self)
    self.boton_adelante.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
    self.boton_atras.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)

    #Layout
    horizontal_lay = QtGui.QHBoxLayout()
    horizontal_lay.addWidget(self.boton_atras)
    horizontal_lay.addWidget(self.boton_adelante)

    self.setLayout(horizontal_lay)

class WidgetImagen(QtGui.QWidget):
  """
  Este widget muestra una galeria de imagenes para un invididuo dado.
  La idea es usar un QLabel para mostrar las imagenes. Los botones van en una subclase.
  """
  def __init__(self, lista_imagenes, parent=None):
    super(WidgetImagen, self).__init__(parent)
    self.iniciar_ui()
    if lista_imagenes:
      self.set_imagen(lista_imagenes[0])
    self.indice_imagenes = 0
    self.lista_imagenes = lista_imagenes

  def iniciar_ui(self):
    #Label
    self.image_label = QtGui.QLabel()
    self.image_label.setBackgroundRole(QtGui.QPalette.Base)
    self.image_label.setSizePolicy(QtGui.QSizePolicy.Ignored,QtGui.QSizePolicy.Ignored)
    self.image_label.setScaledContents(True)

    #Scroll area
    self.scroll_area = QtGui.QScrollArea()
    self.scroll_area.setBackgroundRole(QtGui.QPalette.Dark);
    self.scroll_area.setWidget(self.image_label)
    self.scroll_area.setWidgetResizable(True)

    #Layout
    self.vertical_lay = QtGui.QVBoxLayout()
    self.vertical_lay.addWidget(self.scroll_area)

    #Seteamos el layout para el widget
    self.setLayout(self.vertical_lay)

  def set_imagen(self, image):
    """
    Antes de agregar la imagen al pixmap, la escalamos a 150x150
    """
    self.image_label.setPixmap(QtGui.QPixmap.fromImage(image.scaled(150,150)))

  def atras(self):
    """
    Mostramos la imagen anterior
    """
    self.indice_imagenes = (self.indice_imagenes - 1) % len(self.lista_imagenes)
    if (self.indice_imagenes < 0): self.indice_imagenes = len(self.lista_imagenes) - 1
    self.set_imagen(self.lista_imagenes[self.indice_imagenes])

  def adelante(self):
    """
    Mostramos la siguiente imagen
    """
    self.indice_imagenes = (self.indice_imagenes + 1) % len(self.lista_imagenes)
    self.set_imagen(self.lista_imagenes[self.indice_imagenes])

class WidgetGaleria(WidgetImagen):
  """
  Extiende WidgetImagen agregandole 2 botones para avanzar y retroceder la galeria.
  Para obtener los botones, se compone usa el WidgetBotonesAtrasAdelante.
  lista_imagenes: lista con las imagenes que se van a mostrar en la galeria.
  """
  def __init__(self, lista_imagenes, parent=None):
    super(WidgetGaleria, self).__init__(lista_imagenes, parent)
    self._iniciar_ui()

  def _iniciar_ui(self):
    #Botones para pasar de imagen
    botones = WidgetBotonesAtrasAdelante()
    botones.boton_atras.clicked.connect(self.adelante)
    botones.boton_adelante.clicked.connect(self.atras)

    self.vertical_lay.addWidget(botones)

class WidgetDatos(QtGui.QWidget):
  """
  La idea de este widget es mostrar un grid con los datos de un individuo,
  con los datos de dicc_datos.
  """
  def __init__(self, dicc_datos, parent=None):
    super(WidgetDatos, self).__init__(parent)
    self.labels = dicc_datos
    self.iniciar_ui()

  def iniciar_ui(self):
    """
    La ui es un gridlayout con labels tipo key value
    """
    grid_lay = QtGui.QGridLayout()
    idx = 0
    policy = QtGui.QSizePolicy.Minimum
    for k,v in self.labels.iteritems():
      l1 = QtGui.QLabel(k)
      l1.setSizePolicy(policy, policy)
      grid_lay.addWidget(l1, idx, 0)

      l2 = QtGui.QLabel(v)
      l2.setSizePolicy(policy, policy)
      grid_lay.addWidget(l2, idx, 1)

      idx += 1

    #Hack horrible para que la ultima fila ocupe el mayor espacio posible
    l1 = QtGui.QLabel("")
    l1.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
    grid_lay.addWidget(l1, idx, 0)

    self.setLayout(grid_lay)

class ComboBoxSexo(QtGui.QComboBox):

  def __init__(self):
    super(ComboBoxSexo, self).__init__()
    for s in sexo:
      self.addItem(s)


class MyRadioButtonSexo(QtGui.QRadioButton):

  def __init__(self, text, parent):
    self.parent = parent
    super(MyRadioButtonSexo, self).__init__(text)
    self.clicked.connect(self.click)

  def click(self):
    self.parent.sexo = self.text()

class MyRadioButton(QtGui.QRadioButton):

  def __init__(self, parent):
    self.parent = parent
    super(MyRadioButton, self).__init__()
    self.clicked.connect(self.click)

  def click(self):
    #if (self.parent.iRadioChecked == -1):
    self.parent.widget_botones.botonAgrCaptura.setEnabled(True)
    self.parent.iRadioChecked = self.index

class WidgetScroleable(QtGui.QWidget):
  """
  Agrega una barra de scroll, al widget que se le pasa como parametro.
  """
  def __init__(self, widget, parent=None):
    super(WidgetScroleable, self).__init__(parent)
    self.scroll_area = QtGui.QScrollArea()
    self.scroll_area.setWidget(widget)

    self.lay = QtGui.QVBoxLayout()
    self.lay.addWidget(self.scroll_area)

    self.setLayout(self.lay)

def WidgetListaIndividuosScroleable(similares=None, parent=None):
  return WidgetScroleable(WidgetListaIndividuos(similares, parent))

class WidgetListaIndividuos(QtGui.QWidget):
  """
  Widget que muestra una lista vertical de 1 captura por individuo, con un radiobutton y un boton para mostrar el individuo.
  similares: diccionario de la forma
    {id_individuo: {imagen: <imagen captura>, dicc_datos: <diccionario con los datos del individuo>, capturas: <lista de imagenes de las capturas>}}
  Todas las imagenes son QImage.
  """
  def __init__(self, similares=None, parent=None):
    self.parent = parent
    super(WidgetListaIndividuos, self).__init__(parent)
    if similares is None: similares = {}
    #Creamos el layout y lo seteamos. Las subclases, pueden overridear este metodo para modificar el layout.
    lay = self.crear_layout(similares)
    self.setLayout(lay)

  def crear_layout(self, similares):
    vertical_lay = QtGui.QVBoxLayout()
    for sapo_id, dicc_sapo in similares.iteritems():
      horizontal_lay = QtGui.QHBoxLayout()
      #En vez de pasar la imagen sola, pasamos una lista de 1 elemento con la imagen.
      horizontal_lay.addWidget(WidgetImagen([dicc_sapo["imagen"]]))
      boton_mostrar = QtGui.QPushButton("Mostrar individuo")
      boton_mostrar.clicked.connect(self.launch)
      boton_mostrar.id_individuo = sapo_id
      boton_mostrar.datos_individuo = dicc_sapo["dicc_datos"]
      boton_mostrar.lista_imagenes = dicc_sapo["lista_imagenes"]
      horizontal_lay.addWidget(boton_mostrar)
      vertical_lay.addLayout(horizontal_lay)
    return vertical_lay

  def launch(self):
    WidgetIndividuo(self.sender().lista_imagenes, self.sender().datos_individuo, self)

def WidgetListaIndividuosStandaloneScroleable(similares=None, parent=None):
  return WidgetScroleable(WidgetListaIndividuosStandalone(similares, parent))

class WidgetListaIndividuosStandalone(WidgetListaIndividuos):
  """
  Esta lista de individuos, muestra el thumbnail de cada individuo, los datos del mismo
  y el boton "mostrar individuo" que lanza la galeria.
  """

  def crear_layout(self, similares):
    """
    Metemos un WidgetDatos entre la imagen y el boton mostrar.
    """
    lay = super(WidgetListaIndividuosStandalone, self).crear_layout(similares)
    for idx, key in enumerate(similares):
      lay.itemAt(idx).insertWidget(1,WidgetDatos(similares[key]["dicc_datos"]))
    return lay

def WidgetListaIndividuosRadiosScroleable(similares=None, parent=None):
  return WidgetScroleable(WidgetListaIndividuosRadios(similares, parent))

class WidgetListaIndividuosRadios(WidgetListaIndividuos):
  """
  Sublcase de WidgetListaIndividuos que agrega radiobuttons a cada individuo.
  """

  def crear_layout(self, similares):
    vertical_lay = QtGui.QVBoxLayout()
    self.parent.radios = []
    i = 0
    for dicc_sapo in similares:
      sapo_id = dicc_sapo["id"]
      horizontal_lay = QtGui.QHBoxLayout()
      radio = MyRadioButton(self.parent)
      radio.id_individuo = sapo_id
      radio.index = i
      horizontal_lay.addWidget(radio)
      self.parent.radios.append(radio)
      i = i + 1
      #En vez de pasar la imagen sola, pasamos una lista de 1 elemento con la imagen.
      horizontal_lay.addWidget(WidgetImagen([dicc_sapo["imagen"]]))
      boton_mostrar = QtGui.QPushButton("Mostrar individuo")
      boton_mostrar.clicked.connect(self.launch)
      boton_mostrar.id_individuo = sapo_id
      boton_mostrar.datos_individuo = dicc_sapo["dicc_datos"]
      boton_mostrar.lista_imagenes = dicc_sapo["lista_imagenes"]
      horizontal_lay.addWidget(boton_mostrar)
      vertical_lay.addLayout(horizontal_lay)
    return vertical_lay

class WidgetBotonesAgregarCaptura(QtGui.QWidget):

  def __init__(self, parent = None):
    super(WidgetBotonesAgregarCaptura, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()

  def iniciar_ui(self):
    horizontal_layout = QtGui.QHBoxLayout()
    self.botonNuevo = QtGui.QPushButton("Nuevo")
    self.botonAgrCaptura = QtGui.QPushButton("Agregar Captura")
    self.botonAgrCaptura.setEnabled(False)
    horizontal_layout.addWidget(self.botonNuevo)
    horizontal_layout.addWidget(self.botonAgrCaptura)

    self.botonNuevo.clicked.connect(self.launchNuevo)
    self.botonAgrCaptura.clicked.connect(self.launchAgrCaptura)

    self.setLayout(horizontal_layout)

  def launchNuevo(self):
    WidgetNuevoIndividuo(self.parent)

  def launchAgrCaptura(self):
    WidgetNuevaCaptura(self.parent)
#    print self.parent.iRadioChecked
#    if (self.parent.iRadioChecked != -1):
#      self.parent.agregarCaptura(self.parent.radios[self.parent.iRadioChecked].id_individuo, {})

class WidgetAgregarCaptura(QtGui.QWidget):

  def __init__(self, parent = None):
    super(WidgetAgregarCaptura, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()

  def guardar(self, individuo_id = None):
    db_man = ManagerBase()
    if (individuo_id == None):
      individuo_id = self.parent.radios[self.parent.iRadioChecked].id_individuo
    img_original = self.parent.q_img
    img_transformada = self.parent.qimage_transformada
    img_segmentada = self.parent.qimage_segmentada
    vector_regiones = self.parent.vector_regiones
    fecha = self.fecha.dateTime().toPython() if self.fecha.dateTime() != '01/01/2000 00:00:00' else None
    lat = self.latitud.text() if self.latitud.text() != '' else None
    lon = self.longitud.text() if self.longitud.text() != '' else None
    acompaniantes = self.cantidadSapitos.text() if self.cantidadSapitos.text() != '' else None
    observaciones = self.observaciones.toPlainText() if self.observaciones.toPlainText() != '' else None
    nombre_imagen = self.archivo.text()
    puntos = self.parent.getPoints()
    angulos = self.parent.getAngles()
    largos = self.parent.getLarges()
    fotografo_id = self.fotografos.items.itemData(self.fotografos.items.currentIndex())
    zona_id = self.zona.items.itemData(self.zona.items.currentIndex())
    superficie_ocupada = self.parent.superficie_ocupada
    if (individuo_id and img_original and img_segmentada and img_transformada):
      db_man.crear_captura(individuo_id, img_original, img_transformada, img_segmentada, vector_regiones, fecha, lat, lon,\
                           acompaniantes, observaciones, nombre_imagen, puntos, angulos, largos, fotografo_id, zona_id, superficie_ocupada)
      self.close()

  def iniciar_ui(self):
    self.fecha = QtGui.QDateTimeEdit()
    self.zona = WidgetComboBoxExtensible(Zona, self.parent)
    self.latitud = QtGui.QLineEdit()
    self.longitud = QtGui.QLineEdit()
    self.fotografos = WidgetComboBoxExtensible(Fotografo, self.parent)
    self.cantidadSapitos = QtGui.QLineEdit()
    self.observaciones = QtGui.QTextEdit()
    self.archivo = QtGui.QLineEdit()
    self.archivo.setText(self.parent.filename_nopath)

    qgridLayout = QtGui.QGridLayout()

    qgridLayout.addWidget(QtGui.QLabel("CAPTURA"), 0, 0)
    qgridLayout.addWidget(QtGui.QLabel("fecha: "), 1, 0)
    qgridLayout.addWidget(self.fecha, 1, 1)
    qgridLayout.addWidget(QtGui.QLabel("Zona: "), 2, 0)
    qgridLayout.addWidget(self.zona, 2, 1)
    qgridLayout.addWidget(QtGui.QLabel("Latitud: "), 3, 0)
    qgridLayout.addWidget(self.latitud, 3, 1)
    qgridLayout.addWidget(QtGui.QLabel("Longitud: "), 4, 0)
    qgridLayout.addWidget(self.longitud, 4, 1)
    qgridLayout.addWidget(QtGui.QLabel("Fotografo: "), 5, 0)
    qgridLayout.addWidget(self.fotografos, 5, 1)
    qgridLayout.addWidget(QtGui.QLabel("Sapitos acomp: "), 6, 0)
    qgridLayout.addWidget(self.cantidadSapitos, 6, 1)
    qgridLayout.addWidget(QtGui.QLabel("Observaciones: "), 7, 0)
    qgridLayout.addWidget(self.observaciones, 7, 1)
    qgridLayout.addWidget(QtGui.QLabel("Archivo: "), 8, 0)
    qgridLayout.addWidget(self.archivo, 8, 1)

    self.setLayout(qgridLayout)

class WidgetBuscarCaptura(QtGui.QWidget):

  def __init__(self, parent = None):
    super(WidgetBuscarCaptura, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()
    self.showMaximized()
    self.default_date_time = QtGui.QDateTimeEdit().dateTime()

  def buscar(self):
    individuo_id = self.id_individuo.text() if self.id_individuo.text() != '' else None
    captura_id = self.id_captura.text() if self.id_captura.text() != '' else None
    date_time_inic = self.date_time_inic.dateTime().toPython() if self.date_time_inic.dateTime() != self.default_date_time else None
    date_time_fin = self.date_time_fin.dateTime().toPython() if self.date_time_fin.dateTime() != self.default_date_time else None
    zona_id = self.zona.items.itemData(self.zona.items.currentIndex())
    zona_id = zona_id if zona_id != -1 else None
    fotografo_id = self.fotografo.items.itemData(self.fotografo.items.currentIndex())
    fotografo_id = fotografo_id if fotografo_id != -1 else None
    cant_sapitos_min = self.cant_sapitos_min.text() if self.cant_sapitos_min.text() != '' else None
    cant_sapitos_max = self.cant_sapitos_max.text() if self.cant_sapitos_max.text() != '' else None
    observaciones = self.observaciones.text() if self.observaciones.text() != '' else None
    archivo = self.archivo.text() if self.archivo.text() != '' else None

    db_man = ManagerBase()
    capturas = db_man.buscar_capturas(individuo_id, captura_id, date_time_inic, date_time_fin, zona_id, fotografo_id,\
                         cant_sapitos_min, cant_sapitos_max, observaciones, archivo)

    self.table.set_capturas(capturas)

  def iniciar_ui(self):
    vbox = QtGui.QVBoxLayout()
    qgridLayout = QtGui.QGridLayout()
    vbox.addLayout(qgridLayout)

    boton_buscar = QtGui.QPushButton("Buscar")
    boton_buscar.clicked.connect(self.buscar)
    vbox.addWidget(boton_buscar)

    self.table = WidgetTableCapturas(self)

    vbox.addWidget(self.table)

    db_man = ManagerBase()

    self.id_individuo = QtGui.QLineEdit()
    self.id_individuo.setValidator(QtGui.QIntValidator())
    self.id_captura = QtGui.QLineEdit()
    self.id_captura.setValidator(QtGui.QIntValidator())
    self.sexo = WidgetComboBoxList(sexo, self.parent)
    self.zona = WidgetComboBoxType(Zona, self.parent)
    self.fotografo = WidgetComboBoxType(Fotografo, self.parent)
    self.cant_sapitos_min = QtGui.QLineEdit()
    self.cant_sapitos_min.setValidator(QtGui.QIntValidator())
    self.cant_sapitos_max = QtGui.QLineEdit()
    self.cant_sapitos_max.setValidator(QtGui.QIntValidator())
    self.observaciones = QtGui.QLineEdit()
    self.archivo = QtGui.QLineEdit()

    self.date_time_inic = QtGui.QDateTimeEdit()
    self.date_time_inic.setCalendarPopup(True)
    self.date_time_inic.setCalendarWidget(QtGui.QCalendarWidget())

    self.date_time_fin = QtGui.QDateTimeEdit()
    self.date_time_fin.setCalendarPopup(True)
    self.date_time_fin.setCalendarWidget(QtGui.QCalendarWidget())


    qgridLayout.addWidget(QtGui.QLabel("id individuo: "), 0, 0)
    qgridLayout.addWidget(self.id_individuo, 0, 1)
    qgridLayout.addWidget(QtGui.QLabel("id captura: "), 0, 2)
    qgridLayout.addWidget(self.id_captura, 0, 3)
    qgridLayout.addWidget(QtGui.QLabel("fecha inicio: "), 0, 4)
    qgridLayout.addWidget(self.date_time_inic, 0, 5)
    qgridLayout.addWidget(QtGui.QLabel("fecha fin: "), 0, 6)
    qgridLayout.addWidget(self.date_time_fin, 0, 7)
    qgridLayout.addWidget(QtGui.QLabel("Zona: "), 1, 0)
    qgridLayout.addWidget(self.zona, 1, 1)
    qgridLayout.addWidget(QtGui.QLabel("Fotografo: "), 1, 2)
    qgridLayout.addWidget(self.fotografo, 1, 3)
    qgridLayout.addWidget(QtGui.QLabel("Sapitos acomp min: "), 1, 4)
    qgridLayout.addWidget(self.cant_sapitos_min, 1, 5)
    qgridLayout.addWidget(QtGui.QLabel("Sapitos acomp max: "), 1, 6)
    qgridLayout.addWidget(self.cant_sapitos_max, 1, 7)
    qgridLayout.addWidget(QtGui.QLabel("Observaciones: "), 2, 0)
    qgridLayout.addWidget(self.observaciones, 2, 1)
    qgridLayout.addWidget(QtGui.QLabel("Archivo: "), 2, 2)
    qgridLayout.addWidget(self.archivo, 2, 3)

    self.setLayout(vbox)

    self.show()

class WidgetBuscarIndividuo(QtGui.QWidget):

  def __init__(self, parent = None):
    super(WidgetBuscarIndividuo, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()

  def buscar(self):
    individuo_id = self.id_individuo.text() if self.id_individuo.text() != '' else None
    sexo = self.sexo.items.currentText()
    sexo = sexo if sexo != "..." else None
    observaciones = self.observaciones.text() if self.observaciones.text() != '' else None

    db_man = ManagerBase()
    individuos = db_man.buscar_individuos(individuo_id, sexo, observaciones)

    self.table.set_individuos(individuos)

  def iniciar_ui(self):
    vbox = QtGui.QVBoxLayout()
    qgridLayout = QtGui.QGridLayout()
    vbox.addLayout(qgridLayout)

    boton_buscar = QtGui.QPushButton("Buscar")
    boton_buscar.clicked.connect(self.buscar)
    vbox.addWidget(boton_buscar)

    self.table = WidgetTableIndividuos(self)

    vbox.addWidget(self.table)

    db_man = ManagerBase()

    self.id_individuo = QtGui.QLineEdit()
    self.id_individuo.setValidator(QtGui.QIntValidator())
    self.sexo = WidgetComboBoxList(sexo, self.parent)
    self.observaciones = QtGui.QLineEdit()

    qgridLayout.addWidget(QtGui.QLabel("id individuo: "), 0, 0)
    qgridLayout.addWidget(self.id_individuo, 0, 1)
    qgridLayout.addWidget(QtGui.QLabel("Sexo: "), 0, 2)
    qgridLayout.addWidget(self.sexo, 0, 3)
    qgridLayout.addWidget(QtGui.QLabel("Observaciones: "), 0, 4)
    qgridLayout.addWidget(self.observaciones, 0, 5)

    self.setLayout(vbox)

    self.show()

class WidgetTableIndividuos(QtGui.QTableWidget):
  table_header_labels = ["id individuo", "sexo", "observaciones"]

  def __init__(self, parent, individuos = None):
    super(WidgetTableIndividuos, self).__init__(0, 3, parent)
    self.individuos = individuos
    self.setSortingEnabled(True)
    self.setHorizontalHeaderLabels(self.table_header_labels)
    self.horizontalHeader().resizeSection(1, 150)
    self.horizontalHeader().resizeSection(2, 500)
    self.id = None
    self.opened_windows = {}
    if self.individuos:
      self.load()

  def set_individuos(self, individuos):
    self.individuos = individuos
    self.load()

  def load(self):
    db_man = ManagerBase()

    i = 0
    self.clear()
    self.setSortingEnabled(False)

    while (self.rowCount() > 0):
      self.removeRow(0)

    for individuo in self.individuos:
      item_id = QtGui.QTableWidgetItem("%s" % (individuo.id))
      item_sexo = QtGui.QTableWidgetItem("%s" % (individuo.sexo))
      item_observaciones = QtGui.QTableWidgetItem("%s" % (individuo.observaciones))

      item_id.setFlags(item_id.flags() & ~QtCore.Qt.ItemIsEditable)

      self.insertRow(i)
      self.cellClicked.connect(self.cell_was_clicked)
      self.setItem(i, 0, item_id)
      self.setItem(i, 1, item_sexo)
      self.setItem(i, 2, item_observaciones)
      i += 1
    self.setSortingEnabled(True)
    self.setHorizontalHeaderLabels(self.table_header_labels)

  def cell_was_clicked(self, row, column):
    item = self.item(row, column)
    if column == 0:
      if item.text() not in self.opened_windows:
        self.opened_windows[item.text()] = WidgetIndividuoConCapturas(ManagerBase().get_individuo(item.text()), self)
      else:
        self.opened_windows[item.text()].activateWindow()




class WidgetTableCapturas(QtGui.QTableWidget):
  table_header_labels = ["id individuo", "id captura", "fecha", "zona", "fotografo", "archivo", "segmentada",  "transformada", "original", "observaciones"]

  def __init__(self, parent = None, capturas = None):
    super(WidgetTableCapturas, self).__init__(0, 10, parent)
    self.capturas = capturas
    self.setSortingEnabled(True)
    self.setHorizontalHeaderLabels(self.table_header_labels)
    self.horizontalHeader().resizeSection(5, 150)
    self.horizontalHeader().resizeSection(6, 150)
    self.horizontalHeader().resizeSection(7, 150)
    self.horizontalHeader().resizeSection(8, 150)
    self.horizontalHeader().resizeSection(9, 300)

    if self.capturas:
      self.load()

  def set_capturas(self, capturas):
    self.capturas = capturas
    self.load()

  def load(self):
    db_man = ManagerBase()

    i = 0
    self.clear()
    self.setSortingEnabled(False)

    while (self.rowCount() > 0):
      self.removeRow(0)

    for captura in self.capturas:
      item_id_individuo = QtGui.QTableWidgetItem("%s" % (captura.individuo_id))
      item_id = QtGui.QTableWidgetItem("%s" % (captura.id))
      item_imagen = QtGui.QTableWidgetItem("%s" % (captura.nombre_imagen))
      item_fecha = QtGui.QTableWidgetItem("%s" % (captura.fecha))
      item_fotografo = QtGui.QTableWidgetItem("%s" % (db_man.get_fotografo(captura.fotografo_id).description()))
      item_zona = QtGui.QTableWidgetItem("%s" % (db_man.get_zona(captura.zona_id).description()))
      item_img_seg = QtGui.QTableWidgetItem()
      item_img_seg.setData(QtCore.Qt.DecorationRole, QtGui.QPixmap.fromImage(db_man.bytes_a_imagen(captura.imagen_segmentada).scaled(150, 150)))
      item_img_trans = QtGui.QTableWidgetItem()
      item_img_trans.setData(QtCore.Qt.DecorationRole, QtGui.QPixmap.fromImage(db_man.bytes_a_imagen(captura.imagen_transformada).scaled(150, 150)))
      item_img_origin = QtGui.QTableWidgetItem()
      item_img_origin.setData(QtCore.Qt.DecorationRole, QtGui.QPixmap.fromImage(db_man.bytes_a_imagen(captura.imagen_original).scaled(150, 150)))
      item_observaciones = QtGui.QTableWidgetItem("%s" % (captura.observaciones))

      item_id_individuo.setFlags(item_id_individuo.flags() & ~QtCore.Qt.ItemIsEditable)
      item_id.setFlags(item_id.flags() & ~QtCore.Qt.ItemIsEditable)

      self.insertRow(i)
      self.verticalHeader().resizeSection(i, 150)
      self.setItem(i, 0, item_id_individuo)
      self.setItem(i, 1, item_id)
      self.setItem(i, 2, item_fecha)
      self.setItem(i, 3, item_zona)
      self.setItem(i, 4, item_fotografo)
      self.setItem(i, 5, item_imagen)
      self.setItem(i, 6, item_img_seg)
      self.setItem(i, 7, item_img_trans)
      self.setItem(i, 8, item_img_origin)
      self.setItem(i, 9, item_observaciones)
      i += 1
    self.setSortingEnabled(True)
    self.setHorizontalHeaderLabels(self.table_header_labels)
    export_csv(self)

class WidgetComboBoxList(QtGui.QWidget):

  def __init__(self, list, parent = None):
    super(WidgetComboBoxList, self).__init__(parent)
    self.parent = parent
    self.list = list
    self.iniciar_ui()

  def iniciar_ui(self):
    self.items = QtGui.QComboBox()
    self.items.addItem("...")
    for item in self.list:
        self.items.addItem(item)
    layout = QtGui.QHBoxLayout()
    layout.addWidget(self.items)
    self.setLayout(layout)

class WidgetComboBoxType(QtGui.QWidget):

  def __init__(self, type, parent = None):
    super(WidgetComboBoxType, self).__init__(parent)
    self.parent = parent
    self.type = type
    self.iniciar_ui()

  def iniciar_ui(self):
    self.items = QtGui.QComboBox()
    self.items.addItem("...", -1)
    for item in ManagerBase().all(self.type):
        self.items.addItem(item.description(), item.id)
    layout = QtGui.QHBoxLayout()
    layout.addWidget(self.items)
    self.setLayout(layout)


class WidgetComboBoxExtensible(QtGui.QWidget):

  add_item_widgets = {Fotografo: WidgetAgregarFotografo,
                      Zona: WidgetAgregarZona
  }

  def __init__(self, type, parent = None):
    super(WidgetComboBoxExtensible, self).__init__(parent)
    self.parent = parent
    self.type = type
    self.iniciar_ui()

  def iniciar_ui(self):
    self.hBox = QtGui.QHBoxLayout()
    self.load_items()
    self.add_item_button = QtGui.QPushButton("+")
    self.add_item_button.clicked.connect(self.add_item)
    self.add_item_button.setMaximumWidth(30)
    self.hBox.addWidget(self.add_item_button)
    self.setLayout(self.hBox)

  def load_items(self):
    items = self.hBox.takeAt(0)
    if items != None:
      items.widget().deleteLater()
    self.items = QtGui.QComboBox()
    for item in ManagerBase().all(self.type):
        self.items.addItem(item.description(), item.id)
    self.hBox.insertWidget(0, self.items)

  def extend(self, element):
    self.load_items()
    self.items.setCurrentIndex(self.items.findText(element.description()))

  def add_item(self):
    self.add_item_widget = self.add_item_widgets[self.type](widget_extend = self)
    self.add_item_widget.show()


class WidgetAgregarCapturaConBotonGuardar(QtGui.QWidget):

  def __init__(self, parent = None):
    super(WidgetAgregarCapturaConBotonGuardar, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()


  def iniciar_ui(self):
    qHLayout = QtGui.QHBoxLayout()

    self.setLayout(qHLayout)

    self.setWindowTitle("Formulario para agregar nueva captura")

    botonGuardar = QtGui.QPushButton("Guardar")

    self.widgetCaptura = WidgetAgregarCaptura(self.parent)

    botonGuardar.clicked.connect(self.widgetCaptura.guardar)

    qHLayout.addWidget(self.widgetCaptura)
    qHLayout.addWidget(botonGuardar)

    self.show()

class WidgetNuevaCaptura(QtGui.QWidget):

  def __init__(self, parent = None):
    super(WidgetNuevaCaptura, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()

  def guardar(self):
    self.widgetAgregarCaptura.guardar()
    self.close()

  def iniciar_ui(self):

    qHLayout = QtGui.QHBoxLayout()
    self.setLayout(qHLayout)
    self.setWindowFlags(QtCore.Qt.Window)
    self.setWindowTitle("Formulario para agregar nueva captura")

    botonGuardar = QtGui.QPushButton("Guardar")

    self.widgetAgregarCaptura = WidgetAgregarCaptura(self.parent)
    botonGuardar.clicked.connect(self.guardar)
    qHLayout.addWidget(self.widgetAgregarCaptura)
    qHLayout.addWidget(botonGuardar)


    self.show()



class WidgetNuevoIndividuo(QtGui.QWidget):

  def __init__(self, parent = None):
    super(WidgetNuevoIndividuo, self).__init__(parent)
    self.parent = parent
    self.iniciar_ui()

  def guardar(self):
    db_man = ManagerBase()
    sexo = self.sexo
    observaciones_individuo = self.texto.toPlainText()
    try:
      individuo_id = db_man.crear_individuo_ret_id(sexo, observaciones_individuo)
      self.widgetAgregarCaptura.guardar(individuo_id)
      self.close()
    except:
      print("error!")
      traceback.print_exc()


  def iniciar_ui(self):

    self.sexo = sexo[2]
    self.labeln = QtGui.QLabel("Sexo: ")
    self.labelz = QtGui.QLabel("Observaciones: ")
    self.radioMasculino = MyRadioButtonSexo(sexo[0], self)
    self.radioFemenino = MyRadioButtonSexo(sexo[1], self)
    self.radioNoDeterminado = MyRadioButtonSexo(sexo[2], self)
    self.radioNoDeterminado.setChecked(True)
    self.texto = QtGui.QTextEdit()

    qHLayout = QtGui.QHBoxLayout()
    qgridLayout = QtGui.QGridLayout()

    qHLayout.addLayout(qgridLayout)

    qgridLayout.addWidget(QtGui.QLabel("INDIVIDUO"), 0, 0)
    qgridLayout.addWidget(self.labeln, 1, 0)
    qgridLayout.addWidget(self.radioMasculino, 1, 1)
    qgridLayout.addWidget(self.radioFemenino, 2, 1)
    qgridLayout.addWidget(self.radioNoDeterminado, 3, 1)
    qgridLayout.addWidget(self.labelz, 4, 0)
    qgridLayout.addWidget(self.texto, 4, 1)

    self.setLayout(qHLayout)
    self.setWindowFlags(QtCore.Qt.Window)
    #self.setGeometry(300, 300, 600, 400)
    self.setWindowTitle("Formulario para agregar nuevo individuo")

    botonGuardar = QtGui.QPushButton("Guardar")

    botonGuardar.clicked.connect(self.guardar)

    self.widgetAgregarCaptura = WidgetAgregarCaptura(self.parent)
    qHLayout.addWidget(self.widgetAgregarCaptura)
    qHLayout.addWidget(botonGuardar)


    self.show()

def main():
  app = QtGui.QApplication(sys.argv)
  #ex = WidgetIndividuo()
  from db import ManagerBase
  ex = WidgetListaIndividuosStandaloneScroleable(ManagerBase().all_individuos())
  ex.show()
  sys.exit(app.exec_())

if __name__ == '__main__':
    main()
