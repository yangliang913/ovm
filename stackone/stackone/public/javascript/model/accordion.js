

var accordioncenter;

//Validator to receive only numerical inputs
Ext.form.VTypes.portnumVal  = /^[0-9\-]/;
Ext.form.VTypes.portnumMask = /[\d]/;
Ext.form.VTypes.portnumText = 'In-valid Port Number.';
Ext.form.VTypes.portnum 	= function(v){
	return Ext.form.VTypes.portnumVal.test(v);
};

function Test(){
             Ext.MessageBox.alert("错误","请从用户列表中选择一个记录");
}

function select_ui_type(is_cloud_admin){
    if(has_cloud=='False'){
        var id = Ext.id();
        showWindow('用户',705,470,adminconfig(stackone.constants.StackOne,id),id);
        return null;
    }
    if(is_cloud_admin=='True'){
        var id = Ext.id();
        showWindow('用户',705,470,adminconfig(stackone.constants.CLOUD,id),id);
        return null;
    }

    var userselect_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="120"><b>选择用户类型用于管理.</b></div>&nbsp'
    });
// style="vertical-align: middle"
    var type = new Ext.form.ComboBox({
        fieldLabel: _('选择类型'),
        allowBlank:false,
        store: [[stackone.constants.StackOne,_('管理帐号')]],
        emptyText :"选择类型",
        mode: 'local',
        displayField:'name',
        valueField:'value',
    width: 140,
        triggerAction :'all',
        forceSelection: true,
        name:'plat_form'
    });

    var simple = new Ext.FormPanel({
        labelWidth:120,
        frame:true,
        border:0,
        labelAlign:"right" ,
        width:300,
        height:110,
        labelSeparator: ' ',
        items:[userselect_label,type]
    });

    simple.addButton(_("确定"),function(){
        if (simple.getForm().isValid()) {
            closeWindow();
            showWindow('用户',705,470,adminconfig(type.getValue()));

        }else{
            Ext.MessageBox.alert(_('错误'), _('请选择一个平台.'));
        }
    });
    simple.addButton(_("取消"),function(){
        closeWindow();
    });

    return simple;


}

function adminconfig(type,id) {

    //var users,groups,roles,privlige,opsgroup;
    accordioncenter = new Ext.Panel({
        region:'center',
        width:540,
        height:440,
        id:'accordioncenter',
        items:[userUI(type)]
    });

    var html='<a href="#" onclick="javascript: showNewUI(userUI(&quot;'+type+'&quot;));"><font size="2" face="Helvetica" color="black">'+_('用户')+'</font></a><br>'+
            '<a href="#" onclick="javascript: showNewUI(groupUI(&quot;'+type+'&quot;));"><font size="2" face="Helvetica" color="black">'+_('分组')+'</font></a><br>'+
            '<a href="#" onclick="javascript: showNewUI(roleUI(&quot;'+type+'&quot;));"><font size="2" face="Helvetica" color="black">'+_('角色')+'</font></a><br>';

    if(has_adv_priv=='True'){
        html+='<a href="#" onclick="javascript: showNewUI(privilegeUI(&quot;'+type+'&quot;));"><font size="2" face="Helvetica" color="black">'+_('权限')+'</font></a><br>'+
            '<a href="#" onclick="javascript: showNewUI(operationsUI(&quot;'+type+'&quot;));"><font size="2" face="Helvetica" color="black">'+_('操作')+'</font></a><br>'+
            '<a href="#" onclick="javascript: showNewUI(opsgroupUI(&quot;'+type+'&quot;));"><font size="2" face="Helvetica" color="black">'+_('操作组')+'</font></a><br>'+
            '<a href="#" onclick="javascript: showNewUI(entitytypeUI(&quot;'+type+'&quot;));"><font size="2" face="Helvetica" color="black">'+_('实例类型')+'</font></a>';
    }
    var item1 = new Ext.Panel({
        title: _('用户管理'),
        html: html,
        cls:'empty'

    });

    var item2 = new Ext.Panel({
        title: 'SMTP设置',
        html: '&nbsp&nbsp<a href="#" onclick="javascript:showNewUI(emailSetupUI());"><font size="2" face="Helvetica"color="black">电子邮件设置</font></a>',
        cls:'empty'

    });

    var accordionwest = new Ext.Panel({
        region:'west',
        width:155,
        height:500,
        margins:'0 0 0 0',
        layout:'accordion',
        border:false,
        id:'accordionwest',
        items: [item1,item2]
    });

    var close_button= new Ext.Button({
        id: 'close',
        text: '关闭',
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow(id);
            }
        }
    });

    var outerpanel=new Ext.Panel({
        id:"outerpanel",
        layout:'border',
        width:695,
        height:440,
        cls: 'whitebackground',
        items:[accordionwest,accordioncenter],
        bbar:[{
            xtype: 'tbfill'
        },close_button]
    });

    return outerpanel;

}

