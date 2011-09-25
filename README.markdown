# Living Bibliography

This app queries [Mendeley](http://www.mendeley.com) database (via API) for a specific taxon name and displays a list of references. The idea is to aggregate references about a specific species and extract some fun from it. For example, the most popular organisms, trending taxa, top authors by taxon, etc. Taxon search is powered by [uBio](http://www.ubio.com/) web services allowing the use of a scientific or common name in queries.

Only the basics are working now. You can search and click on a taxon to see a list of related articles. If the taxon is not in the database yet, fetching is run on demand (you will need to wait a bit and refresh the page until I smooth it out to update the page automatically). A taxon page shows a list of references with a few ordering controls (eg, readers, year, journal) and links to the article page, when available.

Give it a try: [livingbib.organelas.com](http://livingbib.organelas.com/)!

This is an experiment Feel free to contribute with ideas and hacks.

## Some ideas

- Apply classification schema to taxa in order to also include references from child
  nodes when browsing higher taxonomic ranks (eg, phylo).
- Define a set of basic statistics for a taxon (eg, active authors, top journals).
- Visualize data with nice graphs.
- Pull data and integrate with external biological databases.
- Provide standard ways to save references (COinS).
