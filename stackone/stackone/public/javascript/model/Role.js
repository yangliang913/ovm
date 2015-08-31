/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* author : Benf<yangbf@stackone.com.cn>
*/

function roleUI(type){

    var top_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">'+_("允许创建/编辑角色. ")+_("以通过群组角色，分配适当权限使您轻松管理各计算资源单位")+'<br/></div>'
    });

    var new_button=new Ext.Button({
        id: 'new_role',
        text: _('新建'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var w=new Ext.Window({
                    title :_('新建角色'),
                    width :500,
                    height:520,
                    modal : true,
                    resizable : false
                });
                w.add(NewRoleDetailsPanel(role_grid,'NEW',null,w,type));
                w.show();
            }
        }
    }) ;

    var remove_button=new Ext.Button({
        id: 'remove_role',
        text: _('移除'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(!role_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从列表中选择一个角色."));
                    return;
                }
                var edit_rec=role_grid.getSelectionModel().getSelected();
                var roleid=edit_rec.get('roleid');
                var rolename=edit_rec.get('rolename');
                var url='/model/delete_role?roleid='+roleid;
                Ext.MessageBox.confirm(_("确认"),_("确定要删除该角色")+rolename+"吗?", function (id){
                    if(id=='yes'){
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    role_grid.getStore().load({params:{type:type}});
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
    var edit_button= new Ext.Button({
        id: 'user_edit',
        text: _('编辑'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(!role_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从列表中选择一个角色."));
                    return ;
                }
                var edit_rec=role_grid.getSelectionModel().getSelected();
                var roleid=edit_rec.get('roleid');
                var url="/model/get_role_details?roleid="+roleid;
                var ajaxReq=ajaxRequest(url,0,"POST",true);

                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            var role=response.role;
                            var w=new Ext.Window({
                                title :_('编辑角色'),
                                width :500,
                                height:520,
                                modal : true,
                                resizable : false
                            });
                            w.add(EditRoleDetailsPanel(role_grid,'EDIT',role,w,type));
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

    var selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var columnModel = new Ext.grid.ColumnModel([
    {
        header: _("编号"),
        width: 0,
        dataIndex: 'roleid',
        hidden:true
    },
    {
        header: _("名称"),
        width: 150,
         dataIndex: 'rolename',
        sortable:true
    },
     {
        header: _("说明"),
        width: 345,
        dataIndex: 'description',
        sortable:false
        }
    ]);

    var role_store =new Ext.data.JsonStore({
        url: "/model/get_roles",
        root: 'rows',
        fields: ['roleid','rolename','description'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){//alert(res.responseText);
               var store_response=Ext.util.JSON.decode(res.responseText);
               Ext.MessageBox.alert(_("Error"),store_response.msg);
           }
        }
    });
    role_store.load({
        params:{
            type:type
        }
    });

    var role_grid=new Ext.grid.EditorGridPanel({
        store: role_store,
        stripeRows: true,
        colModel:columnModel,
        frame:false,
        selModel:selmodel,
        height:360,
        width:515,
        clicksToEdit:1,
        enableHdMenu:false,
        id:'role_grid',
        loadMask:true,
        //        bbar: new Ext.PagingToolbar({
        //            store: role_store,
        //            displayInfo:true,
        //            displayMessage:"Displaying {0} - {1} of {2}"
        //        }),
        tbar:[
            '搜索 (按名称): ',new Ext.form.TextField({
            fieldLabel: _('搜索'),
            name: 'search',
            id: 'search',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    role_grid.getStore().filter('rolename', field.getValue(), false, false);
                }
            }

        }),{
            xtype: 'tbfill'
        },new_button,'-',edit_button,'-',remove_button],
        listeners:{
            rowdblclick:function(grid, rowIndex, e){
                edit_button.fireEvent('click',edit_button);
            }
        }
    });

    var rolepanel=new Ext.Panel({
        id:"rolepanel",
        title:((type==stackone.constants.StackOne)?_(''):_('云'))+_('角色'),
        layout:"form",
        width:535,
        height:450,
        frame:false,
        labelWidth:130,
        bodyBorder:false,
        cls: 'whitebackground',
        bodyStyle:'padding:5px 5px 5px 5px',
        items: [top_label,role_grid ]
    });

    return rolepanel;
}
  function propagate_checkbox(value,params,record){
    var id = Ext.id();
    var disabled = false;
    (function(){
        var cb = new Ext.form.Checkbox({
            renderTo: id,
            width:100,
            height:16,
            disabled:disabled,
            checked:value,

            value:false,
            listeners : {
                check:function(field,checked){
                     if(checked==true){
                            record.set('propagate',true);
                        }else{
                            record.set('propagate',false);
                        }
                }
            }
        });
    }).defer(5);
    return '<span id="' + id + '"></span>';
}

function EditRoleDetailsPanel(grid,mode,role,w,type){

    var role_name=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'rolename',
        width: 280,
        id: 'rolename',
        allowBlank:false
    });
    var role_desc=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'roledesc',
        width: 320,
        id: 'roledesc'
    });
//    var is_cloudadmin=new Ext.form.Checkbox({
//        fieldLabel: _('Is Cloud Admin'),
//        name: 'is_cloudadmin',
//        width: 320,
//        id: 'is_cloudadmin'
//    });

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

    var rec = Ext.data.Record.create([
    {
        name: 'privid',
        type: 'string'
    },
    {
        name: 'id',
        type: 'string'
    },
    {
        name: 'privname',
        type: 'string'
    }
    ]);
    var r=new rec({
        privid: 'None',
        id: '0',
        privname: _('None')
    });

    var priv_store = new Ext.data.JsonStore({
        url: '/model/get_privileges4opsg',
        root: 'rows',
        fields: ['privid', 'privname'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){//alert(res.responseText);
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
            ,
            load:function(store,recs,opts){
//                store.insert(0,[r])
            }
        }
    });
    priv_store.load({
        params:{
            type:type
        }
    });

 

    var columnModel = new Ext.grid.ColumnModel([
    {
        header: _("编号"),
        width: 0,
        sortable: false,
        dataIndex: 'entityid',
        hidden:true
    },
    {
        header: _("实体"),
        width: 110,
        sortable: true,
        dataIndex: 'entityname'
    },
    {
        header: _("实体类型"),
        width: 110,
        sortable: true,
        dataIndex: 'entitytype'
    },
    {
        header: _("权限"),
        width: 100,
        sortable: true,
        dataIndex: 'privilegename',
        editor: new Ext.form.ComboBox({
            typeAhead: true,
            store:priv_store,
            triggerAction: 'all'
            ,valueField:'privname'
            ,displayField:'privname'
            ,mode:'local'
     })},
  
    {
        header: _("Propagate"),
        width: 30,
        sortable: true,
        hidden:(granular_ui!="True"),
        dataIndex: 'propagate',
        renderer:propagate_checkbox
    }
    ]);
    

    var rep_store = new Ext.data.JsonStore({
        url: '/model/get_role_rep',
        root: 'rows',
        fields: ['entityid', 'entityname', 'entitytype','privilegename','propagate'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    rep_store.sort('entityname','ASC');

    var selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var add_button= new Ext.Button({
        id: 'new_entity',
        text: _('添加'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon'
        ,listeners: {
        click: function(btn) {
                var w=new Ext.Window({
                    title :_('实体'),
                    width :480,
                    height:550,
                    modal : true,
                    resizable : false
                });
                w.add(EntityDetailsPanel(rep_grid,'ADD_NEW',null,w,type));
                w.show();
            }
        }
    }) ;

    var delete_button= new Ext.Button({
        id: 'cancel',
        text: _('删除'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
        click:function(combo,record,index){
//            Ext.MessageBox.alert(_('Confirm'), _('Some of the Entities are selected.You are excluding the entities.'));
            var selections=rep_grid.getSelections();
            for (var i=0;i<selections.length;i++){
                var rec=selections[i];
                rep_grid.getStore().remove(rec);
             }
         }
        }
    });

    var rep_grid = new Ext.grid.EditorGridPanel({
        store: rep_store,
        colModel:columnModel,
        stripeRows: true,
        frame:true,
        selModel:selmodel,
        width:'100%',
        autoExpandColumn:2,
        height:380,
        clicksToEdit:1,
        enableHdMenu:false,
        tbar:[
            '搜索(按实体名称): ',new Ext.form.TextField({
            fieldLabel: _('搜索'),
            name: 'search',
            id: 'search',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    rep_grid.getStore().filter('entityname', field.getValue(), false, false);
                }
            }

        }),{
            xtype: 'tbfill'
        },add_button,delete_button]
    });

    var cancel_button= new Ext.Button({
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

    var save_button=new Ext.Button({
        id: 'save',
        text: _('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(rightpanel.getForm().isValid()) {
                    var url="";
                    if(mode=='EDIT'){
                        url='/model/update_role?roleid='+role.id+'&rolename='+role_name.getValue()+
                        '&roledesc='+role_desc.getValue();
                    }

                    //read REP entries
                    var reps="[";
                    var rec_count=rep_store.getCount();
                    for(var i=0;i<rec_count;i++){
                        var rec=rep_store.getAt(i);
                        if(rec.get('privilegename')!=_('None')){
                            var rep="{";
                            rep+="entityid:'"+rec.get('entityid')+"',";
                            rep+="entityname:'"+rec.get('entityname')+"',";
                            rep+="privilegename:'"+rec.get('privilegename')+"',";
                            rep+="propagate:'"+rec.get('propagate')+"'";
                            rep+="},";
                            reps+=rep;
                        }
                    }
                    reps+="]";
                    var json_reps=eval("("+reps+")");

                    var json_data=Ext.util.JSON.encode({
                        "reps":json_reps
                    });
                    url+="&reps="+json_data+"&type="+type;
                    var ajaxReq=ajaxRequest(url,0,"POST",true);//alert(url);
                    ajaxReq.request({
                        success: function(xhr) {
                            w.close();
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                grid.getStore().load({params:{type:type}});
                                Ext.MessageBox.alert(_("成功"),_("已经成功保存"));
                            }else{
                                Ext.MessageBox.alert(_("Failure"),response.msg);
                            }
                        },
                        failure: function(xhr){
                            w.close();
                            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                        }
                    });
                }else{
                    Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
                }

            }
        }
    });

    var rightpanel=new Ext.FormPanel({
        id:"rightpanel",
        layout:"form",
        title:_('角色'),
        width:490,
        height:510,
        frame:true,
        border:false,
        labelWidth:100,
        bodyBorder:false,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[role_name,role_desc]
    });

//    if(type==stackone.constants.CLOUD){
//        rightpanel.add(is_cloudadmin);
//    }
    rightpanel.add(rep_grid);

//    var role_auditpanel=new Ext.Panel({
//        id:"auditpanel",
//        title:_('Audit'),
//        width:490,
//        height:480,
//        layout:"form",
//        frame:true,
//        labelWidth:100,
//        border:false,
//        bodyBorder:false,
//        items:[createdby,createddate,modifiedby,modifieddate ]
//    });

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
        },save_button,'-',cancel_button]

    });

    var edit_role_panel=new Ext.Panel({
        id:"edit_role_panel",
        width:490,
        height:490,
        //frame:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:0px 0px 0px 0px'
        ,bbar:[{
            xtype: 'tbfill'
        },save_button,'-',cancel_button]
        ,items:[tabPanel]
    });

    if(mode=='EDIT'){
        role_name.setValue(role.name);
        if (role_name.getValue()=='admin')
            role_name.disabled=true;
        role_desc.setValue(role.description);

//        if (type==stackone.constants.CLOUD)
//            is_cloudadmin.setValue(role.is_cloudadmin)
//        createdby.setValue(role.createdby);
//        modifiedby.setValue(role.modifiedby)
//        createddate.setValue(role.createddate)
//        modifieddate.setValue(role.modifieddate)

        tabPanel.add(rightpanel);
//        tabPanel.add(role_auditpanel);
//        tabPanel.setActiveTab(role_auditpanel);
        tabPanel.setActiveTab(rightpanel);
        rep_store.load({
            params:{
                roleid:role.id
            }
        });
    }
    return edit_role_panel;
}

