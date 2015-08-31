/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

format = function( text ){
    //check if there are two arguments in the arguments list
    if ( arguments.length <= 1 ){
        //if there are not 2 or more arguments there’s nothing to replace
        //just return the original text
        return text;
    }

    //decrement to move to the second argument in the array
    var tokenCount = arguments.length - 2;
    for( var token = 0; token <= tokenCount; token++ ){
        //iterate through the tokens and replace their placeholders from the original text in order
        text = text.replace( new RegExp( "\\{" + token + "\\}", "gi" ),
            arguments[ token + 1 ] );
    }
    return text;
};