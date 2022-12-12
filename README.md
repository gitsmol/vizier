# Vizier
Vizier provides a number of visual therapy exercises in a standalone application. It is written in Python and uses the DearPyGui library for its graphics.

## Running
Vizier is to be run as a module. Git clone the repo and run 'python -m vizier' from the root directory.

## Code layout
The application consists of several parts:

1. The main interface (__main__)
2. Some helper functions and classes (helpers)
3. A profile to store userdata in a local sqlite db 
4. Exercises in the form of simple drawing algorithms and response evaluations (exercises module)

## Definition of exercises and evaluations
Every excercise contains an exercise object and evaluation logic.

### Exercise objects
An exercise object is a class with a draw() method. The class initializes variables used to draw all parts of the exercise. The draw() method creates a DPG draw_node. It returns a named tuple containing at least the uuid indicating this node. The default is to paint the draw_node in a **hidden** state and let DrawQueue() from the helpers module take care of unhiding the node.

### Evaluation function
An evaluation is a function that paints an exercise a number of times or until the clock runs out. User input is required to progress through the evaluation. This input is evaluated and recorded using the EvaluationSession() class from the helpers module. 

An evaluation function takes a configuration as argument and:
- defines the evaluation logic in a callback function
- retrieves from the configuration:
    - the exercise parameters (what to draw i.e. difficulty)
    - the evaluation parameters (length, duration etc)
- creates an exercise object (eg vergence)
- may create an Answers object to temporarily store answers
- creates the necessary windows and input handlers

The evaluation logic defines how to progress through the evaluation and adjusts the exercise object variables accordingly. For instance, the vergence evaluation function by default states that:

 - They keyboard arrows are recorded as input for the evaluation.
 - The function runs for 2 minutes or until 50 answers have been given.
 - The answer can be True (success) or False (fail).
 - For every 2 True answers, the primary parameter (in this case bg_offset) is increased by its step (1 by default). The 'success' parameter is reset.
 - For every 2 False answers, the primary parameter is reset to its initial value. The 'fail' parameter is reset.
 
### Configuration
An evaluation needs to pass parameters to both the exercise and the EvaluationSession. A configuration consists of
    - Name of the evaluation
    - the associated evaluation function to be called
    - [Name for the config, for instance difficulty level]
        -  Session
            - step
            - duration_secs
            - count
            - display_time [optional]
        -  Exercise
            - [parameters depend on the exercise]
## Helpers
### DrawQueue
Holds a queue of dpg objects. Takes a named tuple containing at least a 'node_uuid'.
   
### EvaluationSession
Takes the 'Session' part of a config. Maintains a timer, keeps the score, stores evaluated answers and calls results when the session is finished.

### Answers
Keeps a temporary record of given answers. This is useful in cases when a series of answers needs to be evaluated by the evaluation logic. For instance, when showing multiple arrows that need to be recalled in the correct order. 
