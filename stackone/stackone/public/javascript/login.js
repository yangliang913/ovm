var login;
//test
function loginconfig(){
    Ext.QuickTips.init();
    
    login = new Ext.FormPanel({
        url:'user_login',
        cls: 'whitebackground',
        labelAlign:'right',
        modal: true,
        monitorValid:true,
        border: false,
        items:[
	{  html:'<h1>登录Stackone-Virtualization-3.0</h1>'
	},
        {
            html:'<div class="pd" id="username">用户</div>'
        },
        {
            hideLabel:true,
            align:'center',
            name:'login',
            xtype:'textfield',
            id:'login',
            allowBlank:false,
            listeners:{
                specialkey : function(btn,e){
                    if(e.getKey()==13){
                        submitLoginForm(login);
                    }
                }
            }
        },
        {
            html:'<div class="pd" id="password-label">密码</div>'
        },
        {
            hideLabel:true,
            name:'password',
            align:'center',
            xtype:'textfield',
            id:'password',
            inputType:'password',
            allowBlank:false,
            listeners:{
                specialkey : function(btn,e){
                    if(e.getKey()==13){
                        submitLoginForm(login);
                    }
                }
            }
        },
        {
            html:'<div class="pd" id="hello-checkbox">LDAP用户: <input type="checkbox" id="checkbox-ldap-user" name="ldap_user"/><input type="button" id="btn-submit" value="确定" onclick="submitLogin();"/></div>'
        }
        ]
        /*
        buttons:[
        {
            text:_('登录'),
            formBind: true,
            handler:function(){
                submitLoginForm(login);
            }
        }]
        */


    });

    var win = new Ext.Window({
        layout:'fit',
        width:400,
        height:300,
        closable: false,
        resizable: false,
        plain: true,
	applyTo:'content',
        border: false,
        items: [login]
        ,defaultButton :"login"
    });
    win.show();
    var clf = document.createElement('div');
    clf.setAttribute('class','clf');
    document.body.appendChild(clf);
}

function submitLogin() {
    submitLoginForm(login);
}

function submitLoginForm(login){

     var loading_label=new Ext.form.Label({
        tittle:'加载...',
        html:'<table><tr><td>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp\n\
               &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp\n\
               </td><td>加载中...<img src=/icons/loading.gif></td></tr></table>',
        xtype:'label'
    });

    if(!login.getForm().isValid()) {
        Ext.Msg.alert(_("失败"), _("请输入账号和密码。"));
        return;
    }

     login.getForm().submit({
        method:'POST',
        waitTitle:_('连接中'),
        waitMsg:_('正在发送数据...'),
        success:function(){
            login.add(loading_label);
            login.setDisabled(true);
            login.doLayout();
            var redirect = '/';
            window.location = redirect;
        },
        failure:function(form, action){
            var msg='';
            switch (action.failureType) {
                case Ext.form.Action.CLIENT_INVALID:
                    msg=_("请输入账号和密码。");
                    break;
                case Ext.form.Action.CONNECT_FAILURE:
                    msg=_("与服务器通讯失败。");
                    break;
                case Ext.form.Action.SERVER_INVALID:
                    //msg=action.result.msg;
                    msg=_("账号或者密码错误。");
                    break;
                default:
                    msg=_('账号或者密码错误。');
                    if(action.result.msg != null){
                        //msg=action.result.msg
                    }
                    break;
            }
            Ext.Msg.alert(_("失败"), msg,function(id){
                login.getForm().reset();
                login.getForm().findField('login').focus(true);
            });
        }
    });
}//test
