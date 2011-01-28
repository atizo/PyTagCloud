# -*- coding: utf-8 -*-
from math import sin, cos, ceil
from pygame import transform, font, mask, Surface, Rect, SRCALPHA, draw
from pygame.sprite import Group, Sprite, collide_mask
from random import randint, choice
import colorsys
from copy import copy
import pygame
import os

TAG_PADDING = 5
STEP_SIZE = 1 #relative to base step size of each spiral function
RADIUS = 1
ECCENTRICITY = 1.5

LOWER_START = 0.45
UPPER_START = 0.55

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
DEFAULT_FONT = 'DroidSans.ttf'
DEFAULT_PALETTE = 'default'

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

LAYOUTS = (LAYOUT_HORIZONTAL, LAYOUT_VERTICAL, LAYOUT_MOST_HORIZONTAL, LAYOUT_MOST_VERTICAL, LAYOUT_MIX)

class Tag(Sprite):
    """
    Font tag sprite. Blit the font to a surface to correct the font padding
    """
    def __init__(self, tag, initial_position, rotation=0, fontname=DEFAULT_FONT, fontzoom=5):
        Sprite.__init__(self)
        self.tag = copy(tag)
        self.rotation = rotation
        fonter = font.Font(os.path.join(FONT_DIR, fontname), int(tag['size'] * fontzoom)).render(tag['tag'], True, tag['color'])
        self.tag['size'] *= fontzoom
        fonter = transform.rotate(fonter, rotation)
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
        self.mask = mask.from_surface(self.image)
        self.mask = self.mask.convolve(CONVMASK, None, (TAG_PADDING, TAG_PADDING))

    def flip(self):
        pos = (self.rect.x, self.rect.y)
        angle = 90 if self.rotation == 0 else - 90
        self.image = transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.mask = mask.from_surface(self.image)
        self.mask = self.mask.convolve(CONVMASK, None, (TAG_PADDING, TAG_PADDING))

def defscale(count, mincount, maxcount, minsize, maxsize):
    return minsize + (maxsize - minsize) * (count * 1.0 / (maxcount - mincount))**0.75

def make_tags(wordcounts, minsize=6, maxsize=36, colors=None, scalef=defscale):
    """
    sizes and colors tags 
    wordcounts is a list of tuples(tags, count). (e.g. how often the
    word appears in a text)
    the tags are assigned sizes between minsize and maxsize, the function used
    is determined by scalef (default: square root)
    color is either chosen from colors (list of rgb tuples) if provided or random
    """
    counts = [tag[1] for tag in wordcounts]
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
    for sp in group:
        if collide_mask(sprite, sp):
            return True
    return False

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
    DEFAULT_STEP = 0.05 #radians
    t = 0
    while True:
        t += DEFAULT_STEP * STEP_SIZE * reverse
        yield (ECCENTRICITY * RADIUS * t * cos(t), RADIUS * t * sin(t))

def _rectangular_spiral(reverse):
    DEFAULT_STEP = 3 #px
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

def _search_place(current_tag, tag_store, sizeRect, spiral, flip):
    """
    Start a spiral search with random direction.
    Break off the Search if the spiral exceeds the bounding Rect
    If vertical is enabled and no position could be found, flip the tag and try again
    """

    reverse = choice((-1, 1))
    start_x = current_tag.rect.x
    start_y = current_tag.rect.y

    boundingRect = _get_group_bounding(tag_store, sizeRect).inflate(2, 2)
    suboptimal = None

    for dx, dy in spiral(reverse) :
        if min((dx, dy)) > (sizeRect.width ** 2 + sizeRect.height ** 2) ** 0.5:
            break

        current_tag.rect.x = start_x + dx
        current_tag.rect.y = start_y + dy

        if not _do_collide(current_tag, tag_store) and sizeRect.contains(current_tag.rect):
            if boundingRect.colliderect(current_tag.rect):
                return
            suboptimal = current_tag.rect.copy()

    if suboptimal:
        current_tag.rect = suboptimal
    elif flip:
        current_tag.flip()
        _search_place(current_tag, tag_store, sizeRect, spiral, flip=False)

def _draw_cloud(
        tag_list, 
        surface, 
        layout=LAYOUT_MIX, 
        fontname=DEFAULT_FONT, 
        palette=DEFAULT_PALETTE, 
        fontzoom=5, 
        rectangular=False):
    #Sort the tags by size and word length
    tag_list.sort(key=lambda tag: len(tag['tag']))
    tag_list.sort(key=lambda tag: tag['size'])
    tag_list.reverse()

    if rectangular:
        spiral = _rectangular_spiral
    else:
        spiral = _archimedean_spiral

    sizeRect = surface.get_rect()
    tag_store = Group()
    for tag in tag_list:
        rot = 0
        flip = False
        if layout == LAYOUT_MIX and randint(0, 2) == 0:
            rot = 90
        elif layout == LAYOUT_VERTICAL:
            rot = 90
        elif layout == LAYOUT_MOST_VERTICAL:
            rot = 90
            flip = True
        elif layout == LAYOUT_MOST_HORIZONTAL:
            flip = True
        
        #set color if tag has no color
        if not hasattr(tag, 'color'):
            pass
        
        currentTag = Tag(tag, (0, 0), rot, fontname=fontname, fontzoom=fontzoom)

        xpos = sizeRect.width - currentTag.rect.width
        if xpos < 0: xpos = 0
        xpos = randint(int(xpos * LOWER_START) , int(xpos * UPPER_START))
        currentTag.rect.x = xpos

        ypos = sizeRect.height - currentTag.rect.height
        if ypos < 0: ypos = 0
        ypos = randint(int(ypos * LOWER_START), int(ypos * UPPER_START))
        currentTag.rect.y = ypos

        _search_place(currentTag, tag_store, sizeRect, spiral, flip)

        tag_store.add(currentTag)
        surface.blit(currentTag.image, currentTag.rect)
    return tag_store

def create_tag_image(
        tags, 
        file, 
        size=(800, 600), 
        background=(255, 255, 255), 
        layout=LAYOUT_MIX, 
        crop=True, 
        fontname=DEFAULT_FONT,
        palette=DEFAULT_PALETTE, 
        fontzoom=2, 
        rectangular=False):
    """
    Create a png tag cloud image
    """
    image_surface = Surface(size, SRCALPHA, 32)
    image_surface.fill(background)
    tag_store = _draw_cloud(tags, image_surface, layout, fontname=fontname, palette=palette, fontzoom=fontzoom, rectangular=rectangular)

    if crop:
        boundingRect = _get_group_bounding(tag_store, size)
        crop_surface = Surface((boundingRect.width, boundingRect.height), pygame.SRCALPHA, 32)
        crop_surface.blit(image_surface, (0, 0), area=boundingRect)
        pygame.image.save(crop_surface, file)
    else:
        pygame.image.save(image_surface, file)

def create_html_data(tags, size=(600, 400), fontname=DEFAULT_FONT, fontzoom=2, rectangular=False):
    """
    Create data structures to be used for HTML tag clouds.
    """
    image_surface = Surface(size, 0, 32)
    image_surface.fill((255, 255, 255))
    tag_store = _draw_cloud(tags, image_surface, layout=LAYOUT_HORIZONTAL, fontname=fontname, fontzoom=fontzoom, rectangular=rectangular)
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
            hsvcolor = colorsys.rgb_to_hsv(tag['color'][0] / 255.0, tag['color'][1] / 255.0, tag['color'][2] / 255.0)
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
