/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

function ESXiUI(node,prntNode,mode,mgd_node,plat){
    var hostname=new Ext.form.TextField({
        fieldLabel: _('主机名称'),
        name: 'host_name',
        id: 'host_name',
        width: 150,
        allowBlank:false
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
        items :[ is_standby ]
    });

    var simple = new Ext.FormPanel({
        labelWidth:120,
        frame:true,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        labelAlign:"right" ,
        width:315,
        height:145,
        labelSeparator: ' ',
        items:[hostname,username,password]
    });
    var url='/node/add_node?group_id='+prntNode.attributes.id;
    if(mode=='edit'){
        url='/node/edit_node?node_id='+node.attributes.id;
        hostname.setValue(mgd_node.hostname);
        hostname.setDisabled(true);
        username.setValue(mgd_node.username);
        is_standby.setValue(mgd_node.is_standby);
//        password.setDisabled(mgd_node.use_keys=='True');
    }
    simple.addButton(_("确定"),function(){
        if (simple.getForm().isValid()) {
               Ext.MessageBox.show({
                    title:_('请稍候...'),
                    msg: _('请稍候...'),
                    width:200,
                    wait:true,
                    waitConfig: {
                        interval:200
                    }
                });
//            simple.getForm().submit({
//                url:url,
                var ajaxReq=ajaxRequest(url,0,"GET");
                ajaxReq.request({
                params: {
                    platform:plat, // # TBI : Temp Need to be fixed.
                    hostname:hostname.getValue(),
                    username:username.getValue(),
                    password:password.getValue(),
                    ssh_port:'22',
                    use_keys:"False",
                    is_standby:(is_standby.getValue())?"True":"False"
                },
                success: function(xhr) {
                    Ext.MessageBox.hide();
//               success: function(xhr) {
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
                    } else {
                        Ext.Msg.alert(_("Success"),response.msg);
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




