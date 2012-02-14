# -*- coding: utf-8 -*-
from copy import copy
from math import sin, cos, ceil
from pygame import transform, font, mask, Surface, Rect, SRCALPHA, draw
from pygame.sprite import Group, Sprite, collide_mask
from random import randint, choice
import colorsys
import math
import os
import pygame
import simplejson


TAG_PADDING = 5
STEP_SIZE = 2 # relative to base step size of each spiral function
RADIUS = 1
ECCENTRICITY = 1.5

LOWER_START = 0.45
UPPER_START = 0.55

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
DEFAULT_FONT = 'Droid Sans'
DEFAULT_PALETTE = 'default'
FONT_CACHE = simplejson.load(open(os.path.join(FONT_DIR, 'fonts.json'), 'r'))

pygame.init()
convsurf = Surface((2 * TAG_PADDING, 2 * TAG_PADDING))
convsurf.fill((255, 0, 255))
convsurf.set_colorkey((255, 0, 255))
draw.circle(convsurf, (0, 0, 0), (TAG_PADDING, TAG_PADDING), TAG_PADDING)
CONVMASK = mask.from_surface(convsurf)

LAYOUT_HORIZONTAL = 0
LAYOUT_VERTICAL = 1
LAYOUT_MOST_HORIZONTAL = 2
LAYOUT_MOST_VERTICAL = 3
LAYOUT_MIX = 4

LAYOUTS = (
           LAYOUT_HORIZONTAL,
           LAYOUT_VERTICAL,
           LAYOUT_MOST_HORIZONTAL,
           LAYOUT_MOST_VERTICAL,
           LAYOUT_MIX
           )

LAST_COLLISON_HIT = None

class Tag(Sprite):
    """
    Font tag sprite. Blit the font to a surface to correct the font padding
    """
    def __init__(self, tag, initial_position, fontname=DEFAULT_FONT):
        Sprite.__init__(self)
        self.tag = copy(tag)
        self.rotation = 0
        
        self.font_spec = load_font(fontname)
        self.font = font.Font(os.path.join(FONT_DIR,
                                           self.font_spec['ttf']),
                                           self.tag['size'])
        fonter = self.font.render(tag['tag'], True, tag['color'])
        frect = fonter.get_bounding_rect()
        frect.x = -frect.x
        frect.y = -frect.y
        self.fontoffset = (-frect.x, -frect.y)
        font_sf = Surface((frect.width, frect.height), pygame.SRCALPHA, 32)
        font_sf.blit(fonter, frect)
        self.image = font_sf
        self.rect = font_sf.get_rect()
        self.rect.width += TAG_PADDING
        self.rect.height += TAG_PADDING
        self.rect.x = initial_position[0]
        self.rect.y = initial_position[1]
        self._update_mask()
        
    def _update_mask(self):
        self.mask = mask.from_surface(self.image)
        self.mask = self.mask.convolve(CONVMASK, None, (TAG_PADDING, TAG_PADDING))

    def flip(self):        
        angle = 90 if self.rotation == 0 else - 90
        self.rotate(angle)
        
    def rotate(self, angle):
        pos = (self.rect.x, self.rect.y)
        self.image = transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self._update_mask()
        
    def update_fontsize(self):
        self.font = font.Font(os.path.join(FONT_DIR, self.font_spec['ttf']),
                              self.tag['size'])
        
def load_font(name):
    for font in FONT_CACHE:
        if font['name'] == name:
            return font
    raise AttributeError('Invalid font name. Should be one of %s' % 
                         ", ".join([f['name'] for f in FONT_CACHE]))

def defscale(count, mincount, maxcount, minsize, maxsize):
    if maxcount == mincount:
        return int((maxsize - minsize) / 2.0 + minsize)
    return int(minsize + (maxsize - minsize) * 
               (count * 1.0 / (maxcount - mincount)) ** 0.8)

def make_tags(wordcounts, minsize=3, maxsize=36, colors=None, scalef=defscale):
    """
    sizes and colors tags 
    wordcounts is a list of tuples(tags, count). (e.g. how often the
    word appears in a text)
    the tags are assigned sizes between minsize and maxsize, the function used
    is determined by scalef (default: square root)
    color is either chosen from colors (list of rgb tuples) if provided or random
    """
    counts = [tag[1] for tag in wordcounts]
    
    if not len(counts):
        return []
    
    maxcount = max(counts)
    mincount = min(counts)
    tags = []
    for word_count in wordcounts:
        color = choice(colors) if colors else (randint(10, 220), randint(10, 220),
                                               randint(10, 220))
        tags.append({'color': color, 'size': scalef(word_count[1], mincount,
                                                    maxcount, minsize, maxsize),
                     'tag': word_count[0]})
    return tags

