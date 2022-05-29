import base64
import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import matplotlib
from top2vec import Top2Vec
from bertopic import BERTopic
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)


def getModelNameFromRoot() -> str:
    root = 'https://streekproduct.streekmarkt.be'
    return root.replace('https://', '').replace('/', '')


def getBlobClient() -> BlobServiceClient:
    connection_string = os.environ.get('STORAGE_CONNECTION_STRING')
    return BlobServiceClient.from_connection_string(
        connection_string)


def downloadFileFromModels(blob_service_client: BlobServiceClient, fileName: str):
    blob_client = blob_service_client.get_blob_client(
        container='models', blob=fileName)
    with open(fileName, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())


def similarWords(top2vec_model: Top2Vec, word: str) -> list[str]:
    results: list[str] = []
    words, word_scores = top2vec_model.similar_words(
        keywords=[word], keywords_neg=[], num_words=20)

    for word, score in zip(words, word_scores):
        results.append(word)
    return results


def findTopics(top2vec_model: Top2Vec, search: str) -> any:
    topic_words, word_scores, topic_scores, topic_nums = top2vec_model.search_topics(
        keywords=[search], num_topics=5)
    return topic_nums


def wordCloudFromTopic(top2vec_model: Top2Vec, topic: any) -> str:
    encoded_img_data = None
    matplotlib.pyplot.switch_backend('Agg')
    wordcloud = top2vec_model.generate_topic_wordcloud(topic)
    if wordcloud:
        random_string = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=5))
        tempfile_name = f'{random_string}.png'
        wordcloud.savefig(tempfile_name)

        with open(tempfile_name, "rb") as image_file:
            encoded_img_data = base64.b64encode(image_file.read())
        os.remove(tempfile_name)
    return encoded_img_data


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
    search = request.form.get('search')
    if search:
        model_name = getModelNameFromRoot()

        # berttopic_model_name = f'{file_name}.bertopic.model'
        top2vec_model_name = f'{model_name}.top2vec.model'

        blob_service_client = getBlobClient()

        # downloadFileFromModels(blob_service_client, berttopic_model_name)
        downloadFileFromModels(blob_service_client, top2vec_model_name)

        top2vec_model = Top2Vec.load(top2vec_model_name)

        results = similarWords(top2vec_model, search)

        topics = findTopics(top2vec_model, search)

        img_data = wordCloudFromTopic(top2vec_model, topics[0])

        if(img_data):
            return render_template('results.html', results=results, img_data=img_data.decode('utf-8'))

        return render_template('results.html', results=results)
    else:
        return redirect(url_for('index'))


@app.route('/api/v1/topics/<topic>', methods=['GET'])
def api_topics(topic: str):
    model_name = getModelNameFromRoot()

    top2vec_model_name = f'{model_name}.top2vec.model'

    blob_service_client = getBlobClient()

    downloadFileFromModels(blob_service_client, top2vec_model_name)

    top2vec_model = Top2Vec.load(top2vec_model_name)

    results = similarWords(top2vec_model, topic)
    return jsonify(results)


if __name__ == '__main__':
    app.run()
