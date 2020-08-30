'''
******************************************************************************************
Cut raster with shape

input --> shape (.shp) polygons of forest stands (Waldorte))
input --> raster (.tiff) raster file with hights of trees
input --> type of calculation Oberhoehe ('oh') or Vorrat ('v')
output --> tree hights (.csv) table with top hights (Oberhoehen) for all forest stands
******************************************************************************************
'''

import os
import numpy as np
import pandas as pd
import fiona
import rasterio
from rasterio.mask import mask

class GISOh(object):

    def __init__(self, shp_path):

        self.shp_path = shp_path


    def main(self, calc_type, raster_path, output_path = ""):

        self.raster_path = raster_path
        self.calc_type = calc_type

        # load shapefile with polygons
        with fiona.open(self.shp_path) as shapefile:
            polygons = [feature for feature in shapefile]

        # load raster with oh information
        raster = rasterio.open(self.raster_path)

        # compute oh
        hight = []
        for polygon in polygons:
            # compute oh for every polygon
            hight.append(self.func_compute_oh(polygon, raster))

        # convert to numpy array
        hight_np = np.asarray(hight)
        # convert to pandas DataFrame
        hight_df = pd.DataFrame(hight, columns=['wo', self.calc_type, 'area'])

        if not output_path == "":
            # write to csv
            hight_df.to_csv(output_path, index=False)

        return hight_df


    # compute oh
    def func_compute_oh(self, geom_all, raster):

        #wo = str(geom_all['properties']['REVIER_NR']) + str(geom_all['properties']['ABTEILUNG']) + geom_all['properties']['UNTERABTEI']
        wo = str(geom_all['properties']['ABTEILUNG']) + geom_all['properties']['UNTERABTEI']
        area = geom_all['properties']['GEOM_Area']
        geom = geom_all['geometry']

        # cutting the raster
        out_image, out_transform = mask(raster, [geom], crop=True)
        #out_meta = raster.meta.copy()

        # set -3.402823e+38 to nan
        out_image[out_image<-3.3e+38]=np.nan

        # flatten array
        flat = out_image.flatten()

        # delete nan
        flat = flat[~np.isnan(flat)]

        # set values under 0 to 0
        flat[flat < 0] = 0

        if flat.size > 0:
            if self.calc_type == 'oh':
                # calculate oh
                measure = np.percentile(flat, 90)
            if self.calc_type == 'v':
                # calculate v
                measure = np.mean(flat)
        else:
            measure = 0

        return wo, measure, area
