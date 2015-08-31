/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var sec_group_grid, sec_group_panel;
var sg_deleted_record_list;
function SecGroupList(vdc_id, windowid_sg,refresh_btn){
    /*
    windowid_sg: window id (e.g., windowid_sg=Ext.id();)
    */

    var deleted_account_id, deleted_region_id;

    //initialize variables
    sg_deleted_record_list="";

    var acc_id, region_id;
    var sec_group_store = new Ext.data.JsonStore({
        url: '/cloud_network/get_sec_group_list?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id,
        root: 'rows',
        fields: ['id', 'name', 'description', 'region', 'region_id', 'account_name', 'account_id', 'record_new', 'record_modified', 'rules_store'],
        successProperty:'success',
        listeners:{
            load:function(my_store, records, options){
                //alert("Loading...");
                //alert(my_store.getCount());
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    sec_group_store.load();

    var columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), hidden: true, dataIndex: 'id'},
        {header: _("名称"), width: 100, sortable: true, dataIndex: 'name'},
        {header: _("说明"), width: 150, sortable: true, dataIndex: 'description'},
        {header: _("区域"), width: 100, hidden: false, sortable: true, dataIndex: 'region'},
        {header: _("区域编号"), hidden: true, sortable: true, dataIndex: 'region_id'},
        {header: _("账户"), width: 100, hidden: false, sortable: true, dataIndex: 'account_name'},
        {header: _("账户编号"), hidden: true, sortable: true, dataIndex: 'account_id'},
        {header: _("新的记录"), width: 100, hidden: true, sortable: true, dataIndex: 'record_new'},
        {header: _("修改记录"), width: 100, hidden: true, sortable: true, dataIndex: 'record_modified'},
        {header: _("Rules Store"), width: 100, hidden: true, sortable: true, dataIndex: 'rules_store'}
    ]);
    

    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var new_button=new Ext.Button({
        name: 'add_key',
        id: 'add_key',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                sec_group_grid.getSelectionModel().clearSelections();
                var windowid_sgd = Ext.id();
                showWindow(_("创建安全组"), 500, 390, SecGroupDetails(vdc_id, "NEW", null, windowid_sgd), windowid_sgd); //380, 365
            }
        }
    });
    
    var remove_button=new Ext.Button({
        name: 'remove_key',
        id: 'remove_key',
        text:_("移除"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedGroup(sec_group_grid)){
                    if(sec_group_grid.getSelectionModel().getCount()>0){
                        var sec_group_name, acc_id, region_id;
                        if (sec_group_grid.getSelectionModel().getSelected() != undefined) {
                            var rec=sec_group_grid.getSelectionModel().getSelected();
                            sec_group_name = rec.get('name');
                            
                            var message_text = "确定要移除安全组(" + sec_group_name + ")吗?";
                            Ext.MessageBox.alert(_("信息"),_(message_text));
                            Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                                if(id=='yes'){
                                    acc_id = rec.get('account_id');
                                    region_id = rec.get('region_id');
        
                                    rec_id = rec.get('id');
                                    rec_name = rec.get('name');
                                    rec_region_id = rec.get('region_id');
                                    rec_account_id = rec.get('account_id');
                                    deleted_region_id = rec.get('region_id');
                                    deleted_account_id = rec.get('account_id');
        
        
                                    var sg_store = sec_group_grid.getStore();
                                    var obj_SG = new Object();
        
                                    if(sg_deleted_record_list.length >= 2) {    //e.g., []
                                        sg_deleted_record_list = String(sg_deleted_record_list).replace("]", ",");
                                    } else if(sg_deleted_record_list.length == 0) {
                                        sg_deleted_record_list = "["
                                    }
                                    var record_dic = "{";
                                    if(rec_id != "" &&  rec_id != undefined) {
                                        record_dic += 'id:"' + rec_id + '"';
                                        record_dic += ',name:"' + rec_name + '"';
                                        record_dic += ',region_id:"' + rec_region_id + '"';
                                        record_dic += ',account_id:"' + rec_account_id + '"';
                                    }
                                    record_dic += "}";
                                    sg_deleted_record_list += record_dic;
                                    sg_deleted_record_list += "]";
                    
        //                             alert("sg_deleted_record_list=" + sg_deleted_record_list);
                                    sec_group_grid.getStore().remove(rec);

                                    var sg_deleted_data;
                                    if(sg_deleted_record_list.length <= 4) {    //e.g., [{}]
                                        sg_deleted_data="NONE";
                                    } else if(sg_deleted_record_list.length > 4) {  //e.g., [{}]
                                        var obj_SG = new Object();
                                        //alert("---------"+sg_deleted_record_list);
                                        sg_deleted_record_list = eval(sg_deleted_record_list);
                                        obj_SG.records = sg_deleted_record_list;
                                        sg_deleted_data = Ext.util.JSON.encode(obj_SG);
                                        if(!acc_id) {
                                            acc_id = deleted_account_id;
                                        }
                                        if(!region_id) {
                                            region_id = deleted_region_id;
                                        }
                                    }
                                    removeSecurityGroup(vdc_id, acc_id, region_id, sg_deleted_data, sec_group_name)
                                    sg_deleted_record_list = "";//Reset global var
                                }
                            });
                        }
                    }
                }
            }
        }
    });
    
    var edit_button=new Ext.Button({
        name: 'edit_key',
        id: 'edit_key',
        text:_("编辑"),
        icon:'icons/storage_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedGroup(sec_group_grid)){
                    var rec=sec_group_grid.getSelectionModel().getSelected();
                    windowid_sgd=Ext.id();
                    showWindow(_("编辑安全组"), 500, 390, SecGroupDetails(vdc_id, "EDIT", rec, windowid_sgd), windowid_sgd);
                }
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
                        title :_('导入安全组'),
                        width :650,
                        height:400,
                        modal : true,
                        resizable : false
                    });

                var module = "SECURITY_GROUP";
                var panal=Import_Security_Group(nw, wait_win, vdc_id, module);
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

    var cancel_button = new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('关闭'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {closeWindow(windowid_sg);}
        }
    });

    var tf_search = new Ext.form.TextField({
        fieldLabel: '搜索',
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
                sec_group_store.filter('name', search_text);
            }
        }
    });
    var cut_tbar = new Array();
    cut_tbar.push({xtype: 'tbfill'});
    cut_tbar.push('搜索: ',tf_search);
    cut_tbar.push(search_button);
    cut_tbar.push('-');
    cut_tbar.push(new_button);
    cut_tbar.push('-');
    cut_tbar.push(edit_button);
    cut_tbar.push('-');
    cut_tbar.push(remove_button);;
    cut_tbar.push('-');
    if(refresh_btn==true){
        cut_tbar.push(refresh_button);
        cut_tbar.push('-');
    }

    sec_group_grid = new Ext.grid.GridPanel({
        store: sec_group_store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:selmodel,
        width:472, //415
        height:385, //405
        enableHdMenu:false,
        tbar:cut_tbar,
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                edit_button.fireEvent('click',edit_button);
            }
         }
    });
    
    var lbl=new Ext.form.Label({
         html:'<div style="" class="labelheading">安全组确定一个网络端口允许/阻止您连接实例。下面列表代表所有帐户和区域的安全组.</div>'
    });

    sec_group_panel = new Ext.Panel({
        labelWidth:50,
        bodyStyle:'padding:0px 0px 0px 0px',
        width:485,//430
        height:468,
        frame:true,
        items:[lbl, sec_group_grid]
        ,bbar:[{xtype: 'tbfill'},
            cancel_button
        ]
    });

    return sec_group_panel;
}

