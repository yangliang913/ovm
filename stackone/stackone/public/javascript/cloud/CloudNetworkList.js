/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
* interface that allows for performing the standard set of VM operations
* (start, stop, pause, kill, shutdown, reboot, snapshot, etc...). It
* also attempts to simplify various aspects of VM lifecycle management.


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
var cloud_network_grid;

function CloudNetworkList(vdc_id, windowid_strg, node_name)
{
		
	
	var cloud_nw_columnModel = new Ext.grid.ColumnModel([
	{header: _("编号"), hidden:true, sortable: false, dataIndex: 'id'},
        {header: _("名称"), width: 100, sortable: false, dataIndex: 'name'},
	{header: _("说明"),hidden:true, sortable: false, dataIndex: 'description'},
        {header: _("地址"), width: 95, sortable: false, dataIndex: 'address'},
        {header: _("DHCP"), width: 145, sortable: false, dataIndex: 'range'},
        {header: _("VM计数"), width:75,sortable: false, dataIndex: 'used_by', align:'right'},
        {header: _("Nated"), width:50,sortable: false, dataIndex: 'nat'},
	{header: _("acc_id"), hidden:true,sortable: false, dataIndex: 'account_id'},
	{header: _("nw_def_id"), hidden:true,sortable: false, dataIndex: 'nw_def_id'}
      ]);

	
	var cloud_network_list_store = new Ext.data.JsonStore({
        url: '/cloud_network/get_nw_defns?vdc_id='+vdc_id,
        root: 'rows',
        fields: [ 'id', 'name', 'description','nat','address','range','used_by','account_id','nw_def_id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
	
    cloud_network_list_store.load();

    var  cloud_nw_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

	var new_button=new Ext.Button({
        name: 'add_button',
        id: 'add_button',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                
                    var url='/cloud_network/allow_private_network_check?vdc_id='+vdc_id;
                    var ajaxReq=ajaxRequest(url,0,"POST",true);
                    ajaxReq.request({
                    success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                              if(response.check==1)
                               {
                                        cloud_network_grid.getSelectionModel().clearSelections();
                                        var windowid_csd = Ext.id();
                                        showWindow(_("创建网络"), 420, 226, CloudNetworkDefinition(vdc_id, "NEW", null, windowid_csd), windowid_csd);
                                }
                                else
                                {
                                    Ext.MessageBox.alert(_("信息"),"你是没有权限创建私有网络，请联系你的管理员");
                                 }
                            }else
                            {
                                Ext.MessageBox.alert(_("失败"),response.msg);
                            }
                        },
        			failure: function(xhr){
                            Ext.MessageBox.alert( _("失败") , xhr.statusText);
                                        }   
                });}

               
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
		
                if(cloud_network_grid.getSelectionModel().getCount()>0){
                    var net_rec=cloud_network_grid.getSelectionModel().getSelected();
                    var nw_id=net_rec.get('id');
                    var nw_def_id=net_rec.get('nw_def_id');
                    var nw_name=net_rec.get('name');
                    var vm_count=net_rec.get('used_by');
                    checkAndRemoveNetwork(nw_id,nw_def_id,nw_name,vdc_id,vm_count)
                }else{
                    Ext.MessageBox.alert(_("失败"),_("请选择要删除的网络"));
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
                if(checkSelectedNetwork(cloud_network_grid)){
                    var rec=cloud_network_grid.getSelectionModel().getSelected();
                    windowid_csd=Ext.id();
                    showWindow(_("编辑网络"),420, 226, CloudNetworkDefinition(vdc_id, "EDIT", rec, windowid_csd), windowid_csd);
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

var refresh_button=new Ext.Button({
                name: 'btnRefreshNetwork',
                id: 'btnRefreshNetwork',
                text:"刷新",
                icon:'icons/refresh.png',
                cls:'x-btn-text-icon',
                hidden: false,
                listeners: {
                    click: function(btn) {
				
                        reloadCloudNetworkDefList();
                    }
                }
            });

cloud_network_grid = new Ext.grid.GridPanel({
        store:cloud_network_list_store ,
        colModel:cloud_nw_columnModel ,
        stripeRows: true,
        frame:false,
        autoScroll:false,
        selModel:cloud_nw_selmodel,
        width:'100%', 
        height:405, 
        enableHdMenu:false,
        tbar:[{xtype: 'tbfill'},
            new_button,
            '-',
            edit_button,
            '-',
            remove_button,
            '-',
            refresh_button
        ],
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                edit_button.fireEvent('click',edit_button);
            }
         }
    });

    var lbl=new Ext.form.Label({
         html:'<div style="" class="labelheading">创建隔离或NAT转发虚拟网络。NAT转发网络将允许你访问公共网络/互联网.</div>'
    });

    var cloud_network_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:'100%',
        height:468,
        frame:true,
        items:[lbl, cloud_network_grid]
        ,bbar:[{xtype: 'tbfill'},
            cancel_button
        ]
    });

    return cloud_network_panel;
}

function checkSelectedNetwork(grid){
    if(grid.getSelections().length==0){
        Ext.MessageBox.alert(_("警告"),_("请选择一个网络"));
        return false;
    }
    return true;
}

function reloadCloudNetworkDefList(){
    cloud_network_grid.enable();
    cloud_network_grid.getStore().load();
}
function wait_for_nw_remove_task(task_id, wait_time, nw_name){
    var url = '/cloud_network/wait_for_task?task_id=' + task_id + '&wait_time=' + wait_time;
    Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: _('正在移除网络...'),
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
                reloadCloudNetworkDefList();
                Ext.MessageBox.alert("成功", "网络" + nw_name + " 成功移除.");
            }else{
                Ext.MessageBox.alert(_("失败"), response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}

function checkAndRemoveNetwork(nw_id,nw_def_id,nw_name,vdc_id,vm_count)
{
    if(vm_count > 0)
    {
        Ext.MessageBox.confirm(_("确认"),"一个 或者更多的虚拟机正在使用这个网络.确定要继续吗?",function(id){
                        if(id=='yes'){
                            removeNetwork(nw_id,nw_def_id,vdc_id,nw_name);
                        }
                    });
    }
    else
    {
         var message_text = "确定要移除" + nw_name + "网络吗?";
         Ext.MessageBox.confirm(_("确认"),message_text,function(id){
         if(id=='yes'){
                       removeNetwork(nw_id,nw_def_id,vdc_id,nw_name);
        }
        });
    }
}

function removeNetwork(nw_id,nw_def_id,vdc_id,nw_name)
{
    
     var url="/cloud_network/remove_network?nw_id="+nw_id+"&nw_def_id=" + nw_def_id 
             +"&vdc_id="+vdc_id;

    var ajaxReq=ajaxRequest(url,0,"POST",true);

    ajaxReq.request({

    success: function(xhr) {

        var response=Ext.util.JSON.decode(xhr.responseText);

        if(response.success){
                var task_id = response.task_id;
                var wait_time = 3000;

                wait_for_nw_remove_task(task_id,wait_time,nw_name);    

        }else{

            Ext.MessageBox.alert(_("失败"),response.msg);

        }

    },

    failure: function(xhr){

        Ext.MessageBox.alert( _("失败") , xhr.statusText);

    }

    });
}
