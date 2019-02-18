from ortools.sat.python import cp_model

class SolutionPrinter(cp_model.CpSolverSolutionCallback):

	def __init__(self, variables):
		cp_model.CpSolverSolutionCallback.__init__(self)
		self.__variables = variables
		self.__solution_count = 0

	# Version for sat problems
	# def on_solution_callback(self):
	# 	self.__solution_count += 1
	# 	for v in self.__variables:
	# 		print('%s=%i' % (v, self.Value(v)), end=' ')
	# 	print()

	def on_solution_callback(self):
		print('Solution %i' % self.__solution_count)

		print('  objective value = %i' % self.ObjectiveValue())
		for v in self.__variables:			
			print('%s=%i' % (v, self.Value(v)), end=' ')
		print()
		self.__solution_count += 1

	def solution_count(self):
		return self.__solution_count


def SimpleSatProgram():

	model = cp_model.CpModel()

	# adding vars
	num_vals = 3

	x = model.NewIntVar(0, num_vals-1, 'x')
	y = model.NewIntVar(0, num_vals-1, 'y')	
	z = model.NewIntVar(0, num_vals-1, 'z')

	model.Add( x != y)

	model.Maximize(x + 2 * y + 3 * z)

	solver = cp_model.CpSolver()

	# status =  solver.Solve(model) basic version

	solution_printer = SolutionPrinter([x, y, z])

	# Searching for all solutions only works for sat problems, not optimization.	
	# Takes a printer which defines a printing callback
	# status = solver.SearchForAllSolutions(model, solution_printer)

	status = solver.SolveWithSolutionCallback(model, solution_printer)
	# Other statuses:
	# 	OPTIMAL	An optimal feasible solution was found.
	#	FEASIBLE	A feasible solution was found, but we don't know if it's optimal.
	# 	INFEASIBLE	The problem was proven infeasible.
	# 	MODEL_INVALID	The given CpModelProto didn't pass the validation step. You can get a detailed error by calling ValidateCpModel(model_proto).
	# 	UNKNOWN	The status of the model is unknown because a search limit was reached.

	# if status == cp_model.OPTIMAL:
	#     print('x = %i' % solver.Value(x))
	#     print('y = %i' % solver.Value(y))
	#     print('z = %i' % solver.Value(z))


SimpleSatProgram()
