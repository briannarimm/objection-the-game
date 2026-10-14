# All custom screens for Objection! Sized for the 1920x1080 virtual resolution
# defined in gui.rpy; Ren'Py auto-scales to physical window size.

# ------------------------------------------------------------
# Image declarations.
# Backdrops force-fit the 1920x1080 viewport (any image with the wrong aspect
# is stretched rather than letterboxed). Scenario art is intentionally NOT
# stretched — see `scenario card_*` below, displayed centered as an overlay.
# ------------------------------------------------------------

image bg courtroom = Transform("images/courtroom.png", xysize=(1920, 1080))

# Square scenario art shown as a "case card" on the right while the judge
# stands on the left — see transform `scenario_right` below. Per-scenario
# images are 1024² (zoom 0.55 → 563px); category-fallback placeholders are
# 600² (zoom 0.94 → ~564px) so both render at the same on-screen size.
image scenario_card cheese = Transform("images/scenarios/cheese.png", zoom=0.55)
image scenario_card pothole = Transform("images/scenarios/pothole.png", zoom=0.55)
image scenario_card roomba = Transform("images/scenarios/roomba.png", zoom=0.55)
image scenario_card trampoline = Transform("images/scenarios/trampoline.png", zoom=0.55)
image scenario_card shopping_cart = Transform("images/scenarios/shopping_cart.png", zoom=0.55)
image scenario_card sourdough = Transform("images/scenarios/sourdough.png", zoom=0.55)
image scenario_card vending = Transform("images/scenarios/vending.png", zoom=0.55)
image scenario_card peloton = Transform("images/scenarios/peloton.png", zoom=0.55)
image scenario_card food = Transform("images/cases/food.png", zoom=0.94)
image scenario_card machine = Transform("images/cases/machine.png", zoom=0.94)
image scenario_card outdoor = Transform("images/cases/outdoor.png", zoom=0.94)
image scenario_card wellness = Transform("images/cases/wellness.png", zoom=0.94)

# Hero gavel — title screen only.
image hero gavel = Transform("images/hero_gavel.png", zoom=0.85)

# OBJECTION! action graphic — used inside the banner screen.
image action objection = Transform("images/objection_banner.png", zoom=0.7)

# Judges — 1024 portraits at zoom 0.55 (~563px tall) so they fit fully ABOVE
# the textbox rather than overlapping it. See `judge_left` transform below
# for the positioning that lifts them up over the namebox.
image judge pomps = Transform("images/judges/pomps.png", zoom=0.55)
image judge larue = Transform("images/judges/larue.png", zoom=0.55)
image judge quirk = Transform("images/judges/quirk.png", zoom=0.55)
image judge stern = Transform("images/judges/stern.png", zoom=0.55)
image judge fitch = Transform("images/judges/fitch.png", zoom=0.55)
image judge winter = Transform("images/judges/winter.png", zoom=0.55)
image judge vibe  = Transform("images/judges/vibe.png", zoom=0.55)
image judge penny = Transform("images/judges/penny.png", zoom=0.55)

# Witnesses — sized like jurors for use in pickers and as on-stand portraits.
image witness derek = Transform("images/witnesses/derek.png", zoom=0.5)
image witness destiny = Transform("images/witnesses/destiny.png", zoom=0.5)
image witness eugene = Transform("images/witnesses/eugene.png", zoom=0.5)
image witness hank = Transform("images/witnesses/hank.png", zoom=0.5)
image witness jerry = Transform("images/witnesses/jerry.png", zoom=0.5)
image witness marvella = Transform("images/witnesses/marvella.png", zoom=0.5)
image witness miriam = Transform("images/witnesses/miriam.png", zoom=0.5)
image witness phyllis = Transform("images/witnesses/phyllis.png", zoom=0.5)
image witness renata = Transform("images/witnesses/renata.png", zoom=0.5)
image witness todd = Transform("images/witnesses/todd.png", zoom=0.5)

# Stage positions for the case phase. The judge sits high enough that their
# body ends just above where the namebox tail starts, so the placard reads as
# "attached to" the figure standing above it (per the VN-mockup reference).
# Math: textbox top at y≈714 (1080 − 330 textbox − 36 yoffset); namebox top
# at y≈678 (textbox top − 36 ypos). Judge image is 563px tall (1024 × 0.55);
# yoffset −402 puts the bottom edge at y=678, right at the namebox top.
transform judge_left:
    xalign 0.30
    yalign 1.0
    yoffset -402

transform scenario_right:
    xalign 0.82
    yalign 0.42

# ------------------------------------------------------------
# Speakers
# ------------------------------------------------------------

define narrator = Character(None, what_italic=True, what_color="#d8ccb8")
# Speaker name shows in the orange namebox; dialogue shows on the dark
# translucent textbox — cream gives the best contrast for both.
define reporter = Character("Reporter", color="#f5ede0", what_color="#f5ede0")
define judgechar = Character("Judge", color="#f5ede0", what_color="#f5ede0")

# ------------------------------------------------------------
# Custom say screen — adds the "[ENTER]" prompt at the bottom-right of
# the textbox so players know to press Enter to advance. Click and Enter
# both still work; Space is unbound (see options.rpy). Styles needed by
# this screen are defined at the bottom of this file.
# ------------------------------------------------------------

screen say(who, what):
    style_prefix "say"

    window:
        id "window"
        style "window"

        if who is not None:
            window:
                id "namebox"
                style "namebox"
                text who id "who" style "say_label"
            # Decorative downward tab at the namebox's bottom-left, like a
            # label clipped to the textbox below. Three stacked solids form
            # a rough downward triangle.
            add Solid("#D85A30"):
                xpos (gui.name_xpos + 30)
                ypos (gui.name_ypos + gui.namebox_height)
                xysize (28, 12)
            add Solid("#D85A30"):
                xpos (gui.name_xpos + 36)
                ypos (gui.name_ypos + gui.namebox_height + 12)
                xysize (16, 8)
            add Solid("#D85A30"):
                xpos (gui.name_xpos + 41)
                ypos (gui.name_ypos + gui.namebox_height + 20)
                xysize (6, 4)

        text what id "what" style "say_dialogue"

        # Press-Enter hint, bottom-right of the textbox.
        text "[[ENTER]":
            xalign 1.0 yalign 1.0
            xoffset -30 yoffset -10
            size 24 color "#7a6a60" italic True

    if not renpy.variant("small"):
        add SideImage() xalign 0.0 yalign 1.0

# ------------------------------------------------------------
# Persistent HUD — score + prestige for both teams. Dingbat font is used
# for the prestige glyph as a decorative flourish.
# ------------------------------------------------------------

