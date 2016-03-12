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


def add_html_tag(matchobj, tag_name='b'):
    return '<{0}>{1}</{2}>'.format(tag_name, matchobj.group(0), tag_name)
