from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector

from .const import DOMAIN


class VibeAlarmSysConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title="VibeAlarmSys Bridge",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required("alarm_entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="alarm_control_panel")
                ),

                vol.Optional(
                    "alarm_trigger_lookback_seconds",
                    default=60,  # <<< DEFAULT AUF 60
                ): vol.Coerce(int),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
