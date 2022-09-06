# http://www.python.org/dev/peps/pep-0396/
__version__ = '5.0.18'
# backward compatibility
version = tuple(int(x) for x in __version__.split('.'))
majorVersionId = version[0]
