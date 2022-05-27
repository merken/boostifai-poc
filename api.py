# import base64
# from datetime import datetime
# import os
# import random
# import string
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
# import matplotlib
# from top2vec import Top2Vec
# from bertopic import BERTopic
# from azure.storage.blob import BlobServiceClient

app = Flask(__name__)

@app.route('/')
def index():
    print('Request for index page received')
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


# @app.route('/search', methods=['POST'])
# def search():
#     #  root = request.form.get('root')
#     root = 'https://streekproduct.streekmarkt.be'
#     search = request.form.get('search')
#     if search:
#         print(f'SEARCHING {root} {search}')
#         with open('connection.string.secret', "r") as connection_string_file:
#             connection_string = connection_string_file.read()

#         blob_service_client = BlobServiceClient.from_connection_string(
#             connection_string)
#         file_name = root.replace('https://', '').replace('/', '')

#         berttopic_model_name = f'{file_name}.bertopic.model'
#         top2vec_model_name = f'{file_name}.top2vec.model'
#         blob_client = blob_service_client.get_blob_client(
#             container='models', blob=top2vec_model_name)
#         with open(top2vec_model_name, "wb") as download_file:
#             download_file.write(blob_client.download_blob().readall())

#         results: list[str] = []
#         top2vec_model = Top2Vec.load(top2vec_model_name)
#         words, word_scores = top2vec_model.similar_words(
#             keywords=[search], keywords_neg=[], num_words=20)
#         for word, score in zip(words, word_scores):
#             results.append(word)

#         topic_words, word_scores, topic_scores, topic_nums = top2vec_model.search_topics(
#             keywords=[search], num_topics=5)
#         matplotlib.pyplot.switch_backend('Agg')
#         wordcloud = top2vec_model.generate_topic_wordcloud(topic_nums[0])
#         random_string = ''.join(random.choices(
#             string.ascii_uppercase + string.digits, k=5))
#         tempfile_name = f'{random_string}.png'
#         wordcloud.savefig(tempfile_name)

#         with open(tempfile_name, "rb") as image_file:
#             encoded_img_data = base64.b64encode(image_file.read())
#         os.remove(tempfile_name)

#         return render_template('results.html', results=results, img_data=encoded_img_data.decode('utf-8'))
#     else:
#         return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
