import pandas as pd
import json
import plotly.plotly as py
import plotly.graph_objs as go

import os

colors = ['#ffffe0','#fffddb','#fffad7','#fff7d1','#fff5cd','#fff2c8',
          '#fff0c4','#ffedbf','#ffebba','#ffe9b7','#ffe5b2','#ffe3af',
          '#ffe0ab','#ffdda7','#ffdba4','#ffd9a0','#ffd69c','#ffd399',
          '#ffd196','#ffcd93','#ffca90','#ffc88d','#ffc58a','#ffc288',
          '#ffbf86','#ffbd83','#ffb981','#ffb67f','#ffb47d','#ffb17b',
          '#ffad79','#ffaa77','#ffa775','#ffa474','#ffa172','#ff9e70',
          '#ff9b6f','#ff986e','#ff956c','#fe916b','#fe8f6a','#fd8b69',
          '#fc8868','#fb8567','#fa8266','#f98065','#f87d64','#f77a63',
          '#f67862','#f57562','#f37261','#f37060','#f16c5f','#f0695e',
          '#ee665d','#ed645c','#ec615b','#ea5e5b','#e85b59','#e75859',
          '#e55658','#e45356','#e35056','#e14d54','#df4a53','#dd4852',
          '#db4551','#d9434f','#d8404e','#d53d4d','#d43b4b','#d2384a',
          '#cf3548','#cd3346','#cc3045','#ca2e43','#c72b42','#c52940',
          '#c2263d','#c0233c','#be213a','#bb1e37','#ba1c35','#b71933',
          '#b41731','#b2152e','#b0122c','#ac1029','#aa0e27','#a70b24',
          '#a40921','#a2071f','#a0051c','#9d0419','#990215','#970212',
          '#94010e','#91000a','#8e0006','#8b0000', '#8b0000']

scl = dict(zip(range(0, 101), colors))
colorscl = [[i * .01, v] for i,v in enumerate(colors)]

def get_scl(obj):
    frac = obj / 10000
    return scl[frac]

def get_scl_density(obj):
    frac = int(obj / 500) * 9
    return scl[frac]

def make_layers(df):
    layers_ls = []
    for x in df.index:
        item_dict = dict(sourcetype = 'geojson',
                        source = df.ix[x]['coordinates'],
                        type = 'fill',
                        color = df.ix[x]['color'])
        layers_ls.append(item_dict)
    return layers_ls

def build_figure(layers_ls, year, colorscl=colorscl,
                 mapbox_access_token=None, name = 'image.png'):
    data = go.Data([
                go.Scattermapbox(
                        lat = [0],
                        lon = [0],
                        marker = go.Marker(
                                      cmax=5000,
                                      cmin=0,
                                      colorscale = colorscl,
                                      showscale = True,
                                      autocolorscale=False,
                                      color=range(0,5000),
                                      colorbar= go.ColorBar(
                                                     len = .89
                                                            )
                                           ),
                        mode = 'markers')
                         ])

    layout = go.Layout(
        title = '{}'.format(year),
        height=1050,
        width=800,
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            layers= layers_ls,
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=39.03,
                lon=-105.7
            ),
            pitch=0,
            zoom=5.5,
            style='light'
        ),
    )

    fig = dict(data = data, layout=layout)
    py.image.save_as(fig, filename=name,
                     width = 750, height= 575)

def make_images(df, the_range = xrange(1990,2041),
                img = 'pop', folder = 'images', fn = 'pop_',
                mat=None):
    for year in the_range:
        year = int(year)
        print year
        year_df = full_df[full_df['year'] == year].copy()
        print '... getting colors'
        if img == 'pop':
            year_df['color'] = year_df['totalPopulation'].apply(get_scl)
        elif img == 'density':
            year_df['color'] = year_df['pop_density'].apply(get_scl_density)
        print '... building layers'
        layers = make_layers(year_df)
        print '... building figure'
        name = '{}_{}.png'.format(fn, year)
        path = folder + '/' + name
        while name not in os.listdir(folder):
            # try:
            build_figure(layers, year,
                        mapbox_access_token=mat,
                        name = path)
            print 'image for year {} built'.format(year)
            # except:
            #     print 'retrying'
            #     continue

if __name__ == '__main__':

    mapbox_access_token = os.environ['MAPBOX_AT']



    df = pd.read_csv('data/Population_Colorado.csv')

    ser_area = pd.read_pickle('data/county_area.pkl')
    ser_area.name = 'area'

    # read in county border data
    with open('data/colorado_counties.geojson') as f:
        counties = json.load(f)

    # format dataframe
    full_df = df.groupby(['county', 'year'], as_index=False).sum()
    full_df.drop(['fipsCode', 'age', 'malePopulation', 'femalePopulation'],
                 inplace = True, axis=1)

    # initialize a dictionary for geolocation by county
    geo_dict = {}

    for x in range(len(counties['features'])):
        # I ignore the last eleven characters in the name since the geojson file includes ' County, CO' in the county names and the population data does not
        name = counties['features'][x]['properties']['name'][:-11]
        if name in df['county'].unique():
            geo_dict[name] = counties['features'][x]
        else:
            print 'not in: ', name

    # make geodict into series
    ser = pd.Series(geo_dict.values(), index = geo_dict.keys())
    ser.name = 'coordinates'

    # join geodict series to population dataframe
    full_df = full_df.join(ser, on='county')
    full_df = full_df.join(ser_area, on='county')

    full_df['pop_density'] = full_df['totalPopulation'].div(full_df['area'])

    # make figure for each year
    make_images(full_df, the_range=xrange(1990,2041), img = 'density',
                folder = 'image_pop_dens', fn = 'pop_density',
                mat=mapbox_access_token)
