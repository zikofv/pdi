#! /usr/bin/env python

"""
Implementacion de deteccion de bordes
"""

from __future__ import division
import sys
import math
from filtros import  *
from imagen import ImagenArchivo, ImagenVacia


def cargar(filename):
  img = ImagenArchivo(filename)
  print "mode: %s" % img.mode
  print "size: %s" % str(img.size)
  return img

class Transformador(object):

  def recorrer_imagen(self, ancho, alto):
    """
    genera tuplas (x,y) entre 0..ancho y 0..alto
    """
    for x in range(ancho):
      for y in range(alto):
        yield (x,y)

  def es_borde(self, x, y, ancho, alto):
    return not ((0 < x < ancho-1) and (0 < y < alto-1))

  def aplicar(self, algoritmo, img):
    """
    Aplica el filtro a la imagen
    """
    ret = ImagenVacia(img.mode, img.size)
    ancho, alto = img.size
    for x,y in self.recorrer_imagen(ancho, alto):
      if not self.es_borde(x, y, ancho, alto):
        algoritmo.aplicar_en_pixel(x, y, img, ret)
    return ret


class Algoritmo(object):
  def aplicar_en_pixel(self, x, y, img, ret):
    raise NotImplementedError

class AlgoritmoRuido(Algoritmo):
  def aplicar_en_pixel(self, x, y, img, ret, filtro):
    """
    Aplica el filtro en el pixel dado por img(x,y)
    devuelve la imagen ret con el pixel x,y modificado
    total = filtro.ancho * filtro.ancho
    """
    sumar = 0.0
    sumag = 0.0
    sumab = 0.0
    for columna, fila, valor in filtro:
      r, g, b = img.getpixel((x+columna, y+fila))
      sumar += valor * r
      sumag += valor * g
      sumab += valor * b
    ret.putpixel((x, y), (int(sumar/total), int(sumag/total),int(sumab/total)))

class AlgoritmoConvulsion(Algoritmo):
  def __init__(self, filtro):
    self.filtro = filtro

  def aplicar_en_pixel(self, x, y, img, ret):
    """
    Devuelve la imagen ret con el pixel x,y modificado. Usa el filtro con la imagen de origen img.
    ret(x,y) = f(filtro, img)
    minimo: el minimo valor posible de la convulsion
    maximo: el maximo valor posible de la convulsion
    Tenemos que dividir por maximo * minimo y luego multiplicar por 255
    """
    minimo = abs(self.filtro.get_minimo()) 
    maximo = abs(self.filtro.get_maximo())
    total = minimo + maximo
    sumar = 0.0
    sumag = 0.0
    sumab = 0.0
    for columna, fila, valor in self.filtro:
      if valor == 0: continue
      r, g, b = img.getpixel((x+columna, y+fila))
      sumar += valor * r
      sumag += valor * g
      sumab += valor * b
    value = (
        int(((sumar + minimo) / total) * 256),
        int(((sumag + minimo) / total) * 256),
        int(((sumab + minimo) / total) * 256),
    )
    ret.putpixel((x, y), value)

class AlgoritmoRoberts(Algoritmo):
  """
  operador de resaltado de bordes de Roberts
  ver tp3 ejercicio 1
  usamos solo el canal R. Asumimos que la img esta en escala de grises.
  """
  def aplicar_en_pixel(self, x, y, img, ret):

    #maximo es sqrt(255**2 + 255 ** 2)
    maximo = 360.62445840513925
    a = math.pow(img.getpixel((x,y))[0] - img.getpixel((x+1,y+1))[0], 2)
    b = math.pow(img.getpixel((x,y+1))[0] - img.getpixel((x+1,y))[0], 2)
    c = math.sqrt(a + b) / maximo
    value = int(c * 255) 
    ret.putpixel((x,y), (value, value, value))

class AlgoritmoMultiplesFiltros(Algoritmo):
  """
  Este algoritmo admite una serie de filtros que luego aplica.
  """

  def __init__(self, filtros_list):
    """
    filtros_list: lista de filtros a aplicar
    """
    self.filtros_list = filtros_list
    maximo = 0
    minimo = 0
    for filtro in self.filtros_list:
      maximo += filtro.get_maximo() 
      minimo += filtro.get_minimo()
    self.intervalo = maximo #- minimo + 1

  def aplicar_en_pixel(self, x, y, img, ret):
    """
    Aplica cada uno de los filtros. Luego suma el resultado de aplicar cada uno, lo normaliza y lo utiliza como
    valor de gris en la imagen de destino.
    """
    gradiente = 0

    for filtro in self.filtros_list:
      gr = 0
      for col, fil, val in filtro:
        gr += img.get_red_pixel((x+col, y+fil)) * val
      gradiente += abs(gr)

    #value = int((gradiente / self.intervalo ) * 255)
    value = int((gradiente / (8*5*255) ) * 255)
    ret.putpixel((x,y), (value,value,value))

class AlgoritmoGradiente(Algoritmo):

  def __init__(self, filtrox, filtroy):
    self.filtrox = filtrox
    self.filtroy = filtroy

  def aplicar_en_pixel(self, x, y, img, ret):
    gx = 0.0
    gy = 0.0
    maximo = math.sqrt(2 * math.pow(4 * 255, 2))
    maximoy = self.filtroy.get_maximo()

    for col, fil, val in self.filtrox:
      gx += img.getpixel((x+col, y+fil))[0] * val

    for col, fil, val in self.filtroy:
      gy += img.getpixel((x+col, y+fil))[0] * val

    value = math.sqrt(math.pow(gx, 2) + math.pow(gy, 2))
    value = int((value / maximo) * 255) 
    ret.putpixel((x,y), (value,value,value))

if __name__ == "__main__":

  img = cargar(sys.argv[1])
  #img.show()
  lista_filtros = []
  for i in PREWITT_LIST:
    lista_filtros.append(Filtro(i, 3))
  algo = AlgoritmoMultiplesFiltros(lista_filtros)
  trans = Transformador()
  img2 = trans.aplicar(algo, img)
  #img2.show()
  img2.save("salida.bmp")