/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
var vm_storage_disk_id=null;
var storage_id=null;
var storage_name=null;
// vmconfig settings main function

function Quiescent_Option_Grid(advance_option_store, label){



 var advance_option_columnModel = new Ext.grid.ColumnModel([    
    {
        header: _("脚本名称"),
        width:100,
        dataIndex: 'attribute',
        //css:'font-weight:bold; color:#414141;',
        editor: new Ext.form.TextField({
            allowBlank: false
        }),
        sortable:true
    },
    {
        header: _("参数"),
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
        name: 'order',
        type: 'string'
    },
    {
        name: 'attribute',
        type: 'string'
    },

    {
        name: 'value',
        type: 'string'
    }
    ]);

    var prov_up=new Ext.Button({
        name: 'prov_up',
        id: 'prov_up',
        text:_("向上"),
        icon:'icons/sequencing-up-icon.png',    //2left.png
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var selected_item =  advance_option_grid.getSelectionModel().getSelected();      
                var index = advance_option_store.indexOf( selected_item); 
                var nextindex = 0;
                if (index != 0)
                {
                    nextindex = index-1
                
                    var new_entry=new prov_rec({
                        attribute: selected_item.get('attribute'),
                        value: selected_item.get('value')
                    });                
                    //advance_option_grid.stopEditing();
                    advance_option_store.insert(nextindex, new_entry);
                    advance_option_grid.getStore().remove(selected_item);
                    //advance_option_grid.startEditing(0, 0);
                }
            }
        }
    });

    var prov_down=new Ext.Button({
        name: 'prov_down',
        id: 'prov_down',
        text:_("向下"),
        icon:'icons/sequencing-down-icon.png',  //2right.png
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var selected_item =  advance_option_grid.getSelectionModel().getSelected();      
                var index = advance_option_store.indexOf( selected_item); 
                var nextindex = 0;                
                if (index != advance_option_store.getCount()-1)
                {

                    //alert (advance_option_store.getCount());

                    nextindex = index+1
                
                    var new_entry=new prov_rec({
                        order: nextindex,
                        attribute: selected_item.get('attribute'),
                        value: selected_item.get('value')
                    });                
                    //advance_option_grid.stopEditing();
                    advance_option_grid.getStore().remove(selected_item);
                    advance_option_store.insert(nextindex, new_entry);

                }
                //advance_option_grid.startEditing(0, 0);
            }
        }
    });

    var prov_add=new Ext.Button({
        name: 'prov_add',
        id: 'prov_add',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var r=new prov_rec({
                    order : "1",
                    attribute: '',
                    value: ' '
                });

                advance_option_grid.stopEditing();
                advance_option_store.insert(0, r);
                advance_option_grid.startEditing(0, 0);
//                 for (var i=0; i=advance_option_store.getCount()-1; i++){
//                     advance_option_store.getAt(i).set('order', i+1);
//                 }
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
        },prov_up,prov_down, prov_add,prov_remove]
    });

    return advance_option_grid;
}
    

function Quiescent_Option_Panel( option_window,advance_option_store, label ){

    var advance_option_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+label+'<br/></div>'
    });


   var advance_option_grid = Quiescent_Option_Grid( advance_option_store, label);
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
//             alert(option_stat);
            
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
                //alert("close");
                //w.close();
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

function get_panel(action,disk_mode,change_seting_mode,winId,dsk_val) {
    var node = leftnav_treePanel.getSelectionModel().getSelectedNode();
    var child_nodes = node.childNodes;
    if (child_nodes != null && child_nodes != undefined && child_nodes != "") {
        node = child_nodes[0]; //Take first node
    }

    var panel = StorageDefinition(node,"SELECT",null,null,node.id,action,disk_mode,change_seting_mode,winId,dsk_val);
    storage_def.add(panel);
    storage_def.show();
    hidefields("SELECT");
}

