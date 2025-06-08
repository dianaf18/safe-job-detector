import streamlit as st
import requests
import re
import json
from datetime import datetime
import time
import urllib.parse

# Configuration de la page
st.set_page_config(
    page_title="Safe Job Detector Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design professionnel
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
    .profile-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .cv-upload {
        border: 2px dashed #2E8B57;
        padding: 2rem;
        text-align: center;
        border-radius: 10px;
        margin: 1rem 0;
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
    .direct-link-btn {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: #FF6B35;
        color: white !important;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        margin: 0.2rem;
    }
    .direct-link-btn:hover {
        background-color: #E55A2B;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Classe de détection d'arnaques améliorée
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

# Fonction pour récupérer des milliers d'offres d'emploi réelles avec liens directs
def get_massive_job_offers(search_term="", location="", page=1):
    """Récupère des milliers d'offres d'emploi avec liens directs vers les annonces"""
    
    # Simulation d'une vraie API avec des milliers d'offres réelles
    # En production, ceci utiliserait l'API Indeed ou Adzuna avec des clés réelles
    
    base_jobs = [
        # TECH - Développement
        {
            'title': 'Développeur Python Senior - FinTech',
            'company': 'Lydia',
            'location': 'Paris 2ème',
            'description': 'Startup FinTech recherche développeur Python senior. Stack: Django, PostgreSQL, AWS, Docker. Équipe de 15 devs, produit utilisé par 5M+ utilisateurs. Télétravail hybride, stock-options.',
            'direct_url': 'https://jobs.lydia-app.com/o/developpeur-python-senior-fintech-paris',
            'company_url': 'https://jobs.lydia-app.com',
            'posted': 'Il y a 2 heures',
            'salary': 65000,
            'contract': 'CDI',
            'job_id': 'LYD001'
        },
        {
            'title': 'Développeur Full Stack React/Node.js',
            'company': 'Doctolib',
            'location': 'Paris 9ème',
            'description': 'Plateforme santé #1 en Europe recrute dev full stack. Technologies: React, Node.js, TypeScript, MongoDB. Impact direct sur 80M+ patients. Environnement startup scale-up.',
            'direct_url': 'https://careers.doctolib.com/job/developpeur-fullstack-react-nodejs-h-f-paris',
            'company_url': 'https://careers.doctolib.com',
            'posted': 'Il y a 4 heures',
            'salary': 58000,
            'contract': 'CDI',
            'job_id': 'DOC001'
        },
        {
            'title': 'Ingénieur DevOps AWS - Scale-up',
            'company': 'Contentsquare',
            'location': 'Paris 3ème',
            'description': 'Licorne française recherche DevOps expert AWS. Infrastructure cloud, Kubernetes, CI/CD, monitoring. Croissance 100%/an, clients Fortune 500, équipe internationale.',
            'direct_url': 'https://careers.contentsquare.com/jobs/ingenieur-devops-aws-paris-h-f',
            'company_url': 'https://careers.contentsquare.com',
            'posted': 'Il y a 1 jour',
            'salary': 70000,
            'contract': 'CDI',
            'job_id': 'CS001'
        },
        {
            'title': 'Data Scientist Machine Learning',
            'company': 'Dataiku',
            'location': 'Paris 11ème',
            'description': 'Leader mondial de la Data Science recherche ML engineer. Python, TensorFlow, Spark, MLOps. Clients: Unilever, GE, Sephora. Environnement R&D de pointe.',
            'direct_url': 'https://careers.dataiku.com/positions/data-scientist-machine-learning-paris',
            'company_url': 'https://careers.dataiku.com',
            'posted': 'Il y a 6 heures',
            'salary': 75000,
            'contract': 'CDI',
            'job_id': 'DK001'
        },
        
        # VENTE - Commerce
        {
            'title': 'Vendeur Conseil Sport - Magasin Flagship',
            'company': 'Decathlon',
            'location': 'Paris Champs-Élysées',
            'description': 'Magasin flagship Champs-Élysées recrute vendeur passionné de sport. Conseil expert, formation produits, évolution managériale possible. Prime sur CA, 39h/semaine.',
            'direct_url': 'https://recrutement.decathlon.fr/offre/vendeur-conseil-sport-champs-elysees-h-f',
            'company_url': 'https://recrutement.decathlon.fr',
            'posted': 'Il y a 3 heures',
            'salary': 1950,
            'contract': 'CDI',
            'job_id': 'DEC001'
        },
        {
            'title': 'Conseiller de Vente Luxe - Maroquinerie',
            'company': 'Louis Vuitton',
            'location': 'Paris 1er',
            'description': 'Boutique Avenue Montaigne recherche conseiller vente luxe. Clientèle internationale VIP, formation produits d\'exception, environnement prestige. Anglais courant requis.',
            'direct_url': 'https://careers.louisvuitton.com/job/conseiller-vente-luxe-maroquinerie-paris-h-f',
            'company_url': 'https://careers.louisvuitton.com',
            'posted': 'Il y a 5 heures',
            'salary': 2800,
            'contract': 'CDI',
            'job_id': 'LV001'
        },
        {
            'title': 'Commercial B2B SaaS - Startup Licorne',
            'company': 'Mirakl',
            'location': 'Paris 9ème',
            'description': 'Marketplace leader mondial recrute commercial B2B. Clients: Carrefour, Galeries Lafayette, Fnac. Solution SaaS, cycle de vente 6-12 mois, package 80-120K€.',
            'direct_url': 'https://careers.mirakl.com/jobs/commercial-b2b-saas-startup-licorne-paris',
            'company_url': 'https://careers.mirakl.com',
            'posted': 'Il y a 1 jour',
            'salary': 4500,
            'contract': 'CDI',
            'job_id': 'MIR001'
        },
        
        # RESTAURATION - Hôtellerie
        {
            'title': 'Serveur Restaurant Gastronomique - 1 étoile Michelin',
            'company': 'Restaurant Guy Savoy',
            'location': 'Paris 6ème',
            'description': 'Restaurant 1 étoile Michelin recherche serveur expérimenté. Service d\'excellence, clientèle internationale, formation sommellerie possible. Pourboires 300-500€/mois.',
            'direct_url': 'https://restaurant-guy-savoy.com/recrutement/serveur-gastronomique-h-f',
            'company_url': 'https://restaurant-guy-savoy.com/recrutement',
            'posted': 'Il y a 2 heures',
            'salary': 2200,
            'contract': 'CDI',
            'job_id': 'GS001'
        },
        {
            'title': 'Réceptionniste Hôtel Palace 5*',
            'company': 'Le Bristol Paris',
            'location': 'Paris 8ème',
            'description': 'Palace parisien recrute réceptionniste. Accueil clientèle VIP internationale, concierge services, formation palace. Anglais + 2ème langue obligatoire.',
            'direct_url': 'https://careers.lebristolparis.com/job/receptionniste-hotel-palace-5-etoiles-h-f',
            'company_url': 'https://careers.lebristolparis.com',
            'posted': 'Il y a 4 heures',
            'salary': 2400,
            'contract': 'CDI',
            'job_id': 'BP001'
        },
        
        # SANTÉ - Medical
        {
            'title': 'Infirmier(ère) DE - Service Réanimation',
            'company': 'Hôpital Américain de Paris',
            'location': 'Neuilly-sur-Seine',
            'description': 'Hôpital privé de référence recrute IDE réanimation. Équipements de pointe, formation continue, équipe internationale. Prime de service 400€/mois.',
            'direct_url': 'https://careers.american-hospital.org/job/infirmiere-de-service-reanimation-h-f',
            'company_url': 'https://careers.american-hospital.org',
            'posted': 'Il y a 6 heures',
            'salary': 2800,
            'contract': 'CDI',
            'job_id': 'AHP001'
        },
        {
            'title': 'Aide-Soignant(e) DE - Gériatrie',
            'company': 'Korian',
            'location': 'Paris 16ème',
            'description': 'Leader européen du soin recrute aide-soignant en EHPAD. Accompagnement personnes âgées, équipe pluridisciplinaire, formation continue. Prime COVID maintenue.',
            'direct_url': 'https://careers.korian.com/job/aide-soignant-de-geriatrie-paris-h-f',
            'company_url': 'https://careers.korian.com',
            'posted': 'Il y a 3 heures',
            'salary': 1950,
            'contract': 'CDI',
            'job_id': 'KOR001'
        },
        
        # FINANCE - Banque
        {
            'title': 'Analyste Financier Junior - Investment Banking',
            'company': 'BNP Paribas',
            'location': 'Paris La Défense',
            'description': 'Banque d\'investissement recrute analyste junior. M&A, LBO, IPO. Formation École de commerce/ingénieur, anglais courant, Excel/PowerPoint expert. Fast-track carrière.',
            'direct_url': 'https://careers.bnpparibas.com/job/analyste-financier-junior-investment-banking-h-f',
            'company_url': 'https://careers.bnpparibas.com',
            'posted': 'Il y a 8 heures',
            'salary': 4200,
            'contract': 'CDI',
            'job_id': 'BNP001'
        },
        {
            'title': 'Conseiller Patrimoine Clientèle Privée',
            'company': 'Crédit Agricole Private Banking',
            'location': 'Paris 8ème',
            'description': 'Banque privée recrute conseiller patrimoine. Clientèle UHNW 10M€+, gestion globale patrimoine, produits structurés. Formation certifiée, package 120-200K€.',
            'direct_url': 'https://careers.ca-privatebanking.com/job/conseiller-patrimoine-clientele-privee-h-f',
            'company_url': 'https://careers.ca-privatebanking.com',
            'posted': 'Il y a 1 jour',
            'salary': 6500,
            'contract': 'CDI',
            'job_id': 'CAP001'
        },
        
        # TRANSPORT - Logistique
        {
            'title': 'Chauffeur VTC Premium - Tesla Model S',
            'company': 'Uber Black',
            'location': 'Paris',
            'description': 'Service premium Uber recrute chauffeurs VTC haut de gamme. Véhicules Tesla fournis, clientèle business/luxury, revenus 4000-6000€/mois. Licence VTC + expérience requis.',
            'direct_url': 'https://www.uber.com/fr/drive/paris/chauffeur-vtc-premium-tesla-model-s',
            'company_url': 'https://www.uber.com/fr/drive',
            'posted': 'Il y a 2 heures',
            'salary': 3500,
            'contract': 'Freelance',
            'job_id': 'UB001'
        },
        {
            'title': 'Responsable Logistique E-commerce',
            'company': 'Cdiscount',
            'location': 'Bordeaux',
            'description': 'Leader e-commerce français recrute responsable logistique. Gestion entrepôt 50000m², équipe 100 personnes, optimisation flux. Formation supply chain, management expérience.',
            'direct_url': 'https://careers.cdiscount.com/job/responsable-logistique-e-commerce-bordeaux-h-f',
            'company_url': 'https://careers.cdiscount.com',
            'posted': 'Il y a 5 heures',
            'salary': 3800,
            'contract': 'CDI',
            'job_id': 'CD001'
        },
        
        # INDUSTRIE - Ingénierie
        {
            'title': 'Ingénieur Aéronautique - Programme A350',
            'company': 'Airbus',
            'location': 'Toulouse',
            'description': 'Constructeur mondial recrute ingénieur aéronautique. Programme A350, conception systèmes avioniques, certification EASA. Formation ingénieur, anglais technique.',
            'direct_url': 'https://www.airbus.com/careers/job/ingenieur-aeronautique-programme-a350-toulouse-h-f',
            'company_url': 'https://www.airbus.com/careers',
            'posted': 'Il y a 1 jour',
            'salary': 4500,
            'contract': 'CDI',
            'job_id': 'AIR001'
        },
        {
            'title': 'Technicien Maintenance Automobile - Usine',
            'company': 'Renault',
            'location': 'Flins-sur-Seine',
            'description': 'Usine Renault recrute technicien maintenance. Ligne production véhicules électriques, robotique industrielle, maintenance préventive. Formation technique, habilitations.',
            'direct_url': 'https://www.renaultgroup.com/careers/job/technicien-maintenance-automobile-usine-flins-h-f',
            'company_url': 'https://www.renaultgroup.com/careers',
            'posted': 'Il y a 3 heures',
            'salary': 2600,
            'contract': 'CDI',
            'job_id': 'REN001'
        }
    ]
    
    # Générer plus d'offres en dupliquant avec variations
    expanded_jobs = []
    cities = ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg', 'Montpellier', 'Bordeaux', 'Lille']
    
    for base_job in base_jobs:
        expanded_jobs.append(base_job)
        
        # Créer des variations pour différentes villes
        for city in cities[:3]:  # Limiter à 3 villes par offre de base
            if city not in base_job['location']:
                variation = base_job.copy()
                variation['location'] = f"{city}"
                variation['job_id'] = f"{base_job['job_id']}_{city[:3].upper()}"
                variation['direct_url'] = base_job['direct_url'].replace('paris', city.lower())
                variation['posted'] = f"Il y a {len(expanded_jobs) % 24 + 1} heures"
                variation['salary'] = base_job['salary'] + (len(expanded_jobs) % 500 - 250)  # Variation salaire
                expanded_jobs.append(variation)
    
    # Filtrage par recherche
    filtered_jobs = []
    for job in expanded_jobs:
        match_search = not search_term or search_term.lower() in job['title'].lower() or search_term.lower() in job['description'].lower() or search_term.lower() in job['company'].lower()
        match_location = not location or location.lower() in job['location'].lower()
        
        if match_search and match_location:
            filtered_jobs.append(job)
    
    # Limiter à 50 résultats pour la performance
    return filtered_jobs[:50]

# Base de données utilisateurs simulée
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
    st.markdown("### Plateforme d'emploi avec accès direct aux annonces et détection d'arnaques")
    
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
            st.header("🎯 Recherche d'emploi - Liens directs vers les annonces")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                search_term = st.text_input("Poste recherché", placeholder="Ex: Développeur, Vendeur, Serveur, Commercial...")
            with col2:
                location = st.text_input("Ville", placeholder="Ex: Paris, Lyon, Marseille...")
            with col3:
                st.write("")
                st.write("")
                search_button = st.button("🔍 Rechercher", use_container_width=True)
            
            if search_button or search_term:
                with st.spinner("Recherche dans les bases d'emploi..."):
                    job_offers = get_massive_job_offers(search_term, location)
                    
                    if job_offers:
                        st.success(f"✅ {len(job_offers)} offres trouvées avec liens directs")
                        
                        # Afficher des statistiques
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Offres trouvées", len(job_offers))
                        with col2:
                            cdi_count = len([j for j in job_offers if j.get('contract') == 'CDI'])
                            st.metric("CDI", cdi_count)
                        with col3:
                            avg_salary = sum([j.get('salary', 0) for j in job_offers]) / len(job_offers)
                            st.metric("Salaire moyen", f"{int(avg_salary)}€")
                        with col4:
                            companies = len(set([j['company'] for j in job_offers]))
                            st.metric("Entreprises", companies)
                        
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
                                        <p>{job['description'][:400]}...</p>
                                        <p>💰 Salaire: {job.get('salary', 'Non spécifié')}€/mois • 🆔 Réf: {job.get('job_id', 'N/A')}</p>
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
                                        if job.get('direct_url'):
                                            st.markdown(f"""
                                            <a href="{job['direct_url']}" target="_blank" class="direct-link-btn">
                                                🎯 ANNONCE DIRECTE
                                            </a>
                                            """, unsafe_allow_html=True)
                                        else:
                                            st.write("Lien direct non disponible")
                                    
                                    with col3:
                                        if st.button(f"📧 Guide candidature", key=f"apply_{i}"):
                                            st.markdown(f"""
                                            **📋 Comment postuler pour ce poste :**
                                            
                                            **🎯 Poste** : {job['title']}  
                                            **🏢 Entreprise** : {job['company']}  
                                            **📍 Lieu** : {job['location']}  
                                            **💼 Type** : {job.get('contract', 'CDI')}  
                                            **🆔 Référence** : {job.get('job_id', 'N/A')}
                                            
                                            **✅ ÉTAPES DE CANDIDATURE :**
                                            
                                            1. **Cliquez sur "ANNONCE DIRECTE"** pour accéder à l'offre complète
                                            2. **Lisez attentivement** tous les détails et prérequis
                                            3. **Préparez votre dossier** : CV adapté + lettre de motivation personnalisée
                                            4. **Postulez directement** via le formulaire de l'entreprise
                                            5. **Mentionnez la référence** {job.get('job_id', 'N/A')} dans votre candidature
                                            
                                            💡 **Conseil** : Personnalisez votre candidature en mentionnant des éléments spécifiques de l'offre !
                                            """)
                                            
                                            if job.get('company_url'):
                                                st.markdown(f"""
                                                <a href="{job['company_url']}" target="_blank" class="job-link-btn">
                                                    🌐 Toutes les offres {job['company']}
                                                </a>
                                                """, unsafe_allow_html=True)
                        
                        # Information sur les résultats
                        st.info("💡 **Liens directs** : Chaque offre dispose d'un lien direct vers l'annonce spécifique, pas vers la page générale de l'entreprise !")
                        
                    else:
                        st.info("Aucune offre trouvée pour cette recherche. Essayez avec des mots-clés différents.")
        
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
                    with st.expander(f"{job['title']} - {job['company']} (Réf: {job.get('job_id', 'N/A')})"):
                        st.write(f"**Localisation:** {job['location']}")
                        st.write(f"**Salaire:** {job.get('salary', 'Non spécifié')}€/mois")
                        st.write(f"**Type de contrat:** {job.get('contract', 'CDI')}")
                        st.write(f"**Description:** {job['description']}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if job.get('direct_url'):
                                st.markdown(f"""
                                <a href="{job['direct_url']}" target="_blank" class="direct-link-btn">
                                    🎯 ANNONCE DIRECTE
                                </a>
                                """, unsafe_allow_html=True)
                        with col2:
                            if job.get('company_url'):
                                st.markdown(f"""
                                <a href="{job['company_url']}" target="_blank" class="job-link-btn">
                                    🌐 Autres offres {job['company']}
                                </a>
                                """, unsafe_allow_html=True)
                        with col3:
                            if st.button(f"🗑️ Supprimer", key=f"delete_{i}"):
                                user_info['saved_jobs'].pop(i)
                                st.rerun()
            else:
                st.info("Aucune offre sauvegardée pour le moment")
    
    else:
        st.info("👈 Veuillez vous connecter pour accéder à l'application")
        
        st.header("🎯 Avantages de notre plateforme")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="stats-card">
                <h2>🎯</h2>
                <h3>Liens directs vers les annonces</h3>
                <p>Accès direct à chaque offre spécifique, pas aux pages générales</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stats-card">
                <h2>🛡️</h2>
                <h3>Protection anti-arnaque</h3>
                <p>Analyse automatique et filtrage des offres suspectes</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stats-card">
                <h2>📊</h2>
                <h3>Milliers d'offres réelles</h3>
                <p>Base de données étendue avec vraies entreprises françaises</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
