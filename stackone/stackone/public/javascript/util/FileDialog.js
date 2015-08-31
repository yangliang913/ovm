/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function FileDialog(node,node_attrs,action,vm){

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
        allowBlank:false,
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
    if(action=='import')
        directory.setValue(node_attrs.configdir);
    else
        directory.setValue(node_attrs.snapshotdir);

    if(action=='hibernate')
        location.setValue(vm.text+".snapshot.xm");

    var store = new Ext.data.JsonStore({
        url: '/node/list_dir_contents?node_id='+node.attributes.id,
        root: 'rows',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        fields: ['id', 'name', 'path', 'date', {name:'isdir', type:'boolean'}],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                var msg=store_response.msg;
                if(store_response.err=='NoDirectory'){
                    directory.setValue('/');
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
    var columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), hidden: true, sortable: true, dataIndex: 'id'},
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
         singleSelect:(action!='import')
    });
    var grid = new Ext.grid.GridPanel({
        store: store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        border:false,
        width:'100%',
        autoExpandColumn:2,
        height:270,
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
                hidden:(action!='hibernate'),
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
                            makeDirectory(node,directory,field,grid);
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
                    makeCall(node,directory,g,location,action,vm);
                }

            }
        }
    });

    var panel = new Ext.Panel({
        layout:'form',
        bodyStyle:'padding:15px 0px 0px 3px',
        cls: 'whitebackground',
        labelWidth:60,
        labelSeparator:' ',
        width:500,
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
                        makeCall(node,directory,grid,location,action,vm);
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

function checkDirectory(directory){
    if(directory.getValue().length==0){
        Ext.MessageBox.alert(_("警告"),_("请选择一个有效目录."));
        return false;
    }
    return true;
}
function ImportFileDialog(node,responseData){    
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

    var ss=(responseData.isRemote=='True')?"ssh://":"";
    hostname.setValue(ss+responseData.username+"@"+responseData.hostname);

    var importstore = new Ext.data.JsonStore({
        url: '/node/list_vm_configs?node_id='+node.attributes.id,
        root: 'rows',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        fields: ['id', 'name', 'path', 'date', {name:'isdir', type:'boolean'}],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                var msg=store_response.msg;
                if(store_response.err=='NoDirectory'){
                        importstore.load({
                        params:{directory:directory.getValue()}
                    });
                    msg+='.<br> 加载中 "/" .';
                }
                Ext.MessageBox.alert("Error",msg);
            }
        }
    });
    importstore.load({
        params:{directory:directory.getValue()}
    });

    var checkBoxSelMod = new Ext.grid.CheckboxSelectionModel({
        singleSelect:false
    });

    var columnModel = new Ext.grid.ColumnModel([
        checkBoxSelMod,
        {header: _("编号"), hidden: true, sortable: true, dataIndex: 'id'},
        {header: "", width: 22, dataIndex: 'isdir',hidden:true},
        {header: _("名称"), width: 120, sortable: true, dataIndex: 'name'},
        {header: _("位置"), width: 300, sortable: true, dataIndex: 'path'},
        {header: _("日期"), width: 200,hidden: true, sortable: true, dataIndex: 'date'},

    ])

    var grid = new Ext.grid.GridPanel({
        store: importstore,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        border:false,
        width:'100%',
        autoExpandColumn:2,
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
            }),
        ],
        listeners: {
            rowclick: function(g,index,evt){
                if(eval(g.getStore().getAt(index).get('isdir'))){
                    g.getSelectionModel().clearSelections();
                    g.getSelectionModel().selectRow(index,false);
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
        width:500,
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
function makeCall(node,directory,grid,location,action,vm){

    var selected=grid.getSelections();
    var len=selected.length;
    if(len==1 && eval(selected[0].get('isdir'))){
        directory.setValue(selected[0].get('path'));
        grid.getStore().load({
            params:{directory:directory.getValue()}
        });
        return;
    }
    if(!checkDirectory(directory))
        return;

    var filename='';
    for(var i=0;i<len;i++){
        if(eval(selected[i].get('isdir')))
            return;
        filename+=((i>0)?",":"")+selected[i].get('name');
    }

    if(action=='import'){
        if(len==0){
            Ext.MessageBox.alert(_("警告"),_("请选择一个文件."));
            return;
        }

        importVMConfig(node,directory.getValue(),filename);

    }else if(action=='restore'){
        if(len==0){
            Ext.MessageBox.alert(_("警告"),_("请选择一个文件."));
            return;
        }

        restoreVM(node,directory.getValue(),filename);

    }else if(action=='hibernate'){
        filename=((filename=='')?location.getValue():filename);
        if(filename==''){
            Ext.MessageBox.alert(_("警告"),_("请输入一个文件名称."));
            return;
        }
        snapshotVM(vm,directory.getValue(),filename);
    }
}

function makeDirectory(node,directory,field,grid){
    var dirname=field.getValue();
    if(dirname.indexOf('/')>-1 || dirname.indexOf('.')>-1 ){
        Ext.MessageBox.alert(_("警告"),_("请输入一个有效名称."));
        return;
    }
    var url="/node/make_dir?node_id="+node.attributes.id+"&parent_dir="+directory.getValue()+"&dir="+dirname;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var res=Ext.util.JSON.decode(xhr.responseText);
            field.hide();
            if(res.success){
                grid.getStore().load({
                    params:{directory:res.newdir}
                });
                directory.setValue(res.newdir);
            }else{
                Ext.MessageBox.alert(_("Error"),res.msg);
            }
        },
        failure: function(xhr){
            try{
                var res=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), res.msg);
            }catch(e){
                Ext.MessageBox.alert(_("错误"),_("失败:")+xhr.statusText);
            }
        }
    });
}

function show_importfile_dialog(node_id,responseData){
    var node=new Ext.tree.TreeNode({
        id:node_id,
        type:stackone.constants.MANAGED_NODE
    });
    showWindow(_("选择虚拟机配置文件"),550,425,ImportVMConfigDialog(node,responseData),null,false,true);
}
