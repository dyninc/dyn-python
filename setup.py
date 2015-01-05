from distutils.core import setup
from dyn import __version__

with open('README.rst') as f:
    readme = f.read()
with open('HISTORY.rst') as f:
    history = f.read()
with open('LICENSE') as f:
    license_file = f.read()
with open('requirements.txt') as f:
    requires = [line.strip() for line in f if line.strip()]
with open('test-requirements.txt') as f:
    tests_requires = [line.strip() for line in f if line.strip()]

setup(
    name='dyn',
    version=__version__,
    keywords=['dyn', 'api', 'dns', 'email', 'dyndns', 'dynemail'],
    long_description='\n\n'.join([readme, history, license_file]),
    description='Dyn REST API wrapper',
    author='Jonathan Nappi, Cole Tuininga',
    author_email='jnappi@dyn.com',
    url='https://github.com/dyninc/dyn-python',
    packages=['dyn', 'dyn/tm', 'dyn/mm', 'dyn/tm/services'],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: Software Development :: Libraries', 
    ],
    install_requires=requires,
    tests_require=tests_requires,
)
