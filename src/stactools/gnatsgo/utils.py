import logging
import os.path
import tempfile

import dask.dataframe as dd
import geopandas as gpd
import numpy as np
import pandas as pd
import pyarrow
import rasterio
from osgeo import gdal, ogr
from pandas import CategoricalDtype, StringDtype
from pyproj import CRS
from pyproj.transformer import Transformer
from rasterio.windows import from_bounds
from shapely.geometry import box, mapping
from stactools.core.utils.convert import cogify

from stactools.gnatsgo.constants import (DEFAULT_TILE_SIZE, GNATSGO_EXTENTS,
                                         PRODUCT, TABLES, VALU1_DESCRIPTIONS)

logger = logging.getLogger(__name__)


class Table:

    def __init__(self, table_name, in_dir, description=None, has_geom=False):
        self.table_name = table_name
        self.description = description
        self.has_geom = has_geom
        self.ssurgo_only = TABLES.get(table_name, {}).get('ssurgo_only', False)
        self.partition = TABLES.get(table_name, {}).get('partition', False)
        self.in_dir = in_dir
        self._file_list()
        self._table_def()
        self.schema = None

    def _file_list(self):
        self.files = {}

        def _add_files(prod, reglist):
            self.files.update({
                reg: os.path.join(self.in_dir, f"{prod}_{reg}.gdb")
                for reg in reglist
            })

        if self.ssurgo_only:
            # get everything from gSSURGO
            if self.partition:  # get all the individual CONUS states
                _add_files(
                    'gSSURGO',
                    PRODUCT['gNATSGO']['CONUS'] + PRODUCT['gSSURGO']['CONUS'])
            else:  # just use the CONUS gdb
                _add_files('gSSURGO', ['CONUS'])
            _add_files(
                'gSSURGO', PRODUCT['gNATSGO']['NON_CONUS'] +
                PRODUCT['gSSURGO']['NON_CONUS'])
        else:
            # use gNATSGO where available, and gSSURGO
            # everywhere else
            if self.partition:
                for prod in PRODUCT:
                    _add_files(prod, PRODUCT[prod]['CONUS'])
            else:
                _add_files('gNATSGO', ['CONUS'])
            for prod in PRODUCT:
                _add_files(prod, PRODUCT[prod]['NON_CONUS'])

    def _table_def(self):
        # get any speficified conversions from constants
        self.astype = TABLES.get(self.table_name, {}).get('astype', {})
        if self.partition:
            # we will partition by state by adding a 'state' column
            # set up a categorical type for the column
            all_states = []
            for prod in PRODUCT:
                all_states += PRODUCT[prod]['CONUS']
                all_states += PRODUCT[prod]['NON_CONUS']
            self.astype['state'] = CategoricalDtype(all_states)

        # inspect gdb for column types that should be converted
        # hope that the first gdb is representative
        gdbfile = self.files['AK']
        # grab the metadata table that describes the columns
        column_meta = gpd.read_file(gdbfile,
                                    driver='OpenFileGDB',
                                    layer='mdstattabcols',
                                    ignore_geometry=True)
        column_meta = column_meta[column_meta.tabphyname == self.table_name]
        # grab the metadata table that describes the categorical types
        choices = gpd.read_file(gdbfile,
                                driver='OpenFileGDB',
                                layer='mdstatdomdet',
                                ignore_geometry=True)

        # also open the gdb to inspect field definitions
        driver = ogr.GetDriverByName('OpenFileGDB')
        f = driver.Open(gdbfile)
        ld = f.GetLayerByName(self.table_name).GetLayerDefn()

        self.columns = {}
        for i in range(ld.GetFieldCount()):
            col = ld.GetFieldDefn(i).GetName()
            self.columns[col] = {}

            self.columns[col]['meta'] = {}
            if self.table_name != 'valu1':  # valu1 is not in metadata tables
                # stash the column description and units for later use
                meta = column_meta[column_meta.colphyname == col].iloc[0]
                if meta.coldesc:
                    self.columns[col]['meta']['description'] = meta.coldesc
                if meta.uom:
                    self.columns[col]['meta']['units'] = meta.uom
            else:  # valu1
                # use column descriptions we extracted from pdf
                self.columns[col]['meta']['description'] = VALU1_DESCRIPTIONS[
                    col]

            if col not in self.astype:  # don't override things we specified
                if ld.GetFieldDefn(i).GetTypeName() == 'Integer':
                    if ld.GetFieldDefn(i).GetSubType() == 2:
                        self.astype[col] = 'Int16'
                    else:
                        self.astype[col] = 'Int32'
                elif ld.GetFieldDefn(i).GetTypeName() == 'Real':
                    self.astype[col] = 'float32'
                elif self.table_name != 'valu1':
                    # valu1 is not in metadata table, but luckily has only ints/floats
                    if meta.logicaldatatype == 'Choice':
                        # lookup possible categorical values and create type
                        cats = choices[choices.domainname ==
                                       meta.domainname].choice.values
                        if len(cats):
                            self.astype[col] = CategoricalDtype(cats)
                        else:
                            self.astype[col] = 'category'
                    else:
                        self.astype[col] = {
                            'Boolean': 'boolean',
                            'Date/Time': 'datetime64',
                            'String': StringDtype(),
                            'Vtext': StringDtype(),
                        }[meta.logicaldatatype]

    def _precompute_categoricals(self):
        """All partitions must use the same CategoricalDtype for a column.
        For any categorical column where categories aren't pre-defined, find
        all possible values across files and define CategoricalDtype..
        """
        categoricals = [
            k for k, v in self.astype.items()
            if v == 'category' and not isinstance(v, CategoricalDtype)
        ]
        if categoricals:
            ignores = list(set(self.columns.keys()) - set(categoricals))
            tmp = self.concat_table(ignore_fields=ignores)
            for c in categoricals:
                categories = list(tmp[c].unique())
                if None in categories:
                    categories.remove(None)
                self.astype[c] = CategoricalDtype(categories)

    def _schema(self, dataframe):
        """Inject column and table metadata (descriptions, units) into
        the parquet schema.
        """
        if self.schema is not None:  # only need to create once
            return self.schema

        self.schema = pyarrow.Schema.from_pandas(dataframe,
                                                 preserve_index=False)
        if self.description is not None:
            self.schema = self.schema.with_metadata(
                {'description': self.description})
        for col in self.schema.names:
            if not col.startswith('__'):
                i = self.schema.get_field_index(col)
                if self.columns.get(col, {}).get('meta', False):
                    field = self.schema.field(i).with_metadata(
                        self.columns[col]['meta'])
                    self.schema = self.schema.set(i, field)

        return self.schema

    def concat_table(self, ignore_fields=None, out_dir=None):
        """Combine state or regional geodatabases for a given table_name.

        If out_dir is specified, resulting table will be written to parquet.
        Otherwise, a geopandas dataframe is returned.
        """
        if self.partition and out_dir:
            self._precompute_categoricals()

        t = None
        for reg in self.files:
            logger.info(self.files[reg])
            tt = gpd.read_file(self.files[reg],
                               driver='OpenFileGDB',
                               layer=self.table_name,
                               ignore_geometry=(not self.has_geom),
                               ignore_fields=ignore_fields)
            for col in [
                    k for k, v in self.astype.items()
                    if v == 'boolean' and k in tt.columns
            ]:
                # boolean columns are a mess of 1-3 character strings.
                # convert to something sensible.
                tt[col] = tt[col].map({
                    'Yes': True,
                    'No ': False,
                    'No': False,
                    '1  ': True,
                    '0  ': False
                })
            if out_dir and self.partition:
                # convert types, add the 'state' column for the partition,
                # and write parquet file for this partition
                tt['state'] = reg
                tt = tt.astype(self.astype)
                tt.info(memory_usage="deep")
                ddtt = dd.from_pandas(tt, npartitions=1)
                ddtt.to_parquet(os.path.join(out_dir,
                                             f"{self.table_name}.parquet"),
                                partition_on=['state'],
                                schema=self._schema(tt),
                                engine='pyarrow',
                                compression='snappy')
            else:
                t = tt if t is None else t.append(tt)

        if out_dir and not self.partition:
            # convert types and write single parquet file
            t = t.astype(self.astype)
            t.info(memory_usage="deep")
            ddt = dd.from_pandas(t, npartitions=1)
            ddt.to_parquet(os.path.join(out_dir, f"{self.table_name}.parquet"),
                           schema=self._schema(t),
                           engine='pyarrow',
                           compression='snappy')
        if not out_dir:
            return t


