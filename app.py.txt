import streamlit as st
import requests
import re
import hashlib
import json
from datetime import datetime
import time

# Configuration de la page
st.set_page_config(
    page_title="Safe Job Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design moderne
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
    .risk-high { color: #DC143C; font-weight: bold; }
    .risk-medium { color: #FF8C00; font-weight: bold; }
    .risk-low { color: #2E8B57; font-weight: bold; }
    .user-info {
        background: #f0f8f0;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Classe de détection d'arnaques améliorée
class AdvancedJobScamDetector:
    def __init__(self):
        self.patterns = {
            "urgence": [r"urgent|rapidement|immédiatement|vite|maintenant"],
            "promesse_argent": [r"\d+\s*€|euros?|salaire élevé|gagner \d+|revenus? garanti"],
            "contacts_non_pro": [r"whatsapp|telegram|gmail\.com|yahoo\.com|hotmail\.com"],
            "fautes_orthographe": [r"opportuniter|debutant|asurer"],
            "paiement_avance": [r"paiement anticipé|frais d'inscription|caution|versement"],
            "travail_domicile": [r"travail à domicile|depuis chez vous|télétravail facile"]
        }
        
        self.pattern_weights = {
            "urgence": 0.3,
            "promesse_argent": 0.5,
            "contacts_non_pro": 0.7,
            "fautes_orthographe": 0.4,
            "paiement_avance": 0.9,
            "travail_domicile": 0.3
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
        
        # Générer des recommandations
        recommendations_map = {
            'urgence': "⚠️ Méfiez-vous des offres créant un sentiment d'urgence artificiel",
            'promesse_argent': "💰 Attention aux promesses de gains élevés sans compétences",
            'contacts_non_pro': "📧 Les recruteurs sérieux utilisent des emails professionnels",
            'fautes_orthographe': "✍️ Vérifiez l'orthographe et la grammaire de l'offre",
            'paiement_avance': "🚨 ALERTE: Ne payez jamais pour obtenir un emploi",
            'travail_domicile': "🏠 Vérifiez la légitimité des offres de télétravail"
        }
        
        unique_patterns = list(set(results['detected_patterns']))
        results['recommendations'] = [recommendations_map[p] for p in unique_patterns if p in recommendations_map]
        
        return results

# Simulation d'une base de données utilisateurs
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "demo@example.com": {
            "password": "demo123",
            "name": "Utilisateur Demo",
            "searches": []
        }
    }

# Simulation d'offres d'emploi (en réalité, on intégrerait une vraie API)
def get_job_offers(search_term="", location=""):
    """Simulation d'une recherche d'offres d'emploi"""
    job_offers = [
        {
            "title": "Développeur Python Senior",
            "company": "TechCorp",
            "location": "Paris",
            "description": "Nous recherchons un développeur Python expérimenté pour rejoindre notre équipe. CDI, salaire selon expérience. Contactez-nous à recrutement@techcorp.fr",
            "url": "https://example.com/job1",
            "posted": "Il y a 2 jours"
        },
        {
            "title": "URGENT! Gagnez 5000€/mois facilement!",
            "company": "EasyMoney",
            "location": "Télétravail",
            "description": "Opportunité unique! Gagnez 5000€ par mois sans expérience! Paiement anticipé de 200€ requis. Contactez rapidement sur WhatsApp: 06.12.34.56.78",
            "url": "https://example.com/job2",
            "posted": "Il y a 1 heure"
        },
        {
            "title": "Assistant(e) Commercial(e)",
            "company": "Commerce Plus",
            "location": "Lyon",
            "description": "Poste d'assistant commercial en CDI. Formation fournie. Salaire fixe + commissions. Candidature à envoyer à rh@commerceplus.fr",
            "url": "https://example.com/job3",
            "posted": "Il y a 1 jour"
        },
        {
            "title": "Travail à domicile - Gains garantis!",
            "company": "HomeWork Pro",
            "location": "France entière",
            "description": "Travaillez depuis chez vous! Revenus garantis de 3000€/mois minimum! Aucune expérience requise. Frais d'inscription: 150€. Contactez-nous vite!",
            "url": "https://example.com/job4",
            "posted": "Il y a 3 heures"
        }
    ]
    
    # Filtrer par terme de recherche
    if search_term:
        job_offers = [job for job in job_offers if search_term.lower() in job['title'].lower() or search_term.lower() in job['description'].lower()]
    
    return job_offers

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
            "searches": []
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
    st.markdown('<h1 class="main-header">🛡️ Safe Job Detector</h1>', unsafe_allow_html=True)
    st.markdown("### Trouvez des offres d'emploi et détectez les arnaques automatiquement")
    
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
        tab1, tab2, tab3 = st.tabs(["🔍 Recherche d'emploi", "🛡️ Analyse d'offre", "📊 Historique"])
        
        with tab1:
            st.header("Recherche d'offres d'emploi")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                search_term = st.text_input("Poste recherché", placeholder="Ex: Développeur Python")
            with col2:
                location = st.text_input("Localisation", placeholder="Ex: Paris")
            
            if st.button("🔍 Rechercher"):
                with st.spinner("Recherche en cours..."):
                    time.sleep(1)  # Simulation du temps de recherche
                    job_offers = get_job_offers(search_term, location)
                    
                    if job_offers:
                        st.success(f"✅ {len(job_offers)} offres trouvées")
                        
                        detector = AdvancedJobScamDetector()
                        
                        for job in job_offers:
                            # Analyser chaque offre
                            analysis = detector.analyze_text(job['description'])
                            
                            # Déterminer la couleur du risque
                            if analysis['risk_score'] >= 0.7:
                                risk_class = "risk-high"
                                risk_emoji = "🚨"
                                risk_text = "RISQUE ÉLEVÉ"
                            elif analysis['risk_score'] >= 0.4:
                                risk_class = "risk-medium"
                                risk_emoji = "⚠️"
                                risk_text = "RISQUE MOYEN"
                            else:
                                risk_class = "risk-low"
                                risk_emoji = "✅"
                                risk_text = "RISQUE FAIBLE"
                            
                            # Afficher l'offre
                            st.markdown(f"""
                            <div class="job-card">
                                <h3>{job['title']}</h3>
                                <p><strong>🏢 {job['company']}</strong> • 📍 {job['location']} • 🕒 {job['posted']}</p>
                                <p>{job['description'][:200]}...</p>
                                <p><span class="{risk_class}">{risk_emoji} {risk_text} ({int(analysis['risk_score']*100)}%)</span></p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Boutons d'action
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                if st.button(f"📋 Analyser en détail", key=f"analyze_{job['title']}"):
                                    st.session_state.selected_job = job
                                    st.session_state.selected_analysis = analysis
                            with col2:
                                st.link_button("🔗 Voir l'offre", job['url'])
                            with col3:
                                if analysis['risk_score'] >= 0.4:
                                    st.button("🚨 Signaler", key=f"report_{job['title']}")
                    else:
                        st.info("Aucune offre trouvée pour cette recherche")
        
        with tab2:
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
                    
                    # Affichage des résultats
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # Jauge de risque
                        risk_percentage = int(analysis['risk_score'] * 100)
                        
                        if risk_percentage >= 70:
                            st.error(f"🚨 RISQUE ÉLEVÉ: {risk_percentage}%")
                        elif risk_percentage >= 40:
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
        
        with tab3:
            st.header("Historique de vos recherches")
            st.info("Fonctionnalité en développement - Vos recherches seront bientôt sauvegardées ici")
    
    else:
        st.info("👈 Veuillez vous connecter pour accéder à l'application")
        
        # Aperçu pour les utilisateurs non connectés
        st.header("🎯 Fonctionnalités")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🔍 Recherche d'emploi
            - Recherche d'offres en temps réel
            - Filtres par poste et localisation
            - Analyse automatique des risques
            """)
        
        with col2:
            st.markdown("""
            ### 🛡️ Détection d'arnaques
            - Analyse intelligente du contenu
            - Score de risque en temps réel
            - Recommandations personnalisées
            """)
        
        with col3:
            st.markdown("""
            ### 📊 Suivi personnel
            - Historique des recherches
            - Offres sauvegardées
            - Alertes personnalisées
            """)

if __name__ == "__main__":
    main()
