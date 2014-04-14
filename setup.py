""" Python Brainfuck Interpreter - Setup """
from setuptools import setup

setup(
    description='Python Brainfuck Interpreter',
    author='Wesley Spikes',
    author_email='wesley.spikes@gmail.com',
    version=0.1,
    packages=['pyfuck'],
    name='pyfuck',
    entry_points={
        'console_scripts': {
            'pyfuck = pyfuck.cli:main'
        }
    }
)
