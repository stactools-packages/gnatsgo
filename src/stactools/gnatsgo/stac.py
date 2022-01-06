import logging
import os
from typing import List, Optional, Union

import pyarrow.parquet as pq
import rasterio
import stac_table
from pystac import (Asset, Collection, Extent, Item, MediaType, SpatialExtent,
                    TemporalExtent)
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import RasterBand, RasterExtension
from shapely.geometry import box, mapping
from stactools.core.io import ReadHrefModifier

from stactools.gnatsgo.constants import (GNATSGO_DATETIME, GNATSGO_DESCRIPTION,
                                         GNATSGO_EXTENTS, GNATSGO_LINKS,
                                         GNATSGO_PROVIDERS, TABLES)
from stactools.gnatsgo.utils import bounds_to_geojson, overall_bbox

logger = logging.getLogger(__name__)


def create_collection(parquet_path: str) -> Collection:
    """Create a STAC Collection

    This function includes logic to extract all relevant metadata from
    an asset describing the STAC collection and/or metadata coded into an
    accompanying constants.py file.

    See `Collection<https://pystac.readthedocs.io/en/latest/api.html#collection>`_.

    parquet_path is a base path where the parquet tables are stored.
                 each will be parsed for the table description.
    Returns:
        Collection: STAC Collection object
    """

    extent = Extent(
        SpatialExtent(GNATSGO_EXTENTS),
        TemporalExtent([GNATSGO_DATETIME, None]),
    )

    collection = Collection(id="gnatsgo",
                            title="The gNATSGO Soil Database",
                            description=GNATSGO_DESCRIPTION,
                            license="proprietary",
                            providers=GNATSGO_PROVIDERS,
                            extent=extent)
    collection.stac_extensions.append(stac_table.SCHEMA_URI)
    collection.keywords = [
        "Soils",
        "SSURGO",
        "USDA",
    ]
    table_tables = []
    for table_name in TABLES.keys():
        print(table_name)
        filters = None
        if TABLES[table_name].get('partition', False):  # type: ignore
            # just read one small state
            filters = [('state', '=', 'NH')]
        t = pq.read_table(os.path.join(parquet_path, f"{table_name}.parquet"),
                          filters=filters)
        table_tables.append({
            "name":
            table_name,
            "description":
            t.schema.metadata[b'description'].decode(),
        })

    collection.extra_fields["table:tables"] = table_tables
    collection.links = GNATSGO_LINKS

    collection.validate()
    return collection


def create_item(asset_hrefs: Union[str, List[str]],
                read_href_modifier: Optional[ReadHrefModifier] = None) -> Item:
    """Create a STAC Item from either a parquet file, or aa tile of gNATSGO/gSSURGO data."""
    if isinstance(asset_hrefs, str):
        asset_hrefs = [asset_hrefs]
    if read_href_modifier:
        modified_hrefs = [read_href_modifier(href) for href in asset_hrefs]
    else:
        modified_hrefs = asset_hrefs

    item_id, extension = os.path.splitext(os.path.basename(modified_hrefs[0]))

    if extension == '.parquet':
        if len(modified_hrefs) > 1:
            raise ValueError('item should contain only one parquet table')
        return _create_item_from_parquet(item_id, modified_hrefs[0])
    else:
        prod, item_id = item_id.split('_', 1)
        return _create_item_from_tile(item_id, modified_hrefs)


def _create_item_from_parquet(table_name: str, asset_href: str) -> Item:
    bbox = overall_bbox()
    geometry = mapping(box(*bbox))

    item = Item(id=table_name,
                bbox=bbox,
                geometry=geometry,
                datetime=GNATSGO_DATETIME,
                properties={})

    # don't do the validate here, because metadata is in byte strings, which angers json
    item = stac_table.generate(asset_href,
                               item,
                               proj=False,
                               count_rows=False,
                               validate=False)

    item.properties['table:columns'] = [
        tc for tc in item.properties['table:columns']
        if not tc['name'].startswith('__')
    ]

    for col in item.properties['table:columns']:
        meta = col.pop('metadata', False)
        if meta and meta.get(b'description', False):
            col['description'] = meta[b'description'].decode()

    item.validate()
    return item


def _create_item_from_tile(tile_id, asset_hrefs) -> Item:
    with rasterio.open(asset_hrefs[0]) as dataset:
        epsg = dataset.crs.to_epsg()
        wkt = dataset.crs.wkt
        bbox = list(dataset.bounds)
        geometry = mapping(box(*bbox))
        transform = dataset.transform
        shape = dataset.shape

    transformed_bbox, transformed_geom = bounds_to_geojson(bbox, dataset.crs)
    item = Item(id=tile_id,
                geometry=transformed_geom,
                bbox=transformed_bbox,
                datetime=GNATSGO_DATETIME,
                properties={},
                stac_extensions=[])

    item.add_links(GNATSGO_LINKS)
    item.common_metadata.gsd = 10
    item.common_metadata.providers = GNATSGO_PROVIDERS
    item.common_metadata.license = "proprietary"

    projection = ProjectionExtension.ext(item, add_if_missing=True)
    projection.epsg = epsg
    projection.wkt2 = wkt
    projection.transform = transform[0:6]
    projection.shape = shape
    projection.geometry = geometry
    projection.bbox = bbox

    # Create data assets
    for href in sorted(asset_hrefs):
        title, junk = os.path.basename(href).split('_', 1)
        data_asset = Asset(href=href,
                           media_type=MediaType.COG,
                           roles=["data"],
                           title=title)
        item.add_asset(title, data_asset)

        rb = []
        with rasterio.open(href) as dataset:
            for i in range(len(dataset.indexes)):
                # nodata = dataset.get_nodatavals()[i]
                # dtype = dataset.dtypes[i]
                rb.append(
                    RasterBand.create(nodata=dataset.get_nodatavals()[i],
                                      data_type=dataset.dtypes[i],
                                      spatial_resolution=10))
        rast_ext = RasterExtension.ext(data_asset, add_if_missing=True)
        rast_ext.bands = rb

    item.validate()
    return item
