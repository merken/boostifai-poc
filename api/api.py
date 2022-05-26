from datetime import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from top2vec import Top2Vec
from bertopic import BERTopic
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/search', methods=['POST'])
def search():
   root = request.form.get('root')
   search = request.form.get('search')
   if search:
        print(f'SEARCHING {root} {search}')
        connection_string = os.getenv('STORAGE_CONNECTION_STRING')
        print(f'connection_string {connection_string}')
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        file_name = root.replace('https://', '').replace('/', '')
        berttopic_model_name = f'{file_name}.bertopic.model'
        blob_client = blob_service_client.get_blob_client(container='models', blob=berttopic_model_name)
        with open(berttopic_model_name, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        berttopic_model = BERTopic.load(berttopic_model_name)
        topics = berttopic_model.find_topics(search)
        return render_template('results.html', results = topics)
   else:
        return redirect(url_for('index'))

if __name__ == '__main__':
   app.run()