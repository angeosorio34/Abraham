import os
import csv
import io
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_secreto_super_seguro_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------
# MODELS
# -----------------

# Association table for Cases and Lawyers (Many to Many)
case_lawyers = db.Table('case_lawyers',
    db.Column('case_id', db.Integer, db.ForeignKey('cases.id'), primary_key=True),
    db.Column('lawyer_id', db.Integer, db.ForeignKey('lawyers.id'), primary_key=True)
)

class Client(db.Model):
    __tablename__ = 'clients'
    ci = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    cases = db.relationship('Case', backref='client', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client {self.name}>"

class Lawyer(db.Model):
    __tablename__ = 'lawyers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Lawyer {self.name}>"

class Case(db.Model):
    __tablename__ = 'cases'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_ci = db.Column(db.String(20), db.ForeignKey('clients.ci'), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.Date, nullable=True) # None means still active
    status = db.Column(db.String(50), nullable=False, default="En trámite") # En trámite, Archivado, etc.
    
    # Relationship many-to-many
    lawyers = db.relationship('Lawyer', secondary=case_lawyers, lazy='subquery',
        backref=db.backref('cases', lazy=True))

    def __repr__(self):
        return f"<Case {self.id} - {self.status}>"


# -----------------
# ROUTES
# -----------------

@app.route('/')
def index():
    cases_in_progress = Case.query.filter_by(status="En trámite").count()
    cases_archived = Case.query.filter_by(status="Archivado").count()
    total_clients = Client.query.count()
    total_lawyers = Lawyer.query.count()
    
    return render_template('index.html', 
                            cases_in_progress=cases_in_progress,
                            cases_archived=cases_archived,
                            total_clients=total_clients,
                            total_lawyers=total_lawyers)

# -------- CLIENTS CRUD --------
@app.route('/clients', methods=['GET', 'POST'])
def clients():
    if request.method == 'POST':
        ci = request.form.get('ci')
        name = request.form.get('name')
        address = request.form.get('address')
        phone = request.form.get('phone')
        
        if Client.query.get(ci):
            flash("Ya existe un cliente con ese CI.", "error")
        else:
            new_client = Client(ci=ci, name=name, address=address, phone=phone)
            db.session.add(new_client)
            db.session.commit()
            flash("Cliente registrado con éxito.", "success")
        return redirect(url_for('clients'))

    all_clients = Client.query.all()
    return render_template('clients.html', clients=all_clients)

@app.route('/client/delete/<ci>', methods=['POST'])
def delete_client(ci):
    client_to_delete = Client.query.get_or_404(ci)
    db.session.delete(client_to_delete)
    db.session.commit()
    flash("Cliente eliminado.", "success")
    return redirect(url_for('clients'))

# -------- LAWYERS CRUD --------
@app.route('/lawyers', methods=['GET', 'POST'])
def lawyers():
    if request.method == 'POST':
        name = request.form.get('name')
        specialty = request.form.get('specialty')
        
        new_lawyer = Lawyer(name=name, specialty=specialty)
        db.session.add(new_lawyer)
        db.session.commit()
        flash("Abogado registrado con éxito.", "success")
        return redirect(url_for('lawyers'))

    all_lawyers = Lawyer.query.all()
    return render_template('lawyers.html', lawyers=all_lawyers)

@app.route('/lawyer/delete/<int:id>', methods=['POST'])
def delete_lawyer(id):
    lawyer_to_delete = Lawyer.query.get_or_404(id)
    db.session.delete(lawyer_to_delete)
    db.session.commit()
    flash("Abogado eliminado.", "success")
    return redirect(url_for('lawyers'))

# -------- CASES CRUD --------
@app.route('/cases', methods=['GET', 'POST'])
def cases():
    if request.method == 'POST':
        client_ci = request.form.get('client_ci')
        start_date_str = request.form.get('start_date')
        status = request.form.get('status')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else datetime.utcnow().date()
        
        new_case = Case(client_ci=client_ci, start_date=start_date, status=status)
        db.session.add(new_case)
        db.session.commit()
        flash("Expediente creado.", "success")
        return redirect(url_for('cases'))

    all_cases = Case.query.all()
    all_clients = Client.query.all()
    all_lawyers = Lawyer.query.all()
    return render_template('cases.html', cases=all_cases, clients=all_clients, lawyers=all_lawyers)

@app.route('/case/<int:id>/assign', methods=['POST'])
def assign_lawyers(id):
    case = Case.query.get_or_404(id)
    lawyer_ids = request.form.getlist('lawyer_ids')
    
    # Clear existing and set new
    case.lawyers = []
    if lawyer_ids:
        lawyers_to_assign = Lawyer.query.filter(Lawyer.id.in_(lawyer_ids)).all()
        case.lawyers.extend(lawyers_to_assign)
    
    db.session.commit()
    flash("Abogados asignados al expediente correctamente.", "success")
    return redirect(url_for('cases'))

@app.route('/case/<int:id>/update_status', methods=['POST'])
def update_case_status(id):
    case = Case.query.get_or_404(id)
    case.status = request.form.get('status')
    db.session.commit()
    flash("Estado de expediente actualizado.", "success")
    return redirect(url_for('cases'))

@app.route('/case/delete/<int:id>', methods=['POST'])
def delete_case(id):
    case_to_delete = Case.query.get_or_404(id)
    db.session.delete(case_to_delete)
    db.session.commit()
    flash("Expediente eliminado.", "success")
    return redirect(url_for('cases'))

@app.route('/export/cases')
def export_cases():
    cases = Case.query.all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID_Expediente', 'CI_Cliente', 'Fecha_Inicio', 'Estado', 'Abogados_Asignados'])
    for c in cases:
        lawyers_str = " | ".join([l.name for l in c.lawyers])
        cw.writerow([c.id, c.client_ci, c.start_date.strftime('%Y-%m-%d'), c.status, lawyers_str])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=expedientes.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
