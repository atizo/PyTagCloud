# -*- coding: utf-8 -*-
#
# Hierarchical bounding boxes performance test
#

from pygame import font, mask, Surface, Rect, SRCALPHA
from pygame.sprite import Sprite, collide_mask, collide_rect
import os
import itertools
import math
import pygame

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../fonts')

pygame.init()

class HierarchicalBBoxeTree(object):
    """
    Create hierarchical bounding boxes for a given sprite
    """
    def __init__(self, sprite, min_box_size = 6):
        self._sprite = sprite
        self._x = sprite.rect.x
        self._y = sprite.rect.y
        self._min_box_size = min_box_size
        self.collide_boxes = [] #@todo: remove - debug only
        self._tree = self.create_tree(self._sprite)        
        
    def _calculate_box(self, tag, node, horizontal):
        if node[0].rect.width / 2 < self._min_box_size and node[0].rect.height / 2 < self._min_box_size:
            return
        
        node[2] = False
        created = False
        
        if horizontal and node[0].rect.width / 2 >= self._min_box_size:
            horizontal = False
            nw1 = math.floor(node[0].rect.width / 2.0)
            nw2 = node[0].rect.width - nw1
            nh1 = nh2 = node[0].rect.height
            b1x = node[0].rect.x
            b2x = node[0].rect.x + nw1
            b1y = b2y = node[0].rect.y
            created = True               
        elif node[0].rect.height / 2 >= self._min_box_size:
            horizontal = True
            nw1 = nw2 = node[0].rect.width
            nh1 = math.floor(node[0].rect.height / 2.0)
            nh2 = node[0].rect.height - nh1
            b1x = b2x = node[0].rect.x
            b1y = node[0].rect.y
            b2y = node[0].rect.y + nh1
            created = True
        
        if created:
            box1 = Box(b1x, b1y, nw1, nh1)
            box2 = Box(b2x, b2y, nw2, nh2)
            
            if collide_mask(box1, tag):  
                child_node = [box1, [], True]
                node[1].append(child_node)
                self._calculate_box(tag, child_node, horizontal)
                
            if collide_mask(box2, tag):    
                child_node = [box2, [], True]
                node[1].append(child_node)
                self._calculate_box(tag, child_node, horizontal)
            
    def _tree_iterator(self, root):
        if len(root) > 0:        
            yield root[0]        
            if len(root[1]) == 1:
                for x in self._tree_iterator(root[1][0]):
                    yield x
            elif len(root[1]) == 2:
                for x in itertools.izip_longest(self._tree_iterator(root[1][0]), self._tree_iterator(root[1][1])):
                    if x[0]:
                        yield x[0]
                    if x[1]:
                        yield x[1]
                        
    def tree_iter(self):
        return self._tree_iterator(self._tree)
    
    def _coll(self, node1, node2):
        
        if collide_rect(node1[0], node2[0]):
            #Check if node1 and node2 are hit leafs
            if node1[2] and node2[2]:
                print "found"
                return True        
            
            self.collide_boxes.append(node1[0])
            
            if len(node1[1]) and len(node2[1]):                                    
                for nodex in node1[1]:
                    for nodey in node2[1]:
                        return self._coll(nodex, nodey)
            elif len(node1[1]) and False:
                print "node1"
                for nodex in node1[1]:
                    return self._coll(nodex, node2)
            elif len(node2[1]) and False:
                print "node2"
                for nodex in node2[1]:
                    return self._coll(nodex, node1)
    
    def collide(self, tree):
        return self._coll(self._tree, tree.tree)
        
    def create_tree(self, tag_sprite):
        tree = [Box(tag_sprite.rect.x, tag_sprite.rect.y, tag_sprite.rect.width, tag_sprite.rect.height), [], True]    
        self._calculate_box(tag_sprite, tree, True)    
        return tree
    
    def gettree(self):
        return self._tree

    tree = property(gettree)
    
    def getsprite(self):
        return self._sprite

    sprite = property(getsprite)
    
    def getx(self):
        return self._x
    
    def setx(self, x):                  
        self._sprite.rect.x = x
        for box in self.tree_iter():
            box.rect.x = box.rect.x + x - self._x            
        self._x = x 

    x = property(getx, setx)
    
    def gety(self):
        return self._y
    
    def sety(self, y):                  
        self._sprite.rect.y = y
        for box in self.tree_iter():
            box.rect.y = box.rect.y + y - self._y            
        self._y = y 

    y = property(gety, sety)


class SimpleTag(Sprite):
    def __init__(self, text, x, y, size):
        Sprite.__init__(self)
        fonter = font.Font(os.path.join(FONT_DIR, "Cantarell-Regular.ttf"), size).render(text, True, (0,0,0))
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

class Box(Sprite):
    def __init__(self, x, y, w, h):
        Sprite.__init__(self)
        self.image = Surface((w, h), SRCALPHA, 32)        
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = mask.from_surface(self.image)
        
        self.border = Surface((self.rect.width, self.rect.height), SRCALPHA, 32)        
        pygame.draw.rect(self.border, (255, 0, 0), Rect(0 , 0, self.rect.width , self.rect.height), 1)
        
    def __cmp__(self, other):        
        if self.rect.x == other.rect.x:
            return self.rect.y > other.rect.y
        else:
            return self.rect.x > other.rect.x
        
    def __str__(self):
        return "Rect(%d, %d, %d, %d)" % (self.rect.x, self.rect.y, self.rect.width, self.rect.height)

if __name__ == '__main__':    
    
    tag_cool = SimpleTag("Cool", 0, 0, 300)
    hbtree1 = HierarchicalBBoxeTree(tag_cool)
    
    tag_aero = SimpleTag("aero", 0, 0, 100)
    hbtree2 = HierarchicalBBoxeTree(tag_aero)
    
    hbtree1.x = 110
    hbtree1.y = 150
    
    hbtree2.x = 340
    hbtree2.y = 300
    
    hbtree1.collide(hbtree2)
    
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
        
        for box2 in hbtree1.tree_iter():
            screen.blit(box2.border, box2.rect)
        
        pygame.display.flip()       
        
    pygame.quit()    