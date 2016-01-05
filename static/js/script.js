(function() {

}).call(this);


function command_click(button){
//    console.log(button.value)

    $.ajax({
        url: '/command',
//        data: $('form').serialize(),
        data: {form:$('form').serialize(), command: button.value},
        type: 'POST',
        command: button.value,
        success: function(response){
            console.log(response);
        },
        error: function(error){
            console.log(error);
        }
    });
};


function UpdateRangeText(value, id) {
    console.log(id);
    document.querySelector('#selected-' + id).value = value;
}
function UpdateRangeSlider(value, id) {
    console.log(id);
    selector = id.replace("selected-", "");
    document.querySelector('#' + selector).value = value;
}
