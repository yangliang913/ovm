/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
var cloud_snapshot_grid;
function CloudManageSnapshot(vdc_id, acc_id, region_id, volume_id, windowId,cp_feature){
    /*
    parameter info:
    vdc_id: virtual data center id
    acc_id: account id
    region_id: region id
    volume_id: storage disk id (external id)
    windowId: window id (e.g., windowId=Ext.id();)
    */
    var columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), hidden: true, dataIndex: 'id'},
        {header: _("名称"), width: 100, sortable: true, dataIndex: 'name'},
        {header: _("说明"), width: 150, sortable: true, dataIndex: 'description'},
        {header: _("快照编号"), width: 120, sortable: true, dataIndex: 'snapshot_id'},
        {header: _("大小"), width: 80, hidden: false, sortable: true, dataIndex: 'display_size'},
        {header: _("大小"), hidden: true, sortable: true, dataIndex: 'size'},
        {header: _("大小单位"), hidden: true, sortable: true, dataIndex: 'size_unit'},
        {header: _("区域编号"), hidden: true, sortable: true, dataIndex: 'region_id'},
        {header: _("区域"), width: 100, hidden: false, sortable: true, dataIndex: 'region'},
        {header: _("账户"), width: 100, hidden: false, sortable: true, dataIndex: 'account_name'},
        {header: _("账户编号"), hidden: true, sortable: true, dataIndex: 'account_id'}
        ]);

    var snapshot_store = null;
    if(volume_id){
        snapshot_store = new Ext.data.JsonStore({
            url: '/cloud_storage/get_snapshots_of_storage?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&volume_id=' + volume_id,
            root: 'rows',
            fields: ['id', 'name', 'description', 'snapshot_id', 'display_size', 'size', 'size_unit', 'region_id', 'region', 'account_name', 'account_id'],
            successProperty:'success'
        });
        snapshot_store.load();
    } else {
        snapshot_store = new Ext.data.JsonStore({
            url: '/cloud_storage/get_all_snapshots?vdc_id=' + vdc_id,
            root: 'rows',
            fields: ['id', 'name', 'description', 'snapshot_id', 'display_size', 'size', 'size_unit', 'region_id', 'region', 'account_name', 'account_id'],
            successProperty:'success'
        });
        snapshot_store.load();
    }

    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    //in the 'Snapshot List' panel.
    var create_storage_button=new Ext.Button({
        name: 'create_storage_button',
        id: 'create_storage_button',
        text:_("创建存储"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var snapshot_rec = cloud_snapshot_grid.getSelectionModel().getSelected();
                var windowId = Ext.id();
                var storage_rec = null;
                var vm_info = null;

                if(snapshot_rec == undefined){
                    Ext.MessageBox.alert('错误','请选择一个快照');
                    return false;
                }

                showWindow(_("创建存储"), 380, 275, CloudStorageDefinition(vdc_id, "NEW", storage_rec, windowId, vm_info, snapshot_rec,cp_feature), windowId); //380, 225

            }
        }
    });

    var new_button=new Ext.Button({
        name: 'add_button',
        id: 'add_button',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var windowId = Ext.id();
                var storage_rec = null;
                showWindow(_("创建快照"), 350, 227, CloudSnapshotDefinition(vdc_id, "NEW", storage_rec, windowId), windowId);
            }
        }
    });
    
    var remove_button=new Ext.Button({
        name: 'remove_button',
        id: 'remove_button',
        text:_("移除"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedSnapshot(cloud_snapshot_grid)){
                    var rec=cloud_snapshot_grid.getSelectionModel().getSelected();
                    var snapshot_name=rec.get('name');
                    var snapshot_id=rec.get('snapshot_id');
                    var region_id=rec.get('region_id');
                    var acc_id=rec.get('account_id');
                    var message_text = "确定要移除(" + snapshot_name + ")快照吗?";
                    Ext.MessageBox.alert(_("信息"),_(message_text));
                    Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                        if(id=='yes'){
                            removeCloudSnapshot(vdc_id, acc_id, region_id, snapshot_id, snapshot_name, cloud_snapshot_grid);
                        }
                    });
                }
            }
        }
    });
    
    var cancel_button = new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('关闭'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {closeWindow(windowId);}
        }
    });

    var tf_search = new Ext.form.TextField({
        fieldLabel: '搜索',
        name: 'tf_search',
        id: 'tf_search',
        width: 120,
        allowBlank:true,
        enableKeyEvents:true
    });

    var search_button = new Ext.Button({
        id: 'search_button',
        name: 'search_button',
        tooltip:'搜索',
        tooltipType : "title",
        icon:'icons/search.png',
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                var search_text = tf_search.getValue();
                snapshot_store.filter('name', search_text);
            }
        }
    });

    var refresh_button=new Ext.Button({
        name: 'refresh_button',
        id: 'refresh_button',
        text:_("导入"),
        icon:'icons/refresh.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                var wait_win = Ext.MessageBox.show({
                        title:_('请稍候...'),
                        msg: '请稍候...',
                        width:300,
                        wait:true,
                        waitConfig: {
                            interval:200
                        }
                    }).hide();//hide

                var nw=new Ext.Window({
                        title :_('导入快照'),
                        width :500,
                        height:400,
                        modal : true,
                        resizable : false
                    });

                var module = "SNAPSHOT";
                var panal=Import_Snapshot(nw, wait_win, vdc_id, module, volume_id, cloud_snapshot_grid);
                nw.add(panal);
                nw.show();

                //this has to be call only after nw.show();
                //reinitializes an existing message box wait_win.
                wait_win.show({
                            title:_('请稍候...'),
                            msg: '请稍候...',
                            width:300,
                            wait:true,
                            waitConfig: {
                                interval:200
                            }
                        });//show

            }
        }
    });

    cloud_snapshot_grid = new Ext.grid.GridPanel({
        store: snapshot_store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:selmodel,
        width:672, //415 472, 673
        height:405, //365
        enableHdMenu:false,
        tbar:[{xtype: 'tbfill'},
            '搜索: ', tf_search,
            search_button,
            '-',
            remove_button,
            '-',
            create_storage_button,
            '-',
            refresh_button
        ]
    });
    
    var lbl="";
    if(volume_id){
        var storage_rec = cloud_storage_grid.getSelectionModel().getSelected();
        
        lbl=new Ext.form.Label({
            html:'<div style="" class="labelheading">This provides snapshots for creating storage. The list represents snapshot of storage ' + storage_rec.get('name') + '.</div>'
        });
    } else {
        lbl=new Ext.form.Label({
            html:'<div style="" class="labelheading">This provides snapshots for creating storage. The list represents snapshot from all accounts and regions.</div>'
        });
    }




    var cloud_snapshot_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:685,//430 485
        height:468,
        frame:true,
        items:[lbl, cloud_snapshot_grid]
        ,bbar:[{xtype: 'tbfill'},
            cancel_button
        ]
    });

    return cloud_snapshot_panel;
}

