from setuptools import setup, find_packages

# Enforce python 3
import sys
if sys.version_info < (3,0):
    sys.exit('Sorry, Python < 3.0 is not supported')

# Read requirements.txt as canonical dependencies
with open("requirements.txt") as data:
    install_requires = [line for line in filter(lambda x: x, data.read().split("\n"))]

# To link in these files (for development) directly just run "pip install -e ."
setup(name="sourcerer",
    version="0.1",
    description="Source control for your source controlled folders",
    author="Steve Armstrong",
    author_email="steve@horsefire.com",
    url="https://github.com/stevearm/sourcerer.git",
    licence="Apache Software License",
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "srcr = sourcerer.cmd:main",
        ],
    },
)
