# -*- coding: utf-8 -*-

import base64
import datetime
import io
import sys
import os
import importlib as imp
import flask
from sys import platform
import time

if sys.version_info[0] >= 3:
    imp.reload(sys)
else:
    reload(sys)
    sys.setdefaultencoding('utf8')


import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dte
import dash_reusable_components as drc

import numpy as np
import pandas as pd
import xlrd
import numbers
from string import punctuation

import re
alphabets = "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co|MD)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
digits = "([0-9])"

column_widths = [125,125,125,125]

dataFrame = []
dataFrameResults = []
downloadLink = ""
downloadLinkxls = ""

error_triggered = 'False'
nClicks = 0
terms = []
ls_initial_column_order = []
ls_final_column_order_output = []
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash('offline example',external_stylesheets=external_stylesheets )
app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True

if sys.platform =="win32":
    image_tim = os.getcwd()+'//tim.png'
    image_filename = os.getcwd()+'//cebi.png'
    image_loading = os.getcwd()+'//loading.gif'
else: #assuming linux or OS
    image_tim = os.getcwd()+'/tim.png'
    image_filename = os.getcwd()+'/cebi.png'
    image_loading = os.getcwd()+'/loading.gif'


encoded_image_tim = base64.b64encode(open(image_tim, 'rb').read())
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
encoded_image_loading = base64.b64encode(open(image_loading, 'rb').read())

app.title = 'CEBI-Miner'

app.layout = html.Div([

	html.Img(id='loading', src='data:image/gif;base64,{}'.format(encoded_image_loading.decode()), style={'padding-left': '40%', 'max-width': '300px', 'display': 'none',
																							'padding-top': '20%', 'position': 'absolute', 'float':'left', 'z-index':'100'}),

	html.Img(id='loading2', src='data:image/gif;base64,{}'.format(encoded_image_loading.decode()), style={'padding-left': '40%', 'max-width': '300px', 'display': 'none',
																							'padding-top': '135%', 'position': 'absolute', 'float':'left', 'z-index':'100'}),

	html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'padding-left': '75%','padding-top': '0%', 'width': '150px', 'max-width': '150px'}),
	html.Img(src='data:image/png;base64,{}'.format(encoded_image_tim.decode()), style={'padding-left': '45%', 'width': '10%', 'max-width': '300px'}),

    html.Div( 'CEBI-Miner',
        style={'text-align': 'center', 'margin-bottom': '15px', 'font-family':'Garmond','font-size':'50px', 'font-weight':'bold'}
    ),


	drc.Card([
	html.Div('Select Dataset:', style={'font-size':'25px', 'font-weight':'bold'}),
    html.H6("Upload file (excel or csv):"),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False),

    html.Br(),
	html.Div(id='output-image-upload'),
    html.Br(),
    html.H6("Uploaded Data:"),

    html.Div("Showing first 50 rows:"),
    html.Div(dte.DataTable(rows=[{}], id='table',editable=False, columns = ls_initial_column_order)),

    #Column of Interest

    html.H6("Column of Interest:"),
    dcc.Dropdown(id='dropdown_table_filterColumn',
                 multi = False,
                 placeholder='Select Column',
				 style={'width': '70.75%'}),


	html.H6("Index Column: (optional)"),
    dcc.Dropdown(id='dropdown_table_indexColumn',
                 multi = False,
                 placeholder='Select Column',
				 options=[
						{'label': 'None', 'value': ''},
						],
					value='',
				 style={'width': '70.75%'}),
    dcc.Input(id='index_keyword', type='text', value='', placeholder='Enter indicator value', style={'width': '50%'}),

	
	html.H6("Include found keyword sentences as a seperate column in results: (Slow with data > 500 records)"),
    dcc.RadioItems(id='keyword_sentences_column',
        options=[
            {'label': 'On', 'value': False},
            {'label': 'Off', 'value': True}        ],
        value=True
    ),



	html.H6("Scopes of Search:"),
    dcc.Dropdown(id='search_scope', multi = False,
                 placeholder='Select Scope',
				 options=[
						{'label': 'Whole Report', 'value': ''},
						{'label': 'Patient Information', 'value': 'Patient Information'},
						{'label': 'Exam Information', 'value': 'Exam Information'},
						{'label': 'Report (with Impression)', 'value': 'Report & Impression'},
						#{'label': 'Report (without Impression)', 'value': 'Report'},
						{'label': 'Impression Only', 'value': 'Impression'},
					],
					value='',
				 style={'width': '70.75%'}),

    #Search Keywords
    html.H6("Search Keywords (comma separated):"),
    dcc.Input(id='search_keywords', type='text', value='', placeholder='Enter here', style={'width': '50%'}),
	#html.Button(
    #    'Add keyword',
    #    id='add_keyword',
    #),
	#dcc.Dropdown(id='list_keywords',
    #    options=[{}],
    #    multi=True
    #),
	], style={'width': '70%'}),
     #style={'text-align': 'center', 'margin-bottom': '15px'}

	html.Br(),

    #Radio button of Associated Words Feature
    #html.Br(),

	drc.Card([
    html.Div('Associated Words Feature:', style={'font-size':'25px', 'font-weight':'bold'}),
    dcc.RadioItems(id='associated_words_feature',
        options=[
            {'label': 'On', 'value': False},
            {'label': 'Off', 'value': True}        ],
        value=True
    ),

    #Associated words
    html.H6("Associated words (comma seperated):"),
    dcc.Input(id='associated_words', type='text', value='', placeholder='Enter here', style={'width': '50%'}),

    #Associated Words Direction and Distance
    html.Br(),
    html.H6("Associated Words Direction:"),
    dcc.Dropdown(id='associated_words_direction',
        options=[
            {'label': 'Before', 'value': 'Before'},
            {'label': 'After', 'value': 'After'}        ],
        multi=True, style={'width': '70.75%'}
    ),

    html.H6("Associated Distance Units:"),
    dcc.RadioItems(id='associated_distance_units',
        options=[
            {'label': ' Word', 'value': 'Words'},
            {'label': ' Sentence', 'value': 'Sentences'}
        ],
        value='Words'
    ),


    # Associated Words Distance
    html.H6("Associated Distance:"),
    dcc.Slider(id='associated_words_distance',
        min=0,
        max=20,
        marks={i: '{}'.format(i) if i == 1 else str(i) for i in range(0, 21)},
        value=0,
    ),
    html.Br(),
    html.Div(' - If "Sentence" is selected as the distance unit, a distance 0 means search within the same sentence.', style={'font-size':'15px'}),
	], style={'width': '70%'}),

    #Radio button of negations
    html.Br(),

	drc.Card([
    html.Div('Negation Words Feature:', style={'font-size':'25px', 'font-weight':'bold'}),
    dcc.RadioItems(id='negation_words_feature',
        options=[
            {'label': 'On', 'value': False},
            {'label': 'Off', 'value': True}        ],
        value=True
    ),

    #Negations words
    html.H6("Negation words (comma seperated):"),
    dcc.Input(id='negation_words', type='text', value='', placeholder='Enter here', style={'width': '50%'}),


    #Negation Words Direction
    html.Br(),
    html.H6("Negation Words Direction:"),
    dcc.Dropdown(id='negation_words_direction',
        options=[
            {'label': 'Before', 'value': 'Before'},
            {'label': 'After', 'value': 'After'}        ],
        multi=True,
		style={'width': '70.75%'}
    ),
    html.H6("Negation Distance Units:"),
    dcc.RadioItems(id='negation_distance_units',
        options=[
            {'label': ' Word', 'value': 'Words'},
            {'label': ' Sentence', 'value': 'Sentences'}
        ],
        value='Words'

    ),
    # Negation Words Distance
    html.H6("Negation Distance:"),
    dcc.Slider(id='negation_words_distance',
        min=0,
        max=20,
        marks={i: '{}'.format(i) if i == 1 else str(i) for i in range(0, 21)},
        value=0,
    ),
    html.Br(),
    html.Div(' - If "Sentence" is selected as the distance unit, a distance 0 means search within the same sentence.', style={'font-size':'15px'}),
	], style={'width': '70%'}),

    #Output and Download
    html.Br(),

	drc.Card([
    html.Div('Output:', style={'font-size':'25px', 'font-weight':'bold'}),

    #Selection Summary
    html.H6("Current Selection Summary:"),
	html.Div(id='selection_summary_0'),
    html.Div(id='selection_summary_1'),
    html.Div(id='selection_summary_2'),
    html.Div(id='selection_summary_3'),

    html.Br(),
    html.Div(id='table_x'),
    html.Button(
        'Run NLP Search',
        id='search',
        #download="output.csv",
        #href="",
        #target="_blank"
    ),
	
    dcc.ConfirmDialog(
        id='alert',
        message='There was an error. After clicking okay, please refresh your browser and try again.',
	),

    #dcc.ConfirmDialog(
    #    id='alert',
    #    message='There was an unexpected error2!',
	#),
	
#	html.Button(
#        'Get Download Link for Table',
#        id='download-button',
#        #download="./results.csv",
#        #href="./results.csv",
#        #target="_blank"
#    ),

	#html.Br(),
	#html.Br(),
	# html.A(
	# 	"Download Results (csv)", id='download-link', href="results.csv", target="", style={'padding-left':'25px'},
	# ),

	html.A(
		"Download Results (xlsx - Excel)", id='download-link-xlsx', href="results.xlsx", target="", style={'padding-left':'25px'},
	),

	#Output Statistics
	html.Br(),
	html.Br(),
	html.H6("Output Statistics:"),
	html.Div(id='output_statistics_1', style={'user-select':'text'}),
    html.Div(id='output_statistics_3', style={'user-select':'text'}),
	html.Div(id='output_statistics_2', style={'user-select':'text'}),
	html.Div(id='output_statistics_4', style={'user-select':'text'}),


    html.Br(),
	html.Br(),
	html.Div("Showing first 50 rows:"),
	html.Div(dte.DataTable(rows=[{}], id='results', editable=False, columns=ls_final_column_order_output, column_widths  = column_widths )),
	html.Br(),

	], style={'width': '70%'}),
])

