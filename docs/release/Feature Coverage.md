# Quickclose 3.0 feature coverage

The supplied version 3 manual was inventoried before implementation. Core functions
were implemented and passed their first 16 calculation checks before the additional
modules were added. This table records implementation coverage; native acceptance
is still pending for all modules. This build is **not full Quickclose feature parity**.

| Reference group | SurveyPrime implementation | Adaptation / remaining work |
|---|---|---|
| CLOSE entry, running area and misclose | Lot entry and report available at any time | Straight/chord distance entered in metres |
| CLOSE curved boundaries | Signed minor/semicircle segment area from chord/radius | Arc/radius conversion is a separate utility; major arcs need subdivision |
| CLOSE view/edit/insert/delete/reverse | Lot editing, origin controls and last-leg undo | Swap by replacement/insertion |
| CLOSE jobs | Numbered saved snapshots, open/delete/new working lot | Numeric job IDs suit physical-key input |
| CLOSE coordinates and area | Endpoint coordinates, straight-closing-chord area plus segments | Simple boundary assumed |
| CLOSE missing elements | One complete leg, two distances, two bearings, mixed pair | Both feasible solutions shown |
| CLOSE Bowditch | Closed loop or fixed end target; adjusted copy/report | Original curve segment areas retained |
| CLOSE rotation/scale | Clockwise rotation and positive scale | Area scales by factor squared |
| CLOSE export and COGO exchange | CSV leg export; lot endpoints to points; ID polygon to lot | Chord endpoints and straight polygon legs exchanged |
| Conversion menu | DMS/decimal/radians/gon, distance, area, acres/roods/perches | International and US feet explicit |
| Angle/time addition/subtraction | Signed DMS sum/difference and separate wrapped result | Durations use the same arithmetic without automatic 24h wrap |
| COGO jobs and point management | Numeric IDs, add/edit/delete, snapshots, CSV staging | Fixed E/N/height order; no automatic ID overwrite |
| COGO traverses/radiations | 2D and 3D radiation; stored origin selection | Repeat from a newly saved point to traverse |
| COGO joins and polygon area | 2D/3D joins and ID-ordered area | Raw grid reports; optional inverse radiation/join corrections |
| COGO line offsets | Forward chainage/offset and inverse projection | Right-positive convention |
| COGO curve offsets | Forward/inverse circular or transition alignment offsets | Access through Road alignment |
| COGO intersections | Bearing/bearing, distance/distance, bearing/distance | Explicit alternate solutions and extensions |
| COGO three-point resection | Multistart iterative solver | Detected singular/ambiguous cases rejected; conditioning review still needed |
| COGO eccentric station | Two known points, observed angle and distance to main | Alternate solutions reviewed before storage |
| COGO corrections | Radiation bearing/scale presets and inverse join display | Corrections intentionally scoped to these workflows |
| COGO transformation | Pivot/rotate/scale, E/N and height shifts | Save a snapshot to retain an original job |
| COGO 3D | Slope/zenith, instrument/target heights, curvature/refraction | Two-face reduction utility supplies mean observations |
| UTILS secants | Two road half-widths and intersection angle | Basic two-road edge-offset form |
| UTILS trig height, radiation, joins, components | Height utility plus shared COGO functions | Explicit zenith and right-offset conventions |
| UTILS fixed area | Parallel-line cut of a convex straight lot | General/nonconvex and curved cut-area solving not implemented |
| UTILS circular curve, truncation, missing tie | Curve components, corner chord, 3D tie | Minor-curve component utility |
| LEVEL | Raw/adjusted run, edit setups, raw/adjusted intermediate sights | Intermediate correction uses the setup's backsight point |
| ATRAV | Backsight plus clockwise-turn traverse, copy to lot, angle-sum balance | Separate observed and balanced copies; user specifies target sum |
| GEOD coordinates/jobs | Explicit ellipsoid/TM configuration; geodetic jobs and CSV | Regional GDF import/catalogs not implemented |
| GEOD conversions/joins/scales | TM, ECEF, small-angle Helmert, Vincenty, line/height factors | Projection domain limited; convergence/arc-to-chord approximate |
| GEOD ground/grid radiation and block shifts | Distance-reduction utility, grid radiation, block shift | User supplies ellipsoidal height and transformation parameters |
| ROAD | Straight, circular, clothoid elements; setout and inverse | Numerical integration/minimization; divide large-turn elements |
| IR printer / Kermit / HP48–50 installation | Prime USB file exchange and CSV export | HP Prime platform adaptation; no infrared printer support |
| ASTRO 3.1 and older Expert libraries | Inventoried as additional supplied references | Outside Quickclose 3.0 feature scope; not implemented |

The outstanding rows above remain tracked in the repository's `AGENTS.md`.
Reference files remain in the local `Quickclose/` folder; release files contain the
original implementation and its documentation.

