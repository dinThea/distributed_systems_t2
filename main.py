from concurrent.futures import ProcessPoolExecutor
from functools import partial
from logging import INFO, FileHandler, StreamHandler, getLogger
from argparse import ArgumentParser
from time import sleep

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
    arg_parser = ArgumentParser(description="Simulador de cadeia de produção")
    arg_parser.add_argument("--factories", dest="number_of_factories", type=int, default=0)
    arg_parser.add_argument("--stores", dest="number_of_stores", type=int, default=0)
    arg_parser.add_argument("--cds", dest="number_of_cds", type=int, default=0)
    arg_parser.add_argument("--clients", dest="number_of_clients", type=int, default=0)

    args = arg_parser.parse_args()

    sleep(5)
    pool = ProcessPoolExecutor()
    create_component(pool, partial(get_factory, logger), args.number_of_factories, 'factory')
    create_component(pool, partial(get_cd, logger), args.number_of_cds, 'cd')
    stores = create_component(pool, partial(get_store, logger), args.number_of_stores, 'store')
    create_component(pool, partial(client_consume, stores), args.number_of_clients, 'client')


if __name__ == '__main__':
    main()
