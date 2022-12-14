def irradiance_simulation(G_c:list, mea, sd):
    '''
    Descripción

    Args:
        G_c = radiación global de cielo despejado
        mea: valor medio del indice de claridad durante el intervalo
        sd: desviación estándar del indice de claridad durante el intervalo

    Returns:
        G: lista con los valores de radiación global, para cada uno de los puntos contenidos en G_c [W/m^2]
    '''
    from numpy import random
    G = []
    n = len(G_c) - G_c.count(0)
    while True:
        s = [ i for i in random.normal(mea, sd, n) ]
        if min( s ) > 0: break 
    for i in range( 0, len(G_c) ):
        if G_c[i] == 0:
            G.append( 0 )
        else:
            K_t = s.pop(0)
            G.append( G_c[i] if K_t >= 1 else G_c[i] * K_t )
    return G


def monthly_irradiance_simulation( irradiance_data, time_zone, latitude, longitude, altitude, climate_type, year, surf_azm, surf_tilt, albedo ):
    # , T_unit, number_of_units
    from .clear_sky_radiation import clear_sky_radiation, transmittance_br_constants
    from .sun_position import sun_position
    from .Incident_irradiance import incident_irradiance
    
    a_0, a_1, k  = transmittance_br_constants( altitude=altitude, climate_type=climate_type )
    I_c_sim = []
    I_sim = []

    for month in irradiance_data['Month'].unique():
        month_data = irradiance_data.query(f'Month == {month}')[['Day','Hour','Minute','Clearsky_GHI','GHI','K_t']]
        mu = month_data.K_t.mean()
        sigma = month_data.K_t.std()
        I_c_month = []
        for data in month_data.itertuples():
            sun_zen, sun_elv, sun_dec, sun_azm, G_on = sun_position( tz=time_zone, lat=latitude , lon=longitude , year=year , month=month , day=data.Day , hour=data.Hour , minute=data.Minute )
            G_cnb, G_cnd = clear_sky_radiation( G_on=G_on, sun_zen=sun_zen, a_0=a_0, a_1=a_1, k=k )
            I_cb, I_cd, I_cr = incident_irradiance( G_on, sun_zen, G_cnb, G_cnd, sun_azm, surf_azm, surf_tilt, albedo )
            I_c_month.append( I_cb + I_cd + I_cr )
        I_c_sim += I_c_month
        I_sim += irradiance_simulation(G_c=I_c_month, mea=mu, sd=sigma)
    return I_sim, I_c_sim

def daily_irradiance_simulation( irradiance_data, time_zone, latitude, longitude, altitude, climate_type, year, surf_azm, surf_tilt, albedo ):
    # , T_unit, number_of_units
    from .clear_sky_radiation import clear_sky_radiation, transmittance_br_constants
    from .sun_position import sun_position
    from .Incident_irradiance import incident_irradiance
    
    a_0, a_1, k  = transmittance_br_constants( altitude=altitude, climate_type=climate_type )
    I_c_sim = []
    I_sim = []
    for month in irradiance_data['Month'].unique():
        for day in irradiance_data.query(f'Month == {month}')['Day'].unique():
            day_data = irradiance_data.query(f'Month == {month} and Day == {day}')[['Day','Hour','Minute','Clearsky_GHI','GHI','K_t']]
            mu = day_data.K_t.mean()
            sigma = day_data.K_t.std()
            I_c_day = []
            for data in day_data.itertuples():
                sun_zen, sun_elv, sun_dec, sun_azm, G_on = sun_position( tz=time_zone, lat=latitude , lon=longitude , year=year , month=month , day=data.Day , hour=data.Hour , minute=data.Minute )
                G_cnb, G_cnd = clear_sky_radiation( G_on=G_on, sun_zen=sun_zen, a_0=a_0, a_1=a_1, k=k )
                I_cb, I_cd, I_cr = incident_irradiance( G_on, sun_zen, G_cnb, G_cnd, sun_azm, surf_azm, surf_tilt, albedo )
                I_c_day.append( I_cb + I_cd + I_cr )
            I_c_sim += I_c_day
            I_sim += irradiance_simulation(G_c=I_c_day, mea=mu, sd=sigma)
    return I_sim, I_c_sim

