# -*- coding: utf-8 -*-
"""
This module contains the primary objects that power Bootstrap.

:copyright: (c) 2012 by Firstname Lastname.
:license: ISC, see LICENSE for more details.
"""

from .errors import BootstrapError


class World(object):
    """The :class:`World <World>` object. It carries out all functionality
    of World."""

    def __init__(self, state=None):
        self.state = state

    def get_state(self):
        """Get the state of the world"""
        return self.state

    def set_state(self, state=None):
        """Set the state of the world"""
        if state:
            self.state = state
        else:
            raise BootstrapError()
