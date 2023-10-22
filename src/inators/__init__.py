from inators import base, magic, melee, range, tool

TOOL_DICT = {
    "base": base.Inator,
    "stick": melee.Whackinator,
    "sword": melee.Swooshinator,
    "bomb": range.Boominator,
    "thunder": magic.SpellInator,
}


def get_inator(tool_id):
    if tool_id in TOOL_DICT:
        return TOOL_DICT[tool_id]()
    print(f"Warning: tool_id {tool_id!r} not found.  Using Null Inator instead")
    return base.Inator()
