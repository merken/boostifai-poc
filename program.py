import os
import time
from bs4 import BeautifulSoup
from top2vec import Top2Vec
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bertopic import BERTopic
from nltk.corpus import stopwords
import nltk
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
import re
from azure.storage.blob import BlobServiceClient
import tensorflow_hub as hub

root_url = os.environ.get('ROOT_URL')
site_url = os.environ.get('SITE_URL')
storage_connection_string = os.environ.get('STORAGE_CONNECTION_STRING')


def scrollPageAndGetSource(pageUrl):
    options = Options()
    options.headless = True
    options.add_argument('headless')
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")

    chrome_prefs = {}
    options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}

    driver = webdriver.Chrome(chrome_options=options)
    print(f"getting {pageUrl}")
    driver.get(pageUrl)
    last_height = driver.execute_script("return document.body.scrollHeight")
    SCROLL_PAUSE_TIME = 5
    print(f"Scrolling page {pageUrl}")
    while True:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(SCROLL_PAUSE_TIME)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        print(f"Scrolling page {pageUrl}")

    print(f"Finished scrolling page {pageUrl}")
    return driver.page_source


def getContentFromPageSource(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    return soup.text.strip()


def findAllInternalLinks(root, page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    a_tags = soup.findAll('a', href=True)
    internal_links: list[str] = []

    for link in a_tags:
        href = link['href']
        if not href.startswith(root):
            continue  # skip external links
        internal_links.append(href)
    return internal_links


def uploadToBlobStorage(connection_string, blob_name, file_path):
    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string)
    blob_client = blob_service_client.get_blob_client(
        container='models', blob=blob_name)
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)


def removeNone(x):
    if not (x is None):
        return x


def removeStopWords(x):
    if x not in stopwords:
        return x


print(f"Starting {root_url} {site_url}")

all_content: list[str] = []

page_source = scrollPageAndGetSource(site_url)
content = getContentFromPageSource(page_source)
all_content.append(content)
internal_links = findAllInternalLinks(root_url, page_source)
unique_links = set(internal_links)
count = 0
for internal_link in unique_links:
    page_source = scrollPageAndGetSource(internal_link)
    content = getContentFromPageSource(page_source)
    all_content.append(content)
    count = count + 1
    print(f'Page iteration: {count}')

print('Cleaning data...')


# first lowercase and remove punctuation
data = []
file_name = root_url.replace('https://', '').replace('/', '')
nltk.download('stopwords')
my_stopwords = nltk.corpus.stopwords.words('dutch') \
    + ['None', 'http', 'https', 'amp', 'com', 'delen']

for content in all_content:
    contentData = content.replace('\n', ' ').replace(
        '(', '').replace(')', '').replace('/', '')
    alpha = re.compile(r'[^a-zA-Z ]+')
    contentData = alpha.sub('', contentData).lower()
    contentData = nltk.tokenize.wordpunct_tokenize(contentData)

#     contentData = list(map(removeStopWords, contentData))
    contentData = list(map(removeNone, contentData))
    contentData = list(filter(None, contentData))
    contentData = ' '.join(contentData)
    data.append(contentData)
corpus = data

print('Saving corpus data...')
corpus_name = f"{file_name}.corpus.json"
file = open(corpus_name, "w+")
content = str(corpus)
file.write(content)
file.close()

print('BERTopic')
umap_model = UMAP(n_neighbors=3, n_components=3, min_dist=0.05)
hdbscan_model = HDBSCAN(min_cluster_size=40, min_samples=40,
                        prediction_data=True, gen_min_span_tree=True)

embedding_model = SentenceTransformer(
    'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
# we add this to remove stopwords that can pollute topcs
vectorizer_model = CountVectorizer(ngram_range=(1, 2), stop_words=my_stopwords)

bertopic_model = BERTopic(
    #     umap_model=umap_model,
    #     hdbscan_model=hdbscan_model,
    embedding_model=embedding_model,
    vectorizer_model=vectorizer_model,
    top_n_words=5,
    language='multilingual',
    calculate_probabilities=True,
    verbose=True
)
topics, probs = bertopic_model.fit_transform(corpus*10)
print('Fitting Done!')

bertopic_model_name = f"{file_name}.bertopic.model"
bertopic_model.save(bertopic_model_name)

print('Top2Vec')
# Using top2vec
embedding_model = hub.load(
    "https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")
top2Vec_model = Top2Vec(
    corpus*10, embedding_model=embedding_model)
print('Fitting Done!')
top2vec_model_name = f"{file_name}.top2vec.model"
top2Vec_model.save(top2vec_model_name)

print('Uploading files to azure storage')
uploadToBlobStorage(storage_connection_string,
                    top2vec_model_name, top2vec_model_name)
uploadToBlobStorage(storage_connection_string, corpus_name, corpus_name)
uploadToBlobStorage(storage_connection_string,
                    bertopic_model_name, bertopic_model_name)
print('program done!')
