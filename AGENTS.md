# SurveyPrime agent guide

## Purpose and status

Build a surveying application for **HP Prime**, using HP PPL. HP 50g User RPL programs
are a different platform. Prioritize lot closes, conversions, and angle addition/
subtraction before extending other surveying tools. All calculator interaction must
work with physical keys; the user's touchscreen cannot be used.

Repository: https://github.com/KRodenberg/SurveyPrime

SurveyPrime is a **development preview** with a native Apps-library package and
41 passing host regression tests. Its three support programs previously passed native
editor checks on the connected Prime, and their main menu launches. The new app's
installation and Apps-library launch still need device verification. Physical-key and
calculation acceptance is in progress. Never describe host interpretation or
successful transfer as proof that HP firmware executes the program.

## Required repository files

| Path | Role |
|---|---|
| `src/*.ppl` | Original PPL program modules |
| `tools/build.py` | Assemble support programs and the native app, icon and containers |
| `tools/ppl_runner.py` | Execute PPL for host regression checks |
| `tests/test_surveyprime.py` | Calculation, keypad, settings and container regressions |
| `.github/workflows/validate.yml` | Run the build and regression checks on GitHub |
| `.gitattributes`, `.gitignore` | Reproducible text files and a minimal tracked-file allowlist |
| `AGENTS.md` | Build, installation, usage, implementation and progress instructions |

Generated output, reference libraries, duplicate documentation, device diagnostics,
downloaded tools, calculator backups and credentials are excluded from Git. Preserve
local copies when cleaning the repository. The ignore rules allow only build and
validation files; update that allowlist deliberately when adding a required dependency.

## Build and host validation

Use Python 3.10 or later. The builder and tests need only the Python standard library.

```sh
python -m unittest discover -s tests -v
python tools/build.py
```

From a clean checkout the build creates twelve files in the ignored `Final Output/`:

- `Application/SurveyPrime.hpappdir/`: the native app folder containing
  `SurveyPrime.hpapp`, `SurveyPrime.hpappprgm`, `SurveyPrime.hpappnote` and `icon.png`.
  This is the entry selected in the calculator's **Apps** library.
- `Programs/SURVEYLIB.hpprgm`, `Programs/SURVEYTOOLS1.hpprgm`,
  `Programs/SURVEYPRIME.hpprgm`: required support programs, installed in that order.
- Matching support `.ppl` files and `SurveyPrime.app.ppl` in `Source/`.
- `SHA256.json`: hashes of the eleven generated app, program and source files.

The native container uses the Prime magic `7c618ab2`, a source-only Connectivity Kit
skeleton and UTF-16LE source. Its name comes from the filename. The generic skeleton
and Base App: None descriptor's MIT notice is preserved in `tools/build.py`; never
remove it. The app descriptor is rebuilt from clean defaults, with a generated
73 x 74 PNG survey icon and an empty note. Do not replace it with a calculator-saved
descriptor carrying another app's settings or last view.

The builder hoists persistent variables into the first program, exports namespaced
helpers, orders helpers before callers, and splits at function boundaries below
30,000 source characters per support program. It emits declarations before ordered local
initializations. Keep the dependency order, size budget and declaration handling
intact. Do not introduce cyclic function dependencies or rely on local reference
folders, downloaded tools or documentation to build.

`src/app.ppl` exports the native `START()` hook and calls the installed
`SURVEYPRIME()` menu. Keep the app entry small. The support modules avoid the native
compiler stalls seen with a single large program, and own the persistent `SC_` jobs.
Installing only the new app wrapper must not replace those existing jobs.

The host interpreter covers this project's PPL subset. It checks actual source, with
independent fixtures including the Quickclose curved-lot example, PROJ projection/
geodesic results, and simulated keypad workflows. It is not HP's compiler.

## Install on the calculator

