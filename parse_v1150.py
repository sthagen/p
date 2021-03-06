#! /usr/bin/env python
"""We are obviously playing with a parser here ..."""
from enum import IntEnum
from functools import partial

import geojson

IN = 'x-plane-v1150-earth_nav.dat'
OUT = 'x-plane-v1150-earth_nav.geojson'
OFFSET = 3
END_ROW_CODE_STR = str(99)


class NDB(IntEnum):
    """NDB class (formerly reception range in nautical miles)."""
    LOCATOR = 15,
    LOW_POWER = 25,
    NORMAL = 50,
    HIGH_POWER = 75,


class VOR(IntEnum):
    """VOR class (formerly reception range in nautical miles)
    Note:
        125 = unspecified but likely high power VOR. Uses the higher of 5.35 class and 5.149 figure of merit.
    """
    TERMINAL = 25,
    LOW_ALTITUDE = 40,
    HIGH_ALTITUDE = 130,
    UNSPECIFIED = 125,


"""DME service volume (formerly maximum reception range) 
- 40, 70, 120 or 150, where 150 means 120 or more for D-OSV or 25, 40, 130, 125 like VOR. 
When provided, use 5.277 D-OSV, otherwise 5.35 class or 5.149 figure of merit, whichever is higher.
"""


def ndb_code(number):
    """Look up an NDB enum."""
    for member in NDB:
        if member == number:
            return member
    return None


def vor_code(number):
    """Look up a VOR enum."""
    for member in VOR:
        if member == number:
            return member
    return None


def parse_ndb(payload):
    """
    Non-directional beacon (NDB):
    -----------------------------
    Row code for an NDB - 2
    Latitude of NDB in decimal degrees - Eight decimal places supported
    Longitude of NDB in decimal degrees - Eight decimal places supported
    Elevation in feet above MSL - Integer. Used to calculate service volumes.
    Frequency in KHz - Integer. Decimal frequencies not supported.
    NDB class (formerly reception range in nautical miles) - 15 = locator, 25 = low power, 50 = normal, 75 = high power NDB
    Not used for NDBs - 0.0
    NDB identifier - Up to four characters. Not unique
    NDB terminal region identifier or ENRT for enroute NDBs - Airport code for terminal NDBs, ENRT otherwise
    ICAO region code of enroute NDB or terminal area airport - Must be region code according to ICAO document No. 7910 For terminal NDBs, the region code of the airport is used
    NDB name - Text, suffix with "NDB"

    Examples:
    ,,,,,,,,,
     2   5.676183333   -0.137808333        0      409    25      0.000   AA ENRT DG ACCRA NDB
     2  13.845277778   20.845555556        0      350    50      0.000   AB ENRT FT ABECHE NDB
     2 -10.366666667   56.600000000        0      429    75      0.000  AGG ENRT FI AGALEGA NDB
     2   5.569177778   -0.181780556        0      258    15      0.000   AL ENRT DG ACCRA NDB
    """
    row_code = 2
    lat, rest = payload.lstrip().split(" ", 1)
    lat = float(lat)
    lon, rest = rest.lstrip().split(" ", 1)
    lon = float(lon)
    elev_ft_above_msl, rest = rest.lstrip().split(" ", 1)
    elev_ft_above_msl = int(elev_ft_above_msl)
    freq_khz, rest = rest.lstrip().split(" ", 1)
    freq_khz = int(freq_khz)
    ndb_class, rest = rest.lstrip().split(" ", 1)
    ndb_class = ndb_code(int(ndb_class))
    ndb_class = ndb_class.name if ndb_class else None
    _, rest = rest.lstrip().split(" ", 1)
    local_id, rest = rest.lstrip().split(" ", 1)
    ndb_terminal_region_id, rest = rest.lstrip().split(" ", 1)
    icao_region_code, rest = rest.lstrip().split(" ", 1)
    name = rest.strip()
    
    return "NDB", row_code, lat, lon, elev_ft_above_msl, freq_khz, ndb_class, None, local_id, ndb_terminal_region_id, icao_region_code, name


