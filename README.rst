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

To install using `easy_install`::

    $ easy_install -U pytagcloud


Downloading and installing from source
--------------------------------------

Download the latest version of PyTagCloud from
http://pypi.python.org/pypi/pytagcloud/

You can install it by doing the following,::

    $ tar xfz pytagcloud-*.tar.gz
    $ cd pytagcloud-*/
    $ python setup.py build
    $ python setup.py install # as root

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
    
    YOUR_TEXT = "A tag cloud is a visual representation for text data, typically\
    used to depict keyword metadata on websites, or to visualize free form text."

    tags = make_tags(get_tag_counts(YOUR_TEXT), maxsize=80)
    
    create_tag_image(tags, 'cloud_large.png', size=(900, 600), fontname='Lobster')

    import webbrowser
    webbrowser.open('cloud_large.png') # see results

More examples can be found in `test.py <https://github.com/atizo/PyTagCloud/blob/master/src/pytagcloud/test/tests.py>`_.

Example
=======
`Demo <https://www.atizo.com/docs/labs/cloud.html>`_

.. image:: https://github.com/atizo/PyTagCloud/raw/master/docs/example.png

Contributing
============

Development of `pytagcloud` happens at Github: https://github.com/atizo/PyTagCloud

You are highly encouraged to participate in the development
of `pytagcloud`. If you don't like Github (for some reason) you're welcome
to send regular patches.
