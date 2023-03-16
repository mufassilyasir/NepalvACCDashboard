var submitpopup = document.getElementById("submit-popup-btn");
var submitpopupnvm = document.getElementById("dismiss-popup-btn")
var discordpopup = document.getElementById("open-popup-btn");
var discordnvm = document.getElementById("hi-popup-btn");


if (submitpopup) {
  document.getElementById("submit-popup-btn").addEventListener("click", function () {
    document.getElementsByClassName("submit-popup")[0].classList.add("active");

  })
};

if (submitpopupnvm) {
  document.getElementById("dismiss-popup-btn").addEventListener("click", function () {
    document.getElementsByClassName("submit-popup")[0].classList.remove("active");
  })
};

if (discordpopup) {

  document.getElementById("open-popup-btn").addEventListener("click", function () {
    document.getElementsByClassName("popup")[0].classList.add("active");

  })
};

if (discordnvm) {
  document.getElementById("hi-popup-btn").addEventListener("click", function () {
    document.getElementsByClassName("popup")[0].classList.remove("active");
  })
};




$(function () {
  var dimmerButton = $('.submit-popup-btn');
  var dimmer = $('.dimmerforsubmit');
  var exit = $('.dismiss-btn');
  dimmerButton.on('click', function () {
    dimmer.show();
  });
  exit.on('click', function () {
    dimmer.hide();
  });
});

$(function() {
  var dimmerButton = $('.open-popup-btn');
  var dimmer = $('.dimmer');
  var exit = $('.hi-btn');
  dimmerButton.on('click', function() {
    dimmer.show();
  });
  exit.on('click', function() {
    dimmer.hide();
  });
});