def parse_vor(payload):
    """
    Includes VOR-DMEs and VORTACs:
    ------------------------------
    Row code for a VOR - 3
    Latitude of VOR in decimal degrees - Eight decimal places supported 
    Longitude of VOR in decimal degrees - Eight decimal places supported 
    Elevation in feet above MSL - Integer. Used to calculate service volumes.
    Frequency in MHZ (multiplied by 100) - Integer - MHz multiplied by 100 (eg. 123.45MHz = 12345)
    VOR class (formerly reception range in nautical miles) - 25 = terminal, 40 = low altitude, 130 = high altitude, 125 = unspecified but likely high power VOR. Uses the higher of 5.35 class and 5.149 figure of merit.
    Slaved variation for VOR, i.e. direction of the 0 radial measured in true degrees - Up to three decimal places supported
    VOR identifier - Up to four characters. Not unique
    ENRT for all VORs - Always ENRT
    ICAO region code - Must be region code according to ICAO document No. 7910
    VOR name - Text, suffix with "VOR", "VORTAC" or "VOR-DME"

    Examples:
    ,,,,,,,,,
    3  40.899277778 -117.812191667     4299    10820    25     16.000  INA ENRT K2 WINNEMUCCA VOR/DME
    3  11.549211111   43.154819444       49    11460    40      2.000  ABI ENRT HD DJIBOUTI TACAN
    3  32.462833333   13.169508333      489    11510   130      2.000  ABU ENRT HL ABU ARGUB VOR/DME
    3  -2.724591667  107.753244444      190    11670   125      1.000  TPN ENRT WI TANJUNG PANDAN VOR/DME
    """
    row_code = 3
    lat, rest = payload.lstrip().split(" ", 1)
    lat = float(lat)
    lon, rest = rest.lstrip().split(" ", 1)
    lon = float(lon)
    elev_ft_above_msl, rest = rest.lstrip().split(" ", 1)
    elev_ft_above_msl = int(elev_ft_above_msl)
    freq_mhz_x_100, rest = rest.lstrip().split(" ", 1)
    freq_mhz_x_100 = int(freq_mhz_x_100)
    vor_class, rest = rest.lstrip().split(" ", 1)
    vor_class = vor_code(int(vor_class))
    vor_class = vor_class.name if vor_class else None
    slv_var, rest = rest.lstrip().split(" ", 1)
    slv_var = float(slv_var)
    local_id, rest = rest.lstrip().split(" ", 1)
    enrt, rest = rest.lstrip().split(" ", 1)
    icao_region_code, rest = rest.lstrip().split(" ", 1)
    name = rest.strip()

    return "VOR", row_code, lat, lon, elev_ft_above_msl, freq_mhz_x_100, vor_class, slv_var, local_id, enrt, icao_region_code, name


