/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* author : Benf<yangbf@stackone.com.cn>
*/
var vm_storage_disk_id=null;
var storage_id=null;
var storage_name=null;
// vmconfig settings main function

function AdvanceOptionGrid(advance_option_store, label){



 var advance_option_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width:150,
        dataIndex: 'attribute',
        //css:'font-weight:bold; color:#414141;',
        editor: new Ext.form.TextField({
            allowBlank: false
        }),
        sortable:true
    },
    {
        header: _("值"),
        dataIndex: 'value',
        editor: new Ext.form.TextField({
            allowBlank: false
        }),
        sortable:true
    }
    ]);


//     var advance_option_store = new Ext.data.JsonStore({
//         url: '/backup/get_copy_options?group_id='+group_id,
//         root: 'rows',
//         fields: ['attribute','value'],
//         successProperty:'success',
//         listeners:{
//             loadexception:function(obj,opts,res,e){
//                 var store_response=Ext.util.JSON.decode(res.responseText);
//                 Ext.MessageBox.alert(_("Error"),store_response.msg);
//             }
//         }
// 
//     });
//    advance_option_store.load();

    var prov_rec = Ext.data.Record.create([
    {
        name: 'attribute',
        type: 'string'
    },

    {
        name: 'value',
        type: 'string'
    }
    ]);

    var prov_add=new Ext.Button({
        name: 'prov_add',
        id: 'prov_add',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var r=new prov_rec({
                    attribute: '',
                    value: ' '
                });

                advance_option_grid.stopEditing();
                advance_option_store.insert(0, r);
                advance_option_grid.startEditing(0, 0);
            }
        }
    });
    var prov_remove=new Ext.Button({
        name: 'prov_remove',
        id: 'prov_remove',
        text:_("移除"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                advance_option_grid.getStore().remove(advance_option_grid.getSelectionModel().getSelected());
            }
        }
    });

    var prov_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var advance_option_grid = new Ext.grid.EditorGridPanel({
        store: advance_option_store,
        id: "advance_option_grid",
        stripeRows: true,
        colModel:advance_option_columnModel,
        frame:false,
        border: false,
        selModel:prov_selmodel,
        autoExpandColumn:1,
        //autoExpandMin:325,
        //autoExpandMax:426,
        autoscroll:true,
        height:300,
        width:'100%',
        clicksToEdit:2,
        enableHdMenu:false,
        tbar:[{
            xtype: 'tbfill'
        },prov_add,prov_remove]
    });

    return advance_option_grid;
}
    

function AdvanceOptionPanel( option_window,advance_option_store, label ){

    var advance_option_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+label+'<br/></div>'
    });


   var advance_option_grid = AdvanceOptionGrid( advance_option_store);
    // advance_option panel declaration
   //var advance_option_store= advance_option_grid.getStore();

    var button_save=new Ext.Button({
        name: 'save',
        id: 'save',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

//             var option_stat="{";
//             for(var i=0;i<advance_option_store.getCount();i++){ 
//                /* var allow_backup_str = "False";  
//                 if (vm_list_store.getAt(i).get("allow_backup"))
//                 {
//                     allow_backup_str = "True";  
//                 }   */      
//                 //option_stat+="{";
//                 //option_stat+="'attribute':";
//                 option_stat+="'"+advance_option_store.getAt(i).get("attribute")+"':";
//                 //option_stat+=", 'value':";
//                 option_stat+="'"+advance_option_store.getAt(i).get("value")+"',";
//                 //option_stat+="},";
//                 
//             }
//             option_stat+="}";
//             
            
            //var option_jdata= eval("("+option_stat+")");

            option_window.close();  
            }
        }
});
    var button_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                
                advance_option_store.load();
                option_window.close();  
                
            }
        }
    });

    var advance_option_panel=new Ext.Panel({
        id:"advance_option_panel",
        layout:"form",
        width:"100%",
        height:350,
        //cls: 'paneltopborder',
        frame:false,
        autoWidth:true,
        border:0,
        //bodyStyle:'padding:0px 0px 0px 0px',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[advance_option_label,advance_option_grid],
        bbar:[
        {
            xtype: 'tbfill'
        },button_save, button_cancel ],
        
        listeners:{
            show:function(p){
                
                if(advance_option_store.getTotalCount()>0){
                    //advance_option_store.sort('attribute','ASC');
                }
            }
        }
    });

return advance_option_panel;
}


function SP_Backup_Grid(node){

    var url_str= ""
    if(node.attributes.nodetype==stackone.constants.SERVER_POOL)
    {
        var node_id = node.attributes.id;
        var node_type = node.attributes.nodetype;
        
        url_str= 'backup/get_backupsetupinfo?node_id=' +node_id+ '&node_type='+ node_type;
    }
    if(node.attributes.nodetype==stackone.constants.DOMAIN)
    { 
        var vm_id = node.attributes.id;
    
        var s_node = node.parentNode;
        var sp_node = s_node.parentNode;
        sp_id = sp_node.attributes.id;
        url_str= 'backup/get_vm_backupsetupinfo?sp_id=' +sp_id+ '&vm_id='+vm_id;
    
    }
    var backup_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var title_edit = new Ext.form.TextField();

    var backup_columnModel = new Ext.grid.ColumnModel([
    {
        header: "Site ID",
        width: 50,
        dataIndex: 'backupsetup_id',
        menuDisabled: false,
        hidden:true,
        editor: title_edit
    },
    {
        header: "名称",
        width: 100,
        dataIndex: 'taskname',
        sortable:true,
        editor: title_edit,
        id:'taskname'

    },
    {
        header: "备份类型",
        width: 100,
        dataIndex: 'backup_type',
        sortable:true,
        editor: title_edit,
        id:'backup_type'

    },
    {
        header: "位置",
        width: 150,
        dataIndex: 'location',
        sortable:true,
        editor: title_edit,
        id:'location'

    },
// {
//         header: "Number of Runs",
//         width: 100,
//         dataIndex: 'num_runs',
//         sortable:true,
//         editor: title_edit,
//         id:'num_runs'
// 
//     },
{
        header: "时间表",
        width: 150,
        dataIndex: 'next_schedule',
        sortable:true,
        editor: title_edit,
        id:'next_schedule'

    },
    ]);

     var backup_store =new Ext.data.JsonStore({
            //url: "/get_backupsetupinfo?sp_id="+ group_id,
            url: url_str,
            root: 'rows',
            fields: [ 'backupsetup_id','taskname','backup_type', 'location', 'next_schedule'  ],
            successProperty:'success',
            listeners:{
                loadexception:function(obj,opts,res,e){
                    var store_response=Ext.util.JSON.decode(res.responseText);
                    Ext.MessageBox.alert("Error",store_response.msg);
                }

            }
        });

    backup_store.load();


    var backup_grid=new Ext.grid.GridPanel({
        store: backup_store,
        stripeRows: true,
        colModel:backup_columnModel,
        frame:false,
        selModel:backup_selmodel,
        height:310, //355
        width:'100%',
        enableHdMenu:false,
        loadMask:true,
        id:'backup_grid',
        layout:'fit'
//        tbar:[backup_new_button,'-',backup_edit_button,'-',backup_remove_button,
//             'Search (by Name): ',new Ext.form.TextField({
//             fieldLabel: 'Search',
//             name: 'search',
//             id: 'search',
//             allowBlank:true,
//             enableKeyEvents:true,
//             listeners: {
//                 keyup: function(field) {
//                     backup_grid.getStore().filter('taskname', field.getValue(), false, false);
//                 }
//             }
// 
//         }),{ xtype: 'tbfill'}],
//         listeners:{
//              rowdblclick:function(grid, rowIndex, e){
//                 backup_edit_button.fireEvent('click',backup_edit_button);
//             }
//         }
    });

return backup_grid;
}

