# Technical sources

The implementation is original PPL, using standard surveying algorithms and the
functional descriptions in the supplied reference collection.

- Supplied `Quickclose/Quickclose_3.0/version3.pdf`: module workflows, requirements,
  and the numerical curved-lot example in sections 4.91–4.96.
- Supplied Prime source programs: platform conventions and existing touch-based
  workflows to replace with physical-key interaction.
- [HP Prime User Guide](https://hpcalcs.com/downloads/HP-Prime_user_guide_EN.pdf):
  PPL syntax, exported variables, graphics, GETKEY, IFERR, and Home settings.
- [HP Prime Quick Start Guide](https://h10032.www1.hp.com/ctg/Manual/c05333004.pdf):
  launching a program by entering its name in Home.
- [Official Prime software downloads](https://updates.moravia-consulting.com/):
  Connectivity Kit and Virtual Calculator. The 2026-09-09 x64 emulator was extracted
  locally for investigation; third-party binaries are development tools in `work/`.
- [Snyder, USGS Professional Paper 1395](https://pubs.usgs.gov/pp/1395/report.pdf):
  Transverse Mercator forward/inverse series.
- [PROJ](https://proj.org/en/stable/): independent numerical cross-checks through
  the locally available pyproj library, EPSG:7856 and ellipsoidal inverses.
- [prime_connection_kit](https://github.com/56phil/prime_connection_kit): published
  descriptions of Prime HID packet framing, file types, CRC, program containers,
  and backup records. Its documented observations were used to build a small
  original Python diagnostic client. No third-party source is included in the app.
- [libhpcalcs / hplp](https://github.com/debrouxl/hplp): protocol provenance cited
  by the connection-kit reference.
