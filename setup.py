import os, re, sys, shutil
from setuptools import setup


basedir = os.path.abspath(os.path.dirname(__file__))
metapath = os.path.join(basedir, 'btbot', '__init__.py')

with open(metapath, 'r', encoding='utf-8') as f:
    metadata = f.read()

def get_meta(meta):
    meta_match = re.search(
        rf'^__{meta}__\s*=\s*[\'\"]([^\'\"]*)[\'\"]',
        metadata, re.MULTILINE)
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError(f'Unable to find __{meta}__ string.')

if os.path.exists(os.path.join(basedir, 'requirements.txt')):
    with open(os.path.join(basedir, 'requirements.txt')) as f:
        required = f.read().splitlines()
else:
    required = None

if len(sys.argv) < 2:
    sys.argv.append('install')
setup(name='btbot',
      version=get_meta('version'),
      license=get_meta('license'),
      description=get_meta('description'),
      author=get_meta('author'),
      author_email=get_meta('email'),
      url=get_meta('url'),
      packages=['btbot'],
      install_requires=required)

r = re.compile(r'.*\.egg-info$|^build$|^dist$')
for dir in os.listdir():
    if r.match(dir):
        shutil.rmtree(dir, ignore_errors=True)
