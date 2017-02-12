from flask import Flask, request, jsonify, make_response

import pandas as pd
import requests
import time
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

import datetime
import io
import random

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter


vehicle_url = 'http://ris.azurewebsites.net/vehicles.json'

r = requests.get(vehicle_url)
df = pd.DataFrame(r.json())

## get columns in order
df = df[['vehicleId', 'latitude',  'longitude',  'route',  'course', 'bearing', 'headsign']]

app = Flask(__name__)


@app.route('/')
def index():
	return '<h1>APIs Project</h1>'


@app.route('/vehicles')
def getVehicles():
	'''/vehicles ◾returns json information for all vehicles'''
	return df.to_json(orient='records')


@app.route('/routes/plot')
def plotRoutes():
	''' /routes/plot returns a plot of the location of all vehicles colored by route including legend'''
	df_slice = df[(df.longitude != 0) & (df.latitude != 0)]
	gb = df_slice.groupby('route')
	df_dict = {key: gb.get_group(key) for key in gb.groups.keys()}

	fig = plt.figure(figsize=(15,15))
	#df_slice.plot.scatter(x='latitude', y='longitude', figsize=(10,10))
	for route, dfg in sorted(df_dict.items()):
		plt.scatter(x=dfg['latitude'], y=dfg['longitude'], label=route)
	
	plt.legend(title='Route:')
	plt.xlabel('latitude')
	plt.ylabel('longitude')

	canvas = FigureCanvas(fig)
	png_output = io.BytesIO()
	canvas.print_png(png_output)
	response = make_response(png_output.getvalue())
	response.headers['Content-Type'] = 'image/png'
	return response
	


## TODO: change json output to strcutured one >> route: {vehicles....}
@app.route('/routes')
def getRoutes():
	'''/routes returns json information for all vehicles grouped by route'''
	
	'''
	#df_list = [gb.get_group(key) for key in gb.groups.keys()]
	#concated_routes = pd.concat(df_list)
	#return concated_routes.to_json(orient='records')
	df_dict = {key: gb.get_group(key).to_json() for key in gb.groups.keys()}

	#structured_routes = pd.concat(df_dict, keys=gb.groups.keys())
	#return structured_routes.to_json(orient='records')
	'''
	# group by route, 
	gb = df.groupby('route')
	# then construct strcutured dict which contains  with dataframes converted to dicts
	df_dict = {str(key): gb.get_group(key).to_dict(orient='records') for key in gb.groups.keys()}
	return json.dumps(df_dict, sort_keys=True)


@app.route('/routes/<int:id>')
def getRoute(id):
	'''/routes/<int:id> ◾returns json information for the vehicles on route id'''
	gb = df.groupby('route')
	return gb.get_group(id).to_json(orient='records')



if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)