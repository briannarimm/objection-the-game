# All phase labels. The round loops through them in order, exiting back to
# `round_start` until a team hits 3 wins.

# ------------------------------------------------------------
# CASE phase — reveal the case and the presiding judge
# ------------------------------------------------------------

label phase_case:
    # Backdrop = full-bleed courtroom. Judge sits left, scenario card floats
    # right; both render on the master layer so the textbox draws over them.
    # Cases without a dedicated scenario image use their category placeholder
    # (food/machine/outdoor/wellness) — same `scenario_right` transform so
    # the on-screen format is identical.
    scene bg courtroom with dissolve
    $ scenario_id = case_card.get("scenario") if case_card else None
    if not scenario_id and case_card:
        $ scenario_id = case_card.get("cat")
    if scenario_id:
        show expression ("scenario_card " + scenario_id) as scenariopic at scenario_right with dissolve

    show expression ("judge " + judge["id"]) as judgepic at judge_left with dissolve
    $ hide_hud = False

    reporter "All rise. Today's docket: [case_card[u'title']]."
    reporter "[case_card[u'desc']]"
    reporter "Presiding: [judge[u'name']]. [judge[u'trait']] — [judge[u'flavor']]."

    judgechar "Proceed with jury selection."
    hide judgepic with dissolve
    if scenario_id:
        hide scenariopic with dissolve
    return

# ------------------------------------------------------------
# JURY phase — 4 alternating picks (P, D, P, D)
# ------------------------------------------------------------

label phase_jury:
    scene bg courtroom with dissolve
    reporter "Counsel, seat your jury. Plaintiff picks first; teams alternate. 3 picks each."

    $ step = 0
    while step < 6:
        $ turn = "Plaintiff" if step % 2 == 0 else "Defendant"
        call screen jury_selection(turn_team=turn)
        $ picked = _return
        if turn == "Plaintiff":
            $ p_jury = p_jury + [picked]
        else:
            $ d_jury = d_jury + [picked]
        $ jury_pool = [j for j in jury_pool if j["name"] != picked["name"]]
        $ step += 1

    reporter "Jury seated. Let the motions fly."
    return

# ------------------------------------------------------------
# MOTIONS phase — 45 second review timer + one question per team to
# determine whether the motions are presented as credible or weakly supported.
# ------------------------------------------------------------

label phase_motions:
    scene bg courtroom with dissolve
    play sound "audio/objection_sting.ogg"
    show screen objection_banner("HOLD IT!") with dissolve
    pause 1.0
    hide screen objection_banner

    $ motion_time_left = MOTION_TIME_SECONDS
    call screen motions_display

    reporter "Time's up. Counsel — prioritize your motions and decide whether to gamble on a wild card."

    # ---- Plaintiff: rank → wild → strength question ----
    call screen motion_ranking(team="plaintiff", cards=p_cards)
    $ p_cards = _return

    call screen wild_offer(team="plaintiff", hindmost=p_cards[2])
    $ choice = _return
    if choice == "draw":
        $ wild_options = _shuffled(WILD_MOTIONS)[:3]
        call screen wild_pick(team="plaintiff", options=wild_options)
        $ p_wild = _return
        $ p_cards = p_cards[:2] + [p_wild]
        reporter "Plaintiff burns the #3 filing and pulls: [p_wild]."

    $ pq = fresh_question()
    $ remember_asked(pq)
    call screen ask_question(team="plaintiff", q=pq, header="Motion Justification")
    $ picked = _return
    $ p_motion_strong = is_correct(pq, picked)
    if p_motion_strong:
        reporter "Plaintiff's counsel grounds the motions in solid authority."
    else:
        reporter "Plaintiff's counsel fumbles the citation. Motions filed but weakly supported."
        reporter "(The correct answer was: [pq[u'a']].)"

    # ---- Defendant: rank → wild → strength question ----
    call screen motion_ranking(team="defendant", cards=d_cards)
    $ d_cards = _return

    call screen wild_offer(team="defendant", hindmost=d_cards[2])
    $ choice = _return
    if choice == "draw":
        $ wild_options = _shuffled(WILD_MOTIONS)[:3]
        call screen wild_pick(team="defendant", options=wild_options)
        $ d_wild = _return
        $ d_cards = d_cards[:2] + [d_wild]
        reporter "Defense burns the #3 filing and pulls: [d_wild]."

    $ dq = fresh_question()
    $ remember_asked(dq)
    call screen ask_question(team="defendant", q=dq, header="Motion Justification")
    $ picked = _return
    $ d_motion_strong = is_correct(dq, picked)
    if d_motion_strong:
        reporter "Defense counsel locks in a clean legal foundation."
    else:
        reporter "Defense counsel mumbles through the doctrine. Motions filed but weakly supported."
        reporter "(The correct answer was: [dq[u'a']].)"

    reporter "Witness selection next."
    return

