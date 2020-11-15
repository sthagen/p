#! /usr/bin/env python
from functools import partial

import geojson

IN = 'x-plane-v810-earth_nav.dat'
OUT = 'x-plane-v810-earth_nav.geojson'
OFFSET = 3
END_ROW_CODE_STR = str(99)


def parse_ndb(payload):
    """
    Non-directional beacon (NDB):
    -----------------------------
    Row code for an NDB - 2
    Latitude of NDB in decimal degrees - Eight decimal places supported
    Longitude of NDB in decimal degrees - Eight decimal places supported
    Elevation in feet above MSL - Integer. Used to calculate service volumes.
    Frequency in KHz - Integer. Decimal frequencies not supported.
    Maximum reception range in nautical miles - Integer
    Not used for NDBs - 0.0
    NDB identifier - Up to four characters. Not unique
    NDB name - Text, suffix with "NDB"

    Examples:
    ,,,,,,,,,
    2  38.08777778 -077.32491667      0   396  50    0.0 APH  A P HILL NDB
    2  57.08382000  009.68009300      0   398  25    0.0 GL   AALBORG NDB
    2  56.28795300  010.77527500      0   374  20    0.0 TU   AARHUS NDB
    2  56.31862500  010.45933100      0   324  20    0.0 ML   AARHUS NDB
    2  68.72318300 -052.78476400      0   336  25    0.0 AA   AASIAAT NDB
    2  53.69833300  091.35000000      0   360  80    0.0 AB   ABAKAN NDB
    2  53.76666700  091.40500000      0   360  80    0.0 AK   ABAKAN NDB
    2  30.06113889 -092.12327778      0   230  50    0.0 BNZ  ABBEVILLE NDB
    2  49.01544444 -122.48777778      0   344  50    0.0 XX   ABBOTSFORD NDB
    2  00.50000000  173.85000000    108   396  25    0.0 AA   ABEMAMA NDB
    2  39.53586111 -076.10638889      0   349  50    0.0 APG  ABERDEEN NDB
    2  57.13833300 -002.40472200      0   336  15    0.0 AQ   ABERDEEN NDB
    2  57.07751400 -002.10570000      0   348  25    0.0 ATF  ABERDEEN/DYCE NDB
    2  52.11633300 -004.55983300      0   370  20    0.0 AP   ABERPORTH NDB
    2  05.25041700 -003.95802800      0   294  50    0.0 PB   ABIDJAN FELIX HOUPHOUET BOIGNY NDB
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
    max_range_nautical_miles, rest = rest.lstrip().split(" ", 1)
    max_range_nautical_miles = int(max_range_nautical_miles)
    _, rest = rest.lstrip().split(" ", 1)
    local_id, rest = rest.lstrip().split(" ", 1)
    name = rest.strip()
    
    return "NDB", row_code, lat, lon, elev_ft_above_msl, freq_khz, max_range_nautical_miles, None, local_id, name


def parse_vor(payload):
    """
    Includes VOR-DMEs and VORTACs:
    ------------------------------
    Row code for a VOR - 3
    Latitude of VOR in decimal degrees - Eight decimal places supported 
    Longitude of VOR in decimal degrees - Eight decimal places supported 
    Elevation in feet above MSL - Integer. Used to calculate service volumes.
    Frequency in MHZ (multiplied by 100) - Integer - MHz multiplied by 100 (eg. 123.45MHz = 12345)
    Maximum reception range in nautical miles - Integer
    Slaved variation for VOR - Up to three decimal places supported
    VOR identifier - Up to four characters. Not unique 
    VOR name - Text, suffix with "VOR", "VORTAC" or "VOR-DME"

    Examples:
    ,,,,,,,,,
    3  57.10371900  009.99557800     57 11670 100    1.0 AAL  AALBORG VOR-DME
    3  30.38702800  048.21761100     10 11450 130    3.0 ABD  ABADAN VOR-DME
    3  53.74500000  091.38500000    827 11330 130    4.0 ABK  ABAKAN VOR-DME
    3  50.13513900  001.85469400    223 10845  60   -3.0 ABB  ABBEVILLE VOR-DME
    3  13.84511100  020.84500000   1804 11450 130    0.0 AE   ABECHE VOR
    3  57.31055600 -002.26722200    600 11430 200   -5.0 ADN  ABERDEEN VOR-DME
    3  45.41736111 -098.36872222   1301 11300 130    7.0 ABR  ABERDEEN VOR-DME
    3  18.24191700  042.65694400   6862 11290 130    1.0 ABH  ABHA VORTAC
    3  05.27719400 -003.91930600     30 11430 130   -7.0 AD   ABIDJAN VOR-DME
    3  32.48133333 -099.86344444   1810 11370 130   10.0 ABI  ABILENE VORTAC
    3  32.46277800  013.16944400    470 11510 130    0.0 ABU  ABU ARGUB VOR-DME
    3  24.44319400  054.64647200     68 11300 100    0.0 AUH  ABU DHABI VOR-DME
    3  22.35488900  031.62200000    640 11350 200    2.0 SML  ABU SIMBEL VOR-DME
    3  09.03779700  007.28509700   1240 11630  40   -2.0 ABC  ABUJA VOR-DME
    3  16.75847222 -099.75397222     16 11590 130    8.0 ACA  ACAPULCO VOR-DME
    3  09.55208333 -069.23791667    758 11340 130  -10.0 AGV  ACARIGUA VOR-DME
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
    max_range_nautical_miles, rest = rest.lstrip().split(" ", 1)
    max_range_nautical_miles = int(max_range_nautical_miles)
    slv_var, rest = rest.lstrip().split(" ", 1)
    slv_var = float(slv_var)
    local_id, rest = rest.lstrip().split(" ", 1)
    name = rest.strip()

    return "VOR", row_code, lat, lon, elev_ft_above_msl, freq_mhz_x_100, max_range_nautical_miles, slv_var, local_id, name


