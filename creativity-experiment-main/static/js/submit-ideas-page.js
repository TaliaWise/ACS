"use strict";

// Because this page utilizses jquery, it needs to be called after where the jquery is loaded in the html.

// This code is what controls the page. It's where you chase most of your geese.


//the submit idea button 
// When the form is submited, we try to send the data to the backend to be processed.
$(document).on('submit', '#wf-form-submit-idea-form', function(e) {
  e.preventDefault();
  console.log('The form was submitted.');
  function_you_want_to_run();
});


//hides the button until after the user gets a prompt
$(document).ready(function(){
    $("#finishbutton").hide();

});


function get_user_token(cookies) {
  cookies = cookies.split(";");
	let user_token = ''
  for (const c in cookies) {
    if (cookies[c].split("=")[0].includes("user_token")) {
      user_token = cookies[c].split("=")[1]
    }
  }
	return user_token
}

// $(document).on('click', '#submit_idea_button', function(){
//     function_you_want_to_run();
// });

let function_you_want_to_run = async function() {

	//from front end
	var submitted_idea = $('#new_idea').val();

	//get this from backend??
	let cookies = document.cookie;
	//console.log(cookies)
	let user_token = get_user_token(cookies)
	//let user_token = cookies.split("=")[1].split(';')[0]
	//console.log(getCookie(cookies))
	//var user_id = 123;


	//get start time of writing idea and delete cookie
	let start_time_cookie = cookies.split(";")[1]
	let start_time = ''
	
	if (start_time_cookie != undefined) {
		start_time = start_time_cookie.split("=")[1]

		//delete cookie
		document.cookie = encodeURIComponent('entered_text') + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT"
	}


	//empties the textbox after the idea was submitted
	$('#new_idea').val('');

	//appends idea to submitted ideas table
	$('#the_table').append("<div class=\"row\"><div class=\"row-text\">" + submitted_idea + "</div></div>");
	//sends to back end in submit idea route
     await $.post(`/submit-idea`, {
     	submitted_idea: submitted_idea,
     	user_token: user_token,
     	start_time: start_time
   		
	 }, function( data ) {
	 	console.log('some data here in line 33 submit ideas js', data)
     });
}


// //the get prompt button
$(document).on('click', '#promptbutton', function(e) {
  e.preventDefault();
  console.log('asked for prompt');
  get_prompt();
});


let get_prompt = async function() {
	
	let cookies = document.cookie;
	let user_token = get_user_token(cookies)
	//let user_token = cookies.split("=")[1].split(';')[0]
	$('#the_prompts').empty().append("<div class='idea-help'>" + 'The prompts will be shown here in a moment...' + "</div>")

	 await $.post(`/get-prompt`, {
	 	user_token: user_token

	 }, function( data ) {
	 	console.log('get prompt in function data', data)
	 	let prompts_words = data

	 	if (data == 'You have not submitted any ideas. Are you sure you already want a hint?'){
			alert('You have not submitted any ideas. Please add and submit at least one creative alternative use idea.')
		}
		else {
			if (data == "If you ran out of ideas again, please click on 'I am completely out of ideas'") {
	  		   $('#the_prompts').empty().append("<div class='idea-help'>" + data + "</div>")
			
			} 
			
			else if (data == 'No word suggestions could be found'){
				$('#the_prompts').empty().append("<div class='idea-help-title'>" + data + "</div><div class='idea-help'></div>")
			}
			else {
	  			$('#the_prompts').empty().append("<div class='idea-help-title'>" + data + "</div><div class='idea-help'>might help you come up with new ideas</div>")
			}
			$("#finishbutton").show();
			$("#promptbutton").hide();
		}
	 		
     });  
}



// finish experiment i guess...
$(document).on('click', '#finishbutton', function(e) {
  e.preventDefault();
  console.log('finished experiment run');
  //finish();
  window.location = "/done"
});


let finish = async function() {
	
	let cookies = document.cookie;
	let user_token = get_user_token(cookies)
	//let user_token = cookies.split("=")[1].split(';')[0]

	 await $.get(`/finished`, {
	 	user_token: user_token
	 });
}