# ------------------------------------------------------------
# WITNESS phase — each team calls 1 of 3 witnesses from a shuffled pool.
# Witness `cred` (credibility) tilt is sent to the AI ruling prompt; vibe
# is shown publicly during selection.
# ------------------------------------------------------------

label phase_witnesses:
    scene bg courtroom with dissolve
    reporter "Counsel, call your first witness. Each side picks one from the available pool."

    # Plaintiff picks from the first 3 of the shuffled pool.
    $ p_pool = witness_pool[:3]
    call screen witness_pick(team="Plaintiff", pool=p_pool)
    $ p_witness = _return
    play sound "audio/whoosh_card.ogg"
    $ witness_pool = [w for w in witness_pool if w["name"] != p_witness["name"]]
    reporter "Plaintiff calls [p_witness[u'name']], [p_witness[u'occ']]."

    # Defendant picks from the next 3 of what's left.
    $ d_pool = witness_pool[:3]
    call screen witness_pick(team="Defendant", pool=d_pool)
    $ d_witness = _return
    play sound "audio/whoosh_card.ogg"
    $ witness_pool = [w for w in witness_pool if w["name"] != d_witness["name"]]
    reporter "Defense calls [d_witness[u'name']], [d_witness[u'occ']]."

    reporter "Discovery next — submit your evidence."
    return

# ------------------------------------------------------------
# Bench conference — judge calls a sidebar between phases. Picks 2 random
# lines from SIDEBAR_LINES plus the judge's own flavor for personality.
# Sets bench_done_this_round so it only fires once per round.
# ------------------------------------------------------------

label bench_conference:
    if bench_done_this_round:
        return
    $ bench_done_this_round = True
    scene bg courtroom with dissolve
    show expression ("judge " + judge["id"]) as judgepic at judge_left with dissolve
    play sound "audio/gavel_slam.ogg"
    judgechar "Counsel, approach the bench."
    $ lines = _shuffled(SIDEBAR_LINES)[:2]
    $ first_line = lines[0]
    $ second_line = lines[1]
    judgechar "[first_line]"
    judgechar "[judge[u'flavor']!c], by the way."
    judgechar "[second_line]"
    judgechar "Carry on."
    hide judgepic with dissolve
    return

# ------------------------------------------------------------
# DISCOVERY phase — each team picks 1 of 3 evidence items, then
# answers an admissibility question. Wrong answer = excluded.
# ------------------------------------------------------------

label phase_discovery:
    scene bg courtroom with dissolve

    call screen discovery_pick(team="Plaintiff", pool=p_ev_pool)
    $ p_ev = _return

    $ pq = fresh_question()
    $ remember_asked(pq)
    call screen ask_question(team="plaintiff", q=pq, header="Admissibility Challenge")
    $ picked = _return
    $ p_ev_admissible = is_correct(pq, picked)
    if p_ev_admissible:
        reporter "Plaintiff's evidence is admitted."
    else:
        reporter "Sustained — plaintiff's evidence is excluded. The judge will not consider it."
        reporter "(The correct answer was: [pq[u'a']].)"

    call screen discovery_pick(team="Defendant", pool=d_ev_pool)
    $ d_ev = _return

    $ dq = fresh_question()
    $ remember_asked(dq)
    call screen ask_question(team="defendant", q=dq, header="Admissibility Challenge")
    $ picked = _return
    $ d_ev_admissible = is_correct(dq, picked)
    if d_ev_admissible:
        reporter "Defense exhibit is admitted."
    else:
        reporter "Sustained — defense exhibit excluded."
        reporter "(The correct answer was: [dq[u'a']].)"

    reporter "Evidence logged. Time for a surprise trivia challenge."
    return

# ------------------------------------------------------------
# TRIVIA phase — first team to buzz picks an answer, wins ★ if correct
# ------------------------------------------------------------

label phase_trivia:
    scene bg courtroom with dissolve
    $ remember_asked(trivia_q)

    call screen trivia_buzzer
    $ buzzer_team = _return

    call screen ask_question(team=buzzer_team, q=trivia_q, header="Trivia Buzz-In")
    $ picked_opt = _return

    $ correct = award_question_prestige(buzzer_team, trivia_q, picked_opt)
    if correct:
        play sound "audio/prestige_ding.ogg"
        reporter "Correct! [STAR_ICON] prestige token to the [buzzer_team] team."
    else:
        reporter "Incorrect. The correct answer was: [trivia_q[u'a']]."
    return