function checkSelectedSnapshot(grid){
    if(grid.getSelections().length==0){
        Ext.MessageBox.alert(_("错误"),_("请选择一个快照"));
        return false;
    }
    return true;
}

function removeCloudSnapshot(vdc_id, acc_id, region_id, snapshot_id, snapshot_name, grid){
    var url='/cloud_storage/remove_snapshot?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&snapshot_id=' + snapshot_id; 

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var wait_msg = _('正在移除快照...');
                var success_msg = _("快照" + snapshot_name + "已经成功移除.");
                var task_id = response.task_id;
                var wait_time = 3000;
                wait_for_snapshot_task(task_id, wait_time, wait_msg, success_msg, null, grid);
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}

function reloadSnapshotList(grid){
    if(grid){
        grid.getStore().load();
    }
}

function wait_for_snapshot_task(task_id, wait_time, wait_msg, success_msg, task_window_id, grid){
    //alert("waiting for task completion...");
    var url = '/cloud_storage/wait_for_task?task_id=' + task_id + '&wait_time=' + wait_time;
    //alert("url is " + url);
    Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: wait_msg,
        width:300,
        wait:true,
        waitConfig: {
            interval:3000
        }
    });

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                reloadSnapshotList(grid);
                Ext.MessageBox.alert("信息", success_msg);

                if(task_window_id) {
                    closeWindow(task_window_id);
                }
            }else{
                Ext.MessageBox.alert(_("失败"), response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }

    });
}

