r"""Write the shapes of the map of the list, with DemandCast's code.

The map of the site colours each country and subdivision of the list by
its years of data. ``data/shapes.geojson`` holds their outlines, one
feature per line, each with the label of its entity: every country of
Natural Earth at 1:50m, under its code, and each subdivision of the
list, under its country code and subdivision code, as DemandCast draws
it, from Natural Earth or from the shapes of grid regions of DemandCast.
Grid regions without a shape in DemandCast are unions of regions of
Natural Earth, without the parts of some regions outside the grid,
which hand-drawn polygons mark. The outlines are simplified and rounded
to 0.01 degrees, enough for a map of the world.

The script runs in the environment of DemandCast, whose code finds the
shapes, from the folder ``demandcast`` of its repository::

    PYTHONPATH=. uv run --locked python \
        path/to/Awesome-Electricity-Demand/scripts/shapes.py

It lists the subdivisions of the list without a shape.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import cartopy.io.shapereader
import geopandas
import shapely
import utils.shapes

import registry

SHAPES_FILE = registry.DATA_DIR / registry.SHAPES_FILE
TOLERANCE = 0.05
GRID = 0.01
# Codes of Natural Earth that differ from those of the list.
COUNTRY_CODES = {"KOS": "XKX", "SDS": "SSD", "PSX": "PSE"}
# Subdivisions without a shape in DemandCast, as unions of regions of
# Natural Earth at 1:10m, by their ISO 3166-2 codes:
# - the markets of Australia smaller than their states: the South
#   West Interconnected System (SWIS), the Queensland (QLD1) and
#   South Australia (SA1) regions of the NEM, and the Darwin-Katherine
#   Interconnected System (DKIS);
# - the departments of Bolivia, which its layer at 1:50m does not have;
# - the national (SEN) and central (SIC) systems of Chile, without
#   Aysén, Magallanes and the medium systems of Los Lagos;
# - the national interconnected system (SIN) of Colombia, without the
#   departments of Amazonas, Guainía, Vaupés and Vichada, the islands
#   of San Andrés and the municipalities whose seats are off it;
# - the price areas of Denmark;
# - the northern interconnected grid (RIN) of Algeria, without Adrar,
#   Illizi, Tamanrasset, Tindouf, the south of Béchar, El Menia and
#   El Borma;
# - Peninsular Malaysia, without Sabah, Sarawak and Labuan;
# - the North and South Islands of New Zealand, without the Chatham and
#   outlying islands;
# - the grid of NTDC in Pakistan, without Gilgit-Baltistan, which has
#   no connection to it, and the area of K-Electric;
# - the systems of Peru: the central-north system (SICN) until 1999,
#   with the southern system (SEIN-2000) from 2000, and the national
#   system today (SEIN), without Loreto but Alto Amazonas, Atalaya
#   and Purús;
# - the grids of the Philippines, without the provinces on off-grid
#   islands (Basilan, Batanes, Catanduanes, Marinduque, Masbate,
#   Mindoro, Palawan, Romblon, Siquijor, Sulu and Tawi-Tawi), with the
#   five grids of the Visayas;
# - the interconnected power systems of Russia, whose regions SO UES
#   lists on the page of each system.
COMPOSITES = {
    "AUS-DKIS": "AU-NT",
    "AUS-QLD1": "AU-QLD",
    "AUS-SA1": "AU-SA",
    "AUS-SWIS": "AU-WA",
    "BOL-B": "BO-B",
    "BOL-C": "BO-C",
    "BOL-H": "BO-H",
    "BOL-L": "BO-L",
    "BOL-O": "BO-O",
    "BOL-P": "BO-P",
    "BOL-S": "BO-S",
    "BOL-T": "BO-T",
    "CHL-SEN": (
        "CL-AN CL-AP CL-AR CL-AT CL-BI CL-CO CL-LI CL-LL CL-LR CL-ML "
        "CL-NB CL-RM CL-TA CL-VS"
    ),
    "CHL-SIC": (
        "CL-AN CL-AR CL-AT CL-BI CL-CO CL-LI CL-LL CL-LR CL-ML CL-NB CL-RM "
        "CL-VS"
    ),
    "COL-SIN": (
        "CO-ANT CO-ARA CO-ATL CO-BOL CO-BOY CO-CAL CO-CAQ CO-CAS CO-CAU "
        "CO-CES CO-CHO CO-COR CO-CUN CO-GUV CO-HUI CO-LAG CO-MAG CO-MET "
        "CO-NAR CO-NSA CO-PUT CO-QUI CO-RIS CO-SAN CO-SUC CO-TOL CO-VAC"
    ),
    "DZA-RIN": (
        "DZ-02 DZ-03 DZ-04 DZ-05 DZ-06 DZ-07 DZ-08 DZ-09 DZ-10 DZ-12 "
        "DZ-13 DZ-14 DZ-15 DZ-16 DZ-17 DZ-18 DZ-19 DZ-20 DZ-21 DZ-22 "
        "DZ-23 DZ-24 DZ-25 DZ-26 DZ-27 DZ-28 DZ-29 DZ-30 DZ-31 DZ-32 "
        "DZ-34 DZ-35 DZ-36 DZ-38 DZ-39 DZ-40 DZ-41 DZ-42 DZ-43 DZ-44 "
        "DZ-45 DZ-46 DZ-47 DZ-48"
    ),
    "DNK-DK1": "DK-81 DK-82 DK-83",
    "DNK-DK2": "DK-84 DK-85",
    "MYS-PENINSULAR": (
        "MY-01 MY-02 MY-03 MY-04 MY-05 MY-06 MY-07 MY-08 MY-09 MY-10 "
        "MY-11 MY-14 MY-16"
    ),
    "NZL-NI": (
        "NZ-AUK NZ-BOP NZ-GIS NZ-HKB NZ-MWT NZ-NTL NZ-TKI NZ-WGN NZ-WKO"
    ),
    "NZL-SI": "NZ-CAN NZ-MBH NZ-NSN NZ-OTA NZ-STL NZ-TAS NZ-WTC",
    "PAK-NTDC": "PK-BA PK-IS PK-JK PK-KP PK-PB PK-SD PK-TA",
    "PER-SEIN": (
        "PE-AMA PE-ANC PE-APU PE-ARE PE-AYA PE-CAJ PE-CAL PE-CUS PE-HUC "
        "PE-HUV PE-ICA PE-JUN PE-LAL PE-LAM PE-LIM PE-LOR PE-MDD PE-MOQ "
        "PE-PAS PE-PIU PE-PUN PE-SAM PE-TAC PE-TUM PE-UCA"
    ),
    "PER-SEIN-2000": (
        "PE-ANC PE-APU PE-ARE PE-AYA PE-CAJ PE-CAL PE-CUS PE-HUC PE-HUV "
        "PE-ICA PE-JUN PE-LAL PE-LAM PE-LIM PE-MOQ PE-PAS PE-PIU PE-PUN "
        "PE-TAC PE-TUM"
    ),
    "PER-SICN": (
        "PE-ANC PE-AYA PE-CAJ PE-CAL PE-HUC PE-HUV PE-ICA PE-JUN PE-LAL "
        "PE-LAM PE-LIM PE-PAS PE-PIU PE-TUM"
    ),
    "PHL-BOHOL": "PH-BOH",
    "PHL-CEBU": "PH-CEB PH-LAP PH-MDE",
    "PHL-LEYTE-SAMAR": "PH-BIL PH-EAS PH-LEY PH-NSA PH-SLE PH-WSA",
    "PHL-LUZON": (
        "PH-ABR PH-ALB PH-APA PH-AUR PH-BAN PH-BEN PH-BTG PH-BUL PH-CAG "
        "PH-CAN PH-CAS PH-CAV PH-IFU PH-ILN PH-ILS PH-ISA PH-KAL PH-LAG "
        "PH-LUN PH-MNL PH-MOU PH-NUE PH-NUV PH-PAM PH-PAN PH-QUE PH-QUI "
        "PH-RIZ PH-SOR PH-TAR PH-ZMB"
    ),
    "PHL-MINDANAO": (
        "PH-AGN PH-AGS PH-BUK PH-CAM PH-COM PH-DAO PH-DAS PH-DAV PH-LAN "
        "PH-LAS PH-MAG PH-MSC PH-MSR PH-NCO PH-SAR PH-SCO PH-SUK PH-SUN "
        "PH-SUR PH-ZAN PH-ZAS PH-ZSI"
    ),
    "PHL-NEGROS": "PH-BCD PH-NEC PH-NER",
    "PHL-PANAY": "PH-AKL PH-ANT PH-CAP PH-GUI PH-ILI",
    "PHL-VISAYAS": (
        "PH-AKL PH-ANT PH-BCD PH-BIL PH-BOH PH-CAP PH-CEB PH-EAS PH-GUI "
        "PH-ILI PH-LAP PH-LEY PH-MDE PH-NEC PH-NER PH-NSA PH-SLE PH-WSA"
    ),
    "RUS-CENTER": (
        "RU-BEL RU-BRY RU-IVA RU-KLU RU-KOS RU-KRS RU-LIP RU-MOS RU-MOW "
        "RU-ORL RU-RYA RU-SMO RU-TAM RU-TUL RU-TVE RU-VLA RU-VLG RU-VOR "
        "RU-YAR"
    ),
    "RUS-EAST": "RU-AMU RU-KHA RU-PRI RU-SA RU-YEV",
    "RUS-NORTHWEST": (
        "RU-ARK RU-KGD RU-KO RU-KR RU-LEN RU-MUR RU-NEN RU-NGR RU-PSK RU-SPE"
    ),
    "RUS-SIBERIA": (
        "RU-AL RU-ALT RU-BU RU-IRK RU-KEM RU-KK RU-KYA RU-NVS RU-OMS "
        "RU-TOM RU-TY RU-ZAB"
    ),
    "RUS-SOUTH": (
        "RU-AD RU-AST RU-CE RU-DA RU-IN RU-KB RU-KC RU-KDA RU-KL RU-ROS "
        "RU-SE RU-STA RU-VGG UA-40 UA-43"
    ),
    "RUS-URALS": (
        "RU-BA RU-CHE RU-KGN RU-KHM RU-KIR RU-ORE RU-PER RU-SVE RU-TYU "
        "RU-UD RU-YAN"
    ),
    "RUS-VOLGA": "RU-CU RU-ME RU-MO RU-NIZ RU-PNZ RU-SAM RU-SAR RU-TA RU-ULY",
}
# Parts of regions outside a grid region, as polygons of longitude and
# latitude in WKT, drawn by hand along the borders of their districts.
# Antofagasta, Chile, but Taltal, its commune in the central system.
ANTOFAGASTA = (
    "POLYGON ((-70.6 -24.5, -70.4 -24.6, -69.2 -24.7, -69.1 -24.9, "
    "-69.2 -25.2, -69 -25.4, -69 -26.5, -66 -26.5, -66 -17, -72 -17, "
    "-72 -24.5, -70.6 -24.5))"
)
# Béchar, Algeria, outside its northern communes on the RIN.
BECHAR = (
    "POLYGON ((-5.4 30.2, -4.5 30.8, -4 30.9, -4.1 31.2, -3.9 31.8, "
    "-3.7 32, -3.2 32, -3.2 32.2, -3 32.3, -2.5 32.4, -1.5 32.4, "
    "-1.4 32.5, -1.1 32.5, -0.8 32.4, -0.1 32.6, 0.2 32.4, 0.2 32.2, "
    "-0.1 31.5, 0.6 30.9, 0.7 30.6, 0 29.6, -0.6 28.8, -0.9 28.6, "
    "-1.8 28.5, -2.8 28, -3.1 28, -3.6 28.3, -5.3 27.9, -5.5 28.1, "
    "-6.3 29.6, -6.1 29.8, -5.6 29.9, -5.4 30.2), (-3.8 31.1, -3.7 31.1, "
    "-3.6 31, -3.7 30.7, -3.6 30.3, -3.1 30.1, -2.3 30.2, -1.6 30.8, "
    "-0.6 30.9, -0.3 30.7, 0.4 30.7, -0.2 31.2, -0.2 31.3, -0.4 31.4, "
    "-0.4 32, -0.2 32.1, -0.2 32.3, -0.7 32.3, -1 32.2, -1.2 32.4, "
    "-1.3 32.2, -1.2 32.1, -1.9 32.2, -1.9 32.1, -2.1 32, -2.3 32, "
    "-2.3 32.2, -2.9 32.1, -3 32, -2.8 31.8, -3.7 31.7, -3.7 31.4, "
    "-3.8 31.3, -3.8 31.1))"
)
# The municipalities of Chocó, Colombia, whose seats are off the
# SIN: Acandí, Unguía, Juradó, Bahía Solano, Nuquí, Alto and Bajo
# Baudó, Litoral del San Juan, Bojayá and Medio Atrato.
CHOCO = (
    "MULTIPOLYGON (((-76.1 6.4, -76 6.2, -76 6.1, -76.2 6, -76.2 6.2, "
    "-76.8 5.8, -77 6.1, -76.7 6.1, -76.7 6.2, -76.8 6.4, -76.9 6.3, "
    "-77.1 6.3, -77.2 6, -77 5.7, -77 5.5, -76.9 5.4, -77.1 5.2, -77.3 5, "
    "-77.1 5, -77.1 4.9, -77 4.9, -77 4.8, -77.2 4.5, -76.6 4.3, "
    "-76.3 4.5, -76.2 4.3, -76.2 4.1, -76.5 3.7, -77.2 3.9, -77.5 3.8, "
    "-77.7 4, -77.8 4.2, -77.6 4.6, -77.6 5.3, -77.8 5.5, -77.6 5.8, "
    "-77.7 6.1, -77.7 6.4, -77.9 6.7, -78.1 7.2, -78 7.6, -77.8 7.7, "
    "-77.6 6.7, -77.4 6.8, -76.8 6.8, -76.8 7, -76.7 7, -76.5 6.4, "
    "-76.1 6.4)), ((-77.5 7.6, -77.6 7.5, -77.7 7.7, -77.5 7.6)), "
    "((-76.9 7.6, -77.1 7.8, -77.1 7.9, -77.3 7.9, -77.4 7.8, -77.4 7.9, "
    "-77.7 8.5, -77.5 8.9, -77.2 8.9, -76.8 8.4, -76.7 8.1, -76.9 7.6)))"
)
# El Menia and Hassi Gara, in Ghardaïa, Algeria, off the RIN.
GHARDAIA = (
    "POLYGON ((2 32.2, 2 32.8, 2.2 33, 4.2 33.3, 5.1 33.1, 5.3 32.9, "
    "5.2 32.7, 5 32.3, 4.6 32.1, 4.4 31.8, 4.5 32.2, 4.8 32.5, 5 32.9, "
    "4.1 33, 4.1 32.7, 3 32.9, 2.2 32.8, 2.3 32.3, 2.2 32.2, 3.6 31.4, "
    "4.1 31.2, 4.3 31.3, 4.1 29.9, 3.7 29.5, 3.6 29.1, 3.1 28.8, "
    "2.1 28.7, 1.8 28.9, 1.6 30.1, 1.8 31.7, 2 32.2))"
)
# Miraflores, in Guaviare, Colombia, whose seat is off the SIN.
GUAVIARE = (
    "POLYGON ((-72.9 1, -72.8 1.1, -72.7 1.1, -72.6 1.4, -72.4 1.4, "
    "-72.3 1.5, -72.4 1.8, -72 2, -71.3 1.6, -71.1 1.7, -71.3 0.9, "
    "-71.9 0.4, -72.2 0.5, -72.9 1))"
)
# The area that K-Electric supplies, Pakistan: Karachi, Gharo and
# Dhabeji, and Hub, Uthal, Vinder and Bela.
K_ELECTRIC = (
    "POLYGON ((66.2 26.35, 66.45 26.35, 66.75 25.85, 66.85 25.5, "
    "67.25 25.6, 67.6 25.2, 67.68 24.85, 67.68 24.65, 66.65 24.75, "
    "66.55 25.35, 66.45 25.85, 66.2 26.35))"
)
# Loreto, Peru, outside Alto Amazonas, its province on the SEIN.
LORETO = (
    "POLYGON ((-79 1, -69 1, -69 -10, -79 -10, -79 1), (-76.8 -6, "
    "-76.4 -6, -76.1 -6.2, -75.7 -6.2, -75.5 -5.9, -75.4 -5.6, "
    "-75.6 -5.5, -75.6 -5.4, -75.6 -5.2, -75.4 -5, -75.7 -4.9, "
    "-75.8 -4.7, -75.8 -4.4, -76 -4.3, -76.1 -4, -76.3 -3.7, -76.4 -3.9, "
    "-76.2 -4.3, -76.4 -4.4, -76.2 -4.8, -75.8 -5, -76 -5.1, -76.5 -5, "
    "-76.7 -5.4, -76.9 -5.5, -76.9 -5.7, -76.8 -6))"
)
# The communes of Los Lagos, Chile, with medium systems of their own:
# Cochamó, Hualaihué, Chaitén, Futaleufú and Palena.
LOS_LAGOS = (
    "POLYGON ((-72.6 -41.7, -72.4 -41.5, -72.4 -41.4, -72.3 -41.5, "
    "-70 -41.5, -70 -45, -73.2 -45, -73.2 -41.7, -72.6 -41.7))"
)
# Mapiripán, in Meta, Colombia, whose seat is off the SIN.
META = (
    "POLYGON ((-70.8 3.4, -70.8 2.8, -71 2.6, -72.5 2.5, -72.6 2.5, "
    "-72.7 2.6, -72.6 2.6, -72.4 2.8, -72.8 3, -72.9 2.9, -72.9 3.2, "
    "-72.4 3.4, -72.2 3.3, -71.6 3.5, -71.2 3.4, -71.1 3.3, -71 3.7, "
    "-70.8 3.4))"
)
# The Northern Territory, Australia, outside the Darwin-Katherine
# Interconnected System.
NORTHERN_TERRITORY = (
    "POLYGON ((128 -10, 139 -10, 139 -27, 128 -27, 128 -10), (130.7 -13, "
    "130.9 -13.5, 131.5 -14, 132 -14.8, 132.8 -14.9, 133 -15.7, "
    "133.4 -15.7, 133.3 -14.3, 132.5 -14.2, 132.1 -13.6, 131.5 -13.2, "
    "131.9 -13.1, 131.9 -12.6, 131.3 -12.2, 130.2 -12.2, 130.2 -12.9, "
    "130.7 -13))"
)
# Ouargla, Algeria, outside its communes on the RIN: El Borma,
# and the parts of Illizi in the Ouargla of Natural Earth.
OUARGLA = (
    "POLYGON ((3.5 30.1, 3.8 31.9, 4.1 32.5, 4.7 32.9, 4.7 33.6, 5 33.7, "
    "6 33.7, 6.1 33.4, 5.2 33.4, 5.1 33.5, 4.9 33.3, 5 32.9, 4.4 32.2, "
    "4.4 31.6, 3.7 29.8, 3.4 29.2, 3 29.1, 3.7 28.5, 5.7 29.7, 6.5 30.1, "
    "7.1 30.1, 6.7 31.1, 6.6 31.6, 6.6 32.8, 6.4 33.1, 6.5 33.2, "
    "6.3 33.6, 6.6 33.5, 7 32.6, 7.2 32.3, 9.1 32.3, 9.3 32.2, 9.8 30.2, "
    "9.5 29.8, 7.3 28.6, 6.8 28.6, 6 28.2, 4.7 28.2, 3.7 28.3, 2.7 29, "
    "2.7 29.3, 3.1 29.5, 3.5 30.1))"
)
# Puerto Leguízamo, in Putumayo, Colombia, whose seat is off the
# SIN.
PUTUMAYO = (
    "POLYGON ((-76.3 0.4, -76.2 0.4, -75.4 0.5, -75.2 0.7, -75.5 0.8, "
    "-75.2 1, -74.7 0.5, -74.5 0.4, -74.4 0.2, -73.7 -0.2, -73.6 -0.5, "
    "-73.7 -0.6, -74.5 -0.8, -75.2 -0.4, -75.5 -0.3, -75.9 -0.2, "
    "-76.4 0.3, -76.3 0.4))"
)
# Queensland, Australia, outside the NEM: the north-west around
# Mount Isa, the Gulf and Channel Country towns, Cape York and the
# Torres Strait.
QUEENSLAND = (
    "MULTIPOLYGON (((137.9 -16, 140.5 -16, 140.6 -17.3, 140.7 -17.6, "
    "140.8 -19, 141.1 -20, 141.3 -20.6, 141.5 -21.6, 142.3 -22.6, "
    "143.4 -23.9, 143.6 -25.5, 143.5 -26.4, 143.5 -29.1, 137.9 -29.1, "
    "137.9 -16)), ((140.9 -16.6, 141.6 -16.4, 142.6 -16.2, 143.6 -16, "
    "144.2 -15.8, 144.5 -15.3, 145 -14.9, 145.4 -14.8, 145.6 -14.5, "
    "144.8 -13.3, 143.9 -11.5, 143.5 -10.2, 143.2 -9.1, 141.9 -9.1, "
    "141 -9.6, 141.2 -10.5, 141 -12.5, 141 -15, 140.9 -16.6)))"
)
# South Australia outside the NEM: the remote north and west.
SOUTH_AUSTRALIA = (
    "POLYGON ((128 -25, 142 -25, 142 -39, 128 -39, 128 -25), (134.4 -34, "
    "135.5 -35.3, 136.4 -36.3, 138.5 -36.3, 139.5 -37.3, 141.1 -38.3, "
    "141.1 -33.8, 140.4 -33.6, 139.4 -33.2, 139.3 -32.6, 138.8 -31.6, "
    "138.6 -30.4, 138.2 -30.4, 138 -31.4, 137.6 -31.2, 137.4 -30.4, "
    "137 -30.2, 135.6 -29.5, 135.4 -29.8, 136.6 -30.6, 136.5 -31.3, "
    "136.3 -32.5, 135.6 -32.6, 134.6 -32.3, 133.4 -31.6, 132.4 -31.9, "
    "132.4 -32.4, 133.6 -32.8, 134.4 -34))"
)
# Taimyr and Norilsk, an isolated power system in Krasnoyarsk Krai,
# Russia.
TAIMYR = (
    "POLYGON ((67.7 68.4, 82.7 68.4, 84.8 67.2, 85.7 68, 86.4 68.1, "
    "87.5 67.3, 90.6 67.4, 93 68.4, 94.2 68.4, 95.4 69.3, 98 69.8, "
    "99.7 69.9, 103.8 69.3, 106.4 69.5, 131.4 69.5, 131.4 82, "
    "67.7 82, 67.7 68.4))"
)
# Atalaya and Purús, in Ucayali, Peru, isolated from the SEIN.
UCAYALI = (
    "POLYGON ((-74.8 -11.1, -74.9 -10.9, -74.8 -10.7, -74.5 -10.5, "
    "-74.7 -10, -74.5 -9.6, -74.4 -10, -74.1 -9.7, -73.7 -9.5, "
    "-73.2 -10.1, -73 -10, -73.2 -9.7, -73.2 -9.4, -72.9 -9.1, "
    "-72.2 -9.2, -71.9 -9.7, -71.4 -9.7, -70.6 -9.1, -70.4 -9.1, "
    "-70.2 -9.3, -70.2 -9.8, -70.5 -10.4, -70.9 -10.8, -71.2 -11.2, "
    "-71.9 -11.3, -72.1 -11.6, -72.5 -11.7, -73.1 -11.6, -73.4 -11.7, "
    "-73.8 -11.5, -74.5 -11.3, -74.8 -11.1))"
)
# Western Australia outside the South West Interconnected System.
WESTERN_AUSTRALIA = (
    "POLYGON ((112 -13, 130 -13, 130 -36, 112 -36, 112 -13), (115 -34.6, "
    "116.5 -35.3, 118 -35.3, 119.6 -34.6, 119.5 -34.2, 119 -34, "
    "120.2 -33.6, 119.6 -32.7, 119.6 -32.1, 119.1 -32.1, 119.3 -31.9, "
    "119.3 -31.7, 120.7 -31.2, 121 -31.1, 121.4 -31.4, 121.8 -31.2, "
    "121.6 -30.9, 121.7 -30.6, 121.3 -30.4, 121.1 -30, 120.4 -30.1, "
    "120.9 -30.9, 120.4 -31.1, 119.4 -31.2, 118.7 -30.9, 118.6 -30.4, "
    "118.2 -30.2, 117.7 -30, 117.4 -30, 117.2 -29.6, 116.7 -29.8, "
    "116.6 -29.3, 116.3 -29.2, 115.9 -28.4, 115.4 -28.2, 115.2 -27.8, "
    "114.8 -27.8, 114.6 -27.6, 113.6 -27.6, 114.6 -34.4, 115 -34.6))"
)
# The 13 Arctic districts of Yakutia, Russia, outside the western,
# central and south Yakutian energy districts of the East.
YAKUTIA = (
    "POLYGON ((91.3 66.5, 106.3 66.5, 108 66.4, 108.8 66.8, "
    "109.5 66.1, 112.7 66.6, 113.5 65.9, 112.3 65.6, 112.8 65.5, "
    "112.6 65.1, 114.1 64.6, 117.2 65.3, 118.3 66.1, 118.1 66.4, "
    "119.2 66.7, 119 66.9, 120.3 66.5, 120.5 65.7, 121.2 65.3, "
    "123.4 64.7, 127 65.6, 127.6 66, 126.9 66.2, 127.3 66.6, "
    "128.5 66.7, 130 66.5, 130.1 66.2, 131.7 65.7, 131.5 65.5, "
    "132.4 64.6, 132.8 64.6, 133.2 65.3, 136.8 66.2, 144.2 65, "
    "146.4 64.2, 171.4 64.2, 171.4 82, 91.3 82, 91.3 66.5))"
)
# The cut of each region of a composite.
CUTS = {
    "AUS-DKIS": {"AU-NT": NORTHERN_TERRITORY},
    "AUS-QLD1": {"AU-QLD": QUEENSLAND},
    "AUS-SA1": {"AU-SA": SOUTH_AUSTRALIA},
    "AUS-SWIS": {"AU-WA": WESTERN_AUSTRALIA},
    "CHL-SEN": {"CL-LL": LOS_LAGOS},
    "CHL-SIC": {"CL-AN": ANTOFAGASTA, "CL-LL": LOS_LAGOS},
    "COL-SIN": {
        "CO-CHO": CHOCO,
        "CO-GUV": GUAVIARE,
        "CO-MET": META,
        "CO-PUT": PUTUMAYO,
    },
    "DZA-RIN": {"DZ-08": BECHAR, "DZ-30": OUARGLA, "DZ-47": GHARDAIA},
    "PAK-NTDC": {"PK-BA": K_ELECTRIC, "PK-SD": K_ELECTRIC},
    "PER-SEIN": {"PE-LOR": LORETO, "PE-UCA": UCAYALI},
    "RUS-EAST": {"RU-SA": YAKUTIA},
    "RUS-SIBERIA": {"RU-KYA": TAIMYR},
}


def natural_earth(name: str, resolution: str) -> Any:
    """Read a layer of the cultural shapes of Natural Earth.

    Parameters
    ----------
    name : str
        Name of the layer, such as "admin_0_countries".
    resolution : str
        Scale of the layer: "10m", "50m" or "110m".

    Returns
    -------
    geopandas.GeoDataFrame
        The shapes of the layer.
    """
    path = cartopy.io.shapereader.natural_earth(
        resolution=resolution, category="cultural", name=name
    )
    return geopandas.read_file(path)


def feature(label: str, geometry: Any) -> dict[str, Any] | None:
    """Simplify a shape into a GeoJSON feature of an entity.

    Parameters
    ----------
    label : str
        Label of the entity.
    geometry : shapely.Geometry
        Shape of the entity, in degrees.

    Returns
    -------
    dict or None
        The feature, with its exterior rings anticlockwise and its holes
        clockwise, as the maps fill them, or None if nothing is left of
        the shape on the grid, as for the smallest territories.
    """
    geometry = shapely.simplify(geometry, TOLERANCE, preserve_topology=True)
    geometry = shapely.set_precision(geometry, GRID)
    if geometry.is_empty:
        return None
    geometry = shapely.orient_polygons(geometry)
    return {
        "type": "Feature",
        "properties": {"label": label},
        "geometry": shapely.geometry.mapping(geometry),
    }


def country_features() -> list[dict[str, Any]]:
    """Return the shapes of the countries of Natural Earth.

    Returns
    -------
    list of dict
        A feature for each country but Antarctica and those too small
        to be left on the grid, under the code of the list.
    """
    countries = natural_earth("admin_0_countries", "50m")
    features = []
    for code, geometry in zip(
        countries["ADM0_A3"], countries.geometry, strict=True
    ):
        if code != "ATA":
            shape = feature(COUNTRY_CODES.get(code, code), geometry)
            if shape is not None:
                features.append(shape)
    return features


def composite(regions: Any, label: str) -> Any:
    """Return the regions of a grid region, without their cut parts.

    Parameters
    ----------
    regions : geopandas.GeoDataFrame
        The regions of Natural Earth.
    label : str
        Label of the grid region, a key of ``COMPOSITES``.

    Returns
    -------
    geopandas.GeoDataFrame
        Its regions, each without its polygon in ``CUTS``, if any.
    """
    codes = COMPOSITES[label].split()
    shape = regions[regions["iso_3166_2"].isin(codes)].copy()
    for code, cut in CUTS.get(label, {}).items():
        rows = shape["iso_3166_2"] == code
        shape.loc[rows, "geometry"] = shape.loc[rows, "geometry"].difference(
            shapely.from_wkt(cut)
        )
    return shape


def subdivision_features() -> tuple[list[dict[str, Any]], list[str]]:
    """Return the shapes of the subdivisions of the list.

    Returns
    -------
    features : list of dict
        A feature for each subdivision with a shape.
    missing : list of str
        The labels of the subdivisions without a shape, with the error.
    """
    regions = natural_earth("admin_1_states_provinces", "10m")
    labels = sorted(
        {
            entity.label
            for source in registry.load_sources().values()
            for entity in source.entities
            if entity.subdivision_code is not None
        }
    )
    features, missing = [], []
    for label in labels:
        try:
            if label in COMPOSITES:
                shape = composite(regions, label)
            else:
                shape = utils.shapes.get_entity_shape(
                    label.replace("-", "_", 1), make_plot=False
                )
            shape = shape if shape.crs is None else shape.to_crs(4326)
            geometry = shapely.union_all(shape.geometry.to_numpy())
        except Exception as e:  # noqa: BLE001 - list every missing shape.
            missing.append(f"{label}: {type(e).__name__}: {e}")
            continue
        shape = feature(label, geometry)
        if shape is None:
            missing.append(f"{label}: empty after simplification")
            continue
        features.append(shape)
    return features, missing


def main() -> int:
    """Write the shapes file and list the subdivisions without a shape.

    Returns
    -------
    int
        0, also when some subdivisions have no shape.
    """
    subdivisions, missing = subdivision_features()
    features = country_features() + subdivisions
    lines = [json.dumps(f, separators=(",", ":")) for f in features]
    SHAPES_FILE.write_text(
        '{"type":"FeatureCollection","features":[\n'
        + ",\n".join(lines)
        + "\n]}\n",
        encoding="utf-8",
    )
    sys.stdout.write(f"{len(features)} shapes written to {SHAPES_FILE}.\n")
    for line in missing:
        sys.stdout.write(f"No shape for {line}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
