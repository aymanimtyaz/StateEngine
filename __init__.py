"""
StateEngine 
-----------
Finite state machines with Flask like state-handler associations

Features
--------
    - Flask like state-handler associations.
      Routes to states and view functions to handlers.
    - Built in state storage via IntegratedStateEngine().

Coming Soon
-----------
    - Distributed state storage using Redis
"""

__author__ = "Ayman Imtyaz"
__email__ = "aymanimtyaz@gmail.com"
__license__ = "MIT"

# Exposing the public interface
from .stateengine import StateEngine, IntegratedStateEngine