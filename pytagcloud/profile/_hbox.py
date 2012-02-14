# -*- coding: utf-8 -*-
#
# Hierarchical bounding boxes performance test
#

from pygame import mask, Surface, Rect, SRCALPHA, draw
from pygame.sprite import Sprite, collide_mask, collide_rect
import itertools
import math

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
        draw.rect(self.border, (255, 0, 0), Rect(0 , 0, self.rect.width ,
                                                        self.rect.height), 1)
        
    def __cmp__(self, other):        
        if self.rect.x == other.rect.x:
            return self.rect.y > other.rect.y
        else:
            return self.rect.x > other.rect.x
        
    def __str__(self):
        return "Rect(%d, %d, %d, %d)" % (self.rect.x, self.rect.y,
                                         self.rect.width, self.rect.height)

class HierarchicalBBoxeTree(object):
    """
    Create hierarchical bounding boxes for a given sprite
    """
    def __init__(self, sprite, min_box_size = 6):
        self._sprite = sprite
        self._init_x = self._x = sprite.rect.x
        self._init_y = self._y = sprite.rect.y
        self._offset_x = self._offset_y = 0
        self._min_box_size = min_box_size
        self.collide_boxes = [] #@todo: remove - debug only
        self._node_index = []
        self._tree = self.create_tree(self._sprite)
        
    def _calculate_box(self, tag, node, horizontal):
        if math.floor(node[0].rect.width / 2.0) <= self._min_box_size and \
        math.floor(node[0].rect.height / 2.0) <= self._min_box_size:
            return
        
        node[2] = False
        created = False
        
        if (horizontal or math.floor(node[0].rect.height / 2.0) <= self._min_box_size) \
        and math.floor(node[0].rect.width / 2.0) >= self._min_box_size:
            horizontal = False
            nw1 = math.floor(node[0].rect.width / 2.0)
            nw2 = node[0].rect.width - nw1
            nh1 = nh2 = node[0].rect.height
            b1x = node[0].rect.x
            b2x = node[0].rect.x + nw1
            b1y = b2y = node[0].rect.y
            created = True               
        elif math.floor(node[0].rect.height / 2.0) >= self._min_box_size:
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
                self._node_index.append(box1)
                node[1].append(child_node)
                self._calculate_box(tag, child_node, horizontal)
                
            if collide_mask(box2, tag):    
                child_node = [box2, [], True]
                self._node_index.append(box2)
                node[1].append(child_node)
                self._calculate_box(tag, child_node, horizontal)
            
    def _tree_iterator(self, root):
        if len(root) > 0:        
            yield root[0]        
            if len(root[1]) == 1:
                for x in self._tree_iterator(root[1][0]):
                    yield x
            elif len(root[1]) == 2:
                for x in itertools.izip_longest(self._tree_iterator(root[1][0]), 
                                                self._tree_iterator(root[1][1])):
                    if x[0]:
                        yield x[0]
                    if x[1]:
                        yield x[1]
                        
    def tree_iter(self):
        return self._tree_iterator(self._tree)
    
    def collide(self, tree):
        for leaf in self.collision_leafs(tree):     
            for other in tree.collision_leafs(self):
                if collide_rect(leaf, other):
                    return True
        return False
    
    def _findleafs(self, node, rect):
        #Stop if there are now more sub nodes
        if len(node[1]) == 0:
            if node[2]: #it was a leaf
                yield node[0]
        
        #Check all child nodes
        for child in node[1]:
            if collide_rect(child[0], rect):                
                for node1 in self._findleafs(child, rect):
                    yield node1
                                
    def collision_leafs(self, tree):
        return self._findleafs(self._tree, tree.tree[0])        
                
    def create_tree(self, tag_sprite):
        tree = [Box(tag_sprite.rect.x, tag_sprite.rect.y, tag_sprite.rect.width,
                    tag_sprite.rect.height), [], True]    
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
        self._sprite.rect.x = self._x = x
        
    x = property(getx, setx)
    
    def gety(self):
        return self._y
    
    def sety(self, y):
        #yoffset = self._y - y
        pass#self._sprite.rect.y = y

    y = property(gety, sety)