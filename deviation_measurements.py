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
def add_new_layer_beneath(image, layer, parent = None):
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
	new_layer = add_layer_into_group(image, 'text outline',  parent, pos + 2)
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


def add_text_outline(image, layer, thickness, feather, parent):
	new_layer = add_new_layer_beneath(image, layer, parent)
	create_selection(image, layer, thickness, feather)
	fill_selection(new_layer, gimpcolor.RGB(0,0,0))	
	pdb.gimp_selection_none(image)
# https://github.com/VegetarianZombie/gimp-text-outliner/blob/bc4ffbdebd06e8610144767c4d28111660c5b730/text-outliner.py


# https://github.com/eib/gimp-plugins/blob/8c8a2ef70975d793685ec7fc5de743f3ebcadb0a/add_watermark_text.py
def add_text(image, text, parent, points = 100, pos = [0,0], antialias = False, letter_spacing = -3, fontname = "Sans", color = (255, 255, 255)):
    #create text-layer (adds it to the image)
    border = -1
    text_layer = pdb.gimp_text_fontname(image, add_layer_into_group(image, 'text', parent, pos = 0), 
                                        pos[0], pos[1], text, border, antialias, points, SIZE_IN_POINTS, fontname)
    
    pdb.gimp_text_layer_set_color(text_layer, color)
    pdb.gimp_text_layer_set_text(text_layer, text)
    pdb.gimp_item_set_name(text_layer, "text")
    pdb.gimp_text_layer_set_letter_spacing(text_layer, letter_spacing)
    # add outline
    thickness = 2 
    feather = 2
    add_text_outline(image, text_layer, thickness, feather, parent)


# https://github.com/iwabuchiken/WS_Others.Art-deprecated.20190617_174059-/blob/fe2dad57431304497cc69bcaccb14a5004dea72d/JVEMV6/46_art/2_image-prog/1_gimp/4_/plugin_2_1_4.py
def draw_pencil_lines(drawable, lines, width = 10, color = gimpcolor.RGB(0,0,0)):
    pdb.gimp_context_set_foreground(color)
    pdb.gimp_context_set_brush_size(width)
    pdb.gimp_pencil(drawable, len(lines), lines)
  

def newline(x1,y1,x2,y2):
	return [x1,y1,x1,y1,x1,y1,x2,y2,x2,y2,x2,y2];


def add_layer_into_group(image, layer_name, group, pos = 1):
  drawable = gimp.Layer(image, layer_name, image.width, image.height, RGBA_IMAGE, 100, NORMAL_MODE)
  pdb.gimp_image_insert_layer(image, drawable, group, pos)
  return drawable


