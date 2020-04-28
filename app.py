# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import plotly.express as px
from dash.dependencies import Input, Output
import os
from zipfile import ZipFile
import urllib.parse
from flask import Flask
import urllib.parse

import pandas as pd
import requests


server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

#Loading Data
data_df = pd.read_csv("cyano_gnps_merged.csv")

NAVBAR = dbc.Navbar(
    children=[
        dbc.NavbarBrand(
            html.Img(src="https://gnps-cytoscape.ucsd.edu/static/img/GNPS_logo.png", width="120px"),
            href="https://gnps.ucsd.edu"
        ),
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink("GNPS CyanoDB/GNPS Overlap", href="#")),
            ],
        navbar=True)
    ],
    color="light",
    dark=False,
    sticky="top",
)

DASHBOARD = [
    dbc.CardHeader(html.H5("GNPS CyanoDB/GNPS Overlap")),
    dbc.CardBody(
        [
            html.Div(id='version', children="Version - Release_1"),
            dcc.Graph(figure=px.histogram(data_df, x="Monoisotopic mass (neutral)", color="Class of compound")),
            
            html.H2(id='title', children='Library Table List'),
            html.Br(),
            dash_table.DataTable(
                id='library-table',
                columns=[
                    {"name": i, "id": i, "deletable": True, "selectable": True} for i in ["Compound identifier ", "Compound name", "GNPSID", "LIBRARY_QUALITY"]
                ],
                data=data_df.to_dict('records'),
                editable=False,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                row_selectable="single",
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current= 0,
                page_size= 10,
            ),
            html.Br(),
            html.H2(id='title2', children='Spectrum Summary'),
            dcc.Loading(
                id="structure",
                children=[html.Div([html.Div(id="loading-output-5")])],
                type="default",
            ),
            dcc.Loading(
                id="linkout",
                children=[html.Div([html.Div(id="loading-output-6")])],
                type="default",
            ),
        ]
    )
]

BODY = dbc.Container(
    [
        dbc.Row([dbc.Col(dbc.Card(DASHBOARD)),], style={"marginTop": 30}),
    ],
    className="mt-12",
)

app.layout = html.Div(children=[NAVBAR, BODY])

@app.callback(
    [Output('structure', "children"), Output('linkout', "children")],
    [Input('library-table', "derived_virtual_data"),
     Input('library-table', "derived_virtual_selected_rows")])
def update_gnps(rows, derived_virtual_selected_rows):
    selected_rows = derived_virtual_selected_rows # These are the rows with check boxes on the interface

    if selected_rows is not None and len(selected_rows) == 1:
        selected_row = rows[derived_virtual_selected_rows[0]]

        print(derived_virtual_selected_rows)
        img_obj = html.Img(id='image', src="https://gnps-structure.ucsd.edu/structureimg?smiles={}".format(urllib.parse.quote(selected_row["COMPOUND_SMILES"])))
        link_obj = html.A(dbc.Button("View In GNPS", color="primary", className="mr-1"), href="https://gnps.ucsd.edu/ProteoSAFe/gnpslibraryspectrum.jsp?SpectrumID={}".format(selected_row["GNPSID"]))

        return [img_obj, link_obj]

    return ["Select a Compound", ""]

if __name__ == "__main__":
    app.run_server(debug=True, port=5000, host="0.0.0.0")
