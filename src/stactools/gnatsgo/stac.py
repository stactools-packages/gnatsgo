import logging
import os
from typing import Dict, List, Optional, Union

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
    """Create gnatsgo STAC Collection

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
        logger.info(table_name)
        s = pq.read_schema(
            os.path.join(parquet_path, f"{table_name}.parquet",
                         '_common_metadata'))
        table_tables.append({
            "name": table_name,
            "description": s.metadata[b'description'].decode(),
        })

    collection.extra_fields["table:tables"] = table_tables
    collection.links = GNATSGO_LINKS

    collection.validate()
    return collection


def create_item(asset_hrefs: Union[str, List[str]],
                read_href_modifier: Optional[ReadHrefModifier] = None,
                storage_options: Optional[Dict] = None) -> Item:
    """Create a STAC Item from either a parquet file, or aa tile of gNATSGO/gSSURGO data."""
    if isinstance(asset_hrefs, str):
        asset_hrefs = [asset_hrefs]
    item_id, extension = os.path.splitext(os.path.basename(asset_hrefs[0]))

    if extension == '.parquet':
        if len(asset_hrefs) > 1:
            raise ValueError('item should contain only one parquet table')
        return _create_item_from_parquet(item_id, asset_hrefs[0],
                                         storage_options)
    else:
        _, item_id = item_id.split('_', 1)
        return _create_item_from_tile(item_id, asset_hrefs, read_href_modifier)


def _create_item_from_parquet(table_name: str,
                              asset_href: str,
                              storage_options: Optional[Dict] = None) -> Item:

    bbox = overall_bbox()
    geometry = mapping(box(*bbox))

    item = Item(id=table_name,
                bbox=bbox,
                geometry=geometry,
                datetime=GNATSGO_DATETIME,
                properties={})

    if storage_options:
        cleaned_options = storage_options.copy()
        cleaned_options.pop('credential', None)
        asset_extra_fields = {"table:storage_options": cleaned_options}
    else:
        asset_extra_fields = None  # type: ignore

    # don't do the validate here, because metadata is in byte strings, which angers json
    item = stac_table.generate(asset_href,
                               item,
                               storage_options=storage_options,
                               asset_extra_fields=asset_extra_fields,
                               proj=False,
                               count_rows=False,
                               validate=False)

    item.assets['data'].href = asset_href
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


def _create_item_from_tile(
        tile_id: str,
        asset_hrefs: List[str],
        read_href_modifier: Optional[ReadHrefModifier] = None) -> Item:
    if read_href_modifier:
        modified_hrefs = [read_href_modifier(href) for href in asset_hrefs]
    else:
        modified_hrefs = asset_hrefs

    with rasterio.open(modified_hrefs[0]) as dataset:
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

    projection = ProjectionExtension.ext(item, add_if_missing=True)
    projection.epsg = epsg
    projection.wkt2 = wkt
    projection.transform = transform[0:6]
    projection.shape = shape
    projection.geometry = geometry
    projection.bbox = bbox

    # Create data assets
    for i, href in enumerate(asset_hrefs):
        title, _ = os.path.basename(href).split('_', 1)
        title = title.replace('-', '_')
        data_asset = Asset(href=href,
                           media_type=MediaType.COG,
                           roles=["data"],
                           title=title)

        item.add_asset(title, data_asset)
        rb = []
        with rasterio.open(modified_hrefs[i]) as dataset:
            if title == 'mukey':
                data_asset.description = "Map unit key is the unique identifier of a record in the Mapunit table."  # noqa
            else:
                data_asset.description = dataset.descriptions[0]
            rb.append(
                RasterBand.create(nodata=dataset.nodatavals[0],
                                  data_type=dataset.dtypes[0],
                                  spatial_resolution=10))
        rast_ext = RasterExtension.ext(data_asset, add_if_missing=True)
        rast_ext.bands = rb

    item.validate()
    return item
