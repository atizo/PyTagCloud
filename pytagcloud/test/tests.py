# -*- coding: utf-8 -*-
from pytagcloud import create_tag_image, create_html_data, make_tags, \
    LAYOUT_HORIZONTAL, LAYOUTS
from pytagcloud.colors import COLOR_SCHEMES
from pytagcloud.lang.counter import get_tag_counts
from string import Template
import os
import time
import unittest

class Test(unittest.TestCase):
    """
    Generate tag clouds and save them to <YOURHOME>/pytagclouds/
    Note: All tests are disabled ('_' prefixed) by default
    """
    
    def setUp(self):
        self.test_output = os.path.join(os.getcwd(), 'out')
        self.hound = open(os.path.join(os.getcwd(), 'pg2852.txt'), 'r')
        
        if not os.path.exists(self.test_output):
            os.mkdir(self.test_output )            
            
    def tearDown(self):
        self.hound.close()
        
    def test_tag_counter(self):
        tag_list = get_tag_counts(self.hound.read())[:50]     
        self.assertTrue(('sir', 350) in tag_list)

    def test_make_tags(self):
        mtags = make_tags(get_tag_counts(self.hound.read())[:60])
        found = False
        for tag in mtags:
            if tag['tag'] == 'sir' and tag['size'] == 40:
                found = True
                break
            
        self.assertTrue(found)

    def test_layouts(self):
        start = time.time()
        tags = make_tags(get_tag_counts(self.hound.read())[:80], maxsize=120)
        for layout in LAYOUTS:
            create_tag_image(tags, os.path.join(self.test_output, 'cloud_%s.png' % layout),
                             size=(900, 600),
                             background=(255, 255, 255, 255),
                             layout=layout, fontname='Lobster')
        print "Duration: %d sec" % (time.time() - start)
        
    def test_large_tag_image(self):
        start = time.time()
        tags = make_tags(get_tag_counts(self.hound.read())[:80], maxsize=120, 
                         colors=COLOR_SCHEMES['audacity'])
        create_tag_image(tags, os.path.join(self.test_output, 'cloud_large.png'), 
                         size=(900, 600), background=(0, 0, 0, 255), 
                         layout=LAYOUT_HORIZONTAL, fontname='Lobster')
        print "Duration: %d sec" % (time.time() - start)

    def test_create_html_data(self):
        """
        HTML code sample
        """
        tags = make_tags(get_tag_counts(self.hound.read())[:100], maxsize=120, colors=COLOR_SCHEMES['audacity'])
        data = create_html_data(tags, (440,600), layout=LAYOUT_HORIZONTAL, fontname='PT Sans Regular')
        
        template_file = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web/template.html'), 'r')    
        html_template = Template(template_file.read())
        
        context = {}
        
        tags_template = '<li class="cnt" style="top: %(top)dpx; left: %(left)dpx; height: %(height)dpx;"><a class="tag %(cls)s" href="#%(tag)s" style="top: %(top)dpx;\
        left: %(left)dpx; font-size: %(size)dpx; height: %(height)dpx; line-height:%(lh)dpx;">%(tag)s</a></li>'
        
        context['tags'] = ''.join([tags_template % link for link in data['links']])
        context['width'] = data['size'][0]
        context['height'] = data['size'][1]
        context['css'] = "".join("a.%(cname)s{color:%(normal)s;}\
        a.%(cname)s:hover{color:%(hover)s;}" % 
                                  {'cname':k,
                                   'normal': v[0],
                                   'hover': v[1]} 
                                 for k,v in data['css'].items())
        
        html_text = html_template.substitute(context)
        
        html_file = open(os.path.join(self.test_output, 'cloud.html'), 'w')
        html_file.write(html_text)
        html_file.close()       

if __name__ == "__main__":
    unittest.main()