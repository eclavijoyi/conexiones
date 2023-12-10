from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime
import os
import time
import mysql.connector

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
db = SQLAlchemy(app)

# Configuración de MySQL
mysql_host = os.getenv('DB_HOST')
mysql_port = int(os.getenv('DB_PORT'))
mysql_user = os.getenv('DB_USER')
mysql_password = os.getenv('DB_PASSWORD')
mysql_db = os.getenv('DB_NAME')

# Función para esperar la disponibilidad de MySQL
def wait_for_mysql(host, port, user, password, database, max_attempts=30, sleep_time=5):
    attempts = 0
    while attempts < max_attempts:
        try:
            # Intentar conectarse a MySQL
            mysql.connector.connect(host=host, port=port, user=user, password=password, database=database)
            print("MySQL is available. Connecting...")
            return
        except mysql.connector.Error as e:
            print(f"MySQL is not yet available. Retrying... ({e})")
            attempts += 1
            time.sleep(sleep_time)

    print("Unable to connect to MySQL. Exiting.")
    exit(1)

# Esperar hasta que MySQL esté disponible
wait_for_mysql(mysql_host, mysql_port, mysql_user, mysql_password, mysql_db)

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
    db.session.close()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print(app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(host='0.0.0.0', port=5000)
