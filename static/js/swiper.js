function getNextName(jsonPostData) {
  var family = getCookie('family');
  var user = getCookie('user');
  var xhr = new XMLHttpRequest();
  if (typeof jsonPostData !== 'undefined') {
    xhr.open("POST", "/n/" + family + "/" + user + "/nextname");
    xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
    xhr.send(JSON.stringify(jsonPostData));
  } else {
    xhr.open("GET", "/n/" + family + "/" + user + "/nextname");
    xhr.send();
  }

  xhr.onload = function () {
    var data = JSON.parse(xhr.responseText);

    var nameCardContainerElement = document.getElementById("namecardcontainer");
    var nameCardElement = document.createElement("div");
    nameCardElement.classList.add("namecard");
    nameCardElement.innerHTML = '<div class="name-title">' + data.name + '</div>';
    nameCardContainerElement.appendChild(nameCardElement);

    if (data.male_probability > 70) {
      nameCardElement.classList.add('male-card');
    }
    else if (data.female_probability > 70) {
      nameCardElement.classList.add('female-card');
    }
    else  {
      nameCardElement.classList.add('neutral-card');
    }

    if (data.origins) {
      var nameOriginsElement = document.createElement("div");
      nameOriginsElement.classList.add('name-origin');
      nameOriginsElement.innerHTML = '<u>Origin</u>: ' + data.origins.join(', ');
      nameCardElement.appendChild(nameOriginsElement);
    }
    if (data.description) {
      var nameDescriptionElement = document.createElement("div");
      nameDescriptionElement.classList.add('name-description');
      nameDescriptionElement.innerText = data.description;
      nameCardElement.appendChild(nameDescriptionElement);
    }

    var ham = new Hammer(nameCardElement);
    ham.on('panleft', function(event) {
      ham.stop();
      nameCardElement.classList.add("rotate-right");
      setTimeout(function(){
        nameCardContainerElement.removeChild(nameCardElement);
        getNextName({name: data.name, status: 'dislike'});
      }, 1000);
    });

    ham.on('panright', function(event) {
      ham.stop();
      nameCardElement.classList.add("rotate-left");
      setTimeout(function(){
        nameCardContainerElement.removeChild(nameCardElement);
        getNextName({name: data.name, status: 'like'});
      }, 1000);

    });
  };
}

window.addEventListener('load', function() {
  getNextName();
}, false);
