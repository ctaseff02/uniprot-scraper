import pandas as pd
import sys
import requests
import json

def main(accession):
    print('🫡  Sending API request to Uniprot...')

    gene = requests.get(f'https://www.ebi.ac.uk/proteins/api/variation/{accession}?format=json')
    
    if gene.status_code == 200:
        print('😃 Request to Uniprot successful.')
        gene_json = json.loads(gene.text)

        features = gene_json['features']

        df = pd.DataFrame(columns=['Position', 'Change', 'Description', 'Genomic Location', 'Significance', 'Source(s) of Significance', 'Significance Review Status'])

        for feature in features:
        
            skip = True

            clinical_significance = ''
            sources = ''
            review_status = ''
            genomic_location = ['unknown']
            descriptions = ''
            change = ''

            if 'clinicalSignificances' in feature:
                for significance in feature['clinicalSignificances']:
                    significance_type = significance['type']
                    if significance_type == 'Likely pathogenic' or significance_type == 'Pathogenic' or significance_type == 'Variant of uncertain significance':
                        skip = False
                        clinical_significance += significance_type
                        sources += ', '.join(significance['sources'])
                        if 'reviewStatus' in significance:
                            review_status += significance['reviewStatus']
                        
            else:
                continue

            if(skip):
                continue
            
            if 'descriptions' in feature:
                for description in feature['descriptions']:
                    if 'value' in description:
                        descriptions += description['value']

            if 'mutatedType' in feature:
                change = feature['wildType'] + feature['begin'] + feature['mutatedType']
            else:
                change = feature['wildType'] + feature['begin'] + 'missing'

            if 'genomicLocation' in feature:
                genomic_location = feature['genomicLocation']
            
            desired_features = {
                'Position': int(feature['begin']),
                'Change': change,
                'Description': descriptions,
                'Genomic Location': genomic_location,
                'Significance': clinical_significance,
                'Source(s) of Signifiance': sources,
                'Significance Review Status': review_status
            }

            df = pd.concat([df, pd.DataFrame(desired_features)], ignore_index=True)
        
        print(df)
        df.to_excel(f'tables/{accession}.xlsx', sheet_name=accession)
        print('🤓 Excel table generated!')
        return df
    
    print(f"😢 Error with status code {gene.status_code} returned with message:\n{gene.reason}")
    return 
    
if __name__ == '__main__':
    arg1 = sys.argv[1]
    main(arg1)