function showNewUI(inplink) {
    accordioncenter.removeAll();
    accordioncenter.add(inplink);
    accordioncenter.doLayout();
}


//############################################################################################
//$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
function emailSetupUI(){
    var email_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">配置/编辑邮件设置<br/></div>'
    });


var email_new_button=new Ext.Button({
        id: 'emailsetup_new',
        text: '新建',
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var w=new Ext.Window({
                    title :'新建电子邮件设置',
                    width :370,
                    height:400,
                    modal : true,
                    resizable : false
                });
                w.add(EmailDetailsPanel(email_grid,'NEW',null,w));
                w.show();

            }
        }
    });

    var email_remove_button=new Ext.Button({
        id: 'email_remove',
        text: '移除',
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(!email_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert("错误","请从列表中选择一个记录");
                    return false;
                }
                var edit_rec=email_grid.getSelectionModel().getSelected();

                var emailsetup_id= edit_rec.get('emailsetup_id');
                var servername=edit_rec.get('servername');
                var url='delete_emailrecord?emailsetup_id='+emailsetup_id;//alert(url);
                Ext.MessageBox.confirm("Confirm","About to delete email record:"+servername+"?", function (id){
                    if(id=='yes'){
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    email_grid.getStore().load();
                                }else{
                                    Ext.MessageBox.alert("Failure",response.msg);
                                }
                            },
                            failure: function(xhr){
                                Ext.MessageBox.alert( "Failure " , xhr.statusText);
                            }
                        });
                    }
                });
            }
        }
    });

    var email_edit_button= new Ext.Button({
        id: 'email_edit',
        text: '编辑',
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(!email_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert("错误","请从列表中选择一个记录");
                    return false;
                }
                var edit_rec=email_grid.getSelectionModel().getSelected();
                var emailsetup_id=edit_rec.get('emailsetup_id');
                var url="/get_emailsetup_details?emailsetup_id="+emailsetup_id;
                var ajaxReq=ajaxRequest(url,0,"POST",true);


                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);

                        if(response.success){
                            var email_details = response.emailsetup_details[0]
                            //popup the Edit window
                            var w=new Ext.Window({
                                title :'编辑邮件设置',
                                width :370,
                                height:400,
                                modal : true,
                                resizable : false
                            });
                            w.add(EmailDetailsPanel(email_grid,'EDIT',email_details,w));
                            w.show();

                        }else{
                            Ext.MessageBox.alert("Failure",response.msg);
                        }
                    },
                    failure: function(xhr){
                        Ext.MessageBox.alert( "Failure " , xhr.statusText);
                    }
                });

               }
        }
    });

     var email_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var title_edit = new Ext.form.TextField();
    var email_columnModel = new Ext.grid.ColumnModel([
    {
        header: "Site ID",
        width: 50,
        dataIndex: 'emailsetup_id',
        menuDisabled: false,
        hidden:true,
        editor: title_edit
    },
    {
        header: "服务器名称",
        width: 150,
        dataIndex: 'servername',
        sortable:true,
        editor: title_edit,
        id:'headerfont'

    },
    {
        header: "说明",
        width: 150,
        dataIndex: 'desc',
        sortable:true,
        editor: title_edit,
        id:'headerfont'

    },
    {
        header: "用户名称",
        width: 150,
        sortable: false,
        dataIndex: 'username',
        editor: title_edit,
        id:'headerfont'

    },
    {
        header: "端口",
        width: 210,
        sortable: false,
        dataIndex: 'port',
        editor: title_edit,
        wordwrap:true,
        id:'headerfont'
    }]);

     var email_store =new Ext.data.JsonStore({
            url: "get_emailsetupinfo",
            root: 'rows',
            fields: [ 'emailsetup_id','servername', 'desc', 'username', 'port' ],
            successProperty:'success',
            listeners:{
                loadexception:function(obj,opts,res,e){
                    var store_response=Ext.util.JSON.decode(res.responseText);
                    Ext.MessageBox.alert("Error2",store_response.msg);
                }

            }
        });

    email_store.load();


    var email_grid=new Ext.grid.GridPanel({
        store: email_store,
        stripeRows: true,
        colModel:email_columnModel,
        frame:false,
        selModel:email_selmodel,
        height:355,
        width:'100%',
        enableHdMenu:false,
        loadMask:true,
        id:'email_grid',
        layout:'fit',
       tbar:[
            '搜索 (按服务器名称): ',new Ext.form.TextField({
            fieldLabel: 'Search',
            name: 'search',
            id: 'search',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    email_grid.getStore().filter('servername', field.getValue(), false, false);
                }
            }

        }),{ xtype: 'tbfill'},email_new_button,'-',email_edit_button,'-',email_remove_button],
        listeners:{
             rowdblclick:function(grid, rowIndex, e){
                email_edit_button.fireEvent('click',email_edit_button);
            }
        }
    });
     var emailpanel=new Ext.Panel({
        id:"emailpanel",
        title:'电子邮件设置',
        layout:"form",
        width:535,
        height:435,
        frame:false,
        labelWidth:130,
        border:0,
        cls: 'whitebackground',
        bodyStyle:'padding:5px 5px 5px 5px',
        items: [email_label,email_grid]
    });

    return emailpanel;
}

