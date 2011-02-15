from setuptools import setup
import pkg_resources
import autocomplete


def get_metadata_version():
    """
    Tries to get the version from the django_autocomplete.egg-info directory.
    """
    try:
        pkg = list(pkg_resources.find_distributions('.', True))[0]
    except IndexError:
        return autocomplete.__version__
    return pkg.version

version = autocomplete.get_mercurial_version() or get_metadata_version()

setup(
    name = 'django-autocomplete',
    version = version,
    description = 'autocomplete utilities for django',
    author = 'Germano Gabbianelli',
    author_email = 'tyrion.mx@gmail.com',
    url = 'http://bitbucket.org/tyrion/django-autocomplete',
    download_url = 'http://bitbucket.org/tyrion/django-autocomplete/downloads',
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
