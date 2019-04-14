import sys
import pdb # for debugging using pdb.set_trace()
from ortools.sat.python import cp_model
from random import randint

# Milestone 1: implement a basic multiple bin packing solver.
# To run this, pass the following paramenters:
# The path to the input csv file
# The path to the output csv file
# The number of cohorts desired

def main():
	# Keep track of data from the file
	countries_counts = {} # How many people in each country?
	country_flags = {} # Will be explained shortly

	students = [] # This is a list of student information, each entry contains [gender, country, email]
	

	with open(sys.argv[1]) as input_file:

		content = input_file.readlines()

		student_count = len(content) # Sanity check
		female_flags = [0]*student_count # Binary array, 0 if student[i] is a male, 1 if student[i] is female.

		# Loop over the student data.
		for i, line in enumerate(content):
			# Split up the line based on ','
			chunks = line.upper().strip().split(',')
			
			# Get the gender of the current student.
			gender = chunks[0].strip()

			# Set up the female_flags if the student is female.
			if gender == "FEMALE": female_flags[i] = 1 

			# Similarly, get the nationality of the student, and add it to the countries_counts dictionary
			country = chunks[1].strip()
			countries_counts[country] = countries_counts.setdefault(country, 0) + 1

			# Add the student to the students array.
			students.append(chunks)

	# Figure out the Female ratio
	female_ratio = sum(female_flags)/student_count
	
	# Get the cohort count from input
	cohort_count = int(sys.argv[3])

	# Figure out the min and max range for cohort sizes. TODO: This could be a dynamically growing.
	cohort_max_size = student_count // cohort_count + 1
	cohort_min_size = student_count // cohort_count

	# create the country_flags dictionary, we want it to map a country name to a tuple: (ratio in the student body, binary list of students that belong to)
	country_flags = {}
	for country, count in countries_counts.items():
		# We will only consider countries that have a presence that would make up a cohort or more.
		# For example with a min cohort size of 32, we will explicitly deal with any country that has 32 or more representatives
		# TODO: That ratio should be a parameter / dynamically growig. 
		if count >= cohort_min_size:
			flags = [ 1 if student_data[1].strip().upper() == country else 0 for student_data in students] # Create a binary array to point out which students belong to this country

			country_flags[country] = (count / student_count, flags) # Store a tuple with the ratio, and the flags for this country in particular.


	# Feed the information to the c-sat solver
	# Results should be a 2d array, result[i] is the list of all student ids that belong to cohort i.
	# ids are in the order in which we read the students from our input file.
	results = solver((female_ratio, female_flags), country_flags, cohort_count, student_count)


	# Output a proper CSV
	output_file = open(sys.argv[2], "w+")
	output_file.write("cohort,gender,country,email,age") #CSV header
	# For each result we get
	for i, result in enumerate(results):
		# For each student in the cohort
		for student_id in result:
			# Write out the cohort number (+1 for human readability), joined with the chunked information we already had
			output_file.write('\n%i,%s' % (i+1, ','.join(students[student_id])))

	output_file.close()

 
def student_assignment_to_student_ids(solver, student_assignment):
	# For a given cohort, the solver has #student_count binary variables in an array
	# This function will return a list of the student ids that were assigned to the cohort. 
	# Imagine if we had 10 students in total, and wanted 5 per cohort, a given assignment might look like: [0,1,0,1,0,1,0,1,0,1]
	# This function would then return [1,3,5,7,9], or the ids of the students that belong to this cohort.

	return [i for i in range(len(student_assignment)) if solver.Value(student_assignment[i]) == 1]

# Gender info is a tuple containing the female ratio in the class, and a binary array that flags which students are female.
# Country info is a dictionary with country name as a key, and a tuple containing the country ratio, and a binary array that flags students which belong to this country
# cohort_count and student_count are self explanatory
def solver(gender_info, country_info, cohort_count, student_count):

	# Give a small range for cohort sizes, this could be revised
	cohort_max_size = student_count // cohort_count + 1
	cohort_min_size = student_count // cohort_count - 1

	# Track gender information:
	female_ratio, female_flags = gender_info

	# Needs some more testing
	cohort_min_females = int(cohort_min_size * female_ratio)
	cohort_max_females = int(cohort_max_size * female_ratio) + 1


	# Create the model
	model = cp_model.CpModel()

	# model should track an int variable for each cohort, Each cohort can have a value between cohort_min_size and cohort_max_size
	# similarly, we track the number of females in the cohort.
	# similarly, for each country we care about, we track a similar count
	cohort_sizes = []
	gender_balance = []
	country_balance = {c: [] for c in country_info} # map a country to a list of constraint

	for cohort_index in range(cohort_count):
		varName = 'cohort-%i' % (cohort_index+1) # Start with cohort-1 etc.

		cohort_sizes.append(model.NewIntVar(cohort_min_size, cohort_max_size, varName))
		gender_balance.append(model.NewIntVar(cohort_min_females, cohort_max_females, varName + '-gender'))

		for country, country_data in country_info.items():
			ratio = country_data[0]
			cohort_min_country = int(cohort_min_size * ratio)
			cohort_max_country = int(cohort_max_size * ratio) + 1

			country_balance[country].append(model.NewIntVar(cohort_min_country, cohort_max_country, varName+'-'+country))

	# Constraint: The value assigned to all cohorts should add up to the number of students.
	model.Add(sum(cohort_sizes) == student_count)
	# TODO: Validate if we need to add a similar contraint as the above, for female students etc.


	# Enforce that the number of student_assignments for a given cohort are equal to the cohort_sizes
	# For each cohort, we have a list of boolean variables representing whether or not any of our students are there.
	# if student_assignments[i][j] is 1, that means that student with id j belongs to cohort i
	student_assignments = [] 

	for c_index in range(cohort_count):
		# Create and append the boolean variables
		student_assignments.append([model.NewBoolVar("s"+str(c_index)+"_"+str(s)) for s in range(student_count)])
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
	# TODO: Check the status in case of errors

	# Prepare results: result[i] should be a list of student ids belonging to cohort i
	result = []

	for c_index in range(cohort_count):
		cohort_assignment = student_assignment_to_student_ids(solver, student_assignments[c_index])
		result.append(cohort_assignment)
	return result


if __name__ == '__main__':
	main()