/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function operationsUI(){

    var operations_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">'+_("一个实体类型的低级别操作")+'<br/></div>'
    });

    var operation_new_button=new Ext.Button({
        id: 'operations_new',
        text: _('新建'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var w=new Ext.Window({
                    title :_('新的操作'),
                    width :450,
                    height:450,
                    modal : true,
                    resizable : false
                });
                w.add(operationDetailsPanel(operation_grid,'NEW',null,w));
                w.show();
            }
        }
    }) ;

    var operation_remove_button=new Ext.Button({
        id: 'operation_remove',
        text: _('移除'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {

            click: function(btn) {
                if(!operation_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从用户列表选择一个记录"));
                    return false;
                }
                var edit_rec=operation_grid.getSelectionModel().getSelected();
                var opid=edit_rec.get('opid');
                var opname=edit_rec.get('opname');

                var url='/model/delete_operation?opid='+opid;

                Ext.MessageBox.confirm(_("确认"),_("确认要删除新建的操作")+opname+"吗?", function (id){
                    if(id=='yes'){
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    operation_grid.getStore().load();
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
    var operation_edit_button= new Ext.Button({
        id: 'operation_edit',
        text: _('编辑'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',

        listeners: {
            click: function(btn) {

                if(!operation_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从用户列表选择一个记录"));
                    return false;
                }
                var edit_rec=operation_grid.getSelectionModel().getSelected();
                var opid=edit_rec.get('opid');
                var ent=edit_rec.get('enttype');
                var url="/model/edit_op_det?opid="+opid+"&enttype="+ent;
                var ajaxReq=ajaxRequest(url,0,"POST",true);

                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            var users_det=response.edit_op_det[0];
                            var w=new Ext.Window({
                                title :_('编辑操作'),
                                width :450,
                                height:450,
                                modal : true,
                                resizable : false
                            });
                            w.add(operationDetailsPanel(operation_grid,'EDIT',users_det,w));
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

    var operation_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });
    var operation_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width: 150,
        sortable:true,
        dataIndex: 'opname'
    },
    {
        header: _("说明"),
        width: 180,
        sortable: true,
        dataIndex: 'description'
    },
    {
        header: _("显示"),
        width: 55,
        sortable: false,
        dataIndex: 'cd'
    },
    {
        header: _("实体类型"),
        width:110,
        sortable: true,
        dataIndex: 'enttype'
    },
    {
        header: _("Op Id"),
        width: 0,
        dataIndex: 'opid',
        menuDisabled: true,
        hidden:true
    }
    ]);

    var operation_store =new Ext.data.JsonStore({
        url: "/model/get_operations",
        root: 'rows',
        fields: ['opname','description', 'cd','enttype', 'opid'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }

        }
    });

    operation_store.load();

    var operation_grid=new Ext.grid.GridPanel({
        store: operation_store,
        stripeRows: true,
        colModel:operation_columnModel,
        frame:false,
        selModel:operation_selmodel,
        height:360,
        width:'100%',
        enableHdMenu:false,
        id:'op_grid',
        layout:'fit',
        loadMask:true,

        //            bbar: new Ext.PagingToolbar({
        //            store: operation_store,
        //            displayInfo:true,
        //            displayMessage:"Displaying userInfo {0} - {1} of {2}"
        //            }),

        tbar:[
            _('搜索 (按名称):'),new Ext.form.TextField({
            fieldLabel: _('搜索'),
            name: 'search',
            id: 'search',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    operation_grid.getStore().filter('opname', field.getValue(), false, false);
                }
            }

        }),{ 
            xtype: 'tbfill'
        },operation_new_button,'-',operation_edit_button,'-',operation_remove_button],
        listeners:{
            rowdblclick:function(grid, rowIndex, e){
                operation_edit_button.fireEvent('click',operation_edit_button);
            }
        }

    });

    var oppanel=new Ext.Panel({
        id:"oppanel",
        title:_('操作'),
        layout:"form",
        width:535,
        height:450,
        cls: 'whitebackground',
        frame:false,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:5px 5px 5px 5px',
        items: [operations_label,operation_grid]
    });

    return oppanel;
}
function operationDetailsPanel(grid,mode,operation,w){
    
    var op_id=new Ext.form.TextField({
        fieldLabel: _('OP Id'),
        name: 'opid',
        width: 150,
        id: 'opid',
        allowBlank:false
    });

    var op_name=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'opname',
        width: 150,
        id: 'opname',
        allowBlank:false
    });
    var desc=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'desc',
        width: 150,
        id: 'desc',
        allowBlank:false
    });
    var context_display=new Ext.form.Checkbox({
        fieldLabel: _('上下文显示'),
        name: 'contextdisplay',
        value: 'true',
        width: 150,
        id: 'contextdisplay',
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
    var disp_name=new Ext.form.TextField({
        fieldLabel: _('显示名称'),
        name: 'dispname',
        width: 150,
        id: 'dispname',
        allowBlank:false
    });
    var icon=new Ext.form.TextField({
        fieldLabel: _('图标'),
        name: 'icon',
        width: 150,
        id: 'icon',
        allowBlank:false
    });

    var url="";
    if(mode=='NEW'){
        url="/model/get_entitytype_map";
    }
    else if(mode=='EDIT'){
        url="/model/get_entitytype_map?opid="+operation.opid;
    }

    var entity_fromstore = new Ext.data.JsonStore({
        url: url,
        root: 'entitytype_det',
        fields: ['entid','entname'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    entity_fromstore.load();

    var entity_tostore = new Ext.data.JsonStore({
        url: '/model/get_toentitytype_map',
        root: 'toentitytype_det',
        fields: ['entid','entname'],
        successProperty:'success',
        sortInfo: {
            field: 'entname',
            direction: 'ASC' // or 'DESC' (case sensitive for local sorting)
        },
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });

    var operation_cancel_button= new Ext.Button({
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

    var operation_save_button=new Ext.Button({
        id: 'save',
        text: _('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',

        listeners: {
            click: function(btn) {
                if(operation_rightpanel.getForm().isValid()) {
                    var url="";
                    if(mode=='NEW'){
                        url="/model/save_oper_det?opname="+op_name.getValue()+"&descr="+desc.getValue()+"&context_disp="+context_display.getValue()+"&entityid="+itemselector.getValue()+"&dispname="+disp_name.getValue()+"&icon="+icon.getValue();
                    }else if(mode=='EDIT'){
                        url="/model/updatesave_op_det?opid="+operation.opid+"&opname="+op_name.getValue()+"&desc="+desc.getValue()+"&entid="+itemselector.getValue()+"&context_disp="+context_display.getValue()+"&dispname="+disp_name.getValue()+"&icon="+icon.getValue();
                    }

                    var ajaxReq=ajaxRequest(url,0,"POST",true);

                    ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                var users_det=response.operation_det[0];
                                if('F'==users_det){
                                    Ext.MessageBox.alert(_("失败"),format(_("操作{0} 已经存在"),op_name.getValue()));
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

    var itemselector=new Ext.ux.ItemSelector({
        name:"itemselector",
        dataFields:["entid","entname"],
        toStore:entity_tostore,
        msWidth:120,
        msHeight:180,
        allowBlank:false,
        valueField:"entid",
        displayField:"entname",
        imagePath:"icons/",
        drawUpIcon:false,
        drawDownIcon:false,
        drawLeftIcon:true,
        drawRightIcon:true,
        drawTopIcon:false,
        drawBotIcon:false,
        toLegend:_("选择"),
        fromLegend:_("可用"),
        fromStore:entity_fromstore,
        toTBar:[{
            text:_("清除"),
            handler:function(){
                itemselector.reset();
            }
        }]
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
        },operation_save_button,'-',operation_cancel_button]

    });

        
    var operation_rightpanel=new Ext.FormPanel({
        id:'rightpanel',
        title:_('操作'),
        layout:"form",
        width:440,
        height:350,
        frame:true,
        labelWidth:100,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[op_name,desc,disp_name,icon,context_display,itemselector]
    });

    var operation_auditpanel=new Ext.Panel({
        id:"auditpanel",
        title:_('审计'),
        width:440,
        height:350,
        layout:"form",
        frame:true,
        labelWidth:100,
        border:false,
        bodyBorder:false,
        items:[createdby,createddate,modifiedby,modifieddate ]
    });


    tabPanel.add(operation_rightpanel);
    tabPanel.setActiveTab(operation_rightpanel);
    if(mode=='EDIT'){

        var opid=operation.opid;
        op_id.setValue(operation.opid);
        op_name.setValue(operation.opname);
        op_name.disabled=true;
        desc.setValue(operation.desc);
        context_display.setValue(operation.contextdisplay);
        disp_name.setValue(operation.dispname);
        icon.setValue(operation.icon);
        entity_fromstore.load();
        entity_tostore.load({
            params:{
                opid:opid
            }
        });
        tabPanel.add(operation_rightpanel);
        tabPanel.add(operation_auditpanel);
        tabPanel.setActiveTab(operation_auditpanel);

        tabPanel.setActiveTab(operation_rightpanel);
        createdby.setValue(operation.createdby);
        modifiedby.setValue(operation.modifiedby)
        createddate.setValue(operation.createddate)
        modifieddate.setValue(operation.modifieddate)
    }

    var new_operation_panel=new Ext.Panel({
        id:"new_operation_panel",
        layout:"form",
        width:440,
        height:440,
        frame:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[tabPanel]
    });
    return new_operation_panel;
}