screen hud():
    zorder 100

    if not hide_hud:
        frame:
            background "#2a1a1aE0"
            xalign 0.5
            ypos 0
            xpadding 36
            ypadding 12

            hbox:
                spacing 48
                vbox:
                    xsize 270
                    text "PLAINTIFF" color "#f5ede0" size 21 xalign 0.5
                    hbox:
                        xalign 0.5
                        spacing 12
                        text "[scores[u'plaintiff']]" color "#D85A30" size 48
                        # Prestige icon comes from the Law & Order dingbats font
                        # (D = filled 5-point star). STAR_ICON wraps the inline
                        # font tag — see gui.rpy.
                        text "[STAR_ICON] [prestige[u'plaintiff']]" color "#f5ede0" size 24 yalign 0.8

                text "vs" color "#d8ccb8" size 30 yalign 0.5

                vbox:
                    xsize 270
                    text "DEFENDANT" color "#f5ede0" size 21 xalign 0.5
                    hbox:
                        xalign 0.5
                        spacing 12
                        text "[scores[u'defendant']]" color "#D85A30" size 48
                        text "[STAR_ICON] [prestige[u'defendant']]" color "#f5ede0" size 24 yalign 0.8

default hide_hud = True

# ------------------------------------------------------------
# Main menu — what you see at game launch and after Quit-to-menu. Hero
# gavel sits behind a darkened wash with the title and Start/Load/etc
# buttons on top.
# ------------------------------------------------------------

screen main_menu():
    tag menu

    add "#1a0d0d"
    add "images/hero_gavel.png":
        xalign 0.5 yalign 0.32
    add "#1a0d0d80"

    vbox:
        xalign 0.5 yalign 0.78
        spacing 18

        text "OBJECTION!" size 130 color "#D85A30" outlines [(6, "#1a0d0d", 0, 0)] xalign 0.5
        text "the party law game" size 36 color "#d8ccb8" italic True xalign 0.5
        null height 24

        textbutton "Play":
            action Start()
            text_size 42
            text_color "#f5ede0"
            text_hover_color "#D85A30"
            xalign 0.5
        textbutton "Load":
            action ShowMenu("load")
            text_size 32
            text_color "#d8ccb8"
            text_hover_color "#D85A30"
            xalign 0.5
        textbutton "Preferences":
            action ShowMenu("preferences")
            text_size 32
            text_color "#d8ccb8"
            text_hover_color "#D85A30"
            xalign 0.5
        textbutton "Quit":
            action Quit(confirm=not main_menu)
            text_size 32
            text_color "#d8ccb8"
            text_hover_color "#D85A30"
            xalign 0.5

# ------------------------------------------------------------
# OBJECTION! banner — flashes the action_OBJECTION graphic + caption.
# ------------------------------------------------------------

transform banner_zoom:
    alpha 0.0 zoom 3.0 rotate -8
    parallel:
        ease 0.12 alpha 1.0 zoom 1.0 rotate 0
    time 1.0
    ease 0.25 alpha 0.0

transform banner_action:
    alpha 0.0 zoom 0.0 rotate -25 xalign 0.5 yalign 0.5
    parallel:
        ease 0.18 alpha 0.95 zoom 0.7 rotate 0
    time 1.0
    ease 0.25 alpha 0.0

screen objection_banner(text_label):
    zorder 200
    modal False

    add "#ffffffE0":
        at transform:
            alpha 0.0
            ease 0.08 alpha 0.9
            time 1.0
            ease 0.25 alpha 0.0

    add "images/objection_banner.png" at banner_action

    text text_label:
        xalign 0.5 yalign 0.85
        color "#D85A30"
        outlines [(6, "#2a1a1a", 0, 0)]
        size 180
        at banner_zoom

# Scenario card now renders on the master layer (see phases.rpy `phase_case`)
# at scenario_right transform, so the textbox draws on top of it. There's no
# separate scenario overlay screen anymore.

# ------------------------------------------------------------
# Jury selection — teams alternate picks from the full juror pool, 3 each
# ------------------------------------------------------------

screen jury_selection(turn_team):
    zorder 50
    modal True
    add "#2a1a1aD0"

    frame:
        xalign 0.5 yalign 0.5
        xsize 1850 ysize 1020
        background "#f5ede0"
        padding (45, 36, 45, 36)

        vbox:
            spacing 21

            text "Jury Selection" size 48 color "#2a1a1a"
            text "Teams alternate picks. Each side seats 3 jurors. Biases hidden until the ruling." size 27 color "#7a6a60"
            text ("[turn_team]'s pick.") size 33 color "#D85A30"

            grid 5 2:
                spacing 14
                xfill True
                for j in jury_pool:
                    button:
                        action Return(j)
                        xsize 340 ysize 200
                        background "#d8ccb8"
                        hover_background "#D85A30"
                        padding (14, 14, 14, 14)
                        vbox:
                            spacing 4
                            xalign 0.5
                            xfill True
                            add ("images/jurors/" + j["img"] + ".png") zoom 0.085 xalign 0.5
                            text "[j[u'name']]" size 19 color "#2a1a1a" xalign 0.5 xsize 308 text_align 0.5
                            text "[j[u'occ']]" size 16 color "#5a4a40" xalign 0.5 xsize 308 text_align 0.5

            null height 12
            hbox:
                spacing 36
                vbox:
                    xsize 800
                    text "PLAINTIFF JURY" size 24 color "#D85A30"
                    for j in p_jury:
                        hbox:
                            spacing 9
                            add ("images/jurors/" + j["img"] + ".png") zoom 0.06
                            text ("[j[u'name']] — [j[u'occ']]") size 21 color "#2a1a1a" yalign 0.5
                vbox:
                    xsize 800
                    text "DEFENDANT JURY" size 24 color "#D85A30"
                    for j in d_jury:
                        hbox:
                            spacing 9
                            add ("images/jurors/" + j["img"] + ".png") zoom 0.06
                            text ("[j[u'name']] — [j[u'occ']]") size 21 color "#2a1a1a" yalign 0.5

# ------------------------------------------------------------
# Motion timer — static cards with a count-down ring
# ------------------------------------------------------------

default motion_time_left = 45

screen motions_display():
    zorder 50
    modal True
    add "#2a1a1aD0"

    frame:
        xalign 0.5 yalign 0.5
        xsize 1650 ysize 900
        background "#f5ede0"
        padding (45, 36)

        vbox:
            spacing 15

            hbox:
                text "Motion Card Phase" size 48 color "#2a1a1a"
                null width 60
                text ("[motion_time_left]s"):
                    size 54
                    color ("#D85A30" if motion_time_left <= 10 else "#2a1a1a")

            text "Strategize with your team before time runs out." size 27 color "#7a6a60"

            hbox:
                spacing 30
                frame:
                    xsize 750
                    background "#d8ccb8"
                    padding (24, 18)
                    vbox:
                        text "PLAINTIFF TEAM" size 27 color "#2a1a1a"
                        for c in p_cards:
                            text ("· [c]") size 27 color "#2a1a1a"
                frame:
                    xsize 750
                    background "#d8ccb8"
                    padding (24, 18)
                    vbox:
                        text "DEFENDANT TEAM" size 27 color "#2a1a1a"
                        for c in d_cards:
                            text ("· [c]") size 27 color "#2a1a1a"

            null height 15
            textbutton "   Skip to discovery   ":
                action Return(True)
                text_size 30

    timer 1.0 action [SetVariable("motion_time_left", motion_time_left - 1), If(motion_time_left <= 0, Return(True), NullAction())] repeat True

# ------------------------------------------------------------
# Motion ranking — each team orders their 3 cards by priority. The chosen
# order is fed back to the AI ruling prompt as "(#1) ... (#2) ... (#3) ..."
# so the team's stated strongest motion gets weighted heavier.
# ------------------------------------------------------------

