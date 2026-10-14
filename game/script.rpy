# Entry point. `label start` is Ren'Py's standard game-start label.

label start:
    # The hero-gavel splash and Start button live in screen main_menu().
    # Once the player clicks Play, this label runs.
    $ hide_hud = True
    scene bg courtroom with dissolve
    play music "audio/courtroom_ambient.ogg" fadein 1.0

    narrator "Two teams. Procedurally generated personal injury cases. The AI judge rules."
    narrator "First team to 3 wins takes the run."

    show screen hud
    $ hide_hud = False

    jump round_loop


label round_loop:
    $ start_round()

    call phase_case from _call_phase_case
    call phase_jury from _call_phase_jury
    call phase_motions from _call_phase_motions

    # 40% chance the judge calls a sidebar after motions. Once per round.
    $ _bench_roll = renpy.random.random()
    if _bench_roll < 0.4:
        call bench_conference from _call_bench_conf_after_motions

    call phase_witnesses from _call_phase_witnesses
    call phase_discovery from _call_phase_discovery
    call phase_trivia from _call_phase_trivia
    call phase_settlement from _call_phase_settlement

    # If settlement was accepted, settle_accept() populated ruling_text already;
    # skip arguments/API call and jump straight to displaying the ruling.
    if settle_resp == "accept":
        call phase_ruling_display from _call_phase_ruling_display_settled
        $ append_round_history(settled=True)
    else:
        call phase_arguments from _call_phase_arguments
        call phase_ruling from _call_phase_ruling
        $ append_round_history()

    if run_is_over():
        $ _payload = highlight_payload()
        if _payload:
            call screen run_highlights(payload=_payload)
        return

    jump round_loop
