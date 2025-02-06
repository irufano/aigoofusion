from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='aigoofusion', 
    version='0.1.3',
    packages=find_packages(),
    description='`AIGooFusion` is a framework for developing applications by large language models (LLMs)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='irufano',
    author_email='irufano.official@gmail.com',
    url='https://github.com/irufano/aigoofusion',  
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)