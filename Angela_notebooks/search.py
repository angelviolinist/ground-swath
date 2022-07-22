from shapely.geometry import Polygon
from typing import List
from datetime import datetime, timedelta
from pystac_client import Client
import formatting as f
import asf_search as asf

# for searching for sentinel2 and landsat8 data
def hls_search(sensor: str, aoi: Polygon, date: List[datetime] = None):
    STAC_URL = 'https://cmr.earthdata.nasa.gov/stac'
    api = Client.open(f'{STAC_URL}/LPCLOUD/')
    
    if 'sentinel2' in sensor.lower():
        hls_collections = ['HLSS30.v2.0']
    elif 'landsat8' in sensor.lower():
        hls_collections = ['HLSL30.v2.0']
    
    if date == None:
        search_datetime = [datetime.combine(date.today(), datetime.min.time()), datetime.now()]
    else:
        search_datetime = date
    
    x, y = aoi.exterior.coords.xy
    
    search_params = {
        "collections": hls_collections,
        "bbox": [x[0],y[0],x[1],y[1]], # list of xmin, ymin, xmax, ymax
        "datetime": search_datetime,
    }
    search_hls = api.search(**search_params)
    hls_collection = search_hls.get_all_items()
    d = list(hls_collection)
    
    return d

# for searching sentinel1 data
def asf_search(aoi: Polygon, date: datetime = None):
    if date == None:
        today = date.today()
        start = str(today) + 'T00:00:00Z'
        end = str(today) + 'T23:59:59Z'
    else:
        start = f.datetime2asfsearch(date[0])
        end = f.datetime2asfsearch(date[1])

    wkt = aoi.wkt
    opts = {
        'platform': asf.PLATFORM.SENTINEL1,
        'processingLevel': [asf.PRODUCT_TYPE.SLC],
        'beamMode': [asf.BEAMMODE.IW],
        'start': start,
        'end': end
    }
    results = asf.geo_search(intersectsWith=wkt,**opts)
    
    return results

# find next acquisition date
def acq_search(sensor_name: str, aoi: Polygon, date):
    
    # put arbitrary hard stop at 3 searches (15 days)
    for rep in range(3):

        if 'landsat8' in sensor_name.lower():
            results = hls_search('landsat8', aoi, [date + timedelta(days = 5 * rep), date + timedelta(days = 5 * (rep + 1))])
            df = f.format_results_for_hls(results)
        elif 'sentinel1' in sensor_name.lower():
            results = asf_search(aoi, [date + timedelta(days = 5 * rep), date + timedelta(days = 5 * (rep + 1))])
            df = f.format_results_for_sent1(results)
        elif 'sentinel2' in sensor_name.lower():
            results = hls_search('sentinel2', aoi, [date + timedelta(days = 5 * rep), date + timedelta(days = 5 * (rep + 1))])
            df = f.format_results_for_hls(results)
            
        if not df.empty:
            break
    
    # extract time of next acquisition
    if not df.empty:

        try:
            next_acq = results.start_datetime[0]
        except:
            next_acq = results.startTime[-1]

    else:
        next_acq = 'Search yielded no results'
    
    return next_acq