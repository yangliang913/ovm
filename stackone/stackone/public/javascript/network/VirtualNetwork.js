/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var virtual_def;
var virtual_nw_grid;
var selNode;
var sSiteId, sGroupId, sNodeId, op_level, op_level_main;
var hideSyncServerButton, hideSyncAllButton;
var server_grid;
var create_network_panel;
var hideServerCol, hideDisplayScopeCol;

var load_counter=0;
var def_timeout;
var curr_def_count=0;
var initial_def_count=0;
var is_timer=false; 
var def_name_adding="";
var adding_def=false;
var removing_def=false;

function VirtualNetwork(node){
    selNode = node;
    var new_button_text = "新建";
    var remove_button_text = "移除"
    var hideEditButton = false;
    var header_text = "";
    var header_text_vlan = "虚拟网络使您创建的虚拟机互相通信，满足你基于业务模型的各种网络需求."
    var header_text_host_nw = "虚拟网络允许虚拟机之间相互沟通."
    //We are checking whether the node passed is server or servergroup.
    if(node.attributes.nodetype == 'DATA_CENTER'){
        //When menu is invoked at data center level
        //Consider the node is a data center
        //node and group would be null
        sSiteId = "site_id=" + node.attributes.id;
        op_level = "&op_level=DC";
        sGroupId = "";
        sNodeId = "";
        hideSyncServerButton = true;
        hideSyncAllButton = true;
        hideServerCol = true;
        hideDisplayScopeCol = false;
        new_button_text = "新建";
        remove_button_text = "移除";
        hideEditButton = false;
        header_text = header_text_vlan;
    }
    else if(node.attributes.nodetype == 'SERVER_POOL'){
        //When menu is invoked at server pool level
        //Consider the node is a group (server pool)
        //node would be null
        sSiteId = "site_id=" + node.parentNode.attributes.id;
        op_level = "&op_level=SP";
        sGroupId = "&group_id=" + node.attributes.id;
        sNodeId = "";
        hideSyncServerButton = true;
        hideSyncAllButton = true;
        hideServerCol = true;
        hideDisplayScopeCol = false;
        new_button_text = "附加";
        remove_button_text = "分离";
        hideEditButton = true;
        header_text = header_text_vlan;
    }
    else{
        //When menu is invoked at server level
        sSiteId = "site_id=" + node.parentNode.parentNode.attributes.id;
        op_level = "&op_level=S";
        sGroupId = "&group_id=" + node.parentNode.attributes.id;
        sNodeId = "&node_id=" + node.attributes.id;
        hideSyncServerButton = false;
        hideSyncAllButton = true;
        hideServerCol = true;
        hideDisplayScopeCol = true;
        new_button_text = "新建";
        remove_button_text = "移除";
        hideEditButton = false;
        header_text = header_text_host_nw;
    }

    op_level_main = op_level;

    var columnModel = new Ext.grid.ColumnModel([

        {header: _("名称"), width: 100, sortable: false, dataIndex: 'name'},
        {header: _("详情"), width: 180, sortable: false, dataIndex: 'definition'},
        {header: _("说明"), width: 120, hidden:true,sortable: false, dataIndex: 'description'},
        {header: _("状态"), width: 55, hidden: false, sortable: false, renderer: showDefStatusLink, dataIndex: 'status'},
        {header: _("范围"), hidden: true, sortable: false, dataIndex: 'scope'},
        {header: _("范围"), width: 80, hidden: hideServerCol, sortable: false, dataIndex: 'server'},
        {header: _("范围"), width: 100, hidden: hideDisplayScopeCol, sortable: false, dataIndex: 'displayscope'},
        {header: _("关联"), hidden: true, sortable: false, dataIndex: 'associated'}
    ]);
     var network_list_store = new Ext.data.JsonStore({
        url: '/network/get_nw_defns?' + sSiteId + op_level + sGroupId + sNodeId,
        root: 'rows',
        fields: [ 'name', 'definition', 'description','status','type','id', 'status', 'scope', 'associated', 'server', 'displayscope'],
        successProperty:'success',
        listeners:{
            load:function(my_store, records, options){
                //alert("Loading...");
                load_counter++;
                //alert("Load counter=" + load_counter);
                if(load_counter>10) {
                    //alert("load counter is 10.");
                    clearTimeout(def_timeout);
                    is_timer=false;
                    //refresh the grid
                    //reloadVirtualNetworkDefList();
                    return;
                }
                curr_def_count = my_store.getCount();
                if(is_timer == true) {
                    if(initial_def_count != curr_def_count) {
                        //alert("Breaking...");
                        if(adding_def==true){
                            for(i=0;i<=curr_def_count;i++) {
                                rec = my_store.getAt(i);
                                if(def_name_adding == rec.get('name') || def_name_adding == "") {
                                    //alert("Breaking for add...");
                                    clearTimeout(def_timeout);
                                    is_timer = false;
                                    adding_def = false;
                                    //refresh the grid
                                    reloadVirtualNetworkDefList();
                                    break;
                                } else {
                                    //alert("Breaking for add II...");
                                    clearTimeout(def_timeout);
                                    is_timer = false;
                                    adding_def = false;
                                    //refresh the grid
                                    reloadVirtualNetworkDefList();
                                    break;
                                }
                            }
                        } else {
                            //alert("Breaking for remove...");
                            clearTimeout(def_timeout);
                            is_timer = false;
                            removing_def = false;
                            //refresh the grid
                            reloadVirtualNetworkDefList();
                        }
                    } else {
                        //alert("Continue loading...");
                        def_timeout = setTimeout("reloadVirtualNetworkDefList()", 1000);
                    }
                }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    network_list_store.load();
    var  virtual_nw_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var new_vlan_button=new Ext.Button({
        name: 'add_network',
        id: 'add_network',
        text: "新建",
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        hidden:((node.attributes.nodetype == 'SERVER_POOL')? false: true),
        listeners: {
            click: function(btn) {
                adding_def=true;
                removing_def=false;

                var url="/network/get_new_private_bridge_name?" + sSiteId + op_level + sGroupId + sNodeId;
                OpenNewVlanNetworkDialog(node, null, null, null, null, url);
            }
        }

    });

    var virtual_new_button=new Ext.Button({
        name: 'add_network',
        id: 'add_network',
        text:new_button_text,
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                adding_def=true;
                removing_def=false;

                if(node.attributes.nodetype == 'DATA_CENTER' ) {
                    //handleEvents(node,'create_network',null);
					var url="/network/get_new_private_bridge_name?" + sSiteId + op_level + sGroupId + sNodeId;
                    OpenNewVlanNetworkDialog(node, null, null, null, null, url);
                } 
                else if( node.attributes.nodetype == 'SERVER_POOL') {
                    //var url="/network/get_new_private_bridge_name?" + sSiteId + op_level + sGroupId + sNodeId;
                    Open_Association_window(node);
                
                } else {
                    var url="/network/get_new_private_bridge_name?" + sSiteId + op_level + sGroupId + sNodeId;
                    OpenNewNetworkDialog(node, null, null, null, null, url);
                }
            }
        }

    });

    var virtual_remove_button=new Ext.Button({
        name: 'remove_network',
        id: 'remove_network',
        text:remove_button_text,
        icon:'icons/delete.png',
        cls:'x-btn-text-icon' ,
        listeners: {
            click: function(btn) {
                adding_def=false;
                removing_def=true;

                if(virtual_nw_grid.getSelectionModel().getCount()>0){
                    var net_rec=virtual_nw_grid.getSelectionModel().getSelected();
                    if(sGroupId != "" && sNodeId != "") {
                        //If the network is defined at data center or server pool level
                        if(net_rec.get('scope') == 'SP' || net_rec.get('scope') == 'DC') {
                            Ext.MessageBox.alert("信息", "数据中心和资源池级别的网络不能在这里被删除");
                            return
                        }
                    }
                    if(net_rec.get('scope') == 'CP') {
                        //"nw1" is part of Virtual Data Center "vdc1". Please use context menu from "vdc1" to manage networks.
                        var displayscope = net_rec.get('displayscope')
                        var vdc_list = displayscope.split(",");
                        //alert(vdc_list);
                        var csep_vdc_name = vdc_list[0].split("-");
                        //alert(csep_vdc_name);
                        //alert(csep_vdc_name[1]);
                        var vdc_name = csep_vdc_name[1]
                        var network_name = net_rec.get("name");
                        var msg_text = '"' + network_name + '"是虚拟数据中心的一部分"' + vdc_name + '". 请从 "' + vdc_name + '"的上下文菜单进行管理.'
                        Ext.MessageBox.alert("信息", msg_text);
                        return;
                    }

                    var message_text = "";
                    if (node.attributes.nodetype == 'DATA_CENTER') {
                        message_text = "确定要移除" + net_rec.get('name') + "网络吗?";
                    } else {
                        message_text = "确定要移除" + net_rec.get('name') + "网络吗?";
                    }

                    Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                        if(id=='yes'){

                            var def_id=net_rec.get('id');
                            var url="/network/remove_nw_defn?" + sSiteId + op_level + sGroupId + sNodeId + "&def_id=" + def_id;
                            var ajaxReq=ajaxRequest(url,0,"POST",true);
                            ajaxReq.request({
                                success: function(xhr) {//alert(xhr.responseText);
                                    var response=Ext.util.JSON.decode(xhr.responseText);
                                    if(response.success){
                                          //Ext.MessageBox.alert("Success",response.msg);
                                          //reloadVirtualNetworkDefList();   
                                          DelayLoadingDefList(virtual_nw_grid);
                                          Ext.MessageBox.alert("成功","任务已经提交.");
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
                }else{
                    Ext.MessageBox.alert(_("失败"),_("请选择一个要删除的网络"));
                }

            }
        }

    });
    
var  virtual_edit_button= new Ext.Button({
        name: 'edit_network',
        id: 'edit_network',
        text:_("编辑"),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        hidden: hideEditButton,
        listeners: {
            click: function(btn) {
                adding_def=false;
                removing_def=false;

                if(virtual_nw_grid.getSelectionModel().getCount()>0){
                    var edit_rec=virtual_nw_grid.getSelectionModel().getSelected();
                    var network_scope = edit_rec.get('scope');
                    var nw_id=edit_rec.get('id');
                    if((node.attributes.nodetype == 'DATA_CENTER' || node.attributes.nodetype == 'SERVER_POOL') && (network_scope=="S")){
                        Ext.MessageBox.alert(_("警告"),_("服务器池级别的网络不可以在这里编辑."));
                        return;
                    }
                    var url="/network/get_edit_network_details?nw_id="+nw_id;
                    var ajaxReq=ajaxRequest(url,0,"POST",true);
                    ajaxReq.request({
                        success: function(xhr) {//alert(xhr.responseText);
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                            
                            windowid=Ext.id();

                            if(node.attributes.nodetype == 'DATA_CENTER' || node.attributes.nodetype == 'SERVER_POOL') {
                    
                                nw_new_win_popup = showWindow(_("编辑虚拟网络"),438,524,VlanDefinition(node,'EDIT',response,panel,network_scope,windowid),null);//438, 460 (438,290),438,284, 354
                            
                            } else {

                                var nw_panel =  VirtualNetworkDefinition(node,'EDIT',response,panel,network_scope,windowid);
                                nw_new_win_popup = showWindow(_("编辑定义"),438,370,nw_panel,null);
                                    
                                    var interface =nw_panel.findById('interface'); 
                                    hideField2(interface);
                                    var bond_details_checkBox =nw_panel.findById('bond_details_checkBox'); 
                                    hideField2(bond_details_checkBox);
                                    var bond_details_grid =nw_panel.findById('bond_details_grid'); 
                                    bond_details_grid.hide();                   
                                    var vlan_checkBox =nw_panel.findById('vlan_checkBox'); 
                                    hideField2(vlan_checkBox);
                                    var vlan_id =nw_panel.findById('vlan_id'); 
                                    hideField2(vlan_id);                    
                                    var gateway =nw_panel.findById('gateway'); 
                                    hideField2(gateway);
                                    var ip_address =nw_panel.findById('ip_address'); 
                                    hideField2(ip_address);                    
                                    var nat_forward =nw_panel.findById('nat_forward');
                                    hideField2(nat_forward);

                                    var hostonly_radio =nw_panel.findById('hostonly_radio'); 
                                    var nat_radio =nw_panel.findById('nat_radio'); 


                                    var network=response.network;

                                    if(network.nw_nat_forward){      
                                        nat_radio.setValue(true);
                                        hostonly_radio.setValue(false);                            
                                    }
                                    else
                                    {                                       
                                        nat_radio.setValue(false);
                                        hostonly_radio.setValue(true);
                        
                                    }

                            }
                              

//                              
                            }else{
                                Ext.MessageBox.alert(_("Failure"),response.msg);
                            }
                        },
                        failure: function(xhr){
                            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                        }
                    });
                }else{
                    Ext.MessageBox.alert(_("失败"),_("请选择一个要编辑的网络"));
                }

            }
        }

    });

    virtual_nw_grid = new Ext.grid.GridPanel({
        store: network_list_store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        selModel:virtual_nw_selmodel,
        width:'100%',
        //autoExpandColumn:2,
        height:350,
        autoScroll:true,
        enableHdMenu:false,
        autoExpandColumn:2,
        tbar:[{
                xtype: 'tbfill'
            },
            new_vlan_button,
            '-',
            virtual_new_button,
            '-',
            virtual_edit_button,
            '-',
            virtual_remove_button,
            '-',
            new Ext.Button({
                name: 'btnSyncAllNetwork',
                id: 'btnSyncAllNetwork',
                icon:'icons/sync-all.png',
                text:"同步所有",
                cls:'x-btn-text-icon',
                hidden: hideSyncAllButton,
                listeners: {
                    click: function(btn) {
                        adding_def=false;
                        removing_def=false;

                        sync_all("NETWORK");
                    }
                }
            }),
            new Ext.Button({
             	name: 'btnSyncServer',
                id: 'btnSyncServer',
                text:"同步服务器",
                icon:'icons/sync-server-icon.png',
                cls:'x-btn-text-icon',
                hidden: hideSyncServerButton,
                listeners: {
                    click: function(btn) {
                        adding_def=false;
                        removing_def=false;

                        if(sNodeId == '') {
                            node_id_temp = sNodeId;
                        }else {
                            node_id_temp = node.attributes.id;
                        }
                        server_sync(node_id_temp, "NETWORK");
                    }
                }
            }),
            '-',
            new Ext.Button({
                name: 'btnRefreshNetwork',
                id: 'btnRefreshNetwork',
                text:"刷新",
                icon:'icons/refresh.png',
                cls:'x-btn-text-icon',
                hidden: false,
                listeners: {
                    click: function(btn) {
                        adding_def=false;
                        removing_def=false;

                        //alert("Refreshing network");
                        reloadVirtualNetworkDefList();
                    }
                }
            })

        ],
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                virtual_edit_button.fireEvent('click',virtual_edit_button);
            }
         }
    });

    var lbl=new Ext.form.Label({
        html:'<div style="" class="labelheading">'+ _(header_text) +'</div>'
//Virtual Networks allow Virtual Machines on the same managed server to communicate with each other
//          html:'<font style: size="2"><i>'+
//              _("Virtual Networks allow VMs on the same managed server to communicate with each other")+
//              '</i></font><br/></div>'
    });

    var panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:450,
        height:420,
        //frame:true,
        cls: 'whitebackground',
        items:[lbl,virtual_nw_grid]
        ,bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('关闭'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {adding_def=false; removing_def=false; closeThisWindow(nw_win_popup);}
                    }
            })
        ]
    });
    create_network_panel = panel;
    return panel;

}
function closeVirtualNetworkDefinition(){
     virtual_def.close();
}
function reloadVirtualNetworkDefList(){
    virtual_nw_grid.enable();
    virtual_nw_grid.getStore().load();
}

