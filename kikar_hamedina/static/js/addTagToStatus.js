$(document).ready(function () {
	$(".add-tag-from-list").click(function () {
		console.log("adding tag")
	});
	$(".add-tag-button").click(function () {
		console.log("adding tag")
		id = $(this).parent().data("statusid")
		tag = $(this).parent().find(".add-tag-input").val()
		$(this).parent().find(".add-tag-input").val("")
		var tags = (String(tag)).split(",")
		console.log(tag)
		console.log(tags)
		
		for (t in tags){
			url = "/add_tag_to_status/?id="+id+"&tag_str="+tags[t]

			$.ajax({
				url: url,
				contentType: "application/json",
				success: function (data) {
					console.log("GOT RESPONSE")
					console.log(data)
					if (data['success']) {
						tag = data['tag']
						console.log(tag)
						var source 		= $("#add-tag-to-status-template").html()
						var template 	= Handlebars.compile(source);
						var html    	= template(tag);
						console.log("html: " + html)
						$("#" + data['id'] + "-tags").prev().css("display","inline")
						$("#" + data['id'] + "-tags").append(html)
					}
					else {
						console.log(data)
						console.log("ERROR AT SERVER")
					}
				},
				error: function(data) {
					console.log("BADDDDD ERROR!!")
				}
			});
		}
	});
    $(".add-tag-input").keydown(function (event) {
//        $('#add-tag-dropdown').removeClass("open")
        inputText = $(".add-tag-input").val()
        id = $(this).parent().parent().data("statusid")
        url = "/search_bar/?text=" + inputText
		
        if (inputText.length > 1) {
            $.ajax({
                url: url,
                contentType: "application/json",
                success: function (data) {

                    $('#add-tag-list').html('')
//                	$('.dropdown-menu').html('')
                    for (var i = 0; i < data['number_of_results']; i++) {
                        var result = data['results'][i]
                        console.log(result)
                        if (result['type'] == "tag") {
                            var source = $("#add-tag-result-tag-list-item-template").html()
                        }
                        var template = Handlebars.compile(source);
                        var html = template(result);
                        $('#add-tag-list').append(html)
                    }
                    if (data['number_of_results'] > 0) {
                        $('#add-tag-dropdown').addClass("open")
                    }
                },
                error: function(data) {
                    console.log("BADDDDD ERROR!!")
                    console.log(data)
                }

            });
        }
    });
})
