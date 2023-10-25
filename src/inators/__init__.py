import logging

from inators import base, magic, melee, range, tool

logger = logging.getLogger(__name__)

TOOL_DICT = {
    "base": base.Inator,
    "stick": melee.Whackinator,
    "sword": melee.Swooshinator,
    "bomb": range.Boominator,
    "thunder emblem": magic.SpellInator,
}


def get_inator(tool_id):
    if tool_id in TOOL_DICT:
        return TOOL_DICT[tool_id]()
    logger.warning(f"tool_id {tool_id!r} not found.  Using Null Inator instead")
    return base.Inator()
