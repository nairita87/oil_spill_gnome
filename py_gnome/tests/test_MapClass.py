# -*- coding: utf-8 -*-
"""
Latest Revision: Mar 26

Can be run with either nose or py.test


@author: brian.zelenke
@author: Chris.Barker
You should  be able to `git checkout prototype; cd py_gnome; python setup.py build; python setup2.py develop` and then run this script.
"""

from __future__ import division
import numpy as np
import gnome.map


def test_map_island_color():
    '''
    Test the creation of a color map with an island inset.
    '''
    m = gnome.map.gnome_map([500,500],
                            "SampleData/MapBounds_Island.bna",
                            color_mode='RGB') #Create a 500x500 pixel map.
    m.image.save('Color_MapBounds.png') #Write the result to the present working directory as a PNG image file.
    assert True
    #assert False #Force this test to fail so that NOSE will print output to the command window.

def test_map_island_monochrome():
    '''
    Test the creation of a black and white map with an island inset.
    '''
    m = gnome.map.lw_map([500,500],"SampleData/MapBounds_Island.bna",2.*60.*60.,"1") #Create a 500x500 pixel map, with an LE refloat half-life of 2 hours (specified here in seconds).
    m.image.save('B&W_MapBounds.png') #Write the result to the present working directory as a PNG image file.
    assert True
    #assert False #Force this test to fail so that NOSE will print output to the command window.

def test_map_in_water():
    '''
    Test whether the location of a particle on the map -- in or out of water -- is determined correctly.
    '''
    m = gnome.map.lw_map([500,500],"SampleData/MapBounds_Island.bna",2.*60.*60.,"1") #Create a 500x500 pixel map, with an LE refloat half-life of 2 hours (specified here in seconds).
    
    #Coordinate of a point within the water area of MapBounds_Island.bna.
    LatInWater=48.1647
    LonInWater=-126.78709
    
    assert(m.in_water((LonInWater,LatInWater))) #Throw an error if the know in-water location returns false.

def test_map_on_land():
    '''
    Test whether the location of a particle on the map -- off or on land -- is determined correctly.
    ''' #Create a 500x500 pixel map, with an LE refloat half-life of 2 hours (specified here in seconds).
    m = gnome.map.lw_map((500,500),
                         "SampleData/MapBounds_Island.bna",
                         2.*60.*60.,
                         color_mode = "1") 
    
    # Coordinate of a point on the island of MapBounds_Island.bna.
    OnLand = (-127, 47.4)
    ## this should be failing! that's not on land == but it is on the map
    assert(m.on_land( OnLand )) #Throw an error if the know on-land location returns false.

def test_in_water_resolution():
    '''
    Test the limits of the precision, to within an order of magnitude, defining whether a point is in or out of water.
    '''
    
    m = gnome.map.lw_map([500,500],"SampleData/MapBounds_Island.bna",2.*60.*60.,"1") #Create a 500x500 pixel map, with an LE refloat half-life of 2 hours (specified here in seconds).
    
    #Specify coordinates of the two points that make up the southeastern coastline segment of the island in the BNA map.
    x1=-126.78709
    y1=47.666667
    x2=-126.44218
    y2=47.833333
    
    #Define a point on the line formed by this coastline segment.
    slope=(y2-y1)/(x2-x1)
    b=y1-(slope*x1)
    py=47.7
    px=(py-b)/slope
    
    #Find the order of magnitude epsilon change in the latitude that causes the
    #given point to "move" from water to land.
    eps=np.spacing(1) #Distance between 1 and the nearest floating point number.
    mag=0.
    running=True
    while running:
        mag=mag+1.0
        print "Order of magnitude: %g" %mag
        running=m.in_water((px,py+(eps*(10.0**mag))))
    
    #Difference in position within an order of magnitude in degrees of latitude necessary to "move" point from water to land.
    dlatO0=(eps*(10.0**(mag-1.0)))
    dlatO1=(eps*(10.0**mag))
    
    print "A particle positioned on a coastline segment must be moved something more than %g meters, but less than %g meters, inland before pyGNOME acknowledges it's no longer in water." %(dlatO0*1852.0,dlatO1*1852.0)


## tests for GnomeMap -- the most basic version
class Test_GnomeMap:
    def test_on_map(self):
        map = gnome.map.GnomeMap()
        assert map.on_map((0.0, 0.0))
        
        # too big latitude
        assert map.on_map( (0.0, 91.0) ) is False

        # too small latitude
        assert map.on_map( (0.0, -91.0) ) is False

        # too big langitude
        assert map.on_map( (0.0, 361.0) ) is False

        # too small langitude
        assert map.on_map( (0.0, -361.0) ) is False
        
    def test_on_map(self):
        map = gnome.map.GnomeMap()
        assert map.on_map((0.0, 0.0))
        
        # too big latitude
        assert map.on_map( (0.0, 91.0) ) is False

        # too small latitude
        assert map.on_map( (0.0, -91.0) ) is False

        # too big longitude
        assert map.on_map( (0.0, 361.0) ) is False

        # too small longitude
        assert map.on_map( (0.0, -361.0) ) is False
        
    def test_on_land(self):
        map = gnome.map.GnomeMap()
        assert map.on_land( (18.0, -87.0) ) is False
        
    def test_in_water(self):
        map = gnome.map.GnomeMap()

        assert map.in_water( (18.0, -87.0) )
        
        assert map.in_water( (370.0, -87.0) ) is False
        
    def test_allowable_spill_position(self):
        map = gnome.map.GnomeMap()

        assert map.allowable_spill_position( (18.0, -87.0) )

        assert map.allowable_spill_position( (370.0, -87.0) ) is False
    