screen motion_ranking(team, cards):
    zorder 50
    modal True
    add "#2a1a1aD0"
    default ranked = []

    frame:
        xalign 0.5 yalign 0.5
        xsize 1500 ysize 800
        background "#f5ede0"
        padding (45, 36)

        vbox:
            spacing 18
            text ("[team!c] team — rank your motions") size 42 color "#D85A30"
            text "Click cards in priority order. #1 is your strongest argument." size 26 color "#7a6a60"

            null height 6
            hbox:
                spacing 18
                xalign 0.5
                for i in range(3):
                    frame:
                        xsize 440 ysize 110
                        background ("#D85A30" if i < len(ranked) else "#d8ccb8")
                        padding (12, 12)
                        vbox:
                            spacing 4
                            text ("#" + str(i + 1)) size 22 color ("#f5ede0" if i < len(ranked) else "#7a6a60")
                            if i < len(ranked):
                                text ranked[i] size 22 color "#f5ede0"
                            else:
                                text "(empty)" size 22 color "#7a6a60" italic True

            null height 12
            text "Available motions:" size 24 color "#2a1a1a"
            vbox:
                spacing 8
                for c in cards:
                    if c in ranked:
                        textbutton ("· " + c + "  (assigned)"):
                            action NullAction()
                            sensitive False
                            text_size 24
                            text_color "#7a6a60"
                            xsize 1380
                            text_xalign 0.0
                    else:
                        textbutton ("· " + c):
                            action SetScreenVariable("ranked", ranked + [c])
                            text_size 24
                            text_color "#2a1a1a"
                            text_hover_color "#D85A30"
                            xsize 1380
                            text_xalign 0.0

            null height 12
            hbox:
                spacing 24
                xalign 0.5
                textbutton "   Reset   " action SetScreenVariable("ranked", []) text_size 26
                if len(ranked) == 3:
                    textbutton "   Confirm ranking   " action Return(list(ranked)) text_size 26

# ------------------------------------------------------------
# Wild card phase — burn the #3 motion to draw 1 of 3 wild cards.
# ------------------------------------------------------------

screen wild_offer(team, hindmost):
    zorder 50
    modal True
    add "#2a1a1aD0"

    frame:
        xalign 0.5 yalign 0.5
        xsize 1350 ysize 460
        background "#f5ede0"
        padding (45, 36)

        vbox:
            spacing 18
            text ("[team!c] team — wild-card opportunity") size 42 color "#D85A30"
            text ("Burn your #3 motion ([hindmost]) to draw a wild card?") size 27 color "#7a6a60"
            text "Wild cards are higher-impact filings the judge will weigh seriously — for better or worse." size 24 color "#7a6a60" italic True
            null height 9
            hbox:
                spacing 30
                xalign 0.5
                textbutton "   Skip — keep my 3 motions   " action Return(None) text_size 27
                textbutton "   Draw 3 wild cards   " action Return("draw") text_size 27

screen wild_pick(team, options):
    zorder 50
    modal True
    add "#2a1a1aD0"

    frame:
        xalign 0.5 yalign 0.5
        xsize 1500 ysize 600
        background "#f5ede0"
        padding (45, 36)

        vbox:
            spacing 18
            text ("[team!c] team — pick a wild card") size 42 color "#D85A30"
            text "Replaces your #3 motion. Choose carefully." size 27 color "#7a6a60"
            null height 9
            for w in options:
                textbutton w:
                    action Return(w)
                    text_size 26
                    text_color "#2a1a1a"
                    text_hover_color "#D85A30"
                    xsize 1380
                    text_xalign 0.0
                    background "#d8ccb8"
                    hover_background "#f5ede0"
                    padding (18, 12)

# ------------------------------------------------------------
# Witness picker — each team picks 1 of 3 from a shared shuffled pool.
# Witness `cred` (credibility) tilt is hidden until the ruling.
# ------------------------------------------------------------

screen witness_pick(team, pool):
    zorder 50
    modal True
    add "#2a1a1aD0"

    frame:
        xalign 0.5 yalign 0.5
        xsize 1750 ysize 920
        background "#f5ede0"
        padding (45, 36)

        vbox:
            spacing 21
            text ("[team!c] team — call your witness") size 42 color "#2a1a1a"
            text "Pick wisely. Vibes are public; credibility is the judge's secret." size 24 color "#7a6a60"

            hbox:
                spacing 24
                for w in pool:
                    button:
                        action Return(w)
                        xsize 540 ysize 700
                        background "#d8ccb8"
                        hover_background "#D85A30"
                        padding (20, 20, 20, 20)
                        vbox:
                            spacing 10
                            xalign 0.5
                            xfill True
                            add ("images/witnesses/" + w["img"] + ".png") zoom 0.32 xalign 0.5
                            text "[w[u'name']]" size 24 color "#2a1a1a" xalign 0.0 xsize 500
                            text "[w[u'occ']]" size 18 color "#5a4a40" xalign 0.0 xsize 500
                            text "[w[u'vibe']]" size 16 color "#7a6a60" xalign 0.0 xsize 500 italic True

# ------------------------------------------------------------
# Discovery — each team picks 1 of 3 evidence items
# ------------------------------------------------------------

screen discovery_pick(team, pool):
    zorder 50
    modal True
    add "#2a1a1aD0"

    frame:
        xalign 0.5 yalign 0.5
        xsize 1700 ysize 820
        background "#f5ede0"
        padding (45, 36)

        vbox:
            spacing 21
            text ("[team] team — pick your evidence") size 42 color "#2a1a1a"
            text "The judge will see this. Choose the one you'll submit." size 24 color "#7a6a60"

            hbox:
                spacing 24
                for e in pool:
                    button:
                        action Return(e)
                        xsize 510 ysize 540
                        background "#d8ccb8"
                        hover_background "#D85A30"
                        padding (18, 18)
                        vbox:
                            spacing 12
                            xalign 0.5
                            add ("images/evidence/" + e["img"] + ".png") zoom 0.20 xalign 0.5
                            text "[e[u'name']]" size 24 color "#2a1a1a" xalign 0.0
                            text "[e[u'flavor']]" size 19 color "#5a4a40" xalign 0.0

# ------------------------------------------------------------
# Generic A/B/C/D question prompt — used by motion activation,
# evidence admissibility, settlement strengthening, and the legacy
# trivia phase. Caller passes a question dict and a team label that
# is shown in the header.
# ------------------------------------------------------------

screen ask_question(team, q, header="Question"):
    zorder 55
    modal True
    add "#2a1a1aE0"

    frame:
        xalign 0.5 yalign 0.5
        xsize 1500 ysize 760
        background "#f5ede0"
        padding (45, 36)

        vbox:
            spacing 21
            hbox:
                text header size 42 color "#D85A30"
                null width 30
                text (team.title() + " team") size 30 color "#7a6a60" yalign 0.6
                null width 30
                text (q["cat"] + " · D" + str(q["diff"])) size 24 color "#7a6a60" yalign 0.6

            text q["q"] size 30 color "#2a1a1a"
            null height 9
            for opt in q["options"]:
                textbutton opt:
                    action Return(opt)
                    xsize 1380
                    text_size 24
                    text_xalign 0.0
                    background "#d8ccb8"
                    hover_background "#D85A30"
                    padding (18, 10)


