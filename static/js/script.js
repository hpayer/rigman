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

