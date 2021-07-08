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
from os.path import join as os_join

import numpy as np
import pyproj as pyproj
import srtm

import geojson
from config_sky import specular_calculator_parameters as parameters


def ellipse_to_json(ellipse_dict):
    features = []
    for key in ellipse_dict:
        features.append(
            geojson.Feature(geometry=geojson.Polygon([[tuple(x) for x in ellipse_dict[key]]]),
                            properties=dict(ID=key)))
    output = os_join(parameters['geojson_path'], 'Ellipse_layer.json')
    with open(output, 'w') as fp:
        geojson.dump(geojson.FeatureCollection(features), fp, sort_keys=True)

    return output


def ellipse_from_spec(spec_lat, spec_lon, observer_alt, sat_elevation, sat_azimuth, lambda_wave_length, vertices=10):
    """ Function to compute the ellipse footprint coordinates

    Args:
        spec_lat (float): Latitude of the specular point center [deg]
        spec_lon (float): Longitude of the specular point center [deg]
        observer_alt (float): vertical distance between receiver and surface [m]
        sat_elevation (float): satellite elevation angle [deg]
        sat_azimuth (float): azimuth angle [deg]
        lambda_wave_length (float): Signal wavelength :math:`\\lambda` [m]
        vertices (int): number of segments in the resulting polygon

    Returns:
        numpy.array: array of lat_s-lon coordinate describing the footprint
    """

    h_clip = np.clip(observer_alt, 0, np.inf)  # clip height to avoid negative values
    s_min_axis = np.sqrt(lambda_wave_length * h_clip / np.sin(np.deg2rad(sat_elevation)) +
                         np.power(lambda_wave_length / 2 / np.sin(np.deg2rad(sat_elevation)), 2))
    s_maj_axis = s_min_axis / np.sin(np.deg2rad(sat_elevation))

    rot = np.deg2rad(-sat_azimuth)
    geo_id = pyproj.Geod(ellps='WGS84')
    angle1, angle2, lat_onv = geo_id.inv(spec_lon, spec_lat, spec_lon, spec_lat + 1)
    angle1, angle2, lon_onv = geo_id.inv(spec_lon, spec_lat, spec_lon + 1, spec_lat)
    coordinates = []
    for angle in np.arange(0, 360.01, 360. / vertices):
        y = s_maj_axis * np.cos(np.deg2rad(angle))
        x = s_min_axis * np.sin(np.deg2rad(angle))
        el_lng = (x * np.cos(rot) - y * np.sin(rot)) / lon_onv
        el_lat = (y * np.cos(rot) + x * np.sin(rot)) / lat_onv
        coordinates.append([spec_lon + el_lng, spec_lat + el_lat])
    return np.asarray(coordinates)


def spec_coordinates(obs_lat, obs_lon, obs_alt, sat_alt, sat_azimuth):
    """ Returns specular point coordinates from RX location and Tx pointing

    Args:
        obs_lat (float): Rx latitude [deg]
        obs_lon (float): Rx longitude [deg]
        obs_alt (float): Rx height over mean sea level [m] RX_alt
        sat_alt (float): Satellite elevation relative to Rx [deg]
        sat_azimuth (float): Satellite azimuth relative to Rx [deg]

    Returns:
        dict(specular_lat:float, specular_lon:float, specular_dem:float):
            - Latitude of specular point
            - Longitude of specular point
            - DEM altitude at specular point location

    """
    geo_id = pyproj.Geod(ellps='WGS84')
    dem_data = srtm.get_data(local_cache_dir=parameters['srtm_cache_path'])
    spec_dem, spec_lon, spec_lat = 0, 0, 0
    for it in range(parameters['number_of_iteration_spec_calc']):
        # logger.debug('Computing fwd geodetic transform ({} iter)'.format(it))
        spec_lon, spec_lat, _ = geo_id.fwd(obs_lon, obs_lat, sat_azimuth,
                                           (obs_alt - spec_dem) / np.tan(np.deg2rad(sat_alt)))

        # logger.debug('Performing DEM lookup ({} iter)'.format(it))
        spec_dem = dem_data.get_elevation(spec_lat, spec_lon)
        if not spec_dem:
            spec_dem = 0
        # print('iter{} -  lat:{} -  lon:{} -  dem:{}'.format(it, end_lat, end_lon, dem))

    return dict(specular_lat=spec_lat, specular_lon=spec_lon, specular_dem=spec_dem)


if __name__ == '__main__':
    print(spec_coordinates(43.5585024, 1.4712832, 151, 31.3671172897884, 142.857166594969))
