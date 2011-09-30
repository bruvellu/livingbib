/*
 * Author: Bruno C. Vellutini
*/

function searchTaxon(redirect) {
  $("#dark-loading").fadeIn();
  if ( redirect == true ) {
    var query = $("#search-query").val();
    Dajaxice.livingbib.alive.search_taxon(Dajax.process, {'query': query, 'redirect': redirect})
  } else {
    $("#search-results").fadeOut("slow", function() {
        var query = $("#search-query").val();
        Dajaxice.livingbib.alive.search_taxon(Dajax.process, {'query': query, 'redirect': redirect})
        });
  }
  return false
}

function endSearch(query) {
  // Activate TableSorter for table of references.
  $("#results-table").dataTable({
    // Full pagination.
    "sPaginationType": "full_numbers",
    // Show processing time.
    "bProcessing": true,
    });
  // Update browser url display.
  // https://developer.mozilla.org/en/DOM/Manipulating_the_browser_history
  var stateObj = { uquery: query };
  history.pushState(stateObj, query, "?query=" + encodeURIComponent(query).replace("%20", "+"));
  $("#search-results").fadeIn();
  $("#dark-loading").fadeOut();
  return false
}

function clearResults() {
  $("#dark-loading").fadeIn();

  //Dajaxice.livingbib.alive.clear_search(Dajax.process)
  // Update browser url display.
  // https://developer.mozilla.org/en/DOM/Manipulating_the_browser_history
  var stateObj = { };
  history.pushState(stateObj, "search", "/search/");

  $("#search-results").fadeOut("fast", function() {
      $(this).html("<div class=\"alert-message notice\">Type a scientific or common name of a taxon in the search box above and press <strong>Search</strong>.</div>") && $("#search-results").fadeIn("slow");
        });
  $("#search-query").val("");
  $("#dark-loading").fadeOut();
  return false
}

// Document ready functions.
$(document).ready(function(){

    // Activate TableSorter for table of references.
    $("#references-table").dataTable({
      // Set default sorting to Year and Readers, descending.
      "aaSorting": [[0,"desc"],[5,"desc"]],
      // Full pagination.
      "sPaginationType": "full_numbers",
      // Show processing time.
      "bProcessing": true,
      // Save the state of the table.
      // "bStateSave": true,
      });

    // Activate TableSorter for table of references.
    $("#results-table").dataTable({
      // Full pagination.
      "sPaginationType": "full_numbers",
      // Show processing time.
      "bProcessing": true,
      });

});





















