"""Add support for the Xiaomi TVs."""
import logging
from threading import Thread

import time
import voluptuous as vol
from datetime import timedelta

from homeassistant.const import CONF_HOST, CONF_NAME, STATE_OFF, STATE_ON
import homeassistant.helpers.config_validation as cv
from homeassistant.components.binary_sensor import (BinarySensorDevice, PLATFORM_SCHEMA, DEVICE_CLASS_POWER)
from pymitv import Discover

DEFAULT_NAME = "mitv state"

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=5)

# No host is needed for configuration, however it can be set.
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Xiaomi TV platform."""
    from pymitv import Discover

    # If a hostname is set. Discovery is skipped.
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    add_entities([MitvBinarySensor(name, host)], True)


class MitvBinarySensor(BinarySensorDevice):
    """representation of a Demo binary sensor."""

    def __init__(self, name, host):
        """Initialize the demo sensor."""
        self._name = name
        self._host = host
        self._state = False
        self._sensor_type = DEVICE_CLASS_POWER
        _LOGGER.debug('%s(%s) registered' % (name, host))

    def update(self):
        try:
            self._state = bool(Discover().check_ip(self._host))
            _LOGGER.debug('%s(%s) changes to %s' % (self.name, self._host, self._state))
        except Exception:
            _LOGGER.debug(Exception)

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return self._sensor_type

    @property
    def name(self):
        """Return the name of the binary sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state
