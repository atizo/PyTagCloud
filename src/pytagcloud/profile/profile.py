from pytagcloud import make_tags, create_tag_image, LAYOUT_MIX
from pytagcloud.colors import COLOR_SCHEMES
from pytagcloud.lang.counter import get_tag_counts
import cProfile
import os
import pstats

tags = None
test_output = None

def init():
    global tags
    global test_output
    
    home_folder = os.getenv('USERPROFILE') or os.getenv('HOME')
    test_output = os.path.join(home_folder, 'pytagclouds')
    
    if not os.path.exists(test_output):
        os.mkdir(test_output )         
    
    hound = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../test/pg2852.txt'), 'r')
    tags = make_tags(get_tag_counts(hound.read())[:50], maxsize=120, colors=COLOR_SCHEMES['audacity'])

def run():
    create_tag_image(tags, os.path.join(test_output, 'cloud_profile.png'), size=(1280, 900), background=(0, 0, 0, 255), layout=LAYOUT_MIX, crop=True, fontname='Lobster', fontzoom=1)

if __name__ == '__main__':
    
    init()

    cProfile.run('run()', 'cloud.profile')
    p = pstats.Stats('cloud.profile')
    p.strip_dirs().sort_stats(-1).print_stats()    
    p.sort_stats('time').print_stats(10)
    p.print_stats()