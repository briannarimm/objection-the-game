# Objection! — Ren'Py project config.

define config.name = _("Objection!")
define gui.show_name = True
define config.version = "1.1"

define gui.about = _p("""
Objection! — the party law game.
Procedurally generated personal injury cases,
judged by Claude.
""")

define build.name = "objection"

define config.has_sound = True
define config.has_music = True
define config.has_voice = False

define config.enter_transition = dissolve
define config.exit_transition = dissolve
define config.intra_transition = dissolve
define config.after_load_transition = None
define config.end_game_transition = None

define config.window = "auto"
define config.window_show_transition = Dissolve(0.2)
define config.window_hide_transition = Dissolve(0.2)

define config.save_directory = "objection-the-game-1760000000"

# Allow the player to resize the game window freely. Ren'Py auto-scales
# the 1920x1080 virtual surface to whatever physical size the window is.
define config.gl_resize = True

init python:
    build.classify('**~', None)
    build.classify('**.bak', None)
    build.classify('**/.**', None)
    build.classify('**/#**', None)
    build.classify('**/thumbs.db', None)

    # Dialogue advance: Enter (return / numeric enter) or click. Space is
    # intentionally removed so the player has to commit a deliberate Enter.
    config.keymap['dismiss'] = [
        'mousedown_1', 'K_RETURN', 'K_KP_ENTER',
    ]

    # Rollback: Ren'Py's default rollback behavior maps scroll-up to "rewind
    # game state to a previous interaction." That conflicts hard with our
    # ruling modal — players scrolling up to read the top of a long opinion
    # were getting time-travelled back to the last phase instead. We strip
    # the mousewheel-up binding from the rollback keymap; PageUp still works
    # for anyone who genuinely wants to rewind, and viewport mousewheel
    # scrolling now reaches the modal as intended.
    config.keymap['rollback'] = ['K_PAGEUP', 'repeat_K_PAGEUP', 'K_AC_BACK']
    config.rollback_side_size = 0
