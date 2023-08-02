
"use strict";

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


$(document).on('click', '#continuebutton', function(e) {
  e.preventDefault();
  direct()
});


let direct = async function() {
console.log('continue please');
  let cookies = document.cookie;
  console.log(cookies)
  let user_token = get_user_token(cookies)
  let qualtrics_url = 'https://technioniit.eu.qualtrics.com/jfe/form/SV_7WhYIIUkDGoHgCa?prolific_id=' + user_token
  window.location.href = qualtrics_url;
}


