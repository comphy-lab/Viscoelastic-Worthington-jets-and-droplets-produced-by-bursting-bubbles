import os

# Read the file with two columns
with open('convert.txt', 'r') as file:
    lines = file.readlines()

# Iterate over the lines and execute the command
for line in lines:
    folder_name, replace_value, length = line.strip().split(" ")
    replace_value = float(replace_value)
    replace_value = 100*replace_value
    replace_value = format(float(replace_value),'.0f' )
    os.chdir(folder_name)
    os.system(f"sed -i 's/for ti in range(nGFS)/for ti in {{{replace_value}}}/g' VideoBurstingBubble_facets_jheight.py")
    os.chdir('..')