# ------------------------------------------------------------
# Trivia buzzer — first to buzz in answers
# ------------------------------------------------------------

screen trivia_buzzer():
    zorder 50
    modal True
    add "#2a1a1aD0"

    frame:
        xalign 0.5 yalign 0.5
        xsize 1500 ysize 480
        background "#f5ede0"
        padding (45, 36)

        vbox:
            spacing 24
            text "Trivia — first to buzz in answers!" size 48 color "#2a1a1a"
            text ("[trivia_q[u'q']]") size 33 color "#2a1a1a"
            null height 15
            hbox:
                spacing 30
                textbutton "   Plaintiff buzzes (Q)   ":
                    action Return("plaintiff")
                    keysym "q"
                    text_size 33
                textbutton "   Defendant buzzes (P)   ":
                    action Return("defendant")
                    keysym "p"
                    text_size 33

# ------------------------------------------------------------
# Settlement offer & response — now interactive: plaintiff
# answers a question to strengthen the offer; both teams gain
# ★ if accepted (small, but lets defenders bank for an appeal).
# ------------------------------------------------------------

screen settle_offer():
    zorder 50
    modal True
    add "#2a1a1aD0"

    frame:
        xalign 0.5 yalign 0.5
        xsize 1350 ysize 500
        background "#f5ede0"
        padding (45, 36)

        vbox:
            spacing 21
            text "Settlement Offer" size 42 color "#2a1a1a"
            text "Plaintiff: offer to settle, or skip and demand trial. Strong settlements (with a correct prep question) are harder for defendants to refuse." size 27 color "#7a6a60"
            null height 9
            hbox:
                spacing 24
                textbutton "Skip — demand trial" action Return("skip") text_size 27
                textbutton "Offer modest" action Return("small") text_size 27
                textbutton "Offer hefty" action Return("large") text_size 27


screen settle_response(offer, strengthened):
    zorder 50
    modal True
    add "#2a1a1aD0"

    frame:
        xalign 0.5 yalign 0.5
        xsize 1350 ysize 500
        background "#f5ede0"
        padding (45, 36)

        vbox:
            spacing 21
            text "Settlement Response" size 42 color "#2a1a1a"
            if strengthened:
                text ("Defendant: plaintiff offered a [offer] settlement, BACKED by a strong legal showing. Accept to bank [STAR_ICON] for both sides; reject and gamble on the judge.") size 27 color "#7a6a60"
            else:
                text ("Defendant: plaintiff offered a [offer] settlement (no preparatory showing). Accept to bank [STAR_ICON] for both sides; reject and gamble on the judge.") size 27 color "#7a6a60"
            null height 9
            hbox:
                spacing 24
                textbutton "Accept — both teams gain [STAR_ICON]" action Return("accept") text_size 27
                textbutton "Reject — go to trial" action Return("reject") text_size 27

# ------------------------------------------------------------
# Closing arguments — verdict director (madlibs sheet).
#
# `template` is one of the VERDICT_TEMPLATES side-blocks (with `intro` and
# `blanks`). The screen tracks `filled` (per-blank picks) and `current` (the
# blank being edited). The full template renders inline at the top, with
# orange-highlighted blanks for current and filled values shown as the
# selected phrase. The bottom area shows option buttons + a "✎ Custom..."
# escape hatch that opens an inline input field.
#
# Live objection interrupt: the OPPOSING team can spend their token to throw
# an objection on the current draft; we Return("objection") and the calling
# label resolves the menu, then re-enters this screen.
# ------------------------------------------------------------

screen verdict_director(team, target_var, template, initial_filled=None, initial_current=0):
    zorder 50
    modal True
    add "#2a1a1aD0"

    # Preserve drafting state across re-entries (e.g. after an objection
    # interrupt). Caller passes the previous filled/current; we copy locally.
    default filled = list(initial_filled) if initial_filled else ["", "", "", "", "", ""]
    default current = initial_current
    default editing_custom = False
    default custom_text = ""

    # Compute opposing team's token count for the OBJECTION! interrupt button.
    $ opposing_team = "Defendant" if team == "Plaintiff" else "Plaintiff"
    $ opposing_tokens = (d_obj_tokens if team == "Plaintiff" else p_obj_tokens)

    frame:
        xalign 0.5 yalign 0.5
        xsize 1700 ysize 1000
        background "#f5ede0"
        padding (45, 36)

        vbox:
            spacing 14

            hbox:
                text ("[team!c] team — closing argument (verdict director)") size 38 color "#D85A30"
                null width 24
                text ("Blank #" + str(current + 1) + " of 6") size 26 color "#7a6a60" yalign 0.6

            text "Click an option to fill the current blank. ✎ Custom lets you free-type. Use ← / → to revisit blanks." size 20 color "#7a6a60"

            null height 4

            # Live preview frame.
            frame:
                xsize 1600 ysize 280
                background "#fbf3e7"
                padding (24, 18)
                $ preview = render_preview(template["intro"], filled, current)
                text preview size 24 color "#2a1a1a"

            null height 4

            # Editor area: dropdown options OR custom-text input.
            if editing_custom:
                vbox:
                    spacing 9
                    text "Custom text for this blank:" size 22 color "#2a1a1a"
                    frame:
                        xsize 1600 ysize 100
                        background "#d8ccb8"
                        padding (18, 10)
                        input:
                            value VariableInputValue("custom_text")
                            length 120
                            color "#2a1a1a"
                            size 24
                            xsize 1560
                    hbox:
                        spacing 24
                        textbutton "   Cancel   " action SetScreenVariable("editing_custom", False) text_size 22
                        textbutton "   Save custom   ":
                            action [
                                SetScreenVariable("filled", filled[:current] + [custom_text] + filled[current+1:]),
                                SetScreenVariable("editing_custom", False),
                            ]
                            text_size 22
            else:
                vbox:
                    spacing 9
                    text ("Options for blank #" + str(current + 1) + ":") size 22 color "#2a1a1a"
                    for opt in template["blanks"][current]:
                        textbutton ("· " + opt):
                            action [
                                SetScreenVariable("filled", filled[:current] + [opt] + filled[current+1:]),
                                If(current < 5,
                                   true=SetScreenVariable("current", current + 1),
                                   false=NullAction()),
                            ]
                            xsize 1600
                            text_xalign 0.0
                            text_size 22
                            text_color "#2a1a1a"
                            text_hover_color "#D85A30"
                    textbutton "   ✎ Custom phrase…   ":
                        action [
                            SetScreenVariable("custom_text", filled[current] if filled[current] else ""),
                            SetScreenVariable("editing_custom", True),
                        ]
                        text_size 22
                        text_color "#7a6a60"

            null height 6

            # Navigation + submit row.
            hbox:
                spacing 18
                xalign 0.5
                if current > 0:
                    textbutton "   ← Previous blank   " action SetScreenVariable("current", current - 1) text_size 22
                if current < 5:
                    textbutton "   Next blank →   " action SetScreenVariable("current", current + 1) text_size 22
                if all(f for f in filled):
                    textbutton "   Submit closing argument   ":
                        action [
                            Function(submit_verdict, target_var, template["intro"], filled),
                            Return(("submit", list(filled), current)),
                        ]
                        text_size 24

    # Floating OBJECTION! button for the opposing team. Only visible if they
    # still have a token. We return ("objection", filled, current) so the
    # calling label can re-enter this screen with the in-progress draft
    # restored after the objection menu resolves.
    if opposing_tokens > 0:
        frame:
            xalign 1.0 yalign 0.0
            xoffset -30 yoffset 30
            background "#D85A30"
            padding (24, 14)
            vbox:
                spacing 4
                xalign 0.5
                text "[opposing_team!c] counsel" size 16 color "#f5ede0" xalign 0.5
                textbutton "OBJECTION!":
                    action Return(("objection", list(filled), current))
                    text_size 30
                    text_color "#f5ede0"
                    text_hover_color "#fbf3e7"

