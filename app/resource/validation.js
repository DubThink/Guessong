$(function(){
   $('join').click(function(){
        $.ajax({
           data: $('form').serialize(),
            type: 'POST',
            success: function () {
                console.log("success");
            },
            error: function(){
               console.log("error");
            }
        });
   });
});

//little ajax script to test if things are working w join room