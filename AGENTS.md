# SurveyPrime agent guide

## Purpose and status

Build a surveying calculator for **HP Prime**, using HP PPL. HP 50g User RPL programs
are a different platform. Prioritize lot closes, conversions, and angle addition/
subtraction before extending other surveying tools. All calculator interaction must
work with physical keys; the user's touchscreen cannot be used.

Repository: https://github.com/KRodenberg/SurveyPrime

The program is a **development preview**. There are 34 passing host regression tests.
An earlier USB transfer and source round-trip succeeded, but native compilation and
execution have not been verified. Never describe host interpretation or successful
transfer as proof that HP firmware compiles or executes the program.

## Required repository files

| Path | Role |
|---|---|
| `src/*.ppl` | Original PPL program modules |
| `tools/build.py` | Assemble source and generate the native program container |
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

From a clean checkout the build creates these files in the ignored `Final Output/`:

- `SURVEYPRIME.hpprgm`: named UTF-16LE program container for the Connectivity Kit.
- `SURVEYPRIME.ppl`: assembled, readable source for inspection or the Prime editor.
- `SHA256.json`: hashes of those two generated files.

The builder verifies that decoding the container reproduces its name and source.
It hoists exported variables before functions and generates forward declarations for
private helper functions. Keep the module order and declaration handling intact when
editing the builder. Do not require local reference folders or documentation to build.

The host interpreter covers this project's PPL subset. It checks actual source, with
independent fixtures including the Quickclose curved-lot example, PROJ projection/
geodesic results, and simulated keypad workflows. It is not HP's compiler.

## Install on the calculator

1. Build and run the host tests using the commands above.
2. Open the [official HP Prime Connectivity Kit](https://updates.moravia-consulting.com/)
   on the computer and connect a powered-on HP Prime by USB.
3. Back up the calculator before replacing an installed program. Exported `SC_` data
   and saved jobs must be preserved before program replacement or memory reset.
4. Open `Final Output/SURVEYPRIME.hpprgm` in the Kit's program editor and run its
   syntax check. Fix any native syntax errors before accepting the build.
5. Send the program to the calculator. If the packaged container cannot be opened,
   create a computer-side Prime program named `SURVEYPRIME`, paste the complete
   `SURVEYPRIME.ppl` source, syntax-check it, and send it through the Kit.
6. Exit any running RPN program using Esc; On can interrupt a program. Then press
   **Home**, use Alpha to enter **`SURVEYPRIME()`**, and press **Enter**. A running
   custom program can consume Home, so exit it first.
7. In SurveyPrime press **9**, then **2**, to run the self-test. Alternatively enter
   **`SURVEYTEST()`** from Home. Expect **16 / 16 passed**.

Launching by name from Home avoids the Program Catalog's touchscreen Run button.
The earlier standalone diagnostic `SPTEST()` may still exist on the original device;
the packaged program exports `SURVEYTEST()` so their names do not conflict.

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
| `core.ppl` | DMS, bearings, closure/area, Bowditch, missing elements, unit factors |
| `keypad.ppl` | GETKEY interaction, menus, numeric forms, reports, formatting |
| `priority_ui.ppl` | Lot workflows/jobs/exchange, conversions and angle arithmetic |
| `missing_ui.ppl` | Missing closing-leg workflows and alternate solutions |
| `geometry.ppl` | COGO, resection, clipping, levels, road geometry and face reduction |
| `geodesy.ppl` | Explicit TM/UTM, ECEF, Helmert, Vincenty and geodetic jobs |
| `extended_ui.ppl` | COGO, point jobs, utilities, levels, angle traverse and road menus |
| `selftest.ppl` | Exported `SURVEYTEST()` with 16 priority checks |
| `main.ppl` | Exported `SURVEYPRIME()`, top-level navigation and settings cleanup |

Use namespaced `SC_` variables for persistent jobs and working data. Keep observations
separate from adjusted results; ask before replacing saved data. Do not use the user's
general-purpose matrices or lists as scratch storage.

Main execution uses degree mode (`HAngle:=0`) and restores Home angle/number settings
on normal exit or a caught error. A hard On interruption can bypass cleanup. Keep
pure calculations separate from input and display routines. Use GETKEY for interaction;
do not add touch APIs, touch buttons, MOUSE, or touch-dependent input dialogs.

## Progress and remaining work

- [x] Priority lot-close, conversion and angle workflows implemented before extensions.
- [x] Additional COGO, levelling, traverse, utility, geodesy and road modules implemented.
- [x] 34 host tests passing; calculation self-test has 16 priority cases.
- [x] Native program packaging and earlier USB source round-trip verified.
- [x] Minimal build/validation repository; generated output and local materials ignored.
- [ ] Native compiler acceptance and successful on-calculator self-test.
- [ ] Native keypad, graphics, persistence and Home-setting acceptance checks.
- [ ] Regional GDF import/catalogs and generalized nonconvex/curved fixed-area cuts.

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

## References

- [HP Prime User Guide](https://hpcalcs.com/downloads/HP-Prime_user_guide_EN.pdf): PPL,
  exported variables, GETKEY, graphics, IFERR and Home settings.
- [HP Prime Quick Start Guide](https://h10032.www1.hp.com/ctg/Manual/c05333004.pdf):
  running programs from Home.
- [Snyder, USGS Paper 1395](https://pubs.usgs.gov/pp/1395/report.pdf): TM series.
- [PROJ](https://proj.org/en/stable/): independent projection/geodesic fixture reference.

The supplied Quickclose manuals provided functional requirements. The implementation
is original source; proprietary reference libraries are local materials, not build inputs.
