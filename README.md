# Objection!

Objection! is a courtroom party game for two teams made using Claude Code. Players argue made-up legal cases in front of a judge. An AI model (Claude) acts as the judge and writes the final ruling.

The game is built with [Ren'Py](https://www.renpy.org/), a free engine for visual novels. It runs on Windows, macOS, and Linux.

> **Note:** This project was "vibe coded". The author wrote most of the code by describing the wanted result to an AI coding assistant (Claude Code) and accepting the generated code, with limited line-by-line review. The code can contain errors and has not been fully tested or audited. Use it at your own risk.

## Contents

- [How the game works](#how-the-game-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configure the API key](#configure-the-api-key)
- [Start the game](#start-the-game)
- [Controls](#controls)
- [Game flow](#game-flow)
- [Project structure](#project-structure)
- [Change the game content](#change-the-game-content)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## How the game works

Two teams, the Plaintiff and the Defendant, play a series of rounds. Each round is a new case. The first team to win 3 rounds wins the run.

In each round, the teams:

1. Read a case.
2. Choose jurors.
3. Argue motions against a timer.
4. Examine evidence.
5. Answer a legal trivia question.
6. Write a closing argument.

The AI judge reads the arguments and the round details. The judge then writes a ruling in the style of a court opinion and names a winner.

No legal knowledge is necessary. The game is for entertainment. It does not give legal advice.

## Requirements

| Item | Requirement |
|------|-------------|
| Ren'Py SDK | Version 8.x (developed with 8.5) |
| Operating system | Windows, macOS, or Linux |
| Internet connection | Required for the judge's ruling |
| Anthropic API key | Required for the judge's ruling |
| Players | 2 teams, one shared computer |

The game uses the Anthropic API. API use is not free. Anthropic charges for each ruling. See the [Anthropic pricing page](https://www.anthropic.com/pricing) for current rates.

## Installation

1. Download and install the Ren'Py SDK from [renpy.org](https://www.renpy.org/latest.html).
2. Clone or download this repository.
3. Start the Ren'Py launcher.
4. Select **Preferences**, then set the **Projects Directory** to the folder that contains this project.
5. Select **Objection!** from the project list.

## Configure the API key

The game needs an Anthropic API key to request rulings.

1. Create a key in the [Anthropic Console](https://console.anthropic.com/).
2. Give the key to the game in one of these ways:
   - **Environment variable:** Set `ANTHROPIC_API_KEY` to your key before you start Ren'Py.
   - **Key file:** Create a file named `api_key.txt` in the `game/` folder. Put only the key in the file, on one line.
3. Restart the game.

The game reads the environment variable first. If the variable is not set, the game reads `game/api_key.txt`.

The file `api_key.txt` is listed in `.gitignore`, so Git does not track it. Do not remove it from `.gitignore`. Do not share the file.

If the key is missing or not valid, the game cannot create a ruling.

## Start the game

1. In the Ren'Py launcher, select **Objection!**.
2. Select **Launch Project**.
3. Select **Start** in the game's main menu.

## Controls

| Action | Input |
|--------|-------|
| Advance dialogue | Space or left mouse click |
| Plaintiff buzzes in (trivia) | **Q** |
| Defendant buzzes in (trivia) | **P** |

## Game flow

Each round has these phases, in this order:

| Phase | Description |
|-------|-------------|
| Case | The game shows the facts of the case. |
| Jury | Teams select jurors. |
| Motions | Teams argue motions. A timer limits the time (45 seconds). |
| Discovery | Teams examine pieces of evidence. |
| Trivia | Teams buzz in to answer a legal question. |
| Settlement | Each side can accept a settlement offer. |
| Arguments | Each team writes an argument. |
| Ruling | The AI judge writes a ruling and names the winner. |

If one side accepts a settlement, the game skips the arguments and ruling phases. It shows a pre-written ruling.

After a ruling, a team can appeal. An appeal asks the judge for a new ruling. The new ruling replaces the previous result.

## Project structure

```
objection-the-game/
├── game/
│   ├── script.rpy       Start label and round loop
│   ├── phases.rpy       One label for each game phase
│   ├── state.rpy        Scores, round state, and helper functions
│   ├── data.rpy         Cases, judges, motions, trivia, jurors, evidence
│   ├── screens.rpy      Menus, HUD, buzzer, and other screens
│   ├── claude_api.rpy   Connection to the Anthropic API
│   ├── api_key.txt      Your API key (you create this file; Git ignores it)
│   ├── options.rpy      Project settings
│   ├── gui.rpy          Interface style settings
│   ├── audio/           Sound effects and music
│   ├── fonts/           Typefaces
│   └── images/          Art for courtrooms, judges, jurors, and evidence
├── new-assets/          Source assets and question banks (working files)
├── LICENSE              MIT License (code)
└── LICENSE-CONTENT.txt  CC BY 4.0 (creative content)
```

## Change the game content

All static content is in `game/data.rpy`. The file holds lists of cases, judges, motions, trivia questions, jurors, and evidence.

To add a trivia question, add a new entry to the trivia list. Use the same fields as the existing entries.

The file `game/state.rpy` sets the number of wins needed (`WINS_TO_TAKE_RUN`) and the motion timer (`MOTION_TIME_SECONDS`).

After you change a file, restart the game in the Ren'Py launcher.

## Troubleshooting

| Symptom | Cause | Solution |
|---------|-------|----------|
| The judge returns no ruling | The API key is missing or not valid | Check `ANTHROPIC_API_KEY` or `game/api_key.txt`. |
| The log shows `CERTIFICATE_VERIFY_FAILED` | The game cannot find security certificates | Install the `certifi` package, or use a Ren'Py SDK that includes it. |
| The log shows a 404 error from the API | The model name is retired | Set `CLAUDE_MODEL` in `game/claude_api.rpy` to a current model. |
| The game stops with a script error | A script file has a syntax error | Read `errors.txt` or `traceback.txt` in the project folder. |

Diagnostic messages that start with `[Objection!]` are written to `log.txt`.

## License

This project uses two licenses:

- **Code** (`*.rpy` files and scripts): [MIT License](LICENSE).
- **Creative content** (case text, question banks, and artwork and sound effects created by the author): [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-CONTENT.txt).

The following items are not covered by these licenses and keep their original licenses:

- The Ren'Py engine.
- Third-party fonts in `game/fonts/` (`OldNewspaperTypes`, `WeThePeople`, and `laworder-dingbats`).
- Any other third-party asset.

Check the license of each third-party asset before you redistribute the game.
