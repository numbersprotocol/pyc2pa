import subprocess

from setuptools import setup
from setuptools import find_packages


with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name='caitools',
    version='v1.0.0',
    description='Content Authenticity Initiative Tools.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/numbersprotocol.io/starling-cai',
    author='Numbers Inc.',
    author_email='dev@numbersprotocol.io',
    license='GPLv3',
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    keywords=['wheels'],
    packages=find_packages(exclude=['tests']),
    install_requires=[
        #'multibase',
        #'multihash',
        #'tox',
    ],
    python_requires='>=3',
    entry_points={
        'console_scripts': [
            'cai_tool=caitools.cai_tool:main',
        ]
    },
    test_suite='tests'
)