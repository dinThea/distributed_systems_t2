from concurrent.futures import ProcessPoolExecutor

from cadeia.main.factories import get_cd, get_store


def main():
    pool = ProcessPoolExecutor()
    cd = get_cd()
    pool.submit(cd.start)
    for i in range(20):
        store = get_store()
        pool.submit(store.start)


if __name__ == '__main__':
    main()