function call_vm_backupNow (node,node_id, action){

    params="vm_id="+node.attributes.id;
    url="/backup/backup_policy_count?"+params;     

    Ext.MessageBox.confirm(_("确认"),_("确定想要备份 (" + node.attributes.text + ")虚拟机吗?"),function(id){
        if(id=='yes'){
            var ajaxReq=ajaxRequest(url,0,"GET",true);
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    
                    if(response.success){                
                        if (response.policy_count == "0")
                        { 
                            Ext.MessageBox.alert("失败","没有与此虚拟机相关的备份策略，请在服务器池设置备份策略");          
                        }     
                        else if (response.policy_count == "1")
                        {   
                            params2="vm_id="+node.attributes.id+"&config_id="+ response.first_backup_id;
                            url2="/backup/backupVMNow?"+params2;  
                                
                            var ajaxReq=ajaxRequest(url2,0,"GET",true);
                            ajaxReq.request({
                                success: function(xhr) {
                                    var response=Ext.util.JSON.decode(xhr.responseText);
                                    
                                    if(response.success){   
                                                    
                                        //closeWindow();
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
                        else
                        {   
                            showWindow(_("立即备份"),540,450, vmBackupNowUI(node,node.attributes.id, action));
                            
                        }
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
function vmBackupNowUI(node,node_id, action){

    
    backup_grid= SP_Backup_Grid(node)    

    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('确定'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                if(!backup_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert("错误","请从列表中选择一个记录");
                    return false;
                }
                var edit_rec=backup_grid.getSelectionModel().getSelected();
                var backupsetup_id=edit_rec.get('backupsetup_id');
                

                params="vm_id="+node_id+"&config_id="+ backupsetup_id;
                url="/backup/backupVMNow?"+params;     
                
    
                var ajaxReq=ajaxRequest(url,0,"GET",true);
                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        //alert(response)
                        if(response.success){
                            backup_grid.getStore().load();
                            closeWindow();
                            //Ext.MessageBox.alert("Sucess",response.msg);
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
    })

    var button_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                
                //w.close();
                closeWindow();
                
            }
        }
    });

    var backupnow_desc_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250"> 请从下面选择一个备份策略用于备份.<br/ <br/></div>'
    });


    var tlabel_bcakupnow=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg"></div>'
    });

     var backupnow_panel=new Ext.Panel({
        id:"backupnow_panel",
        //title:'backup Setup',
        layout:"form",
        width:525,
        height:380,
        frame:false,
        labelWidth:130,
        border:0,
        cls: 'whitebackground',
        bodyStyle:'padding:5px 5px 5px 5px',
        items: [ backup_grid],
        tbar: [tlabel_bcakupnow],
        bbar:[{xtype: 'tbfill'},button_ok, button_cancel]
    });

    var backupnow_details_panel=new Ext.Panel({
        id:"backupnow_details",
        layout:"form",
        width:530,
        //cls: 'whitebackground paneltopborder',
        height:420,
        frame:false,       
        labelWidth:130,       
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[backupnow_desc_label, backupnow_panel]
    });

    return backupnow_details_panel;

 


}
function spBackupTaskUI(action,node,group_id,windid){

    var backup_desc_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250"> 在这里，你可以定义一个或多个备份策略。每个策略定义了不同选项，进度和要备份的虚拟机. <br/></div>'
    });


var backup_new_button=new Ext.Button({
        id: 'backup_new',
        text: '新建',
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {                
                backupPanel = SPBackupConfigSettings(backup_grid, node,group_id, 'NEW', null);
                showWindow(_("为服务器池创建备份策略" + node.text), 640, 507, backupPanel );
                
                 var month_checkBoxgroup =backupPanel.findById('month_checkBoxgroup'); 
                 hideField(month_checkBoxgroup);

                //var Managed_Location_textbox =backupPanel.findById('Managed_Location'); 
                //showField(Managed_Location_textbox);
                
                var RemoteServerName =backupPanel.findById('Remote_server'); 
                hideField(RemoteServerName);

                var User_Name_textbox =backupPanel.findById('User_Name'); 
                hideField(User_Name_textbox);
                
                var Password_textbox =backupPanel.findById('Password'); 
                hideField(Password_textbox);

                var ssh_port_textbox =backupPanel.findById('ssh_port'); 
                hideField(ssh_port_textbox);
                
                var usekey_checkBox =backupPanel.findById('usekey'); 
                hideField(usekey_checkBox);

                var Location_textbox =backupPanel.findById('Location'); 
                //hideField(Remote_Location_textbox);
                
                var TestConnect_button =backupPanel.findById('testConnect'); 
                 TestConnect_button.hide();

//                     showField(Managed_Location_textbox);
//                     hideField(RemoteServerName);
//                     hideField(User_Name_textbox);
//                     hideField(Password_textbox);
//                     hideField(ssh_port_textbox);
//                     hideField(usekey_checkBox);
//                     hideField(Remote_Location_textbox);
                    //hideField(TestConnect_button);
                   
                

            }
        }
    });

    var backup_remove_button=new Ext.Button({
        id: 'backup_remove',
        text: '移除',
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(!backup_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert("错误","请从列表选择一个记录");
                    return false;
                }
                var edit_rec=backup_grid.getSelectionModel().getSelected();

                var backupsetup_id= edit_rec.get('backupsetup_id');
                var taskname=edit_rec.get('taskname');
                var url='backup/delete_backuprecord?backupsetup_id='+backupsetup_id+ '&group_id='+group_id;
                
                Ext.MessageBox.confirm("确认","确定要移除 "+taskname+"备份策略吗?", function (id){
                    if(id=='yes'){
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    backup_grid.getStore().load();
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

    var backup_edit_button= new Ext.Button({
        id: 'backup_edit',
        text: '编辑',
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(!backup_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert("错误","请从列表选择一个记录");
                    return false;
                }
                var edit_rec=backup_grid.getSelectionModel().getSelected();
                var backupsetup_id=edit_rec.get('backupsetup_id');
                var url="/backup/get_backupsetup_details?backupsetup_id="+backupsetup_id;
                var ajaxReq=ajaxRequest(url,0,"POST",true);


                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);

                        if(response.success){
                            var backup_details = response.backupsetup_details[0];
                            backupPanel = SPBackupConfigSettings(backup_grid, node,group_id, 'EDIT',backup_details)

                            showWindow(_("编辑服务器池的备份策略 " + node.text), 640, 507,backupPanel );

                            var scheduleType_combo =backupPanel.findById('scheduleType_combo'); 
                            
                            var hourCombo =backupPanel.findById('hourCombo');
                            var week_checkBoxgroup =backupPanel.findById('week_checkBoxgroup');                
                            var month_checkBoxgroup =backupPanel.findById('month_checkBoxgroup'); 
                            var hr_label = backupPanel.findById('hr_label');
                            var hr_panel = backupPanel.findById('hr_panel');
                            var time_label = backupPanel.findById('time_label');
                            var Minute_Combo = backupPanel.findById('Minute_Combo');
                            var min_label = backupPanel.findById('min_label');
                            switch (scheduleType_combo.getValue()) {
                                case "Hourly":
//                                     HourCombo.disable();
//                                     Week_checkBoxgroup.disable();
//                                     Month_checkBoxgroup.disable();
                                    //hr_label.hide();
                                    //hideField(hr_panel);
                                    hr_panel.hide();
                                    hideField(hourCombo);
                                    hideField(week_checkBoxgroup);
                                    hideField(month_checkBoxgroup);
                
                                    break;
                                case "Daily":
                                    hr_label.show();
                                    hr_panel.show();
                                    showField(hourCombo);
                                    hideField(week_checkBoxgroup);
                                    hideField(month_checkBoxgroup);
                                    break;
                                case "Weekly":
                                    hr_label.show();
                                    hr_panel.show();
                                    scheduleType_combo.setValue("Monthly")
                                    scheduleType_combo.setValue("Weekly")
                                    showField(hourCombo);
                                    showField(week_checkBoxgroup);
                                    hideField(month_checkBoxgroup);
                                    break;
                                case "Monthly":
                                    hr_label.show();
                                    hr_panel.show();
                                    showField(hourCombo);
                                    hideField(week_checkBoxgroup);
                                    showField(month_checkBoxgroup);
                                    break;
                                case "Manual":
                                    hr_label.hide();
                                    hideField(hourCombo);
                                    hr_panel.hide();
                                    hideField(week_checkBoxgroup);
                                    hideField(month_checkBoxgroup);
                                    time_label.hide();
                                    hideField(Minute_Combo);
                                    min_label.hide();
                                    break;
                            }




                var Managed_Location_textbox =backupPanel.findById('Managed_Location'); 
                
                
                var RemoteServerName =backupPanel.findById('Remote_server'); 
                

                var User_Name_textbox =backupPanel.findById('User_Name'); 
                
                
                var Password_textbox =backupPanel.findById('Password'); 
               

                var ssh_port_textbox =backupPanel.findById('ssh_port'); 
                
                
                var usekey_checkBox =backupPanel.findById('usekey'); 
               

                var Location_textbox =backupPanel.findById('Location'); 
                
                
                var TestConnect_button =backupPanel.findById('testConnect'); 
                //var RemoteServer_radio =backupPanel.findById('remote_server'); 
                 
                //var ManagedServer_radio =backupPanel.findById('managed_server'); 
                var Remote_Managed_combo =backupPanel.findById('Remote_Managed_combo'); 
                 
                
                Remote_Managed_combo.setValue('Remote Server');
                
                if (backup_details.is_remote)
                {
                    //RemoteServer_radio.setValue(false);
                    //ManagedServer_radio.setValue(false);
                    //RemoteServer_radio.setValue(true);
                    Remote_Managed_combo.setValue('Remote Server');
                    //Managed_Location_textbox.disable();
                    RemoteServerName.setValue(backup_details.backup_server_details.server);
                    User_Name_textbox.setValue(backup_details.backup_server_details.username);
                    Password_textbox.setValue(backup_details.backup_server_details.password);
                    ssh_port_textbox.setValue(backup_details.backup_server_details.ssh_port);
                    usekey_checkBox.setValue(backup_details.backup_server_details.use_key);
                    //Remote_Location_textbox.setValue(config_setting.backup_destination);
                }
                else
                {
                    Remote_Managed_combo.setValue('Managed Server');
                    //RemoteServer_radio.setValue(false);
                    //ManagedServer_radio.setValue(true);
                    //Managed_Location_textbox.setValue(backup_details.backup_destination);
                    //ManagedServer_combo.setValue(config_setting.backup_server_details.);
                    hideField(RemoteServerName);
                    hideField(User_Name_textbox);
                    hideField(Password_textbox);
                    hideField(ssh_port_textbox);
                    hideField(usekey_checkBox);
//                    hideField(Remote_Location_textbox);
                    //hideField(TestConnect_button);
                    TestConnect_button.hide();
                    
    
                }
                
                Location_textbox.setValue(backup_details.backup_destination);
                            

                

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

    var backup_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var title_edit = new Ext.form.TextField();

    var backup_columnModel = new Ext.grid.ColumnModel([
    {
        header: "Site ID",
        width: 50,
        dataIndex: 'backupsetup_id',
        menuDisabled: false,
        hidden:true,
        editor: title_edit
    },
    {
        header: "名称",
        width: 150,
        dataIndex: 'taskname',
        sortable:true,
        editor: title_edit,
        id:'taskname'

    },
    {
        header: "备份类型",
        width: 100,
        dataIndex: 'backup_type',
        sortable:true,
        editor: title_edit,
        id:'backup_type'

    },
//     {
//         header: "Location",
//         width: 200,
//         dataIndex: 'location',
//         sortable:true,
//         editor: title_edit,
//         id:'location'
// 
//     },
//     {
//         header: "Number of Runs",
//         width: 100,
//         dataIndex: 'num_runs',
//         sortable:true,
//         editor: title_edit,
//         id:'num_runs'
// 
//     },
    {
        header: "时间表",
        width: 360,
        dataIndex: 'next_schedule',
        sortable:true,
        editor: title_edit,
        id:'next_schedule'

    },
    ]);
    
    node_id = node.attributes.id;
    node_type = node.attributes.nodetype;
     var backup_store =new Ext.data.JsonStore({
            url: 'backup/get_backupsetupinfo?node_id=' +node_id+ '&node_type='+ node_type,
            root: 'rows',
            fields: [ 'backupsetup_id','taskname','backup_type', 'location', 'num_runs', 'next_schedule'  ],
            successProperty:'success',
            listeners:{
                loadexception:function(obj,opts,res,e){
                    var store_response=Ext.util.JSON.decode(res.responseText);
                    Ext.MessageBox.alert("Error2",store_response.msg);
                }

            }
        });

    backup_store.load();


    var backup_grid=new Ext.grid.GridPanel({
        store: backup_store,
        stripeRows: true,
        colModel:backup_columnModel,
        frame:false,
        selModel:backup_selmodel,
        height:360,
        width:'100%',
        //autoExpandColumn:3,
        //autoExpandMin:100,
        enableHdMenu:false,
        loadMask:true,
        id:'backup_grid',
        layout:'fit',
       tbar:[{ xtype: 'tbfill'}, backup_new_button,'-', backup_edit_button,'-', backup_remove_button, 
//'-',
//             'Search (by Name): ',new Ext.form.TextField({
//             fieldLabel: 'Search',
//             name: 'search',
//             id: 'search',
//             allowBlank:true,
//             enableKeyEvents:true,
//             listeners: {
//                 keyup: function(field) {
//                     backup_grid.getStore().filter('taskname', field.getValue(), false, false);
//                 }
//             }
// 
//         })
        ],
        listeners:{
             rowdblclick:function(grid, rowIndex, e){
                backup_edit_button.fireEvent('click',backup_edit_button);
            }
        }
    });


     var backuppanel=new Ext.Panel({
        id:"backuppanel",
        //title:'backup Setup',
        layout:"form",
        width:635,
        height:435,
        frame:false,
        labelWidth:130,
        border:0,
        cls: 'whitebackground',
        //bodyStyle:'padding:5px 5px 5px 5px',
        items: [backup_desc_label,backup_grid],
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('关闭'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {closeWindow(windid);}
                    }
            })
        ]
    });

    return backuppanel;
}


function SPBackupConfigSettings (backup_grid,node, group_id, mode, config_setting){


     count=0;

    // tree panel for left side tree view
    var treePanel= new Ext.tree.TreePanel({
        region:'west',
        width:180,
        rootVisible:false,
        border: false,
        lines : false,
        id:'treePanel',
        cls:'leftnav_treePanel',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        listeners: {
            click: function(item) {
                
                count=0;
                var id=item.id;
                //alert (id.substr(4,id.length));
                process_panel2(card_panel,treePanel,id.substr(4,id.length));
                //process_panel(card_panel,treePanel,1);

                if(scheduleType_combo.getValue() == "Manual") {
                    hr_label.hide();
                    hideField(HourCombo);
                    hr_panel.hide();
                    hideField(Week_checkBoxgroup);
                    hideField(Month_checkBoxgroup);
                    time_label.hide();
                    hideField(Minute_Combo);
                    min_label.hide();
                }
            }
        }
    });

    // root node of tree view
    var rootNode = new Ext.tree.TreeNode({
        text    : 'Root Node',
        draggable: false,
        id      : 'rootnode',
        listeners: {
            expand : function(btn) {
                treePanel.getNodeById("node0").select();
            }
        }
    });
    var generalNode = new Ext.tree.TreeNode({
        text: _('常规'),
        draggable: false,
        id: "node0",
        icon:'icons/vm-general.png',
        nodeid: "general",
        leaf:false,
        allowDrop : false
       // cls:"labelcolor"
    });

    
    var scheduleNode = new Ext.tree.TreeNode({
        text: _('时间表'),
        draggable: false,
        id: "node2",
        nodeid: "schedule",
        icon:'icons/templates-parameters.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

    var storageNode = new Ext.tree.TreeNode({
        text: _('备份位置'),
        draggable: false,
        id: "node1",
        nodeid: "storage",
        icon:'icons/vm-storage.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

    var excludeVMNode = new Ext.tree.TreeNode({
        text: _('虚拟机'),
        draggable: false,
        id: "node3",
        nodeid: "ExcludedVMs",
        icon:'icons/vm-misc.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

    var advanceNode = new Ext.tree.TreeNode({
        text: _('高级选项'),
        draggable: false,
        id: "node4",
        nodeid: "advance_options",
        icon:'icons/vm-boot-param.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
    
    var leftnavhdg="";
    //var vmmatch = action.match("vm")
    //if(vmmatch)
    //leftnavhdg="Configure Backup ";
    //else
    //    leftnavhdg=_("Template Settings");
    var treeheading=new Ext.form.Label({
        html:'<br/><center><font size="2">'+leftnavhdg+'</font></center><br/>'
    });

    var side_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:180,
        height:588,
        id:'side_panel',
        cls:'westPanel',
        items:[treeheading,treePanel]

    });
  
var button_prev=new Ext.Button({
        id: 'move-prev',
        //text: _('Prev'),
        disabled: true,
        icon:'icons/2left.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                process_panel2(card_panel,treePanel,-1);
            }
        }
    });
    var button_next=new Ext.Button({
        id: 'move-next',
        //text: _('Next'),
        icon:'icons/2right.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                process_panel2(card_panel,treePanel,1);
            }
        }
    });

 var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('确定'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                if(!SPTaskName.getValue())
                {
                    Ext.MessageBox.alert(_("错误"),_("请输入常规选项下的任务名称"));
                    return false;
                }
                if(SPTaskName.getValue()){                      
                    //var validate=false;
                    var TaskName=SPTaskName.getValue();
                    var  x = TaskName;
                    var invalid_chars=new Array('!','@','#','$','%','^','&','(',')','|','?','>','<','[',']','{','}','*','"',',','.','"',';',':','?','/','\'');
                    for(var i=0;i<x.length;i++){
                        for(var j=0;j<=invalid_chars.length;j++){
                            if(x.charAt(i) == invalid_chars[j]){
                                Ext.MessageBox.alert(_("错误"),_("任务名称不能包含下面特殊字符.<br>")+
                                "space,comma,single quote,double quotes,'!','@','#',<br>'$','%','^','&','(',')','|','?','>','<','[',']','{','}','*','.',';',':','?','/'");
                                return false;
                            }
                        }
                    }
                }   
     
           

            var general_object=new Object();
            general_object.taskname=SPTaskName.getValue();           
            
            if (coldBackup_radio.getValue() == true)
            {
                general_object.coldBackup= "COLD";
                
            }
            else
            {                
                general_object.coldBackup= "HOT"
            }
            //general_object.copyRaw=copyRaw_radio.getValue();
            //
            if (copyRaw_radio.getValue() == true)
                general_object.copyRaw="RAW"
            else
                general_object.copyRaw="CONTENT"

            general_object.transferMethod= transferMethod_combo.getValue();
            general_object.full_backup= full_backup_radio.getValue();
            general_object.use_tar = tar_checkBox.getValue();
            general_object.compression_type= compression_combo.getValue();
            

            var transferMethod_options_stat="{";
            for(var i=0;i<transferMethod_option_store.getCount();i++){ 
            
                transferMethod_options_stat+="'"+transferMethod_option_store.getAt(i).get("attribute")+"':";
                //option_stat+=", 'value':";
                transferMethod_options_stat+="'"+transferMethod_option_store.getAt(i).get("value")+"',";
                //option_stat+="},";
                
            }
            transferMethod_options_stat+="}";
            var transferMethod_options_stat_jdata= eval("("+transferMethod_options_stat+")");

//             var file_backup_option_stat="{";
//             for(var i=0;i<file_backup_advance_option_store.getCount();i++){ 
//             
//                 file_backup_option_stat+="'"+file_backup_advance_option_store.getAt(i).get("attribute")+"':";
//                 //option_stat+=", 'value':";
//                 file_backup_option_stat+="'"+file_backup_advance_option_store.getAt(i).get("value")+"',";
//                 //option_stat+="},";
//                 
//             }
//             file_backup_option_stat+="}";
//             var file_backup_option_jdata= eval("("+file_backup_option_stat+")");           
// 
//             general_object.file_backup_option_stat= file_backup_option_jdata;
             general_object.transferMethod_options= transferMethod_options_stat_jdata;


            var schedule_object=new Object();
            schedule_object.scheduleType= scheduleType_combo.getValue();
            schedule_object.Hour= HourCombo.getValue();
            schedule_object.Minute=Minute_Combo.getValue();



            var weekday_stat="";
            for(var i=0;i<7;i++){
                if (week_array[i].getValue())
                {     
                //weekday_stat+="{";
                //weekday_stat+="'id':";
                    if(weekday_stat != "")
                    {
                        weekday_stat+=",";
                        //weekday_stat+=week_array[i].getName(); 
                        weekday_stat+=i;
                    } 
                    else{
                        //weekday_stat+=week_array[i].getName(); 
                        weekday_stat+=i;
                    }
              
                    
                }
            }

        var monthday_stat="";
            for(var i=1;i<=31;i++){
                if (month_array[i].getValue())
                {     
                
                    if(monthday_stat != "")
                    {
                        monthday_stat+=",";
                        
                        monthday_stat+=i;
                    } 
                    else{
                        
                        monthday_stat+=i;
                    }
              
                    
                }
            }
            
            //Validations
            if(scheduleType_combo.getValue() == "Weekly") {
                if(weekday_stat == "") {
                    Ext.MessageBox.alert(_("信息"),_("请选择周的一天"));
                    return;
                }
            }
            else if(scheduleType_combo.getValue() == "Monthly") {
                if(monthday_stat == "") {
                    Ext.MessageBox.alert(_("信息"),_("请选择月的一天"));
                    return;
                }
            }

//             var weekday_stat="dict(";
//             for(var i=1;i<=7;i++){
//                 if(week_array[i].getValue())
//                 {
//                     
//                     //weekday_stat+="";
//                     weekday_stat+=week_array[i].getName();
//                     weekday_stat+="= "; 
//                     weekday_stat+= "True";                 
//                     weekday_stat+=",";
//                 }
//             }
//             weekday_stat+=")";

            schedule_object.weekday_stat = weekday_stat;
            schedule_object.monthday_stat = monthday_stat;
            schedule_object.Week= "Friday";//Week_checkBoxgroup.getValue();
            schedule_object.Month= "30";//Month_checkBoxgroup.getValue();
            if(reten_finite_day_radio.checked == true) {
                schedule_object.Purge= Purge_TextBox.getValue();
            } else {
                schedule_object.Purge = "";
            }

            var storage_object=new Object();
            //storage_object.RemoteServer= RemoteServer_radio.getValue();
            if(Remote_Managed_combo.getValue() == 'Remote Server')
            {
                storage_object.RemoteServer = true;
            }
            else
            {
            storage_object.RemoteServer = false;
            }
            //storage_object.ManagedServer= ManagedServer_combo.getValue();
            storage_object.RemoteServerName=RemoteServerName.getValue();
            storage_object.User_Name= User_Name_textbox.getValue();
            storage_object.password= Password_textbox.getValue();
            storage_object.ssh_port= ssh_port_textbox.getValue();
            storage_object.use_key = usekey_checkBox.getValue();

            
            storage_object.Location= Location_textbox.getValue();


            var excludeVM_object=new Object();
            var vm_stat="[";
            for(var i=0;i<vm_list_store.getCount();i++){
               /* var allow_backup_str = "False";  
                if (vm_list_store.getAt(i).get("allow_backup"))
                {
                    allow_backup_str = "True";  
                }   */      
                vm_stat+="{";
                vm_stat+="'id':";
                vm_stat+="'"+vm_list_store.getAt(i).get("id")+"'";
                vm_stat+=", 'allow_backup':";
                vm_stat+="'"+vm_list_store.getAt(i).get("allow_backup")+"'";
                vm_stat+="},";
            }
            vm_stat+="]";
            
            var vm_jdata= eval("("+vm_stat+")");
            
            excludeVM_object.vm_stat = vm_jdata;
            excludeVM_object.includeAll_VM = includeAll_radio.getValue();
           
        
            
            
            var jsondata= json_data(general_object, schedule_object, storage_object, excludeVM_object);

            params="group_id="+group_id+"&config="+jsondata;
            url="/backup/StoreBackup_ConfigRecord?"+params;       
            if(mode=='EDIT'){
                params="group_id="+group_id+"&config="+jsondata+"&backupsetup_id="+config_setting.backupsetup_id;

                url="/backup/updateSPTaskRecord?"+params;       
            }
   

            
//             url="/spTaskDetails?group_id="+group_id+"&taskname="+SPTaskName.getValue()+"&transferMethod="+transferMethod_combo.getValue()+"&location="+Location.getValue()+"&User_Name="+User_Name.getValue()+"&password="+Password_text.getValue()+"&scheduleType="+scheduleType_combo.getValue()+"&time="+HourCombo.getValue()+"&Weekday="+Weekday+ "&Monthday="+Monthday+ "&purgetime="+ Purge.getValue();
            

            var ajaxReq=ajaxRequest(url,0,"GET",true);
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    
                    if(response.success){
                        backup_grid.getStore().load();
                        closeWindow();
                        //Ext.MessageBox.alert("Sucess",response.msg);
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
 var button_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {                
                
                closeWindow();
                
            }
        }
    });

var hr_label=new Ext.form.Label({
    id: 'hr_label',
    text: "Hr"
    //    html:'<div class="backgroundcolor" width="20"> Hr</div>'
        
    });

var HourCombo=new Ext.form.ComboBox({
        //anchor:'90%',
        width:35,
        id: 'hourCombo',
        editable: false,
        fieldLabel:"Hr",   
        hideLabel: true,
        allowBlank:false,
        triggerAction:'all',
        //ctCls:ctCls,
        //labelStyle: 'width:'+10+'px;',
        store:[['01', '01'],
                ['02', '02'],
                ['03', '03'],
                ['04', '04'],
                ['05', '05'],
                ['06', '06'],
                ['07', '07'],
                ['08', '08'],
                ['09', '09'],
                ['10', '10'],
                ['11', '11'],
                ['12', '12'],
                ['13', '13'],
                ['14', '14'],
                ['15', '15'],
                ['16', '16'],
                ['17', '17'],
                ['18', '18'],
                ['19', '19'],
                ['20', '20'],
                ['21', '21'],
                ['22', '22'],
                ['23', '23'],
                ['24', '24'],
               ],
        forceSelection: true,
        mode:'local',
        value:'23',
        listeners: {

                // 'select' will be fired as soon as an item in the ComboBox is selected with mouse, keyboard.
                select: function(combo, record, index){
                    
                    
                }
        }

    });

var min_label=new Ext.form.Label({
    id: 'min_label',
    text: "Min"
    //    html:'<div class="backgroundcolor" width="20"> Min</div>'
        
    });

var Minutestore = new Ext.data.SimpleStore({
        fields: ['dataFieldName', 'displayFieldName'],
        data: [['00', '00'], ['01', '01'], ['02', '02'], ['03', '03'], ['04', '04'],['05', '05'],['06', '06'],['07', '07'], ['08', '08'], ['09', '09'], ['10', '10'],['11', '11'], ['12', '12'], ['13', '13'], ['14', '14'],['15', '15'],['16', '16'],['17', '17'], ['18', '18'], ['19', '19'], ['20','20'], ['21', '21'], ['22', '22'], ['23', '23'], ['24', '24'], ['25', '25'], ['26', '26'], ['27', '27'], ['28', '28'], ['29', '29'], ['30', '30'], ['31', '31'], ['32', '32'], ['33', '33'], ['34', '34'],['35', '35'],['36', '36'],['37', '37'], ['38', '38'], ['39', '39'], ['40', '40'], ['41', '41'], ['42', '42'], ['43', '43'], ['44', '44'],['45', '45'],['46', '46'],['47', '47'], ['48', '48'], ['49', '49'], ['50', '50'], ['51', '51'], ['52', '52'], ['53', '53'], ['54', '54'],['55', '55'],['56', '56'],['57', '57'], ['58', '58'], ['59', '59']]
        
    });

var Minute_Combo=new Ext.form.ComboBox({
        id: 'Minute_Combo',
        //anchor:'90%',
        width:35,
        //minListWidth: 90,
        fieldLabel:"Min",
        hideLabel: true,
        allowBlank:false,
        triggerAction:'all',
        editable: false,
        labelStyle: 'width:'+10+'px;',
        store:Minutestore, 
        displayField: 'displayFieldName',   // what the user sees in the popup
        valueField: 'dataFieldName',        // what is passed to the 'change' event
             
        forceSelection: true,
        mode:'local',
        value: '00',
        disabled: false,
        listeners: {
           
                select: function(combo, record, index){                    
                    //combo2.show();
//                     if (combo.getValue() == 'Weekly')
//                         Week_combo.enable();
//                     else
//                         Week_combo.disable(); 
//                     HourCombo.setVisible(true);
                    //combo2.hideLabel = false
                }
        }

    });





var week_array = [];

for(var i=0; i<7; i++)
{
    label_str = "";
//     if(i ==1)
//          label_str = "Monday";
    switch (i) {
    case 0:
       label_str = "周一";
        break;
    case 1:
       label_str = "周二";
        break;
    case 2:
        label_str = "周三";
        break;
    case 3:
        label_str = "周四";
        break;
    case 4:
        label_str = "周五";
        break;
    case 5:
        label_str = "周六";
        break;
    case 6:
        label_str = "周日";
        break;
    }
    

    
    
    var weekday_checkBox=  new Ext.form.Checkbox({
        name: 'WDay'+i,
        checked: false,
        boxLabel: label_str,
        width : 100
    });
    if (i == 6)
    {
        weekday_checkBox.setValue(true);
    }
        week_array[i]= weekday_checkBox;    

}






var Week_checkBoxgroup = new Ext.form.CheckboxGroup({
    id:'week_checkBoxgroup',
    xtype: 'checkboxgroup',
    fieldLabel: "周的一天",
    itemCls: 'x-check-group-alt',
    width:"100%",

    //disabled: true,
    // Put all controls in a single column with width 100%
    columns: 2,
    items:
[
            week_array[0],
            week_array[1],
            week_array[2],
            week_array[3],
            week_array[4],  
            week_array[5],
            week_array[6],  
           


    ]
    });


var month_array = [];

for(var i=1; i<=31; i++)
{
    label_str = ""+ i;    

    var monthday_checkBox=  new Ext.form.Checkbox({
        name: 'MDay'+i,
        checked: false,
        boxLabel: label_str,
        width: 50
    });
    if (i ==31)
    {
        monthday_checkBox.setValue(true);
    }
        month_array[i]= monthday_checkBox;    

}

var Month_checkBoxgroup = new Ext.form.CheckboxGroup({
    id:'month_checkBoxgroup',
    xtype: 'checkboxgroup',
    fieldLabel: "月的一天",
    itemCls: 'x-check-group-alt',
    disabled: true,
    // Put all controls in a single column with width 100%
    columns: 5,
    items: [
        month_array[1],
        month_array[2],
        month_array[3],
        month_array[4],
        month_array[5],
        month_array[6],
        month_array[7],
        month_array[8],
        month_array[9],
        month_array[10],
        month_array[11],
        month_array[12],
        month_array[13],
        month_array[14],
        month_array[15],
        month_array[16],
        month_array[17],
        month_array[18],
        month_array[19],
        month_array[20],
        month_array[21],
        month_array[22],
        month_array[23],
        month_array[24],
        month_array[25],
        month_array[26],
        month_array[27],
        month_array[28],
        month_array[29],
        month_array[30],
        month_array[31],
            

    ]
    });

var MonthDatestore = new Ext.data.SimpleStore({
        fields: ['dataFieldName', 'displayFieldName'],
        data: [['1', '1'], ['2', '2'], ['3', '3'], ['4', '4'],['5', '5'],['6', '6'],['7', '7'], ['8', '8'], ['9', '9'], ['10', '10'],['11', '11'], ['12', '12'], ['13', '13'], ['14', '14'],['15', '15'],['16', '16'],['17', '17'], ['18', '18'], ['19', '19'], ['20','20'], ['21', '21'], ['22', '22'], ['23', '23'], ['24', '24'], ['25', '25'], ['26', '26'], ['27', '27'], ['28', '28'], ['29', '29'], ['30', '30']]
        
    });



 var scheduleType_combo=new Ext.form.ComboBox({
        //anchor:'90%',
        id: 'scheduleType_combo',        
        width:120,
        minListWidth: 90,
        fieldLabel:"频率",
        allowBlank:false,
        triggerAction:'all',
        editable: false,
        store:[//['Hourly',_('Hourly')],
                ['Daily',_('Daily')],
                ['Weekly',_('Weekly')],
                ['Monthly',_('Monthly')],
                ['Manual',_('Manual')]
               ],
        forceSelection: true,
        mode:'local',
        value: 'Weekly',
        listeners: {
   
                select: function(combo, record, index){
                    
                    //combo2.show();
                    if (combo.getValue() == 'Hourly')
                    {
                        time_label.show();
                        showField(Minute_Combo);
                        min_label.show();

                        hr_label.hide();
                        hideField(HourCombo);
                        hr_panel.hide();
                        //hideField(hr_panel);
                        hideField(Week_checkBoxgroup);
                        hideField(Month_checkBoxgroup);
                    }
                    if (combo.getValue() == 'Daily')
                    {
                        time_label.show();
                        showField(Minute_Combo);
                        min_label.show();

                        hr_label.show();
                        hr_panel.show();
                        showField(HourCombo);                        
                        hideField(Week_checkBoxgroup);
                        hideField(Month_checkBoxgroup);
                        
                    }
                    if (combo.getValue() == 'Weekly')
                    {
                        time_label.show();
                        showField(Minute_Combo);
                        min_label.show();

                        hr_label.show();
                        hr_panel.show();
                        showField(HourCombo);
                        showField(Week_checkBoxgroup);
                        hideField(Month_checkBoxgroup);
                    }
                    else if(combo.getValue() == 'Monthly')
                    {
                        time_label.show();
                        showField(Minute_Combo);
                        min_label.show();

                        hr_label.show();
                        hr_panel.show();
                        showField(HourCombo);
                        hideField(Week_checkBoxgroup);
                        showField(Month_checkBoxgroup);           
                    } else if (combo.getValue() == 'Manual')
                    {
                        hr_label.hide();
                        hideField(HourCombo);
                        hr_panel.hide();
                        hideField(Week_checkBoxgroup);
                        hideField(Month_checkBoxgroup);
                        
                        time_label.hide();
                        hideField(Minute_Combo);
                        min_label.hide();
                    }

                    
                }
        }

    });





var time_label=new Ext.form.Label({
        id: 'time_label',
        text: "时间:  "
        //html:'<div class="backgroundcolor" width="20"> <br/> Time:</div>'
    });
var Blank_label=new Ext.form.Label({
        //text: " sss",
        html:'<div class="backgroundcolor" width="20"> <br/></div>'
    });

var Dummy_radio=  new Ext.form.Radio({
        boxLabel: '', name: 'dummy_radio',  id: 'dummy',checked: true, hideLabel: true, hidden: true});


/*
var TimeGroup = {
        xtype: 'fieldset',
        border: false,
        id: 'TimeGroup',
        //title: 'TimeGroup',
        //labelWidth: 100,
//         columns: 2,
        autoHeight: true,
        items: [ 
        {            
            layout:'column',
            border:false,
            //labelWidth: 100,
            items:[ 
            {
                columnWidth:.25,
                border:false,
                width: 90,
                layout: 'form',
                x:0,
                //labelWidth: 30,
                items: [time_label]
             },{
                columnWidth:.25,
                border:false,
                width: 100,
                layout: 'form',
                labelWidth: 30,                
                items: [HourCombo]
             },{
                columnWidth:.25,
                border:false,
                width: 100,
                layout: 'form',
                labelWidth: 30,
                items: [Minute_Combo]
//             
            }]                
                     
        }]
    } 
   */

//var hr_padding_str= '5px 0px 0px 0px';
    var hr_panel= new Ext.Panel({
    
            //columnWidth:.25,
            id: 'hr_panel',
            border:false,
            width: 25,
            layout: 'form',
            layoutConfig: {
                labelSeparator:''                    
            },
            bodyStyle:'padding:5px 0px 0px 0px',
            labelWidth: 25,
            items: [hr_label]
    });

var scheduleType_combo_Group = {
        xtype: 'fieldset',
        border: false,
        id: 'scheduleType_combo_Group',        
        autoHeight: true,
        labelWidth: 110,
        items: [ 
        {            
            layout:'column',
            border:false,
            width: 400,
            //labelWidth: 100,
            items:[ 
            {
                columnWidth:1.0,
                border:false,
                width: 350,
                layout: 'form',
                //labelWidth: 30,
                items: [scheduleType_combo]
            
            }]                
                     
        },
        {            
            layout:'column',
            border:false,
            //labelWidth: 100,            
            items:[ 
            {
                columnWidth:.25,
                border:false,
                //width: 105,
                width: 115,
                layout: 'form',
                //labelWidth: 30,
                items: [time_label]
             },{
                columnWidth:.25,
                border:false,
                width: 60,
                layout: 'form',
                layoutConfig: {
                    labelSeparator:''                   
                },
                labelWidth: 25,
                items: [HourCombo]
//            },{
                //columnWidth:.25,
//                 border:false,
//                 width: 25,
//                 layout: 'form',
//                 layoutConfig: {
//                     labelSeparator:'',                    
//                 },
//                 bodyStyle:'padding:5px 0px 0px 0px',
//                 labelWidth: 25,
//                 items: [hr_label]
},
                hr_panel
             ,{
                columnWidth:.25,
                border:false,
                width: 60,
                layout: 'form',
                layoutConfig: {
                    labelSeparator:''                    
                },
                labelWidth: 25,
                items: [Minute_Combo]
            },{
                columnWidth:.25,
                border:false,
                width: 25,
                layout: 'form',
                layoutConfig: {
                    labelSeparator:''                    
                },
                labelWidth: 25,
                bodyStyle:'padding:5px 0px 0px 0px',
                items: [min_label]
//             
            }]                
                     
        },
        //TimeGroup,
        Week_checkBoxgroup,
        Month_checkBoxgroup,

        ]
    } 
   



   
    // Schedule Panel declaration

 var schedule_desc_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250"> 指定虚拟机的备份频率. <br/><br/></div>'
    });

var label_schedule=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("时间表")+'<br/></div>'
    });

    var tlabel_Schedule=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">时间表</div>'
    });



    var schedule_panel=new Ext.Panel({
        height:550,
        layout:"form",
        frame:false,       
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[scheduleType_combo_Group],
        tbar:[tlabel_Schedule],
        listeners: {
            add: function(this_p, component, index) {
//            showField(HourCombo);
             //hideField(Week_checkBoxgroup);
//             hideField(Month_checkBoxgroup);
            }
        }
    });



    var schedule_details_panel=new Ext.Panel({
        id:"panel2",
        layout:"form",
        width:100,
        //cls: 'whitebackground paneltopborder',
        height:550,
        frame:false,       
        labelWidth:130,       
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[schedule_panel]
    });



    // General Panel declaration

    var SPTaskName=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'spTask_name',
        width: 235,
        id: 'spTask_name',
        allowBlank:false

    });


