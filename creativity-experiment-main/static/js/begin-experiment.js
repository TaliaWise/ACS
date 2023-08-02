"use strict";


// //the get prompt button
$(document).on('click', '#promptbutton', function(e) {
  e.preventDefault();
  console.log('does this even ever run I dont think so');
  get_prompt();
});


let get_prompt = async function() {
	
	let cookies = document.cookie;
	let user_token = cookies.split("=")[1]

	 await $.post(`/get-prompt`, {

	 	user_token: user_token

	 }, function( data ) {
	 	console.log('get prompt in function data', data)
     });
}