def to_parquet(in_dir, out_dir, tables=None):
    mdstattabs = gpd.read_file(os.path.join(in_dir, 'gSSURGO_CONUS.gdb'),
                               driver='OpenFileGDB',
                               layer='mdstattabs')
    if not tables:
        # do 'em all
        tables = TABLES.keys()
    for table_name in tables:
        logger.info(table_name)
        logger.info("  concatting table")
        desc = None
        if table_name != 'valu1':  # valu1 is not in metadata tables
            descriptions = mdstattabs[mdstattabs.tabphyname ==
                                      table_name].tabdesc
            if len(descriptions) and descriptions.item():
                desc = descriptions.item()
        else:
            desc = VALU1_DESCRIPTIONS['table']

        t = Table(table_name, in_dir, description=desc)
        t.concat_table(out_dir=out_dir)


def overall_bbox():
    min_lon = 180
    min_lat = 90
    max_lon = -180
    max_lat = -90
    for bbox in GNATSGO_EXTENTS:
        if bbox[0] < min_lon:
            min_lon = bbox[0]
        if bbox[1] < min_lat:
            min_lat = bbox[1]
        if bbox[2] > max_lon:
            max_lon = bbox[2]
        if bbox[3] > max_lat:
            max_lat = bbox[3]
    return [min_lon, min_lat, max_lon, max_lat]


