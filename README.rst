=============
 PyTagCloud
=============

PyTagCloud let you create simple tag clouds inspired by http://www.wordle.net/

Currently, the following output formats have been written and are working:

- PNG images
- HTML/CSS code

If you have ideas for other formats please let us know.

Installation
============

You can install PyTagCloud either via the Python Package Index (PyPI) or from source.

To install using `pip`::

    $ pip install -U pytagcloud

To install using form source `download it <https://github.com/atizo/PyTagCloud/zipball/master>`_::

    $ python setup.py install

Requirements
------------

#. Install `pygame <http://www.pygame.org/download.shtml>`_ >= 1.9.1::

    $ apt-get install python-pygame
    
#. Install simplejson::

   $ pip install simplejson

Quick start
===========

You probably want to see some code by now, so here's an example:
::

    from pytagcloud import create_tag_image, make_tags
    from pytagcloud.lang.counter import get_tag_counts
    
    YOUR_TEXT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."

    tags = make_tags(get_tag_counts(), maxsize=120)
    
    create_tag_image(tags, 'cloud_large.png', size=(900, 600), fontname='Lobster')

More examples can be found in `test.py <https://github.com/atizo/PyTagCloud/blob/master/src/pytagcloud/test/tests.py>`_.

Example
=======
`Demo <https://www.atizo.com/docs/labs/cloud.html>`_

.. image:: https://github.com/atizo/PyTagCloud/raw/master/docs/example.png

