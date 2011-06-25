from djutils.queue.decorators import queue_command
from runalive import fetch

@queue_command
def fetch_references(taxon_name):
    '''Fetch references from Mendeley related to a taxon.'''
    fetch(taxon_name)
