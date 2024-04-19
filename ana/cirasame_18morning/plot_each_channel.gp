# Set input and output file paths
data_file = "output.dat"
output_file = "channel_plots.pdf"

# Set plot title and labels
set xlabel "ADCValue"
set ylabel "Channel Data"

# Set output file format and resolution
set terminal pdfcairo enhanced font "arial,10"

# Set x range
set xrange [100:500]

# Set y scale to logarithmic
set logscale y

# Open the output PDF file
set output output_file

# Loop over each channel and plot on a separate page
do for [i=0:127] {
    # Plot the data for channel i
    plot data_file using 1:(column(i+2)):(1.5) with circles lc rgb "blue" fs solid title sprintf("Channel %d", i)
}

# Close the output PDF file
set output