# ------------------------------------------------------------
# Objection grounds picker — used when an opposing team throws an
# objection during the verdict director. Returning the picked ground
# (or None for "withdrawn") lets the calling label log it and re-enter.
# ------------------------------------------------------------

screen objection_pick(team):
    zorder 70
    modal True
    add "#2a1a1aE0"

    frame:
        xalign 0.5 yalign 0.5
        xsize 1200 ysize 580
        background "#f5ede0"
        padding (45, 36)

        vbox:
            spacing 18
            xalign 0.5
            text ("[team!c] counsel — on what grounds?") size 38 color "#D85A30" xalign 0.5
            text "Spending the token logs your objection on the closing draft." size 22 color "#7a6a60" xalign 0.5
            null height 9
            for g in OBJECTION_GROUNDS:
                textbutton g:
                    action Return(g)
                    xsize 1080
                    text_xalign 0.0
                    text_size 24
                    text_color "#2a1a1a"
                    text_hover_color "#D85A30"
                    background "#d8ccb8"
                    hover_background "#fbf3e7"
                    padding (18, 10)
            null height 6
            textbutton "   Withdraw — keep my token   " action Return(None) text_size 22 xalign 0.5

# ------------------------------------------------------------
# Ruling modal — replaces the textbox dialogue for displaying the verdict.
# Long Sonnet-4.6 rulings (1500+ chars) overflow the textbox; a centered
# scrollable frame handles arbitrary length cleanly. The Appeal button
# only renders when the losing team has the prestige to spend.
# ------------------------------------------------------------

screen ruling_modal(ruling, can_appeal_now, losing_team_name, is_appeal=False, court_header="", court_subheader="", caption="", before_line="", opinion_label="", disposition=""):
    zorder 100
    modal True
    add "#1a1010d8"

    frame:
        xalign 0.5 yalign 0.5
        xsize 1500 ysize 940
        background "#f5ede0"
        padding (54, 36, 54, 36)

        vbox:
            spacing 6
            xalign 0.5

            # ── Federal court header (WeThePeople display font) ──
            if court_header:
                text court_header:
                    xalign 0.5
                    size 44
                    color "#2a1a1a"
                    font "fonts/WeThePeople.ttf"
            if court_subheader:
                text court_subheader:
                    xalign 0.5
                    size 22
                    color "#7a6a60"

            # Decorative rule under the header.
            null height 4
            add Solid("#2a1a1a") xalign 0.5 xysize (1380, 2)
            null height 8

            # ── Case caption ──
            if caption:
                text caption:
                    xalign 0.5
                    size 26
                    color "#2a1a1a"
                    italic True

            if before_line:
                text before_line:
                    xalign 0.5
                    size 20
                    color "#5a4a40"

            # Disposition badge — only shows for appellate opinions
            if disposition:
                null height 4
                frame:
                    xalign 0.5
                    background ("#D85A30" if disposition == "REVERSED" else "#2a1a1a")
                    padding (16, 6, 16, 6)
                    text disposition:
                        size 20
                        color "#f5ede0"
                        bold True

            null height 6

            # Opinion title (e.g. OPINION OF THE COURT, CONCURRING, DISSENTING)
            $ default_label = ("APPEAL OPINION" if is_appeal else "OPINION OF THE COURT")
            text (opinion_label or default_label):
                xalign 0.5
                size 32
                color "#D85A30"
                bold True

            null height 10

            # ── Opinion body — scrollable viewport ──
            viewport:
                id "ruling_viewport"
                xsize 1380 ysize 480
                scrollbars "vertical"
                mousewheel True
                draggable True

                vbox:
                    text ruling:
                        substitute False
                        size 22
                        color "#2a1a1a"
                        xsize 1340
                        line_leading 4

            null height 8

            hbox:
                xalign 0.5
                spacing 30

                if can_appeal_now:
                    textbutton ("Spend [STAR_ICON] to appeal ([losing_team_name])"):
                        action Return("appeal")
                        background "#D85A30"
                        hover_background "#2a1a1a"
                        padding (28, 14, 28, 14)
                        text_size 24
                        text_color "#f5ede0"
                        text_xalign 0.5

                textbutton "Accept ruling":
                    action Return("accept")
                    background "#d8ccb8"
                    hover_background "#D85A30"
                    padding (28, 14, 28, 14)
                    text_size 24
                    text_color "#2a1a1a"
                    text_hover_color "#f5ede0"
                    text_xalign 0.5

# ------------------------------------------------------------
# End-of-run highlights — three recap cards before the run_end screen.
# ------------------------------------------------------------

screen run_highlights(payload):
    zorder 50
    modal True
    add "#2a1a1aE0"

    frame:
        xalign 0.5 yalign 0.5
        xsize 1700 ysize 940
        background "#f5ede0"
        padding (45, 36)

        vbox:
            spacing 18
            xalign 0.5
            text "RUN HIGHLIGHTS" size 60 color "#D85A30" xalign 0.5
            text ("[payload[u'winner']!c] takes the run.") size 30 color "#2a1a1a" xalign 0.5

            null height 6
            hbox:
                spacing 24
                xalign 0.5

                # Card 1 — Most memorable ruling.
                frame:
                    xsize 520 ysize 640
                    background "#fbf3e7"
                    padding (24, 18)
                    vbox:
                        spacing 9
                        text "MOST MEMORABLE RULING" size 24 color "#D85A30"
                        text ("Round " + str(payload["best_ruling"]["round"]) + " — " + payload["best_ruling"]["case_title"]) size 20 color "#7a6a60" italic True
                        null height 6
                        $ excerpt = payload["best_ruling"]["ruling_text"][:380] + ("…" if len(payload["best_ruling"]["ruling_text"]) > 380 else "")
                        text excerpt size 18 color "#2a1a1a"

                # Card 2 — Most ridiculous evidence.
                frame:
                    xsize 520 ysize 640
                    background "#fbf3e7"
                    padding (24, 18)
                    vbox:
                        spacing 9
                        text "MOST RIDICULOUS EVIDENCE" size 24 color "#D85A30"
                        if payload["evidence"]:
                            text ("Round " + str(payload["evidence"][0])) size 20 color "#7a6a60" italic True
                            null height 6
                            text payload["evidence"][2] size 22 color "#2a1a1a"
                            text ("(submitted by " + payload["evidence"][1] + ")") size 18 color "#7a6a60"
                        else:
                            text "No evidence was admitted this run." size 20 color "#2a1a1a"

                # Card 3 — Jury MVP.
                frame:
                    xsize 520 ysize 640
                    background "#fbf3e7"
                    padding (24, 18)
                    vbox:
                        spacing 9
                        text "JURY MVP" size 24 color "#D85A30"
                        if payload["mvp"]:
                            text payload["mvp"]["name"] size 26 color "#2a1a1a"
                            null height 6
                            text ("Seated " + str(payload["mvp"]["rounds"]) + " round(s) for the winning team.") size 18 color "#7a6a60" italic True
                        else:
                            text "Jury impact inconclusive." size 20 color "#2a1a1a"

            null height 12
            textbutton "   Continue   ":
                action Return(True)
                text_size 28
                xalign 0.5

