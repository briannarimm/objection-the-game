# Runtime game state + round helpers.
# Everything here is a plain Python object/function, so Ren'Py's save system
# will persist it just fine.

default scores = {"plaintiff": 0, "defendant": 0}
# Both teams start with 1 prestige star so an appeal is always reachable in
# round 1 — losing-team-with-zero-stars meant the appeal flow was never
# exercised on first-round rulings.
default prestige = {"plaintiff": 1, "defendant": 1}

default case_card = None
default judge = None

default jury_pool = []
default p_jury = []
default d_jury = []

default p_cards = []
default d_cards = []

# Wild card drawn (if any) during the wild-draw phase — replaces the team's
# #3 motion. None if the team skipped the wild draw.
default p_wild = None
default d_wild = None

# Outcome of the motions phase per team — affects how the AI judge sees the
# motion cards. True = "credible legal grounding"; False = "asserted but
# weakly supported."
default p_motion_strong = False
default d_motion_strong = False

default p_ev_pool = []
default d_ev_pool = []
default p_ev = None
default d_ev = None

# Whether each team's evidence is admissible (judge sees it). False if the
# team failed the discovery question — judge is told the evidence was excluded.
default p_ev_admissible = True
default d_ev_admissible = True

default trivia_q = None
default trivia_bonus = ""     # "plaintiff" / "defendant" / ""

# Per-round bookkeeping to avoid showing the same question twice in one round.
default asked_qs = []

default p_arg = ""
default d_arg = ""

# Witnesses — each team picks 1 of 3 from a shuffled witness pool. Stored as
# the witness dict (so AI prompt can pull name/occ/vibe/cred without re-lookup).
default witness_pool = []
default p_witness = None
default d_witness = None

# Live objections during closing arguments. Each team gets 1 token per round.
# `*_objections_log` records what was thrown against each team's argument so
# the judge prompt can mention sustained/overruled objections.
default p_obj_tokens = 1
default d_obj_tokens = 1
default p_arg_objections = []   # objections thrown AT the plaintiff's argument
default d_arg_objections = []   # objections thrown AT the defendant's argument

# Bench-conference once-per-round flag.
default bench_done_this_round = False

# History of completed rounds — used by the end-of-run highlights screen.
# Each entry: {round, winner, ruling_text, judge_name, p_ev, d_ev, p_witness,
# d_witness, p_jury, d_jury, settled}
default round_history = []

default settle_offer = ""     # "small" / "large" / ""
default settle_resp = ""      # "accept" / "reject" / ""
default settle_strengthened = False  # plaintiff answered prep Q correctly

default ruling_text = ""
default winner = ""            # "plaintiff" / "defendant" / ""
default appealed = False

# Appeals — set when an appeal is granted.
default cert_question = ""              # the certified question for review
default en_banc_judges = []              # the 3-judge panel (judge dicts)
default en_banc_results = []             # list of {"judge", "winner", "text"} after en banc

define WINS_TO_TAKE_RUN = 3
define MOTION_TIME_SECONDS = 45
define SETTLE_PRESTIGE_REWARD = 1   # ★ awarded to BOTH teams on settlement accept

