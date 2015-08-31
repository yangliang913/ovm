/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function userUI(type){
    var user_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">'+_("创建 /编辑用户")+_(" 分配用户到组")+'<br/></div>'
    });
   

    var user_new_button=new Ext.Button({
        id: 'user_new',
        text: _('新建'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var w=new Ext.Window({
                    title :'New User',
                    width :370,
                    height:440,
                    modal : true,
                    resizable : false
                });
                w.add(userDetailsPanel(user_grid,'NEW',null,w,type));
                w.show();
            }
        }
    });

    var user_remove_button=new Ext.Button({
        id: 'user_remove',
        text: _('移除'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(!user_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从用户列表选择一个记录"));
                    return false;
                }
                var edit_rec=user_grid.getSelectionModel().getSelected();
                var userid=edit_rec.get('userid');
                var username=edit_rec.get('username');
                var url='/model/delete_user?userid='+userid;//alert(url);
                Ext.MessageBox.confirm(_("确认"),_("确定要删除该用户")+username+"吗?", function (id){
                    if(id=='yes'){
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    user_grid.getStore().load({params:{type:type}});
                                }else{
                                    Ext.MessageBox.alert(_("Failure"),response.msg);
                                }
                            },
                            failure: function(xhr){
                                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                            }
                        });
                    }
                });
            }
        }
    });

    var user_edit_button= new Ext.Button({
        id: 'user_edit',
        text: _('编辑'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(!user_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从用户列表中选择一个记录"));
                    return false;
                }
                var edit_rec=user_grid.getSelectionModel().getSelected();
                var userid=edit_rec.get('userid');
                var url="/model/edit_user_det?userid="+userid;
                var ajaxReq=ajaxRequest(url,0,"POST",true);

                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            var users_det=response.edit_user_det[0];
                            var w=new Ext.Window({
                                title :_('编辑用户'),
                                width :370,
                                height:440,
                                modal : true,
                                resizable : false
                            });
                            w.add(userDetailsPanel(user_grid,'EDIT',users_det,w,type));
                            w.show();
                        }else{
                            Ext.MessageBox.alert(_("Failure"),response.msg);
                        }
                    },
                    failure: function(xhr){
                        Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                    }
                });

            }
        }
    });

    var user_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var user_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("用户编号"),
        width: 0,
        dataIndex: 'userid',
        menuDisabled: false,
        hidden:true
    },
    {
        header: _("用户名"),
        width: 150,
        dataIndex: 'username',
        sortable:true
    },
    {
        header: _("名称"),
        width: 180,
        sortable: true,
        dataIndex: 'name'
    },
    {
        header: _("分组"),
        width: 165,
        sortable: false,
        dataIndex: 'group',
        wordwrap:true
    }]);

    var user_store =new Ext.data.JsonStore({
        url: "/model/get_users",
        root: 'rows',
        fields: ['userid','username', 'name', 'group'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){               
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    user_store.load({
        params:{
            type:type
        }
    });

    var user_grid=new Ext.grid.GridPanel({
        store: user_store,
        stripeRows: true,
        colModel:user_columnModel,
        frame:false,
        selModel:user_selmodel,
        height:355,
        //width:515,
        width: '100%',
        enableHdMenu:false,
        loadMask:true,
        id:'user_grid',
        layout:'fit',
        tbar:[
            _('搜索(按名称): '),new Ext.form.TextField({
            fieldLabel: _('搜索'),
            name: 'search',
            id: 'search',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    user_grid.getStore().filter('username', field.getValue(), false, false);
                }
            }
        }),{ 
            xtype: 'tbfill'
        },user_new_button,user_edit_button,user_remove_button],
        listeners:{
            rowdblclick:function(grid, rowIndex, e){
                user_edit_button.fireEvent('click',user_edit_button);
            }
        }
    });
    var userpanel=new Ext.Panel({
        id:"userpanel",
        title:((type==stackone.constants.StackOne)?_(''):_('云'))+_('用户'),
        layout:"form",
        width:535,
        height:450,
        cls: 'whitebackground',
        frame:false,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:5px 5px 5px 5px',
        items: [user_label,user_grid]
    });

    return userpanel;
}

