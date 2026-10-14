# Claude API wrapper. Each request runs on its own background thread so
# Ren'Py's main loop keeps drawing during the verdict wait. Three flavors:
#   - request_ruling_async       (single ruling for the trial judge)
#   - request_cert_question_async (drafts the certified question for appeal)
#   - request_en_banc_async       (parallel panel of 3 judges for appeal)

init python:
    import json
    import os
    import ssl
    import threading
    import random as _api_random
    try:
        import urllib.request as _urlreq
        import urllib.error as _urlerr
    except ImportError:
        import urllib2 as _urlreq
        _urlerr = _urlreq

    def _make_ssl_context():
        """Build an SSL context that can verify api.anthropic.com.

        Ren'Py's bundled Python doesn't include `Install Certificates.command`
        nor a wired-up CA bundle, so the default urllib context fails with
        CERTIFICATE_VERIFY_FAILED. Try, in order:
          1. certifi (if bundled or installable)
          2. macOS system bundle at /etc/ssl/cert.pem
          3. Linux system bundle at /etc/ssl/certs/ca-certificates.crt
          4. ssl.create_default_context() with whatever the OS exposes
          5. Unverified — last-resort, with a loud console warning. This is
             a single-user game calling a fixed Anthropic endpoint, so the
             security exposure is minimal, but we still want it visible.
        """
        # 1. certifi
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
            print("[Objection!] SSL context: certifi (%s)" % certifi.where())
            return ctx
        except Exception:
            pass
        # 2-3. system bundles
        for path in ("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt"):
            try:
                if os.path.exists(path):
                    ctx = ssl.create_default_context(cafile=path)
                    print("[Objection!] SSL context: system bundle (%s)" % path)
                    return ctx
            except Exception:
                pass
        # 4. OS default (may be empty on Ren'Py-bundled Python)
        try:
            ctx = ssl.create_default_context()
            if ctx.get_ca_certs():
                print("[Objection!] SSL context: OS default (loaded %d certs)" % len(ctx.get_ca_certs()))
                return ctx
        except Exception:
            pass
        # 5. Unverified fallback.
        print("[Objection!] WARNING: SSL verification disabled — no CA bundle "
              "could be located. The Claude API will still work but the "
              "connection is not authenticated. Install certifi to fix.")
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    _SSL_CTX = _make_ssl_context()

    # ----- API KEY ---------------------------------------------------------
    # The key is NOT stored in source. It is read from, in order:
    #   1. The ANTHROPIC_API_KEY environment variable.
    #   2. A plain-text file named api_key.txt in the game folder
    #      (git-ignored; one line containing only the key).
    def _load_api_key():
        key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if key:
            return key
        try:
            path = os.path.join(renpy.config.gamedir, "api_key.txt")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read().strip()
        except Exception as e:
            print("[Objection!] Could not read api_key.txt: %r" % (e,))
        print("[Objection!] WARNING: no API key found. Set ANTHROPIC_API_KEY "
              "or create game/api_key.txt.")
        return ""

    CLAUDE_API_KEY = _load_api_key()
    # -----------------------------------------------------------------------

    CLAUDE_URL = "https://api.anthropic.com/v1/messages"
    # Opus 4.7 with adaptive thinking and high effort — markedly higher-
    # quality opinions (richer doctrinal reasoning, better in-character
    # voice, more lawyerly sentence structure) at the cost of latency.
    #
    # Note: Opus 4.7 does NOT accept `thinking.type=enabled` + a fixed
    # budget like older models. It requires `thinking.type=adaptive` and
    # `output_config.effort` ("low" / "medium" / "high"). Using the wrong
    # shape returns 400 invalid_request_error.
    #
    # If you want to fall back to faster cheaper rulings, swap to
    # "claude-sonnet-4-6" and drop both `thinking` and `output_config`
    # from the request body in _post_claude.
    CLAUDE_MODEL = "claude-opus-4-7"
    CLAUDE_API_VERSION = "2023-06-01"
    CLAUDE_MAX_TOKENS = 4000
    CLAUDE_OUTPUT_EFFORT = "high"
    # Opus + adaptive-high can run 30-90s depending on prompt complexity.
    # The polling loop checks every 250ms so the game stays responsive.
    CLAUDE_TIMEOUT_SECONDS = 180

    # Something in the user's paste pipeline keeps replacing ASCII letters
    # with visually-identical Cyrillic glyphs (and sometimes the registered
    # trademark sign). HTTP headers are ASCII-only, so the Anthropic call
    # blows up with UnicodeEncodeError before it ever leaves the machine.
    # We auto-correct the unambiguous Cyrillic→Latin substitutions here so
    # a re-paste isn't required every time the key gets re-corrupted.
    _CYRILLIC_TO_LATIN = {
        u'А': 'A', u'В': 'B', u'Е': 'E', u'К': 'K',
        u'М': 'M', u'Н': 'H', u'О': 'O', u'Р': 'P',
        u'С': 'C', u'Т': 'T', u'Х': 'X',
        u'а': 'a', u'в': 'b', u'е': 'e', u'к': 'k',
        u'о': 'o', u'р': 'p', u'с': 'c', u'у': 'y',
        u'х': 'x',
    }

    def _sanitize_key(key):
        return ''.join(_CYRILLIC_TO_LATIN.get(c, c) for c in key)

    CLAUDE_API_KEY = _sanitize_key(CLAUDE_API_KEY)
    if any(ord(c) >= 128 for c in CLAUDE_API_KEY):
        # Still non-ASCII after sanitization (e.g. ® or other look-alikes
        # that aren't unambiguous). API call will fail; flag it so we know
        # to inspect rather than chasing ghosts.
        print("[Objection!] WARNING: CLAUDE_API_KEY still contains non-ASCII characters after sanitization. The API call will fail until the key is re-typed cleanly.")

    # ---- Result buckets ---------------------------------------------------
    _claude_result = {"text": None, "winner": None, "is_appeal": False, "done": False}
    _cert_q = {"text": None, "done": False}
    _en_banc = {"slots": [], "done_flags": [], "lock": threading.Lock()}

    FALLBACK_RULING = (
        "RULING: The court has experienced a catastrophic technical failure. "
        "VERDICT: DEFENDANT WINS by default due to plaintiff's inability to locate a working server."
    )
    FALLBACK_CERT_QUESTION = (
        "Whether the doctrine of res ipsa loquitur applies when the instrumentality "
        "in question is metaphorical, allegorical, or merely vibes-based."
    )

    def _parse_winner(text):
        if not text:
            return ""
        if "VERDICT: PLAINTIFF WINS" in text:
            return "plaintiff"
        if "VERDICT: DEFENDANT WINS" in text:
            return "defendant"
        return ""

    def _extract_text(parsed):
        # Pure duck typing — NO isinstance checks. Ren'Py's init-python scope
        # shadows the builtin `dict` with its RevertableDict class, so
        # `isinstance(parsed, dict)` returns False even when parsed *is* a
        # plain dict (json.loads returns builtins.dict, isinstance compares
        # to RevertableDict). This was the source of the 0-char ruling bug.
        try:
            for block in parsed["content"]:
                if block["type"] == "text":
                    return block["text"] or ""
        except (KeyError, TypeError, AttributeError) as e:
            print("[Objection!] _extract_text: access error %r" % (e,))
        except Exception as e:
            print("[Objection!] _extract_text: unexpected %r" % (e,))
        return ""

    def _post_claude(prompt, max_tokens=None):
        """Send a single prompt to Claude and return the extracted text. Raises on failure."""
        print("[Objection!] _post_claude: model=%s, prompt=%d chars, key_prefix=%s..." % (
            CLAUDE_MODEL, len(prompt), CLAUDE_API_KEY[:15],
        ))
        # Adaptive thinking + high effort gives Opus room to reason about
        # doctrine, juror personalities, and tone before drafting. The
        # response may include `thinking` content blocks before the final
        # `text` block; _extract_text filters by type=="text" so the
        # thinking content is silently dropped.
        request_body = {
            "model": CLAUDE_MODEL,
            "max_tokens": max_tokens or CLAUDE_MAX_TOKENS,
            "messages": [{"role": "user", "content": prompt}],
            "thinking": {"type": "adaptive"},
            "output_config": {"effort": CLAUDE_OUTPUT_EFFORT},
        }
        body = json.dumps(request_body).encode("utf-8")
        req = _urlreq.Request(CLAUDE_URL, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("x-api-key", CLAUDE_API_KEY)
        req.add_header("anthropic-version", CLAUDE_API_VERSION)
        try:
            resp = _urlreq.urlopen(req, timeout=CLAUDE_TIMEOUT_SECONDS, context=_SSL_CTX)
            raw = resp.read().decode("utf-8")
            parsed = json.loads(raw)
            # Belt-and-suspenders: try _extract_text first, then a direct
            # inline scan as fallback in case the helper somehow fails.
            text = _extract_text(parsed) or ""
            if not text:
                print("[Objection!] _post_claude returned 0 chars. Raw response (first 1500 chars):")
                print(raw[:1500])
                print("[Objection!] Parsed content blocks: %r" % (parsed.get("content"),))
                print("[Objection!] Stop reason: %r" % parsed.get("stop_reason"))
            else:
                # Render markdown to Ren'Py text tags AND escape any [...]
                # stage directions so the text engine never tries to
                # interpolate them as Python expressions. See
                # markdown_to_renpy in state.rpy. This is the single point
                # where AI-generated text becomes safe to pass to any Ren'Py
                # `text` displayable downstream.
                text = markdown_to_renpy(text)
                print("[Objection!] _post_claude OK: %d chars returned (markdown-rendered)" % len(text))
            return text
        except _urlerr.HTTPError as e:
            try:
                err_body = e.read().decode("utf-8", errors="replace")
            except Exception:
                err_body = "(unreadable)"
            print("[Objection!] _post_claude HTTPError %s: %s" % (e.code, err_body[:500]))
            raise
        except Exception as e:
            print("[Objection!] _post_claude %s: %r" % (type(e).__name__, e))
            raise

    # ---- Trial-judge ruling -----------------------------------------------

    def _build_ruling_prompt(is_appeal, judge_override=None, override_intro=None):
        judge = judge_override or store.judge
        c = store.case_card
        bias = "%.2f" % jury_bias_total()
        desc = jury_description()
        bonus_line = (
            ("The %s team won the trivia bonus." % store.trivia_bonus)
            if store.trivia_bonus else "No trivia bonus awarded."
        )
        settle_line = "No settlement was offered."
        if store.settle_resp == "reject":
            settle_line = "Plaintiff offered a %s settlement; defendant rejected it." % store.settle_offer
            if store.settle_strengthened:
                settle_line += " Plaintiff backed the offer with credible legal authority."
        appeal_note = ""
        trial_court_note = ""
        if is_appeal:
            trial_winner = (store.winner or "").upper() or "UNKNOWN"
            trial_court_note = (
                "\n\nTRIAL COURT BELOW ruled: %s. You are sitting as a Circuit Judge "
                "on the United States Court of Appeals for the %s, reviewing this judgment "
                "de novo. State whether you AFFIRM or REVERSE the trial court."
            ) % (trial_winner + " WINS" if trial_winner != "UNKNOWN" else "no party prevailed",
                 CIRCUIT_NAME)

        if store.p_ev_admissible and store.p_ev:
            p_ev_str = "%s (%s)" % (store.p_ev["name"], store.p_ev["flavor"])
        elif store.p_ev:
            p_ev_str = "EXCLUDED — %s was not admitted by the court" % store.p_ev["name"]
        else:
            p_ev_str = "none submitted"

        if store.d_ev_admissible and store.d_ev:
            d_ev_str = "%s (%s)" % (store.d_ev["name"], store.d_ev["flavor"])
        elif store.d_ev:
            d_ev_str = "EXCLUDED — %s was not admitted by the court" % store.d_ev["name"]
        else:
            d_ev_str = "none submitted"

        def _witness_line(w):
            if not w:
                return "no witness called"
            tilt = w.get("cred", 0.0)
            tilt_word = (
                "highly credible" if tilt >= 0.2 else
                "credible" if tilt >= 0.05 else
                "neutral" if -0.05 < tilt < 0.05 else
                "questionable" if tilt > -0.2 else
                "openly hostile/unreliable"
            )
            return "%s, %s — %s [%s, cred=%+.2f]" % (
                w["name"], w["occ"], w["vibe"], tilt_word, tilt,
            )

        p_witness_line = _witness_line(store.p_witness)
        d_witness_line = _witness_line(store.d_witness)

        def _arg_with_objections(arg, objections):
            base = arg if arg else "(no argument submitted)"
            if objections:
                base += " [OBJECTIONS LODGED AGAINST THIS ARGUMENT: %s — judge should consider whether to sustain or overrule]" % ", ".join(objections)
            return base

        p_arg_line = _arg_with_objections(store.p_arg, store.p_arg_objections)
        d_arg_line = _arg_with_objections(store.d_arg, store.d_arg_objections)

        p_motion_qual = "credible legal grounding" if store.p_motion_strong else "weakly supported"
        d_motion_qual = "credible legal grounding" if store.d_motion_strong else "weakly supported"

        def _format_ranked_motions(cards, wild, qual):
            # cards is in priority order (#1 = strongest); wild (if set) is
            # one of the cards and should be flagged as a high-impact filing
            # the judge should weigh seriously.
            parts = []
            for i, c in enumerate(cards):
                tag = " [WILD CARD — heightened scrutiny]" if (wild and c == wild) else ""
                parts.append("(#%d) %s%s" % (i + 1, c, tag))
            return "; ".join(parts) + (" — %s" % qual)

        p_cards_str = _format_ranked_motions(store.p_cards, store.p_wild, p_motion_qual)
        d_cards_str = _format_ranked_motions(store.d_cards, store.d_wild, d_motion_qual)

        # Pick a fresh flavor from this judge's flavor list each call so the
        # AI doesn't reuse the same tic across rounds.
        chosen_flavor = pick_judge_flavor(judge)

        if is_appeal:
            court_label = "United States Court of Appeals for the %s" % CIRCUIT_NAME
            seat_label = "Circuit Judge"
        else:
            court_label = "%s, %s" % (DISTRICT_COURT_HEADER, DISTRICT_NAME)
            seat_label = "District Judge"

        intro = override_intro or (
            "You are %s, sitting as a %s of the %s. "
            "You are known for your %s temperament; this round you %s. "
            "Write in character: dry, witty, with the absurdist streak of a "
            "judge who has seen too much."
        ) % (judge["name"], seat_label, court_label, judge["trait"], chosen_flavor)

        return (
            "%s\n\n"
            "==== CASE FILE ====\n"
            "Caption: %s v. The Defendant — \"%s\"\n"
            "Facts: %s\n\n"
            "==== TRIAL RECORD ====\n"
            "Jury (composite bias %s, positive favors plaintiff): %s\n\n"
            "Plaintiff's motion cards (ranked by counsel, #1 = strongest):\n  %s\n"
            "Defendant's motion cards (ranked by counsel, #1 = strongest):\n  %s\n\n"
            "Plaintiff's witness: %s\n"
            "Defendant's witness: %s\n\n"
            "Plaintiff's evidence: %s\n"
            "Defendant's evidence: %s\n\n"
            "Plaintiff's closing argument: \"%s\"\n"
            "Defendant's closing argument: \"%s\"\n\n"
            "Other context: %s %s%s%s\n\n"
            "==== INSTRUCTIONS ====\n"
            "Write a federal-court-style opinion of 4-7 sentences (or up to ~250 words). "
            "Format it like a real published opinion, but with your personal stylistic "
            "flair. Your opinion MUST:\n"
            " (1) Open with a brief framing of the dispute (one sentence is fine).\n"
            " (2) Address at least two of the following: a ranked motion, a witness's "
            "credibility, an evidentiary ruling, an objection, a juror by name, the "
            "settlement posture.\n"
            " (3) State your reasoning in character — channel your temperament. "
            "Use **bold** for the key holding and *italic* for emphasis on dramatic "
            "phrases. (Markdown formatting renders properly in our text engine.)\n"
            " (4) End with a memorable, in-character one-liner.\n"
            " (5) On its OWN final line, output exactly: VERDICT: [PLAINTIFF/DEFENDANT] WINS\n"
            "\n"
            "Do NOT use square brackets [ ] for stage directions — write any aside as a "
            "regular sentence. Do NOT include a 'RULING:' prefix; jump straight into the opinion."
        ) % (
            intro,
            "The Plaintiff", c["title"], c["desc"],
            bias, desc,
            p_cards_str, d_cards_str,
            p_witness_line, d_witness_line,
            p_ev_str, d_ev_str,
            p_arg_line, d_arg_line,
            bonus_line, settle_line, trial_court_note, appeal_note,
        )

    def _claude_worker(is_appeal):
        # Two layers of try/except: inner protects the API call; outer guards
        # everything else (prompt build, dict access). The `finally` is the
        # absolute floor — done MUST become True or the polling screen hangs.
        text = FALLBACK_RULING
        w = "defendant"
        try:
            try:
                prompt = _build_ruling_prompt(is_appeal)
                parsed_text = _post_claude(prompt)
                if parsed_text:
                    text = parsed_text
                    w = _parse_winner(text) or "defendant"
            except Exception as e:
                print("[Objection!] ruling API call failed: %r" % (e,))
        except Exception as e:
            print("[Objection!] ruling worker outer error: %r" % (e,))
        finally:
            try:
                _claude_result["text"] = text
                _claude_result["winner"] = w
                _claude_result["is_appeal"] = is_appeal
            except Exception:
                pass
            _claude_result["done"] = True

    def request_ruling_async(is_appeal):
        _claude_result["text"] = None
        _claude_result["winner"] = None
        _claude_result["is_appeal"] = is_appeal
        _claude_result["done"] = False
        t = threading.Thread(target=_claude_worker, args=(is_appeal,))
        t.daemon = True
        t.start()

    def claude_result_ready():
        return _claude_result["done"]

    def consume_claude_result():
        return (
            _claude_result["text"] or FALLBACK_RULING,
            _claude_result["winner"] or "defendant",
            _claude_result["is_appeal"],
        )

    # ---- Certified question (appeal step 1) ------------------------------

    def _build_cert_question_prompt():
        c = store.case_card
        return (
            "You are the Reporter of Decisions for an appellate court. The trial court "
            "below ruled on the following case:\n\n"
            "CASE: \"%s\" — %s\n\n"
            "Original verdict: %s won.\n\n"
            "Draft ONE certified question for en banc review. The question should "
            "(a) sound like a real legal issue framed for appellate review (e.g., "
            "\"Whether the trial court erred in...\"), (b) be specifically grounded "
            "in the absurd facts of THIS case, and (c) be a single sentence under 280 "
            "characters. Output ONLY the question text, nothing else."
        ) % (c["title"], c["desc"], (store.winner or "no one").capitalize())

    def _cert_q_worker():
        text = FALLBACK_CERT_QUESTION
        try:
            try:
                prompt = _build_cert_question_prompt()
                parsed_text = _post_claude(prompt, max_tokens=300)
                if parsed_text:
                    text = parsed_text.strip().strip('"').strip()
            except Exception as e:
                print("[Objection!] cert-question API call failed: %r" % (e,))
        except Exception as e:
            print("[Objection!] cert-question outer error: %r" % (e,))
        finally:
            try:
                _cert_q["text"] = text
            except Exception:
                pass
            _cert_q["done"] = True

    def request_cert_question_async():
        _cert_q["text"] = None
        _cert_q["done"] = False
        t = threading.Thread(target=_cert_q_worker)
        t.daemon = True
        t.start()

    def cert_question_ready():
        return _cert_q["done"]

    def consume_cert_question():
        return _cert_q["text"] or FALLBACK_CERT_QUESTION

    # ---- En banc panel (appeal step 2) -----------------------------------

    def pick_en_banc_panel():
        """Three random judges, excluding the trial judge."""
        trial_id = store.judge["id"] if store.judge else None
        pool = [j for j in JUDGES if j["id"] != trial_id]
        _api_random.shuffle(pool)
        return pool[:3]

    def _en_banc_worker(slot_idx, panel_judge, cert_question):
        text = FALLBACK_RULING
        w = "defendant"
        try:
            try:
                chosen_flavor = pick_judge_flavor(panel_judge)
                intro = (
                    "You are %s, a Circuit Judge sitting by designation on a 3-judge "
                    "panel of the United States Court of Appeals for the %s. "
                    "You are known for your %s temperament; this round you %s. "
                    "Write your opinion as a polished federal appellate opinion — "
                    "with measured doctrinal reasoning, but in character."
                ) % (
                    panel_judge["name"], CIRCUIT_NAME,
                    panel_judge["trait"], chosen_flavor,
                )
                base = _build_ruling_prompt(True, judge_override=panel_judge, override_intro=intro)
                prompt = base + (
                    "\n\n==== CERTIFIED QUESTION ====\n"
                    "The trial court certified the following question for review:\n"
                    "  \"%s\"\n\n"
                    "Address the certified question directly. Begin your opinion with a "
                    "single short header line indicating your disposition: write either "
                    "\"AFFIRMED.\" if you agree with the trial court's verdict, or "
                    "\"REVERSED.\" if you disagree. Then write the opinion body. "
                    "End with the VERDICT: [PLAINTIFF/DEFENDANT] WINS line as instructed."
                ) % cert_question
                parsed_text = _post_claude(prompt)
                if parsed_text:
                    text = parsed_text
                    w = _parse_winner(text) or "defendant"
            except Exception as e:
                print("[Objection!] en-banc API call failed: %r" % (e,))
        except Exception as e:
            print("[Objection!] en-banc outer error: %r" % (e,))
        finally:
            try:
                with _en_banc["lock"]:
                    _en_banc["slots"][slot_idx] = {
                        "judge": panel_judge,
                        "winner": w,
                        "text": text,
                    }
                    _en_banc["done_flags"][slot_idx] = True
            except Exception:
                try:
                    _en_banc["done_flags"][slot_idx] = True
                except Exception:
                    pass

    def request_en_banc_async(panel_judges, cert_question):
        n = len(panel_judges)
        _en_banc["slots"] = [None] * n
        _en_banc["done_flags"] = [False] * n
        for i, pj in enumerate(panel_judges):
            t = threading.Thread(target=_en_banc_worker, args=(i, pj, cert_question))
            t.daemon = True
            t.start()

    def en_banc_ready():
        return all(_en_banc["done_flags"]) if _en_banc["done_flags"] else False

    def consume_en_banc_results():
        return list(_en_banc["slots"])
