from distutils.core import setup

with open('README.rst') as stream:
    long_description = stream.read().decode('utf-8')

setup(
    name = 'pytagcloud',
    version = '0.3.2',
    description = "Create beautiful tag clouds as images or HTML",
    long_description = long_description,
    author = 'Reto Aebersold',
    author_email = 'aeby@atizo.com',
    url = 'https://github.com/atizo/PyTagCloud',    
    packages = ['pytagcloud', 'pytagcloud.lang'],
    package_dir = {'pytagcloud': 'src/pytagcloud'},
    package_data = {'pytagcloud': ['fonts/*.*']},
    classifiers = [
                   'Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   ],
)