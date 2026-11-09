# SurveyPrime user guide

Use the physical-key instructions in `START HERE.md` to launch and navigate.
All calculations use planar metres unless a conversion or geodetic field explicitly
names another unit. Intermediate calculations retain precision; report values are rounded.

## 1. Lot closes

Choose **1 Lot closes → 1 Add leg**. Enter the azimuth in DD.MMSS and a positive
distance. Choose Straight, Curve: add segment area, or Curve: subtract segment area.
For a curved boundary the entered distance is its **chord**, followed by the radius.
The radius must be at least half the chord. The segment must be a minor arc or semicircle.
Choose whether its segment area is added to or removed from the straight-chord polygon.

**Misclose and area** reports the endpoint error in E/N, its magnitude, the bearing
of the line needed to close, chord perimeter, closure ratio, square metres, and hectares.
An open figure's area uses a straight closing chord to the origin. A closure under
1E-9 m is reported as within numerical tolerance instead of displaying an infinite ratio.
The reported error vector is endpoint minus start; the closing vector is its negative.
Area assumes a simple, non-self-intersecting boundary.

**View / edit legs** offers viewing, replacement, insertion, deletion, reversal,
rotation/scaling, and a coordinate origin. Observed data is retained separately from
the last Bowditch adjustment. Editing observations invalidates that adjustment.
Reversal preserves the chosen add/subtract curve-segment areas. Scale changes
multiply lengths by the factor and segment areas by its square.

The lot menu also has last-leg undo with confirmation. Copy coordinates to the point
database assigns consecutive numeric IDs to the start and every endpoint, with an
explicit collision check. The point polygon workflow can copy straight legs back to a lot.

**Coordinates** shows the start point and each successive chord endpoint.

**Bowditch adjustment** can close to the start or a specified end E/N coordinate.
Corrections to E and N are proportional to the observed leg lengths. Results are a
separate adjusted copy; the observed lot is retained. Curve segment areas retain
their original values while chord endpoint coordinates are adjusted. For a link
traverse, the adjusted report still describes displacement relative to the start;
use the final coordinates to check its fixed endpoint.

**Save / open / new lot** keeps numbered snapshots of the legs and origin. Opening
a job requires confirmation and replaces the working lot. Saving makes a new
snapshot, so an earlier saved version remains available. The working lot and saved
jobs persist between normal program runs.

**Missing elements** uses the currently entered known legs and appends missing
closing legs after confirmation. It supports a complete closing leg, two unknown
distances, two unknown bearings, or a bearing on one leg with a distance on another.
Both valid solutions are shown when the geometry permits two. Unknown distances
must be positive; parallel or impossible cases are rejected.

For CSV export, use the lot job menu's export command. It places leg number,
decimal-degree azimuth, chord length, and signed segment area in `SC_TEXT` for retrieval
with the Connectivity Kit.

### Known example

A 100 m square with bearings `0`, `90`, `180`, `270` has area **10,000 m²** and
numerically zero misclose. Shortening the last leg to 99.9 m gives a **0.1 m** error.

The supplied curved-lot example is also in the self-test: five legs with an added
minor circular segment produce approximately **0.057592 m** misclose, ratio **1:10464**,
and **21,287.96 m²** unadjusted area.

## 2. Conversions

Convert DMS and decimal degrees; degrees, radians and gon; distance units; area units;
or square metres to acres/roods/perches. A menu explicitly selects the source and
destination unit. International feet and US survey feet are separate choices.

- International foot = 0.3048 m exactly.
- US survey foot = 1200/3937 m exactly.
- Link = 0.201168 m; chain = 20.1168 m, both international definitions.
- International acre = 4046.8564224 m²; 1 acre = 4 roods = 160 square perches.

The geodetic latitude/longitude forms use decimal degrees. Use the conversion tool
first if those coordinates are supplied as packed DMS.

## 3. Angle addition and subtraction

Enter both signed DMS angles. Subtraction means **A − B**. The result includes a
signed DMS angle, packed DD.MMSS, decimal degrees, and a separate 0–360 wrapped value.
Signed results can exceed one revolution. Back bearing, wrap, and quadrant-to-azimuth
conversions are also available.

For example, `12.5959 + 0.0002` gives **13° 00′ 01″**. `10 − 0.0001` gives
**9° 59′ 59″**. The same arithmetic works for durations entered as HH.MMSS;
the signed result is not automatically wrapped at 24 hours.

## 4. Coordinate geometry

The point database uses positive integer point IDs and E/N/height coordinates.
Computed coordinates can be saved after review. Replacing an ID needs confirmation.
Numbered point jobs save independent snapshots.

- **Radiation:** horizontal distance and height difference, or slope distance with
  zenith angle, instrument/target heights and refraction coefficient. A zenith angle
  is 0° vertically up, 90° horizontal and 180° vertically down. `k=1` disables the
  curvature/refraction term. The two-face reduction utility produces mean observations
  for entry into this form.
- **Join:** azimuth, horizontal distance, height difference, slope distance and zenith angle.
  The azimuth of coincident planar points is conventionally reported as zero.
- **Line offsets:** chainage from a reference point and signed perpendicular offset.
  Positive offset is to the right looking from A to B.
- **Intersections:** bearing/bearing, distance/distance and bearing/distance. Circle
  intersections can give two results; check the required side. Negative ray lengths
  at line intersections identify backward extensions.
- **Three-point resection:** known points A/B/C and clockwise direction differences
  B−A and C−A. Singular, nonconvergent and detected ambiguous geometry is rejected.
  Use well-distributed control; the iterative solver is not a precision/conditioning certificate.
- **Two-point eccentric station:** known main station and reference object, their
  observed directions, and horizontal distance to the main station. Review each solution.
