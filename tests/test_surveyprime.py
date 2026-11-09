"""Independent fixtures and keypad regressions executing the shipped PPL source."""
from pathlib import Path
import math
import random
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build import source, encode, decode
from ppl_runner import Runner


class SurveyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = source()

    def setUp(self):
        self.r = Runner(self.text)

    def call(self, name, *args):
        return self.r.call(name,*args)

    def closeEnough(self,a,b,tol=1E-7):
        self.assertAlmostEqual(a,b,delta=tol)

    def test_native_program_container(self):
        self.assertEqual(decode(encode('SURVEYPRIME',self.text)),('SURVEYPRIME',self.text))

    def test_selftest(self):
        self.r.keys=[30]
        self.assertEqual(self.call('SURVEYTEST'),[16,16,[]])

    def test_selftest_restores_radians(self):
        self.r.globals['HAngle']=1; self.r.keys=[30]
        self.assertEqual(self.call('SURVEYTEST'),[16,16,[]])
        self.assertEqual(self.r.globals['HAngle'],1)

    def test_signed_dms_and_boundaries(self):
        for a,b in [(0.30,0.5),(-0.0001,-1/3600),(360,360),(12.3456,12+34/60+56/3600)]:
            self.closeEnough(self.call('SC_DEC',a),b)
        for a in [12.60,0.006,12.5961,-1.60]: self.assertFalse(self.call('SC_DMSOK',a))
        for a in [0,0.595999,360,-0.59]: self.assertTrue(self.call('SC_DMSOK',a))
        self.closeEnough(self.call('SC_PACK',12+59/60+59.9999/3600),13)

    def test_random_dms_roundtrip(self):
        rng=random.Random(42)
        for _ in range(150):
            x=rng.uniform(-1000,1000)
            self.closeEnough(self.call('SC_DEC',self.call('SC_PACK',x)),x,2E-7)

    def test_azimuth_quadrants(self):
        for e,n,b in [(0,1,0),(1,0,90),(0,-1,180),(-1,0,270),(1,1,45),(-1,-1,225)]:
            self.closeEnough(self.call('SC_AZ',e,n),b)

    def test_translated_coordinates_do_not_change_area(self):
        legs=[[0,100,0],[90,100,0],[180,100,0],[270,100,0]]
        pts=self.call('SC_COORDS',legs,350000,6200000)
        self.closeEnough(self.call('SC_POLYAREA',pts),10000)

    def test_bowditch_link_target(self):
        legs=[[0,100,0],[90,80,0],[180,99.9,0]]
        before=[list(x) for x in legs]
        adjusted=self.call('SC_BOW',legs,81,0.5)
        r=self.call('SC_CLOSE',adjusted)
        self.closeEnough(r[0],81); self.closeEnough(r[1],0.5)
        self.assertEqual(legs,before)

    def test_reverse_preserves_area_and_roundtrip(self):
        legs=[[0,20,0],[90,30,5],[180,20,0],[270,30,0]]
        rev=self.call('SC_REVERSE',legs)
        self.closeEnough(self.call('SC_CLOSE',legs)[5],self.call('SC_CLOSE',rev)[5])
        self.assertEqual(self.call('SC_REVERSE',rev),legs)

    def test_missing_two_bearings_both_solutions(self):
        x=self.call('SC_2BEAR',100,100,100,100)
        for b1,b2 in [(x[0],x[1]),(x[2],x[3])]:
            p=self.call('SC_RAD',0,0,b1,100); p=self.call('SC_RAD',*p,b2,100)
            self.closeEnough(p[0],100); self.closeEnough(p[1],100)
        self.assertEqual(self.call('SC_2BEAR',1000,0,1,1),[])
        self.assertEqual(self.call('SC_2DIST',1,1,0,180),[])

    def test_missing_mixed_two_valid_solutions(self):
        solutions=self.call('SC_MIXED',10,10,11,0)
        self.assertEqual(len(solutions),2)
        for bearing,distance in solutions:
            p=self.call('SC_RAD',0,0,bearing,11)
            p=self.call('SC_RAD',*p,0,distance)
            self.closeEnough(p[0],10); self.closeEnough(p[1],10)

    def test_unit_definitions(self):
        self.closeEnough(self.call('SC_DFACT',4)*100,self.call('SC_DFACT',5))
        self.closeEnough(self.call('SC_DFACT',2)**2,self.call('SC_AFACT',3))
        self.closeEnough(self.call('SC_AFACT',5),4046.8564224)
        self.assertNotEqual(self.call('SC_DFACT',2),self.call('SC_DFACT',3))

    def test_intersections_and_tangencies(self):
        p=self.call('SC_BB',0,0,45,100,0,315)
        self.closeEnough(p[0],50); self.closeEnough(p[1],50)
        self.assertEqual(self.call('SC_BB',0,0,0,1,0,180),[])
        p=self.call('SC_DD',0,0,5,8,0,5)
        self.closeEnough(abs(p[0][1]),3)
        self.closeEnough(p[0][0],4)
        self.assertEqual(self.call('SC_DD',0,0,1,8,0,1),[])
        p=self.call('SC_BD',0,0,90,10,3,5)
        self.assertEqual(len(p),2)
        self.closeEnough(p[0][0],14); self.closeEnough(p[1][0],6)

    def test_line_offsets(self):
        p=self.call('SC_CHAIN',10,20,30,100,-5)
        q=self.call('SC_OFFSET',10,20,30,*p)
        self.closeEnough(q[0],100); self.closeEnough(q[1],-5)

    def test_resection_synthetic_known_position(self):
        pts=[[0,0,0],[300,0,0],[100,250,0]]
        e,n=80,70
        dirs=[self.call('SC_AZ',p[0]-e,p[1]-n) for p in pts]
        p=self.call('SC_RESECT',pts,(dirs[1]-dirs[0])%360,(dirs[2]-dirs[0])%360)
        self.assertEqual(len(p),3)
        self.closeEnough(p[0],e,1E-4); self.closeEnough(p[1],n,1E-4)

    def test_curve_and_height(self):
        p=self.call('SC_CURVE',100,90)
        self.closeEnough(p[0],50*math.pi); self.closeEnough(p[1],100*math.sqrt(2))
        self.closeEnough(p[2],100)
        p=self.call('SC_HEIGHT',100,90,1.5,1.2,1)
        self.closeEnough(p[0],100); self.closeEnough(p[1],0.3)

    def test_two_face_reduction_across_north(self):
        p=self.call('SC_FACES',359.99,89.99,100,180.01,270.03,100.002)
        self.closeEnough(p[0],0); self.closeEnough(p[1],89.98); self.closeEnough(p[2],100.001)
        self.closeEnough(p[3],0.02); self.closeEnough(p[4],0.01)

    def test_lot_point_exchange_and_undo(self):
        self.r.globals['SC_LEGS']=[[0,100,0],[90,100,0],[180,100,0],[270,100,0]]
        self.r.keys=[30,30,43,30]
        self.call('SC_LOTPOINTS')
        self.assertEqual(len(self.r.globals['SC_POINTS']),5)
        self.closeEnough(self.r.globals['SC_POINTS'][2][1],100)
        self.closeEnough(self.r.globals['SC_POINTS'][2][2],100)
        self.r.keys=[34,43,4]  # Lot menu 9, confirm 2, return.
        self.call('SC_LOT')
        self.assertEqual(len(self.r.globals['SC_LEGS']),3)

    def test_angular_balance_preserves_observations(self):
        self.r.globals['SC_TURNS']=[[90.001,100],[90,100],[90,100],[90,100]]
        original=[list(x) for x in self.r.globals['SC_TURNS']]
        self.r.keys=[39,30,30,43,4]  # Balance 6, accept 360, dismiss, retain copy, Esc.
        self.call('SC_ATRAVUI')
        self.assertEqual(self.r.globals['SC_TURNS'],original)
        self.closeEnough(sum(x[0] for x in self.r.globals['SC_TBALANCED']),360)

    def test_fixed_area_cut(self):
        p=self.call('SC_CUT',[[0,0],[100,0],[100,100],[0,100]],0,2500)
        self.closeEnough(p[0],25); self.closeEnough(p[1],2500)

    def test_level_adjustment(self):
        p=self.call('SC_LEVEL',[[1.5,1,100],[1,1.6,300]],10,10,1)
        self.closeEnough(p[0],-0.1)
        self.closeEnough(p[1][0][1],10.525); self.closeEnough(p[1][-1][1],10)

    def test_road_line_arc_transition(self):
        p=self.call('SC_ROAD',[[100,0,0],[50*math.pi,0.01,0.01]],[0,0,0,0],100+50*math.pi,0)
        self.closeEnough(p[0],100,1E-5); self.closeEnough(p[1],200,1E-5); self.closeEnough(p[2],90)
        p=self.call('SC_ROADSTEP',0,0,0,[100,0,0.01],100)
        # Independent power-series integral for a clothoid, theta=s^2/20000.
        e=sum((-1)**j*(1/20000)**(2*j+1)*100**(4*j+3)/(math.factorial(2*j+1)*(4*j+3)) for j in range(9))
        n=sum((-1)**j*(1/20000)**(2*j)*100**(4*j+1)/(math.factorial(2*j)*(4*j+1)) for j in range(9))
        self.closeEnough(p[0],e,1E-5); self.closeEnough(p[1],n,1E-5)

    def test_ecef_known_axes_and_roundtrip(self):
        cfg=self.r.globals['SC_PROJ']
        p=self.call('SC_ECEF',0,0,0,cfg)
        self.closeEnough(p[0],6378137); self.closeEnough(p[1],0); self.closeEnough(p[2],0)
        for lat,lon,h in [(-33.9,151.2,50),(45,-120,0),(0,179,1000),(90,0,30),(-90,0,20)]:
            xyz=self.call('SC_ECEF',lat,lon,h,cfg)
            out=self.call('SC_UNECEF',*xyz,cfg)
            self.closeEnough(out[0],lat); self.closeEnough(out[1],lon); self.closeEnough(out[2],h,1E-5)

    def test_projection_central_meridian_and_roundtrip(self):
        cfg=self.r.globals['SC_PROJ']
        p=self.call('SC_GRID',0,153,cfg)
        self.closeEnough(p[0],500000); self.closeEnough(p[1],10000000); self.closeEnough(p[2],0.9996)
        for lat,lon in [(-33.9,151.2),(-80,150),(0,156),(84,150)]:
            p=self.call('SC_GRID',lat,lon,cfg)
            out=self.call('SC_UNGRID',p[0],p[1],cfg)
            self.closeEnough(out[0],lat,1E-7); self.closeEnough(out[1],lon,1E-6)

    def test_geodesic_equator_and_identity_transform(self):
        cfg=self.r.globals['SC_PROJ']
        p=self.call('SC_VINCENTY',0,0,0,1,cfg)
        self.closeEnough(p[0],6378137*math.pi/180,1E-5); self.closeEnough(p[1],90); self.closeEnough(p[2],270)
        self.assertEqual(self.call('SC_HELMERT',[1,2,3],[0,0,0,0,0,0,0]),[1,2,3])
        self.assertEqual(self.call('SC_HELMERT',[1,2,3],[4,5,6,0,0,0,0]),[5,7,9])

    def test_independent_proj_fixtures(self):
        # PROJ via pyproj, GDA2020/MGA56 (EPSG:7856), generated 2026-11-09.
        cfg=self.r.globals['SC_PROJ']
        fixtures=[(-33.9,151.2,333568.9410107018,6247473.336947628),
                  (-35.1,153.2,518228.1124953245,6115848.930891806),
                  (-80,150,441867.78486627154,1116915.0441517476),
                  (84,156,534994.6550617069,19329005.1823543)]
        for lat,lon,e,n in fixtures:
            result=self.call('SC_GRID',lat,lon,cfg)
            self.closeEnough(result[0],e,0.001); self.closeEnough(result[1],n,0.001)
        out=self.call('SC_VINCENTY',-33,151,-34,152,cfg)
        self.closeEnough(out[0],144692.11054549526,0.00001)
        self.closeEnough(out[1],140.31885377956405,1E-7)

    def test_eccentric_station(self):
        e,n=20,30
        alpha=(self.call('SC_AZ',100-e,-n)-self.call('SC_AZ',-e,-n))%360
        out=self.call('SC_ECC',0,0,100,0,math.hypot(e,n),alpha)
        self.assertTrue(any(abs(p[0]-e)+abs(p[1]-n)<1E-6 for p in out))
        for p in out:
            self.closeEnough(math.hypot(*p),math.hypot(e,n))
        self.assertEqual(self.call('SC_ECC',0,0,100,0,5,180),[])

    def test_alignment_inverse_offset(self):
        legs=[[50*math.pi,0.01,0.01]]
        origin=[0,0,0,1000]
        p=self.call('SC_ROAD',legs,origin,1050,5)
        self.r.budget=2000000
        q=self.call('SC_ROADNEAR',legs,origin,p[0],p[1])
        self.closeEnough(q[0],1050,1E-5); self.closeEnough(q[1],5,1E-5)

    def test_keypad_menu_shortcuts_and_arrows(self):
        self.r.keys=[44]; self.assertEqual(self.call('SC_MENU','Test',['a','b','c']),3)
        self.r.keys=[2,30]; self.assertEqual(self.call('SC_MENU','Test',['a','b','c']),3)
        self.r.keys=[12,30]; self.assertEqual(self.call('SC_MENU','Test',['a','b','c']),2)
        self.r.keys=[4]; self.assertEqual(self.call('SC_MENU','Test',['a']),0)

    def test_keypad_numeric_replace_cancel_sign_and_backspace(self):
        self.r.keys=[42,43,48,44,30]
        self.assertEqual(self.call('SC_NUM','t','label','help',999),[1,12.3])
        self.r.keys=[4]; self.assertEqual(self.call('SC_NUM','t','l','h',5),[0,0])
        self.r.keys=[42,43,19,27,30]; self.assertEqual(self.call('SC_NUM','t','l','h',5),[1,-1])
        self.r.keys=[30]; self.assertEqual(self.call('SC_NUM','t','l','h',5),[1,5])

    def test_main_exit_restores_mode(self):
        self.r.globals.update(HAngle=1,HFormat=2,HDigits=7,HSeparator=1); self.r.keys=[4]
        self.call('SURVEYPRIME')
        self.assertEqual(self.r.globals['HAngle'],1)
        self.assertEqual(self.r.globals['HFormat'],2)
        self.assertEqual(self.r.globals['HDigits'],7)
        self.assertEqual(self.r.globals['HSeparator'],1)

    def test_failed_number_is_not_committed(self):
        self.r.keys=[48,30,30,4]  # '.', Enter -> error page, Enter -> dismiss, Esc -> cancel.
        self.assertEqual(self.call('SC_NUM','t','l','h',5),[0,0])

    def test_priority_end_to_end_no_touch(self):
        # Main -> lot -> add -> bearing 0, distance 100, straight -> report -> exit.
        self.r.keys=[42,42,30,42,47,47,30,42,43,30,4,4]
        self.call('SURVEYPRIME')
        self.assertEqual(self.r.globals['SC_LEGS'],[[0,100,0]])
        self.assertTrue(any('Misclose:' in str(t[0]) for t in self.r.drawn))

    def test_touch_apis_absent(self):
        stripped='\n'.join(line.split('//',1)[0] for line in self.text.splitlines())
        self.assertNotRegex(stripped,r'\b(?:MOUSE|DRAWMENU|INPUT|CHOOSE|WAIT\(-1\))\b')


if __name__ == '__main__': unittest.main()
