(function() {

}).call(this);


function command_click(button){
//    console.log(button.value)

    $.ajax({
        url: '/command',
        data: {form:$('form').serialize(), command: button.value},
        type: 'POST',
        command: button.value,
        success: function(response){
            var command = button.value
            if (command == 'open') {
                response = JSON.parse(response);
                console.log(response);
                $.each(response, function(field_name, value){
                    var field  = document.getElementsByName(field_name)[0];
                    field.value = value;
                    }
                )
            }
            if (command == 'save'){
                console.log('save')
            }

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


$("#camera_config-camera_config").change(function() {
    var config_name = $(this).find(":selected").val();
//    console.log(config_name)
//    $("#config_name").attr("placeholder", config_name)
    $("#config_name").attr("value", config_name)
    $("#delete_config_name").attr("value", config_name)
});
