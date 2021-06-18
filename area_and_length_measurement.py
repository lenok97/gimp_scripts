#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import string
from gimpfu import *
from array import array
import getpass
import os, os.path

SIZE_IN_PIXELS = 0
SIZE_IN_POINTS = 1
HISTOGRAM_VALUE = 0

def write_to_file(file_name, line):
    try:
        with open(file_name, 'a') as file: 
            file.writelines(line + '\n') 
    except Exception:
        gimp.message('Can not write results to '+ file_name 
                     + '\n Restart Gimp in admin mode and close the file in other programs')


#https://github.com/VegetarianZombie/gimp-text-outliner/blob/bc4ffbdebd06e8610144767c4d28111660c5b730/text-outliner.py
# Adds a new layer beneath the given layer. Return value is the new layer
def add_new_layer_beneath(image, layer, name, parent = None):
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
	new_layer = add_layer_into_group(image, name,  parent, pos + 2)
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


def add_outline(image, layer, thickness, feather, parent):
	new_layer = add_new_layer_beneath(image, layer, 'text_outline', parent)
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
    add_outline(image, text_layer, thickness, feather, parent)


def add_layer_into_group(image, layer_name, group, pos = 1):
    drawable = gimp.Layer(image, layer_name, image.width, image.height, RGBA_IMAGE, 100, NORMAL_MODE)
    pdb.gimp_image_insert_layer(image, drawable, group, pos)
    return drawable


def finish_execution(image, message):
    gimp.message(message)
    pdb.gimp_image_undo_group_end(image)
    pdb.gimp_context_pop()

 
def stroke_selection(image, drawable, group):
    # set context for stroke
    pdb.gimp_context_set_opacity(90)
    pdb.gimp_context_set_paint_mode(LAYER_MODE_NORMAL)
    pdb.gimp_context_set_stroke_method(STROKE_LINE)
    pdb.gimp_context_set_line_width(2.5)
    # color   gimpcolor.RGB(255,0,0)
    border_layer = add_new_layer_beneath(image, drawable, 'crack_outline', group)
    pdb.gimp_drawable_edit_stroke_selection(border_layer)


# https://github.com/iwabuchiken/WS_Others.Art-deprecated.20190617_174059-/blob/fe2dad57431304497cc69bcaccb14a5004dea72d/JVEMV6/46_art/2_image-prog/1_gimp/4_/plugin_2_1_4.py
def draw_pencil_lines(drawable, lines, width = 10, color = gimpcolor.RGB(0,0,0)):
    pdb.gimp_context_set_foreground(color)
    pdb.gimp_context_set_brush_size(width)
    pdb.gimp_pencil(drawable, len(lines), lines)
  

def newline(x1,y1,x2,y2):
	return [x1,y1,x1,y1,x1,y1,x2,y2,x2,y2,x2,y2];


def paint_scale_line(image, group, scale_factor, units):
    offset = int(2 / scale_factor)
    pdb.gimp_image_resize(image, image.width + offset, image.height + offset, offset, -offset)
    
    background = gimp.Layer(image, 'background', image.width, image.height, RGBA_IMAGE, 100, NORMAL_MODE)
    pdb.gimp_image_insert_layer(image, background, None, 255)
    pdb.gimp_selection_all(image)

    fill_selection(background, gimpcolor.RGB(255,255,255))
    
    color = gimpcolor.RGB(0,0,0)
    line_width = 2
    drawable = gimp.Layer(image, 'vertical_line', image.width, image.height, RGBA_IMAGE, 100, NORMAL_MODE)
    pdb.gimp_image_insert_layer(image, drawable, group, 1)
    x1 = 0
    x2 = 2 / scale_factor
    y = image.height
    while (y > 0):
        draw_pencil_lines(drawable, 
                          newline(x1, y, x2, y), 
                          line_width, color)
        y -= 10 / scale_factor

    drawable = gimp.Layer(image, 'horizontal_line', image.width, image.height, RGBA_IMAGE, 100, NORMAL_MODE)
    pdb.gimp_image_insert_layer(image, drawable, group, 1)
    x = 0
    y1 = image.height
    y2 = image.height - 2 / scale_factor

    add_text(image, str(10) + ' '+ units, group, 
             pos = [0, y1],
             points = int (0.05 * image.width))

    while (x < image.width):
        draw_pencil_lines(drawable, 
                          newline(x, y1, x, y2), 
                          line_width, color)
        x += 10 / scale_factor


