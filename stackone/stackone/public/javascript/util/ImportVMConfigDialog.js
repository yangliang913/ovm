/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* author : Benf<yangbf@stackone.com.cn>
*/

function ImportVMConfigDialog(node,node_attrs){
    if (node_attrs.auto_discover == true){
        importVMConfiguration(node,"");
        return null;
    }
    var hostname=new Ext.form.TextField({
        fieldLabel: _('主机'),
        name: 'host',
        id: 'host',
        disabled:true,
        border:false,
        labelStyle: 'font-weight:bold;',
        width:320
    });
    var directory=new Ext.form.TextField({
        fieldLabel: _('目录'),
        name: 'directory',
        id: 'directory',
        labelStyle: 'font-weight:bold;',
        width:320,
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
    var location=new Ext.form.TextField({
        fieldLabel: _('位置'),
        name: 'location',
        id: 'location',
        labelStyle: 'font-weight:bold;',
        width:320,
        enableKeyEvents:true,
        listeners:{
            keyup : function(field,e){
                grid.getSelectionModel().clearSelections();
            }
        }
    });

    var ss=(node_attrs.isRemote=='True')?"ssh://":"";
    hostname.setValue(ss+node_attrs.username+"@"+node_attrs.hostname);
//    directory.setValue(node_attrs.configdir);
    var store = new Ext.data.JsonStore({
        url: '/node/list_vm_configs?node_id='+node.attributes.id,
        root: 'rows',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        fields: ['id', 'name', 'path', 'date', {name:'isdir', type:'boolean'},'status_icon'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                var msg=store_response.msg;
                if(store_response.err=='NoDirectory'){
                    store.load({
                        params:{directory:directory.getValue()}
                    });
                    msg+='.<br> 加载中 "/" .';
                }
                Ext.MessageBox.alert("Error",msg);
            }
        }
    });
    store.load({
        params:{directory:directory.getValue()}
    });

    var checkBoxSelMod = new Ext.grid.CheckboxSelectionModel({
        singleSelect:false
    });

    var columnModel = new Ext.grid.ColumnModel([
        checkBoxSelMod,
        {header: _("编号"), hidden: true, sortable: true, dataIndex: 'id'},
        {header: "", width: 22,sortable: true,dataIndex: 'isdir',renderer:function(value,params,record){
                if(!value)
                    return '<img src="icons/file.png" />';
                else
                    return '<img src="icons/folder.png" />';
            }
        },
        {header: _("名称"), width: 160, sortable: true, dataIndex: 'name'},
        {header: _("状态"), width: 80, sortable: true, dataIndex: 'status_icon'},
        {header: _("位置"), width: 160,sortable: true, dataIndex: 'path'},
        {header: _("日期"), width: 150, sortable: true, dataIndex: 'date'}
    ]);

    var grid = new Ext.grid.GridPanel({
        store: store,
        colModel:columnModel,
        collapsible:true,
        stripeRows: true,
        frame:false,
        border:false,
        width:'100%',
        autoExpandColumn:3,
        height:270,
        selModel:checkBoxSelMod,
        enableColumnHide:false,
        tbar:[
            new Ext.Button({
                name: '刷新',
                id: 'refresh',
                icon:'icons/refresh.png',
                cls:'x-btn-icon',
                listeners: {
                    click: function(btn) {
                        if(!checkDirectory(directory))
                            return;
                        grid.getStore().load();

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
                }
            }
        }
    });

    var Importpanel = new Ext.Panel({
        layout:'form',
        bodyStyle:'padding:15px 0px 0px 3px',
        cls: 'whitebackground',
        labelWidth:60,
        labelSeparator:' ',
        width:535,
        height:400,
        items:[hostname,directory,location,grid],
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
                        var len=selected.length;
                        if(len==0){
                            Ext.MessageBox.alert(_("警告"),_("请至少选择一个文件."))
                            return;
                        }
                        var paths=''
                        for(var j=0;j<len;j++){
                             paths+=((j>0)?",":"")+selected[j].get('path');
                        }
                        importVMConfiguration(node,paths);
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
    return Importpanel;
}