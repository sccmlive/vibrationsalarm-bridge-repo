from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.device_registry import async_get as async_get_dev_reg

from .const import (
    DOMAIN,
    CONF_ALARM_ENTITY,
    CONF_ESPHOME_DEVICE,
    CONF_NODE_NAME,
    CONF_ESPHOME_DEVICES,
    CONF_NODE_NAMES,
    CONF_SEND_PANEL_NAME,
    CONF_SEND_SOURCE_TEXT,
    DEFAULT_SEND_PANEL_NAME,
    DEFAULT_SEND_SOURCE_TEXT,
    CONF_TRIGGER_ENTITIES,
    CONF_TRIGGER_RESET_SECONDS,
    CONF_TRIGGER_COOLDOWN_SECONDS,
    CONF_PREFER_TRIGGER_FRIENDLY_NAME,
    DEFAULT_PREFER_TRIGGER_FRIENDLY_NAME,
    DEFAULT_TRIGGER_RESET_SECONDS,
    DEFAULT_TRIGGER_COOLDOWN_SECONDS,
    CONF_ALARM_TRIGGER_LOOKBACK_SECONDS,
    DEFAULT_ALARM_TRIGGER_LOOKBACK_SECONDS,
    CONF_AUTO_TRACK_DEVICE_CLASSES,
    DEFAULT_AUTO_TRACK_DEVICE_CLASSES,
)


def _slugify_node_name(name: str) -> str:
    s = name.strip().lower().replace("-", "_").replace(" ", "_")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


async def _guess_esphome_node_name_from_device(hass, device_id: str) -> str | None:
    dev_reg = async_get_dev_reg(hass)
    device = dev_reg.async_get(device_id)
    if not device:
        return None
    # Prefer the ESPHome identifier, which is normally ("esphome", "<node_name>")
    for domain, ident in device.identifiers:
        if domain == "esphome" and isinstance(ident, str) and ident.strip():
            return _slugify_node_name(ident)

    # Fallback (less reliable): friendly device name
    if device.name:
        return _slugify_node_name(device.name)
    return None


class VibrationsalarmBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 4

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            alarm_entity = user_input[CONF_ALARM_ENTITY]
            # Multi-target: list of ESPHome device_ids
            esphome_device_ids = user_input[CONF_ESPHOME_DEVICES]
            send_panel_name = user_input.get(CONF_SEND_PANEL_NAME, DEFAULT_SEND_PANEL_NAME)
            send_source_text = user_input.get(CONF_SEND_SOURCE_TEXT, DEFAULT_SEND_SOURCE_TEXT)
            prefer_trigger_friendly_name = bool(user_input.get(CONF_PREFER_TRIGGER_FRIENDLY_NAME, DEFAULT_PREFER_TRIGGER_FRIENDLY_NAME))

            lookback_seconds = int(user_input.get(CONF_ALARM_TRIGGER_LOOKBACK_SECONDS, DEFAULT_ALARM_TRIGGER_LOOKBACK_SECONDS))
            auto_track_device_classes = bool(user_input.get(CONF_AUTO_TRACK_DEVICE_CLASSES, DEFAULT_AUTO_TRACK_DEVICE_CLASSES))

            trigger_entities = user_input.get(CONF_TRIGGER_ENTITIES) or []
            trigger_reset_seconds = int(user_input.get(CONF_TRIGGER_RESET_SECONDS, DEFAULT_TRIGGER_RESET_SECONDS))
            trigger_cooldown_seconds = int(user_input.get(CONF_TRIGGER_COOLDOWN_SECONDS, DEFAULT_TRIGGER_COOLDOWN_SECONDS))

            # Optional override: comma-separated node names in the same order as selected devices.
            node_override_raw = (user_input.get(CONF_NODE_NAMES) or "").strip()
            node_names: list[str] = []

            if node_override_raw:
                node_names = [_slugify_node_name(x) for x in node_override_raw.split(",") if x.strip()]
                if len(node_names) != len(esphome_device_ids):
                    errors[CONF_NODE_NAMES] = "node_count_mismatch"
            else:
                for dev_id in esphome_device_ids:
                    guessed = await _guess_esphome_node_name_from_device(self.hass, dev_id)
                    if not guessed:
                        errors[CONF_NODE_NAMES] = "node_required"
                        break
                    node_names.append(guessed)

            if not errors:
                title = f"VibeAlarmSys Bridge ({alarm_entity} → {len(node_names)} Gerät(e))"
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_ALARM_ENTITY: alarm_entity,
                        CONF_ESPHOME_DEVICES: esphome_device_ids,
                        CONF_NODE_NAMES: node_names,
                        CONF_SEND_PANEL_NAME: send_panel_name,
                        CONF_SEND_SOURCE_TEXT: send_source_text,
                        CONF_TRIGGER_ENTITIES: trigger_entities,
                        CONF_TRIGGER_RESET_SECONDS: trigger_reset_seconds,
                        CONF_TRIGGER_COOLDOWN_SECONDS: trigger_cooldown_seconds,
                        CONF_PREFER_TRIGGER_FRIENDLY_NAME: prefer_trigger_friendly_name,
                        CONF_ALARM_TRIGGER_LOOKBACK_SECONDS: lookback_seconds,
                        CONF_AUTO_TRACK_DEVICE_CLASSES: auto_track_device_classes,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_ALARM_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="alarm_control_panel")
                ),
                vol.Required(CONF_ESPHOME_DEVICES): selector.DeviceSelector(
                    selector.DeviceSelectorConfig(integration="esphome", multiple=True)
                ),
                # Optional: comma-separated list of node names (same order as selected devices)
                vol.Optional(CONF_NODE_NAMES, default=""): str,
                vol.Optional(CONF_SEND_PANEL_NAME, default=DEFAULT_SEND_PANEL_NAME): bool,
                vol.Optional(CONF_SEND_SOURCE_TEXT, default=DEFAULT_SEND_SOURCE_TEXT): bool,
                vol.Optional(CONF_PREFER_TRIGGER_FRIENDLY_NAME, default=DEFAULT_PREFER_TRIGGER_FRIENDLY_NAME): bool,
                vol.Optional(CONF_ALARM_TRIGGER_LOOKBACK_SECONDS, default=DEFAULT_ALARM_TRIGGER_LOOKBACK_SECONDS): vol.Coerce(int),
                vol.Optional(CONF_AUTO_TRACK_DEVICE_CLASSES, default=DEFAULT_AUTO_TRACK_DEVICE_CLASSES): bool,
                vol.Optional(CONF_TRIGGER_ENTITIES, default=[]): selector.EntitySelector(
                    selector.EntitySelectorConfig(multiple=True)
                ),
                vol.Optional(CONF_TRIGGER_RESET_SECONDS, default=DEFAULT_TRIGGER_RESET_SECONDS): vol.Coerce(int),
                vol.Optional(CONF_TRIGGER_COOLDOWN_SECONDS, default=DEFAULT_TRIGGER_COOLDOWN_SECONDS): vol.Coerce(int),

            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)