function checkSelectedGroup(grid){
    if(grid.getSelections().length==0){
        Ext.MessageBox.alert(_("警告"),_("请选择一个安全组"));
        return false;
    }
    return true;
}

function removeSecGroup(sec_group_name){
    var url='/cloud_network/delete_security_group?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&sec_group_name=' + sec_group_name; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                reloadSecGroupList();
                Ext.MessageBox.alert("成功", response.msg);
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}

function reloadSecGroupList(){
    sec_group_grid.getStore().load();
}

function wait_for_sg_task(task_id, wait_time, wait_msg, success_msg, windowid_sg, mode, vdc_id){
    //alert("waiting for task completion...");
    //alert("mode is " + mode);
    var url = '/cloud_network/wait_for_task?task_id=' + task_id + '&wait_time=' + wait_time;
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
                if(mode != "PROVISION") {
                    reloadSecGroupList();
                } else {
                       Ext.getCmp("security_group_grid").getStore().load({
                             params:{
                                 vdc_id:vdc_id,
                                 acc_id:Ext.getCmp('account').getValue(),
                                 region_id:Ext.getCmp("region_general").getValue(),
                                 sec_type:"provision"
                             }

                            }
                       );
                }
                Ext.MessageBox.alert("信息", success_msg);
                closeWindow(windowid_sg);
            }else{
                Ext.MessageBox.alert(_("失败"), response.status);
                closeWindow(windowid_sg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }

    });
}

