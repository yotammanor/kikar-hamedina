class NoDefaultProvided(object):
    pass


def getattrd(obj, name, default=NoDefaultProvided):
    """
    Same as getattr(), but allows dot notation lookup
    Discussed in:
    http://stackoverflow.com/questions/11975781
    """
    try:
        return reduce(getattr, name.split("."), obj)
    except AttributeError, e:
        if default != NoDefaultProvided:
            return default
        raise

def join_queries(q1, q2, operator):
    """Join two queries with operator (e.g. or_, and_) while handling empty queries"""
    return operator(q1, q2) if (q1 and q2) else (q1 or q2)

