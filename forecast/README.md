# Como executar o docker
## Para fazer o build:
docker build -t forecast-app .

## Para executar a imagem
docker run -d -p 5001:5001 --name forecast-app forecast-app
