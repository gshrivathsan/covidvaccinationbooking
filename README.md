# Covid Vaccination System
![image](https://github.com/gshrivathsan/covidvaccinationbooking/assets/82453782/f0f3b71e-d8f2-43e7-a3af-7145dc56bcd4)


## Devrev Coding Task 2 (Round 2)

### Requirements

#### Type of Users
    
    •User
    •Admin

#### User Use Cases

    ●	Login
    ●	Sign up (with apt data validations)
    ●	Searching for Vaccination centre and    working hours
    ●	Apply for a vaccination slot (only 10 candidates allowed per day)
    ●	Logout

#### Admin Use Cases

    ●	Login (Seperate login for Admin)
    ●	Add Vaccination Centres
    ●	Get dosage details (group by centres)
    ●	Remove vaccination centres

### Tech Stack
    ● Backend  : FLASK
    ● Frontend : HTML, CSS, JS
    ● Database : Sqlite


### Prerequisites

    ● Python 3.9 or above

### Setup


    ● Clone the github repo.
    ● Install the requirements.txt file
        $ pip install -r requirements.txt
    ● Navigate the IDE terminal to the project path
    ● Run the following commands to start the flask application
        > $env:FLASK_APP = "app.py"
        > $env:FLASK_DEBUG = "1"
        > flask run 
    ● Click the localhost URL appeared in the terminal.


### Features

     ● Admin and Users have separate login/logout.
     ● Admin can add/view/remove vaccination centers.
     ● Admin can view/remove the registered users.
     ● Users can book a slot.
     ● Users can view their booking history.
     ● Both admin and users can search for a vaccination center/ working hours.

