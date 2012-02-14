# -*- coding: utf-8 -*-
#
# Hierarchical bounding boxes performance test
#

from pygame import font, mask, Surface, SRCALPHA
from pygame.sprite import Sprite, collide_mask, collide_rect
import os
import pygame
import sys
import timeit
from pytagcloud.profile.hbox import HierarchicalBBoxeTree
import cProfile
import pstats

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../fonts')

pygame.init()

class SimpleTag(Sprite):
    def __init__(self, text, x, y, size):
        Sprite.__init__(self)
        fonter = font.Font(os.path.join(FONT_DIR, "Cantarell-Regular.ttf"),
                           size).render(text, True, (0,0,0))
        frect = fonter.get_bounding_rect()
        frect.x = -frect.x
        frect.y = -frect.y
        font_sf = Surface((frect.width, frect.height), SRCALPHA, 32)
        font_sf.blit(fonter, frect)
        self.image = font_sf
        self.rect = font_sf.get_rect()        
        self.rect.x = x
        self.rect.y = y
        self.mask = mask.from_surface(self.image)

if __name__ == '__main__':    
    
    tag_cool = SimpleTag("Cool", 110, 150, 300)
    hbtree1 = HierarchicalBBoxeTree(tag_cool)d
    tag_aero = SimpleTag("aero", 300, 200, 180)
    hbtree2 = HierarchicalBBoxeTree(tag_aero)
    
    #hbtree1.x = 110
    #hbtree1.y = 150
    
    #hbtree2.x = 300
    #hbtree2.y = 360
    
    def collide1():
        hbtree2.collide(hbtree1)
        
    cProfile.run('collide1()', 'aha.profile')
    p = pstats.Stats('aha.profile')
    p.strip_dirs().sort_stats(-1).print_stats()    
    p.sort_stats('time').print_stats(10)
    #p.print_stats()
        
    #t = timeit.Timer(setup='from __main__ import collide1', stmt='collide1()')
    #print t.timeit()
    
    def collide4():
        collide_rect(tag_cool, tag_aero)
    
    t = timeit.Timer(setup='from __main__ import collide4', stmt='collide4()')
    print t.timeit()

    def collide2():
        collide_mask(tag_cool, tag_aero)
        
    t = timeit.Timer(setup='from __main__ import collide2', stmt='collide2()')
    print t.timeit()

    """
    #collide_mask way
    def doit1():
        for x in xrange(2):
            hbtree2.y -= 1
    
    t = timeit.Timer(setup='from __main__ import doit1', stmt='doit1()')

    print t.timeit()

    def doit2():
        for x in xrange(2):
            tag_aero.rect.y -= 1
        
    t = timeit.Timer(setup='from __main__ import doit2', stmt='doit2()')
    print t.timeit()
    
    sys.exit()
    
    hbtree2.y = 360
    hbtree2.x = 100
    """
    
    """
    start2 = time.time()
    hit = True
    while hit:        
        if collide_mask(tag_cool, tag_aero):
            tag_aero.rect.y -= 1
            tag_aero.rect.x += 1
        else:
            hit = False
            
    print "Duration:", (time.time() - start2) * 1000
    """
    """
    start2 = time.time()
    hit = True
    while hit:        
        if hbtree2.collide(hbtree1):
            hbtree2.y -= 1
        else:
            hit = False
            
    print "Duration:", (time.time() - start2) * 1000
    """
    
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
        
        screen.blit(hbtree1.sprite.image, hbtree1.sprite.rect)
        screen.blit(hbtree2.sprite.image, hbtree2.sprite.rect)
        
        for box1 in hbtree1.collide_boxes:
            screen.blit(box1.border, box1.rect)
        
        for box2 in hbtree2.collide_boxes:
            screen.blit(box2.border, box2.rect)
        
        for box3 in hbtree2.tree_iter():
            pass#screen.blit(box3.border, box3.rect)
        
        pygame.display.flip()       
        
    pygame.quit()    