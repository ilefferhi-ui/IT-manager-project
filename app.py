from flask import Flask, request, jsonify, render_template
from database import init_db, get_db
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ─── PAGES ────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ─── INVENTAIRE ───────────────────────────────────────────
@app.route('/api/materiels', methods=['GET'])
def get_materiels():
    db = get_db()
    rows = db.execute('''
        SELECT m.*, COUNT(t.id) as nb_tickets
        FROM materiels m
        LEFT JOIN tickets t ON t.materiel_id = m.id AND t.statut != "Résolu"
        GROUP BY m.id
        ORDER BY m.nom
    ''').fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/materiels', methods=['POST'])
def add_materiel():
    data = request.json
    db = get_db()
    db.execute('''
        INSERT INTO materiels (nom, type, marque, modele, numero_serie, localisation, statut, date_achat, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['nom'], data['type'], data.get('marque',''), data.get('modele',''),
          data.get('numero_serie',''), data.get('localisation',''), data.get('statut','Actif'),
          data.get('date_achat',''), data.get('notes','')))
    db.commit()
    return jsonify({'success': True, 'id': db.execute('SELECT last_insert_rowid()').fetchone()[0]})

@app.route('/api/materiels/<int:mid>', methods=['PUT'])
def update_materiel(mid):
    data = request.json
    db = get_db()
    db.execute('''
        UPDATE materiels SET nom=?, type=?, marque=?, modele=?, numero_serie=?,
        localisation=?, statut=?, date_achat=?, notes=? WHERE id=?
    ''', (data['nom'], data['type'], data.get('marque',''), data.get('modele',''),
          data.get('numero_serie',''), data.get('localisation',''), data.get('statut','Actif'),
          data.get('date_achat',''), data.get('notes',''), mid))
    db.commit()
    return jsonify({'success': True})

@app.route('/api/materiels/<int:mid>', methods=['DELETE'])
def delete_materiel(mid):
    db = get_db()
    db.execute('DELETE FROM materiels WHERE id=?', (mid,))
    db.commit()
    return jsonify({'success': True})

# ─── TICKETS ──────────────────────────────────────────────
@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    db = get_db()
    rows = db.execute('''
        SELECT t.*, m.nom as materiel_nom, m.type as materiel_type
        FROM tickets t
        LEFT JOIN materiels m ON t.materiel_id = m.id
        ORDER BY
            CASE t.priorite WHEN 'Critique' THEN 1 WHEN 'Haute' THEN 2 WHEN 'Moyenne' THEN 3 ELSE 4 END,
            t.date_creation DESC
    ''').fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/tickets', methods=['POST'])
def add_ticket():
    data = request.json
    db = get_db()
    db.execute('''
        INSERT INTO tickets (titre, description, priorite, statut, materiel_id, demandeur, technicien, date_creation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['titre'], data.get('description',''), data.get('priorite','Moyenne'),
          data.get('statut','Ouvert'), data.get('materiel_id') or None,
          data.get('demandeur',''), data.get('technicien',''),
          datetime.now().strftime('%Y-%m-%d %H:%M')))
    db.commit()
    # Si le matériel est lié → le passer en "En panne"
    if data.get('materiel_id'):
        db.execute("UPDATE materiels SET statut='En panne' WHERE id=?", (data['materiel_id'],))
        db.commit()
    return jsonify({'success': True, 'id': db.execute('SELECT last_insert_rowid()').fetchone()[0]})

@app.route('/api/tickets/<int:tid>', methods=['PUT'])
def update_ticket(tid):
    data = request.json
    db = get_db()
    db.execute('''
        UPDATE tickets SET titre=?, description=?, priorite=?, statut=?,
        materiel_id=?, demandeur=?, technicien=? WHERE id=?
    ''', (data['titre'], data.get('description',''), data.get('priorite','Moyenne'),
          data.get('statut','Ouvert'), data.get('materiel_id') or None,
          data.get('demandeur',''), data.get('technicien',''), tid))
    db.commit()
    # Si résolu → remettre le matériel en Actif
    if data.get('statut') == 'Résolu' and data.get('materiel_id'):
        db.execute("UPDATE materiels SET statut='Actif' WHERE id=?", (data['materiel_id'],))
        db.commit()
    return jsonify({'success': True})

@app.route('/api/tickets/<int:tid>', methods=['DELETE'])
def delete_ticket(tid):
    db = get_db()
    db.execute('DELETE FROM tickets WHERE id=?', (tid,))
    db.commit()
    return jsonify({'success': True})

# ─── STATS ────────────────────────────────────────────────
@app.route('/api/stats', methods=['GET'])
def get_stats():
    db = get_db()
    stats = {
        'materiels_total': db.execute('SELECT COUNT(*) FROM materiels').fetchone()[0],
        'materiels_actifs': db.execute("SELECT COUNT(*) FROM materiels WHERE statut='Actif'").fetchone()[0],
        'materiels_en_panne': db.execute("SELECT COUNT(*) FROM materiels WHERE statut='En panne'").fetchone()[0],
        'tickets_total': db.execute('SELECT COUNT(*) FROM tickets').fetchone()[0],
        'tickets_ouverts': db.execute("SELECT COUNT(*) FROM tickets WHERE statut='Ouvert'").fetchone()[0],
        'tickets_critiques': db.execute("SELECT COUNT(*) FROM tickets WHERE priorite='Critique' AND statut!='Résolu'").fetchone()[0],
    }
    return jsonify(stats)

if __name__ == '__main__':
    init_db()
    app.run(debug=False, port=5000) 