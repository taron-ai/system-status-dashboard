/*

Copyright 2012 - Tom Alessi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

*/

// Place (and replace) the default text in input boxes
function default_text_input(name,defaulttext) {

    var input = $('input[name='+name+']');
    
    // Set the default text
    // If its empty, set to the default text, otherwise leave alone meaning we had a bad form submit
    // so let DJango keep the bad data there
    if(input.val() == 'None' | input.val() == '') {
        input.val(defaulttext); 
    }
    
    input.on('focus', function(){
        if(input.val() != defaulttext)
            input.addClass('typing');
        else
            input.removeClass('typing');
        
    }).on('keydown', function(){        
        if(defaulttext == input.val()) input.val('');
        
        input.addClass('typing');
    }).on('blur', function(){
        if(input.val() == '') input.val(defaulttext);

    });

}


// Place (and replace) the default text in textarea boxes
function default_text_textarea(name,defaulttext) {

    var input = $('textarea[name='+name+']');
        
    // Set the default text
    // If its empty, set to the default text, otherwise leave alone meaning we had a bad form submit
    // so let DJango keep the bad data there
    if(input.val() == 'None' | input.val() == '') {
        input.val(defaulttext); 
    }
    
    input.on('focus', function(){
        if(input.val() != defaulttext)
            input.addClass('typing');
        else
            input.removeClass('typing');
        
    }).on('keydown', function(){        
        if(defaulttext == input.val()) input.val('');
        
        input.addClass('typing');
    }).on('blur', function(){
        if(input.val() == '') input.val(defaulttext);

    });

}

// Add or remove input fields
function changeElement(action,divName,fieldName,size) {

   var div = document.getElementById(divName);

   // Obtain all of the input fields in the div
   var inputs = div.getElementsByTagName("input");
   var last_item = inputs.length - 1;
   var last = inputs[last_item].id;

   if (action == 'add') {
      var count = Number(last.split("_")[1]) + 1;
      var input = document.createElement('input');
      var br = document.createElement('br');

      input.id = fieldName + "_" + count;
      br.id = fieldName + "_" + 'br_' + count;

      input.name = fieldName;
      br.name = fieldName + 'br_';

      input.type = "text";
      input.className = "dash_url";
      input.size = size;
      div.appendChild(input);
      div.appendChild(br);
   } else {
      var count = Number(last.split("_")[1]);

      // If there is only one textfield, quit
      if (count == 1) {return;}
    
      // Remove the field
      var field_name = fieldName + "_" + count;
      var input = document.getElementById(field_name);
      div.removeChild(input);

      // Remove the break
      var br_name = fieldName + "_" + 'br_' + count;
      var br = document.getElementById(br_name);
      div.removeChild(br);

   }
}

/* Responsive tables, add graphical queue if td > 3
From: http://www.design4lifeblog.com/responsive-tables/
*/

$(document).ready(function () {
//If a table has more than 3 tds show visual scroll cue

  $("table.responsive").each(function () {
    if ($("td", this).length > 3) {
        $(this).before("<div style='position:relative;'><span class='MobiScroll'></span></div>");
      }
  });
});