//Start - Changes from Showing definition status
function showDetailsLink(data,cellmd,record,row,col,store) {
    if(data != "") {
        var server_id = record.get("id");
        var vn_sync_details = record.get("details");
        var returnVal = '<a href="#" onclick="showDetails()">Details</a>';
        return returnVal;
    }
    else {
        return data;
    }
}

function showDetails() {
    var rec = server_grid.getSelectionModel().getSelected();
    var vn_sync_details = rec.get('details');

    if (vn_sync_details == null) {
        vn_sync_details = "No details found";
    }
    txt_details.setValue(vn_sync_details);
    win_detail_status.show(this);
}

function showDefStatusLink(data,cellmd,record,row,col,store) {
    var returnVal = "";
    if(data != "") {
        var def_id = record.get("id");
        var sStatus = record.get("status");
        var associated = record.get("associated");

        if (sStatus=="OUT_OF_SYNC"){
            icon="out-of-sync-icon"
        }else if(sStatus=="IN_SYNC"){
            icon="in-sync-icon"
        }

        var fn = "showServerDefList('" + def_id + "','" + sStatus + "')";
        //returnVal = '<a href="#" onClick=' + fn + '>' + data + '</a>';
        returnVal = '<a href="#" onClick=' + fn + '> <img width=13 height=13 src=../icons/'+icon+'.png/> </a>';
        /*
        if(selNode.attributes.nodetype == 'DATA_CENTER'){
            if (associated == false) {
                returnVal = "";  //If difinition is not associated with any server then show status as blank
            }
        }
        */
    }
    return returnVal;
}

