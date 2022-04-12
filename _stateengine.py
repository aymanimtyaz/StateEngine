"""
This module contains the code implementing the finite state machines
as well as the public APIs to access them. The public APIs get 
exported to __init.py__ for ease of importing.

Private Classes
---------------
_StateMachineBase()

Public Classes
--------------
StateEngine(_StateMachineBase)
"""

from typing import Callable, Optional, Union

from ._common_utils import State
from ._errors import (
    NoHandlerAssociation, NoDefaultState, DefaultStateHandlerClash,
    InvalidStateType, StateHandlerClash, OutsideHandlerContext
)


class _StateMachineBase:
    """
    The base class that implements the finite state machine
    """

    # stores the current state, should only be accessed within a handler's context using _get_current_state property
    _current_state: State = None

    # stores the handler that is being executed in the current context using the _get_current_handler property
    _current_handler: Union[Callable, None] = None

    def __init__(self):
        self._state_handlers = {}
        self._default_state_handler = {}

    def _register_handler(self, state: State, default: Optional[bool]=False) -> Callable:
        """ Registers a state to a handler function """

        def state_to_handler_mapper(func: Callable):
            # states must be either a string, integer, or float
            if not isinstance(state, (str, int, )) or isinstance(state, bool):
                raise InvalidStateType

            # assigning default state to its handler
            if default:
                if self._default_state_handler != {}:
                    raise DefaultStateHandlerClash
                self._default_state_handler[state] = func
            # assigning intermediate states to their handlers
            else:
                if state in self._state_handlers.keys():
                    raise StateHandlerClash(state)
                else:
                    self._state_handlers[state] = func
            return func

        return state_to_handler_mapper
    
    def _execute_handler(self, current_state: State, *args, **kwargs) -> State:

        # Setting up the handler context variables
        # Setting up the variables in case current_state is None or the default state
        if current_state is None or current_state in self._default_state_handler:
            if self._default_state_handler is None:
                raise NoDefaultState
            self._current_state = list(self._default_state_handler.keys())[0]
            self._current_handler = self._default_state_handler[self._current_state]

        # setting up the variables in case the current state is an intermediate state
        else:
            if current_state not in self._state_handlers:
                raise NoHandlerAssociation(current_state)
            self._current_state = current_state
            self._current_handler = self._state_handlers[current_state]

        # executing the state machine and getting a new state
        new_state = self._current_handler(*args, **kwargs)

        # resetting the handler context variables to None as we aren't within the context of a handler anymore
        self._current_state = None
        self._current_handler = None

        # returning the new state
        return new_state

    @property
    def _get_current_state(self) -> State:
        """
        Returns the current state

        Will raise an error if called from outside a handler context
        """

        # if the current_handler is None, we are outside a handler context and an error will be raised
        if not self._current_handler:
            raise OutsideHandlerContext("current_state")

        return self._current_state

    @property
    def _get_current_handler(self) -> Callable:
        """
        Returns the state handler function of the current context

        Will raise an error if called from outside a handler context
        """

        # if the current handler variable is None, raise an Error
        if not self._current_handler:
            raise OutsideHandlerContext("current_handler")

        return self._current_handler


class StateEngine(_StateMachineBase):
    """
    StateEngine - Finite State Machines in pure Python!
    """
    def __init__(self):
        super().__init__()
    
    def state_handler(self, state: State, default: Optional[bool]=False) -> Callable:
        """
        Register a state to a state handler using a state_handler decorator

        Params
        ------
        state:
            The state for which the handler function is being defined.
        default: Optional, default is False
            Flags the handler for handling default/None states.
        """
        return _StateMachineBase._register_handler(self, state, default)

    def execute(self, state: State, *args, **kwargs) -> State:
        """
        Run the state machine by passing it a state and inputs
        All arguments after state will be passed as input to the state 
        machine.

        Params
        ------
        state:
            The state which the state machine is currently in.
        *args, **kwargs:
            The inputs to the state machine.
        """
        return _StateMachineBase._execute_handler(self, state, *args, **kwargs)

    @property
    def current_state(self) -> State:
        """
        Get the current state of a state machine, accessible only
        within a handler context.
        """
        return self._get_current_state

    @property
    def current_handler(self) -> Callable:
        """
        Get the current handler of a state machine, accessible only
        within a handler context.
        """
        return self._get_current_handler
