/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function credentialsForm(){
    var username=new Ext.form.TextField({
        fieldLabel: _('用户名'),
        name: 'user_name',
        allowBlank:false,
        width: 150,
        value:'root'
    });
    var password=new Ext.form.TextField({
        fieldLabel: _('密码'),
        name: 'pwd',
        allowBlank:false,
        width: 150,
        inputType : 'password'
    });
    var form = new Ext.FormPanel({
        labelWidth:90,
        frame:true,
        border:0,
        labelAlign:"left" ,
        width:280,
        height:120,
        labelSeparator: ' ',
        items:[username,password]
    });

    return form;
}



