/* Author: 

*/

function searchTaxon(redirect) {
  $("#dark-loading").fadeIn();
  $("#search-results").fadeOut();
  var query = $("#search_query").val()
  Dajaxice.livingbib.alive.search_taxon(Dajax.process, {'query': query, 'redirect': redirect})
  return false
}

function endSearch(query) {
  // Update browser url display.
  // https://developer.mozilla.org/en/DOM/Manipulating_the_browser_history
  var stateObj = { uquery: query };
  history.pushState(stateObj, query, "?query=" + encodeURIComponent(query).replace("%20", "+"));
  $("#search-results").fadeIn();
  $("#dark-loading").fadeOut();
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
      // ThemeRoller.
      //"bJQueryUI": true,
      // Save the state of the table.
      // "bStateSave": true,
      });

    $('#reference-list select').change(function () {
        var myform = $(this).closest('form');
        myform.submit();
    });

    $('#reference-list input').change(function () {
        var myform = $(this).closest('form');
        myform.submit();
    });

});





















