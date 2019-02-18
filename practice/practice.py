from ortools.linear_solver import pywraplp

def main():
	solver = pywraplp.Solver('SolveSimpleSystem', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

	# Creating the variables for the solver.
	x = solver.NumVar(-solver.infinity(), solver.infinity(), 'x')
	y = solver.NumVar(-solver.infinity(), solver.infinity(), 'y')

	# Adding contraints: x + 2y <= 14
	c1 = solver.Constraint(-solver.infinity(), 14)
	c1.SetCoefficient(x, 1)
	c1.SetCoefficient(y, 2)

	# Adding contraints: 3x - y >= 0
	c2 = solver.Constraint(0, solver.infinity())
	c2.SetCoefficient(x, 3)
	c2.SetCoefficient(y, -1)

	# Adding contraints: x - y <= 2
	c3 = solver.Constraint(-solver.infinity(), 2)
	c3.SetCoefficient(x, 1)
	c3.SetCoefficient(y, -1)

	# Objecive function

	objective = solver.Objective()
	objective.SetCoefficient(x, 3)
	objective.SetCoefficient(y, 4)
	objective.SetMaximization()

	# Call the solver
	solver.Solve()

	print(3*x.solution_value() + 4 * y.solution_value())
	print(x.solution_value())
	print(y.solution_value())

if __name__ == '__main__':
	main()
