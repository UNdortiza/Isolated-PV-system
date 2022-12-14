def incident_irradiance( G_on, sun_zen, G_cnb, G_cnd, sun_azm, surf_azm, surf_tilt, albedo ):
    '''
    Descripción

    Args:
        G_on :  
        sun_zen :  
        G_cnb :  
        G_cnd :  
        sun_azm :  
        surf_azm :  
        surf_tilt :  
        albedo : 
    Returns:
        I_cb : 
        I_cd : 
        I_cr : 
    '''
    from math import sin, cos, pi, acos, degrees, radians, sqrt
    # surface angles to radians
    gamma_s = radians(surf_azm)
    beta_s = radians(surf_tilt)

    # Angle of incidence
    AOI = sin( sun_zen ) * cos( sun_azm - gamma_s ) * sin( beta_s ) + cos( sun_zen ) * cos( beta_s )
    if AOI < -1:
        AOI = pi
    elif AOI > 1:
        AOI = 0
    else:
        AOI = acos( AOI )
    # print("AOI = ",degrees( AOI ), '◦')

    # Incident Beam Irradiance
    I_cb = G_cnb * cos( AOI )
    # print('I_b = ',I_b)

    # Incident Sky Diffuse Irradiance : HDKR Model
    A_i  = G_cnb / G_on if G_on != 0 else 0
    R_b = cos( AOI ) / cos( sun_zen )
    f = sqrt( G_cnb  / (G_cnb + G_cnd ) ) if (G_cnb + G_cnd ) != 0 else 0
    s = sin( beta_s / 2 )**3
    circumsolar = G_cnd * cos( sun_zen ) * A_i * R_b
    isotropic = G_cnd * cos( sun_zen ) * ( 1 - A_i ) * ( ( 1 + cos( AOI ) ) / 2 )
    iso_horizon = isotropic * ( 1 + f * s )
    I_cd = iso_horizon + circumsolar
    # print('I_d = ',I_d)

    # Incident Ground-reflected Irradiance
    I_cr = albedo * ( G_cnb  + G_cnd ) * cos( sun_zen ) * ( 1 - cos( beta_s ) ) / 2
    # print('I_r = ',I_r)
    return I_cb, I_cd, I_cr