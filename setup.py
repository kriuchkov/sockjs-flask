import setuptools

setuptools.setup(
    name="sockjs-flask",
    version="0.2.0",
    url="https://github.com/borntyping/cookiecutter-pypackage-minimal",

    author="Kryuchkov Nikita",
    author_email="pycodi@hotmail.com",

    description="SockJs for Flask",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[
        'gevent',
        'gevent-websocket',
        'werkzeug',
        'flask',
        'multidict',
    ],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
