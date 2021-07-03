#!/usr/bin/env python

import altair as alt
import altair_saver
import io
import numpy as np
import pandas as pd
import random
import streamlit as st


DATA_TYPES = {
    'quantitative': 'Q',
    'ordinal':      'O',
    'nominal':      'N',
}

DELIMITERS = {
    'comma':      ',',
    'semi-colon': ';',
    'space':      ' ',
    'tab':        '\t',
}

# see https://vega.github.io/vega/docs/schemes/#reference
COLOR_SCHEMES = (
    # sequential single-hue schemes
    'blues',
    'tealblues',
    'teals',
    'greens',
    'browns',
    'oranges',
    'reds',
    'purples',
    'warmgreys',
    'greys',
    # sequential nulti-hue schemes
    'viridis',
    'magma',
    'inferno',
    'plasma',
    'cividis',
    'turbo',
    'bluegreen',
    'bluepurple',
    'goldgreen',
    'goldorange',
    'goldred',
    'greenblue',
    'orangered',
    'purplebluegreen',
    'purpleblue',
    'purplered',
    'redpurple',
    'yellowgreenblue',
    'yellowgreen',
    'yelloworagnebrown',
    'yelloworangered',
    # for dark backgrounds
    'darkblue',
    'darkgold',
    'darkgreen',
    'darkmulti',
    'darkred',
    # for light backgrounds
    'lightgreyred',
    'lightgreyteal',
    'lightmulti',
    'lightorange',
    'lighttealblue',
    # diverging schemes
    'blueorange',
    'brownbluegreen',
    'purplegreen',
    'pinkyellowgreen',
    'purpleorange',
    'redblue',
    'redgrey',
    'redyellowblue',
    'redyellowgreen',
    'spectral',
    # cyclical schemes
    'rainbow',
    'sinebow',
    # categorical schemes
    'accent',
    'category10',
    'category20',
    'category20b',
    'category20c',
    'dark2',
    'paired',
    'pastel1',
    'pastel2',
    'set1',
    'set2',
    'set3',
    'tableau10',
    'tableau20',
)

MISSING_COLORS = [
    'white',
    'grey',
    'black',
    'lightgreen',
    'green',
    'lightblue',
    'blue',
    'lightred',
    'red',
]

def create_topo_data(url, feature):
    return alt.topo_feature(url, feature)



def read_data(uri, encoding=None, delimiter=None):
    if uri.lower().endswith('.csv'):
        return pd.read_csv(uri, encoding=encoding, delimiter=delimiter)
    elif uri.lower().endswith('.xlsx'):
        return pd.read_excel(uri)
    else:
        raise ValueError(f'file type of ""{uri}"" is unknown')


def read_file(name, byte_stream, encoding=None, delimiter=None):
    if name.lower().endswith('.csv'):
        return pd.read_csv(io.BytesIO(byte_stream), encoding=encoding,
                           delimiter=delimiter)
    elif name.lower().endswith('.xlsx'):
        return pd.read_excel(io.BytesIO(byte_stream))
    else:
        raise ValueError(f'file type of ""{name}"" is unknown')


def validate_data(data):
    if len(data.columns) < 2:
        raise ValueError('data should have at least a NIS code and a data column')
    nis_code_pos = [idx for idx, col_name in enumerate(data.columns)
                        if col_name.lower() == 'niscode']
    if len(nis_code_pos) > 1:
        raise ValueError('multiple columns have NIS code name')
    elif len(nis_code_pos) == 0:
        raise ValueError('NIS code column is missing')
    else:
        columns = list(data.columns)
        columns[nis_code_pos[0]] = 'niscode'
        data.columns = columns
    if data.niscode.dtype != np.int64:
        raise ValueError('data type for NIS code is incorret, should be integer')


def create_plot(topo_data, data, column_name, data_type, tooltip_columns=None,
                stroke='darkgrey', strokeWidth=0.9, legend_title=None,
                scheme='reds', missing_color='white'):
    lookup_columns = [column_name]
    if tooltip_columns is not None:
        lookup_columns.extend(tooltip_columns)
    if legend_title is None:
        legend_title = column_name
    base = alt.Chart(topo_data) \
            .mark_geoshape() \
            .encode(
                color=alt.Color(f'{column_name}:{data_type}',
                                legend=alt.Legend(title=legend_title), 
                                scale=alt.Scale(scheme=scheme)),
                tooltip=[f'{column}:N' for column in tooltip_columns],
            ).transform_lookup(
                lookup='properties.CODE_INS',
                from_=alt.LookupData(data, 'niscode', lookup_columns)
            ).properties(
                width=600,
                height=450,
            )
    return alt.Chart(topo_data).mark_geoshape(stroke=stroke, strokeWidth=strokeWidth) \
            .encode(
                color=alt.value(missing_color),
                opacity=alt.value(0.9),
            ) + base


def create_quantitative_plot(topo_data, data, column_name,
                             stroke='lightgrey', strokeWidth=0.5,
                             legend_title=None, scheme='reds', missing_color='white'):
    return create_plot(topo_data, data, column_name, 'Q',
                       stroke, strokeWidth, legend_title, scheme, missing_color)


def create_nominal_plot(topo_data, data, column_name,
                        stroke='lightgrey', strokeWidth=0.5,
                        legend_title=None, scheme='reds', missing_color='white'):
    return create_plot(topo_data, data, column_name, 'N',
                       stroke, strokeWidth, legend_title, scheme, missing_color)

BE_GEO_URL = 'https://gist.githubusercontent.com/jandot/ba7eff2e15a38c6f809ba5e8bd8b6977/raw/eb49ce8dd2604e558e10e15d9a3806f114744e80/belgium_municipalities_topojson.json'
BE_MUNICIPALITIES_FEATURE = 'BE_municipalities'


if __name__ == '__main__':
    '''# Map Maker
    '''

    file_column1, file_column2 = st.beta_columns(2)
    with file_column1:
        data_file = st.file_uploader('Data file')
    with file_column2:
        encoding = st.selectbox('File encoding', ('utf-8', 'iso-8859-1'))
        delimiter = DELIMITERS[st.selectbox('Data delimiter',
                                             list(DELIMITERS.keys()))]

    topo_municipalities = create_topo_data(BE_GEO_URL, BE_MUNICIPALITIES_FEATURE)

    if data_file:
        file_name = data_file.name
        bytes_array = data_file.read()
        data = read_file(file_name, bytes_array, encoding=encoding, delimiter=delimiter)
        validate_data(data) 

        data_column1, data_column2, data_column3 = st.beta_columns(3)
        with data_column1:
            column_name = st.selectbox('Data column',
                                       [column for column in data.columns
                                        if column not in ('niscode',)])
        with data_column2:
            data_type = DATA_TYPES[st.selectbox('Data type', list(DATA_TYPES.keys()))]
        with data_column3:
            color_scheme = st.selectbox('Color scheme', COLOR_SCHEMES)
            missing_color = st.selectbox('Missing color', MISSING_COLORS)
        tooltip_names = st.multiselect('Tooltip columns',
                                       [column for column in data.columns
                                        if column not in ('niscode',)])
        plot = create_plot(topo_data=topo_municipalities, data=data,
                           column_name=column_name, data_type=data_type,
                           tooltip_columns=tooltip_names, scheme=color_scheme,
                           missing_color=missing_color)
        st.write(plot)
