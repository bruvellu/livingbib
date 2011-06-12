/* Author: 

*/

// Document ready functions.
$(document).ready(function(){

    $('.paperlist select').change(function () {
        var myform = $(this).closest('form');
        myform.submit();
    });

    $('.paperlist input').change(function () {
        var myform = $(this).closest('form');
        myform.submit();
    });

});





















