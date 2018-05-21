# -*- coding: utf-8 -*-

""" Return a map with all the keys and tuples for the values
"""
def dictDiff(a, b):
    if not isinstance(a, dict) or not isinstance(b, dict):
        raise ValueError("a and b must be dict")
    diff = dict()
    for key in set().union(a.keys()).union(b.keys()):
        aValue = a.get(key, None)
        bValue = b.get(key, None)
        diff[key] = (aValue, bValue)
    return diff