function VMConfigSettings(action,node_id,group_id,image_node,state,vm_config,dom_id,mgd_node, vm_id){
    var change_seting_mode="";
    var servername="",osname="";
    var windowid;
    if(mgd_node != null){
        servername=mgd_node.text;
    }
    if(vm_config != null){
        osname=vm_config.os_name;
    }
//    if(state==1||state==2||state==null){
//        change_seting_mode="EDIT_VM_CONFIG";
//    }else if (state=="b"||state=="r"||state==""){
//        change_seting_mode="EDIT_VM_INFO";
//    }
    
    if(state==stackone.constants.RUNNING || state==stackone.constants.PAUSED){
        change_seting_mode="EDIT_VM_INFO";
    }else{
        change_seting_mode="EDIT_VM_CONFIG";
    }

    if (action == "change_vm_settings") {
        disable_location = false;
    } else {
        disable_location = false;
    }

    var platform="";
    var url="/node/get_platform?"
    if(image_node!=null)
        url+="node_id="+image_node.attributes.nodeid+"&type="+stackone.constants.IMAGE;
    else if(node_id!=null)
        url+="node_id="+mgd_node.attributes.id+"&type="+stackone.constants.MANAGED_NODE; 
    
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                platform=response.platform;
                vm_device_store.load({
                    params:{
                        platform:platform
                    }
                });
                platform_UI_helper(platform,change_seting_mode,true);
                var platform_mode="";
                if(platform==stackone.constants.VCENTER ){
                    if(action=='edit_image_settings'){
                       platform_mode="EDIT_TEMPLATE";
                    }else if(action=='provision_image'||action=='provision_vm'){
                       platform_mode="PROVISION_VM"
                    }else if(action=='change_vm_settings'){
                        platform_mode="EDIT_VM"
                    }
                 
                 platform_UI_helper(platform,platform_mode,true);
                }
            }
            else
                Ext.MessageBox.alert(_("Failure"),response.msg);
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
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
                process_panel(card_panel,treePanel,id.substr(4,id.length),"treepanel");
            }
        }
    });

    // root node of tree view
    var rootNode = new Ext.tree.TreeNode({
        text	: 'Root Node',
        draggable: false,
        id		: 'rootnode',
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

    var disksNode = new Ext.tree.TreeNode({
        text: _('存储'),
        draggable: false,
        id: "node1",
        nodeid: "disk",
        icon:'icons/vm-storage.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
    var networkNode = new Ext.tree.TreeNode({
        text: _('网络'),
        draggable: false,
        id: "node2",
        nodeid: "network",
        icon:'icons/vm-network.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
    var bootparamsNode = new Ext.tree.TreeNode({
        text: _('启动参数'),
        draggable: false,
        id: "node3",
        icon:'icons/vm-boot-param.png',
        nodeid: "bootparams",
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });


    var miscellaneousNode = new Ext.tree.TreeNode({
        text: _('其它选项'),
        draggable: false,
        id: "node4",
        nodeid: "disk",
        icon:'icons/vm-misc.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

    var provisioningNode = new Ext.tree.TreeNode({
        text: _('模板参数'),
        draggable: false,
        id: "node8",
        nodeid: "disk",
        icon:'icons/templates-parameters.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

    var backupNode = new Ext.tree.TreeNode({
        text: _('备份'),
        draggable: false,
        id: "node5",
        nodeid: "disk",
        icon:'icons/back-up-icon.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
    var credentialNode = new Ext.tree.TreeNode({
        text: _('认证'),
        draggable: false,
        id: "node6",
        nodeid: "credentialNode",
        icon:'icons/credentials-icon.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

    var highAvailabilityNode = new Ext.tree.TreeNode({
        text: _('高可用'),
        draggable: false,
        id: "node7",
        nodeid: "ha",
        icon:'icons/high-availability-icon.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
    var schedulingNode = new Ext.tree.TreeNode({
        text: _('自动化'),
        draggable: false,
        id: "node9",
        nodeid: "disk",
        icon:'icons/scheduling-icon.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
    var leftnavhdg="";
    var vmmatch = action.match("vm")
    if(vmmatch)
        leftnavhdg="虚拟机设置";
    else
        leftnavhdg=_("模板设置");
    var treeheading=new Ext.form.Label({
        html:'<br/><center><font size="2"></font></center><br/>'
    });

    var side_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:180,
        height:430,
        id:'side_panel',
        cls:'westPanel',
        items:[treeheading,treePanel]

    });



    var params="node_id="+node_id;
    var label_general=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("常规")+'<br/></div>'
    });

    // json store for image combo
    var grp_store = new Ext.data.JsonStore({
        url: '/template/get_target_image_groups?'+params,
        root: 'image_groups',
        fields: ['name', 'id'],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load:function(store,recs,opts){
                if(action=="provision_vm"){
                    image_group.setValue(recs[0].get('id'));
                    image_group.fireEvent('select',image_group,recs[0],0);
                }
            }
        }
    });
    if (action!="edit_image_settings" && action!="change_vm_settings" )
        grp_store.load();
    var image_group=new Ext.form.ComboBox({
        fieldLabel: _('模板组'),
        allowBlank:false,
        triggerAction:'all',
        store: grp_store,
        emptyText :_("选择模板组"),
        displayField:'name',
        valueField:'id',
        width: 250,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'image_group',
        id:'image_group',
        mode:'local',
        listeners:{
            select:function(combo,record,index){
                var grpid=record.get('id');
                if (action!="edit_image_settings"){
                    image.getStore().load({
                        params:{
                            image_group_id:grpid
                        }
                    });
                    image.setValue("");
                }
            }
        }
    });

    var img_store = new Ext.data.JsonStore({
        url: '/template/get_target_images?'+params,
        root: 'images',
        fields: ['name', 'id', 'group_id'],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load:function(store,recs,opts){
                if(action=="provision_vm"){
                    image.setValue(recs[0].get('id'));
                    image.fireEvent('select',image,recs[0],0);
                }
            }
        }
    });

    var image=new Ext.form.ComboBox({
        fieldLabel: _('模板名称'),
        allowBlank:false,
        triggerAction:'all',
        store: img_store,
        emptyText :_("选择模板名称"),
        displayField:'name',
        valueField:'id',
        width: 250,
        id:'image',
        forceSelection: true,
        name:'image',
        mode:'local',
        listeners:{

            select:function(obj,rec,index){
                //                alert(obj.getValue());
                //                image_id=obj.getValue();
                image_id=rec.get('id');

                //To load "Network Model" combobox when selecting template
                nw_model.load({
                    params:{
                        image_id:image_id
                    }
                });

                //To load "Select Network" combobox when selecting template
                available_nws_store.load({
                    params:{
                        image_id:image_id
                    }
                });

                var url="/node/get_initial_vmconfig?image_id="+image_id;
                var ajaxReq=ajaxRequest(url,0,"GET",true);
                ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        var platform_mode="";
                        var platform = response.vm_config.platform;
                        
                        if(action=='provision_image'||action=='provision_vm'){
                            platform = response.vm_config.img_platform;
                            if(platform==stackone.constants.VCENTER){
                                platform_mode='PROVISION_VM'
                                platform_UI_helper(platform,platform_mode,true);
                            }else{
                                platform_mode='PROVISION_VM'
                                platform_UI_helper(platform,platform_mode,false);
                            }


                        }

                        if(response.success){
                            vm_config=response.vm_config;
                            vmname.setValue("");
                            memory.setValue(vm_config.memory);
                            vcpu.setValue(vm_config.vcpus);
                            os_flavor.setValue(vm_config.os_flavor);
                            osname=vm_config.os_name;
                            os_flavor.fireEvent('select',os_flavor,null,null);
                            os_version.setValue(vm_config.os_version);
                            allow_backup.setValue(vm_config.allow_backup);
                            vm_config_filename.setValue(vm_config.filename);

                            if(vm_config.bootloader.length>0){
                                boot_chkbox.setValue(true);
                                boot_loader.enable();
                                boot_loader.setValue(vm_config.bootloader);
                                bootparams_panel.getComponent("kernel").disable();
                                bootparams_panel.getComponent("ramdisk").disable()
                            }else{
                                boot_chkbox.setValue(false);
                                boot_loader.setValue("/usr/bin/pygrub");
                                boot_loader.disable();
                            }

                            kernel.setValue(vm_config.kernel);
                            ramdisk.setValue(vm_config.ramdisk);
                            root_device.setValue(vm_config.root);
                            kernel_args.setValue(vm_config.extra);
                            for (var i=0;i<shutdown_event_map.getCount();i++){
                                var rec=shutdown_event_map.getAt(i);
                                if (rec.get("id")==vm_config.on_reboot)
                                    on_reboot.setValue(rec.get("value"));
                                if (rec.get("id")==vm_config.on_crash)
                                    on_crash.setValue(rec.get("value"));
                                if (rec.get("id")==vm_config.on_shutdown)
                                    on_shutdown.setValue(rec.get("value"));
                            }
                            Ext.getCmp("email_id").setValue(vm_config.email_id);
                        }
                        else
                            Ext.MessageBox.alert(_("Failure"),response.msg);
                    },
                    failure: function(xhr){
                        Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                    }
                });

                miscellaneous_store.load({
                    params:{
                        image_id:image_id,
                        group_id:group_id,
                        action:action
                    }
                });

                provisioning_store.load({
                    params:{
                        image_id:image_id
                    }
                });

                disks_store.load({
                    params:{
                        image_id:image_id,
                        mode:action,
                        group_id:group_id,
                        action:action
                    }
                });
                network_store.load({
                    params:{
                        image_id:image_id
                    //                        mode:action
                    }
                });
            }
        }
    });

    var server=new Ext.form.TextField({
        fieldLabel: _('服务器'),
        name: 'server_name',
        width: 125,
        id: 'server_name',
        allowBlank:false,
        height:22

    });

    var server_label=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:_('服务器:<div style="width:134px"/>')
    });

    var server_dum=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var server_prefer=new Ext.form.Checkbox({
        id: 'server_prefer',
        checked:(mgd_node!=null && mgd_node.attributes.nodetype!=null),
        boxLabel: _('(首选服务器)<br/><div style="height:7px"/>')

    });
    var server_det_panel=new Ext.Panel({
        id:"server_det_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        items:[server_label,server,server_dum,server_prefer]
    });

    var vm_name_exist_flag = false;
    var vmname=new Ext.form.TextField({
        fieldLabel: _('虚拟机名称'),
        name: 'vmname',
        width: 235,
        id: 'vmname',
        allowBlank:false,
        enableKeyEvents:true
        ,
        listeners:{
            keyup:function(textbox,e){
                if (action=="change_vm_settings"){
                    var l = vm_config.filename.split("/");
                    var path ='';
                    for(var i=1;i<l.length-1;i++){
                        path += '/'+l[i];
                    }
                    vm_config_filename.setValue(path+"/"+textbox.getValue());
                }else{
                    vm_config_filename.setValue(vm_config.filename+"/"+textbox.getValue());
                }
            },
            blur:function(textbox,e){
                var url="/node/check_vm_name?vm_name="+textbox.getValue()+"&vm_id="+vm_id;
                var ajaxReq=ajaxRequest(url,0,"GET",true);
                ajaxReq.request({
                        success: function(xhr) {//alert(xhr.responseText);
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                vm_name_exist_flag = false;
                            }else{
                                vm_name_exist_flag = true;
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


//   var vm_config_filename=new Ext.form.TextField({
//        fieldLabel: _('VM Config File Name'),
//        name: 'vm_config_filename',
//        width: 250,
//        id: 'vm_config_filename',
//        allowBlank:false
//    });
     var vm_config_filename=new Ext.form.TriggerField({
            fieldLabel: '配置文件名称',
            name: 'vm_config_filename',
            allowBlank:false,
            id: 'vm_config_filename',
            width:250,
            triggerClass : "x-form-search-trigger"
        });
     vm_config_filename.onTriggerClick = function(){
            var url="";
            if(mgd_node != null){
                url="node_id="+mgd_node.attributes.id;
            }
            file_browser=new Ext.Window({title:"选择文件",width : 515,height: 425,modal : true,resizable : false});
            file_browser.add(FileBrowser("/","",url,true,false,vm_config_filename,file_browser));
            if(!vm_config_filename. disabled)
                file_browser.show();
    };


    var memory=new Ext.form.TextField({
        fieldLabel: _('内存(MB)'),
        name: 'memory',
        width: 80,
        id: 'memory',
        allowBlank:false
    });
    var vcpu=new Ext.form.TextField({
        fieldLabel: _('虚拟CPUs'),
        name: 'vcpu',
        width: 80,
        id: 'vcpu',
        allowBlank:false
    });

    var auto_start_vm=new Ext.form.Checkbox({
        fieldLabel: _('服务器启动时开启VM'),
        id: 'auto_start_vm'
    });

//    var start_vm=new Ext.form.Checkbox({
//        fieldLabel: _('Start VM after Provisioning'),
//        id: 'start_vm'
//    });
    /*
    var os_flavor=new Ext.form.TextField({
        fieldLabel: _('Guest OS Flavor'),
        name: 'os_flavor',
        width: 235,
        id: 'os_flavor',
//        disabled:!(action=="edit_image_settings"||action=="change_vm_settings"),
        allowBlank:false
    });
    var os_name=new Ext.form.TextField({
        fieldLabel: _('Guest OS Name'),
        name: 'os_name',
        width: 235,
        id: 'os_name',
//        disabled:!(action=="edit_image_settings"||action=="change_vm_settings"),
        allowBlank:false
    });
    */   
   var name_rec = Ext.data.Record.create([
        {
            name: 'id',
            type: 'string'
        },
        {
            name: 'name',
            type: 'string'
        }
    ]);
    var os_flavor_store = new Ext.data.SimpleStore({
        fields: ['id', 'name'],
        data : stackone.constants.OS_FLAVORS,
        sortInfo:{
            field:'name',
            direction:'ASC'
        }
    });


    var os_flavor=new Ext.form.ComboBox({
        fieldLabel: _('操作系统'),
        name: 'os_flavor',
        id: 'os_flavor',
        allowBlank:false,
        triggerAction:'all',
        store: os_flavor_store,
        emptyText :_("选择操作系统"),
        displayField:'name',
        valueField:'id',
        width: 250,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        mode:'local',
        listeners:{
            select:function(combo,record,index){
                var flavor=combo.getValue();
                os_names.removeAll();
                os_name.setValue("");
                var tmpname="",j=0;
                var osnames=stackone.constants.OS_NAMES;
                for(var i=0;i<osnames.length;i++){
                    if(osnames[i][2]==flavor){
                        var rec=new name_rec({
                            id: osnames[i][0],
                            name: osnames[i][1]
                        });
                        tmpname=(j==0)?osnames[i][1]:tmpname;
                        os_names.add([rec]);
                        j++;
                    }
                }
                os_names.sort('name','ASC');
                if(osname!=""){
                    os_name.setValue(osname);
                    osname="";
                }else{
                    os_name.setValue(tmpname);
                }
            }
        }
     });      

    var os_names = new Ext.data.SimpleStore({
        fields: ['id', 'name'],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        data : []
    });
    var os_name=new Ext.form.ComboBox({
        fieldLabel: _('发行版本'),
        name: 'os_name',
        id: 'os_name',
        allowBlank:false,
        triggerAction:'all',
        store: os_names,
        emptyText :_("选择发行版本"),
        displayField:'name',
        valueField:'id',
        width: 250,
        //forceSelection: true,
        mode:'local'
     }); 

    var os_version=new Ext.form.TextField({
        fieldLabel: _('版本号'),
        name: 'os_version',
        width: 235,
        id: 'os_version',
//        disabled:!(action=="edit_image_settings"||action=="change_vm_settings"),
        allowBlank:false
    });

    var allow_backup=  new Ext.form.Checkbox({
        name: 'allow_backup',
        checked: true,
        id: 'allow_backup',
        //boxLabel: 'Allow backup',
        fieldLabel: _('允许备份')
        
    });

//    var update_template=new Ext.form.Checkbox({
//        fieldLabel: _('Update Template'),
//        id:'update_template'
//    })
    var template_version=new Ext.form.TextField({
        fieldLabel: _('模板版本'),
        name: 'version',
        width: 80,
        id: 'template_version',
        allowBlank:false
//        enableKeyEvents:true
        //listeners:{  }
    });

    // General Panel declaration

    var tlabel_general=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("常规")+'</div>'
    });
    var general_panel=new Ext.Panel({
        height:330,
        layout:"form",
        frame:false,       
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        //items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],
        tbar:[tlabel_general]
    });

    var general_details_panel=new Ext.Panel({
        id:"panel0",
        layout:"form",
        width:100,
        //cls: 'whitebackground paneltopborder',
        height:120,
        frame:false,       
        labelWidth:130,       
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[general_panel]
    });

    //general_panel.add(label_general,general_panel);

    var disk_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("存储")+'<br/></div>'
    });


    var disks_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("类型"),
        width: 60,
        dataIndex: 'type',
        sortable:true
    },

    {
        header: _("位置"),
        width: 190,
        dataIndex: 'filename'
    },

    {
        header: _("虚拟机设备"),
        width: 80,
        dataIndex: 'device'
    },

    {
        header: _("模式"),
        width: 40,
        dataIndex: 'mode'
    },
    {
        header: _("备份内容"),
        width: 80,
        dataIndex: 'backup_content'
    },
    {
        header: _("跳过备份"),
        width: 80,
        dataIndex: 'skip_backup',
        hidden:true
    },

    {
        header: _("选项"),
        width: 40,
        dataIndex: 'option',
        hidden:true
    },

    {
        header: _("创建磁盘"),
        width: 40,
        dataIndex: 'disk_create',
        hidden:true
    },

    {
        header: _("大小"),
        width: 40,
        dataIndex: 'size',
        hidden:true
    },

    {
        header: _("磁盘类型"),
        width: 40,
        dataIndex: 'disk_type',
        hidden:true
    },

    {
        header: _("Template Src"),
        width: 40,
        dataIndex: 'image_src',
        hidden:true
    },

    {
        header: _("Template Src Format"),
        width: 40,
        dataIndex: 'image_src_type',
        hidden:true
    },

    {
        header: _("Template Src Format"),
        width: 40,
        dataIndex: 'image_src_format',
        hidden:true
    },

    {
        header: _("文件系统"),
        width: 40,
        dataIndex: 'fs_type',
        hidden:true
    },
    {
        header: _("存储名称"),
        width: 150,
        dataIndex: 'storage_name',
        hidden:false
    },
    {
        header: _("存储磁盘编号"),
        width: 150,
        dataIndex: 'storage_disk_id',
        hidden:true
    },
    {
        header: _("存储编号"),
        width: 150,
        dataIndex: 'storage_id',
        hidden:true
    },
    {
        header: _("共享"),
        width: 48,
        dataIndex: 'shared',
        renderer:show_disk_checkbox,
        hidden:true
    }
    ]);


    var disks_store = new Ext.data.JsonStore({
        url: '/node/get_disks',
        root: 'disks',
        fields: ['type','filename','device','mode', 'backup_content',{
            name:'shared',
            type: 'boolean'
        },'option','disk_create',
        'size','disk_type','image_src','image_src_type','image_src_format',
        'fs_type','storage_disk_id','storage_id','storage_name','sequence','skip_backup'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }

        }
    });

    var disk_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });
    var network_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });
    var misc_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });
    var prov_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });


    var rem_button= new Ext.Button({
        id: 'remove',
        text: _('删除'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                disks_grid.getStore().remove(disks_grid.getSelectionModel().getSelected());
            }
        }
    });
    var is_remote=new  Ext.form.Hidden({
        id:"is_remote",
        value:false

    });
    var disk_mode="";
    var disk_new_button=new Ext.Button({
        id: 'new',
        text: _('新建'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                        
                btn.toggle(true);
                disk_mode="NEW";
                disk_details_panel.show();
                windowid=Ext.id();
                showWindow(_("存储详情"),450,440,disk_details_panel,windowid);
                disk_new_button.disable();
                disks_grid.disable();
                disk_ref_fldset.hide();
                disks_grid.getSelectionModel().clearSelections();
                var url="/node/get_disks?image_id="+image_id+"&mode=NEW"+
                "&group_id="+group_id+"&action="+action;
                var ajaxReq=ajaxRequest(url,0,"GET",true);
                ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            var new_disk=response.disks[0];
                            disks_options.setValue(new_disk.option);
                            //
                            var recs=disks_options.getStore();
                            var new_rec="";

                            for (var i=0;i<recs.getCount();i++){
                                if(new_disk.option==recs.getAt(i).get('id')){
                                    new_rec=recs.getAt(i);
                                    break;
                                }
                            }

                            //                                    var record=disks_options.getStore().get();
                            disks_options.fireEvent('select',disks_options,new_rec,0);
                            disks_type_value=new_disk.type;
                            disk_size.setValue(new_disk.size);
                            if(action=="change_vm_settings" && disk_mode=="NEW")
                                disk_location.setValue("");
                            else
                                disk_location.setValue(new_disk.filename);

                            device_mode.setValue(new_disk.mode);
                            vm_device.setValue(new_disk.device);
                            //                                    d_shared=new_disk.shared;
                            //                                    d_disk_create=new_disk.disk_create;
                            //                                    d_disk_type=new_disk.disk_type;
                            ref_disk_location.setValue(new_disk.image_src);
                            ref_disk_type.setValue(new_disk.image_src_type);
                            format.setValue(new_disk.image_src_format);
                            if(new_disk.fs_type==null)
                                file_system.setValue("");
                            else
                                file_system.setValue(new_disk.fs_type);

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


    var disk_remove_button= new Ext.Button({
        id: 'remove',
        text: _('移除'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                if(!disks_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从列表选择一个项目"));
                    return false;
                }
                var disk_rec=disks_grid.getSelectionModel().getSelected()
                device=disk_rec.get('device').replace(":cdrom","");
                disks_grid.getStore().remove(disks_grid.getSelectionModel().getSelected());

                    var create_var = device + "_disk_create";
                    var image_src_var = device + "_image_src";
                    var image_src_type_var = device + "_image_src_type";
                    var image_src_format_var = device + "_image_src_format";
                    var size_var = device + "_disk_size";
                    var disk_fs_type_var = device + "_disk_fs_type";
                    var disk_type_var = device + "_disk_type";
                    var device_attribute=new Array(create_var,image_src_var,image_src_type_var,image_src_format_var,
                        size_var,disk_fs_type_var,disk_type_var);
                   
                    for (var i=provisioning_store.getCount()-1;i>=0;i--){
                        var rec=provisioning_store.getAt(i);
                        for(var j=0;j<device_attribute.length;j++){
                            if(rec.get("attribute")==device_attribute[j]){
                                provisioning_store.remove(rec);
                            }
                        }
                    }


            }
        }
    });

    var device="";
    var edit_button= new Ext.Button({
        id: 'edit',
        text: _('编辑'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                if(!disks_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从列表选择一个项目"));
                    return false;
                }
                disk_mode="";
                windowid=Ext.id();
                showWindow(_("存储详情"),450,440,disk_details_panel,windowid);
                //We are hiding "disk_ref_fldset" here because we have found it hidden on click of "New" button.
                disk_ref_fldset.hide();
                //var rec=grid.getStore().getAt(rowIndex);
                var rec=disks_grid.getSelectionModel().getSelected();
                var grid_store=rec;
                device=grid_store.get('device').replace(":cdrom","");
                //                alert(rec.get('type'));
                //                rec.set('id',rec.get('option'));
                disks_options.setValue(rec.get('option'));

                var x=0;
                while(x<disks_options_store.getCount()){
                    if(disks_options_store.getAt(x).get('id')==rec.get('option')){
                        rec=disks_options_store.getAt(x);
                        break;
                    }
                    x++;
                }
                disks_type_store.load({
                    params:{
                        type:rec.get('id'),
                        mode:action
                    }
                });
                disks_options.fireEvent('select',disks_options,rec,0);

                disk_location.setValue(grid_store.get('filename'));
                vm_device.setValue(grid_store.get('device'));
                device_mode.setValue(grid_store.get('mode'));
                backup_content_textbox.setValue(grid_store.get('backup_content'));
                chk_skip_backup.setValue(grid_store.get('skip_backup'));
                disk_size.setValue(grid_store.get('size'));
                ref_disk_type.setValue(grid_store.get('image_src_type'));
                ref_disk_location.setValue(grid_store.get('image_src'));
                format.setValue(grid_store.get('image_src_format'));
                disks_type_value=grid_store.get('type');
                if(grid_store.get('fs_type')==null)
                    file_system.setValue("");
                else
                    file_system.setValue(grid_store.get('fs_type'));
                disk_new_button.toggle(false);
                disks_grid.disable();
                disk_details_panel.setVisible(true);
            // disks_grid.getStore().remove(disks_grid.getSelectionModel().getSelected());
            }
        }
    });
    
    var up_button= new Ext.Button({
        id: 'up',
        text: _('向上'),
        icon:'icons/sequencing-up-icon.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                    if(!disks_grid.getSelectionModel().getSelected()){
                        Ext.MessageBox.alert(_("错误"),_("请从列表选择一个项目"));
                        return false;
                    }
                    var selected_rec=disks_grid.getSelectionModel().getSelected();
                    var selected_idx=disks_grid.getStore().indexOf(selected_rec);
                    if (selected_idx>0){
                        var up_rec=disks_grid.getStore().getAt(selected_idx-1);
                        disks_grid.getStore().remove(selected_rec);
                        disks_grid.getStore().remove(up_rec);

                        disks_grid.getStore().insert(selected_idx-1,selected_rec);
                        disks_grid.getStore().insert(selected_idx,up_rec);
                        disks_grid.getSelectionModel().selectRow(selected_idx-1);
                    }
                }
            }
    });
    var down_button= new Ext.Button({
        id: 'down',
        text: _('向下'),
        icon:'icons/sequencing-down-icon.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                    if(!disks_grid.getSelectionModel().getSelected()){
                        Ext.MessageBox.alert(_("错误"),_("请从列表选择一个项目"));
                        return false;
                    }
                    var selected_rec=disks_grid.getSelectionModel().getSelected();
                    var selected_idx=disks_grid.getStore().indexOf(selected_rec);
                    if (selected_idx<disks_grid.getStore().getCount()-1){
                        var down_rec=disks_grid.getStore().getAt(selected_idx+1);
                        disks_grid.getStore().remove(selected_rec);
                        disks_grid.getStore().remove(down_rec);
                        
                        disks_grid.getStore().insert(selected_idx,down_rec);
                        disks_grid.getStore().insert(selected_idx+1,selected_rec);
                        disks_grid.getSelectionModel().selectRow(selected_idx+1);
                    }

                }
            }
    });

    var disks_type_value="";
    var disks_grid = new Ext.grid.GridPanel({
        store: disks_store,
        stripeRows: true,
        colModel:disks_columnModel,
        frame:false,
        border:false,
        selModel:disk_selmodel,
        //autoExpandColumn:1,
        //autoScroll:true,
        //height:'100%',
        height:305,
        width:'100%',
        forceSelection: true,
        enableHdMenu:false,
        id:'disks_grid',
        tbar:[_("<b>存储</b>"),{
            xtype: 'tbfill'
        },up_button,down_button,is_remote,disk_new_button,edit_button,disk_remove_button],
        listeners:{
            //            rowclick: function(grid, rowIndex, e) {
            // disk_details_panel.setVisible(true);
            //                disk_mode="";
            //                var rec=grid.getStore().getAt(rowIndex);
            //                var grid_store=rec;
            ////                alert(rec.get('type'));
            ////                rec.set('id',rec.get('option'));
            //                disks_options.setValue(rec.get('option'));
            //
            //                var x=0;
            //                while(x<disks_options_store.getTotalCount()){
            //                    if(disks_options_store.getAt(x).get('id')==rec.get('option')){
            //                        rec=disks_options_store.getAt(x);
            //                        break;
            //                    }
            //                    x++;
            //                }
            //                disks_type_store.load({
            //                      params:{
            //                          type:rec.get('id'),
            //                          mode:action
            //                      }
            //                });
            //                disks_options.fireEvent('select',disks_options,rec,0);
            //
            //                disk_location.setValue(grid_store.get('filename'));
            //                vm_device.setValue(grid_store.get('device'));
            //                device_mode.setValue(grid_store.get('mode'));
            //                disk_size.setValue(grid_store.get('size'));
            //                ref_disk_type.setValue(grid_store.get('image_src_type'));
            //                ref_disk_location.setValue(grid_store.get('image_src'));
            //                format.setValue(grid_store.get('image_src_format'));
            //                disks_type_value=grid_store.get('type');
            //                if(grid_store.get('fs_type')==null)
            //                    file_system.setValue("");
            //                else
            //                    file_system.setValue(grid_store.get('fs_type'));
            //                disk_new_button.toggle(false);
            //        fill_details(rec.get('type'),rec.get('location'),rec.get('vm_device'),rec.get('mode'))
            //           }

            rowdblclick:function(grid, rowIndex, e){
                edit_button.fireEvent('click',edit_button);
            }
        }

    });
    
    var disks_options_store = new Ext.data.JsonStore({
        url: '/node/get_disks_options_map',
        root: 'disks_options',
        fields: ['id','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load:function(store,recs,opts){
                disks_options.setValue(recs[0].get('value'));
                disks_options.fireEvent('select',disks_options,recs[0],0);
            }
        }
    });
    disks_options_store.load();


    var disks_options=new Ext.form.ComboBox({
        width:150,
        minListWidth:150,
        fieldLabel:_("选项"),
        allowBlank:false,
        triggerAction:'all',
        id:'disks_options',
        store:disks_options_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        selectOnFocus:true,
        mode:'local',
        listeners:{

            select:function(disk_opt,rec,index){
                try {
                    rec_id_temp = rec.get('id');
                } catch (ex) {
                    return;
                }
                if(rec != undefined || rec != null || rec != "") {
                    disks_type_store.load({
                        params:{
                            type:rec.get('id'),
                            mode:action
                        }
                    })
    
                    if(action=="provision_vm"||action=="provision_image"||action=="edit_image_settings"){
    
                        if(rec.get('id')=='USE_REF_DISK')
                        {
                            disk_ref_fldset.show();
                        }else{
                            disk_ref_fldset.hide();
                        }
                        for(var i=0;i<disk_elements.length;i++){
    
                            disk_details_panel.findById(disk_elements[i]).disable();
                        //Ext.get(disk_elements[i]).up('.x-form-item').setDisplayed(false);
                        }
                        var new_elements=disk_elements_map[rec.get('id')];
                        for(i=0;i<new_elements.length;i++){
                            disk_details_panel.findById(new_elements[i]).enable();
                        //Ext.get(new_elements[i]).up('.x-form-item').setDisplayed(true);
                        }
                    }
                }
            }
        }
    });

    var disk_elements=new Array('disks_type','vm_device','disk_size','disk_location','file_system','ref_disk_type','ref_disk_location','format',
        'device_mode');

    var disk_elements_map=new Array();
    disk_elements_map['CREATE_DISK']=new Array('disks_type','disk_size','file_system','disk_location','vm_device','device_mode');
    disk_elements_map['USE_DEVICE']=new Array('disk_location','file_system','vm_device','device_mode');
    disk_elements_map['USE_ISO']=new Array('disk_location','vm_device','device_mode');
    disk_elements_map['USE_REF_DISK']=new Array('disks_type','disk_location','file_system','ref_disk_location',
        'ref_disk_type','format','vm_device','device_mode');


    var disks_type_store = new Ext.data.JsonStore({
        url: '/node/get_disks_type_map',
        root: 'disks_type',
        fields: ['id','value','disk_type'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
            ,
            load:function(store,recs,opts){
                //                alert(disks_type_value);"Status "
                if(disks_type_value===""){
                    disks_type.setValue(recs[0].get('id'));
                    disks_type.selectedIndex=0;
                }else{                    
                    //                    alert(disks_type_value);
                    disks_type.setValue(disks_type_value);
                    for(var i=0;i<recs.length;i++){
                        if(recs[i].get('id')===disks_type_value){
                            disks_type.selectedIndex=i;
                            break;
                        }
                    }
                    disks_type_value="";
                }
            }
        }
    }); 
    //    disks_type_store.load();
    var disks_type=new Ext.form.ComboBox({
        width: 150,
        minListWidth: 150,
        fieldLabel:_("类型"),
        allowBlank:false,
        triggerAction:'all',
        store:disks_type_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'disks_type'
    });


    var vm_device_store = new Ext.data.JsonStore({
        url: '/node/get_vmdevice_map',
        root: 'vm_device',
        fields: ['id','value'],
        sortInfo:{
            field:'value',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    }
    );
    //vm_device_store.load();
    var vm_device=new Ext.form.ComboBox({
        width:75 ,
        fieldLabel:_("虚拟机设备"),
        allowBlank:false,
        triggerAction:'all',
        store:vm_device_store,
        displayField:'value',
        valueField:'id',
        //forceSelection: true,
        editable: true,
        mode:'local',
        id:'vm_device'
    });

    var disk_size=new Ext.form.TextField({
        fieldLabel: _("大小(MB)"),
        name: 'disk_size',
        width: 75,
        id: 'disk_size',
        allowBlank:false
    });


    var disk_location=new Ext.form.TriggerField({
        fieldLabel: _("位置"),
        name: 'disk_location',
        allowBlank:false,
        id: 'disk_location',
        width:220,
        disabled:disable_location,
        //        disabled:!is_manual,
        triggerClass : "x-form-search-trigger"
    });
    disk_location.onTriggerClick = function(){
        file_browser=new Ext.Window({
            title:_("选择文件"),
            width : 515,
            height: 425,
            modal : true,
            resizable : false
        });
        var url="";
        if(mgd_node != null){
            url="node_id="+mgd_node.attributes.id;
        }
        if(!disk_location.disabled){
            file_browser.add(FileBrowser("/","",url,true,false,disk_location,file_browser));
            file_browser.show();
        }
    //            get_disklocation();
    };

    var disk_fs_store = new Ext.data.JsonStore({
        url: '/node/get_disk_fs_map',
        root: 'disk_fs',
        fields: ['id','value'],
        sortInfo:{
            field:'value',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    }
    );
    disk_fs_store.load();

    var file_system=new Ext.form.ComboBox({
        width: 85,
        fieldLabel:_("文件系统"),
        allowBlank:false,
        triggerAction:'all',
        store:disk_fs_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'file_system'
    });

    var ref_disk_location=new Ext.form.TriggerField({
        fieldLabel: _("参考磁盘位置"),
        name: 'ref_disk_location',
        width: 280,
        id: 'ref_disk_location',
        allowBlank:false,
        triggerClass : "x-form-search-trigger"
    });
    ref_disk_location.onTriggerClick = function(){
        file_browser=new Ext.Window({
            title:_("选择文件"),
            width : 515,
            height: 425,
            modal : true,
            resizable : false
        });
        var url="";
        if(mgd_node != null){
            url="node_id="+mgd_node.attributes.id;
        }
        if(!ref_disk_location.disabled){
            file_browser.add(FileBrowser("/","",url,true,false,ref_disk_location,file_browser));
            file_browser.show();
        }
    //            get_disklocation();
    };

    var ref_disk_type_store = new Ext.data.JsonStore({
        url: '/node/get_ref_disk_type_map',
        root: 'ref_disk_type',
        fields: ['id','value'],
        sortInfo:{
            field:'value',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    }
    );
    ref_disk_type_store.load();

    var ref_disk_type=new Ext.form.ComboBox({
        width: 85,
        minListWidth: 85,
        fieldLabel:_("参考磁盘类型"),
        allowBlank:false,
        triggerAction:'all',
        store:ref_disk_type_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'ref_disk_type',
        listeners:{
            select:function(combo,record,index){
                format.getStore().load({
                    params:{
                        format_type:record.get('id')
                    }
                })
            }
            }
    });

    var ref_disk_format_store = new Ext.data.JsonStore({
        url: '/node/get_ref_disk_format_map',
        root: 'ref_disk_img_format',
        fields: ['id','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    }
    );

    var format=new Ext.form.ComboBox({
        width: 75,
        minListWidth: 75,
        fieldLabel:_("参考文件格式"),
        allowBlank:false,
        triggerAction:'all',
        store:ref_disk_format_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'format'
    });
    var device_mode_store = new Ext.data.JsonStore({
        url: '/node/get_device_mode_map',
        root: 'device_mode',
        fields: ['id','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    }
    );
    device_mode_store.load();
    var device_mode=new Ext.form.ComboBox({
        width:90,
        minListWidth: 90,
        fieldLabel:_("设备模式"),
        allowBlank:false,
        triggerAction:'all',
        store:device_mode_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'device_mode'
    });


    var storage_button=new Ext.Button({
        id: 'storage_button',
        width:120,
        icon:'/icons/storage_pool.png',
        cls:'x-btn-text-icon',
        listeners:{
            click: function(btn) {
                storage_def=new Ext.Window({
                    title:_("存储详情"),
                    width : 435,
                    height: 500,
                    modal : true,
                    resizable : false
                });
                var winId=Ext.id();
                var node = leftnav_treePanel.getSelectionModel().getSelectedNode();
                if(node.attributes.nodetype == "IMAGE") {
                    //node = provision_node_tree.getSelectionModel().getSelectedNode();
                    //provision_node_tree is null here (provision_node_tree is related to NodeSelectionDialog). So take Data_Center node
                    node = leftnav_treePanel.getRootNode().childNodes[0]
                }

                if(node.attributes.nodetype == "SERVER_POOL") {
                    //expand the server pool node
                    //we are expanding node here to get the first child node. If the node is not expanded then we will get "undefined" node.
                    node.expand();
                    var dsk_val = disks_options.getValue();
                    //wait for 3 seconds for the node getting expanded. Then try to get childNodes.
                    setTimeout("get_panel('"+action+"','"+disk_mode+"','"+change_seting_mode+"','" +winId+"','"+dsk_val+"')", 3000);
                    /*
                    var child_nodes = node.childNodes;
                    if (child_nodes != null && child_nodes != undefined && child_nodes != "") {
                        node = child_nodes[0]; //Take first node
                    }
                    */
                }else if(node.attributes.nodetype == "DOMAIN") {
                    node = node.parentNode;
                }

                if(node.attributes.nodetype != "SERVER_POOL") {
                    var panel = StorageDefinition(node,"SELECT",null,null,node.id,action,disk_mode,change_seting_mode,winId, disks_options.getValue());
                    storage_def.add(panel);
                    storage_def.show();
                    hidefields("SELECT");
                }
            }

        }
    });
    
    var disk_det_fldset=new Ext.form.FieldSet({
        title: _('存储详情'),
        collapsible: false,
        autoHeight:true,            
        width:450,
        labelWidth:90,
        layout:'column',

        items: [{
            width: 400,
            layout:'form',
            border:false,
            items:[disks_options]
        },{
            width: 400,
            layout:'form',
            border:false,
            items:[disks_type]
        },
        {
            width: 350,
            layout:'form',
            border:false,
            items:[disk_location]
        },
        {
            width: 50,
            layout:'form',
            border:false,
            items:[storage_button]
        },
        {
            width: 200,
            layout:'form',
            border:false,
            items:[disk_size]
        },
        {
            width: 200,
            layout:'form',
            border:false,
            items:[file_system]
        }
        ]

    });

    var disk_ref_fldset=new Ext.form.FieldSet({
        title: _('参考磁盘详情'),
        collapsible: false,
        autoHeight:true,
        width:450,
        labelWidth:85,
        layout:'column',
        items: [{
            width: 210,
            layout:'form',
            border:false,
            items:[ref_disk_type]
        },
        {
            width: 200,
            layout:'form',
            border:false,
            items:[format]
        },
        {
            width: 430,
            layout:'form',
            border:false,
            items:[ref_disk_location]
        }
        ]

    });
    var disk_vm_fldset=new Ext.form.FieldSet({
        title: _('虚拟机设备详情'),
        collapsible: false,
        autoHeight:true,
        width:450,
        labelWidth:85,
        layout:'column',
        items: [{
            width: 200,            
            layout:'form',
            border:false,
            items:[vm_device]
        },
        {
            width: 200,           
            layout:'form',
            border:false,
            items:[device_mode]
        }

        ]

    });

    var backup_content_textbox=new Ext.form.TextField({
        fieldLabel: _("目录/文件"),
        name: 'backup_content',
        width: 290,
        id: 'backup_content',
        allowBlank:true,
        hideLabel: false
    });

    var chk_skip_backup=new Ext.form.Checkbox({
        fieldLabel:_('跳过备份'),
        width: 200,
        checkboxToggle:false,
        checked:false,
        listeners:{
            check:function(field,checked){
                if (checked) {
                    //alert("checked");
                    backup_content_textbox.setValue("");
                    backup_content_textbox.disable();
                } else {
                    //alert("unchecked");
                    backup_content_textbox.enable();
                }
            }
        }
    });

       
    var Backup_content_group=new Ext.form.FieldSet({
        title: _('备份内容详情'),
        collapsible: false,
        autoHeight:true,
        width:450,
        labelWidth:100,
       
        items: [chk_skip_backup, backup_content_textbox

        ]

    });



    var disk_save_button=new Ext.Button({
        id: 'save',
        text: _('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(disk_location.getValue()){
                    var disk_loc=disk_location.getValue();
                    var  x = disk_loc;
                    var invalid_chars=new Array('!','@','#','%','^','&','(',')','|','?','>','<','[',']','*','"',',','"',';','?','\'');
                    for(var i=0;i<x.length;i++){
                        for(var j=0;j<=invalid_chars.length;j++){
                            if(x.charAt(i) == invalid_chars[j]){
                                Ext.MessageBox.alert(_("错误"),_("磁盘位置不能包含下面特殊字符.<br>")+
                                "comma,single quote,double quotes,'!','@','#',<br>,'%','^','&','(',')','|','?','>','<','[',']','*',';','?','\'");
                                return false;
                            }
                        }
                    }
                }

                disk_new_button.enable();
                disks_grid.enable();
                disk_mode="";
                var shared_val=false;
                //                        shared_val=is_remote.getValue();
                if (is_remote.getValue()=="true")
                    shared_val=true;

                //                        alert(shared_val==false);
                is_remote.setValue(false);

                if(disk_new_button.pressed){
                    //                              alert(disks_type.selectedIndex);
                    device=vm_device.getRawValue().replace(":cdrom","");
                    
                    var r=new disk_rec({
                        option: disks_options.getValue(),
                        type: disks_type.getValue(),
                        filename: disk_location.getValue(),
                        device: vm_device.getRawValue(),
                        mode: device_mode.getValue(),
                        backup_content: backup_content_textbox.getValue(),
                        skip_backup: chk_skip_backup.getValue(),

                        fs_type: file_system.getValue(),
                        size: disk_size.getValue(),
                        image_src: ref_disk_location.getValue(),
                        image_src_type: ref_disk_type.getValue(),
                        image_src_format: format.getValue(),
                        disk_type:disks_type.getStore().getAt(disks_type.selectedIndex).get('disk_type'),
                        shared:shared_val,
                        storage_disk_id: vm_storage_disk_id,
                        storage_id: storage_id,
                        storage_name: storage_name
                    //                                    disk_create: 'yes'
                    });
                    if (!vm_device.getRawValue())
                    {
                        Ext.MessageBox.alert(_("错误"),_("请选择虚拟机设备详情下的设备") );

                        disks_grid.disable();
                        return false
                    }if (!disk_location.getValue())
                    {
                        Ext.MessageBox.alert(_("错误"),_("请输入磁盘位置") );
                        disks_grid.disable();
                        return false
                    }
                    if(!device_mode.getValue()){
                        Ext.MessageBox.alert(_("错误"),_("请选择虚拟机设备详情下的设备模式") );
                        return false
                    }
                    //Device validation
                    new_device=vm_device.getRawValue().replace(":cdrom","");
                    if(validate_device(disks_store, new_device)==false) return false;
                    disks_store.insert(disks_store.getCount(), r);
                    disk_new_button.toggle(false);
                    //make vm_storage_disk_id null after it is used in disks_store.
                    vm_storage_disk_id=null;
                    storage_id=null;
                    storage_name=null;
                }else{
                    // edit
                    var edit_rec=disks_grid.getSelectionModel().getSelected();

                    if (!vm_device.getRawValue())
                    {
                        Ext.MessageBox.alert(_("错误"),_("请选择虚拟机设备详情下的设备") );
                        return false
                    }
                    if (!disk_location.getValue())
                    {
                        Ext.MessageBox.alert(_("错误"),_("请输入磁盘位置"));
                        return false
                    }

                    if(!device_mode.getValue()){
                        Ext.MessageBox.alert(_("错误"),_("请选择虚拟机设备详情下的设备模式") );
                        return false
                    }
                    if(edit_rec.get("device") != vm_device.getRawValue()) {
                        //Device validation
                        new_device=vm_device.getRawValue().replace(":cdrom","");
                        if(validate_device(disks_store, new_device)==false) return false;
                    }

                    //                            alert(edit_rec.get('type'));
                    edit_rec.set('option',disks_options.getValue());
                    edit_rec.set('type',disks_type.getValue());
                    edit_rec.set('filename',disk_location.getValue());
                    edit_rec.set('device',vm_device.getRawValue());
                    edit_rec.set('mode',device_mode.getValue());
                    edit_rec.set('backup_content', backup_content_textbox.getValue());
                    edit_rec.set('skip_backup', chk_skip_backup.getValue());

                    edit_rec.set('fs_type',file_system.getValue());
                    edit_rec.set('size',disk_size.getValue());
                    edit_rec.set('image_src',ref_disk_location.getValue());
                    edit_rec.set('image_src_type',ref_disk_type.getValue());
                    edit_rec.set('image_src_format',format.getValue());
                    edit_rec.set('disk_type',disks_type.getStore().getAt(disks_type.selectedIndex).get('disk_type'));
                    edit_rec.set('shared',shared_val);

                //                            Ext.MessageBox.alert( "Status " , "Disk Values Edited");
                    var create_var = device + "_disk_create";
                    var image_src_var = device + "_image_src";
                    var image_src_type_var = device + "_image_src_type";
                    var image_src_format_var = device + "_image_src_format";
                    var size_var = device + "_disk_size";
                    var disk_fs_type_var = device + "_disk_fs_type";
                    var disk_type_var = device + "_disk_type";
                    var device_attribute=new Array(create_var,image_src_var,image_src_type_var,image_src_format_var,
                        size_var,disk_fs_type_var,disk_type_var);

//                    alert(provisioning_store.getCount());
                    for (var i=provisioning_store.getCount()-1;i>=0;i--){ 
                        var rec=provisioning_store.getAt(i);
//                        alert(rec.get("attribute"));

                        for(var j=0;j<device_attribute.length;j++){
                            if(rec.get("attribute")==device_attribute[j]){
                                provisioning_store.remove(rec);
                            }
                        }
                    }
//                    alert(provisioning_store.getCount());
                    device=vm_device.getRawValue().replace(":cdrom","");
//                    alert(device);
                    
                }

                var create_var = device + "_disk_create";
                var image_src_var = device + "_image_src";
                var image_src_type_var = device + "_image_src_type";
                var image_src_format_var = device + "_image_src_format";
                var size_var = device + "_disk_size";
                var disk_fs_type_var = device + "_disk_fs_type";
                var disk_type_var = device + "_disk_type";

                var create_value = null;
                if (disks_options.getValue() == "CREATE_DISK"){
                    create_value = "yes";
                    ref_disk_location.setValue("");
                    ref_disk_type.setValue("");
                    format.setValue("");
                }
                if (disks_options.getValue() == "USE_REF_DISK"){
                    if (disks_type.getValue().replace(" ","") == "phy" &&
                        disks_type.getStore().getAt(disks_type.selectedIndex).get('disk_type') == "")
                        create_value = "";
                    else
                        create_value = "yes";
                }

                if (create_value==null || create_value != "yes"){
                    disk_size.setValue(0);
                    if (disks_options.getValue() != "USE_REF_DISK"){
                        ref_disk_location.setValue("");
                        ref_disk_type.setValue("");
                        format.setValue("");
                    }
                }
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
                
                var device_attribute=new Array(create_var,image_src_var,image_src_type_var,image_src_format_var,
                size_var,disk_fs_type_var,disk_type_var);
                var device_value=new Array(create_value,ref_disk_location.getValue(),ref_disk_type.getValue(),
                format.getValue(),disk_size.getValue(),file_system.getValue(),
                disks_type.getStore().getAt(disks_type.selectedIndex).get('disk_type'));

                for(var i=0;i<device_attribute.length;i++){
//                    alert(device_attribute[i]+"---"+device_value[i]);
                    if(device_value[i]!=null && device_value[i]!="" && device_value[i]!=0) {
                        var prov_r=new prov_rec({
                                attribute: device_attribute[i],
                                value: device_value[i]
                            });
                        provisioning_store.insert(0, prov_r);
                    }
                }
                closeWindow(windowid,false);
                disk_details_panel.hide();
            }
        }

    })
    var toptbar=new Ext.Panel({
        border:false,
        tbar:[{
            xtype: 'tbfill'
        },disk_new_button,disk_save_button]
    });
    var disk_rec = Ext.data.Record.create([
    {
        name: 'option',
        type: 'string'
    },

    {
        name: 'type',
        type: 'string'
    },

    {
        name: 'filename',
        type: 'string'
    },

    {
        name: 'device',
        type: 'string'
    },

    {
        name: 'mode',
        type: 'string'
    },
    {
        name: 'backup_content',
        type: 'string'
    },

    {
        name: 'disk_create',
        type: 'string'
    },

    {
        name: 'size',
        type: 'string'
    },

    {
        name: 'disk_type',
        type: 'string'
    },

    {
        name: 'image_src',
        type: 'string'
    },

    {
        name: 'image_src_type',
        type: 'string'
    },

    {
        name: 'image_src_format',
        type: 'string'
    },

    {
        name: 'fs_type',
        type: 'string'
    },

    {
        name: 'shared',
        type: 'boolean'
    }
    ]);
    
    var cancel_button= new Ext.Button({
        id: 'cancel',
        text: _('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                closeWindow(windowid,false);
                disk_new_button.enable();
                disks_grid.enable();
                disk_details_panel.hide();
                disk_new_button.toggle(false);
            }
        }
    });

    var lbldiskinfo=new Ext.form.Label({
        html:'<div class="backgroundcolor">'+
            _("请点击保存或取消退出")+'</div>',
        hidden:true
    });
    var bottombar=new Ext.Panel({
        border:false,
        bbar:[{
            xtype: 'tbfill'
        }, lbldiskinfo, disk_save_button,cancel_button,disk_new_button]
    })

    var disk_details_panel=new Ext.Panel({
        height:410,
        layout:"form",
        frame:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        //cls: 'paneltopborder',
        width:430,
        border:0,
        bodyBorder:false,
        id:'diskdetailspanel',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[disk_det_fldset,disk_ref_fldset,disk_vm_fldset, Backup_content_group],
        bbar:[{
            xtype: 'tbfill'
        }, lbldiskinfo, disk_save_button, cancel_button]
    });
    //    disk_details_panel.setVisible(false);

    // disk panel changes
    var disk_lbl=new Ext.form.Label({
        html:_("&nbsp;使用向上或向下箭头来更改磁盘的顺序. &nbsp;")
    });
    var seq_des=_("The sequence of disks to be saved  will be in the same order as shown in the table.");

    var tooltip_seq=new Ext.form.Label({
        html:'<img src=icons/information.png onClick=show_desc("'+escape(seq_des)+'") />'
    })
    var seq_panel=new Ext.Panel({
        id:"seq_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[disk_lbl,tooltip_seq]
    });
    var notshown=true;
    var disks_panel=new Ext.Panel({
        id:"panel1",
        //        width:100,
        //        height:100,
        //        layout:"form",
        //cls: 'paneltopborder',
        frame:false,
        width:440,
        height:425,
        border:true,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[disks_grid,seq_panel]
        ,
        listeners:{
            show:function(p){
                if(disks_store.getCount()>0 && notshown){
                    disks_store.sort('sequence','ASC');
                    notshown=false;
                }
            }
        }
    });

    var network_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("网络")+'<br/></div>'
    });
    var network_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width: 100,
        dataIndex: 'name',
        sortable:true
    },

    {
        header: _("详情"),
        width: 150,
        sortable: false,
        dataIndex: 'description'
    },

    {
        header: _("MAC地址"),
        width: 120,
        sortable: false,
        dataIndex: 'mac'
    },
    {
        header: _("型号"),
        width: 80,
        sortable: false,
        dataIndex: 'model'
    },
    {
        header: _("nw_id"),
        width: 80,
        sortable: false,
        dataIndex: 'nw_id',
        hidden: false
    }
    ]);

    var network_store = new Ext.data.JsonStore({
        url: "/network/get_nws",
        root: 'rows',
        fields: [ 'name', 'description', 'mac', 'type','bridge','model', 'nw_id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });


    var network_new_button=new Ext.Button({
        id: 'network_new',
        text: _('新建'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                //                        btn.toggle(true);
                //                        available_nws.setValue(available_nws.getStore().getAt(0).get('value'));
                btn.toggle(true);
                network_details_panel.show();
                windowid=Ext.id();
                showWindow(_("网络详情"),450,270,network_details_panel,windowid);
                network_new_button.disable();
                network_grid.disable();
                network_grid.getSelectionModel().clearSelections();
                var url="/network/get_new_nw?image_id="+image_id+"&mode="+action+"&node_id="+node_id;
                var ajaxReq=ajaxRequest(url,0,"POST",true);
                ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            //                                    alert(response.rows[0]);
                            var new_network=response.rows[0];
                            available_nws.setValue(new_network.description);
                            if(new_network.mac=="Autogenerated"){
                                mac_address.setValue("");
                            }else{
                                mac_address.setValue(new_network.mac);
                            }
                            network_model.setValue("");
                        //                                    alert(new_network.mac);
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
    var network_remove_button=new Ext.Button({
        id: 'network_remove',
        text: _('移除'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                network_grid.getStore().remove(network_grid.getSelectionModel().getSelected());
                var vif="["
                var net_len=network_store.getCount();
                for(var i=0;i<net_len;i++){
                    var mac= network_store.getAt(i).get("mac");
                    if(mac=="Autogenerated")
                        mac="$AUTOGEN_MAC";
                    var bridge= network_store.getAt(i).get("bridge");
                    if(bridge=="Default")
                        bridge="$DEFAULT_BRIDGE";
                    var model=network_store.getAt(i).get("model");
                    vif+="'mac="+mac+", bridge="+bridge+",model="+model+"'";
                    if(i!=net_len-1)
                        vif+=",";
                }
                //                                    alert(vif);
                vif+="]";
                //                                   vif= eval("("+vif+")");
                //                                   alert(vif);
                var misc_len=miscellaneous_store.getCount();
                for(i=0;i<misc_len;i++){
                    var misc_rec1=miscellaneous_store.getAt(i);
                    if (misc_rec1.get('attribute')=="vif"){
                        misc_rec1.set('value',vif);
                    }
                }
            }
        }
    });
    var network_edit_button= new Ext.Button({
        id: 'edit',
        text: _('编辑'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                if(!network_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从列表选择一个项目"));
                    return false;
                }
                windowid=Ext.id();
                showWindow(_("网络详情"),450,270,network_details_panel,windowid);
                available_nws.setValue(network_grid.getSelectionModel().getSelected().get("description"));
                if(network_grid.getSelectionModel().getSelected().get("mac")=="Autogenerated"){
                    mac_address.setValue("");
                    specify_mac.setValue(false);
                }else{
                    mac_address.setValue(network_grid.getSelectionModel().getSelected().get("mac"));
                    specify_mac.setValue(true);
                }
                network_model.setValue(network_grid.getSelectionModel().getSelected().get("model"));
                network_new_button.toggle(false);
                network_grid.disable();
                network_details_panel.setVisible(true);
            // disks_grid.getStore().remove(disks_grid.getSelectionModel().getSelected());
            }
        }
    });
    var network_grid=new Ext.grid.GridPanel({
        store: network_store,
        stripeRows: true,
        colModel:network_columnModel,
        frame:false,
        border:false,
        //autoScroll:true,
        selModel:network_selmodel,
        //autoExpandColumn:1,
        height:305,
        //height: '100%',
        //        width:418,
        width:"100%",
        enableHdMenu:false,
        id:'network_grid',
        tbar:[_("<b>网络</b>"),{
            xtype: 'tbfill'
        },network_new_button,network_edit_button,network_remove_button],
        listeners:{
            //            rowclick:function(grid, rowIndex, e){
            //  network_details_panel.setVisible(true);
            //                available_nws.setValue(grid.getSelectionModel().getSelected().get("description"));
            //                if(grid.getSelectionModel().getSelected().get("mac")=="Autogenerated"){
            //                    mac_address.setValue("");
            //                }else
            //                    mac_address.setValue(grid.getSelectionModel().getSelected().get("mac"));
            //                network_new_button.toggle(false);
            rowdblclick:function(grid, rowIndex, e){
                network_edit_button.fireEvent('click',network_edit_button);
            }
        }

    });

    var network_save_button=new Ext.Button({
        id: 'network_save',
        text: _('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                network_new_button.enable();
                network_grid.enable();
                var nw_id = available_nws.getSelectedRecord().get("nw_id");
//                alert("---------"+nw_id);
                var bridge=available_nws.getValue();
                var mac=mac_address.getValue();
                if(mac=="") {
                    mac="$AUTOGEN_MAC";
                }
                var model=network_model.getValue()
                var url="/network/get_nw_det?bridge="+bridge+"&mac="+mac+"&model="+model+"&nw_id="+nw_id;
                var ajaxReq=ajaxRequest(url,0,"POST",true);
                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            var network_det=response.nw_det[0];

                            if(network_new_button.pressed){
                                var r=new disk_rec({
                                    name: network_det.name,
                                    description: network_det.description,
                                    mac: network_det.mac,
                                    type: network_det.type,
                                    bridge: network_det.bridge,
                                    model:network_det.model,
                                    nw_id:network_det.nw_id
                                });

                                network_store.insert(0, r);
                                network_new_button.toggle(false);
                            }else{
                                // edit
                                var edit_rec=network_grid.getSelectionModel().getSelected();
                                edit_rec.set('name',network_det.name);
                                edit_rec.set('description', network_det.description);
                                edit_rec.set('mac',network_det.mac);
                                edit_rec.set('type',network_det.type);
                                edit_rec.set('bridge',network_det.bridge);
                                edit_rec.set('model',network_det.model);
                                edit_rec.set('nw_id',network_det.nw_id);
                            }
                            specify_mac.setValue(false);
                            network_details_panel.hide();
                            network_new_button.toggle(false);
                            closeWindow(windowid,false);
                            //change in misc panel
                            var vif="["
                            var net_len=network_store.getCount();
                            for(var i=0;i<net_len;i++){
                                var mac= network_store.getAt(i).get("mac");
                                if(mac=="Autogenerated")
                                    mac="$AUTOGEN_MAC";
                                var bridge= network_store.getAt(i).get("bridge");
                                if(bridge=="Default")
                                    bridge="$DEFAULT_BRIDGE";
                                var model= network_store.getAt(i).get("model");
                                if (model==null)
                                    model="";
                                var nw_id = network_store.getAt(i).get("nw_id");
                                if (nw_id == null)
                                    nw_id = ""
                                vif+="'mac="+mac+", bridge="+bridge+",model="+model+",nw_id="+nw_id+"'";
                                if(i!=net_len-1)
                                    vif+=",";
                            }

                            vif+="]";

                            var misc_len=miscellaneous_store.getCount();
                            var found=false;
                            for(i=0;i<misc_len;i++){
                                var misc_rec1=miscellaneous_store.getAt(i);
                                if (misc_rec1.get('attribute')=="vif"){
                                    found=true;
                                    misc_rec1.set('value',vif);
                                }
                            }
                            if(found==false){
                                var r=new misc_rec({
                                    attribute: 'vif',
                                    value: vif
                                });
                                miscellaneous_store.insert(0, r);
                                miscellaneous_store.sort('attribute','ASC');
                            }

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

    var network_button_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                specify_mac.setValue(false);
                closeWindow(windowid,false);
                network_new_button.enable();
                network_new_button.toggle(false);
                network_grid.enable();
                network_details_panel.hide();
            }
        }
    });
    var lblnwinfo=new Ext.form.Label({
        html:'<div class="backgroundcolor">'+_("请点击保存或取消退出")+'</div>',
        hidden:true
    });
    var net_toptbar=new Ext.Panel({
        border:false,
        bbar:[{
            xtype: 'tbfill'
        },lblnwinfo,network_save_button,network_button_cancel]
    });


    var nwlb=new Ext.form.Label({
        //        margins: {left:200},
        html:'<div align="left" width="400" style="margin-left:130px"><i>'+
            _("指定您希望虚拟机使用的网络. ")+'</i></div><br/>'
    });
    var nwlb3=new Ext.form.Label({
        //        margins: {left:200},
        //        text:"Tip: If not Specified, auto generated mac would be used. "
        html:'<div align="right" width="600"><i>'+
            _("提示：如果不指定，将使用自动生成的MAC地址.")+'</i></div>'
    });

    var available_nws_store = new Ext.data.JsonStore({
        url: "/network/get_available_nws?mode="+action+"&op_level=S&node_id="+node_id,
        root: 'rows',
        fields: ['name', 'value', 'nw_id'],
        id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
            ,
            load:function(store,recs,opts){
                available_nws.selectedIndex=0;

            }
        }
    });
    
    var available_nws=new Ext.form.ComboBox({
        fieldLabel: _('选择网络:'),
        store:available_nws_store,
        triggerAction:'all',
        emptyText :"",
        displayField:'name',
        valueField:'value',
        width:220,
        minListWidth:220,
        allowBlank: false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'available_nws',
        id:'available_nws',
        mode:'local'
    });

    var specify_mac=new Ext.form.Checkbox({
        fieldLabel:_('指定MAC 地址:'),
        width: 200,
        checkboxToggle:false,
        checked:false,
        listeners:{
            check:function(combo,checked){
                if (checked) {
                    mac_address.enable();
                } else {
                    mac_address.setValue("");
                    mac_address.disable();
                }
            }
        }
    });
    var mac_address=new Ext.form.TextField({
        fieldLabel: _('MAC 地址:'),
        name: 'MAC address',
        width: 220,
        id: 'address',
        hidemode:'offset',
        disabled:true

    });

    var network_det_fldset=new Ext.form.FieldSet({
        title: _('网络详情'),
        collapsible: false,
        // autoHeight:true,
        height:250,
        width:420,
        labelWidth:120
    });


    var nw_model = new Ext.data.JsonStore({
        url: "/network/get_network_models",
        root: 'rows',
        fields: ['name', 'value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
            ,
            load:function(store,recs,opts){
                    nw_model.selectedIndex=0;

            }
        }
     });

     var network_model=new Ext.form.ComboBox({
        fieldLabel: _('网卡类型:'),
        store:nw_model,
        triggerAction:'all',
        emptyText :"",
        displayField:'value',
        valueField:'value',
        width:220,
        minListWidth:220,
        allowBlank: false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'model_nws',
        id:'model_nws',
        mode:'local'
    });

    network_det_fldset.add(available_nws);
    network_det_fldset.add(nwlb);
    if(action!="change_vm_settings")
        network_det_fldset.add(specify_mac);
    network_det_fldset.add(mac_address);
    network_det_fldset.add(nwlb3);
    network_det_fldset.add(network_model);

    var network_details_panel=new Ext.Panel({
        height:230,
        layout:"form",
        frame:false,
        //        hidden:true,
        //        autoWidth:true,
        width:430,
        border:false,
        bodyBorder:false,
        //        bodyStyle:'padding:0px 0px 0px 0px',
        items:[network_det_fldset],
        bbar:[{
            xtype: 'tbfill'
        },lblnwinfo,network_save_button,network_button_cancel]
    });

    network_details_panel.add(network_det_fldset);
    var network_panel=new Ext.Panel({
        id:"panel2",
        layout:"form",
        //cls:'paneltopborder', 
        frame:false,
        width:440,
        height:425,
        border:0,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[network_grid]
        ,
        listeners:{
            show:function(p){
                if(network_store.getCount()>0){
                    network_store.sort('name','ASC');
                }
            }
        }
    });

    var boot_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("引导参数")+'<br/></div>'
    });
    var boot_loader=new Ext.form.TextField({
        id: 'boot_loader',
        hideLabel:true,
        width:250
    //        value:'/usr/bin/pygrub'

    });
    var boot_chkbox= new Ext.form.Checkbox({
        boxLabel: _('引导加载程序'),
        name: 'boot_check',
        id: 'boot_check',
        width:106,
        listeners:{
            check:function(field,checked){
                boot_loader_check(bootparams_panel,boot_loader,checked)
            }
        }
    });
    var boot_check=new Ext.form.CheckboxGroup({
        hideLabel: true,
        id: 'boot_check_group',
        items:[boot_chkbox,boot_loader]
    });

    var kernel=new Ext.form.TriggerField({
        fieldLabel: _('内核'),
        name: 'kernel',
        id: 'kernel',
        width:250,

        triggerClass : "x-form-search-trigger"
    });
    kernel.onTriggerClick = function(){
        file_browser=new Ext.Window({
            title:_("选择文件"),
            width : 515,
            height: 425,
            modal : true,
            resizable : false
        });
        var url="";
        if(mgd_node != null){
            url="node_id="+mgd_node.attributes.id;
        }
        if(!kernel.disabled){
            file_browser.add(FileBrowser("/","",url,true,false,kernel,file_browser));
            file_browser.show();
        }
    };

    var ramdisk=new Ext.form.TriggerField({
        fieldLabel: _('内存盘'),
        name: 'ramstorage',
        // allowBlank:false,
        id: 'ramdisk',
        width:250,

        //        disabled:!is_manual,
        triggerClass : "x-form-search-trigger"
    });
    ramdisk.onTriggerClick = function(){
        file_browser=new Ext.Window({
            title:_("选择文件"),
            width : 515,
            height: 425,
            modal : true,
            resizable : false
        });
        var url="";
        if(mgd_node != null){
            url="node_id="+mgd_node.attributes.id;
        }
        if(!ramdisk.disabled){
            file_browser.add(FileBrowser("/","",url,true,false,ramdisk,file_browser));
            file_browser.show();
        }
    };

    var root_device=new Ext.form.TextField({
        fieldLabel: _('根设备'),
        name: 'root_device',
        width: 250,
        id: 'root_device',
        value:''
    });
    var kernel_args=new Ext.form.TextField({
        fieldLabel: _('内核参数'),
        name: 'kernel_args',
        width: 250,
        id: 'kernel_args',
        value:''
    });

    var shutdown_event_map = new Ext.data.JsonStore({
        url: '/node/get_shutdown_event_map',
        fields: ['id','value'],
        root: 'shutdown_event_map',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load:function(store,recs,opts){
                if (vm_config !=null){
                    //                   on_reboot.selectByValue(vm_config.on_reboot,true);
                    for (var i=0;i<recs.length;i++){
                        if (recs[i].get("id")==vm_config.on_reboot)
                            on_reboot.setValue(recs[i].get("value"));
                        if (recs[i].get("id")==vm_config.on_crash)
                            on_crash.setValue(recs[i].get("value"));
                        if (recs[i].get("id")==vm_config.on_shutdown)
                            on_shutdown.setValue(recs[i].get("value"));
                    }
                }
            }
        }
    });
    shutdown_event_map.load();

    var on_shutdown=new Ext.form.ComboBox({
        fieldLabel: _('关闭电源时'),
        allowBlank:false,
        width: 250,
        store:shutdown_event_map,
        id:'on_shutdown',
        forceSelection: true,
        triggerAction:'all',
        minListWidth:250,
        displayField:'value',
        valueField:'id',
        mode:'local'


    });
    var on_reboot=new Ext.form.ComboBox({
        fieldLabel: _('重启时'),
        allowBlank:false,
        width: 250,
        id:'on_reboot',
        store:shutdown_event_map,
        forceSelection: true,
        triggerAction:'all',
        minListWidth:250,
        displayField:'value',
        valueField:'id',
        mode:'local'


    });

    var on_crash=new Ext.form.ComboBox({
        fieldLabel: _('注销时'),
        allowBlank:false,
        width: 250,
        id:'on_crash',
        store:shutdown_event_map,
        forceSelection: true,
        triggerAction:'all',
        minListWidth:250,
        displayField:'value',
        valueField:'id',
        mode:'local'

    });

    // Boot Params panel declaration

    var tlabel_bootparams=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("引导参数")+'</div>'
    });
    var bootparams_panel =new Ext.Panel({
        height:'100%',
        layout:"form",
        frame:false,       
        width:'100%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],
        tbar:[tlabel_bootparams]
    });

    var bootparams_details_panel=new Ext.Panel({
        id:"panel3",
        layout:"form",
        width:100,
        height:100,
        //cls: 'whitebackground paneltopborder',        
        frame:false,
        autoWidth:true,
        border:0,
        bodyStyle:'border-top:1px solid #AEB2BA;',
//         items:[boot_label,boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash]
        items:[bootparams_panel]
    });

    // Miscellaneous Panel declaration

    var misce_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading" >'+_("其它选项")+'<br/></div>'
    });

    var miscellaneous_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("属性"),
        width:150,
        dataIndex: 'attribute',
        css:'font-weight:bold; color:#414141;',
        editor: new Ext.form.TextField({
            allowBlank: false
        }),
        sortable:true
    },

    {
        header: _("值"),
        dataIndex: 'value',
        editor: new Ext.form.TextField({
//            allowBlank: false
        }),
        sortable:true
    }
    ]);


    var miscellaneous_store = new Ext.data.JsonStore({
        url: '/node/get_miscellaneous_configs',
        root: 'rows',
        fields: ['attribute','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
            ,
            load:function(){
                miscellaneous_panel.doLayout();
            }
        }
    }
    );

    var misc_rec = Ext.data.Record.create([
    {
        name: 'attribute',
        type: 'string'
    },

    {
        name: 'value',
        type: 'string'
    }
    ]);

    var misc_add=new Ext.Button({
        name: 'misc_add',
        id: 'misc_add',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var r=new misc_rec({
                    attribute: '',
                    value: ' '
                });

                misc_grid.stopEditing();
                miscellaneous_store.insert(0, r);
                misc_grid.startEditing(0, 0);
            }
        }
    });
    var misc_remove=new Ext.Button({
        name: 'misc_remove',
        id: 'misc_remove',
        text:_("移除"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                misc_grid.getStore().remove(misc_grid.getSelectionModel().getSelected());
            }
        }
    });

    var misc_grid = new Ext.grid.EditorGridPanel({
        store: miscellaneous_store,
        stripeRows: true,
        colModel:miscellaneous_columnModel,
        frame:false,
        border: false,
        selModel:misc_selmodel,
        autoExpandColumn:1,
        //autoExpandMin:325,
        //autoExpandMax:426,
        autoscroll:true,
        //autoHeight:true,
        height:305,
        //height: '100%',
        width: '100%',
        clicksToEdit:2,
        enableHdMenu:false,
        tbar:[_("<b>其它选项</b>"),{
            xtype:'tbfill'
        },misc_add,misc_remove]

    });
    //    alert(misc_grid.)
    var miscellaneous_panel=new Ext.Panel({
        id:"panel4",
        layout:"form",
        //width:100,
        //height:100,
        //cls: 'paneltopborder',
        frame:false,
        autoWidth:true,
        //        autoScroll:true,
        border:true,
        //bodyStyle:'padding:0px 0px 0px 0px',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[misc_grid]
        ,
        listeners:{
            show:function(p){
                if(miscellaneous_store.getCount()>0){
                    miscellaneous_store.sort('attribute','ASC');
                }
            }            
        }
    });

    var provisioning_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("模板参数")+'<br/></div>'
    });


    var provisioning_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("属性"),
        width:150,
        dataIndex: 'attribute',
        css:'font-weight:bold; color:#414141;',
        editor: new Ext.form.TextField({
            allowBlank: false
        }),
        sortable:true
    },

    {
        header: _("值"),
        dataIndex: 'value',
        editor: new Ext.form.TextField({
//            allowBlank: false
        }),
        sortable:true
    }
    ]);


    var provisioning_store = new Ext.data.JsonStore({
        url: '/node/get_provisioning_configs',
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
        text:_("New"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var r=new prov_rec({
                    attribute: '',
                    value: ' '
                });

                provisioning_grid.stopEditing();
                provisioning_store.insert(0, r);
                provisioning_grid.startEditing(0, 0);
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
                provisioning_grid.getStore().remove(provisioning_grid.getSelectionModel().getSelected());
            }
        }
    });
    var provisioning_grid = new Ext.grid.EditorGridPanel({
        store: provisioning_store,
        stripeRows: true,
        colModel:provisioning_columnModel,
        frame:false,
        border: false,
        selModel:prov_selmodel,
        autoExpandColumn:1,
        //autoExpandMin:325,
        //autoExpandMax:426,
        autoscroll:true,
        height:305,
        width:'100%',
        clicksToEdit:2,
        enableHdMenu:false,
        tbar:[{
            xtype: 'tbfill'
        },prov_add,prov_remove]
    });
    // Provisioning panel declaration


    var provisioning_panel=new Ext.Panel({
        id:"panel8",
        layout:"form",
        width:"100%",
        height:390,
        //cls: 'paneltopborder',
        frame:false,
        autoWidth:true,
        border:0,
        //bodyStyle:'padding:0px 0px 0px 0px',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[provisioning_label,provisioning_grid]
        ,
        listeners:{
            show:function(p){
                if(provisioning_store.getCount()>0){
                    provisioning_store.sort('attribute','ASC');
                }
            }
        }
    });


