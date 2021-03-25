#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Импортируем необходимые модули
import math
import string
#import Image
from gimpfu import *
from array import array

# https://github.com/khufkens/GIMP_save_load_guides/blob/79229c289777cae9d505083eda22db14032930ee/GIMP_save_load_guides.py
def guides_to_guide_data(image):
    guide_detail = ["Guide", '']
    guide_width_and_height = [image.width,image.height]
    horizontal_guides = []
    vertical_guides = []
	#read guide info into arrays 
    guide_id = pdb.gimp_image_find_next_guide(image,0)
    while guide_id > 0:
        if pdb.gimp_image_get_guide_orientation(image,guide_id) == ORIENTATION_HORIZONTAL:
            horizontal_guides.append(pdb.gimp_image_get_guide_position(image,guide_id))
        else:
            vertical_guides.append(pdb.gimp_image_get_guide_position(image,guide_id))
        guide_id = pdb.gimp_image_find_next_guide(image,guide_id)
	#if empty add some place holders so we don't have to deal with empty list
    if len(horizontal_guides) == 0:
        horizontal_guides = [100000]
    if len(vertical_guides) == 0:
        vertical_guides = [100000]
    #gimp.message(str(horizontal_guides))

    return [guide_detail,guide_width_and_height,horizontal_guides,vertical_guides]

import getpass

SIZE_IN_PIXELS = 0
SIZE_IN_POINTS = 1

# https://github.com/eib/gimp-plugins/blob/8c8a2ef70975d793685ec7fc5de743f3ebcadb0a/add_watermark_text.py
def add_text(image, text, points = 100, antialias = False, letter_spacing = -3, fontname = "Sans", color = (255, 255, 255)):
    x = 0
    y = 0
    border = -1
    watermark_shadow_opacity = 60.0
    #undo-start
    pdb.gimp_context_push();
    pdb.gimp_image_undo_group_start(image);
    
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
   # pdb.script-fu-drop-shadow(image, text_layer, gimpcolor.RGB(0, 0, 0, 255),
                                           # 30.0, 6.0, 0.0, 5.0, watermark_shadow_opacity, NORMAL_MODE)

    #undo-end
    pdb.gimp_image_undo_group_end(image);
    pdb.gimp_context_pop();

# https://github.com/iwabuchiken/WS_Others.Art-deprecated.20190617_174059-/blob/fe2dad57431304497cc69bcaccb14a5004dea72d/JVEMV6/46_art/2_image-prog/1_gimp/4_/plugin_2_1_4.py
def draw_pencil_lines(drawable, lines, width = 10, color = gimpcolor.RGB(39,221,65)):
    pdb.gimp_context_set_foreground(color)
    pdb.gimp_context_set_brush_size(width)
    #pdb.gimp_paintbrush_default(drawable, len(lines), lines)
    pdb.gimp_pencil(drawable, len(lines), lines)
  
def draw_rect(drawable, x1, y1, x2, y2):
  lines = [x1, y1, x2, y1, x2, y2, x1, y2, x1, y1]
  draw_pencil_lines(drawable, lines)

def newline(x1,y1,x2,y2):
	return [x1,y1,x1,y1,x1,y1,x2,y2,x2,y2,x2,y2];

def add_colored_border(image, drawable, real_size, photo_size, border_color):
  pdb.gimp_context_push()
  # Запрещаем запись информации для отмены действий,
  # что бы все выполненные скриптом операции можно было отменить одим махом
  # нажав Ctrl + Z или выбрав из меню "Правка" пункт "Отменить действие"
  pdb.gimp_image_undo_group_start(image)
  
  ## get info from guides
  #guide_detail, guide_width_and_height, horizontal_guides, vertical_guides = guides_to_guide_data(image)
  ##grab selection bounding box values
  #selection = pdb.gimp_selection_bounds(image);

  #x1 = selection[1];
  #y1 = selection[2];
  #x2 = selection[3];
  #y2 = selection[4];

  ##adds a new path
  #if (len(vertical_guides) > 0) or (len(horizontal_guides) > 0): #if there is at least one guide defined we create a path

  #    all_vertical_points = sorted(set(vertical_guides + [x1,x2]))
  #    all_horizontal_points = sorted(set(horizontal_guides + [y1,y2]))

	 # #draw vertical lines
  #    for ix in range(0,len(vertical_guides)):
  #          drawable = image.new_layer("vertical_line")
  #          for iy in range(0,len(all_horizontal_points)-1):
  #              draw_pencil_lines(drawable, newline(vertical_guides[ix],all_horizontal_points[iy],vertical_guides[ix],all_horizontal_points[iy+1]))

	 # #draw horizontal lines
  #    for iy in range(0,len(horizontal_guides)):
  #          drawable = image.new_layer("horizontal_line")
  #          for ix in range(0,len(all_vertical_points)-1):
  #              draw_pencil_lines(drawable, newline(all_vertical_points[ix],horizontal_guides[iy],all_vertical_points[ix+1],horizontal_guides[iy]))

  #    target_photo_size = float(abs(vertical_guides[0]-vertical_guides[1]))
  #    target_real_size = (real_size / float(photo_size)) * target_photo_size

  #    file_name = pdb.gimp_image_get_filename(image)
  #    add_text(image, str(round(target_real_size, 1)) + ' mm.') 
  #    with open(r"C:\test.csv", 'a') as file: 
  #          file.writelines(file_name + ';'+ str(target_real_size) + '\n') 
  #else:
  #      gimp.message('No guides on image')



  # get info from vectors
  vectors = pdb.gimp_image_get_active_vectors(image)
  strokes_num, strokes = pdb.gimp_vectors_get_strokes(vectors)
  stroke_type, n_points, cpoints, closed = pdb.gimp_vectors_stroke_get_points(vectors, strokes[0])
  c_len = len(cpoints)

  draw_pencil_lines(drawable, newline(cpoints[0], cpoints[1], cpoints[c_len-2], cpoints[c_len-1]))
  photo_size = pdb.gimp_vectors_stroke_get_length(vectors, strokes[1], 1)
  gimp.message(str(real_size) + ' '+str(photo_size))
  target_photo_size = float(abs(cpoints[0] - cpoints[c_len-2]))
  target_real_size = (real_size / float(photo_size)) * target_photo_size
  
  #pdb.gimp_image_remove_vectors(image, vectors)

  file_name = pdb.gimp_image_get_filename(image)
  add_text(image, str(round(target_real_size, 1)) + ' mm.') 
  with open(r"C:\test.csv", 'a') as file: 
      file.writelines(file_name + ';'+ str(target_real_size) + '\n') 
 
  # Обновляем изоборажение на дисплее
  pdb.gimp_displays_flush()
  # Разрешаем запись информации для отмены действий
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