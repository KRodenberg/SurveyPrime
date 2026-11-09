# Validation — 2026-11-09

## Result

**34 host regression tests pass. Native compilation and execution remain unverified.**
This is a development preview. A syntax check in the HP Connectivity Kit and an
on-device `SURVEYTEST()` run are still required before accepting it as a usable release.

## What was executed

```powershell
python -m unittest discover -s tests -v
python tools/build.py
```

The tests parse and execute the actual generated PPL source through a small
project-specific interpreter. They cover:

- DMS carry/borrow, signed inputs, validation and 150 deterministic round trips.
- All azimuth quadrants; square closure/area and a translated polygon.
- The supplied Quickclose curved-boundary example: misclose about 0.057592 m,
  ratio about 1:10464 and area about 21,287.96 m².
- Bowditch link targets and preservation of input observations.
- Both missing-bearing and mixed missing-element solutions; singular cases.
- International and US survey foot definitions.
- Line/circle intersections, offsets and a synthetic three-point resection.
- An eccentric-station solution and circular-alignment inverse offset.
- Curve components, slope/height reduction and fixed-area clipping.
- A level-run adjustment reaching the specified finish RL.
- Two-face reduction across North; lot/point exchange and last-leg undo; angular
  balancing that retains the original observations.
- Straight/circular/clothoid alignment calculations, including an independent
  power-series check of a transition element.
- Cartesian axes, geodetic round trips and seven-parameter identities.
- Four independently generated PROJ projection fixtures, within 0.001 m at each fixture.
- An ellipsoidal inverse independently checked against PROJ.
- Menu digits/arrows/Esc, numeric replacement/backspace/sign/cancel, Home settings
  restoration, and an end-to-end lot entry/report sequence without touch APIs.
- Native program container encoding/decoding back to the same name and source.

The host interpreter approximates PPL semantics; agreement there does not establish
HP firmware syntax, graphics layout, keyboard buffering, persistent-variable behavior
or numeric equivalence. It deliberately identifies itself as a host test tool.

## On-calculator self-test

`SURVEYTEST()` contains 16 priority checks and should show **16 / 16 passed**.
The connected Prime accepted the separate SPTEST diagnostic and the complete
SURVEYPRIME application. The complete release source was retrieved in a subsequent
checksum-verified backup and matched exactly. No physical execution result has been
observed. Its touchscreen is reported broken. The existing RPN app handles the Home
key itself, so it must be exited before launching from Home.

The device temporarily stopped enumerating and later returned. A dropped packet in
the large backup was resolved by collecting the HID stream in memory before writing
records to disk. The completed backup has 53 objects, including both new programs;
all four original program records remain byte-identical to the initial backup.

## Native acceptance still required

1. Check `SURVEYPRIME.hpprgm` with HP's compiler and fix any native syntax errors.
2. Run `SURVEYTEST()` and confirm all 16 checks on the target Prime.
3. Exercise Enter, Esc, digits and arrows on every menu and numeric form.
4. Enter/save/reopen a lot, exit/restart and verify persistence and Home settings.
5. Verify curved-lot and adjusted-area reports against independent calculations.
6. Review long reports for clipping and compare 3D/geodetic/road cases on native firmware.

Native verification is the main remaining release issue. The build also intentionally
has the limitations detailed in `Feature Coverage.md` and `User Guide.md`.