def parse_loc(payload, row_code):
    """
    Includes localisers (inc. LOC-only), LDAs and SDFs:
    ---------------------------------------------------
    Row code for a localizer associated with an ILS - 4=ILS localizer, 5=stand-alone localizer (inc LOC, LDA & SDF)
    Latitude of localiser in decimal degrees - Eight decimal places supported.
    Longitude of localiser in decimal degrees - Eight decimal places supported.
    Elevation in feet above MSL - Integer
    Frequency in MHZ (multiplied by 100) - Integer - MHz multiplied by 100 (eg. 123.45MHz = 12345)
    Maximum reception range in nautical miles - Integer - Terminal range is 25nm by default
    Localizer bearing in true degrees prefixed by integer magnetic front course times 360 - Up to three decimal places supported. Magnetic Front Course in integer degrees multiplied by 360 and added (e.g. front course of 164 degrees magnetic on localizer true bearing of 180.343 degrees becomes 59,040 + 180.343 = 59,220.343). This allows the true front course to be read accurately by clients unaware of the magnetic part, because fmod(59220.343, 360)==180.343.
    Localizer identifier - Up to four characters. Usually start with "I". Unique within airport terminal area
    Airport ICAO code - Up to four characters. Must be valid airport code
    Airport ICAO region code - Must be region code according to ICAO document No. 7910
    Associated runway number - Up to three characters
    Localiser name - Use "ILS-cat-I", "ILS-cat-II", "ILS-cat-III", "LOC", "LDA" or "SDF"

    Examples:
    ,,,,,,,,,
     4  36.692211111    3.217516667      131    11030    18  84112.655   AG DAAG DA 23 ILS-cat-III
     4  36.691050000    3.213302778       66    10850    18  33211.684   HB DAAG DA 09 ILS-cat-II
     4  22.795277778    5.444166667     4518    10850    18  72561.894   TM DAAT DA 20 ILS-cat-I
     4  36.816508333    7.808491667       59    10970    18  66786.872   AN DABB DA 19 ILS-cat-II
     4  36.290372222    6.609722222     2316    10830    18 122379.306   CS DABC DA 34 ILS-cat-I
     4  36.286136111    6.612638889     2359    10930    18 114076.228   CT DABC DA 32 ILS-cat-I
     4  35.613055556   -0.643861111      295    10990    18  89527.197   OR DAOO DA 25L ILS-cat-I
     4  31.629238889   -2.260983333     2661    10810    18  65699.985   BC DAOR DA 18 ILS-cat-I
     4  34.803333333    5.723333333      246    11090    18 111910.030   BI DAUB DA 31 ILS-cat-I
     4  32.384705556    3.792541667     1512    10950    18 109022.330   GH DAUG DA 30 ILS-cat-II

    """
    row_code = row_code
    lat, rest = payload.lstrip().split(" ", 1)
    lat = float(lat)
    lon, rest = rest.lstrip().split(" ", 1)
    lon = float(lon)
    elev_ft_above_msl, rest = rest.lstrip().split(" ", 1)
    elev_ft_above_msl = int(elev_ft_above_msl)
    freq_mhz_x_100, rest = rest.lstrip().split(" ", 1)
    freq_mhz_x_100 = int(freq_mhz_x_100)
    max_range_nautical_miles, rest = rest.lstrip().split(" ", 1)
    max_range_nautical_miles = int(max_range_nautical_miles)
    bearing_true_degrees, rest = rest.lstrip().split(" ", 1)
    bearing_true_degrees = float(bearing_true_degrees)
    local_id, rest = rest.lstrip().split(" ", 1)
    airport_icao, rest = rest.lstrip().split(" ", 1)
    icao_region_code, rest = rest.lstrip().split(" ", 1)
    runway_no, rest = rest.lstrip().split(" ", 1)
    name = rest.strip()

    return "LOC", row_code, lat, lon, elev_ft_above_msl, freq_mhz_x_100, max_range_nautical_miles, bearing_true_degrees, local_id, airport_icao, icao_region_code, runway_no, name


