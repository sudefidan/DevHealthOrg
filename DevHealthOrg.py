import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Constant -> (Adjustable) Minimum number of meetings for sufficient healthcare
VISIT_THRESHOLD = 12

# Data store
users = {}
beneficiaries = set()
districts = set()

# Read users
with open('data/users.txt', 'r') as file:
    for line in file:
        user_id, beneficiary_ids = line.strip().split(': ')
        beneficiary_ids = beneficiary_ids.split(',')
        users[user_id] = beneficiary_ids  # add data to dict
        beneficiaries.update(beneficiary_ids) # update with unique ids

# Read disctricts
temp_pair = set() # temporary beneficiary-district pairs for identificiation
with open('data/areas.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        beneficiary_id, district_id = row
        temp_pair.add((beneficiary_id, district_id)) #a dd to temp
        districts.add(district_id) # add data to set

# Read visits
visits = {}
with open('data/visits.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:
        date, visit_type, beneficiary_id = row # read data of each visit
        if beneficiary_id not in visits:
            visits[beneficiary_id] = 0
        visits[beneficiary_id] += 1 # add data to dict

# Calculate the insufficient healthcare beneficiaries in each district
insufficient = {district: 0 for district in districts} # dict for district-beneficiary pair
for user_id, beneficiary_ids in users.items(): # for each beneficiary
    for beneficiary_id in beneficiary_ids:
        if beneficiary_id in visits and visits[beneficiary_id] < VISIT_THRESHOLD: # check if beneficiary met the required visit
            district_id = next((district_id for district_id in districts if (beneficiary_id, district_id) in temp_pair), None) #iterate each district
            if district_id:
                insufficient[district_id] += 1 # increment the count

# Write results to a CSV file
with open('insufficient_per_district.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['District', 'Number of Insufficient Beneficiaries', 'Risk Level'])
    risk_levels = []
    for district, count in insufficient.items():
        if count > 200:
            risk_level = 'Extremely High'
        elif count > 150:
            risk_level = 'High'
        elif count > 100:
            risk_level = 'Moderate'
        elif count > 50:
            risk_level = 'Low'
        else:
            risk_level = 'Extremely Low'
        writer.writerow([district, count, risk_level])
        risk_levels.append(risk_level)

# Visualisation -plotting
districts_list = list(insufficient.keys())
beneficiaries_count = list(insufficient.values())

# Color palette
colors = ['red' if level == 'Extremely High' else 'orange' if level == 'High' else 'yellow' if level == 'Moderate' else 'green' if level == 'Low' else 'skyblue' for level in risk_levels]

plt.figure(figsize=(10, 6))
plt.bar(districts_list, beneficiaries_count, color=colors)

for i, count in enumerate(beneficiaries_count):
    plt.text(i, count, str(count), ha='center', va='bottom')

plt.xlabel('Districts', fontsize=10)
plt.ylabel('Number of Insufficient Beneficiaries', fontsize=10)
plt.title('Districts with Beneficiaries without Sufficient Healthcare', fontsize=14)

plt.xticks(rotation=90, ha='right')
plt.grid(True)

red_patch = mpatches.Patch(color='red', label='> 200 (Extremely High)')
orange_patch = mpatches.Patch(color='orange', label='150-200 (High)')
yellow_patch = mpatches.Patch(color='yellow', label='100-150 (Moderate)')
green_patch = mpatches.Patch(color='green', label='50-100 (Low)')
blue_patch = mpatches.Patch(color='skyblue', label='50 < (Extremely Low)')

plt.legend(handles=[red_patch, orange_patch, yellow_patch, green_patch, blue_patch], loc='upper right')

plt.show()