# ------------------------------------------------------------
# SETTLEMENT phase — plaintiff offers; if they offer, they answer a
# preparatory question that strengthens (or weakens) the offer.
# Defendant accepts/rejects. On accept, BOTH teams bank ★.
# ------------------------------------------------------------

label phase_settlement:
    scene bg courtroom with dissolve
    call screen settle_offer
    $ choice = _return

    if choice == "skip":
        $ settle_offer = ""
        reporter "Plaintiff demands a full trial. No settlement offered."
        return

    $ settle_offer = choice

    # Plaintiff answers a preparatory question to strengthen the offer.
    $ sq = fresh_question()
    $ remember_asked(sq)
    call screen ask_question(team="plaintiff", q=sq, header="Settlement Prep")
    $ picked = _return
    $ settle_strengthened = is_correct(sq, picked)
    if settle_strengthened:
        reporter "Plaintiff cites authority precisely. The offer carries weight."
    else:
        reporter "Plaintiff fumbles. The offer is on the table without much heft."
        reporter "(The correct answer was: [sq[u'a']].)"

    call screen settle_response(offer=settle_offer, strengthened=settle_strengthened)
    $ resp = _return

    if resp == "accept":
        $ settle_accept()
        play sound "audio/prestige_ding.ogg"
        reporter "Defendant accepts. Case closed without verdict — both teams bank [STAR_ICON]."
    else:
        $ settle_resp = "reject"
        reporter "Defendant rejects the offer. To arguments."
    return

# ------------------------------------------------------------
# ARGUMENTS phase — text input per team
# ------------------------------------------------------------

label phase_arguments:
    scene bg courtroom with dissolve
    play sound "audio/objection_sting.ogg"
    show screen objection_banner("OBJECTION!") with dissolve
    pause 1.0
    hide screen objection_banner

    $ template = get_verdict_template(case_card)
    play sound "audio/typewriter_loop.ogg"

    # ---- Plaintiff closing ----
    $ p_arg = ""
    $ p_filled = ["", "", "", "", "", ""]
    $ p_cur = 0
    $ p_done = False
    while not p_done:
        call screen verdict_director(team="Plaintiff", target_var="p_arg", template=template["plaintiff"], initial_filled=p_filled, initial_current=p_cur)
        $ ret = _return
        $ tag = ret[0] if isinstance(ret, tuple) else None
        if tag == "objection":
            $ p_filled = list(ret[1])
            $ p_cur = ret[2]
            # Defense spends a token to throw an objection on plaintiff's draft.
            call screen objection_pick(team="Defendant")
            $ ground = _return
            if ground:
                $ d_obj_tokens = max(0, d_obj_tokens - 1)
                $ p_arg_objections = list(p_arg_objections) + [ground]
                play sound "audio/objection_sting.ogg"
                show screen objection_banner("OBJECTION!") with dissolve
                pause 0.8
                hide screen objection_banner
                reporter "Defense objects on grounds of [ground]. Noted for the record."
            # Loop re-enters verdict_director with preserved p_filled/p_cur.
        else:
            $ p_done = True

    # ---- Defendant closing ----
    $ d_arg = ""
    $ d_filled = ["", "", "", "", "", ""]
    $ d_cur = 0
    $ d_done = False
    while not d_done:
        call screen verdict_director(team="Defendant", target_var="d_arg", template=template["defendant"], initial_filled=d_filled, initial_current=d_cur)
        $ ret = _return
        $ tag = ret[0] if isinstance(ret, tuple) else None
        if tag == "objection":
            $ d_filled = list(ret[1])
            $ d_cur = ret[2]
            call screen objection_pick(team="Plaintiff")
            $ ground = _return
            if ground:
                $ p_obj_tokens = max(0, p_obj_tokens - 1)
                $ d_arg_objections = list(d_arg_objections) + [ground]
                play sound "audio/objection_sting.ogg"
                show screen objection_banner("OBJECTION!") with dissolve
                pause 0.8
                hide screen objection_banner
                reporter "Plaintiff objects on grounds of [ground]. Noted for the record."
        else:
            $ d_done = True

    return

# ------------------------------------------------------------
# RULING phase — call Claude, show deliberation screen, display verdict,
# offer appeal if possible, check for run end.
# ------------------------------------------------------------

label phase_ruling:
    scene bg courtroom with dissolve
    play music "audio/tense_deliberation.ogg" fadein 0.6
    $ request_ruling_async(False)

    # Screen-side polling: the deliberating screen's own timer checks
    # claude_result_ready() every 250ms and Returns when done. This is more
    # reliable than label-side `renpy.pause(hard=True)` polling, which can
    # fail to pick up state changes from the worker thread under some
    # Ren'Py 8.x configurations. The screen also has a 90s hard timeout +
    # manual skip button as safety nets.
    call screen deliberating(label_text="The court deliberates...", subline="(and is probably eating a sandwich)", poll_for="ruling")

    $ (text, w, is_appeal) = consume_claude_result()
    $ apply_verdict(text, w, is_appeal)

