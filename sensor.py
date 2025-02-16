"""Wikipedia Sensor for Home Assistant."""
import logging
import aiohttp
import wikipediaapi
import datetime
import asyncio

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(minutes=5)
DOMAIN = "wikipedia_sensor"

BLOCKWORDS = [
    'sinh ngày', 'thực vật', 'hoa', 'cây', 'tỉnh',
    'ngành', 'lớp', 'bộ', 'họ', 'chi', 'loài',
    'làng', 'huyện', 'vùng', 'xã', 'thị trấn', 'thành phố', 'dân số', 'xứ',
    'hành tinh', 'ngôi sao',
    'nhóm nhạc', 'nhạc', 'ca sỹ', 'bài hát',
    'enzyme',
    'chính trị', 'nga', 'game', 'bóng đá',
    'ngôi sao', 'diễn viên', 'người mẫu', 'tài tử', 'nghệ sĩ'
]

wikipedia_api = wikipediaapi.Wikipedia(
    language='vi',
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent='HomeAssistant-Wikipedia-Sensor'
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Wikipedia sensor from config entry."""
    coordinator = WikipediaDataUpdateCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([WikipediaSensor(coordinator)])

class WikipediaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Wikipedia data."""

    def __init__(self, hass: HomeAssistant):
        """Initialize Wikipedia data coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Wikipedia Sensor",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch Wikipedia data."""
        async with aiohttp.ClientSession() as session:
            while True:  # Keep trying until a valid article is found
                try:
                    async with session.get('https://vi.wikipedia.org/api/rest_v1/page/random/summary') as response:
                        if response.status == 404:
                            _LOGGER.warning("Wikipedia API returned 404, trying again...")
                            await asyncio.sleep(1)
                            continue
                        elif response.status != 200:
                            _LOGGER.warning("Wikipedia API error: HTTP %d", response.status)
                            await asyncio.sleep(5)
                            continue

                        wiki_json = await response.json()
                        title_wiki = wiki_json.get('title', '')
                        summary_wiki = wiki_json.get('extract', '')

                        if any(word in title_wiki.lower() for word in BLOCKWORDS) or any(word in summary_wiki.lower() for word in BLOCKWORDS):
                            _LOGGER.info("Skipping blocked article: %s", title_wiki)
                            await asyncio.sleep(1)
                            continue

                        picture_wiki = wiki_json.get('originalimage', {}).get('source', '')

                        return {
                            "title": title_wiki,
                            "picture": picture_wiki if picture_wiki else "No image available",
                            "url": f"https://vi.wikipedia.org/wiki/{title_wiki}",
                            "summary_post": summary_wiki
                        }

                except Exception as e:
                    _LOGGER.error("Error fetching Wikipedia data: %s", str(e))
                    raise UpdateFailed(f"Failed to fetch Wikipedia data: {e}")

class WikipediaSensor(CoordinatorEntity, Entity):
    """Representation of a Wikipedia Sensor."""

    def __init__(self, coordinator):
        """Initialize Wikipedia Sensor."""
        super().__init__(coordinator)
        self._attr_name = "Wikipedia Ngẫu Nhiên"
        self._attr_unique_id = "wikipedia_ngau_nhien"

    @property
    def state(self):
        """Return the state of the sensor."""
        return len(self.coordinator.data.get("summary_post", ""))

    @property
    def extra_state_attributes(self):
        """Return entity-specific state attributes."""
        return self.coordinator.data
