import setuptools

setuptools.setup(
    name="sockjs-flask",
    version="0.3",
    url="https://github.com/pycodi/sockjs-flask",
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
        'kombu'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
