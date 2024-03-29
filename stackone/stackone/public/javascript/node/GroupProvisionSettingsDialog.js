﻿/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function GroupProvisionSettingsDialog(node){

    var columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), width: 50, hidden: true, dataIndex: 'id'},
        {header: _("可变"), width: 150, sortable: false, dataIndex: 'variable',css:'font-weight:bold; color:#414141;',editor: new Ext.form.TextField({
                       allowBlank: false
                   })
        },
        {header: _("值"), width: 200, sortable: false, dataIndex: 'value',editor: new Ext.form.TextField({
                       allowBlank: false
                   })}
    ]);

    var store = new Ext.data.JsonStore({
        url: '/node/get_group_vars?group_id='+node.attributes.id,
        root: 'rows',
        fields: ['id', 'variable', 'value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert("Error",store_response.msg);
            }
        }
    });
    store.load();
    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var rec = Ext.data.Record.create([
           {name: 'id', type: 'string'},
           {name: 'variable', type: 'string'},
           {name: 'value', type: 'string'}
    ]);

    var grid = new Ext.grid.EditorGridPanel({
        store: store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        selModel:selmodel,
        width:'100%',
        autoExpandColumn:2,
        height:290,
        clicksToEdit:2,
        enableHdMenu:false,
        tbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'add_var',
                id: 'add_var',
                text:_("添加"),
                icon:'icons/add.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        var r=new rec({
                            id: '',
                            variable: ' ',
                            value: ''
                        });

                        grid.stopEditing();
                        store.insert(0, r);
                        grid.startEditing(0, 0);
                    }
                }
            }),
            '-',
            new Ext.Button({
                name: 'remove_var',
                id: 'remove_var',
                text:_("移除"),
                icon:'icons/delete.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        grid.getStore().remove(grid.getSelectionModel().getSelected());
                    }
                }
            })
        ]
    });

    var lbl=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">'+_("此处定义的设置模板中的值将覆盖原有的模板配置.")+
                _("(以＃开头的值将被忽略)") +'<br/></div>'
//         text:_("Settings defined here override the values in the template at the time of provisioning.")+
//                 _("(Values begining with # are ignored)")
    });

	var panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:495,
        height:350,
        items:[lbl,grid],
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'ok',
                id: 'ok',
                text:_('确定'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon whitebackground',
                listeners: {
                    click: function(btn) {
                        var recs=store.getRange(0,store.getCount());
                        saveGroupVars(node,recs);
                        closeWindow();
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

function saveGroupVars(node,records){
    var url="/node/save_group_vars?group_id="+node.attributes.id;
    
    for(var i=0;i<records.length;i++){
        url+="&"+records[i].get('variable')+"="+records[i].get('value');
    }
    //for # can not be passed through the url, replacing it with *
    url=url.replace(/#/g,"*");
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var res=Ext.util.JSON.decode(xhr.responseText);
            if(res.success){
                //Ext.MessageBox.alert("OK",res.msg);
            }else
                Ext.MessageBox.alert(_("Error"),res.msg);
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });

}
