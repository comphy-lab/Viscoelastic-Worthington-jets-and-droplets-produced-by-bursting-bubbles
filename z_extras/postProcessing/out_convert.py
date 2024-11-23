import numpy as np 

with open('out_maxjlength_time.txt', 'r') as file:
    data = file.readlines()
    # print(data)
    
for i in range(0, 201, 2):
    first = data[i].strip()
    second = data[i+1].strip().split(",")
    combined_row = [first] + second
    with open('convert.txt', 'a') as output_file:
        output_file.write(' '.join(combined_row)+ '\n')
