/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function CloudSnapshotList(vdc_id, acc_id, region_id, windowid_snap){
    /*
    windowid_snap: window id (e.g., windowid_snap=Ext.id();)
    */

    var columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), hidden: true, dataIndex: 'id'},
        {header: _("名称"), width: 100, sortable: true, dataIndex: 'name'},
        {header: _("说明"), width: 200, sortable: true, dataIndex: 'description'},
        {header: _("大小"), width: 80, sortable: true, dataIndex: 'volume_size'}
    ]);

    var snapshot_store = new Ext.data.JsonStore({
        url: '/cloud_storage/get_snapshot_list?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id,
        root: 'rows',
        fields: ['id', 'name', 'description', 'volume_size'],
        successProperty:'success',
        listeners:{
            load:function(my_store, records, options){
                //Ext.MessageBox.alert(_("Info"),_("Snapshots are loaded."));
                Ext.MessageBox.hide();
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    snapshot_store.load();

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
                if(checkSelectedSnapshot(cloud_snapshot_grid)) {
                    var rec = cloud_snapshot_grid.getSelectionModel().getSelected();
                    tf_snapshot.setValue(rec.get('name'));
                    closeWindow(windowid_snap);
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
            click: function(btn) {closeWindow(windowid_snap);}
        }
    });

    var cloud_snapshot_grid = new Ext.grid.GridPanel({
        store: snapshot_store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:selmodel,
        width:398,
        height:400,
        enableHdMenu:false
    });
    
    var cloud_snapshot_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        autoHeight:true,
        frame:true,
        items:[cloud_snapshot_grid]
        ,bbar:[{xtype: 'tbfill'},
            ok_button,
            '-',
            cancel_button
        ]
    });

    return cloud_snapshot_panel;
}

function checkSelectedSnapshot(grid){
    if(grid.getSelections().length==0){
        Ext.MessageBox.alert(_("警告"),_("请选择一个快照"));
        return false;
    }
    return true;
}
