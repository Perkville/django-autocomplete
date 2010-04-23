Installation
============

Installing the stable version
-----------------------------

You can install Django AutoComplete with `pip`_ or `easy_install`_::

    pip install django-autocomplete
    easy_install django-autocomplete

Alternatively you can download the `last stable release`_ from the Python
Package Index and run ``python setup.py install`` from a terminal to
install it.

.. _`pip`: http://pypi.python.org/pypi/pip/
.. _`easy_install`: http://pypi.python.org/pypi/setuptools/
.. _`last stable release`: http://pypi.python.org/pypi/django-autocomplete/

Installing the development version
----------------------------------

To get the latest updates and bug fixes install the developement version.
You can do this by cloning the Mercurial repository with::

    $ hg clone http://bitbucket.org/tyrion/django-autocomplete/

Then you have to put the :file:`autocomplete` directory under your
``sys.path``.

To update your local repository run the following commands from the
:file:`django-autocomplete` directory::

    $ hg pull
    $ hg update

Serving the media files
-----------------------

In order to work properly Django AutoComplete needs some javascript files.
These files are contained in the :file:`autocomplete/media` directory and
*must* be served from your ``{{ MEDIA_URL }}``.

.. note::

    Remember to put ``{{ form.media }}`` in your template's <head> otherwise
    the Javascript won't be loaded.

.. seealso::

    `Static Files <http://docs.djangoproject.com/en/dev/howto/static-files/>`_
        How to correctly serve static files.

    :ref:`media-files-configuration`
        How to customize the media files of Django AutoComplete.


.. _`How to serve static files`: http://docs.djangoproject.com/en/dev/howto/static-files/
