from flask_restful.utils.crypto import decrypt, encrypt
DEFAULT_PAGE_SIZE = 50


def retrieve_next_page(key, seed, args, callback, initial_bookmark=None):
    """
    A helper for the bookmark pager.

    :param key: the private key of you API
    :param seed: the crypo seed for this session
    :param args: the verbatim filtering+paging arguments
    :param callback: a function that takes (a dictionary of filters, the current bookmark, the page size)
                 and return a tuple (next_results, dictionary_ready_for_next_iteration, approx_number_of_element_left)
    :param initial_bookmark: pass here an optional initial bookmark for the first request
    :return: the tuple result_list and new encrypted bookmark
    """
    filter = dict(args)
    if 'pager_info' in filter:
        initial_bookmark = decrypt(filter.pop('pager_info'), key, seed)

    page_size = filter.pop('page_size', DEFAULT_PAGE_SIZE)

    result_list, new_bookmark, approx_result_size = callback(filter, initial_bookmark, page_size)

    # restore for the next iteration
    filter['pager_info'] = encrypt(new_bookmark, key, seed)
    filter['page_size'] = page_size

    return result_list, filter, approx_result_size