- **Polygon area:** enter stored IDs in boundary order and finish with ID zero.
- **Transform points:** clockwise rotation and planar scale about a pivot, E/N translation,
  and a separate height shift. Original point jobs can be saved before transforming.
- **Radiation/join corrections:** an explicit bearing correction and distance scale
  apply to radiation entry, with inverse corrections available on join reports.
  Other tools work directly in the stated grid coordinates and units.

### Point file exchange

The point menu exports CSV to `SC_TEXT`. A point import is staged in `SC_ROWS` as
`{{ID,E,N,H},...}` and committed only after validation and confirmation. The separate
geodetic menu uses `SC_GROWS` as `{{ID,lat,lon,h},...}` with decimal degrees and
ellipsoidal heights. Duplicate or non-integer IDs are rejected.

The repository contains `tools/import_points.py` to convert a numeric 3/4-column CSV
to an `SPIMPORT.hpprgm` staging program. Install SurveyPrime first, send that helper,
run `SPIMPORT()` from Home, then select Import in the appropriate point menu.
An omitted height defaults to zero. The helper's output must use a new filename.

## 5. Survey utilities

- Circular curve components from radius and deflection, radius and chord, or radius
  and arc length: arc, chord, tangent, mid-ordinate, external and segment area.
  Deflection must be strictly between 0° and 180° for this utility.
- Trigonometric heighting with zenith angle and optional curvature/refraction.
- Along/right and East/North components of a bearing/distance.
- Fixed-area cut of the current straight-sided convex lot by a parallel line.
  The retained side satisfies `E*cos(b) − N*sin(b) <= cut offset`, relative to the lot origin.
  Curved lots and targets outside the original area are rejected; convexity is a user precondition.
- Truncation chord from two corner setbacks and their included angle.
- Missing 3D tie between two slope/zenith observations from the same station.
- Road-intersection edge offsets from road half-widths and intersection angle.
- Two-face reduction of horizontal directions, zenith angles and slope distances.
  Face I zenith must be 0°..180°, face II 180°..360°. The report includes horizontal
  face disagreement and zenith index error, with wrap handled across North.

## 6. Levelling

Set start and known finish RL. Add backsight, foresight and a positive setup distance.
The report shows raw RLs and adjusted RLs, with error distributed by distance or equally
by setup. Raw observations remain available for editing. Intermediate sights refer to
a setup number and use that setup's backsight to compute raw RL.

Deleting setups is disabled while intermediate sights exist, to preserve their references.
A new empty run clears both setups and intermediate sights. Intermediate reports can
also use adjusted backsight-point RLs. An intermediate's position within the setup
is not observed, so no additional within-setup distance correction is inferred.

## 7. Angle traverse

Set the initial backsight azimuth. Each observation is the clockwise turn from the
backsight to the forward line, followed by its horizontal distance. The next station's
backsight is the previous forward azimuth plus 180°. View the computed bearings or
copy them to the working lot for closure and Bowditch adjustment. Angle-sum balancing
distributes the discrepancy equally into a separate copy. Set the required sum in decimal
degrees: the default `(n−2)*180` applies to polygon interior angles; other observation
conventions require a different target. Observed turns remain available independently.

## 8. Geodesy and road alignment

### Geodesy

Set the ellipsoid and projection explicitly. The default is GRS80 / zone 56 South.
UTM configuration supports zones 1–60 and both hemispheres, using GRS80 or WGS84.
Custom Transverse Mercator accepts `a`, inverse flattening, central meridian, origin
latitude, central scale and false E/N. An ellipsoid choice alone does not define a
datum, reference epoch, or transformation between datums.

The forward/inverse series is limited to latitude −80°..84° and longitude within
3.5° of the central meridian. Four checked fixtures agree with PROJ within 1 mm;
that is evidence for those cases, not a uniform accuracy guarantee over the domain.
Convergence and the displayed arc-to-chord comparison are approximations.

Tools include grid/geodetic conversion, geodetic/Cartesian XYZ, a small-angle
seven-parameter **position-vector** transform, Vincenty ellipsoidal inverse, grid
joins, line scale, mean-radius height reduction, grid radiation and block shifts.
Near-antipodal nonconvergent Vincenty cases return an error. Use ellipsoidal heights
for height reduction (`h = RL + geoid separation`). A geoid model is not supplied.

Geodetic point jobs store ID/latitude/longitude/ellipsoidal height and the projection
settings. CSV import/export is available in the geodetic point menu. Historic regional
GDF files are references; their automatic import and named datum catalogs are not implemented.

### Road alignment

Set E/N origin, initial tangent azimuth and starting chainage. Append straight,
circular, or clothoid transition elements. Radius is positive for a right turn and
negative for a left turn. A transition accepts entry/exit signed radii; zero denotes
a straight tangent. Curvature changes linearly with distance along the element.

Set out a chainage and signed right offset, or find the closest alignment chainage/offset
of a coordinate. Elements are integrated using composite Simpson quadrature.
Each element is restricted to at most 180° of turning; divide larger elements.
Alignment inversion uses sampled bracketing and numerical minimization. For overlapping
alignments, verify which branch is required. Nonzero along residual identifies endpoint projection.

## Data and settings

Working data is stored in exported `SC_` variables. The app restores Home angle mode,
number format, precision and separators on normal exit and caught calculation errors.
A hard ON interruption can bypass cleanup; check Home settings after interrupting a program.
Saved jobs should be backed up before editing/replacing the program, clearing memory,
or resetting the calculator. CSV exports and computer backups are the interchange route;
HP48/50 infrared printing and Kermit menus are replaced by Prime file exchange.
