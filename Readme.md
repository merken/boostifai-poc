Create Azure Storage Account and save the KEY.
Create Blob Container named 'models'

Create ingestion.env file with contents:
```
ROOT_URL=
SITE_URL=
STORAGE_CONNECTION_STRING=
``` 

```docker build . -t boostifai_ingestion```
```docker run --shm-size="2g" --env-file ingestion.env boostifai_ingestion```

Create api.env file with contents:
```
STORAGE_CONNECTION_STRING=
``` 

```
cd ./api 
docker build .-t boostifai_app
docker run -p 8080:80 --env-file api.env boostifai_app
```