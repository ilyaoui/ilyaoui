#!/usr/bin/env python3
"""
OAuth2 Helper pour TeamSnap API
--------------------------------
Ce script aide à obtenir un Access Token pour l'API TeamSnap.

Étapes:
1. Enregistrez votre application sur TeamSnap Developer Portal
2. Obtenez votre Client ID et Client Secret
3. Utilisez ce script pour compléter le flux OAuth2
"""

import requests
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
import json
from typing import Dict, Optional

TEAMSNAP_AUTH_URL = "https://auth.teamsnap.com/oauth/authorize"
TEAMSNAP_TOKEN_URL = "https://auth.teamsnap.com/oauth/token"
TEAMSNAP_API_URL = "https://api.teamsnap.com/v3"


class TeamSnapOAuth:
    """Gère le flux OAuth2 pour TeamSnap"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = "urn:ietf:wg:oauth:2.0:oob"):
        """
        Initialise le client OAuth

        Args:
            client_id: Client ID de votre application TeamSnap
            client_secret: Client Secret de votre application
            redirect_uri: URI de redirection (par défaut: out-of-band)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_authorization_url(self, scope: str = "read write") -> str:
        """
        Génère l'URL d'autorisation

        Args:
            scope: Scopes demandés (par défaut: read write)

        Returns:
            URL d'autorisation complète
        """
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': scope
        }

        auth_url = f"{TEAMSNAP_AUTH_URL}?{urlencode(params)}"
        return auth_url

    def exchange_code_for_token(self, authorization_code: str) -> Dict:
        """
        Échange le code d'autorisation contre un access token

        Args:
            authorization_code: Code d'autorisation reçu

        Returns:
            Dictionnaire contenant access_token, refresh_token, etc.
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }

        try:
            response = requests.post(TEAMSNAP_TOKEN_URL, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de l'échange du code: {e}")
            if hasattr(e.response, 'text'):
                print(f"Détails: {e.response.text}")
            return {}

    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Rafraîchit un access token expiré

        Args:
            refresh_token: Refresh token obtenu précédemment

        Returns:
            Nouveau dictionnaire de tokens
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

        try:
            response = requests.post(TEAMSNAP_TOKEN_URL, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors du rafraîchissement: {e}")
            return {}

    def test_token(self, access_token: str) -> bool:
        """
        Teste si un access token est valide

        Args:
            access_token: Token à tester

        Returns:
            True si le token est valide
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(f"{TEAMSNAP_API_URL}/me", headers=headers)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


def interactive_oauth_flow():
    """
    Flux OAuth2 interactif en ligne de commande
    """
    print("=" * 70)
    print("TEAMSNAP OAUTH2 AUTHENTICATION")
    print("=" * 70)
    print()
    print("Pour obtenir vos credentials:")
    print("1. Allez sur: https://www.teamsnap.com/documentation/apiv3")
    print("2. Contactez l'équipe TeamSnap pour obtenir un Client ID/Secret")
    print("   (api@teamsnap.com)")
    print()

    client_id = input("Entrez votre Client ID: ").strip()
    client_secret = input("Entrez votre Client Secret: ").strip()

    if not client_id or not client_secret:
        print("\n✗ Client ID et Client Secret sont requis!")
        return

    oauth = TeamSnapOAuth(client_id, client_secret)

    # Étape 1: Obtenir l'URL d'autorisation
    print("\n--- ÉTAPE 1: AUTORISATION ---")
    auth_url = oauth.get_authorization_url()
    print(f"\n1. Ouvrez cette URL dans votre navigateur:")
    print(f"\n   {auth_url}\n")

    open_browser = input("Ouvrir automatiquement dans le navigateur? (o/n): ").strip().lower()
    if open_browser == 'o':
        webbrowser.open(auth_url)

    print("\n2. Connectez-vous et autorisez l'application")
    print("3. Copiez le code d'autorisation reçu")
    print()

    # Étape 2: Échanger le code contre un token
    print("--- ÉTAPE 2: OBTENTION DU TOKEN ---")
    auth_code = input("\nEntrez le code d'autorisation: ").strip()

    if not auth_code:
        print("\n✗ Code d'autorisation requis!")
        return

    print("\nÉchange du code contre un access token...")
    token_data = oauth.exchange_code_for_token(auth_code)

    if token_data and 'access_token' in token_data:
        print("\n✓ Succès! Token obtenu.")
        print("\n" + "=" * 70)
        print("VOS CREDENTIALS:")
        print("=" * 70)
        print(f"\nAccess Token: {token_data['access_token']}")

        if 'refresh_token' in token_data:
            print(f"Refresh Token: {token_data['refresh_token']}")

        if 'expires_in' in token_data:
            print(f"Expire dans: {token_data['expires_in']} secondes")

        # Test du token
        print("\n--- ÉTAPE 3: TEST DU TOKEN ---")
        print("Test de l'access token...")
        if oauth.test_token(token_data['access_token']):
            print("✓ Token valide et fonctionnel!")
        else:
            print("✗ Token invalide ou erreur de connexion")

        # Sauvegarder dans un fichier
        save = input("\nSauvegarder dans config.json? (o/n): ").strip().lower()
        if save == 'o':
            config = {
                'client_id': client_id,
                'client_secret': client_secret,
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token', ''),
                'expires_in': token_data.get('expires_in', 0)
            }

            with open('config.json', 'w') as f:
                json.dump(config, f, indent=2)

            print("✓ Configuration sauvegardée dans config.json")

    else:
        print("\n✗ Échec de l'obtention du token")
        print("Vérifiez vos credentials et réessayez")

    print("\n" + "=" * 70)


def load_config_and_test():
    """
    Charge la configuration depuis config.json et teste le token
    """
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        print("Configuration chargée depuis config.json")
        print(f"Client ID: {config['client_id']}")

        oauth = TeamSnapOAuth(config['client_id'], config['client_secret'])

        print("\nTest de l'access token...")
        if oauth.test_token(config['access_token']):
            print("✓ Token valide!")
            return config['access_token']
        else:
            print("✗ Token expiré ou invalide")

            if config.get('refresh_token'):
                print("\nTentative de rafraîchissement du token...")
                new_tokens = oauth.refresh_access_token(config['refresh_token'])

                if new_tokens and 'access_token' in new_tokens:
                    print("✓ Token rafraîchi avec succès!")

                    # Mettre à jour la config
                    config.update(new_tokens)
                    with open('config.json', 'w') as f:
                        json.dump(config, f, indent=2)

                    return new_tokens['access_token']

        return None

    except FileNotFoundError:
        print("Fichier config.json non trouvé")
        print("Exécutez d'abord le flux OAuth pour créer la configuration")
        return None
    except json.JSONDecodeError:
        print("Erreur de lecture du fichier config.json")
        return None


if __name__ == "__main__":
    import sys

    print("TeamSnap OAuth2 Helper\n")

    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Mode test: charge et teste la config existante
        load_config_and_test()
    else:
        # Mode interactif: flux OAuth complet
        interactive_oauth_flow()
