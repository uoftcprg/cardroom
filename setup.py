#!/usr/bin/env python3

from setuptools import find_packages, setup

with open('README.rst', 'r') as file:
    long_description = file.read()

setup(
    name='cardroom',
    version='0.0.0',
    description='Poker tournament and table management library',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/uoftcprg/cardroom',
    author='University of Toronto Computer Poker Research Group',
    author_email='uoftcprg@outlook.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Education',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords=[
        'game',
        'game-development',
        'holdem-poker',
        'imperfect-information-game',
        'poker',
        'poker-engine',
        'poker-game',
        'poker-library',
        'poker-strategies',
        'python',
        'texas-holdem',
    ],
    project_urls={
        'Documentation': 'https://cardroom.readthedocs.io/en/latest/',
        'Source': 'https://github.com/uoftcprg/cardroom',
        'Tracker': 'https://github.com/uoftcprg/cardroom/issues',
    },
    packages=find_packages(),
    install_requires=['pokerkit~=0.3.0'],
    python_requires='>=3.11',
    package_data={'cardroom': ['py.typed']},
)
