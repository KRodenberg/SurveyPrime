# SurveyPrime implementation tasks and progress

## User requirements

- HP Prime only, confirmed by the user on 2026-11-09.
- Lot closes, conversions, and angle addition/subtraction take first priority.
- Clear menus and complete operation using physical keys; touchscreen input is unavailable.
- Inventory the supplied Quickclose 3.0 references and port their surveying workflows.
- Diagnose the connected calculator and preserve existing data.
- Maintain this task/progress/issues record; keep a clean `Final Output/` folder.
- Use GitHub for version control: https://github.com/KRodenberg/SurveyPrime

## Progress — 2026-11-09

- [x] Create this file before implementation.
- [x] Inventory Quickclose 3.0, Prime examples, and additional 3.1/Expert references.
- [x] Confirm HP Prime target; HID identity `03F0:2441`, firmware `V2.060.650`.
- [x] Read device information and capture its screen over HID.
- [x] Take checksum-verified backups before transferring new programs.
- [x] Implement the priority calculation core and pass 16 checks before extending it.
- [x] Implement physical-key menus, numeric entry, paging, cancellation and validation.
- [x] Implement straight/curved lots, editing/undo, jobs, coordinates, closure/area,
      Bowditch loop/link adjustment, missing elements, rotation/scaling and CSV.
- [x] Implement conversions, angle sum/difference, quadrant/back/wrapped bearings.
- [x] Implement point jobs, lot exchange, 2D/3D radiation/joins, intersections, offsets,
      three-point resection, eccentric station, transforms, and CSV staging.
- [x] Implement curve/height/components/cut-area/truncation/tie/secant/two-face utilities.
- [x] Implement raw/adjusted levelling, intermediate sights, observed/balanced angle traverses.
- [x] Implement TM/UTM, ECEF, Helmert, Vincenty, scale reductions and geodetic jobs,
      plus straight/circular/clothoid alignment setout and inverse offsets.
- [x] Pass 34 host tests against the actual generated PPL source.
- [x] Independently check four projection cases and an ellipsoidal inverse against PROJ.
- [x] Build native `.hpprgm`, readable source, user guide, feature map and hashes.
- [x] Transfer new `SURVEYPRIME` program and retrieve its full source byte-for-byte.
- [x] Verify all four original program records remain byte-identical after transfers.
- [x] Create/authenticate the private GitHub repository and initialize local history.
- [ ] Push the complete final snapshot and confirm GitHub Actions checks.
- [ ] Obtain a native syntax check and execute `SURVEYTEST()` on the target.
- [ ] Verify every menu/form, persistence, graphics and settings restoration on native firmware.
- [ ] Complete remaining Quickclose parity: regional GDF import/catalogs and generalized
      nonconvex/curved fixed-area cuts. IR/Kermit workflows use Prime CSV/USB exchange.

## Current state

`Final Output/` contains a development-preview package. The priority functions and
additional modules have implementation and host tests. Native execution is **not yet
verified**; do not describe this as a completed/full-parity release.
`docs/release/Feature Coverage.md` records supported workflows and remaining work.

The standalone diagnostic on the device is `SPTEST()` (16 priority checks). The full
application's test is `SURVEYTEST()` to avoid duplicate exported names. Exit the running
RPN app with Esc (or On to interrupt), press Home, type `SURVEYPRIME()` or the test name,
and press Enter. No touchscreen Run button is needed for this launch route.

## Issues encountered and resolutions

1. **Target ambiguity:** user confirmed Prime; HID identity corroborates it. The supplied
   HP48/50 libraries cannot execute on Prime and serve as functional references.
2. **Windows device query denied:** PnP/HID inspection and protocol definitions provided
   working readiness, information, screenshots and backup access.
3. **No GitHub credentials/repository:** user authenticated through GitHub device flow.
   Private repository created; Git authentication verified in Windows Credential Manager.
4. **Git/sandbox ownership mismatch:** ordinary shell startup failed after Git initialization.
   Authorized project commands use the normal-user escalation path. This is an environment issue.
5. **Curved-area discrepancy:** degree-mode `ACOS(-1)` had been used as pi. Replaced it
   with a constant; the reference area and all priority checks then passed.
6. **Broken touchscreen / RPN app:** the existing app consumes Home while running.
   Source inspection identified Esc/On exit paths; physical-key instructions were supplied.
7. **USB temporarily absent:** device later reappeared and accepted the complete app.
8. **Large backup dropped packet:** buffering the HID stream before disk writes resolved
   it; retry returned all 53 objects with CRCs verified and exact release-source match.
9. **Native verification pending:** official emulator startup was reached, but no native
   compiler/execution result was obtained. Physical keypad execution remains pending.
10. **Backup state differences:** 37/51 original records match, including all four original
    programs. Two settings and twelve app-state records differ; fields are not attributed.
    Retain both snapshots and do not claim all calculator state was unchanged.

## Required release checks

```powershell
python -m unittest discover -s tests -v
python tools/build.py
```

The host runner is a project-specific interpreter, not HP firmware. Never present its
tests as native compilation, hardware execution or exhaustive accuracy evidence.
Native acceptance steps are in `docs/release/Validation.md`.

## Working rules

- Update this record when implementation, verification, or issues change.
- Preserve reference files and private calculator backups.
- Confirm a program name is absent before its first transfer; preserve existing programs.
- Keep raw device data and downloaded development tools in ignored `work/`.
- Keep release files reproducible with `tools/build.py`; synchronize GitHub history.
- All app interactions must use physical keys through GETKEY; no touch APIs.
- State bearing, DMS, distance, offset, coordinate, curve-area and datum conventions explicitly.
