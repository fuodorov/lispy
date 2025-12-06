import lispy


def run(code: str):
    """
    Parse and evaluate a Scheme expression string.
    """
    return lispy.eval(lispy.parse(code))
