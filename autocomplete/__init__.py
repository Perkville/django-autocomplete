def get_installed_version(version='unknown'):
    import os
    import pkg_resources
    path = os.path.join(__path__[0], os.pardir)
    try:
        pkg = list(pkg_resources.find_distributions(path, True))[0]
    except IndexError:
        return version
    return pkg.version


def get_version(version='unknown'):
    import os
    path = os.path.join(__path__[0], os.pardir)
    try:
        from mercurial.hg import repository
        from mercurial.ui import ui
        from mercurial import node, error
    except ImportError:
        return get_installed_version(version)
    try:
        repo = repository(ui(), path)
    except error.RepoError:
        return get_installed_version(version)
    tip = repo.changelog.tip()
    rev = repo.changelog.rev(tip)
    return '%s.dev%d' % (version, rev)

__version__ = get_version('1.0')