var SPTaskNameGroup = {
        xtype: 'fieldset',      
        border: false,
        autoHeight: true,
        bodyStyle:'padding:5px 5px 0',
        layout:'column',
        items: [{
                width: 420,
                layout:'form',
                labelWidth: 60,
                border: false,
                items:[SPTaskName]}]
}


//         items:[
//             
//     

    var is_Remote_checkBox=  new Ext.form.Checkbox({

        name: '远程',
        checked: false,
        boxLabel: '远程存储位置',
        labelSeparator: '', 
        listeners: {
            check: function(this_checkbox, checked) {
                if(checked)
                {
                    //tarfile_used= true;
                }
                else
                {
                   //tarfile_used= false;
                }
            }

        }
    });

    var coldBackup_radio=  new Ext.form.Radio({
        boxLabel: '冷备份 (备份时虚拟机将要关闭)', name: 'rgcol', inputValue: 1, id: 'cold',checked: true, hideLabel: true});

    var coldBackup_label=new Ext.form.Label({
        text: "备份前虚拟机将要关闭"
        //html:'<div style="" class="boldlabelheading">'+_("General")+'<br/></div>'
    });


    var hotBackup_radio=  new Ext.form.Radio({
        boxLabel: '热备份(备份期间不影响虚拟机运行)', name: 'rgcol', inputValue: 2, id: 'hot', checked: false, hideLabel: true});

    var label_hot_backup_tip = new Ext.form.Label({
        html:'<table><tr><td width="100%"><i>提示: 热备份需要LVM。如果您没有LVM，可能导致最终的备份不一致.</i></td></tr></table>'
    });
   
