from flask import Flask, render_template, request, jsonify, send_from_directory
from googleapiclient.discovery import build
from flask_swagger_ui import get_swaggerui_blueprint
import os

app = Flask(__name__)

# Clé API YouTube Data (à stocker de manière sécurisée)
api_key = 'AIzaSyAzycTU0Au65krEZCJp5-DX_7RCvWwam-s'

# Initialisez l'API YouTube Data
youtube = build('youtube', 'v3', developerKey=api_key)

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = 'static/swagger.json'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "YouTube Search API"
    },
)

app.register_blueprint(swaggerui_blueprint)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    page_token = request.args.get('pageToken')
    max_results = 10
    if not query:
        return jsonify({'error': 'Aucune requête spécifiée'}), 400

    try:
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            type='video',
            maxResults=max_results,
            pageToken=page_token
        ).execute()

        results = []
        for item in search_response['items']:
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            thumbnail = item['snippet']['thumbnails']['default']['url']
            url = f'https://www.youtube.com/watch?v={video_id}'
            results.append({'url': url, 'thumbnail': thumbnail, 'title': title})

        next_page_token = search_response.get('nextPageToken', '')
        prev_page_token = search_response.get('prevPageToken', '')

        return jsonify({
            'youtube_results': results,
            'nextPageToken': next_page_token,
            'prevPageToken': prev_page_token
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/swagger.json')
def swagger_json():
    return send_from_directory(os.path.dirname(__file__), 'swagger.json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5016, debug=True)
