import setuptools

setuptools.setup(
    name="sockjs-flask",
    version="0.1.9",
    url="https://github.com/borntyping/cookiecutter-pypackage-minimal",

    author="Kryuchkov Nikita",
    author_email="pycodi@hotmail.com",

    description="SockJs for Flask",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[
        'gevent>=1.2.2',
        'gevent-websocket>=0.10.1',
        'werkzeug',
        'flask',
        'multidict',
        'eventwebsocket'
    ],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
