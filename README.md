# uniprot-scraper
 for emma :)

 ## How to run program
 1. Open terminal
 2. Navigate to where you cloned this repository
 3. Run the command:

 ```
python3 variants.py '(insert variant name here)'
 ```
 4. Tables will be exported to /tables


### Troubleshooting notes:

If you are getting an error on the API call, check the variant name. Even if it is 100% correct, Uniprot might have made a mistake. If this happens, go to the variant you want on Uniprot and:

1. Click download
2. Click Generate URL for API
3. Make sure the variant name matches exactly what appears in the link. 

    For example: https://www.ebi.ac.uk/proteins/api/variation/Q12879?format=json


 with love,

 connor <3