$('textarea').keyup( function (e) { 
	e.preventDefault();

	if(e.which == 13) {
        alert("To enter an idea, please click on the 'Submit idea' button.");
    }
    if (e.code == 'Period') {
    	alert("To enter an idea, please click on the 'Submit idea' button. Please submit each idea one at a time with the button, there is no need for a period at the end.");
    }
	//console.log(e.key, e.code);
	console.log(e.code);
	let val = e.code;
    text_area(val);
});

let text_area = async function(v) {
	let cookies = document.cookie;
	let user_token = get_user_token(cookies)
	console.log('user token', user_token);

	console.log(v, 'is v');

	await $.post('/text_area_input', {
		val: v
	}, function( data ) {
	 	console.log('some data here in line 133 text area input js', data)
	 });
}


$('textarea').on('focus', function(e) {
	console.log('focused')
	text_area_focus();
});


let text_area_focus = async function(e) {
	let cookies = document.cookie;
	let user_token = get_user_token(cookies)

	//let user_token = cookies.split("=")[1].split(';')[0];
	console.log('user token', user_token);

	await $.post('/text_area_focus', {
		val: 'focus'
	},function( data ) {
	 	console.log('some data here in line 151 text area input js', data)
	 });
}



//detect change in submit idea text on input (only works in certain versions::: check which versions)
/*
$('textarea').on('input', function(e) {
	console.log('text changed')
  	e.preventDefault();

  	let cookies = document.cookie;
  	//let entered_text_cookie = new Promise(get_correct_cookie(cookies, 'entered_text').then(meta => {
  	//	console.log('in get correct cookie')
  	//	entered_text_cookie = meta;
  	// }) => {});
  	

  	//let entered_text_cookie = get_correct_cookie(cookies, 'entered_text')



  	console.log('first' + entered_text_cookie)

  	if (entered_text_cookie != undefined) {
  		// found one: do nothing
  		console.log('not undefined')
  	}
  	else {
  		//if it is undefined add a cookie
  		console.log('none found')
  		on_text_input();
  	}
});


let on_text_input = async function() {

 await $.post(`/get-time`, {
 		data :'data'

	 }, function( data ) {
	 	//adds the cookie
	 	console.log('in data')
	 	console.log('data' + data)
	 	document.cookie = "entered_text=" + data;
     });
}


// detect focus on textarea
$('textarea').on('focus', function(e) {
    	console.log('focused')
  		e.preventDefault();

  		let cookies = document.cookie;

  		console.log(cookies)
  		let entered_text_cookie = get_correct_cookie(cookies, 'clicked_on_textarea')

  		console.log('read' + readCookie('entered_text'))

  		//let entered_text_cookie = cookies.split(";")[1]
  		//find the right one:


  		console.log('first' + entered_text_cookie)

  		if (entered_text_cookie != undefined) {
  			// found one: do nothing
  			console.log('not undefined')
  		}
  		else {
  			//if it is undefined add a cookie
  			console.log('none found')
  			on_focus();
  	}
});



let get_correct_cookie = async function(cookies, name) {
	let list_cookies = cookies.split(";")
	let cookie = '';
	for (const x of list_cookies) { 
		console.log(x); 
		let n = x.split("=");
		console.log('n is' + n);
		console.log('name' + name);

			if (n[0].trim() == name) {
				cookie = n;
				console.log('cookie' + cookie)
			}
		}
	return cookie
}


function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}



let on_focus = async function() {

 await $.post(`/get-time`, {
 		data :'data'

	 }, function( data ) {
	 	//adds the cookie
	 	console.log('in data')
	 	console.log('data' + data)
	 	document.cookie = "clicked_on_textarea=" + data;
     });
}
*/

// #maybe can save cookie with start time of text area then send to back end at submit :) and update on next change...
// #if it already exists then do nothing, if none exists then add the cookie, if submit then send first time with submit + delete the cookie
// #if no new idea since 









