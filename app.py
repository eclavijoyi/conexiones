from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@localhost/{os.getenv('DB_NAME')}"
db = SQLAlchemy(app)

class Comision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cant = db.Column(db.Integer)
    costo_conecion = db.Column(db.Float)
    id_vendedor = db.Column(db.Integer, db.ForeignKey('vendedor.id_vendedor'))
    fecha = db.Column(db.DateTime)

class Vendedor(db.Model):
    id_vendedor = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(50))
    comisiones = db.relationship('Comision', backref='vendedor', lazy=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resultados', methods=['POST'])
def resultados():
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    results = db.session.query(
        Vendedor.Nombre.label('vendedora'),
        db.func.sum(Comision.cant).label('Total_Conexiones'),
        db.func.sum(Comision.cant * Comision.costo_conecion).label('total')
    ).join(Comision).filter(
        Comision.fecha.between(start_date, end_date)
    ).group_by(Vendedor.Nombre).order_by(db.desc('total')).all()

    return render_template('resultados.html', results=results)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