//Backup Panel
function showBackupCheckBox(value,params,record){
        var id = Ext.id();
        (function(){
            var disable = false;
            if( record.get('backup_all')== true)
            {
                disable = true;
            }

            new Ext.form.Checkbox({
                renderTo: id,
                checked:value,
                width:100,
                height:16,
                disabled :disable,
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

     var ha_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("高可用")+'<br/></div>'
     });

//Backup Panel
    Quiescent_script_url ='/node/get_quiescent_script_options';         
    if(action == "change_vm_settings"){         
        Quiescent_script_url ='/node/get_quiescent_script_options?dom_id='+ dom_id+ '&node_id='+node_id;
    }

    var quiescent_script_option_store = new Ext.data.JsonStore({
        url: Quiescent_script_url,
        id: 'quiescent_script_option_store',
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
    quiescent_script_option_store.load();




    var Quiescent_script_Option_button=new Ext.Button({
        id: 'Quiescent_script_Option_button',
        text: _('配置'),
        //disabled: true,
        //icon:'icons/2right.png',
        //cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                label = "";
                var w=new Ext.Window({
                    title :'配置静态脚本',
                    width :400,
                    height:380,
                    modal : true,
                    resizable : false
                });
                w.add(Quiescent_Option_Panel( w,quiescent_script_option_store, label));                
                w.show();
                
            }
        }
    });

    var Quiescent_script_label=new Ext.form.Label({
        html:_('静态脚本:<div style="width:110px"/>')
    }); 
    
   
    
    var advance_det_panel=new Ext.Panel({
        id:"advance_det_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        items:[Quiescent_script_label,Quiescent_script_Option_button]
    });


    var Quiescent_script_group = {
        xtype: 'fieldset',
        title: '静态脚本详情',
        autoHeight: true,
        bodyStyle:'padding:5px 5px 0',
        items: [advance_det_panel ]
    }

    

    var Purge_TextBox=new Ext.form.TextField({
        fieldLabel: _('保留备份'),
        //boxLabel: _('days'),
        name: 'Purge',
        width: 30,
        id: 'backup_retain_days',
        allowBlank:true,
        value: 30
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
        text: ' 天'
    });
    var RetentionPolicyGroup = {
        xtype: 'fieldset',
        title: '保留策略:',
        autoHeight: true,
        bodyStyle:'padding:5px 5px 0',
        items: [{            
            layout:'column',
            border:false,
            items:[{
                columnWidth:.37,
                layout: 'form',
                layoutConfig: {
                    labelSeparator:''
                },
                labelWidth: 100,
                border:false,
                items: [ Purge_TextBox]
                },{
                columnWidth:.5,
                layout: 'form',
                layoutConfig: {
                    labelSeparator:''
                },
                border:false,
                items: [Purge_TextBox2 ]
                }]
        }
                ]

    }

    

    var backupconfig_list_columnModel = new Ext.grid.ColumnModel([
        {header: "备份编号", hidden: true, dataIndex: 'backup_id'},
        {header: "备份策略", width: 100, sortable: true, dataIndex: 'name'},
        {
            header: "类型", width:80, sortable: true, 
            dataIndex: 'backup_type' 
            
        },
        {
            header: "频率", width:80, sortable: true, 
            dataIndex: 'frequency' 
            
        },   
        {
            header: "保留天数", width:90, sortable: true, 
            dataIndex: 'retention_days', 
            editor: new Ext.form.TextField({
                allowBlank: false
            })
        },
         {header: "选择", width: 50, sortable: true, renderer: showBackupCheckBox, dataIndex: 'allow_backup'},
        {header: "完全备份", hidden: true, dataIndex: 'backup_all'}
        
    ]);

    url_vm_list_store= '/backup/get_backupConfig_of_sp?group_id=' +group_id;    
    if(action == "change_vm_settings"){        
        url_vm_list_store= '/backup/get_backupConfig_of_sp?group_id=' +group_id+ '&vm_id='+vm_id;
        //alert(url_vm_list_store);
    }

    var backupconfig_list_store = new Ext.data.JsonStore({
//         url: '/storage/get_vm_list?group_id=' + "1",
        id: 'backupconfig_list_store',
        url: url_vm_list_store,
        root: 'rows',
        fields: ['backup_id', {name: 'allow_backup', type: 'boolean'}, 'name','backup_type','frequency', 'retention_days', 'backup_all' ],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e) {
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    backupconfig_list_store.load();

    var backupconfig_list_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var select_all_Button=new Ext.Button({
        name: 'select_all',
        id: 'select_all',
        text:_("选择所有"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                for(var i=0;i<backupconfig_list_store.getCount();i++){
                
                    backupconfig_list_store.getAt(i).set('allow_backup',true);
               
                }
                
            }
        }
    });
   

    backupconfig_list_grid = new Ext.grid.EditorGridPanel({
        id: 'backupconfig_list_grid',
        store: backupconfig_list_store,
        colModel:backupconfig_list_columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:backupconfig_list_selmodel,
        width:'100%',
        height:180,
        //height:'100%',
        autoExpandColumn:1,
        autoExpandMin:100,
        enableHdMenu:false,
        clicksToEdit:2
//         tbar:[{
//             xtype:'tbfill'
//         }, select_all_Button,]
    });

    var backup_desc_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">此处显示了将备份的虚拟机列表. <br/></div>'
    });
 
    var label_backup =new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("备份")+'<br/></div>'
    });

    var tlabel_backup =new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("备份")+'</div>'
    });

    var backup_grid_text =new Ext.form.Label({
        html:'<div>'+_("为虚拟机选择备份策略")+'<br/><br/></div>'
    });

    var backup_panel=new Ext.Panel({
        height:500,
        layout:"form",
        frame:false,       
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[Quiescent_script_group, backup_grid_text, backupconfig_list_grid],
        
       
        tbar:[tlabel_backup ]
    });


    var backup_details_panel=new Ext.Panel({
        id:"panel5",
        layout:"form",
        width:100,
        //cls: 'whitebackground paneltopborder',
        height:500,
        frame:false,       
        labelWidth:130,       
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[ backup_panel]
    });

     