1. Build and run the host tests using the commands above.
2. Open the [official HP Prime Connectivity Kit](https://updates.moravia-consulting.com/)
   and connect a powered-on HP Prime by USB. Exit any running menu using the physical
   Esc key before backup or transfer; On can interrupt if needed.
3. Back up the calculator before replacing any installed program. Exported `SC_` data
   and saved jobs must be preserved before program replacement or memory reset.
4. If the support programs are not installed or are being updated, in
   `Final Output/Programs/` open and send `SURVEYLIB.hpprgm`, then
   `SURVEYTOOLS1.hpprgm`, then `SURVEYPRIME.hpprgm`. Check each dependency before
   checking the next program.
   The names and order matter because later programs call earlier exported helpers.
   If using source, create each correctly named computer-side program and paste its
   matching `.ppl` file from `Final Output/Source/`. Do not paste the three files
   into one large program.
5. For an on-device check, press **Shift + 1**, highlight the required program with
   arrows, press **Enter** to open its editor, then **Esc** to save/check. Fix any
   reported error before proceeding. The catalog moves recently opened programs to
   the top, so verify the highlighted name rather than counting from a stale order.
6. Import the complete `Final Output/Application/SurveyPrime.hpappdir` folder into
   the Kit and send it to the calculator's Applications. Keep its four files together.
7. On the calculator press **Apps**, highlight **SurveyPrime** with the arrow keys,
   then press **Enter** to start. Its native `START()` hook opens the surveying menu.
   Use Esc to leave the menu before switching apps. No touchscreen input or typed
   program name is required for normal use.
8. In SurveyPrime press **9**, then **2**, to run the self-test. Alternatively enter
   **`SURVEYTEST()`** from Home. Expect **16 / 16 passed**.

For diagnostics the support entry `SURVEYPRIME()` can still run from Home. The Home
title shows the active app's name; that title alone does not mean its menu is running.
The earlier standalone diagnostic `SPTEST()` may still exist on the original device;
the surveying app uses `SURVEYTEST()` so their names do not conflict.

After a native syntax check, verify every menu and numeric form using only physical
keys. Enter, edit, save and reopen a lot; exit/restart to check persistence. Check
closure, curved area and Bowditch results, plus restoration of Home settings. Record
the actual device/firmware and observed results here when these checks are completed.

## Keypad use and conventions

- Main menu: **1** Lot closes, **2** Conversions, **3** Angles, **4** COGO,
  **5** Utilities, **6** Levelling, **7** Angle traverse, **8** Geodesy/road,
  **9** Help/self-test.
- Digits select numbered items. Up/Down move the selection or page through reports.
  Enter confirms; Esc cancels the current input or returns one menu.
- Numeric input accepts digits, decimal point, sign, Backspace and EEX. Typing a
  digit replaces the initial value; Enter alone keeps it.
- DMS input is **DD.MMSS**: `123.3045` means 123 degrees, 30 minutes, 45 seconds.
  Minutes/seconds must be below 60; a minus sign applies to the whole angle.
- Azimuths run clockwise from North. Survey distances and coordinates are metres;
  the conversion menu explicitly selects other units. International and US survey
  feet are separate definitions.
- Coordinates are Easting, Northing, height. Positive offset is to the right looking
  along the reference direction. Geodetic forms use decimal degrees and ellipsoidal heights.
- Curved lot legs use chord distance and a signed minor/semicircle segment area.
  Open-lot area includes a straight closing chord. Boundaries must be simple.

## Implementation map

| Module | Responsibilities |
|---|---|
| `app.ppl` | Native Apps-library `START()` hook that launches the surveying menu |
| `core.ppl` | DMS, bearings, closure/area, Bowditch, missing elements, unit factors |
| `keypad.ppl` | GETKEY interaction, menus, numeric forms, reports, formatting |
| `priority_ui.ppl` | Lot workflows/jobs/exchange, conversions and angle arithmetic |
| `missing_ui.ppl` | Missing closing-leg workflows and alternate solutions |
| `geometry.ppl` | COGO, resection, clipping, levels, road geometry and face reduction |
| `geodesy.ppl` | Explicit TM/UTM, ECEF, Helmert and Vincenty calculations |
| `geodesy_ui.ppl` | Geodesy menus and persistent geodetic point-job workflows |
| `extended_ui.ppl` | COGO, point jobs, utilities, levels, angle traverse and road menus |
| `selftest.ppl` | Exported `SURVEYTEST()` with 16 priority checks |
| `main.ppl` | Exported `SURVEYPRIME()`, top-level navigation and settings cleanup |

Use namespaced `SC_` variables for persistent jobs and working data. Keep observations
separate from adjusted results; ask before replacing saved data. Do not use the user's
general-purpose matrices or lists as scratch storage.

Main execution uses degree mode (`HAngle:=1`) with `AAngle:=0` so the active app
inherits Home's setting. Home modes are 0 radians, 1 degrees and 2 gradians; app
modes are 0 inherit, 1 radians, 2 degrees and 3 gradians. Restore both Home and app
angle/number settings on normal exit or a caught error. A hard On interruption can
bypass cleanup. Keep
pure calculations separate from input and display routines. Use GETKEY for interaction;
do not add touch APIs, touch buttons, MOUSE, or touch-dependent input dialogs.

## Progress and remaining work

- [x] Priority lot-close, conversion and angle workflows implemented before extensions.
- [x] Additional COGO, levelling, traverse, utility, geodesy and road modules implemented.
- [x] 41 host tests passing; calculation self-test has 16 priority cases.
- [x] Native app folder, clean descriptor, START hook and generated survey icon.
- [x] Real native container packaging, independent container reading and USB source round-trips.
- [x] Minimal build/validation repository; generated output and local materials ignored.
- [x] Native editor/compiler acceptance of all three generated programs.
- [x] Main menu launched on the physical calculator.
- [ ] New app installed and launched from the physical Apps library.
- [ ] Successful on-calculator self-test.
- [ ] Native keypad, graphics, persistence and Home-setting acceptance checks.
- [ ] Regional GDF import/catalogs and generalized nonconvex/curved fixed-area cuts.

On 2026-11-10 the user reported a native "Syntax error". Fixes include smaller
`LOCAL` groups, explicit ordered initialization, distinct parameter names (including
replacing `e`), degree mode with the app override cleared, and a correctly terminated
USB source payload. The original package wrapper was also replaced with the actual
native container format. A monolithic program and a 60,000-character menu program
stalled the native editor/compiler. The three programs below 30,000 characters each
passed native checks. Helpers are ordered before callers without forward prototypes.

Native diagnostics used the USB-connected Prime (product ID `2441`, reported version
`V2.060.650`), without changing firmware. Backups and diagnostic programs remain local
and ignored. USB screenshots and keypad events support diagnosis despite the broken
touchscreen. Host interpretation and a linter remain supplementary checks.
USB key arrays can navigate native catalogs but dropped letters during Alpha entry;
use individually paced keys for names. USB-injected keys did not move the running
GETKEY menu. A physical-key test has been requested; do not claim it passed until
its result is observed.

The Apps-library conversion adds a small native app while retaining the already
compiled support programs. The launcher, package structure, PNG dimensions/checksums
and settings restoration have host coverage. Installation is awaiting an idle
calculator: a full backup timed out while the existing GETKEY menu was running, and
physical Esc/On followed by Home has been requested. Do not replace an app or saved
jobs without first obtaining the calculator backup.

Current fixed-area cutting is limited to convex straight lots. Resection and alignment
inversion are numerical solvers. Projection is limited to latitude -80..84 degrees and
within 3.5 degrees of its central meridian; convergence/arc-to-chord are approximate.
Do not claim full Quickclose parity or a uniform accuracy guarantee from the host fixtures.

## Rules for future changes

- Update this guide when build requirements, calculator use, progress or known issues change.
- Run the host tests and builder after relevant source changes; native changes need native checks.
- Keep generated outputs out of commits. Keep the repository limited to necessary build/
  validation files and this guide; retain private/local data outside tracked paths.
- Preserve existing calculator programs and back up data before transfers or replacement.
- Review both valid geometric solutions where applicable; validate units and input ranges.
- Use a pi constant independently of angle mode; `ACOS(-1)` returns 180 in degree mode.
- Declare at most eight variables per `LOCAL` statement; split larger groups while
  preserving initialization order. Keep native angle enums in host tests accurate.
- Avoid built-in symbol names for parameters and loop indices; current code uses
  `ee`, `ii`, `idx` and `obs`. Use `SC_ITEM` for portable multi-level list access.
- Rebuild the native app folder and manifest after launcher or icon changes; check
  the app from the Apps library, not only the diagnostic program entry in Home.

## References

- [HP Prime User Guide](https://hpcalcs.com/downloads/HP-Prime_user_guide_EN.pdf): PPL,
  exported variables, GETKEY, graphics, IFERR and Home settings.
- [HP Prime Quick Start Guide](https://h10032.www1.hp.com/ctg/Manual/c05333004.pdf):
  running programs from Home.
- [Snyder, USGS Paper 1395](https://pubs.usgs.gov/pp/1395/report.pdf): TM series.
- [PROJ](https://proj.org/en/stable/): independent projection/geodesic fixture reference.

The supplied Quickclose manuals provided functional requirements. The implementation
is original source; proprietary reference libraries are local materials, not build inputs.
