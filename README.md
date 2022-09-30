# distributed_systems_t2
# Nomes 
Iago Barbosa 759027
Lucas Pereira 726561

# Como executar ?
Se você for executar via docker os seguintes passos são necessários: 
  docker built -t nome_da_image .
  docker run nome_da_imagem -d
  E para ver os logs use o seguinte comando:
    docker logs nome_do_container
Caso opte por não executar via docker siga esse passo-a-passo:
  Primeiro instale o Poetry:
    export POETRY_VERSION="1.1.12"
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/${POETRY_VERSION}/get-poetry.py | python3 -
    ln -s /root/.poetry/bin/poetry /usr/local/bin/poetry
    cd {pasta_desejada}
    poetry install
    poetry shell
  Agora pode executar:
    python3 main.py
