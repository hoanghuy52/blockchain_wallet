

function loading_effect(method, text) {
  if (text == undefined) {
    text = "Rekognition....."
  }
  if (method === 'on') {
      $.Toast.showToast({
          // toast message
          "title": text,
          // "success", "none", "error"
          "icon": "loading",
          "duration": -1
      });
  } else if (method === 'off') {
      $.Toast.hideToast();
  }

}

function makeid(length) {
  var result           = '';
  var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  var charactersLength = characters.length;
  for ( var i = 0; i < length; i++ ) {
     result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  return result;
}
