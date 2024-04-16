import pandas as pd
import pvlib


def get_solar_irradiance(lon: float,
                         lat: float,
                         slope: float,
                         aspect: float,
                         day: str) -> float:
        """calculate solar potential (total irradiance (W/m^2)) for specific location at specific day """

        tus = pvlib.location.Location(lon, lat)
        times = pd.date_range(start=day, periods=24, freq='1h', tz=tus.tz)
        ephem_data = tus.get_solarposition(times)
        irrad_data = tus.get_clearsky(times)
        dni_et = pvlib.irradiance.get_extra_radiation(times)
        AM = pvlib.atmosphere.get_relative_airmass(ephem_data['apparent_zenith'])
        
        irradiance_hour = pvlib.irradiance.get_total_irradiance(slope, aspect, 
                                                                        ephem_data['apparent_zenith'], 
                                                                        ephem_data['azimuth'],
                                                                        dni=irrad_data['dni'], 
                                                                        ghi=irrad_data['ghi'], 
                                                                        dhi=irrad_data['dhi'],
                                                                        dni_extra=dni_et, airmass=AM)
        irradiance_day = irradiance_hour.poa_global.sum()
        return irradiance_day