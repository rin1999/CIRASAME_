# Set terminal to PNG format
set terminal png

# Set output file name
set output "gain-vs-biasDAC.png"

# Set title for the plot
set title "Gain vs Bias DAC"

# Set labels for x and y axes
set xlabel "Bias DAC"
set ylabel "Gain"

# Set grid
set grid

# Set point type to filled circle
set style line 1 pointtype 7 pointsize 1.5

# Define the comments for each point
comment(x, y, text) = sprintf("set label \"%s\" at %f,%f center", text, x, y)

#comment(125, 80, "hoge")

# Plot the data from the file with filled circles and lines
plot "gain-vs-biasDAC.dat" using 1:2 with linespoints linestyle 1 title columnheader