function NewRoleDetailsPanel(grid,mode,role,w,type){

    var role_name=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'rolename',
        width: 280,
        id: 'rolename',
        allowBlank:false
    });
    var role_desc=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'roledesc',
        width: 320,
        id: 'roledesc'
    });
//    var is_cloudadmin=new Ext.form.Checkbox({
//        fieldLabel: _('Is Cloud Admin'),
//        name: 'is_cloudadmin',
//        width: 320,
//        id: 'is_cloudadmin'
//    });

    var add_button= new Ext.Button({
        id: 'new_entity',
        text: _('添加'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon'
        ,listeners: {
        click: function(btn) {
                if (!role_name.getValue() && !role_desc.getValue()){
                    Ext.MessageBox.alert(_('错误'), _('请确保你已经输入了角色名和说明.'));
                }
                else{
                var w=new Ext.Window({
                    title :_('添加实体'),
                    width :480,
                    height:550,
                    modal : true,
                    resizable : false
                });
                w.add(EntityDetailsPanel(rep_grid1,'ADD_NEW',null,w,type));
                w.show();
            }
          }
        }
    }) ;

    var rep_store1 =new Ext.data.SimpleStore({
        fields: ['entityid','entitytype','entityname','context','privilegename']

    });


    var delete_button= new Ext.Button({
        id: 'cancel',
        text: _('删除'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
        click:function(combo,record,index){
            var rec_select=rep_grid1.getSelections();
            var len=rec_select.length;
            if(len==0){
                Ext.MessageBox.alert(_("警告"),_("请至少选择一行."))
                return;
            }
            //Ext.MessageBox.alert(_('Confirm'), _('Some of the Entities are selected.You are excluding the entities.'));
            for (var i=0;i<len;i++){
                var edit_rec=rec_select[i];
                rep_grid1.getStore().remove(edit_rec);
            }

        }
       }
    });

    var selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });
    var columnModel = new Ext.grid.ColumnModel([
    {
        header: _("编号"),
        width: 0,
        sortable: false,
        dataIndex: 'entityid',
        hidden:true
    },
    {
        header: _("实体"),
        width: 140,
        sortable: true,
        dataIndex: 'entityname'
    },
    {
        header: _("实体类型"),
        width: 110,
        sortable: true,
        dataIndex: 'entitytype'
    },
    {
        header: _("类型名称"),
        width: 110,
        sortable: false,
        dataIndex: 'typename',
        hidden:true
    },
    {
        header: _("上下文"),
        width: 110,
        sortable: false,
        dataIndex: 'context'
    },
    {
        header: _("权限"),
        width: 100,
        sortable: true,
        dataIndex: 'privilegename'
        ,renderer:function(value,params,record,row){
            var etype=record.get("typename");
            var non_granular=true;
            if(granular_ui!="True"){
                 non_granular=(etype != stackone.constants.SERVER_POOL &&
                    etype != stackone.constants.IMAGE_GROUP && etype !=stackone.constants.VDC)
                if (type == stackone.constants.CLOUD){
                    non_granular = false;
                }
            }
            if(etype != stackone.constants.IMAGE && etype != stackone.constants.DOMAIN
                    && etype !=stackone.constants.CLOUD_TEMP && etype !=stackone.constants.CLOUD_VM
                        && non_granular==true){
                params.attr='ext:qtip="Add Entity"' +
                    'style="background-image:url(icons/add.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            }
            return value;
        }
    },
    {
        header: _("Propagate"),
        width: 30,
        sortable: true,
        hidden:(granular_ui!="True"),
        dataIndex: 'propagate',
        renderer:propagate_checkbox
     }

    ]);

    var rep_grid1 = new Ext.grid.EditorGridPanel({
        store: rep_store1,
        colModel:columnModel,
        stripeRows: true,
        frame:true,
        border:true,
        selModel:selmodel,
        width:'100%',
        autoExpandColumn:2,
        height:344,
        clicksToEdit:1,
        enableHdMenu:false
        ,listeners: {
           cellclick: function(grid ,rowIndex,columnIndex,e,b) {
               if (columnIndex!=5){
                   return;
               }
               var record = grid.getStore().getAt(rowIndex);
               var etype=record.get("typename");
               var non_granular=true;
               if(granular_ui!="True"){
                    non_granular=(etype != stackone.constants.SERVER_POOL &&
                            etype != stackone.constants.IMAGE_GROUP && etype !=stackone.constants.VDC)
                    if (type == stackone.constants.CLOUD){
                        non_granular = false;
                    }
               }
               if(etype != stackone.constants.IMAGE && etype != stackone.constants.DOMAIN
                    && etype !=stackone.constants.CLOUD_TEMP && etype !=stackone.constants.CLOUD_VM
                        && non_granular==true){
                   var w=new Ext.Window({
                        title :_('添加实体'),
                        width :480,
                        height:550,
                        modal : true,
                        resizable : false
                    });
                    w.add(EntityDetailsPanel(rep_grid1,'ADD_CHILD',null,w,type));
                    w.show();
               }
            }
        }

    });

    var cancel_button= new Ext.Button({
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

    var save_button=new Ext.Button({
        id: 'save',
        text: _('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                Ext.MessageBox.show({
                            title:_('请稍候...'),
                            msg: _('请稍候...'),
                            width:300,
                            wait:true,
                            waitConfig: {
                                interval:200
                            }
                        });
                if(rightpanel.getForm().isValid()) {
                    var url="";
                    if(mode=='NEW'){
                        url='/model/add_role?rolename='+role_name.getValue()+
                        '&roledesc='+role_desc.getValue()+"&type="+type;

//                        if (type==stackone.constants.CLOUD)
//                            url+="&is_cloudadmin="+is_cloudadmin.getValue()

                    }
                    //read REP entries
                    var reps="[";
                    var rec_count=rep_store1.getCount();
                    for(var i=0;i<rec_count;i++){
                        var rec=rep_store1.getAt(i);
                        if(rec.get('privilegename')!=_('None')){
                            var rep="{";
                            rep+="entityid:'"+rec.get('entityid')+"',";
                            rep+="entityname:'"+rec.get('entityname')+"',";
                            rep+="privilegename:'"+rec.get('privilegename')+"',";
                            rep+="propagate:'"+rec.get('propagate')+"'";
                            rep+="},";
                            reps+=rep;
                        }
                    }
                    reps+="]";
                    var json_reps=eval("("+reps+")");
                    var json_data=Ext.util.JSON.encode({
                        "reps":json_reps
                    });
                    url+="&reps="+json_data;
                    var ajaxReq=ajaxRequest(url,0,"POST",true);//alert(url);
                    ajaxReq.request({
                        success: function(xhr) {
                            w.close();
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                grid.getStore().load({params:{type:type}});
                                Ext.MessageBox.alert(_("成功"),_("已经成功保存"));
                            }else{
                                Ext.MessageBox.alert(_("Failure"),response.msg);
                            }
                        },
                        failure: function(xhr){
                            w.close();
                            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                        }
                    });
                }else{
                    Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
                }

            }
        }
    });

    var reppanel=new Ext.Panel({
        id:"reppanel",
        layout:"form",
        width:490,
        height:380,
        frame:true,
        border:false,
        bodyBorder:false,
        labelWidth:150,
        bodyStyle:'padding:0px 0px 0px 0px'
        ,tbar:[
            '搜索(按实体): ',new Ext.form.TextField({
            fieldLabel: _('搜索'),
            name: 'search',
            id: 'search',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    rep_grid1.getStore().filter('Name', field.getValue(), false, false);
                }
            }

        }),{
            xtype: 'tbfill'
        },add_button,delete_button],
        items:[rep_grid1]
    });


    var rightpanel=new Ext.FormPanel({
        id:"rightpanel",
        layout:"form",
        width:490,
        height:85,
        frame:true,
        border:false,
        labelWidth:100,
        bodyBorder:false,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[role_name,role_desc]
    });

