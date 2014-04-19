# -*- coding: utf-8 -*-

"""
bootstrap.util
~~~~~~~~

This module provides utility functions that are used within Bootstrap
that are also useful for external consumption.

:copyright: (c) 2012 by Firstname Lastname.
:license: ISC, see LICENSE for more details.

"""


def black():
    """The world is black."""

    return [True, True, True, True]


def white():
    """The world is white."""

    return [False, False, False, False]


def gray():
    """The world is gray."""

    return [False, True, False, True]
