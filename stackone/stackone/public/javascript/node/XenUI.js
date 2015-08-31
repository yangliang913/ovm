/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function XenUI(node,prntNode,mode,mgd_node){
    var hostname=new Ext.form.TextField({
        fieldLabel: _('主机名称'),
        name: 'host_name',
        id: 'host_name',
        width: 150,
        allowBlank:false
    });
    var protocol = new Ext.form.ComboBox({
        fieldLabel: _('Xen Protocol'),
        store: [['tcp','XML-RPC'],['ssl','XML-RPC over SSL'],['ssh_tunnel','XML-RPC over SSH Tunnel']],
        allowBlank:false,
        mode: 'local',
        width: 150,
        forceSelection: true,
        value:'tcp',
        name:'prtcl',
        triggerAction :'all',
        id:'protocol'
    });

    var username=new Ext.form.TextField({
        fieldLabel: _('用户名'),
        name: 'user_name',
        id: 'user_name',
        value:'root',
        width: 150,
        allowBlank:false
    });
    var password=new Ext.form.TextField({
        fieldLabel: _('密码'),
        name: 'pwd',
        id: 'pwd',
        width: 150,
        inputType : 'password'
    });
    var xen_port=new Ext.form.TextField({
        fieldLabel: _('Xen端口'),
        name: 'xenport',
        id: 'xen_port',
        width: 150,
        allowBlank:false,
        value:8006
    });
    var xen_mgrn_port=new Ext.form.TextField({
        fieldLabel: _('Xen 迁移端口'),
        name: 'xenmigrationport',
        id: 'xen_migration_port',
        allowBlank:false,
        width: 150,
        value:8002
    });
    var ssh_port=new Ext.form.TextField({
        fieldLabel: _('SSH端口'),
        name: 'sshport',
        id: 'sshport',
        allowBlank:false,
        width: 150,
        value:22
    });
    var use_keys=new Ext.form.Checkbox({
        fieldLabel: _('使用SSH Keys'),
        name: 'usekeys',
        id: 'usekeys',
        width: 150
//        listeners:{
//            check:function(field,checked){
//                password.setDisabled(checked);
//            }
//        }
    });
    var is_standby=new Ext.form.Checkbox({
        fieldLabel: _('备用'),
        name: 'is_standby',
        id: 'is_standby',
        width: 150
//        listeners:{
//            check:function(field,checked){
//                password.setDisabled(checked);
//            }
//        }
    });

    var fldset=new Ext.form.FieldSet({
        title: _('高级'),
        collapsible: true,
        autoHeight:true,
        width: 300,
        collapsed: false,
        items :[ xen_port,xen_mgrn_port,ssh_port,use_keys,is_standby ]
    });

    var simple = new Ext.FormPanel({
        labelWidth:120,
        frame:true,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        labelAlign:"right" ,
        width:315,
        height:320,
        labelSeparator: ' ',
        items:[hostname,protocol,username,password,fldset]
    });
    var url='/node/add_node?group_id='+prntNode.attributes.id;
    use_keys.setValue(true); // Default to true
    if(mode=='edit'){
        url='/node/edit_node?node_id='+node.attributes.id;
        hostname.setValue(mgd_node.hostname);
        hostname.setDisabled(true);
        username.setValue(mgd_node.username);
        protocol.setValue(mgd_node.protocol);
        xen_port.setValue(mgd_node.xen_port);
        xen_mgrn_port.setValue(mgd_node.migration_port);
        ssh_port.setValue(mgd_node.ssh_port);
        use_keys.setValue(mgd_node.use_keys=='True');
        is_standby.setValue(mgd_node.is_standby);
//        password.setDisabled(mgd_node.use_keys=='True');
    }
    simple.addButton(_("确定"),function(){
        if (simple.getForm().isValid()) {
            //simple.getForm().submit({
             Ext.MessageBox.show({
                title:_('请稍候...'),
                msg: _('请稍候...'),
                width:200,
                wait:true,
                waitConfig: {
                    interval:200
                }
            });
            var ajaxReq=ajaxRequest(url,0,"GET");
            ajaxReq.request({
                //url:url,
                params: {
                    platform:'xen',
                    hostname:hostname.getValue(),
                    username:username.getValue(),
                    password:password.getValue(),
                    protocol:protocol.getValue(),
                    xen_port:xen_port.getValue(),
                    xen_migration_port:xen_mgrn_port.getValue(),
                    ssh_port:ssh_port.getValue(),
                    use_keys:use_keys.getValue(),
                    is_standby:(is_standby.getValue())?"True":"False"
                },
                success: function(xhr) {
                    Ext.MessageBox.hide();
                    //Ext.Msg.alert(_("Success"),response.msg );
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(!response.success){
                        Ext.Msg.alert(_("Failure"),response.msg);
                        return;
                    }
                    closeWindow();
                    var node_id=response.node_id;
                    var responseData=response.nodeobj;
                    prntNode.fireEvent('click',prntNode);
                    if(mode!='edit' && responseData.auto_discover != true){
                        show_importfile_dialog(node_id,responseData);
                    }

                },
                failure: function(xhr) {
                    Ext.MessageBox.hide();
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    Ext.Msg.alert(_("Failure"),response.msg); 
                },

                waitMsg:_('加载中...')
            });
        }else{
            Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
        }
    });
    simple.addButton(_("取消"),function(){
        closeWindow();
    });

    return simple;
}

