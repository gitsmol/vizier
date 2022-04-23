# Vizier
Vizier provides a number of visual therapy exercises in a standalone application. It is written in Python and uses the DearPyGui library for its graphics.

## Layout
The application consists of several parts:

1. The main interface (__main__)
2. Some helper functions and classes (helpers)
3. Exercises in the form of simple drawing algorithms (exercises)
4. Evaluations that draw the exercises and evaluate user responses (evaluations)

## Definition of exercises and evaluations
And exercise is a class with a draw() method. The class initializes variables used to draw all parts of the exercise. The draw() method creates a DPG draw_node. It returns a named tuple containing at least the uuid indicating this node. The default is to paint the draw_node in a **hidden** state and let DrawQueue() from the helpers module take care of unhiding the node.

An evaluation is a function that paints an exercise a number of times or until the clock runs out. User input is required to progress through the evaluation. This input is evaluated and recorded using the Evaluation() class from the helpers module. 

A typical evaluation is done by:

- creating an exercise object such as exercises.Anaglyph()
- creating an object containing the queue from helpers.DrawQueue()
- running an evaluation function like evaluations.anaglyph()
- recording the state and outcomes of the evaluation in an evaluation object: evaluations.Evaluation()

The evaluation logic defines how to progress through the evaluation and adjusts the exercise object variables accordingly. For instance, the anaglyph evaluation function by default states that:

 - They keyboard arrows are recorded as input for the evaluation.
 - The function runs for 2 minutes or until 50 answers have been given.
 - The answer can be True (success) or False (fail).
 - For every 2 True answers, the primary parameter (in this case bg_offset) is increased by its step (1 by default). The 'success' parameter is reset.
 - For every 2 False answers, the primary parameter is reset to its initial value. The 'fail' parameter is reset.
 
