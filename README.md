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
	# the input isn't used here but it
	# must still be passed to the handler
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
### Running the state machine
The state machine can be executed by passing it a state and an input. It should be run after all the state handlers have been defined. A state machine can be run using ```StateEngine.execute()``` as:
```python
...
some_state = ...
some_input = ...
new_state = state_machine.execute(state=some_state, input=some_input)
...
```
A new state will be returned depending on the input and the logic defined in the corresponding handler.
A practical way to make use of the state machine would be to run it in a loop, or as a response to an event such as an HTTP request

### Using ```IntegratedStateEngine```
```IntegratedStateEngine``` essentially abstracts out the responsibility of handling and storing states away from the user.
They must simple assign an ID for each state machine and ensure that the ID is unique.
The only difference in implementation between ```StateEngine``` and ```IntegratedStateEngine``` is the way the machine is executed. All other code related to registering handlers will be the same:
```python
...
uid = ...
input = ...
state_machine.execute(uid=uid, input=input)
...
```
The state for the state machine corresponding to ```uid``` will be retrieved and used to run the state machine. The new state value returned from the state handler will be assigned to ```uid```.

A state value can also be passed to the state machine. It will override any state value associated with ```uid``` and be used to execute the state machine:
```python
...
uid = ...
input = ...
state = ...
state_machine.execute(uid=uid, input=input, state=state)
...
```
```IntegratedStateEngine``` uses a Python dictionary to map UIDs to states. This is not very scalable, for example if ```IntegratedStateEngine``` is used to respond to HTTP requests and many workers of the program are running; Sticky sessions will have to be used. This will be improved upon in a later update by using something like Redis to store states.
### A note on ```None``` states
The default handler (if defined) for a state machine can be executed by passing the corresponding state value OR ```None``` as the state argument in execute. If a default state handler is not defined and a ```None``` is passed, an exception will be raised.
### Important points
- A handler function should only return states. Furthermore, it should only return states that are registered to a state handler. Returning an unregistered state will raise a ```NoHandlerAssociation``` exception.
- The states can only be of types ```str```, ```int```, and ```float```. An ```InvalidStateType``` exception will be raised otherwise.
- States must be unique. Two state handlers can not have the same state argument. A ```StateHandlerClash``` exception will be raised otherwise.
- Only one default state can exist for a state machine. Trying to assign more than one default state handle will raise a ```DefaultStateHandlerClash``` exception.
- A default state is not necessary. However, if ```state=None``` is passed to ```execute```, and a default state handler is not defined. A ```NoDefaultState``` exception will be raised.
- If using ```IntegratedStateEngine```, the ```uid``` passed to ```execute()``` should only be of types ```str```, ```int```, or ```float```. An ```InvalidUIDType``` exception will be raised otherwise.
### Good practices
- The states' names should reflect what their handlers are supposed to do. This will make it easy to debug and maintain the state machine code in the future.

### To Do
- [x] Make unpacking inputs to state handlers more Pythonic.
- [ ] Use Redis to store state in ```IntegratedStateEngine```
- [ ] Improve API documentation.

### Examples of StateEngine in use
- [spndr](https://github.com/aymanimtyaz/spndr)

#### If you have any questions or suggestions about StateEngine, you can open up an issue or create a PR if you've made some improvements . You can also email me at aymanimtyaz@gmail.com :)