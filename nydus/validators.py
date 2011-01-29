def is_int(num):
    """This value should be an integer."""
    try:
        return int(num)
    except:
        raise NydusException( "This attribute must be a valid integer, used: %r" % num)

def is_even(num):
    """This value should be an even number"""
    i = is_int(num)
    if i % 2 == 0:
        return True
    else:
        raise NydusException( "This attribute must be an even number, used: %r" % num)

