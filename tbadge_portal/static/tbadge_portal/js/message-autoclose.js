/**
 * Created by Lawrence.Ouyang on 8/30/2016.
 */
$(function() {
    $('#message-close').on("click", function() {
        $('.alert-message').animate({"height": 0, "padding-top": 0, "padding-bottom": 0}, 500);
        setTimeout(function() {
            $('.alert-message').remove();
        }, 500);
    });

    if ($('.alert-message').length) {
        setTimeout(function() {
            $('.alert-message').animate({"height": 0, "padding-top": 0, "padding-bottom": 0}, 500);}, 4000);
        setTimeout(function () {
            $('.alert-message').remove();}, 4500);
    }
});