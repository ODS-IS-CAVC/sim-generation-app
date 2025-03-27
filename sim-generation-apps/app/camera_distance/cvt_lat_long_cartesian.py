import numpy as np

from commons.constants import *


def convert_cartesian_to_lat_long(x, y, phi0_deg, lambda0_deg):
    """平面直角座標を緯度経度に変換する

    Args:
        x (float): 変換したいx座標[m]
        y (float): 変換したいy座標[m]
        phi0_deg (float): 平面直角座標系原点の緯度[度]（分・秒でなく小数であることに注意）
        lambda0_deg (float): 平面直角座標系原点の経度[度]（分・秒でなく小数であることに注意）

    Returns:
        [float, float]: 緯度[度], 経度[度]
    """
    # 緯度経度・平面直角座標系原点をラジアンに直す
    phi0_rad = np.deg2rad(phi0_deg)
    lambda0_rad = np.deg2rad(lambda0_deg)

    # 定数 (a, F: 世界測地系-測地基準系1980（GRS80）楕円体)
    m0 = 0.9999
    a = 6378137.
    F = 298.257222101

    n = 1. / (2*F - 1)
    A0 = 1 + (n**2)/4. + (n**4)/64
    A1 = -(3./2)*(n - (n**3)/8 - (n**5)/64)
    A2 = (15./16)*(n**2 - (n**4)/4)
    A3 = -(35./48)*(n**3 - (5./16)*(n**5))
    A4 = (315./512)*(n**4)
    A5 = -(693./1280)*(n**5)
    A_array = np.array([A0, A1, A2, A3, A4, A5])

    b1 = (1./2)*n - (2./3)*(n**2) + (37./96) * \
        (n**3) - (1./360)*(n**4) - (81./512)*(n**5)
    b2 = (1./48)*(n**2) + (1./15)*(n**3) - \
        (437./1440)*(n**4) + (46./105)*(n**5)
    b3 = (17./480)*(n**3) - (37./840)*(n**4) - (209./4480)*(n**5)
    b4 = (4397./161280)*(n**4) - (11./504)*(n**5)
    b5 = (4583./161280)*(n**5)
    beta_array = np.array([b1, b2, b3, b4, b5])

    d1 = 2.*n - (2./3)*(n**2) - 2.*(n**3) + (116./45) * \
        (n**4) + (26./45)*(n**5) - (2854./675)*(n**6)
    d2 = (7./3)*(n**2) - (8./5)*(n**3) - (227./45) * \
        (n**4) + (2704./315)*(n**5) + (2323./945)*(n**6)
    d3 = (56./15)*(n**3) - (136./35)*(n**4) - \
        (1262./105)*(n**5) + (73814./2835)*(n**6)
    d4 = (4279./630)*(n**4) - (332./35)*(n**5) - (399572./14175)*(n**6)
    d5 = (4174./315)*(n**5) - (144838./6237)*(n**6)
    d6 = (601676./22275)*(n**6)
    delta_array = np.array([d1, d2, d3, d4, d5, d6])

    A_hat = ((m0*a)/(1.+n))*A_array[0]
    Sphi0_hat = ((m0*a)/(1.+n))*(A_array[0]*phi0_rad +
                                 A_array[1:] @ np.sin(2*phi0_rad*np.arange(1, 6)))

    Xi = (x + Sphi0_hat) / A_hat
    Eta = y / A_hat

    Xi_comma = Xi - (beta_array * np.sin(2*Xi*np.arange(1, 6))
                     ) @ np.cosh(2*Eta*np.arange(1, 6))
    Eta_comma = Eta - (beta_array * np.cos(2*Xi*np.arange(1, 6))
                       ) @ np.sinh(2*Eta*np.arange(1, 6))

    chi = np.arcsin(np.sin(Xi_comma)/np.cosh(Eta_comma))
    latitude = chi + delta_array @ np.sin(2*chi*np.arange(1, 7))
    longitude = lambda0_rad + np.arctan(np.sinh(Eta_comma)/np.cos(Xi_comma))

    return [np.rad2deg(latitude), np.rad2deg(longitude)]


