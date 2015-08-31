/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function credentialsform(node){
    var username=new Ext.form.TextField({
        fieldLabel: _('用户名'),
        name: 'user_name',
        allowBlank:false,
        width: 150,
        value:'root'
    });
    var password=new Ext.form.TextField({
        fieldLabel: _('密码'),
        name: 'pwd',
        allowBlank:false,
        width: 150,
        inputType : 'password'
    });
    var form = new Ext.FormPanel({
        labelWidth:90,
        frame:true,
        border:0,
        labelAlign:"left" ,
        width:280,
        height:120,
        labelSeparator: ' ',
        items:[username,password]
    });

    form.addButton(_("确定"),function(){
        if (form.getForm().isValid()) {
            var uname=username.getValue();
            var pwd=password.getValue();
            closeWindow();
            connectNode(node,uname,pwd);
            
        }else{
            Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
        }
    });
    form.addButton(_("取消"),function(){
        Ext.MessageBox.alert(_('错误:'), format(_("{0}:服务器没有验证"),node.text));
        form.destroy();
        closeWindow();
    });

    return form;
}

function connectNode(node,username,password){
    var url="/node/connect_node?node_id="+node.attributes.id+"&username="+username+"&password="+password;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    var iconClass=node.getUI().getIconEl().className;
    node.getUI().getIconEl().className="x-tree-node-icon loading_icon";
    ajaxReq.request({
        success: function(xhr) {
            node.getUI().getIconEl().className=iconClass;
            var res=Ext.util.JSON.decode(xhr.responseText);
            if(res.success){
                node.fireEvent('click',node);
            }else{
                if(res.error=='Not Authenticated'){
                    showWindow(_("认证 ")+node.text,280,150,credentialsform(node));
                    return;
                }else{
                    Ext.MessageBox.alert(_("Error"),res.msg);
                }
            }
        },
        failure: function(xhr){
            node.getUI().getIconEl().className=iconClass;
            Ext.MessageBox.alert(_("错误"),_("失败: ") +xhr.statusText);
        }
    });
}