var label_name =new Ext.form.Label({
        html:'<div style="" ><b>'+_("名称")+'</b><br/></div>'
    });

var label_value =new Ext.form.Label({
        html:'<div style="" ><b>'+_("值")+'</b><br/></div>'
    });

var label_checkbox =new Ext.form.Label({
        html:'<div style="" >'+_("")+'<br/></div>'
    });

var hot_name_textbox_array = [];
var hot_value_textbox_array = [];
var hot_option_checkbox = [];
for (var i=0; i<10; i++)
{
    hot_name_textbox_array[i] = new Ext.form.TextField({
        //fieldLabel: _('Purge for days'),
        hideLabel: true,
        name: 'Name'+i,
        width: 140,
        id: 'Name'+i,
        allowBlank:true,
        value: "Option"+i
    });

    hot_value_textbox_array[i] =new Ext.form.TextField({
        //fieldLabel: _('Purge for days'),
        hideLabel: true,
        name: 'Value'+i,
        width: 140,
        id: 'Value'+i,
        allowBlank:true,
        value: "value"+i
    });

    hot_option_checkbox[i] =new Ext.form.Checkbox({
        name: 'hot_option'+i,
        checked: true,
        hideLabel: true
        //boxLabel: label_str,
    });
}


for (var i=4; i<10; i++)
{
    hot_name_textbox_array[i].setValue("");
    hot_value_textbox_array[i].setValue("");
    hot_option_checkbox[i].setValue(false);
}




var Name_Value_Group = {
        xtype: 'fieldset',        
        //x:0,
        border:false,
//         columns: 2,
        autoHeight: true,
        items: [{            
            layout:'column',
            border: false,
            items:[
{
                columnWidth:.1,
                layout: 'form',
                border: false,
                //x:0,
                items: [ label_checkbox, hot_option_checkbox[0], hot_option_checkbox[1], hot_option_checkbox[2],  hot_option_checkbox[3], hot_option_checkbox[4], hot_option_checkbox[5]]
            },
{
                columnWidth:.45,
                layout: 'form',
                border: false,
                //x:0,
                items: [ label_name, hot_name_textbox_array[0], hot_name_textbox_array[1], hot_name_textbox_array[2], hot_name_textbox_array[3], hot_name_textbox_array[4], hot_name_textbox_array[5]]
            },{
                columnWidth:.45,
                layout: 'form',
                border: false,
                items: [label_value, hot_value_textbox_array[0], hot_value_textbox_array[1], hot_value_textbox_array[2], hot_value_textbox_array[3], hot_value_textbox_array[4], hot_value_textbox_array[5]],
                }]


            }]
        }


    var option_window=new Ext.Window({
                    title :'高级选项',
                    width :400,
                    height:400,
                    modal : true,
                    resizable : false
                });
      

    var hot_stat = "[";
  var button_save=new Ext.Button({
        name: 'save',
        id: 'save',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
            for (var i=0; i<10; i++)
            {
                if(hot_option_checkbox[i].getValue())
                {
                    if(hot_name_textbox_array[i].getValue() != "")
                    {
                        hot_stat+="{";
                        hot_stat+="'name':";
                        hot_stat+=hot_name_textbox_array[i].getValue();
                        hot_stat+=", 'value':";
                        hot_stat+=hot_value_textbox_array[i].getValue();
                        hot_stat+="},";
                    }
                
                } 
            }
            hot_stat+="]";            
            option_window.close();  
}
        }
});