def parse_loc(payload, row_code):
    """
    Includes localisers (inc. LOC-only), LDAs and SDFs:
    ---------------------------------------------------
    Row code for a localizer associated with an ILS - 4=ILS localizer, 5=stand-alone localizer (inc LOC, LDA & SDF)
    Latitude of localiser in decimal degrees - Eight decimal places supported.
    Longitude of localiser in decimal degrees - Eight decimal places supported.
    Elevation in feet above MSL - Integer
    Frequency in MHZ (multiplied by 100) - Integer - MHz multiplied by 100 (eg. 123.45MHz = 12345)
    Maximum reception range in nautical miles - Integer
    Localiser bearing in true degrees - Up to three decimal places supported
    Localiser identifier - Up to four characters. Usually start with “I”. Not unique
    Airport ICAO code - Up to four characters. Must be valid airport code
    Associated runway number - Up to three characters
    Localiser name - Use "ILS-cat-I", "ILS-cat-II", "ILS-cat-III", "LOC", "LDA" or "SDF"

    Examples:
    ,,,,,,,,,
    4  39.98091100 -075.87781400    660 10850  18     281.662 IMQS 40N  29  ILS-cat-I
    4 -09.45892200  147.23122500    128 11010  18     148.638 IWG  AYPY 14L ILS-cat-I
    4 -09.42763300  147.21190000    103 10950  18     328.625 IBB  AYPY 32R ILS-cat-I
    4  76.53263092 -068.63301849    251 10950  18      85.060 IITL BGTL 08T ILS-cat-I
    4  63.99333333 -022.60544444    163 11130  18       0.020 IKN  BIKF 02  ILS-cat-I
    4  63.98505556 -022.58375000    171 10950  18      89.970 IKF  BIKF 11  ILS-cat-II
    4  63.96313889 -022.60544444    137 11030  18     180.020 IKO  BIKF 20  ILS-cat-II
    4  63.98502778 -022.66172222    111 10850  18     270.020 IKW  BIKF 29  ILS-cat-I
    4  65.74222222 -019.57722222      8 10970  18     351.000 IKR  BIKR 01  ILS-cat-I

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
    runway_no, rest = rest.lstrip().split(" ", 1)
    name = rest.strip()

    return "LOC", row_code, lat, lon, elev_ft_above_msl, freq_mhz_x_100, max_range_nautical_miles, bearing_true_degrees, local_id, airport_icao, runway_no, name


def parse_gli(payload):
    """
    Glideslope associated with an ILS:
    ----------------------------------
    Row code for a glideslope - 6
    Latitude of glideslope aerial in decimal degrees - Eight decimal places supported
    Longitude of glideslope aerial in decimal degrees - Eight decimal places supported
    Elevation in feet above MSL - Integer
    Frequency in MHZ (multiplied by 100) - Integer - MHz multiplied by 100 (eg. 123.45MHz = 12345)
    Maximum reception range in nautical miles - Integer
    Associated localiser bearing in true degrees prefixed by glideslope angle - Up to three decimal places supported.
        Glideslope angle multiplied by 100,000 and added (eg. Glideslope of 3.25 degrees on heading of 123.456 becomes 325123.456)
    Glideslope identifier - Up to four characters. Usually start with "I". Not unique
    Airport ICAO code - Up to four characters. Must be valid airport code
    Associated runway number - Up to three characters
    Name - "GS"

    Examples:
    ,,,,,,,,,
    6  39.97729400 -075.86027500    655 10850  10  300281.662 IMQS 40N  29  GS
    6 -09.43270300  147.21644400    128 11010  10  302148.638 IWG  AYPY 14L GS
    6 -09.44922200  147.22658900    103 10950  10  300328.625 IBB  AYPY 32R GS
    6  76.53109741 -068.75268555    251 10950  10  300085.060 IITL BGTL 08T GS
    6  65.64850000 -018.06780556     44 11190  10  500358.140 IEY  BIAR 01  GS
    6  65.27911111 -014.40944444    123 10930  10  300025.260 IES  BIEG 04  GS
    6  63.96708333 -022.60344444    180 11130  10  300000.020 IKN  BIKF 02  GS
    6  63.98641667 -022.64833333    150 10950  10  300089.970 IKF  BIKF 11  GS
    6  63.98913889 -022.60233333    199 11030  10  300180.020 IKO  BIKF 20  GS
    6  63.98613889 -022.59905556    214 10850  10  300270.020 IKW  BIKF 29  GS
    6  65.74222222 -019.57750000     16 10970  10  300351.000 IKR  BIKR 01  GS
    6  64.13363889 -021.94091667     48 10990  10  350175.260 IRK  BIRK 19  GS
    6  42.58277800  021.03630600   1794 11010  10  300175.689 PRS  BKPR 17  GS

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
    runway_no, rest = rest.lstrip().split(" ", 1)
    name = rest.strip()

    return "GLI", row_code, lat, lon, elev_ft_above_msl, freq_mhz_x_100, max_range_nautical_miles, bearing_true_degrees, local_id, airport_icao, runway_no, name


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
    Associated runway number - Up to three characters
    Name - "OM", "MM" or "IM"
    
    Examples:
    ,,,,,,,,,
    7  39.96071900 -075.75077800    660     0   0     281.662 ---- 40N  29  OM
    7 -09.37615000  147.17686700    128     0   0     148.638 ---- AYPY 14L OM
    7  65.87777778 -017.46333333     51     0   0      11.446 ---- BIHU 03  OM
    7  63.98508333 -022.73211111    171     0   0      89.970 ---- BIKF 11  OM
    7  64.30544444 -021.97127778     20     0   0     175.260 ---- BIRK 19  OM
    7  51.08105932 -113.90926177   3557     0   0     298.792 ---- CYYC 28  OM
    7  36.69396400  003.08995300     82     0   0      91.730 ---- DAAG 09  OM
    7  36.75166100  003.31432200     82     0   0     232.742 ---- DAAG 23  OM

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
    runway_no, rest = rest.lstrip().split(" ", 1)
    name = rest.strip()

    return "MRK", row_code, lat, lon, elev_ft_above_msl, None, None, bearing_true_degrees, None, airport_icao, runway_no, name