function EmailDetailsPanel(grid,mode,emaildetails,w){

    var email_cancel_button= new Ext.Button({
        id: 'cancel',
        text: '取消',
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
               w.close();

            }
        }
    });

    var email_test_button= new Ext.Button({
        id: 'test',
        text: '测试',
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                    var vsecure;
                    if ( radio_no_var.checked == true ) {
                            vsecure = 1;
                    }
                    else if ( radio_tls_var.checked == true ) {
                            vsecure = 2;
                    }
                    else if ( radio_ssl_var.checked == true ) {
                            vsecure = 3;
                    }


                    url="/send_test_email?desc="+desc_var.getValue()+"&servername="+servername_var.getValue()+"&port="+port_var.getValue()+"&useremail="+useremail_var.getValue()+"&password="+password_var.getValue()+"&secure="+vsecure;


                    var ajaxReq=ajaxRequest(url,0,"GET",true);
                    ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                Ext.MessageBox.alert("Sucess",response.msg);
                            }else{
                                Ext.MessageBox.alert("Failure",response.msg);
                            }
                        },
                        failure: function(xhr){
                            Ext.MessageBox.alert( "Failure " , xhr.statusText);
                        }
                    });

            }
        }
    });

    var email_save_button=new Ext.Button({
        id: 'save',
        text: '保存',
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                //setup_form = simple.getForm()
                var url="",flag=false,errmsg="";

                var vsecure;
                if ( radio_no_var.checked == true ) {
                        vsecure = 1;
                }
                else if ( radio_tls_var.checked == true ) {
                        vsecure = 2;
                }
                else if ( radio_ssl_var.checked == true ) {
                        vsecure = 3;
                }

                if(simple.getForm().isValid())
                {

                    if(mode=='NEW'){
                        url="/save_email_setup_details?desc="+desc_var.getValue()+"&servername="+servername_var.getValue()+"&port="+port_var.getValue()+"&useremail="+useremail_var.getValue()+"&password="+password_var.getValue()+"&secure="+vsecure;

                    }else if(mode=='EDIT'){
                        url="/update_email_setup_details?desc="+desc_var.getValue()+"&servername="+servername_var.getValue()+"&port="+port_var.getValue()+"&useremail="+useremail_var.getValue()+"&password="+password_var.getValue()+"&secure="+vsecure;

                }
                    // add ajax request call here
                    var ajaxReq=ajaxRequest(url,0,"GET",true);
                    ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                Ext.MessageBox.alert("Success",response.msg);
                                    w.close();
                                    grid.getStore().load();
                            }else{
                                Ext.MessageBox.alert("Failure",response.msg);
                            }

                        },
                        failure: function(xhr){
                            Ext.MessageBox.alert( "Failure " , xhr.statusText);
                        }
                    });

                }
                else
                {
                    Ext.MessageBox.alert( "Failure " , 'Invalid enteries');
                }
            }
