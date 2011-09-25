from djutils.queue.decorators import queue_command
from livingbib.runalive import fetch

@queue_command
def fetch_references(taxon_name):
    '''Fetch references from Mendeley related to a taxon.'''
    #FIXME Check if query is already in queue line before adding.
    fetch(taxon_name)
