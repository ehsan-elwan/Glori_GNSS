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
import re
from datetime import timedelta, datetime as dt
from os.path import exists, join as os_join

import pandas as pd
import requests
from pytz import utc
from skyfield.api import load, wgs84

from config_sky import downloader_parameters
from config_sky import earth_observer_parameters


def downloadTLE(obs_date):
    if obs_date >= dt.today().date():
        obs_date = dt.today().date()
    check_cache = os_join(downloader_parameters['cache']['path'], "GPS_OPS_{}.txt".format(str(obs_date)))
    if exists(check_cache):
        print("Found {} in cache.".format("GPS_OPS_{}.txt".format(str(obs_date))))
        return check_cache
    print("Downloading TLE {} file to cache...".format(obs_date))
    try:
        r = requests.get(downloader_parameters['request']['url'])
        if r.status_code != 200:
            r.raise_for_status()
        with open(check_cache, mode='w') as f:
            f.write(r.text)
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    return check_cache


def estimate_position(obs_lat, obs_lon, obs_alt, obs_datetime, filter_elevation_angle, export=False):
    stations_url = downloadTLE(obs_datetime.date())
    satellites = load.tle_file(stations_url)
    ts = load.timescale()
    t = ts.from_datetime(obs_datetime.astimezone(utc))
    observer = wgs84.latlon(obs_lat, obs_lon, obs_alt)
    df = pd.DataFrame(columns=['prn_id', 'elevation (°)', 'azimuth (°)', 'distance (Km)',
                               'observer_lat', 'observer_lon', 'observer_alt',
                               'observer_date', 'next_rise_above_{}'.format(filter_elevation_angle),
                               'culminate', 'next_rise_below_{}'.format(filter_elevation_angle)])
    for index, sat in enumerate(satellites):
        difference = sat - observer
        topocentric = difference.at(t)
        alt, az, distance = topocentric.altaz()
        t0, events = sat.find_events(observer, t, ts.from_datetime(obs_datetime.astimezone(utc) + timedelta(days=1)),
                                     altitude_degrees=earth_observer_parameters['altitude_degrees_filter'])
        events = list(events)
        df.loc[index] = [re.search('PRN ..', sat.name).group(), alt.degrees, az.degrees, distance.km, obs_lat, obs_lon,
                         obs_alt, obs_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                         t0[events.index(0)].utc_strftime('%Y-%m-%dT%H:%M:%S'),
                         t0[events.index(1)].utc_strftime('%Y-%m-%dT%H:%M:%S'),
                         t0[events.index(2)].utc_strftime('%Y-%m-%dT%H:%M:%S')]
    df = df.sort_values(by=['prn_id']).reset_index(drop=True)
    if export:
        df.to_csv(earth_observer_parameters['observation_output'], index=False)
    return df


if __name__ == "__main__":
    observe_datetime = dt(2021, 7, 7, 15, 45, 00)
    estimate_position(43.558502399999995, 1.4712832, 151, observe_datetime, 10)
