import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext import automap
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# DB/ORM
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#flask
app = Flask(__name__)

#home page that displays available routes
@app.route("/")
def home():
    print("home() function called")
    return (
        f"Home Page<br />"
        f"Available routes: <br />"
        f"/api/v1.0/precipitation <br />"
        f"/api/v1.0/stations <br />"
        f"/api/v1.0/tobs <br />"
        f"/api/v1.0/<start> <br />"
        f"/api/v1.0/<start>/<end> <br />"
    )

# prcp page that returns json of query using date as key and prcp as value
@app.route("/api/v1.0/precipitation")
def precipitation():
    # query
    session = Session(engine)
    
    first_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year).filter()
    session.close()

    #convert to json
    precipitation = []

    for date, prcp in results:
        dictionary = {}
        dictionary["Date"] = date
        dictionary["Precipitation"] = prcp
        precipitation.append(dictionary)

    return jsonify(precipitation)

# stations page that returns a json list of stations
@app.route("/api/v1.0/stations")
def stations():
    #query
    session = Session(engine)

    results = session.query(Station.name).all()
    session.close()
    #convert
    station_names = list(np.ravel(results))
    return jsonify(station_names)

# tobs page that returns a json list of temp observations for the previous year for the most\
# active station
@app.route("/api/v1.0/tobs")
def tobs():
    #query
    session = Session(engine)

    active_st = session.query(Measurement.station, func.count(Measurement.id)).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).first()
    st_date = session.query(Measurement.date).filter(Measurement.station == active_st[0]).order_by(Measurement.date.desc()).first()
    q_date = dt.date(2017, 8, 18) - dt.timedelta(365)

    selection2 = [Measurement.date, Measurement.tobs]
    results = session.query(*selection2).filter(Measurement.station == active_st[0]).filter(Measurement.date >= q_date).all()
    session.close()

    # convert
    tobs = list(np.ravel(results))
    return jsonify(tobs)

# returns a json list of avg, min, max temp for all dates >= start date
@app.route("/api/v1.0/<start>")
def start(start):
    #query
    session = Session(engine)
    
    lo = session.query(Measurement.date, func.min(Measurement.tobs)).filter(Measurement.date >= start).all()
    hi = session.query(Measurement.date, func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    avg = session.query(Measurement.date, func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    #convert
    start_dt = list(np.ravel(results))
    return jsonify(start_dt)

# returns a json list of min, max, avg temp for all dates between start and end date inclusive
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    
    lo = session.query(Measurement.date, func.min(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    hi = session.query(Measurement.date, func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    avg = session.query(Measurement.date, func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    #convert
    end_dt = list(np.ravel(results))
    return jsonify(end_dt)

if __name__ == "__main__":
    app.run(debug=True)