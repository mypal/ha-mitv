"""Add support for the Xiaomi TVs."""
import logging
from threading import Thread

import time
import voluptuous as vol

from homeassistant.const import CONF_HOST, CONF_NAME, STATE_OFF, STATE_ON
import homeassistant.helpers.config_validation as cv
from homeassistant.components.binary_sensor import (BinarySensorDevice, PLATFORM_SCHEMA, DEVICE_CLASS_POWER)

DEFAULT_NAME = "mitv state"

_LOGGER = logging.getLogger(__name__)

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
    # add_entities(MitvBinarySensor(tv, DEFAULT_NAME) for tv in Discover().scan())
    add_entities([MitvBinarySensor(name, host)])


class MitvBinarySensor(BinarySensorDevice):
    """representation of a Demo binary sensor."""

    def __init__(self, name, host):
        """Initialize the demo sensor."""
        self._name = name
        self._host = host
        self._state = False
        self._sensor_type = DEVICE_CLASS_POWER
        self._thread = QueryThread(self)
        self._thread.start()
        _LOGGER.debug('%s(%s) registered' % (name, host))

    def update(self, state):
        _LOGGER.debug('%s\'s state changes to %s' % (self.name, state))
        self._state = state
        self.schedule_update_ha_state()

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return self._sensor_type

    @property
    def should_poll(self):
        """No polling needed for a demo binary sensor."""
        return False

    @property
    def name(self):
        """Return the name of the binary sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state

    @property
    def host(self):
        return self._host


class QueryThread(Thread):
    def __init__(self, mitv: MitvBinarySensor):
        super().__init__()
        self._mitv = mitv
        self._delay = 5

    def run(self) -> None:
        from pymitv import Discover
        while True:
            try:
                new = Discover().check_ip(self._mitv.host)
                _LOGGER.debug('%s\'s state is %s', (self._mitv.name, new))
                if new != self._mitv.is_on:
                    self._mitv.update(new)
            except Exception:
                _LOGGER.debug('exception occurred: %s' % Exception)
            time.sleep(self._delay)
