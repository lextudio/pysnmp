# http://www.python.org/dev/peps/pep-0396/
__version__ = "7.0.4"
# another variable is required to prevent semantic release from updating version in more than one place
main_version = __version__
# backward compatibility
# for beta versions, integer casting throws an exception, so string part must be cut off
if "beta" in __version__:
    main_version = __version__.split("-beta")[0]
version = tuple(int(x) for x in main_version.split("."))
major_version_id = version[0]
