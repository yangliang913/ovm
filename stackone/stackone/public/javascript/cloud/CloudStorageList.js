/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
var cloud_storage_grid;
function CloudStorageList(vdc_id, windowid_strg, node_name,cp_feature,refresh_btn){
    /*
    windowid_strg: window id (e.g., windowid_strg=Ext.id();)
    */
    var w = 100;
    if(!is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT)){
        w = 150;
    }
    var columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), hidden: true, dataIndex: 'id'},
        {header: _("名称"), width: w, sortable: true, dataIndex: 'name'},
        {header: _("说明"), width: w, sortable: true, dataIndex: 'description'},
        {header: _("卷编号"), width: w, sortable: true, dataIndex: 'volume_id'},
        {header: _("大小"), width: 70, hidden: false, sortable: true, dataIndex: 'display_size'},
        {header: _("大小"), hidden: true, sortable: true, dataIndex: 'size'},
        {header: _("大小单元"), hidden: true, sortable: true, dataIndex: 'size_unit'},
        {header: _("快照编号"), width: 100, sortable: true, dataIndex: 'snapshot',
            hidden:!is_feature_enabled(cp_feature, stackone.constants.CF_SNAPSHOT)},
        {header: _("Zone"), width: 100, sortable: true, dataIndex: 'zone',
            hidden:!is_feature_enabled(cp_feature, stackone.constants.CF_REGION)},
        {header: _("Zone Id"), width: 100, hidden: true, sortable: true, dataIndex: 'zone_id'},
        {header: _("区域编号"), hidden: true, sortable: true, dataIndex: 'region_id'},
        {header: _("区域"), width: 100, sortable: true, dataIndex: 'region',
            hidden:!is_feature_enabled(cp_feature, stackone.constants.CF_REGION)},
        {header: _("账户"), width: 100, sortable: true, dataIndex: 'account_name',
            hidden:!is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT)},
        {header: _("账户编号"), hidden: true, sortable: true, dataIndex: 'account_id'},
        {header: _("状态"), width: 80, hidden: true, sortable: true, dataIndex: 'status'},
        {header: _("附件信息"), width: 150, hidden: true, sortable: true, dataIndex: 'attach_info'},
        {header: _("所用"), width: w, hidden: false, sortable: true, dataIndex: 'vm_name'},
        {header: _("所用"), width: 100, hidden: true, sortable: true, dataIndex: 'used_by'}
        ]);

    var acc_id, region_id;
    var volume_store = new Ext.data.JsonStore({
        url: '/cloud_storage/get_volume_list?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id,
        root: 'rows',
        fields: ['id', 'name', 'description', 'volume_id', 'display_size', 'size', 'size_unit', 'snapshot', 'zone', 'zone_id', 'region_id', 'region', 'account_id', 'account_name', 'status', 'attach_info', 'used_by', 'vm_name'],
        successProperty:'success'
    });
    volume_store.load();

    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var create_snapshot_button=new Ext.Button({
        name: 'create_snapshot_button',
        id: 'create_snapshot_button',
        text:_("新建快照"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var rec = cloud_storage_grid.getSelectionModel().getSelected();
                if(!rec) {
                    Ext.MessageBox.alert("错误", "请选择一个存储");
                    return;
                }
                var windowId = Ext.id();
                showWindow(_("创建快照"), 350, 227, CloudSnapshotDefinition(vdc_id, "NEW", rec, windowId), windowId); //350, 200
            }
        }
    });

    var snapshot_list_button=new Ext.Button({
        name: 'snapshot_list_button',
        id: 'snapshot_list_button',
        text:_("快照列表"),
        icon:'icons/vm_list.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var rec = cloud_storage_grid.getSelectionModel().getSelected();
                if(!rec) {
                    Ext.MessageBox.alert("错误", "请选择一个存储");
                    return;
                }

                var acc_id = rec.get("account_id");
                var region_id = rec.get("region_id");
                var volume_id = rec.get("volume_id");
                var windowId = Ext.id();
                showWindow(_("快照") + ":- " + node_name, 700, 500, CloudManageSnapshot(vdc_id, acc_id, region_id, volume_id, windowId,cp_feature), windowId);
            }
        }
    });

    var attach_button=new Ext.Button({
        name: 'attach_button',
        id: 'attach_button',
        text:_("附加"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedStorage(cloud_storage_grid)){
                    rec = cloud_storage_grid.getSelectionModel().getSelected();
                    var windowid_csa = Ext.id();
                    showWindow(_("附加存储"), 380, 210, CloudStorageAttachWin(vdc_id, rec, windowid_csa), windowid_csa); //380, 435
                }
            }
        }
    });

    var detach_button=new Ext.Button({
        name: 'detach_button',
        id: 'detach_button',
        text:_("分离"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedStorage(cloud_storage_grid)){
                    rec = cloud_storage_grid.getSelectionModel().getSelected();
                    var storage_name = rec.get('name');
                    var vm_name = rec.get('vm_name');
                    var volume_id = rec.get('volume_id');
                    var instance_id = rec.get('used_by');
                    var acc_id = rec.get('account_id');
                    var region_id = rec.get('region_id');
                    
                    if(instance_id) {
                        var message_text = "你希望从虚拟机(" + vm_name + ")分离(" + storage_name + ") 存储吗 ?";
                        Ext.MessageBox.alert(_("信息"),_(message_text));
                        Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                            if(id=='yes'){
                                detachCloudStorage(vdc_id, acc_id, region_id, volume_id, instance_id, null, null, storage_name, cloud_storage_grid);
                            }
                        });
                    } else {
                        Ext.MessageBox.alert(_("信息"),_("虚拟机没有附加存储."));
                    }

                }
            }
        }
    });

    var strg_defn_width = 380 , strg_defn_height=275;
    if(!is_feature_enabled(cp_feature, stackone.constants.CF_REGION)){
        strg_defn_height=175;
    }
    var new_button=new Ext.Button({
        name: 'add_button',
        id: 'add_button',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                cloud_storage_grid.getSelectionModel().clearSelections();
                var windowid_csd = Ext.id();
                showWindow(_("创建存储"), strg_defn_width, strg_defn_height,
                    CloudStorageDefinition(vdc_id, "NEW", null, windowid_csd, null, null, cp_feature), windowid_csd); //380, 225
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
                if(checkSelectedStorage(cloud_storage_grid)){
                    var storage_name, acc_id, region_id;
                    var rec=cloud_storage_grid.getSelectionModel().getSelected();
                    storage_name=rec.get('name');
                    volume_id=rec.get('volume_id');
                    region_id=rec.get('region_id');
                    acc_id=rec.get('account_id');
                    var message_text = "确定要移除(" + storage_name + ")吗?";
                    Ext.MessageBox.alert(_("信息"),_(message_text));
                    Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                        if(id=='yes'){
                            removeCloudStorage(vdc_id, acc_id, region_id, volume_id, storage_name, cloud_storage_grid);
                        }
                    });
                }
            }
        }
    });
    
    var edit_button=new Ext.Button({
        name: 'edit_button',
        id: 'edit_button',
        text:_("编辑"),
        icon:'icons/storage_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedStorage(cloud_storage_grid)){
                    var rec=cloud_storage_grid.getSelectionModel().getSelected();
                    windowid_csd=Ext.id();
                    showWindow(_("编辑存储"), strg_defn_width, strg_defn_height,
                        CloudStorageDefinition(vdc_id, "EDIT", rec, windowid_csd,null, null, cp_feature), windowid_csd);
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
            click: function(btn) {closeWindow(windowid_strg);}
        }
    });

    var tf_search = new Ext.form.TextField({
        fieldLabel: 'Search',
        name: 'tf_search',
        id: 'tf_search',
        width: 85,
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
                volume_store.filter('name', search_text);
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
                        title :_('导入存储'),
                        width :500,
                        height:400,
                        modal : true,
                        resizable : false
                    });

                var module = "STORAGE";
                var panal=Import_Storage(nw, wait_win, vdc_id, module, cloud_storage_grid);
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
    
    var toolbar_list = new Array();
    toolbar_list.push('搜索: ');
    toolbar_list.push(tf_search);
    toolbar_list.push(search_button,{
        xtype: 'tbfill'});
    toolbar_list.push(new_button,'-');
    toolbar_list.push(edit_button,'-');
    toolbar_list.push(remove_button,'-');
    toolbar_list.push(attach_button,'-');
    toolbar_list.push(detach_button,'-');
    if(is_feature_enabled(cp_feature, stackone.constants.CF_SNAPSHOT)){
        toolbar_list.push(create_snapshot_button,'-');
        toolbar_list.push(snapshot_list_button,'-');                  
    }
    if(refresh_btn==true){
       toolbar_list.push(refresh_button,'-');
    }
        
    cloud_storage_grid = new Ext.grid.GridPanel({
        store: volume_store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:selmodel,
        autoExpandColumn:3,
        width:847, //415 472, 673
        height:405, //365
        enableHdMenu:false,
        tbar:toolbar_list,
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                edit_button.fireEvent('click',edit_button);
            }
         }
    });
    
    var lbl=new Ext.form.Label({
         html:'<div style="" class="labelheading">stackone提供了供实例使用的存储卷。下述代表您的帐户或区域所分配的存储.</div>'
    });

    var cloud_storage_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:860,//430 485 685
        height:468,
        frame:true,
        items:[lbl, cloud_storage_grid]
        ,bbar:[{xtype: 'tbfill'},
            cancel_button
        ]
    });

    return cloud_storage_panel;
}

