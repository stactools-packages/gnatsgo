[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/stactools-packages/gnatsgo/main?filepath=docs/installation_and_basic_usage.ipynb)

# stactools-gnatsgo

- Name: gnatsgo
- Package: `stactools.gnatsgo`
- PyPI: https://pypi.org/project/stactools-gnatsgo/
- Owner: @justinfisk
- Dataset homepage: https://www.nrcs.usda.gov/wps/portal/nrcs/detail/soils/survey/geo/?cid=nrcseprd1464625
- STAC extensions used:
  - [proj](https://github.com/stac-extensions/projection)
  - [raster](https://github.com/stac-extensions/raster)
  - [table](https://github.com/stac-extensions/table)

Package to assist with conversion of gNATSGO data to cloud-optimized formats,
and creation of associated STAC metadata.

## Examples

### STAC objects

- [Collection](examples/collection.json)
- [Raster Item](examples/conus_101445_1580705_265285_1416865.json)
- [Table Item](examples/chorizon.json)

### Command-line usage

This package expects that you have downloaded and unpacked gNATSGO and gSSURGO
state, territory, and CONUS geodatabases into a common directory, and have
extracted the 10m map-unit-key raster from each state and territory geodatabase,
and stored as a geotiff with the same base name, e.g. `gNATSGO_AR.gdb` and
`gNATSGO_AR.tif`. For the following examples, it is assumed that these were
unpacked into `data/inputs` and the converted assets will be stored in
`data/outputs/tables` and `data/outputs/tiles`.

Combine tabular data across geodatabases and convert to parquet:

```bash
$ stac gnatsgo to-parquet data/inputs data/outputs/tables
```

Convert the state and territory rasters to tiled COGs:

```bash
$ stac gnatsgo tile data/inputs data/outputs/tiles
```

Create additional derived rasters for commonly mapped values provided in the
`gSSURGO` `valu1` table using the parquet tables and tiled COGs created above::

```bash
$ stac gnatsgo create-derived-rasters data/outputs/tables/valu1.parquet data/outputs/tiles/conus_*/mukey_conus_*.tif
```

Create STAC collection including collection-level `table` metadata:

```bash
$ stac gnatsgo create-collection examples/collection.json data/inputs
```

Create a STAC item from assets. This will accept either a single table's
parquet file (with a `.parquet` extension), or a list of raster assets for a given tile:

```bash
$ stac gnatsgo create-item examples/chorizon.json data/outputs/tables/chorizon.parquet
```
or
```bash
$ stac gnatsgo create-item examples/conus_101445_1580705_265285_1416865.json data/outputs/tiles/conus_101445_1580705_265285_1416865/*.tif
```

Use `stac gnatsgo --help` to see all subcommands and options.
