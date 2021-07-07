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
#
# Config file
#
# =========================================================================

from os.path import dirname, realpath, join as os_join


downloader_parameters = dict(
    request=dict(
        url="https://celestrak.com/NORAD/elements/gps-ops.txt",
    ),
    cache=dict(
        path=os_join(dirname(realpath(__file__)), 'tle_cache')
    )
)

earth_observer_parameters = dict(
    altitude_degrees_filter=10,
    observation_output = os_join(dirname(realpath(__file__)),'observation_output')
)
