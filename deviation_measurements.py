#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Импортируем необходимые модули
import math
import string
from gimpfu import *
from array import array
import getpass

SIZE_IN_PIXELS = 0
SIZE_IN_POINTS = 1


def write_to_file(file_name, line):
    try:
        with open(file_name, 'a') as file: 
            file.writelines(line + '\n') 
    except Exception:
      gimp.message('Can not write results to '+ file_name + '\n Restart Gimp in admin mode and close the file in other programs')


#https://github.com/VegetarianZombie/gimp-text-outliner/blob/bc4ffbdebd06e8610144767c4d28111660c5b730/text-outliner.py
# Adds a new layer beneath the given layer. Return value is the new layer
def add_new_layer_beneath(image, layer):
	# Get the layer position.
	pos = 0;
	for i in range(len(image.layers)):
		if(image.layers[i] == layer):
			pos = i
	
	if image.base_type is RGB:
		type = RGBA_IMAGE
	else:
		type = GRAYA_IMAGE
		
	# Add a new layer below the selected one
	new_layer = gimp.Layer(image, "text outline", image.width, image.height, type, 100, NORMAL_MODE)
	image.add_layer(new_layer, pos+1)	
	return new_layer

# Selects the contents of the given layer, then grows it by "thickness"
# and feathers it by "feather" pixels
def create_selection(image, layer, thickness, feather):
	# Select the text
	pdb.gimp_selection_layer_alpha(layer)
	
	# Grow the selection
	pdb.gimp_selection_grow(image, thickness)
	
	# Feather it
	if (feather > 0):
		pdb.gimp_selection_feather(image, feather)		


# Fills the current selection using the given color, painting onto the
# given layer.
def fill_selection(layer, color):
	# Cache existing foreground color
	old_fg = pdb.gimp_palette_get_foreground()	
	# Set foreground color
	pdb.gimp_palette_set_foreground(color)	
	pdb.gimp_bucket_fill(layer, 0, 0, 100, 0, 0, 1, 1)	
	# Restore cached foreground color
	pdb.gimp_palette_set_foreground(old_fg)	


def add_text_outline(image, layer, thickness, feather):
	gimp.progress_init("Drawing outline around text")
	new_layer = add_new_layer_beneath(image, layer)
	gimp.progress_update(33)
	create_selection(image, layer, thickness, feather)
	gimp.progress_update(66)
	
	fill_selection(new_layer, gimpcolor.RGB(0,0,0))	
	gimp.progress_update(100)
	pdb.gimp_selection_none(image)
# https://github.com/VegetarianZombie/gimp-text-outliner/blob/bc4ffbdebd06e8610144767c4d28111660c5b730/text-outliner.py


# https://github.com/eib/gimp-plugins/blob/8c8a2ef70975d793685ec7fc5de743f3ebcadb0a/add_watermark_text.py
def add_text(image, text, points = 100, antialias = False, letter_spacing = -3, fontname = "Sans", color = (255, 255, 255)):
    x = 0
    y = 0
    border = -1
    watermark_shadow_opacity = 60.0

    #create text-layer (adds it to the image)
    text_layer = pdb.gimp_text_fontname(image, None, x, y, text, border, antialias, points, SIZE_IN_POINTS, fontname)
    
    layer_margins = 5
    x = image.width/2 
    y = image.height/2 - text_layer.height - layer_margins #bottom
    
    pdb.gimp_text_layer_set_color(text_layer, color)
    pdb.gimp_text_layer_set_text(text_layer, text)
    pdb.gimp_item_set_name(text_layer, "text")
    pdb.gimp_layer_set_offsets(text_layer, x, y)
    pdb.gimp_text_layer_set_letter_spacing(text_layer, letter_spacing)
    
    # add shadow
    thickness = 2 
    feather = 2
    add_text_outline(image, text_layer, thickness, feather)


