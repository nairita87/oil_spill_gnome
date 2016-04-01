"""
Script to test GNOME with chesapeake bay data (netCDF 3D triangle grid)
Eventually update to use Grid Map rather than BNA
"""

import os
from datetime import datetime, timedelta

import numpy as np

from gnome import scripting
from gnome import utilities
from gnome.basic_types import datetime_value_2d, numerical_methods

from gnome.utilities.remote_data import get_datafile

from gnome.model import Model

from gnome.map import MapFromBNA
from gnome.environment import Wind
from gnome.spill import point_line_release_spill, continuous_release_spill
from gnome.movers import RandomMover, constant_wind_mover, GridCurrentMover

from gnome.outputters import Renderer
from gnome.environment.vector_field import tri_vector_field
from gnome.movers import UGridCurrentMover
import gnome.utilities.profiledeco as pd

# define base directory
base_dir = os.path.dirname(__file__)


def make_model(images_dir=os.path.join(base_dir, 'images')):
    print 'initializing the model'

    start_time = datetime(2015, 9, 24, 1, 1)
    # start_time = datetime(2015, 12, 18, 06, 01)

    # 1 day of data in file
    # 1/2 hr in seconds
    model = Model(start_time=start_time,
                  duration=timedelta(hours=48),
                  time_step=900)

    mapfile = get_datafile(os.path.join(base_dir, 'columbia_river.bna'))

    print 'adding the map'
    model.map = MapFromBNA(mapfile, refloat_halflife=0.0)  # seconds

    # draw_ontop can be 'uncertain' or 'forecast'
    # 'forecast' LEs are in black, and 'uncertain' are in red
    # default is 'forecast' LEs draw on top
    renderer = Renderer(
        mapfile, images_dir, image_size=(600, 1200))
#     renderer.viewport = ((-123.35, 45.6), (-122.68, 46.13))
#     renderer.viewport = ((-122.9, 45.6), (-122.6, 46.0))

    print 'adding outputters'
    model.outputters += renderer

    print 'adding a spill'
    # for now subsurface spill stays on initial layer
    # - will need diffusion and rise velocity
    # - wind doesn't act
    # - start_position = (-76.126872, 37.680952, 5.0),
    spill1 = continuous_release_spill(initial_elements=1000,
                                      num_elements=400,
                                      start_position=(-122.625,
                                                      45.609,
                                                      0.0),
                                      release_time=start_time,
                                      end_position=(-122.6, 45.605, 0.0),
                                      end_release_time=start_time + timedelta(seconds=36000))

    model.spills += spill1

    print 'adding a RandomMover:'
    model.movers += RandomMover(diffusion_coef=10000)

    print 'adding a wind mover:'

    model.movers += constant_wind_mover(0.5, 0, units='m/s')

    print 'adding a current mover:'

    curr_file = get_datafile('COOPSu_CREOFS24.nc')
    vec_field = tri_vector_field(curr_file)
    vec_field.set_appearance(on=True)
    vec_field.set_appearance(mask=vec_field.velocities)
    renderer.grids += [vec_field]

    renderer.delay = 25
    u_mover = UGridCurrentMover(vec_field)
    model.movers += u_mover

    # curr_file = get_datafile(os.path.join(base_dir, 'COOPSu_CREOFS24.nc'))
    # c_mover = GridCurrentMover(curr_file)
    # model.movers += c_mover

    return model


if __name__ == "__main__":
    pd.profiler.enable()
    startTime = datetime.now()
    scripting.make_images_dir()
    model = make_model()
    print "doing full run"
    rend = model.outputters[0]
    field = rend.grids[0]
#     rend.graticule.set_DMS(True)
    for step in model:
        if step['step_num'] == 0:
            rend.set_viewport(((-122.9, 45.6), (-122.6, 46.0)))
#             rend.set_viewport(((-122.8, 45.65), (-122.75, 45.7)))
        #             rend.set_viewport(((-123.25, 48.125), (-122.5, 48.75)))
        #         if step['step_num'] == 18:
        #             rend.set_viewport(((-123.1, 48.55), (-122.95, 48.65)))
#         if step['step_num'] == 10:
            # field.set_appearance(masked=True)
#             rend.set_viewport(((-122.8, 45.75), (-122.75, 45.85)))
        # print step
        print "step: %.4i -- memuse: %fMB" % (step['step_num'],
                                              utilities.get_mem_use())
    print datetime.now() - startTime
    pd.profiler.disable()
    pd.print_stats(0.2)
