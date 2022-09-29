from concurrent.futures import ProcessPoolExecutor
from functools import partial
from logging import INFO, FileHandler, StreamHandler, getLogger

from cadeia.main.factories import (
    client_consume,
    create_component,
    get_cd,
    get_factory,
    get_store
)
logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(FileHandler('cadeia_de_abastecimento.log'))
logger.addHandler(StreamHandler())


def main():
    pool = ProcessPoolExecutor()
    create_component(pool, partial(get_factory, logger), 4, 'factory')
    create_component(pool, partial(get_cd, logger), 1, 'cd')
    stores = create_component(pool, partial(get_store, logger), 4, 'store')
    create_component(pool, partial(client_consume, stores), 4, 'client')


if __name__ == '__main__':
    main()