# https://github.com/iwabuchiken/WS_Others.Art-deprecated.20190617_174059-/blob/fe2dad57431304497cc69bcaccb14a5004dea72d/JVEMV6/46_art/2_image-prog/1_gimp/4_/plugin_2_1_4.py
def draw_pencil_lines(drawable, lines, width = 10, color = gimpcolor.RGB(0,0,0)):
    pdb.gimp_context_set_foreground(color)
    pdb.gimp_context_set_brush_size(width)
    #pdb.gimp_paintbrush_default(drawable, len(lines), lines)
    pdb.gimp_pencil(drawable, len(lines), lines)
  
def newline(x1,y1,x2,y2):
	return [x1,y1,x1,y1,x1,y1,x2,y2,x2,y2,x2,y2];

def add_deviation_layout(image, drawable, real_size):
  pdb.gimp_context_push()
  #undo-start
  pdb.gimp_image_undo_group_start(image)
  
  # get info from vectors
  vectors = pdb.gimp_image_get_active_vectors(image)
  strokes_num, strokes = pdb.gimp_vectors_get_strokes(vectors)

  str0_size = pdb.gimp_vectors_stroke_get_length(vectors, strokes[0], 1)
  str1_size = pdb.gimp_vectors_stroke_get_length(vectors, strokes[1], 1)

  if (str0_size >= str1_size):
      hypotenuse_stroke = strokes[0]
      photo_size = str1_size
  else:
      hypotenuse_stroke = strokes[1]
      photo_size = str0_size

  stroke_type, n_points, cpoints, closed = pdb.gimp_vectors_stroke_get_points(vectors, hypotenuse_stroke)
  c_len = len(cpoints)
  
  x = [cpoints[0], cpoints[c_len-2]]
  y = [cpoints[1], cpoints[c_len-1]]

  pencil_width = int (100 * photo_size /image.width)
  if pencil_width < 1:
      pencil_width = 1
  drawable = image.new_layer('hypotenuse')
  draw_pencil_lines(drawable, newline(x[0], y[0], x[1], y[1]), width = pencil_width, color = gimpcolor.RGB(0,255,0))

  # CHECK !!!
  x.sort(reverse = False)
  y.sort(reverse = True)

  drawable = image.new_layer('small_leg')
  draw_pencil_lines(drawable, newline(x[0], y[0], x[1], y[0]), width = pencil_width, color = gimpcolor.RGB(255,0,0))
  drawable = image.new_layer('big_leg')
  draw_pencil_lines(drawable, newline(x[1], y[1], x[1], y[0]), width = pencil_width, color = gimpcolor.RGB(0,255,0))
  
  target_photo_size = float(abs(float(cpoints[0]) - cpoints[c_len-2]))
  target_real_size = (real_size / float(photo_size)) * target_photo_size
  
  add_text(image, str(round(target_real_size, 1)) + ' mm.') 
  img_name = pdb.gimp_image_get_filename(image)
  
  write_to_file(r"C:\test.csv", img_name + ';'+ str(target_real_size))
  #pdb.gimp_image_remove_vectors(image, vectors)

  pdb.gimp_displays_flush()
  # undo-end
  pdb.gimp_image_undo_group_end(image)
  pdb.gimp_context_pop()

