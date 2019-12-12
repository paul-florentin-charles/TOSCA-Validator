# Question strucutre

## For a text

We use XMLHttpRequest javascript object to send a POST request containing the typed text.
The request is initialised with the _open()_ method, whose arguments are the type of REST request and the destination address.
The form of the message is as described below, with 'txt' being the entered text, with its line breaks replaced by '\n'.

```{"data" : "' + txt + '" }```

It is then sent, using the _sent()_ method of the XMLHttpRequest object.


## For an individual YAML file

We use ajax function provided by JQuery to send a POST request containing the uploaded file.
The file is appened to a FormData object, that is send afterwards.
The form of the request is as following :

	$.ajax({
		url: '/api/validate/file', // destination address of the ajax request
		type: 'post',
		data: form, // form is a FormData object that contains the YAML file
		success: function(data) {
			// What to do on success, with the answer contained in 'data'
		}
	})


## For an archive

Similar to a unique YAML file, but with '/api/validate/archive' as the url field.