//    if (type==stackone.constants.CLOUD)
//        rightpanel.add(is_cloudadmin);

    var new_role_panel=new Ext.Panel({
        id:"new_role_panel",
        width:490,
        height:490,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:0px 0px 0px 0px'
        ,bbar:[{
            xtype: 'tbfill'
        },save_button,'-',cancel_button]
        ,items:[rightpanel,reppanel]
    });

    return new_role_panel;
}

function EntityDetailsPanel(grid,mode,role,w,type){
    var type_combo_value="",type_combo_raw_value="";
    var top_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">'+_("请选择对象并为其分配需要的权限.")+'</div>',
        id:'label_role'
    });
    var top_label2=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">'+_("请选择子对象并为其分配需要的权限.")+'</div>',
        id:'label_role'
    });

    var selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });

    var type_store = new Ext.data.JsonStore({
        url: '/model/get_entitytype_role',
        root: 'rows',
        fields: ['typeid', 'name','display'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){//alert(res.responseText);
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load:function(store,recs,opts){
            }
        }
    });
     type_store.load({
         params:{
             type:type
         }
     });

    var type_combo=new Ext.form.ComboBox({
        id: 'type',
        fieldLabel: _('实体类型'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择实体"),
        store: type_store,
        width:190,
        displayField:'display',
        valueField:'name',
        typeAhead: true,
        minListWidth:50,
        mode:'local',
        forceSelection: true,
        selectOnFocus:true,
        listeners:{
            select:function(combo,record,index){
                var etype=record.get('name');
                type_combo_raw_value = combo.getRawValue();
                type_combo_value = combo.getValue();
                entity_store.load({
                    params:{
                        type:etype
                    }
                });
                setREPColumnHeaders(etype, columnModel);
            }
        }
    });

    var entity_store = new Ext.data.JsonStore({
        url: '/model/get_entities_bytype?',
        root: 'rows',
        fields: ['id', 'name','parent', 'grnd_parent'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){//alert(res.responseText);
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });

    var priv_store = new Ext.data.JsonStore({
        url: '/model/get_privileges4opsg',
        root: 'rows',
        fields: ['privid', 'privname'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){//alert(res.responseText);
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    priv_store.load({
        params:{
            type:type
        }
    });

    var rep_rec = Ext.data.Record.create([
    {
        name: 'entityid',
        type: 'string'
    },
    {
        name: 'entitytype',
        type: 'string'
    },
    {
        name: 'typename',
        type: 'string'
    },
    {
        name: 'entityname',
        type: 'string'
    },
    {
        name:'context',
        type:'string'
    },
    {
        name: 'privilegename',
        type: 'string'
    }
    ]);
    var priv_combo=new Ext.form.ComboBox({
        fieldLabel: _('权限'),
        allowBlank:false,
        width: 190,
        store:priv_store,
        id:'priv_combo',
        forceSelection: true,
        triggerAction:'all',
        emptyText :_("None"),
        minListWidth:50,
        displayField:'privname',
        valueField:'privname',
        mode:'local'
    });

    var cancel_button= new Ext.Button({
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

    var columnModel = new Ext.grid.ColumnModel([
    {
        header: _("编号"),
        width: 0,
        sortable: false,
        dataIndex: 'id',
        hidden:true
    },
    {
        header: _("实体"),
        width: 180,
        sortable: true,
        dataIndex: 'name'
    },
    {
        header: _(""),
        width: 100,
        sortable: false,
        dataIndex: 'parent'
    },
    {
        header: _(""),
        width: 100,
        sortable: false,
        dataIndex: 'grnd_parent'
    },
    {
        header: _("Propagate"),
        width: 30,
        sortable: true,
        hidden:(granular_ui!="True"),
        dataIndex: 'propagate',
        renderer:propagate_checkbox
        },
    selmodel
   ])
   var select_entities_grid = new Ext.grid.EditorGridPanel({
        stripeRows: true,
        colModel:columnModel,
        border:true,
        selModel:selmodel,
        clicksToEdit:1,
        enableHdMenu:false,
        id:'ent_grid',
        loadMask:true,
        store: entity_store,
        width:'100%',
        autoExpandColumn:1,
        height:340
        ,tbar:[
            '搜索(按实体): ',new Ext.form.TextField({
            fieldLabel: _('搜索'),
            name: 'search',
            id: 'search',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    select_entities_grid.getStore().filter('name', field.getValue(), false, false);
                }
            }

        })]
    });


  var submit_button= new Ext.Button({
    id: 'add',
    text: _('确定'),
    icon:'icons/accept.png',
    cls:'x-btn-text-icon',
    listeners: {
        click: function(btn) {

            var selections=select_entities_grid.getSelections();
            if(selections.length==0){
                Ext.MessageBox.alert(_('错误'), _('请至少选择一行.'));
                return;
            }
            for (var i=0;i<=selections.length-1;i++){
                if (mode=="ADD_NEW"){
                    var new_entry=new rep_rec({
                    entityid:selections[i].get('id'),
                    entitytype:type_combo_raw_value,
                    typename:type_combo_value,
                    entityname:selections[i].get('name'),
                    propagate:selections[i].get('propagate'),

                    privilegename: priv_combo.getValue()
                    });
                }
                if(mode=="ADD_CHILD"){
                    var rec=grid.getSelectionModel().getSelected();
                    new_entry=new rep_rec({
                    entityid:selections[i].get('id'),
                    entitytype:type_combo_raw_value,
                    typename:type_combo_value,
                    entityname:selections[i].get('name'),
                    propagate:selections[i].get('propagate'),
                    context:rec.get('entityname'),
                    privilegename: priv_combo.getValue()
                    });
                }

                var n=grid.getStore().getCount();
                for (var j=0;j<n;j++){
                    var rec=grid.getStore().getAt(j);
                    if(rec.get("entityid")==selections[i].get('id')){
                        grid.getStore().remove(rec);
                        break;
                    }
                }
                grid.getStore().insert(0,new_entry);
            }
            w.close();
        }
   }
   });
   if (mode=="ADD_NEW"){
        if(type==stackone.constants.StackOne)
            priv_combo.setValue("VIEW");
        else if (type==stackone.constants.CLOUD)
            priv_combo.setValue("VIEW_CLOUD");
        //type_combo.setValue("Data Center");
    }
    if(mode=="ADD_CHILD"){//alert("===")
        type_combo.disabled=true;
        if(type==stackone.constants.StackOne)
            priv_combo.setValue("VIEW");
        else if (type==stackone.constants.CLOUD)
            priv_combo.setValue("VIEW_CLOUD");
        var rec=grid.getSelectionModel().getSelected();

        var typename = rec.get('typename');
        if (typename==stackone.constants.DATA_CENTER){
          typename=stackone.constants.SERVER_POOL
        }
        else if (typename==stackone.constants.IMAGE_STORE){
          typename=stackone.constants.IMAGE_GROUP
        }
        else if (typename==stackone.constants.SERVER_POOL){
          typename=stackone.constants.MANAGED_NODE
        }
        else if (typename==stackone.constants.IMAGE_GROUP){
          typename=stackone.constants.IMAGE
        }
        else if (typename==stackone.constants.MANAGED_NODE){
          typename=stackone.constants.DOMAIN
        }
        else if(typename==stackone.constants.VDC){
            if (granular_ui != "True"){
                type_combo.enable();
                type_combo.setValue("Select Type");
                type_store.load({
                params:{
                    type:"VDC_Cloud"
                    }
                });
            }
            else{
                type_combo.enable();
                type_combo.setValue("Select Type");
                type_store.load({
                params:{
                    type:"VDC_granular_Cloud"
                    }
                });
            }
        }
        else if(typename==stackone.constants.VDC_VM_FOLDER){
            typename=stackone.constants.CLOUD_VM
        }
        else if(typename==stackone.constants.TMP_LIB){
            typename=stackone.constants.CLOUD_TMPGRP
        }
        else if(typename==stackone.constants.CLOUD_TMPGRP){
            typename=stackone.constants.CLOUD_TEMPLATE
        }
        stackone.type_map = {
            "DATA_CENTER":"Data Center",
            "IMAGE_STORE":"Template Library",
            "SERVER_POOL":"Server Pool",
            "IMAGE_GROUP":"Template Group",
            "MANAGED_NODE":"Server",
            "DOMAIN":"Virtual Machine",
            "IMAGE":"Template",
            "VDC":"Virtual DataCenter",
            "VDC_VM_FOLDER":"Virtual Machines Folder",
            "TMP_LIB":"Template Library",
            "CLOUD_TMPGRP":"Template Group",
            "CLOUD_TEMPLATE":"Template",
            "CLOUD_VM":"Cloud VM"
        }
            type_combo_value=typename;
            type_combo_raw_value=eval("stackone.type_map."+typename);
            if(typename!=stackone.constants.VDC){
                type_combo.setValue(type_combo_raw_value);
            }
            entity_store.load({
            params:{
                type:typename,
                parententityid:rec.get('entityid')
                }
            });
            setREPColumnHeaders(typename, columnModel);
        }

     var mainentitypanel=new Ext.Panel({
        id:"entpanel",
        width:470,
        layout:"form",
        height:520,
        frame:false,
        border:false,
        bodyBorder:false,
        labelWidth:100,
        bodyStyle:'padding-top:0px;padding-left:0px;'
        ,bbar:[{
            xtype: 'tbfill'
        },submit_button,'-',cancel_button]
//        ,items:[top_label,type_combo,select_entities_grid,priv_combo]
    });

   var entitypanel1=new Ext.Panel({
        id:"entpanel1",
        layout:"form",
        width:465,
        height:420,
        frame:true,
        border:true,
        bodyBorder:true,
        labelWidth:100,
        cls: 'whitebackground',
        bodyStyle:'padding-left:10px,padding-right:0px'
       // ,items:[type_combo,select_entities_grid]
    });

    var entitypanel2=new Ext.Panel({
        id:"entpanel2",
        layout:"form",
        width:465,
        height:100,
        frame:false,
        border:true,
        bodyBorder:true,
        labelWidth:100,
         cls: 'whitebackground',
        bodyStyle:'padding-left:10px;'
       // ,items:[type_combo,select_entities_grid]
    });
    var fldset=new Ext.form.FieldSet({
        title: _(''),
        collapsible: false,
        autoHeight:true,
        width: 450,
        collapsed: false
//        items :[ xen_port,xen_mgrn_port,ssh_port,use_keys,is_standby ]
    });
    if (mode=='ADD_NEW'){
        fldset.add(top_label);
    }else{
        fldset.add(top_label2);
    }
    fldset.add(type_combo);
    fldset.add(select_entities_grid);
    entitypanel1.add(fldset);
    entitypanel2.add(priv_combo);
    mainentitypanel.add(entitypanel1);
    mainentitypanel.add(entitypanel2);

   return mainentitypanel;
}

function setREPColumnHeaders(etype, columnModel){
    if (etype==stackone.constants.DATA_CENTER || etype==stackone.constants.IMAGE_STORE
        || etype==stackone.constants.SERVER_POOL || etype==stackone.constants.IMAGE_GROUP){
        columnModel.setHidden(2, true);
        columnModel.setHidden(3, true);
    }
    if (etype==stackone.constants.MANAGED_NODE){
        columnModel.setHidden(2, false);
        columnModel.setColumnHeader(2, "Server Pool");
        columnModel.setHidden(3, true);
    }
    if (etype==stackone.constants.IMAGE){
        columnModel.setHidden(2, false);
        columnModel.setColumnHeader(2, "Template Group");
        columnModel.setHidden(3, true);
    }
    if (etype==stackone.constants.DOMAIN){
        columnModel.setHidden(2, false);
        columnModel.setHidden(3, false);
        columnModel.setColumnHeader(2, "Server");
        columnModel.setColumnHeader(3, "Server Pool");
    }
    if (etype==stackone.constants.VDC){
        columnModel.setHidden(2, true);
        columnModel.setHidden(3, true);
    }
}