init python:
    import random as _random
    import re as _re

    # Precompiled regexes for markdown_to_renpy. Bold MUST be matched before
    # italic so `**foo**` isn't mis-parsed as `*` + `*foo*` + `*`.
    _re_md = _re.compile(r"\*\*(.+?)\*\*", _re.DOTALL)
    _re_md_italic_star = _re.compile(r"\*([^\*\n]+?)\*")
    # Word-boundaried underscores so identifiers like snake_case don't italicize.
    _re_md_italic_under = _re.compile(r"\b_([^_\n]+?)_\b")

    # Court branding constants — referenced by both the prompt builder (so
    # the AI knows it's writing a District/Circuit opinion) and the modal
    # (header text). Keeping them centralized so a future tagline rebrand
    # is a single-line change.
    DISTRICT_NAME = "District of Northern Absurdia"
    CIRCUIT_NAME = "Twelfth Circuit"
    DISTRICT_COURT_HEADER = "United States District Court"
    DISTRICT_COURT_SUBHEADER = "DISTRICT OF NORTHERN ABSURDIA"
    CIRCUIT_COURT_HEADER = "United States Court of Appeals"
    CIRCUIT_COURT_SUBHEADER = "FOR THE TWELFTH CIRCUIT"

    def pick_judge_flavor(judge):
        """Random flavor from `flavors` list; falls back to legacy `flavor`."""
        if not judge:
            return ""
        flavors = judge.get("flavors")
        if flavors:
            return _random.choice(flavors)
        return judge.get("flavor", "")

    def _shuffled(seq):
        out = list(seq)
        _random.shuffle(out)
        return out

    def _pick(seq):
        if not seq:
            return None
        return _random.choice(seq)

    def start_round():
        store.case_card = _pick(CASES)
        store.judge = _pick(JUDGES)
        # Full juror pool so each side can pick 3. The selection screen removes
        # picked jurors from the pool as they're seated.
        store.jury_pool = _shuffled(JURORS)
        store.p_jury = []
        store.d_jury = []
        cards = _shuffled(MOTIONS)
        store.p_cards = cards[0:3]
        store.d_cards = cards[3:6]
        store.p_wild = None
        store.d_wild = None
        store.p_motion_strong = False
        store.d_motion_strong = False
        ev = _shuffled(EVIDENCE)
        store.p_ev_pool = ev[0:3]
        store.d_ev_pool = ev[3:6]
        store.p_ev = None
        store.d_ev = None
        store.p_ev_admissible = True
        store.d_ev_admissible = True
        store.trivia_q = random_question()
        store.trivia_bonus = ""
        # Reserve the trivia question so motions/discovery/settlement don't
        # pick it before the buzz-in phase.
        store.asked_qs = [store.trivia_q["q"]]
        store.witness_pool = _shuffled(WITNESSES)
        store.p_witness = None
        store.d_witness = None
        store.p_obj_tokens = 1
        store.d_obj_tokens = 1
        store.p_arg_objections = []
        store.d_arg_objections = []
        store.bench_done_this_round = False
        store.p_arg = ""
        store.d_arg = ""
        store.settle_offer = ""
        store.settle_resp = ""
        store.settle_strengthened = False
        store.ruling_text = ""
        store.winner = ""
        store.appealed = False
        store.cert_question = ""
        store.en_banc_judges = []
        store.en_banc_results = []

    def reset_game():
        store.scores = {"plaintiff": 0, "defendant": 0}
        store.prestige = {"plaintiff": 1, "defendant": 1}
        store.round_history = []

    def get_verdict_template(case):
        """Resolve a case to its closing-argument madlibs template.
        Lookup order: scenario → category → None (which falls back to free text)."""
        if not case:
            return None
        scenario = case.get("scenario")
        if scenario and scenario in VERDICT_TEMPLATES:
            return VERDICT_TEMPLATES[scenario]
        cat = case.get("cat", "")
        return VERDICT_TEMPLATES.get(cat)

    def assemble_verdict(template_intro, filled):
        """Substitute filled[i] for {i} markers; missing values render as ___."""
        out = template_intro
        for i in range(len(filled)):
            value = filled[i] if filled[i] else "___"
            out = out.replace("{" + str(i) + "}", value)
        return out

    def _escape_renpy_text(s):
        # Ren'Py's text engine treats { and [ as the start of tags / interpolation.
        # User-typed custom phrases must escape both. Empty / None passes through.
        if not s:
            return s
        return s.replace("{", "{{").replace("[", "[[")

    def markdown_to_renpy(s):
        """Convert AI-generated markdown into Ren'Py text tags.

        Sonnet emits **bold**, *italic*, and _italic_ in its rulings, plus the
        occasional bracketed stage direction like [pauses to dab eyes]. Ren'Py's
        text engine reads `[expr]` as Python interpolation, so unescaped
        brackets crash with SyntaxError. This helper:
          1. Escapes `[` → `[[` so brackets render as literal text.
          2. Translates `**X**` → `{b}X{/b}` for bold.
          3. Translates `*X*` and `_X_` → `{i}X{/i}` for italic.

        We intentionally do NOT escape `{` here — the Ren'Py tags we just
        emitted need real braces. The AI prompt is told to use markdown only;
        if it ever emits a literal `{`, it will collide with text tag syntax,
        but that's a rare edge case we accept.

        Order matters: bold must come before italic, otherwise `**foo**` would
        be mis-parsed as `*` `*foo*` `*`.
        """
        if not s:
            return s
        # 1. Escape opening brackets first so AI stage directions render literally.
        out = s.replace("[", "[[")
        # 2. Bold: **X** → {b}X{/b}. Non-greedy. \1 is the inner text.
        out = _re_md.sub(r"{b}\1{/b}", out) if _re_md else out
        # 3. Italic: *X* → {i}X{/i} (after bold so we don't eat **'s).
        out = _re_md_italic_star.sub(r"{i}\1{/i}", out) if _re_md_italic_star else out
        # 4. Italic underscore form: _X_ → {i}X{/i}. Word-boundaried so
        #    "snake_case" identifiers don't get italicized.
        out = _re_md_italic_under.sub(r"{i}\1{/i}", out) if _re_md_italic_under else out
        return out

    def render_preview(intro, filled, current):
        """Render the verdict-director template inline, current blank highlighted."""
        out = intro
        for i in range(len(filled)):
            marker = "{" + str(i) + "}"
            if filled[i]:
                rep = "{color=#D85A30}" + _escape_renpy_text(filled[i]) + "{/color}"
            elif i == current:
                rep = "{color=#D85A30}{u}______{/u}{/color}"
            else:
                rep = "______"
            out = out.replace(marker, rep)
        return out

    def submit_verdict(target_var, intro, filled):
        """Assemble the final closing argument and write it to store.<target_var>."""
        final = intro
        for i in range(len(filled)):
            final = final.replace("{" + str(i) + "}", filled[i] or "___")
        setattr(store, target_var, final)

    def append_round_history(settled=False):
        """Capture the just-finished round for the end-of-run highlights."""
        try:
            entry = {
                "round": len(store.round_history) + 1,
                "winner": store.winner,
                "ruling_text": store.ruling_text or "",
                "judge_name": (store.judge or {}).get("name", "?"),
                "case_title": (store.case_card or {}).get("title", "?"),
                "p_ev": (store.p_ev or {}).get("name", None),
                "d_ev": (store.d_ev or {}).get("name", None),
                "p_witness": (store.p_witness or {}).get("name", None),
                "d_witness": (store.d_witness or {}).get("name", None),
                "p_jury": [j["name"] for j in store.p_jury],
                "d_jury": [j["name"] for j in store.d_jury],
                "appealed": bool(store.appealed),
                "settled": bool(settled),
                "p_arg": store.p_arg or "",
                "d_arg": store.d_arg or "",
            }
            store.round_history = list(store.round_history) + [entry]
        except Exception as e:
            print("[Objection!] append_round_history failed: %r" % (e,))

    def highlight_payload():
        """Compute the 3 highlight cards shown at end of run."""
        history = store.round_history or []
        if not history:
            return None
        # MOST MEMORABLE RULING — longest ruling text (proxy for "ranty-est")
        best = max(history, key=lambda h: len(h.get("ruling_text", "")))
        # MOST RIDICULOUS EVIDENCE — random across all rounds, prefer non-None
        ev_pool = []
        for h in history:
            if h.get("p_ev"):
                ev_pool.append((h["round"], "Plaintiff", h["p_ev"]))
            if h.get("d_ev"):
                ev_pool.append((h["round"], "Defendant", h["d_ev"]))
        evidence_pick = _random.choice(ev_pool) if ev_pool else None
        # JURY MVP — winning team's juror with strongest tilt for that team
        winner_team = run_winner()
        mvp = None
        if winner_team:
            cand_lists = [h.get("p_jury" if winner_team == "plaintiff" else "d_jury", []) for h in history]
            seen = {}
            for names in cand_lists:
                for n in names:
                    seen[n] = seen.get(n, 0) + 1
            if seen:
                mvp_name = max(seen, key=seen.get)
                mvp = {"name": mvp_name, "rounds": seen[mvp_name]}
        return {
            "best_ruling": best,
            "evidence": evidence_pick,
            "mvp": mvp,
            "winner": winner_team,
        }

    def jury_bias_total():
        total = 0.0
        for j in store.p_jury + store.d_jury:
            total += float(j["bias"])
        return total

    def jury_description():
        parts = []
        for j in store.p_jury + store.d_jury:
            parts.append("%s (%s)" % (j["name"], j["occ"]))
        return ", ".join(parts) if parts else "no jury selected"

    def losing_team():
        if store.winner == "plaintiff":
            return "defendant"
        if store.winner == "defendant":
            return "plaintiff"
        return ""

    def can_appeal():
        losing = losing_team()
        if not losing:
            return False
        if store.appealed:
            return False
        return store.prestige.get(losing, 0) >= 1

    def spend_appeal():
        losing = losing_team()
        if store.prestige.get(losing, 0) < 1:
            return False
        store.prestige[losing] -= 1
        store.appealed = True
        return True

    def apply_verdict(text, w, is_appeal):
        store.ruling_text = text
        if w:
            if not is_appeal:
                store.scores[w] = store.scores.get(w, 0) + 1
            elif is_appeal and store.winner and w != store.winner:
                store.scores[store.winner] = max(0, store.scores.get(store.winner, 0) - 1)
                store.scores[w] = store.scores.get(w, 0) + 1
        store.winner = w or store.winner

    def en_banc_majority():
        """Return ('plaintiff'|'defendant', summary) from the 3-judge panel.
        Individual opinions are displayed by phases.rpy iterating over
        store.en_banc_results, so the summary here is just a one-liner.
        """
        if not store.en_banc_results:
            return ("defendant", "Panel could not reach a quorum.")
        votes = {"plaintiff": 0, "defendant": 0}
        for r in store.en_banc_results:
            w = r.get("winner") or "defendant"
            votes[w] = votes.get(w, 0) + 1
        winner = "plaintiff" if votes["plaintiff"] > votes["defendant"] else "defendant"
        loser_votes = votes["plaintiff"] + votes["defendant"] - votes[winner]
        summary = "The Circuit Court, sitting in panel, rules %d-%d: judgment for the %s." % (
            votes[winner], loser_votes, winner.upper(),
        )
        return (winner, summary)

    def _strip_verdict_tail(text):
        """Remove a trailing VERDICT: X WINS line from an opinion body.
        Used when reformatting concurring / dissenting opinions so the body
        ends with 'I concur.' / 'I respectfully dissent.' instead of the
        verdict tag that the API was instructed to emit for vote parsing.
        """
        if not text:
            return text
        cleaned = _re.sub(r"\s*VERDICT\s*:\s*[A-Z]+\s+WINS\.?\s*$", "", text,
                          flags=_re.IGNORECASE | _re.MULTILINE).rstrip()
        return cleaned

    def label_panel_opinions(majority_winner, trial_winner=None):
        """Two-step labeling pass for the en-banc panel results:

        STEP 1 — MAJORITY DISPOSITION.
        The lead/majority opinion's disposition is determined first, by
        comparing the majority winner against the trial-court winner:
          - majority winner == trial winner  →  'AFFIRMED'
          - majority winner != trial winner  →  'REVERSED'
        That single disposition is shown ONLY on the lead opinion's badge —
        it represents the court's overall judgment on the appeal.

        STEP 2 — CONCUR / DISSENT.
        The other two panel judges' labels are determined by whether their
        individual vote agrees with the majority's vote (i.e., do they
        agree with affirming/reversing as the majority did?):
          - panel judge vote == majority winner  →  'Concurring Opinion'
          - panel judge vote != majority winner  →  'Dissenting Opinion'
        The first panel judge whose vote matches the majority becomes the
        lead ('Opinion of the Court'); subsequent same-side judges concur.
        Concur/dissent opinions do NOT carry an AFFIRMED/REVERSED badge
        (the lead opinion has already established the court's disposition).

        Each opinion's body is rewritten so concur/dissent end on
        'I concur.' / 'I respectfully dissent.' instead of the
        VERDICT-X-WINS tag the AI was asked to emit for vote parsing.
        """
        if not store.en_banc_results:
            return
        majority_disposition = ""
        if trial_winner:
            majority_disposition = (
                "AFFIRMED" if majority_winner == trial_winner else "REVERSED"
            )

        lead_assigned = False
        results = list(store.en_banc_results)
        for r in results:
            judge_winner = r.get("winner") or "defendant"
            in_majority = (judge_winner == majority_winner)
            text = r.get("text") or ""

            if in_majority and not lead_assigned:
                r["opinion_label"] = "Opinion of the Court"
                r["disposition"] = majority_disposition
                # Lead opinion keeps body as-is — the AI wrote a complete
                # ruling and the badge will display the disposition.
                lead_assigned = True
            elif in_majority:
                r["opinion_label"] = "Concurring Opinion"
                r["disposition"] = ""
                r["text"] = _strip_verdict_tail(text) + "\n\n{i}I concur in the judgment.{/i}"
            else:
                r["opinion_label"] = "Dissenting Opinion"
                r["disposition"] = ""
                r["text"] = _strip_verdict_tail(text) + "\n\n{i}I respectfully dissent.{/i}"
        store.en_banc_results = results

    def run_is_over():
        return store.scores["plaintiff"] >= WINS_TO_TAKE_RUN or store.scores["defendant"] >= WINS_TO_TAKE_RUN

    def run_winner():
        if store.scores["plaintiff"] >= WINS_TO_TAKE_RUN:
            return "plaintiff"
        if store.scores["defendant"] >= WINS_TO_TAKE_RUN:
            return "defendant"
        return ""

    def settle_accept():
        store.settle_resp = "accept"
        store.scores["plaintiff"] += 1
        store.winner = "plaintiff"
        # Both sides bank ★ — defenders may need it for an appeal next round,
        # plaintiffs benefit from compounding influence on the judge.
        store.prestige["plaintiff"] += SETTLE_PRESTIGE_REWARD
        store.prestige["defendant"] += SETTLE_PRESTIGE_REWARD
        bump = " The strengthened legal posture forced their hand." if store.settle_strengthened else ""
        payout = "hefty sum" if store.settle_offer == "large" else "modest payout"
        store.ruling_text = (
            "SETTLEMENT REACHED. Defendant accepted plaintiff's %s offer.%s "
            "Plaintiff walks away with a %s and no formal verdict. "
            "Both teams bank %s from the resolved docket."
        ) % (store.settle_offer, bump, payout, STAR_ICON)

    def award_question_prestige(team, q, picked_option):
        """Used by trivia phase. Returns True if correct."""
        if team and picked_option == q["a"]:
            store.trivia_bonus = team
            store.prestige[team] = store.prestige.get(team, 0) + 1
            return True
        return False

    def is_correct(q, picked_option):
        return bool(q) and picked_option == q["a"]

    def remember_asked(q):
        if q is not None:
            store.asked_qs = list(store.asked_qs) + [q["q"]]

    def fresh_question():
        """Pick a question we haven't already asked this round."""
        return random_question(exclude=store.asked_qs)