//

        }
    });


    var tabPanel=new Ext.TabPanel({
        defaults: {
            autoScroll:true
        },
        margins: '2 2 2 0',
        minTabWidth: 115,
        tabWidth:135,
        activeTab:0,
        border:false,
        id:'tabpanel',
        bbar:[{
            xtype: 'tbfill'
        },email_test_button,'-',email_save_button,'-',email_cancel_button]
    });


     var desc_var=new Ext.form.TextField({
        fieldLabel: '说明',
        name: 'desc',
        width: 150,
        id: 'desc'
    });

    var servername_var=new Ext.form.TextField({
        fieldLabel: '服务器名称',
        name: 'servername',
        id: 'servername',
        width: 150,
        allowBlank:false
    });

    var port_var = new Ext.form.TextField({
        fieldLabel: '端口',
        name: 'port',
        id: 'port',
        width: 50,
        value: '25',
        vtype: 'portnum'
    });

    var settingGroup = {
        xtype: 'fieldset',
        title: '安全和认证',
        autoHeight: true,
        bodyStyle:'padding:5px 5px 0',
        items: [desc_var,
                servername_var,
                port_var]

    }

     var useremail_var = new Ext.form.TextField({
        fieldLabel: '用户名',
        width: 150,
        name: 'useremail',
        id: 'useremail',
	    vtype: 'email',
        allowBlank:false

     });

    var password_var = new Ext.form.TextField({
        fieldLabel: '密码',
        width: 150,
        name: 'password',
        id: 'password',
	   inputType:'password'
    });

    var radio_no_var=  new Ext.form.Radio({
        boxLabel: 'No', name: 'rgcol', inputValue: 1, id: 'no',checked: true});

    var radio_tls_var=  new Ext.form.Radio({
        boxLabel: 'TLS', name: 'rgcol', inputValue: 2, id: 'tls'});

    var radio_ssl_var=  new Ext.form.Radio({
        boxLabel: 'SSL', name: 'rgcol', inputValue: 3, id:'ssl'});

    var checkbox_var=  new Ext.form.Checkbox({
        name: 'use_name_password',
        checked: true,
        boxLabel: '用户名和密码',
        listeners: {
            check: function(this_checkbox, checked) {
                if(checked)
                {
                    useremail_var.enable();
                    password_var.enable();
                }
                else
                {
                    useremail_var.disable();
                    useremail_var.setValue('');
                    password_var.disable();
                    password_var.setValue('');
                }
            }

        }
    });

     var authenticationGroup = {
        xtype: 'fieldset',
        title: '设置',
        autoHeight: true,
        items: [
            checkbox_var,
            useremail_var,
            password_var,
            {
                xtype: 'radiogroup',
                fieldLabel: '用户安全连接',
                itemCls: 'x-check-group-alt',
                columns: 3,
                width: 150,
                labelAlign: 'top',
                items: [
                    radio_no_var,
                    radio_tls_var,
                    radio_ssl_var
                ]
            }

        ]
        }



   simple = new Ext.FormPanel({
        labelWidth: 80, // label settings here cascade unless overridden
        frame:true,
        title: '邮件服务器',
        bodyStyle:'padding:5px 5px 0',
        width: 300,
        height:300,
        defaults: {width: 300},
        defaultType: 'textfield',
        items: [
        settingGroup,
        authenticationGroup
        ]
   });

    if(mode=="EDIT"){
        desc_var.setValue( emaildetails.desc);
        servername_var.setValue(emaildetails.servername);
        servername_var.disabled=true;
        port_var.setValue(emaildetails.port);
        useremail_var.setValue(emaildetails.username);
        password_var.setValue(emaildetails.password);

        if(emaildetails.username == '')
        {
            useremail_var.disable();
            password_var.disable();
            checkbox_var.checked = false
        }

        vsecure = emaildetails.use_secure;
        if( vsecure == 1)
        {
            radio_no_var.setValue(true);
            radio_tls_var.setValue(false);
            radio_ssl_var.setValue(false);
        }
        else if (vsecure == 2)
        {
            radio_no_var.setValue(false);
            radio_tls_var.setValue(true);
            radio_ssl_var.setValue(false);
        }
        else if (vsecure == 3)
        {
            radio_no_var.setValue(false);
            radio_tls_var.setValue(false);
            radio_ssl_var.setValue(true);
        }

    }

    tabPanel.add(simple);
    tabPanel.setActiveTab(simple);

    var new_email_panel=new Ext.Panel({
        id:"new_email_panel",
        layout:"form",
        width:350,
        height:400,
        frame:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[tabPanel]
    });

    return new_email_panel;

}
