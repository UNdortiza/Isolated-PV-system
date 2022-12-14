def rationing(I_sim, energy_per_hour, n_m, A_m, eta_m, n_b, v_b, E_b_max, l_b_min, l_b_0 ):
    '''
    Calcula el porcentaje de días de racionamiento en el periodo correspondiente a los datos de irradiancia y energía consumida por hora
    
    Args:
        I_sim : DataFrame con los datos de mes, dia, hora e irradiancia horaria simulada para un periodo deseado
        energy_per_hour : datos horarios de consumo energético por hora [W]
        n_m : numero de módulos en el arreglo [u]
        A_m : area efectiva de cada modulo [m^2]
        eta_m : eficiencia del modulo [%]
        n_b : numero de baterías [u]
        v_b : tension DC de la batería [V]
        E_b_max : capacidad maxima de la batería [Ah]
        l_b_min : porcentaje mínimo de nivel bajo para la batería [%]
        l_b_0 : porcentaje inicial del nivel para las baterías [%]
        
    Returns:
        r : indice de días de racionamiento 
    '''
    from pandas import unique
    # Se define función para calculo de energía que genera el arreglo de módulos solares en función de la irradiancia
    energy_array = lambda I : I * A_m * n_m * eta_m/100 # por una 1 hora [Wh]

    # Calculando parámetros de capacidad maxima y minima del sistema de almacenamiento
    E_bs_max =  n_b * E_b_max * v_b # [Wh]
    E_bs_min =  E_bs_max * l_b_min / 100 # [Wh]

    # Inicializando variables que guardan el estado actual de energía en los paneles y baterías
    E_b = E_bs_max * l_b_0/100 # energía almacenada en el sistema de baterías
    events = []
    E_n = I_sim.loc[:, ('Month','Day','Hour')]
    for data in I_sim.itertuples():
        E_a = energy_array(data.I_sim) * 0.86 # energía generada por el arreglo de módulos en la ultima hora
        E_c = energy_per_hour[data.Index] # energía consumida en la ultima hora
        E_n.loc[data.Index,'E_c'] = E_c
        E_n.loc[data.Index,'E_a'] = E_a
        E_n.loc[data.Index,'E_b'] = E_b 
        if E_c >= E_a:
            if E_c > ( E_a + E_b - E_bs_min ):
                E_b = E_bs_min
                events.append( ( data.Month, data.Day ) )
            else:
                E_b = E_a + E_b - E_c
        else:
            E_ex = E_a - E_c
            if E_b + E_ex > E_bs_max:
                E_b = E_bs_max
            else:
                E_b = E_b + E_ex
        
    # Elimina los eventos duplicados para el mismo dia
    events = unique( events )
    #calcula el indice de racionamiento
    r = len(events) / len( I_sim.groupby( ['Month','Day'] ) )
    return r, events, E_n


def rationing_monteCarlo(iterations,irradiance_data, time_zone, latitude, longitude, altitude, climate_type, year, surf_azm, surf_tilt, albedo, energy_per_hour, n_m, A_m, eta_m, n_b, v_b, E_b_max, l_b_min, l_b_0):
    from .irrandiance_simulation import daily_irradiance_simulation
    # lista en donde se guardan los indicies de racionamiento calculados en cada iteración
    rationing_indices = []
    for i in range(iterations):
        # En cada iteración se efectúa una simulación de irradiancia horaria con valores medios y desviaciones estándar diarias del indice de claridad
        df_sim = irradiance_data.loc[:, ('Month','Day','Hour')]
        df_sim['I_sim'], df_sim['I_c'] = daily_irradiance_simulation( irradiance_data=irradiance_data, time_zone=time_zone, latitude=latitude, longitude=longitude, altitude=altitude, climate_type=climate_type, year=year, surf_azm=surf_azm, surf_tilt=surf_tilt, albedo=albedo )
        # Calculada la simulación de irradiancia en un periodo anual, simula el racionamiento en función del perfil de demanda y la configuración de baterías y módulos
        r, events, E_n = rationing(I_sim=df_sim, energy_per_hour=energy_per_hour*len(df_sim.groupby(['Month','Day'])),  n_m=n_m, A_m=A_m, eta_m=eta_m, n_b=n_b, v_b=v_b, E_b_max=E_b_max, l_b_min=l_b_min, l_b_0=l_b_0 )
        rationing_indices.append(r)
    return rationing_indices