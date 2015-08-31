/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function FileBrowser(dir,file,url,singleSelect,new_dir,browseField,browseWindow,objData){

    var directory=new Ext.form.TextField({
        fieldLabel: _('目录'),
        name: 'directory',
        id: 'directory',
        allowBlank:false,
        labelStyle: 'font-weight:bold;',
        width:320,
        value:dir,
        listeners:{
            specialkey : function(btn,e){
                if(e.getKey()==13){
                    grid.getStore().load({
                        params:{directory:directory.getValue()}
                    });
                }
            }
        }
    });
//    var location=new Ext.form.TextField({
//        fieldLabel: 'Location',
//        name: 'location',
//        id: 'location',
//        labelStyle: 'font-weight:bold;',
//        width:320,
//        value:file,
//        enableKeyEvents:true,
//        listeners:{
//            keyup : function(field,e){
//                grid.getSelectionModel().clearSelections();
//            }
//        }
//    });

    var store = new Ext.data.JsonStore({
        url: '/node/list_dir_contents?'+url,
        root: 'rows',
        fields: ['id', 'name', 'path', 'date', {name:'isdir', type:'boolean'}],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert("Error",store_response.msg);
            }
        }
    });
    store.load({
        params:{directory:directory.getValue()}
    });
    store.sort('name','ASC');
    var columnModel = new Ext.grid.ColumnModel([
        {header: _("Id"), hidden: true, sortable: true, dataIndex: 'id'},
        {header: "", width: 22, dataIndex: 'isdir',renderer:function(value,params,record){
                if(!value)
                    return '<img src="icons/file.png" />';
                else
                    return '<img src="icons/folder.png" />';
            }
        },
        {header: _("名称"), width: 150, sortable: true, dataIndex: 'name'},
        {header: _("路径"), hidden: true, width: 120, sortable: true, dataIndex: 'path'},
        {header: _("日期"), width: 200, sortable: true, dataIndex: 'date'}
    ]);

    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:singleSelect
    });
    var grid = new Ext.grid.GridPanel({
        store: store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        border:false,
        width:'100%',
        autoExpandColumn:2,
        height:310,
        selModel:selmodel,
        enableColumnHide:false,
        tbar:[
            new Ext.Button({
                name: '刷新',
                id: 'refresh',
                //tooltip:'Refresh',
                //tooltipType : "title",
                icon:'icons/refresh.png',
                cls:'x-btn-icon',
                listeners: {
                    click: function(btn) {
                        if(!checkDirectory(directory))
                            return;
                        grid.getStore().load({
                            params:{directory:directory.getValue()}
                        });
                    }
                }
            }),
            '-',
            new Ext.Button({
                name: '创建',
                id: 'create',
                //tooltip:'Create Folder',
                //tooltipType : "title",
                hidden:!new_dir,
                icon:'icons/folder_add.png',
                cls:'x-btn-icon',
                listeners: {
                    click: function(btn) {
                        var txtFld=grid.getTopToolbar().items.get('newdir');
                        txtFld.show();
                        txtFld.setValue(_('New Folder Name'));
                        txtFld.focus(true);
                    }
                }
            }),
            new Ext.form.TextField({
                name: 'newdir',
                id: 'newdir',
                width:200,
                hidden:true,
                listeners: {
                    specialkey : function(field,e){
                        if(e.getKey()==13){
                            makeDirectory(directory,field,grid,url);
                        }
                    },
                    blur:function(field){
                        field.hide();
                    }
                }
            })
        ],
        listeners: {
            rowclick: function(g,index,evt){
                if(eval(g.getStore().getAt(index).get('isdir'))){
                    g.getSelectionModel().clearSelections();
                    g.getSelectionModel().selectRow(index,false);
                }
            },
            rowdblclick: function(g,index,evt) {
                if(eval(g.getStore().getAt(index).get('isdir'))){
                    directory.setValue(g.getStore().getAt(index).get('path'));
                    grid.getStore().load({
                        params:{directory:directory.getValue()}
                    });
                }else{
                    //setLocationValue(g.getStore().getAt(index).get('path'));
                    browseField.setValue(g.getStore().getAt(index).get('path'));
                    browseWindow.close();
                }

            }
        }
    });

    var panel = new Ext.Panel({
        layout:'form',
        bodyStyle:'padding:15px 0px 0px 3px',
        labelWidth:60,
        labelSeparator:' ',
        width:500,
        height:400,
        items:[directory,grid],
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'ok',
                id: 'ok',
                text:_('确定'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        var selected=grid.getSelections();
                         if(eval(selected[0].get('isdir'))){
                            directory.setValue(selected[0].get('path'));
                            grid.getStore().load({
                                params:{directory:directory.getValue()}
                            });
                            return;
                        }
                        
                        //setLocationValue(selected[0].get('path'));
                        browseField.setValue(selected[0].get('path'));

                        //Start-This is for vm restore
                        if(browseField.id=="txt_ref_disk") {
                            ref_disk = txt_ref_disk.getValue();
//                             alert("ref_disk=" + ref_disk)
                            txt_ref_disk.setValue("");
                            //from node/RestoreBackup.js
                            RestoreBackup(objData.server_id, objData.vm_id, "", objData.result_id, false, ref_disk);
                        }
                        //End-This is for vm restore

                        browseWindow.close();
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
                    click: function(btn) {closeFileBrowser();}
                }
            })
        ]
    });

    return panel;
}

function checkDirectory(directory){
    if(directory.getValue().length==0){
        Ext.MessageBox.alert(_("警告"),_("请选择一个有效的目录."));
        return false;
    }
    return true;
}