def parse_gli(payload):
    """
    Glideslope associated with an ILS:
    ----------------------------------
    Row code for a glideslope - 6
    Latitude of glideslope aerial in decimal degrees - Eight decimal places supported
    Longitude of glideslope aerial in decimal degrees - Eight decimal places supported
    Elevation in feet above MSL - Integer
    Frequency in MHZ (multiplied by 100) - Integer - MHz multiplied by 100 (eg. 123.45MHz = 12345)
    Maximum reception range in nautical miles - Integer - Terminal range is 25nm by default
    Associated localizer bearing in true degrees prefixed by glideslope angle - Up to three decimal places supported. Glideslope angle multiplied by 100,000 and added (e.g. Glideslope of 3.25 degrees on heading of 123.456 becomes 325123.456)
    Glideslope identifier - Up to four characters. Usually start with "I". Unique within airport terminal area
    Airport ICAO code - Up to four characters. Must be valid airport code
    Airport ICAO region code - Must be region code according to ICAO document No. 7910
    Associated runway number - Up to three characters
    Name - "GS"

    Examples:
    ,,,,,,,,,
     6  36.710150000    3.249166667      131    11030    18 300232.655   AG DAAG DA 23 GS
     6  36.690944444    3.174277778       66    10850    18 300091.684   HB DAAG DA 09 GS
     6  22.823888889    5.455277778     4518    10850    18 328201.894   TM DAAT DA 20 GS
     6  36.842438889    7.811202778       59    10970    18 300186.872   AN DABB DA 19 GS
     6  36.264838889    6.620272222     2316    10830    18 315339.306   CS DABC DA 34 GS
     6  36.272086111    6.631463889     2359    10930    18 300316.228   CT DABC DA 32 GS
     6  35.624527778   -0.614444444      295    10990    18 300247.197   OR DAOO DA 25L GS
     6  31.656047222   -2.260013889     2661    10810    18 300179.985   BC DAOR DA 18 GS
     6  34.785833333    5.746944444      246    11090    18 300310.030   BI DAUB DA 31 GS
     6  32.369391667    3.819586111     1512    10950    18 300302.330   GH DAUG DA 30 GS

    """
    row_code = 6
    lat, rest = payload.lstrip().split(" ", 1)
    lat = float(lat)
    lon, rest = rest.lstrip().split(" ", 1)
    lon = float(lon)
    elev_ft_above_msl, rest = rest.lstrip().split(" ", 1)
    elev_ft_above_msl = int(elev_ft_above_msl)
    freq_mhz_x_100, rest = rest.lstrip().split(" ", 1)
    freq_mhz_x_100 = int(freq_mhz_x_100)
    max_range_nautical_miles, rest = rest.lstrip().split(" ", 1)
    max_range_nautical_miles = int(max_range_nautical_miles)
    bearing_true_degrees, rest = rest.lstrip().split(" ", 1)
    bearing_true_degrees = float(bearing_true_degrees)
    local_id, rest = rest.lstrip().split(" ", 1)
    airport_icao, rest = rest.lstrip().split(" ", 1)
    icao_region_code, rest = rest.lstrip().split(" ", 1)
    runway_no, rest = rest.lstrip().split(" ", 1)
    name = rest.strip()

    return "GLI", row_code, lat, lon, elev_ft_above_msl, freq_mhz_x_100, max_range_nautical_miles, bearing_true_degrees, local_id, airport_icao, icao_region_code, runway_no, name


