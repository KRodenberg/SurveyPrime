"""Convert numeric point CSV to a small keypad-runnable Prime import program.

Usage: python tools/import_points.py points.csv output.hpprgm [--geodetic]
CSV: ID,E,N,H or ID,lat,lon,h. Header optional; height defaults to zero.
The generated program fills a staging variable. The user explicitly imports it
inside SurveyPrime, so existing point data cannot be replaced by running it.
"""
import argparse
import csv
import math
from pathlib import Path
from build import encode

def convert(path,geodetic=False):
    rows=[]
    ids=set()
    for number,row in enumerate(csv.reader(Path(path).read_text(encoding='utf-8-sig').splitlines()),1):
        if not row or not any(x.strip() for x in row): continue
        if not rows and row[0].strip().lower() in ('id','point','point_id','point number'): continue
        if len(row) not in (3,4): raise ValueError(f'Row {number}: expected 3 or 4 columns')
        values=[float(x.strip()) for x in row]
        if len(values)==3: values.append(0)
        if not all(math.isfinite(x) and abs(x)<1E99 for x in values): raise ValueError(f'Row {number}: non-finite or excessive value')
        if values[0]<1 or int(values[0])!=values[0] or values[0] in ids: raise ValueError(f'Row {number}: invalid or duplicate point ID')
        if geodetic and (abs(values[1])>90 or abs(values[2])>180): raise ValueError(f'Row {number}: latitude / longitude outside range')
        ids.add(values[0]); rows.append(values)
    if not rows: raise ValueError('No point rows found')
    data='{'+','.join('{'+','.join(format(x,'.15g') for x in row)+'}' for row in rows)+'}'
    var='SC_GROWS' if geodetic else 'SC_ROWS'
    return ('#pragma mode( separator(.,;) integer(h32) )\nEXPORT SPIMPORT()\nBEGIN\n'
            f'  {var}:={data};\n  RETURN {len(rows)};\nEND;\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv'); parser.add_argument('output'); parser.add_argument('--geodetic',action='store_true')
    args=parser.parse_args()
    if Path(args.output).exists(): parser.error('Output exists; choose a new filename')
    text=convert(args.csv,args.geodetic)
    Path(args.output).write_bytes(encode('SPIMPORT',text))
    print('Created',args.output,'; install SurveyPrime first, run SPIMPORT(), then Import from its Points menu.')