# Functions

# file upload function

#Telling user at the end what they entered
#keywords = [" ".join(x.strip().split()) for x in keywords.split(',')]
#neg_words = [" ".join(x.strip().split()) for x in neg_words.split(',')]
#assoc_words = [" ".join(x.strip().split()) for x in assoc_words.split(',')]

@app.callback(
    Output(component_id='selection_summary_0', component_property='children'),
    [Input('dropdown_table_filterColumn','value')]
    )
def search_keywords_summary(input1):
    if input1 == None:
        return 'Column of interest: None. You must select a column of interest before running the NLP search.'
    else:
        return 'Column of interest: {}'.format(input1)

@app.callback(
    Output(component_id='selection_summary_0', component_property='style'),
    [Input('dropdown_table_filterColumn','value')]
    )
def column_of_interest_color(input1):
    if input1 == None:
        style_bad = {'color': 'red'}
        return style_bad
    else:
        style_good = {'color': 'black'}
        return  style_good  


@app.callback(
    Output(component_id='selection_summary_1', component_property='children'),
    [Input('search_keywords','value')]
    )
def search_keywords_summary(input1):
    if input1 == '':
        return "No search words entered. You must enter search keywords before running the NLP search."
    else:
        words = [" ".join(x.strip().split()) for x in input1.split(',')]
        if words[-1] =="":
            words.pop()
            return 'Search keywords: {}'.format(words)
        else:
            return 'Search keywords: {}'.format(words)

@app.callback(
    Output(component_id='selection_summary_1', component_property='style'),
    [Input('search_keywords','value')]
    )
def search_keywords_summary_color(input1):
    if input1 == '':
        style_bad = {'color': 'red'}
        return style_bad
    else:
        style_good = {'color': 'black'}
        return style_good


@app.callback(
    Output(component_id='selection_summary_2', component_property='children'),
    [Input('associated_words', 'value'),
    Input('associated_words_feature', 'value'),
	Input('associated_words_distance', 'value'),
	Input('associated_words_direction', 'value'),
    Input('associated_distance_units', 'value')]
    )
def update_associated_words_summary(input1, input2, distance, directions, distance_units):
	if input2 == False: #false is on
		words = [" ".join(x.strip().split()) for x in input1.split(',')]
		if (len(words)==1 and words[0] ==""):
			return 'Associated feature is turned on, but no words have been entered.'
		
		if directions == None or directions == []: 
			if words[-1]=="":
				words.pop()
				return 'Associated words: {}. Distance Unit: {}.  Search distance: {}.   Search Direction: {}.'.format(words, str(distance_units), str(distance), str(directions)) +  'You must select an associated search direction.' 
			else:
				return 'Associated words: {}. Distance Unit: {}.  Search distance: {}.   Search Direction: {}.'.format(words, str(distance_units), str(distance), str(directions)) +  'You must select an associated search direction.' 
		
		if words[-1]=="":
			words.pop()
			return 'Associated words: {}. Distance Unit: {}.  Search distance: {}.   Search Direction: {}.'.format(words, str(distance_units), str(distance), str(directions))
		else:
			return 'Associated words: {}. Distance Unit: {}.  Search distance: {}.   Search Direction: {}.'.format(words, str(distance_units), str(distance), str(directions)) 
	else:
		return 'Associated feature is turned off.'


