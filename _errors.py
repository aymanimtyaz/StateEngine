"""
This module containes all the exceptions that can potentially be
raised by the state machine.

Exceptions
----------
NoHandlerAssociation()
NoDefaultState()
DefaultStateHandlerClash()
IncorrectStateType()
StateHandlerClash()
InvalidUIDType()
"""
class NoHandlerAssociation(Exception):

    def __init__(self, faulty_state):
        super().__init__(
            f"State '{faulty_state}' does not have a handler associated with "
            "it. Make sure that all state handlers only return valid state "
            "values that are associated with some handler.")

class NoDefaultState(Exception):

    def __init__(self):
        super().__init__(
            "No handler association set for the state machine's entry point. "
            "Set an entrypoint handler as: "
            "state_handler(state=..., default=True), to handle entry states.")

class DefaultStateHandlerClash(Exception):

    def __init__(self):
        super().__init__(
            "An entry point handler for the state machine has already been "
            "defined.")

class InvalidStateType(Exception):

    def __init__(self):
        super().__init__(
            "A state can only be of types 'str', 'int', or 'float'. "
            "Only entry point states can be None, use start=True in "
            "'register_handler' arguments to set a handler for a starting "
            "state.")

class StateHandlerClash(Exception):

    def __init__(self, state):
        super().__init__(
            f"state '{state}' is already linked to a callback.")

class InvalidUIDType(Exception):

    def __init__(self):
        super().__init__(
            "A UID Can only be of types 'str', 'int', or 'float'")