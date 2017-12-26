import os
from setuptools import setup, find_packages

__author__ = 'Josue Kouka'
__email__ = 'josuebrunel@gmail.com'
__version__ = '0.2'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


requirements = read('requirements.txt').splitlines()

setup(
    name="pysxm",
    version=__version__,
    description="Simple and extensible xml python marsheller",
    long_description=read("README.rst"),
    author=__author__,
    author_email=__email__,
    url="https://github.com/josuebrunel/pysxm",
    download_url="https://github.com/josuebrunel/pysxm/archive/{0}.tar.gz".format(__version__),
    keywords=['xml', 'data binding', 'data', 'binding'],
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License'
    ],
    platforms=['Any'],
    license='MIT',
    install_requires=requirements
)
