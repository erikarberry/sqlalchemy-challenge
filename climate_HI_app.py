import numpy as np
import datetime as dt
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.Station
Measurements = Base.classes.measurements

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home_page():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs/<br/>"
        f"/api/v1.0/start/<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query all dates and precipitation from prev year
    #last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    last_year = dt.date(2017,8, 23) - dt.timedelta(days = 365)
    results = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date > last_year).\
        order_by(Measurements.date).all()
    
    # Create a dictionary using date as the key and prcp as the value.
    prcp_by_date = []
    for rain in results:
        rain_dict = {}
        rain_dict["date"] = rain.date
        rain_dict["prcp"] = rain.prcp
        prcp_by_date.append(rain_dict)

    # Return the JSON representation of the directory
    return jsonify(prcp_by_date)

@app.route("/api/v1.0/stations")
def stations():
    # Query stations
    results = session.query(Station.name).all()
    # Convert list of tuples into normal list
    station_names = list(np.ravel(results))
    # Return the JSON representation of the directory
    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query all dates and temps from prev year
    #last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    last_year = dt.date(2017,8, 23) - dt.timedelta(days = 365)
    # Query all temperature observations
    results = session.query(Measurements.tobs).filter(Measurements.date > last_year).\
        order_by(Measurements.date).all()
    # Convert list of tuples into normal list
    temps = list(np.ravel(results))
    # Return the JSON representation of the directory
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Query temperature observations
    results = session.query(func.min(Measurements.tobs), func.max(Measurements.tobs), func.avg(Measurements.tobs)).\
        filter(Measurements.date >= start).all()
    # Convert list of tuples into normal list
    start_temps = list(np.ravel(results))
    # Return the JSON representation of the directory
    return jsonify(start_temps)

@app.route("/api/v1.0/<start>/<end>")
def trip_range(start, end):
    # Query temperature observations
    results = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start).\
        filter(Measurements.date <= end).all()
    # Convert list of tuples into normal list
    end_temps = list(np.ravel(results))
    # Return the JSON representation of the directory
    return jsonify(end_temps)


if __name__ == '__main__':
    app.run(debug=True)
