/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* author : Benf<yangbf@stackone.com.cn>
*/

function privilegeUI(){
    var privilege_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">'+_("创建/编辑权限. ")+_("添加操作组到权限")+'<br/></div>'
    });
    
    var privilege_new_button=new Ext.Button({
        id: 'privilege_new',
        text: _('新建'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var w=new Ext.Window({
                    title :_('新建权限'),
                    width :420,
                    height:450,
                    modal : true,
                    resizable : false
                });
                w.add(privDetailsPanel(privilege_grid,'NEW',null,w));
                w.show();
            }
        }
    }) ;
    var privilege_remove_button=new Ext.Button({
        id: 'privilege_remove',
        text: _('移除'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {

            click: function(btn) {

                if(!privilege_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("	请从权限列表选择一个记录"));
                    return false;
                }
                var edit_rec=privilege_grid.getSelectionModel().getSelected();
                var privid=edit_rec.get('privilegeid');

                var url='/model/delete_privilege?privilegeid='+privid;
                Ext.MessageBox.confirm(_("确认"),_("确定要删除该权限吗?"), function (id){
                    if(id=='yes'){
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    privilege_grid.getStore().load();
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

    var privilege_edit_button= new Ext.Button({
        id: 'privilege_edit',
        text: _('编辑'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',

        listeners: {
            click: function(btn) {
                if(!privilege_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从权限列表选择一个记录"));
                    return false;
                }
                var edit_rec=privilege_grid.getSelectionModel().getSelected();
                var privilegeid=edit_rec.get('privilegeid');
                var url="/model/edit_privilege_det?privilegeid="+privilegeid;
                var ajaxReq=ajaxRequest(url,0,"POST",true);

                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            var privdateails=response.edit_privilege_det[0];
                            var privid=privdateails.privilegeid;
                            var w=new Ext.Window({
                                title :_('编辑权限'),
                                width :420,
                                height:450,
                                modal : true,
                                resizable : false
                            });
                            w.add(privDetailsPanel(privilege_grid,'EDIT',privdateails,w));
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


    var privilege_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var privilege_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("权限编号"),
        width: 0,
        dataIndex: 'privilegeid',
        menuDisabled: true,
        hidden:true
    },
    {
        header: _("权限名称"),
        width: 150,
        dataIndex: 'privilegename',
        sortable:false
    },
    {
        header: _("操作组"),
        width: 150,
        dataIndex: 'opgroups',
        sortable:false,
        wordwrap:true
    },
    {
        header: _("说明"),
        width: 195,
        dataIndex: 'desc',
        sortable:false,
        wordwrap:true
    },
    {
        header: _("搜索名称"),
        width:0,
        dataIndex: 'searchName',
        menuDisabled:false,
        hidden:true
    }
    ]);

    var privilege_store =new Ext.data.JsonStore({
        url: "/model/get_privileges",
        root: 'rows',
        fields: ['privilegeid','privilegename','opgroups','desc','searchName'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }

        }
    });

    privilege_store.load();

    var privilege_grid=new Ext.grid.GridPanel({
        store: privilege_store,
        stripeRows: true,
        colModel:privilege_columnModel,
        frame:false,
        selModel:privilege_selmodel,
        autoscroll:true,
        height:360,
        width:515,
        enableHdMenu:false,
        id:'privilege_grid',

        //  bbar: new Ext.PagingToolbar({
        //      store: privilege_store,
        //      displayInfo:true,
        //      displayMessage:"Displaying privilegeInfo {0} - {1} of {2}"
        //  }),

        tbar:[
            _('搜索(按名称): '),new Ext.form.TextField({
            fieldLabel: _('搜索'),
            name: 'search',
            id: 'search',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    privilege_grid.getStore().filter('searchName', field.getValue(), false, false);
                }
            }

        }),{ 
            xtype: 'tbfill'
        },privilege_new_button,'-',privilege_edit_button,'-',privilege_remove_button],
        listeners:{
            rowdblclick:function(grid, rowIndex, e){
                privilege_edit_button.fireEvent('click',privilege_edit_button);
            }
        }

    });

    var privilegepanel=new Ext.Panel({
        id:"privilegepanel",
        title:_('权限'),
        layout:"form",
        width:535,
        height:450,
        frame:false,
        labelWidth:130,
        border:0,
        cls: 'whitebackground',
        bodyStyle:'padding:0px 0px 0px 0px',
        items: [privilege_label,privilege_grid]
    });

    return privilegepanel;
}


function privDetailsPanel(grid,mode,priv,w){
    var privilege_label=new Ext.form.Label({
        html:'<div style="" width="250"><br></div>'
    });

    var privilege_label2=new Ext.form.Label({
        html:'<div style="" class="backgroundcolor" width="250">'+_("分配操作组")+'<br/></div><br>'
    });

    var privilege_id=new Ext.form.TextField({
        fieldLabel: _('权限编号'),
        name: 'privilegeid',
        width: 150,
        id: 'privilegeid',
        allowBlank:false,
        disabled: true
    });
    var privilege_name=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'privilegename',
        width: 150,
        id: 'privilegename',
        allowBlank:false
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

    var url="";
    if(mode=='NEW'){
        url="/model/get_opsgroups_map";
    }
    else if(mode=='EDIT'){
        url="/model/get_opsgroups_map?privid="+priv.privilegeid;
    }

    var privileges_fromstore = new Ext.data.JsonStore({
        url: url,
        root: 'opsgroup_det',
        fields: ['opsgroupid','opsgroupname'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    privileges_fromstore.load();

    var privileges_tostore = new Ext.data.JsonStore({
        url: '/model/get_toopsgroups_map',
        root: 'toopsgroup_det',
        fields: ['opsgroupid','opsgroupname'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    
    var privilege_cancel_button= new Ext.Button({
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

    var privilege_save_button=new Ext.Button({
        id: 'save',
        text: _('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(privilege_rightpanel.getForm().isValid()) {
                    var url="";
                    if(privilegeitemselector.toStore.getCount()==0){
                        Ext.MessageBox.alert(_("请至少选择一个操作组"));
                        return;
                    }
                    if(mode=='NEW'){
                        url='/model/save_privilege_details?privilegeid='+privilege_id.getValue()+
                        '&privilegename='+privilege_name.getValue()+'&opsgrups='+privilegeitemselector.getValue();
                    }else if(mode=='EDIT'){
                        var record=null;
                        var  opsgrpids="";
                        var rec_count=privilegeitemselector.toStore.getCount();
                        for (var i=0; i<rec_count; i++) {
                            record = privilegeitemselector.toStore.getAt(i);
                            var  opsgrid=record.get('opsgroupid');
                            opsgrpids+=opsgrid+",";
                        }
                        url='/model/updatesave_privilege_details?privilegeid='+priv.privilegeid+'&privilegename='+privilege_name.getValue()+
                        '&opsgrups='+opsgrpids;
                    }

                    var ajaxReq=ajaxRequest(url,0,"POST",true);

                    ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                var privileges_det=response.privilege_det[0];
                                if('F'==privileges_det){
                                    Ext.MessageBox.alert(_("失败"),format(_("权限{0}已经存在"),privilege_name.getValue()));
                                    return false;
                                }
                                Ext.MessageBox.alert(_("成功"),_("已经成功保存"));
                                w.close();
                                grid.getStore().load();

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
        border:false,
        id:'tabpanel',
        bbar:[{
            xtype: 'tbfill'
        },privilege_save_button,'-',privilege_cancel_button]

    });

    var privilegeitemselector=new Ext.ux.ItemSelector({
        name:"itemselector",
        dataFields:["opsgroupid", "opsgroupname"],
        toStore:privileges_tostore,
        msWidth:150,
        msHeight:250,
        valueField:"opsgroupid",
        displayField:"opsgroupname",
        imagePath:"icons/",
        drawUpIcon:false,
        drawDownIcon:false,
        drawLeftIcon:true,
        drawRightIcon:true,
        drawTopIcon:false,
        drawBotIcon:false,
        toLegend:_("选择"),
        fromLegend:_("可用"),
        store: privileges_fromstore,
        fromStore:privileges_fromstore,

        toTBar:[{
            text:_("清除"),
            handler:function(){
                privilegeitemselector.reset();
            }
        }]

    });

    var privilege_rightpanel=new Ext.FormPanel({
        id:"rightpanel",
        layout:"form",
        title:_('权限'),
        width:300,
        height:350,
        frame:true,
        labelWidth:35,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[privilege_name,privilege_label,privilege_label2,privilegeitemselector]
    });

    var privilege_auditpanel=new Ext.Panel({
        id:"auditpanel",
        title:_('审计'),
        width:300,
        height:350,
        layout:"form",
        frame:true,
        labelWidth:100,
        border:false,
        bodyBorder:false,
        items:[createdby,createddate,modifiedby,modifieddate ]
    });

    if(mode=='EDIT'){
        privilege_name.setValue(priv.privilegename);
//        privilege_name.disabled=true;
        privileges_tostore.load({
            params:{
                privilegeid: priv.privilegeid
            }
        });

        tabPanel.add(privilege_rightpanel);
        tabPanel.add( privilege_auditpanel);
        tabPanel.setActiveTab(privilege_auditpanel);
        tabPanel.setActiveTab(privilege_rightpanel);

        createdby.setValue(priv.createdby);
        modifiedby.setValue(priv.modifiedby);
        createddate.setValue(priv.createddate);
        modifieddate.setValue(priv.modifieddate);

    }

    tabPanel.add(privilege_rightpanel);
    tabPanel.setActiveTab(privilege_rightpanel);

    var new_privilege_panel=new Ext.Panel({
        id:"new_privilege_panel",
        layout:"form",
        width:400,
        height:480,
        frame:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[tabPanel]
    });

    return new_privilege_panel;

}

