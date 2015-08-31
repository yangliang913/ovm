/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function CloudInstanceList(vdc_id, acc_id, region_id, called_from, windowid_inst, zone_id){
    /*
    windowid_inst: window id (e.g., windowid_inst=Ext.id();)
    */

    var columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), hidden: true, dataIndex: 'id'},
        {header: _("名称"), width: 140, sortable: true, dataIndex: 'name'},
        {header: _("实例"), width: 140, sortable: true, dataIndex: 'instance_id'},
        {header: _("状态"), width: 100, hidden: false, sortable: true, dataIndex: 'status'}
        ]);

    var vm_status = "SHUTDOWN";
    if(called_from == "PUBLIC_IP") {
        vm_status = "RUNNING";
    }

    var instance_store=new Ext.data.JsonStore({
        url: '/cloud_storage/get_instance_list?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&vm_status=' + vm_status + '&zone_id=' + zone_id,
        root: 'rows',
        fields: ['id', 'name', 'instance_id', 'status'],
        successProperty:'success',
        listeners:{
            load:function(my_store, records, options){
                var msg;
                if(!my_store.getCount()) {
                    if(vm_status == "RUNNING") {
                        msg = "这是没有正在运行的实例."
                    }
                    else {
                        msg = "这是没有实例在同一个区里."
                    }
                    Ext.MessageBox.alert("信息", msg);
                }
            }
        }
    });
    instance_store.load();

    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    
    var ok_button = new Ext.Button({
        name: 'ok_button',
        id: 'ok_button',
        text:_('确定'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedInstance(cloud_instance_grid)) {
                    var rec = cloud_instance_grid.getSelectionModel().getSelected();
                    tf_instance.setValue(rec.get('instance_id'));
                    if(tf_instance_name) {
                        if(rec.get('name')) {
                            tf_instance_name.setValue(rec.get('name'));
                        } else {
                            tf_instance_name.setValue(rec.get('instance_id'));
                        }
                    }
                    closeWindow(windowid_inst);
                }
            }
        }
    });

    var cancel_button = new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {closeWindow(windowid_inst);}
        }
    });

    var cloud_instance_grid = new Ext.grid.GridPanel({
        store: instance_store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:selmodel,
        width:398,
        height:400,
        enableHdMenu:false
        //tbar:[{xtype: 'tbfill'}],
    });
    
    var cloud_snapshot_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        autoHeight:true,
        frame:true,
        items:[cloud_instance_grid]
        ,bbar:[{xtype: 'tbfill'},
            ok_button,
            '-',
            cancel_button
        ]
    });

    return cloud_snapshot_panel;
}

function checkSelectedInstance(grid){
    if(grid.getSelections().length==0){
        Ext.MessageBox.alert(_("警告"),_("请选择一个实例"));
        return false;
    }
    return true;
}
