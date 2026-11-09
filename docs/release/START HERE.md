# SurveyPrime — start here

**Target:** HP Prime. **Build:** 0.1 development preview.

The priority functions are lot closes, conversions, and angle addition/subtraction.
The program also includes the surveying tools listed in `Feature Coverage.md`.
Native execution verification is still pending; `Validation.md` records the tests
completed so far.

## Install from the computer

1. Obtain the [HP Prime Connectivity Kit](https://updates.moravia-consulting.com/).
2. Connect and power on your HP Prime. Back up any existing SurveyPrime data before
   replacing an installed version.
3. Open `SURVEYPRIME.hpprgm` in the Kit's program editor and run its syntax check.
4. Send the program to the connected calculator.

`SURVEYPRIME.ppl` is the readable source for inspection or pasting into a new Prime
program in the computer editor. The `.hpprgm` file is the packaged program.

## Start using physical keys

1. Press **Home**, the house key.
2. Use **Alpha** to type **`SURVEYPRIME()`**.
3. Press **Enter**.

You can start it from Home without touching the Program Catalog's Run button.
HP documents Home entry as a way to run programs.

If the existing RPN SurveyCalc is still running, press **Esc** to leave its entry/
selection state and **Esc** again to exit. **On** can interrupt a running program.
Then press Home and enter the program name. Home can be handled by a running custom
program, so leave that program first.

Inside SurveyPrime:

| Key | Action |
|---|---|
| 1–9 | Select the matching numbered item |
| Up / Down | Move the highlighted item; page through reports |
| Enter | Select, accept a value, or return from a report |
| Esc | Cancel the current input or return one menu |
| Digits / decimal point | Replace the initial value with a new number |
| +/− or minus | Change the sign |
| Backspace | Remove the last character |
| EEX | Enter an exponent, such as `1E3` |

The main menu puts **1 Lot closes**, **2 Conversions**, and **3 Add / subtract angles** first.

## Input conventions

- Survey distances and coordinates are **metres**. Conversion tools name both units.
- Bearings are azimuths clockwise from **North**.
- DMS entry uses **DD.MMSS**: `123.3045` means 123° 30′ 45″.
- Minutes and seconds must each be below 60. A minus sign applies to the entire angle.
- Coordinate order is **Easting, Northing, height**.

## Run the calculation self-test

From Home enter **`SURVEYTEST()`**, then Enter. The expected result is **16 / 16 passed**.
It can also be selected under **9 Help / self-test → 2 Run self-test**.
The self-test does not replace a saved lot or point job.

The earlier standalone diagnostic already transferred to the calculator is named
`SPTEST()`. The packaged app uses `SURVEYTEST()` so the two can coexist.

