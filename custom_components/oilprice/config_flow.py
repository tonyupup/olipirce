import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_NAME, CONF_REGION

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
            vol.Required(CONF_NAME): str,
            vol.Required(CONF_REGION): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )