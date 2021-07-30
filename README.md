# The Sickulator

Created by: Jack Driscoll, Thomas Hancock, Julia Harbord, Jonah Kornberg, and Dahlia La Pommeray

Link to Issue tracker: https://trello.com/b/rdkSQQiJ/sickulator

Link to repository: https://github.com/JKornberg/Sickulator

# Installation
`pip install sickulator`

Run with `sickulator`

# Description
The Sickulator is an agent-based simulator made to visually represent the spread of disease in a small city. The user is provided several configurable options to affect the outcome of the "sickulation". 

# Controls
Arrow keys control the camera, and left-clicking on an agent or building provides a brief description. Selected agents are automatically followed by the camera.

# References
Kids Can Code - https://www.youtube.com/watch?v=3UxnelT9aCo&list=PLsk-HSGFjnaGQq7ybM8Lgkh5EMxUWPm2i

Assets - www.kenney.nl
# Development set up

### Mac OS / Linux

```
python3 -m virtualenv venv
source venv/bin/activate
# If you're using VSCode, make sure your python interpreter is set to 'venv' #
pip install --upgrade pip
pip install -r requirements.txt
python sickulator/main.py
```