label phase_ruling_display:
    play music "audio/courtroom_ambient.ogg" fadein 0.8
    play sound "audio/gavel_slam.ogg"
    play sound "audio/verdict_fanfare.ogg"
    # Judge delivers the verdict in a centered modal so long rulings don't
    # overflow the textbox. Appeal button is shown inline only when the
    # losing team has the prestige to spend.
    show expression ("judge " + judge["id"]) as judgepic at judge_left with dissolve

    $ _can_appeal = (settle_resp != "accept" and can_appeal())
    $ _losing = losing_team() if _can_appeal else ""
    $ _trial_caption = "%s, Plaintiff, v. The Defendant — \"%s\"" % ("The People" if False else "The Plaintiff", case_card["title"])
    $ _trial_before = "Before %s, %s." % (judge["name"], "District Judge")
    call screen ruling_modal(
        ruling=ruling_text,
        can_appeal_now=_can_appeal,
        losing_team_name=_losing,
        is_appeal=False,
        court_header=DISTRICT_COURT_HEADER,
        court_subheader=DISTRICT_COURT_SUBHEADER,
        caption=_trial_caption,
        before_line=_trial_before,
        opinion_label="Opinion of the Court",
        disposition="",
    )
    $ ruling_choice = _return

    if ruling_choice == "appeal" and _can_appeal:
        $ spend_appeal()
        play sound "audio/crowd_gasp.ogg"
        reporter "Appeal filed. The trial judge will certify a question for review..."

        # Step 1: ask Claude to draft a certified question.
        play music "audio/tense_deliberation.ogg" fadein 0.6
        $ request_cert_question_async()
        call screen deliberating(label_text="Drafting certified question...", subline="(the judge consults the Reporter of Decisions)", poll_for="cert")
        $ cert_question = consume_cert_question()

        reporter "Certified question:"
        reporter "[cert_question]"

        # Step 2: assemble a 3-judge panel (different from trial judge).
        $ en_banc_judges = pick_en_banc_panel()
        $ p_names = ", ".join([j["name"] for j in en_banc_judges])
        reporter "An en banc panel will hear the appeal: [p_names]."

        # Step 3: ask the panel to rule (3 parallel API calls).
        $ request_en_banc_async(en_banc_judges, cert_question)
        call screen en_banc_panel(panel_judges=en_banc_judges, cert_q=cert_question)
        $ en_banc_results = consume_en_banc_results()

        # Step 4: compute majority FIRST so each panel judge's opinion
        # carries its proper label (Opinion of the Court / Concurring /
        # Dissenting) when displayed. apply_verdict happens after the
        # opinions roll so ruling_text holds the summary line.
        $ (panel_winner, panel_summary) = en_banc_majority()
        $ trial_winner_pre_appeal = winner
        $ label_panel_opinions(panel_winner, trial_winner_pre_appeal)
        play music "audio/courtroom_ambient.ogg" fadein 0.8
        hide judgepic with dissolve
        $ _appeal_caption = "On Appeal — \"%s\"" % case_card["title"]
        $ _idx = 0
        while _idx < len(en_banc_results):
            $ panel_r = en_banc_results[_idx]
            $ panel_text = panel_r["text"]
            $ panel_judge_obj = panel_r["judge"]
            $ panel_before = "Before %s, Circuit Judge." % panel_judge_obj["name"]
            $ panel_label = panel_r.get("opinion_label", "Opinion")
            $ panel_disp = panel_r.get("disposition", "")
            show expression ("judge " + panel_judge_obj["id"]) as judgepic at judge_left with dissolve
            play sound "audio/gavel_slam.ogg"
            call screen ruling_modal(
                ruling=panel_text,
                can_appeal_now=False,
                losing_team_name="",
                is_appeal=True,
                court_header=CIRCUIT_COURT_HEADER,
                court_subheader=CIRCUIT_COURT_SUBHEADER,
                caption=_appeal_caption,
                before_line=panel_before,
                opinion_label=panel_label,
                disposition=panel_disp,
            )
            hide judgepic with dissolve
            $ _idx += 1

        $ apply_verdict(panel_summary, panel_winner, True)
        play sound "audio/verdict_fanfare.ogg"
        reporter "[panel_summary]"
    else:
        hide judgepic with dissolve

    if run_is_over():
        call screen run_end
        $ reset_game()
        return

    menu:
        "Next case?"
        "Next case":
            pass
        "New game":
            $ reset_game()
    return
