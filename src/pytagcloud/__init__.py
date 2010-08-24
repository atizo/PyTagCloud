# -*- coding: utf-8 -*-
from pygame import transform, font, mask, Surface, Rect, SRCALPHA, draw
from pygame.sprite import Group, Sprite, collide_mask
from random import randint, choice
from math import sin, cos, ceil
import colorsys
import pygame

TAG_PADDING = 5
STEP_SIZE = 0.05
RADIUS = 1
ECCENTRICITY = 1.5

LOWER_START = 0.45
UPPER_START = 0.55

convsurf = Surface((2 * TAG_PADDING, 2 * TAG_PADDING))
convsurf.fill((255, 0, 255))
convsurf.set_colorkey((255, 0, 255))
draw.circle(convsurf, (0, 0, 0), (TAG_PADDING, TAG_PADDING), TAG_PADDING)
CONVMASK = mask.from_surface(convsurf)

class Tag(Sprite):
    """
    Font tag sprite. Blit the font to a surface to correct the font padding
    """
    def __init__(self, tag, initial_position, rotation=0, fontname='fonts/Arial.ttf', fontzoom=5):
        Sprite.__init__(self)
        self._tag = tag
        fonter = font.Font(fontname, int(tag['size'] * fontzoom)).render(tag['tag'], True, tag['color'])
        self._tag['size'] *= fontzoom
        fonter = transform.rotate(fonter, rotation)
        frect = fonter.get_bounding_rect()
        frect.x = -frect.x
        frect.y = -frect.y        
        self._fontoffset = (-frect.x, -frect.y)
        font_sf = Surface((frect.width, frect.height), pygame.SRCALPHA, 32)
        font_sf.blit(fonter, frect)        
        self.image = font_sf
        self.rect = font_sf.get_rect()
        self.rect.width += TAG_PADDING
        self.rect.height += TAG_PADDING
        self.rect.x = initial_position[0]
        self.rect.y = initial_position[1]
        self.mask = mask.from_surface(self.image)
        self.mask = self.mask.convolve(CONVMASK, None, (TAG_PADDING, TAG_PADDING))

    def get_tag(self):
        return self._tag
    tag = property(get_tag)
    
    def get_fontoffset(self):
        return self._fontoffset
    fontoffset = property(get_fontoffset)
        
def _do_collide(sprite, group):
    """
    Use mask based collision detection
    """
    for sp in group:
        if collide_mask(sprite, sp):
            return True
    return False

def _get_group_bounding(tag_store, size):
    if tag_store:
        rects = [tag.rect for tag in tag_store]
        return rects[0].unionall(rects[1:])
    return Rect(0, 0, size[0], size[1])

def _archimedean_spiral(t):
    return (ECCENTRICITY * RADIUS * t * cos(t), RADIUS * t * sin(t))

def _rectangular_spiral(t):
    if t < 0:
        return _rectangular_spiral(-t)
    pos = (t - int(t)) if (t - int(t)) else 1
    px = (-1 + 2 * (ceil(t + 1) % 2 + pos * (ceil(t) % 2)))
    py = (-1 + 2 * (ceil(t) % 2 + pos * (ceil(t + 1) % 2)))
    return (px * RADIUS * ceil(t / 4.) * (-1 + 2 * (ceil(t / 2.) % 2)),
            py * RADIUS * ceil((t - 1) / 4.) * (-1 + 2 * (ceil((t - 1) / 2.) % 2)))

def _search_place(current_tag, tag_store, sizeRect, spiral):
    """
    Start an (archimedean)spiral search with random direction.
    Break off the Search if the spiral exceeds size.
    """
    
    reverse = choice((-1,1))
    
    t = 0.
    start_x = current_tag.rect.x
    start_y = current_tag.rect.y
    
    while RADIUS * t < (sizeRect.width**2 + sizeRect.height**2)**0.5:
        if not _do_collide(current_tag, tag_store) and sizeRect.contains(current_tag.rect):
            break
         
        dx, dy = spiral(reverse * t)
        current_tag.rect.x = start_x + dx
        current_tag.rect.y = start_y + dy
        
        t += STEP_SIZE
            
