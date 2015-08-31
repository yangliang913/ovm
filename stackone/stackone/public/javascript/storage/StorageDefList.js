/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var storage_def,storage_grid,storage_panel;
var selNode;
var sSiteId, sGroupId, sNodeId,op_level;
var hideSyncAll;
var server_grid;
var windowid;

var strg_load_counter=0;
var strg_timeout;
var curr_strg_count=0;
var initial_strg_count=0;
var is_timer=false; 
var strg_name_adding="";
var adding_storage=false;
var removing_storage=false;

var hideServerPoolsCol;
function StorageDefList(node){
    selNode = node;

    //We are checking whether the node passed is server or servergroup.
    if(node.attributes.nodetype == 'DATA_CENTER'){
        //When menu is invoked at data center level
        //Consider the node is a data center
        //node and group would be null
        sSiteId = "site_id=" + node.attributes.id;
        op_level = "&op_level=DC";
        sGroupId = "";
        sNodeId = "";
        hideSyncAll = true;
        new_button_text = "新建";
        remove_button_text = "移除";
        hideEditButton = false;
        hideServerPoolsCol = true;
        edit_seperator = "-";
        headingmsg = "配置存储自动化以使服务器池的所有服务器共享存储资源.";
    }
    else if(node.attributes.nodetype == 'SERVER_POOL'){
        //When menu is invoked at server pool level
        //Consider the node is a group (server pool)
        //node would be null
        sSiteId = "site_id=" + node.parentNode.attributes.id;
        op_level = "&op_level=SP";
        sGroupId = "&group_id=" + node.attributes.id;
        sNodeId = "";
        hideSyncAll = false;
        new_button_text = "附加";
        remove_button_text = "分离";
        hideEditButton = true;
        hideServerPoolsCol = true;
        edit_seperator = "";
        //headingmsg = "This represents shared storage resources available to all servers with in a Server Pool.";
        headingmsg = "此处登记提供给本服务器池的存储资源. stackone将进行更改，使所有服务器可以访问存储.";
    }
    else{
        //When menu is invoked at server level
        //Consider the node is a server
        sSiteId = "site_id=" + node.parentNode.parentNode.attributes.id;
        op_level = "&op_level=S";
        sGroupId = "&group_id=" + node.parentNode.attributes.id;
        sNodeId = "&node_id=" + node.attributes.id;
        hideSyncAll = true;
        new_button_text = "新建";
        remove_button_text = "移除";
        hideEditButton = false;
        hideServerPoolsCol = true;
        edit_seperator = "-";
        headingmsg = "这意味着服务器共享存储资源.";

    }

    var columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), hidden: true, dataIndex: 'id'},
        {header: _("名称"), width: 80, sortable: false, dataIndex: 'name'},
        {header: _("类型"), width: 40, sortable: false, dataIndex: 'type'},
        {header: _("大小(GB)"), width: 60, sortable: false, dataIndex: 'size'},
        {header: _("定义"), hidden: true, sortable: false, dataIndex: 'definition'},
        {header: _("服务器池"), hidden: hideServerPoolsCol, sortable: true, dataIndex: 'serverpools'},
        {header: _("说明"), width: 135, sortable: false, dataIndex: 'description'},
        {header: _("状态"), width: 90, hidden: false, sortable: false, renderer: showStorageDefStatusLink, dataIndex: 'status'},//100
        {header: _("范围"), hidden: true, sortable: false, dataIndex: 'scope'},
        {header: _("关联"), hidden: true, sortable: false, dataIndex: 'associated'}
        ]);

    var store = new Ext.data.JsonStore({
        url: '/storage/get_storage_def_list?' + sSiteId + op_level + sGroupId,
        root: 'rows',
        fields: ['id', 'name', 'type','size', 'definition', 'description','stats','connection_props','status', 'scope', 'associated', 'serverpools'],
        successProperty:'success',
        listeners:{
            load:function(my_store, records, options){
                //alert("Loading...");
                strg_load_counter++
                if(strg_load_counter>10) {
                    clearTimeout(strg_timeout);
                    is_timer = false;
                    return;
                }
                curr_strg_count = my_store.getCount();
                if(is_timer == true) {
                    if(initial_strg_count != curr_strg_count) {
                        //alert("Breaking...");
                        if(adding_storage==true){
                            for(i=0;i<=curr_strg_count;i++) {
                                rec = my_store.getAt(i);
                                if(selNode.attributes.nodetype == 'SERVER_POOL') {
                                    if(strg_name_adding == rec.get('name') || strg_name_adding == "") {
                                        //alert("Breaking for add...");
                                        clearTimeout(strg_timeout);
                                        is_timer = false;
                                        adding_storage = false;
                                        break;
                                    }
                                } else if(parseFloat(rec.get('size')) > 0) {
                                    //alert("Breaking for add...");
                                    clearTimeout(strg_timeout);
                                    is_timer = false;
                                    adding_storage = false;
                                    setTimeout("reloadStorageDefList()", 5000);
                                    break;
                                }
                            }
                        } else {
                            //alert("Breaking for remove...");
                            clearTimeout(strg_timeout);
                            is_timer = false;
                            removing_storage = false;
                        }
                    } else {
                        strg_timeout = setTimeout("reloadStorageDefList()", 1000);
                    }
                }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    store.load();

    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var storage_new_button=new Ext.Button({
        name: 'add_storage',
        id: 'add_storage',
        text:_(new_button_text),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                adding_storage=true;
                removing_storage=false;
                storage_grid.getSelectionModel().clearSelections();
//                storage_details=StorageDefinition(node.attributes.id,"NEW",null);
                windowid=Ext.id();
                storage_scope=null;
                showWindow(_("存储详情"),435,500,StorageDefinition(node,"NEW",null,storage_scope,null,null,null,null,windowid),windowid);
//                storage_panel.add(storage_details);
                hidefields("NEW");

            }
        }
    });
    var storage_remove_button=new Ext.Button({
        name: 'remove_storage',
        id: 'remove_storage',
        text:_(remove_button_text),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                adding_storage=false;
                removing_storage=true;
                if(checkSelectedStorage(storage_grid)){
                    if(storage_grid.getSelectionModel().getCount()>0){
                        var rec=storage_grid.getSelectionModel().getSelected();
                        var message_text = "确定要移除" + rec.get('name') + " 存储吗?";
                        var storage_id=storage_grid.getSelectionModel().getSelected().get('id');
                        CheckAndRemoveStorage(storage_id,node,storage_grid,message_text);
                        /*
                        Ext.MessageBox.confirm(_("Confirm"),message_text,function(id){
                            if(id=='yes'){
                                var storage_id=storage_grid.getSelectionModel().getSelected().get('id');
                                //removeStorage(storage_id,node,storage_grid);
                                CheckAndRemoveStorage(storage_id,node,storage_grid);
                            }
                        });
                        */
                    }
                }
            }
        }
    });
    var storage_rename_button=new Ext.Button({
        name: 'rename_storage',
        id: 'rename_storage',
        text:_("重命名"),
        icon:'icons/storage_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedStorage(storage_grid)){
                    var storage_id=storage_grid.getSelectionModel().getSelected().get('id');
                    renameStorage(storage_id,node,storage_grid);
                }
            }
        }
    });
    var storage_edit_button=new Ext.Button({
        name: 'edit_storage',
        id: 'edit_storage',
        text:_("编辑"),
        icon:'icons/storage_edit.png',
        cls:'x-btn-text-icon',
        hidden: hideEditButton,
        listeners: {
            click: function(btn) {
                adding_storage=false;
                removing_storage=false;
                if(checkSelectedStorage(storage_grid)){
                    var rec=storage_grid.getSelectionModel().getSelected();
                    var storage_scope = rec.get('scope');
//                      storage_details=StorageDefinition(node.attributes.id,"EDIT",rec);
                    windowid=Ext.id();
                    showWindow(_("存储详情"),435,500,StorageDefinition(node,"EDIT",rec,storage_scope,null,null,null,null,windowid),windowid);
//                      storage_panel.add(storage_details);
                    showStorageFields(rec.get('type'));
                    hidefields("EDIT");
                   
                }
            }
        }
    });
    var storage_test_button=new Ext.Button({
        name: 'test_storage',
        id: 'test_storage',
        text:_("测试"),
        icon:'icons/storage_test.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                adding_storage=false;
                removing_storage=false;
                if(checkSelectedStorage(storage_grid)){
                    var rec=storage_grid.getSelectionModel().getSelected();
//                      storage_details=StorageDefinition(node.attributes.id,"TEST",rec);
                     windowid=Ext.id();
                     storage_scope=null;
                     showWindow(_("存储详情"),435,500,StorageDefinition(node,"TEST",rec,storage_scope,null,null,null,null,windowid),windowid);

//                      storage_panel.add(storage_details);
                    showStorageFields(rec.get('type'));
                    hidefields("TEST");                   
                }
            }
        }
    })

    var storage_details;
    storage_grid = new Ext.grid.GridPanel({
        store: store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:selmodel,
        width:415,
        height:365,
        enableHdMenu:false,
        tbar:[{xtype: 'tbfill'},
            storage_new_button,            
            '-',
            //We are hiding the rename button as per requirement 
			//since edit functionality is doing rename also.
            //storage_rename_button,
            //'-',
            storage_edit_button,
            '-',
            storage_test_button,
            '-',
            storage_remove_button,

            new Ext.Button({
                name: 'btnSyncAll',
                id: 'btnSyncAll',
                text:"全部同步",
                icon:'icons/sync-all-icon.png',
                cls:'x-btn-text-icon',
                hidden:hideSyncAll,
                listeners: {
                    click: function(btn) {
                        adding_storage=false;
                        removing_storage=false;
                        sync_all("STORAGE");
                    }
                }
            }),
            new Ext.Button({
                name: 'btnRefreshStorage',
                id: 'btnRefreshStorage',
                text:"刷新",
                icon:'icons/refresh.png',
                cls:'x-btn-text-icon',
                hidden: false,
                listeners: {
                    click: function(btn) {
                        adding_storage=false;
                        removing_storage=false;
                        //alert("Refreshing storage");
                        reloadStorageDefList();
                    }
                }
            })
        ],
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                storage_edit_button.fireEvent('click',storage_edit_button);
            }
         }
    });

    var lbl=new Ext.form.Label({
         html:'<div style="" class="labelheading">'+headingmsg+'</div>'
    });

	storage_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:430,
        height:468,
