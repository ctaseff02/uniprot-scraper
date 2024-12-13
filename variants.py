import pandas as pd
import requests
import json
import sys

def polyphen_score(accession: str, genomic_locations: dict):
    print('🧐 Sending API request to Ensembl VEP...')
    server = "https://rest.ensembl.org"
    ext = "/vep/human/hgvs"
    headers={ "Content-Type" : "application/json", "Accept" : "application/json"}
    r = requests.post(server+ext, headers=headers, data=genomic_locations, timeout=30)
 
    if not r.ok:
        print('👺 API call failed for some reason.')
        r.raise_for_status()
        sys.exit()  
    
    print('🤩 Request to Ensembl VEP successful.')
    decoded = r.json()

    polyphen_df = pd.DataFrame(columns=['Genomic Location', 'Polyphen Score'])

    _input = '?'
    polyphen_score = 0

    for vep in decoded:
        if 'input' in vep:
            _input = vep['input']
        if 'transcript_consequences' in vep:
            for consequence in vep['transcript_consequences']:
                if ('polyphen_score' in consequence) & ('missense_variant' in consequence['consequence_terms']):
                    polyphen_score = consequence['polyphen_score']

                    excel_columns = {
                        'Genomic Location': [_input],    
                        'Polyphen Score': [polyphen_score]
                    }

                    polyphen_df = pd.concat([polyphen_df, pd.DataFrame(excel_columns)], ignore_index=True)

    with pd.ExcelWriter(f'tables/{accession}.xlsx', engine='openpyxl', mode='a', if_sheet_exists='new') as writer: # pylint: disable=abstract-class-instantiated
        polyphen_df.to_excel(writer, sheet_name='polyphen_scores', index=False)

    #return polyphen_df

def main(accessions: list):
    failed_accessions = []
    count = 0
    for accession in accessions:
        print(f'🫡  Sending API request to Uniprot for {accession}...                   {count}/' + str(len(accessions)))

        gene = requests.get(f'https://www.ebi.ac.uk/proteins/api/variation/{accession}?format=json', timeout=30)
        
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
                            descriptions += description['value'] + ', '

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
            
            df.to_excel(f'tables/{accession}.xlsx', sheet_name='significances')
            mask = df['Significance'] != 'Variant of uncertain significance'
            gene_locs = df[~mask]
            
            gene_locs_list = gene_locs['Genomic Location'].tolist()

            genomic_locations = json.dumps({"hgvs_notations": gene_locs['Genomic Location'].tolist()})

            if 'unknown' in genomic_locations:
                print('Unitprot found no genomic locations.')
                continue
            
            if len(gene_locs_list) > 200:
                print("🤬 Provided gene variant has greater than 200 gene locations. Polyphen scores will appear in multiple sheets.")
                for i in range(0, len(gene_locs_list), 200):
                    genomic_locations_subset = json.dumps({"hgvs_notations": gene_locs_list[i:i + 200]})
                    polyphen_score(accession, genomic_locations_subset)
            else:
                polyphen_score(accession, genomic_locations)

            print('🤓 Excel table generated!')

        else:
            print(f"😢 Error with status code {gene.status_code} returned with message: {gene.reason}\n")
            failed_accessions.append(accession)

        count += 1

    if len(failed_accessions) > 0:
        print(f"😔 Here's a list of variants we were unable to scrape: {failed_accessions}")

if __name__ == '__main__':
    prompt = input('👩‍🔬 What variant name(s) would you like to scrape for? Please seperate each name by a comma.\n').split(",")
    unique_prompt = []
    prompt_list = [string.strip() for string in unique_prompt]

    for item in prompt:
        if item not in unique_prompt:
            unique_prompt.append(item)
    

    main(unique_prompt)
    print("😺 Scrape complete!")