
    
def sum_to_n(n, size, limit=None): #from http://stackoverflow.com/questions/2065553/python-get-all-numbers-that-add-up-to-a-number
    """Produce all lists of `size` positive integers in decreasing order
    that add up to `n`."""
    if size == 1:
        yield [n]
        return
    if limit is None:
        limit = n
    start = (n + size - 1) // size
    stop = min(limit, n - size + 1) + 1
    for i in range(start, stop):
        for tail in sum_to_n(n - i, size - 1, i):
            yield [i] + tail
    

def consecutivegaps(n): 
    """Compute all possible single consecutive gaps in a sequence (no gaps allowed at immediate beginning or end of a sequence). Returns
    (beginindex, length) tuples. Runs in  O(n(n+1) / 2) time. Argument is the length of the sequence rather than the sequence itself"""
    begin = 1
    while begin < n:
        length = (n - 1) - begin
        while length > 0:
            yield (begin, length)
            length -= 1
        begin += 1