def _draw_cloud(tags, surface, vertical=True, fontname='fonts/Arial.ttf', fontzoom=5, rectangular=False):
        #Sort the tags
    tag_list = sorted(tags, key=lambda tag: tag['size'])
    tag_list.reverse()
    
    if rectangular:
        spiral = _rectangular_spiral
    else:
        spiral = _archimedean_spiral
    
    sizeRect = surface.get_rect()
    tag_store = Group()
    for tag in tag_list:
        rot = 0
        if vertical and randint(0,2) == 0:
            rot = 90
        currentTag = Tag(tag, (0,0), rot, fontname=fontname, fontzoom=fontzoom)
        
        xpos = sizeRect.width - currentTag.rect.width
        if xpos < 0: xpos = 0
        xpos = randint(int(xpos * LOWER_START) , int(xpos * UPPER_START))
        currentTag.rect.x = xpos
        
        ypos = sizeRect.height - currentTag.rect.height
        if ypos < 0: ypos = 0
        ypos = randint(int(ypos * LOWER_START), int(ypos * UPPER_START))
        currentTag.rect.y = ypos
        
        _search_place(currentTag, tag_store, sizeRect, spiral)
                
        tag_store.add(currentTag)
        surface.blit(currentTag.image, currentTag.rect)
    return tag_store

def create_tag_image(tags, file, size=(800,600), background=(255,255,255), vertical=True, crop=True, fontname='fonts/Arial.ttf', fontzoom=2, rectangular=False):
    """
    Create a png tag cloud image
    """
    pygame.init()
    image_surface = Surface(size, SRCALPHA, 32)
    image_surface.fill(background)
    tag_store = _draw_cloud(tags, image_surface, vertical, fontname=fontname, fontzoom=fontzoom, rectangular=rectangular)
    
    if crop:
        boundingRect = _get_group_bounding(tag_store, size)
        crop_surface = Surface((boundingRect.width, boundingRect.height), pygame.SRCALPHA, 32)
        crop_surface.blit(image_surface, (0,0), area=boundingRect)
        pygame.image.save(crop_surface, file)
    else:
        pygame.image.save(image_surface, file)
        
def create_html_data(tags, size=(600,400), fontname='fonts/Arial.ttf', fontzoom=2, rectangular=False):
    """
    Create data structures to be used for HTML tag clouds.
    """
    pygame.init()
    image_surface = Surface(size, 0, 32)
    image_surface.fill((255,255,255))
    tag_store = _draw_cloud(tags, image_surface, False, fontname=fontname, fontzoom=fontzoom, rectangular=rectangular)
    tag_store = sorted(tag_store, key=lambda tag: tag.tag['size'])
    tag_store.reverse()
    data = {
            'css': [],
            'links': []
            }
    color_map = {}
    num_color = 0
    for tag in tags:
        if not color_map.has_key(tag['color']):
            color_name = "c%d" % num_color
            hsvcolor = colorsys.rgb_to_hsv(tag['color'][0]/255.0,tag['color'][1]/255.0,tag['color'][2]/255.0)
            lighter = hsvcolor[2] + 0.3
            if lighter > 1: lighter = 1
            light = colorsys.hsv_to_rgb(hsvcolor[0], hsvcolor[1], lighter)
            data['css'].append('a.%s{color: %s;}' % (color_name, '#%02x%02x%02x' % tag['color']))
            data['css'].append('a.%s:hover{color: %s;}' % (color_name, '#%02x%02x%02x' % (light[0] * 255, light[1] * 255, light[2] * 255)))
            color_map[tag['color']] = color_name
            num_color += 1
    
    for stag in tag_store:
        tag = {
               'tag': stag.tag['tag'],
               'cls': color_map[stag.tag['color']], 
               'top': stag.rect.top - stag.fontoffset[1], 
               'left': stag.rect.left - stag.fontoffset[0],
               'size': stag.tag['size']
               }
        data['links'].append(tag)
    return data