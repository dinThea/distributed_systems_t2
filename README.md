# Trabalho 2 de Sistemas Distribuídos
## Nomes 
Iago Barbosa 759027

Lucas Pereira 726561

## Como executar ?
1. Se você for executar **via docker** os seguintes passos são necessários:
  ```bash
  docker built -t nome_da_image .
  
docker-compose up -d --scale factory=14 --scale client_and_store=10
```
  Para ver os logs use o seguinte comando:
  ```bash
    docker-compose logs -f
  ```
2. Caso opte por **não executar via docker** siga esse passo-a-passo:
  
  Primeiro instale o Poetry:
  ```bash
    export POETRY_VERSION="1.1.12"
    
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/${POETRY_VERSION}/get-poetry.py | python3 -
    
    ln -s /root/.poetry/bin/poetry /usr/local/bin/poetry
    
    cd {pasta_desejada}
    
    poetry install
    
    poetry shell
  ```
  Agora pode executar:
  ```bash
    python3 main.py
  ```
Para acessar o **hivemq** as credencias são: 

```bash
HIVEMQTT_USER=iago123
HIVEMQTT_PASSWD=iago1234
HIVEMQTT_HOST=ffd901cec6ad4b739f71918282c611b9.s2.eu.hivemq.cloud
HIVEMQTT_PORT=8883
```
