"""
Setup скрипт для создания исполняемого файла Helper.exe
"""
from setuptools import setup, find_packages

setup(
    name='Helper',
    version='1.0.0',
    description='Helper - приложение для управления шаблонами текстов',
    author='teja1337',
    packages=find_packages(),
    install_requires=[
        'customtkinter>=5.2.2',
        'pillow>=10.1.0',
    ],
    entry_points={
        'console_scripts': [
            'helper=main:main',
        ],
    },
    python_requires='>=3.9',
)
