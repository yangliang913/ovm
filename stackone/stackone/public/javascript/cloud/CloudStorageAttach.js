/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var tf_instance, tf_instance_name; //This variable we have declared at form level because we need to access it from CloudInstanceList.js.
function CloudStorageAttachWin(vdc_id, storage_rec, windowid_csa) {
    /*
    storage_rec: security group rule record (selected record in security grid rule store).
    windowid_csa window id (e.g., windowid_csa=Ext.id();)
    */
    var cloud_storage_attach_form;

    var tf_id=new Ext.form.TextField({
        //fieldLabel: _('Id'),
        name: 'tf_id',
        id: 'tf_id',
        width: 200,
        allowBlank:true,
        hidden: true
    });
    var tf_device=new Ext.form.TextField({
        fieldLabel: _('设备:'),
        name: 'tf_device',
        id: 'tf_device',
        width: 200,
        allowBlank:false,
        hidden: false
    });
    var tf_region=new Ext.form.TextField({
        //fieldLabel: _('Region'),
        name: 'tf_region',
        id: 'tf_region',
        width: 100,
        allowBlank:true,
        hidden: false,
        border: 0,
        disabled: true
    });
    var tf_storage=new Ext.form.TextField({
        fieldLabel: _('存储:'),
        name: 'tf_storage',
        id: 'tf_storage',
        width: 200,
        allowBlank:false,
        hidden: true,
        disabled: true
    });

    var tf_storage_name=new Ext.form.TextField({
        fieldLabel: _('存储:'),
        name: 'tf_storage_name',
        id: 'tf_storage_name',
        width: 200,
        allowBlank:false,
        hidden: false,
        disabled: true
    });

    tf_instance=new Ext.form.TextField({
        fieldLabel: _('实例'),
        name: 'tf_instance',
        id: 'tf_instance',
        width: 150,
        allowBlank: false,
        hidden: true,
        disabled: true
    });

    tf_instance_name=new Ext.form.TextField({
        fieldLabel: _('实例'),
        name: 'tf_instance_name',
        id: 'tf_instance_name',
        width: 150,
        allowBlank: false,
        hidden: false,
        disabled: true
    });

    var lbl_device_info=new Ext.form.Label({
        html:_('<div style="width:500px;color:gray"><table><tr><td width=80px></td><td>Windows设备: xvdf through xvdp <br\>Linux设备: /dev/sdf through /dev/sdp</td></tr></div>')
    });

    var lbl_region=new Ext.form.Label({
        html:_('<div style="width:125px"/>')
    });

    var region_space=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });

    var attach_button = new Ext.Button({
        name: 'attach_button',
        id: 'attach_button',
        text:_("附加"),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedStorage(cloud_storage_grid)){
                    if(cloud_storage_attach_form.getForm().isValid()){
                        var storage_name = storage_rec.get("name");
                        var volume_id = tf_storage.getValue();
                        var instance_id = tf_instance.getRawValue();
                        var device = tf_device.getValue();
                        var acc_id = storage_rec.get("account_id");
                        var region_id = storage_rec.get("region_id");
                        attachCloudStorage(vdc_id, acc_id, region_id, volume_id, instance_id, device, windowid_csa, storage_name, cloud_storage_grid);
                    }
                }
            }
        }
    });

    var cancel_button = new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_("取消"),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow(windowid_csa);
            }
        }
    });

    var instance_button = new Ext.Button({
        name: 'instance_button',
        id: 'instance_button',
        text:_(""),
        icon:'/icons/storage_pool.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var acc_id = storage_rec.get("account_id");
                var region_id = storage_rec.get("region_id");
                var zone_id = storage_rec.get("zone_id");
                var windowid_inst = Ext.id();
                showWindow(_("虚拟机"), 425, 475, CloudInstanceList(vdc_id, acc_id, region_id, "STORAGE", windowid_inst, zone_id), windowid_inst);
            }
        }
    });

    //Collect values from grid
    if (cloud_storage_grid.getSelectionModel().getSelected() != undefined) {
        tf_id.value = storage_rec.get('id');
        tf_storage.value = storage_rec.get('volume_id');
        if(storage_rec.get('name')) {
            tf_storage_name.value = storage_rec.get('name');
        } else {
            tf_storage_name.value = storage_rec.get('volume_id');
        }
    }

    var instance_fldset=new Ext.form.FieldSet({
        //title: _('Instance Details'),
        collapsible: false,
        autoHeight:true,
        width:'100%',
        labelWidth:80,
        layout:'column',
        border:false,
        style:'padding:0px 0px 0px 0px',
        items: [{
            width: 243,
            height:22,
            layout:'form',
            border:false,
            items:[tf_instance_name]
        },{
            width: 50,
            height:22,
            layout:'form',
            border:false,
            items:[instance_button]
        }]
    });

    function get_cloud_storage_attach_form() {
        cloud_storage_attach_form = new Ext.FormPanel({
            //title: _("Create Storage"),
            labelWidth:80,
            frame:true,
            border:0,
            bodyStyle:'padding:0px 0px 0px 0px',
            labelAlign:"left" ,
            height: 180,
            labelSeparator: ' ',
            items:[tf_id, tf_storage_name, instance_fldset, tf_device, lbl_device_info],
            bbar:[{xtype: 'tbfill'},
                attach_button,
                '-',
                cancel_button
            ]
        });
        return cloud_storage_attach_form;
    };

    var return_form = get_cloud_storage_attach_form();
    return return_form;
}

function attachCloudStorage(vdc_id, acc_id, region_id, volume_id, instance_id, device, windowid_csa, storage_name, grid){
    var url='/cloud_storage/attach_volume?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&volume_id=' + volume_id + '&instance_id=' + instance_id + '&device=' + device + '&storage_name=' + storage_name;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var wait_msg = _('正在附加存储...');
                var success_msg = _("存储" + storage_name + "附加成功.");
                var task_id = response.task_id;
                var wait_time = 3000;
                wait_for_storage_task(task_id, wait_time, wait_msg, success_msg, windowid_csa, grid);
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}

