##############################################################################
#
# Copyright (c) 2010 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except:
    README = ''
    CHANGES = ''

tests_extras = ['nose', 'coverage']
docs_extras = ['Sphinx', 'repoze.sphinx.autointerface']

setup(name='venusian',
      version='1.0a5',
      description='A library for deferring decorator actions',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: Jython",
          ],
      keywords='web wsgi zope',
      author="Chris McDonough, Agendaless Consulting",
      author_email="pylons-devel@googlegroups.com",
      url="http://pylonsproject.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      extras_require = {
          'testing':tests_extras,
          'docs':docs_extras,
          },
      tests_require = [],
      install_requires = [],
      # Normal "setup.py test" can't support running the venusian tests under
      # py 2.4 or 2.5; when it scans the 'classdecorators' fixture, it
      # barfs.  We can't depend on nose in setup_requires here because folks use
      # this under "pip bundle" which does not support setup_requires.
      # So you just have to know to install nose and run "setup.py nosetests"
      # rather than setup.py test.
      test_suite='venusian',
      entry_points = """\
      """
      )

