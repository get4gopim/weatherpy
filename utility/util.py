
def index_of(original_string, search_string):
    delimiter_idx = -1

    try:
        delimiter_idx = original_string.index(search_string)
    except ValueError:
        delimiter_idx = -1

    return delimiter_idx;