@app.callback(
    Output(component_id='selection_summary_2', component_property='style'),
    [Input('associated_words', 'value'),
    Input('associated_words_feature', 'value'),
	Input('associated_words_distance', 'value'),
	Input('associated_words_direction', 'value'),
    Input('associated_distance_units', 'value')]
    )
def update_negation_words_summary_color(input1, input2, distance, directions, distance_units):
	print(directions)
	if input2 == False: #false is on
		words = [" ".join(x.strip().split()) for x in input1.split(',')]
		if (len(words)==1 and words[0] ==""):
			return {'color': 'red'}
		elif (directions == None or directions == []):
			return {'color': 'red'}
		else:
			return {'color': 'black'}





@app.callback(
    Output(component_id='selection_summary_3', component_property='children'),
    [Input('negation_words', 'value'),
    Input('negation_words_feature', 'value'),
	Input('negation_words_distance', 'value'),
	Input('negation_words_direction', 'value'),
    Input('negation_distance_units', 'value')]
    )
def update_associated_words_summary(input1, input2, distance, directions, distance_units):
	if input2 == False: #false is on
		words = [" ".join(x.strip().split()) for x in input1.split(',')]
		if (len(words)==1 and words[0] ==""):
			return 'Negation feature is turned on, but no words have been entered.'
		
		if directions == None or directions == []: 
			if words[-1]=="":
				words.pop()
				return 'Negation words: {}. Distance Unit: {}.  Search distance: {}.   Search Direction: {}.'.format(words, str(distance_units), str(distance), str(directions)) +  'You must select a negation search direction.' 
			else:
				return 'Negation words: {}. Distance Unit: {}.  Search distance: {}.   Search Direction: {}.'.format(words, str(distance_units), str(distance), str(directions)) +  'You must select a negation search direction.' 
		
		if words[-1]=="":
			words.pop()
			return 'Negation words: {}. Distance Unit: {}.  Search distance: {}.   Search Direction: {}.'.format(words, str(distance_units), str(distance), str(directions))
		else:
			return 'Negation words: {}. Distance Unit: {}.  Search distance: {}.   Search Direction: {}.'.format(words, str(distance_units), str(distance), str(directions)) 
	else:
		return 'Negation feature is turned off.'

@app.callback(
    Output(component_id='selection_summary_3', component_property='style'),
    [Input('negation_words', 'value'),
    Input('negation_words_feature', 'value'),
	Input('negation_words_distance', 'value'),
	Input('negation_words_direction', 'value'),
    Input('negation_distance_units', 'value')]
    )
def update_negation_words_summary_color(input1, input2, distance, directions, distance_units):
	print(directions)
	if input2 == False: #false is on
		words = [" ".join(x.strip().split()) for x in input1.split(',')]
		if (len(words)==1 and words[0] ==""):
			return {'color': 'red'}
		elif (directions == None or directions == []):
			return {'color': 'red'}
		else:
			return {'color': 'black'}

################################################################



def parse_contents(contents, filename):
	content_type, content_string = contents.split(',')

	decoded = base64.b64decode(content_string)
	try:
		if '.csv' in filename:
			# Assume that the user uploaded a CSV file
			df = pd.read_csv(
				io.StringIO(decoded.decode('utf-8')), encoding='utf-8')
		elif '.xls' in filename:
			# Assume that the user uploaded an excel file

			df = pd.read_excel(io.BytesIO(decoded), None)

			if "Sheet1" in df.keys():
				df = df["Sheet1"]
			else:
				df = df[next(iter(df))]
				
		#df = df.replace("empty row", "")

	except Exception as e:
		print(e)
		return None

	return df

