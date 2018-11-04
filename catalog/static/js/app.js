$(".brighten").click(function() {
  window.location = $(this).find("a").attr("href");
  return false;
});

$(".demo-card-wide").hover(
    function() {
        $(this).toggleClass('mdl-shadow--8dp').toggleClass('mdl-shadow--2dp');

    }
);
var hide = {
    loginbutton: function(){
      $('.signInButtonTitle').hide();
      $('.signOutButtonTitle').show();
      $('.signInButton').hide();
      $('#user_info').show();
      $('#logout_button1').show();
    },
    userinfo: function(){
      $('#user_info').hide();
      $('.signInButtonTitle').show();
      $('.signOutButtonTitle').hide();
      $('.signInButton').show();
      $('#logout_button1').hide();
    }
}

if((logged == 'null')||(logged=='')){
  hide.userinfo();
}
else{
  hide.loginbutton();
}

var notification = document.querySelector('.mdl-js-snackbar');

var validateDetails = function() {
  var gamename = $('#gamename');
  var authorname = $('#authorname');
  var coverUrl = $('#coverurl');
  var description = $('#description');
  var category = $('#category');

  if (gamename.val() == "") {
    notification.MaterialSnackbar.showSnackbar(
      {
        message: "Game name can not be empty!"
      }
    );
    gamename.focus();
    return false;
  }
  else if (coverUrl.val() == "") {
    notification.MaterialSnackbar.showSnackbar(
      {
        message: "Cover Image Url is required :) !"
      }
    );
    coverUrl.focus();
    return false;
  }
  else if (description.val() == "") {
    notification.MaterialSnackbar.showSnackbar(
      {
        message: "What is a description of your game ?"
      }
    );
    description.focus();
    return false;
  }
  else if (category.val() == "") {
    notification.MaterialSnackbar.showSnackbar(
      {
        message: "What is the game's category ?"
      }
    );
    return false;
  }

  $('#gameForm').submit();

};

var googleSignInCallback = function(authResult){
    if (authResult['code']){
        $.ajax({
            type: 'POST',
            url: '/gconnect?state=' + state,
            processData: false,
            contentType: 'application/json',
            data: authResult['code'],
            success: function(result){
                if(result){
                    var img = result['img'].replace('https','http');
                    hide.loginbutton();
                    $('#userImg').attr('src',img);
                    $('#userName').html(result['name']);
                    $('#userEmail').html(result['email']);
                    logged = 'google';
                }
                else if (authResult['error']){
                    console.log("Following Error Occured:" + authResult['error']);
                }
                else{
                    console.log('Connection failed, Check your Connection !');
                }
            }
        });
    }
};


var logout = function(){

   if(logged=='google'){

    $.ajax({

      type: 'POST',
      url: '/logout',
      processData: false,
      contentType: 'application/json',
      success: function(result){
        if(result['state'] == 'loggedOut'){
          console.log(window.location.href + "?error=" + "successLogout");
          notification.MaterialSnackbar.showSnackbar(
            {
              message: "You have been Successfully Logged out!"
            }
          );
          hide.userinfo();

        }
        else if (result['state'] == 'notConnected'){
          notification.MaterialSnackbar.showSnackbar(
            {
              message: "User not Logged in!"
            }
          );
        }
        else if (result['state'] == 'errorRevoke'){
          notification.MaterialSnackbar.showSnackbar(
            {
              message: "Error Revoking User Token!"
            }
          );
        }

      }

    });

   }
   else{

     notification.MaterialSnackbar.showSnackbar(
       {
         message: "User not Logged in!"
       }
     );
   }

}

gapi.signin.render("googleSignIn", {
              'clientid': '45745583403-rnm6t7dnpdmvv3f5blioba1drn21nfns.apps.googleusercontent.com',
              'callback': googleSignInCallback,
              'cookiepolicy': 'single_host_origin',
              'requestvisibleactions': 'http://schemas.google.com/AddActivity',
              'scope': 'openid email',
              'redirecturi': 'postmessage',
              'accesstype': 'offline',
              'approvalprompt': 'force'
});

gapi.signin.render("googleSignInCustom", {
              'clientid': '45745583403-rnm6t7dnpdmvv3f5blioba1drn21nfns.apps.googleusercontent.com',
              'callback': googleSignInCallback,
              'cookiepolicy': 'single_host_origin',
              'requestvisibleactions': 'http://schemas.google.com/AddActivity',
              'scope': 'openid email',
              'redirecturi': 'postmessage',
              'accesstype': 'offline',
              'approvalprompt': 'force'
});

$('#logout_button').click(function(){
    logout();
});

$('#logout_button1').click(function() {
  logout();
});