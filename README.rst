SockJS server for Flask
============

.. image:: https://img.shields.io/pypi/v/sockjs-flask.svg
    :target: https://pypi.python.org/pypi/sockjs-flask
    :alt: Latest PyPI version

.. image:: https://travis-ci.org/borntyping/cookiecutter-pypackage-minimal.png
   :target: https://travis-ci.org/borntyping/cookiecutter-pypackage-minimal
   :alt: Latest Travis CI build status

`sockjs` is a `SockJS <http://sockjs.org>`_ integration for Flask.  SockJS interface
is implemented as a flask route. Its possible to create any number of different sockjs routes, ie `/sockjs/*` or `/mycustom-sockjs/*`.
You can provide different session implementation and management for each sockjs route.

Usage
-----

Client side code::

  <script src="//cdnjs.cloudflare.com/ajax/libs/sockjs-client/1.1.4/sockjs.js"></script>
  <script>
      var sock = new SockJS('http://localhost:5000/sockjs');

      sock.onopen = function() {
        console.log('open');
      };

      sock.onmessage = function(obj) {
        console.log(obj);
      };

      sock.onclose = function() {
        console.log('close');
      };
  </script>


Installation
------------

Requirements
^^^^^^^^^^^^

Compatibility
-------------

Licence
-------

Authors
-------

`sockjs-flask` was written by `Kryuchkov Nikita <pycodi@hotmail.com>`_.