//        hidemode:"offset",
        frame:true,
        items:[lbl,storage_grid]
        ,bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('关闭'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {adding_storage=false; removing_storage=false; closeWindow();}
                }
            })
        ]
    });

    return storage_panel;
}

function checkSelectedStorage(grid){
    if(grid.getSelections().length==0){
        Ext.MessageBox.alert(_("警告"),_("请选择一个存储."));
        return false;
    }
    return true;
}

function closeStorageDefinition(){
    storage_def.close();
}

function renameStorage(storage_id,node,grid){

    Ext.MessageBox.prompt(_("重命名共享存储"),_("输入新共享存储的名称"),function(btn, text){
        if (btn == 'ok'){
            if(text.length==0){
                Ext.MessageBox.alert(_("错误"),_("Please enter valid Name."));
                return;
            }
            var url="/storage/rename_storage_def?" + sSiteId + sGroupId + "&storage_id="+storage_id+"&new_name="+text; 
            var ajaxReq=ajaxRequest(url,0,"GET",true);
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
                        grid.getStore().load();
                    }else{
                        Ext.MessageBox.alert(_("Failure"),response.msg);
                    }

                },
                failure: function(xhr){
                    Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                }
            });
        }
    });


}

function CheckAndRemoveStorage(storage_id,node,grid,message_text){
    var url="/storage/is_storage_allocated?storage_id="+storage_id; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                if(response.msg == "IN_USE") {
                    Ext.MessageBox.confirm(_("确认"),"更多的虚拟机正在使用同一存储。确定要继续吗?",function(id){
                        if(id=='yes'){
                            removeStorage(storage_id,node,grid);
                        }
                    });
                } else {
                    Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                        if(id=='yes'){
                            removeStorage(storage_id,node,grid);
                        }
                    });
                }
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function removeStorage(storage_id,node,grid){
    var url="/storage/remove_storage_def?" + sSiteId + op_level + sGroupId + "&storage_id="+storage_id; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                //Ext.MessageBox.alert(_("Info"),response.msg);
                grid.getStore().load();
                //storage_dc_grid.getStore().load();
                DelayReloadStorageDefList();
                Ext.MessageBox.alert("成功", "任务已经提交.");
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function reloadStorageDefList(){
    storage_grid.getStore().load();
}

//Start - Changes from Showing definition status
function showStorageDetailsLink(data,cellmd,record,row,col,store) {
    if(data != "") {
        var server_id = record.get("id");
        var storage_sync_details = record.get("details");
        var returnVal = '<a href="#" onClick="showStorageSyncDetails()">Details</a>';
        return returnVal;
    }
    else {
        return data;
    }
}

function showSyncStatus(data,cellmd,record,row,col,store) {
    if(data != "") {
        var sStatus = record.get("status");
        var icon;
        if (sStatus=="OUT_OF_SYNC"){
            icon="out-of-sync-icon"
        }else if(sStatus=="IN_SYNC"){
            icon="in-sync-icon"
        }

        var returnVal = '<img width=13 height=13 src=../icons/'+icon+'.png/> ';
        return returnVal;
    }
    else {
        return data;
    }
}

function showStorageSyncDetails() {
    var rec = server_grid.getSelectionModel().getSelected();
    var storage_sync_details = rec.get('details');

    if (storage_sync_details == null) {
        storage_sync_details = "No details found";
    }
    txt_details.setValue(storage_sync_details);
    win_detail_status.show(this);
}

var txt_details=new Ext.form.TextArea({
    readOnly:true
});

var win_detail_status = new Ext.Window({
    title: '同步详情',
    layout:'fit',
    width:300,
    height:300,
    closeAction:'hide',
    plain: true,
    items:[txt_details],
    bbar:[{xtype: 'tbfill'},
        new Ext.Button({
            text:"确定",
            icon:'icons/accept.png',
            cls:'x-btn-text-icon',
            listeners: {
                click: function(btn) {
                    win_detail_status.hide();
                }
            }
        })
    ]
});

function showStorageDefStatusLink(data,cellmd,record,row,col,store) {
    var returnVal = "";
    if(data != "") {
        var def_id = record.get("id");
        var sStatus = record.get("status");
        var associated = record.get("associated");

        var fn = "showServerStorageDefList('" + def_id + "','" + sStatus + "')";
        var icon;
        if (sStatus=="OUT_OF_SYNC"){
            icon="out-of-sync-icon"
        }else if(sStatus=="IN_SYNC"){
            icon="in-sync-icon"
        }

        returnVal = '<a href="#" onClick=' + fn + '> <img width=13 height=13 src=../icons/'+icon+'.png/> </a>';
        //if(selNode.attributes.nodetype == 'DATA_CENTER' || selNode.attributes.nodetype == 'SERVER_POOL'){
        if(selNode.attributes.nodetype == 'SERVER_POOL'){
            if (associated == false) {
                returnVal = ""; //If difinition is not associated with any server then show status as blank
            }
        }
    }
    return returnVal;
}

function showServerStorageDefList(id, sStatus) {
    var win, storageId;
    //get selected definition id
    var hide_serverpool = true;
    if (sGroupId == "") {   //DC level
        hide_serverpool = false;
    }

    if(checkSelectedStorage(storage_grid)){
        storageId = storage_grid.getSelectionModel().getSelected().get('id');
        sel_def_name = storage_grid.getSelectionModel().getSelected().get('name');
    }

    var lbl_desc=new Ext.form.Label({
        html:"<div><font size='2'><i>这代表选定的存储连接状态的服务器列表.</i></font></div><br/>"
    });

    var label_level = "";
    if(selNode.attributes.nodetype == 'DATA_CENTER'){
        label_level = "Site";
    } else {
        label_level = "Server Pool";
    }

    var lbl_server=new Ext.form.Label({
        html:"<div><font size='2'><i><b>" + label_level + "</b> - " + selNode.attributes.text + ". <br /><b>Storage</b> - " +  sel_def_name + "</i></font></div>"
    });

    var serverDefListColumnModel = new Ext.grid.ColumnModel([
        {header: "编号", hidden: true, dataIndex: 'id'},
        {header: "服务器池", width: 125, hidden: hide_serverpool, sortable: true, dataIndex: 'serverpool'},
        {header: "服务器", width: 125, sortable: true, dataIndex: 'name'},
        {header: "状态", width: 90, sortable: true, renderer: showSyncStatus, dataIndex: 'status'},
        {header: "详情", width: 90, sortable: true, renderer: showStorageDetailsLink, dataIndex: 'details_link'},
        {header: "详情", hidden: true, dataIndex: 'details'}
    ]);

    var serverDefListStore = new Ext.data.JsonStore({
        url: '/storage/get_server_storage_def_list?' + sSiteId + sGroupId + '&def_id=' + storageId + '&defType=STORAGE',
        root: 'rows',
        fields: ['id', 'name', 'status', 'details', 'serverpool'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert("Error",store_response.msg);
            }
        }
    });
    serverDefListStore.load();

    var serverDefListSelModel = new Ext.grid.RowSelectionModel({
            singleSelect: false
    });
    
    server_grid = new Ext.grid.GridPanel({
        store: serverDefListStore,
        colModel:serverDefListColumnModel,
        stripeRows: true,
        frame:true,
        autoScroll:true,
        selModel:serverDefListSelModel,
        width:420,  //372,
        //autoExpandColumn:2,
        height:195, //157,
        enableHdMenu:false
    });
    
    // create the window on the first click and reuse on subsequent clicks
    win = new Ext.Window({
        title: '状态',
        layout:'fit',
        width:450,
        height:350,
        closeAction:'hide',
        plain: true,
        items: new Ext.Panel({
            id: "serverDefPanel",
            bodyStyle:'padding:10px 0px 0px 0px',
            //width:500,
            //height:300,
            hidemode:"offset",
            frame:true,
            items:[lbl_desc, lbl_server, server_grid]
        }),
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'btnSvrDefListsync',
                id: 'btnSvrDefListsync',
                text:"同步",
                icon:'icons/sync-server-icon.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        //alert("Sync clicked");
                        var server_ids = '';
                        var sm = server_grid.getSelectionModel();
                        var rows = sm.getSelections();
                        for(i=0; i<rows.length; i++) {
                            if(i == rows.length-1) {
                                server_ids += rows[i].get('id');
                            } else {
                                server_ids += rows[i].get('id') + ',';
                            }
                        }
                        //sync the definition with all the linked servers.
                        sync_storage_defn(server_ids, storageId, server_grid);
                    }
                }
            }),
            '-',
            new Ext.Button({
                name: 'btnSvrDefListClose',
                id: 'btnSvrDefListClose',
                text:"关闭",
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        win.hide();
                    }
                }
            })
        ]
    });
    win.show(this);
}