def get_angle (p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    dX = x2 - x1
    dY = y2 - y1
    rads = math.atan2(-dY, dX) #wrong for finding angle/declination?
    return math.degrees(rads)


def add_angle_layout(image, drawable):
  pdb.gimp_context_push()
  #undo-start
  pdb.gimp_image_undo_group_start(image)

   #get info from vectors
  vectors = pdb.gimp_image_get_active_vectors(image)
  strokes_num, strokes = pdb.gimp_vectors_get_strokes(vectors)
  stroke_type, n_points, cpoints, closed = pdb.gimp_vectors_stroke_get_points(vectors, strokes[0])
  
  gimp.message(str(len(cpoints)))
  c_len = len(cpoints)
  x = [cpoints[0], cpoints[c_len-2]]
  y = [cpoints[1], cpoints[c_len-1]]

  x1y1 = [cpoints[0], cpoints[1]]
  x2y2 = [cpoints[c_len-2], cpoints[c_len-1]]

  pencil_width = int (1000 /image.width)
  if pencil_width < 1:
      pencil_width = 1

  drawable = image.new_layer('hypotenuse')
  draw_pencil_lines(drawable, newline(x1y1[0], x1y1[1], x2y2[0], x2y2[1]), width = pencil_width, color = gimpcolor.RGB(255,0,0))
  angle = abs(90 - abs(get_angle([x2y2[0], x1y1[1]], [x1y1[0], x2y2[1]])))

  drawable = image.new_layer('big_leg')
  if (x2y2[1] < x1y1[1]):
      draw_pencil_lines(drawable, newline(x2y2[0], x2y2[1], x2y2[0], x1y1[1]), width = pencil_width, color = gimpcolor.RGB(0,255,0))
  else:
      draw_pencil_lines(drawable, newline(x1y1[0], x1y1[1], x1y1[0], x2y2[1]), width = pencil_width, color = gimpcolor.RGB(0,255,0))
  # draw_pencil_lines(drawable, newline(x[0], y[0], x[0], y[1]), width = pencil_width, color = gimpcolor.RGB(0,255,0))


  add_text(image, str(round(angle, 2)) + '°') 
  img_name = pdb.gimp_image_get_filename(image)
  write_to_file(r"C:\test.csv", img_name + ';'+ str(round(angle, 2)))

  gimp.message(str(x))
  gimp.message(str(y))

  pdb.gimp_displays_flush()
  # undo-end
  pdb.gimp_image_undo_group_end(image)
  pdb.gimp_context_pop()


# Регистрируем функции в PDB
register(
          "python-fu-add-deviation-layout", # Имя регистрируемой функции
          "Добавление размеров объекта", # Информация о дополнении
          "Позволяет измерить объект, используя какой-то известный размер другого объекта на фото. Наносит разметку с размером на изображение и записывает результат в файл", # Короткое описание выполняемых скриптом действий
          "Lena Kolos", # Информация об авторе
          "Lena Kolos (koloslena97@gmail.com)", # Информация о копирайте (копилефте?)
          "22.03.2021", # Дата изготовления
          "Измерение отклонений объектов", # Название пункта меню, с помощью которого дополнение будет запускаться
          "*", # Типы изображений с которыми может работать дополнение
          [
              (PF_IMAGE, "image", "Исходное изображение", None), # Указатель на изображение
              (PF_DRAWABLE, "drawable", "Исходный слой", None), # Указатель на слой
              (PF_FLOAT, "real_size", "Реальный размер объекта (mm.)", "255"), # Реальный размер объекта  в милиметрах
          ],
          [], # Список переменных которые вернет дополнение
          add_deviation_layout, menu="<Image>/Deviation measurements/") # Имя исходной функции и меню в которое будет помещён пункт запускающий дополнение

register(
          "python-fu-add-angle-layout", # Имя регистрируемой функции
          "Добавление размеров объекта", # Информация о дополнении
          "Позволяет измерить объект, используя какой-то известный размер другого объекта на фото. Наносит разметку с размером на изображение и записывает результат в файл", # Короткое описание выполняемых скриптом действий
          "Lena Kolos", # Информация об авторе
          "Lena Kolos (koloslena97@gmail.com)", # Информация о копирайте (копилефте?)
          "22.03.2021", # Дата изготовления
          "Измерение углов", # Название пункта меню, с помощью которого дополнение будет запускаться
          "*", # Типы изображений с которыми может работать дополнение
          [
              (PF_IMAGE, "image", "Исходное изображение", None), # Указатель на изображение
              (PF_DRAWABLE, "drawable", "Исходный слой", None), # Указатель на слой
          ],
          [], # Список переменных которые вернет дополнение
          add_angle_layout, menu="<Image>/Deviation measurements/") # Имя исходной функции и меню в которое будет помещён пункт запускающий дополнение

# Запускаем скрипт
main()