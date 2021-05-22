"""
This module contains the code implementing the finite state machines
as well as the public APIs to access them. The public APIs get 
exported to __init.py__ for ease of importing.

Private Classes
---------------
_StateMachineBase()
_StateStore()

Public Classes
--------------
StateEngine(_StateMachineBase)
IntegratedStateEngine(_StateMachineBase, _StateStore)
"""

from ._errors import (NoHandlerAssociation, NoDefaultState, 
    DefaultStateHandlerClash, InvalidStateType, StateHandlerClash,
    InvalidUIDType)

class _StateMachineBase:
    """
    The base class that implements the finite state machine
    """

    def __init__(self):
        self._state_handlers = {}
        self._default_state_handler = {}

    def _register_handler(self, state, default=False):
        """ Registers a state to a handler function """

        def state_to_handler_mapper(func):
            # states must be either a string, integer, or float
            if (not isinstance(state, (str, int, float, )) 
                        or isinstance(state, bool)):
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

        return state_to_handler_mapper
    
    def _execute_handler(self, current_state, *args, **kwargs):
        # executing a default state handler
        if (current_state is None or current_state in 
                self._default_state_handler):
            if self._default_state_handler is None:
                raise NoDefaultState
            current_state = list(self._default_state_handler.keys())[0]
            new_state = self._default_state_handler[current_state](*args, **kwargs)
        # executing an intermediate state handler
        else:
            if current_state not in self._state_handlers:
                raise NoHandlerAssociation(current_state)
            new_state = self._state_handlers[current_state](*args, **kwargs)
        return new_state

class _StateStore:
    """
    This class implements a store that can be used to abstract out the 
    responsibility of storing states for different machines.
    """

    def __init__(self):
        self._store = {}

    def _create_or_update_state(self, uid, state):
        if (not isinstance(uid, (str, int, float, )) 
                or isinstance(uid, bool)):
            raise InvalidUIDType
        self._store[uid] = state

    def _get_state(self, uid):
        return self._store.get(uid, None)

    def _delete_state(self, uid):
        if uid in self._store:
            del self._store[uid]

class StateEngine(_StateMachineBase):
    """
    Finite state machines using Flask like state-handler associations

    Basic Usage
    -----------

        import random
        import time

        from stateengine import StateEngine

        eng = StateEngine()

        @eng.state_handler("asleep")
        def asleep_handler(input):
            if input == "wake up":
                print("waking up")
                return "awake"
            return "asleep"

        @eng.state_handler("awake", default=True)
        def awake_handler(input):
            if input == "go to sleep":
                print("going to sleep")
                return "asleep"

        state = None
        while True:
            input = random.choice(["wake up", "go to sleep"])
            state = eng.execute(state, input)
            time.sleep(3)
            Methods
            -------
            state_handler(state, default=False)
            execute(state, input)

    Methods
    -------
    state_handler(state, default=False)
    execute(state, *args, **kwargs)
    """
    def __init__(self):
        super().__init__()
    
    def state_handler(self, state, default=False):
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

    def execute(self, state, *args, **kwargs):
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

class IntegratedStateEngine(_StateMachineBase, _StateStore):
    """
    Finite state machines using Flask like state-handler associations

    Basic Usage
    -----------

        import random
        import time

        from stateengine import IntegratedStateEngine

        eng = IntegratedStateEngine()

        @eng.state_handler("asleep")
        def asleep_handler(input):
            if input == "wake up":
                print("waking up")
                return "awake"
            return "asleep"

        @eng.state_handler("awake", default=True)
        def awake_handler(input):
            if input == "go to sleep":
                print("going to sleep")
                return "asleep"
            # return "awake"

        uid = "example_id"
        while True:
            input = random.choice(["wake up", "go to sleep"])
            eng.execute(uid, input)
            time.sleep(3)

    Methods
    -------
    state_handler(state, default=False)
    execute(uid, *args, **kwargs)
    """
    def __init__(self):
        _StateMachineBase.__init__(self)
        _StateStore.__init__(self)
        
    def state_handler(self, state, default=False):
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

    def execute(self, uid, *args, **kwargs):
        """
        Run a state machine by passing it a uid and an input(s)

        The uid will be used to uniquely identify and store states in
        the state store. All arguments after the uid will be passed as
        input to the state machine.

        Parameters
        ----------
        uid:
            An value that can be used to uniquely identify a state machine.
            Maintaining the uniqueness of this value is the responsibility
            of the end user.
        *args, **kwargs:
            Inputs to the state engine. This consists of all the information
            required by the state engine to successfully return a state after
            processing the input.
        """
        current_state = _StateStore._get_state(self, uid)
        new_state = _StateMachineBase._execute_handler(
            self, current_state, *args, **kwargs)

        # deleting the uid from the state store if the new state is
        # the default state or None
        if (new_state == None or 
                new_state == list(self._default_state_handler.keys())[0]):
            _StateStore._delete_state(self, uid)
        else:
            _StateStore._create_or_update_state(self, uid, new_state)