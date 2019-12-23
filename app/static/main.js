$(document).ready(function(){
    $(".update_likes")

    // like and unlike click
    $(".like, .unlike").click(function(){
        const id = this.id;   // Getting Button id
        const split_id = id.split(":");

        var like = split_id[0];
        var user_id = split_id[1];
        var blogpost_id = split_id[2];

        // Finding click type
        var type = 0;
        if (text == "like"){
            type = 1;
        }else{
            type = 0;
        }

        // AJAX Request
        var that = $(this);
        $.ajax({
            url: that.attr('action'),
            type: 'post',
            data: {postid:postid,type:type},
            dataType: 'json',
            success: function(data){
                var likes = data['likes'];
                var unlikes = data['unlikes'];

                $("#likes_"+postid).text(likes);        // setting likes
                $("#unlikes_"+postid).text(unlikes);    // setting unlikes

                if(type == 1){
                    $("#like_"+postid).css("color","#ffa449");
                    $("#unlike_"+postid).css("color","lightseagreen");
                }

                if(type == 0){
                    $("#unlike_"+postid).css("color","#ffa449");
                    $("#like_"+postid).css("color","lightseagreen");
                }


            }

        });

    });

});