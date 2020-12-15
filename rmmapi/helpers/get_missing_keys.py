def get_missing_keys(data, required_keys):
    """Given a dictionary and a list of required keys, return a list of all keys
    that were not set in the dictionary"""
    return [ key for key in required_keys if not key in data ]
