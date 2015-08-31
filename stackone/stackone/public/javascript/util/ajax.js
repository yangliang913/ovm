/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function ajaxRequest(url,timeout,method,unmask){

    var ajaxReq = new Ext.data.Connection({
        url:url,
        disableCaching:false,
        timeout:timeout,
        method:method,
        listeners: {
            'beforerequest': {
                fn: function(con, opt){
//                    if(!unmask)
//                        Ext.get('centerPanel').mask(_('Loading...'));
                },
                scope: this
            },
            'requestcomplete': {
                fn: function(con, res, opt){
                    if(!unmask)
                        Ext.get('centerPanel').unmask();
                },
                scope: this
            },
            'requestexception': {
                fn: function(con, res, opt){
                    if(!unmask)
                        Ext.get('centerPanel').unmask();
                },
                scope: this
            }
        }
    });

    return ajaxReq;
}