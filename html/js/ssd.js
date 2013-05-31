/*

Copyright 2013 - Tom Alessi

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