function userDetailsPanel(grid,mode,user,w,type){
//    var user_label2=new Ext.form.Label({
//        html:'<div style="" class="backgroundcolor" align="center" width="250">'+_("Group Select")+'<br/></div><br>'
//    });

    var user_id=new Ext.form.TextField({
        fieldLabel: _('用户编号'),
        name: 'userid',
        width: 150,
        id: 'userid',
        allowBlank:false,
        disabled: true
    });
    var user_name=new Ext.form.TextField({
        fieldLabel: _('用户名称'),
        name: 'username',
        width: 150,
        id: 'username',
        allowBlank:false
    });
    var user_fname=new Ext.form.TextField({
        fieldLabel: _('姓'),
        name: 'fname',
        width: 150,
        id: 'fname',
        allowBlank:false
    });
    var user_lname=new Ext.form.TextField({
        fieldLabel: _('名'),
        name: 'lname',
        width: 150,
        id: 'lname',
        allowBlank:false
    });
    var display_name=new Ext.form.TextField({
        fieldLabel: _('昵称'),
        name: 'dispname',
        width: 150,
        id: 'dispname',
        allowBlank:false
    });
    var user_password=new Ext.form.TextField({
        fieldLabel: _('密码'),
        name: 'password',
        width: 150,
        id: 'pass',
        inputType:'password',
        allowBlank:false
    });
    var user_repass=new Ext.form.TextField({
        fieldLabel: _('确认密码'),
        name: 'repass',
        width: 150,
        id: 'repass',
        inputType:'password',
        initialPassField: 'pass',
        allowBlank:false
    });
    var user_email=new Ext.form.TextField({
        fieldLabel: _('电子邮件'),
        name: 'email',
        width: 165,
        id: 'email',
        allowBlank:false
    });
    var user_phone=new Ext.form.NumberField({
        fieldLabel: _('电话'),
        name: 'phone',
        width: 150,
        id: 'phone',
        allowBlank:true
    });
    var createdby=new Ext.form.TextField({
        fieldLabel: _('创建者'),
        name: 'createdby',
        width: 150,
        id: 'createdby',
        allowBlank:false,
        disabled:true

    });
    var createddate=new Ext.form.TextField({
        fieldLabel: _('创建日期'),
        name: 'createddate',
        width: 150,
        id: 'createddate',
        allowBlank:false,
        disabled:true

    });
    var modifiedby=new Ext.form.TextField({
        fieldLabel: _('修改者'),
        name: 'modifiedby',
        width: 150,
        id: 'modifiedby',
        allowBlank:false,
        disabled:true

    });
    var modifieddate=new Ext.form.TextField({
        fieldLabel: _('修改日期'),
        name: 'modifieddate',
        width: 150,
        id: 'modifieddate',
        allowBlank:false,
        disabled:true

    });
   
    var newpasswrd=new Ext.form.TextField({
        fieldLabel: _('新密码'),
        name: 'newpass',
        width: 150,
        id: 'newpass',
        inputType:'password'
    });

    var confpasswrd=new Ext.form.TextField({
        fieldLabel: _('确认密码'),
        name: 'confpass',
        width: 150,
        id: 'confpass',
        inputType:'password'
    });


    var user_status_store = new Ext.data.JsonStore({
        url: '/model/get_user_status_map',
        root: 'user_status',
        fields: ['id','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    user_status_store.load();
    var user_status=new Ext.form.ComboBox({
        width:80,
        minListWidth: 90,
        fieldLabel:_("状态"),
        allowBlank:false,
        triggerAction:'all',
        store:user_status_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'user_status'
    });

    var url="";
    if(mode=='NEW'){
        url="/model/get_groups_map";
    }
    else if(mode=='EDIT'){
        url="/model/get_groups_map?userid="+user.userid;
    }
//    var groups_fromstore = new Ext.data.JsonStore({
//        url: url,
//        root: 'group_det',
//        fields: ['groupid','groupname'],
//        successProperty:'success',
//        //        remoteSort :true,
//        sortInfo: {
//            field: 'groupname',
//            direction: 'ASC' // or 'DESC' (case sensitive for local sorting)
//        },
//        listeners:{
//            loadexception:function(obj,opts,res,e){
//                var store_response=Ext.util.JSON.decode(res.responseText);
//                Ext.MessageBox.alert(_("Error"),store_response.msg);
//            },
//            load:function(store,recs,opts){
//
//            }
//        }
//    });

    //groups_fromstore.load();
//    var groups_tostore = new Ext.data.JsonStore({
//        url: '/model/get_togroups_map',
//        root: 'togroup_det',
//        fields: ['groupid','groupname'],
//        successProperty:'success',
//        sortInfo: {
//            field: 'groupname',
//            direction: 'ASC' // or 'DESC' (case sensitive for local sorting)
//        },
//        listeners:{
//            loadexception:function(obj,opts,res,e){
//                var store_response=Ext.util.JSON.decode(res.responseText);
//                Ext.MessageBox.alert(_("Error"),store_response.msg);
//            }
//        }
//    });

    var user_cancel_button= new Ext.Button({
        id: 'cancel',
        text: _('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                w.close();
            }
        }
    });
    
    var user_save_button=new Ext.Button({
        id: 'save',
        text: _('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {                
                if(user_rightpanel.getForm().isValid()) {
                    var url="",flag=false,errmsg="";
                    var uid="";
                    
                    
                    var repass= user_repass.getValue();
                    if(mode=="NEW" && user_password.getValue()!=repass){
                        errmsg+="<br>"+_("密码信息不匹配");
                        flag=true;
                    }
                    

                    var email=user_email.getValue();
                    if(!EmailCheck(email)){
                        errmsg+="<br>"+_("请输入有效的电子邮件标识");
                        flag=true;
                    }
//                    if(groupitemselector.toStore.getCount()==0){
//                        errmsg+="<br>"+_("Please select at least one Group");
//                        flag=true;
//                    }

                    if(flag){
                        Ext.MessageBox.alert(_("警告"),errmsg);
                        return ;
                    }
                    uid=user_name.getValue()
                    if(mode=='NEW'){

                        url="/model/save_user_det?userid="+user_id.getValue()+
                            "&username="+user_name.getValue()+"&fname="+user_fname.getValue()+
                            "&lname="+user_lname.getValue()+"&displayname="+display_name.getValue()+
                            "&password="+user_password.getValue()+"&email="+user_email.getValue()+
                            "&phone="+user_phone.getValue()+"&status="+user_status.getValue()+"&type="+type;
                    }else if(mode=='EDIT'){                        
                        
                        var flag=false,errmsg="";
                        //var rec_count=groupitemselector.toStore.getCount();
                        var change_passwd=passwrd_fldset.getEl().child('legend').child('input').dom.checked;
                        if(change_passwd == true)
                        {
                            if(newpasswrd.getValue() == "")
                            {
                                errmsg+="<br>"+_("请输入新密码");
                                flag=true;
                            }
                            if(newpasswrd.getValue() != "")
                            {
                                if(newpasswrd.getValue() != confpasswrd.getValue())
                                {
                                    errmsg+="<br>"+_("密码信息不匹配");
                                    flag=true;
                                }
                            }
                        }
                        if(flag){
                            Ext.MessageBox.alert(_("警告"),errmsg);
                            return ;
                        }
                    
                        url="/model/updatesave_user_det?userid="+user_id.getValue()+
                            "&username="+user_name.getValue()+"&fname="+user_fname.getValue()+
                            "&lname="+user_lname.getValue()+"&displayname="+display_name.getValue()+
                            "&email="+user_email.getValue()+"&phone="+user_phone.getValue()+
                            "&status="+user_status.getValue()+"&changepass="+change_passwd+
                            "&newpasswd="+newpasswrd.getValue();
                
                    }

                    var ajaxReq=ajaxRequest(url,0,"POST",true);
                    ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                var users_det=response.user_det[0];
                                if('F'==users_det){
                                    Ext.MessageBox.alert(_("失败"),format(_("用户{0}已经存在"),uid));
                                    return false;
                                }
                                else if('E' == users_det){
                                    Ext.MessageBox.alert(_("失败"),_("该电子邮件已经存在!"));
                                    return false;
                                }
                                Ext.MessageBox.alert(_("成功"),_("已经成功保存"));
                                w.close();
                                grid.getStore().load({params:{type:type}});
                            }else{
                                Ext.MessageBox.alert(_("Failure"),response.msg);
                            }
                        },
                        failure: function(xhr){
                            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                        }
                    });
                }
                else{
                    Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
                }
            }
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
        cls: 'whitebackground',
        border:false,
        id:'tabpanel',
        bbar:[{
            xtype: 'tbfill'
        },user_save_button,user_cancel_button]
    });

    var user_rightpanel=new Ext.FormPanel({
        id:"rightpanel",
        title:_('用户'),
        layout:"form",
        width:300,
        height:345,
        //frame:true,
        labelWidth:100,
        border:0,
        bodyStyle:'padding:10px 10px 10px 10px'
    //items:[user_name,user_fname,user_lname,user_password,user_repass,user_email,user_phone,user_status]
    });

    var passwrd_fldset=new Ext.form.FieldSet({
        checkboxToggle:true,
        collapsed: true,
        title: _('修改密码'),
        id: 'change_passwd',
        autoHeight:true,
        width:280,
        labelWidth:90,
        layout:'column',
        items: [{
            width: 300,
            layout:'form',
            items:[newpasswrd,confpasswrd]
        }]
    });

    user_rightpanel.add(user_name);
    user_rightpanel.add(user_fname);
    user_rightpanel.add(user_lname);
    user_rightpanel.add(display_name);
    
    if(mode=="NEW"){
        user_rightpanel.add(user_password);
        user_rightpanel.add(user_repass);
    }
    user_rightpanel.add(user_email);
    user_rightpanel.add(user_phone);
    user_rightpanel.add(user_status);    

    var user_auditpanel=new Ext.Panel({
        id:"auditpanel",
        title:_('审计'),
        width:300,
        height:345,
        layout:"form",
        frame:true,
        labelWidth:100,
        border:false,
        bodyBorder:false,
        items:[createdby,createddate,modifiedby,modifieddate ]
    });

