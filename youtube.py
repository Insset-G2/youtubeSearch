from flask import Flask, render_template, request, jsonify
from googleapiclient.discovery import build

app = Flask(__name__)

# Clé API YouTube Data (à stocker de manière sécurisée)
api_key = 'AIzaSyAzycTU0Au65krEZCJp5-DX_7RCvWwam-s'

# Initialisez l'API YouTube Data
youtube = build('youtube', 'v3', developerKey=api_key)


@app.route('/')
def index():
    # Renvoie le template HTML index.html lorsque la route racine est accédée
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    # Récupère les paramètres de la requête GET : query (recherche) et pageToken (jeton de page)
    query = request.args.get('query')
    page_token = request.args.get('pageToken')
    max_results = 10
    if not query:
        # Si aucun paramètre de recherche n'est spécifié, renvoie une erreur
        return jsonify({'error': 'Aucune requête spécifiée'})

    try:
        # Effectue une recherche YouTube en utilisant l'API avec les paramètres spécifiés
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            type='video',
            maxResults=max_results,
            pageToken=page_token
        ).execute()

        # Initialise une liste pour stocker les résultats de la recherche
        results = []
        for item in search_response['items']:
            # Récupère les informations pertinentes pour chaque vidéo dans les résultats de la recherche
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            thumbnail = item['snippet']['thumbnails']['default']['url']
            url = f'https://www.youtube.com/watch?v={video_id}'
            # Ajoute les informations de la vidéo à la liste des résultats
            results.append({'url': url, 'thumbnail': thumbnail, 'title': title})

        # Récupère les jetons de page suivante et précédente, s'ils existent
        next_page_token = search_response.get('nextPageToken', '')
        prev_page_token = search_response.get('prevPageToken', '')

        # Renvoie les résultats de la recherche ainsi que les jetons de page suivante et précédente
        return jsonify({
            'youtube_results': results,
            'nextPageToken': next_page_token,
            'prevPageToken': prev_page_token
        })

    except Exception as e:
        # En cas d'erreur, renvoie un message d'erreur sous forme JSON
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    # Exécute l'application Flask en mode debug lorsqu'elle est exécutée directement
    app.run(host='0.0.0.0', port=5016, debug=True)