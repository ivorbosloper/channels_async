from setuptools import find_packages, setup
from channels_async import __version__

setup(
    name='channels_async',
    version=__version__,
    url='https://github.com/ivorbosloper/channels_async',
    author='Ivor Bosloper',
    author_email='ivorbosloper@gmail.com',
    description="",
    license='BSD',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=[
        'Django>=1.11',
        'channels>=1.1.5'
        'asgiref~=1.1',
    ],
    extras_require={
        'tests': [
            'coverage',
            'flake8>=2.0,<3.0',
            'isort',
        ],
        'tests:python_version < "3.0"': ['mock'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
    ],
)