function showServerDefList(id, sStatus) {
    var win, sel_def_id;
    //get selected definition id
    if (checkSelectedNetwork(virtual_nw_grid)) {
        sel_def_id = virtual_nw_grid.getSelectionModel().getSelected().get('id');
        sel_def_name = virtual_nw_grid.getSelectionModel().getSelected().get('name');
    }

    var lbl_desc=new Ext.form.Label({
        html:"<div><font size='2'><i>This represents the list of servers linked with the selected network along with the status.</i></font></div><br/>"
    });

    var lbl_server=new Ext.form.Label({
        html:"<div><font size='2'><i><b>服务器池</b> - " + selNode.attributes.text + ". <br /><b>网络</b> - " +  sel_def_name + "</i></font></div>"
    });

    var serverDefListColumnModel = new Ext.grid.ColumnModel([
        {header: "编号", hidden: true, dataIndex: 'id'},
        {header: "", width: 15, sortable: false, dataIndex: 'nw_svc_host'},
        {header: "服务器", width: 150, sortable: false, dataIndex: 'name'},
        {header: "状态", width: 105, sortable: false, renderer: showSyncStatus, dataIndex: 'status'},
        {header: "详情", width: 85, sortable: false, renderer: showDetailsLink, dataIndex: 'details_link'},
        {header: "详情", hidden: true, dataIndex: 'details'}
    ]);

    var serverDefListStore = new Ext.data.JsonStore({
        url: '/network/get_server_nw_def_list?' + sSiteId + sGroupId + '&def_id=' + sel_def_id + '&defType=NETWORK',
        root: 'rows',
        fields: ['id', 'nw_svc_host', 'name', 'status', 'details'],
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
        width:372, //400
        //autoExpandColumn:2,
        height:140,
        enableHdMenu:false

    });
    
    // create the window on the first click and reuse on subsequent clicks
    win = new Ext.Window({
        //applyTo:'hello-win',
        title: '状态',
        layout:'fit',
        width:400,
        height:300,
        closeAction:'hide',
        plain: true,
        items: new Ext.Panel({
            id: "serverDefPanel",
            bodyStyle:'padding:10px 0px 0px 0px',
            //width:350,
            //height:250,
            hidemode:"offset",
            frame:true,
            items:[lbl_desc, lbl_server, server_grid]
        }),
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'btnSvrDefListsync',
                id: 'btnSvrDefListsync',
                text:"Sync",
                icon:'icons/sync-server-icon.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
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
                        sync_defn(server_ids, sel_def_id);
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

function sync_defn(server_ids, def_id){
    if (server_ids == "") {
        Ext.MessageBox.alert("警告","请选择服务器.");
        return;
    }

    var url="sync_defn?" + sSiteId + sGroupId + "&server_ids=" + server_ids + "&def_id=" + def_id + "&defType=NETWORK"; 
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

function checkSelectedNetwork(grid){
    if(grid.getSelections().length==0){
        Ext.MessageBox.alert("警告","请选择一个网络.");
        return false;
    }
    return true;
}

function server_sync(node_id, def_type){
    var url="server_sync?node_id=" + node_id + "&def_type=" + def_type; 
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

function associate_nw_defns(def_type, def_ids){
    if(def_ids == ""){
        Ext.MessageBox.alert("警告","请选择网络");
        return;
    }

    var url="/network/associate_nw_defns?" + sSiteId + op_level + sGroupId + sNodeId + "&def_type=" + def_type + "&def_ids=" + def_ids; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                virtual_nw_dc_grid.getStore().load();
                closeWindow(windowid);
                reloadVirtualNetworkDefList();
                Ext.MessageBox.alert("成功","网络和服务器池已经关联");
            }else{
                Ext.MessageBox.alert("Failure",response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( "Failure " , xhr.statusText);
        }
    });
}

//End - Changes from Showing definition status

function OpenNewNetworkDialog(objNode, strSiteId, strGroupId, strNodeId, strOpLevel, url) {
    if (url == null) {
        url="/network/get_new_private_bridge_name?site_id=" + strSiteId + "&op_level=" + strOpLevel + "&group_id=" + strGroupId + "&node_id=" + strNodeId;
    }
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                windowid=Ext.id();
                var win_height = 380;
                if(objNode.attributes.nodetype == 'SERVER_POOL'){
                        win_height = 450;
                } else {
                        win_height = 370;
                }
                //win_height = win_height+ 180;

                nw_panel = VirtualNetworkDefinition(objNode,'NEW',response,create_network_panel,null,windowid)
                nw_new_win_popup = showWindow(_("新的定义"),438,win_height,nw_panel,null);

                var interface =nw_panel.findById('interface'); 
                hideField2(interface);
                var bond_details_checkBox =nw_panel.findById('bond_details_checkBox'); 
                hideField2(bond_details_checkBox);
                var bond_details_grid =nw_panel.findById('bond_details_grid'); 
                bond_details_grid.hide();
//                 hideField2(bond_details_grid);
                var vlan_checkBox =nw_panel.findById('vlan_checkBox'); 
                hideField2(vlan_checkBox);
                var vlan_id =nw_panel.findById('vlan_id'); 
                hideField2(vlan_id);
//                 var bridgename =nw_panel.findById('bridgename'); 
//                 hideField2(bridgename);

                var gateway =nw_panel.findById('gateway'); 
                hideField2(gateway);
                var ip_address =nw_panel.findById('ip_address'); 
                hideField2(ip_address);

                var nat_forward =nw_panel.findById('nat_forward');
                //alert( nat_forward.getValue());
                hideField2(nat_forward);

                //nw_new_win_popup = showWindow(_("New Definition"),438,win_height,PhysicalNetworkDefinition(objNode,'NEW',response,create_network_panel,null,windowid),null);
                if(objNode.attributes.nodetype == 'SERVER_POOL'){
                    nw_def_form.getBottomToolbar().hide();
                }
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.hide();
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function OpenNewVlanNetworkDialog(objNode, strSiteId, strGroupId, strNodeId, strOpLevel, url) {
    if (url == null) {
        url="/network/get_new_private_bridge_name?site_id=" + strSiteId + "&op_level=" + strOpLevel + "&group_id=" + strGroupId + "&node_id=" + strNodeId;
    }
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                windowid=Ext.id();

                nw_new_win_popup = showWindow(_("新的虚拟网络"),438,534,VlanDefinition(objNode,'NEW',response,create_network_panel,null,windowid),null); //460 (438,290),284,354
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.hide();
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}




function Open_Association_window(node) {
    var sSiteId, sGroupId, sNodeId, op_level;
    if(node.attributes.nodetype == 'SERVER_POOL'){
        //When menu is invoked at server pool level
        //Consider the node is a group (server pool)
        //node would be null
        sSiteId = "site_id=" + node.parentNode.attributes.id;
        op_level = "&op_level=DC";
        sGroupId = "&group_id=" + node.attributes.id;
        sNodeId = "";
        
    }


    var columnModel = new Ext.grid.ColumnModel([

        {header: _("名称"), width: 80, sortable: false, dataIndex: 'name'},
        {header: _("详情"), width: 100, sortable: false, dataIndex: 'definition'},
        {header: _("说明"), width: 120, sortable: false, dataIndex: 'description'},
        {header: _("状态"), width: 100, hidden: true, sortable: false, renderer: showDefStatusLink, dataIndex: 'status'},
        {header: _("范围"), width: 80, hidden: true, sortable: false, dataIndex: 'scope'},
        {header: _("范围"), width: 80, hidden: true, sortable: false, dataIndex: 'server'},
        {header: _("范围"), width: 100, hidden: true, sortable: false, dataIndex: 'displayscope'},
        {header: _("关联"), width: 80,hidden: true, sortable: false, dataIndex: 'associated'}
    ]);

    var network_list_store = new Ext.data.JsonStore({
//         url: '/network/get_nw_defns?' + sSiteId + op_level + sGroupId + sNodeId,
        url: '/network/get_nw_dc_defns?' + sSiteId + op_level + sGroupId + sNodeId,
        root: 'rows',
//         fields: [ 'name', 'definition', 'description','status','type','id', 'status', 'scope', 'associated', 'server', 'displayscope'],
        fields: [ 'name', 'definition', 'description','status','type','id', 'status', 'scope', 'associated', 'server', 'displayscope'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    network_list_store.load();
    var  virtual_nw_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });


    var virtual_nw_grid = new Ext.grid.GridPanel({
        store: network_list_store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        selModel:virtual_nw_selmodel,
        width:'100%',
        //autoExpandColumn:2,
        height:358,//355
        autoScroll:true,
        enableHdMenu:false,
        autoExpandColumn:2,
        tbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'btnAssociate',
                id: 'btnAssociate',
                text:"附加",    //Associate
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        //var storageId = storage_dc_grid.getSelectionModel().getSelected().get('id');
                        var def_ids = "";
                        var sm = virtual_nw_grid.getSelectionModel();
                        var rows = sm.getSelections();
                        for(i=0; i<rows.length; i++) {
                            if(i == rows.length-1) {
                                def_ids += rows[i].get('id');
                            } else {
                                def_ids += rows[i].get('id') + ',';
                            }
                        }
                        associate_vlans("NETWORK",def_ids, association_window);
                    }
                }
            }),
            '-',
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('关闭'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        association_window.close();
                    }
                }
            })
        ],
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                virtual_edit_button.fireEvent('click',virtual_edit_button);
            }
         }
    });

    var info_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250"> 选择虚拟网络关联到服务器池.<br/></div>'
    });
    var association_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:450,
        height:380,
        //frame:true,
        cls: 'whitebackground',
        items:[info_label,virtual_nw_grid]        
    });
    
    var association_window=new Ext.Window({
                    title :'虚拟网络详情', //VLAN Details
                    width :460,
                    height:410,
                    modal : true,
                    resizable : false
                });
    association_window.add(association_panel);                
    association_window.show();

    
}

function associate_vlans(def_type, def_ids, association_window ){
    if(def_ids == ""){
        Ext.MessageBox.alert("警告","请选择vlan");
        return;
    }

    var url="/network/associate_defns?" + sSiteId + op_level + sGroupId + "&def_type=" + def_type + "&def_ids=" + def_ids; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                //closeWindow(windowid);
                //reloadVirtualNetworkDefList();
                association_window.close();
                //Ext.MessageBox.alert("Success","Virtual Networks is associated with the server pool.");
                Ext.MessageBox.alert("成功","任务已经提交.");
                DelayLoadingDefList(virtual_nw_grid);
            }else{
                Ext.MessageBox.alert("Failure",response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( "Failure " , xhr.statusText);
        }
    });
}


function DelayLoadingDefList(grid) {
    is_timer = true;
    load_counter=0;
    initial_def_count = grid.getStore().getCount();
    def_name_adding = "";
    //def_name_adding = nw_name.getValue();
    //def_timeout = setTimeout("reloadVirtualNetworkDefList()", 10);
    reloadVirtualNetworkDefList();
}
