/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
var public_ip_grid, public_ip_panel;
function PublicIPList(vdc_id, windowid_ip, cp_feature,refresh_btn){

//    if(is_feature_enabled(cp_feature,stackone.constants.CF_ACCOUNT))
//         accounthide=false
//    else
//        accounthide=true
//
//    if(is_feature_enabled(cp_feature,stackone.constants.CF_REGION))
//    regionhide=false
//    else
//    regionhide=true

    var hide_name = true;
    var hide_desc = true;
    var hide_reg = false;
    var hide_acc = false;

    var ip_width = 150;
    var inst_width = 150;
    var reg_width = 150;
    var acc_width = 150;

    if(!is_feature_enabled(cp_feature, stackone.constants.CF_REGION))
    {//dont need edit button for CMS
//        hide_name = true;
//        hide_desc = true;
        hide_reg = true;
        hide_acc = true;
        //adjust column width for CMS
        ip_width = 300;
        inst_width = 300;
    }


    var columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), hidden: true, dataIndex: 'id'},
        {header: _("名称"), width: 80, sortable: true, dataIndex: 'name', hidden:hide_name},
        {header: _("说明"), width: 150, sortable: true, dataIndex: 'description', hidden:hide_desc},
        {header: _("公共IP"), width: ip_width, sortable: true, dataIndex: 'public_ip'},
        {header: _("虚拟机"), width: inst_width, hidden: false, sortable: true, dataIndex: 'instance_name'},
        {header: _("区域"), width: reg_width, sortable: true, dataIndex: 'region', hidden:hide_reg},
        {header: _("区域编号"), hidden: true, sortable: true, dataIndex: 'region_id'},
        {header: _("账户"), width: acc_width, sortable: true, dataIndex: 'account_name', hidden:hide_acc},
        {header: _("账户编号"), hidden: true, sortable: true, dataIndex: 'account_id'}
        ]);

    var store = new Ext.data.JsonStore({
        url: '/cloud_network/get_public_ip_list?vdc_id=' + vdc_id,
        root: 'rows',
        fields: ['id', 'name', 'description', 'public_ip', 'instance_name', 'region', 'region_id', 'account_id', 'account_name'],
        successProperty:'success'
    });
    store.load();

    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

//    var req_pub_ip_win_height = 125;
//    if(!is_feature_enabled(cp_feature, stackone.constants.CF_REGION)){
//        req_pub_ip_win_height = 100;
//    }
    
    var new_button=new Ext.Button({
        name: 'add_ip',
        id: 'add_ip',
        text:_("请求"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                public_ip_grid.getSelectionModel().clearSelections();
                var windowid=Ext.id();
                if(is_feature_enabled(cp_feature, stackone.constants.CF_REGION)){
                    showWindow(_("请求公共IP"),380,140,PublicIPDefinition(vdc_id, "NEW", null, windowid, cp_feature),windowid);//435
                }
                else{
                        var message_text = "确定要请求新的公共IP吗?";
                        Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                            if(id=='yes'){
                                request_public_ip(vdc_id, "", "", "NEW", null)
                            }
                        });

                }
            }
        }
    });

    var remove_button=new Ext.Button({
        name: 'remove_ip',
        id: 'remove_ip',
        text:_("释放"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedPublicIP(public_ip_grid)){
                    if(public_ip_grid.getSelectionModel().getCount()>0){
                        var acc_id, region_id, public_ip;
                        if (public_ip_grid.getSelectionModel().getSelected() != undefined) {
                            var rec=public_ip_grid.getSelectionModel().getSelected();
                            var public_ip_id=rec.get('id');
                            var public_ip=rec.get('public_ip');
                            var acc_id=rec.get('account_id');
                            var region_id=rec.get('region_id');
                            var instance_name = rec.get('instance_name');
                            var message_text="";
                            
                            if(instance_name){
                                message_text="公共IP ("+ public_ip +") 与虚拟机 ("+instance_name+")关联, 释放它将导致虚拟机无法联网。确定要释放 ("+ public_ip +")吗? " ;
                            }else{
                                message_text = "确定要释放公共IP (" + public_ip + ")吗?";
                            }
                            
                            Ext.MessageBox.alert(_("信息"),_(message_text));
                            Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                                if(id=='yes'){
                                    removePublicIP(vdc_id, acc_id, region_id, public_ip, public_ip_id);
                                }
                            });
                        }
                    }
                }
            }
        }
    });
    var edit_button=new Ext.Button({
        name: 'edit_ip',
        id: 'edit_ip',
        text:_("编辑"),
        icon:'icons/storage_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedPublicIP(public_ip_grid)){
                    var rec=public_ip_grid.getSelectionModel().getSelected();
                    var windowid=Ext.id();
                    showWindow(_("编辑公共IP"),380,190,PublicIPDefinition(vdc_id,"EDIT",rec,windowid),windowid);
                }
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
                if(checkSelectedPublicIP(public_ip_grid)){
                    rec = public_ip_grid.getSelectionModel().getSelected();
                    var windowid_csa = Ext.id();
                    showWindow(_("附加公共IP"), 400, 150, PublicIPAttachWin(vdc_id, rec, windowid_csa), windowid_csa); //380, 435
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
                if(checkSelectedPublicIP(public_ip_grid)){
                    var rec = public_ip_grid.getSelectionModel().getSelected();
                    var public_ip_id = rec.get('id');
                    var public_ip = rec.get('public_ip');
                    var acc_id = rec.get('account_id');
                    var region_id = rec.get('region_id');
                    var instance_name = rec.get('instance_name');
                    if(instance_name) {
                        var message_text = "确定要分离公共ip (" + public_ip + ")吗?";
                        Ext.MessageBox.alert(_("信息"),_(message_text));
                        Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                            if(id=='yes'){
                                detachPublicIP(vdc_id, acc_id, region_id, public_ip, public_ip_id);
                            }
                        });
                    } else {
                        Ext.MessageBox.alert(_("信息"), _("公共IP未和实例关联."));
                    }

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


                var w=new Ext.Window({
                        title :_('导入公共IP'),
                        width :500,
                        height:400,
                        modal : true,
                        resizable : false
                    });


                var module = "PUBLIC_IP";
                var p = Import_Public_IP(w, wait_win, vdc_id, module);
                w.add(p);
                w.show();

                //this has to be call only after w.show();
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

    var tf_search = new Ext.form.TextField({
        fieldLabel: '搜索',
        name: 'tf_search',
        id: 'tf_search',
        width: 85,
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {
            }
        }
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
                store.filter('name', search_text);
            }
        }
    });


    var cut_tbar = new Array();
    cut_tbar.push({xtype: 'tbfill'});
