from datetime import datetime
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
from rasterio.crs import CRS
from warnings import warn

# for formatting the datetime object to asfsearch syntax
def datetime2asfsearch(entered_date: datetime) -> str:
    return datetime.strftime(entered_date,'%Y') + '-' + datetime.strftime(entered_date,'%m') + '-' + datetime.strftime(entered_date,'%d') + 'T' + datetime.strftime(entered_date,'%H') + ':' + datetime.strftime(entered_date,'%M') + ':' + datetime.strftime(entered_date,'%S') + 'Z'

# for formatting the asfsearch syntax to datetime object
def asfsearch2datetime(entered_date: str) -> datetime:
    try:
        dtime = datetime.strptime(entered_date, '%Y-%m-%dT%H:%M:%S.%f')
    except:
        try:
            dtime = datetime.strptime(entered_date, '%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            dtime = datetime.strptime(entered_date, '%Y-%m-%d %H:%M:%S') 
    return dtime

# reformat results from asf_search list to geodataframe
def format_results_for_sent1(results: list) -> gpd.GeoDataFrame:
    geometry = [shape(r.geojson()['geometry']) for r in results]
    data = [r.properties for r in results]

    df = pd.DataFrame(data)
    df = gpd.GeoDataFrame(df, geometry=geometry, crs=CRS.from_epsg(4326))

    if df.empty:
        warn('Dataframe is empty! Check inputs.')
        return df

    df['startTime'] = pd.to_datetime(df.startTime)
    df['stopTime'] = pd.to_datetime(df.stopTime)
    df['start_date'] = pd.to_datetime(df.startTime.dt.date)
    df['start_date_str'] = df.start_date.dt.date.map(str)
    df['pathNumber'] = df['pathNumber'].astype(int)
    df.drop(columns=['browse'], inplace=True)
    df = df.sort_values(by=['startTime', 'pathNumber']).reset_index(drop=True)

    return df

# reformat results from hls_search list to geodataframe
def format_results_for_hls(results: list) -> gpd.GeoDataFrame:
    geometry = [shape(r.geometry) for r in results]
    data = [r.properties for r in results]
    # print(len(data))

    df = pd.DataFrame(data)
    df = gpd.GeoDataFrame(df, geometry=geometry, crs=CRS.from_epsg(4326))

    if df.empty:
        warn('Dataframe is empty! Check inputs.')
        return df
    
    df['startTime'] = pd.to_datetime(df.start_datetime.replace('Z',''))
    df['stopTime'] = pd.to_datetime(df.end_datetime.replace('Z',''))
#     df['start_date'] = pd.to_datetime(df.start_datetime.replace('Z','').dt.date)
#     df['start_date_str'] = df.start_datetime.replace('Z','').dt.date.map(str)
    df = df.sort_values(by=['startTime']).reset_index(drop=True)

    return df

# convert a shapely object (point or polygon) to geodataframe
def shape2gdf(shape, filename: str) -> gpd.GeoDataFrame:
    data = {}
    data['coordinates'] = [shape.wkt]
    data['coordinates'] = gpd.GeoSeries.from_wkt(data['coordinates'])
    df = pd.DataFrame(data)
    df = gpd.GeoDataFrame(df, geometry = 'coordinates', crs=CRS.from_epsg(4326))
    df.to_file(filename + '.geojson',driver='GeoJSON')
    
    return df