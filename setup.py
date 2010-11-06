from setuptools import setup
import autocomplete

setup(
    name = 'django-autocomplete',
    version = autocomplete.__version__,
    description = 'autocomplete utilities for django',
    author = 'Germano Gabbianelli',
    author_email = 'tyrion.mx@gmail.com',
    url = 'http://bitbucket.org/tyrion/django-autocomplete2',
    download_url = 'http://bitbucket.org/tyrion/django-autocomplete2/downloads',
    packages = ['autocomplete'],
    include_package_data = True,
    classifiers = [
        'Development Status :: 4 - Beta', 
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
