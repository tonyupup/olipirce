import re
import logging
import datetime
import aiohttp
import async_timeout
from bs4 import BeautifulSoup
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, CONF_NAME, CONF_REGION

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(hours=8)
ICON = 'mdi:gas-station'

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the sensor platform (YAML)."""
    async_add_entities([OilPriceSensor(config[CONF_NAME], config[CONF_REGION], async_get_clientsession(hass))], True)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor from a config entry."""
    async_add_entities([OilPriceSensor(
        config_entry.data[CONF_NAME],
        config_entry.data[CONF_REGION],
        async_get_clientsession(hass)
    )], True)

class OilPriceSensor(Entity):
    """Representation of an Oil Price Sensor."""

    def __init__(self, name: str, region: str, session):
        """Initialize the sensor."""
        self._name = name
        self._region = region
        self._session = session
        self._state = None
        self._entries = {}
        self._attr_unique_id = f"oilprice_{region}"

    async def async_update(self):
        """Fetch the latest oil price data."""
        _LOGGER.debug("Updating oil price info from http://www.qiyoujiage.com/")
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
                        k = re.search(r"\d+", dl.select('dt')[0].text).group()
                        self._entries[k] = dl.select('dd')[0].text
                    self._entries["update_time"] = datetime.datetime.now().strftime('%Y-%m-%d')
                    self._entries["tips"] = soup.select("#youjiaCont > div:nth-of-type(2) > span")[0].text.strip()

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Error fetching oil price data: %s", err)
            self._state = "unavailable"

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