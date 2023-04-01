# This file will take the output from prepare_data and:
# 1. Try to parse Table 1 data for each PDF
# -- The top left corner of each page will be searched to see if there is data for the top 12 minerals
# -- Trace minerals, due to parsing difficulties, will not be included at this time
# -- Only the first set of sample data will be kept at this time
# The output will either be a df or a dictionary of all lunar samples. 
# The stretch goal is to get that dictionary into a python library that can be pip'd. 
# The underlying processing and data should never have to be ran by an outsider since the pdfs are constant
