var family = getCookie('family');
var user = getCookie('user');

function clearLocations() {
  var locationListContainer = document.getElementById("location-list");
  locationListContainer.innerHTML = '';
}

function getLocations() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/n/" + family + "/" + user + "/getsettings", true);
  xhr.onload  = function() {
    var locationListContainer = document.getElementById("location-list");
    clearLocations();

    var jsonResponse = JSON.parse(xhr.responseText);
    if (jsonResponse['regions'] !== null) {
      for (var i = 0; i < jsonResponse['regions'].length; i++) {
        var locationPreference = document.createElement('button');
        locationPreference.classList.add('btn');
        locationPreference.classList.add('btn-primary');
        locationPreference.classList.add('mr-1');
        var regionValue = jsonResponse['regions'][i];
        locationPreference.value = jsonResponse['regions'][i];
        locationPreference.innerText = jsonResponse['regions'][i] + ' ';
        locationPreference.onclick = function () { removeLocation(this); };
        locationPreference.classList.add('locationPreference');
        var removeElement = document.createElement("i");
        removeElement.classList.add("fas");
        removeElement.classList.add("fa-times-circle");
        locationPreference.appendChild(removeElement);
        locationListContainer.appendChild(locationPreference);
      }
    }
  };
  xhr.send(null);
}

function addLocation() {
  var dropdownLocationsList = document.getElementById("dropdownFocusLocations");
  var optionValue = dropdownLocationsList.options[dropdownLocationsList.selectedIndex].value;
  var optionText = dropdownLocationsList.options[dropdownLocationsList.selectedIndex].text;
  dropdownLocationsList.selectedIndex = "0";
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/n/" + family + "/" + user + "/setsettings");
  xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
  jsonPostData = {
    'settingname': 'addregion',
    'settingvalue': optionValue
  };
  xhr.send(JSON.stringify(jsonPostData));
  xhr.onload  = function() {
    getLocations();
  };
}

function removeLocation(button) {
  var locationToRemove = button.value;

  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/n/" + family + "/" + user + "/setsettings");
  xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
  jsonPostData = {
    'settingname': 'removeregion',
    'settingvalue': locationToRemove
  };
  xhr.send(JSON.stringify(jsonPostData));
  xhr.onload  = function() {
    getLocations();
  }
}

window.addEventListener('load', function() {
  var copyprojecturl = document.getElementById("copy-project-url");
  copyprojecturl.addEventListener('click', function () {
    var copyText = document.getElementById("project-url");

    /* Select the text field */
    copyText.select();

    /* Copy the text inside the text field */
    document.execCommand("copy");
  });

  var req = new XMLHttpRequest();
  req.overrideMimeType("application/json");
  req.open('GET', '/static/data/regions.json', true);
  req.onload  = function() {
     var jsonResponse = JSON.parse(req.responseText);

     var dropdownLocationsList = document.getElementById("dropdownFocusLocations");
     dropdownLocationsList.innerHTML = '<option>Focus on popular names in ...</option>';
     for (var regionName in jsonResponse) {
        if (jsonResponse.hasOwnProperty(regionName)) {
          var locationDropdownElement = document.createElement("option");
          locationDropdownElement.innerText = regionName;
          locationDropdownElement.value = jsonResponse[regionName].key;
          dropdownLocationsList.appendChild(locationDropdownElement);
        }
     }
  };
  req.send(null);

  getLocations();

  var malefemaleslider = document.getElementById("malefemaleprob");

  malefemaleslider.oninput = function() {
    var jsonPostData = { 'settingname': 'malefemaleprob', 'settingvalue': this.value };

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/n/" + family + "/" + user + "/setsettings");
    xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
    xhr.send(JSON.stringify(jsonPostData));
  }
}, false);
