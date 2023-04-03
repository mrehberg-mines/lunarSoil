# Introduction

This repo is meant to digitize the data within the Lunar Compendium. It looks at all of the sample data `https://www.lpi.usra.edu/lunar/samples/#catalogues,` on the PDFs of this website. It uses a PDF scraper to take the data within the first `Table 1` which contains the information on sample characteristics. It also pulls in the api sample data from `https://curator.jsc.nasa.gov/rest/lunarapi/samples/sampledetails/`. This is all combined into the file `ouputs\final_out.csv`. 

There were 948 sample IDs from the initial website. Almost all of these had API data that could be matched. There were 568 parsed characterizations from the PDFs. Some of these captured multiple trails from within the PDF. If this was the case it was shown by appending all the parsed data into a single cell containing a list. 

-Matthew Rehberg