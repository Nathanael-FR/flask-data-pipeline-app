from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import plotly.express as px
import pandas as pd
from config import Config
from datetime import datetime, timedelta
import plotly.graph_objects as go

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

class Eco2mix(db.Model):
    __tablename__ = 'eco2mix_data'
    id = db.Column(db.Integer, primary_key=True)
    date_heures = db.Column(db.DateTime)
    date = db.Column(db.Date)
    heures = db.Column(db.Time)
    consommation = db.Column(db.Integer)
    prevision_j_1 = db.Column(db.Integer)
    prevision_j = db.Column(db.Integer)
    fioul = db.Column(db.Integer)
    charbon = db.Column(db.Integer)
    gaz = db.Column(db.Integer)
    nucleaire = db.Column(db.Integer)
    eolien = db.Column(db.Integer)
    solaire = db.Column(db.Integer)
    hydraulique = db.Column(db.Integer)
    pompage = db.Column(db.Integer)
    bioenergies = db.Column(db.Integer)
    ech_physiques = db.Column(db.Integer)
    taux_de_co2 = db.Column(db.Integer)
    ech_comm_angleterre = db.Column(db.Integer)
    ech_comm_espagne = db.Column(db.Integer)
    ech_comm_italie = db.Column(db.Integer)
    ech_comm_suisse = db.Column(db.Integer)
    ech_comm_allemagne_belgique = db.Column(db.Integer)
    fioul_tac = db.Column(db.Integer)
    fioul_cogen = db.Column(db.Integer)
    fioul_autres = db.Column(db.Integer)
    gaz_tac = db.Column(db.Integer)
    gaz_cogen = db.Column(db.Integer)
    gaz_ccg = db.Column(db.Integer)
    gaz_autres = db.Column(db.Integer)
    hydraulique_fildeleau_eclusee = db.Column(db.Integer)
    hydraulique_lacs = db.Column(db.Integer)
    hydraulique_step_turbinage = db.Column(db.Integer)
    bioenergies_dechets = db.Column(db.Integer)
    bioenergies_biomasse = db.Column(db.Integer)
    bioenergies_biogaz = db.Column(db.Integer)
    stockage_batterie = db.Column(db.Integer)
    destockage_batterie = db.Column(db.Integer)
    eolien_terrestre = db.Column(db.Integer)
    eolien_offshore = db.Column(db.Integer)

@app.route('/')
def index():

    date = datetime.now() - timedelta(days=1)
    data = Eco2mix.query.filter_by(date=date.date()).all()

    df = pd.DataFrame([(d.heures, d.fioul, d.charbon, d.gaz, d.nucleaire, d.eolien, d.solaire, d.hydraulique, d.bioenergies) for d in data], 
                      columns=['heures', 'fioul', 'charbon', 'gaz', 'nucleaire', 'eolien', 'solaire', 'hydraulique', 'bioenergies'])

    df['heures'] = pd.to_datetime(df['heures'], format='%H:%M:%S').dt.strftime('%H:%M')
    df = df.sort_values(by='heures')

    heures_data = df['heures'].tolist()
    fioul_data = df['fioul'].tolist()
    charbon_data = df['charbon'].tolist()
    gaz_data = df['gaz'].tolist()
    nucleaire_data = df['nucleaire'].tolist()
    eolien_data = df['eolien'].tolist()
    solaire_data = df['solaire'].tolist()
    hydraulique_data = df['hydraulique'].tolist()
    bioenergies_data = df['bioenergies'].tolist()

    return render_template('index.html', 
                           heures_data=heures_data, 
                           fioul_data=fioul_data,
                           charbon_data=charbon_data,
                           gaz_data=gaz_data,
                           nucleaire_data=nucleaire_data,
                           eolien_data=eolien_data,
                           solaire_data=solaire_data,
                           hydraulique_data=hydraulique_data,
                           bioenergies_data=bioenergies_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
