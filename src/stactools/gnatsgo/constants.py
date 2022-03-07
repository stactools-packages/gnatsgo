import datetime

from pystac import Link, Provider, ProviderRole

GNATSGO_DESCRIPTION = """
The gridded National Soil Survey Geographic Database (gNATSGO) is a USDA-NRCS Soil & Plant Science Division (SPSD) composite database that provides complete coverage of the best available soils information for all areas of the United States and Island Territories. It was created by combining data from the Soil Survey Geographic Database (SSURGO), State Soil Geographic Database (STATSGO2), and Raster Soil Survey Databases (RSS) into a single seamless ESRI file geodatabase.

SSURGO is the SPSD flagship soils database that has over 100 years of field-validated detailed soil mapping data. SSURGO contains soils information for more than 90 percent of the United States and island territories, but unmapped land remains. STATSGO2 is a general soil map that has soils data for all of the United States and island territories, but the data is not as detailed as the SSURGO data. The Raster Soil Surveys (RSSs) are the next generation soil survey databases developed using advanced digital soil mapping methods.

The gNATSGO database is composed primarily of SSURGO data, but STATSGO2 data was used to fill in the gaps. The RSSs are newer product with relatively limited spatial extent.  These RSSs were merged into the gNATSGO after combining the SSURGO and STATSGO2 data. The extent of RSS is expected to increase in the coming years.
"""  # noqa

GNATSGO_PROVIDERS = [
    Provider(
        "United States Department of Agriculture, Natural Resources Conservation Service",  # noqa
        roles=[
            ProviderRole.LICENSOR, ProviderRole.PRODUCER,
            ProviderRole.PROCESSOR, ProviderRole.HOST
        ],
        url=("https://www.nrcs.usda.gov/")),
]

GNATSGO_LINKS = [
    Link(
        "handbook",
        "https://www.nrcs.usda.gov/wps/PA_NRCSConsumption/download?cid=nrcs142p2_051847&ext=pdf",
        "application/pdf",
        "gSSURGO User Guide",
        extra_fields={"description": "Also includes data usage information"}),
]

GNATSGO_DATETIME = datetime.datetime(2020, 7, 1, tzinfo=datetime.timezone.utc)

GNATSGO_EXTENTS = [
    [-170.8513, -14.3799, -169.4152, -14.1432],  # AS
    [138.0315, 5.1160, 163.1902, 10.2773],  # FM
    [144.6126, 13.2327, 144.9658, 13.6572],  # GU
    [-159.7909, 18.8994, -154.7815, 22.2464],  # HI
    [170.9690, 6.0723, 171.9169, 8.71933],  # MH
    [145.0127, 14.1086, 145.9242, 18.8172],  # MP
    [130.8048, 2.9268, 134.9834, 8.0947],  # PW
    [157.3678, 49.0546, -117.2864, 71.4567],  # AK
    [-67.9506, 17.0140, -64.3973, 19.3206],  # PRUSVI
    [-127.8881, 22.8782, -65.2748, 51.6039],  # CONUS
]

# gNATSGO is only provided in states/territories where gSSURGO is gappy
PRODUCT = {
    'gNATSGO': {
        'CONUS': [
            'AR', 'AZ', 'CA', 'CO', 'FL', 'GA', 'ID', 'KY', 'MI', 'MN', 'MS',
            'MT', 'ND', 'NH', 'NM', 'NV', 'NY', 'OK', 'OR', 'TN', 'TX', 'UT',
            'VA', 'VT', 'WA', 'WY'
        ],
        'NON_CONUS': ['AK', 'PRUSVI'],
    },
    'gSSURGO': {
        'CONUS': [
            'AL', 'CT', 'DC', 'DE', 'IA', 'IL', 'IN', 'KS', 'LA', 'MA', 'MD',
            'ME', 'MO', 'NC', 'NE', 'NJ', 'OH', 'PA', 'RI', 'SC', 'SD', 'WI',
            'WV'
        ],
        'NON_CONUS': ['AS', 'FM', 'GU', 'HI', 'MH', 'MP', 'PW'],
    },
}