//    var groupitemselector=new Ext.ux.ItemSelector({
//        name:"itemselector",
//        dataFields:["groupid","groupname"],
//        toStore:groups_tostore,
//        msWidth:148,
//        msHeight:250,
//        allowBlank:false,
//        valueField:"groupid",
//        displayField:"groupname",
//        imagePath:"icons/",
//        drawUpIcon:false,
//        drawDownIcon:false,
//        drawLeftIcon:true,
//        drawRightIcon:true,
//        drawTopIcon:false,
//        drawBotIcon:false,
//        toLegend:_("Selected"),
//        fromLegend:_("Available"),
//        fromStore:groups_fromstore,
//        toTBar:[{
//            text:_("Clear"),
//            handler:function(){
//                groupitemselector.reset();
//            }
//        }]
//    });
//    var groupassign_details_panel=new Ext.FormPanel({
//        id:"groupassignpanel",
//        title:_('Group'),
//        width:300,
//        height:300,
//        layout:"form",
//        frame:true,
//        labelWidth:5,
//        border:false,
//        bodyBorder:false,
//        items: [user_label2, groupitemselector]
//    });
    
    var user_group=new Ext.form.TextField({
        fieldLabel: _('分组'),
        name: 'groups',         
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'user_group'
    });
    
    if(mode=="EDIT"){

        var userid=user.userid;
        user_id.setValue(user.userid);
        user_name.setValue(user.username);
        user_name.disabled=true;
        user_fname.setValue(user.fname);
        user_lname.setValue(user.lname);
        display_name.setValue(user.displayname);
        user_email.setValue(user.email);
        user_phone.setValue(user.phone);
        user_status.setValue(user.status);
        user_group.setValue(user.groupname);
        user_rightpanel.add(user_group);
        user_rightpanel.add(passwrd_fldset);

//        groups_fromstore.load();
//        groups_tostore.load({
//            params:{
//                userid:userid
//            }
//        });

        tabPanel.add(user_rightpanel);
//        tabPanel.add(groupassign_details_panel);
        tabPanel.add(user_auditpanel);
        tabPanel.setActiveTab(user_auditpanel);
//        tabPanel.setActiveTab(groupassign_details_panel);
        tabPanel.setActiveTab(user_rightpanel);
        createdby.setValue(user.createdby);
        modifiedby.setValue(user.modifiedby)
        createddate.setValue(user.createddate)
        modifieddate.setValue(user.modifieddate)

    }else if(mode=="NEW"){
        user_status.setValue("Active");
    }

        tabPanel.add(user_rightpanel);
