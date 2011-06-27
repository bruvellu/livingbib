/* Author: 

*/

function search_submit() {
    var query = $("#id_query").val();
    $("#search-results").load(
            "/search/?query=" + encodeURIComponent(query)
            );
    // Update browser url display.
    // https://developer.mozilla.org/en/DOM/Manipulating_the_browser_history
    var stateObj = { uquery: query };
    history.pushState(stateObj, query, "?query=" + encodeURIComponent(query).replace("%20", "+"))
    return false;
}


// Document ready functions.
$(document).ready(function(){

    // Anexa a submissão do formulário com a função.
    $("#search-page #search-form").submit(search_submit);

    // Ativa o loading quando existe um Ajax call.
    $('#loading').hide()
        .ajaxStart(function() {
            $(this).fadeIn();
        })
        .ajaxStop(function() {
            $(this).fadeOut();
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





















