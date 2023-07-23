input_file = 'C:/Users/aniqp/Documents/project_air_quality/datafiles/kitchener_pm25.csv'
output_file = 'C:/Users/aniqp/Documents/project_air_quality/datafiles/kitchener_pm25.csv'

with open(input_file, 'r') as f:
    lines = f.readlines()

# Remove empty lines
lines = [line for line in lines if line.strip()]

# Save the modified content back to the output file
with open(output_file, 'w') as f:
    f.writelines(lines)