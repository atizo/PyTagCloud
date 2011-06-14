# -*- coding: utf-8 -*-
#
# Naive implementation of hierarchical bounding boxes
#

from pygame import font, mask, Surface, Rect, SRCALPHA
from pygame.sprite import Sprite, collide_mask
import os
import pygame
from pytagcloud.profile.btree import CBOrdTree


FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../fonts')

pygame.init()

class SimpleTag(Sprite):
    def __init__(self, text, x, y):
        Sprite.__init__(self)
        fonter = font.Font(os.path.join(FONT_DIR, "Cantarell-Regular.ttf"), 300).render(text, True, (0,0,0))
        frect = fonter.get_bounding_rect()
        frect.x = -frect.x
        frect.y = -frect.y
        font_sf = Surface((frect.width, frect.height), pygame.SRCALPHA, 32)
        font_sf.blit(fonter, frect)
        self.image = font_sf
        self.rect = font_sf.get_rect()        
        self.rect.x = x
        self.rect.y = y
        self.mask = mask.from_surface(self.image)

class Box(Sprite):
    def __init__(self, x, y, w, h):
        Sprite.__init__(self)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA, 32)        
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = mask.from_surface(self.image)
        
        self.border = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA, 32)        
        pygame.draw.rect(self.border, (255, 0, 0), Rect(0 , 0, self.rect.width , self.rect.height), 1)
        
    def __cmp__(self, other):        
        if self.rect.x == other.rect.x:
            return self.rect.y > other.rect.y
        else:
            return self.rect.x > other.rect.x
        
    def __str__(self):
        return "Rect(%d, %d, %d, %d)" % (self.rect.x, self.rect.y, self.rect.width, self.rect.height)

def calculate_box(tag, tree, root, horizontal):
    if root.data.rect.width / 2 < 4 or root.data.rect.height / 2 < 4:
        return
    
    if horizontal:
        horizontal = False
        
        nw = root.data.rect.width / 2
        nh = root.data.rect.height
        
        b1x = root.data.rect.x
        b2x = root.data.rect.x + nw
        b1y = b2y = root.data.rect.y                
    else:
        horizontal = True
        
        nw = root.data.rect.width
        nh = root.data.rect.height / 2
        
        b1x = b2x = root.data.rect.x
        b1y = root.data.rect.y
        b2y = root.data.rect.y + nh 
   
    box1 = Box(b1x, b1y, nw, nh)
    box2 = Box(b2x, b2y, nw, nh)
    
    if collide_mask(box1, tag):    
        node = tree.insert(root, box1)
        calculate_box(tag, tree, node, horizontal)
        
    if collide_mask(box2, tag):    
        node = tree.insert(root, box2)
        calculate_box(tag, tree, node, horizontal) 
    
def go():    
    tag1 = SimpleTag("Cool", 100, 100)
    box1 = Box(tag1.rect.x, tag1.rect.y, tag1.rect.width, tag1.rect.height)
    
    btree = CBOrdTree()
    
    root = btree.addNode(box1)
    
    calculate_box(tag1, btree, root, True)
    
    rlist = []
        
    btree.toList(root, rlist)
        
    return tag1, rlist

if __name__ == '__main__':    
    
    font_tag, rlist = go()
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("PyTagCloud Intersection Test")
    
    done = False
    clock = pygame.time.Clock()    
    
    while done==False:         
        
        clock.tick(10)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done=True
                
        screen.fill((255,255,255))
        
        screen.blit(font_tag.image, font_tag.rect)
        
        for e in rlist:
            screen.blit(e.border, e.rect)
        
        pygame.display.flip()       
        
    pygame.quit()    