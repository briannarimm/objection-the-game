# Objection! theming. Based on the original React component's palette:
#   INK #2a1a1a, BG #f5ede0, ACC #D85A30, SUB #d8ccb8

init offset = -2

# Virtual resolution. Ren'Py renders at this resolution and scales the
# rendered surface to the physical window — so a single 1920x1080 build
# scales cleanly to 720p, 1440p, or 4K windows. config.physical_width/height
# below let the player resize freely.
define gui.init_width = 1920
define gui.init_height = 1080
init python:
    gui.init(1920, 1080)

define gui.accent_color = "#D85A30"
define gui.idle_color = "#7a6a60"
define gui.idle_small_color = "#8a7a70"
define gui.hover_color = "#D85A30"
define gui.selected_color = "#2a1a1a"
define gui.insensitive_color = "#8a7a7080"
define gui.muted_color = "#d8ccb8"
define gui.hover_muted_color = "#e8d8c0"

define gui.text_color = "#2a1a1a"
define gui.interface_text_color = "#2a1a1a"

# Custom fonts. The newspaper face is the body text everywhere; the dingbats
# face is referenced by name from individual screens for icons (★, gavel,
# scales, etc.). Both are bundled under game/fonts/.
define gui.text_font = "fonts/OldNewspaperTypes-main.ttf"
define gui.name_text_font = "fonts/OldNewspaperTypes-main.ttf"
define gui.interface_text_font = "fonts/OldNewspaperTypes-main.ttf"

# All text sizes scaled 1.5x from the original 1280x720 design.
define gui.text_size = 33
define gui.name_text_size = 45
define gui.interface_text_size = 33
define gui.label_text_size = 42
define gui.notify_text_size = 27
define gui.title_text_size = 90

define gui.main_menu_background = "#2a1a1a"
define gui.game_menu_background = "#f5ede0"

define gui.textbox_height = 330
define gui.textbox_yalign = 1.0

# Namebox sits directly below where the judge is standing. Judge is at
# xalign 0.30 (screen-center 576px) and now positioned high enough that the
# body bottom is just above the namebox top — so the placard reads as a
# nameplate "attached to" the figure above it. xpos 122 within the
# 1500-wide centered textbox content puts the namebox centered around
# x≈576, directly under the judge.
define gui.name_xpos = 122
define gui.name_ypos = -36
define gui.name_xalign = 0.0

define gui.dialogue_xpos = 30
define gui.dialogue_ypos = 60
define gui.dialogue_width = 1330

define gui.namebox_width = 380
define gui.namebox_height = 70
define gui.namebox_borders = Borders(15, 15, 15, 15)
define gui.namebox_tile = False

define gui.button_width = None
define gui.button_height = 63
define gui.button_borders = Borders(15, 9, 15, 9)
define gui.button_tile = False
define gui.button_text_font = gui.interface_text_font
define gui.button_text_size = gui.interface_text_size
define gui.button_text_xalign = 0.5
define gui.button_text_idle_color = gui.idle_color
define gui.button_text_hover_color = gui.hover_color
define gui.button_text_selected_color = gui.selected_color
define gui.button_text_insensitive_color = gui.insensitive_color

define gui.choice_button_width = 1350
define gui.choice_button_height = None
define gui.choice_button_tile = False
define gui.choice_button_borders = Borders(150, 15, 150, 15)
define gui.choice_button_text_font = gui.text_font
define gui.choice_button_text_size = gui.text_size
define gui.choice_button_text_xalign = 0.5
define gui.choice_button_text_idle_color = "#2a1a1a"
define gui.choice_button_text_hover_color = "#D85A30"

define gui.slot_button_width = 414
define gui.slot_button_height = 309
define gui.slot_button_borders = Borders(15, 15, 15, 15)
define gui.slot_button_text_size = 21

define gui.file_slot_cols = 3
define gui.file_slot_rows = 2

define gui.navigation_xpos = 60
define gui.skip_ypos = 15
define gui.notify_ypos = 68
define gui.choice_spacing = 33
define gui.navigation_spacing = 6
define gui.pref_spacing = 15
define gui.pref_button_spacing = 0
define gui.page_spacing = 0
define gui.slot_spacing = 15

define gui.main_menu_text_xalign = 1.0

define gui.quick_button_text_size = 21
define gui.quick_button_text_idle_color = gui.idle_small_color
define gui.quick_button_text_hover_color = gui.hover_color
define gui.quick_button_text_selected_color = gui.accent_color
define gui.quick_button_text_insensitive_color = gui.insensitive_color

# Dingbat-font icons. Inline {font=...}{/font} so any text string can drop in
# an icon glyph. The Iconian "Law & Order" face maps each Latin letter to a
# legal-themed icon — D is the cleanest 5-point star, N is a gavel, j is a
# scales-of-justice in a square, l is Lady Justice.
define STAR_ICON = "{font=fonts/laworder-dingbats.ttf}{size=+6}D{/size}{/font}"
define GAVEL_ICON = "{font=fonts/laworder-dingbats.ttf}{size=+6}N{/size}{/font}"
define SCALES_ICON = "{font=fonts/laworder-dingbats.ttf}{size=+6}j{/size}{/font}"