def add_area_layout(image, drawable, real_size, units, save_file, log_file):
    pdb.gimp_context_push()
    #undo-start
    pdb.gimp_image_undo_group_start(image)
   # drawable = pdb.gimp_image_merge_visible_layers(image, 0)
    
    temp_layer = add_new_layer_beneath(image, drawable, 'filled_selection')
    fill_selection(temp_layer, gimpcolor.RGB(0,125,125))	
    _, _, _, pixels, _, _ = pdb.gimp_drawable_histogram(temp_layer, HISTOGRAM_VALUE, 0, 1)

   # pdb.gimp_item_delete(temp_layer)

   # pdb.gimp_file_load_layer(image, 'scale_line.png')

    group = pdb.gimp_layer_group_new(image)
    pdb.gimp_item_set_name(group, 'area_layout')
    pdb.gimp_image_insert_layer(image, group, None, 0)
    
    stroke_selection(image, drawable, group)
 
    # get info from vectors
    vectors = pdb.gimp_image_get_active_vectors(image)
    if (vectors == None):
        finish_execution (image,
                          'Не обнаружено векторов. Добавьте вектор по диаметру стойки')
        return

    strokes_num, strokes = pdb.gimp_vectors_get_strokes(vectors)
    if (strokes_num != 1):
        finish_execution (image,
                          'Неверная разметка. Для операции требуетя 1 вектор. На изображении сейчас: '+ str (strokes_num))
        return

    photo_size = pdb.gimp_vectors_stroke_get_length(vectors, strokes[0], 1)
    scale_factor = (real_size / float(photo_size)) #reality/photo scale factor
    gimp.message(str(photo_size)+' '+str(real_size)+' '+str(scale_factor)+' '+str(pixels))
    real_area_size =  float(pixels) * math.pow(scale_factor, 2)

    add_text(image, str(round(real_area_size, 1)) + ' '+ units + '²', group, 
             pos = [0, 0],
             points = int (0.05 * image.width))
    paint_scale_line(image, group, scale_factor, units)

    img_name = pdb.gimp_image_get_filename(image)
  
    ## write header for new file
    #if (not(os.path.exists(log_file))):
    #    write_to_file(log_file, 'img_name;sample_real_size;target_real_size;units')

    #write_to_file(log_file, img_name + ';'+  str(real_size) + ';'
    #              + str(round(target_real_size, 1))+ ';' + units+ '²')
   
    pdb.gimp_displays_flush()

    # undo-end
    finish_execution (image,'Завершено')
    if (save_file):
        merge_and_export(image, img_name, '_deviation')
    #pdb.gimp_image_remove_vectors(image, vectors)


def add_length_layout(image, drawable, real_size, units, save_file, log_file):
    pdb.gimp_context_push()
    #undo-start
    pdb.gimp_image_undo_group_start(image)

    group = pdb.gimp_layer_group_new(image)
    pdb.gimp_item_set_name(group, 'length_layout')
    pdb.gimp_image_insert_layer(image, group, None, 0)
     
    # get info from vectors
    vectors = pdb.gimp_image_get_active_vectors(image)
    if (vectors == None):
        finish_execution (image,
                          'Не обнаружено векторов. Добавьте вектор по диаметру стойки и вдоль объекта')
        return

    strokes_num, strokes = pdb.gimp_vectors_get_strokes(vectors)
    if (strokes_num != 2):
        finish_execution (image,
                          'Неверная разметка. Для операции требуетя 2 вектора. На изображении сейчас: '+ str (strokes_num))
        return

    # first vector is object size mark used to find out reality/photo scale factor 
    photo_size = pdb.gimp_vectors_stroke_get_length(vectors, strokes[0], 1)
    # second vector is extent of object 
    obj_len = pdb.gimp_vectors_stroke_get_length(vectors, strokes[1], 1)
    stroke_type, n_points, cpoints, closed = pdb.gimp_vectors_stroke_get_points(vectors, strokes[1])
    length_layer = add_layer_into_group(image, 'length_line', group)
    c_len = len(cpoints)
    gimp.message(str(cpoints))
    pencil_width = int (1000 /image.width)
    if pencil_width < 1:
        pencil_width = 1
    i = 0
    while i < c_len-8:
        draw_pencil_lines(length_layer, 
                         newline(cpoints[i], cpoints[i+1], cpoints[i+6], cpoints[i+7]), 
                         width = pencil_width, color = gimpcolor.RGB(0,255,0))
        i+=6
    pdb.gimp_layer_set_opacity(length_layer, 30)

    scale_factor = (real_size / float(photo_size)) #reality/photo scale factor
    real_length_size =  float(obj_len) *scale_factor

    add_text(image, str(round(real_length_size, 1)) + ' '+ units, group, 
             pos = [0, 0],
             points = int (0.05 * image.width))
    paint_scale_line(image, group, scale_factor, units)

    img_name = pdb.gimp_image_get_filename(image)
  
    ## write header for new file
    #if (not(os.path.exists(log_file))):
    #    write_to_file(log_file, 'img_name;sample_real_size;target_real_size;units')

    #write_to_file(log_file, img_name + ';'+  str(real_size) + ';'
    #              + str(round(target_real_size, 1))+ ';' + units+ '²')
   
    pdb.gimp_displays_flush()

    # undo-end
    finish_execution (image,'Завершено')
    if (save_file):
        merge_and_export(image, img_name, '_deviation')
    #pdb.gimp_image_remove_vectors(image, vectors)



