//Only show one login/logut button and hide client's account for google
const hidden = {
    googlePress: function(){
      $('.googleOut').show();
      $('.googleButtonLegend').show();
      $('.googleButton').hide();
      $('#client').show();
      $('#logout_button1').show();
    },
    clientdata: function(){
      $('.googleOut').hide();
      $('#client').hide();
      $('.googleButtonLegend').hide();
      $('.googleButton').show();
      $('#logout_button1').hide();
    }
}

// Hide client data if client isn't logged in 
if((logged == 'null')||(logged=='')){
  hidden.clientdata();
}
else{
  hidden.googlePress();
}

// set the document selector to a variable
const alert = document.querySelector('.mdl-js-snackbar');

var confirmAttributes = function() {
  let gamename = $('#gamename');
  let coverUrl = $('#coverurl');
  let description = $('#description');
  let category = $('#category');

// If client's entry value doesn't have input, have snackbar notify client
  if (gamename.val() == "") {
    alert.MaterialSnackbar.showSnackbar(
      {
        message: "You should give your game a name !"
      }
    );
    gamename.focus();
    return false;
  }
  else if (coverUrl.val() == "") {
    alert.MaterialSnackbar.showSnackbar(
      {
        message: "You should insert a url for your cover art !"
      }
    );
    coverUrl.focus();
    return false;
  }
  else if (description.val() == "") {
    alert.MaterialSnackbar.showSnackbar(
      {
        message: "What is a description of your game ?"
      }
    );
    description.focus();
    return false;
  }
  else if (category.val() == "") {
    alert.MaterialSnackbar.showSnackbar(
      {
        message: "What is the game's category ?"
      }
    );
    return false;
  }

  //Make sure information is submitted
  $('#gameForm').submit();

};

// Use ajax call to retrieve google account information and check connection
var googleOauthCallback = function(authResult){
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
                    hidden.googlePress();
                    $('#clientImg').attr('src',img);
                    $('#clientName').html(result['name']);
                    $('#clientEmail').html(result['email']);
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

// Make sure client is able to log out successfully or whether client is logged in. 
let logout = function(){

   if(logged=='google'){

    $.ajax({

      type: 'POST',
      url: '/logout',
      processData: false,
      contentType: 'application/json',
      success: function(result){
        if(result['state'] == 'loggedOut'){
          console.log(window.location.href + "?error=" + "successLogout");
          alert.MaterialSnackbar.showSnackbar(
            {
              message: "You have been Successfully Logged out!"
            }
          );
          hidden.clientdata();

        }
        else if (result['state'] == 'notConnected'){
          alert.MaterialSnackbar.showSnackbar(
            {
              message: "User is not logged in !"
            }
          );
        }
        else if (result['state'] == 'errorRevoke'){
          alert.MaterialSnackbar.showSnackbar(
            {
              message: "There was an error Revoking the User Token!"
            }
          );
        }

      }

    });

   }
   else{

     alert.MaterialSnackbar.showSnackbar(
       {
         message: "User not Logged in!"
       }
     );
   }

}



gapi.signin.render("googleSignIn", {
              'clientid': '45745583403-rnm6t7dnpdmvv3f5blioba1drn21nfns.apps.googleusercontent.com',
              'callback': googleOauthCallback,
              'cookiepolicy': 'single_host_origin',
              'requestvisibleactions': 'http://schemas.google.com/AddActivity',
              'scope': 'openid email',
              'redirecturi': 'postmessage',
              'accesstype': 'offline',
              'approvalprompt': 'force'
});



$('#logout_button1').click(function() {
  logout();
});