def parse_mrk(payload, row_code):
    """
    Marker beacons - Outer (OM), Middle (MM) and Inner (IM) Markers:
    ----------------------------------------------------------------
    Row code for a middle marker - 7=OM, 8=MM, 9=IM
    Latitude of marker in decimal degrees - Eight decimal places supported
    Longitude of marker in decimal degrees - Eight decimal places supported
    Elevation in feet above MSL - Integer
    Not used - 0
    Not used - 0
    Associated localiser bearing in true degrees - Up to three decimal places supported
    Not used - Use “----“ to indicate no associated ID
    Airport ICAO code - Up to four characters. Must be valid airport code
    Airport ICAO region code - Must be region code according to ICAO document No. 7910
    Associated runway number - Up to three characters
    Name - "OM", "MM" or "IM"
    
    Examples:
    ,,,,,,,,,
     7  36.751661111    3.314322222       82        0     0    232.655   AG DAAG DA 23 OM
     7  36.693888889    3.090000000       82        0     0     91.683   HB DAAG DA 09 OM
     7  36.223738889    6.686819444     2254        0     0    316.228   CT DABC DA 32 OM
     8  36.719166667    3.261388889       82        0     0    232.655   AG DAAG DA 23 MM
     8  36.876638889   10.233972222        0        0     0    192.291  TSI DTTA DT 19 MM
     8 -26.542777778   31.286666667        0        0     0     53.305  IMS FDMS FD 07 MM
     9  61.248019444 -149.850219444      192        0     0     80.021 IEDF PAED PA 06 IM
     9  64.802127778 -147.886813889      430        0     0     38.049 ICNA PAFA PA 02L IM
     9  61.167966667 -150.047686111      127        0     0     89.913 IANC PANC PA 07R IM
    """
    row_code = row_code
    lat, rest = payload.lstrip().split(" ", 1)
    lat = float(lat)
    lon, rest = rest.lstrip().split(" ", 1)
    lon = float(lon)
    elev_ft_above_msl, rest = rest.lstrip().split(" ", 1)
    elev_ft_above_msl = int(elev_ft_above_msl)
    _, rest = rest.lstrip().split(" ", 1)
    _, rest = rest.lstrip().split(" ", 1)
    bearing_true_degrees, rest = rest.lstrip().split(" ", 1)
    bearing_true_degrees = float(bearing_true_degrees)
    _, rest = rest.lstrip().split(" ", 1)
    airport_icao, rest = rest.lstrip().split(" ", 1)
    icao_region_code, rest = rest.lstrip().split(" ", 1)
    runway_no, rest = rest.lstrip().split(" ", 1)
    name = rest.strip()

    return "MRK", row_code, lat, lon, elev_ft_above_msl, None, None, bearing_true_degrees, None, airport_icao, icao_region_code, runway_no, name


def parse_dme(payload, row_code):
    """
    Distance Measuring Equipment (DME):
    -----------------------------------
    Row code for a DME - 12=Suppress frequency, 13=display frequency
    Latitude of DME in decimal degrees - Eight decimal places supported
    Longitude of DME in decimal degrees - Eight decimal places supported
    Elevation in feet above MSL - Integer
    Frequency in MHZ (multiplied by 100) - Integer - MHz multiplied by 100 (eg. 123.45MHz = 12345)
    DME service volume (formerly maximum reception range) - 40, 70, 120 or 150, where 150 means 120 or more for D-OSV or 25, 40, 130, 125 like VOR. When provided, use 5.277 D-OSV, otherwise 5.35 class or 5.149 figure of merit, whichever is higher.
    DME bias in nautical miles. - Default is 0.0 - Up to one decimal place supported
    Identifier - Up to four characters. Unique within terminal or ICAO region.
    Airport ICAO code (for DMEs associated with an ILS) ENRT for DMEs associated with VORs, VORTACs, NDBs or standalone DMEs - Up to four characters. Must be valid ICAO code ENRT otherwise
    ICAO region code of enroute DME or terminal area airport - Must be region code according to ICAO document No. 7910 For terminal DMEs, the region code of the airport is used
    Associated runway number (for DMEs associated with an ILS) - 1) Only used for DMEs associated with an ILS. 2) Up to three characters
    DME name (all DMEs) - 1) "DME-ILS" if associated with ILS 2) Suffix "DME" to navaid name for VOR-DMEs, VORTACs & NDB-DMEs (eg. "SEATTLE VORTAC DME" in example data) 3) For standalone DMEs just use DME name

    Examples:
    ,,,,,,,,,
    12 -09.43270300  147.21644400    128 11010  18       0.200 IWG  AYPY 14L DME-ILS
    12 -09.44922200  147.22658900    103 10950  18       0.200 IBB  AYPY 32R DME-ILS
    12  67.01870000 -050.68232200    172 10955  18       1.600 ISF  BGSF 10  DME-ILS
    12  63.96708333 -022.60344444    180 11130  18       0.000 IKN  BIKF 02  DME-ILS
    12  63.98913889 -022.60233333    199 11030  18       0.000 IKO  BIKF 20  DME-ILS
    12  63.98613889 -022.59905556    214 10850  18       0.000 IKW  BIKF 29  DME-ILS
    12  65.74222222 -019.57750000     16 10970  18       0.000 IKR  BIKR 01  DME-ILS
    12  42.58361100  021.03638900   1794 11010  18       0.100 PRS  BKPR 17  DME-ILS
    12  49.90634415 -099.96163061   1343 11010  18       0.000 IBR  CYBR 08  DME-ILS
    12  45.52196465 -073.40816937     90 11110  18       0.000 IHU  CYHU 24R DME-ILS

    12   9.037802778    7.285102778     1191    11630   130      0.000  ABC ENRT DN ABUJA VOR/DME
    12  11.549211111   43.154819444       49    11460    40      0.000  ABI ENRT HD DJIBOUTI TACAN DME
    12  32.462833333   13.169508333      489    11510   130      0.000  ABU ENRT HL ABU ARGUB VOR/DME
    13  28.601611111  -17.756583333      197    11240   130      0.000   BV ENRT GC LA PALMA DME
    13  33.521497222   -7.677186111      365    11690   130      0.000  CBA ENRT GM ANFA DME
    13 -12.349388889   49.295027778      374    11210   130      0.000   DI ENRT FM ANTSIRANANA DME

    """
    row_code = row_code
    lat, rest = payload.lstrip().split(" ", 1)
    lat = float(lat)
    lon, rest = rest.lstrip().split(" ", 1)
    lon = float(lon)
    elev_ft_above_msl, rest = rest.lstrip().split(" ", 1)
    elev_ft_above_msl = int(elev_ft_above_msl)
    freq_mhz_x_100, rest = rest.lstrip().split(" ", 1)
    freq_mhz_x_100 = int(freq_mhz_x_100)
    dme_service_voumne, rest = rest.lstrip().split(" ", 1)
    dme_service_voumne = int(dme_service_voumne)
    bearing_true_degrees, rest = rest.lstrip().split(" ", 1)
    bearing_true_degrees = float(bearing_true_degrees)
    local_id, rest = rest.lstrip().split(" ", 1)
    airport_icao, rest = rest.lstrip().split(" ", 1)
    icao_region_code, rest = rest.lstrip().split(" ", 1)
    name = rest.strip()

    return "DME", row_code, lat, lon, elev_ft_above_msl, freq_mhz_x_100, dme_service_voumne, bearing_true_degrees, local_id, airport_icao, icao_region_code, name


