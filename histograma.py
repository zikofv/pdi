#!/usr/bin/env python
from __future__ import division
from imagen import ImagenArchivo
import matplotlib.pyplot as plt
import numpy as np
import colorsys
import sys

def cargar(filename):
  img = ImagenArchivo(filename)
  print "mode: %s" % img.mode
  print "size: %s" % str(img.size)
  return img

def crear_histograma(img):
  ancho, alto = img.size

  histo = []

  for x in range(ancho):
    for y in range(alto):
      r, g, b = img.getpixel((x, y))
      if not (r == 0 and g == 0 and b == 0):
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        histo.append(h)

  plt.hist(histo, bins=np.arange(0., 1., 0.001))
  plt.show()

if __name__ == '__main__':
  if len(sys.argv) <= 1:
    print "Uso:"
    print "%s imagen_entrada.jpg" % sys.argv[0]
  img = cargar(sys.argv[1])
  crear_histograma(img)
