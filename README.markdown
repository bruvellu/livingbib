# Living Bibliography

This app queries Mendeley database (via API) for a specific taxon name and displays a list of references. The idea is to aggregate references about a specific species and extract some fun from it. For example, the most popular organisms, trending taxa, top authors by taxon, etc. There are many hiccups, of course, but I decided to give it a try.  

For now I just layed out the basic models and templates and got 50 references
from some model organisms. Have a [look](http://livingbib.organelas.com/)!

Feel free to contribute with ideas and hacks.

Here is a quicklist with some features:

## ToDos

- Main page showing the most popular taxa.
- Proper taxonomic tree pulled from ITIS.
- Search with smooth taxon name autocomplete.
- Show number of results, top authors and top journals for each taxon.
- Display graph with number of publications per year for taxon.
- Create links from identifiers.
- Provide links to external taxonomic/biological databases (eol, wikispecies, etc).
- Pull and display image and taxon description (from wikispecies/eol?).
- Quickly order list with Ajax calls and refine results by metadata.
- Search twitter and other activity streams for live feed about a taxon.
- Provide an easy way to save references to reference managers (coins).
