import os
from distutils.core import setup

# sync with __init__.py
version = '0.1'

setup(
    name="dyn",
    version=version,
    keywords=["dynect", "api", "dns"],
    long_description=open(os.path.join(os.path.dirname(__file__),"README"), "r").read(),
    description="Dyn Python SDK",
    author="Cole Tuininga",
    author_email="ctuininga@dyn.com",
    url="https://github.com/dyninc/dyn-py"
    packages=['dyn'],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: Software Development :: Libraries', 
    ],
)