//     // Setup the form panel
//     var hotBackupOption_Panel = new Ext.form.FormPanel({
//         region     : 'center',
//         //title      : 'Generic Form Panel',
//         //bodyStyle  : 'padding: 10px; background-color: #DFE8F6',
//         labelWidth : 100,
//         width      : 390,
//         height: 370,
//         //height:'100%',
//         items      : [
//             //rsync_options,
//             //cp_options,
//             Name_Value_Group
//             
//         ],
//         bbar:[
//         {
//             xtype: 'tbfill'
//         },button_save],
//     });
/*
    hot_url ='/backup/get_hot_options?group_id='+group_id; 
    if(mode=='EDIT'){                
            hot_url ='/backup/get_hot_options?group_id='+group_id+ "&backupsetup_id="+config_setting.backupsetup_id; 
    }
   

    var hot_advance_option_store = new Ext.data.JsonStore({
        url: hot_url,
        root: 'rows',
        fields: ['attribute','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }

    });
hot_advance_option_store.load();

    
    var hotBackupOption_button=new Ext.Button({
        id: 'hotBackupOption',
        text: _('Options'),
        fieldLabel: 'Advance options',  
        //icon:'icons/2right.png',
        //cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var label = "Hot Backup Option";
                var w=new Ext.Window({
                    title :'Advance Options ',
                    width :400,
                    height:380,
                    modal : true,
                    resizable : true
                });                
                w.add(AdvanceOptionPanel(group_id, w, hot_advance_option_store, label));
                w.show();
                
            }
        }
    });*/

    var hotBackup_label=new Ext.form.Label({
        text: "备份期间虚拟机保持正常运行"
        //html:'<div style="" class="boldlabelheading">'+_("General")+'<br/></div>'
    });


    var advance_label=new Ext.form.Label({
        text: "高级选项: "        
    });


    var backupType_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">选择其中的一个选项. 冷备份期间虚拟机将要关闭，而热备份期间则不影响虚拟机的运行. <br/></div>'
    });

    var BackupTypeGroup = {
        xtype: 'fieldset',
        //title: 'Backup Type:',
        border: false,
        autoHeight: true,
        //bodyStyle:'padding:5px 5px 0',
        items: [backupType_label, 
            {            
            layout:'column',
            border:false,
            items:[{
                columnWidth:.5,
                layout: 'form',
                border:false,
                items: [ coldBackup_radio]
                },{
                columnWidth:.5,
                layout: 'form',
                border:false,
                items: [ hotBackup_radio]
                }]
            },
            
            ]
           

    }

    



    var BackupType_radiogroup = new Ext.form.RadioGroup({
    id:'myGroup',
    xtype: 'radioxgroup',
    //fieldLabel: 'Backup Type',
    hideLabel: true,
    itemCls: 'x-check-group-alt',
    // Put all controls in a single column with width 100%
    columns: 2,
    items: [
        coldBackup_radio, 
        hotBackup_radio       
    ]
    });

    var cold_hot_group = {
        xtype: 'fieldset',
        //title: 'Backup Content:',
        autoHeight: true,
        border:false,
        //bodyStyle:'padding:5px 5px 0',
        items: [{            
            layout:'column',
            border:false,
            items:[{
                columnWidth:.5,
                layout: 'form',
                border:false,
                items: [ coldBackup_radio]
                },{
                columnWidth:.5,
                layout: 'form',
                border:false,
                items: [ hotBackup_radio]
                }]
        }]
    }

    var copyRaw_radio=  new Ext.form.Radio({
        boxLabel: '磁盘镜像备份(复制整个磁盘)', name: 'copytype_radio', inputValue: 2, id: 'copyRaw_radio', checked:true, hideLabel: true});

    var CopyRaw_label=new Ext.form.Label({
        text: "Store the disk byte by byte"
        //html:'<div style="" class="boldlabelheading">'+_("General")+'<br/></div>'
    });

    var CopyRawGroup = {
        xtype: 'fieldset',
        //title: 'hotBackupGroup',
        
        x:0,
        border:false,
//         columns: 2,
        autoHeight: true,
        items: [
            copyRaw_radio,
            CopyRaw_label]
        }

    var copyContent_radio=  new Ext.form.Radio({
        boxLabel: '文件备份(从磁盘复制内容)', name: 'copytype_radio', inputValue: 2, id: 'copyContent_radio', hideLabel: true});

    var rsync_options = new Ext.form.TextField({
        fieldLabel : 'rsync',
        name       : 'rsync_options'
    });


    var cp_options = new Ext.form.TextField({
        fieldLabel : 'cp',
        name       : 'cp_options'
    });


  

    // Setup the form panel
    var copyContent_Panel = new Ext.form.FormPanel({
        region     : 'center',
        //title      : 'Generic Form Panel',
        //bodyStyle  : 'padding: 10px; background-color: #DFE8F6',
        labelWidth : 100,
        width      : 400,
        height:'100%',
        items      : [
            rsync_options,
            cp_options,
            
        ]
    });

   
    var copyContent_label=new Ext.form.Label({
        text: "开始备份前需要先挂载文件"
        //html:'<div style="" class="boldlabelheading">'+_("General")+'<br/></div>'
    });

    var copyContent_Group = {
        xtype: 'fieldset',
        //title: 'hotBackupGroup',
        //x:0,
        border:false,
//         columns: 2,
        autoHeight: true,
        items: [
            copyContent_radio,
            copyContent_label]
        }


    
/*
    file_backup_url ='/backup/get_file_backup_options?group_id='+group_id; 
    if(mode=='EDIT'){                
            file_backup_url ='/backup/get_file_backup_options?group_id='+group_id+ "&backupsetup_id="+config_setting.backupsetup_id; 
    }
   

var file_backup_advance_option_store = new Ext.data.JsonStore({
        url: file_backup_url,
        root: 'rows',
        fields: ['attribute','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }

    });
file_backup_advance_option_store.load();



 var copyContent_Option_button=new Ext.Button({
        id: 'copyContent_Option_button',
        text: _('Options'),
        //icon:'icons/2right.png',
        //cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                label = "File Backup Options";
                var w=new Ext.Window({
                    title :'Advance Options ',
                    width :400,
                    height:380,
                    modal : true,
                    resizable : false
                });                
                w.add(AdvanceOptionPanel(group_id, w,file_backup_advance_option_store, label));                
                w.show();
                
            }
        }
    });
*/

    var tarfile_used= false;
    var tar_checkBox=  new Ext.form.Checkbox({
        name: 'Create_tar_file',
        x: 10,
        checked: false,
        boxLabel: '创建tar文件',
        hideLabel: true,
        labelSeparator: '', 
        listeners: {
            check: function(this_checkbox, checked) {
                if(checked)
                {
                    tarfile_used= true;
                    compression_combo.enable();
                }
                else
                {
                    tarfile_used= false;
                    compression_combo.disable();
                }
            }

        }
    });

var compression_combo=new Ext.form.ComboBox({
        //anchor:'90%',
        width:80,
        minListWidth: 80,
        fieldLabel:"压缩",
        allowBlank:false,
        triggerAction:'all',
        disabled: true,
        editable: false,
        //labelStyle: 'width:'+100+'px;',
        store:[['NONE',_('NONE')],
                ['GZIP',_('GZIP')],
                //['GUNZIP',_('GUNZIP')],
                ['BZIP2',_('BZIP2')],                
               ],
        forceSelection: true,
        mode:'local',
        value: 'NONE'       

    });


 var backupContent_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250"> 选择其中的一个选项. 磁盘镜像备份将复制整个磁盘, 而文件备份则从磁盘复制内容. <br/></div>'
    });

 var advance_label2=new Ext.form.Label({
        text: "高级选项: "
        //html:'<div style="" class="boldlabelheading">'+_("General")+'<br/></div>'
    });

var BackupContentGroup = {
        xtype: 'fieldset',
        //title: 'Backup Content:',
        autoHeight: true,
        border:true,
        //bodyStyle:'padding:5px 5px 0',
        items: [backupContent_label,
            {            
            layout:'column',
            border:false,
            items:[{
                columnWidth:.5,
                layout: 'form',
                border:false,
                items: [ copyRaw_radio]
                },{
                columnWidth:.5,
                layout: 'form',
                border:false,
                items: [ copyContent_radio]
                }]
//         }, {            
//             layout:'column',
//             border: false,
//             //labelWidth: 100,
//             items:[ 
//             {
//                 columnWidth:.5,
//                 width: 150,
//                 layout: 'form',
//                 border: false,
//                 labelWidth: 30,
//                 items: [advance_label2]
//             },{
//                 columnWidth:.5,
//                 width: 150,
//                 border: false,
//                 layout: 'form',
//                 labelWidth: 30,
//                 items: [copyContent_Option_button]
//                 }]

        }]
}

var Tar_checkBox_Group = {
        xtype: 'fieldset',
        //title: 'Backup Content:',
        autoHeight: true,
        border:false,
        //bodyStyle:'padding:5px 5px 0',
        items: [{                          
            layout:'column',
            border: false,
            //labelWidth: 100,
            items:[ 
            {
                columnWidth:.5,
                width: 150,
                layout: 'form',
                border: false,
                labelWidth: 30,
                items: [tar_checkBox]
            },{
                columnWidth:.5,
                width: 150,
                border: false,
                layout: 'form',
                labelWidth: 25,
                items: [compression_combo]
                }]


            }]

    }
    
 var hor_line=new Ext.form.Label({

        html:'<div><hr><br/></div>'
        
    });
 var hor_line2=new Ext.form.Label({

        html:'<div><hr><br/></div>'
        
    });


    var BackupOptionsGroup = {
        xtype: 'fieldset',
        title: '备份选项:',
        border: false,
        autoHeight: true,
        bodyStyle:'padding:5px 5px 0',
        layout:'column',
//         items: [//BackupTypeGroup,
//                 coldBackup_radio,
//                 hotBackup_radio,
//                 hor_line,
//                 //backupContent_label,                
//                 //BackupContentGroup,
//                 copyRaw_radio,
//                 copyContent_radio,
//                 hor_line2,
//                 //Tar_checkBox_Group
//                 ]

        items:[
            {
                width: 420,
                layout:'form',
                border: false,
                items:[coldBackup_radio]
            },{
                width: 420,
                height:25,
                layout:'form',
                border: false,
                items:[hotBackup_radio]
            },{
                width: 380,
                layout:'form',
                border: false,
                items:[label_hot_backup_tip]
            },{
                width: 350,
                height:15,
                layout:'form',
                border: false,
                items:[hor_line]
            },{
                width: 420,
                layout:'form',
                border: false,
                items:[copyRaw_radio]
            },{
                width: 420,
                layout:'form',
                border: false,
                items:[copyContent_radio]
            },{
                width: 350,
                layout:'form',
                border: false,
                items:[hor_line2]
            },{
                width: 150,
                layout:'form',
                border: false,
                items:[tar_checkBox]
            },{
                width: 250,
                layout:'form',
                border: false,
                labelWidth: 80,
                items:[compression_combo]
        }]
    }


 var Purge_TextBox=new Ext.form.TextField({
        fieldLabel: _('保留备份'),
        //boxLabel: _('days'),
        name: 'Purge',
        width: 30,
        id: 'Purge',
        allowBlank:true,
        value: 30,
        hideLabel: true
        //disabled: true

    });

    var Purge_TextBox2=new Ext.form.TextField({
        fieldLabel: _('天'),
        //boxLabel: _('days'),
        name: 'Purge2',
        width: 30,
        id: 'Purge2',
        allowBlank:true,
        value: 30,
        hidden: true
        //disabled: true

    });




    var day_label=new Ext.form.Label({        
        text: '天'
    });
   

    var reten_indefinitely_radio=  new Ext.form.Radio({
        boxLabel: '保留备份无期限', name: 'retention_radio', id: 'reten_indefinitely_radio', hideLabel: true, checked: true});

    var reten_finite_day_radio=  new Ext.form.Radio({
        boxLabel: '保留备份', name: 'retention_radio', id: 'reten_finite_day_radio', hideLabel: true});  

    var RetentionPolicyGroup = {
        xtype: 'fieldset',
        title: '保留策略:',
        border:false,
        autoHeight: true,
        bodyStyle:'padding:5px 5px 0',
        //items: [{            
        layout:'column',
    //    border:false,
        items:[{
                width: 420,
                layout:'form',
                border: false,
                items:[reten_indefinitely_radio]
            },{
                width: 145,
                layout:'form',
                border: false,
                items:[reten_finite_day_radio]
            },{
                width: 35,
                layout:'form',
                border: false,
                items:[Purge_TextBox]
            },{
                width: 50,
                layout:'form',
                border: false,
                bodyStyle:'padding:5px 0px 0px 0px',
                items:[ day_label]
            }]


    }
    
    
    var label_general=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("常规")+'<br/></div>'
    });

    var general_desc_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250"> This is used to define type and methodolgy used for backup. <br/><br/></div>'
    });


    var tlabel_general=new Ext.form.Label({        
//         html:'<div class="toolbar_hdg">General</div>'
        html:'<div class="toolbar_hdg">'+_("常规")+'</div>'

    });
   
   
    
    var general_panel=new Ext.Panel({
        height:560,
        layout:"form",
        frame:false,       
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[SPTaskNameGroup, BackupOptionsGroup, RetentionPolicyGroup],
       
        tbar:[tlabel_general]
        //tbar: [general_tb],

    });

    var general_details_panel=new Ext.Panel({
        id:"panel0",
        layout:"form",
        width:100,
        //cls: 'whitebackground paneltopborder',
        height:564,
        frame:false,       
        labelWidth:130,       
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[ general_panel, ]
    });

   