//Credentials panel

    var ip_address=new Ext.form.TextField({
        fieldLabel: _('IP地址'),
        name: 'ip_address',
        width: 235,
        id: 'ip_address',
        allowBlank:true
    });

    var username=new Ext.form.TextField({
        fieldLabel: _('用户名'),
        name: 'username',
        width: 235,
        id: 'vm_username',
        allowBlank:true
    });

    var password=new Ext.form.TextField({
        fieldLabel: _('密码'),
        name: 'password',
        width: 235,
        id: 'vm_password',
        allowBlank:true,
        inputType:'password'
    });

    var ssh_port=new Ext.form.TextField({
        fieldLabel: _('SSH端口'),
        name: 'ssh_port',
        width: 50,
        id: 'ssh_port',
        allowBlank:true
        
    });
    

    var use_ssh_key= new Ext.form.Checkbox({
        fieldLabel: _('使用SSH key'),
        name: 'use_ssh_key',
        id: 'use_ssh_key',
        checked: false
    });
        



    var VM_Credentials = {
        xtype: 'fieldset',
        title: '虚拟机认证:',
        autoHeight: true,
        bodyStyle:'padding:5px 5px 0',
        items: [ip_address,username, password,ssh_port, use_ssh_key ]
    }

    var credential_desc_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250"> 此处显示了将备份的虚拟机列表. <br/></div>'
    });
 
    var label_credential =new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("认证")+'<br/></div>'
    });

    var tlabel_credential =new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("认证")+'</div>'
    });

    var credential_panel=new Ext.Panel({
        height:500,
        layout:"form",
        frame:false,       
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[ VM_Credentials],
        
       
        tbar:[tlabel_credential ]
    });


    var credential_details_panel=new Ext.Panel({
        id:"panel6",
        layout:"form",
        width:100,
        //cls: 'whitebackground paneltopborder',
        height:500,
        frame:false,       
        labelWidth:130,       
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[ credential_panel]
    });




