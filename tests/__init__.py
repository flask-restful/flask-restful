#!/usr/bin/env python

import functools

import pytest


def expected_failure(test):
    @functools.wraps(test)
    def inner(*args, **kwargs):
        try:
            test(*args, **kwargs)
        except Exception:
            pytest.skip("Test failed as expected")
        else:
            raise AssertionError('Failure expected')
    return inner
