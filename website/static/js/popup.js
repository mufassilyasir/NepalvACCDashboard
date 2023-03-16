var discordpopup = document.getElementById("open-popup-btn");
var discordnvm = document.getElementById("hi-popup-btn");
var namepopup = document.getElementById("open-me");
var avatarpopup = document.getElementById("setavatar");
var avatarnvmbtn = document.getElementById("avatar-nvm-btn");
var nvmpopupbtn = document.getElementById("nvm-popup-btn")

if (discordpopup){

document.getElementById("open-popup-btn").addEventListener("click",function(){
  document.getElementsByClassName("popup")[0].classList.add("active");
  
})
};

if (discordnvm){
document.getElementById("hi-popup-btn").addEventListener("click",function(){
  document.getElementsByClassName("popup")[0].classList.remove("active");
})
};


if (namepopup){
document.getElementById("open-me").addEventListener("click",function(){
  document.getElementsByClassName("modal-name")[0].classList.add("active");
  
})
 
};

if (avatarpopup){
document.getElementById("setavatar").addEventListener("click",function(){
  document.getElementsByClassName("avatar-modal")[0].classList.add("active");
    
})
  
};
if (avatarnvmbtn){
document.getElementById("avatar-nvm-btn").addEventListener("click",function(){
  document.getElementsByClassName("avatar-modal")[0].classList.remove("active");
});
};

if (nvmpopupbtn){
document.getElementById("nvm-popup-btn").addEventListener("click",function(){
  document.getElementsByClassName("modal-name")[0].classList.remove("active");
});
};

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


$(function() {
  var dimmerButton = $('.open-me');
  var dimmer = $('.dimmer2');
  var exit = $('.nvm-btn');
  dimmerButton.on('click', function() {
    dimmer.show();
  });
  exit.on('click', function() {
    dimmer.hide();
  });
});

$(function() {
  var dimmerButton = $('.setavatar');
  var dimmer = $('.dimmer3');
  var exit = $('.avatar-nvm');
  dimmerButton.on('click', function() {
    dimmer.show();
  });
  exit.on('click', function() {
    dimmer.hide();
  });
});
