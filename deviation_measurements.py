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


# Fills the current selection using the given colour, painting onto the
# given layer.
def fill_selection(layer, colour):
	# Cache existing foreground colour
	old_fg = pdb.gimp_palette_get_foreground()	
	# Set foreground colour
	pdb.gimp_palette_set_foreground(colour)	
	pdb.gimp_bucket_fill(layer, 0, 0, 100, 0, 0, 1, 1)	
	# Restore cached foreground colour
	pdb.gimp_palette_set_foreground(old_fg)	


def add_text_outline(image, layer, thickness, feather):
	gimp.progress_init("Drawing outline around text")
	new_layer = add_new_layer_beneath(image, layer)
	gimp.progress_update(33)
	create_selection(image, layer, thickness, feather)
	gimp.progress_update(66)
	colour = pdb.gimp_context_get_foreground()
	fill_selection(new_layer, colour)	
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
    pdb.gimp_item_set_name(text_layer, "Watermark")
    pdb.gimp_layer_set_offsets(text_layer, x, y)
    pdb.gimp_text_layer_set_letter_spacing(text_layer, letter_spacing)
    
    # add shadow
    thickness = 2 
    feather = 2
    add_text_outline(image, text_layer, thickness, feather)


# https://github.com/iwabuchiken/WS_Others.Art-deprecated.20190617_174059-/blob/fe2dad57431304497cc69bcaccb14a5004dea72d/JVEMV6/46_art/2_image-prog/1_gimp/4_/plugin_2_1_4.py
def draw_pencil_lines(drawable, lines, width = 10, color = gimpcolor.RGB(39,221,65)):
    pdb.gimp_context_set_foreground(color)
    pdb.gimp_context_set_brush_size(width)
    #pdb.gimp_paintbrush_default(drawable, len(lines), lines)
    pdb.gimp_pencil(drawable, len(lines), lines)
  
def newline(x1,y1,x2,y2):
	return [x1,y1,x1,y1,x1,y1,x2,y2,x2,y2,x2,y2];

def add_colored_border(image, drawable, real_size, photo_size, border_color):
  pdb.gimp_context_push()
  #undo-start
  pdb.gimp_image_undo_group_start(image)
  
  # get info from vectors
  vectors = pdb.gimp_image_get_active_vectors(image)
  strokes_num, strokes = pdb.gimp_vectors_get_strokes(vectors)
  stroke_type, n_points, cpoints, closed = pdb.gimp_vectors_stroke_get_points(vectors, strokes[0])
  c_len = len(cpoints)

  draw_pencil_lines(drawable, newline(cpoints[0], cpoints[1], cpoints[c_len-2], cpoints[c_len-1]))
  photo_size = pdb.gimp_vectors_stroke_get_length(vectors, strokes[1], 1)

  target_photo_size = float(abs(cpoints[0] - cpoints[c_len-2]))
  target_real_size = (real_size / float(photo_size)) * target_photo_size
  
  #pdb.gimp_image_remove_vectors(image, vectors)

  file_name = pdb.gimp_image_get_filename(image)
  add_text(image, str(round(target_real_size, 1)) + ' mm.') 
  with open(r"C:\test.csv", 'a') as file: 
      file.writelines(file_name + ';'+ str(target_real_size) + '\n') 
 
  pdb.gimp_displays_flush()
  # undo-end
  pdb.gimp_image_undo_group_end(image)
  pdb.gimp_context_pop()

# Регистрируем функцию в PDB
register(
          "python-fu-add-colored-border", # Имя регистрируемой функции
          "Добавление цветной рамки к изображению", # Информация о дополнении
          "Рисует вокруг изображения рамку заданного цвета и заданной ширины", # Короткое описание выполняемых скриптом действий
          "Lena Kolos", # Информация об авторе
          "Lena Kolos (koloslena97@gmail.com)", # Информация о копирайте (копилефте?)
          "22.03.2021", # Дата изготовления
          "Измерения отклонений подвесок", # Название пункта меню, с помощью которого дополнение будет запускаться
          "*", # Типы изображений с которыми может работать дополнение
          [
              (PF_IMAGE, "image", "Исходное изображение", None), # Указатель на изображение
              (PF_DRAWABLE, "drawable", "Исходный слой", None), # Указатель на слой
              (PF_INT, "real_size", "Реальный размер объекта (mm.)", "255"), # Реальный размер объекта  в милиметрах
              (PF_INT, "photo_size", "Размер объекта на фото в пикселях (точки растра)", "10"), # Размер объекта на фото в пикселях (точки растра)
              (PF_COLOR, "border_color",  "Цвет разметки", (39,221,65)) # Цвет разметки
              
          ],
          [], # Список переменных которые вернет дополнение
          add_colored_border, menu="<Image>/Deviation measurements/") # Имя исходной функции и меню в которое будет помещён пункт запускающий дополнение

# Запускаем скрипт
main()