#####
from gnome.map import RasterMap
from gnome.utilities import map_canvas
class Test_RasterMap():
    """
    some tests for the raster map
    """
    
    # a very simple raster:
    w, h = 20, 12
    raster = np.zeros((w, h), dtype=np.uint8)
    # set some land in middle:
    raster[6:13, 4:8] = 1
        
    def test_on_map(self):
        map = RasterMap(refloat_halflife = 6, #hours
                        bitmap_array= self.raster,
                        map_bounds = ( (-50, -30), (-50, 30), (50, 30), (50, -30) ),
                        projection=map_canvas.NoProjection(),
                        )
        assert map.on_map((0.0, 0.0))

        assert map.on_map((55.0, 0.0)) is False
        
    def test_on_land(self):
        map = RasterMap(refloat_halflife = 6, #hours
                        bitmap_array= self.raster,
                        map_bounds = ( (-50, -30), (-50, 30), (50, 30), (50, -30) ),
                        projection=map_canvas.NoProjection(),
                        )
        print "testing a land point:"
        assert map.on_land((10, 6)) # right in the middle
        
        print "testing a water point:"
        assert not map.on_land((19.0, 11.0))
        
    def test_spillable_area(self):
        # anywhere not on land is spillable...
        # in this case
        map = RasterMap(refloat_halflife = 6, #hours
                        bitmap_array= self.raster,
                        map_bounds = ( (-50, -30), (-50, 30), (50, 30), (50, -30) ),
                        projection=map_canvas.NoProjection(),
                        )
        print "testing a land point:"
        assert not map.allowable_spill_position((10, 6)) # right in the middle of land
        
        print "testing a water point:"
        assert map.allowable_spill_position((19.0, 11.0))
    
    def test_spillable_area2(self):
        # a test with a polygon spillable area
        
        poly = ( (5,2), (15,2), (15,10), (10,10), (10,5) )
        map = RasterMap(refloat_halflife = 6, #hours
                        bitmap_array= self.raster,
                        map_bounds = ( (-50, -30), (-50, 30), (50, 30), (50, -30) ),
                        projection=map_canvas.NoProjection(),
                        spillable_area = poly
                        )
        
        # cases that are spillable
        assert map.allowable_spill_position((11.0, 3.0))
        assert map.allowable_spill_position((14.0, 9.0))
        
        # in polygon, but on land:
        assert not map.allowable_spill_position((11.0, 6.0))

        # outside polygon, on land:
        assert not map.allowable_spill_position((8.0, 6.0))

        # outside polygon, off land:
        assert not map.allowable_spill_position((3.0, 3.0))

from gnome.map import MapFromBNA
class Test_MapfromBNA:
    filename = "SampleData/Mapbounds_Island.bna"
    bna_map = MapFromBNA("SampleData/MapBounds_Island.bna", 6)
    def test__init__(self):
        m = MapFromBNA(self.filename, 6, raster_size=1000)
    
    def test_map_in_water(self):
        '''
        Test whether the location of a particle on in water -- is determined correctly.
        '''
        InWater=( -126.78709, 48.1647 )
        
        assert self.bna_map.in_water(InWater) #Throw an error if the know in-water location returns false.
        assert not self.bna_map.on_land(InWater)

    def test_map_in_water2(self):
        InWater = (-126.971456, 47.935608) # in water, but inside land Bounding box
        assert self.bna_map.in_water(InWater) #Throw an error if the know in-water location returns false.

    def test_map_on_land(self):
        '''
        Test whether the location of a particle  on land -- is determined correctly.
        '''
        
        OnLand = (-127, 47.8)
        assert self.bna_map.on_land( OnLand )  #Throw an error if the know on-land location returns false.
        assert not self.bna_map.in_water( OnLand )  #Throw an error if the know on-land location returns false.

    def test_map_in_lake(self):
        '''
        Test whether the location of a particle in a lake-- is determined correctly.
        '''
        InLake = (-126.8, 47.84)
        assert self.bna_map.in_water( InLake )  #Throw an error if the know on-land location returns false.
        assert not self.bna_map.on_land( InLake )  #Throw an error if the know on-land location returns false.

    def test_map_spillable(self):
        point = (-126.984472, 48.08106) # in water, in spillable
        assert self.bna_map.allowable_spill_position( point )  #Throw an error if the know on-land location returns false.

    def test_map_spillable_lake(self):
        point = (-126.793592, 47.841064) # in lake, should be spillable
        assert self.bna_map.allowable_spill_position( point )  #Throw an error if the know on-land location returns false.
    
    def test_map_not_spillable(self):        
        point = (-127, 47.8) # on land should not be spillable
        assert not self.bna_map.allowable_spill_position( point )  #Throw an error if the know on-land location returns false.

    def test_map_not_spillable2(self):
        point = (127.244752, 47.585072) # in water, but outside spillable area
        assert not self.bna_map.allowable_spill_position( point )  #Throw an error if the know on-land location returns false.
    
    def test_map_not_spillable3(self):
        point = (127.643856, 47.999608) # off the map -- should not be spillable
        assert not self.bna_map.allowable_spill_position( point )  #Throw an error if the know on-land location returns false.

    def test_map_on_map(self):
        point = (-126.12336, 47.454164)
        assert self.bna_map.on_map( point )

    def test_map_off_map(self):
        point = (-126.097336, 47.43962)
        assert not self.bna_map.on_map( point )
    