function sync_storage_defn(server_ids, def_id, server_grid){
    if (server_ids == "") {
        Ext.MessageBox.alert("警告","请选择一个服务器.");
        return;
    }

    var url="sync_defn?" + sSiteId + sGroupId + "&server_ids=" + server_ids + "&def_id=" + def_id + "&defType=STORAGE"; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                Ext.MessageBox.alert("成功","同步过程中的任务已经提交");
                //reload data in grid here
                server_grid.getStore().load();
            }else{
                Ext.MessageBox.alert("Failure",response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( "Failure " , xhr.statusText);
        }
    });
}

function sync_all(def_type){
    var url="sync_all?" + sSiteId + sGroupId + "&def_type=" + def_type; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                Ext.MessageBox.alert("成功","同步过程中的任务已经提交");
            }else{
                Ext.MessageBox.alert("Failure",response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( "Failure " , xhr.statusText);
        }
    });
}

function associate_defns(def_type, def_ids){
    if(def_ids == ""){
        Ext.MessageBox.alert("警告","请选择存储");
        return;
    }

    var url="/storage/associate_defns?" + sSiteId + op_level + sGroupId + "&def_type=" + def_type + "&def_ids=" + def_ids; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                DelayReloadStorageDefList();
                Ext.MessageBox.alert("成功", "任务已经提交.");
                //reloadStorageDefList();
                closeWindow(windowid);
                storage_grid.enable();
                //Ext.MessageBox.alert("Success",response.msg);
            }else{
                Ext.MessageBox.alert("Failure",response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( "Failure " , xhr.statusText);
        }
    });
}

