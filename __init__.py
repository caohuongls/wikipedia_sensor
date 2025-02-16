"""Wikipedia Sensor integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "wikipedia_sensor"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Wikipedia Sensor from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # ✅ Fix: Await async_forward_entry_setup
    await hass.config_entries.async_forward_entry_setup(entry, "sensor")

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload Wikipedia Sensor integration."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
