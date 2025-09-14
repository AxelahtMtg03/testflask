from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
import datetime
import os
from datetime import timedelta


app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuration adaptée pour Vercel
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Base en mémoire
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "ma_cle_secrete_vercel")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

# Initialisation de la base de données
db = SQLAlchemy(app)

# Modèle de données (copié de models.py pour éviter les imports)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    nom = db.Column(db.String(50), nullable=False)
    genre = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

# Création de la base de données au démarrage
@app.before_request
def create_tables():
    # Vérifier si la table existe déjà
    if not hasattr(create_tables, 'tables_created'):
        db.create_all()
        create_tables.tables_created = True

@app.route('/')
def accueil():
    title = "Site de Vente de Produits"
    header = "Bienvenue sur notre site de vente de produits"
    current_year = datetime.datetime.now().year
    site_name = "Vente de Produits"
    return render_template(
        'accueil.html',
        title=title,
        header=header,
        current_year=current_year,
        site_name=site_name
    )

@app.route("/inscription", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        # Récupération des informations du formulaire
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        prenom = request.form['prenom']
        nom = request.form['nom']
        genre = request.form['genre']

        # Vérification si l'utilisateur existe déjà
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Ce nom d'utilisateur est déjà pris. Veuillez en choisir un autre.", "danger")
        else:
            # Création d'un nouvel utilisateur
            new_user = User(username=username, email=email, password=password, 
                           prenom=prenom, nom=nom, genre=genre)
            db.session.add(new_user)
            db.session.commit()
            flash("Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
            return redirect("/connexion")

    return render_template("inscription.html")

@app.route('/connexion', methods=['GET', 'POST'])  
def connexion():
    if request.method == 'POST':
        # Récupération des informations du formulaire
        email = request.form['email']
        password = request.form['password']

        # Vérification de l'adresse email et du mot de passe
        utilisateur = User.query.filter_by(email=email, password=password).first()

        if utilisateur:
            # Configuration de la session
            session.permanent = True
            session['id'] = utilisateur.id
            session['pseudo'] = utilisateur.username
            session['mail'] = utilisateur.email
            session['nom'] = utilisateur.nom
            session['prenom'] = utilisateur.prenom
            session['mdp'] = utilisateur.password
            session['genre'] = utilisateur.genre
            session['log'] = True
            
            flash("Connexion réussie !", "success")
            return redirect("/")  
        else:
            flash("Email ou mot de passe incorrect.", "danger")
    return render_template('connexion.html')

@app.route('/deconnexion') 
def deconnexion():
    session.clear()
    flash("Vous avez été déconnecté avec succès.", "info")
    return redirect("/")

# Gestion des erreurs 404
@app.errorhandler(404)
def not_found(e):
    return render_template("accueil.html"), 404

# Initialisation de l'application
with app.app_context():
    db.create_all()