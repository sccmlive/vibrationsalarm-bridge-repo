DOMAIN = "vibe_alarm_sys"

CONF_ALARM_ENTITY = "alarm_entity"
# Legacy single-target keys (kept for backward compatibility)
CONF_ESPHOME_DEVICE = "esphome_device_id"
CONF_NODE_NAME = "node_name"

# New multi-target keys
CONF_ESPHOME_DEVICES = "esphome_device_ids"
CONF_NODE_NAMES = "node_names"

CONF_SEND_PANEL_NAME = "send_panel_name"
CONF_SEND_SOURCE_TEXT = "send_source_text"

DEFAULT_SEND_PANEL_NAME = True
DEFAULT_SEND_SOURCE_TEXT = True

# --- Universal Trigger Detection (no Alarmo dependency) ---
# When the alarm_control_panel switches to "triggered", the integration will look for the
# most recently triggered binary_sensor (off -> on) within this time window and send its
# friendly name to the ESPHome device via set_alarm_source.
TRIGGER_WINDOW_SECONDS = 30


# Optional: additional entities that should trigger a push to ESPHome even if the alarm panel
# itself does not switch to "triggered" (e.g., camera motion binary_sensors).
CONF_TRIGGER_ENTITIES = "trigger_entities"
CONF_TRIGGER_RESET_SECONDS = "trigger_reset_seconds"
CONF_TRIGGER_COOLDOWN_SECONDS = "trigger_cooldown_seconds"

DEFAULT_TRIGGER_RESET_SECONDS = 10
DEFAULT_TRIGGER_COOLDOWN_SECONDS = 5