//Storage details 

var transferMethod_combo=new Ext.form.ComboBox({
        //anchor:'90%',
        width:90,
        minListWidth: 90,
        fieldLabel:"选择",
        allowBlank:false,
        triggerAction:'all',
        //ctCls:ctCls,
        //labelStyle: 'width:'+60+'px;',
        store:[
                ['CP',_('复制')],
                //['SCP',_('Secure copy')],
                ['RSYNC',_('同步')],
                //['FTP',_('FTP')],
                ['CUSTOM',_('自定义')],
               ],
        forceSelection: true,
        mode:'local',
        editable : false,
        value: 'CP',
        listeners: {
           
                select: function(combo, record, index){
                    
                    //combo2.show();
                    if (combo.getValue() == 'RSYNC' || combo.getValue() == 'CUSTOM') //Local copy
                    {
                        full_backup_radio.enable();
                        incremental_backup_radio.enable();
                        full_backup_radio.show();
                        incremental_backup_radio.show();
                       
                    }                    
                    else
                    {
//                         full_backup_radio.setValue(true);
//                         full_backup_radio.disable();
//                         incremental_backup_radio.setValue(false);
//                         incremental_backup_radio.disable();
                        full_backup_radio.hide();
                        incremental_backup_radio.hide();
                       
                    }

//                     if (combo.getValue() == 'CUSTOM' || combo.getValue() == 'CP') //Local copy
//                     {
//                         //full_backup_radio.enable();
//                         //incremental_backup_radio.enable();
//                         transferMethod_Option_button.enable()
//                        
//                     }                    
//                     else
//                     {
// //                         full_backup_radio.setValue(true);
// //                         full_backup_radio.disable();
// //                         incremental_backup_radio.setValue(false);
// //                         incremental_backup_radio.disable();
//                         transferMethod_Option_button.disable()
//                        
//                     }
                    
                }
        }

    });


    transferMethod_url ='/backup/get_transferMethod_options?group_id='+group_id; 
    if(mode=='EDIT'){                
            transferMethod_url ='/backup/get_transferMethod_options?group_id='+group_id+ "&backupsetup_id="+config_setting.backupsetup_id; 
    }

    var transferMethod_option_store = new Ext.data.JsonStore({
        url: transferMethod_url,
        root: 'rows',
        fields: ['attribute','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }

    });
    transferMethod_option_store.load();




    var transferMethod_Option_button=new Ext.Button({
        id: 'destination_Option_button',
        text: _('选项'),
        //disabled: true,
        //icon:'icons/2right.png',
        //cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                label = "Transfer Method Options";
                var w=new Ext.Window({
                    title :'高级选项 ',
                    width :400,
                    height:380,
                    modal : true,
                    resizable : false
                });
                w.add(AdvanceOptionPanel( w,transferMethod_option_store,  label));                
                w.show();
                
            }
        }
    });



    var full_backup_radio=  new Ext.form.Radio({
        boxLabel: '完全备份', name: 'full_increment', inputValue: 1, id: 'full_backup_radio',checked: true, hideLabel: true, width: 150, hidden: true});

    var incremental_backup_radio=  new Ext.form.Radio({
        boxLabel: '增量备份', name: 'full_increment', inputValue: 1, id: 'incremental_backup_radio',checked: false, hideLabel: true, hidden:true, width: 150});

    var Full_Incr_radiogroup = new Ext.form.RadioGroup({
        id:'Full_Incr_radiogroup',
        xtype: 'radioxgroup',
        //fieldLabel: 'Backup Type',
        hideLabel: true,
        itemCls: 'x-check-group-alt',
        // Put all controls in a single column with width 100%
        columns: 2,
        items: [
            full_backup_radio, 
            incremental_backup_radio       
        ]
    });


    var transferMethod_Group = {
        xtype: 'fieldset',
        //fieldLabel: "Transfer Method",
        border: false,
        title: '传输方法:',
        autoHeight: true,
        bodyStyle:'padding:5px 5px 0',
        items: [{            
            layout:'column',
            border:false,
            items:[{
                columnWidth:.5,
                layout: 'form',                
                labelWidth: 95,
                width: 210,
                border:false,
                items: [ transferMethod_combo]
                },{
                columnWidth:.5,
                layout: 'form',
                layoutConfig: {
                    labelSeparator:''                    
                },
                border:false,
                items: [transferMethod_Option_button ]
                }]
        },
        Full_Incr_radiogroup ]

    }




    

    var ManagedServer_desc_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250"> 备份的存储位置是虚拟机的管理服务器.<br/></div>'
    });


    var ManagedServer_radio=  new Ext.form.Radio({
        boxLabel: '管理服务器', name: 'server_col', inputValue: 1, id: 'managed_server',checked: true, hideLabel: true});

    var Managed_Location_textbox =new Ext.form.TextField({
        fieldLabel: _('位置'),
        name: 'Managed_Location',
        width: 235,
        id: 'Managed_Location',
        value: '/var/cache/stackone/backup',
        allowBlank:true,
        disabled: false        

    });
    
    var ManagedServer_Group = {
        xtype: 'fieldset',        
        x:10,
        labelWidth: 100,
        border:true,       
        autoHeight: true,
        items: [Managed_Location_textbox]
        }

    var RemoteServer_desc_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">备份位置是远程服务器.<br/></div>'
    });

    

    var RemoteServer_radio=  new Ext.form.Radio({
        boxLabel: '远程服务器', name: 'server_col', inputValue: 2, id: 'remote_server',hideLabel: true,
        listeners: {
        check: function(this_radio, checked) {
                if(checked)
                {
                    
//                     Managed_Location_textbox.disable();
//                     RemoteServerName.enable();
//                     User_Name_textbox.enable();
//                     Password_textbox.enable();
//                     ssh_port_textbox.enable();
//                     usekey_checkBox.enable();
//                     Remote_Location_textbox.enable();
//                     TestConnect_button.enable();
                    hideField(Managed_Location_textbox);
                    showField(RemoteServerName);
                    showField(User_Name_textbox);
                    showField(Password_textbox);
                    showField(ssh_port_textbox);
                    showField(usekey_checkBox);
                    showField(Remote_Location_textbox);
                    //showField(TestConnect_button);
                    TestConnect_button.show();
                }
                else
                {
                    
//                     Managed_Location_textbox.enable();
//                     RemoteServerName.disable();
//                     User_Name_textbox.disable();
//                     Password_textbox.disable();
//                     ssh_port_textbox.disable();
//                     usekey_checkBox.disable();
//                     Remote_Location_textbox.disable();
//                     TestConnect_button.disable();
                    showField(Managed_Location_textbox);
                    hideField(RemoteServerName);
                    hideField(User_Name_textbox);
                    hideField(Password_textbox);
                    hideField(ssh_port_textbox);
                    hideField(usekey_checkBox);
                    hideField(Remote_Location_textbox);
                    //hideField(TestConnect_button);
                    TestConnect_button.hide();
                    
                }
            }
        }});

    var ServerLocation_radiogroup = new Ext.form.RadioGroup({
    id:'ServerLocation_radiogroup',
    xtype: 'radioxgroup',
    fieldLabel: '服务器',
    itemCls: 'x-check-group-alt',
    // Put all controls in a single column with width 100%
    columns: 1,
    items: [
        ManagedServer_radio, 
        RemoteServer_radio       
    ]
    });

    var RemoteServerName=new Ext.form.TextField({
        fieldLabel: _('服务器'),
        name: 'Remote_server',
        width: 235,        
        id: 'Remote_server',
        allowBlank:true
        //hidden: true

    });

     var User_Name_textbox=new Ext.form.TextField({
        fieldLabel: _('用户名'),
        name: 'User_Name',
        width: 235,
        id: 'User_Name',
        allowBlank:true
        //hidden: true

    });

    var Password_textbox=new Ext.form.TextField({
        fieldLabel: _('密码'),
        name: 'Password',
        width: 235,
        id: 'Password',
        allowBlank:true,
        //hidden: true,
        inputType:'password'

    });

    var ssh_port_textbox =new Ext.form.TextField({
        fieldLabel: _('ssh端口'),
        name: 'ssh port',
        width: 100,
        id: 'ssh_port',
        value: '22',
        allowBlank:false
        //hidden: true,        

    });   


    var usekey_checkBox=  new Ext.form.Checkbox({
        name: 'usekey_checkBox',
        checked: false,
        id: 'usekey',
        //hidden: true,
        //boxLabel: 'usekey',
        fieldLabel: _('使用Key')
    });

var TestConnect_button=new Ext.Button({
        id: 'testConnect',
        text: '测试连接',
        fieldLabel: 'Name',
        hideLabel: false,
        //icon:'icons/add.png',
        //cls:'x-btn-text-icon',
        //disabled: true,   
        listeners: {
            click: function(btn) { 
                    var servername =  RemoteServerName.getValue();    
                    var username = User_Name_textbox.getValue();
                    var password = Password_textbox.getValue();
                    var ssh_port = ssh_port_textbox.getValue();
                    var usekey = usekey_checkBox.getValue();
                    var url='backup/ping_server?server='+ servername + '&username=' + username + '&password=' + password+ '&ssh_port='+ ssh_port + '&usekey='+ usekey
                    var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    Ext.MessageBox.alert("Success", response.ping_result);
                                    //backup_grid.getStore().load();
                                }else{
                                    Ext.MessageBox.alert("Failure",response.msg);
                                }
                            },
                            failure: function(xhr){
                                Ext.MessageBox.alert( "Failure " , xhr.statusText);
                            }
                        });

                //Ext.MessageBox.alert("Sucess","Connection established");
                //showWindow(_("Create new backup task "), 640, 600, SPBackupConfigSettings(backup_grid, group_id, 'NEW', null));
                

            }
        }
    });

var TestConnect_button_Group = {
        xtype: 'fieldset',        
        //x:0,
        border:false,
        //labelWidth:1,
//         columns: 2,
        autoHeight: true,
        items: [{            
            layout:'column',
            border:false,
            items:[
            {
                columnWidth:.5,
                width: 95,
                layout: 'form',
                border:false,
                //labelWidth:10,
                items: [ Dummy_radio]
            },{
                columnWidth:.5,
                layout: 'form',
                border:false,
                layoutConfig: {
                    labelSeparator:''   
                },

                items: [TestConnect_button]                
                }]

            }]
        }
    
    


    var Remote_Location_textbox =new Ext.form.TextField({
        fieldLabel: _('位置'),
        name: 'remote_location',
        width: 235,
        id: 'remote_location',
        value: '/Storage/backup/',
        allowBlank:true,
        disabled: true        

    });
    var Dummy_radio2=  new Ext.form.Radio({
        boxLabel: '', name: 'dummy_radio2',  id: 'dummy2',checked: true, hideLabel: true, hidden: true});
    
    var RemoteServer_Group = {
        xtype: 'fieldset',        
        x:10,
        labelWidth: 100,
        border:false,        
        //labelWidth:1,
//         columns: 2,
        autoHeight: true,
        items: [RemoteServerName, User_Name_textbox, Password_textbox,ssh_port_textbox,   usekey_checkBox,  {            
            layout:'column',
            border:false,
            items:[
            {
                columnWidth:.5,
                width: 105,
                layout: 'form',
                border:false,
                //labelWidth:10,
                items: [ Dummy_radio2]
            },{
                columnWidth:.5,
                layout: 'form',
                border:false,
                layoutConfig: {
                    labelSeparator:''   
                },

                items: [TestConnect_button]                
                }]

            }]
        }

    //RemoteServer_Group.hidden == false;

