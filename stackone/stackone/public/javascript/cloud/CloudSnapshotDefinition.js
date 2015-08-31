/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var tf_storage, tf_storage_name; //This is declared at form level because we need to access it from CloudVolumeList.js
function CloudSnapshotDefinition(vdc_id, mode, storage_rec, windowId) {
    /*
    parameter info:
    mode: this would be "NEW" or "EDIT".
    storage_rec: storage record (selected record in storage grid store).
    windowId window id (e.g., windowId=Ext.id();)
    */
    var cloud_snapshot_def_form, acc_id, region_id;
    
    var tf_name=new Ext.form.TextField({
        fieldLabel: _('名称:'),
        name: 'tf_name',
        id: 'tf_name',
        width: 200,
        allowBlank:false,
        hidden: false
    });

    var tf_desc=new Ext.form.TextField({
        fieldLabel: _('说明:'),
        name: 'tf_desc',
        id: 'tf_desc',
        width: 200,
        allowBlank:false,
        hidden: false
    });

    tf_storage=new Ext.form.TextField({
        fieldLabel: _('存储'),
        name: 'tf_storage',
        id: 'tf_storage',
        width: 150,
        allowBlank:false,
        hidden: true
    });

    tf_storage_name=new Ext.form.TextField({
        fieldLabel: _('存储'),
        name: 'tf_storage_name',
        id: 'tf_storage_name',
        width: 150,
        allowBlank:false,
        hidden: false
    });

    var cmb_account_common = create_account_dropdown(vdc_id, "provision");
    var cmb_region_common = create_region_dropdown(vdc_id);

    var cmb_account = new Ext.form.ComboBox({
        id: 'cmb_account',
        fieldLabel: _('账户:'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择账户"),
        store:cmb_account_common.getStore(),
        width:200,
        displayField:'name',
        editable:false,
        valueField:'value',
        typeAhead: true,
        minListWidth:50,
        labelSeparator:" ",
        mode:'local',
        forceSelection: true,
        selectOnFocus:true,
        listeners: {
            select: function(combo, record, index){
                cmb_region_common.getStore().load({
                    params:{
                            vdcid:vdc_id,
                            accountid:cmb_account.getValue()
                        }
                });
            }
        }
    });

    var cmb_region = new Ext.form.ComboBox({
        id: 'cmb_region',
        fieldLabel: _('区域:'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择区域"),
        store:cmb_region_common.getStore(),
        width:200,
        displayField:'name',
        editable:false,
        valueField:'value',
        typeAhead: true,
        minListWidth:50,
        labelSeparator:" ",
        mode:'local',
        forceSelection: true,
        selectOnFocus:true,
        listeners: {
            select: function(combo, record, index){
                zone_store.load({
                    params:{
                        region_id:cmb_region.getValue(),
                        acc_id:cmb_account.getValue(),
                        vdc_id:vdc_id
                    }
                });
            }
        }
    });

    var storage_button = new Ext.Button({
        name: 'storage_button',
        id: 'storage_button',
        text:_(""),
        icon:'/icons/storage_pool.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var windowId = Ext.id();
                var region_id = cmb_region.getValue();
                var account_id = cmb_account.getValue();

                if(!account_id) {
                    Ext.MessageBox.alert("信息", "请选择账户.");
                    return;
                } else if(!region_id) {
                    Ext.MessageBox.alert("信息", "请选择区域.");
                    return;
                }
                var zone_id = null;
                var vm_id = null;
                var list_type = "SNAPSHOT";
                showWindow(_("存储列表"), 425, 475, CloudVolumeList(vdc_id, account_id, region_id, zone_id, vm_id, windowId, list_type), windowId);
            }
        }
    });
        
    var save_button = new Ext.Button({
        name: 'save',
        id: 'save',
        text:((mode=="EDIT")? _("保存"):_("创建")),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var url, wait_msg, success_msg, snapshot_name, desc, region_id, acc_id;
                if (cloud_snapshot_def_form.getForm().isValid()) {
                    snapshot_name = tf_name.getValue();
                    desc = tf_desc.getValue();
                    volume_id = tf_storage.getValue();
                    if(storage_rec) {
                        acc_id = storage_rec.get("account_id");
                        region_id = storage_rec.get("region_id");
                    } else {
                        acc_id = cmb_account.getValue();
                        region_id = cmb_region.getValue();
                    }

                    if(mode == "NEW") {
                        url='/cloud_storage/add_snapshot?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&volume_id=' + volume_id + '&name=' + snapshot_name + '&desc=' + desc;
                        wait_msg = _('正在创建快照...');
                        success_msg = _("快照" + snapshot_name + "创建成功.");
                    } else {
                        url='/cloud_storage/edit_snapshot?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&volume_id=' + volume_id + '&name=' + snapshot_name + '&desc=' + desc;
                        wait_msg = _('正在更新存储...');
                        success_msg = _("快照" + snapshot_name + " 更新成功.");
                    }

                    var ajaxReq=ajaxRequest(url,0,"GET",true);
                    ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                var task_id = response.task_id;
                                var wait_time = 3000;
                                
                                wait_for_snapshot_task(task_id, wait_time, wait_msg, success_msg, windowId, cloud_snapshot_grid);
                            }else{
                                Ext.MessageBox.alert("失败",response.msg);
                            }
                        },
                        failure: function(xhr){
                            Ext.MessageBox.alert( "失败" , xhr.statusText);
                        }
                    });
                }else{
                    Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
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
                closeWindow(windowId);
            }
        }
    });

    if(mode=="NEW"){
        if(storage_rec){
            tf_storage.value = storage_rec.get('volume_id');
            tf_storage_name.value = storage_rec.get('name');
            cmb_account.setValue(storage_rec.get('account_name'));
            cmb_region.setValue(storage_rec.get('region'));
            tf_storage.disable();
            tf_storage_name.disable();
            storage_button.disable();
            cmb_account.disable();
            cmb_region.disable();
        }
    }else{
        if(storage_rec){
            tf_storage.value = storage_rec.get('volume_id');
            tf_storage_name.value = storage_rec.get('name');
            cmb_account.setValue(storage_rec.get('account_name'));
            cmb_region.setValue(storage_rec.get('region'));
            tf_storage.disable();
            tf_storage_name.disable();
            storage_button.disable();
            cmb_account.disable();
            cmb_region.disable();
        }
    }

    var snapshot_fldset=new Ext.form.FieldSet({
        //title: _('Snapshot Details'),
        collapsible: false,
        autoHeight:true,
        width:'100%',
        labelWidth:80, //120
        layout:'column',
        border:false,
        style:'padding:0px 0px 0px 0px',    //top, right, bottom, left
        items: [{
            width: 243,
            layout:'form',
            border:false,
            items:[tf_storage_name]
        },{
            width: 50,
            layout:'form',
            border:false,
            items:[storage_button]
        }]
    });

    function get_cloud_snapshot_def_form() {
        cloud_snapshot_def_form = new Ext.FormPanel({
            //title: _("Create Storage"),
            labelWidth:80, //120
            frame:true,
            border:0,
            bodyStyle:'padding:10px 0px 0px 0px',
            labelAlign:"left" ,
            height: 197, //195
            labelSeparator: ' ',
            items:[tf_name, tf_desc, cmb_account, cmb_region, snapshot_fldset],
            bbar:[{xtype: 'tbfill'},
                save_button,
                '-',
                cancel_button
            ]
        });
         if(cmb_account.getStore().getCount()==0){
            cmb_account.hide();
            cmb_account.hideLabel = true;
        }
        return cloud_snapshot_def_form;
    };

    var return_form = get_cloud_snapshot_def_form();
    return return_form;
}
