import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv
from homeassistant.core import callback
from .const import DOMAIN, CONF_NAME, CONF_REGION
from enum import Enum


class RegionEnum(Enum):
    BEIJING= "beijing"
    SHANGHAI= "shanghai"
    TIANJIN= "tianjin"
    CHONGQING= "chongqing"
    FUJIAN= "fujian"
    SHENZHEN= "shenzhen"
    GANSU= "gansu"
    GUANGDONG= "guangdong"
    GUANGXI= "guangxi"
    GUIZHOU= "guizhou"
    HAINAN= "hainan"
    HEBEI= "hebei"
    HENAN= "henan"
    HUBEI= "hubei"
    HUNAN= "hunan"
    JILIN= "jilin"
    JIANGSU= "jiangsu"
    JIANGXI= "jiangxi"
    LIAONING= "liaoning"
    ZHEJIANG= "zhejiang"
    NEIMENGGU= "neimenggu"
    ANHUI= "anhui"
    NINGXIA= "ningxia"
    QINGHAI= "qinghai"
    SHANDONG= "shandong"
    SHANXI3= "shanxi-3"
    SHANXI= "shanxi"
    SICHUAN= "sichuan"
    XIZANG= "xizang"
    HEILONGJIANG= "heilongjiang"
    XINJIANG= "xinjiang"
    YUNNAN= "yunnan"
    GUONEIYOUJIA= "guoneiyoujia"
    JIAYOUZHAN= "jiayouzhan"



class OilPriceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Oil Price."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(f"oilprice_{user_input[CONF_REGION]}")
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input
            )

        data_schema = vol.Schema({
            vol.Required(CONF_NAME): cv.string,
            vol.Required(CONF_REGION): cv.enum(RegionEnum),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )