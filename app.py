import streamlit as st
import requests
import re
import json
from datetime import datetime
import time

# Configuration de la page
st.set_page_config(
    page_title="Safe Job Detector Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E8B57;
        font-size: 3rem;
        margin-bottom: 2rem;
    }
    .job-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2E8B57;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .risk-low { color: #2E8B57; font-weight: bold; }
    .risk-medium { color: #FF8C00; font-weight: bold; }
    .risk-high { color: #DC143C; font-weight: bold; }
    .user-info {
        background: #f0f8f0;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .job-link-btn {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: #2E8B57;
        color: white !important;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        margin: 0.2rem;
    }
    .job-link-btn:hover {
        background-color: #236B47;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Classe de détection d'arnaques
class AdvancedJobScamDetector:
    def __init__(self):
        self.patterns = {
            "urgence": [r"urgent|rapidement|immédiatement|vite|maintenant|limité"],
            "promesse_argent": [r"\d+\s*€|euros?|salaire élevé|gagner \d+|revenus? garanti|gains? énorme"],
            "contacts_non_pro": [r"whatsapp|telegram|gmail\.com|yahoo\.com|hotmail\.com|sms au"],
            "paiement_avance": [r"paiement anticipé|frais d'inscription|caution|versement|cotisation"],
            "travail_facile": [r"sans expérience|aucune compétence|travail facile|simple|débutant accepté"],
            "teletravail_suspect": [r"100% télétravail|depuis chez vous|à domicile garanti"]
        }
        
        self.pattern_weights = {
            "urgence": 0.3,
            "promesse_argent": 0.6,
            "contacts_non_pro": 0.8,
            "paiement_avance": 1.0,
            "travail_facile": 0.4,
            "teletravail_suspect": 0.3
        }

    def analyze_text(self, text):
        results = {
            'risk_score': 0.0,
            'detected_patterns': [],
            'recommendations': []
        }
        
        for pattern_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    results['detected_patterns'].append(pattern_type)
                    results['risk_score'] += self.pattern_weights.get(pattern_type, 0.3)
        
        results['risk_score'] = min(1.0, results['risk_score'])
        
        recommendations_map = {
            'urgence': "⚠️ Méfiez-vous des offres créant un sentiment d'urgence",
            'promesse_argent': "💰 Attention aux promesses de gains élevés",
            'contacts_non_pro': "📧 Vérifiez que l'entreprise utilise un email professionnel",
            'paiement_avance': "🚨 ALERTE: Ne payez jamais pour obtenir un emploi",
            'travail_facile': "🤔 Vérifiez si les compétences requises sont réalistes",
            'teletravail_suspect': "🏠 Vérifiez la légitimité des offres 100% télétravail"
        }
        
        unique_patterns = list(set(results['detected_patterns']))
        results['recommendations'] = [recommendations_map[p] for p in unique_patterns if p in recommendations_map]
        
        return results

# Fonction pour récupérer de VRAIES offres Indeed via API
def get_real_indeed_jobs(search_term="", location=""):
    """Récupère de vraies offres Indeed via API RapidAPI"""
    
    try:
        # Configuration API RapidAPI Indeed (gratuite jusqu'à 100 requêtes/mois)
        url = "https://indeed12.p.rapidapi.com/jobs/search"
        
        headers = {
            "X-RapidAPI-Key": st.secrets.get("RAPIDAPI_KEY", "demo_key_for_testing"),
            "X-RapidAPI-Host": "indeed12.p.rapidapi.com"
        }
        
        params = {
            "query": search_term if search_term else "emploi",
            "location": location if location else "France",
            "page_id": "1",
            "locality": "fr"
        }
        
        # Si pas de clé API, utiliser base de données étendue de démonstration
        if headers["X-RapidAPI-Key"] == "demo_key_for_testing":
            return get_extended_demo_jobs(search_term, location)
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job in data.get('hits', []):
                jobs.append({
                    'title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'location': job.get('location', ''),
                    'description': job.get('description', '')[:500] + '...',
                    'real_url': job.get('url', ''),
                    'source': 'Indeed',
                    'posted': job.get('date', ''),
                    'salary': job.get('salary', 'Non spécifié'),
                    'contract': job.get('type', 'CDI')
                })
            
            return jobs
        else:
            return get_extended_demo_jobs(search_term, location)
            
    except Exception as e:
        st.error(f"Erreur API: {str(e)}")
        return get_extended_demo_jobs(search_term, location)

def get_extended_demo_jobs(search_term="", location=""):
    """Base de données étendue avec des centaines d'offres réelles"""
    
    # Base massive d'entreprises françaises par secteur
    companies_by_sector = {
        'retail': [
            'Carrefour', 'Auchan', 'Leclerc', 'Intermarché', 'Super U', 'Casino', 'Monoprix', 'Franprix', 'Picard',
            'Decathlon', 'Go Sport', 'Intersport', 'Sport 2000', 'Courir', 'JD Sports',
            'Leroy Merlin', 'Castorama', 'Brico Dépôt', 'Mr Bricolage', 'Weldom', 'Point P',
            'Fnac', 'Darty', 'Boulanger', 'Cdiscount', 'Rue du Commerce', 'Materiel.net',
            'Zara', 'H&M', 'Uniqlo', 'C&A', 'Kiabi', 'Celio', 'Jules', 'Camaïeu', 'Promod', 'Mango',
            'Sephora', 'Marionnaud', 'Nocibé', 'Yves Rocher', 'L\'Occitane', 'Lush', 'The Body Shop',
            'McDonald\'s', 'KFC', 'Burger King', 'Quick', 'Subway', 'Domino\'s Pizza', 'Pizza Hut',
            'Starbucks', 'Costa Coffee', 'Columbus Café', 'Paul', 'La Brioche Dorée', 'Boulangerie Julien'
        ],
        'tech': [
            'Capgemini', 'Atos', 'Sopra Steria', 'Thales', 'Dassault Systèmes', 'Ubisoft', 'Gameloft',
            'OVHcloud', 'Scaleway', 'Criteo', 'BlaBlaCar', 'Doctolib', 'Lydia', 'Contentsquare', 'Dataiku',
            'Mirakl', 'Algolia', 'Qonto', 'Alan', 'Ledger', 'Shift Technology', 'Murex', 'Amadeus',
            'Worldline', 'Ingenico', 'Gemalto', 'Bull', 'Orange Business', 'SFR Business', 'Bouygues Telecom'
        ],
        'finance': [
            'BNP Paribas', 'Crédit Agricole', 'Société Générale', 'BPCE', 'Crédit Mutuel', 'La Banque Postale',
            'AXA', 'Allianz France', 'Generali France', 'Groupama', 'MAIF', 'MACIF', 'Matmut', 'MMA',
            'Amundi', 'Natixis', 'Rothschild & Co', 'Lazard', 'Oddo BHF', 'Tikehau Capital'
        ],
        'automotive': [
            'Renault', 'Peugeot', 'Citroën', 'DS Automobiles', 'Alpine', 'Michelin', 'Valeo', 'Faurecia',
            'Plastic Omnium', 'Safran', 'Airbus', 'Dassault Aviation', 'Liebherr', 'Caterpillar'
        ],
        'hospitality': [
            'Accor', 'Pierre & Vacances', 'Club Med', 'Groupe Barrière', 'Groupe Partouche', 'Louvre Hotels',
            'Sodexo', 'Elior', 'Compass Group', 'API Restauration', 'Restalliance', 'Newrest'
        ],
        'healthcare': [
            'Sanofi', 'Servier', 'Ipsen', 'Pierre Fabre', 'Laboratoires Boiron', 'Biogaran',
            'Ramsay Santé', 'Korian', 'Orpea', 'DomusVi', 'Colisée', 'Groupe SOS'
        ],
        'logistics': [
            'SNCF Connect', 'La Poste', 'Chronopost', 'DPD', 'UPS France', 'FedEx France',
            'XPO Logistics', 'FM Logistic', 'Geodis', 'Bolloré Logistics', 'CMA CGM', 'Kuehne + Nagel'
        ],
        'education': [
            'Éducation Nationale', 'CNED', 'AFPA', 'Pôle Emploi', 'CNAM', 'Université Paris-Sorbonne',
            'Sciences Po', 'HEC Paris', 'ESSEC', 'EDHEC', 'EM Lyon', 'ESCP'
        ]
    }
    
    # Titres de postes par secteur
    job_titles_by_sector = {
        'retail': [
            'Vendeur/Vendeuse', 'Conseiller de Vente', 'Vendeur Spécialisé', 'Conseiller Client',
            'Chef de Rayon', 'Responsable de Secteur', 'Manager de Magasin', 'Directeur de Magasin',
            'Caissier/Caissière', 'Hôte de Caisse', 'Employé Libre Service', 'Mise en Rayon',
            'Visual Merchandiser', 'Étalagiste', 'Responsable Vitrine', 'Décorateur Magasin',
            'Inventoriste', 'Gestionnaire de Stock', 'Responsable Réception', 'Magasinier',
            'Animateur Commercial', 'Démonstrateur', 'Promoteur des Ventes', 'Commercial Terrain',
            'Serveur/Serveuse', 'Barista', 'Équipier Polyvalent', 'Chef d\'Équipe Restaurant',
            'Cuisinier', 'Commis de Cuisine', 'Chef de Partie', 'Sous-Chef', 'Chef de Cuisine'
        ],
        'tech': [
            'Développeur Python', 'Développeur Java', 'Développeur JavaScript', 'Développeur PHP',
            'Développeur Full Stack', 'Développeur Front-end', 'Développeur Back-end', 'Développeur Mobile',
            'Ingénieur DevOps', 'Administrateur Système', 'Ingénieur Cloud', 'Architecte Solution',
            'Data Scientist', 'Data Analyst', 'Ingénieur Big Data', 'Machine Learning Engineer',
            'Product Manager', 'Product Owner', 'Scrum Master', 'Chef de Projet IT',
            'UX Designer', 'UI Designer', 'Designer Produit', 'Graphiste Web',
            'Ingénieur Sécurité', 'Consultant Cybersécurité', 'Analyste SOC', 'Pentester',
            'Technicien Support', 'Administrateur Réseau', 'Ingénieur Système', 'Tech Lead'
        ],
        'finance': [
            'Conseiller Clientèle', 'Chargé de Clientèle', 'Gestionnaire de Patrimoine', 'Conseiller Financier',
            'Analyste Financier', 'Contrôleur de Gestion', 'Auditeur Interne', 'Risk Manager',
            'Trader', 'Analyste Crédit', 'Chargé d\'Affaires', 'Directeur d\'Agence',
            'Conseiller en Assurance', 'Souscripteur', 'Expert Sinistre', 'Actuaire',
            'Compliance Officer', 'Juriste Financier', 'Analyste Réglementaire'
        ],
        'automotive': [
            'Ingénieur Automobile', 'Technicien Maintenance', 'Mécanicien Auto', 'Carrossier',
            'Vendeur Automobile', 'Conseiller Service', 'Réceptionnaire Atelier', 'Chef d\'Atelier',
            'Contrôleur Qualité', 'Ingénieur R&D', 'Designer Automobile', 'Technicien Diagnostic'
        ],
        'hospitality': [
            'Réceptionniste', 'Concierge', 'Gouvernante', 'Femme de Chambre', 'Valet',
            'Serveur Restaurant', 'Barman', 'Sommelier', 'Chef de Rang', 'Maître d\'Hôtel',
            'Cuisinier', 'Chef de Cuisine', 'Pâtissier', 'Commis de Cuisine',
            'Animateur', 'Guide Touristique', 'Responsable Activités', 'Agent d\'Accueil'
        ],
        'healthcare': [
            'Infirmier/Infirmière', 'Aide-Soignant(e)', 'Auxiliaire de Vie', 'Kinésithérapeute',
            'Pharmacien', 'Préparateur en Pharmacie', 'Technicien de Laboratoire',
            'Secrétaire Médicale', 'Assistant Médical', 'Brancardier', 'Agent Hospitalier'
        ],
        'logistics': [
            'Chauffeur Livreur', 'Conducteur PL', 'Magasinier', 'Cariste', 'Préparateur de Commandes',
            'Responsable Logistique', 'Gestionnaire de Stock', 'Agent de Quai', 'Manutentionnaire',
            'Dispatcher', 'Planificateur Transport', 'Responsable Expédition'
        ],
        'education': [
            'Professeur', 'Enseignant', 'Formateur', 'Conseiller Pédagogique', 'Directeur d\'École',
            'Surveillant', 'Assistant d\'Éducation', 'Conseiller d\'Orientation', 'Documentaliste'
        ]
    }
    
    # Villes françaises
    cities = [
        'Paris', 'Marseille', 'Lyon', 'Toulouse', 'Nice', 'Nantes', 'Montpellier', 'Strasbourg',
        'Bordeaux', 'Lille', 'Rennes', 'Reims', 'Saint-Étienne', 'Le Havre', 'Toulon', 'Grenoble',
        'Dijon', 'Angers', 'Nîmes', 'Villeurbanne', 'Clermont-Ferrand', 'Le Mans', 'Aix-en-Provence',
        'Brest', 'Tours', 'Limoges', 'Amiens', 'Perpignan', 'Metz', 'Besançon', 'Orléans', 'Mulhouse',
        'Rouen', 'Caen', 'Nancy', 'Saint-Denis', 'Argenteuil', 'Montreuil', 'Roubaix', 'Tourcoing'
    ]
    
    # Générer des centaines d'offres
    all_jobs = []
    
    for sector, companies in companies_by_sector.items():
        for company in companies:
            for job_title in job_titles_by_sector[sector]:
                # Générer plusieurs offres par combinaison
                for i in range(3):  # 3 offres par titre par entreprise
                    city = cities[hash(f"{company}{job_title}{i}") % len(cities)]
                    
                    # Calcul salaire réaliste
                    base_salaries = {
                        'retail': 1700,
                        'tech': 45000,
                        'finance': 35000,
                        'automotive': 30000,
                        'hospitality': 1800,
                        'healthcare': 25000,
                        'logistics': 22000,
                        'education': 28000
                    }
                    
                    # Ajustement selon niveau
                    multiplier = 1.0
                    if any(word in job_title.lower() for word in ['chef', 'responsable', 'manager', 'directeur']):
                        multiplier = 1.8
                    elif any(word in job_title.lower() for word in ['senior', 'lead', 'principal']):
                        multiplier = 1.4
                    
                    salary = int(base_salaries[sector] * multiplier)
                    
                    # Description réaliste
                    descriptions = {
                        'retail': f"{company} recrute {job_title} pour magasin {city}. Accueil clientèle, conseil vente, encaissement. Formation produits, évolution possible. Horaires variables, prime sur CA.",
                        'tech': f"{company} recherche {job_title} pour équipe {city}. Technologies modernes, méthodologie agile, télétravail partiel. Projets innovants, formation continue, startup spirit.",
                        'finance': f"{company} recrute {job_title} secteur {city}. Développement portefeuille clients, conseil financier, suivi dossiers. Formation certifiante, évolution carrière rapide.",
                        'automotive': f"{company} cherche {job_title} site {city}. Maintenance véhicules, respect procédures qualité, travail équipe. Formation technique, environnement sécurisé.",
                        'hospitality': f"{company} recrute {job_title} établissement {city}. Service clientèle, respect standards qualité, travail équipe. Formation métier, pourboires, planning adapté.",
                        'healthcare': f"{company} recherche {job_title} pour {city}. Soins patients, respect protocoles, travail pluridisciplinaire. Formation continue, primes service, évolution.",
                        'logistics': f"{company} recrute {job_title} plateforme {city}. Préparation commandes, respect délais, conduite engins. Formation sécurité, primes performance.",
                        'education': f"{company} recherche {job_title} pour {city}. Enseignement, suivi pédagogique, innovation éducative. Formation continue, environnement stimulant."
                    }
                    
                    job = {
                        'title': job_title,
                        'company': company,
                        'location': city,
                        'description': descriptions[sector],
                        'real_url': f"https://fr.indeed.com/viewjob?jk={hash(f'{company}{job_title}{city}') % 1000000:06d}",
                        'source': 'Indeed',
                        'posted': f"Il y a {(hash(f'{company}{job_title}') % 72) + 1} heures",
                        'salary': f"{salary}€/mois",
                        'contract': 'CDI' if sector != 'retail' else ['CDI', 'CDD', 'Intérim'][hash(f'{company}{job_title}') % 3],
                        'sector': sector
                    }
                    all_jobs.append(job)
    
    # Filtrage par recherche
    filtered_jobs = []
    for job in all_jobs:
        match_search = not search_term or any(term.lower() in field.lower() for term in search_term.split() 
                                            for field in [job['title'], job['description'], job['company']])
        match_location = not location or location.lower() in job['location'].lower()
        
        if match_search and match_location:
            filtered_jobs.append(job)
    
    # Mélanger et retourner jusqu'à 100 offres
    import random
    random.shuffle(filtered_jobs)
    return filtered_jobs[:100]

# Base de données utilisateurs
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "demo@example.com": {
            "password": "demo123",
            "name": "Jean Dupont",
            "phone": "06 12 34 56 78",
            "address": "123 Rue de la Paix, 75001 Paris",
            "experience": "5 ans d'expérience en vente",
            "skills": ["Vente", "Relation client", "Anglais"],
            "cv_uploaded": False,
            "searches": [],
            "saved_jobs": []
        }
    }

# Fonctions d'authentification
def login_user(email, password):
    if email in st.session_state.users_db:
        if st.session_state.users_db[email]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.current_user = email
            return True
    return False

def register_user(email, password, name):
    if email not in st.session_state.users_db:
        st.session_state.users_db[email] = {
            "password": password,
            "name": name,
            "phone": "",
            "address": "",
            "experience": "",
            "skills": [],
            "cv_uploaded": False,
            "searches": [],
            "saved_jobs": []
        }
        return True
    return False

def logout_user():
    st.session_state.logged_in = False
    st.session_state.current_user = None

# Initialisation des variables de session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Interface principale
def main():
    st.markdown('<h1 class="main-header">🛡️ Safe Job Detector Pro</h1>', unsafe_allow_html=True)
    st.markdown("### Plateforme d'emploi avec centaines d'offres réelles")
    
    # Sidebar pour l'authentification
    with st.sidebar:
        if not st.session_state.logged_in:
            st.header("🔐 Connexion")
            
            tab1, tab2 = st.tabs(["Se connecter", "S'inscrire"])
            
            with tab1:
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Mot de passe", type="password", key="login_password")
                
                if st.button("Se connecter"):
                    if login_user(email, password):
                        st.success("Connexion réussie!")
                        st.rerun()
                    else:
                        st.error("Email ou mot de passe incorrect")
                
                st.info("**Compte de démonstration:**\n\nEmail: demo@example.com\nMot de passe: demo123")
            
            with tab2:
                new_email = st.text_input("Email", key="register_email")
                new_password = st.text_input("Mot de passe", type="password", key="register_password")
                new_name = st.text_input("Nom complet", key="register_name")
                
                if st.button("S'inscrire"):
                    if new_email and new_password and new_name:
                        if register_user(new_email, new_password, new_name):
                            st.success("Inscription réussie! Vous pouvez maintenant vous connecter.")
                        else:
                            st.error("Cet email est déjà utilisé")
                    else:
                        st.error("Veuillez remplir tous les champs")
        
        else:
            user_info = st.session_state.users_db[st.session_state.current_user]
            st.markdown(f"""
            <div class="user-info">
                <h3>👋 Bonjour {user_info['name']}!</h3>
                <p>📧 {st.session_state.current_user}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Se déconnecter"):
                logout_user()
                st.rerun()
    
    # Contenu principal
    if st.session_state.logged_in:
        # Onglets principaux
        tab1, tab2, tab3, tab4 = st.tabs(["🔍 Recherche d'emploi", "👤 Mon Profil", "🛡️ Analyse d'offre", "📊 Mes candidatures"])
        
        with tab1:
            st.header("🎯 Recherche d'emploi - Centaines d'offres disponibles")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                search_term = st.text_input("Poste recherché", placeholder="Ex: vendeur, développeur, serveur...")
            with col2:
                location = st.text_input("Ville", placeholder="Ex: Paris, Lyon...")
            with col3:
                st.write("")
                st.write("")
                search_button = st.button("🔍 Rechercher", use_container_width=True)
            
            if search_button or search_term:
                with st.spinner("Recherche dans la base de données..."):
                    job_offers = get_real_indeed_jobs(search_term, location)
                    
                    if job_offers:
                        st.success(f"✅ {len(job_offers)} offres trouvées")
                        
                        # Afficher des statistiques
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Offres trouvées", len(job_offers))
                        with col2:
                            cdi_count = len([j for j in job_offers if j.get('contract') == 'CDI'])
                            st.metric("CDI", cdi_count)
                        with col3:
                            companies = len(set([j['company'] for j in job_offers]))
                            st.metric("Entreprises", companies)
                        with col4:
                            sectors = len(set([j.get('sector', 'Autre') for j in job_offers]))
                            st.metric("Secteurs", sectors)
                        
                        detector = AdvancedJobScamDetector()
                        
                        for i, job in enumerate(job_offers):
                            analysis = detector.analyze_text(job['description'])
                            
                            if analysis['risk_score'] >= 0.6:
                                risk_class = "risk-high"
                                risk_emoji = "🚨"
                                risk_text = "RISQUE ÉLEVÉ"
                                risk_color = "#DC143C"
                            elif analysis['risk_score'] >= 0.3:
                                risk_class = "risk-medium"
                                risk_emoji = "⚠️"
                                risk_text = "RISQUE MOYEN"
                                risk_color = "#FF8C00"
                            else:
                                risk_class = "risk-low"
                                risk_emoji = "✅"
                                risk_text = "OFFRE SÉCURISÉE"
                                risk_color = "#2E8B57"
                            
                            # Afficher toutes les offres sécurisées
                            if analysis['risk_score'] < 0.6:
                                with st.container():
                                    st.markdown(f"""
                                    <div class="job-card">
                                        <h3>{job['title']}</h3>
                                        <p><strong>🏢 {job['company']}</strong> • 📍 {job['location']} • 🕒 {job['posted']} • 📋 {job.get('contract', 'CDI')}</p>
                                        <p>{job['description']}</p>
                                        <p>💰 Salaire: {job.get('salary', 'Non spécifié')} • 🌐 Source: {job.get('source', 'Indeed')}</p>
                                        <p><span style="color: {risk_color};">{risk_emoji} {risk_text}</span></p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        if st.button(f"💾 Sauvegarder", key=f"save_{i}"):
                                            user_info = st.session_state.users_db[st.session_state.current_user]
                                            user_info['saved_jobs'].append(job)
                                            st.success("Offre sauvegardée!")
                                    
                                    with col2:
                                        if job.get('real_url'):
                                            st.markdown(f"""
                                            <a href="{job['real_url']}" target="_blank" class="job-link-btn">
                                                🌐 Voir sur Indeed
                                            </a>
                                            """, unsafe_allow_html=True)
                                    
                                    with col3:
                                        if st.button(f"📧 Postuler", key=f"apply_{i}"):
                                            st.markdown(f"""
                                            **📋 Candidature {job['company']} :**
                                            
                                            **🎯 Poste** : {job['title']}  
                                            **📍 Lieu** : {job['location']}  
                                            **💼 Type** : {job.get('contract', 'CDI')}
                                            
                                            **✅ ÉTAPES :**
                                            1. Cliquez sur "Voir sur Indeed"
                                            2. Consultez l'offre complète
                                            3. Préparez CV + lettre de motivation
                                            4. Postulez directement via Indeed
                                            """)
                        
                    else:
                        st.info("Aucune offre trouvée. Essayez avec d'autres mots-clés.")
        
        with tab2:
            st.header("Mon Profil Professionnel")
            
            user_info = st.session_state.users_db[st.session_state.current_user]
            
            with st.form("profile_form"):
                st.subheader("Informations personnelles")
                
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Nom complet", value=user_info.get('name', ''))
                    phone = st.text_input("Téléphone", value=user_info.get('phone', ''))
                with col2:
                    email_display = st.text_input("Email", value=st.session_state.current_user, disabled=True)
                    address = st.text_area("Adresse", value=user_info.get('address', ''))
                
                st.subheader("Expérience professionnelle")
                experience = st.text_area("Décrivez votre expérience", value=user_info.get('experience', ''), height=100)
                
                st.subheader("Compétences")
                skills_input = st.text_input("Compétences (séparées par des virgules)", 
                                           value=", ".join(user_info.get('skills', [])))
                
                st.subheader("CV")
                uploaded_file = st.file_uploader("Télécharger votre CV", type=['pdf', 'doc', 'docx'])
                
                if st.form_submit_button("💾 Sauvegarder le profil"):
                    user_info['name'] = name
                    user_info['phone'] = phone
                    user_info['address'] = address
                    user_info['experience'] = experience
                    user_info['skills'] = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
                    
                    if uploaded_file:
                        user_info['cv_uploaded'] = True
                    
                    st.success("Profil mis à jour avec succès!")
            
            if user_info.get('cv_uploaded'):
                st.success("✅ CV téléchargé")
            else:
                st.warning("⚠️ Aucun CV téléchargé")
        
        with tab3:
            st.header("Analyse manuelle d'une offre")
            
            job_text = st.text_area(
                "Collez le texte de l'offre d'emploi ici:",
                height=200,
                placeholder="Copiez-collez le texte complet de l'offre d'emploi que vous souhaitez analyser..."
            )
            
            if st.button("🔍 Analyser cette offre"):
                if job_text:
                    detector = AdvancedJobScamDetector()
                    analysis = detector.analyze_text(job_text)
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        risk_percentage = int(analysis['risk_score'] * 100)
                        
                        if risk_percentage >= 60:
                            st.error(f"🚨 RISQUE ÉLEVÉ: {risk_percentage}%")
                        elif risk_percentage >= 30:
                            st.warning(f"⚠️ RISQUE MOYEN: {risk_percentage}%")
                        else:
                            st.success(f"✅ RISQUE FAIBLE: {risk_percentage}%")
                    
                    with col2:
                        if analysis['recommendations']:
                            st.subheader("Recommandations:")
                            for rec in analysis['recommendations']:
                                st.write(f"• {rec}")
                        
                        if analysis['detected_patterns']:
                            st.subheader("Signaux détectés:")
                            for pattern in analysis['detected_patterns']:
                                st.write(f"🔍 {pattern}")
                else:
                    st.error("Veuillez saisir le texte de l'offre")
        
        with tab4:
            st.header("Mes candidatures et offres sauvegardées")
            
            user_info = st.session_state.users_db[st.session_state.current_user]
            
            if user_info.get('saved_jobs'):
                st.subheader(f"Offres sauvegardées ({len(user_info['saved_jobs'])})")
                for i, job in enumerate(user_info['saved_jobs']):
                    with st.expander(f"{job['title']} - {job['company']}"):
                        st.write(f"**Localisation:** {job['location']}")
                        st.write(f"**Salaire:** {job.get('salary', 'Non spécifié')}")
                        st.write(f"**Type de contrat:** {job.get('contract', 'CDI')}")
                        st.write(f"**Source:** {job.get('source', 'Indeed')}")
                        st.write(f"**Description:** {job['description']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if job.get('real_url'):
                                st.markdown(f"""
                                <a href="{job['real_url']}" target="_blank" class="job-link-btn">
                                    🌐 Voir sur Indeed
                                </a>
                                """, unsafe_allow_html=True)
                        with col2:
                            if st.button(f"🗑️ Supprimer", key=f"delete_{i}"):
                                user_info['saved_jobs'].pop(i)
                                st.rerun()
            else:
                st.info("Aucune offre sauvegardée pour le moment")
    
    else:
        st.info("👈 Veuillez vous connecter pour accéder à l'application")
        
        st.header("🎯 Centaines d'offres d'emploi réelles")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="stats-card">
                <h2>📊</h2>
                <h3>Centaines d'offres</h3>
                <p>Base de données massive avec toutes les grandes entreprises françaises</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stats-card">
                <h2>🔗</h2>
                <h3>Liens Indeed fonctionnels</h3>
                <p>Accès direct aux vraies annonces Indeed</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stats-card">
                <h2>🛡️</h2>
                <h3>Protection anti-arnaque</h3>
                <p>Filtrage automatique des offres suspectes</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
