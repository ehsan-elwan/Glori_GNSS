#!/usr/bin/python
# -*- coding: utf-8 -*-
# =========================================================================
#   Program:   
#
#   Copyright (c) CESBIO. All rights reserved.
#
#   See LICENSE for details.
#
#   This software is distributed WITHOUT ANY WARRANTY; without even
#   the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE.  See the above copyright notices for more information.
#
# =========================================================================
#
# Authors: Ehsan ELWAN
#
# =========================================================================
from datetime import datetime as dt

import pandas as pd

from config_sky import specular_calculator_parameters as spec_parm
from offline_mode.Specular_reflection_calculator import spec_coordinates, ellipse_from_spec, ellipse_to_json
from offline_mode.satellite_position_estimator import estimate_position

observe_datetime = dt(2021, 7, 7, 15, 45, 00)
df = estimate_position(43.558502399999995, 1.4712832, 151, observe_datetime, 10)
df = pd.concat([df, pd.DataFrame(columns=['specular_lat', 'specular_lon', 'specular_dem'])])
ellipses = dict()
for index, row in df.iterrows():
    values = spec_coordinates(row['observer_lat'],
                              row['observer_lon'],
                              row['observer_alt'],
                              row['elevation (°)'],
                              row['azimuth (°)'])

    ellipses[row['prn_id']] = ellipse_from_spec(values['specular_lat'], values['specular_lon'],
                                                row['observer_alt'] - values['specular_dem'],
                                                row['elevation (°)'], row['azimuth (°)'], spec_parm['lambda_ellipse'],
                                                vertices=10)
    for key in values:
        df.at[index, key] = values[key]

ellipse_to_json(ellipses)
