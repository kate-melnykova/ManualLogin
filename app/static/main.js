$(document).ready(function(){
    $(".post-like").click(function(event){
        console.log('Inside jQuery')
        var span = $(this);
        var href = span.parent().attr('href');
        var like_id = href.split('=');
        like_id = like_id[like_id.length - 1];
        var split_id = like_id.split('_');
        const text = split_id[0];
        if (text === 'like'){
            let type = 1;
        } else {
            let type = -1;
        }
        const blogpost_id = split_id[2];
        event.preventDefault();
        $.ajax({
            url: span.parent().attr('href'),
            success: function(){
                let cur_likes = $("#like_count:"+blogpost_id | string).text();
                cur_likes = parseInt(cur_likes) + type;
                $("#like_count:"+blogpost_id).html(likes);
            },
            error: function(response, error){
            }

        })
        event.preventDefault();
    });

});