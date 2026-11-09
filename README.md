# SurveyPrime

A keypad-operated surveying program for **HP Prime**. Start it from Home by entering
`SURVEYPRIME()` and pressing Enter. All in-program interaction uses physical keys.

The first implementation milestone was lot closes, conversions, and angle arithmetic.
These now have regression tests, including the supplied Quickclose curved-lot example.
The program also includes COGO, level runs, angle traverses, geodesy, and road alignment tools.

**Status: development preview, native execution verification pending.**
The host tests execute the actual PPL source using a project-specific interpreter.
That checks calculations and keypad transitions but does not replace HP's compiler.
See [validation](docs/release/Validation.md) for the exact evidence and remaining work.

- [Clean release folder](Final%20Output/)
- [Installation and keypad launch](docs/release/START%20HERE.md)
- [User guide](docs/release/User%20Guide.md)
- [Quickclose feature coverage](docs/release/Feature%20Coverage.md)
- [Implementation tasks and issues](AGENTS.md)
- [Hardware diagnosis](docs/DEVICE_DIAGNOSTICS.md)

## Development

Python 3.10+ is sufficient for the build and host regression suite. Neither requires
third-party dependencies. Source modules live in `src/`.

```powershell
python -m unittest discover -s tests -v
python tools/build.py
```

The build produces a named UTF-16LE `.hpprgm` container, readable PPL, documentation,
and SHA-256 hashes. It verifies the program container by decoding it back to source.
GitHub Actions repeats the tests and checks that generated release files are current.

`tools/prime_link.py` is a separate developer diagnostic utility requiring `hidapi`.
It can query a Prime, capture its screen, back up objects, and transfer a program.
Backups contain calculator user data and belong in the ignored `work/` folder.
The on-calculator app does not require Python or any host dependency.

Original source was written for this project from the functional requirements in
the supplied manuals. Local reference material remains in `Quickclose/`.
