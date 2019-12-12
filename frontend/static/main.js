/* Utilitaries */

function adapt_str_to_json(text) {
  return text.replace(/\n/g, "\\n")
             .replace(/\r/g, "\\r")
             .replace(/\t/g, "\\t")
             .replace(/"/g, '\\"');
}

function get_errors(text) {
  obj = JSON.parse(text)
  errors = obj.errors
  return errors
}

function get_error_code(number, details) {
  switch (number) {
    case 0.0:
      return "0.0 - Generic error"
    case 0.1:
      return "0.1 - No YAML file in archive"
    case 0.2:
      return "0.2 - Potentially harmful .tar"
    case 0.3:
      return "0.3 - Unsupported archive type (only .tar, .tar.gz, .tar.bz2 and .zip archives are supported)"
    case 0.4:
      return "0.4 - Generic archive error"
    case 1.0:
      return "1.0 - Wrong YAML syntax"
    case 2.0:
      return "2.0 - " + details
    case 3.11:
      return "3.11 - MISSING_REQUIREMENT_DEFINITION: The requirement is assigned but not defined"
    case 3.12:
      return "3.12 - NODE_TYPE_NOT_COHERENT: The type " + details[0] + " of the target node " + details[1] + " is not valid (as it differs from that indicated in the requirement definition)."
    case 3.13:
      return "3.13 - CAPABILITY_TYPE_NOT_COHERENT: The type of the target capability is not valid (as it differs from that indicated in the requirement definition)."
    case 3.14:
      return "3.14 - MISSING_CAPABILITY_ERROR: The target node template " + details[0] + " is not offering any capability whose type is compatible with " + details[1] + " (indicated in the requirement definition)."
    case 3.15:
      return "3.15 - RELATIONSHIP_TYPE_NOT_COHERENT: The type of the outgoing relationship is not valid (as it differs from that indicated in the requirement definition)."
    case 3.21:
      return "3.21 - CAPABILITY_VALID_TARGET_TYPE_ NOT_COHERENT: The type of the target capability " + details[0] + " is not valid (as it differs from that indicated in the definition of the type of the outgoing relationship)."
    case 3.22:
      return "3.22 - MISSING_CAPABILITY_VALID_TARGET_TYPE: The target node template " + details[0] + " is not offering any capability whose type is compatible with those indicated as valid targets for the type of the outgoing relationship."
    case 3.31:
      return "3.31 - CAPABILITY_VALID_SOURCE_TYPE_ NOT_COHERENT: The node type " + details[0] + " is not a valid source type for the capability targeted by the outgoing relationship (as it differs from those indicated in the capability type)."
    case 3.32:
      return "3.32 - CAPABILITY_DEFINITION_VALID_SOURCE_TYPE_NOT_COHERENT: The node type " + details[0] + " is not a valid source type for the capability targeted by the outgoing relationship (as it differs from those indicated in the capability definitions in the type of " + details[1] + ")."
    case 4.0:
      return "4.0 - Missing imported file : " + details[0]
    default:
      return "Unknown error"
  }
}

function change_label(file, name) {
  var labels = document.getElementsByTagName('LABEL')
  for (var i = 0; i < labels.length; i++) {
    if (labels[i].htmlFor == name) {
      labels[i].innerHTML = file.name;
      break;
    }
  }
}

function return_import(file_content) {
  if (!file_content) return []

  file_content = file_content.split("\n")
  var i = 0
  while (file_content[i] !== "imports:" && i < file_content.length) {
    i += 1
  }
  if (i == file_content.length) return []

  i += 1
  var j = 0
  files_name = new Array()
  while (file_content[i].startsWith("  -")) {
    files_name[j] = file_content[i].slice(4)
    i += 1
    j += 1
  }
  return files_name
}

function belong_to(str, array) {
  for (var i = 0; i < array.length; i++) {
    if (array[i] == str) {
      return true
    }
  }
  return false
}

/* Main functions */

function createTab(name, index, attr) {
  /* Creation of a new tab */

  // IN THE NAVBAR
  var navlist = document.getElementById('navlist')
  var navelement = document.createElement('li')
  navelement.setAttribute('class', 'nav-item ' + attr)
  var navlink = document.createElement('a')
  navlink.setAttribute('data-toggle','tab')
  navlink.setAttribute('class', 'nav-link ' + attr)
  navlink.href = '#tab' + String(index)
  navlink.setAttribute('role', 'tab')
  var text = document.createTextNode(name)
  navlink.appendChild(text)
  navelement.appendChild(navlink)
  navlist.appendChild(navelement)

  // ACTUAL TAB CONTENT
  var divresult = document.getElementById('result')
  var tab = document.createElement('div')
  tab.setAttribute('class', 'container-fluid tab-pane ' + attr)
  tab.id = 'tab' + String(index)
  var errlist = document.createElement('ul')
  errlist.setAttribute('class', 'container-fluid')
  errlist.id ='errors' + String(index)
  var prewrap = document.createElement('pre')
  var filebox = document.createElement('div')
  filebox.setAttribute('class', 'container-fluid')
  filebox.id = 'box_result_file' + String(index)
  prewrap.appendChild(filebox)
  tab.appendChild(errlist)
  tab.appendChild(prewrap)
  divresult.appendChild(tab)
}

function display_result(file_name, file_content, names, errors, index, attr) {
  createTab(file_name, index, attr)

  var imports = return_import(file_content)

  var _names = new Array(names.length)
  for (var i = 0; i < names.length; i++) {
    _names[i] = names[i].substr(names[i].indexOf('/') + 1)
  }

  var lines = file_content.split("\n")
  /* Numbering lines */
  for (var l = 0; l < lines.length; l++) {
    lines[l] = l + 1 + "    " + lines[l]
  }

  /* Adding classic errors */
  var lines_tab = new Array()
  var error_codes_tab = new Array()
  var error_details_tab = new Array()
    var cpt = 0
  for (var i = 0; i < errors.length; i++) {
      if ("lines" in errors[i]) {
	  lines_tab[cpt] = errors[i].lines
	  error_codes_tab[cpt] = errors[i].code
	  error_details_tab[cpt] = errors[i].details
	  cpt++
      } else {
	  lines_tab[cpt] = [-1]
	  error_codes_tab[cpt] = errors[i].code
	  cpt++
      }
  }

  var list = document.getElementById('errors' + String(index))

  /** Creation of the new errors **/

  /* errors list filling*/
    for (var i = 0; i < error_codes_tab.length; i++) {
	var error = document.createElement('li')
	error.id = 'err' + String(i)
	error.style["list-style-type"] = "none"
	if (error_codes_tab[i] >= 3.0 && error_codes_tab[i] < 4.0) {
	    var tmp_text = ""
	    for (var j = 0; j < lines_tab[i].length - 1; j++) {
		tmp_text += lines[lines_tab[i][j] - 1] + "\n"
	    }
	    tmp_text += lines[lines_tab[i][j] - 1]
	    var text = document.createTextNode("Sommelier error\n" + tmp_text)
	} else if (error_codes_tab[i] == 2.0) {
	    var text = document.createTextNode("TOSCA Parser Error : " + errors[i].type)
	}
	else if (error_codes_tab[i] == 1.0) {
	    var tmp_text = ""
	    for (var j = 0; j < lines_tab[i].length - 1; j++) {
		tmp_text += lines[lines_tab[i][j] - 1] + "\n"
	    }
	    tmp_text += lines[lines_tab[i][j] -1]
	    var text = document.createTextNode("Syntax error\n" + tmp_text)
	}
	else if (error_codes_tab[i] >= 0.0 && error_codes_tab[i] < 1.0) var text = document.createTextNode("Generic error")
	else var text = document.createTextNode("Unknown error")
    error.appendChild(text)
    list.appendChild(error)
    error = document.createElement('li')
    error.id = 'c-err' + String(i)
    error.style["list-style-type"] = "none"
    text = document.createTextNode(get_error_code(error_codes_tab[i], error_details_tab[i]))
    error.appendChild(text)
    list.appendChild(error)
  }

  /* Removal of -1 elements in lines_tab */
  for (var i = 0; i < lines_tab.length; i++) {
    if (lines_tab[i][0] == -1) {
      lines_tab.splice(i)
    }
  }

    /* Sorting lines into a single dimension array */
    tmp_tab = []
    cpt = 0
    for (var i = 0; i < lines_tab.length; i++) {
	for (var j = 0; j < lines_tab[i].length; j++) {
	    tmp_tab[cpt] = lines_tab[i][j] - 1
	    cpt++
	}
    }
    lines_tab = tmp_tab
    /*lines_tab.filter(function(item, i, ar) {
	return ar.indexOf(item) === i
    })*/
    lines_tab.sort(function(a, b) {
	return a - b
    })

  /* file box filling*/
  if (lines_tab.length == 0) {
    file_content = lines.slice(0, lines.length).join('<br>')
    document.getElementById('box_result_file' + String(index)).innerHTML += file_content
  } else {
    for (var i = 0; i < lines_tab.length; i++) {
      if (i == 0) {
        file_content = lines.slice(0, lines_tab[i]).join('<br>')
        document.getElementById('box_result_file' + String(index)).innerHTML += file_content
      } else {
        file_content = lines.slice(lines_tab[i - 1] + 1, lines_tab[i]).join('<br>')
        document.getElementById('box_result_file'+ String(index)).innerHTML += file_content
      }
      document.getElementById('box_result_file' + String(index)).innerHTML += '<br><span id="highlight">' + lines[lines_tab[i]] + '</span>'
    }
    file_content = lines.slice(lines_tab[i - 1] + 1, lines.length).join('<br>')
    document.getElementById('box_result_file' + String(index)).innerHTML += file_content
  }
}

function display_archive_result(data) {
  /* Resetting the boxes */
  if (document.getElementById('result')) document.getElementById('result').innerHTML = null
  if (document.getElementById('navlist')) document.getElementById('navlist').innerHTML = null

  /* Parsing the data */
  obj = JSON.parse(data)
  files = obj.files

  /* Filling names array with all the files contained in the archive*/
  names = []
  for (var i = 0; i < files.length; i++) {
    names[i] = files[i].name
  }

  /* Displaying errors */
  if (files[0].result.valid) display_result(files[0].name, files[0].content, names, [], 0, 'active valid')
  else display_result(files[0].name, files[0].content, names, files[0].result.errors, 0, 'active unvalid')
  for (var i = 1; i < files.length; i++) {
    if (files[i].result.valid) display_result(files[i].name, files[i].content, names, [], i, 'valid')
    else display_result(files[i].name, files[i].content, names, files[i].result.errors, i, 'unvalid')
  }
}

function submit_text(text) {
  var xhttp = new XMLHttpRequest()
  xhttp.open("POST", "api/validate/text", true)
  xhttp.setRequestHeader("Content-type", "application/json")

  xhttp.onreadystatechange = function() { //Call a function when the state changes.
    if(xhttp.readyState == 4) {
      /* Resetting the boxes */
      if (document.getElementById('result')) document.getElementById('result').innerHTML = null
      if (document.getElementById('navlist')) document.getElementById('navlist').innerHTML = null

      /* Create the error tab and fill it */
      if (JSON.parse(xhttp.responseText).valid) display_result("File submitted through the text box", text, [], [], 0, 'active valid')
      else display_result("File submitted through the text box", text, [], get_errors(xhttp.responseText), 0, 'active unvalid')
    }
  }

  txt = adapt_str_to_json(text)
  xhttp.send('{"data" : "' + txt + '" }')
}

function submit_file(file) {
  /* File reader */
  var reader = new FileReader()
  reader.readAsText(file, "UTF-8")

  /* File */
  var formData = new FormData()
  formData.append('file', file)

  /* Called when the reading is done */
  reader.onloadend = function() {
    /* Sends the file directly */
    $.ajax({
      url: '/api/validate/file',
      type: 'post',
      data: formData,
      processData: false,
      contentType: false,
      success: function(data) {
        /* Resetting the boxes */
        if (document.getElementById('result')) document.getElementById('result').innerHTML = null
        if (document.getElementById('navlist')) document.getElementById('navlist').innerHTML = null

        /* Create the error tab and fill it */
        if (JSON.parse(data).valid) display_result(file.name, reader.result, [], [], 0, 'active valid')
        else display_result(file.name, reader.result, [], get_errors(data), 0, 'active unvalid')
      }
    })
  }
}

function submit_archive(archive) {
  /* Archive */
  var formData = new FormData()
  formData.append('file', archive)

  /* Sends the archive */
  $.ajax({
    url: '/api/validate/archive',
    type: 'post',
    data: formData,
    processData: false,
    contentType: false,
    success: function(data) {
      display_archive_result(data)
    }
  })
}
