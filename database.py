import sqlite3
import g as flask_g

DB_PATH = 'it_manager.db'

def get_db():
    try:
        from flask import g
        if 'db' not in g:
            g.db = sqlite3.connect(DB_PATH)
            g.db.row_factory = sqlite3.Row
        return g.db
    except RuntimeError:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS materiels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            type TEXT NOT NULL,
            marque TEXT DEFAULT '',
            modele TEXT DEFAULT '',
            numero_serie TEXT DEFAULT '',
            localisation TEXT DEFAULT '',
            statut TEXT DEFAULT 'Actif',
            date_achat TEXT DEFAULT '',
            notes TEXT DEFAULT ''
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            description TEXT DEFAULT '',
            priorite TEXT DEFAULT 'Moyenne',
            statut TEXT DEFAULT 'Ouvert',
            materiel_id INTEGER REFERENCES materiels(id) ON DELETE SET NULL,
            demandeur TEXT DEFAULT '',
            technicien TEXT DEFAULT '',
            date_creation TEXT DEFAULT '',
            date_resolution TEXT DEFAULT ''
        )
    ''')
    # Données de démo
    count = conn.execute('SELECT COUNT(*) FROM materiels').fetchone()[0]
    if count == 0:
        conn.executemany('''
            INSERT INTO materiels (nom, type, marque, modele, numero_serie, localisation, statut, date_achat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            ('PC-Bureau-01', 'PC Bureau', 'Dell', 'OptiPlex 7090', 'SN-001-XY', 'Salle 101', 'Actif', '2022-03-15'),
            ('PC-Bureau-02', 'PC Bureau', 'HP', 'ProDesk 600', 'SN-002-AB', 'Salle 102', 'En panne', '2021-11-20'),
            ('Laptop-DG-01', 'Laptop', 'Lenovo', 'ThinkPad X1', 'SN-003-CD', 'Direction', 'Actif', '2023-01-10'),
            ('Switch-Réseau-01', 'Switch', 'Cisco', 'Catalyst 2960', 'SN-004-EF', 'Salle Serveur', 'Actif', '2020-06-05'),
            ('Imprimante-RDC', 'Imprimante', 'Brother', 'HL-L8360CDW', 'SN-005-GH', 'Rez-de-chaussée', 'Maintenance', '2021-08-22'),
            ('Serveur-NAS-01', 'Serveur', 'Synology', 'DS920+', 'SN-006-IJ', 'Salle Serveur', 'Actif', '2022-09-01'),
        ])
        conn.executemany('''
            INSERT INTO tickets (titre, description, priorite, statut, materiel_id, demandeur, technicien, date_creation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            ('PC-Bureau-02 ne démarre plus', 'Écran noir au démarrage, aucun bip', 'Haute', 'Ouvert', 2, 'M. Benali', 'Tech. Karim', '2025-05-06 09:15'),
            ('Imprimante RDC bourrage papier répétitif', 'Bourrage à chaque impression recto-verso', 'Moyenne', 'En cours', 5, 'Mme. Trabelsi', 'Tech. Sonia', '2025-05-05 14:30'),
            ('Accès réseau lent - Salle 101', 'Latence > 500ms depuis hier matin', 'Critique', 'Ouvert', None, 'Équipe Dev', '', '2025-05-07 08:00'),
        ])
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée.")

if __name__ == '__main__':
    init_db()