def has_data(row):
    """Detect end of data token."""
    return not row.startswith(END_ROW_CODE_STR)


def echo(payload, row_code):
    """ TODO. """
    concept = "FPAP" if row_code == 14 else ("GLS" if row_code == 15 else "LTP/FTP")
    return concept, row_code, payload


def parse(row):
    """In current data revision expect from the 37116 data rows (including the stop data row):
    5252 2
    4210 3
    3830 4
     347 5
    3830 6
     791 7
     516 8
     169 9
    6934 12
     421 13
    5346 14
     123 15
    5346 16
       1 99
    """
    if not has_data(row):
        return None

    parser = {
        2: parse_ndb,
        3: parse_vor,
        4: partial(parse_loc, row_code=4),
        5: partial(parse_loc, row_code=5),
        6: parse_gli,
        7: partial(parse_mrk, row_code=7),
        8: partial(parse_mrk, row_code=8),
        9: partial(parse_mrk, row_code=9),
        12: partial(parse_dme, row_code=12),
        13: partial(parse_dme, row_code=13),
        14: partial(echo, row_code=14),
        15: partial(echo, row_code=15),
        16: partial(echo, row_code=16),
    }
    row_code, payload = row.split(" ", 1)
    return parser.get(int(row_code))(payload)


def main():
    record_no = 0
    with open(IN, "rt", encoding="utf-8") as handle:
        for row in handle.readlines()[OFFSET:]:
            record_no += 1
            text = row.strip()
            record = parse(text)
            if not record:
                break
            print(record_no, record)

main()
