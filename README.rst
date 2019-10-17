Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-mprls/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/mprls/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://discord.gg/nBQh6qu
    :alt: Discord

.. image:: https://travis-ci.com/adafruit/Adafruit_CircuitPython_MPRLS.svg?branch=master
    :target: https://travis-ci.com/adafruit/Adafruit_CircuitPython_MPRLS
    :alt: Build Status

CircuitPython library to support Honeywell MPRLS digital pressure sensors.

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Usage Example
=============

.. code-block:: python

	import time
	import board
	import busio
	import adafruit_mprls

	i2c = busio.I2C(board.SCL, board.SDA)

	# Simplest use, connect to default over I2C
	mpr = adafruit_mprls.MPRLS(i2c, psi_min=0, psi_max=25)


	while True:
	    print((mpr.pressure,))
	    time.sleep(1)

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_MPRLS/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
