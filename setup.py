from setuptools import setup
import re

# Get version from init.py, adapted from
# https://github.com/kennethreitz/requests/blob/master/setup.py#L32
with open('lnextract/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

setup(
    name='lnextract',
    version=version,
    author='Luke Emery-Fertitta',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database',
    ],

    packages=[
        'lnextract',
    ],
    entry_points={
        'console_scripts': [
            'lnextract = lnextract.__main__:main'
        ]
    },
    install_requires=[
        'pandas',
        'nltk',
    ],
    extras_require={
        'igraph': ['python-igraph'],
    },
)