//    cut_tbar.push('Search: ');
//    cut_tbar.push(tf_search);
//    cut_tbar.push(search_button);
    cut_tbar.push('-');
    cut_tbar.push(new_button);
//    if(is_feature_enabled(cp_feature, stackone.constants.CF_REGION))
//    {//dont need edit button for CMS
//        cut_tbar.push('-');
//        cut_tbar.push(edit_button);
//    }
    cut_tbar.push('-');
    cut_tbar.push(remove_button);
    cut_tbar.push('-');
    cut_tbar.push(attach_button);
    cut_tbar.push('-');
    cut_tbar.push(detach_button);
    cut_tbar.push('-');
    if(refresh_btn==true)
    {
        cut_tbar.push(refresh_button);
        cut_tbar.push('-');
    }
    

    public_ip_grid = new Ext.grid.GridPanel({
        store: store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:selmodel,
        width:610, //485
        height:385,
        enableHdMenu:false,
        tbar:cut_tbar,
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
//                if(is_feature_enabled(cp_feature, stackone.constants.CF_REGION))
//                {//dont need edit button for CMS
//                    edit_button.fireEvent('click',edit_button);
//                }
            }
         }
    });

    var lbl=new Ext.form.Label({
         html:'<div style="" class="labelheading">公共IP地址即静态IP地址，该列表代表您所有的公共IP地址，以便赋予您的虚拟机及相关应用.</div>'
    });

    public_ip_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        //width:485,//430
        height:468,
        frame:true,
        items:[lbl, public_ip_grid]
        ,bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('关闭'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {closeWindow(windowid_ip);}
                }
            })
        ]
    });

    return public_ip_panel;
}

function checkSelectedPublicIP(grid){
    if(grid.getSelections().length==0){
        Ext.MessageBox.alert(_("警告"),_("请选择一个公共IP"));
        return false;
    }
    return true;
}

function removePublicIP(vdc_id, acc_id, region_id, public_ip, public_ip_id){
    var url='/cloud_network/delete_public_ip?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&public_ip=' + public_ip + '&public_ip_id=' + public_ip_id;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var task_id = response.task_id;
                var wait_time = 3000;
                var wait_msg = _('正在释放IP...');
                var success_msg = _("公共IP " + public_ip + "释放成功.");
                wait_for_public_ip_task(task_id, wait_time, wait_msg, success_msg, null);
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}

function detachPublicIP(vdc_id, acc_id, region_id, public_ip, public_ip_id){
    var url='/cloud_network/detach_public_ip?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&public_ip=' + public_ip + '&public_ip_id=' + public_ip_id;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var task_id = response.task_id;
                var wait_time = 3000;
                var wait_msg = _('正在分离公共IP...');
                var success_msg = _("公共IP " + public_ip + " 分离成功.");
                wait_for_public_ip_task(task_id, wait_time, wait_msg, success_msg, null);
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}

function reloadPublicIPList(){
    public_ip_grid.getStore().load();
}

