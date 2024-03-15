#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(
    name='cardroom',
    version='0.0.1.dev13',
    description='A Django application for poker tournament and table management',
    long_description=open('README.rst').read(),
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
        'channels',
        'django',
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
    install_requires=[
        'channels[daphne]>=4.0.0,<5',
        'Django>=4.2.9,<5',
        'djangorestframework>=3.14.0,<4',
        'pokerkit~=0.4.10',
    ],
    python_requires='>=3.11',
    package_data={'cardroom': ['py.typed', 'static/**/*', 'templates/**/*']},
)
