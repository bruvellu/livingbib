#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Client that access uBio.'''

from base64 import b64decode
from urllib2 import urlopen, quote
from xml.etree.ElementTree import parse
from keycode import keycode_string

class uBio:
    '''Integration with uBio.'''
    def __init__(self):
        self.baseurl = 'http://www.ubio.org/webservices/service.php?function='
        self.key = keycode_string
        print 'Started uBio.'

    def call(self, url):
        '''Standard function to call, parse, and return the results.'''
        root = parse(urlopen(url)).getroot()
        return root

    def build_url(self, parameters, key=True):
        '''Build url from a list of parameters, function name must be first.'''
        if key:
            parameters.append('keyCode=%s' % self.key)
        parstring = '&'.join(parameters)
        url = self.baseurl + parstring
        return url

    def xmltodic(self, elements):
        '''Convert elements extracted from xml to a python dictionary.'''
        if not elements:
            return []
        b64tags = ['nameString', 'fullNameString', 'nameStringLink', 
                'fullNameStringLink']

        converted = []

        for value in elements:
            item = {}
            for field in value:
                if field.tag in b64tags:
                    item[field.tag] = b64decode(field.text)
                else:
                    item[field.tag] = field.text
            converted.append(item)

        return converted

    def compile(self, scientific, vernacular):
        '''Compile list of taxa to be shown.

        Uses the taxon name as key to store the different versions.

        Layout:
            
            {
                'Clypeaster subdepressus': {
                    'vernacular': [{
                        'languageCode': 'xxx', 'nameStringLink': 'Schefflera 
                        actinophylla', 'nameString': 'octopus tree', 
                        'packageName': 'Apiales', 'packageID': '648', 
                        'languageName': 'unspecified', 'fullNameStringLink': 
                        'Schefflera actinophylla (Endl.) H. A. T. Harms', 
                        'namebankIDLink': '475857', 'namebankID': '4755217'
                        },],
                    'scientific': [{
                        'fullNameString': 'Sepia octopus Molina, 1789', 
                        'rankID': '24', 'nameString': 'Sepia octopus', 
                        'packageName': 'Cephalopoda', 'packageID': '22', 
                        'rankName': 'species', 'basionymUnit': '0', 
                        'namebankID': '640849'
                        },]
                }
            }
        '''
        final = {}

        # Prepare.
        if scientific:
            for entry in scientific:
                final[entry['nameString']] = {'scientific': [], 'vernacular': []}
        if vernacular:
            for entry in vernacular:
                final[entry['nameStringLink']] = {'scientific': [], 'vernacular': []}

        # Populate scientific.
        if scientific:
            for entry in scientific:
                final[entry['nameString']]['scientific'].append(entry)
        # Populate vernacular.
        if vernacular:
            for entry in vernacular:
                final[entry['nameStringLink']]['vernacular'].append(entry)

        # Convert to list.
        final_list = []
        for k, v in final.iteritems():
            final_list.append({
                'name': k,
                'vernacular': v['vernacular'],
                'scientific': v['scientific'],
                })
        final_list.sort()

        return final_list

    def search_name(self, query):
        '''Search for a name.

        namebank_search:
            This function will return NameBankIDs that match given search terms

        ex: http://www.ubio.org/webservices/service.php?function=namebank_search&searchName=Octopus&sci=1&vern=1&keyCode=

        searchName - search term to search by nameString
        searchAuth - search term to search by authorship
        searchYear - search term to search by year
        order - (nameString or languageCode) by default the results will be ordered by nameString
        sci - (0 or 1) to include scientific name results
        vern - (0 or 1) to include vernacular (common name) results
        keyCode - your personal uBio keycode. If you don't have one, obtain one here

        Standard 'value' from xml scientificNames:
            <value>
                <namebankID>2842955</namebankID>
                <nameString>QXN0cmFjYW50aGEgb2N0b3B1cw==</nameString>
                <fullNameString>QXN0cmFjYW50aGEgb2N0b3B1cw==</fullNameString>
                <packageID>663</packageID>
                <packageName>Rosales</packageName>
                <basionymUnit>722509</basionymUnit>
                <rankID>24</rankID>
                <rankName>species</rankName>
            </value>

        Standard 'value from xml vernacularNames:
            <value>
                <namebankID>4637287</namebankID>
                <nameString>QW5nZWwgb2N0b3B1cw==</nameString>
                <languageCode>eng</languageCode>
                <languageName>English</languageName>
                <packageID>22</packageID>
                <packageName>Cephalopoda</packageName>
                <namebankIDLink>514143</namebankIDLink>
                <nameStringLink>VmVsb2RvbmEgdG9nYXRhIHRvZ2F0YQ==</nameStringLink>
                <fullNameStringLink>VmVsb2RvbmEgdG9nYXRhIHRvZ2F0YSBDaHVuLCAxOTE1</fullNameStringLink>
            </value>
        '''
        # Encode query (eg, replace ' ' by '%20').
        quoted = quote(query)
        parameters = [
                'namebank_search', # function
                'searchName=%s' % quoted, # search name
                'sci=1', # scientific names
                'vern=1', # vernacular names
                ]
        url = self.build_url(parameters)
        results = self.call(url)

        # Parse raw xml values.
        sci_names = results.findall('scientificNames/value')
        vern_names = results.findall('vernacularNames/value')
        # Convert to python list of dictionaries.
        scientific_names = self.xmltodic(sci_names)
        vernacular_names = self.xmltodic(vern_names)

        final = self.compile(scientific_names, vernacular_names)

        return final