//     var destination_Option_button=new Ext.Button({
//         id: 'destination_Option_button',
//         text: _('Options'),
//         //icon:'icons/2right.png',
//         //cls:'x-btn-text-icon',
//         listeners: {
//             click: function(btn) {
//                 label = "Destination Options";
//                 var w=new Ext.Window({
//                     title :'Advance Options ',
//                     width :400,
//                     height:380,
//                     modal : true,
//                     resizable : false
//                 });
//                 w.add(AdvanceOptionPanel( w,transferMethod_option_store,  label));                
//                 w.show();
//                 
//             }
//         }
//     });
// 
//     var advance_label3=new Ext.form.Label({
//         text: "Advanced Options: "
//         //html:'<div style="" class="boldlabelheading">'+_("General")+'<br/></div>'
//     });
// 
//     var DestinationOptionGroup = {
//         xtype: 'fieldset',
//         //title: 'Backup Content:',
//         autoHeight: true,
//         bodyStyle:'padding:5px 5px 0',
//         items: [{            
//             layout:'column',
//             border: false,
//             //labelWidth: 100,
//             items:[ 
//             {
//                 columnWidth:.5,
//                 width: 215,
//                 layout: 'form',
//                 border: false,
//                 labelWidth: 30,
//                 items: [advance_label3]
//             },{
//                 columnWidth:.5,
//                 width: 150,
//                 border: false,
//                 layout: 'form',
//                 labelWidth: 30,
//                 items: [destination_Option_button]
//                 }]
// 
//         }]
// 
//     }

var Remote_Managed_combo=new Ext.form.ComboBox({
        //anchor:'90%',
        width:110,
        id: 'Remote_Managed_combo',
        minListWidth: 110,
        fieldLabel:"选择",   
        //hideLabel: true,
        allowBlank:false,
        triggerAction:'all',
        editable: false,
        store:[['Managed Server', 'Managed Server'],
                ['Remote Server', 'Remote Server'],                
               ],
        forceSelection: true,
        mode:'local',
        value:'Managed Server',
        listeners: {                
                select: function(combo, record, index){               
                if(combo.getValue() == 'Remote Server')
                {
                    
//                     Managed_Location_textbox.disable();
//                     RemoteServerName.enable();
//                     User_Name_textbox.enable();
//                     Password_textbox.enable();
//                     ssh_port_textbox.enable();
//                     usekey_checkBox.enable();
//                     Remote_Location_textbox.enable();
//                     TestConnect_button.enable();
//                    hideField(Managed_Location_textbox);
                    showField(RemoteServerName);
                    showField(User_Name_textbox);
                    showField(Password_textbox);
                    showField(ssh_port_textbox);
                    showField(usekey_checkBox);
                    //showField(Remote_Location_textbox);
                    //showField(TestConnect_button);
                    TestConnect_button.show();
                }
                else
                {
                    
//                     Managed_Location_textbox.enable();
//                     RemoteServerName.disable();
//                     User_Name_textbox.disable();
//                     Password_textbox.disable();
//                     ssh_port_textbox.disable();
//                     usekey_checkBox.disable();
//                     Remote_Location_textbox.disable();
//                     TestConnect_button.disable();
//                    showField(Managed_Location_textbox);
                    hideField(RemoteServerName);
                    hideField(User_Name_textbox);
                    hideField(Password_textbox);
                    hideField(ssh_port_textbox);
                    hideField(usekey_checkBox);
//                    hideField(Remote_Location_textbox);
                    //hideField(TestConnect_button);
                    TestConnect_button.hide();
                    
                }
                    
                }
        }

    });

var Remote_Managed_label=new Ext.form.Label({
    //text: "Hr",
        html:'<div class="backgroundcolor" > ] 下拉包含托管服务器和远程服务器</div>'
        
    });

var Location_textbox =new Ext.form.TextField({
        fieldLabel: _('位置'),        
        name: 'Location',
        width: 235,
        id: 'Location',
        value: '/var/cache/stackone/backup',
        allowBlank:true,
        disabled: false        

    });


var close_bracket_label=new Ext.form.Label({
    //text: "Hr",
        html:'<div class="backgroundcolor" > ] </div>'        
    });


var hor_line3=new Ext.form.Label({

        html:'<div><hr></div>'
        
    });

