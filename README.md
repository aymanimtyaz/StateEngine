# StateEngine
Finite state machines in Python

## Example Usage
```python
"""
Using StateEngine to simulate the change of physical states of water
"""

from StateEngine import StateEngine

water_states = StateEngine()


@water_states.state_handler("solid")
def ice(sm_input):
    if sm_input == "melting":
        print("turning to liquid")
        return "liquid"
    elif sm_input == "sublimation":
        print("turning to gas")
        return "gas"
    else:
        print("remaining as a solid")
        return "solid"


@water_states.state_handler("liquid", default=True)
def water(sm_input):
    if sm_input == "freezing":
        print("turning to solid")
        return "solid"
    elif sm_input == "boiling":
        print("turning to gas")
        return "gas"
    else:
        print("remaining as a liquid")
        return "liquid"


@water_states.state_handler("gas")
def vapour(sm_input):
    if sm_input == "condensing":
        print("turning to liquid")
        return "liquid"
    elif sm_input == "depositing":
        print("turning to solid")
        return "solid"
    else:
        print("remaining as a gas")
        return "gas"


if __name__ == "__main__":
    state = None
    while True:
        user_input = input("> ")
        state = water_states.execute(state, user_input)


```

## Installation
The stateengine package is not on PyPi yet. To use stateengine, clone the repository and put it in the working directory of your project:
```
git clone https://github.com/aymanimtyaz/stateengine.git
```

## Usage
### Creating a state machine
A state machine can be created by creating a state machine object. The constructor does not take any arguments:
```python
from stateengine import StateEngine

state_machine = StateEngine()
...
```

### Assigning states to state handlers
States can be assigned to state handlers using the ```state_handler()```  decorator function as:
```python
...
@state_machine.state_handler(state="example_state")
def example_state_handler(input):
	... 
```
A default state can be assigned by passing ```default=True``` as an argument to ```state_handler```. Note that there can only be one default state.
```python
...
@state_machine.state_handler(state="example_state", default=True)
def example_state_handler(input):
	... 
```
The state handler function should only return other states that have been registered with a state handler, signifying a state transition.

### Assigning multiple states to a single state handler
Multiple states can also be assigned to a handler. This can be done by stacking the ```state_handler``` decorator:
```python
...
@state_machine.state_handler("state_1")
@state_machine.state_handler("state_2")
@state_machine.state_handler("state_3")
def a_handler_function(input):
	...
	return ...
...
```
The order in which the decorators for each state are stacked does not matter.

### Running the state machine
The state machine can be executed by passing it a state and an input. It should be run after all the state handlers have been defined. A state machine can be run using ```execute()``` as:
```python
...
some_state = ...
some_input_1 = ...; some_input_2 = ...; ...
new_state = state_machine.execute(
	state=some_state, some_input_1=some_input_1, some_input_2=some_input_2, ...)
...
```
A new state will be returned depending on the input and the logic defined in the corresponding handler.
A practical way to make use of the state machine would be to run it in a loop, or as a response to an event such as an HTTP request

### Accessing the current state using the ```state_handler``` property
```current_state``` is a property that can be used to access the current state from within a handler function. This may seem pointless at first glance, but becomes really useful when a handler is assigned to more than one state:
```python
...
@state_machine.state_handler("state_1")
@state_machine.state_handler("state_2")
def a_handler_function(input):
	print(f"The current state is {state_machine.current_state}")
	return ...
...
```

### A note on ```None``` states
The default handler (if defined) for a state machine can be executed by passing the corresponding state value OR ```None``` as the ```state``` argument to ```execute()```. If a default state handler is not defined and a ```None``` is passed, an exception will be raised.

### Important points
- A handler function should only return states. Furthermore, it should only return states that are registered to a state handler. Returning an unregistered state will raise a ```NoHandlerAssociation``` exception.
- The states can only be of types ```str``` and ```int```. An ```InvalidStateType``` exception will be raised otherwise.
- States must be unique. Two state handlers can not have the same state argument. A ```StateHandlerClash``` exception will be raised otherwise.
- Only one default state can exist for a state machine. Trying to assign more than one default state handler will raise a ```DefaultStateHandlerClash``` exception.
- A default state is not necessary. However, if ```state=None``` is passed to ```execute```, and a default state handler is not defined. A ```NoDefaultState``` exception will be raised.
- The ```current_state``` property can only be accessed from within a handler context, that is, inside a handler function. Trying to access it from outside a handler function will raise a ```OutsideHandlerContext``` exception.

### Good practices
- The states' names should reflect what their handlers are supposed to do. This will make it easy to maintain and debug the state machine code in the future.

### To Do
- [x] Make unpacking inputs to state handlers more Pythonic.
- [x] Allow a handler to handle multiple states.
- [ ] Improve API documentation.
- [ ] Add use cases in the docs.

### Examples of StateEngine in use
- [spndr](https://github.com/aymanimtyaz/spndr)

#### If you have any questions or suggestions about StateEngine, you can open up an issue or create a PR if you've made some improvements . You can also email me at aymanimtyaz@gmail.com :)