function refresh_list_sg(w, sel_secgroups, vdc_id, module){
    //alert("refreshing list...");
    var url = '/cloud_network/save_imported_items_from_cloud?items=' + sel_secgroups + '&vdc_id=' + vdc_id + '&module=' + module;
    //alert("url is " + url);

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var task_id = response.task_id;
                var wait_time = 3000;
                wait_for_refresh_sg_task(task_id, wait_time)
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


function wait_for_refresh_sg_task(task_id, wait_time){
    //alert("waiting for task completion...");
    var url = '/cloud_network/wait_for_task?task_id=' + task_id + '&wait_time=' + wait_time;
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
                reloadSecGroupList();
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


function removeSecurityGroup(vdc_id, acc_id, region_id, sg_deleted_data, sg_name){
    var url='/cloud_network/remove_security_group?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&sg_deleted_data=' + sg_deleted_data;
    // alert("url=" + url);
    var msg=_('正在移除安全组...');
    
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var task_id = response.task_id;
                var wait_time = 3000;
                var wait_msg = '正在移除安全组....';
                var success_msg = "安全组 " + sg_name + "成功移除.";
                wait_for_sg_task(task_id, wait_time, wait_msg, success_msg, null);
            }else{
                Ext.MessageBox.alert("失败",response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( "失败 " , xhr.statusText);
        }
    });
}



function Import_Security_Group(w, wait_win, vdc_id, module)
{

    var tlabel_security_group=new Ext.form.Label({
        html:'<div>'+_("导入安全组")+'<br/></div>'
    });

    var label_security_group=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("安全组")+'<br/></div>'
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

                var l = security_group_store.getTotalCount();
                var sec_group_list = new Array();
                for (var i=0;i<l;i++){
                    var r = security_group_store.getAt(i);
                    if(r.get("is_selected")){
                       var dt = {
                                'id' : r.get('id'),
                                'name' : r.get('name'),
                                'description' : r.get('description'),
                                'region' : r.get('region')
                            }
                      sec_group_list.push(dt);
                    }
                }

                if(sec_group_list.length == 0){
                     Ext.MessageBox.alert(_("错误"),_("请选择一个安全组"));
                     return;
                }
                refresh_list_sg(w, Ext.util.JSON.encode(sec_group_list), vdc_id, module)

            }
        }
    });


    var security_group_store = new Ext.data.JsonStore({
        url: '/cloud_network/refresh_list',
        root: 'rows',
        fields: ['id', 'name', 'description', 'region', 'used_by'],
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
    security_group_store.load(args);


//    var selmodel=new Ext.grid.CheckboxSelectionModel({
//            singleSelect:false
//        });

     var security_group_grid = new Ext.grid.GridPanel({
        store: security_group_store,
        enableHdMenu:false,
//        selModel:selmodel,
        id:'security_group_grid',
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
                width: 150,
                sortable: true,
                dataIndex: 'name'
            },
            {
                header: _("说明"),
                width: 150,
                sortable: true,
                dataIndex: 'description'
            },
            {
                header   : '区域',
                width     : 120,
                sortable : true,
                dataIndex: 'region',
                 hidden : false
            },
            {
                header : '所用',
                width  : 100,
                sortable : true,
                dataindex :'used_by',
                hidden : false
            },
            {header:_("选择"),width: 55, sortable: true, dataIndex: 'is_selected', renderer:render_select_checkbox}
        ],

        stripeRows: true,
        height: 310,
        width:620,
        tbar:[label_security_group,{
            xtype: 'tbfill'
             }],
        listeners: {

         }
    });


    var security_group_panel=new Ext.Panel({
        id:"security_group_panel",
        width:630,
        height:367,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        bbar:[{
            xtype: 'tbfill'
        },button_ok, button_cancel],
        items:[tlabel_security_group, security_group_grid]
    });

   var outerpanel=new Ext.FormPanel({
       height: 380,
       width: 640,
       autoEl: {},
       layout: 'column',
       items: [security_group_panel]
   });

   return outerpanel
}