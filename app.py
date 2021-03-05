import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///hawaii.sqlite",connect_args={'check_same_thread':False})


# reflect the database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# # Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask
from flask import Flask, jsonify

app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():

    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    prcp_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).order_by(Measurement.date.desc()).all()
        
    json_prcp = []
    for date, prcp in prcp_query:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        json_prcp.append(prcp_dict)
        
    return jsonify(json_prcp)

@app.route("/api/v1.0/stations")
def stations():
    station_query = session.query(Station.station, Station.name).all()

    json_station = []
    for station, name in station_query:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        json_station.append(station_dict)

    return jsonify(json_station)

@app.route("/api/v1.0/tobs")
def tobs():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    tobs_query = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()

    json_tobs = []
    for date, tobs in tobs_query:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        json_tobs.append(tobs_dict)
        
    return jsonify(json_tobs)

@app.route("/api/v1.0/<start>")
def start_route(start):
    search_date = dt.datetime.strptime(start, '%Y-%m-%d')
    start = search_date
    start_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    json_start = list(np.ravel(start_query))
    return jsonify(json_start)

@app.route("/api/v1.0/<start>/<end>")
def both_route(start,end):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    start = start_date
    end = end_date
    both_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    json_both = list(np.ravel(both_query))
    return jsonify(json_both)


if __name__ == "__main__":
    app.run(debug=True)