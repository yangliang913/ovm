/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var key_def_form;
function KeyPairDefinition(vdc_id, mode, key_pair, windowid) {
    var tf_key_name=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'key_name1',
        id: 'key_name1',
        width: 200,
        allowBlank:false,
        hidden: false
    });
    var tf_key_desc=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'key_desc1',
        id: 'key_desc1',
        width: 200,
        allowBlank:false,
        hidden: false
    });

    var region_store = new Ext.data.JsonStore({
        root: 'rows',
        fields: ['id', 'region'],
        autoLoad: true,
        data: {rows: [{'id':'US East (Virginia)', 'region':'US East (Virginia)'}, {'id':'US West (N. California)', 'region':'US West (N. California)'}, {'id':'EU West (Ireland)', 'region':'EU West (Ireland)'}, {'id':'Asia Pacific (Singapore)', 'region':'Asia Pacific (Singapore)'}]}
    });

    var cmb_region = create_region_dropdown(vdc_id);
    cmb_region.width = 200;


    var cmb_account=null;
    if (mode=="PROVISION"){
        cmb_account = create_account_dropdown(vdc_id,null,"key_pair");
        cmb_account.setValue(Ext.getCmp("account").getRawValue());
        cmb_account.disable();
        cmb_region.setValue(Ext.getCmp("region_general").getRawValue());
        cmb_region.disable();

    }
    else
        cmb_account = create_account_dropdown(vdc_id, "provision");

    cmb_account.width = 200;

    var save_button = new Ext.Button({
        name: 'save',
        id: 'save',
        text:((mode=="EDIT")? _("保存"):_("创建")),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var msg, url, key_name, key_desc;
                if (key_def_form.getForm().isValid()) {
                    if(mode == "EDIT") {
                        if (key_pair_grid.getSelectionModel().getSelected() != undefined) {
                            key_name = key_pair.get('name');
                            key_desc = tf_key_desc.getValue();
                            acc_id = key_pair.get("account_id");
                            region_id = key_pair.get("region_id");

                            url='/cloud_network/edit_key?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&key_name=' + key_name + '&desc=' + key_desc;
                            msg=_('正在更新密钥对...');
                        }
                    } else {

                        if (mode=="NEW") {
                            var acc_id = cmb_account.getValue();
                            var region_id = cmb_region.getValue();
                        }else if  (mode=="PROVISION") {
                            acc_id = Ext.getCmp("account").getValue();
                            region_id = Ext.getCmp("region_general").getValue();

                        }
                        key_name=tf_key_name.getValue();
                        key_desc=tf_key_desc.getValue();

                        url='/cloud_network/add_key?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&key_name=' + key_name + '&desc=' + key_desc;
                        msg=_('正在创建密钥对...');
                    }

                    var ajaxReq=ajaxRequest(url,0,"GET",true);
                    ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                    var task_id = response.task_id;
                                    var wait_time = 3000;
                                    wait_for_kp_create_task(task_id, wait_time, mode, msg, vdc_id, acc_id, region_id, key_name, windowid);
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
                closeWindow(windowid);
            }
        }
    });

    function get_key_def_form() {
        key_def_form = new Ext.FormPanel({
            //title: _("Create Key Pair"),
            labelWidth:80, //120
            frame:true,
            border:0,
            bodyStyle:'padding:5px 0px 5px 5px', //top, right, bottom, left
            labelAlign:"left" ,
            //width:380, //418
            height: 160,
            //autoHeight:true,
            labelSeparator: ' ',
            items:[tf_key_name, tf_key_desc, cmb_account, cmb_region],
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
        
        return key_def_form;
    };

    if(mode=="EDIT"){
        if (key_pair_grid.getSelectionModel().getSelected() != undefined) {
            tf_key_name.value = key_pair.get('name');
            tf_key_desc.value = key_pair.get('description');
            cmb_account.setValue(key_pair.get('account_name'));
            cmb_region.setValue(key_pair.get('region'));
        }
        tf_key_name.disable();
        cmb_region.disable();
        cmb_account.disable();
    };

    var return_form = get_key_def_form();
    return return_form;
}

function wait_for_kp_create_task(task_id, wait_time, mode, msg, vdc_id, acc_id, region_id, key_name, windowid){
    //alert("waiting for task completion...");
    //alert("mode is " + mode);
    var url = '/cloud_network/wait_for_task?task_id=' + task_id + '&wait_time=' + wait_time;
    //alert("url is " + url);
    Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: msg,
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
                //Ext.MessageBox.alert("Success", response.status);
                if(mode != "PROVISION")
                    reloadKPList();
                else{
                    Ext.getCmp("key_pair").getStore().load({
                     params:{
                         vdc_id:vdc_id,
                         acc_id:Ext.getCmp("account").getValue(),
                         region_id:Ext.getCmp("region_general").getValue(),
                         kp_type:"provision"
                     }
                    }
                    );

                }
                if(mode == "NEW" || mode == "PROVISION" ) {
                    var message_text = "确定要下载key吗?"
                    Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                        if(id=='yes'){
                            downloadKeyPair(vdc_id, acc_id, region_id, key_name);
                        }
                        Ext.MessageBox.alert(_("信息"), _("密钥对" + key_name + "创建成功."));
                        closeWindow(windowid);
                    });
                } else {
                    Ext.MessageBox.alert(_("信息"), _("密钥对" + key_name + "更新成功."));
                    closeWindow(windowid);
                }
            }else{
                Ext.MessageBox.alert(_("失败"), response.status);
                closeWindow(windowid);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }

    });
}
