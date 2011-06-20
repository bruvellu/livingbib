/* Author: 

*/

// Document ready functions.
$(document).ready(function(){

    $('#reference-list select').change(function () {
        var myform = $(this).closest('form');
        myform.submit();
    });

    $('#reference-list input').change(function () {
        var myform = $(this).closest('form');
        myform.submit();
    });

});





















