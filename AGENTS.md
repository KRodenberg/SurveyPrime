# Survey calculator implementation

## Requirements and priorities

- Build a clear survey calculator operated entirely with physical keys.
- Implement and verify lot closes, conversions, and angle addition/subtraction first.
- Inventory the supplied Quickclose 3.0 examples and track feature coverage before extending the program.
- Identify and inspect the connected HP 50g without deleting or overwriting calculator data.
- Confirm the target calculator: HP 50g (User RPL) and HP Prime (HP PPL) are different platforms.
- Keep release files and concise user documentation in `Final Output/`.
- Use Git and GitHub for version control; preserve supplied reference files.

## Implementation tasks

- [x] Create this task and progress record before implementation.
- [ ] Inventory Quickclose examples and identify supported workflows.
- [ ] Inspect calculator connection, installed transfer tools, and development tools.
- [ ] Resolve target platform and document input conventions.
- [ ] Implement lot entry, editing, closure, area, and closure reporting.
- [ ] Implement conversions and angle addition/subtraction with input validation.
- [ ] Verify core calculations against independent known examples.
- [ ] Implement remaining identified Quickclose features after the core passes.
- [ ] Verify keypad navigation and calculator compatibility.
- [ ] Package a clean release with installation instructions and known limitations.
- [ ] Commit work and synchronize to GitHub if an authenticated destination is available.

## Current progress

2026-11-09: Workspace initially contains only the `Quickclose/` reference folder.
No existing source code or Git repository was visible in the initial directory listing.
Implementation has not started; reference and device inspection are next.

## Issues and uncertainties

- The request names an "HP50 Prime", while the connected device is described as an HP 50g. Target platform needs clarification.
- Calculator connection, firmware, transfer availability, and reference contents have not yet been inspected.
- GitHub repository and authentication are not yet known.

## Working rules

- Update this file when task status, test evidence, or issues change.
- Do not claim hardware or emulator verification without actually running it.
- Do not overwrite calculator programs or user data during diagnosis.
- Keep reference material separate from original implementation and release artifacts.
- Use explicit angle, bearing, distance, coordinate, and area conventions in code and documentation.
