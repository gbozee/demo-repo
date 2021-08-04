import json
from flask import Flask, jsonify, request,render_template
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine


app = Flask(__name__)
# the connection string is as a result of mysql-connector-python
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+mysqlconnector://root:somewordpress@localhost:3306/wordpress"
db = SQLAlchemy(app)
Base = automap_base(db.Model)

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
Base.prepare(engine, reflect=True)

# pull the tables from the database
States = Base.classes.states
Party = Base.classes.party
PollingUnit = Base.classes.polling_unit
LGA = Base.classes.lga
Ward = Base.classes.ward
AnnouncedPUResult = Base.classes.announced_pu_results
AnnouncedLgaResult = Base.classes.announced_lga_results


@app.route("/")
def hello_world():
    lga = LGA.query.all()
    # data = AnnouncedPUResult.query.all()
    # result = [
    #     {
    #         "score": x.party_score,
    #         "date": str(x.date_entered),
    #         "name": x.party_abbreviation,
    #     }
    #     for x in data
    # ]
    # return jsonify({"data": result}), 200
    return render_template('index.html',lgas=lga)


def send_result(lga):
    lga_polling_units = PollingUnit.query.filter(PollingUnit.lga_id == lga.lga_id).all()
    polling_ids = [x.uniqueid for x in lga_polling_units]
    results = AnnouncedPUResult.query.filter(
        AnnouncedPUResult.polling_unit_uniqueid.in_(polling_ids)
    ).all()
    total_result = sum([x.party_score for x in results])
    estimated_result = AnnouncedLgaResult.query.filter(
        AnnouncedLgaResult.lga_name == lga.lga_id
    ).first()
    return {
        "lga": lga.lga_name,
        "calculated_total": total_result,
        "estimated_total": estimated_result.party_score,
    }


@app.route("/result", methods=["POST"])
def total_result():
    data = json.loads(request.data)
    lga = LGA.query.filter(LGA.lga_name == data.get("lga")).first()
    lga_polling_units = PollingUnit.query.filter(PollingUnit.lga_id == lga.lga_id).all()
    polling_ids = [x.uniqueid for x in lga_polling_units]
    results = AnnouncedPUResult.query.filter(
        AnnouncedPUResult.polling_unit_uniqueid.in_(polling_ids)
    ).all()
    total_result = sum([x.party_score for x in results])
    estimated_result = AnnouncedLgaResult.query.filter(
        AnnouncedLgaResult.lga_name == lga.lga_id
    ).first()
    # lgas = LGA.query.all()
    # results = [send_result(x) for x in lgas]
    return jsonify(results), 200
    return (
        jsonify(
            {
                "lga": data.get("lga"),
                "calculated_total": total_result,
                "estimated_total": estimated_result.party_score,
            }
        ),
        200,
    )
