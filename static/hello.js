/*
 * http://stackoverflow.com/questions/18260815/use-gapi-client-javascript-to-execute-my-custom-google-api
 * https://developers.google.com/appengine/docs/java/endpoints/consume_js
 * https://developers.google.com/api-client-library/javascript/reference/referencedocs#gapiclientload
 *
 */

/**
 * After the client library has loaded, this init() function is called.
 * The init() function loads the helloworldendpoints API.
 */

function init() {

	// You need to pass the root path when you load your API
	// otherwise calls to execute the API run into a problem

	// rootpath will evaulate to either of these, depending on where the app is running:
	// //localhost:8080/_ah/api
	// //your-app-id/_ah/api

	var rootpath = "//" + window.location.host + "/_ah/api";

	// Load the helloworldendpoints API
	// If loading completes successfully, call loadCallback function
	gapi.client.load('helloworldendpoints', 'v1', loadCallback, rootpath);
}

/*
 * When helloworldendpoints API has loaded, this callback is called.
 *
 * We need to wait until the helloworldendpoints API has loaded to
 * enable the actions for the buttons in index.html,
 * because the buttons call functions in the helloworldendpoints API
 */
function loadCallback () {
	// Enable the button actions
	enableButtons ();
}

function enableButtons () {
	// Set the onclick action
	btn = document.getElementById("input_greet_generically");
	btn.onclick= function(){greetGenerically();};
	// Update the button label now that the button is active
	btn.value="Click me for a generic greeting";

	// Set the onclick action
	btn = document.getElementById("input_greet_by_name");
	btn.onclick=function(){greetByName();};
	// Update the button label now that the button is active
	btn.value="Click me for a personal greeting";

	// Set the onclick action
	btn = document.getElementById("create_user");
	btn.onclick=function(){testNewUser();};
	// Update the button label now that the button is active
	btn.value="Test new_user";

	// Set the onclick action
	btn = document.getElementById("add_data");
	btn.onclick=function(){testAddData();};
	// Update the button label now that the button is active
	btn.value="Test add_data";

	// Set the onclick action
	btn = document.getElementById("new_game");
	btn.onclick=function(){testNewGame();};
	// Update the button label now that the button is active
	btn.value="Test new_game";

}

function testNewGame () {

	newGameRequest = {
		'sayer_category': 'ACTOR',
		'num_hints': 3,
		'user_name': 'cskomra'
	}
	endpoint = gapi.client.helloworldendpoints

	var request = endpoint.new_game(newGameRequest);
	console.log(request);

	request.execute(theCallback);
}

function testAddData () {

	addData = {
		'sayer_category': 'ENTREPRENEUR',
		'sayer': 'Peter Thiel',
		'saying': 'A great company is a consipiracy to change the world.',
		'hints': "2014^^Business^^Male^^Zero to One^^PT"
	}
	endpoint = gapi.client.helloworldendpoints

	var request = endpoint.add_data(addData);
	console.log(request);

	request.execute(theCallback);
}

function greetGenerically () {
	// Construct the request for the sayHello() function
	var request = gapi.client.helloworldendpoints.sayHello();

	// Execute the request.
	// On success, pass the response to sayHelloCallback()
	request.execute(sayHelloCallback);
}

function greetByName () {
	// Get the name from the name_field element
	var name = document.getElementById("name_field").value;

	// Call the sayHelloByName() function.
	// It takes one argument "name"
	// On success, pass the response to sayHelloCallback()
	var request = gapi.client.helloworldendpoints.sayHelloByName({'name': name});
	request.execute(sayHelloCallback);
}

function testNewUser () {

	newUserRequest = {
		'user_name': 'cskomra',
		'email': 'connie@cskomra.com'
	}

	endpoint = gapi.client.helloworldendpoints
	var request = endpoint.create_user(newUserRequest);
	console.log(request);

	request.execute(theCallback);
}

// Process the JSON response
// In this case, just show an alert dialog box
// displaying the value of the message field in the response
function sayHelloCallback (response) {
	alert(response.greeting);
}

function theCallback(response){
	console.log(response);
	alert("Done!")
}



