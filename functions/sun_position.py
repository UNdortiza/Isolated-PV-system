def sun_position(tz, lat, lon, year, month, day, hour, minute):
    from numpy import pi
    from math import sin, cos, atan, asin, acos, tan, degrees, radians
    '''
     retorna en coordenadas celestes la posición del sol, dada una ubicación, fecha y hora local.

    Args:
        tz : time zone [hrs W of GMT] (tz)
        lat : latitude [decimal ◦North of equator] (lat)
        lon : longitude [decimal ◦West of GMT] (lon)
        year : year [e.g., 1988] (yr)
        month : month year [1-12] (mo)
        day : day of year [1-365] (day)
        hour : hour of day local time [0-23] (hr)
        minute : minute of hour [0-59] (min)

    Returns:
        sun_zen : Solar zenith angle [deg] (zeta)
        sun_elv : Solar altitude angle [deg] (alpha)
        sun_dec : solar declination angle (delta)
        sun_azm : Solar azimuth angle [deg] (gamma)
    '''
    # Effective Time

    k = 1 if year % 4 == 0 else 0
    month_duration = [k, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    a = sum(month_duration[:month])
    jdoy = day + a
    
    t_utc = hour + ( minute / 60 ) - tz
    
    ## corrección de zona horaria y dia del año para los casos en que el calculo anterior da negativo o mayor a 24
    if t_utc < 0:
        t_utc += 24
        jdoy -= 1
    elif t_utc > 24:
        t_utc -= 24
        jdoy += 1

    # print( 'jdoy =' , jdoy )
    # print( 't_utc =' , t_utc )

    julian = 32916.5 + 365 * (year - 1949) + (year - 1949) / 4 + jdoy + t_utc / 24 - 51545
    # print( 'julian =', julian )
    # Sun Angles

    ## ecliptic coordinates

    def coordinate_correction ( variable, min_value, max_value ):
        from math import trunc
        aux = variable - max_value * trunc( variable / max_value )
        corrected_variable = aux if aux >= min_value else aux + max_value
        return corrected_variable

    ### mean longitude [degrees]
    mnlong = coordinate_correction(variable=( 280.46 +  0.9856474* julian ), min_value=0, max_value=360)
    # print('mnlong =', mnlong )
    ### mean anomaly [radians]
    mnanom = coordinate_correction(variable=radians( 357.528 + 0.9856003 * julian ), min_value=0, max_value=2*pi)
    # print('mnanom =',mnanom )
    ### ecliptic longitude [radians]
    eclong = coordinate_correction(variable=radians( mnlong + 1.915 * sin( mnanom ) + 0.02 * sin( 2 * mnanom ) ), min_value=0, max_value= 2*pi)
    # print('eclong =',eclong )
    ### obliquity of the ecliptic [radians]
    obleq = radians( 23.439 - 0.0000004 * julian )
    # print('obleq =',obleq )

    ## celestial coordinates

    ### right ascension[radians]
    ra = atan( ( cos( obleq ) * sin( eclong ) ) / cos( eclong ) )
    if ( cos( eclong ) < 0 ):
        ra += pi
    elif ( cos( obleq ) * sin( eclong ) < 0 ):
        ra += 2 * pi

    # print('ra = ', ra)

    ### sun_dec : solar declination angle (delta) [radians]
    sun_dec = asin( sin( obleq ) * sin( eclong ) )
    # print('sun_dec =', degrees(sun_dec), '◦')

    ## Local coordinates

    ### Greenwich mean siderial time[hours]
    gmst = coordinate_correction(variable=( 6.697375 + 0.0657098242 * julian + t_utc ), min_value=0, max_value=24)
    # print('gmst =', gmst)

    ### Local mean siderial time[hours]
    lmst = coordinate_correction(variable=( gmst + lon / 15 ), min_value=0, max_value=24)
    # print('lmst = ',lmst)

    ### Hour Angle[radians]
    HA = radians( 15 * lmst ) - ra

    if ( HA < -pi ) :
        HA += ( 2 * pi )
    elif ( HA > pi ):
        HA -= ( 2 * pi )
    # print('HA = ', degrees(HA),'◦')

    ### Sun altitude angle, not corrected for refraction [radians]
    alpha_0 = sin( sun_dec ) * sin( radians(lat) ) + cos( sun_dec ) * cos( radians( lat ) ) * cos( HA )
    # # print('alpha_0 = ',alpha_0 )

    if alpha_0 > 1 :
        alpha_0 = pi / 2
    elif alpha_0 < -1 :
        alpha_0 = -pi / 2
    else:
        alpha_0 = asin( alpha_0 )

    # # print('alpha_0 = ', alpha_0 )

    ### Sun altitude angle corrected for refraction
    alpha_0d = degrees( alpha_0 )

    r = 0
    if alpha_0d > -0.56:
        r =  3.51561 * ( ( 0.1594 + 0.0196 * alpha_0d + 0.00002 * alpha_0d**2 ) / ( 1 + 0.505 * alpha_0d + 0.0845 * alpha_0d**2 ) )
    else:
        r = 0.56

    ### sun_elv : Solar altitude angle [radians] (alpha)
    sun_elv = pi / 2 if alpha_0d + r > 90 else ( alpha_0d + r ) * pi / 180 
    # print('sun_elv = ', degrees(sun_elv),'◦' )

    ### sun_azm : Solar azimuth angle [radians] (gamma)
    gamma = ( sin( alpha_0 ) * sin( pi * lat / 180 ) - sin( sun_dec ) ) / ( cos( alpha_0 ) * cos( pi * lat / 180 ) )

    if gamma > 1:
        gamma = 0 
    elif gamma < -1:
        gamma = pi
    else:
        gamma = acos( gamma )

    if HA < -pi:
        sun_azm = gamma
    elif 0 < HA < pi:
        sun_azm = pi + gamma
    else:
        sun_azm = pi - gamma
    
    # print('sun_azm = ', degrees(sun_azm),'◦' )

    ### sun_zen : Solar zenith angle [radians] (zeta)
    sun_zen = pi / 2 - sun_elv

    # print('sun_zen = ', degrees(sun_zen) ,'◦' )

    # Sunrise and Sunset Hours

    ## sunrise hour angle[radians]
    HAR = -tan( lat ) * tan( sun_dec )
    if HAR >= 1: # Sun is down
        HAR = 0
    elif HAR <= -1: # Sun is up
        HAR = pi
    else: # sunrise hour
        HAR = acos( HAR )    
    ## Ecuation Of Time[hours]
    EOT = ( 1 / 15 ) * mnlong - ( pi / 180 ) * ra
    if EOT < -0.33:
        EOT += 24
    elif EOT > 0.33:
        EOT -= 24
    
    ## Sunrise and Sunset time in local standard decimal time
    t_sun = 12 - lon / 15 - tz - EOT
    t_sunrise = t_sun - 180 * HAR / ( 15 * pi )
    t_sunset = t_sun + 180 * HAR / ( 15 * pi )

    # Extraterrestrial Radiation
    ## is the extraterrestrial radiation incident on the plane normal to the radiation on
    G_on = 1367 * ( 1 + 0.033 * cos( radians( 360 * jdoy / 365 ) ) )
    if ( 0 < sun_zen < pi / 2 ):
        G_on = G_on 
    else:
        G_on = 0
    # print('G_o =', G_on)

    # True Solar Time and Eccentricity correction factor
    t_truesolar = hour + minute / 60 + lon / 15 - tz + EOT
    E_0 =1 / ( 1.00014 - 0.01671 * cos( mnanom ) - 0.00014 * cos( 2 * mnanom ) )**2

    return sun_zen, sun_elv, sun_dec, sun_azm, G_on