//VM Priority Panel
     var vmpriority_store = new Ext.data.JsonStore({
        url: '/ha/get_vm_priority',
        root: 'vm_priority',
        fields: ['id','value'],
        sortInfo:{
            field:'id',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            load:function(obj,recs,f){
                if(action=="change_vm_settings") {
//                    vm_prior.setValue(vm_config.ha_priority);
                    for(var i=0;i<recs.length;i++){
                        if(recs[i].get("value")==vm_config.ha_priority){
                            vm_prior.setValue(recs[i].get("id"));
                        }
                    }
                }else{
                    vm_prior.selectedIndex=0;
                    vm_prior.setValue(0);
                }
            },

            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });


    vmpriority_store.load();

    var vm_prior=new Ext.form.ComboBox({
                id:"vm_prior",
                width: 100,
                fieldLabel: _('虚拟机的优先级'),
                allowBlank:false,
                triggerAction:'all',
                store:vmpriority_store,
                displayField:'value',
                valueField:'id',
                forceSelection: true,
                mode:'local',
                listWidth:100
            });

     var pr_des=_("虚拟机的优先级适用于故障迁移阶段.");
     var tooltip_priority=new Ext.form.Label({
        html:'<img src=icons/information.png onClick=show_desc("'+escape(pr_des)+'") />'
     })

   var prior_panel=new Ext.Panel({
        id:"prior_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        items:[
            {
                width:"75%",
                border:false,
                layout:'form',
                items:[vm_prior]
            },            {
                width:"10%",
                border:false,
                layout:'form',
                items:[tooltip_priority]
            }
        ]
    });


     var prefer_store = new Ext.data.JsonStore({
        url: '/ha/get_preferred_servers?grp_id='+group_id,
        root: 'prefer_servers',
        fields: ['id','value'],
        sortInfo:{
            field:'value',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            load:function(obj,resc,f){
                if(action=="change_vm_settings") {
                    preferred_server.setValue(vm_config.preferred_nodeid);
                }

            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    }
    );
    prefer_store.load();

    var preferred_server=new Ext.form.ComboBox({
                id:"preferred_server",
                width: 100,
                fieldLabel: _('首选服务器'),
                allowBlank:false,
                triggerAction:'all',
                store:prefer_store,
                displayField:'value',
                valueField:'id',
                forceSelection: true,
                mode:'local',
                listWidth:100
            });

    var tlabel_ha=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("高可用")+'</div>'
    });
    var ha_panel =new Ext.Panel({
        height:'100%',
        layout:"form",
        frame:false,
        width:'100%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[prior_panel],
        tbar:[tlabel_ha]
    });

    var ha_details_panel=new Ext.Panel({
        id:"panel7",
        layout:"form",
        width:100,
        height:100,
        //cls: 'whitebackground paneltopborder',
        frame:false,
        autoWidth:true,
        border:0,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        labelWidth:150,
//         items:[boot_label,boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash]
        items:[ha_panel]
    });


    var schedule_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("自动化")+'<br/></div>'
    });

     var scheduling_label=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("自动化")+'</div>'
    });

    var schedule_panel =schedule_time(vm_config,state,action);

    var scheduling_in_panel =new Ext.Panel({
        height:'100%',
        layout:"form",
        frame:false,
        width:'100%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 0px 0px 0px',
//        items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],
        tbar:[scheduling_label]
    });

    var scheduling_panel=new Ext.Panel({
        id:"panel9",
        layout:"form",
        width:350,
        height:"100%",
        //cls: 'whitebackground paneltopborder',
        frame:false,
        autoWidth:true,
        border:0,
        bodyStyle:'border-top:1px solid #AEB2BA;',
//         items:[boot_label,boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash]
        items:[scheduling_in_panel,schedule_panel]
    });
    // change setting panel for in mem and on disk radio buttons
    var inmemory=new Ext.form.Radio({
        boxLabel: _('内存'),
        id:'inmemory',
        name:'radio',
        listeners:{
            check:function(field,checked){
                if(checked==true){
                    platform_UI_helper(platform,change_seting_mode,false);
                    change_seting_mode="EDIT_VM_INFO";
                    platform_UI_helper(platform,change_seting_mode,true);
                    memory.setValue(vm_config.inmem_memory);
                    vcpu.setValue(vm_config.inmem_vcpus);
                }
                radio_check(bootparams_panel,miscellaneous_panel,disks_panel,checked);
            }
            }
    });

    var indisk=new Ext.form.Radio({
        boxLabel: _('磁盘'),
        id:'ondisk',
        name:'radio',
        listeners:{
            check:function(field,checked){
                if(checked==true){
                    platform_UI_helper(platform,change_seting_mode,false);
                    change_seting_mode="EDIT_VM_CONFIG";
                    platform_UI_helper(platform,change_seting_mode,true);
                    memory.setValue(vm_config.memory);
                    vcpu.setValue(vm_config.vcpus);
                }
            }
            }
    });

    var radio_group= new  Ext.form.RadioGroup({
        fieldLabel: _('修改设置'),
        columns: [100, 100],
        vertical: true,
        id:'radiogroup',
        items: [inmemory,indisk]

    });

    var change_settings=new Ext.Panel({
        id:"change_settings",
        width:435,
        layout:"form",
        height:35,
        frame:false,
        border: false,
        hidden:(action=="edit_image_settings"),
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[radio_group]
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
                disk_details_panel.destroy();
                network_details_panel.destroy();
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
                if (vm_name_exist_flag == true){
                    Ext.MessageBox.alert(_("错误"),_("虚拟机 <b>"+vmname.getValue()+"</b> 已经存在."));
                    return false;
                }
                if(action=="provision_vm"||action=="provision_image"||action=="change_vm_settings"){
                       //alert('vmname');
                    if(!vmname.getValue())
                    {
                        Ext.MessageBox.alert(_("错误"),_("请输入常规选项卡下的虚拟机名称"));
                        return false;
                    }
                    if(!checkSpecialCharacters(vmname.getValue(), "虚拟机名称")){
                    return;
                    }

                }
                if(action=="change_vm_settings"){
//                    var vert_split=template_version.getValue().split(".");
                    var vers=vm_config.template_versions;
                    if(vers.length!=0){
                        var version=template_version.getValue();
                        if(!version || isNaN(version) ||
                            (version.indexOf(".")==-1) || version.split(".")[1].length!=1 ||
                            (version<1.0)){
                          Ext.MessageBox.alert(_("错误"),
                                _("根据“常规”选项卡，请输入正确的模板版本. eg:1.2"));
                          return false;
                        }
                        var flag=false;
                        var ver_list="";
                        for(var i=0;i<vers.length;i++){
                            if(version==vers[i])
                                flag=true;
                            ver_list+=vers[i].toFixed(1);
                            if (i!=vers.length-1)ver_list+=", ";
                        }
                        if (!flag){
                            Ext.MessageBox.alert(_("错误"),_("输入一个可用的模板版本 "+
                                ver_list));
                            return false;
                        }
                    }
                }
                       //alert('vmname');
                if(!os_flavor.getValue())
                {
                    Ext.MessageBox.alert(_("错误"),_("请输入“常规”选项卡下的客户机操作系统"));
                    return false;
                }
                if(!os_name.getRawValue())
                {
                    Ext.MessageBox.alert(_("错误"),_("请输入“常规”选项卡下的客户机操作系统名称"));
                    return false;
                }
                if(!os_version.getValue())
                {
                    Ext.MessageBox.alert(_("错误"),_("请输入“常规”选项卡下的客户机操作系统版本"));
                    return false;
                }

                var misc_recs=miscellaneous_store.getRange(0,miscellaneous_store.getCount());
                var provision_recs=provisioning_store.getRange(0,provisioning_store.getCount());

                //alert('Mode'+change_seting_mode);
                SubmitVMSettings(mgd_node,action,general_panel,backup_panel,bootparams_panel,ha_panel,
                    node_id,group_id,dom_id,image_id,misc_recs,provision_recs,vm_config,
                    change_seting_mode, quiescent_script_option_store, vm_id);

                disk_details_panel.destroy();
                network_details_panel.destroy();
            }
        }
    });

    var button_prev=new Ext.Button({
        id: 'move-prev',
        //text: _('Prev'),
        disabled: true,
        icon:'icons/2left.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                process_panel(card_panel,treePanel,-1);
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
                process_panel(card_panel,treePanel,1);
            }
        }
    });


    // card panel for all panels
    var card_panel=new Ext.Panel({
        width:435,
        height:390,
        layout:"card",
        id:"card_panel",
        //        activeItem:0,
        cls: 'whitebackground',
        border:false,
        bbar:[
        {
            xtype: 'tbfill'
        },button_prev,button_next,button_ok,button_cancel],
        items:[general_details_panel,disks_panel,network_panel,bootparams_details_panel
            ,miscellaneous_panel, backup_details_panel, credential_details_panel]
    //
    });


    var right_panel=new Ext.Panel({
        id:"right_panel",
        width:448,
        height:600,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[change_settings]
    });



    rootNode.appendChild(generalNode);
    rootNode.appendChild(disksNode);
    rootNode.appendChild(networkNode);
    rootNode.appendChild(bootparamsNode);
    rootNode.appendChild(miscellaneousNode);
    rootNode.appendChild(backupNode);
    rootNode.appendChild(credentialNode);

    treePanel.setRootNode(rootNode);
   

    if(action=="change_vm_settings" ){

        //disks_options.disable();
        //disk_size.disable();
        //file_system.disable();
        ref_disk_location.disable();
        ref_disk_type.disable();
        format.disable();
        //button_prev.hide();
        //button_next.hide();

    }
    if(action=="edit_image_settings"){
       // button_prev.hide();
        //button_next.hide();
    }

    //    alert("memory="+vm_config.inmem_memory);
    var image_id="";


    if (action=="change_vm_settings") {
        general_panel.add(image);
        general_panel.add(server);
        general_panel.add(vmname);
        general_panel.add(vm_config_filename);
        general_panel.add(template_version);
        template_version.setValue(vm_config.template_version);
        memory.setValue(vm_config.memory);
        vcpu.setValue(vm_config.vcpus);
        os_flavor.setValue(vm_config.os_flavor);
        osname=vm_config.os_name;
        os_flavor.fireEvent('select',os_flavor,null,null);
        os_version.setValue(vm_config.os_version);
        allow_backup.setValue(vm_config.allow_backup);
        vm_config_filename.setValue(vm_config.filename);
        username.setValue(vm_config.username);
        password.setValue(vm_config.password);
        ip_address.setValue(vm_config.ip_address);        
        ssh_port.setValue(vm_config.ssh_port);        
        use_ssh_key.setValue(vm_config.use_ssh_key);

        Purge_TextBox.setValue(vm_config.backup_retain_days)

        image.setValue(vm_config.image_name);
        image.setDisabled(true);
        server.setValue(servername);
        server.setDisabled(true);
        vmname.setValue(dom_id);
        vmname.setDisabled(false);
        vm_config_filename.disable();

        boot_loader.setValue(vm_config.bootloader);
        if(vm_config.auto_start_vm!=null){
            auto_start_vm.setValue(vm_config.auto_start_vm);
        }else{
            auto_start_vm.setValue(0);
        }
//        if(vm_config.ha_enabled==1){
//            auto_start_vm.setDisabled(true);
//        }

        kernel.setValue(vm_config.kernel);
        ramdisk.setValue(vm_config.ramdisk);
        root_device.setValue(vm_config.root);
        kernel_args.setValue(vm_config.extra);

        //        right_panel.add(change_settings);
		
        image_id=vm_config.image_id;
		// added by Alex
		available_nws_store.load({
            params:{
                image_id:image_id
            }
        });
        nw_model.load({
            params: {
                image_id: image_id
            }
        });
        //        specify_mac.setVisible(false);
        mac_address.enable();
        ha_panel.add(preferred_server);
        rootNode.appendChild(highAvailabilityNode);
        card_panel.add(ha_details_panel);
        rootNode.appendChild(schedulingNode);
        card_panel.add(scheduling_panel);


    }else if (action =="provision_vm" ){
        image_group.selectedIndex=0;
        image.selectedIndex=0;

        general_panel.add(image_group);
        general_panel.add(image);
        general_panel.add(server_det_panel);
        general_panel.add(vmname);
        general_panel.add(vm_config_filename);
        //general_panel.add(start_vm);
        server.setValue(servername);
        server.setDisabled(true);
        change_settings.disable();

        rootNode.appendChild(highAvailabilityNode);
        card_panel.add(ha_details_panel);

        rootNode.appendChild(schedulingNode);
        card_panel.add(scheduling_panel);

    //rootNode.appendChild(provisioningNode);
    //card_panel.add(provisioning_panel);
    }else if(action=="provision_image"){
        change_settings.disable();
        general_panel.add(image_group);
        general_panel.add(image);
        general_panel.add(server_det_panel);
        general_panel.add(vmname);
        general_panel.add(vm_config_filename);
        image_group.setValue(image_node.parentNode.text);
        image.setValue(image_node.text);
        image.setDisabled(true);
        server.setValue(servername);
        server.setDisabled(true)
        image_group.setDisabled(true);

        image_id=image_node.attributes.nodeid;

        memory.setValue(vm_config.memory);
        vcpu.setValue(vm_config.vcpus);
        os_flavor.setValue(vm_config.os_flavor);
        osname=vm_config.os_name;
        os_flavor.fireEvent('select',os_flavor,null,null);
        os_version.setValue(vm_config.os_version);
        allow_backup.setValue(vm_config.allow_backup);
        vm_config_filename.setValue(vm_config.filename);

        boot_loader.setValue(vm_config.bootloader);
        kernel.setValue(vm_config.kernel);
        ramdisk.setValue(vm_config.ramdisk);
        root_device.setValue(vm_config.root);
        kernel_args.setValue(vm_config.extra);

        rootNode.appendChild(highAvailabilityNode);
        card_panel.add(ha_details_panel);

        rootNode.appendChild(schedulingNode);
        card_panel.add(scheduling_panel);

        //To load "Select Network" combobox
        available_nws_store.load({
            params:{
                image_id:image_id
            }
        });

        //To load "Network Model" combobox
        nw_model.load({
            params:{
                image_id:image_id
            }
        });
        
    //        rootNode.appendChild(provisioningNode);
    //        card_panel.add(provisioning_panel);

    }else if(action=="edit_image_settings"){
        change_settings.disable();
        general_panel.add(image_group);
        general_panel.add(image);
        general_panel.add(template_version);
        //general_panel.add(vm_config_filename);
        if(image_node.parentNode == null){
            image_group.setValue(vm_config.group);
        }else{
            image_group.setValue(image_node.parentNode.text);
        }
        image.setValue(image_node.text);
        image.setDisabled(true);

        image_group.setDisabled(true);

        image_id=image_node.attributes.nodeid;

        //vm_config_filename.setValue(vm_config.filename);
        memory.setValue(vm_config.memory);
        vcpu.setValue(vm_config.vcpus);
//        template_version.setDisabled(true);
        template_version.setValue(vm_config.version);
        os_flavor.setValue(vm_config.os_flavor);
        osname=vm_config.os_name;
        os_flavor.fireEvent('select',os_flavor,null,null);
        os_version.setValue(vm_config.os_version);
        allow_backup.setValue(vm_config.allow_backup);
        //alert(allow_backup.getValue());
        //        vm_config_filename.setDisabled(true);
        //        (function(){
        //            Ext.get("vm_config_filename").setVisible(false);
        //            Ext.get("vm_config_filename").up('.x-form-item').setDisplayed(false);
        //        }).defer(25)

        boot_loader.setValue(vm_config.bootloader);
        kernel.setValue(vm_config.kernel);
        ramdisk.setValue(vm_config.ramdisk);
        root_device.setValue(vm_config.root);
        kernel_args.setValue(vm_config.extra);

        rootNode.appendChild(provisioningNode);
        card_panel.add(provisioning_panel);
        storage_button.setVisible(false);
    }
    disks_type.selectedIndex=0;
    if (state==stackone.constants.RUNNING || state==stackone.constants.PAUSED){
        //        alert(vm_config.inmem_memory);
        inmemory.setValue(true);
        indisk.setValue(false);
        bootparams_panel.disable();
        miscellaneous_panel.disable();
        //        disks_panel.disable();
        //        alert(vm_config);
        memory.setValue(vm_config.inmem_memory);
        vcpu.setValue(vm_config.inmem_vcpus);
    }else if(state==stackone.constants.SHUTDOWN || state==stackone.constants.CRASHED ||
            state==stackone.constants.NOT_STARTED || state==stackone.constants.UNKNOWN ) {
 
        inmemory.disable();
        indisk.setValue(true);
        change_seting_mode="EDIT_VM_CONFIG";
        change_settings.disable();

    }

    // advance settings

    if(action =="change_vm_settings"||action =="edit_image_settings")
    {
        side_panel.enable();

    }else{
        side_panel.enable();
    //adv_show.disable();
    }

    if (action==='edit_image_settings'){
        provisioning_store.load({
            params:{
                image_id:image_id
            }
        });

        //To load "Select Network" combobox when editing template
        available_nws_store.load({
            params:{
                image_id:image_id
            }
        });

        //To load "Network Model" combobox when editing template
        nw_model.load({
            params:{
                image_id:image_id
            }
        });


    }
    if(action=="change_vm_settings" || action=="provision_image"||action=="edit_image_settings"){
        if(vm_config.bootloader!=null && vm_config.bootloader.length>0){
            boot_chkbox.setValue(true);
            bootparams_panel.getComponent("kernel").disable();
            bootparams_panel.getComponent("ramdisk").disable();
        }else{
            boot_chkbox.setValue(false);
            boot_loader.setValue("/usr/bin/pygrub");
            boot_loader.disable();
        }


        miscellaneous_store.load({
            params:{
                image_id:image_id,
                node_id:node_id,
                dom_id:dom_id,
                group_id:group_id,
                action:action
            }
        });

        disks_store.load({
            params:{
                image_id:image_id,
                mode:action,
                node_id:node_id,
                dom_id:dom_id,
                group_id:group_id,
                action:action
            }
        });
        network_store.load({
            params:{
                image_id:image_id,
                //                        mode:action,
                dom_id:dom_id,
                node_id:node_id
            }
        });
    }
    if(action=="provision_image"){
        provisioning_store.load({
            params:{
               image_id:image_id
            }
        });
    }


    var outerpanel=new Ext.FormPanel({
        width:900,
        height:440,
        autoEl: {},
        layout: 'column',
        items:[side_panel,right_panel]

    });



    general_panel.add(memory);
    general_panel.add(vcpu);
    general_panel.add(os_flavor);
    general_panel.add(os_name);
    general_panel.add(os_version);
    //general_panel.add(allow_backup);
    