//        tabPanel.add(groupassign_details_panel);
//        tabPanel.setActiveTab(groupassign_details_panel);
        tabPanel.setActiveTab(user_rightpanel);
    
    var new_users_panel=new Ext.Panel({
        id:"new_user_panel",
        layout:"form",
        width:350,
        height:450,
        cls: 'whitebackground',
        frame:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[tabPanel]
    });

    return new_users_panel;

}

function ckNumber(value) {
    var validate=false;
    var  x = value;
    var nos=new Array('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E',
        'F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','!','@','#','$','%','^','&','(',')','|','?','>','<','[',']','{','}','*','"',',','.','"',';',':','?','/','\'');
    for(var i=0;i<value.length;i++){
        for(var j=0;j<=nos.length;j++){
            if(x.charAt(i) == nos[j]){
                //alert("Only Numbers Are Allowed")
                value="";
                focus();
                return validate;
            }
        }
    }
    validate=true;
    return validate;
}

function EmailCheck(email){
    email = email;
    var validate=false;
    var pattern=/^([a-zA-Z0-9_.-])+@([a-zA-Z0-9_.-])+\.([a-zA-Z])+([a-zA-Z])+/;
    if(! pattern.test(email)){
        //alert("Properly , give the Email Address (__ @__ .__)");
        return validate;
    }
    else{
        validate=true;
        return validate;
    }

}
