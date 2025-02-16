"""Config flow for Wikipedia Sensor integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries

_LOGGER = logging.getLogger(__name__)

DOMAIN = "wikipedia_sensor"  # ✅ Define DOMAIN here

class WikipediaSensorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wikipedia Sensor."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Wikipedia Sensor", data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({})
        )