CONUS = {
    'gSSURGO': [
        'AL', 'CT', 'DC', 'DE', 'IA', 'IL', 'IN', 'KS', 'LA', 'MA', 'MD', 'ME',
        'MO', 'NC', 'NE', 'NJ', 'OH', 'PA', 'RI', 'SC', 'SD', 'WI', 'WV'
    ],
    'gNATSGO': [
        'AR', 'AZ', 'CA', 'CO', 'FL', 'GA', 'ID', 'KY', 'MI', 'MN', 'MS', 'MT',
        'ND', 'NH', 'NM', 'NV', 'NY', 'OK', 'OR', 'TN', 'TX', 'UT', 'VA', 'VT',
        'WA', 'WY'
    ],
}

NON_CONUS = {
    'gSSURGO': ['AS', 'FM', 'GU', 'HI', 'MH', 'MP', 'PW'],
    'gNATSGO': ['AK', 'PRUSVI'],
}

DEFAULT_TILE_SIZE = 163840

TABLES = {
    'chaashto': {},
    'chconsistence': {},
    'chdesgnsuffix': {},
    'chfrags': {},
    'chorizon': {
        'partition': True,
        'astype': {
            'hzname': 'category'
        },
    },
    'chpores': {},
    'chstruct': {},
    'chstructgrp': {},
    'chtext': {
        'astype': {
            'textcat': 'category',
            'textsubcat': 'category',
        },
    },
    'chtexture': {},
    'chtexturegrp': {
        'astype': {
            'texture': 'category',
            'texdesc': 'category',
        },
    },
    'chtexturemod': {},
    'chunified': {},
    'cocanopycover': {},
    'cocropyld': {},
    'codiagfeatures': {},
    'coecoclass': {
        'astype': {
            'ecoclasstypename': 'category',
            'ecoclassref': 'category',
        },
    },
    'coeplants': {
        'astype': {
            'plantsym': 'category',
            'plantsciname': 'category',
            'plantcomname': 'category',
        },
    },
    'coerosionacc': {},
    'coforprod': {},
    'coforprodo': {},
    'cogeomordesc': {
        'astype': {
            'geomftname': 'category',
            'geomfname': 'category',
            'geomfmod': 'category',
        },
    },
    'cohydriccriteria': {},
    'cointerp': {
        'partition': True,
        'astype': {
            'mrulename': 'category',
            'rulename': 'category',
            'interphrc': 'category',
        },
    },
    'comonth': {
        'partition': True,
    },
    'component': {
        'boolean': ['majcompflag'],
        'astype': {
            'mukey': int
        },
    },
    'copm': {},
    'copmgrp': {},
    'copwindbreak': {
        'astype': {
            'plantsym': 'category',
            'plantsciname': 'category',
            'plantcomname': 'category',
        },
    },
    'corestrictions': {},
    'cosoilmoist': {},
    'cosoiltemp': {},
    'cosurffrags': {},
    'cosurfmorphgc': {},
    'cosurfmorphhpp': {},
    'cosurfmorphmr': {},
    'cosurfmorphss': {},
    'cotaxfmmin': {},
    'cotaxmoistcl': {},
    'cotext': {
        'astype': {
            'textcat': 'category',
            'textsubcat': 'category',
        },
    },
    'cotreestomng': {
        'astype': {
            'plantsym': 'category',
            'plantsciname': 'category',
            'plantcomname': 'category',
        },
    },
    'cotxfmother': {},
    'distinterpmd': {
        'partition': True,
    },
    'distlegendmd': {},
    'distmd': {},
    'laoverlap': {},
    'legend': {},
    'legendtext': {},
    'mapunit': {
        'astype': {
            'mukey': int
        },
    },
    'muaggatt': {
        'astype': {
            'mukey': int
        },
    },
    'muaoverlap': {
        'astype': {
            'mukey': int
        },
    },
    'mucropyld': {
        'astype': {
            'mukey': int
        },
    },
    'mutext': {
        'astype': {
            'mukey': int
        },
    },
    'sacatalog': {},
    'sainterp': {
        'partition': True,
    },
    'valu1': {
        'ssurgo_only': True,
        'astype': {
            'mukey': int
        },
    },
}