def merge_and_export(image, out_file, prefix = ''):
    pdb.gimp_context_push()
    # undo-start
    pdb.gimp_image_undo_group_start(image)
    # remove input file extension
    ex = '.' + out_file.split('.')[-1] 
    out_file = out_file.replace(ex, '')

    result = pdb.gimp_image_merge_visible_layers(image, 0)
    pdb.file_png_save(image, result, out_file + prefix + '.png', image.name, 0,9,1,1,1,1,1)
    pdb.gimp_displays_flush()
    pdb.gimp_image_undo_group_end(image)
    pdb.gimp_context_pop()


# Регистрируем функции в PDB
register(
          "python-fu-add-area-layout", # Имя регистрируемой функции
          "Добавление разметки площади", # Информация о дополнении
          "Позволяет измерить площадь области, используя какой-то известный размер другого объекта на фото. Наносит разметку на изображение и записывает результат в файл", # Короткое описание выполняемых скриптом действий
          "Lena Kolos", # Информация об авторе
          "Lena Kolos (koloslena97@gmail.com)", # Информация о копирайте (копилефте?)
          "15.04.2021", # Дата изготовления
          "Измерение площади выделенной области", # Название пункта меню, с помощью которого дополнение будет запускаться
          "*", # Типы изображений с которыми может работать дополнение
          [
              (PF_IMAGE, "image", "Исходное изображение", None), # Указатель на изображение
              (PF_DRAWABLE, "drawable", "Исходный слой", None), # Указатель на слой
              (PF_FLOAT, "real_size", "Реальный размер объекта (в ед. из.):", 50), # Реальный размер объекта  в ед. измерения
              (PF_STRING, "units", "Единицы измерения (ед. из.):", "cm"),
              (PF_BOOL, "save_file", "Экспортировать результат?", True), # Сохранить ли файл
              (PF_STRING, "log_file", "Файл для записи измерений в текстовом виде:", os.path.expanduser("~\Documents\gimp_areas.csv")), # имя файла для логирования результатов
          ],
          [], # Список переменных которые вернет дополнение
          add_area_layout, menu="<Image>/Deviation measurements/") # Имя исходной функции и меню в которое будет помещён пункт запускающий дополнение


register(
          "python-fu-add-length-layout", # Имя регистрируемой функции
          "Добавление разметки протяженности", # Информация о дополнении
          "Позволяет измерить протяженность объекта, используя какой-то известный размер другого объекта на фото. Наносит разметку на изображение и записывает результат в файл", # Короткое описание выполняемых скриптом действий
          "Lena Kolos", # Информация об авторе
          "Lena Kolos (koloslena97@gmail.com)", # Информация о копирайте (копилефте?)
          "15.06.2021", # Дата изготовления
          "Измерение протяженности объекта", # Название пункта меню, с помощью которого дополнение будет запускаться
          "*", # Типы изображений с которыми может работать дополнение
          [
              (PF_IMAGE, "image", "Исходное изображение", None), # Указатель на изображение
              (PF_DRAWABLE, "drawable", "Исходный слой", None), # Указатель на слой
              (PF_FLOAT, "real_size", "Реальный размер объекта (в ед. из.):", 50), # Реальный размер объекта  в ед. измерения
              (PF_STRING, "units", "Единицы измерения (ед. из.):", "cm"),
              (PF_BOOL, "save_file", "Экспортировать результат?", True), # Сохранить ли файл
              (PF_STRING, "log_file", "Файл для записи измерений в текстовом виде:", os.path.expanduser("~\Documents\gimp_length.csv")), # имя файла для логирования результатов
          ],
          [], # Список переменных которые вернет дополнение
          add_length_layout, menu="<Image>/Deviation measurements/") # Имя исходной функции и меню в которое будет помещён пункт запускающий дополнение

# Запускаем скрипт
main()
