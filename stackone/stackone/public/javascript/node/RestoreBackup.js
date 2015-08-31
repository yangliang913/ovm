/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* author : Benf<yangbf@stackone.com.cn>
*/

function Restore_restore_grid(node){
    if(node.attributes.nodetype==stackone.constants.SERVER_POOL)
    {
        sp_id = node.attributes.id;
        url_str= 'backup/get_backupsetupinfo?sp_id=' +sp_id;
    }
    if(node.attributes.nodetype==stackone.constants.DOMAIN)
    { 
        vm_id = node.attributes.id;
    //alert(node_id);
        var s_node = node.parentNode;
        var sp_node = s_node.parentNode;
        sp_id = sp_node.attributes.id;
        url_str= 'restore/get_backupresult_info?sp_id=' +sp_id+ '&vm_id='+ vm_id;
    
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
        header: "策略",
        width: 100,
        dataIndex: 'taskname',
        sortable:true,
        editor: title_edit,
        id:'taskname'

    },    
    {
        header: "位置",
        width: 250,
        dataIndex: 'location',
        sortable:true,
        editor: title_edit,
        id:'location'

    },
    {
        header: "上次备份",
        width: 150,
        dataIndex: 'last_backup',
        sortable:true,
        editor: title_edit,
        id:'last_backup'

    },
    {
        header: "备份结果编号",
        width: 150,
        dataIndex: 'backup_result_id',
        hidden:true,
        editor: title_edit,
        id:'backup_result_id'

    },
    ]);

     var backup_store =new Ext.data.JsonStore({
            //url: "/get_backupsetupinfo?sp_id="+ group_id,
            url: url_str,
            root: 'rows',
            fields: [ 'backupsetup_id','taskname','location', 'last_backup', 'backup_result_id'  ],
            successProperty:'success',
            listeners:{
                loadexception:function(obj,opts,res,e){
                    var store_response=Ext.util.JSON.decode(res.responseText);
                    Ext.MessageBox.alert("Error2",store_response.msg);
                }

            }
        });

    backup_store.load();


    var restore_grid=new Ext.grid.GridPanel({
        store: backup_store,
        stripeRows: true,
        colModel:backup_columnModel,
        frame:false,
        border: false,
        selModel:backup_selmodel,
        height:310,
        width:'100%',
        enableHdMenu:false,
        loadMask:true,
        id:'restore_grid',
        layout:'fit',
//        tbar:[backup_new_button,'-',backup_edit_button,'-',backup_remove_button,
//             'Search (by Name): ',new Ext.form.TextField({
//             fieldLabel: 'Search',
//             name: 'search',
//             id: 'search',
//             allowBlank:true,
//             enableKeyEvents:true,
//             listeners: {
//                 keyup: function(field) {
//                     restore_grid.getStore().filter('taskname', field.getValue(), false, false);
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

return restore_grid;
}

var txt_ref_disk=new Ext.form.TextField({
    fieldLabel: _("txt_ref_disk"),
    name: 'txt_ref_disk',
    width: 200,
    id: 'txt_ref_disk',
    allowBlank:true,
    hideLabel: false
});

function Restore(vm_id, result_id, server_id) {
//     alert("Restore is called");

    file_browser=new Ext.Window({
        title:_("选择文件"),
        width : 515,
        height: 425,
        modal : true,
        resizable : false
    });
    var objData = new Object();
    objData.vm_id = vm_id;
    objData.result_id = result_id;
    objData.recent_backup = false;
    objData.server_id = server_id;
    file_browser.add(FileBrowser("/","","",true,false,txt_ref_disk,file_browser,objData));
    file_browser.show();
}

function RestoreBackup(server_id, vm_id, backupsetup_id, backup_result_id, recent_backup, ref_disk) {
//     alert("RestoreBackup is called");

    params="server_id=" + server_id + "&vm_id=" + vm_id + "&config_id=" + backupsetup_id + "&backup_result_id=" + backup_result_id + "&ref_disk=" + ref_disk;
    url="/restore/restore?" + params;

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            //alert(response)
            if(response.success){
                if(recent_backup==true) {
                    restore_grid.getStore().load();
                    closeWindow();
                }
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


function call_RestoreRecentBackup (node,node_id, action){
    Ext.MessageBox.confirm(_("确认"),_("确定要还原 (" + node.attributes.text + ")虚拟机吗? 这一过程将关闭虚拟机."),function(id){
        if(id=='yes'){
            params="vm_id="+node.attributes.id;
            url="/restore/restore_count?"+params;     
            
        
            var ajaxReq=ajaxRequest(url,0,"GET",true);
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    
                    if(response.success){                
                        if (response.policy_count == "0")
                        { 
                            Ext.MessageBox.alert("失败","没有与虚拟机相关的备份策略");          
                        }     
                        else //if (response.policy_count == "1")
                        {  
                            if (response.restore_count == "0")
                            { 
                                Ext.MessageBox.alert("失败","没有与虚拟机相关的备份记录");          
                            } 
                            else
                            {  
                                showWindow(_("最近的备份"),540,430, RestoreRecentBackup(node,node.attributes.id, action));

                                /*
                                var vm_id = node.attributes.id;
                                var backupsetup_id= response.last_backup_id;
                                var backup_result_id = response.last_restore_id;
                                var ref_disk = true;
            
                            // RestoreBackup("", vm_id, backupsetup_id, backup_result_id, true); 
                                params2="server_id=" + "" + "&vm_id=" + vm_id + "&config_id=" + backupsetup_id + "&backup_result_id=" + backup_result_id + "&ref_disk=" + ref_disk;
                                url2="/restore/restore?" + params2;
                                
                                var ajaxReq=ajaxRequest(url2,0,"GET",true);
                                ajaxReq.request({
                                    success: function(xhr) {
                                        var response=Ext.util.JSON.decode(xhr.responseText);
                                        //alert(response)
                                        if(response.success){
        //                                     if(recent_backup==true) {
        //                                         //restore_grid.getStore().load();
        //                                         //closeWindow();
        //                                     }
                                            //Ext.MessageBox.alert("Sucess",response.msg);
                                        }else{
                                            Ext.MessageBox.alert("Failure",response.msg);
                                        }
                                    },
                                    failure: function(xhr){
                                        Ext.MessageBox.alert( "Failure " , xhr.statusText);
                                    }
                                });
                                */
                            }
                            
                        }/*
                        else
                        {   
                            if (response.restore_count == "0")
                            { 
                                Ext.MessageBox.alert("Failure","No Backup record exist for the Virtual Machine");          
                            } 
                            else
                            {  
                                showWindow(_("Recent Backup's"),540,430, RestoreRecentBackup(node,node.attributes.id, action));
                            }
                            
                        }*/
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


function RestoreRecentBackup(node, vm_id, action){
//     alert("RestoreRecentBackup is called");

    restore_grid= Restore_restore_grid(node)

    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('确定'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                if(!restore_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert("错误","请从列表选择一个记录");
                    return false;
                }
                var edit_rec=restore_grid.getSelectionModel().getSelected();
                var backupsetup_id=edit_rec.get('backupsetup_id');
                var backup_result_id=edit_rec.get('backup_result_id');
                
                RestoreBackup("", vm_id, backupsetup_id, backup_result_id, true);

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
                //alert("close");
                //w.close();
                closeWindow();
                
            }
        }
    });

    var backupnow_desc_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250"> 选择其中的一个备份进行还原.<br/></div>'
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
        //bodyStyle:'padding:5px 5px 5px 5px',
        items: [ restore_grid],
        tbar: [tlabel_bcakupnow],
        bbar:[{xtype: 'tbfill'},button_ok, button_cancel],
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

function BackedUpVMlist(node){    
    if(node.attributes.nodetype==stackone.constants.SERVER_POOL)
    {
        sp_id = node.attributes.id;
        url_str= 'backup/BackedUpVMlist?sp_id=' +sp_id;
    }
//     if(node.attributes.nodetype==stackone.constants.DOMAIN)
//     { 
//         vm_id = node.attributes.id;
//     //alert(node_id);
//         var s_node = node.parentNode;
//         var sp_node = s_node.parentNode;
//         sp_id = sp_node.attributes.id;
//         url_str= 'restore/get_backupresult_info?sp_id=' +sp_id+ '&vm_id='+ vm_id;
//     
//     }
    var backed_vm_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var title_edit = new Ext.form.TextField();

    var backed_vm_columnModel = new Ext.grid.ColumnModel([
    {
        header: "vm ID",
        width: 50,
        dataIndex: 'vm_id',
        menuDisabled: false,
        hidden:true,
        //editor: title_edit
    },
    {
        header: "名称",
        width: 100,
        dataIndex: 'vm_name',
        sortable:true,
        //editor: title_edit,
        id:'vm_name'

    },    
    {
        header: "服务器",
        width: 100,
        dataIndex: 'server',
        sortable:true,
        //editor: title_edit,
        id:'server'

    },
    {
        header: "客户机操作系统",
        width: 100,
        dataIndex: 'os_name',
        sortable:true,
        //editor: title_edit,
        id:'os_name'

    },
    {
        header: "模板",
        width: 120,
        dataIndex: 'template',
        sortable:true,
        //editor: title_edit,
        id:'template'

    },
    {
        header: "选择",
        width: 50,
        dataIndex: 'backup_history',
        sortable:true,        
        id:'backup_history',
        renderer:function(value,params,record,row){            
               
     
                var node_id = record.get("vm_id");  
               
                var fn1= "VMBackupResultPanel('"+node_id+"')";    
                var returnVal = '<a href="#" onClick=' + fn1 + ' ><img title="可用于还原的备份记录" src="icons/file_edit.png "/></a>';
                
                return returnVal;
             
            }
    }

   
    ]);

     var backed_vm_store =new Ext.data.JsonStore({
            //url: "/get_backupsetupinfo?sp_id="+ group_id,
            url: url_str,
            root: 'info',
            fields: [ 'vm_id','vm_name','server','os_name','template', 'backup_history' ],
            successProperty:'success',
            listeners:{
                loadexception:function(obj,opts,res,e){
                    var store_response=Ext.util.JSON.decode(res.responseText);
                    Ext.MessageBox.alert("Error",store_response.msg);
                }

            }
        });

    backed_vm_store.load();


    var backed_vm_grid=new Ext.grid.GridPanel({
        store: backed_vm_store,
        stripeRows: true,
        colModel:backed_vm_columnModel,
        frame:false,
        selModel:backed_vm_selmodel,
        height:310,
        width:'100%',
        enableHdMenu:false,
        loadMask:true,
        id:'restore_grid',
        layout:'fit',

    });

    var backed_vm_panel=new Ext.Panel({
        height:310,
        layout:"form",
        frame:false,       
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,        
        items:[backed_vm_grid],       
        
    });



return backed_vm_panel;

}


function VMBackupResultPanel(node_id){
    
    var task_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("任务编号"),
        width: 80,
        dataIndex: 'taskid',
        hidden:true        
    },
    {
        header: _("名称"),
        width: 100,
        dataIndex: 'name',
        sortable:true        
    },    

    {
        header: _("开始时间"),
        width: 100,
        dataIndex: 'starttime',
        sortable:true        
    },
    {
        header: _("结束时间"),
        width: 100,
        dataIndex: 'endtime',
        sortable:true
    },
    {
        header: _("大小"),
        width: 70,
        dataIndex: 'backup_size',
        sortable:true
    },
    {
        header: _("状态"),
        width: 100,
        dataIndex: 'status',        
        renderer:function(value,params,record,row){            
            //  if(value =='Failed' || value =='Succeeded')
            //{
                params.attr='ext:qtip="Show Message"' +
                    'style="background-image:url(icons/information.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            //}
            return value;
        }
    },
    {
        header: _("还原"),
        width: 50,
        dataIndex: 'restore',        
        renderer: showBackupResultDetailLink,
//          renderer:function(value,params,record,row){            
//                if( value =='Success'){
//                 params.attr='ext:qtip="Show Message"' +
//                     'style="background-image:url(icons/file_edit.png) '+
//                     '!important; background-position: right;'+
//                     'background-repeat: no-repeat;cursor: pointer;"';
//             }
//              return value;
//          }
    },
//     {
//         header: _("Backup Location"),
//         width: 250,
//         dataIndex: 'location',
//         sortable:true
//     }
   
   ]);



    function showBackupResultDetailLink(data,cellmd,record,row,col,store) {
            var returnVal;
            var status= record.get("status");
            if(status == 'Success')
            
            {
                
                returnVal = '<a href="#"><img title="还原虚拟机" src="icons/small_snapshot.png "/></a>';
            }
    
            return returnVal;       
    }


/*
function restore_function(node_id) {
    
   alert(node_id);
    

}*/

    var task_store = new Ext.data.JsonStore({
        url: 'backup/get_vm_backup_task_result?node_id='+node_id,
        root: 'rows',
        fields: ['taskid','name','location', 'backup_size','starttime', 'endtime','status', 'errmsg', 'restore'],
        sortInfo: {
            field: 'starttime',
            direction: 'DESC' 
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });  

    task_store.load();      

    
    
     var backupresult_info_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: task_store,
        colModel:task_columnModel,
        stripeRows: true,
        frame:false,
        //autoExpandColumn:3,
        //autoExpandMax:300,
        border:true,
        enableHdMenu:true,
        autoScroll:true,
        id:'backupresult_info_grid',
        
        width:'100%',
        //autoExpandColumn:1,
        height:220,
        //tbar:[label_task],
        listeners: {
            cellclick: function(grid ,rowIndex,columnIndex,e,b) {
                //alert(rowIndex);
//alert(columnIndex);

                var record = grid.getStore().getAt(rowIndex);
                if (columnIndex == 5)
                {
                    //if(record.get('status') =='Failed'||record.get('status') =='Succeeded'){
                        var err=record.get('errmsg');
                        showTaskMessage('Message',err);
                    //}
                }
                if (columnIndex == 6)
                {
                    if(record.get('status') =='Success'){                        
                        var backup_result_id =record.get('restore');
                        //showTaskMessage('Message',err);

                        Ext.MessageBox.confirm(_("确认"),"确定要还原备份吗?",function(id){
                            if(id=='yes'){
                                RestoreBackup(node_id, "", record.get('taskid'), false);
                            }
                        });
                    }
                }
                
            }
        },



    });

//     var backupresult_panel=new Ext.Panel({
//         height:560,
//         layout:"form",
//         frame:false,       
//         width:'100%',
//         autoScroll:true,
//         border:false,
//         bodyBorder:false,
//         bodyStyle:'padding:5px 5px 5px 5px',
//         items:[backupresult_info_grid],       
//         
//     });

    var restore_window=new Ext.Window({
                    title :'历史备份',
                    width :700,
                    height:250,
                    modal : true,
                    resizable : true
                });
    restore_window.add(backupresult_info_grid);
    restore_window.show();



    //return backupresult_panel;
    
    
}