import logging
from typing import List

import click

from stactools.gnatsgo import stac
from stactools.gnatsgo.constants import DEFAULT_TILE_SIZE
from stactools.gnatsgo.utils import create_value_ad_rasters, tile, to_parquet

logger = logging.getLogger(__name__)


def create_gnatsgo_command(cli):
    """Creates the stactools-gnatsgo command line utility."""

    @cli.group(
        "gnatsgo",
        short_help=("Commands for working with stactools-gnatsgo"),
    )
    def gnatsgo():
        pass

    @gnatsgo.command("to-parquet",
                     help="convert tables in incoming GDB files to parquet")
    @click.argument("gssurgo_dir")
    @click.argument("gnatsgo_dir")
    @click.argument("out_dir")
    @click.argument("tables", nargs=-1)
    def to_parquet_command(gssurgo_dir: str, gnatsgo_dir: str, out_dir: str,
                           tables: List[str]):
        """convert gNATSGO and gSSURGO tables from incoming GDB files to parquet

        Args:
            gssurgo_dir (str): directory containing gSSURGO CONUS and by-state GDBs
            gnatsgo_dir (str): directory containing gBATSGO CONUS and by-state GDBs
            out_dir (str): path to output dir
        """
        to_parquet(gssurgo_dir, gnatsgo_dir, out_dir, tables)

    @gnatsgo.command("tile", help="convert state/territory tifs to tiled")
    @click.argument("gnatsgo_dir")
    @click.argument("gssurgo_dir")
    @click.argument("out_dir")
    @click.option("-s", "--size", default=DEFAULT_TILE_SIZE)
    def tile_command(gnatsgo_dir, gssurgo_dir, out_dir, size):
        """Tiles the input files to a grid.
        The source gNATSGO data contain state-based 10m GeoTIFFS, so we tile.

        Args:
            gnatsgo_dir (str): directory containing state/territory gnatsgo mukey rasters
            gssurgo_dir (str): directory containing state/territory gssurgo mukey rasters
            out_dir (str): output directory
        """
        tile(gnatsgo_dir, gssurgo_dir, out_dir, size)

    @gnatsgo.command(
        "create-value-ad-rasters",
        help="create raster layers using the value-ad table provided by ssurgo"
    )
    @click.argument("gssurgo_gdb")
    @click.argument("mukey_files", nargs=-1)
    def value_ad_command(gssurgo_gdb: str, mukey_files: List[str]):
        """gSSURGO provides a "value ad" table with commonly calculated values
        for each map unit. Use this table and the mukey rasters to create COGs.

        Args:
            gssurgo_gdb (str): path to the gSSURGO CONUS geodatabase
            mukey_files (list): list of mukey rasters to process
        """
        create_value_ad_rasters(gssurgo_gdb, mukey_files)

    @gnatsgo.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.argument("destination")
    @click.argument("parquet_path")
    def create_collection_command(destination: str, parquet_path: str):
        """Creates a STAC Collection

        Args:
            parquet_path (str): A path to directory containing parquet tables
            destination (str): An HREF for the Collection JSON
        """
        collection = stac.create_collection(parquet_path)
        collection.set_self_href(destination)
        collection.save_object()
        return None

    @gnatsgo.command("create-item", short_help="Create a STAC item")
    @click.argument("destination")
    @click.argument("sources", nargs=-1)
    def create_item_command(destination: str, sources: List[str]):
        """Creates a STAC Item

        Args:
            sources (List[str]): HREFs of the Assets associated with the Item
            destination (str): An HREF for the STAC Collection
        """
        item = stac.create_item(sources)

        item.save_object(dest_href=destination)

        return None

    return gnatsgo
