# SPDX-FileCopyrightText: 2018 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_mprls`
====================================================

CircuitPython library to support Honeywell MPRLS digital pressure sensors

* Author(s): ladyada

Implementation Notes
--------------------

**Hardware:**

* Adafruit `Adafruit MPRLS Ported Pressure Sensor Breakout
  <https://www.adafruit.com/product/3965>`_ (Product ID: 3965)

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

"""

# imports

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_MPRLS.git"


import time
from adafruit_bus_device.i2c_device import I2CDevice
from digitalio import Direction
from micropython import const

_MPRLS_DEFAULT_ADDR = const(0x18)


class MPRLS:
    """
    Driver base for the MPRLS pressure sensor

    :param ~busio.I2C i2c_bus: The I2C bus the MPRLS is connected to
    :param int addr: The I2C device address. Defaults to :const:`0x18`
    :param ~microcontroller.Pin reset_pin: Optional ``digitalio.pin`` for hardware resetting
    :param ~microcontroller.Pin eoc_pin: Optional ``digitalio pin``
                                         for getting End Of Conversion signal
    :param float psi_min: The minimum pressure in PSI, defaults to :const:`0`
    :param float psi_max: The maximum pressure in PSI, defaults to :const:`25`

    **Quickstart: Importing and using the MPRLS**

        Here is an example of using the :class:`MPRLS` class.
        First you will need to import the libraries to use the sensor

        .. code-block:: python

            import board
            import adafruit_mprls

        Once this is done you can define your `board.I2C` object and define your sensor object

        .. code-block:: python

            i2c = board.I2C()  # uses board.SCL and board.SDA
            mpr = adafruit_mprls.MPRLS(i2c, psi_min=0, psi_max=25)

        Now you have access to the :attr:`pressure` attribute

        .. code-block:: python

            pressure = mpr.pressure

    """

    def __init__(
        self,
        i2c_bus,
        *,
        addr=_MPRLS_DEFAULT_ADDR,
        reset_pin=None,
        eoc_pin=None,
        psi_min=0,
        psi_max=25
    ):
        # Init I2C
        self._i2c = I2CDevice(i2c_bus, addr)
        self._buffer = bytearray(4)

        # Optional hardware reset pin
        if reset_pin is not None:
            reset_pin.direction = Direction.OUTPUT
            reset_pin.value = True
            reset_pin.value = False
            time.sleep(0.01)
            reset_pin.value = True
        time.sleep(0.005)  # Start up timing

        # Optional end-of-conversion pin
        self._eoc = eoc_pin
        if eoc_pin is not None:
            self._eoc.direction = Direction.INPUT

        if psi_min >= psi_max:
            raise ValueError("Min PSI must be < max!")
        self._psimax = psi_max
        self._psimin = psi_min
        # That's pretty much it, there's no ID register :(

    @property
    def pressure(self):
        """The measured pressure, in hPa"""
        return self._read_data()

    def _read_data(self):
        """Read the status & 24-bit data reading"""
        self._buffer[0] = 0xAA
        self._buffer[1] = 0
        self._buffer[2] = 0
        with self._i2c as i2c:
            # send command
            i2c.write(self._buffer, end=3)
            # ready busy flag/status
            while True:
                # check End of Convert pin first, if we can
                if self._eoc is not None:
                    if self._eoc.value:
                        break
                # or you can read the status byte
                i2c.readinto(self._buffer, end=1)
                if not self._buffer[0] & 0x20:
                    break
            # no longer busy!
            i2c.readinto(self._buffer, end=4)

        # check other status bits
        if self._buffer[0] & 0x01:
            raise RuntimeError("Internal math saturation")
        if self._buffer[0] & 0x04:
            raise RuntimeError("Integrity failure")

        # All is good, calculate the PSI and convert to hPA
        raw_psi = (self._buffer[1] << 16) | (self._buffer[2] << 8) | self._buffer[3]
        # use the 10-90 calibration curve
        psi = (raw_psi - 0x19999A) * (self._psimax - self._psimin)
        psi /= 0xE66666 - 0x19999A
        psi += self._psimin
        # convert PSI to hPA
        return psi * 68.947572932
