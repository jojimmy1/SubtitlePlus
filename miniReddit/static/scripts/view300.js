$(document).ready(function() { 
		$('#{{pagenum}}').attr("class", "active");
		$('#hi1{{key[1]}}').on('submit',function(event) { 
			$.ajax({
			data : {
				userid : $('#id11{{key[1]}}').val(),
				count1 : $('#count11{{key[1]}}').val(),
				postid : $('#post11{{key[1]}}').val()
			},
			type : 'POST',
			url : '/vote'
		})
		.done(function(data) {

			if (data.error) {
				alert("You have alreday voted.")
			}
			else {
				$("#vote00{{key[1]}}").text(data.count);
			}
		});

		event.preventDefault();
	}); 
		$('#hi2{{key[1]}}').on('submit',function(event) { 
			$.ajax({
			data : {
				userid : $('#id22{{key[1]}}').val(),
				count1 : $('#count22{{key[1]}}').val(),
				postid : $('#post22{{key[1]}}').val()
			},
			type : 'POST',
			url : '/vote'
		})
		.done(function(data) {

			if (data.error) {
				alert("You have alreday voted.")
			}
			else {
				$("#vote00{{key[1]}}").text(data.count);
			}
		});

		event.preventDefault();
	});
}); 