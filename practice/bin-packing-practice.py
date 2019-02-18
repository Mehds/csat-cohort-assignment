from ortools.algorithms import pywrapknapsack_solver
import pdb

def main():

	weights = [[565, 406, 194, 130, 435, 367,  147, 421, 255], [565, 406, 194, 130, 435, 367,  147, 421, 255]]
	capacities = [425, 425]
	values = weights[0]

	solver = pywrapknapsack_solver.KnapsackSolver(pywrapknapsack_solver.KnapsackSolver.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'test')


	solver.Init(values, weights, capacities)


	computed_value1 = solver.Solve()
	packed_items = [x for x in range(0, len(weights[0])) if solver.BestSolutionContains(x)]
	packed_weights = [weights[0][i] for i in packed_items]

	print(packed_items)
	print(packed_weights)

	print(computed_value1)

	
	computed_value2 = solver.Solve()

	packed_items = [x for x in range(0, len(weights[0])) if solver.BestSolutionContains(x)]
	packed_weights = [weights[0][i] for i in packed_items]

	print(packed_items)
	print(packed_weights)

	print(computed_value2)

	computed_value3 = solver.Solve()

	packed_items = [x for x in range(0, len(weights[0])) if solver.BestSolutionContains(x)]
	packed_weights = [weights[0][i] for i in packed_items]

	print(packed_items)
	print(packed_weights)

	print(computed_value3)

if __name__ == '__main__':
	main()