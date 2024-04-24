#!/bin/bash

# A useful handy script to sort incomplete threshold scan data.
#  After the out filename to be read as the first argument,
# list the CIRASAME number to be rescued. Redirect the output to
# as needed.
#
# e.g
# bin/out_sorter.sh ana/out/pulseheightfit_all_20240423_1440.out 1 2 3 4 5 6 7 8 9 10 11 12 > ana/out/pulseheightfit_all_20240423_1400-1620merged.out
# bin/out_sorter.sh ana/out/pulseheightfit_all_20240423_1620.out 13 14 15 16 17 18 >> ana/out/pulseheightfit_all_20240423_1400-1620me


# Check if the correct number of arguments is provided
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <filename> <value1> [<value2> ...]"
    exit 1
fi

# Assign the filename to a variable
filename="$1"

# Extract values from the arguments starting from the second argument
shift
values=("$@")

# Read the file line by line and filter based on the second column value
while IFS= read -r line || [ -n "$line" ]; do
    # Check if the line is not empty
    if [ -n "$line" ]; then
        # Extract the second column value using awk
        value=$(echo "$line" | awk '{print $2}')
        
        # Check if the second column value matches any of the provided values
        for val in "${values[@]}"; do
            if [ "$value" = "$val" ]; then
                # Output the line if there is a match
                echo "$line"
                break
            fi
        done
    fi
done < "$filename"
