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
import cProfile
import pstats

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../fonts')

pygame.init()


if __name__ == '__main__':    
    
    
    for x in xrange(10):
        fsize = 50 + 10 * x
        thefont = font.Font(os.path.join(FONT_DIR, "cantarell-regular-webfont.ttf"), fsize)

        print "Lineheight", thefont.get_linesize()
        print "Size", fsize
        print "Ascent", thefont.get_ascent()
        print "Descent", thefont.get_descent()
        print "Diff", thefont.get_linesize() - (thefont.get_ascent() + abs(thefont.get_descent()))
        text = thefont.render("Cooer", True, (0,0,0))
        print "Text h", text.get_bounding_rect()
        print ""

    metrics =  thefont.metrics("Cooer")
    
    print min([f[2] for f in metrics])
    print max([f[3] for f in metrics])
    print metrics[0]
    
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("PyTagCloud Font Alignment")    
    
    done = False
    clock = pygame.time.Clock()    
    
    while done==False:         
        
        clock.tick(10)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done=True
                
        screen.fill((255,255,255))
        
        screen.blit(text, (100,100))
       
        
        pygame.display.flip()       
        
    pygame.quit()    