def _do_collide(sprite, group):
    """
    Use mask based collision detection
    """
    global LAST_COLLISON_HIT
    # Test if we still collide with the last hit
    if LAST_COLLISON_HIT and collide_mask(sprite, LAST_COLLISON_HIT):
        return True
    
    for sp in group:
        if collide_mask(sprite, sp):
            LAST_COLLISON_HIT = sp
            return True
    return False

def _get_tags_bounding(tag_store):
    if not len(tag_store):
        return Rect(0,0,0,0)
    rects = [tag.rect for tag in tag_store]
    return rects[0].unionall(rects[1:])
        
def _get_group_bounding(tag_store, sizeRect):
    if not isinstance(sizeRect, pygame.Rect):
        sizeRect = Rect(0, 0, sizeRect[0], sizeRect[1])
    if tag_store:
        rects = [tag.rect for tag in tag_store]
        union = rects[0].unionall(rects[1:])
        if sizeRect.contains(union):
            return union
    return sizeRect

def _archimedean_spiral(reverse):
    DEFAULT_STEP = 0.05 # radians
    t = 0
    r = 1
    if reverse:
        r = -1
    while True:
        t += DEFAULT_STEP * STEP_SIZE * r
        yield (ECCENTRICITY * RADIUS * t * cos(t), RADIUS * t * sin(t))

def _rectangular_spiral(reverse):
    DEFAULT_STEP = 3 # px
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    if reverse:
        directions.reverse()
    direction = directions[0]

    spl = 1
    dx = dy = 0
    while True:
        for step in range(spl * 2):
            if step == spl:
                direction = directions[(spl - 1) % 4]
            dx += direction[0] * STEP_SIZE * DEFAULT_STEP
            dy += direction[1] * STEP_SIZE * DEFAULT_STEP
            yield dx, dy
        spl += 1

def _search_place(current_tag, tag_store, canvas, spiral, ratio):
    """
    Start a spiral search with random direction.
    Resize the canvas if the spiral exceeds the bounding rectangle
    """

    reverse = choice((0, 1))
    start_x = current_tag.rect.x
    start_y = current_tag.rect.y
    min_dist = None
    opt_x = opt_y = 0
    
    current_bounding = _get_tags_bounding(tag_store)
    cx = current_bounding.w / 2.0
    cy = current_bounding.h / 2.0

    for dx, dy in spiral(reverse):
        current_tag.rect.x = start_x + dx
        current_tag.rect.y = start_y + dy
        if not _do_collide(current_tag, tag_store):
            if canvas.contains(current_tag.rect):
                tag_store.add(current_tag)
                return
            else:
                # get the distance from center                
                current_dist = (abs(cx - current_tag.rect.x) ** 2 + 
                                abs(cy - current_tag.rect.y) ** 2) ** 0.5      
                if not min_dist or current_dist < min_dist:
                    opt_x = current_tag.rect.x
                    opt_y = current_tag.rect.y 
                    min_dist = current_dist
                
                # only add tag if the spiral covered the canvas boundaries
                if abs(dx) > canvas.width / 2.0 and abs(dy) > canvas.height / 2.0:
                    current_tag.rect.x = opt_x                    
                    current_tag.rect.y = opt_y                    
                    tag_store.add(current_tag)
                    
                    new_bounding = current_bounding.union(current_tag.rect)
                    
                    delta_x = delta_y = 0.0
                    if new_bounding.w > canvas.width:
                        delta_x = new_bounding.w - canvas.width
                        
                        canvas.width = new_bounding.w
                        delta_y = ratio * new_bounding.w - canvas.height
                        canvas.height = ratio * new_bounding.w                                        
                        
                    if new_bounding.h > canvas.height:                        
                        delta_y = new_bounding.h - canvas.height
                        
                        canvas.height = new_bounding.h
                        canvas.width = new_bounding.h / ratio
                        delta_x = canvas.width - canvas.width
                    
                    # realign
                    for tag in tag_store:
                        tag.rect.x += delta_x / 2.0
                        tag.rect.y += delta_y / 2.0
                    
                    
                    canvas = _get_tags_bounding(tag_store)
                               
                    return  

