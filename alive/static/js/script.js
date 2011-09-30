/* Author: 

*/

function newSearch(redirect) {
  Dajaxice.livingbib.alive.search_taxon(Dajax.process, {'query': $("#search_query").val(), 'redirect': redirect})
}

function search_submit() {
    $("#search-results").fadeOut();
    var query = $("#id_query").val();
    $("#search-results").load(
            "/search/?query=" + encodeURIComponent(query)
            );
    // Padronize to lowercase
    var queryLower = query.toLowerCase()
    // Update browser url display.
    // https://developer.mozilla.org/en/DOM/Manipulating_the_browser_history
    var stateObj = { uquery: query };
    history.pushState(stateObj, query, "?query=" + encodeURIComponent(queryLower).replace("%20", "+"));
    return false;
}

// Document ready functions.
$(document).ready(function(){

    // Anexa a submissão do formulário com a função.
    var searchForm = $("#search-form")
    if ( searchForm.hasClass('ajax') == true ) {
      searchForm.submit(search_submit);
      }

    // Ativa o loading quando existe um Ajax call.
    $('#loading').hide()
        .ajaxStart(function() {
            $(this).fadeIn();
        })
        .ajaxStop(function() {
            $(this).fadeOut();
            $("#search-results").fadeIn('slow');
        });

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





