VALU1_DESCRIPTIONS = {
    "table":
    "Included with the gSSURGO database, but not a part of the standard SSURGO dataset is a table called Valu1. This table contains 57 pre-summarized or “ready to map” attributes derived from the official SSURGO database. These attribute data are pre-summarized to the map unit level using best-practice generalization methods intended to meet the needs of most users. The generalization methods include map unit component weighted averages and percent of the map unit meeting a given criteria. These themes were prepared to better meet the mapping needs of users of soil survey information and can be used with both SSURGO and gridded SSURGO (gSSURGO) datasets.",  # noqa
    "aws0_5":
    "Available water storage estimate (AWS) in a standard zone 1 (0-5 cm depth), expressed in mm. The volume of plant available water that the soil can store in this layer based on all map unit components (weighted average). NULL values are presented where data are incomplete or not available.",  # noqa
    "aws5_20":
    "Available water storage estimate (AWS) in standard layer 2 (5-20 cm depth), expressed in mm. The volume of plant available water that the soil can store in this layer based on all map unit components (weighted average). NULL values are presented where data are incomplete or not available.",  # noqa
    "aws20_50":
    "Available water storage estimate (AWS) in standard layer 3 (20-50 cm depth), expressed in mm. The volume of plant available water that the soil can store in this layer based on all map unit components (weighted average). NULL values are presented where data are incomplete or not available.",  # noqa
    "aws50_100":
    "Available water storage estimate (AWS) in standard layer 3 (50-100 cm depth), expressed in mm. The volume of plant available water that the soil can store in this layer based on all map unit components (weighted average). NULL values are presented where data are incomplete or not available.",  # noqa
    "aws100_150":
    "Available water storage estimate (AWS) in standard layer 5 (100-150 cm depth), expressed in mm. The volume of plant available water that the soil can store in this layer based on all map unit components (weighted average). NULL values are presented where data are incomplete or not available.",  # noqa
    "aws150_999":
    "Available water storage estimate (AWS) in standard layer 6 (150 cm to the reported depth of the soil profile), expressed in mm. The volume of plant available water that the soil can store in this layer based on all map unit components (weighted average). NULL values are presented where data are incomplete or not available.",  # noqa
    "aws0_20":
    "Available water storage estimate (AWS) in standard zone 2 (0-20 cm depth), expressed in mm. The volume of plant available water that the soil can store in this zone based on all map unit components (weighted average). NULL values are presented where data are incomplete or not available.",  # noqa
    "aws0_30":
    "Available water storage estimate (AWS) in standard zone 3 (0-30 cm depth), expressed in mm. The volume of plant available water that the soil can store in this zone based on all map unit components (weighted average). NULL values are presented where data are incomplete or not available.",  # noqa
    "aws0_100":
    "Available water storage estimate (AWS) in standard zone 4 (0-100 cm depth), expressed in mm. The volume of plant available water that the soil can store in this zone based on all map unit components (weighted average). NULL values are presented where data are incomplete or not available.",  # noqa
    "aws0_150":
    "Available water storage estimate (AWS) in standard zone 5 (0-150 cm depth), expressed in mm. The volume of plant available water that the soil can store in this zone based on all map unit components (weighted average). NULL values are presented where data are incomplete or not available.",  # noqa
    "aws0_999":
    "Available water storage estimate (AWS) in total soil profile (0 cm to the reported depth of the soil profile), expressed in mm. The volume of plant available water that the soil can store in this layer based on all map unit components (weighted average). NULL values are presented where data are incomplete or not available.",  # noqa
    "tk0_5a":
    "Thickness of soil components used in standard layer 1 or standard zone 1 (0-5 cm) expressed in cm (weighted average) for the available water storage calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk5_20a":
    "Thickness of soil components used in standard layer 2 (5-20 cm) expressed in cm (weighted average) for the available water storage calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk20_50a":
    "Thickness of soil components used in standard layer 3 (20-50 cm) expressed in cm (weighted average) for the available water storage calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk50_100a":
    "Thickness of soil components used in standard layer 4 (50-100 cm) expressed in cm (weighted average) for the available water storage calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk100_150a":
    "Thickness of soil components used in standard layer 5 (100-150 cm) expressed in cm (weighted average) for the available water storage calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk150_999a":
    "Thickness of soil components used in standard layer 6 (150 cm to the reported depth of the soil profile) expressed in cm (weighted average) for the available water storage calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk0_20a":
    "Thickness of soil components used in standard zone 2 (0-20 cm) expressed in cm (weighted average) for the available water storage calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk0_30a":
    "Thickness of soil components used in standard zone 3 (0-30 cm) expressed in cm (weighted average) for the available water storage calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk0_100a":
    "Thickness of soil components used in standard zone 4 (0-100 cm) expressed in cm (weighted average) for the available water storage calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk0_150a":
    "Thickness of soil components used in standard zone 5 (0-150 cm) expressed in cm (weighted average) for the available water storage calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk0_999a":
    "Thickness of soil components used in total soil profile (0 cm to the reported depth of the soil profile) expressed in cm (weighted average) for the available water storage calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "musumcpcta":
    "The sum of the comppct_r (SSURGO component table) values used in the available water storage calculation for the map unit. Useful metadata information. NULL values are presented where data are incomplete or not available.",  # noqa
    "soc0_5":
    "Soil organic carbon stock estimate (SOC) in standard layer 1 or standard zone 1 (0-5 cm depth). The concentration of organic carbon present in the soil expressed in grams C per square meter to a depth of 5 cm. NULL values are presented where data are incomplete or not available.",  # noqa
    "soc5_20":
    "Soil organic carbon stock estimate (SOC) in standard layer 2 (5-20 cm depth). The concentration of organic carbon present in the soil expressed in grams C per square meter for the 5-20 cm layer. NULL values are presented where data are incomplete or not available.",  # noqa
    "soc20_50":
    "Soil organic carbon stock estimate (SOC) in standard layer 3 (20-50 cm depth). The concentration of organic carbon present in the soil expressed in grams C per square meter for the 20-50 cm layer. NULL values are presented where data are incomplete or not available.",  # noqa
    "soc50_100":
    "Soil organic carbon stock estimate (SOC) in standard layer 4 (50-100 cm depth). The concentration of organic carbon present in the soil expressed in grams C per square meter for the 50-100 cm layer. NULL values are presented where data are incomplete or not available.",  # noqa
    "soc100_150":
    "Soil organic carbon stock estimate (SOC) in standard layer 5 (100-150 cm depth). The concentration of organic carbon present in the soil expressed in grams C per square meter for the 100-150 cm layer. NULL values are presented where data are incomplete or not available.",  # noqa
    "soc150_999":
    "Soil organic carbon stock estimate (SOC) in standard layer 6 (150 cm to the reported depth of the soil profile). The concentration of organic carbon present in the soil expressed in grams C per square meter for the 150 cm and greater depth layer. NULL values are presented where data are incomplete or not available.",  # noqa
    "soc0_20":
    "Soil organic carbon stock estimate (SOC) in standard zone 2 (0-20 cm depth). The concentration of organic carbon present in the soil expressed in grams C per square meter to a depth of 20 cm. NULL values are presented where data are incomplete or not available.",  # noqa
    "soc0_30":
    "Soil organic carbon stock estimate (SOC) in standard zone 3 (0-30 cm depth). The concentration of organic carbon present in the soil expressed in grams C per square meter to a depth of 30 cm. NULL values are presented where data are incomplete or not available.",  # noqa
    "soc0_100":
    "Soil organic carbon stock estimate (SOC) in standard zone 4 (0-100 cm depth). The concentration of organic carbon present in the soil expressed in grams C per square meter to a depth of 100 cm. NULL values are presented where data are incomplete or not available.",  # noqa
    "soc0_150":
    "Soil organic carbon stock estimate (SOC) in standard zone 5 (0-150 cm depth). The concentration of organic carbon present in the soil expressed in grams C per square meter to a depth of 150 cm. NULL values are presented where data are incomplete or not available.",  # noqa
    "soc0_999":
    "Soil organic carbon stock estimate (SOC) in total soil profile (0 cm to the reported depth of the soil profile). The concentration of organic carbon present in the soil expressed in grams C per square meter for the total reported soil profile depth. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk0_5s":
    "Thickness of soil components used in standard layer 1 or standard zone 1 (0-5 cm) expressed in cm (weighted average) for the Soil Organic Carbon calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk5_20s":
    "Thickness of soil components used in standard layer 2 (5-20 cm) expressed in cm (weighted average) for the Soil Organic Carbon calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk20_50s":
    "Thickness of soil components used in standard layer 3 (20-50 cm) expressed in cm (weighted average) for the Soil Organic Carbon calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk50_100s":
    "Thickness of soil components used in standard layer 4 (50-100 cm) expressed in cm (weighted average) for the Soil Organic Carbon calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk100_150s":
    "Thickness of soil components used in standard layer 5 (100-150 cm) expressed in cm (weighted average) for the Soil Organic Carbon calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk150_999s":
    "Thickness of soil components used in standard layer 6 (150 cm to the reported depth of the soil profile) expressed in cm (weighted average) for the Soil Organic Carbon calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk0_20s":
    "Thickness of soil components used in standard zone 2 (0-20 cm) expressed in cm (weighted average) for the Soil Organic Carbon calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk0_30s":
    "Thickness of soil components used in standard zone 3 (0-30 cm) expressed in cm (weighted average) for the Soil Organic Carbon calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk0_100s":
    "Thickness of soil components used in standard zone 4 (0-100 cm) expressed in cm (weighted average) for the Soil Organic Carbon calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk0_150s":
    "Thickness of soil components used in standard zone 5 (0-150 cm) expressed in cm (weighted average) for the Soil Organic Carbon calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "tk0_999s":
    "Thickness of soil components used in total soil profile (0 cm to the reported depth of the soil profile) expressed in cm (weighted average) for the Soil Organic Carbon calculation. NULL values are presented where data are incomplete or not available.",  # noqa
    "musumcpcts":
    "The sum of the comppct_r (SSURGO component table) values used in the soil organic carbon calculation for the map unit. Useful metadata information. NULL values are presented where data are incomplete or not available.",  # noqa
    "nccpi3corn":
    "National Commodity Crop Productivity Index for Corn (weighted average) for major earthy components. Values range from .01 (low productivity) to .99 (high productivity). Earthy components are those soil series or higher level taxa components that can support crop growth (Dobos et al., 2012). Major components are those soil components where the majorcompflag = 'Yes' (SSURGO component table). NULL values are presented where data are incomplete or not available.",  # noqa
    "nccpi3soy":
    "National Commodity Crop Productivity Index for Soybeans (weighted average) for major earthy components. Values range from .01 (low productivity) to .99 (high productivity). Earthy components are those soil series or higher level taxa components that can support crop growth (Dobos et al., 2012). Major components are those soil components where the majorcompflag = 'Yes' (SSURGO component table). NULL values are presented where data are incomplete or not available.",  # noqa
    "nccpi3cot":
    "National Commodity Crop Productivity Index for Cotton (weighted average) for major earthy components. Values range from .01 (low productivity) to .99 (high productivity). Earthy components are those soil series or higher level taxa components that can support crop growth (Dobos et al., 2012). Major components are those soil components where the majorcompflag = 'Yes' (SSURGO component table). NULL values are presented where data are incomplete or not available.",  # noqa
    "nccpi3sg":
    "National Commodity Crop Productivity Index for Small Grains (weighted average) for major earthy components. Values range from .01 (low productivity) to .99 (high productivity). Earthy components are those soil series or higher level taxa components that can support crop growth (Dobos et al., 2012). Major components are those soil components where the majorcompflag = 'Yes' (SSURGO component table). NULL values are presented where data are incomplete or not available.",  # noqa
    "nccpi3all":
    "National Commodity Crop Productivity Index that has the highest value among Corn and Soybeans, Small Grains, or Cotton (weighted average) for major earthy components. Values range from .01 (low productivity) to .99 (high productivity). Earthy components are those soil series or higher level taxa components that can support crop growth (Dobos et al., 2012). Major components are those soil components where the majorcompflag = 'Yes' (SSURGO component table). NULL values are presented where data are incomplete or not available.",  # noqa
    "pctearthmc":
    "The National Commodity Crop Productivity Index map unit percent earthy is the map unit summed comppct_r for major earthy components. Earthy components are those soil series or higher level taxa components that can support crop growth (Dobos et al., 2012). Major components are those soil components where the majorcompflag = 'Yes' (SSURGO component table). Useful metadata information. NULL values are presented where data are incomplete or not available.",  # noqa
    "rootznemc":
    "Root zone depth is the depth within the soil profile that commodity crop (cc) roots can effectively extract water and nutrients for growth. Root zone depth influences soil productivity significantly. Soil component horizon criteria for root-limiting depth include: presence of hard bedrock, soft bedrock, a fragipan, a duripan, sulfuric material, a dense layer, a layer having a pH of less than 3.5, or a layer having an electrical conductivity of more than 12 within the component soil profile. If no root-restricting zone is identified, a depth of 150 cm is used to approximate the root zone depth (Dobos et al., 2012). Root zone depth is computed for all map unit major earthy components (weighted average). Earthy components are those soil series or higher level taxa components that can support crop growth (Dobos et al., 2012). Major components are those soil components where the majorcompflag = 'Yes' (SSURGO component table). NULL values are presented where data are incomplete or not available.",  # noqa
    "rootznaws":
    "Root zone (commodity crop) available water storage estimate (RZAWS) , expressed in mm, is the volume of plant available water that the soil can store within the root zone based on all map unit earthy major components (weighted average). Earthy components are those soil series or higher level taxa components that can support crop growth (Dobos et al., 2012). Major components are those soil components where the majorcompflag = 'Yes' (SSURGO component table). NULL values are presented where data are incomplete or not available.",  # noqa
    "droughty":
    "zone for commodity crops that is less than or equal to 6 inches (152 mm) expressed as \"1\" for a drought vulnerable soil landscape map unit or \"0\" for a non-droughty soil landscape map unit or NULL for miscellaneous areas (includes water bodies) or where data were not available. It is computed as a weighted average for major earthy components. Earthy components are those soil series or higher level taxa components that can support crop growth (Dobos et al., 2012). Major components are those soil components where the majorcompflag = 'Yes'",  # noqa
    "pwsl1pomu":
    "Potential Wetland Soil Landscapes (PWSL) is expressed as the percentage of the map unit that meets the PWSL criteria. The hydric rating (soil component variable \u201chydricrating\u201d) is an indicator of wet soils. For version 1 (pwsl1), those soil components that meet the following criteria are tagged as PWSL and their comppct_r values are summed for each map unit. Soil components with hydricrating = 'YES' are considered PWSL. Soil components with hydricrating = \u201cNO\u201d are not PWSL. Soil components with hydricrating = 'UNRANKED' are tested using other attributes, and will be considered PWSL if any of the following conditions are met: drainagecl = 'Poorly drained' or 'Very poorly drained' or the localphase or the otherph data fields contain any of the phrases \"drained\" or \"undrained\" or \"channeled\" or \"protected\" or \"ponded\" or \"flooded\". If these criteria do not determine the PWSL for a component and hydricrating = 'UNRANKED', then the map unit will be classified as PWSL if the map unit name contains any of the phrases \"drained\" or \"undrained\" or \"channeled\" or \"protected\" or \"ponded\" or \"flooded\". For version 1 (pwsl1), waterbodies are identified as \"999\" when map unit names match a list of terms that identify water or intermittent water or map units have a sum of the comppct_r for \"Water\" that is 80% or greater. NULL values are presented where data are incomplete or not available.",  # noqa
    "musumcpct":
    "The sum of the comppct_r (SSURGO component table) values for all listed components in the map unit. Useful metadata information. NULL values are presented where data are incomplete or not available.",  # noqa
    "mukey":
    "Map unit key is the unique identifier of a record in the Mapunit table. Use this column to join the Component table to the Mapunit table and the valu1 table to the MapUnitRaster_10m raster map layer to map valu1 themes."  # noqa
}