def _draw_cloud(
        tag_list,
        layout=LAYOUT_MIX,
        size=(500,500),
        fontname=DEFAULT_FONT,
        rectangular=False):
    
    # sort the tags by size and word length
    tag_list.sort(key=lambda tag: len(tag['tag']))
    tag_list.sort(key=lambda tag: tag['size'])
    tag_list.reverse()

    # create the tag space
    tag_sprites = []
    area = 0
    for tag in tag_list:
        tag_sprite = Tag(tag, (0, 0), fontname=fontname)
        area += tag_sprite.mask.count()
        tag_sprites.append(tag_sprite)
    
    canvas = Rect(0, 0, 0, 0)
    ratio = float(size[1]) / size[0]
    
    if rectangular:
        spiral = _rectangular_spiral
    else:
        spiral = _archimedean_spiral
        
    aligned_tags = Group()
    for tag_sprite in tag_sprites:
        angle = 0
        if layout == LAYOUT_MIX and randint(0, 2) == 0:
            angle = 90
        elif layout == LAYOUT_VERTICAL:
            angle = 90
        
        tag_sprite.rotate(angle)

        xpos = canvas.width - tag_sprite.rect.width
        if xpos < 0: xpos = 0
        xpos = randint(int(xpos * LOWER_START) , int(xpos * UPPER_START))
        tag_sprite.rect.x = xpos

        ypos = canvas.height - tag_sprite.rect.height
        if ypos < 0: ypos = 0
        ypos = randint(int(ypos * LOWER_START), int(ypos * UPPER_START))
        tag_sprite.rect.y = ypos

        _search_place(tag_sprite, aligned_tags, canvas, spiral, ratio)            
    canvas = _get_tags_bounding(aligned_tags)
    
    # resize cloud
    zoom = min(float(size[0]) / canvas.w, float(size[1]) / canvas.h)
    
    for tag in aligned_tags:
        tag.rect.x *= zoom
        tag.rect.y *= zoom
        tag.rect.width *= zoom
        tag.rect.height *= zoom
        tag.tag['size'] = int(tag.tag['size'] * zoom)
        tag.update_fontsize() 
    
    canvas = _get_tags_bounding(aligned_tags)
    
    return canvas, aligned_tags

def create_tag_image(
        tags, 
        output, 
        size=(500,500), 
        background=(255, 255, 255), 
        layout=LAYOUT_MIX, 
        fontname=DEFAULT_FONT,
        rectangular=False):
    """
    Create a png tag cloud image
    """
    
    if not len(tags):
        return
    
    sizeRect, tag_store = _draw_cloud(tags,
                                      layout,
                                      size=size, 
                                      fontname=fontname,
                                      rectangular=rectangular)
    
    image_surface = Surface((sizeRect.w, sizeRect.h), SRCALPHA, 32)
    image_surface.fill(background)
    for tag in tag_store:
        image_surface.blit(tag.image, tag.rect)
    pygame.image.save(image_surface, output)

def create_html_data(tags, 
        size=(500,500), 
        layout=LAYOUT_MIX, 
        fontname=DEFAULT_FONT,
        rectangular=False):
    """
    Create data structures to be used for HTML tag clouds.
    """
    
    if not len(tags):
        return
    
    sizeRect, tag_store = _draw_cloud(tags,
                                      layout,
                                      size=size, 
                                      fontname=fontname,
                                      rectangular=rectangular)
    
    tag_store = sorted(tag_store, key=lambda tag: tag.tag['size'])
    tag_store.reverse()
    data = {
            'css': {},
            'links': []
            }
    
    color_map = {}
    for color_index, tag in enumerate(tags):
        if not color_map.has_key(tag['color']):
            color_name = "c%d" % color_index
            hslcolor = colorsys.rgb_to_hls(tag['color'][0] / 255.0, 
                                           tag['color'][1] / 255.0, 
                                           tag['color'][2] / 255.0)
            lighter = hslcolor[1] * 1.4
            if lighter > 1: lighter = 1
            light = colorsys.hls_to_rgb(hslcolor[0], lighter, hslcolor[2])
            data['css'][color_name] = ('#%02x%02x%02x' % tag['color'], 
                                       '#%02x%02x%02x' % (light[0] * 255,
                                                          light[1] * 255,
                                                          light[2] * 255))
            color_map[tag['color']] = color_name

    for stag in tag_store:
        line_offset = 0
        
        line_offset = stag.font.get_linesize() - (stag.font.get_ascent() +  abs(stag.font.get_descent()) - stag.rect.height) - 4
        
        tag = {
               'tag': stag.tag['tag'],
               'cls': color_map[stag.tag['color']],
               'top': stag.rect.y - sizeRect.y,
               'left': stag.rect.x - sizeRect.x,
               'size': int(stag.tag['size'] * 0.85),
               'height': int(stag.rect.height * 1.19) + 4,
               'width': stag.rect.width,
               'lh': line_offset
               }
        
        data['links'].append(tag)
        data['size'] = (sizeRect.w, sizeRect.h * 1.15)
            
    return data
