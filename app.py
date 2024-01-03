# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
#1. /
#Start at the homepage.
#List all the available routes.
@app.route("/")

def welcome():
    """Welcome to the Hawaii Climate API!<br/>"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter start date as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter the start date and end date as YYYY-MM-DD/YYYY-MM-DD)<br/>"
    )

#2. /api/v1.0/precipitation
#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")

def precipitation():
    session = Session(engine)

    one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    last_date = dt.date(one_year.year, one_year.month, one_year.day)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_date).order_by(Measurement.date).all()

    session.close()

    p_dict = dict(results)

    return jsonify(p_dict)

#3. /api/v1.0/stations
#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")

def stations():
    session = Session(engine)

    stat = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]

    results = session.query(*stat).all()

    session.close()

    stations = []
    for station, name, lat, long, elev in results:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Long"] = long
        station_dict["Elevation"] = elev
        stations.append(station_dict)

    return jsonify(stations)

#4. /api/v1.0/tobs
#Query the dates and temperature observations of the most-active station for the previous year of data.
#Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")

def tobs():
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.station == 'USC00519281').all()
    session.close()

    tob_temp = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tob_temp.append(tobs_dict)
    
    return jsonify(tob_temp)

#5. /api/v1.0/<start> and /api/v1.0/<start>/<end>
#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>")

def temp_start(start):
        session = Session(engine)
        
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start_date).all()
        
        session.close()

        temp_starts = []
        for min_temp, max_temp, avg_temp in results:
            start_dict = {}
            start_dict["Minimum Temperature"] = min_temp
            start_dict["Maximum Temperature"] = max_temp
            start_dict["Average Temperature"] = avg_temp
            temp_starts.append(start_dict)

        return jsonify(temp_starts)

@app.route("/api/v1.0/<start>/<end>")

def temp_range(start,end):
    session = Session(engine)

    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date).\
    filter(Measurement.date <= end_date).all()
    session.close()

    temp_ranges = []
    for min_temp, max_temp, avg_temp in results:
        range_dict = {}
        range_dict["Minimum Temperature"] = min_temp
        range_dict["Maximum Temperature"] = max_temp
        range_dict["Average Temperature"] = avg_temp
        temp_ranges.append(range_dict)
    
    return jsonify(temp_ranges)

if __name__ == '__main__':
    app.run(debug=True)