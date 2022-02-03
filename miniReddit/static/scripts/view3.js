$(document).ready(function() { 
		$('form').on('submit',function(event) { 
			prompt("You have alreday voted.")
			$.ajax({
			data : {
				userid : $('#userid').val(),
				count1 : $('#count1').val(),
				post1 : $('#postid').val()
			},
			type : 'POST',
			url : '/vote'
		})
		.done(function(data) {

			if (data.error) {
				prompt("You have alreday voted.")
			}
			else {
				$("#vote00").text(data.count);
		});

		event.preventDefault();
	}); 
}); 