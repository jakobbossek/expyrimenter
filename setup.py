import setuptools

setuptools.setup(
    name = 'expyrimenter',
    version = '1.0.0',
    author = 'Jakob Bossek',
    author_email = 'j.bossek@gmail.com',
    description = 'Easy management of parallel commputing jobs using different parallelisation backends.',
    url = 'https://github.com/jakobbossek/expyrimenter/',
    # tell PyPi that we use markdown and not RestructuredText
    packages = setuptools.find_packages(exclude = ['tests']),
    python_requires = '>=3.7',
    # py_modules = ['randvec'],
    # package_dir = {},
    # make it easy for users to find the package
    # (see https://pypi.org/classifiers/)
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        # 'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    # for production dependencies
    install_requires = [],
    # for optional (development) requirements
    extras_require = {
        'dev': [
            'pytest >=3.7',
        ]
    },
)
