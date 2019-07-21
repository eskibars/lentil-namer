window.addEventListener('load', function() {
  var nameCardContainerElements = document.getElementsByClassName("card");
  for (var i = 0; i < nameCardContainerElements.length; i++) {
    var element = nameCardContainerElements[i];
    element.addEventListener('click', function(clickedElement) {
      var family = getCookie('family');
      var user = getCookie('user');

      if (clickedElement.currentTarget.classList.contains('bg-danger')) {
        jsonPostData = { 'name': clickedElement.srcElement.innerText, 'status': 'like' };
        clickedElement.currentTarget.classList.remove('bg-danger');
        clickedElement.currentTarget.classList.add('bg-success');
      } else {
        jsonPostData = { 'name': clickedElement.srcElement.innerText, 'status': 'dislike' };
        clickedElement.currentTarget.classList.remove('bg-success');
        clickedElement.currentTarget.classList.add('bg-danger');
      }

      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/n/" + family + "/" + user + "/nextname");
      xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
      xhr.send(JSON.stringify(jsonPostData));
    });
  }
}, false);
