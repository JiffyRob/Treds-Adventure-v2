from pygame_menu import font, themes, widgets

menu_theme = themes.Theme(
    # all colors match the NinjaAdventure palette
    background_color=(20, 27, 27),
    border_color=(45, 105, 123),
    border_width=1,
    cursor_color=(255, 255, 255),
    cursor_selection_color=(242, 234, 241),
    cursor_switch_ms=550,
    focus_background_color=(142, 124, 115),
    fps=30,
    readonly_color=(78, 72, 74),
    readonly_selected_color=(142, 124, 115),
    scrollbar_shadow=False,
    scrollbar_slider_color=(78, 72, 74),
    scrollbar_thick=6,
    selection_color=(255, 255, 255),
    surface_clear_color=(20, 27, 27),
    title=True,
    title_background_color=(45, 105, 123),
    title_bar_style=widgets.MENUBAR_STYLE_UNDERLINE,
    title_close_button=False,
    title_fixed=False,
    title_floating=True,
    title_font=font.FONT_8BIT,
    title_font_antialias=False,
    title_font_color=(255, 255, 255),
    title_font_shadow=False,
    title_font_size=16,
    title_offset=(4, 4),
    title_updates_pygame_display=True,
    widget_font=font.FONT_MUNRO,
    widget_font_size=31,
    # widget_selection_effect=widgets.LeftArrowSelection((15, 15)),
)