# ------------------------------------------------------------
# Deliberating — shown while Claude is being called.
#
# Animation strategy: every 60ms a screen-local `delib_tick` int increments,
# which drives BOTH the dot phase and the sweeping progress bar position.
# Cycling status text rotates every ~1.5s. Timers inside screens are
# guaranteed to fire and re-render — unlike pure ATL transforms (which can
# stall under `renpy.pause(hard=True)` in some 8.x builds) this pattern is
# bulletproof and impossible to miss visually.
# ------------------------------------------------------------

# Single-element pulse — kept for the en-banc panel header reference.
transform delib_pulse:
    alpha 0.3
    block:
        ease 0.5 alpha 1.0
        ease 0.5 alpha 0.3
        repeat

# Status messages rotate while the API thinks. Picked at random per show.
default DELIB_STATUS_LINES = [
    "The court is reading the briefs...",
    "The judge consults the leather-bound case reporter...",
    "The bailiff brews fresh coffee...",
    "The reporter of decisions sharpens a pencil...",
    "Counsel pace nervously in the gallery...",
    "Someone shuffles papers loudly...",
    "The clerk locates the correct rubber stamp...",
    "The judge reviews the jury's facial expressions...",
    "The court considers the witness's testimony...",
    "A pigeon enters the courtroom and is escorted out...",
]