############ changing  DAVID 11/13
@app.callback(Output('output-image-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        return 'File uploaded: "{}"'.format(list_of_names)
########################


############ LOADING RAEIN #####################
#@app.callback(Output('loading', 'style'),
#             [Input('search', 'n_clicks')])
#def switch_loading(n_clicks):

#	if n_clicks:

#		return {'padding-left': '40%', 'max-width': '300px', 'display': 'none', 'padding-top': '185%', 'position': 'absolute', 'float':'left', 'z-index':'100'}

#	return {'padding-left': '40%', 'max-width': '300px', 'display': 'none', 'padding-top': '20%', 'position': 'absolute', 'float':'left', 'z-index':'100'}

#@app.callback(Output('loading', 'style'),
#             [Input('upload-data', 'filename')])
#def switch_loading(rows):

#	return {'padding-left': '40%', 'max-width': '300px', 'display': 'none', 'padding-top': '20%', 'position': 'absolute', 'float':'left', 'z-index':'100'}

#################################

#callback table column order
@app.callback(Output('table', 'columns'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename')])
def update_ouput_columns(contents, filename):
	if contents is not None:
		df = parse_contents(contents, filename)
		if df is not None:
			global ls_initial_column_order
			ls_initial_column_order = df.columns.tolist()
			return ls_initial_column_order
		else:
			return []
	else:
		return []

# callback table creation
@app.callback(Output('table', 'rows'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename')])
def update_output(contents, filename):
    if contents is not None:
        df = parse_contents(contents, filename)
        if df is not None:
            global dataFrame
            df = df.fillna('empty row')
            dataFrame = df.to_dict('records')
            return (df.head(50)).to_dict('records')
        else:
            return [{}]
    else:
        return [{}]


#callback update options of filter dropdown
@app.callback(Output('dropdown_table_filterColumn', 'options'),
				[Input('table', 'rows'),
				Input('upload-data', 'contents')],
				  [State('upload-data', 'filename'),
				   State('upload-data', 'last_modified')])
def update_filter_column_options(rows, list_of_contents, list_of_names, list_of_dates):
		#dff = pd.DataFrame(tablerows) # <- problem! dff stays empty even though table was uploaded
		#print "updating... dff empty?:", dff.empty #result is True, labels stay empty
		return [{'label': i, 'value': i} for i in ls_initial_column_order]

#callback update options of filter dropdown
@app.callback(Output('dropdown_table_indexColumn', 'options'),
				[Input('table', 'rows'),
				Input('upload-data', 'contents')],
				  [State('upload-data', 'filename'),
				   State('upload-data', 'last_modified')])
def update_index_column_options(rows, list_of_contents, list_of_names, list_of_dates):
		#dff = pd.DataFrame(tablerows) # <- problem! dff stays empty even though table was uploaded
		#print "updating... dff empty?:", dff.empty #result is True, labels stay empty
		return [{'label': 'None', 'value': ''}] + [{'label': i, 'value': i} for i in ls_initial_column_order]


######################  Keywords DropDown  #######################

#@app.callback(Output('list_keywords', 'options'),
#              [Input('add_keyword', 'n_clicks'),
#			   Input('search_keywords', 'value')])
#def add_keywords(nclicks, text):
#	if nclicks:
#		terms = terms + [{'label': text, 'value': text}]
#		return terms

######################  Disabling #################
#@app.callback(Output('search', 'disabled'),
#              [Input('negation_words_feature', 'value')])
#def update_search_button(negation):
#		return negation

@app.callback(Output('negation_words', 'disabled'),
              [Input('negation_words_feature', 'value')])
def update_negation(negation):
		return negation

@app.callback(Output('negation_words_direction', 'disabled'),
              [Input('negation_words_feature', 'value')])
def update_negation(negation):
		return negation

@app.callback(Output('negation_words_distance', 'disabled'),
              [Input('negation_words_feature', 'value')])
def update_negation(negation):
		return negation

@app.callback(Output('negation_distance_units', 'disabled'),
              [Input('associated_words_feature', 'value')])
def update_associated(negation):
		return negation

@app.callback(Output('associated_words', 'disabled'),
              [Input('associated_words_feature', 'value')])
def update_associated(associated):
		return associated

@app.callback(Output('associated_words_direction', 'disabled'),
              [Input('associated_words_feature', 'value')])
def update_associated(associated):
		return associated

@app.callback(Output('associated_words_distance', 'disabled'),
              [Input('associated_words_feature', 'value')])
def update_associated(associated):
		return associated

@app.callback(Output('associated_distance_units', 'disabled'),
              [Input('associated_words_feature', 'value')])
def update_associated(associated):
		return associated

@app.callback(Output('download-link', 'href'),
              [Input('search', 'n_clicks')])
def update_associated(n_clicks):
		if n_clicks != None:
			return "results.csv"
		else:
			return "#"

@app.callback(Output('download-link-xlsx', 'href'),
              [Input('search', 'n_clicks')])
def update_associated(n_clicks):
		if n_clicks != None:
			return "results.xlsx"
		else:
			return "#"
			
@app.callback(Output('alert', 'displayed'),
              [Input('search', 'n_clicks')])
def display_confirm(n_clicks):
		if n_clicks != None:
			time.sleep(10)
			global error_triggered			
			if error_triggered == 'True':
				print(error_triggered)
				return True
			else:
				print(error_triggered)
				return False
		else:
			print(error_triggered)
			return False

@app.callback(Output('alert', 'message'),
              [Input('alert', 'submit_n_clicks')])
def hide_alert_box(submit_n_clicks):
		#time.sleep(15)
		global error_triggered	
		if submit_n_clicks != None:
				error_triggered = 'False'  
		return 'There was an error. After clicking okay, please refresh your browser and try again.'

######################  BACK END   #######################

@app.callback(Output('results', 'rows'),
              [Input('search', 'n_clicks')],
				[State('dropdown_table_filterColumn', 'value'),
				State('dropdown_table_indexColumn', 'value'),
				State('search_scope', 'value'),
				State('search_keywords', 'value'),
				State('index_keyword', 'value'),
				State('table', 'rows'),
				State('negation_words_feature', 'value'),
				State('negation_words', 'value'),
				State('negation_words_direction', 'value'),
				State('negation_distance_units', 'value'),
				State('negation_words_distance', 'value'),
				State('associated_words_feature', 'value'),
				State('associated_words', 'value'),
				State('associated_words_direction', 'value'),
				State('associated_distance_units', 'value'),
				State('associated_words_distance', 'value'),
				State('keyword_sentences_column', 'value')])				
def update_results(n_clicks, column, index, scope, keywords, index_val, reportsArr, neg, neg_words, neg_dir, neg_units, neg_dis, assoc, assoc_words, assoc_dir, assoc_units, assoc_dis, keyword_sentences_column):

		time.sleep(2)

		global nClicks
		if n_clicks != None: #== nClicks + 1:
			nClicks += 1
			#df = pd.DataFrame(reportsArr)
			global ls_initial_column_order
			df = pd.DataFrame(dataFrame, columns=ls_initial_column_order)

			############ Select index column satisfied rows ##############

			index_val = [" ".join(x.strip().split()) for x in index_val.split(',')]

			if index != "" and index is not None and not (df.dtypes[index] == 'int64' or df.dtypes[index] == 'float64'):
				if len(index_val) == 1:
					df = df.loc[df[index].str.lower() == str(index_val[0]).lower()]
				else:
					frames = []
					for i in index_val:
						temp = df.loc[df[index].str.lower() == str(i).lower()]
						frames.append(temp)

					df = pd.concat(frames)

			elif index != "" and index is not None and (df.dtypes[index] == 'int64' or df.dtypes[index] == 'float64'):
				if len(index_val) == 1:
					df = df.loc[df[index] == float(index_val[0])]
				else:
					frames = []
					for i in index_val:
						temp = df.loc[df[index] == float(i)]
						frames.append(temp)

					df = pd.concat(frames)

			################

			if scope != "":
				scope_results = get_scope(df.columns.get_loc(column), scope, df.values[:])
				#print(len(scope_results), len(df.values[:]), scope_results[:2])
				df = pd.DataFrame(np.append(np.array(scope_results, dtype=object), df.values[:], axis=1), columns=np.concatenate((['Search_Scope'], df.columns)))
				# df = df.fillna('')
				column = 'Search_Scope'

			#print(df.columns)

			if not keyword_sentences_column:
				if not assoc:
					if not neg:
						new_columns = np.concatenate((['TERM_Counts', 'ASSOC_Counts', 'NEG_Counts', 'Keyword_Sentences'], df.columns))
					else:
						new_columns = np.concatenate((['TERM_Counts', 'ASSOC_Counts', 'Keyword_Sentences'], df.columns))
				else:
					if not neg:
						new_columns = np.concatenate((['TERM_Counts', 'NEG_Counts', 'Keyword_Sentences'], df.columns))
					else:
						new_columns = np.concatenate((['TERM_Counts', 'Keyword_Sentences'], df.columns))
			else:
				if not assoc:
					if not neg:
						new_columns = np.concatenate((['TERM_Counts', 'ASSOC_Counts', 'NEG_Counts'], df.columns))
					else:
						new_columns = np.concatenate((['TERM_Counts', 'ASSOC_Counts'], df.columns))
				else:
					if not neg:
						new_columns = np.concatenate((['TERM_Counts', 'NEG_Counts'], df.columns))
					else:
						new_columns = np.concatenate((['TERM_Counts'], df.columns))
			try:
				result = pd.DataFrame(Search(df.columns.get_loc(column), keywords, df.values[:], neg, neg_words, neg_dir, neg_units, neg_dis, assoc, assoc_words, assoc_dir, assoc_units, assoc_dis, keyword_sentences_column), columns=new_columns)
				result = result.replace("empty row", "")
			except Exception as err:
				global error_triggered
				error_triggered = 'True'
				return [{}]
			
			print(list(new_columns))
			global dataFrameResults
			global downloadLink, downloadLinkxls
			dataFrameResults = result.to_dict('records')
			downloadLink = result.to_csv('results.csv', index=False, columns=list(new_columns))
			writer = pd.ExcelWriter('results.xlsx', engine='xlsxwriter')
			downloadLinkxls = result.to_excel(writer, sheet_name='Sheet1', index=False)
			workbook  = writer.book
			worksheet = writer.sheets['Sheet1']

			header_format = workbook.add_format({
						'bold': True,
						'text_wrap': True,
						'valign': 'top',
						'fg_color': '#D7E4BC',
						'border': 1})

			for col_num, value in enumerate(new_columns):
				worksheet.write(0, col_num, value, header_format)

			writer.save()

			return (result.head(50)).to_dict('records')

		else:
			return [{}]

##################################################################################################
# Output Results Statistics:
@app.callback(Output(component_id='output_statistics_1', component_property='children'),
              [Input('results', 'rows')])
def results_statistics_1(rows):
	if rows != [{}]:
		global DataFrameResults
		df_results = pd.DataFrame.from_dict(dataFrameResults)
		records_keywords = len(df_results.loc[df_results['TERM_Counts']>=1])
		records_keywords_perc = round( (100*records_keywords/len(df_results)),2)
		return ('Records containing keywords: \n\t {}    ({}% of {} total records)'.format(str(records_keywords),str(records_keywords_perc), str(len(df_results))))

@app.callback(Output(component_id='output_statistics_3', component_property='children'),
              [Input('results', 'rows')])
def results_statistics_3(rows):
	if rows != [{}]:
		global DataFrameResults
		df_results = pd.DataFrame.from_dict(dataFrameResults)
		if 'ASSOC_Counts' in (df_results.columns.tolist()):
			records_assoc = len(df_results.loc[df_results['ASSOC_Counts']>=1])
			records_assoc_perc = round( (100*records_assoc/len(df_results)),2)
			return ('Records with keywords containing asssociated words within set associated word distance and direction: {}    ({}% of {} total records)'.format(str(records_assoc),str(records_assoc_perc), str(len(df_results))))


@app.callback(Output(component_id='output_statistics_2', component_property='children'),
              [Input('results', 'rows')])
def results_statistics_2(rows):
	if rows != [{}]:
		global DataFrameResults
		df_results = pd.DataFrame.from_dict(dataFrameResults)
		if 'NEG_Counts' in (df_results.columns.tolist()):
			records_negs = len(df_results.loc[df_results['NEG_Counts']>=1])
			records_negs_perc = round( (100*records_negs/len(df_results)),2)
			return ('Records with keywords containing negations within set negation word distance and direction: {}    ({}% of {} total records)'.format(str(records_negs),str(records_negs_perc),str(len(df_results))))

###################################################################################################

#Download link function ################

#@app.callback(Output('download-link', 'href'),
#				[Input('search', 'n_clicks')])
#def update_column_results(n_clicks):
#	global dataFrameResults
#	print(downloadLink)
#	print("data:text/csv;charset=utf-8," + urllib.parse.quote(downloadLink))
#	return "data:text/csv;charset=utf-8," + dataFrameResults # + urllib.parse.quote(downloadLink)

@app.server.route('/results.csv')
def download_csv():
    return flask.send_file('results.csv',
                     mimetype='text/csv',
                     attachment_filename='results.csv',
                     as_attachment=True)

@app.server.route('/results.xlsx')
def download_xlsx():
    return flask.send_file('results.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     attachment_filename='results.xlsx',
                     as_attachment=True,
					 cache_timeout=0)

####################################

#ADDED DAVID ORDERS_COLUMNS
#callback table column order
@app.callback(Output('results', 'columns'),
				[Input('search', 'n_clicks')],
				[State('dropdown_table_filterColumn', 'value'),
				State('dropdown_table_indexColumn', 'value'),
				State('search_scope', 'value'),
				State('search_keywords', 'value'),
				State('index_keyword', 'value'),
				State('table', 'rows'),
				State('negation_words_feature', 'value'),
				State('negation_words', 'value'),
				State('negation_words_direction', 'value'),
				State('negation_distance_units', 'value'),
				State('negation_words_distance', 'value'),
				State('associated_words_feature', 'value'),
				State('associated_words', 'value'),
				State('associated_words_direction', 'value'),
				State('associated_distance_units', 'value'),
				State('associated_words_distance', 'value'),
				State('keyword_sentences_column', 'value')])
def update_column_results(n_clicks, column, index, scope, keywords, index_val, reportsArr, neg, neg_words, neg_dir, neg_units, neg_dis, assoc, assoc_words, assoc_dir, assoc_units, assoc_dis, keyword_sentences_column):
		global nClicks
		if n_clicks != None: #== nClicks + 1:
			#df = pd.DataFrame(reportsArr)
			global ls_initial_column_order
			df = pd.DataFrame(dataFrame, columns=ls_initial_column_order)

			############ Select index column satisfied rows ##############

			index_val = [" ".join(x.strip().split()) for x in index_val.split(',')]

			if index != "" and index is not None and not (df.dtypes[index] == 'int64' or df.dtypes[index] == 'float64'):
				if len(index_val) == 1:
					df = df.loc[df[index].str.lower() == str(index_val[0]).lower()]
				else:
					frames = []
					for i in index_val:
						temp = df.loc[df[index].str.lower() == str(i).lower()]
						frames.append(temp)

					df = pd.concat(frames)

			elif index != "" and index is not None and (df.dtypes[index] == 'int64' or df.dtypes[index] == 'float64'):
				if len(index_val) == 1:
					df = df.loc[df[index] == float(index_val[0])]
				else:
					frames = []
					for i in index_val:
						temp = df.loc[df[index] == float(i)]
						frames.append(temp)

					df = pd.concat(frames)

			################

			if scope != "":
				scope_results = get_scope(df.columns.get_loc(column), scope, df.values[:])
				#print(len(scope_results), len(df.values[:]), scope_results[:2])
				df = pd.DataFrame(np.append(np.array(scope_results, dtype=object), df.values[:], axis=1), columns=np.concatenate((['Search_Scope'], df.columns)))
				column = 'Search_Scope'

			if not keyword_sentences_column:
				if not assoc:
					if not neg:
						new_columns = np.concatenate((['TERM_Counts', 'ASSOC_Counts', 'NEG_Counts', 'Keyword_Sentences'], df.columns))
					else:
						new_columns = np.concatenate((['TERM_Counts', 'ASSOC_Counts', 'Keyword_Sentences'], df.columns))
				else:
					if not neg:
						new_columns = np.concatenate((['TERM_Counts', 'NEG_Counts', 'Keyword_Sentences'], df.columns))
					else:
						new_columns = np.concatenate((['TERM_Counts', 'Keyword_Sentences'], df.columns))
			else:
				if not assoc:
					if not neg:
						new_columns = np.concatenate((['TERM_Counts', 'ASSOC_Counts', 'NEG_Counts'], df.columns))
					else:
						new_columns = np.concatenate((['TERM_Counts', 'ASSOC_Counts'], df.columns))
				else:
					if not neg:
						new_columns = np.concatenate((['TERM_Counts', 'NEG_Counts'], df.columns))
					else:
						new_columns = np.concatenate((['TERM_Counts'], df.columns))
						

			#result = pd.DataFrame(Search(df.columns.get_loc(column), keywords, df.values[:], neg, neg_words, neg_dir, neg_units, neg_dis, assoc, assoc_words, assoc_dir, assoc_units, assoc_dis), columns=new_columns)

			global ls_final_column_order_output
			#ls_final_column_order_output = result.columns.tolist()
			ls_final_column_order_output = new_columns.tolist()

			#ls_final_column_order_output = ls_final_column_order_output[-2:] + ls_final_column_order_output[:-2]

			return ls_final_column_order_output

		else:
			return [] #ls_final_column_order_output

def get_scope(column, scope, reportsArr):

		reports = reportsArr[:, column]

		if scope == "":
			return reports

		#scopes = [" ".join(x.strip().split()) for x in scope.split(',')]
		scopes = [" ".join(x.strip().split()) for x in scope.split('&')]
		print(scopes)

		filtered = []

		for r in reports:
			if isinstance(r, int) or isinstance(r, float) or len(r) < 1 :
				filtered.append([r])
				continue
			StartIndex = 0
			EndIndex = len(r)
			for i, s in enumerate(scopes):

				if i == 0:

					if "information" not in s.lower():
						if "\n" + s + ":" in r:
							StartIndex = r.index("\n" + s + ":")
						elif "\n" + s + " :" in r:
							StartIndex = r.index("\n" + s + " :")
						elif "\n" + s.lower() + ":" in r.lower():
							StartIndex = r.lower().index("\n" + s.lower() + ":")
						elif "\n" + s.lower() + " :" in r.lower():
							StartIndex = r.lower().index("\n" + s.lower() + " :")
						elif s + ":" in r:
							StartIndex = r.index(s + ":")
						elif s + " :" in r:
							StartIndex = r.index(s + " :")
						elif s.lower() + ":" in r.lower():
							StartIndex = r.lower().index(s.lower() + ":")
						elif s.lower() + " :" in r.lower():
							StartIndex = r.lower().index(s.lower() + " :")
							
						if StartIndex < 0 or StartIndex > len(r):
							StartIndex = 0

					else:
						if "\n" + s.lower() + "\n" in r.lower():
							StartIndex = r.lower().index("\n" + s.lower() + "\n")

				if len(scopes) == i + 1:
					if s.lower() == "patient information" and "\nexam information\n" in r.lower():
						EndIndex = r.lower().index("\nexam information\n")

					elif s.lower() == "exam information" and "\nresult information\n" in r.lower():
						EndIndex = r.lower().index("\nresult information\n")

					elif s.lower() == "report" and "\nimpression:" in r.lower():
						EndIndex = r.lower().index("\nimpression:")

					elif s.lower() == "impression" and "\nend of impression" in r.lower():
						EndIndex = r.lower().index("\nend of impression")
						
					#elif s.lower() == "impression" and "\ncritical results were communicated" in r.lower():
						#EndIndex = r.lower().index("\ncritical results were communicated")
						
					#elif s.lower() == "impression" and "\ni, the teaching physician" in r.lower():
						#EndIndex = r.lower().index("\ni, the teaching physician")
					
					elif s.lower() == "impression" and "\napproved by attending" in r.lower():
						EndIndex = r.lower().index("\napproved by attending")
						
					elif s.lower() == "patient information" and " exam information" in r.lower():
						EndIndex = r.lower().index(" exam information")

					elif s.lower() == "exam information" and " result information" in r.lower():
						EndIndex = r.lower().index(" result information\n")

					elif s.lower() == "report" and " impression:" in r.lower():
						EndIndex = r.lower().index(" impression:")

					elif s.lower() == "impression" and " end of impression" in r.lower():
						EndIndex = r.lower().index(" end of impression")
						
					#elif s.lower() == "impression" and "\ncritical results were communicated" in r.lower():
						#EndIndex = r.lower().index("\ncritical results were communicated")
						
					#elif s.lower() == "impression" and "\ni, the teaching physician" in r.lower():
						#EndIndex = r.lower().index("\ni, the teaching physician")
					
					elif s.lower() == "impression" and " approved by attending" in r.lower():
						EndIndex = r.lower().index(" approved by attending")
						
					if EndIndex < 0 or EndIndex > len(r):
						EndIndex = -1

			filtered.append([r[StartIndex:EndIndex]])

		return filtered

def split_into_sentences(text):

		text = " " + text + "  "
		text = text.replace("   "," ")
		text = text.replace("  "," ")
		text = text.replace("\n\n",".<stop>")
		text = text.replace("M.D.","MD")
		text = text.replace("e.g.","eg")
		text = text.replace("i.e.","ie")
		text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
		text = re.sub(digits + "[.]","\\1<prd>",text)
		text = re.sub(digits + " [.]","\\1<prd>",text)
		#text = re.sub(digits + " [.]" + digits,"\\1<prd>\\2",text)
		#text = re.sub(digits + "[.]  " + digits,"\\1<prd>\\2",text)
		#text = re.sub(digits + "[.] " + digits,"\\1<prd>\\2",text)
		#text = re.sub(digits + " [.] " + digits,"\\1<prd>\\2",text)
		#text = re.sub(digits + "[.]  " + alphabets,"\\1<prd>\\2",text)
		#text = re.sub(digits + "[.] " + alphabets,"\\1<prd>\\2",text)
		text = re.sub(alphabets + "[:]  " + alphabets,"\\1<prd>\\2",text)
		text = re.sub(alphabets + "[:] " + alphabets,"\\1<prd>\\2",text)
		text = re.sub(digits + "[:]" + digits,"\\1<prd>\\2",text)
		#text = text.replace(":",".<stop>")

		text = re.sub(prefixes,"\\1<prd>",text)
		text = re.sub(websites,"<prd>\\1",text)
		if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
		text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
		text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
		text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
		text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
		text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
		text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
		text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
		if "”" in text: text = text.replace(".”","”.")
		if "\"" in text: text = text.replace(".\"","\".")
		if "!" in text: text = text.replace("!\"","\"!")
		if "?" in text: text = text.replace("?\"","\"?")
		text = text.replace(".",".<stop>")
		text = text.replace("?","?<stop>")
		text = text.replace("!","!<stop>")
		text = text.replace("<prd>",".")
		sentences = text.split("<stop>")
		sentences = sentences[:-1]
		sentences = [" " + s.strip() + " " for s in sentences]
		return sentences

def Search(column, keywords, reportsArr, neg, neg_words, neg_dir, neg_units, neg_dis, assoc, assoc_words, assoc_dir, assoc_units, assoc_dis, keyword_sentences_column):

		reportsArr = np.asarray(reportsArr)

		#keywords = keywords.replace(",", " ")

		#keywords = (keywords.strip()).split()

		reports = reportsArr[:, column]

		counts, neg_counts, assoc_counts = [], [], []

		keywords = [" ".join(x.replace("'", "").strip().split()) for x in keywords.split(',')]
		neg_words = [" ".join(x.replace("'", "").strip().split()) for x in neg_words.split(',')]
		assoc_words = [" ".join(x.replace("'", "").strip().split()) for x in assoc_words.split(',')]
		if keywords[-1] =="":
			keywords.pop()
		if neg_words[-1] =="":
			neg_words.pop()
		if assoc_words[-1] =="":
			assoc_words.pop()
		
		for punc in punctuation:
			for index, keyword in enumerate(keywords):
				keywords[index] = keyword.replace(punc, ' ' + punc + ' ')

			for index, keyword in enumerate(neg_words):
				neg_words[index] = keyword.replace(punc, ' ' + punc + ' ')

			for index, keyword in enumerate(assoc_words):
				assoc_words[index] = keyword.replace(punc, ' ' + punc + ' ')
		
		if '' in keywords:
			keywords = keywords.remove('')
		if '' in neg_words:
			neg_words = neg_words.remove('')
		if '' in assoc_words:
			assoc_words = assoc_words.remove('')

		print(keywords, neg_words, assoc_words)

		keyword_sentences_report = []
		keyword_sentences_report = np.array(keyword_sentences_report)

		for index, report in enumerate(reports):

			counts.append([0])
			neg_counts.append([0])
			assoc_counts.append([0])

			if isinstance(report, int) or isinstance(report, float) or len(report) < 1 :
				continue

			####################### LOWER CASE #############################

			report = report + " . "
			report = report.lower()

			###########################################

			###### add space before punctuation #########
			for punc in punctuation:
				report = report.replace(punc, ' ' + punc + ' ')

			###### Eliminate double spaces ######
			report = report.strip()
			report = " ".join(report.split())
			report = " " + report

			keyword_sentences = []
			keyword_sentences = np.array(keyword_sentences)
			
			sentences = split_into_sentences(report)

			for keyword in keywords:

				####################### LOWER CASE #############################

				keyword = keyword.lower()

				###########################################

				keyword = " " + keyword + " "
				if not isinstance(report, numbers.Number) and keyword in report + " ":
					counts[-1][0] += (" " + report + " ").count(keyword)
				elif isinstance(report, numbers.Number) and keyword in str(report) + " ":
					counts[-1][0] += (" " + str(report) + " ").count(keyword)
				else:
					continue

                ############ Extra column for sentences with keyword #############
				if not keyword_sentences_column:
					for i, sentence in enumerate(sentences):
						# print(sentence)
						if keyword in " " + sentence + " ":
							if len(keyword_sentences) == 0:
								keyword_sentences = np.array([keyword + " - " + sentence + "\n\n"]) #							keyword_sentences = np.array([str(i) + " - " + keyword + " - " + sentence + "\n\n"])
								#keyword_sentences = np.array([keyword + ": " + (sentences[max(0,i-1)] if max(0,i-1) != i else "") + "\n" + sentence + "\n" + (sentences[min(len(sentences)-1,i+1)] if min(len(sentences)-1,i+1) != i else "") + "\n\n"])
							else:
								keyword_sentences = np.append(keyword_sentences, keyword + " - " + sentence + "\n\n") #keyword_sentences = np.append(keyword_sentences, str(i) + " - " + keyword + " - " + sentence + "\n\n")
								#keyword_sentences = np.append(keyword_sentences, keyword + ": " + (sentences[max(0,i-1)] if max(0,i-1) != i else "") + "\n" + sentence + "\n" + (sentences[min(len(sentences)-1,i+1)] if min(len(sentences)-1,i+1) != i else "") + "\n\n")
							# print(keyword_sentences)

                #########################################################

				if not neg:
					######## Negation by words ##############
					if neg_units == "Words":

						#sentences = split_into_sentences(report)

						for i, sentence in enumerate(sentences):
							while keyword in sentence + " ":

								beginString = sentence.find(keyword) + len(keyword) + 1
								endString = sentence.find(keyword) - 1
								for i in range(neg_dis):
									if 'Before' in neg_dir:
										endString = sentence.rfind(' ', 0, endString)
									if 'After' in neg_dir:
										beginString = sentence.find(' ', beginString, len(sentence)) + 1

								if 'After' in assoc_dir and sentence[sentence.find(keyword) + len(keyword) + 1:].find(keyword) > 0:
									beginString = min(beginString, sentence.find(keyword) + len(keyword) + 1 + sentence[sentence.find(keyword) + len(keyword) + 1:].find(keyword))
								if 'Before' in assoc_dir and sentence[endString:beginString].rfind(keyword[0]+'~'+keyword[1:]) > 0:
									endString = max(endString, endString + sentence[endString:beginString].rfind(keyword[0]+'~'+keyword[1:]) + len(keyword) + 1)

								if type(neg_words) != type([]):
									neg_words = [neg_words]
								for nword in neg_words:

									####################### LOWER CASE #############################

									nword = nword.lower()

									###########################################

									#print(keyword, nword)
									#print("Before: ", report[endString + 1:report.find(keyword)])
									#print("After: ", report[report.find(keyword)+len(keyword):beginString - 1])
									if ('Before' in neg_dir or 'After' in neg_dir) and \
										(" " + nword + " " in " " + sentence[endString + 1:sentence.find(keyword)] + " " or " " + nword + " " in " " + sentence[sentence.find(keyword)+len(keyword):beginString - 1] + " "):
										neg_counts[-1][0] += 1

								sentence = sentence[:sentence.find(keyword)+1] + '~' + sentence[sentence.find(keyword)+1:]


					######## Negation by sentences ##############
					else:
						#sentences = split_into_sentences(report)

						for i, sentence in enumerate(sentences):
							if keyword in sentence + " ":
								for nword in neg_words:

									####################### LOWER CASE #############################

									nword = nword.lower()

									###########################################

									if neg_dis == 0 and " " + nword + " " in sentences[i] + " ":
										neg_counts[-1][0] += 1
										continue
									if ('Before' in neg_dir):
										for j in sentences[max(0, i - neg_dis): i]:
											if " " + nword + " " in " " + j + " ":
												neg_counts[-1][0] += 1
									if ('After' in neg_dir):
										for j in sentences[i+1: min(len(sentences), i + neg_dis + 1)]:
											if " " + nword + " " in " " + j + " ":
												neg_counts[-1][0] += 1

				if not assoc:
					######## Association by words ##############
					if assoc_units == "Words":

						#sentences = split_into_sentences(report)

						for i, sentence in enumerate(sentences):
							if index < 235:
								print(sentence)
							while keyword in sentence + " ":

								beginString = sentence.find(keyword) + len(keyword) + 1
								endString = sentence.find(keyword) - 1
								for i in range(assoc_dis):
									if 'Before' in assoc_dir:
										endString = sentence.rfind(' ', 0, endString)
									if 'After' in assoc_dir:
										beginString = sentence.find(' ', beginString, len(sentence)) + 1

								if index < 235:
									print(sentence[endString:beginString])

								if 'After' in assoc_dir and sentence[sentence.find(keyword) + len(keyword) + 1:].find(keyword) > 0:
									beginString = min(beginString, sentence.find(keyword) + len(keyword) + 1 + sentence[sentence.find(keyword) + len(keyword) + 1:].find(keyword))
								if 'Before' in assoc_dir and sentence[endString:beginString].rfind(keyword[0]+'~'+keyword[1:]) > 0:
									endString = max(endString, endString + sentence[endString:beginString].rfind(keyword[0]+'~'+keyword[1:]) + len(keyword) + 1)

								if index < 235:
									print(sentence[endString:beginString])

								if type(assoc_words) != type([]):
									assoc_words = [assoc_words]
								for aword in assoc_words:

									####################### LOWER CASE #############################

									aword = aword.lower()

									###########################################

									if ('Before' in assoc_dir or 'After' in assoc_dir) and \
										(" " + aword + " " in " " + sentence[endString + 1:sentence.find(keyword)] + " " or " " + aword + " " in " " + sentence[sentence.find(keyword)+len(keyword):beginString - 1] + " "):
										assoc_counts[-1][0] += 1

								sentence = sentence[:sentence.find(keyword)+1] + '~' + sentence[sentence.find(keyword)+1:]


					######## Association by sentences ##############
					else:
						#sentences = split_into_sentences(report)

						for i, sentence in enumerate(sentences):
							if keyword in sentence + " ":
								# print()
								# print(i, keyword, sentence)
								# print()

								for aword in assoc_words:

									####################### LOWER CASE #############################

									aword = aword.lower()

									###########################################

									if assoc_dis == 0 and " " + aword + " " in " " + sentences[i] + " ":
										assoc_counts[-1][0] += 1
										continue
									if ('Before' in assoc_dir):
										for j in sentences[max(0, i - assoc_dis): i]:
											if " " + aword + " " in " " + j + " ":
												assoc_counts[-1][0] += 1
									if ('After' in assoc_dir):
										for j in sentences[i+1: min(len(sentences), i + assoc_dis + 1)]:
											if " " + aword + " " in " " + j + " ":
												assoc_counts[-1][0] += 1

			# if report == '':
			# 	print(np.array([" ".join(keyword_sentences)]))
			# 	return
			if not keyword_sentences_column:
				if len(keyword_sentences) == 0:
					keyword_sentences = np.array([""])
				# print(keyword_sentences)
				if len(keyword_sentences_report) == 0:
					keyword_sentences_report = np.array([" ".join(keyword_sentences)])
				else:
					#if len(keyword_sentences) > 1:
						#print(keyword_sentences_report)
						#print("----------------------------------------")
						#print(keyword_sentences)
					keyword_sentences_report = np.append(keyword_sentences_report, np.array([" ".join(keyword_sentences)]), axis=0)
					#if len(keyword_sentences) > 1:
						#print("----------------------------------------")
						#print(keyword_sentences_report)
						#print("----------------------------------------")
				# print("keyword_sentences:", np.shape(keyword_sentences))
				# print("keyword_sentences_report:", np.shape(keyword_sentences_report))

		counts = np.array(counts, dtype=object)
		neg_counts = np.array(neg_counts, dtype=object)
		assoc_counts = np.array(assoc_counts, dtype=object)
		keyword_sentences_report = np.array(keyword_sentences_report, dtype=object)


		if not assoc:
			if not neg:
				if not keyword_sentences_column:			
					result = np.append(np.expand_dims(keyword_sentences_report, axis=1), reportsArr, axis=1)
					result = np.append(neg_counts, result, axis=1)
				else:
					result = np.append(neg_counts, reportsArr, axis=1)
				result = np.append(assoc_counts, result, axis=1)
				result = np.append(counts, result, axis=1)

			else:
				if not keyword_sentences_column:			
					result = np.append(np.expand_dims(keyword_sentences_report, axis=1), reportsArr, axis=1)
					result = np.append(assoc_counts, result, axis=1)
				else:
					result = np.append(assoc_counts, reportsArr, axis=1)
				result = np.append(counts, result, axis=1)
		else:
			if not neg:
				if not keyword_sentences_column:			
					result = np.append(np.expand_dims(keyword_sentences_report, axis=1), reportsArr, axis=1)
					result = np.append(neg_counts, result, axis=1)
				else:
					result = np.append(neg_counts, reportsArr, axis=1)
				result = np.append(counts, result, axis=1)

			else:
				# print(np.shape(reportsArr), np.shape(np.expand_dims(keyword_sentences_report, axis=1)))
				if not keyword_sentences_column:			
					result = np.append(np.expand_dims(keyword_sentences_report, axis=1), reportsArr, axis=1)
					result = np.append(counts, result, axis=1)
				else:
					result = np.append(counts, reportsArr, axis=1)

		return result


#############################################

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

if __name__ == '__main__':
	app.run_server(debug=True)
