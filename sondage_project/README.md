# 🗳️ SondageApp — Application de sondages Django

Application complète de création, diffusion et analyse de sondages développée avec Django (MVT), MySQL, Bootstrap 5 et Chart.js.

---

## 📐 Architecture — Diagramme de classes respecté

```
Participant (abstraite — héritage multi-table)
├── Utilisateur  (AbstractUser + Participant) → table accounts_utilisateur
└── Anonyme      (Participant)               → table accounts_anonyme

Sondage  ──1──→ Question ──1──→ Choix
                                    ↑
Reponse ──FK──→ Participant         │
    │                               │
    └──→ ReponseDetail ──M2M──→ Choix

ModèleSondage ──0..*──→ Sondage
```

---

## 🚀 Installation rapide

### 1. Cloner / extraire le projet

```bash
cd sondage_project
```

### 2. Créer l'environnement virtuel

```bash
python -m venv env

# Windows
env\Scripts\activate

# Mac / Linux
source env/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Créer la base de données MySQL

```sql
-- Dans MySQL (ligne de commande ou phpMyAdmin)
CREATE DATABASE sondage_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configurer la base de données

Dans `config/settings.py`, modifier le mot de passe MySQL :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sondage_db',
        'USER': 'root',
        'PASSWORD': 'VOTRE_MOT_DE_PASSE',  # ← modifier ici
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 6. Appliquer les migrations

```bash
python manage.py makemigrations accounts
python manage.py makemigrations surveys
python manage.py makemigrations responses
python manage.py migrate
```

### 7. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### 8. Lancer le serveur

```bash
python manage.py runserver
```

➡️ Ouvrir : **http://127.0.0.1:8000**

---

## 🗂️ Structure du projet

```
sondage_project/
├── config/                  ← Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                ← App Utilisateurs
│   ├── models.py            → Participant, Utilisateur, Anonyme
│   ├── views.py             → inscription, connexion, profil
│   ├── forms.py             → InscriptionForm, ConnexionForm
│   ├── urls.py
│   └── admin.py
│
├── surveys/                 ← App Sondages
│   ├── models.py            → ModèleSondage, Sondage, Question, Choix
│   ├── views.py             → dashboard, creer, editer, dupliquer...
│   ├── forms.py             → SondageForm, QuestionForm, ChoixForm
│   ├── urls.py
│   └── admin.py
│
├── responses/               ← App Réponses
│   ├── models.py            → Reponse, ReponseDetail
│   ├── views.py             → repondre, resultats, export CSV/Excel
│   ├── urls.py
│   └── admin.py
│
├── templates/
│   ├── base.html            ← Layout principal (navbar, footer)
│   ├── home.html
│   ├── accounts/            → inscription · connexion · profil
│   ├── surveys/             → dashboard · creer · editer · detail...
│   └── responses/           → repondre · resultats · remerciement
│
├── static/
│   ├── css/
│   └── js/
│
├── manage.py
└── requirements.txt
```

---

## 📋 Fonctionnalités implémentées

### Gestion des utilisateurs
- ✅ Inscription avec choix du rôle (Créateur / Participant / Les deux)
- ✅ Connexion par email + mot de passe
- ✅ Profil avec historique des sondages créés et participations
- ✅ Participant **anonyme** identifié par IP + token UUID (session)

### Création de sondages
- ✅ Interface de création en 2 étapes
- ✅ 4 types de questions : choix unique, choix multiple, échelle 1-5, texte libre
- ✅ Logique conditionnelle (question visible selon réponse précédente)
- ✅ Protection par mot de passe
- ✅ Dates de début/fin configurables
- ✅ Duplication de sondages

### Diffusion et participation
- ✅ Lien public unique (UUID) pour partager
- ✅ Sondage public ou privé
- ✅ Restriction une seule réponse par participant
- ✅ Participation anonyme sans compte obligatoire
- ✅ Interface responsive Bootstrap 5

### Analyse des résultats
- ✅ Graphiques Chart.js (pie, barres, distribution)
- ✅ Statistiques par question (pourcentages, moyennes)
- ✅ Export CSV avec BOM Excel
- ✅ Export Excel (.xlsx) avec mise en forme

### Administration
- ✅ Interface Django Admin complète pour les 3 apps
- ✅ Dashboard créateur avec statistiques globales
- ✅ Suppression avec confirmation

---

## 🔗 URLs principales

| URL | Description |
|-----|-------------|
| `/` | Page d'accueil |
| `/admin/` | Interface d'administration Django |
| `/accounts/inscription/` | Création de compte |
| `/accounts/connexion/` | Connexion |
| `/accounts/profil/` | Profil utilisateur |
| `/dashboard/` | Tableau de bord créateur |
| `/sondages/` | Liste des sondages publics |
| `/sondages/creer/` | Créer un sondage |
| `/sondages/<uuid>/` | Voir un sondage |
| `/sondages/<uuid>/questions/` | Gérer les questions |
| `/reponses/<uuid>/repondre/` | Répondre à un sondage |
| `/reponses/<uuid>/resultats/` | Voir les résultats |
| `/reponses/<uuid>/export/csv/` | Export CSV |
| `/reponses/<uuid>/export/excel/` | Export Excel |

---

## 🛠️ Technologies utilisées

- **Django 4.2** — Framework MVT
- **MySQL** — Base de données
- **Bootstrap 5.3** — Interface responsive
- **Chart.js 4.4** — Graphiques interactifs
- **Bootstrap Icons** — Icônes
- **django-crispy-forms** — Formulaires stylisés
- **openpyxl** — Export Excel

---

## 👥 Modèle d'héritage des participants

```python
# Participant (table accounts_participant)
#   ├── Utilisateur hérite de AbstractUser + Participant
#   │     → identifié par email + mot de passe
#   │     → rôle : créateur / participant / les deux
#   └── Anonyme hérite de Participant
#         → identifié par adresse IP + token UUID en session
#         → aucun compte requis

# Dans Reponse :
participant = FK → Participant  # couvre les deux cas, jamais NULL
```
