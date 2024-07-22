# Import the dependencies.

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime, timedelta

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
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    
    '''Available api routes'''
    return ("""
    <h1>This is a climate app</h1>
    <h3>Available Routes:</h3>
    <ul>
        <li><a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></li>
        <li><a href="/api/v1.0/stations">/api/v1.0/stations</a></li>
        <li><a href="/api/v1.0/tobs">/api/v1.0/tobs</a></li>
        <li>/api/v1.0/&lt;start&gt;</li>
        <li>/api/v1.0/&lt;start&gt;/&lt;end&gt;</li>
    </ul>
    """)


#Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d').date()
    one_year_ago = recent_date - timedelta(days=365)
    precipitation_r = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).all()
    session.close()

    precipitation_dic = {date: prcp for date, prcp in precipitation_r}
    return jsonify(precipitation_dic)


#Stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.name,station.station).all()
    session.close()

    station_list = [{"station_id":station[0],"name":station[1]} for station in results]
    return jsonify(station_list)


#Tobs
@app.route("/api/v1.0/tobs")
def tobs():
    # defined station with most activity
    most_active_station = 'USC00519281'
    session = Session(engine)
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d').date()
    one_year_ago = recent_date - timedelta(days=365)
    temperature_12=session.query(measurement.date,measurement.tobs).filter(measurement.date>=one_year_ago).filter(measurement.date<=most_recent_date).filter(measurement.station == most_active_station).all()
    session.close()
    
    tobs_dic = {date: tobs for date, tobs in temperature_12}
    return jsonify(tobs_dic)


#Start
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    result =session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_date).all()
    session.close()

    temp = list(result[0])
    return jsonify(temp)


#Start_end
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    result =session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()

    temp = list(result[0])
    return jsonify(temp)



if __name__ == "__main__":
    app.run(debug=True)
