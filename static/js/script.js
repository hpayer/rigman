(function() {

}).call(this);


function command_click(button){
    console.log(button.value)

    $.ajax({
        url: '/command',
        data: $('form').serialize(),
        type: 'POST',
        success: function(response){
            console.log(response);
        },
        error: function(error){
            console.log(error);
        }
    });
};

