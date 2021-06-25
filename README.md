# StateEngine
Finite state machines in Python, using Flask like state - handler associations

## Example Usage
```python
"""
Using StateEngine to create a simple state machine based
chatbot that takes the name and age of the user and echoes
them back
"""

from stateengine import StateEngine

# dict person is a stand-in for a database
person = {
	"example_person":{
	}
}

# creating a StateEngine object
chatbot = StateEngine()

# registering the default/starting state and its handler
@chatbot.state_handler("default", default=True)
def  start(_id, text):
	# _id and text are taken as inputs here
	# the input isn't used here but it
	# must still be passed to the handler.
	# In this case the presence of input is
	# the input itself, intuitively speaking
	print("Hey! What's your name?")
	# the handlers should only
	# return the state to transition to
	# Make sure that the states returned
	# are valid, that is, are registered to a
	# state handler
	return  "ask_for_age"

# registering a state and its handler
@chatbot.state_handler("ask_for_age")
def  ask_for_age(_id, text):
	person[_id]["name"] = text
	print(f"Welcome! {person[_id]['name']}. How old are you?")
	return  "give_final_output"

# registering another state and its handler
@chatbot.state_handler("give_final_output")
def  give_final_output(_id, text):
	try:
		age = int(text)
	except  ValueError  as e:
		print("Your age is supposed to be numeric.")
		return  "give_final_output"
	person[_id]["age"] = age
	print(
		f"Hi!, {person[_id]['name']} who is {person[_id]['age']} years old!"
		" Nice to meet you!")
	return  None

def  main():
	# initializing a starting state value
	# None states translate to the state defined as default
	state=None
	while  True:
		state = chatbot.execute(state=state, _id="example_person", text=input())

if  __name__ == "__main__":
	main()
```

## Installation
The stateengine package is not on PyPi yet. To use stateengine, clone the repository and put it in the working directory of your project:
```
git clone https://github.com/aymanimtyaz/stateengine.git
```

## Usage 
Anyone who is acquainted with the Flask ecosystem should have no trouble using StateEngine. Assigning handlers to states in StateEngine is analogous to assigning routes to view functions in Flask.
### Creating a state machine
A state machine can be created by creating a state machine object. The constructor does not take any arguments:
```python
from stateengine import StateEngine

state_machine = StateEngine()
...
```

### Assigning states to state handlers
States can be assigned to state handlers using the ```StateEngine.state_handler()```  decorator function as:
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
The state machine can be executed by passing it a state and an input. It should be run after all the state handlers have been defined. A state machine can be run using ```StateEngine.execute()``` as:
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
The default handler (if defined) for a state machine can be executed by passing the corresponding state value OR ```None``` as the state argument in execute. If a default state handler is not defined and a ```None``` is passed, an exception will be raised.

### Using ```IntegratedStateEngine```
```IntegratedStateEngine``` essentially abstracts out the responsibility of handling and storing states away from the user.
They must simply assign an ID for each state machine and ensure that the ID is unique.
The only difference in implementation between ```StateEngine``` and ```IntegratedStateEngine``` is the way the machine is executed. All other code related to registering handlers will be the same:
```python
...
from stateengine import IntegratedStateEngine
state_machine = IntegratedStateEngine()
uid = ...
input = ...
state_machine.execute(uid=uid, input=input)
...
```
The state for the state machine corresponding to ```uid``` will be retrieved and used to run the state machine. The new state value returned from the state handler will be assigned to ```uid```.
By default, a python dictionary is used to store states. Setting the ```use_redis``` argument to ```True``` while initializing an ```IntegratedStateEngine``` object will cause ```IntegratedStateEngine``` to use Redis to store states, which can be more scalable:
```python
...
state_machine = IntegratedStateEngine(use_redis=True)
...
```

### Important points
- A handler function should only return states. Furthermore, it should only return states that are registered to a state handler. Returning an unregistered state will raise a ```NoHandlerAssociation``` exception.
- The states can only be of types ```str```, ```int```, and ```float```. An ```InvalidStateType``` exception will be raised otherwise.
- States must be unique. Two state handlers can not have the same state argument. A ```StateHandlerClash``` exception will be raised otherwise.
- Only one default state can exist for a state machine. Trying to assign more than one default state handle will raise a ```DefaultStateHandlerClash``` exception.
- A default state is not necessary. However, if ```state=None``` is passed to ```execute```, and a default state handler is not defined. A ```NoDefaultState``` exception will be raised.
- If using ```IntegratedStateEngine```, the ```uid``` passed to ```execute()``` should only be of types ```str```, ```int```, or ```float```. An ```InvalidUIDType``` exception will be raised otherwise.
- The ```current_state``` property can only be accessed from within a handler context, that is, inside a handler function. Trying to access it from outside a handler function will raise a ```OutsideHandlerContext``` exception.
- If using ```IntegratedStateEngine``` with ```use_redis``` set to ```True```, make sure the Redis database that is being used as the state store is up and running properly, any problems with Redis will raise a ```RedisStateStoreError```.

### Good practices
- The states' names should reflect what their handlers are supposed to do. This will make it easy to maintain and debug the state machine code in the future.

### To Do
-  [x] Make unpacking inputs to state handlers more Pythonic.
-  [x] Allow a handler to handle multiple states.
- [ ] Add a global ```current_state``` object that stores the current state.
-  [x] Use Redis to store state in ```IntegratedStateEngine```
- [ ] Improve API documentation.
- [ ] Add use cases in the docs.

### Examples of StateEngine in use
- [spndr](https://github.com/aymanimtyaz/spndr)

#### If you have any questions or suggestions about StateEngine, you can open up an issue or create a PR if you've made some improvements . You can also email me at aymanimtyaz@gmail.com :)