# Connected calculator diagnosis — 2026-11-09

The calculator initially described as an HP 50g identifies itself over Windows HID
as **HP Prime**, USB `03F0:2441` (Prime G2 family). The user confirmed HP Prime as
the sole target platform.

## Confirmed

- Windows enumerates the device with its HID driver started.
- HID product and manufacturer strings both identify HP Prime.
- Prime readiness query returns `59` (`Y`).
- Device-information query reports firmware `V2.060.650`.
- A USB screen capture successfully shows the existing RPN surveying environment.
- A checksum-verified backup before transfer contains **51 objects**.
- Its four original program objects are identified before choosing a diagnostic name.
- The new name `SPTEST` is absent from that backup.
- Sending `SPTEST` is accepted; a subsequent checksum-verified backup contains **52 objects**.
- All four original program records are byte-identical after this transfer.
- 37 of the 51 original complete records are identical. Two settings and twelve
  application-state records differ between snapshots; their changes have not been
  attributed to individual state fields. Both complete snapshots are retained.

## Execution status

The user reported that the touchscreen cannot activate the Program Catalog's Run
button. The documented keypad route was supplied: **Home → `SPTEST()` → Enter**.
No physical-calculator execution result has been observed or reported yet.

The USB device temporarily ceased to enumerate and later returned. A later screen
capture still showed the existing RPN app. Inspection of its supplied source confirms
that it handles Home while running. Physical Esc exits its entry/selection states and
then the program; On can interrupt it. The revised keypad instructions were supplied.

## Complete application transfer

- A fresh backup confirmed `SURVEYPRIME` did not already exist.
- The complete application was transferred under that new name and readiness returned `Y`.
- A large backup initially failed packet sequencing. The diagnostic client was changed
  to buffer the entire stream before disk writes, avoiding HID queue stalls.
- A retry completed with **53 checksum-verified objects**.
- The complete UTF-16LE release source is present byte-for-byte in the retrieved program record.
- All four original program records remain byte-identical; the same fourteen settings/
  application-state records differ from the initial snapshot.
- The release exports `SURVEYTEST()` to coexist with the earlier standalone `SPTEST()`.

Native compilation/execution is still pending a keypad start; receiving and retrieving
the source does not establish that the program compiles or runs.

The official Virtual Calculator was also extracted and investigated. Its startup
screen was reached; no native program execution or compiler result was obtained.

## Private diagnostic artifacts

Local `work/device-backup-before/` and `work/device-backup-test/` contain the raw
objects and indexes. `work/hardware-before.png` and `work/device-info.bin` contain
the original screen and device response. These remain local, outside the release
and Git history. `work/device-backup-before-release/` and
`work/device-backup-release-verified/` preserve snapshots surrounding the full transfer.

Reproduce the original-program comparison with:

```powershell
python tools/audit_backup.py work/device-backup-before work/device-backup-test
```
