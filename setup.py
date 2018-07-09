import os
import re
import codecs
from setuptools import setup


cwd = os.path.abspath(os.path.dirname(__file__))

def read(filename):
    with codecs.open(os.path.join(cwd, filename), 'rb', 'utf-8') as h:
        return h.read()

metadata = read(os.path.join(cwd, 'icobot', '__init__.py'))

def get_meta(meta):
    meta_match = re.search(
        r"""^__{meta}__\s+=\s+['\"]([^'\"]*)['\"]""".format(meta=meta),
       metadata, re.MULTILINE)
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError('Unable to find __{meta}__ string.'.format(meta=meta))

if os.path.exists('requirements.txt'):
    with open('requirements.txt') as f:
        required = f.read().splitlines()

setup(
    name='ICOBot',
    version=get_meta('version'),
    license=get_meta('license'),
    description=get_meta('description'),
    author=get_meta('author'),
    author_email=get_meta('email'),
    url=get_meta('url'),
    #packages=['icobot'],
    #install_requires=['python-twitter', 'google-api-python-client', 'pysocks',
    #                  'requests'],
    install_requires=required
)