var  Remote_Managed_group=new Ext.form.FieldSet({
        title: _('备份选项:'),
        collapsible: false,
        autoHeight:true,
        width:450,
        layoutConfig: {
                    labelSeparator:''   
                },

        //labelWidth:42,
        border: false,
        layout:'column',
        items: [
            {
                width: 420,
                layout:'form',
                border: false,
                //labelWidth:42,
//                 layoutConfig: {
//                     labelSeparator:''   
//                 },
                items:[Remote_Managed_combo]
//             },{
//                 width: 220,
//                 layout:'form',
//                 border: false,
//                 items:[Remote_Managed_label]
            },{
                width: 420,
                layout:'form',
                border: false,
                //labelWidth:55,
//                 layoutConfig: {
//                     labelSeparator:''   
//                 },
                items:[Location_textbox]
//             },{
//                 width: 10,
//                 layout:'form',
//                 border: false,
//                 labelWidth:55,
//                 layoutConfig: {
//                     labelSeparator:''   
//                 },
//                 items:[close_bracket_label]
//RemoteServerName, User_Name_textbox, Password_textbox,ssh_port_textbox,   usekey_checkBox, 
            },{
                width: 420,
                layout:'form',
                border: false,                
                items:[RemoteServerName]
 },{
                width: 420,
                layout:'form',
                border: false,                
                items:[User_Name_textbox]
 },{
                width: 420,
                layout:'form',
                border: false,                
                items:[Password_textbox]
 },{
                width: 420,
                layout:'form',
                border: false,                
                items:[ssh_port_textbox]
 },{
                width: 420,
                layout:'form',
                border: false,                
                items:[usekey_checkBox]
 },{
                width: 420,
                layout:'form',
                border: false,                
                items:[TestConnect_button]
            },{
                width: 350,
                layout:'form',
                border: false,                
                items:[hor_line3]
            }]
});


    


    var storage_desc_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250"> 允许设置备份的存储位置.<br/></div>'
    });

    var label_storage=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("备份位置")+'<br/></div>'
    });

    var tlabel_storage=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">备份位置</div>'
    });

    var storage_panel=new Ext.Panel({
        height:500,
        layout:"form",
        labelWidth: 100,
        layoutConfig: {
            labelSeparator: ':'   
        },

        frame:false,       
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        labelSeparator: "",
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[ Remote_Managed_group, transferMethod_Group],
        //items:[ Remote_Managed_group, RemoteServer_Group,  hor_line3,transferMethod_Group],
       
        tbar:[tlabel_storage]
    });


    var storage_details_panel=new Ext.Panel({
        id:"panel1",
        layout:"form",
        width:100,
        //cls: 'whitebackground paneltopborder',
        height:120,
        frame:false,       
        labelWidth:130,       
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[storage_panel]
    });




     //Start - Associate definition from DC level
    function showVMCheckBox(value,params,record){
        var id = Ext.id();
        (function(){
            new Ext.form.Checkbox({
                renderTo: id,
                checked:value,
                width:100,
                height:16,
                id:"chkVM",
                listeners:{
                    check:function(field,checked){
                        if(checked==true){
                            record.set('allow_backup',true);
                        }else{
                            record.set('allow_backup',false);
                        }
                    }
                }
            });
        }).defer(20)
        return '<span id="' + id + '"></span>';
    }

    var checkBoxSelMod = new Ext.grid.CheckboxSelectionModel({
        singleSelect:false,
        listeners:{
            rowdeselect : function(chksel ,rowIndex,record ) {
                record.set('allow_backup',false);
            },
            rowselect : function(chksel ,rowIndex,record ) {
                record.set('allow_backup',true);
            }

        }
    });

    var vm_list_columnModel = new Ext.grid.ColumnModel([
        {header: "编号", hidden: true, dataIndex: 'id'},
        {header: "虚拟机", width: 110, sortable: true, dataIndex: 'vm', id: 'vm'},
        {header: "模板", width: 120, sortable: true, dataIndex: 'template', id: 'image_name'},
        {header: "客户机操作系统", width: 100, sortable: true, dataIndex: 'os_name', id: 'os_name'},
        {header: "备份", width: 50, sortable: true, renderer: showVMCheckBox, dataIndex: 'allow_backup',hidden:true},
        checkBoxSelMod
        
    ]);

    url_vm_list_store= '/backup/get_vms_backupInfo_from_pool?group_id=' +group_id;
    if(mode=="EDIT"){        
        url_vm_list_store= '/backup/get_vms_backupInfo_from_list?group_id=' +group_id+ '&backup_id='+config_setting.backupsetup_id;
    }

    var vm_list_store = new Ext.data.JsonStore({
        url: url_vm_list_store,
        root: 'rows',
        fields: ['id', {name: 'allow_backup', type: 'boolean'}, 'vm', 'template','os_name'],
        successProperty:'success',
        listeners:{
            load:function(obj,rec,f){
                var rows=new Array()
                var j=0;
                for(var i=0;i<rec.length;i++){
                    if (rec[i].get("allow_backup")){
                         rows[j]=i;
                         j++;
                    }
                }
                checkBoxSelMod.selectRows(rows);
            },
            loadexception:function(obj,opts,res,e) {
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    vm_list_store.load();

    var vm_list_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:false
    });

    var select_all_Button=new Ext.Button({
        name: 'select_all',
        id: 'select_all',
        text:_("选择全部"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                for(var i=0;i<vm_list_store.getCount();i++){                     
                
                vm_list_store.getAt(i).set('allow_backup',true);
               
            }
                
            }
        }
    });

    var new_vm_Button=new Ext.Button({
        name: 'new_vm_Button',
        id: 'new_vm_Button',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                Provision(node,null,"provision_vm");
                
            }
        }
    });

    vm_list_grid = new Ext.grid.GridPanel({
        store: vm_list_store,
        colModel:vm_list_columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:checkBoxSelMod,
        width:425,
        height:230,
        //height:'100%',
        //autoExpandColumn:1,
        enableHdMenu:false,
        tbar:[{ xtype: 'tbfill'}, '搜索: ',new Ext.form.TextField({
            fieldLabel: '搜索',
            name: 'search2',
            id: 'search2',
            allowBlank:true,
            enableKeyEvents:true,
            listeners: {
                keyup: function(field) {
                    vm_list_grid.getStore().filter('vm', field.getValue(), false, false);
                    var rows=new Array()
                    var j=0;
                    for(var i=0;i<vm_list_store.getCount();i++){
                        if (vm_list_store.getAt(i).get("allow_backup")){
                             rows[j]=i;
                             j++;
                        }
                    }
                    checkBoxSelMod.selectRows(rows);
                }
            }

        })]

    });

    var excludevm_desc_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250"> 选择将要使用这个策略备份的虚拟机.<br/><br/></div>'
    });
 
    var label_excludevm =new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("虚拟机")+'<br/></div>'
    });

    var tlabel_excludevm =new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">虚拟机</div>'
    });


    var includeAll_radio=  new Ext.form.Radio({
        boxLabel: '所有虚拟机', name: 'include_radio_gr', id: 'includeAll_radio',checked: false, hideLabel: true, 
        listeners: {
            check: function(this_radio, checked) { 
                for(var i=0;i<vm_list_store.getCount();i++){                     
                    vm_list_store.getAt(i).set('allow_backup',true);
                }
                if (vm_list_store.getCount()>0){
                    checkBoxSelMod.selectRange(0,vm_list_store.getCount());
                }
            //vm_list_store.getStore().load();
            vm_list_grid.disable();
                
            }
        }
    });
 
    var includeAll_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250"> 此项将默认包含所有虚拟机. <br/><br/></div>'
        //text: "This will include all newly provision virtual machines as well",
    });

    var select_individual_radio=  new Ext.form.Radio({
        boxLabel: '特定虚拟机', name: 'include_radio_gr', id: 'select_individual_radio',checked: true, hideLabel: true, listeners: {
            check: function(this_radio, checked) {
                if (checked)
                    vm_list_grid.enable();
            }
                
        }
    });

    var select_individual_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">备份的虚拟机列表<br/><br/></div>'
        //text: "List of virtual machines available for backup",
    });

    var excludevm_panel=new Ext.Panel({
        height:500,
        layout:"form",
        frame:false,       
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[includeAll_radio, includeAll_label,  select_individual_radio, select_individual_label, vm_list_grid],
        //items:[ManagedServer_radio, ManagedServer_combo,RemoteServer_radio,RemoteServerName,  User_Name, Password_text,ssh_port,  Location, ],        
       
        tbar:[tlabel_excludevm, ]
    });

    var excludevm_details_panel=new Ext.Panel({
        id:"panel3",
        layout:"form",
        width:100,
        //cls: 'whitebackground paneltopborder',
        height:500,
        frame:false,       
        labelWidth:130,       
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[excludevm_panel]
        ,listeners:{
            show:function(p){
                if(vm_list_store.getCount()>0){
                    vm_list_store.sort('vm','ASC');
                }
            }
        }
    });




   
    var label_advance_options =new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("高级选项")+'<br/></div>'
    });

    var tlabel_advance_options =new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">高级选项</div>'
    });






 var advance_option_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("属性"),
        width:150,
        dataIndex: 'attribute',
        //css:'font-weight:bold; color:#414141;',
        editor: new Ext.form.TextField({
            allowBlank: false
        }),
        sortable:true
    },
    {
        header: _("值"),
        dataIndex: 'value',
        editor: new Ext.form.TextField({
            allowBlank: false
        }),
        sortable:true
    }
    ]);


    var advance_option_store = new Ext.data.JsonStore({
        url: '/backup/get_copy_options?group_id='+group_id,
        root: 'rows',
        fields: ['attribute','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }

    });
    advance_option_store.load();
    

    var prov_rec = Ext.data.Record.create([
    {
        name: 'attribute',
        type: 'string'
    },

    {
        name: 'value',
        type: 'string'
    }
    ]);

    var prov_add=new Ext.Button({
        name: 'prov_add',
        id: 'prov_add',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var r=new prov_rec({
                    attribute: '',
                    value: ' '
                });

                advance_option_grid.stopEditing();
                advance_option_store.insert(0, r);
                advance_option_grid.startEditing(0, 0);
            }
        }
    });
    var prov_remove=new Ext.Button({
        name: 'prov_remove',
        id: 'prov_remove',
        text:_("移除"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                advance_option_grid.getStore().remove(advance_option_grid.getSelectionModel().getSelected());
            }
        }
    });

    var prov_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var advance_option_grid = new Ext.grid.EditorGridPanel({
        store: advance_option_store,
        id: "advance_option_grid",
        stripeRows: true,
        colModel:advance_option_columnModel,
        frame:false,
        border: false,
        selModel:prov_selmodel,
        autoExpandColumn:1,
        autoExpandMin:250,
        //autoExpandMax:426,
        autoscroll:true,
        //height:200,
        width:'100%',
        height:400,
        clicksToEdit:2,
        enableHdMenu:false,
        tbar:[tlabel_advance_options,{
            xtype: 'tbfill'
        },prov_add,prov_remove]
    });


    
   
    var advance_options_panel=new Ext.Panel({
        height:435,
        layout:"form",
        frame:false,   
        //width: 300,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding:5px 5px 5px 5px',
        items:[advance_option_grid ]
        //items:[ManagedServer_radio, ManagedServer_combo,RemoteServer_radio,RemoteServerName,  User_Name, Password_text,ssh_port,  Location, ],        
       
        //tbar:[tlabel_advance_options,  ]
    });



    var advance_options_details_panel=new Ext.Panel({
        id:"panel4",
        layout:"form",
        width:100,
        //cls: 'whitebackground paneltopborder',
        height:500,
        frame:false,       
        labelWidth:130,       
        bodyStyle:'border-top:1px solid #AEB2BA;',
        //items:[label_advance_options, advance_options_panel]
        items:[ advance_options_panel]
    });

    
    if(mode=="EDIT"){

            SPTaskName.setValue(config_setting.taskname);
            if (config_setting.backup_type == "COLD")
            {
                coldBackup_radio.setValue(true);
                hotBackup_radio.setValue(false);
            }
                
            else{
                hotBackup_radio.setValue(true);                
                coldBackup_radio.setValue(false);
            }

            if(config_setting.backup_content == "RAW")
            {
                copyRaw_radio.setValue(true);  
                copyContent_radio.setValue(false);  
            }  
            else
            {
                copyRaw_radio.setValue(false);  
                copyContent_radio.setValue(true);  
            }
            //transferMethod_combo.setValue(config_setting.);           

            scheduleType_combo.setValue(config_setting.backup_occurance);
//             switch (config_setting.backup_occurance) {
//                 case "Hourly":
//                     HourCombo.disable();
//                     Week_checkBoxgroup.disable();
//                     Month_checkBoxgroup.disable();
// //                     showField(HourCombo);
// //                     hideField(Week_checkBoxgroup);
// //                     hideField(Month_checkBoxgroup);
// 
//                     break;
//                 case "Daily":
//                     HourCombo.enable();
//                     Week_checkBoxgroup.disable();
//                     Month_checkBoxgroup.disable();
//                     break;
//                 case "Weekly":
//                     HourCombo.enable();
//                     Week_checkBoxgroup.enable();
//                     Month_checkBoxgroup.disable();
//                     break;
//                 case "Monthly":
//                     HourCombo.enable();
//                     Week_checkBoxgroup.disable();
//                     Month_checkBoxgroup.enable();
//                     break;
//             }



            HourCombo.setValue(config_setting.backup_time_hr);
            Minute_Combo.setValue(config_setting.backup_time_min);
            //Week_checkBoxgroup.enable()
            //Week_checkBoxgroup.setValue(1)
            var listlenght =0;
            for(var i=0; i<7; i++)
            {
                //var name_both = week_array[i].getName() + config_setting.backup_weekday_list[listlenght];
                
                var str_i ="" +i;
                if (str_i == config_setting.backup_weekday_list[listlenght])
                {
                    //week_array[i].getValue();
                    
                    week_array[i].setValue(true);
                    listlenght++;
                }
                else
                {
                    week_array[i].setValue(false);
                }

            }

            listlenght =0;
            for(var i=1; i<=31; i++)
            {
                //var name_both = week_array[i].getName() + config_setting.backup_weekday_list[listlenght];
                
                var str_i ="" +i;
                if (str_i == config_setting.backup_monthday_list[listlenght])
                {
                    //week_array[i].getValue();
                    
                    month_array[i].setValue(true);
                    listlenght++;
                }
                else
                {
                    month_array[i].setValue(false);
                }

            }


          
//             schedule_object.Week= "Friday";//Week_checkBoxgroup.setValue(config_setting.);
//             schedule_object.Month= "30";//Month_checkBoxgroup.setValue(config_setting.);
//            alert(config_setting.backup_purge_days);
            reten_indefinitely_radio.checked = false;
            reten_finite_day_radio.checked = false;
            if(config_setting.backup_purge_days == 0) {
                reten_indefinitely_radio.checked = true;
            } else {
                reten_finite_day_radio.checked = true;
            }

            Purge_TextBox.setValue(config_setting.backup_purge_days);
// 
//             if (config_setting.is_remote)
//             {
//                 RemoteServer_radio.setValue(true);
//                 ManagedServer_radio.setValue(false);
//                 Managed_Location_textbox.disable();
//                 RemoteServerName.setValue(config_setting.backup_server_details.server);
//                 User_Name_textbox.setValue(config_setting.backup_server_details.username);
//                 Password_textbox.setValue(config_setting.backup_server_details.password);
//                 ssh_port_textbox.setValue(config_setting.backup_server_details.ssh_port);
//                 usekey_checkBox.setValue(config_setting.backup_server_details.use_key);
//                 Remote_Location_textbox.setValue(config_setting.backup_destination);
//             }
//             else
//             {
//                 RemoteServer_radio.setValue(false);
//                 ManagedServer_radio.setValue(true);
//                 Managed_Location_textbox.setValue(config_setting.backup_destination);
//                 //ManagedServer_combo.setValue(config_setting.backup_server_details.);
// 
//             }
           
            transferMethod_combo.setValue(config_setting.transferMethod);
            if (config_setting.transferMethod == 'RSYNC' || config_setting.transferMethod == 'CUSTOM') //Local copy
            {
                full_backup_radio.enable();
                incremental_backup_radio.enable();
                full_backup_radio.show();
                incremental_backup_radio.show();
                if (config_setting.full_backup)
                {
                    full_backup_radio.setValue(true);
                    incremental_backup_radio.setValue(false);
                }
                else
                {
                    full_backup_radio.setValue(false);
                    incremental_backup_radio.setValue(true);
                }
            
            }                    
            else
            {
//                 full_backup_radio.setValue(true);
//                 full_backup_radio.disable();
//                 incremental_backup_radio.setValue(false);
//                 incremental_backup_radio.disable();
                full_backup_radio.hide();
                incremental_backup_radio.hide();
            
            }

//             if (config_setting.transferMethod == 'CUSTOM' || config_setting.transferMethod == 'CP') //Local copy
//             {
//                 //full_backup_radio.enable();
//                 //incremental_backup_radio.enable();                
//                 transferMethod_Option_button.enable()
//             
//             }                    
//             else
//             {
// 
//                 transferMethod_Option_button.disable()
//             
//             }


            if (config_setting.includeAll_VM)
            {
                includeAll_radio.setValue(true);
                select_individual_radio.setValue(false);
            }
            else
            {
                includeAll_radio.setValue(false);
                select_individual_radio.setValue(true);
            }
            
            if(config_setting.use_tar)
            {
                tar_checkBox.setValue(true);
                compression_combo.enable();
                compression_combo.setValue(config_setting.compression_type);
            }
            else
            {
                tar_checkBox.setValue(false);
                compression_combo.disable();
            
            }

    
    }


    // card panel for all panels
    var card_panel=new Ext.Panel({
        width:435,
        height:464,
        layout:"card",
        id:"card_panel",
        //        activeItem:0,
        cls: 'whitebackground',
        border:false,
        bbar:[
        {
            xtype: 'tbfill'
        },button_prev,button_next,button_ok,button_cancel],
        items:[general_details_panel, storage_details_panel, schedule_details_panel,  excludevm_details_panel, advance_options_details_panel ]
    //
    });


    var right_panel=new Ext.Panel({
        id:"right_panel",
        width:448,
        height:480,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        bodyStyle:'padding:5px 5px 5px 5px'
        //items:[change_settings]
    });



    rootNode.appendChild(generalNode);    
    rootNode.appendChild(storageNode);   
    rootNode.appendChild(scheduleNode); 
    rootNode.appendChild(excludeVMNode);
    //For this release, we are hiding it.
    //rootNode.appendChild(advanceNode);

    treePanel.setRootNode(rootNode);   


    var outerpanel=new Ext.FormPanel({
        width:900,
        height:550,
        autoEl: {},
        layout: 'column',
        items:[side_panel,right_panel]

    });

    
    right_panel.add(card_panel);      
    
    card_panel.activeItem = 0
    return outerpanel;

}


function process_panel2(panel,treePanel,value)
{
    
    count=count+parseInt(value);   
    if(count==0){
        panel.getBottomToolbar().items.get('move-prev').disable();
    }else{
        panel.getBottomToolbar().items.get('move-prev').enable();
    }
    if (count==panel.items.length-1){
        panel.getBottomToolbar().items.get('move-next').disable();
    }else{
        panel.getBottomToolbar().items.get('move-next').enable();
    }
    panel.getLayout().setActiveItem("panel"+count);
    treePanel.getNodeById("node"+count).select();

}

function json_data(general_object, schedule_object, storage_object, excludeVM_object){
    var jsondata= Ext.util.JSON.encode({
    "general_object":general_object,
    "schedule_object":schedule_object,
    "storage_object":storage_object,
    "excludeVM_object":excludeVM_object    
    });
    return jsondata;

}

function hideField(field)
{
field.disable();// for validation
field.hide();
field.getEl().up('.x-form-item').setDisplayed(false); // hide label
}

function showField(field)
{
field.enable();
field.show();
field.getEl().up('.x-form-item').setDisplayed(true);// show label
}

function purge_single_backup(node, node_id, action){
    var result_id = ""

    result_id = g_bkp_grd_result_id
    if(result_id == null || result_id == "" || result_id == undefined) {
        Ext.MessageBox.alert("信息", "不可以清除备份.");
        return
    }

    params="result_id="+result_id+"&node_id="+node_id;
    url="/backup/purge_single_backup?"+params;

    Ext.MessageBox.confirm(_("确认"),_("确定要清除虚拟机的备份 (" + node.attributes.text + ")吗?"),function(id){
        if(id=='yes'){
            var ajaxReq=ajaxRequest(url,0,"GET",true);
            ajaxReq.request({
                success: function(xhr) {
                    //var response=Ext.util.JSON.decode(xhr.responseText);
                    Ext.MessageBox.alert("Success","Task submitted.");
                },
                failure: function(xhr){
                    Ext.MessageBox.alert( "Failure " , xhr.statusText);
                }
            });
        }
    });
}