function wait_for_public_ip_task(task_id, wait_time, wait_msg, success_msg, task_window_id,mode,vdcid){
    //alert("waiting for task completion...");
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
                //alert("---mode--"+mode);
                if(mode == "PROVISION") {
                    Ext.getCmp("publicIP_pair").getStore().load({
                        params:{
                            vdc_id:vdcid,
                            acc_id:Ext.getCmp("account").getValue(),
                            region_id:Ext.getCmp("region_general").getValue(),
                            pi_type:"provision"
                        }
                    });
                } else if(mode == "EDIT_VM") {
                    Ext.getCmp("publicIP_pair").getStore().load({
                        params:{
                            vdc_id:vdcid,
                            acc_id:cloud_account_id,
                            region_id:cloud_region_id,
                            pi_type:"provision"
                        }
                    });

                } else {
                    reloadPublicIPList();
                }
                Ext.MessageBox.alert("信息", success_msg);
                if(task_window_id) {
                    closeWindow(task_window_id);
                }
            }else{
                Ext.MessageBox.alert(_("失败"), response.status);
                if(task_window_id)
                    closeWindow(task_window_id);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }

    });
}

function refresh_list_public_ip(w, sel_ips, vdc_id, module){
    //alert("refreshing list...");
    var url = '/cloud_network/save_imported_items_from_cloud?items=' + sel_ips + '&vdc_id=' + vdc_id + '&module=' + module;
    //alert("url is " + url);

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var task_id = response.task_id;
                var wait_time = 3000;
                wait_for_refresh_public_ip_task(task_id, wait_time)
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

function wait_for_refresh_public_ip_task(task_id, wait_time){
    //alert("waiting for task completion...");
    var url = '/cloud_network/wait_for_task?task_id=' + task_id + '&wait_time=' + wait_time;
    //alert("url is " + url);
    var refresh_win = Ext.MessageBox.show({
                title:_('请稍候...'),
                msg: _('正在刷新列表...'),
                width:300,
                wait:true,
                waitConfig: {
                    interval:200
                }
            });

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                reloadPublicIPList();
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



function Import_Public_IP(w, wait_win, vdc_id, module)
{

    var tlabel_public_ip=new Ext.form.Label({
        html:'<div>'+_("导入公共IPs")+'<br/></div>'
    });

    var label_public_ip=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("公共IPs")+'<br/></div>'
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

                var l = public_ip_store.getTotalCount();
                var address_list = new Array();
                for (var i=0;i<l;i++){
                    var r = public_ip_store.getAt(i);
                    if(r.get("is_selected")){
                        var dt = {'address' : r.get('address'),
                                'region' : r.get('region')};
                        address_list.push(dt);
                    }
                }
                if(address_list.length == 0){
                     Ext.MessageBox.alert(_("错误"),_("请选择一个公共IP"));
                     return;
                }
                refresh_list_public_ip(w, Ext.util.JSON.encode(address_list), vdc_id, module)

                               
            }
        }
    });


    var public_ip_store = new Ext.data.JsonStore({
        url: '/cloud_network/refresh_list',
        root: 'rows',
        fields: ['id', 'address', 'region', 'used_by','is_selected'],
        successProperty:'success',
        listeners:{
            load:function(store){
//                  var size=store.getCount();
//                   for (var i=0;i<size;i++){
//                        if (store.getAt(i).get('used_by') != ""){
////                            public_ip_grid.getSelectionModel().deselectRow(i,true);
//                      }
//                    }
                wait_win.hide();
            }
        }
    });

    var args = {params:{vdc_id:vdc_id,
                            module:module
                        }
                };
                
    public_ip_store.load(args);
    

    var selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false,
            listeners:{
                rowselect:function(sel_model, index, record){                    
                    },
                selectAll: function(){
                    }
                }
        });

     var public_ip_grid = new Ext.grid.GridPanel({
        store: public_ip_store,
        enableHdMenu:false,
        selModel:selmodel,
        id:'public_ip_grid',
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
                header   : '地址',
                width    : 145,
                sortable : true,
                dataIndex: 'address',
                hidden : false
            },
            {
                header   : '区域',
                width     : 150,
                sortable : true,
                dataIndex: 'region',
                 hidden : false
            },
            {
                header : '所用',
                width  : 95,
                sortable : true,
                dataindex :'used_by',
                hidden : false
            },
            {header:_("选择"),width: 50, sortable: true, dataIndex: 'is_selected', renderer:render_select_checkbox}
        ],

        stripeRows: true,
        height: 310,
        width:475,
        tbar:[label_public_ip,{
            xtype: 'tbfill'
             }],
        listeners: {

         }
    });


    var public_ip_panel=new Ext.Panel({
        id:"public_ip_panel",
        width:490,
        height:367,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        bbar:[{
            xtype: 'tbfill'
        },button_ok, button_cancel],
        items:[tlabel_public_ip, public_ip_grid]
    });

   var outerpanel=new Ext.FormPanel({
       height: 380,
       width: 495,
       autoEl: {},
       layout: 'column',
       items: [public_ip_panel]
   });

   return outerpanel
}