function checkSelectedStorage(grid){
    if(grid.getSelections().length==0){
        Ext.MessageBox.alert(_("错误"),_("请选择一个存储"));
        return false;
    }
    return true;
}

function removeCloudStorage(vdc_id, acc_id, region_id, volume_id, storage_name, grid){
    var url='/cloud_storage/remove_volume?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&volume_id='+volume_id; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var wait_msg = _('正在移除存储...');
                var success_msg = _("存储" + storage_name + "移除成功.");
                var task_id = response.task_id;
                var wait_time = 3000;
                wait_for_storage_task(task_id, wait_time, wait_msg, success_msg, null, grid);
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}

function reloadStorageList(grid){
    if(grid){
        grid.getStore().load();
    }
}

function detachCloudStorage(vdc_id, acc_id, region_id, volume_id, instance_id, device, force, storage_name, grid, remove_object){
    var url='/cloud_storage/detach_volume?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&volume_id=' + volume_id + '&instance_id=' + instance_id + '&device=' + device + '&force=' + force;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var wait_msg = _('正在分离存储...');
                var success_msg = _("存储 " + storage_name + "分离成功.");
                var task_id = response.task_id;
                var wait_time = 3000;

                var volume_object = null;
                wait_for_storage_task(task_id, wait_time, wait_msg, success_msg, null, grid, volume_object, remove_object);
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}