def bounds_to_geojson(bbox: list, in_crs: int) -> tuple:
    transformer = Transformer.from_crs(in_crs,
                                       CRS.from_epsg(4326),
                                       always_xy=True)
    transformed_bbox = list(transformer.transform_bounds(*bbox))
    return transformed_bbox, mapping(box(*transformed_bbox, ccw=True))


def tile(in_dir, out_dir, size=DEFAULT_TILE_SIZE):
    """Mosiacs state rasters and tile to a grid"""
    for prod in PRODUCT:
        for state in PRODUCT[prod]['NON_CONUS']:
            logger.info(state)
            tile_image(os.path.join(in_dir, f"{prod}_{state}.tif"), out_dir,
                       size, state.lower())
    with tempfile.TemporaryDirectory() as tmpdir:
        vrt_file = os.path.join(tmpdir, 'mukey.vrt')
        create_conus_vrt(in_dir, vrt_file)
        tile_image(vrt_file, out_dir, size, "conus")


def tile_image(infile, outdir, size, basename=None):
    with rasterio.open(infile) as dataset:
        tiles = create_tiles(*dataset.bounds, size)
        for tile in tiles:
            td = dataset.read(1,
                              window=from_bounds(tile._left, tile._bottom,
                                                 tile._right, tile._top,
                                                 dataset.transform))
            if not np.all(td == dataset.nodata):
                tile.subset(infile, outdir, basename)
            else:
                logger.warn("   no data -- skipping")


def create_conus_vrt(in_dir, outfile):
    file_list = []
    for prod in PRODUCT:
        file_list += [
            os.path.join(in_dir, f"{prod}_{state}.tif")
            for state in PRODUCT[prod]['CONUS']
        ]
    gdal.BuildVRT(outfile, file_list)


def create_tiles(left, bottom, right, top, size):
    x = left
    y = bottom
    tiles = []
    while x < right:
        while y < top:
            tile = Tile(x, y, min(x + size, right), min(y + size, top))
            tiles.append(tile)
            y += size
        x += size
        y = bottom
    return tiles


class Tile:

    def __init__(self, left, bottom, right, top):
        self._left = left
        self._bottom = bottom
        self._right = right
        self._top = top

    def subset(self, infile, outdir, base):
        tile_id = (f"{base}_{str(int(self._left))}_{str(int(self._top))}_"
                   f"{str(int(self._right))}_{str(int(self._bottom))}")
        os.makedirs(os.path.join(outdir, tile_id), exist_ok=True)
        outfile = os.path.join(outdir, tile_id, f"mukey_{tile_id}.tif")
        extra_args = [
            "-co", "RESAMPLING=NEAREST", "-projwin",
            str(self._left),
            str(self._top),
            str(self._right),
            str(self._bottom)
        ]
        return cogify(infile, outfile, extra_args=extra_args)


def create_derived_rasters(parquet_table,
                           mukey_files,
                           destination=None,
                           parquet_storage_options=None):
    logger.info("reading parquet table")
    valu1 = pd.read_parquet(
        parquet_table,
        engine='pyarrow',
        storage_options=parquet_storage_options).set_index('mukey')

    cogs_produced = []
    for mukey_file in mukey_files:
        if '?' in mukey_file:
            mf_tmp, _ = mukey_file.split('?', 1)
        else:
            mf_tmp = mukey_file
        in_dir, file_name = os.path.split(mf_tmp)
        logger.info("processing %s", file_name)

        _, suffix = file_name.split("_", 1)
        out_dir = destination if destination is not None else in_dir

        with rasterio.open(mukey_file) as f:
            profile = f.profile
            profile.update(driver='COG')

            mukey = f.read(1)
            unique_mukeys, inverse = np.unique(mukey, return_inverse=True)
            logger.info("  unique mukeys: %d", len(unique_mukeys))

            for col in valu1.columns:
                if col == 'mukey':
                    continue
                logger.info("  starting %s", col)
                if valu1[col].dtype.name == 'Int16':
                    valu1[col] = valu1[col].fillna(-9999).astype('int16')
                    profile.update(dtype=rasterio.int16,
                                   nodata=-9999,
                                   resampling='NEAREST')
                elif valu1[col].dtype.name == 'float32':
                    profile.update(dtype=rasterio.float32)
                else:
                    raise TypeError('unsupported type')
                out_file = os.path.join(out_dir,
                                        f"{col.replace('_', '-')}_{suffix}")

                d = (valu1[col].groupby(level=0).first().reindex(
                    unique_mukeys,
                    fill_value=profile['nodata']).to_numpy()[inverse].reshape(
                        mukey.shape))
                if valu1[col].dtype.name == 'float32':
                    d = np.nan_to_num(d, nan=profile['nodata'])
                if (d == profile['nodata']).all():
                    logger.info('no valid data -- skipping')
                    continue
                with rasterio.open(out_file, 'w', **profile) as dst:
                    dst.write_band(1, d.astype(profile['dtype']))
                    dst.set_band_description(1, VALU1_DESCRIPTIONS[col])
                logger.info('    finishd %s', col)
                cogs_produced.append(out_file)
    return cogs_produced