function DelayReloadStorageDefList()
{
    is_timer = true;
    strg_load_counter=0;
    initial_strg_count = storage_grid.getStore().getCount();
    if(selNode.attributes.nodetype == 'SERVER_POOL'){
        strg_name_adding = storage_dc_grid.getSelectionModel().getSelected().get('name');
        //alert("strg_name_adding= " + strg_name_adding )
    }
    //check the record count in the grid and if you get record count by +1 and the name of the newly added record then break the following loop. This is called on load event of store.

    strg_timeout = setTimeout("reloadStorageDefList()", 1000); 
}

function DelayReloadStorageDefList_Old()
{
    initial_strg_count = storage_grid.getStore().getCount();
    if(selNode.attributes.nodetype == 'SERVER_POOL'){
        strg_name_adding = storage_dc_grid.getSelectionModel().getSelected().get('name');
        //alert("strg_name_adding= " + strg_name_adding )
    }
    //check the record count in the grid and if you get record count by +1 and the name of the newly added record then break the following loop. This is called on load event of store.
    i=0;
    for (var i=1; i<=10; i++)
    {
        DelayReload();
    }
    return i
}

function DelayReload()
{
    //Call function after every second
    setTimeout("reloadStorageDefList()", 1000); 
    is_timer = true;
}
//End - Changes from Showing definition status
