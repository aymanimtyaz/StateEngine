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

from typing import Callable, Optional, Any, Union

import redis

from ._common_utils import State, UID
from ._errors import (
    NoHandlerAssociation, NoDefaultState,
    DefaultStateHandlerClash, InvalidStateType, StateHandlerClash,
    InvalidUIDType, OutsideHandlerContext, RedisStateStoreError)


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
            if not isinstance(state, (str, int, float, )) or isinstance(state, bool):
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


class _StateStore:
    """
    This class implements a store that can be used to abstract out the 
    responsibility of storing states for different machines. Redis can
    also be used as a state store.
    """

    def __init__(self, use_redis: Optional[bool]=False) -> None:
        self._redis = use_redis
        if not self._redis:
            self._store: Any = dict()
        else:
            self._store = redis.Redis(decode_responses=True, db=1)

    def _create_or_update_state(self, uid: UID, state: State) -> None:
        if (not isinstance(uid, (str, int, float, ))
                or isinstance(uid, bool)):
            raise InvalidUIDType
        if self._redis is True:
            try:
                self._store.set(uid, state)
            except redis.exceptions.ConnectionError as e:
                raise RedisStateStoreError(e)
        else:
            self._store[uid] = state

    def _get_state(self, uid: UID) -> State:
        if self._redis is True:
            try:
                return self._store.get(uid)
            except redis.exceptions.ConnectionError as e:
                raise RedisStateStoreError(e)
        return self._store.get(uid, None)

    def _delete_state(self, uid: UID) -> None:
        if self._redis is True:
            try:
                self._store.delete(uid)
            except redis.exceptions.ConnectionError as e:
                raise RedisStateStoreError(e)
        if uid in self._store:
            del self._store[uid]


class StateEngine(_StateMachineBase):
    """
    Finite state machines using Flask like state-handler associations

    Basic Usage
    -----------
    ```
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
    ```
    Methods
    -------
    state_handler(state, default=False)
    execute(state, *args, **kwargs)

    Properties
    ----------
    - current_state
    - current_handler
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


class IntegratedStateEngine(_StateMachineBase, _StateStore):
    """
    Finite state machines using Flask like state-handler associations.
    Comes with a built in state store.

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
    execute(state, *args, **kwargs)

    Properties
    ----------
    - current_state
    - current_handler
    """
    def __init__(self, use_redis: Optional[bool]=False) -> None:
        """
        Initialize an IntegratedStateMachine object

        IntegratedStateMachine objects come with state stores that abstract
        away the responsibility of handling states, Redis can also be used
        as a state store.

        Params
        ------
        use_redis: Optional, default is False
            Use Redis as a state store instead of a Python dict
        """
        _StateMachineBase.__init__(self)
        _StateStore.__init__(self, use_redis=use_redis)
        
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

    def execute(self, uid: UID, *args, **kwargs) -> None:
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
        if (new_state is None or
                new_state == list(self._default_state_handler.keys())[0]):
            _StateStore._delete_state(self, uid)
        else:
            _StateStore._create_or_update_state(self, uid, new_state)

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
