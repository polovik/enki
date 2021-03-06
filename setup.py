#!/usr/bin/env python

import os
import sys
import pkgutil

""" setuptools ignores my .desktop and .cfg files
try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup
"""
from distutils.core import setup

from enki.core.defines import PACKAGE_NAME, PACKAGE_VERSION, PACKAGE_URL

def _checkDepencencies():
    """Check if 3rdparty software is installed in the system.
    Notify user, how to install it
    """
    _SEE_SITE_PLAIN = 'See http://enki-editor.org/install-sources.html'
    ok = True
    try:
        import PyQt4
    except ImportError, ex:
        print 'Failed to import Qt4 python bindings:'
        print '\t' + str(ex)
        ok = False

    try:
        import PyQt4.Qsci
    except ImportError, ex:
        print "Failed to import QScintilla 2 python bindings:"
        print '\t' + str(ex)
        ok = False

    try:
        import pyparsing
    except ImportError, ex:
        print "Failed to import pyparsing:"
        print '\t' + str(ex)
        ok = False
    
    if not ok:
        print 'See http://enki-editor.org/install-sources.html'

    return ok

"""hlamer: A bit hacky way to exclude desktop files from distribution,
but, I don't know how to do it better in crossplatform way
"""
def _isWinDist():
    for arg in sys.argv:
        if arg.startswith('--format') and \
           ('wininst' in arg or \
            'msi' in arg):
               return True
    return False

"""Install .desktop and .xpm and .desktop only on unixes
hlamer: We should use relative pathes here, without /usr/, so it will be installed to
/usr/local/share with setup.py and to /usr/share with Debian packages.
BUT KDE4 on Suse 12.02 ignores data in /usr/local/share, and, probably, some other systems do
Therefore Enki always installs its .desktop and icons to /usr/share
"""
if (('install' in sys.argv or \
     'install_data' in sys.argv) and \
        os.name != 'posix') or \
    'bdist' in sys.argv and _isWinDist() or \
    'bdist_winints' in sys.argv or \
    'bdist_msi' in sys.argv:
        data_files = []
else:
    data_files=[('/usr/share/applications/', ['enki.desktop']),
                ('/usr/share/pixmaps/', ['icons/logo/48x48/enki.png']),
                ('/usr/share/icons/hicolor/32x32/apps', ['icons/logo/32x32/enki.png']),
                ('/usr/share/icons/hicolor/48x48/apps', ['icons/logo/48x48/enki.png']),
                ('/usr/share/icons/hicolor/scalable/apps', ['icons/logo/enki.svg'])
                ]

classifiers = ['Development Status :: 3 - Alpha',
               'Environment :: X11 Applications :: Qt',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: GNU General Public License (GPL)',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Topic :: Software Development',
               'Topic :: Text Editors :: Integrated Development Environments (IDE)'
               ]

long_description = \
"""Some of features:

 * Syntax highlighting for more than 30 languages
 * Bookmarks
 * Search and replace functionality for files and directories. Regular expressions are supported
 * File browser
 * Autocompletion, based on document contents
 * Hightly configurable
"""

if 'install' in sys.argv and \
    not '--force' in sys.argv:
        if not _checkDepencencies():
            sys.exit(-1)

packages=['enki',
          'enki/core',
          'enki/lib',
          'enki/widgets',
          'enki/plugins',
          'enki/resources']

package_data={'enki' : ['ui/*.ui',
                           'config/*.json']
             }

for loader, name, ispkg in pkgutil.iter_modules(['enki/plugins']):
    if ispkg:
        packages.append('enki/plugins/' + name)
        package_data['enki'].append('plugins/%s/*.ui' % name)


setup(  name=PACKAGE_NAME.lower(),
        version=PACKAGE_VERSION,
        description='Simple programmers text editor',
        long_description=long_description,
        author='Andrei Kopats',
        author_email='hlamer@tut.by',
        url=PACKAGE_URL,
        download_url='https://github.com/hlamer/enki/tags',
        packages=packages,
        package_data=package_data,
        scripts=['bin/enki'],
        data_files=data_files,
        classifiers=classifiers,
        license='gpl2',
        requires=['pyparsing']
        )
