/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var public_ip_def_form;
function PublicIPDefinition(vdc_id, mode, ip_rec, windowid, cp_feature) {

    var lbl=new Ext.form.Label({
         html:'<div style="" class="labelheading">请选择你请求新公共IP的区域</div><br/>'
    });

    var tf_name=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'tf_name',
        id: 'tf_name',
        width: 200,
        allowBlank:true,
        hidden: false
    });
    var tf_desc=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'tf_desc',
        id: 'tf_desc',
        width: 200,
        allowBlank:true,
        hidden: false
    });

    var cmb_region = create_region_dropdown(vdc_id);
    cmb_region.width = 200;

    var cmb_account=null;
    if (mode=="PROVISION" || mode=="EDIT_VM"){
        cmb_account = create_account_dropdown(vdc_id, null, "public_ip");
        cmb_account.setValue(Ext.getCmp("account").getRawValue());
        cmb_account.disable();
//        cmb_region.setValue(Ext.getCmp("region_general").getRawValue());
//        cmb_region.disable();
    }
    else
        cmb_account = create_account_dropdown(vdc_id, "public_ip");

    cmb_account.width = 200;

    var save_button = new Ext.Button({
        name: 'save',
        id: 'save',
        text:((mode=="EDIT")? _("保存"):_("请求")),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                //var url, wait_msg, success_msg, ip_name, ip_desc, acc_id, region_id;
                if (public_ip_def_form.getForm().isValid()) {
                    acc_id = cmb_account.getValue();
                    region_id = cmb_region.getValue();
                    request_public_ip(vdc_id, acc_id, region_id, mode, windowid)

//                    var public_ip_name = tf_name.getValue();
//                    if(mode == "EDIT") {
//                        if (public_ip_grid.getSelectionModel().getSelected() != undefined) {
//                            rec = public_ip_grid.getSelectionModel().getSelected();
//                            acc_id = rec.get("account_id");
//                            region_id = rec.get("region_id");
//                            public_ip_id = rec.get('id');
//                            ip_name = tf_name.getValue();
//                            ip_desc = tf_desc.getValue();
//
//                            url='/cloud_network/edit_public_ip?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&public_ip_id=' + public_ip_id + '&name=' + ip_name + '&description=' + ip_desc;
//                            wait_msg = _('Updating Public IP...');
//                            success_msg = _("Public IP updated successfully.");
//                        }
//                    } else {
//                        if (mode=="NEW") {
//                            acc_id = cmb_account.getValue();
//                            region_id = cmb_region.getValue();
//                        }else if  (mode=="PROVISION") {
//                            acc_id = Ext.getCmp("account").getValue();
//                            region_id = cmb_region.getValue();
//                        }else if  (mode=="EDIT_VM") {
//                            acc_id = cloud_account_id;
//                            region_id = cloud_region_id;
//                        }
//                        msg=_('Requesting Public IP...');
//                        ip_name=tf_name.getValue();
//                        ip_desc=tf_desc.getValue();
//                        url='/cloud_network/create_public_ip?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&name=' + ip_name + '&description=' + ip_desc;
//                        wait_msg = _('Requesting Public IP...');
//                        success_msg = _("Public IP request completed successfully.");
//                    }
//                    var ajaxReq=ajaxRequest(url,0,"GET",true);
//                    ajaxReq.request({
//                        success: function(xhr) {
//                            var response=Ext.util.JSON.decode(xhr.responseText);
//                            if(response.success){
//                                    var task_id = response.task_id;
//                                    var wait_time = 3000;
//                                    wait_for_public_ip_task(task_id, wait_time, wait_msg, success_msg, windowid,mode,vdc_id);
//                            }else{
//                                Ext.MessageBox.alert("Failure",response.msg);
//                            }
//                        },
//                        failure: function(xhr){
//                            Ext.MessageBox.alert( "Failure " , xhr.statusText);
//                        }
//                    });


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

//    var req_pub_ip_panel_height = 100;
//    if(!is_feature_enabled(cp_feature, stackone.constants.CF_REGION)){
//        req_pub_ip_panel_height = 75;
//    }

    function get_public_ip_def_form() {
        public_ip_def_form = new Ext.FormPanel({
            //title: _("Create Key Pair"),
            labelWidth:80, //120
            frame:true,
            border:0,
            bodyStyle:'padding:5px 0px 5px 5px',    //top, right, bottom, left
            labelAlign:"left" ,
            //width:380, //418
            height: 115,
            //autoHeight:true,
            labelSeparator: ' ',
            items:[lbl,cmb_account, cmb_region],
            bbar:[{xtype: 'tbfill'},
                save_button,
                '-',
                cancel_button
            ]
        });
        return public_ip_def_form;
    };

    if(mode=="EDIT"){
        if (public_ip_grid.getSelectionModel().getSelected() != undefined) {
            tf_name.value = ip_rec.get('name');
            tf_desc.value = ip_rec.get('description');
            cmb_region.value = ip_rec.get('region');
            cmb_account.value = ip_rec.get('account_name');
        }
        cmb_region.disable();
    };

        cmb_account.hide();
        cmb_account.hideLabel = true;

    if (cp_feature != undefined)
        if(!is_feature_enabled(cp_feature, stackone.constants.CF_REGION))
            {//right now, Region is disabled for CMS
                cmb_region.hide();
                cmb_region.hideLabel = true;

                //hide Name and description for CMS.
//                tf_name.hide();
//                tf_name.hideLabel = true;
//                tf_name.allowBlank = true;
//                tf_desc.hide();
//                tf_desc.hideLabel = true;
//                tf_desc.allowBlank = true;
            }
    var return_form = get_public_ip_def_form();
    return return_form;
}



function request_public_ip(vdc_id, acc_id, region_id, mode, windowid){

    var url, wait_msg, success_msg, ip_name, ip_desc;
        if(mode == "EDIT") {
            //if (public_ip_grid.getSelectionModel().getSelected() != undefined) {
                //rec = public_ip_grid.getSelectionModel().getSelected();
                //acc_id = rec.get("account_id");
                //region_id = rec.get("region_id");
                public_ip_id = "";
                ip_name = "";
                ip_desc = "";

                url='/cloud_network/edit_public_ip?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&public_ip_id=' + public_ip_id + '&name=' + ip_name + '&description=' + ip_desc;
                wait_msg = _('正在更新公共IP...');
                success_msg = _("公共IP更新成功.");
            //}
        } else {
            //if (mode=="NEW") {
                //acc_id = cmb_account.getValue();
                //region_id = cmb_region.getValue();
            //}else if  (mode=="PROVISION") {
                //acc_id = Ext.getCmp("account").getValue();
                //region_id = cmb_region.getValue();
            //}else if  (mode=="EDIT_VM") {
                //acc_id = cloud_account_id;
                //region_id = cloud_region_id;
            //}
            msg=_('正在请求公共IP...');
            ip_name="";
            ip_desc="";
            url='/cloud_network/create_public_ip?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&name=' + ip_name + '&description=' + ip_desc;
            wait_msg = _('正在请求公共IP...');
            success_msg = _("公共IP请求成功.");
        }
        
        var ajaxReq=ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                        var task_id = response.task_id;
                        var wait_time = 3000;
                        wait_for_public_ip_task(task_id, wait_time, wait_msg, success_msg, windowid,mode,vdc_id);
                }else{
                    Ext.MessageBox.alert("失败",response.msg);
                }
            },
            failure: function(xhr){
                Ext.MessageBox.alert( "失败" , xhr.statusText);
            }
        });
}








