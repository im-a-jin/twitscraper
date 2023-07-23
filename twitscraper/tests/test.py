import logging

def test_fifocache():
    from twitscraper.utils import FIFOCache
    logger = logging.getLogger('test_fifocache')

    cache = FIFOCache(4)

    get1 = {"a": 1, "b": 2, "c": 3}
    cache.update(get1)
    logger.info(cache)
    assert list(cache.keys()) == ["a", "b", "c"], "Order is not preserved."

    get2 = {"b": 4, "c": 5, "d": 6}
    cache.update(get2)
    logger.info(cache)
    assert list(cache.keys()) == ["a", "b", "c", "d"], "Order is not preserved."

    get3 = {"e": 7, "f": 8, "g": 9}
    cache.update(get3)
    logger.info(cache)
    assert list(cache.keys()) == ["d", "e", "f", "g"], "Size is not preserved."

    get4 = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6}
    cache.update(get4)
    logger.info(cache)
    assert list(cache.keys()) == ["3", "4", "5", "6"], "FIFO ordering failed."

    get5 = {"A": "A", "B": "B", "C": "C", "D": "D"}
    cache.update(reversed(get5.items()))
    logger.info(cache)
    assert list(cache.keys()) == ["D", "C", "B", "A"], "FIFO reversing failed."