screen deliberating(label_text="The court deliberates...", subline="(and is probably eating a sandwich)", poll_for="ruling"):
    zorder 60
    modal True
    add "#2a1a1aE0"

    # `delib_tick` ticks every 60ms — drives bar sweep + dot cycle.
    default delib_tick = 0
    timer 0.06 action SetScreenVariable("delib_tick", (delib_tick + 1) % 600) repeat True

    # Polling timer — checks the appropriate ready function and Returns when
    # the worker thread completes. Screen-side polling is more reliable than
    # `renpy.pause(hard=True)` in a label loop, which can fail to pick up
    # state changes from the worker thread in some Ren'Py 8.x configurations.
    if poll_for == "ruling":
        timer 0.25 action If(claude_result_ready(), Return(True), NullAction()) repeat True
    elif poll_for == "cert":
        timer 0.25 action If(cert_question_ready(), Return(True), NullAction()) repeat True
    elif poll_for == "en_banc":
        timer 0.25 action If(en_banc_ready(), Return(True), NullAction()) repeat True

    # Hard safety-net timeout. If the worker is wedged for 90s the screen
    # force-exits with Return(False) so the player isn't trapped.
    default delib_seconds = 0
    timer 1.0 action SetScreenVariable("delib_seconds", delib_seconds + 1) repeat True
    if delib_seconds >= 90:
        timer 0.0 action Return(False)

    # Dot phase: 0..3, advances every ~0.4s.
    $ dot_phase = (delib_tick // 7) % 4

    # Bar value: sweeps 0→100→0 over ~2.4s.
    $ raw_pos = delib_tick % 40
    $ bar_value = raw_pos * 5 if raw_pos <= 20 else (40 - raw_pos) * 5

    # Status line: rotates every ~1.5s.
    $ status_idx = (delib_tick // 25) % len(DELIB_STATUS_LINES)
    $ status_line = DELIB_STATUS_LINES[status_idx]

    frame:
        xalign 0.5 yalign 0.5
        xsize 1200 ysize 520
        background "#f5ede0"
        padding (54, 42)

        vbox:
            spacing 18
            xalign 0.5
            yalign 0.5
            text label_text size 44 color "#2a1a1a" xalign 0.5
            text subline size 26 color "#7a6a60" xalign 0.5 italic True

            null height 18

            # Sweeping indeterminate progress bar.
            bar:
                xalign 0.5
                xsize 1020
                ysize 28
                value bar_value
                range 100
                left_bar Solid("#D85A30")
                right_bar Solid("#d8ccb8")
                thumb None
                thumb_shadow None

            null height 6

            # Cycling status line.
            text status_line size 26 color "#2a1a1a" xalign 0.5 italic True

            null height 12

            # The dingbats face has no plain dot glyph — closest compact
            # icon is the lowercase `n` (small gavel on a block). Three
            # pulsing gavels read as "the judge is mentally tapping while
            # thinking" — thematic, and visually distinct from the prestige
            # star (D).
            hbox:
                xalign 0.5
                spacing 32
                text "{font=fonts/laworder-dingbats.ttf}n{/font}" size 64 color ("#D85A30" if dot_phase >= 1 else "#3a2a2a")
                text "{font=fonts/laworder-dingbats.ttf}n{/font}" size 64 color ("#D85A30" if dot_phase >= 2 else "#3a2a2a")
                text "{font=fonts/laworder-dingbats.ttf}n{/font}" size 64 color ("#D85A30" if dot_phase >= 3 else "#3a2a2a")

            null height 12

            # Quiet skip button, in case the worker truly wedges. The label
            # treats Return(False) as "use whatever fallback is currently set".
            textbutton "   Skip & accept current ruling   ":
                action Return(False)
                xalign 0.5
                text_size 18
                text_color "#7a6a60"
                text_hover_color "#D85A30"

# ------------------------------------------------------------
# End-of-run screen
# ------------------------------------------------------------

screen run_end():
    zorder 50
    modal True
    add "#2a1a1aE0"

    frame:
        xalign 0.5 yalign 0.5
        xsize 1050 ysize 450
        background "#f5ede0"
        padding (45, 36)

        vbox:
            spacing 21
            xalign 0.5
            text ("[run_winner()!c] wins the run!") size 54 color "#D85A30" xalign 0.5
            text ("Final — Plaintiff [scores[u'plaintiff']] · Defendant [scores[u'defendant']]") size 30 color "#2a1a1a" xalign 0.5
            null height 24
            textbutton "   New game   ":
                action Return(True)
                text_size 33
                xalign 0.5

# ------------------------------------------------------------
# En banc panel — three judges deliberate the certified question.
# Same animation pattern as `deliberating` so timers fire.
# ------------------------------------------------------------

screen en_banc_panel(panel_judges, cert_q):
    zorder 60
    modal True
    add "#2a1a1aE0"

    # Screen-side polling — Returns when all 3 panel workers have set their
    # done_flags. Plus a 120s safety net (3× the single-call timeout).
    timer 0.25 action If(en_banc_ready(), Return(True), NullAction()) repeat True
    default panel_seconds = 0
    timer 1.0 action SetScreenVariable("panel_seconds", panel_seconds + 1) repeat True
    if panel_seconds >= 120:
        timer 0.0 action Return(False)

    # Tick for dot animation.
    default panel_tick = 0
    timer 0.06 action SetScreenVariable("panel_tick", (panel_tick + 1) % 600) repeat True
    $ panel_dot_phase = (panel_tick // 7) % 4

    frame:
        xalign 0.5 yalign 0.5
        xsize 1620 ysize 780
        background "#f5ede0"
        padding (54, 42, 54, 42)

        vbox:
            spacing 16
            xalign 0.5

            text "United States Court of Appeals":
                xalign 0.5
                size 38
                color "#2a1a1a"
                font "fonts/WeThePeople.ttf"
            text "FOR THE TWELFTH CIRCUIT — EN BANC REVIEW":
                xalign 0.5
                size 20
                color "#7a6a60"

            null height 4
            add Solid("#2a1a1a") xalign 0.5 xysize (1500, 2)
            null height 4

            text "Certified question:" size 22 color "#7a6a60" xalign 0.5
            text cert_q:
                xalign 0.5
                xsize 1480
                size 22
                color "#2a1a1a"
                substitute False
                text_align 0.5

            null height 6

            hbox:
                spacing 36
                xalign 0.5
                for j in panel_judges:
                    vbox:
                        spacing 6
                        xalign 0.5
                        add ("images/judges/" + j["id"] + ".png") zoom 0.16 xalign 0.5
                        text j["name"] size 18 color "#2a1a1a" xalign 0.5

            null height 8

            # Constrain the gavel row to its own fixed-size frame so the
            # glyphs (which the dingbats face renders wider than their
            # nominal pt size) cannot drift past the modal edge.
            frame:
                xalign 0.5
                xsize 420 ysize 90
                background None
                padding (0, 0, 0, 0)
                hbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 36
                    text "{font=fonts/laworder-dingbats.ttf}n{/font}" size 56 color ("#D85A30" if panel_dot_phase >= 1 else "#3a2a2a")
                    text "{font=fonts/laworder-dingbats.ttf}n{/font}" size 56 color ("#D85A30" if panel_dot_phase >= 2 else "#3a2a2a")
                    text "{font=fonts/laworder-dingbats.ttf}n{/font}" size 56 color ("#D85A30" if panel_dot_phase >= 3 else "#3a2a2a")

# ------------------------------------------------------------
# Styles for the say screen. The auto-generated Ren'Py template defines
# `style window`, `style namebox`, `style say_label`, `style say_dialogue`
# in screens.rpy — without them, the say screen falls back to the default
# (top-left, default font) and crashes on namebox lookup. We re-create
# them here, themed for the cream-on-dark Objection! palette.
# ------------------------------------------------------------

style window is default
style say_label is default
style say_dialogue is default
style say_thought is say_dialogue

style namebox is default
style namebox_label is say_label

style window:
    xalign 0.5
    yalign 1.0
    yoffset -36
    xsize 1500
    ysize gui.textbox_height
    # Slightly more transparent (~62% alpha) so the judge body is clearly
    # visible behind the textbox — reads as "the judge is speaking from
    # there" rather than "the textbox is covering the textbox."
    background "#1a10109e"
    padding (54, 30, 54, 30)

style namebox:
    xpos gui.name_xpos
    xanchor 0.0
    ypos gui.name_ypos
    xsize gui.namebox_width
    ysize gui.namebox_height
    background "#D85A30"
    padding (20, 10, 20, 10)

style say_label:
    color "#f5ede0"
    font gui.name_text_font
    size 32
    bold True
    xalign 0.0
    yalign 0.5

style say_dialogue:
    font gui.text_font
    size gui.text_size
    color "#f5ede0"
    xpos gui.dialogue_xpos
    ypos gui.dialogue_ypos
    xsize gui.dialogue_width
    line_leading 4

# Default text everywhere uses our newspaper font.
style default:
    font gui.text_font
    color gui.text_color
    size gui.text_size

style button_text:
    font gui.button_text_font
    size gui.button_text_size

# ------------------------------------------------------------
# Choice menu (the "Next case?" / appeal menu rendered via Ren'Py's built-in
# `menu:` blocks). Default style draws no background, so dark choice text
# on the courtroom backdrop was unreadable. Cream button + dark text gives
# proper contrast.
# ------------------------------------------------------------

style choice_vbox:
    spacing 18
    xalign 0.5
    yalign 0.5

style choice_button is default:
    background "#f5ede0"
    hover_background "#D85A30"
    xsize 1100
    xalign 0.5
    padding (30, 18, 30, 18)

style choice_button_text is default:
    font gui.text_font
    size 30
    color "#2a1a1a"
    hover_color "#f5ede0"
    selected_color "#D85A30"
    xalign 0.5

# ------------------------------------------------------------
# Game menu (Esc → Save/Load/Preferences/Quit). Default Ren'Py uses
# gui.game_menu_background (#f5ede0 cream) but on this build it was
# rendering as transparent over the courtroom — dark text was nearly
# invisible. Force a solid cream backing and theme all the menu element
# colors against it.
# ------------------------------------------------------------

style game_menu_outer_frame is empty:
    background "#f5ede0"
    xfill True
    yfill True

style game_menu_navigation_frame:
    xsize 360
    yfill True
    background "#2a1a1a"
    padding (30, 30, 30, 30)

style game_menu_content_frame is empty:
    left_margin 60
    right_margin 60
    top_margin 30
    bottom_margin 30

style game_menu_label is gui_label:
    xpos 60
    ysize 180

style game_menu_label_text:
    font gui.text_font
    size 50
    color "#D85A30"

style return_button is navigation_button:
    xpos 60
    yalign 1.0
    yoffset -45

style return_button_text is navigation_button_text

style navigation_button is gui_button:
    xsize 290
    background None

style navigation_button_text:
    font gui.text_font
    size 26
    color "#d8ccb8"
    hover_color "#D85A30"
    selected_color "#f5ede0"

style page_label_text:
    color "#2a1a1a"
    size 22

style page_button is gui_button:
    background None
    padding (12, 6, 12, 6)

style page_button_text:
    font gui.text_font
    size 22
    color "#7a6a60"
    hover_color "#D85A30"
    selected_color "#2a1a1a"

style slot_button is gui_button:
    background "#d8ccb8"
    hover_background "#D85A30"
    xsize 414
    ysize 309
    padding (15, 15, 15, 15)

style slot_button_text:
    font gui.text_font
    size 20
    color "#2a1a1a"
    hover_color "#f5ede0"
    selected_color "#D85A30"

style slot_time_text is slot_button_text
style slot_name_text is slot_button_text

style pref_label_text:
    color "#2a1a1a"
    size 28

style pref_vbox:
    xsize 300

style radio_button is gui_button:
    background None

style radio_button_text:
    font gui.text_font
    size 22
    color "#7a6a60"
    hover_color "#D85A30"
    selected_color "#D85A30"

style check_button is radio_button
style check_button_text is radio_button_text

style about_label_text:
    color "#2a1a1a"
    size 24

style help_label_text:
    color "#2a1a1a"
    size 28

# ------------------------------------------------------------
# Themed vertical scrollbar for the ruling modal's viewport. Default
# Ren'Py scrollbars are gray/blue and clash with the cream/orange palette.
# These styles override the global vscrollbar so any viewport with
# `scrollbars "vertical"` picks up our theme.
# ------------------------------------------------------------

style vscrollbar:
    xsize 16
    base_bar Solid("#d8ccb8")
    thumb Solid("#D85A30")
    bar_vertical True

style vscrollbar_thumb:
    background Solid("#D85A30")

# ------------------------------------------------------------
# Custom `choice` screen — Ren'Py uses this for any `menu:` block. The
# engine fallback was rendering with no background and tiny text, hence
# the overlapping "Next case?" / "Yes — next case" / "New game" mess in
# screenshots. This replaces it with cream buttons, big readable text,
# and a stable centered layout.
# ------------------------------------------------------------

screen choice(items):
    style_prefix "choice"
    add "#1a1010c0"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 18

        for i in items:
            textbutton i.caption:
                action i.action
                xsize 1100
                xalign 0.5
                background "#f5ede0"
                hover_background "#D85A30"
                padding (30, 18, 30, 18)
                text_size 30
                text_color "#2a1a1a"
                text_hover_color "#f5ede0"
                text_xalign 0.5

# ------------------------------------------------------------
# Game menu wrapper + Save / Load / Preferences screens.
#
# We don't ship the auto-generated Ren'Py screens.rpy, so the engine was
# falling back to bare-bones layouts (the "Empty Slot. Empty Slot." dark-
# on-dark screenshot the user reported). These deliberately-themed
# replacements use our cream/orange palette.
# ------------------------------------------------------------

screen game_menu_nav():
    # Right-side navigation rail used by every game-menu sub-screen.
    vbox:
        xalign 1.0 yalign 0.5
        xoffset -60
        spacing 16
        textbutton _("Resume") action Return() text_size 28 text_color "#7a6a60" text_hover_color "#D85A30"
        textbutton _("Save") action ShowMenu("save") text_size 28 text_color "#7a6a60" text_hover_color "#D85A30"
        textbutton _("Load") action ShowMenu("load") text_size 28 text_color "#7a6a60" text_hover_color "#D85A30"
        textbutton _("Preferences") action ShowMenu("preferences") text_size 28 text_color "#7a6a60" text_hover_color "#D85A30"
        textbutton _("Main Menu") action MainMenu() text_size 28 text_color "#7a6a60" text_hover_color "#D85A30"
        textbutton _("Quit") action Quit(confirm=not main_menu) text_size 28 text_color "#7a6a60" text_hover_color "#D85A30"

screen file_slots(title, save_mode):
    # Shared 3×2 file-slot grid used by save and load.
    add "#f5ede0"

    text title:
        xpos 60 ypos 30
        size 56 color "#D85A30"

    # Page selector.
    hbox:
        xalign 0.5 ypos 110
        spacing 18
        textbutton _("<") action FilePagePrevious() text_size 28 text_color "#7a6a60" text_hover_color "#D85A30"
        for page in range(1, 9):
            textbutton "[page]":
                action FilePage(page)
                text_size 26
                text_color "#7a6a60"
                text_hover_color "#D85A30"
                text_selected_color "#D85A30"
        textbutton _(">") action FilePageNext() text_size 28 text_color "#7a6a60" text_hover_color "#D85A30"

    grid 3 2:
        xalign 0.5 ypos 200
        xspacing 30
        yspacing 30
        for slot in range(1, 7):
            button:
                action (FileAction(slot) if save_mode else FileLoad(slot))
                xsize 440 ysize 320
                background "#d8ccb8"
                hover_background "#D85A30"
                padding (18, 12, 18, 12)
                vbox:
                    spacing 8
                    text "[slot]. [FileTime(slot, format=_('%A, %B %d %Y, %H:%M'), empty=_('empty slot'))!t]" size 18 color "#2a1a1a"
                    text "[FileSaveName(slot)]" size 16 color "#5a4a40"
                    if FileLoadable(slot):
                        add FileScreenshot(slot) xalign 0.5

    use game_menu_nav

screen save():
    tag menu
    use file_slots(_("Save Game"), True)

screen load():
    tag menu
    use file_slots(_("Load Game"), False)

screen confirm(message, yes_action, no_action):
    # Used by Ren'Py for "Are you sure you want to quit?" and similar.
    # Engine fallback rendered dark text on black — this provides a themed
    # cream box matching the rest of our UI.
    modal True
    zorder 200

    add "#1a1010d0"

    frame:
        xalign 0.5 yalign 0.5
        xsize 900 ysize 320
        background "#f5ede0"
        padding (45, 36, 45, 36)

        vbox:
            spacing 30
            xalign 0.5
            yalign 0.5
            text message:
                xalign 0.5
                size 32
                color "#2a1a1a"
                text_align 0.5

            hbox:
                spacing 30
                xalign 0.5
                textbutton _("Yes"):
                    action yes_action
                    xsize 200
                    background "#D85A30"
                    hover_background "#2a1a1a"
                    padding (24, 14, 24, 14)
                    text_size 28
                    text_color "#f5ede0"
                    text_xalign 0.5
                textbutton _("No"):
                    action no_action
                    xsize 200
                    background "#d8ccb8"
                    hover_background "#D85A30"
                    padding (24, 14, 24, 14)
                    text_size 28
                    text_color "#2a1a1a"
                    text_hover_color "#f5ede0"
                    text_xalign 0.5

screen preferences():
    tag menu
    add "#f5ede0"

    text _("Preferences"):
        xpos 60 ypos 30
        size 56 color "#D85A30"

    vbox:
        xalign 0.5 yalign 0.5
        xsize 1300
        spacing 36

        hbox:
            spacing 60
            xalign 0.5

            vbox:
                xsize 360
                spacing 12
                text _("Display") size 26 color "#2a1a1a" bold True
                textbutton _("Window") action Preference("display", "window") text_size 22 text_color "#7a6a60" text_hover_color "#D85A30" text_selected_color "#D85A30"
                textbutton _("Fullscreen") action Preference("display", "fullscreen") text_size 22 text_color "#7a6a60" text_hover_color "#D85A30" text_selected_color "#D85A30"

            vbox:
                xsize 360
                spacing 12
                text _("Skip") size 26 color "#2a1a1a" bold True
                textbutton _("Unseen Text") action Preference("skip", "toggle") text_size 22 text_color "#7a6a60" text_hover_color "#D85A30" text_selected_color "#D85A30"
                textbutton _("After Choices") action Preference("after choices", "toggle") text_size 22 text_color "#7a6a60" text_hover_color "#D85A30" text_selected_color "#D85A30"

        hbox:
            spacing 60
            xalign 0.5

            vbox:
                xsize 420
                spacing 8
                text _("Music Volume") size 24 color "#2a1a1a"
                bar value Preference("music volume") xsize 360
            vbox:
                xsize 420
                spacing 8
                text _("Sound Volume") size 24 color "#2a1a1a"
                bar value Preference("sound volume") xsize 360
            vbox:
                xsize 420
                spacing 8
                text _("Text Speed") size 24 color "#2a1a1a"
                bar value Preference("text speed") xsize 360

    use game_menu_nav
