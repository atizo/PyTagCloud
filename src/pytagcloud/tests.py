# -*- coding: utf-8 -*-
import os
import time
import unittest
from pytagcloud import create_tag_image, create_html_data, make_tags

class Test(unittest.TestCase):

    def setUp(self):
        self.home = os.getenv('USERPROFILE') or os.getenv('HOME')
        self.tags = [
                      {'color': (232, 43, 30), 'size': 9, 'tag': u'C++'},
                      {'color': (200, 188, 107), 'size': 9, 'tag': u'i18n'},
                      {'color': (85, 122, 102), 'size': 32, 'tag': u'Python'},
                      {'color': (69, 54, 37), 'size': 13, 'tag': u'Javascript'},
                      {'color': (69, 54, 37), 'size': 15, 'tag': u'Ajax'},
                      {'color': (200, 188, 107), 'size': 4, 'tag': u'XML'},
                      {'color': (200, 188, 107), 'size': 13, 'tag': u'QT'},
                      {'color': (200, 188, 107), 'size': 11, 'tag': u'CSS'},
                      {'color': (160, 182, 136), 'size': 7, 'tag': u'Mysql'},
                      {'color': (232, 43, 30), 'size': 12, 'tag': u'PostgreSQL'},
                      {'color': (69, 54, 37), 'size': 11, 'tag': u'HTML'},
                      {'color': (200, 188, 107), 'size': 9, 'tag': u'Teaching'},
                      {'color': (160, 182, 136), 'size': 27, 'tag': u'Django'},
                      {'color': (160, 182, 136), 'size': 11, 'tag': u'SQL'},
                      {'color': (232, 43, 30), 'size': 25, 'tag': u'Linux'},
                      {'color': (232, 43, 30), 'size': 14, 'tag': u'Java'},
                      {'color': (85, 122, 102), 'size': 19, 'tag': 'Design'},
        ]
        self.wordcounts = {
            u'C++' : 30,
            u'i18n' : 40,
            u'Python' : 100,
            u'Javascript' : 70,
            u'Ajax' : 50,
            u'XML' : 40,
            u'QT' : 20, 
            u'CSS' : 30,
            u'Mysql' : 30,
            u'PostgreSQL' : 35,
            u'HTML' : 55,
            u'Teaching' : 60,
            u'Django' : 22,
            u'SQL' : 77,
            u'Linux' : 59,
            u'Java' : 47,
        }

    def test_make_tags(self):
        self.mtags =  make_tags(self.wordcounts)
        print self.mtags
        create_tag_image(self.mtags, os.path.join(self.home, 'cloud_mtags.png'), size=(600, 500), background=(255, 255, 255, 255), vertical=True, crop=True, fontname='fonts/Arial.ttf', fontzoom=3)

    def test_create_tag_image(self):
        start = time.time()
        create_tag_image(self.tags, os.path.join(self.home, 'cloud.png'), size=(600, 500), background=(255, 255, 255, 255), vertical=True, crop=True, fontname='fonts/Arial.ttf', fontzoom=3)
        print "Duration: %d sec" % (time.time() - start)

    def test_create_tag_image_rect(self):
        home = os.getenv('USERPROFILE') or os.getenv('HOME')
        start = time.time()
        create_tag_image(self.tags, os.path.join(home, 'cloud_rect.png'), size=(300, 400), background=(255, 255, 255, 255), vertical=False, crop=False, rectangular=True, fontname='fonts/Arial.ttf', fontzoom=3)
        print "Duration: %d sec" % (time.time() - start)

    def test_create_html_data(self):
        """
        HTML code sample
        """
        data = create_html_data(self.tags, size=(600, 400), fontname='fonts/Arial.ttf', fontzoom=3)
        print '\nCSS\n'
        for style in data['css']:
            print style

        print '\nHTML\n'
        for link in data['links']:
            print '<a class="tag %(cls)s" href="#" style="top: %(top)dpx; left: %(left)dpx; font-size: %(size)dpx;">%(tag)s</a>' % link

if __name__ == "__main__":
    unittest.main()