def add_deviation_layout(image, drawable, real_size):
  pdb.gimp_context_push()
  #undo-start
  pdb.gimp_image_undo_group_start(image)
  
  # get info from vectors
  vectors = pdb.gimp_image_get_active_vectors(image)
  strokes_num, strokes = pdb.gimp_vectors_get_strokes(vectors)

  # a longer stroke is hypotenuse, other is object size mark used to find out reality/photo scale factor 
  str0_size = pdb.gimp_vectors_stroke_get_length(vectors, strokes[0], 1)
  str1_size = pdb.gimp_vectors_stroke_get_length(vectors, strokes[1], 1)

  if (str0_size >= str1_size):
      hypotenuse_stroke = strokes[0]
      photo_size = str1_size
  else:
      hypotenuse_stroke = strokes[1]
      photo_size = str0_size

  # draw hypotenuse using coordinates of stroke points
  stroke_type, n_points, cpoints, closed = pdb.gimp_vectors_stroke_get_points(vectors, hypotenuse_stroke)
  c_len = len(cpoints)

  start_pos = [cpoints[0], cpoints[1]]
  end_pos = [cpoints[c_len-2], cpoints[c_len-1]]

  group = pdb.gimp_layer_group_new(image)
  pdb.gimp_item_set_name(group, 'deviation_layout')
  pdb.gimp_image_insert_layer(image, group, None, 0)

  pencil_width = int (10 / photo_size)
  if pencil_width < 1:
      pencil_width = 1
  
  draw_pencil_lines(add_layer_into_group(image, 'hypotenuse', group), 
                    newline(start_pos[0], start_pos[1], end_pos[0], end_pos[1]), 
                    width = pencil_width, color = gimpcolor.RGB(0,255,0))

  draw_pencil_lines(add_layer_into_group(image, 'small_leg', group), 
                    newline(start_pos[0], end_pos[1], end_pos[0], end_pos[1]), 
                    width = pencil_width, color = gimpcolor.RGB(255,0,0))

  draw_pencil_lines(add_layer_into_group(image, 'small_leg_', group), 
                    newline(start_pos[0], start_pos[1], end_pos[0], start_pos[1]), 
                    width = pencil_width, color = gimpcolor.RGB(255,0,0))

  draw_pencil_lines(add_layer_into_group(image, 'big_leg', group), 
                    newline(start_pos[0], start_pos[1], start_pos[0], end_pos[1]), 
                    width = pencil_width, color = gimpcolor.RGB(0,255,0))

  draw_pencil_lines(add_layer_into_group(image, 'big_leg_', group), 
                    newline(end_pos[0], start_pos[1], end_pos[0], end_pos[1]), 
                    width = pencil_width, color = gimpcolor.RGB(0,255,0))

  target_photo_size = float(abs(float(cpoints[0]) - cpoints[c_len-2]))
  scale_factor = (real_size / float(photo_size)) #reality/photo scale factor
  target_real_size = scale_factor * float(target_photo_size)
  
  add_text(image, str(round(target_real_size, 1)) + ' mm.', group, 
           pos = [int(float(start_pos[0]) + end_pos[0])/2, int(float(start_pos[1]) + end_pos[1])/2],
           points = int (0.05 * image.width))
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
    rads = math.atan2(-dY, dX) 
    return math.degrees(rads)


def add_angle_layout(image, drawable):
  pdb.gimp_context_push()
  #undo-start
  pdb.gimp_image_undo_group_start(image)

  #get info from vectors
  vectors = pdb.gimp_image_get_active_vectors(image)
  strokes_num, strokes = pdb.gimp_vectors_get_strokes(vectors)
  stroke_type, n_points, cpoints, closed = pdb.gimp_vectors_stroke_get_points(vectors, strokes[0])
  
  # draw hypotenuse using coordinates of stroke points
  c_len = len(cpoints)
  start_pos = [cpoints[0], cpoints[1]]
  end_pos = [cpoints[c_len-2], cpoints[c_len-1]]

  pencil_width = int (1000 /image.width)
  if pencil_width < 1:
      pencil_width = 1

  group = pdb.gimp_layer_group_new(image)
  pdb.gimp_item_set_name(group, 'angle_layout')
  pdb.gimp_image_insert_layer(image, group, None, 0)

  draw_pencil_lines(add_layer_into_group(image, 'hypotenuse', group), 
                    newline(start_pos[0], start_pos[1], end_pos[0], end_pos[1]), 
                    width = pencil_width, color = gimpcolor.RGB(255,0,0))
  angle = abs(90 - abs(get_angle([end_pos[0], start_pos[1]], [start_pos[0], end_pos[1]])))
  
  # get position to draw vertical line
  start_line_pos = start_pos
  end_line_pos = end_pos
  if (end_pos[1] < start_pos[1]):
      start_line_pos = end_pos
      end_line_pos = start_pos

  draw_pencil_lines(add_layer_into_group(image, 'vertical_line', group), 
                    newline(start_line_pos[0], start_line_pos[1], start_line_pos[0], end_line_pos[1]), 
                    width = pencil_width, color = gimpcolor.RGB(0,255,0))

  add_text(image, str(round(angle, 1)) + '°', group,
           pos = [int(float(start_pos[0]) + end_pos[0])/2, int(float(start_pos[1]) + end_pos[1])/2],
           points = int (0.05 * image.width))
 
  img_name = pdb.gimp_image_get_filename(image)
  write_to_file(r"C:\test.csv", img_name + ';'+ str(round(angle, 1)))

  #pdb.gimp_image_remove_vectors(image, vectors)

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