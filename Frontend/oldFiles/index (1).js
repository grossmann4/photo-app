
window.SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition

function voiceSearch(){
    if ('SpeechRecognition' in window) {
        console.log("SpeechRecognition is Working");
        let final_transcript = "";
        let speechRecognition = new window.SpeechRecognition();
        speechRecognition.continuous = true;
        speechRecognition.interimResults = true;
        

        speechRecognition.onstart = () => {
            // Show the Status Element
            console.log("here");
            document.querySelector("#status").style.display = "block";
        };
        speechRecognition.onerror = () => {
            // Hide the Status Element
            console.log("error");
            document.querySelector("#status").style.display = "none";
        };
        speechRecognition.onend = () => {
            // Hide the Status Element
            console.log("there");
            document.querySelector("#status").style.display = "none";
        };

        speechRecognition.onresult = (event) => {
            // Create the interim transcript string locally because we don't want it to persist like final transcript
            let interim_transcript = "";
        
            // Loop through the results from the speech recognition object.
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                // If the result item is Final, add it to Final Transcript, Else add it to Interim transcript
                if (event.results[i].isFinal) {
                final_transcript += event.results[i][0].transcript;
                } else {
                interim_transcript += event.results[i][0].transcript;
                }
            }
        
            // Set the Final transcript and Interim transcript.
            document.querySelector("#search_query").value = final_transcript;
            var t = document.getElementById('search_query').value;
            console.log("val: " + t);
            //document.querySelector("#interim").innerHTML = interim_transcript;
        };
    
        // Set the onClick property of the start button
        document.querySelector("#start").onclick = () => {
        // Start the Speech Recognition
        speechRecognition.start();
        console.log("starting");
        };
        // Set the onClick property of the stop button
        document.querySelector("#stop").onclick = () => {
        // Stop the Speech Recognition
        speechRecognition.stop();
        console.log("stopping");
        };


    } else {
        console.log("SpeechRecognition is Not Working");
    }

}

function textSearch() {
    var searchText = document.getElementById('search_query');
    if (!searchText.value) {
        alert('Please enter a valid text or voice input!');
    } else {
        searchText = searchText.value.trim().toLowerCase();
        console.log('Searching Photos....');
        searchPhotos(searchText);
    }
    
}

function searchPhotos(searchText) {

    console.log(searchText);
    document.getElementById('search_query').value = searchText;
    document.getElementById('photos_search_results').innerHTML = "<h4 style=\"text-align:center\">";

    var params = {
        'q' : searchText
    };
    
    var body = {
        'Content-Type': 'application/json'
    }
    sdk.searchGet(params, params, body)
        .then(function(result) {
            console.log("Result : ", result);
            image_paths = result["data"];
            console.log("image_paths : ", image_paths);
            var photosDiv = document.getElementById("photos_search_results");
            photosDiv.innerHTML = "";

            var n;
            for (n = 0; n < image_paths.length; n++) {
                images_list = image_paths[n].split('/');
                imageName = images_list[images_list.length - 1];

                photosDiv.innerHTML += '<figure><img src="' + image_paths[n] + '" style="width:25%"><figcaption>' + imageName + '</figcaption></figure>';
            }

        }).catch(function(result) {
            console.log(result);
        });
}

function uploadPhoto() {
    var filePath = (document.getElementById('uploaded_file').value).split("\\");
    var fileName = filePath[filePath.length - 1];
    
    if (!document.getElementById('custom_labels').innerText == "") {
        var customLabels = document.getElementById('custom_labels');
    }
    console.log(fileName);
    console.log(custom_labels.value);

    var reader = new FileReader();
    var file = document.getElementById('uploaded_file').files[0];
    console.log('File : ', file);
    document.getElementById('uploaded_file').value = "";

    if ((file['name'] == "") || (!['png', 'jpg', 'jpeg'].includes(file['name'].split(".")[1]))) {
        alert("Please upload a valid .png/.jpg/.jpeg file!");
    } else {

        var params = {};
        var additionalParams = {
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': file.type
            }
        };
        
        reader.onload = function (event) {
            body = btoa(event.target.result);
            console.log('Reader body : ', body);
            return sdk.uploadPut(params, additionalParams)
            .then(function(result) {
                console.log(result);
            })
            .catch(function(error) {
                console.log(error);
            })
        }
        reader.readAsBinaryString(file);
    }
}
