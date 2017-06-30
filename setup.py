#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

module_name = 'vk_messages_bot'


def get_version(version_tuple):
    # additional handling of a,b,rc tags, this can be simpler depending on your versioning scheme
    if not isinstance(version_tuple[-1], int):
        return '.'.join(
            map(str, version_tuple[:-1])
        ) + version_tuple[-1]
    return '.'.join(map(str, version_tuple))


# path to the packages __init__ module in project source tree
init = os.path.join(os.path.dirname(__file__), module_name, '__init__.py')

version_line = list(
    filter(lambda l: l.startswith('VERSION'), open(init))
)[0]

# VERSION is a tuple so we need to eval its line of code.
# We could simply import it from the package but we
# cannot be sure that this package is importable before
# finishing its installation
VERSION = get_version(eval(version_line.split('=')[-1]))

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "python-telegram-bot",
    "requests",
    "simplejson",
    "jsonpickle",
]

setup(
    name=module_name,
    version=VERSION,
    description="Telegram Bot that lets you receive messages from VK and reply to them",
    long_description=readme + '\n\n' + history,
    author="Roman Zaynetdinov",
    author_email='zaynetro@gmail.com',
    url='https://github.com/zaynetro/vk-messages-bot',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires='~=3.4',
    license="MIT",
    zip_safe=True,
    keywords='vk vkontakte messages messenger telegram forward bot',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'vk-messages-bot={}.__main__:main'.format(module_name),
        ],
    },
)
