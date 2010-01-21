Installation
============

You can install Django AutoComplete with `pip`_ or `easy_install`_::

    pip install django-autocomplete
    easy_install django-autocomplete

Alternatively you can download the `last stable release`_ from the Python
Package Index and run :command:`python setup.py install` from a terminal to
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

Getting the latest changes
^^^^^^^^^^^^^^^^^^^^^^^^^^
To update your local repository run the following commands from the
:file:`django-autocomplete` directory::

    $ hg pull
    $ hg update

