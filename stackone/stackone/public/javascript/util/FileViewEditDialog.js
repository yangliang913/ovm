﻿/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function FileViewEditDialog(content,message,mode,type,node,action){
    
    var editor=new Ext.form.TextArea({
        width: 500,
        height: 445,
        value:content,
        bodyStyle:'padding:0px 0px 0px 0px',
        readOnly:!(mode=='edit')
    });
    var panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:505,
        height:475,
        items:[editor],
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'ok',
                id: 'ok',
                text:_('确定'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        closeWindow();
                        saveContent(node,action,editor.getValue());
                    }
                }
            }),
            '-',
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('取消'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {closeWindow();}
                }
            })
        ]
    });

    return panel;

}

function saveContent(node,action,content){
    var url="";
    if(action=='edit_image_script'){
        url="/template/save_image_script?image_id="+node.attributes.nodeid;
    }else if(action=='edit_image_desc'){
        url="/template/save_image_desc?image_id="+node.attributes.nodeid;
    }else if(action=='edit_vm_config_file'){
        url="/node/save_vm_config_file?dom_id="+node.attributes.id+
        "&node_id="+node.parentNode.attributes.id;
    }
    
    var ajaxReq = ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        params:{content:content},
        success: function(xhr) {
            var res=Ext.util.JSON.decode(xhr.responseText);
            if(res.success){
                node.fireEvent('click',node);
            }else
                Ext.MessageBox.alert(_("Error"),res.msg);
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}