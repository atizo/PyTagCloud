# -*- coding: utf-8 -*-
import re
from pytagcloud.lang.stopwords import StopWords
from operator import itemgetter
from collections import defaultdict

def get_tag_counts(text):
    """
    Search tags in a given text. The language detection is based on stop lists.
    This implementation is inspired by https://github.com/jdf/cue.language. Thanks Jonathan Feinberg.
    """
    words = map(lambda x:x.lower(), re.findall(r"[\w']+", text, re.UNICODE))
    
    s = StopWords()     
    s.load_language(s.guess(words))
    
    counted = defaultdict(int)
    
    for word in words:
        if not s.is_stop_word(word) and len(word) > 1:
            counted[word] += 1
      
    return sorted(counted.iteritems(), key=itemgetter(1), reverse=True)
    
