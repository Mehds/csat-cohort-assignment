import sys
# import pdb # for debugging using pdb.set_trace()
import time
from ortools.sat.python import cp_model

# Milestone 1: implement a basic multiple bin packing solver.

def main():
	# Keep track of data from the file
	countries_counts = {} # How many people in each country?
	country_flags = {}
	genders = {} # How many people in each gender?
	students = [] # This is a list of student information, each entry contains [gender, country, email]

	with open(sys.argv[1]) as input_file:

		content = input_file.readlines()
		while len(content) < 5000:
			content += content

		student_count = len(content) # Sanity check
		female_flags = [0]*student_count 

		for i, line in enumerate(content):
			chunks = line.upper().strip().split(',')

			gender = chunks[0].strip()
			genders[gender] = genders.setdefault(gender, 0) + 1
			if gender == "FEMALE": female_flags[i] = 1 

			country = chunks[1].strip()
			countries_counts[country] = countries_counts.setdefault(country, 0) + 1

			students.append(chunks)


	# print(genders)
	# print(countries_counts)
	print(student_count)
	# print(female_flags)
	female_ratio = sum(female_flags)/len(female_flags)

	cohort_count = int(sys.argv[3])

	cohort_max_size = student_count // cohort_count + 1
	cohort_min_size = student_count // cohort_count

	# create the country_flags dictionary, we want it to map a country name to a tuple: (ratio in the student body, binary list of students that belong to)
	#TODO: Make this less ugly
	country_flags = {}
	for country, count in countries_counts.items():
		# We will only consider countries that have a presence that would make up at least 20% of a cohort. 
		# For example with a min cohort size of 32, we will explicitly deal with any country that has 6 or more representatives
		if count >= cohort_min_size // 5:
			flags = [ 1 if student_data[1].strip().upper() == country else 0 for student_data in students]

			country_flags[country] = [count / student_count, flags]

	# print(country_flags)

	# Feed the information to the c-sat solver
	# Results should be a 2d array, result[i] is the list of all student ids that belong to cohort i.
	# ids are in the order in which we read the students from our input file.
	results = solver((female_ratio, female_flags), country_flags, cohort_count = cohort_count, student_count = student_count)


	# # Output a proper CSV
	# output_file = open(sys.argv[2], "w+")
	# output_file.write("cohort,gender,country,email")
	# # For each result we get
	# for i, result in enumerate(results):
	# 	# For each student in the cohort
	# 	for student_id in result:
	# 		# Write out the cohort number (+1 for human readability), joined with the chunked information we already had
	# 		output_file.write('\n%i,%s' % (i+1, ','.join(students[student_id])))

	# output_file.close()

 
def student_assignment_to_student_ids(solver, student_assignment):
	# For a given cohort, the solver has #student_count boolean variables. This lets us check 

	return [i for i in range(len(student_assignment)) if solver.Value(student_assignment[i]) == 1]
	# output = []
	# for i, assignment in enumerate(student_assignment):
	# 	if solver.Value(assignment) == 1:
	# 		output.append(i)

	# return output

def solver(gender_info, country_info, cohort_count=10, student_count=1):

	# Give a small range for cohort sizes, this could be revised
	cohort_max_size = student_count // cohort_count + 1
	cohort_min_size = student_count // cohort_count

	# Track gender information:
	female_ratio, female_flags = gender_info

	cohort_min_females = int(cohort_max_size * female_ratio)
	cohort_max_females = cohort_min_females + 1


	# Create the model
	model = cp_model.CpModel()

	# model should track an int variable for each cohort, Each cohort can have a value between cohort_min_size and cohort_max_size
	# similarly, we track the number of females in the cohort.
	# similarly, for each country we care about, we track a similar 
	cohort_sizes = []
	gender_balance = []
	country_balance = {c: [] for c in country_info} # map a country to a list of constraint
	for cohort_index in range(cohort_count):
		varName = 'cohort-%i' % (cohort_index+1)

		cohort_sizes.append(model.NewIntVar(cohort_min_size, cohort_max_size, varName))
		gender_balance.append(model.NewIntVar(cohort_min_females, cohort_max_females, varName + '-gender'))
		for country, country_data in country_info.items():
			ratio = country_data[0]
			cohort_min_country = int(cohort_min_size * ratio)
			cohort_max_country = cohort_min_country + 1
			country_balance[country].append(model.NewIntVar(cohort_min_country, cohort_max_country, varName+'-'+country))

	# Constraint: The value assigned to all cohorts should add up to the number of students.
	model.Add(sum(cohort_sizes) == student_count)


	# for c in cohort_sizes:
	# 	model.Add(c >= cohort_min_size) Now redundant given that the int var already has the min value

	# Enforce that the number of student_assignments for a given cohort are equal to the cohort_sizes
	# For each cohort, we have a list of boolean variables representing whether or not any of our students are there.
	# if student_assignments[i][j] is 1, that means that student with id j belongs to cohort i
	student_assignments = [] 

	for c_index in range(cohort_count):
		# Create and append the boolean variables
		student_assignments.append([model.NewBoolVar("s"+str(c_index)+str(s)) for s in range(student_count)])
		# Enforce the constraint that the sum of students assigned to the cohort should equal the cohort size.
		model.Add(sum(student_assignments[c_index]) == cohort_sizes[c_index])
		# Enforce that the sum of all female assignments to the cohort should equal the gender_balance goal for the cohort
		model.Add(sum([student_assignments[c_index][i] for i in range(student_count) if female_flags[i] == 1]) == gender_balance[c_index])
		for country, country_data in country_info.items():
			flags = country_data[1]
			model.Add(sum([student_assignments[c_index][i] for i in range(student_count) if flags[i] == 1]) == country_balance[country][c_index])

	# For each student, we must make sure that they belong to a single cohort
	# This needs to happen after all the boolean variables have been created
	for s_index in range(student_count):
		# Add a constraint that the sum of all student_assignments[i][s] for a specific s is 1
		model.Add(sum([student_assignments[c_index][s_index] for c_index in range(cohort_count)]) == 1)


	# Create a solver object, then solve
	solver = cp_model.CpSolver()
	status = solver.Solve(model)

	# Prepare results: result[i] should be a list of student ids belonging to cohort i
	result = []

	for c_index in range(cohort_count):
		# print('%s, %s' % (solver.Value(cohort_sizes[c_index]), solver.Value(gender_balance[c_index])))
		cohort_assignment = student_assignment_to_student_ids(solver, student_assignments[c_index])
		result.append(cohort_assignment)
		# print(cohort_assignment)

		# for s in student_assignments[c_index]:
		# 	print(solver.Value(s))
		# print('------------------------')


	# print()
	return result


if __name__ == '__main__':
	start = time.time()
	main()
	end = time.time()
	print(end - start)