function wait_for_storage_task(task_id, wait_time, wait_msg, success_msg, task_window_id, grid, volume_object, remove_object){
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
                if(volume_object || remove_object) {
                    Ext.MessageBox.hide();
                } else {
                    reloadStorageList(grid);
                    Ext.MessageBox.alert("信息", success_msg);
                }
                if(task_window_id) {
                    closeWindow(task_window_id);
                }
                //attach newly created storage with the instance. This is for when you are in edit VM mode.
                if(volume_object) {
                    var vdc_id = volume_object.vdc_id;
                    var acc_id = volume_object.acc_id;
                    var region_id = volume_object.region_id;
                    var zone_id = volume_object.zone_id;
                    var instance_id = volume_object.instance_id;
                    var vm_id = volume_object.vm_id;
                    var vm_name = volume_object.vm_name;
                    var storage_name = volume_object.storage_name;

                    var windowid_strg= Ext.id();
                    showWindow(_("附加存储"), 380, 210, CloudStorageAttachAtVMLevel(vdc_id, acc_id, region_id, zone_id, vm_id, vm_name, storage_name, instance_id, null, windowid_strg), windowid_strg);
                }
                
                //remove volume on click of Remove button. This is when you are in edit VM mode.
                if(remove_object) {
                    var vdc_id = remove_object.vdc_id;
                    var account_id = remove_object.account_id;
                    var region_id = remove_object.region_id;
                    var volume_id = remove_object.volume_id;
                    var storage_name = remove_object.storage_name;
                    var r_grid = remove_object.grid;
                    reloadStorageList(r_grid);
                    removeCloudStorage(vdc_id, account_id, region_id, volume_id, storage_name, r_grid);
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


function refresh_list_storage(w, sel_storages, vdc_id, module, grid){
    //alert("refreshing list...");
    var url = '/cloud_network/save_imported_items_from_cloud?items=' + sel_storages + '&vdc_id=' + vdc_id + '&module=' + module;
    //alert("url is " + url);

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var task_id = response.task_id;
                var wait_time = 3000;
                wait_for_refresh_storage_task(task_id, wait_time, grid)
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


function wait_for_refresh_storage_task(task_id, wait_time, grid){
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
                reloadStorageList(grid);
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


function Import_Storage(w, wait_win, vdc_id, module, stor_grid)
{

    var tlabel_storage=new Ext.form.Label({
        html:'<div>'+_("导入存储")+'<br/></div>'
    });

    var label_storage=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("存储")+'<br/></div>'
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

                var l = storage_store.getTotalCount();
                var volume_list = new Array();
                for (var i=0;i<l;i++){
                    var r = storage_store.getAt(i);
                    if(r.get("is_selected")){
                      var dt = {'id' : r.get('id'),
                            'name' : r.get('name'),
                            'size' : r.get('size'),
                            'snapshot_id' : r.get('snapshot_id'),
                            'zone' : r.get('zone'),
                            'region' : r.get('region')}
                    volume_list.push(dt);
                    }
                }

                if(volume_list.length == 0){
                     Ext.MessageBox.alert(_("错误"),_("请选择一个存储"));
                     return;
                }
                refresh_list_storage(w, Ext.util.JSON.encode(volume_list), vdc_id, module, stor_grid)

            }
        }
    });


    var storage_store = new Ext.data.JsonStore({
        url: '/cloud_network/refresh_list',
        root: 'rows',
        fields: ['id', 'name', 'size', 'snapshot_id', 'zone', 'region', 'used_by','is_selected'],
        successProperty:'success',
        listeners:{
            load:function(store){
                wait_win.hide();
            }
        }
    });


    var args = {params:{vdc_id:vdc_id,
                            module:module
                        }
                };
    storage_store.load(args);


    var selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });

     var storage_grid = new Ext.grid.GridPanel({
        store:storage_store,
        enableHdMenu:false,
        selModel:selmodel,
        id:'storage_grid',
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
                header: _("大小"),
                width: 40,
                sortable: true,
                dataIndex: 'size'
            },
            {
                header: _("快照编号"),
                width: 85,
                sortable: true,
                dataIndex: 'snapshot_id'
            },
            {
                header: _("Zone"),
                width: 65,
                sortable: true,
                dataIndex: 'zone'
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
                width  : 55,
                sortable : true,
                dataindex :'used_by',
                hidden : false
            },
            {header:_("选择"),width: 40, sortable: true, dataIndex: 'is_selected', renderer:render_select_checkbox}
        ],

        stripeRows: true,
        height: 310,
        width:475,
        tbar:[label_storage,{
            xtype: 'tbfill'
             },],
        listeners: {

         }
    });


    var storage_panel=new Ext.Panel({
        id:"stroage_panel",
        width:490,
        height:367,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        bbar:[{
            xtype: 'tbfill'
        },button_ok, button_cancel],
        items:[tlabel_storage, storage_grid]
    });

   var outerpanel=new Ext.FormPanel({
       height: 380,
       width: 495,
       autoEl: {},
       layout: 'column',
       items: [storage_panel]
   });

   return outerpanel
}