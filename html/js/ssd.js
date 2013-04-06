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
    
    input.val(defaulttext);
    
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
    
    input.val(defaulttext);
    
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