//    if (action =="provision_vm" || action =="provision_image"){
//        general_panel.add(start_vm);
//    }
    if (action!='edit_image_settings'){
        general_panel.add(auto_start_vm);
    }
//    if(action==='edit_image_settings'){
//
//    }
    
    right_panel.add(card_panel);
    //alert(card_panel.getLayout());
    card_panel.activeItem = 2;
    card_panel.activeItem = 0;
    return outerpanel;

}


function schedule_time(vm_config,state,action){

    var start_msg_lbl=new Ext.form.Label({
         html:'<b>'+ _("开始:") +'</b><br/>'
     });
    var restart_msg_lbl=new Ext.form.Label({
         html:'<b>'+ _("重启:") +'</b><br/>'
     });
    var prov_msg_lbl=new Ext.form.Label({
         html:'<b>'+ _("部署:") +'</b>'
     });

    var end_msg_lbl=new Ext.form.Label({
         html:'<b>'+ _("过期:") +'</b><br/>'
     });
    
    var prov_panel=panel_component("provision",prov_msg_lbl,action,state,vm_config);

    var prov_mainpanel=new Ext.Panel({
        collapsible: false,
        border:false,
        width:"100%",
        id:"prov_mainpanel",
//        bodyStyle:'padding-left:10px',
        items: [prov_panel]
        });

    var start_panel=panel_component("start",start_msg_lbl,action,state,vm_config);

    var start_mainpanel=new Ext.Panel({
        collapsible: false,
        border:false,
        width:"100%",
        id:"start_mainpanel",
//        bodyStyle:'padding-left:10px',
        items: [start_panel]
        });

    var restart_panel=panel_component("restart",restart_msg_lbl,action,state,vm_config);
    var restart_mainpanel=new Ext.Panel({
        collapsible: false,
        border:false,
        width:"100%",
        id:"restart_mainpanel",
//        bodyStyle:'padding-left:10px',
        items: [restart_panel]
        });

    var retire_panel=panel_component("retire",end_msg_lbl,action,state,vm_config);
    var retire_mainpanel=new Ext.Panel({
        collapsible: false,
        border:false,
        width:"100%",
        id:"end_mainpanel",
//        bodyStyle:'padding-left:10px',
        items: [retire_panel]
        });


    var on_retire_store = new Ext.data.JsonStore({
        url: '/node/get_schedule_values?type=on_retire',
        root: 'sch_values',
        fields: ['id','value'],
        sortInfo:{
            field:'value',
            direction:'DESC'
        },
        successProperty:'success',
        listeners:{
            load:function(obj,resc,f){

            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    }
    );
    on_retire_store.load();

    var on_retire=new Ext.form.ComboBox({
                id:"on_retire",
                width: 70,
                fieldLabel: _('<b>过期<b>'),
                allowBlank:false,
                triggerAction:'all',
                store:on_retire_store,
                displayField:'value',
                valueField:'id',
                forceSelection: true,
                mode:'local',
                listWidth:70
      });
      var dummy_panel=new Ext.Panel({
        border:false,
        height:10,
        id:"_dummy"
     });

     var onretire_mainpanel=new Ext.Panel({
        border:false,
        width:"100%",
        id:"onretire_mainpanel",
        layout:'form',
//        bodyStyle:'padding-left:30px',
        items:[on_retire,dummy_panel]
        });
    var email_msg_lbl=new Ext.form.Label({
         html:'<b>'+ _("通知:") +'</b><br/>'
     });
     var email_panel=create_email_panel(vm_config);
     var email_mainpanel=new Ext.Panel({
        border:false,
        width:"100%",
        hidden:true,
        id:"email_mainpanel",
        bodyStyle:'padding-left:60px',
        items: [onretire_mainpanel,email_msg_lbl,email_panel]
        });

    var scheduling_in_panel =new Ext.Panel({
        height:'100%',
        layout:"form",
        frame:false,
        width:'100%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-left:10px',
        items:[prov_mainpanel,start_mainpanel,restart_mainpanel,retire_mainpanel,email_mainpanel]
    });
    Ext.getCmp("on_retire").setValue("Shutdown");
    if(vm_config!=null && vm_config.on_retire){
        Ext.getCmp("on_retire").setValue(vm_config.on_retire);
    }

    return scheduling_in_panel;

}
function check_date(chk_date,chk_time,name){
   var msg="";
   var date=new Date();
   var prov_on=Ext.getCmp("provision_combo").getValue();
   var start_on=Ext.getCmp("start_combo").getValue();
   var time;
   if (chk_time!=null)
       time=chk_time.split(":");
   if (chk_date!=null)
       chk_date.setHours(time[0], time[1]);
   var flag=false;

   if (prov_on=="Later"){
        var prov_date=Ext.getCmp("provision_schdate").getValue();
        var prov_time=Ext.getCmp("provision_schtime").getRawValue();
        if (prov_date=="" || prov_time==""){
            msg="Select values for provision date and time";
            Ext.MessageBox.alert(_("Error"),msg);
            return msg;
        }
        var ptime=prov_time.split(":");
        prov_date.setHours(ptime[0], ptime[1]);
        if (chk_date<=prov_date){
            flag=true;
        }
    }
    else if(prov_on=="Now" && chk_date<=date)
          flag=true;
   if (start_on=="Later"){
        var start_date=Ext.getCmp("start_schdate").getValue();
        var start_time=Ext.getCmp("start_schtime").getRawValue();
//        if (start_date=="" || start_time==""){
//            msg="Select values for start date and time";
//            Ext.MessageBox.alert(_("Error"),msg);
//            return msg;
//        }
        var sttime=start_time.split(":");
        if(start_date!==""){
            start_date.setHours(sttime[0], sttime[1]);
            if (chk_date<=start_date){
                flag=true;
            }
        }
    }
    if(start_on=="On Provisioning" && chk_date<=date)
          flag=true;
    if(flag){
            msg=name +" time should be after start time";
            Ext.MessageBox.alert(_("Error"),msg);
            return msg;
    }
   return msg;

}

function create_email_panel(vm_config){    
    var email_lbl=new Ext.form.Label({
         html: _("邮箱")
     });
    var email_id=new Ext.form.TextField({
        boxLabel: _('邮箱:'),
        name: 'email_id',
        hideLabel:true,
        width: 200,
        id: 'email_id'

    });

   var email_id_panel=new Ext.Panel({
        height:30,
        border:false,
        width:480,
        labelAlign:'right',
        layout:'table',
        labelSeparator:' ',
        layoutConfig: {columns:2},
        id:"email_id_panel",
        items: [
        {
            width: 70,
            layout:'form',
            border:false,
            items:[email_lbl]
        },
        {
            width: 200,
            layout:'form',
            border:false,
            items:[email_id]
        }]
   });

    var notify_panel=create_notify_panel(vm_config);
    var repeat_panel=create_repeat_panel(vm_config);

    var email_notification_panel=new Ext.Panel({
        border:false,
        height:"100%",
        width:"97%",
        id:"email_notification_panel",
        bodyStyle:'padding-right:10px',
        items: [email_id_panel,notify_panel,repeat_panel]
     });

      if (vm_config!=null && vm_config.email_id!=null){
          email_id.setValue(vm_config.email_id);
      }

     return email_notification_panel;

}
function create_notify_panel(vm_config){

    var email_lbl=new Ext.form.Label({
         html: _("通知&nbsp;&nbsp;&nbsp;&nbsp;提前")
     });
    var days=new Ext.form.NumberField({
        name: 'days',
        hideLabel:true,
        width: 50,
        id: 'days'

    });
    var day_lbl=new Ext.form.Label({
         html: _("&nbsp;&nbsp;天")
     });
    /*var hours=new Ext.form.NumberField({
        name: 'hours',
        hideLabel:true,
        width: 50,
        id: 'hours'

    });*/
    var hr_lbl=new Ext.form.Label({
         html: _("")
     });

    var email_notify_panel=new Ext.Panel({
        height:30,
        border:false,
        width:480,
        labelAlign:'right',
        layout:'table',
        labelSeparator:' ',
        layoutConfig: {columns:5},
        id:"email_notify_panel",
        items: [
        {
            width: 70,
            layout:'form',
            border:false,
            items:[email_lbl]
        },
        {
            width: 50,
            layout:'form',
            border:false,
            items:[days]
        }
        ,
        {
            width: 38,
            layout:'form',
            border:false,
            items:[day_lbl]
        }
        ,
        /*{
            width: 50,
            layout:'form',
            border:false,
            items:[hours]
        }
        ,*/
        {
            width: 160,
            layout:'form',
            border:false,
            items:[hr_lbl]
        }

    ]
   });
   if (vm_config!=null && vm_config.days_before!=null){
          days.setValue(vm_config.days_before);
    }
   /*if (vm_config!=null && vm_config.hours_before!=null){
          hours.setValue(vm_config.hours_before);
    }*/
   return email_notify_panel;
}

function create_repeat_panel(vm_config){

    var email_repeat=new Ext.form.Label({
         html: _("提醒频率")
     });
    var rep_hours=new Ext.form.NumberField({
        name: 'rep_hours',
        hideLabel:true,
        width: 50,
        id: 'rep_hours'

    });
     var hr_lbl=new Ext.form.Label({
         html: _("&nbsp;&nbsp;小时")
     });
    /*var rep_min=new Ext.form.NumberField({
        name: 'rep_min',
        hideLabel:true,
        width: 50,
        id: 'rep_min'

    });*/
    /*var min_lbl=new Ext.form.Label({
         html: _("&nbsp;min")
     });*/

   var email_repeat_panel=new Ext.Panel({
        height:30,
        border:false,
        width:480,
        labelAlign:'right',
        layout:'table',
        labelSeparator:' ',
        layoutConfig: {columns:5},
        id:"email_repeat_panel",
        items: [
        {
            width: 70,
            layout:'form',
            border:false,
            items:[email_repeat]
        },
        {
            width: 50,
            layout:'form',
            border:false,
            items:[rep_hours]
        }
        ,
        {
            width: 160,
            layout:'form',
            border:false,
            items:[hr_lbl]
        }
        /*,
        {
            width: 50,
            layout:'form',
            border:false,
            items:[rep_min]
        }
        ,
        {
            width: 150,
            layout:'form',
            border:false,
            items:[min_lbl]
        }*/

    ]
   });
   if (vm_config!=null && vm_config.rep_hours!=null){
          rep_hours.setValue(vm_config.rep_hours);
    }
   /*if (vm_config!=null && vm_config.hours_before!=null){
          rep_min.setValue(vm_config.rep_min);
    }*/
   return email_repeat_panel;
}
function panel_component(panel_id,lbl,action,state,vm_config){
    var date=new Date();
    var hrs=date.getHours();
    var mins=date.getMinutes();
    var mod=(mins+5)-(mins%5);
    var time=hrs+":"+((mod<10)?"0":"")+mod;

    var sch_store = new Ext.data.JsonStore({
        url: '/node/get_schedule_values',
        root: 'sch_values',
        fields: ['id','value'],
        sortInfo:{
            field:'value',
            direction:'DESC'
        },
        successProperty:'success',
        listeners:{
            load:function(obj,rec,f){
                if(panel_id=="retire"){
                     sch_store.sort("id","ASC");
                }
                if(panel_id=="start" && action=="change_vm_settings"){
                    sch_store.removeAt(0);
//                    sch_store.getAt(0).set("id","Later");
                    sch_store.getAt(0).set("value","Schedule");
                }
                if(panel_id=="restart" && action=="change_vm_settings"){
//                    sch_store.removeAt(0);
                    sch_store.getAt(0).set("value","Schedule");
                }
                if(panel_id=="start"){
                     sch_store.sort("id","ASC");
                     Ext.getCmp("start_schdate").setValue("");
                     Ext.getCmp("start_schtime").setValue("");
                }
                if(panel_id=="restart"){
                     sch_store.sort("id","ASC");
                     Ext.getCmp("restart_schdate").setValue("");
                     Ext.getCmp("restart_schtime").setValue("");
                }
                //alert(sch_store.getAt(0).get('id'));
                Ext.getCmp(panel_id+"_combo").setValue(sch_store.getAt(0).get('id'));

                if(panel_id=="retire"){
                      Ext.getCmp("retire_schdate").setValue("");
                      Ext.getCmp("retire_schtime").setValue("");
                }

               if (vm_config!=null && vm_config.start_time!=null && panel_id=="start"){
//                      Ext.getCmp("start_combo").setValue("Schedule");
                      Ext.getCmp("start_combo").fireEvent('select',Ext.getCmp("start_combo"),
                        sch_store.getAt(0),0);
                      set_date_time(Ext.getCmp("start_schdate"),Ext.getCmp("start_schtime"),
                        vm_config.start_time);
                }else{
                      Ext.getCmp("start_combo").fireEvent('select',Ext.getCmp("start_combo"),
                        sch_store.getAt(0),0);
                }
               if (vm_config!=null && vm_config.restart_time!=null && panel_id=="restart"){
//                      Ext.getCmp("start_combo").setValue("Schedule");
                      Ext.getCmp("restart_combo").fireEvent('select',Ext.getCmp("restart_combo"),
                        sch_store.getAt(0),0);
                      set_date_time(Ext.getCmp("restart_schdate"),Ext.getCmp("restart_schtime"),
                        vm_config.restart_time);
                }else{
                      Ext.getCmp("restart_combo").fireEvent('select',Ext.getCmp("restart_combo"),
                        sch_store.getAt(0),0);

                }

                if ( vm_config!=null && vm_config.retire_time!=null && panel_id=="retire"){
                      Ext.getCmp("retire_combo").setValue("Specific Date");
                      Ext.getCmp("retire_combo").fireEvent('select',Ext.getCmp("retire_combo"),
                      sch_store.getAt(1),0);
                      set_date_time(Ext.getCmp("retire_schdate"),Ext.getCmp("retire_schtime"),
                        vm_config.retire_time);
                }

                if (panel_id=="start" && action=="change_vm_settings"){
                    if (vm_config!=null && vm_config.start_time==null ){
                           Ext.getCmp("start_schdate").setValue("");
                           Ext.getCmp("start_schtime").setValue("");
                    }
                }

            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    }
    );
    sch_store.load({
        params:{
             type:panel_id
          }
    });

    var combo=new Ext.form.ComboBox({
                id:panel_id+"_combo",
                width: 100,
                fieldLabel: _(''),
                allowBlank:false,
                triggerAction:'all',
                store:sch_store,
                displayField:'value',
                valueField:'id',
                forceSelection: true,
                mode:'local',
                hideLabel:true,
                listWidth:100,
                listeners:{
                    select:function(combo,record,index){
                         var type=record.get('id');
                        if (panel_id=="retire"){
                            if (type=="Specific Date"){
                                Ext.getCmp("email_mainpanel").setVisible(true);
//                                Ext.getCmp("retire_schdate").enable();
//                                Ext.getCmp("retire_schtime").enable();
                                Ext.getCmp("retire_datelbl").setVisible(true);
                                Ext.getCmp("retire_timelbl").setVisible(true);
                                Ext.getCmp("retire_schdate").setVisible(true);
                                Ext.getCmp("retire_schtime").setVisible(true);
                            }else if(type=="Never"){
                                Ext.getCmp("email_mainpanel"). setVisible(false);
//                                Ext.getCmp("retire_schdate").disable();
//                                Ext.getCmp("retire_schtime").disable();
                                Ext.getCmp("retire_datelbl").setVisible(false);
                                Ext.getCmp("retire_timelbl").setVisible(false);
                                Ext.getCmp("retire_schdate").setVisible(false);
                                Ext.getCmp("retire_schtime").setVisible(false);
                            }
                        }

                        if (panel_id=="provision"){
                            if (type=="Later"){
//                                Ext.getCmp("provision_schdate").enable();
//                                Ext.getCmp("provision_schtime").enable();
                                Ext.getCmp("provision_datelbl").setVisible(true);
                                Ext.getCmp("provision_timelbl").setVisible(true);
                                Ext.getCmp("provision_schdate").setVisible(true);
                                Ext.getCmp("provision_schtime").setVisible(true);

                            }else if(type=="Now"){
//                                Ext.getCmp("provision_schdate").disable();
//                                Ext.getCmp("provision_schtime").disable();
                                Ext.getCmp("provision_datelbl").setVisible(false);
                                Ext.getCmp("provision_timelbl").setVisible(false);
                                Ext.getCmp("provision_schdate").setVisible(false);
                                Ext.getCmp("provision_schtime").setVisible(false);
                            }
                        }

                        if(panel_id=="start"){
                            if (type=="Later"){
//                                Ext.getCmp("start_schdate").enable();
//                                Ext.getCmp("start_schtime").enable();
                                Ext.getCmp("start_datelbl").setVisible(true);
                                Ext.getCmp("start_timelbl").setVisible(true);
                                Ext.getCmp("start_schdate").setVisible(true);
                                Ext.getCmp("start_schtime").setVisible(true);
                            }else if(type=="On Provisioning"){
//                                Ext.getCmp("start_schdate").disable();
//                                Ext.getCmp("start_schtime").disable();
                                Ext.getCmp("start_datelbl").setVisible(false);
                                Ext.getCmp("start_timelbl").setVisible(false);
                                Ext.getCmp("start_schdate").setVisible(false);
                                Ext.getCmp("start_schtime").setVisible(false);
                            }
                        }
                          if(panel_id=="restart"){
                            if (type=="Later"){
                                Ext.getCmp("restart_datelbl").setVisible(true);
                                Ext.getCmp("restart_timelbl").setVisible(true);
                                Ext.getCmp("restart_schdate").setVisible(true);
                                Ext.getCmp("restart_schtime").setVisible(true);
                            }
                        }

                 }
                }
      });
    var date_lbl=new Ext.form.Label({
        id:panel_id+"_datelbl",
        html:_('日期:')+"&nbsp;"
        ,hidden:true
    });
    var time_lbl=new Ext.form.Label({
        id:panel_id+"_timelbl",
        html:_('时间:')+"&nbsp;"
        ,hidden:true
    });
     var schdate=new Ext.form.DateField({
        fieldLabel: _('日期'),
        name: panel_id+'_schdate',
        hideLabel:true,
//        disabled:true,
        width: 80,
        anchor:'100%',
        minValue:date,
        format:'m/d/Y',
        id: panel_id+'_schdate',
        value:date
        ,hidden:true,
        listeners:{
            select : function(combo,record,index ) {
                    if (panel_id=="retire")
                        check_date(schdate.getValue(),schtime.getRawValue(),_("retire"));
            }
        }
    });
    var schtime=new Ext.form.TimeField({
        fieldLabel: _('时间'),
        name:panel_id+'_schtime',
//        disabled:true,
        hideLabel:true,
        format:'H:i',
        anchor:'100%',
        id: panel_id+'_schtime',
//        minValue:time,
        value:time,
        increment:5,
        width:50,
        listWidth:60,
        maxHeight:80
        ,hidden:true,
        listeners:{
            select : function(combo,record,index ) {
                    if (panel_id=="retire")
                    check_date(schdate.getValue(),schtime.getRawValue(),_("retire"));
            }
        }
    });
    var dummy_panel=new Ext.Panel({
        border:false,
        height:10,
        id:panel_id+"_dummy"
     });

       var panel=new Ext.Panel({
        height:30,
        border:false,
        width:480,
        labelAlign:'right',
        layout:'table',
        labelSeparator:' ',
        layoutConfig: {columns:6},
        id:panel_id,
        items: [
         {
            width: 63,
            layout:'form',
            border:false,
            items:[lbl]
        },
        {
            width: 120,
            layout:'form',
            border:false,
            items:[combo]
        },
        {
            width: 35,
            layout:'form',
            border:false,
            items:[date_lbl]
        },
        {
            width: 100,
            layout:'form',
            border:false,
            items:[schdate]
        },
          {
            width: 35,
            layout:'form',
            border:false,
            items:[time_lbl]
        },{
            width: 70,
            layout:'form',
            border:false,
            items:[schtime]
        }]

    });
    var m_panel=new Ext.Panel({
        border:false,
        height:"100%",
        width:"100%",
        id:panel_id+"_mp",
        items:[panel,dummy_panel]
     });

      if ((panel_id=="start") && (state==stackone.constants.RUNNING || state==stackone.constants.PAUSED)){
              combo.disable();

              date_lbl.setVisible(false);
              schdate.setVisible(false);
              schdate.disable();
              time_lbl.setVisible(false);
              schtime.setVisible(false);
              schtime.disable();
       }
       if(action!="provision_vm" && action!="provision_image"){
//              Ext.getCmp("provision_schdate").disable();
//              Ext.getCmp("provision_schtime").disable();
              Ext.getCmp("provision_combo").disable();
              Ext.getCmp("provision_datelbl").setVisible(false);
              Ext.getCmp("provision_timelbl").setVisible(false);
              Ext.getCmp("provision_schdate").setVisible(false);
              Ext.getCmp("provision_schtime").setVisible(false);
       }
    return m_panel;
}

function format_date_value(value){
      var pad_zero="0";
      if (value.length<2)
          value=pad_zero+value;
      return value;
}
function set_date_time(schdate,schtime,value){
      var st_date=new Date(value);
      var month=format_date_value(String(st_date.getMonth()+1));
      var day=format_date_value(String(st_date.getDate()));

      var date_toset=month+"/"+day+"/"+st_date.getFullYear();

      var hours=format_date_value(String(st_date.getHours()));
      var minutes=format_date_value(String(st_date.getMinutes()));

      var time_toset=hours+":"+minutes;

      schdate.setValue(date_toset);
      schtime.setValue(time_toset);
}

function process_panel(panel,treePanel,value,type)
{

    var root_node=treePanel.getNodeById("rootnode");
    var children=root_node.childNodes;
    var selected_node_id;
    var node_ids=new Array();
        for(var i=0;i<children.length;i++){
            node_ids[i]=children[i].attributes.id;
            if(type=="treepanel"){
                if(node_ids[i].substr(4,node_ids[i].length)==value)
                    selected_node_id=node_ids[i];
            }
            else{
                var current_selected_nodeid=treePanel.getSelectionModel().getSelectedNode().attributes.id;
                if(node_ids[i]==current_selected_nodeid){
                    selected_node_id=children[parseInt(i)+parseInt(value)].attributes.id;
                }
            }
        }

    if(selected_node_id==children[0].attributes.id){
        panel.getBottomToolbar().items.get('move-prev').disable();
    }else{
        panel.getBottomToolbar().items.get('move-prev').enable();
    }
    if (selected_node_id==children[children.length-1].attributes.id){
        panel.getBottomToolbar().items.get('move-next').disable();
    }else{
        panel.getBottomToolbar().items.get('move-next').enable();
    }

    panel.getLayout().setActiveItem("panel"+selected_node_id.replace("node",""));
    treePanel.getNodeById(selected_node_id).select();
}
function boot_loader_check(bootparams_panel,boot_loader,checked){
    if (checked==true){
        boot_loader.enable();
        bootparams_panel.getComponent("kernel").disable();
        bootparams_panel.getComponent("ramdisk").disable();
    }
    else{
        boot_loader.disable();
        bootparams_panel.getComponent("kernel").enable();
        bootparams_panel.getComponent("ramdisk").enable();
    }
}
function radio_check(bootparams_panel,miscellaneous_panel,disks_panel,checked){
    if (checked==true){
        bootparams_panel.disable();
        miscellaneous_panel.disable();
    //        disks_panel.disable();
    }
    else{
        bootparams_panel.enable();
        miscellaneous_panel.enable();
    //        disks_panel.enable();
    }

}

function show_disk_checkbox (value,params,record){
    var id = Ext.id();
    (function(){
        new Ext.form.Checkbox({
            renderTo: id,
            checked:value,
            width:100,
            height:16,
            disabled:true,
            id:"disk_share_check",
            listeners:{
                check:function(field,checked){
                    if(checked==true){
                        record.set('shared',true);
                    }else{
                        record.set('shared',false);
                    }
                }
            }
        });
    }).defer(5)
    return '<span id="' + id + '"></span>';
}
function SubmitVMSettings(node,action,general_panel,backup_panel,bootparams_panel,ha_panel,
        node_id,group_id,dom_id,image_id,misc_recs,
            provision_recs,vm_config,mode, quiescent_script_option_store, vm_id){


    //    dgrid.getRange(0,dgrid.getCount());
    var filename="";
    //alert(general_panel.getComponent('vm_config_filename'));
    if (general_panel.getComponent('vm_config_filename'))
        filename=general_panel.getComponent('vm_config_filename').getValue();
    var memory=general_panel.getComponent('memory').getValue();
    var vcpus=general_panel.getComponent('vcpu').getValue();
    var disk_grid=Ext.getCmp("disks_grid");
    var disk_store=disk_grid.getStore();
    var colModel=disk_grid.getColumnModel();
    var len=colModel.getColumnCount();

    var network_grid=Ext.getCmp("network_grid");
    var network_store=network_grid.getStore();
    var net_colModel=network_grid.getColumnModel();
    var net_len=net_colModel.getColumnCount();

    var general_object=new Object();
    var boot_params_object=new Object();
    var misc_object=new Object();
    var provision_object=new Object();
    var storage_status_object=new Object();
    var network_object=new Object();
    var backup_object=new Object();
    var high_avail_object=new Object();
    var scheduling_object=new Object();

    var os_flavor=general_panel.getComponent('os_flavor').getValue();
    var os_name=general_panel.getComponent('os_name').getRawValue();
    //var allow_backup = general_panel.getComponent('allow_backup').getValue();
    var os_version=general_panel.getComponent('os_version').getValue();
    var preferred_nodeid;

    if (general_panel.getComponent('server_det_panel')!=null){
        var server_preferred=general_panel.getComponent('server_det_panel').items.get("server_prefer").getValue();
        if ((action=="provision_vm"||action=="provision_image") && server_preferred){
            preferred_nodeid=node_id;
        }
    }
    var disk_name=dom_id;
    var vm_name="";
    var version="";
    
    if(action=="change_vm_settings"){
        vm_name=general_panel.getComponent('vmname').getValue();
        version=general_panel.getComponent('template_version').getValue();
        preferred_nodeid=ha_panel.getComponent('preferred_server').getValue();

        action=mode;
    }else if(action=="provision_vm"||action=="provision_image"){
        action="PROVISION_VM";
        vm_name=general_panel.getComponent('vmname').getValue();
        disk_name=vm_name;
//        var start_checked=general_panel.getComponent('start_vm').getValue();
//        if(start_checked == true)
//            start_checked='yes';
//        else
//            start_checked='no';
    }else if(action=="edit_image_settings"){
        action="EDIT_IMAGE";
    }

    var auto_start_vm=0;
    if(action!='EDIT_IMAGE'){
        auto_start_vm=general_panel.getComponent('auto_start_vm').getValue();
        if(auto_start_vm == true)
            auto_start_vm=1;
        else
            auto_start_vm=0;
    }
    //
    var disk_stat="[";
    for(var i=0;i<disk_store.getCount();i++){
        disk_stat+="{";
        for(var j=0;j<len;j++){
            var fld=colModel.getDataIndex(j);
            disk_stat+="'"+fld+"':";
            var val=disk_store.getAt(i).get(fld);

            if(val===""){
                disk_stat+="'"+disk_store.getAt(i).get(fld)+"'";
            }else if (val==null) {
                disk_stat+=null;
            //                alert(val+"---"+(val==null));
            }else if (!(isNaN(val))){
                disk_stat+=disk_store.getAt(i).get(fld);
            }else{
                if(fld=="filename" && action!="EDIT_IMAGE"){
                    val=disk_store.getAt(i).get(fld).replace("$VM_NAME",disk_name);
                    disk_stat+="'"+val+"'";
                }else{
                    var value=disk_store.getAt(i).get(fld);
                    if (fld=="type")
                        value=value.replace(" ","")
                    disk_stat+="'"+value+"'";
                }
            }
            disk_stat+=(j==(len-1))?"":",";
        }
        disk_stat+="}";
        
        if (i!=disk_store.getCount()-1)
            disk_stat+=",";
    }
    disk_stat+="]";
    //    alert(disk_stat);

    var disk_jdata= eval("("+disk_stat+")");

    storage_status_object.disk_stat=disk_jdata;

    var vif="["
    for(i=0;i<network_store.getCount();i++){
        //        for(j=0;j<net_len;j++){
        //            var net_fld=net_colModel.getDataIndex(j);
        vif+="{ mac:'"+network_store.getAt(i).get("mac")+"'";
        vif+=","
        vif+="bridge:'"+network_store.getAt(i).get("bridge")+"'";
        vif+=","
        vif+="name:'"+network_store.getAt(i).get("name")+"'";
        vif+=","
        vif+="nw_id:'"+network_store.getAt(i).get("nw_id")+"'";
        vif+=" }"
        //        }
        if (i!=network_store.getCount()-1)
            vif+=","
    }
    vif+="]"
    //    alert(vif);
    //vif= eval("("+vif+")");
    vif=Ext.util.JSON.decode(vif);

    network_object.network=vif;
    //    alert(network_object.network);




    var boot_loader=bootparams_panel.getComponent('boot_check_group').items.get('boot_loader').getValue();
    var boot_check=bootparams_panel.getComponent('boot_check_group').items.get('boot_check').getValue();
    var kernel=bootparams_panel.getComponent('kernel').getValue();
    var ramdisk=bootparams_panel.getComponent('ramdisk').getValue();
    var extra=bootparams_panel.getComponent('kernel_args').getValue();
    var root=bootparams_panel.getComponent('root_device').getValue();
    var on_reboot=bootparams_panel.getComponent('on_reboot').getValue().toLowerCase();
    var on_crash=bootparams_panel.getComponent('on_crash').getValue().toLowerCase();
    var on_shutdown=bootparams_panel.getComponent('on_shutdown').getValue().toLowerCase();

    var vm_priority=ha_panel.getComponent('prior_panel').items.itemAt(0).items.get("vm_prior").getValue();
    //    alert(boot_loader+ "--" +boot_check);

    var params;
    var url;
    var ajaxReq;

    for(var i=0;i<misc_recs.length;i++){
        var attribute=misc_recs[i].get("attribute");
        var misc_value="";

        misc_value=process_value(misc_recs[i].get("value"));
        if(attribute!=""){
            try{
                eval('misc_object.'+attribute+'='+misc_value);
            }catch(ex){
                Ext.MessageBox.alert(_('错误'), _('无效的属性值: <b>'+attribute+ '</b> '));
                return;
            }
        }
    }

    for(i=0;i<provision_recs.length;i++){
        attribute=provision_recs[i].get("attribute");
        var prov_value=process_value(provision_recs[i].get("value"));
        if(attribute!=""){
            try{
                eval('provision_object.'+attribute+'='+prov_value);
            }catch(ex){
                Ext.MessageBox.alert(_('错误'), _('无效的属性值: <b>'+attribute+ '</b> '));
                return;
            }
        }
    }

    general_object.filename=filename;
    general_object.memory=memory;
    general_object.vcpus=vcpus;
//    general_object.start_checked=start_checked;
//    general_object.update_version=update_version;
    general_object.template_version=version;
    general_object.preferred_nodeid=preferred_nodeid;
    //    vm_config.memory=memory;
    //    vm_config.vcpus=vcpus;

    general_object.os_flavor=os_flavor;
    general_object.os_name=os_name;
    general_object.os_version=os_version;
    general_object.auto_start_vm=auto_start_vm;
    //general_object.allow_backup = allow_backup;
    //alert(os_flavor+"--"+os_name+"--"+os_version);

    boot_params_object.boot_check=boot_check;
    if(boot_check==true){
        boot_params_object.boot_loader=boot_loader;
    }else{
        boot_params_object.kernel=kernel;
        boot_params_object.ramdisk=ramdisk;
    }

    boot_params_object.extra=extra;
    boot_params_object.root=root;

    boot_params_object.on_reboot=on_reboot;
    boot_params_object.on_crash=on_crash;
    boot_params_object.on_shutdown=on_shutdown;

    high_avail_object.vm_priority=vm_priority;

    //    vm_config.kernel=kernel;
    //    vm_config.ramdisk=ramdisk;
    //    vm_config.on_reboot=on_reboot;
    //    vm_config.on_crash=on_crash;

    

//     var quiescent_script_option_store= quiescent_script_option_store;
    //var quiescent_script_option_store= Ext.getCmp("quiescent_script_option_store");
    //var backupconfig_list_grid=backup_panel.getComponent('backupconfig_list_grid').
    //quiescent_script_option_store.load();
    
    var quiescent_script_stat="{";
    for(var i=0;i<quiescent_script_option_store.getCount();i++){           
        //quiescent_script_stat+="{";
        //quiescent_script_stat+="'backup_id':";
        quiescent_script_stat+="'"+quiescent_script_option_store.getAt(i).get("attribute")+"':";
        //quiescent_script_stat+=", 'backup_all':";
        quiescent_script_stat+="'"+quiescent_script_option_store.getAt(i).get("value")+"'";        
        quiescent_script_stat+=",";
    }
    quiescent_script_stat+="}";
    //alert(quiescent_script_stat);      
    
    var quiescent_script_stat_jdata= eval("("+quiescent_script_stat+")");    
    backup_object.quiescent_script_stat = quiescent_script_stat_jdata;    

    var username = Ext.getCmp("vm_username");
    backup_object.username = username.getValue();
    var password = Ext.getCmp("vm_password");
    backup_object.password = password.getValue()
    var ip_address = Ext.getCmp("ip_address");
    backup_object.ip_address = ip_address.getValue()
    var ssh_port = Ext.getCmp("ssh_port");    
    backup_object.ssh_port = ssh_port.getValue()
    var use_ssh_key = Ext.getCmp("use_ssh_key");
    backup_object.use_ssh_key = use_ssh_key.getValue()
  
    
    
    var backup_retain_days = Ext.getCmp("backup_retain_days");
    backup_object.backup_retain_days = backup_retain_days.getValue()
//     alert(backup_retain_days.getValue());
    


    

    var backupconfig_list_grid= Ext.getCmp("backupconfig_list_grid");
    //var backupconfig_list_grid=backup_panel.getComponent('backupconfig_list_grid').
    var backupconfig_list_store=backupconfig_list_grid.getStore();
    //var backupconfig_list_store= backup_panel.findById('backupconfig_list_store'); 
    
        var backup_stat="[";
        for(var i=0;i<backupconfig_list_store.getCount();i++){ 
            /* var allow_backup_str = "False";  
            if (vm_list_store.getAt(i).get("allow_backup"))
            {
                allow_backup_str = "True";  
            }   */      
            backup_stat+="{";
            backup_stat+="'backup_id':";
            backup_stat+="'"+backupconfig_list_store.getAt(i).get("backup_id")+"'";
            backup_stat+=", 'backup_all':";
            backup_stat+="'"+backupconfig_list_store.getAt(i).get("backup_all")+"'";
            backup_stat+=", 'allow_backup':";
            backup_stat+="'"+backupconfig_list_store.getAt(i).get("allow_backup")+"'";
            backup_stat+="},";
        }
        backup_stat+="]";
        
        var backup_jdata= eval("("+backup_stat+")");
        //alert(vm_jdata);
        backup_object.backup_stat = backup_jdata;    
        //alert(backup_object.backup_stat);    

    var prov_on=Ext.getCmp("provision_combo").getValue();
    scheduling_object.prov_on=prov_on;
    if (prov_on=="Later"){
        var prov_date=Ext.getCmp("provision_schdate").getValue();
        var prov_time=Ext.getCmp("provision_schtime").getRawValue();
        if (prov_date=="" || prov_time==""){
            Ext.MessageBox.alert(_("错误"),"请选择部署的日期和时间");
            return;
        }
        scheduling_object.prov_time=prov_time;
        scheduling_object.prov_date=String(prov_date);
    }



    var start_on=Ext.getCmp("start_combo").getValue();
    if(start_on=="Later"){
        var start_date=Ext.getCmp("start_schdate").getValue();
        var start_time=Ext.getCmp("start_schtime").getRawValue();
        if (start_date!="" & start_time==""){
            Ext.MessageBox.alert(_("错误"),"请选择开始时间");
            return;
        }
        if (start_date=="" & start_time!=""){
            Ext.MessageBox.alert(_("错误"),"请选择开始日期");
            return;
        }
        if (start_date=="" && start_time==""){
            start_on="Never";
        }
        scheduling_object.start_time=start_time;
        scheduling_object.start_date=String(start_date);
    }
    scheduling_object.start_on=start_on;

    var restart_on=Ext.getCmp("restart_combo").getValue();
    if(restart_on=="Later"){
        var restart_date=Ext.getCmp("restart_schdate").getValue();
        var restart_time=Ext.getCmp("restart_schtime").getRawValue();
        if (restart_date!="" & restart_time==""){
            Ext.MessageBox.alert(_("错误"),"请选择重启时间");
            return;
        }
        if (restart_date=="" & restart_time!=""){
            Ext.MessageBox.alert(_("错误"),"请选择重启日期");
            return;
        }
        if (restart_date=="" && restart_time==""){
            restart_on="Never";
        }
        scheduling_object.restart_time=restart_time;
        scheduling_object.restart_date=String(restart_date);
    }
    scheduling_object.restart_on=restart_on;

    var retire=Ext.getCmp("retire_combo").getValue();
    scheduling_object.retire=retire;
    if(retire=="Specific Date"){
          scheduling_object.on_retire=Ext.getCmp("on_retire").getValue();
          var retire_date=Ext.getCmp("retire_schdate").getValue();
          var retire_time=Ext.getCmp("retire_schtime").getRawValue();

          var stat=validate_datetime(retire_date,retire_time,"retire");
          if (!stat)
              return;
        scheduling_object.retire_time=retire_time;
        scheduling_object.retire_date=String(retire_date);
    }

    var email_id=Ext.getCmp("email_id").getValue();
    var email_days_before=Ext.getCmp("days").getValue();
    //var email_hours_before=Ext.getCmp("hours").getValue();
    var email_hours_before='';
    var email_rep_hours=Ext.getCmp("rep_hours").getValue();
    //var email_rep_min=Ext.getCmp("rep_min").getValue();
    var email_rep_min='';

    if(retire=="Specific Date" && !EmailCheck(email_id)){
        Ext.MessageBox.alert(_("错误"),_("请输入一个有效的邮箱"));
        return;
    }
    if (email_days_before=="" || email_days_before==null)
        email_days_before=0;
    if (email_hours_before=="" || email_hours_before==null)
        email_hours_before=0;

    if (email_rep_hours=="" || email_rep_hours==null)
        email_rep_hours=0;
    if (email_rep_min=="" || email_rep_min==null)
        email_rep_min=0;

    scheduling_object.email_id=email_id;
    scheduling_object.email_days_before=email_days_before;
    scheduling_object.email_hours_before=email_hours_before;
    scheduling_object.email_rep_hours=email_rep_hours;
    scheduling_object.email_rep_min=email_rep_min;

    var jsondata= json(general_object,boot_params_object,
        misc_object,provision_object,storage_status_object,
        network_object,backup_object,high_avail_object,scheduling_object);

    params="image_id="+image_id+"&config="+jsondata+"&mode="+action;
    
    if (node_id!=null)
        params+="&node_id="+node_id;
    if (group_id!=null)
        params+="&group_id="+group_id;
    if (vm_id!=null)
        params+="&dom_id="+vm_id;

    if (action=="PROVISION_VM" || action == "EDIT_VM_INFO" || "EDIT_VM_CONFIG")
        params+="&vm_name="+vm_name;
    
    url="/node/vm_config_settings?"+params;    
    if(action == "PROVISION_VM" || action == "EDIT_VM_INFO"){
        closeWindow();
        if(action=="PROVISION_VM"){
            showScheduleWindow(node,_("新建VM"),url,action);
        }else{
            showScheduleWindow(node,_("修改虚拟机设置"),url,action);
        }
    }else if(action=="EDIT_IMAGE"){

        var yes_button= new Ext.Button({
            id: 'yes',
            text: _('是'),
            icon:'icons/accept.png',
            cls:'x-btn-text-icon',
            //                enableToggle:true,
            listeners: {
                click: function(btn) {
                    var version=(update_version_panel.getComponent("new_version").getValue()).toString();
//                    var vert_split=version.split(".");
                    if(!version || isNaN(version) ||version.indexOf(".")==-1||
                    version.split(".")[1].length>1 || (version<1.0))
                    {
                        Ext.MessageBox.alert(_("错误"),
                                _("请输入正确的模板版本. eg:1.2"));
                        return false;
                    }
                    else if(version <= vm_config.version)
                    {
                       Ext.MessageBox.alert(_("错误"),
                                _("新版本必须大于当前版本."));
                        return false;
                    }                   

                    general_object.update_version=true;
                    general_object.new_version=version;
                    var jsondata=json(general_object,boot_params_object,
                    misc_object,provision_object,storage_status_object,network_object, backup_object);
                    params="image_id="+image_id+"&config="+jsondata+"&mode="+action;
                    url="/node/vm_config_settings?"+params;
                    vm_config_settings(node,url,action,vm_config.vm_count,vm_config.old_vmcount,image_id,version,true);
                    closeWindow(windowid,true);
                }
            }
        });
        var no_button= new Ext.Button({
            id: 'no',
            text: _('跳过'),
            icon:'icons/cancel.png',
            cls:'x-btn-text-icon',
            //                enableToggle:true,
            listeners: {
                click: function(btn) {
                    var version=parseFloat(vm_config.version)
                    general_object.update_version=false;
//                    general_object.new_version="";
                    var jsondata= json(general_object,boot_params_object,
                    misc_object,provision_object,storage_status_object,network_object, backup_object);
                    params="image_id="+image_id+"&config="+jsondata+"&mode="+action;
                    url="/node/vm_config_settings?"+params;
                    vm_config_settings(node,url,action,vm_config.vm_count,vm_config.old_vmcount,image_id,version,false);
                    closeWindow(windowid,true);
                }
            }
        });
        var button_panel=new Ext.Panel({
            id:"button_panel",
            layout:"column",
            width:'100%',
            height:50,
            frame:false,
            bodyStyle:"padding-left:60px",
            items: [
            {
                width: 100,
                layout:'form',
                items:[yes_button]
            },
            {
                width: 100,
                layout:'form',
                items:[no_button]
            }]
        });
        var update_version_panel=update_template_version(vm_config);
        var panel=new Ext.Panel({
            id:"button_panel",
            layout:"column",
//            width:270,
            height:360,
            items:[update_version_panel,button_panel]
        });
        var windowid=Ext.id();
        showWindow(_("修改版本"),278,180,panel,windowid);
        closeWindow();//to close the vm settings panel
    }else{
        closeWindow();//to close the vm settings panel
        vm_config_settings(node,url,action);
    }
}

function vm_config_settings(node,url,action,vm_count,old_vmcount,image_id,version,update_version){

     Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: _('请稍候...'),
        width:600,
        wait:true,
        waitConfig: {
            interval:200
        }
    });
    //alert('jsondata:'+jsondata.general_object.start_checked);
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);

            Ext.MessageBox.hide();
            if(response.success){
                var msg="";
                if (action =="EDIT_VM_INFO")
                    msg=_("虚拟机配置任务已经提交");
//                    task_panel_do();
                if (action =="PROVISION_VM"){
                     msg=_("新建VM任务提交");
//                     task_panel_do();
                }
                if(action=="EDIT_IMAGE"){
                    msg=_("模板设置修改成功");
                    if(old_vmcount!=0 || (vm_count != 0 && update_version)){
                        var wid=Ext.id();
                        var panel=show_affected_vms(image_id,wid,version);
                        showWindow(_("Virtual Machines"),300,325,panel,wid,true);
                        return;
                    }
                }
                if(action=="EDIT_VM_CONFIG"){
                    msg=_("虚拟机设置修改成功");
                    node.fireEvent('click',node);
                }


                Ext.MessageBox.alert(_("Status"),msg);
                if (action =="EDIT_VM_INFO" || action =="PROVISION_VM"){
//                    node.fireEvent('click',node);
                }

            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.hide();
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
  }

function set_disklocation(type,disk_context,vm_config_action,disk_mode,change_seting_mode){
    vm_storage_disk_id = null;
    storage_id = null;
    storage_name = null;
    vm_storage_disk_id = disk_context.id;
    vm_storage_allocated = disk_context.storage_allocated;
    vm_name = disk_context.vm_name;
    storage_id = disk_context.storage_id;
    storage_name = disk_context.storage_name;
    volume_group = disk_context.volume_group;

    if (vm_config_action=="provision_vm"||vm_config_action=="provision_image"){
        var option = Ext.getCmp("disks_options").getValue();
        if (option == "CREATE_DISK"){
            if(disk_context.type != "nfs" && disk_context.type != "lvm" && disk_context.type != "cifs" && disk_context.type != "gfs" && disk_context.type != "ocfs"){
                Ext.MessageBox.alert( _("失败") , _("无效的选择：只有在文件系统存储上才可以创建新磁盘。请选择文件系统存储，例如NFS."));
                return false;
            }
        }
        else if (option == "USE_DEVICE"){
            if (disk_context.type == "nfs"){
                Ext.MessageBox.alert( _("失败") , _("无效的选择 :基于文件的存储（NFS）存储不能被选定为现有磁盘。请选择iSCSI或AoE存储."));
                return false;
            }
        }
    } else if (vm_config_action=="change_vm_settings"){
        var option = Ext.getCmp("disks_options").getValue();
        if (option == "CREATE_DISK"){
            if (disk_mode == "NEW") {
                var new_loc = "$STORAGE_" + storage_name + "/$DISK_NAME.disk.xm";
                Ext.getCmp("disk_location").setValue(new_loc);
                if(disk_context.type == "lvm"){
                    Ext.getCmp("disks_type").setValue("lvm");
                } else {
                    Ext.getCmp("disks_type").setValue("file");
                }
            }

            return true;
        }
    }

    if(vm_storage_allocated==true) {
        Ext.MessageBox.alert("失败", "无效的选择: 存储已分配给虚拟机 " + vm_name + ".");
        return false;
    }

    if (disk_context.type == "aoe"){
        Ext.getCmp("disk_location").setValue(disk_context.disk);
        Ext.getCmp("disks_type").setValue("phy");
    }else if(disk_context.type == "iscsi" || disk_context.type == "fc"){
        Ext.getCmp("disk_location").setValue(disk_context.interface);
        Ext.getCmp("disks_type").setValue("phy");
    }else if(disk_context.type == "nfs" || disk_context.type == "lvm" || disk_context.type == "cifs" || disk_context.type == "gfs" || disk_context.type == "ocfs"){
        if (disk_context.name == null && disk_context.disk == null && volume_group != null){  //For lvm
            var d_name = ""
            if (disk_mode == "NEW")
                d_name = "$VM_NAME.disk.xm";
            else{
                var loc = Ext.getCmp("disk_location").getValue();
                if (loc.length>0){
                    var disk_loc_splot=loc.split("/");
                    d_name=disk_loc_splot[disk_loc_splot.length-1];;
                }
            }
            var new_loc = "/dev/" + volume_group + "/" + d_name;
            Ext.getCmp("disk_location").setValue(new_loc);
            Ext.getCmp("disks_type").setValue("phy", "LVM");
        }else if (disk_context.name == disk_context.disk){  //For nfs
            var d_name = ""
            if (disk_mode == "NEW")
                d_name = "$VM_NAME.disk.xm";
            else{
                var loc = Ext.getCmp("disk_location").getValue();
                if (loc.length>0){
                    var disk_loc_splot=loc.split("/");
                    d_name=disk_loc_splot[disk_loc_splot.length-1];;
                }
            }
            var new_loc=disk_context.disk+"/"+d_name;
            //             alert(new_loc);
            Ext.getCmp("disk_location").setValue(new_loc);
            Ext.getCmp("disks_type").setValue("file");
        }else{
            Ext.getCmp("disk_location").setValue(disk_context.disk);
            Ext.getCmp("disks_type").setValue("file");
        }
        //        alert(Ext.getCmp("disks_type").getStore().getAt(0).get('id'));
//        if (Ext.getCmp("disks_type").getStore().getAt(0).get('id') == "phy"){
//            if (change_seting_mode == "EDIT_VM_CONFIG")
//                Ext.getCmp("disks_type").setValue("phy");
//            else
//                Ext.getCmp("disks_type").setValue("file");
//        }
    }
    Ext.getCmp("is_remote").setValue(true);
    return true;
}

function platform_UI_helper(platform,change_seting_mode,flag){
    var components=new stackone.PlatformUIHelper(platform,change_seting_mode).getComponentsToDisable();
    //alert(components.length+"--"+components);
    for(var z=0;z<components.length;z++){
        Ext.getCmp(components[z]).setDisabled(flag);
    }
}
function update_template_version(vm_config){
    var current_version=new Ext.form.TextField({
        fieldLabel: _('当前版本'),
        name: 'current_version',
        width: 80,
        id: 'current_version',
        disabled:true

    });
    var new_version=new Ext.form.TextField({
        fieldLabel: _('新版本'),
        name: 'new_version',
        width: 80,
        id: 'new_version',
        allowDecimals:true

    });
    var label=new Ext.form.Label({
        html:'<div ><b>'+_("如果您已经取得了显著的变化，那么，建议您更改模板的版本.")+'</b></div><br/>'
    });

    var update_version_panel=new Ext.Panel({
        id:"update_version_panel",
        layout:"form",
        width:285,
        height:120,
        frame:false,
        labelWidth:130,
        border:0,
        items:[label,current_version,new_version]
    });
    current_version.setValue(vm_config.version);
    if(Ext.getCmp("template_version").getValue() != vm_config.version){
        var new_vers=Ext.getCmp("template_version").getValue();
        new_version.setValue(new_vers);
     }
    else{
        var new_ver=parseFloat(vm_config.version)+parseFloat(0.1);
        new_ver=new_ver.toFixed(1);
        new_version.setValue(new_ver);
   }
    return update_version_panel;
}

function show_affected_vms(image_id,wid,Version){
    var label=new Ext.form.Label({
        html:'<div class="boldlabelheading"><b>'+_("模板设置修改成功")+'</b></div><br/>'
    });

    var vm_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width: 110,
        dataIndex: 'vm',
        sortable:true
    },

    {
        header: _("服务器"),
        width: 110,
        dataIndex: 'server'
    },
    {
        header: _("版本"),
        width: 50,
        dataIndex: 'template_version'
    }
    ]);


    var vms_store = new Ext.data.JsonStore({
        url: "/template/get_template_version_info?image_id="+image_id,
        root: 'rows',
        fields: ['vmid','vm','server','template_version','node_id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }

        }
    });
    vms_store.load();

    var label2=new Ext.form.Label({
        html:'<div ><b>'+("下面的虚拟机没有最新版本的模板"+" "+(Version))+'</b></div><br/>'
    });

    var yes_button2= new Ext.Button({
        id: 'yes',
        text: _('关闭'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon'
        ,listeners: {
            click: function(btn) {
                closeWindow(wid);
            }
        }
    });
    var label_vm=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("虚拟机")+'</div>',
        id:'label_vm'
    });
    var vms_grid = new Ext.grid.GridPanel({
        store: vms_store,
        id:'vms_grid',
        stripeRows: true,
        colModel:vm_columnModel,
        frame:false,
        border:false,
//        selModel:disk_selmodel,
        //autoExpandColumn:1,
        autoScroll:true,
        height:220,
        width:'100%',
        forceSelection: true,
        tbar:[label_vm,{
            xtype: 'tbfill'
        }],
        enableHdMenu:false
         ,listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            }
        }
    });

    var vms_panel=new Ext.Panel({
        id:"vms_panel",
        layout:"form",
        closable:true,
        width:'100%',
        height:300,
        labelWidth:130,
        border:0,
        frame:true,
        items:[label,label2,vms_grid]
    });

    vms_panel.addButton(yes_button2);
    return vms_panel;
}
function json(general_object,boot_params_object,misc_object,provision_object,
        storage_status_object,network_object,backup_object,high_avail_object,scheduling_object){

    var jsondata= Ext.util.JSON.encode({
    "general_object":general_object,
    "boot_params_object":boot_params_object,
    "misc_object":misc_object,
    "provision_object":provision_object,
    "storage_status_object":storage_status_object,
    "backup_object":backup_object,
    "network_object":network_object,
    "high_avail_object":high_avail_object,
    "scheduling_object":scheduling_object
    });
    return jsondata;

}

function validate_device(disks_store, new_device) {
    //alert(disks_store.getTotalCount());
    for (var i=0;i<disks_store.getCount();i++){
        var rec=disks_store.getAt(i);
        //alert(rec.get("device"));
        if(rec != null) {
            if(rec.get("device").replace(":cdrom","") == new_device) {
                Ext.MessageBox.alert(_("错误"),_("此装置已经使用"));
                return false;
            }
        }
    }
    return true;
}

function process_value(value){
     var val=value.toString();
     if (val.charAt(0)==" ")
         val=val.substr(1);
     if(val.charAt(0)=="[" || val.charAt(0)=="{"){
           value=val;
     }else{
           value="'"+value+"'";
     }
     return value;
}

function validate_datetime(date,time,type){
    if (date=="" || time==""){
        Ext.MessageBox.alert(_("错误"),"Select values for "+type+" date and time");
        return false;
    }
    var date_status=check_date(date,time,type);
    if(date_status.length>0){
        Ext.MessageBox.alert(_("Error"),date_status);
        return false;
    }
    return true;
}
