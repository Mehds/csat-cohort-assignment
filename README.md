## What is this about? 

The purpose of this project is to create scripts that can fairly quickly create balanced cohorts of students.

"Balanced" is a function of multiple parameters that can be toggled on or off based on the data provided. The current version of the code for example balances gender and nationality in the cohort assignment. In other words, the Male/Female ratio in any given cohort should be as close to the Male/Female ration of the whole population as possible. If a nationality represents 15% of the student body, then no single cohort should have more than 15% of its students with that nationality.

## Technologies used

The current solution leverage [or-tools](https://developers.google.com/optimization/introduction/python "Or-tools python guide"), and takes a linear programming approach to solving the cohort assignment problem. The code is fairly well commented, and this repo comes with examples from the documentation for practice purposes.

## To do list:
The current implementation mostly works, but there is still a need for several bugfixes and improvements:
1. **Dynamic range increase:** Based on the ratios found in the population, we calculate upper and lower bounds for representation within each cohort (There can be a minimum of x males, and a maximum of y males for example.) Given that these values are integers, the system of equations generated is not always solveable. Currently this means a manual change to the logic to accomodate for this. Ideally, we should catch errors from the platform, then broaden the range if the stricter one was not solveable. 
1. **Performance scaling:** The script scales with number of cohorts and number of students. Number of cohorts seems to be the main contributor to performance as it sharply increases the number of variables and assignments needed. Suggestions to accomodate for higher performance is to divide and conquer: Instead of trying to assign 20 valid cohorts in one go for example, assign 2 valid ones, then for each data set assign 2 new valid ones, etc. 
1. **Addapting to peer groups:** Fundamentally the peer group creation problem is the same as the cohort creation problem. Giving the user an option to generate peer groups given data on existing cohorts would be key.
1. **Usefulness to the ALU team:** This is currently a simple script that should be packaged in some kind of online or offline application that would be simpler to use for the registrar team.
