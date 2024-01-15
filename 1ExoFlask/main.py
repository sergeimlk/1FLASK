#main.py
# Importation des modules Flask, render_template, request, redirect, url_for
from flask import Flask, render_template, request, redirect, url_for
# Importation du module sqlite3 pour la gestion de la base de données
import sqlite3
# Importation du module datetime pour travailler avec les dates et heures
from datetime import datetime
# Importation du module requests pour effectuer des requêtes HTTP vers l'API de news
import requests

# Création de l'application Flask
app = Flask(__name__)
# Clé secrète pour Flask-Login
app.secret_key = 'your_secret_key'  # Assurez-vous de changer ceci en une clé réelle


# Fonction pour établir une connexion à la base de données
def connect_db():
    return sqlite3.connect('database.db')

# Fonction pour créer la table 'users' si elle n'existe pas
def create_user_table():
    with connect_db() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prenom TEXT,
                nom TEXT,
                sexe TEXT,
                pseudo TEXT,
                email TEXT,
                password TEXT
            )
        ''')

# Création de la table 'users' au lancement de l'application
create_user_table()

# Page d'accueil
@app.route('/')
def home():
    print("Reached the home route")
    return render_template('index.html')

# Formulaire d'inscription
@app.route('/test-formulaire', methods=['GET', 'POST'])
def test_formulaire():
    error_message = None

    if request.method == 'POST':
        # Validation des données du formulaire
        form_data = request.form
        if not all(form_data.values()):
            error_message = "Veuillez remplir tous les champs du formulaire."
        else:
            # Vérification de l'existence du pseudo
            with connect_db() as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE pseudo = ?", (form_data['pseudo'],))
                if c.fetchone() is None:
                    # Ajout des informations dans la base de données
                    hashed_password = generate_password_hash(form_data['password'], method='pbkdf2:sha256')
                    c.execute("INSERT INTO users (prenom, nom, sexe, pseudo, email, password) VALUES (?, ?, ?, ?, ?, ?)",
                              (form_data['prenom'], form_data['nom'], form_data['sexe'], form_data['pseudo'], form_data['email'], hashed_password))
                    conn.commit()
                    # Affichage du message de succès
                    salutation = "Monsieur" if form_data['sexe'] == 'M' else "Madame"
                    return f"Inscription réussie. Bonjour {salutation} {form_data['prenom']} {form_data['nom']}, votre nom d'utilisateur est {form_data['pseudo']}, et votre email est {form_data['email']}"
                else:
                    error_message = "Ce pseudo est déjà utilisé"

    return render_template('test-formulaire.html', error_message=error_message)

# Page des utilisateurs inscrits
@app.route('/utilisateurs-inscrits')
def utilisateurs_inscrits():
    with connect_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        users_data = c.fetchall()
    return render_template('utilisateurs-inscrits.html', users=users_data)

# Nouvelle route pour la page de dessin (draw)
@app.route('/draw')
def draw():
    # Ajoutez le contenu de cette route en fonction de vos besoins
    return render_template('draw.html')

# Nouvelle route pour la page de recherche de news
@app.route('/news-form')
def news_form():
    return render_template('news_form.html')


# Nouvelle route pour la page de news
@app.route('/news', methods=['GET', 'POST'])
def news():
    if request.method == 'POST':
        # Récupérez le symbole (ticker) de l'entreprise depuis le formulaire
        ticker = request.form.get('ticker')

        # Récupérez les informations sur l'action depuis l'API de données boursières
        stock_info = get_stock_info(ticker)

        # Récupérez les informations depuis l'API devapi.ai
        api_key = 'xUc8b0wrH2OSQlG4hp1DB2wNG7HBSDxGbXk2j0OX'
        api_url = f'https://devapi.ai/docs/api/v1/markets/stocks/{ticker}?apikey={api_key}'
        response = requests.get(api_url)

        if response.status_code == 200:
            api_data = response.json()
            # Utilisez les données de l'API comme nécessaire dans votre modèle
            return render_template('news.html', ticker=ticker, stock_info=stock_info, api_data=api_data)
        else:
            # Gérez les erreurs ici
            return render_template('error.html', message='Erreur lors de la récupération des données de l\'API')

    return render_template('news_form.html')

# Page des crédits
@app.route('/credits')
def credits_page():
    return render_template('credits.html')

# Exécution de l'application Flask
if __name__ == '__main__':
    app.run(debug=True)