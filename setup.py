from distutils.core import setup
import codecs
import os

if os.path.exists("README.rst"):
    long_description = codecs.open("README.rst", "r", "utf-8").read()
else:
    long_description = "See http://pypi.python.org/pypi/pytagcloud/"

setup(
    name = 'pytagcloud',
    version = '0.3.5',
    description = "Create beautiful tag clouds as images or HTML",
    long_description = long_description,
    author = 'Reto Aebersold',
    author_email = 'aeby@atizo.com',
    url = 'https://github.com/atizo/PyTagCloud',    
    packages = ['pytagcloud', 'pytagcloud.lang'],
    package_data = {'pytagcloud': ['fonts/*.*'], 'pytagcloud.lang': ['fonts/*.*', 'stop/*']},
    platforms = ["any"],
    license = "BSD",
    classifiers = [
                   'Development Status :: 4 - Beta',
                   'License :: OSI Approved :: BSD License',
                   'Topic :: Multimedia :: Graphics',
                   'Topic :: Text Processing :: Fonts',
                   'Topic :: Text Processing :: Markup :: HTML',
                   'Intended Audience :: Developers',
                   'Environment :: Web Environment',
                   'Programming Language :: Python',
                   'Operating System :: OS Independent',
                   'Operating System :: POSIX',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: MacOS :: MacOS X'
                   ],
)