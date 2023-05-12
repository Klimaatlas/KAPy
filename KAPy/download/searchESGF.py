""" Search ESGF to get a list of files to download """

#TODO:
# * Make into a function, accepting configuration object
# * Add a progress indicator
# * Get all alternative URLs for duplicate copies. These can be used if the first option fails
# * Handle issue with facets warning
# * Handle path specification

from pyesgf.search import SearchConnection
import os

#Setup search connection
conn = SearchConnection('https://esg-dn1.nsc.liu.se/esg-search/',
                        distrib=True)
ctx = conn.new_context(domain='AFR-22,AFR-44,AFR-44i',
                       variable='tas',
                       time_frequency='mon',
                       facets='experiment')
print('Found', ctx.hit_count ,'hits...')

#Write each URL out to a separate file
for ds in ctx.search():
    files = ds.file_context().search()
    for f in files:
        fname=os.path.basename(f.download_url)
        with open('scratch/downloads/URLs/'+fname,'w') as URLfile:
            URLfile.write(f.opendap_url)
        