function refresh_list_snapshot(w, sel_snapshots, vdc_id, module, grid){
    //alert("refreshing list...");
    var url = '/cloud_network/save_imported_items_from_cloud?items=' + sel_snapshots + '&vdc_id=' + vdc_id + '&module=' + module;
    //alert("url is " + url);

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var task_id = response.task_id;
                var wait_time = 200;
                wait_for_refresh_snapshot_task(task_id, wait_time, grid)
                w.close();
            }else{
                Ext.MessageBox.alert(_("失败"), response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}


function wait_for_refresh_snapshot_task(task_id, wait_time, grid){
    //alert("waiting for task completion...");
    var url = '/cloud_storage/wait_for_task?task_id=' + task_id + '&wait_time=' + wait_time;
    //alert("url is " + url);
    var refresh_win = Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: _('正在刷新列表...'),
        width:300,
        wait:true,
        waitConfig: {
            interval:3000
        }
    });

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                reloadSnapshotList(grid);
                refresh_win.hide();
//                Ext.MessageBox.alert("Info", response.status);
            }else{
                Ext.MessageBox.alert(_("失败"), response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}



function Import_Snapshot(w, wait_win, vdc_id, module, volume_id, snap_grid)
{

    var tlabel_snapshot=new Ext.form.Label({
        html:'<div>'+_("导入快照")+'<br/></div>'
    });

    var label_snapshot=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("快照")+'<br/></div>'
    });

    var button_cancel=new Ext.Button({
    name: 'cancel',
    id: 'cancel',
    text:_('关闭'),
    icon:'icons/cancel.png',
    cls:'x-btn-text-icon',
    listeners: {
        click: function(btn) {
            w.close();
        }
    }
    });


    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                var l = snapshot_store.getTotalCount();
                var snapshot_list = new Array();
                for (var i=0;i<l;i++){
                    var r = snapshot_store.getAt(i);
                    if(r.get("is_selected")){
                      var dt = {'id' : r.get('id'),
                            'name' : r.get('name'),
                            'description' : r.get('description'),
                            'size' : r.get('size'),
                            'volume_id' : r.get('volume_id'),
                            'region' : r.get('region')}
                        snapshot_list.push(dt);
                    }
                }

                if(snapshot_list.length == 0){
                     Ext.MessageBox.alert(_("错误"),_("请选择一个快照"));
                     return;
                }
                refresh_list_snapshot(w, Ext.util.JSON.encode(snapshot_list), vdc_id, module, snap_grid)

            }
        }
    });


    var snapshot_store = new Ext.data.JsonStore({
        url: '/cloud_network/refresh_list',
        root: 'rows',
        fields: ['id', 'name', 'description', 'size', 'volume_id', 'region', 'used_by','is_selected'],
        successProperty:'success',
        listeners:{
            load:function(store){
                wait_win.hide();
            }
        }
    });

    var args = {params:{vdc_id:vdc_id,
                            module:module,
                            context:Ext.util.JSON.encode({'volume_id':volume_id})
                        }
                };
    snapshot_store.load(args);


    var selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });

     var snapshot_grid = new Ext.grid.GridPanel({
        store: snapshot_store,
        enableHdMenu:false,
        selModel:selmodel,
        id:'snapshot_grid',
        columns: [
            {
                id       :'id',
                header   : '编号',
                width    : 0,
                sortable : true,
                dataIndex: 'id',
                hidden : true
            },
            {
                header: _("名称"),
                width: 75,
                sortable: true,
                dataIndex: 'name'
            },
            {
                header: _("说明"),
                width: 160,
                sortable: true,
                dataIndex: 'description'
            },
            {
                header: _("大小"),
                width: 40,
                hidden: false,
                sortable: true,
                dataIndex: 'size'
            },
            {
                header: _("volume_id"),
                width: 80,
                hidden: true,
                sortable: true,
                dataIndex: 'volume_id'
            },
            {
                header   : '区域',
                width     : 65,
                sortable : true,
                dataIndex: 'region',
                 hidden : false
            },
            {
                header : 'Used_by',
                width  : 80,
                sortable : true,
                dataindex :'used_by',
                hidden : false
            },
            {header:_("选择"),width: 40, sortable: true, dataIndex: 'is_selected', renderer:render_select_checkbox}
        ],

        stripeRows: true,
        height: 310,
        width:475,
        tbar:[label_snapshot,{
            xtype: 'tbfill'
             },],
        listeners: {

         }
    });


    var snapshot_panel=new Ext.Panel({
        id:"snapshot_panel",
        width:490,
        height:367,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        bbar:[{
            xtype: 'tbfill'
        },button_ok, button_cancel],
        items:[tlabel_snapshot, snapshot_grid]
    });

   var outerpanel=new Ext.FormPanel({
       height: 380,
       width: 495,
       autoEl: {},
       layout: 'column',
       items: [snapshot_panel]
   });

   return outerpanel
}
