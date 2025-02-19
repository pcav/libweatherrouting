import unittest
import weatherrouting
import random
import datetime
import os
import math
import json
import datetime

from weatherrouting.routers.linearbestisorouter import LinearBestIsoRouter

class mock_grib:
    def __init__(self,starttws,starttwd, fuzziness ):
        self.starttws = starttws
        self.starttwd = starttwd
        self.fuzziness = fuzziness
        self.seedSource = datetime.datetime.fromisoformat('2000-01-01T00:00:00')
        
    def tws_var(self,t=None):
        if t:
            delta = t - self.seedSource
            random.seed(delta.total_seconds())
        return self.starttws + self.starttws*(random.random()*self.fuzziness -self.fuzziness/2)

    def twd_var(self,t=None):
        if t:
            delta = t - self.seedSource
            random.seed(delta.total_seconds())
        return self.starttwd + self.starttwd*(random.random()*self.fuzziness -self.fuzziness/2)

    def getWindAt(self, t, lat, lon):
        return ( math.radians(self.twd_var(t)), self.tws_var(t), )

class mock_point_validity:

    def __init__(self, track, factor=4):
        self.mean_point = ((track[0][1]+track[1][1])/2, (track[0][0]+track[1][0])/2)
        self.mean_island = weatherrouting.utils.pointDistance(*(track[0]+track[1]))/factor

    def point_validity(self, y, x):
        if weatherrouting.utils.pointDistance(x,y,*(self.mean_point)) < self.mean_island:
            return False
        else:
            return True

    def line_validity(self, y1, x1, y2, x2):
        if weatherrouting.utils.pointDistance(x1,y2,*(self.mean_point)) < self.mean_island:
            return False
        else:
            return True

polar_obj = weatherrouting.Polar(os.path.join(os.path.dirname(__file__),'Bavaria38.pol'))


class TestRouting_lowWind_noIsland(unittest.TestCase):

    def setUp(self):
        grib = mock_grib(2,180,0.1)
        self.track = [(5,38),(5.2,38.2)]
        island_route = mock_point_validity(self.track)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_obj,
            self.track,
            grib,
            datetime.datetime.fromisoformat('2021-04-02T12:00:00'),
            pointValidity = island_route.point_validity,
        )
        
    def test_step(self):
        res = None 
        i = 0
        
        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1

        self.assertEqual(i, 8)
        self.assertEqual(not res.path, False)

        path_to_end = res.path + [[*self.track[-1],'']]
        self.assertEqual( res.time, datetime.datetime.fromisoformat('2021-04-02 19:00:00'))
        self.assertEqual(len(json.dumps(weatherrouting.utils.pathAsGeojson(path_to_end))), 2844)


class TestRouting_lowWind_mockIsland_5(unittest.TestCase):

    def setUp(self):
        grib = mock_grib(2,180,0.1)
        self.track = [(5,38),(5.2,38.2)]
        island_route = mock_point_validity(self.track, factor=5)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_obj,
            self.track,
            grib,
            datetime.datetime.fromisoformat('2021-04-02T12:00:00'),
            pointValidity = island_route.point_validity,
        )
        
    def test_step(self):
        res = None 
        i = 0
        
        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1

        self.assertEqual(i, 7)
        self.assertEqual(not res.path, False)


class checkRoute_mediumWind_mockIsland_8(unittest.TestCase):

    def setUp(self):
        grib = mock_grib(5,45,0.5) 
        self.track = [(5,38),(4.6,37.6)]
        island_route = mock_point_validity(self.track, factor=8)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_obj,
            self.track,
            grib,
            datetime.datetime.fromisoformat('2021-04-02T12:00:00'),
            lineValidity = island_route.line_validity,
        )
        
    def test_step(self):
        res = None 
        i = 0

        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1
        
        self.assertEqual(i, 6)
        self.assertEqual(not res.path, False)

class checkRoute_highWind_mockIsland_3(unittest.TestCase):

    def setUp(self):
        grib = mock_grib(10,270,0.5) 
        self.track = [(5,38),(5.5,38.5)]
        island_route = mock_point_validity(self.track, factor=3)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_obj,
            self.track,
            grib,
            datetime.datetime.fromisoformat('2021-04-02T12:00:00'),
            lineValidity = island_route.line_validity,
        )
        
    def test_step(self):
        res = None 
        i = 0

        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1
        
        self.assertEqual(i, 6)
        self.assertEqual(not res.path, False)
        