/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function CloudVolumeList(vdc_id, acc_id, region_id, zone_id, vm_id, windowid_inst, list_type){
    /*
    windowid_inst: window id (e.g., windowid_inst=Ext.id();)
    */

    var columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), hidden: true, dataIndex: 'id'},
        {header: _("名称"), width: 100, sortable: true, dataIndex: 'name'},
        {header: _("卷编号"), width: 100, sortable: true, dataIndex: 'volume_id'},
        {header: _("大小"), hidden: true, sortable: true, dataIndex: 'size'},
        {header: _("单元"), hidden: true, sortable: true, dataIndex: 'size_unit'},
        {header: _("大小"), width: 80, hidden: false, sortable: true, dataIndex: 'display_size'},
        {header: _("状态"), width: 80, hidden: false, sortable: true, dataIndex: 'status'}
        ]);

    var task_url = "";

    if(list_type == "VM_ATTACH") {
        task_url = '/cloud_storage/get_volume_list_for_attach?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&zone_id=' + zone_id + '&vm_id=' + vm_id;
    } else if(list_type == "SNAPSHOT") {
        task_url = '/cloud_storage/get_volume_list_for_snapshot?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id;
    }

    var volume_store=new Ext.data.JsonStore({
        url: task_url,
        root: 'rows',
        fields: ['id', 'name', 'volume_id', 'size', 'size_unit', 'display_size', 'status'],
        successProperty:'success',
        listeners:{
            load:function(my_store, records, options){
                var msg;
                if(!my_store.getCount()) {
                    msg = "这是没有可用的存储."
                    Ext.MessageBox.alert("Info", msg);
                }
            }
        }
    });
    volume_store.load();

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
                if(checkSelectedVolume(cloud_volume_grid)) {
                    var rec = cloud_volume_grid.getSelectionModel().getSelected();
                    tf_storage.setValue(rec.get('volume_id'));
                    tf_storage_name.setValue(rec.get('name'));
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

    var cloud_volume_grid = new Ext.grid.GridPanel({
        store: volume_store,
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
        items:[cloud_volume_grid]
        ,bbar:[{xtype: 'tbfill'},
            ok_button,
            '-',
            cancel_button
        ]
    });

    return cloud_snapshot_panel;
}

function checkSelectedVolume(grid){
    if(grid.getSelections().length==0){
        Ext.MessageBox.alert(_("警告"),_("请选择一个存储."));
        return false;
    }
    return true;
}
