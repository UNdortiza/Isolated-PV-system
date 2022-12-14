def clear_sky_radiation ( G_on, sun_zen, a_0, a_1, k ):
    '''
    Descripción

    Args:
        G_on :
        sun_zen  :
        a_0 :
        a_1 :
        k :

    Returns:
        G_cnb :
        G_cnd :
    '''
    from math import exp, cos
    # atmospheric transmittance for beam radiation
    tau_b = a_0 + a_1 * exp( - k / cos( sun_zen ) )
    # print('tau_b =',tau_b)
    # clear-sky horizontal beam radiation 
    G_cnb = G_on * tau_b 
    # ratio of diffuse radiation to the extraterrestrial (beam) radiation on the horizontal plane
    tau_d = 0.271 - 0.294 * tau_b
    G_cnd = G_on * tau_d
    return G_cnb, G_cnd


def transmittance_br_constants( altitude, climate_type ):
    '''
    Descripción

    Args:
        altitude :
        climate_type :

    Returns:
        a_0 :
        a_1 :
        k :
    '''
    correction_factors={'Tropical': [ 0.95, 0.98, 1.02 ], 'Midlatitude summer': [ 0.97, 0.99, 1.02 ], 'Subarctic summer': [ 0.99, 0.99, 1.01 ], 'Midlatitude winter': [ 1.03, 1.01, 1,.00 ] }
    # calculating the values for the standard atmosphere
    A = altitude / 1000 # km
    a_0_ = 0.4237 - 0.00821 * ( 6 - A ) ** 2
    a_1_ = 0.5055 + 0.00595 * ( 6.5 - A ) ** 2
    k_ = 0.2711 + 0.01858 * ( 2.5 - A ) ** 2
    # print( 'a_0* = ', a_0_ ,'. a_1* =',a_1_,'. k* =',k_)
    r = correction_factors[climate_type]

    a_0 = a_0_ * r[0]
    a_1 = a_1_ * r[1]
    k = k_ * r[2]
    
    return a_0, a_1, k 

