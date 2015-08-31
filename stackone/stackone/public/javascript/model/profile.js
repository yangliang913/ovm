/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/


function changepass(username){

    var old_passwd=new Ext.form.TextField({
        fieldLabel: _('旧密码'),
        name: 'oldpasswd',
        inputType: 'password',
        width: 130,
        id: 'oldpasswd',
        allowBlank:false
    });
    
    var new_passwd=new Ext.form.TextField({
        fieldLabel: _('新密码'),
        name: 'newpasswd',
        inputType: 'password',
        width: 130,
        id: 'newpasswd',
        allowBlank:false
    });
    var confirm_passwd=new Ext.form.TextField({
        fieldLabel: _('确认密码'),
        name: 'confpasswd',
        inputType: 'password',
        width: 130,
        id: 'confpasswd',
        allowBlank:false
    });

    var changePasswd = new Ext.FormPanel({
        labelWidth:130,
//        url:"/model/change_user_password?userid="+username+"&newpasswd="+new_passwd.getValue()+"&oldpasswd="+old_passwd.getValue(),
        frame:true,
        //title: 'User:'+username,
        // collapsible:true,
        autowidth:true,
        height:200,
        bodyStyle: 'padding: 10px 10px 0 20px;',
        padding:200,
        modal: true,
        defaultType:'textfield',
        monitorValid:true,
        items:[old_passwd,new_passwd,confirm_passwd],
        buttons:[{
            text:'确定',
            icon:'icons/accept.png',
            cls:'x-btn-text-icon',
            handler:function(){
                var flag=false,errmsg="";
                if(new_passwd.getValue() == "")
                {
                    errmsg+="<br>"+_("请输入新的密码");
                    flag=true;
                }
                if(new_passwd.getValue() != "")
                {
                    if(new_passwd.getValue() != confirm_passwd.getValue())
                    {
                        errmsg+="<br>"+_("新密码和确认密码不一致");
                        flag=true;
                    }
                }
                if(flag){
                    Ext.MessageBox.alert(_("警告"),errmsg);
                    return ;
                }
                var password=new_passwd.getValue();
                    var  x = password;
                    var invalid_chars=new Array(' ','!','@','#','$','%','^','&','(',')','|','?','>','<','[',']','{','}','*','"',',','"',';',':','?','/','\'');
                    for(var i=0;i<x.length;i++){
                        for(var j=0;j<=invalid_chars.length;j++){
                            if(x.charAt(i) == invalid_chars[j]){
                                Ext.MessageBox.alert(_("错误"),_("密码不能包含下列特殊字符.<br>")+
                                "space,comma,single quote,double quotes,'!','@','#',<br>'$','%','^','&','(',')','|','?','>','<','[',']','{','}','*',';',':','?','/'");
                                return;
                            }
                        }
                    }
                var url="/model/change_user_password?userid="+username+"&newpasswd="+password+"&oldpasswd="+old_passwd.getValue();
                var ajaxReq=ajaxRequest(url,0,"POST",true);

                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            closeWindow();
                            Ext.MessageBox.alert(_("成功"),_("密码已经成功修改."));
                        }else{
                            Ext.MessageBox.alert(_("Failure"),response.msg);
                        }
                    },
                    failure: function(xhr){
                        Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                    }
                });
            }
        },
        {
            text: '取消',
            icon:'icons/cancel.png',
            cls:'x-btn-text-icon',
            handler:function()
            {
                closeWindow();
            }

        }]
    });

    var change_passwrd=new Ext.Panel({
        width:390,
        height:170,
        layout: 'fit',
        items:[changePasswd]

    });
    return change_passwrd
}

