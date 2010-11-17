__version__ = '1.0'

def get_installed_version():
    import pkg_resources
    try:
        autocomplete = pkg_resources.get_distribution('django-autocomplete')
    except pkg_resources.DistributionNotFound:
        return __version__
    return autocomplete.version

def get_version(installed=True):
    import os
    path = os.path.join(__path__[0], os.pardir)
    try:
        from mercurial.hg import repository
        from mercurial.ui import ui
        from mercurial import node, error

        repo = repository(ui(), path)
    except:
        if installed:
            return get_installed_version()
        return __version__
    tip = repo.changelog.tip()
    rev = repo.changelog.rev(tip)
    return '%s.dev%d' % (__version__, rev)
