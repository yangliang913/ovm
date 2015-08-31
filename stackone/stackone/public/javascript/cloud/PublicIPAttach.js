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
function PublicIPAttachWin(vdc_id, ip_rec, windowid_ipa) {
    /*
    ip_rec: security group rule record (selected record in security grid rule store).
    windowid_ipa window id (e.g., windowid_ipa=Ext.id();)
    */
    var public_ip_attach_form;

    var tf_id=new Ext.form.TextField({
        //fieldLabel: _('Id'),
        name: 'tf_id',
        id: 'tf_id',
        width: 200,
        allowBlank:true,
        hidden: true
    });
    var tf_public_ip=new Ext.form.TextField({
        fieldLabel: _('公共IP:'),
        name: 'tf_public_ip',
        id: 'tf_public_ip',
        width: 200,
        allowBlank:false,
        hidden: false,
        disabled: true
    });
    tf_instance=new Ext.form.TextField({
        fieldLabel: _('虚拟机'),
        name: 'tf_instance',
        id: 'tf_instance',
        width: 180,
        allowBlank: false,
        hidden: false,
        disabled: true
    });

    tf_instance_name=new Ext.form.TextField({
        fieldLabel: _('实例'),
        name: 'tf_instance_name',
        id: 'tf_instance_name',
        width: 180,
        allowBlank: false,
        hidden: false,
        disabled: true
    });

    var attach_button = new Ext.Button({
        name: 'attach_button',
        id: 'attach_button',
        text:_("附加"),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedPublicIP(public_ip_grid)){
                    if(public_ip_attach_form.getForm().isValid()){
                        var rec = public_ip_grid.getSelectionModel().getSelected();
                        var public_ip_id = rec.get('id');
                        var public_ip = rec.get('public_ip');
                        var acc_id = rec.get('account_id');
                        var region_id = rec.get('region_id');
                        var instance_name = tf_instance.getValue();
                        attachPublicIP(vdc_id, acc_id, region_id, public_ip, public_ip_id, instance_name, windowid_ipa);
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
                closeWindow(windowid_ipa);
            }
        }
    });

    var instance_button = new Ext.Button({
        name: 'instance_button',
        id: 'instance_button',
        text:_(""),
        icon:'/icons/search.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var acc_id = ip_rec.get("account_id");
                var region_id = ip_rec.get("region_id");
                var windowid_inst = Ext.id();
                showWindow(_("虚拟机"), 425, 475, CloudInstanceList(vdc_id, acc_id, region_id, "PUBLIC_IP", windowid_inst, null), windowid_inst);
            }
        }
    });

    //Collect values from grid
    if (public_ip_grid.getSelectionModel().getSelected() != undefined) {
        tf_id.value = ip_rec.get('id');
        tf_public_ip.value = ip_rec.get('public_ip');
    }

    var instance_fldset=new Ext.form.FieldSet({
        //title: _('Instance Details'),
        collapsible: false,
        autoHeight:true,
        width:'100%',
        labelWidth:100, //120
        layout:'column',
        border:false,
        style:'padding:0px 0px 0px 0px', //top, right, bottom, left
        items: [{
            width: 283,
            height:22,
            hidden:true,
            layout:'form',
            border:false,
            items:[tf_instance]
        },
        {
            width: 283,
            height:22,
            layout:'form',
            border:false,
            items:[tf_instance_name]
        },
        {
            width: 50,
            height:22,
            layout:'form',
            border:false,
            items:[instance_button]
        }]
    });

    function get_public_ip_attach_form() {
        public_ip_attach_form = new Ext.FormPanel({
            //title: _("Create Public IP"),
            labelWidth:100, //120
            frame:true,
            border:0,
            bodyStyle:'padding:0px 0px 0px 0px',    //top, right, bottom, left
            labelAlign:"left" ,
            height: 120,
            labelSeparator: ' ',
            items:[tf_id, tf_public_ip, instance_fldset],
            bbar:[{xtype: 'tbfill'},
                attach_button,
                '-',
                cancel_button
            ]
        });
        return public_ip_attach_form;
    };

    var return_form = get_public_ip_attach_form();
    return return_form;
}

function attachPublicIP(vdc_id, acc_id, region_id, public_ip, public_ip_id, instance_name, windowid_ipa){
    var url='/cloud_network/attach_public_ip?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&public_ip=' + public_ip + '&public_ip_id=' + public_ip_id + '&instance_name=' + instance_name;

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var task_id = response.task_id;
                var wait_time = 3000;
                var wait_msg = _('正在附加公共IP...');
                var success_msg = _("公共IP " + public_ip + "附加成功.");
                wait_for_public_ip_task(task_id, wait_time, wait_msg, success_msg, windowid_ipa);
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}
