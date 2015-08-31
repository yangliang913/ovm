/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var tf_snapshot; //This is declared at form level because we need to access it from CloudSnapshotList.js
function CloudStorageDefinition(vdc_id, mode, storage_rec, windowid_csd, vm_info, snapshot_rec, cp_feature) {
    /*
    mode: this would be "NEW" or "EDIT".
    storage_rec: storage record (selected record in storage grid store).
    windowid_csd window id (e.g., windowid_csd=Ext.id();)
    */
    var cloud_storage_def_form, acc_id, region_id;
    if(snapshot_rec){
        var acc_id = snapshot_rec.get('account_id');
        var region_id = snapshot_rec.get('region_id');
    }

    var zone_store =new Ext.data.JsonStore({
        url: "/cloud/get_all_zones?",
        root: 'rows',
        fields: ['name','id'],
        successProperty:'success',
        listeners:{
            load:function(obj,opts,res,e){
                if(zone_store.getCount()==1){
                    cmb_zone.setValue(zone_store.getAt(0).get('id'));
                    cmb_zone.fireEvent('select',cmb_zone,zone_store.getAt(0),0);
                }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    
    var size_store=new Ext.data.JsonStore({
        root: 'rows',
        fields: ['name', 'value'],
        autoLoad: true,
        data: {rows: [{'name':'GiB', 'value':'GiB'}, {'name':'TiB', 'value':'TiB'}]}
    });

    var tf_id=new Ext.form.TextField({
        //fieldLabel: _('Id'),
        name: 'tf_id',
        id: 'tf_id',
        width: 200,
        allowBlank:true,
        hidden: true
    });
    
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

    var tf_size=new Ext.form.NumberField({
        fieldLabel: _('大小:'),
        name: 'tf_size',
        id: 'tf_size',
        width: 75,
        allowBlank:false,
        hidden: false
    });

    var cmb_size_unit=new Ext.form.ComboBox({
        //fieldLabel: _('Size'),
        triggerAction:'all',
        root:'rows',
        store: size_store,
        displayField:'name',
        valueField:'value',
        width: 60,
        allowBlank: false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'cmb_size_unit',
        id:'cmb_size_unit',
        mode:'local'
    });

    var cmb_zone=new Ext.form.ComboBox({
        fieldLabel: _('Zone:'),
        triggerAction:'all',
        root:'rows',
        store: zone_store,
        emptyText :_("选择Zone"),
        editable:false,
        displayField:'name',
        valueField:'id',
        width: 200,
        allowBlank: false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'cmb_zone',
        id:'cmb_zone',
        mode:'local',
        hidden:!is_feature_enabled(cp_feature, stackone.constants.CF_REGION)
    });
    cmb_zone.hideLabel = !is_feature_enabled(cp_feature, stackone.constants.CF_REGION);

    tf_snapshot=new Ext.form.TextField({
        fieldLabel: _('快照'),
        name: 'tf_snapshot',
        id: 'tf_snapshot',
        width: 150,
        allowBlank:true,
        hidden:!is_feature_enabled(cp_feature, stackone.constants.CF_SNAPSHOT)
    });
    tf_snapshot.hideLabel=!is_feature_enabled(cp_feature, stackone.constants.CF_SNAPSHOT);

    var snapshot_button = new Ext.Button({
        name: 'snapshot_button',
        id: 'snapshot_button',
        text:_(""),
        icon:'/icons/storage_pool.png',
        cls:'x-btn-text-icon',
        hidden:!is_feature_enabled(cp_feature, stackone.constants.CF_SNAPSHOT),
        listeners: {
            click: function(btn) {
                var windowid_snap = Ext.id();
                var account_id = cmb_account.getValue();
                var region_id = cmb_region.getValue();
                if(!cmb_account.getValue()) {
                    Ext.MessageBox.alert("信息", "请选择账户.");
                } else if(!cmb_region.getValue()) {
                    Ext.MessageBox.alert("信息", "请选择区域.");
                } else {
                    showWindow(_("快照列表"), 425, 475, CloudSnapshotList(vdc_id, account_id, region_id, windowid_snap), windowid_snap);

                    Ext.MessageBox.show({
                        title:_('请稍候...'),
                        msg: _('正在加载快照...'),
                        width:300,
                        wait:true,
                        waitConfig: {
                            interval:3000
                        }
                    });

                }
            }
        }
    });

    //disable 'list snapshot' button for 'Create Storage' in the 'Snapshot List' panel.
    if(snapshot_rec != undefined){
        snapshot_button.disable();
    }
    
    var account_store =new Ext.data.JsonStore({
        url: "/cloud/get_accountsforvdc?vdcid="+vdc_id,
        root: 'info',
        fields: ['name','value'],
        successProperty:'success',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        listeners:{
            load:function(obj,opts,res,e){
                if(account_store.getCount()==1){
                    cmb_account.setValue(account_store.getAt(0).get('value'));
                    cmb_account.fireEvent('select',cmb_account,account_store.getAt(0),0);
                }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    var cmb_account = new Ext.form.ComboBox({
        id: 'cmb_account',
        fieldLabel: _('账户:'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择账户"),
        store:account_store,
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
        hidden : !is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT),
        listeners: {
            select: function(combo, record, index){
                region_store.load({
                    params:{
                            vdcid:vdc_id,
                            accountid:cmb_account.getValue()
                        }
                });
            }
        }
    });
    cmb_account.hideLabel = !is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT);
    account_store.load();

    var region_store =new Ext.data.JsonStore({
        url: "/cloud/get_regionforvdc?",
        root: 'info',
        fields: ['name','value'],
        successProperty:'success',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        listeners:{
            load:function(obj,opts,res,e){
                if(region_store.getCount()==1){
                    cmb_region.setValue(region_store.getAt(0).get('value'));
                    cmb_region.fireEvent('select',cmb_region,region_store.getAt(0),0);
                }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    region_store.load({
        params:{
            vdcid:vdc_id
        }
    });

    var cmb_region = new Ext.form.ComboBox({
        id: 'cmb_region',
        fieldLabel: _('区域:'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择区域"),
        store:region_store,
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
        hidden : !is_feature_enabled(cp_feature, stackone.constants.CF_REGION),
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
    cmb_region.hideLabel = !is_feature_enabled(cp_feature, stackone.constants.CF_REGION);
        
    var save_button = new Ext.Button({
        name: 'save',
        id: 'save',
        text:((mode=="EDIT")? _("保存"):_("创建")),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var url, wait_msg, success_msg, desc, size, size_unit, zone, region, region_id, acc_id;
                if (cloud_storage_def_form.getForm().isValid()) {
                    storage_name = tf_name.getValue();
                    if(mode == "EDIT") {
                        if (cloud_storage_grid.getSelectionModel().getSelected() != undefined) {
                            rec = cloud_storage_grid.getSelectionModel().getSelected();
                            storage_id = rec.get('id');
                            storage_name = tf_name.getValue();
                            storage_desc = tf_desc.getValue();
                            acc_id = storage_rec.get("account_id");
                            region_id = storage_rec.get("region_id");
    
                            url='/cloud_storage/edit_volume?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&volume_id=' + storage_id + '&name=' + storage_name + '&desc=' + storage_desc;
                            wait_msg = _('正在更新存储...');
                            success_msg = _("存储" + storage_name + "更新成功.");
                        }
                    } else {
                        s_name=tf_name.getValue();
                        desc=tf_desc.getValue();
                        size=tf_size.getValue();
                        size_unit=cmb_size_unit.getValue();
                        zone=cmb_zone.getRawValue();
                        zone_id=cmb_zone.getValue();
                        snapshot=tf_snapshot.getValue(); //this is snapshot_id (external id)
                        region=cmb_zone.getValue();
                        if(snapshot_rec){
                            acc_id = snapshot_rec.get("account_id");
                            region_id = snapshot_rec.get("region_id");
                            snapshot = snapshot_rec.get("snapshot_id");
                        } else {
                            acc_id = cmb_account.getValue();
                            region_id = cmb_region.getValue();
                        }

                        if(snapshot) {
                            url='/cloud_storage/add_volume?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&name=' + s_name + '&desc=' + desc + '&size=' + size + '&size_unit=' + size_unit + '&zone=' + zone + '&zone_id=' + zone_id + '&snapshot=' + snapshot;
                        } else {
                            url='/cloud_storage/add_volume?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&name=' + s_name + '&desc=' + desc + '&size=' + size + '&size_unit=' + size_unit + '&zone=' + zone + '&zone_id=' + zone_id;
                        }
                        wait_msg = _('正在创建存储...');
                        success_msg = _("存储 " + storage_name + "创建成功.");
                    }

                    var ajaxReq=ajaxRequest(url,0,"GET",true);
                    ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                var task_id = response.task_id;
                                var wait_time = 3000;
                                
                                var volume_object = null;
                                if(vm_info){
                                    
                                    var vm_id, vm_name, instance_id;
                                    if(vm_info.getCount()>0){
                                        var rec = vm_info.getAt(0);
                                        vm_id = rec.get("id");
                                        vm_name = rec.get("name");
                                        instance_id = rec.get("instance_id");
                                    }else{
                                        //alert("count is zero");
                                    }

                                    volume_object = new Object();
                                    volume_object.vdc_id = vdc_id;
                                    volume_object.acc_id = acc_id;
                                    volume_object.region_id = region_id;
                                    volume_object.zone_id = zone_id;
                                    volume_object.volume_id = null;
                                    volume_object.instance_id = instance_id;
                                    volume_object.vm_id = vm_id;
                                    volume_object.vm_name = vm_name;
                                    volume_object.storage_name = storage_name;
                                }
                                wait_for_storage_task(task_id, wait_time, wait_msg, success_msg, windowid_csd, cloud_storage_grid, volume_object);
                            }else{
                                Ext.MessageBox.alert("失败",response.msg);
                            }
                        },
                        failure: function(xhr){
                            Ext.MessageBox.alert( "失败 " , xhr.statusText);
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
                closeWindow(windowid_csd);
            }
        }
    });

    if(mode=="EDIT"){
        if (cloud_storage_grid.getSelectionModel().getSelected() != undefined) {
            tf_id.value = storage_rec.get('id');
            tf_name.value = storage_rec.get('name');
            tf_desc.value = storage_rec.get('description');
            tf_size.value = storage_rec.get('size');
            cmb_size_unit.value = storage_rec.get('size_unit');
            cmb_zone.value = storage_rec.get('zone');
            tf_snapshot.value = storage_rec.get('snapshot');
            cmb_account.value = storage_rec.get('account_name');
            cmb_region.value = storage_rec.get('region');
        }
        tf_size.disable();
        cmb_size_unit.disable();
        cmb_zone.disable();
        tf_snapshot.disable();
        snapshot_button.disable();
        cmb_account.disable();
        cmb_region.disable();
    } else {
        if(snapshot_rec) {
            cmb_account.value = snapshot_rec.get('account_name');
            cmb_region.value = snapshot_rec.get('region');
            tf_snapshot.value = snapshot_rec.get('name');
            cmb_account.disable();
            cmb_region.disable();
            tf_snapshot.disable();

            //load zone combobox
            zone_store.load({
                params:{
                    region_id:snapshot_rec.get('region_id'),
                    acc_id:snapshot_rec.get('account_id'),
                    vdc_id:vdc_id
                }
            });
        }
    };

    var lbl_size=new Ext.form.Label({
        html:_('大小:<div style="width:85px"/>')
    });

    var size_space=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });

    var size_panel = new Ext.Panel({
        //fieldLabel: _('Size'),
        bodyStyle:'padding:0px 0px 0px 0px',
        width:'100%',
        height: 26,
        frame:false,
        layout:'column',
        items:[lbl_size, tf_size, size_space, cmb_size_unit]
    });

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
            items:[tf_snapshot]
        },{
            width: 50,
            layout:'form',
            border:false,
            items:[snapshot_button]
        }]
    });

    var height = 245;
    if (!is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT)){
        height = 145;
    }
    function get_cloud_storage_def_form() {
        cloud_storage_def_form = new Ext.FormPanel({
            //title: _("Create Storage"),
            labelWidth:80, //120
            frame:true,
            border:0,
            bodyStyle:'padding:0px 0px 0px 0px',
            labelAlign:"left" ,
            height: height, 
            labelSeparator: ' ',
            items:[tf_id, tf_name, tf_desc, size_panel, cmb_account, cmb_region, cmb_zone, snapshot_fldset],
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
        return cloud_storage_def_form;
    };

    var return_form = get_cloud_storage_def_form();
    return return_form;
}
