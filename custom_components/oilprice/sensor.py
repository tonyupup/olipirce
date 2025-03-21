import re
import logging
import voluptuous as vol
import datetime
import aiohttp
import async_timeout
from bs4 import BeautifulSoup
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME, CONF_REGION
from homeassistant.helpers.aiohttp_client import async_get_clientsession

__version__ = '0.1.0'
_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(hours=8)
ICON = 'mdi:gas-station'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_REGION): cv.string,
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the oil price sensor."""
    _LOGGER.info("Setting up oil price sensor")
    name = config[CONF_NAME]
    region = config[CONF_REGION]

    session = async_get_clientsession(hass)
    async_add_entities([OilPriceSensor(name, region, session)], True)

class OilPriceSensor(Entity):
    """Representation of an Oil Price Sensor."""

    def __init__(self, name: str, region: str, session):
        """Initialize the sensor."""
        self._name = name
        self._region = region
        self._session = session
        self._state = None
        self._entries = {}

    async def async_update(self):
        """Fetch the latest oil price data."""
        _LOGGER.info("Updating oil price info from http://www.qiyoujiage.com/")
        url = f'http://www.qiyoujiage.com/{self._region}.shtml'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
        }

        try:
            async with async_timeout.timeout(10):
                async with self._session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    text = await response.text()

                    soup = BeautifulSoup(text, "lxml")
                    dls = soup.select("#youjia > dl")
                    self._state = soup.select("#youjiaCont > div")[1].contents[0].strip()

                    for dl in dls:
                        k = re.search("\d+", dl.select('dt')[0].text).group()
                        self._entries[k] = dl.select('dd')[0].text
                    self._entries["update_time"] = datetime.datetime.now().strftime('%Y-%m-%d')
                    self._entries["tips"] = soup.select("#youjiaCont > div:nth-of-type(2) > span")[0].text.strip()

        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching data: %s", err)
            self._state = None
            self._entries = {}
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout fetching data")
            self._state = None
            self._entries = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return ICON

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._entries