def parse_dme(payload, row_code):
    """
    Distance Measuring Equipment (DME):
    -----------------------------------
    Row code for a DME - 12=Suppress frequency, 13=display frequency
    Latitude of DME in decimal degrees - Eight decimal places supported
    Longitude of DME in decimal degrees - Eight decimal places supported
    Elevation in feet above MSL - Integer
    Frequency in MHZ (multiplied by 100) - Integer - MHz multiplied by 100 (eg. 123.45MHz = 12345)
    Minimum reception range in nautical miles - Integer
    DME bias in nautical miles. - Default is 0.000
    Identifier Up to four characters. - Not unique.
    Airport ICAO code (for DMEs associated with an ILS) - 1) Only used for DMEs associated with an ILS. 2) Up to four characters. Must be valid ICAO code
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

    try:
        runway_no, rest = rest.lstrip().split(" ", 1)
        name = rest.strip()
    except ValueError:
        runway_no = None
        name = rest.strip()
    return "DME", row_code, lat, lon, elev_ft_above_msl, freq_mhz_x_100, max_range_nautical_miles, bearing_true_degrees, local_id, airport_icao, runway_no, name


def has_data(row):
    """Detect end of data token."""
    return not row.startswith(END_ROW_CODE_STR)


def parse(row):

    if not has_data(row):
        return None

    parser = {
        2: parse_ndb,
        3: parse_vor,
        4: partial(parse_loc, row_code=4),
        5: partial(parse_loc, row_code=5),
        6: parse_vor,
        7: partial(parse_mrk, row_code=7),
        8: partial(parse_mrk, row_code=8),
        9: partial(parse_mrk, row_code=9),
        12: partial(parse_dme, row_code=12),
        13: partial(parse_dme, row_code=13),
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
