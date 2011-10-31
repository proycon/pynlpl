
    
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
    

def consecutivegaps(n, leftmargin = 0, rightmargin = 0): 
    """Compute all possible single consecutive gaps in any sequence of the specified length. Returns
    (beginindex, length) tuples. Runs in  O(n(n+1) / 2) time. Argument is the length of the sequence rather than the sequence itself"""
    begin = leftmargin
    while begin < n:
        length = (n - rightmargin) - begin
        while length > 0:
            yield (begin, length)
            length -= 1
        begin += 1



    
