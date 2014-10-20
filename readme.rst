pytest-growl
------------
 :Author: Anthony Long
 :Date: 20/10/2014
 :Version: 0.1

This plugin sends growl notifications when your test session begins and ends, along with result counts in a short format.

.. image:: screenshot.png

The theme displayed in the image is included if you wish to use it.


Installation
____________

Install with pip::

  pip install pytest-growl


Usage
_____

Invoke with the ``--growl`` option. Unfortunately py.test will not accept the option without a value::

  py.test --growl=GROWL
