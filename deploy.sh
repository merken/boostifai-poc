cd api
zip -r boostifaiapi.zip . -x '.??*'
curl -X POST -u '$boostifaiapipoc' --data-binary @"boostifaiapi.zip" -H 'Content-Type: application/zip' https://boostifaiapipoc.scm.azurewebsites.net/api/zipdeploy
