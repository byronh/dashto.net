#!/usr/bin/env python

import setuptools
from setuptools.command.test import test as test_command


requires = [
    'aioredis==0.1.5',
    'alembic',
    'cryptacular',
    'psycopg2',
    'pyramid',
    'pyramid_jinja2',
    'pyramid_debugtoolbar',
    'pyramid_redis_sessions',
    'pyramid_storage',
    'pyramid_tm',
    'pyramid_wtforms',
    'sqlalchemy',
    'transaction',
    'waitress',
    'webhelpers',
    'websockets',
    'zope.sqlalchemy',
]


class PyTest(test_command):
    """ Use py.test as the default test runner. """
    def __init__(self, dist, **kw):
        super().__init__(dist, **kw)
        self.test_args = None
        self.test_suite = None

    def finalize_options(self):
        test_command.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        pytest.main(self.test_args)


setuptools.setup(
    name='dashto',
    version='0.0',
    description='dashto.net',
    author='Byron Henze',
    author_email='byronh@gmail.com',
    url='https://github.com/byronh/dashto.net',
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    install_requires=requires,
    dependency_links=['http://github.com/aio-libs/aioredis/tarball/master#egg=aioredis-0.1.5'],
    entry_points="""
        [paste.app_factory]
        main = dashto:main
        [console_scripts]
        """
)
