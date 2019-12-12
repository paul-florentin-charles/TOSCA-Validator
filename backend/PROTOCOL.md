# Protocol to communicate with the TOSCA validator back-end

The back-end of the TOSCA validator exposes a RESTful API (default route for the API : _/api/validate_).
The following endpoints are exposed :
* Validation request for a string containing the content of the file (default route : _/text_).
* Validation request for a single TOSCA file (default route : _/file_).
* Validation request for an archive containing several TOSCA files (default route : _/archive_).

## Question structure
All validation requests are POST requests (*data* for text validation, and *files* for file/archive validation) at specific endpoints of the back-end API. The following sections show 

### For a text
The format of a request for a text is straightforward  :

    {"data" : string }

The string contains the content of the TOSCA file that will be analysed.

### For an individual YAML file
For a YAML file validation, the sent request is simple too :

    {"file" : file}

The TOSCA file is sent in place of *file*, and will be validated.

### For an archive
The structure is the same as with the file validation request, but an archive is sent. The app knows wether it's a YAML file or an archive depending in the endpoint at which the request is received.

## Answer structure

### For a single file input (or a string containing a file)

When you ask for the validation of a single TOSCA file, you get an answer with the following structure :

    {
	  "valid": bool,
	  "errors": list[object]
    }

* The attribute **valid** is *true* if the parsed TOSCA file is valid, *false* otherwise.
* The attribute **errors** contains a list of errors found in the TOSCA file, if it is not valid. If the file is valid, there will be no attribute **errors**.

An error object has the following structure :

    {
	  "code": float,
	  ...
	}

* The attribute **code** contains the code of the error. Error codes will be discussed later in this document.
* The error object may contain many other attributes, but their presence depend on the error code.


### For an archive input
The structure of the answer for an archive containing several files is slightly different from the answer for a single file :

	{
	  "valid": bool,
	  "errors": list[object]
	  "files": list[{"name": string, "result": object}]
    }

* The attribute **valid** is *true* if the archive was successfuly analysed and all parsed TOSCA files in it are valid, *false* otherwise.
* The attribute **errors** is only present if **valid** is *false*. It contains errors linked to the archive (not the files in it). For example, if the archive is invalid or of an unsupported type, the resulting errors will be there.
* The attribute **files** is only present if **errors** is empty (if the archive was successfully opened and analysed). It contains a list of individual answers for the files found in the archive, alongside with their names.


### Error codes

Error codes are floats representing the errors. The integer part of the number is the class of the error :

* `0.*` : internal or unknown errors.
* `1.*` : YAML syntax errors.
* `2.*` : errors raised by OpenStack's TOSCA parser.
* `3.*` : errors returned by Sommelier.

#### Internal errors (0.*)

These error codes refer to errors not related with YAML or TOSCA parsing.

* `0.0`  : _Generic error_ - Something went wrong internally... (It's not supposed to happen).
* `0.1`  : _Bad request error_ - The request was bad or empty (for example, sending an archive validation request to the file end point).
* `0.2`  : _Generic file/text error_ - Something went wrong while trying to deal with the file/text...
* `0.3`  : _Generic archive error_ - Something went wrong while trying to deal with the archive (the archive might be corrupted..?).
* `0.31` : _No file in archive_ - No YAML file has been found in a sent archive.
* `0.32` : _Potentially harmful .tar_- The sent _.tar_ archive may be harmful (for example, contains files with paths including **..** or starting with **/**).
* `0.33` : _Unsupported archive type_ -  The sent archive is of an unsupported type (only .tar, .tar.gz, .tar.bz2 and .zip archives are supported).


#### YAML syntax errors (1.*)

There is only the `1.0` error. It means that the provided file has a wrong YAML syntax. The **error** object may contain a `"lines"` field containing a list of lines involved in the error (possibly empty).

#### OpenStack errors (2.*)

Currently, there is only the `2.0` error : an error returned by OpenStack's TOSCA parser. However, the **error** object also contains much more information about the error in the following fields :
* `"type"`   : A more precise error name, for example "ImportError"
* `"details"`: Details about the error, for exemple "Import of example.yaml has failed."
* `"lines"`  : A list of lines in which the error may be located

**NB : The list of lines returned is less accurate than with the other error types. Some invalid lines may be missing. It's unlikely but possible that some given lines contain no error too.**


#### Sommelier errors (3.*)

**error** objects conaining an error code from Sommelier contain the following fields :

* `"lines"`  : The lines involved in the error.
* `"node"`   : The node which contains the error.
* `"req"`    : The requirement that hasn't been fulfilled.
* `"details"`: It is a list of strings in which details related to the error may be found, see below in description of errors.

The sub-codes (digits after the floating point) correspond to the error codes returned by Sommelier :
* `3.11`: _MISSING REQUIREMENT DEFINITION_ - The requirement is assigned but not defined.
* `3.12`: _NODE TYPE NOT COHERENT_ - The type **details[0]** of the target node **details[1]** is not valid (as it differs from that indicated in the requirement definition).
* `3.13`: _CAPABILITY TYPE NOT COHERENT_ - The type of the target capability is not valid (as it differs from that indicated in the requirement definition).
* `3.14`: _MISSING CAPABILITY ERROR_ - The target node template **details[0]** is not offering any capability whose type is compatible with **details[1]** (indicated in the requirement definition).
* `3.15`: _RELATIONSHIP TYPE NOT COHERENT_ - The type of the outgoing relationship is not valid (as it differs from that indicated in the requirement definition).
* `3.21`: _CAPABILITY VALID TARGET TYPE NOT COHERENT_ - The type of the target capability **details[0]** is not valid (as it differs from that indicated in the definition of the type of the outgoing relationship).
* `3.22`: _MISSING CAPABILITY VALID TARGET TYPE_ - The target node template **details[0]** is not offering any capability whose type is compatible with those indicated as valid targets for the type of the outgoing relationship
* `3.31`: _CAPABILITY VALID SOURCE TYPE NOT COHERENT_ - The node type **details[0]** is not a valid source type for the capability targeted by the outgoing relationship (as it differs from those indicated in the capability type).
* `3.32`: _CAPABILITY DEFINITION VALID SOURCE TYPE NOT COHERENT_ - The node type **details[0]** is not a valid source type for the capability targeted by the outgoing relationship (as it differs from those indicated in the capability definitions in the type of **details[1]**).
