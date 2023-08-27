# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask,jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app=Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def Home():
    """List all available api routes"""
    return (
        f"Available Routes:<br/>"
        f"Precipation data:/api/v1.0/precipitation<br/>"
        f"All Stations:/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate/enddate<br/>"
        f"Add the start and end date in the format YYYY-MM-DD"
        
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipation measure and the date"""
    #  Perform a query to retrieve the data and precipitation scores
    # Calculate the date one year from the last date in data set.
    year = dt.date(2017,8,23)-dt.timedelta(days=365)

    data=session.query(measurement.date,measurement.prcp).filter(measurement.date>=year).all()
    
    session.close()

    # Convert 
    all_precipataion = dict(data)

    return jsonify(all_precipataion )

@app.route("/api/v1.0/stations")
def stations():
    
    # Create our session (link) from Python to DB 
    session = Session(engine)

    """Return all station data"""

    # Perform a query to retrieve all stations 
    all_stations = session.query(station.station, station.name).all()
    
    # Convert this data into a list 
    stn_list = list(np.ravel(all_stations))
   
    return jsonify(stn_list)

    session.close()

    # Convert this data into a list 
    #     stations= []
    #     for station, name in all_stations :
    #         station_dict = {}
    #         station_dict["station"] = station
    #         station_dict["name"] = name
    #     stations.append(station_dict)

    #     return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to DB 
    session = Session(engine)  
      
    # active station for the last year 

    results = session.query(measurement.date, measurement.tobs)\
        .filter(measurement.station == 'USC00519281')\
        .filter(measurement.date.between('2016-08-23', '2017-08-23'))\
        .order_by(measurement.date).all()
    session.close()

    temp_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperature"] = tobs
        temp_data.append(tobs_dict)

    return jsonify(temp_data)
  
@app.route("/api/v1.0/<start>")
def start(start):

    # Create our session (link) from Python to DB 
    session = Session(engine) 

    """Return a list of TMIN, TMAX, & TAVG for all dates >= to start date."""
    session = Session(engine)

    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    results1 = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
        .filter(measurement.date >= start_date).all()
    
    session.close()

    start_tobs_data = []
    for min, max, avg in results1:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Max"] = max
        tobs_dict["Avg"] = avg
        start_tobs_data.append(tobs_dict)

    return jsonify(start_tobs_data)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a list of TMIN, TMAX, & TAVG for the dates from the start date to the end date, inclusive.."""

# Create our session (link) from Python to DB 
    session = Session(engine)  

    start = dt.datetime.strptime(start, '%Y-%m-%d')
    end = dt.datetime.strptime(end, '%Y-%m-%d')
    results2 = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
        .filter(measurement.date.between(start, end)).all()
    
    session.close()

    start_to_end = []
    for min, max, avg in results2:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Max"] = max
        tobs_dict["Avg"] = avg
        start_to_end.append(tobs_dict)

    return jsonify(start_to_end)

if __name__ == '__main__':
    app.run(debug=True)