def convert_lat_long_to_cartesian(phi_deg, lambda_deg, phi0_deg, lambda0_deg):
    """緯度経度を平面直角座標に変換する

    Args:
        phi_deg (float): 変換したい緯度[度]（分・秒でなく小数であることに注意）
        lambda_deg (float): 変換したい経度[度]（分・秒でなく小数であることに注意）
        phi0_deg (float): 平面直角座標系原点の緯度[度]（分・秒でなく小数であることに注意）
        lambda0_deg (float): 平面直角座標系原点の経度[度]（分・秒でなく小数であることに注意）

    Returns:
        [float, float]: x, y (変換後の平面直角座標[m])
    """
    # 緯度経度・平面直角座標系原点をラジアンに直す
    phi_rad = np.deg2rad(phi_deg)
    lambda_rad = np.deg2rad(lambda_deg)
    phi0_rad = np.deg2rad(phi0_deg)
    lambda0_rad = np.deg2rad(lambda0_deg)

    # 定数 (a, F: 世界測地系-測地基準系1980（GRS80）楕円体)
    m0 = 0.9999
    a = 6378137
    F = 298.257222101

    n = 1/(2*F - 1)
    A0 = 1 + n**2/4 + n**4/64
    A1 = (-3/2) * (n - n**3/8 - n**5/64)
    A2 = (15/16) * (n**2 - n**4/4)
    A3 = (-35/48) * (n**3 - (5/16)*(n**5))
    A4 = (315/512) * n**4
    A5 = (-693/1280) * n**5

    alpha1 = n/2 - 2*n**2/3 + 5*(n**3)/16 + 41*(n**4)/180 - 127*(n**5)/288
    alpha2 = 13*n**2/48 - 3*(n**3)/5 + 557*(n**4)/1440 + 281*(n**5)/630
    alpha3 = 61*(n**3)/240 - 103*(n**4)/140 + 15061*(n**5)/26880
    alpha4 = 49561*(n**4)/161280 - 179*(n**5)/168
    alpha5 = 34729*(n**5)/80640

    A_arr = np.array([A0, A1, A2, A3, A4, A5])
    alpha_arr = np.array([alpha1, alpha2, alpha3, alpha4, alpha5])

    Sphi0_hat = (m0*a / (1+n)) * (A0*phi0_rad +
                                  A_arr[1:] @ np.sin(2*phi0_rad*np.arange(1, 6)))
    A_hat = (m0*a / (1+n)) * A0

    lambda_c = np.cos(lambda_rad - lambda0_rad)
    lambda_s = np.sin(lambda_rad - lambda0_rad)

    t1 = 2*np.sqrt(n)/(1+n)
    t = np.sinh(np.arctanh(np.sin(phi_rad)) -
                t1*np.arctanh(t1*np.sin(phi_rad)))
    t_hat = np.sqrt(1 + pow(t, 2))

    Xi_comma = np.arctan(t/lambda_c)
    Eta_comma = np.arctanh(lambda_s/t_hat)

    sum_2 = (alpha_arr * np.sin(2*Xi_comma*np.arange(1, 6))
             ) @ np.cosh(2*Eta_comma*np.arange(1, 6))
    sum_3 = (alpha_arr * np.cos(2*Xi_comma*np.arange(1, 6))
             ) @ np.sinh(2*Eta_comma*np.arange(1, 6))
    x = A_hat * (Xi_comma + sum_2) - Sphi0_hat
    y = A_hat * (Eta_comma + sum_3)

    return [x, y]


def cvt_plane_cartesian_to_world(xp, yp):
    """平面直角座標系を世界座標系に変更する
 
    Args:
        xp (float): 平面直角座標系の x座標
        yp (float): 平面直角座標系の y座標
 
    Returns:
        [float, float]: 世界座標
    """
    xw = yp
    yw = xp
    return [xw, yw]


def cvt_world_to_plane_cartesian(xw, yw):
    """世界座標系を平面直角座標系に変更する
 
    Args:
        xw (float): 世界座標系のx座標
        yw (float): 世界座標系のx座標
 
    Returns:
        [float, float]: 世界座標
    """
    yp = xw
    xp = yw
    return [xp, yp]


def degree2decimal(degrees, minutes, seconds):
    return degrees + (minutes / 60) + (seconds / 3600)


def decimal2degree(deg_decimal):
    deg = int(deg_decimal)
    seconds = (deg_decimal - int(deg_decimal)) * 3600
    minutes = seconds / 60
    seconds = seconds % 60
    return deg, minutes, seconds


def extract_degree_from_string(deg_str):
    """Extract (degree, minutes, second) from string

    Args:
        deg_str (str): string with format deg度mm分ss秒ffff

    Returns:
        [int, int, float]: degree, minutes, second
    """
    deg, remainder = deg_str.split('度')
    minutes, remainder = remainder.split('分')
    seconds = remainder.replace('秒', '.')

    deg = int(deg)
    minutes = int(minutes)
    seconds = float(seconds)

    return deg, minutes, seconds


def calc_org_lat_long(epsg_code: str = "auto", gps_data: np.ndarray = None):
    """Calculate original latitude & longitude from epsg code

    Args:
        epsg_code (str, optional): epsg code. Defaults to "auto".
        gps_data (np.ndarray, optional): GPS data. Defaults to None.

    Returns:
        (float, float): original latitude & longitude
    """
    if epsg_code == 'auto':
        lat_lon_diffs = []
        lat0_lon0_decimal = {}

        for area_id, area_info in LAT_LONG_ORG.items():
            lat0_deg, lat0_min, lat0_sec = extract_degree_from_string(area_info['lat'])
            lat0 = degree2decimal(lat0_deg, lat0_min, lat0_sec)
            lon0_deg, lon0_min, lon0_sec = extract_degree_from_string(area_info['lon'])
            lon0 = degree2decimal(lon0_deg, lon0_min, lon0_sec)

            lat_diff_avg = np.abs((gps_data[:, 0] - lat0).mean())
            lon_diff_avg = np.abs((gps_data[:, 1] - lon0).mean())
            lat_lon_diffs.append({area_id: np.array([lat_diff_avg, lon_diff_avg])})
            lat0_lon0_decimal[area_id] = [lat0, lon0]

        lat_lon_diffs = sorted(lat_lon_diffs, key=lambda item: list(item.values())[0].mean())
        epsg_code = list(lat_lon_diffs[0].keys())[0]
        phi0_deg, lambda0_deg = lat0_lon0_decimal[epsg_code]

    else:
        lat0_deg, lat0_min, lat0_sec = extract_degree_from_string(LAT_LONG_ORG[epsg_code]['lat'])
        phi0_deg = degree2decimal(lat0_deg, lat0_min, lat0_sec)
        lon0_deg, lon0_min, lon0_sec = extract_degree_from_string(LAT_LONG_ORG[epsg_code]['lon'])
        lambda0_deg = degree2decimal(lon0_deg, lon0_min, lon0_sec)

    return phi0_deg, lambda0_deg, epsg_code