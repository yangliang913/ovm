/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
var nw_win_popup;
function handleEvents(node,action,item,objData){
//   alert("handleEvents is called");
// alert("parent id= " + node.parentNode.attributes.id);
// alert("node id= " + node.attributes.id);
// alert("node id= " + node.attributes.text);
// alert("nodetype= " + node.attributes.nodetype);
// alert("action= " + action);

    if(objData == undefined || objData == null || objData == "") {
        objData = null;
    }
    ///////////// VM ////////////
    if(node.attributes.nodetype=="DOMAIN"){
        if(action=='hibernate'){
            getNodeProperties(node,node.parentNode,action);
            return;
        }else if(action=='migrate'){
            getTargetNodes(node,node.parentNode,action);
            return;
        }else if(action=='edit_vm_config_file'){
            getVMConfigFile(node,action);
            return;
        }else if(action=='remove_vm_config'){
            removeVMConfigFile(node,action);
            return;
        }else if(action=='set_boot_device'){
            getBootDevice(node,action);
            return;
        }else if(action=='change_vm_settings'){
            changeVmSettings(node,action);
            return;
        }else if(action=='delete'){
            removeVM(node,action);
            return;
        }else if(action=='view_console'){
            select_view(node.parentNode,node);
//            getVNCInfo(node.parentNode,node);
            return;
        }else if(action=='backup_now'){
        //showWindow(_("Backup Now "),540,450, vmBackupNowUI(node,node.attributes.id, action));
        call_vm_backupNow(node,node.attributes.id, action);


        return;
        }else if(action=='restore_backup'){
            call_RestoreRecentBackup(node,node.attributes.id, action);
            //showWindow(_("Recent Backup's"),540,430, RestoreRecentBackup(node,node.attributes.id, action));
        return;
        }else if(action=='purge_backup'){
            purge_single_backup(node, node.attributes.id, action);
            return;
        }else if(action=='create_image_from_vm'){
            create_image_from_vm(node, action);
            return;
        }
        else if(action=='annotate'){
            annotateEntity(node,action);
            return;
        }else if(action=='start'){
            //do maintenance check only for vm operation 'start'.
            //Here 'node' means vm.
            maintenance_check(node.parentNode, "start", item, node);
//            vm_action(node,item);
            return;
         }
        vm_action(node,item);
        return;

     ///////////// SERVER_POOL ////////////
    }else if(node.attributes.nodetype=="SERVER_POOL"){
        if(action=='manage_virtual_networks'){
            nw_win_popup = showWindow(_("管理虚拟网络")+":- "+node.text,466,450,VirtualNetwork(node),null,true);
            return;
        } else if(action=='purge_backup'){
            purge_single_backup(node, node.attributes.id, action);
            return;
        }
    ///////////// DATA_CENTER ////////////
    }else if(node.attributes.nodetype=="DATA_CENTER"){
        if(action=='manage_virtual_networks'){
            nw_win_popup = showWindow(_("管理虚拟网络")+":- "+node.text,466,450,VirtualNetwork(node),null,true);
           return;
        } else if(action=='purge_backup'){
            purge_single_backup(node, node.attributes.id, action);
            return;
        } else if(action=='manage_vlan_id_pool'){
            windowid=Ext.id();
            showWindow(_("管理VLAN ID池")+":- "+node.text,496,450,VLANIDPool(node, windowid),windowid,true); //466
           return;
        }
    }else if(node.attributes.nodetype=="VDC"){

        ////////////// get CP Feature based on VDC /////////////////////
        vdcid = node.attributes.id;
        var url = "/cloud/get_cp_feature_set?vdc_id="+vdcid;
        var ajaxReq=ajaxRequest(url,0,"POST",true);
        ajaxReq.request({
            success: function(xhr) {
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                    var cp_feature = response.info;
                    //// Handle VDC Events ////
                    handleEventsForVDC(node, action, item, objData, cp_feature);
                }else{
                    Ext.MessageBox.alert(_("失败"),_("无法加载供应商的特点."));
                }
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
            }
        })

        
    }else if(node.attributes.nodetype=="VDC_FOLDER"){

        if(action=='provision_vdc'){
        
        showWindow(_("选择"+stackone.constants.IAAS),320,130,addCloudProviderForVDC(node));
//        VDCConfigSettings(node.attributes.id,node.text,node.attributes.nodetype,"NEW",cmsvdc);
        }
    }else if(node.attributes.nodetype=="VDC_VM_FOLDER"){

        if(action=='provision_vm'){
            CloudVMConfig(node.parentNode, "PROVISION", node);
            return;
        }
    }else if(node.attributes.nodetype=="CLOUD_VM"){
         if (action=="connect"){
    //        select_view(node,node,'CLOUD');
            cloud_select_view(node.attributes.vdcid,node);//cloud_select_view(node.parentNode,node);node.attributes.vdcid
         }else if (action=="edit_vm"){
            //edit_vm(node.parentNode,node);
            CloudVMConfig(node, "EDIT_VM");
         }else if(action=="create_template"){
             showWindow(_("从虚拟机创建模板 "+node.text),420,205,create_template(node));
         }
         else{
             cloud_vm_action(node,item);
         }
    }
   else if(node.attributes.nodetype=="CLOUD_TEMPLATE"){
	   Create_AMI(node,'create_template',item.provider_id,item.account_id,item.region_id,item.vdc_id);
    }

//    alert(action);
    switch (action) {

        case 'edit_cloud_provider':
            editCloudProvider(node);
            break;

         case 'delete_cloud_provider':
            deleteCloudProvider(node);
            break;

        case 'add_cloud_provider':
           showWindow(_("选择"+stackone.constants.IAAS+"类型"),320,130,addCloudProvider(node));
           break;
        case 'restore_from_backup':
            getTargetNodes(null,node,action,objData);
            break;
        case 'restore_hibernated':
            getNodeProperties(null,node,'restore');
            break;
        case 'add_server_pool':
            addServerPool(node);
            break;
        case 'manage_public_ip_pool':
            manage_public_ip_pool(node);
            break;
        case 'manage_vcenters':
            showWindow(_("管理vCenters"),466,450,vCenterlist(node));
            break;
        case 'remove_server_pool':
            removeServerPool(node);
            break;
        case 'add_node':
            showWindow(_("选择平台"),315,120,select_platform(node));
            break;
        case 'dwm_policy':
            showWindow(_("配置动态负载均衡")+":- "+node.text,630,535,DVM_Policy(node),null,false);
            break;
        case 'connect_all':
            connectAll(node,null,true);
            break;
        case 'group_provision_settings':
            showWindow(_("提供设置")+" :- "+node.text,510,375,GroupProvisionSettingsDialog(node));
            break;
        case 'provision_vm':
            if (node.attributes.nodetype==stackone.constants.SERVER_POOL){
                Provision(node,null,"provision_vm"); 
            } else {
                maintenance_check(node, "provision_vm", null, null);
            }            
            break;
        case 'edit_node':
            getNodeProperties(null,node,'edit_node');
            break;
       
        case 'ssh_node':
            getSshTerminal(node);
            break;
        case 'migrate_server':
            getTargetSP(node.childNodes,node,node.parentNode,action);
            break;
        case 'connect_node':
            connectNode(node,"","")
            //node.fireEvent('click',node);
            break;
        case 'restore_from_backup':
            getNodeProperties(null,node,'restore');
            break;
        case 'import_vm_config':
            maintenance_check(node, "import_vm_config", null, null);
//            getNodeProperties(null,node,'import');
            break;
        case 'remove_node':
            removeNode(node);
            break;
        case 'server_maintenance':
            showWindow(_("服务器维护"),530,480 ,serverMaintenance(node));
            break;
        case 'power_management':
            DWM_fence_ui(node);
            break;
        case 'start_all':
            maintenance_check(node, "start_all", item, null);
//            server_action(node,item);
            break;
        case 'shutdown_all':
            server_action(node,item);
            break;
        case 'kill_all':
            server_action(node,item);
            break;
        case 'migrate_all':
            getTargetNodes('all',node,action);
            break;
        case 'create_network':
            getTargetNodes(null,node,action);
            break;
        case 'add_image_group':
            addImageGroup(node);
            break;
        case 'remove_image_group':
            removeImageGroup(node);
            break;
        case 'rename_image_group':
            renameImageGroup(node);
            break;
        case 'clone_image':
            cloneImage(node);
            break;
        case 'remove_image':
            removeImage(node);
            break;
        case 'rename_image':
            renameImage(node);
            break;
        case 'edit_image_script':
            editImageScript(node,action);
            break;
        case 'edit_image_desc':
            editImageDesc(node,action);
            break;
        case 'provision_image':
            getTargetNodes(null,node,action);
            break;
        case 'import_appliance':
//            showApplianceList(node,action);
               showWindow(_("创建模板")+":- "+node.text,400,300 ,templateform(node));
            break;
        case 'storage_pool':
            showWindow(_("存储")+":- "+node.text,444,495,StorageDefList(node),null,true);
            break;
       case 'edit_image_settings':
            editImageSettings(node,action);
            break;
       case 'manage_virtual_networks':
            nw_win_popup = showWindow(_("管理虚拟网络")+":- "+node.text,466,450,VirtualNetwork(node),null,true);
           break;
       case 'backup_vm_settings':
           windid=Ext.id();
           var backup_panel= spBackupTaskUI(action,node,node.attributes.id,windid)
           showWindow(_("配置备份"),650,470, backup_panel,windid);
           break;
       case 'restore_backedup_vm':

           var node_ids=new Array();
           var node_id=node.attributes.id;
           var evt="click";
           var e= null;
           node.fireEvent('restore',node);
           var backup_history_panel=  centerPanel.findById('backup_history');
           centerPanel.setActiveTab(backup_history_panel)
           break;
       case 'configure_high_availability':
           configueHighAvailability(node,action)
           break;
     case 'annotate':
           annotateEntity(node,action);
           break;
    }
}


function handleEventsForVDC(node, action, item, objData, cp_feature)
{        var vdc_id = node.attributes.id;
     
        if(action=='cloud_security_group'){
            var windowid_sg = Ext.id();
            if(is_feature_enabled(cp_feature,stackone.constants.CF_REFRESH)){
                var url="/cloud/privilege_for_import_operation?vdc_id="+node.attributes.id;
                var ajaxReq=ajaxRequest(url,0,"POST",true);
                ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            showWindow(_("安全组")+":- "+node.text,500,495,SecGroupList(node.attributes.id, windowid_sg,response.info),windowid_sg); //width. height 495
                        }else{    //
                            Ext.MessageBox.alert(_("Error"),response.msg);
                            return;
                        }
                    },
                    failure: function(xhr){
                       Ext.MessageBox.alert(_("错误"),"检索数据时出错.");
                       return;
                    }
                });
            } else {
                showWindow(_("安全组")+":- "+node.text,500,495,SecGroupList(node.attributes.id, windowid_sg),windowid_sg,false); //width. height 495
            }
            
        } else if(action=='cloud_key_pair'){
            var windowid_kp = Ext.id();
            if(is_feature_enabled(cp_feature,stackone.constants.CF_REFRESH)){
                var url="/cloud/privilege_for_import_operation?vdc_id="+node.attributes.id;
                var ajaxReq=ajaxRequest(url,0,"POST",true);
                ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            showWindow(_("密钥对")+":- "+node.text,575,495,KeyPairList(node.attributes.id, windowid_kp,response.info),windowid_kp); //width. height 495
                        }else{    //
                            Ext.MessageBox.alert(_("错误"),response.msg);
                            return;
                        }
                    },
                    failure: function(xhr){
                       Ext.MessageBox.alert(_("错误"),"检索数据时出错.");
                       return;
                    }
                });
            } else {
                showWindow(_("密钥对")+":- "+node.text,575,495,KeyPairList(node.attributes.id, windowid_kp),windowid_kp,false); //width. height 495
            }
            
        } else if(action=='cloud_storage'){
            var windowid_s = Ext.id();
            if(is_feature_enabled(cp_feature,stackone.constants.CF_REFRESH)){
                var url="/cloud/privilege_for_import_operation?vdc_id="+node.attributes.id;
                var ajaxReq=ajaxRequest(url,0,"POST",true);
                ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            showWindow(_("存储")+":- "+node.text,875,500,CloudStorageList(node.attributes.id, windowid_s,node.text,cp_feature,response.info),windowid_s); //width. height 495
                        }else{    //
                            Ext.MessageBox.alert(_("错误"),response.msg);
                            return;
                        }
                    },
                    failure: function(xhr){
                       Ext.MessageBox.alert(_("错误"),"检索数据时出错.");
                       return;
                    }
                });
            } else {
                showWindow(_("存储")+":- "+node.text,875,500,CloudStorageList(node.attributes.id, windowid_s,node.text,cp_feature),windowid_s,false); //width. height 495
            }
            
        } else if(action=='cloud_network'){
            var windowid_s = Ext.id();
            showWindow(_("管理网络")+":- "+node.text,495,500,CloudNetworkList(node.attributes.id, windowid_s, node.text),windowid_s); //width. height 495
            return;
        } else if(action=='cloud_snapshot'){
            var vdc_id = node.attributes.id;
            var acc_id = null;
            var region_id = null;
            var volume_id = null;
            var windowId = Ext.id();
            showWindow(_("快照")+":- "+node.text, 700, 500, CloudManageSnapshot(vdc_id, acc_id, region_id, volume_id, windowId,cp_feature), windowId);
            return;
        } else if(action=='cloud_public_ip'){
            var windowid_ip = Ext.id();
            if(is_feature_enabled(cp_feature,stackone.constants.CF_REFRESH)){
                var url="/cloud/privilege_for_import_operation?vdc_id="+node.attributes.id;
                var ajaxReq=ajaxRequest(url,0,"POST",true);
                ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            showWindow(_("公共IPs")+":- "+node.text,638,495,PublicIPList(node.attributes.id, windowid_ip, cp_feature,response.info),windowid_ip); //width. height 495
                        }else{    //
                            Ext.MessageBox.alert(_("错误"),response.msg);
                            return;
                        }
                    },
                    failure: function(xhr){
                       Ext.MessageBox.alert(_("错误"),"检索数据时出错.");
                       return;
                    }
                });
            } else {
                showWindow(_("公共IPs")+":- "+node.text,638,495,PublicIPList(node.attributes.id, windowid_ip, cp_feature),windowid_ip,false); //width. height 495
            }
            
        }
        else if(action=='edit_vdc'){            
            VDCConfig(node.attributes.id,node.text,node.attributes.nodetype,"EDIT",node.attributes.cp_type);
            return;
        }
        else if(action=='delete_vdc'){
            deleteVirtualDataCenter(node);
            return;
        }
                }




function addCloudProvider(node)
{


   var store = new Ext.data.JsonStore({
        url: '/get_provider_types?',
        root: 'rows',
        fields: ['name', 'value'],
        //id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    store.load();
    var cloudform = new Ext.form.ComboBox({
        fieldLabel: _('选择类型'),
        allowBlank:false,
        store: store,
        emptyText :"选择类型",
        mode: 'local',
        displayField:'name',
        valueField:'value',
        width: 180,
        triggerAction :'all',
        forceSelection: true,
        name:'cloud_form'
    });

    var simple = new Ext.FormPanel({
        labelWidth:80,
        frame:true,
        border:0,
        width:300,
        height:100,
        labelSeparator: ' ',
        items:[cloudform]
    });
    simple.addButton(_("确定"),function(){
        if (simple.getForm().isValid()) {
            closeWindow();
            var cp_type=cloudform.getValue();
                 
                GetCloudProvider(node, "ADD", 0, cp_type)
        }
         else{

                    Ext.MessageBox.alert(_('错误'), _('请选择一个类型.'));
                }
                
    });


    simple.addButton(_("取消"),function(){
        closeWindow();
    });
    return simple;

}

function addCloudProviderForVDC(node){
    
   var store = new Ext.data.JsonStore({
        url:'/get_cp?',//"/cloud/get_cloud_providers?"//get_provider_types?
        root: 'rows',
        fields: ['name', 'value','cp_id'],
        //id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load:function(store,recs,opts){
                if (store.getCount()==0){
                    Ext.MessageBox.alert(_("警告")," No "+stackone.constants.IAAS+ "已经定义. 请创建一个 "+stackone.constants.IAAS);
                    return;
                }
                cloudform.selectedIndex=0;

            }
        }

    });
    store.load();
    var cloudform = new Ext.form.ComboBox({
        fieldLabel: _('选择IaaS'),
        allowBlank:false,
        store: store,
        emptyText :"选择IaaS",
        mode: 'local',
        displayField:'name',
        valueField:'cp_id',
        width: 180,
        triggerAction :'all',
        forceSelection: true,
        name:'cloud_form',
        id:'cloudformqq'
    });

    var simple = new Ext.FormPanel({
        labelWidth:80,
        frame:true,
        border:0,
        width:300,
        height:100,
        labelSeparator: ' ',
        items:[cloudform]
    });
    simple.addButton(_("确定"),function(){
        if (simple.getForm().isValid()) {
            closeWindow();
            cloudform.store=store
            var cp_id=cloudform.getSelectedRecord().get('cp_id');
            var cloud_value=cloudform.getSelectedRecord().get('value');
            VDCConfig(node.attributes.id,node.text,node.attributes.nodetype,"NEW",cloud_value,cp_id);
        } else {
            Ext.MessageBox.alert(_('错误'), _('请选择一个IaaS.'));
        }

    });

    simple.addButton(_("取消"),function(){
        closeWindow();
    });
    return simple;

}



function maintenance_check(node, action, item, vm){

    var m_url = "/node/is_in_maintenance_mode?node_id="+node.attributes.id;
    
    var ajaxReq=ajaxRequest(m_url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success)
            {
                if(response.is_maintenance)
                  //if in Maintenance mode.
                  {     //Show Maintenance Warning.
                        Ext.Msg.confirm('警告', "服务器"+ node.attributes.nodeid +" 进入维护模式. 确定要继续吗?", function(btn)
                        {
                            if (btn == 'yes')
                            {
                                switch (action) {
                                    case 'provision_vm':
                                        Provision(node, null, "provision_vm");
                                        break;
                                    case 'start_all':
                                        server_action(node,item);
                                        break;
                                    case 'import_vm_config':
                                        getNodeProperties(null, node, 'import');
                                        break;
                                    case 'start':
                                        //do maintenance check only for vm operation 'start'.
                                        vm_action(vm, item);
                                        break;  
                                        
                                }
                            }
                            else{
                               return;
                            }
                        });
                   }
                  else
                      //if not in Maintenance mode.
                      {
                            switch (action) {
                                case 'provision_vm':
                                    Provision(node, null, "provision_vm");
                                    break;
                                case 'start_all':
                                    server_action(node, item);
                                    break;
                                case 'import_vm_config':
                                    getNodeProperties(null, node, 'import');
                                    break;
                                case 'start':
                                    vm_action(vm,item);
                                    break;
                            }
                      }
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure"), xhr.statusText);
        }
    });
}






//function confirmAction(node,url,id,action,later){

function editCloudProvider(node){
    var node_id=node.attributes.id;
    var url='cloud_provider/get_cloudprovider_details?node_id='+node_id
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr){
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var result=response.rows;
                var type=result.type
                var name=result.name
                GetCloudProvider(node, "EDIT", result, type)
            }
            else{
                Ext.MessageBox.alert(_("Failure") ,response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure"), xhr.statusText);
        }

    })

}

function deleteCloudProvider(node){
    var node_id=node.attributes.id;
    var iaaSName=node.text;
     var msg=format(_(iaaSName+"  "+stackone.constants.IAAS +"将要删除.是否继续?"),node.text);
    Ext.MessageBox.confirm(_("确认"),msg,function(id){
        if (id == 'yes'){
    var url='cloud_provider/delete_cloudprovider?node_id='+node_id+"&group_id="+node.parentNode.attributes.id;
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr){
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                Ext.MessageBox.alert(_("状态") ,iaaSName+" "+stackone.constants.IAAS+" 已经成功删除");
            }
            else{
                Ext.MessageBox.alert(_("Failure") ,response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure"), xhr.statusText);
        }

    })
        }
    })
}
function deleteVirtualDataCenter(node){
    var node_id=node.attributes.id;
    var delete_from_cloud=false;
    var delete_user=false;
    var msg_user="确定要删除属于这个数据中心的所有用户吗?.";
    var users_ids;
    if(node.attributes.cp_type==stackone.constants.CMS){
        var msg="删除虚拟服务器池,所有相应的实体也将被删除.";
        delete_from_cloud=true;
        Ext.MessageBox.confirm(_("确认"),msg,function(id){
            if (id == 'yes'){
                
                Ext.MessageBox.confirm(_("确认"),msg_user,function(id1){
                    if (id1 == 'yes'){
                       delete_user=true;
                    }
                    var url='cloud/delete_virtualdatacenter?vdc_id='+node_id+"&delete_from_cloud="+delete_from_cloud+'&delete_user='+delete_user;
                    var ajaxReq=ajaxRequest(url,0,"POST",true);
                    ajaxReq.request({
                        success: function(xhr){
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                Ext.MessageBox.alert(_("Status") ,response.msg);
                            }else{
                                Ext.MessageBox.alert(_("Failure") ,response.msg);
                            }
                        }
                        ,failure: function(xhr){
                            Ext.MessageBox.alert( _("Failure"), xhr.statusText);
                        }
                    })

                });
             }else{
                return;
             }

        })

    }else{
//        var msg=format(_("Delete Virtual Machines from Cloud also?."),node.text);
        delete_user=false;
        Ext.Msg.show({
            title:'确认',
            msg: _("确定要删除相应的实体，以及云吗?"),
            buttons: Ext.Msg.YESNOCANCEL,
            fn: function(id){
                if(id=='cancel'){
                     return;
                }
                if(id=='yes'){
                     delete_from_cloud=true;
                }
                 Ext.MessageBox.confirm(_("确认"),msg_user,function(id1){
                    if (id1 == 'yes'){
                       delete_user=true;
                    }
                    var url='cloud/delete_virtualdatacenter?vdc_id='+node_id+"&delete_from_cloud="+delete_from_cloud+'&delete_user='+delete_user;
                    var ajaxReq=ajaxRequest(url,0,"POST",true);
                    ajaxReq.request({
                        success: function(xhr){
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                Ext.MessageBox.alert(_("Status") ,response.msg);
                            }
                            else{
                                Ext.MessageBox.alert(_("Failure") ,response.msg);
                            }
                        },
                        failure: function(xhr){
                            Ext.MessageBox.alert( _("Failure"), xhr.statusText);
                        }

                    });
                 })
                
               
            },
            animEl: 'elId',
            icon: Ext.MessageBox.QUESTION
        });

    }
}

function confirmAction(node,url,id,action,parentClick){

    if(id=='yes'){
     //        if((!later) && (action=="start" || action == "shutdown" || action=="delete" )){
            var org_action=action;
            if (org_action=="start_view_console"){
                action="start";
            }
            if(action=="start" || action == "shutdown" || action=="delete" || action=="reboot"){
                var sch_url="/node/get_vmschedule_status?dom_id="+node.attributes.id+"&action="+action;
                var ajaxReq=ajaxRequest(sch_url,0,"GET",true);
                ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                               var response=Ext.util.JSON.decode(xhr.responseText);
                               if(response.success){
                                   if (response.status){
                                            Ext.MessageBox.confirm(_("警告"),_("Already scheduled for "+action+" action on "+response.exe_time+", proceed "+action+"?" ),function(id){
                                                if(id=='yes'){
                                                     submit_schedule(node,url,parentClick,org_action);
                                                }
                                            });
                                   }else{
                                       submit_schedule(node,url,parentClick,org_action);
                                   }
                                }
                            },
                            failure: function(xhr){
                                Ext.MessageBox.alert( _("Failure"), xhr.statusText);
                            }
                        });
            }
            else{
                submit_schedule(node,url,parentClick,org_action);
            }
    }
}

function submit_schedule(node,url,parentClick,action){

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                if(parentClick){
                    node.parentNode.fireEvent('click',node.parentNode);
                    Ext.MessageBox.alert(_("Success"),response.msg);
                }else{
                    Ext.MessageBox.alert(_("Success"),response.msg);
                }
                if(action=="start_view_console"){
                    (function(){
                         select_view(node.parentNode,node);
                    }).defer(response.wait_time*1000)
                }
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
//            node.parentNode.fireEvent('click',node.parentNode);
//            task_panel_do();

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure"), xhr.statusText);
        }
    });
}

function vm_action(vm,btn){
    var url="/node/vm_action";
    var action=btn.id;
    if (action=="start_view_console"){
        action="start";
    }

    url+="?dom_id="+vm.attributes.id+"&node_id="+vm.parentNode.attributes.id+"&action="+action;

//    showScheduleWindow(vm,format(_("{0} {1} on {2}? "),btn.tooltip,vm.text,vm.parentNode.text),url,btn.id,btn);

    if(btn.id=='start' || btn.id=='start_view_console')
        confirmAction(vm,url,'yes',btn.id);
    else
        Ext.MessageBox.confirm(_("确认"),format(_("确定要{0}吗? "),btn.tooltip,vm.text,vm.parentNode.text), function (id){
            confirmAction(vm,url,id,btn.id);
        });
}

function server_action(node,btn){
    var url="/node/server_action";
    url+="?node_id="+node.attributes.id+"&action="+btn.id;

//    showScheduleWindow(node,format(_("{0} in {1} on {2}? "),btn.tooltip,node.text,node.parentNode.text),url,btn.id,btn);

    Ext.MessageBox.confirm(_("确认"), format(_("在{1}上{0}吗? "),btn.tooltip,node.text,node.parentNode.text), function(id){
        if(id=='yes'){
            var ajaxReq=ajaxRequest(url,0,"GET");
            ajaxReq.request({
                success: function(xhr) {
                    var action_response=Ext.util.JSON.decode(xhr.responseText);
                    if(action_response.success){
                        Ext.MessageBox.alert(_("Success"),action_response.msg);
//                        node.fireEvent('click',node);
                    }else{
                        Ext.MessageBox.alert(_("Error"),action_response.msg);
                    }
                },
                failure: function(xhr){
                    Ext.MessageBox.alert( _("Failure") + xhr.statusText);
                }
            });
        }
    });
}

function getTargetSP(vm,node,sp,action,objData){
    var url="/node/get_migrate_target_sps?node_id="+node.attributes.id+"&sp_id="+sp.attributes.id;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var res=Ext.util.JSON.decode(xhr.responseText);
            if(eval(res.success)){
                show_dialog_SP(node,res,action,vm,sp,objData);
            }else{
                Ext.MessageBox.alert(_("Error"),res.msg);
            }
        },
        failure: function(xhr){
            //alert('Fail');
            try{
                var res=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), res.msg);
            }catch(e){
                Ext.MessageBox.alert(_("错误"),_("失败: ") +xhr.statusText);
            }
        }
    });
}


function removeNode(node){
    var url="/node/remove_node";
    url+="?node_id="+node.attributes.id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                url+="&force=True"
                var msg="";
                msg+=format(_("您希望从 {1} 删除 {0} 吗? "), node.text,node.parentNode.text);
                if(response.vms>0){
                    msg+=_("在该服务器上创建的所有虚拟机也将被删除， ");
                    msg+="<br>"+_("相关VBDs/卷不会被删除，是否继续？");
                }
                Ext.MessageBox.confirm(_("确认"),msg, function(id){
                            confirmAction(node,url,id,null,false);
                });
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function getNodeProperties(vm,node,action){
    var url="/node/get_node_properties";
    url+="?node_id="+node.attributes.id;

    var ajaxReq=ajaxRequest(url,0,"GET");
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(!response.success){
                Ext.MessageBox.alert(_("Failure"),response.msg);
                return;
            }
            if(action=='edit_node')
                show_platform(node,response.node);
            else
                show_dialog(node,response.node,action,vm);

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function importVMConfig(node,directory,filenames){
    //alert(directory+"--"+filenames);
    var url="/node/import_vm_config?node_id="+node.attributes.id+"&directory="+directory+"&filenames="+filenames;
    var ajaxReq=ajaxRequest(url,0,"GET");
    closeWindow();
    ajaxReq.request({
        success: function(xhr) {
            var import_response=Ext.util.JSON.decode(xhr.responseText);
            if(import_response.success)
                Ext.MessageBox.alert(_("Success"),import_response.msg);
            else
                Ext.MessageBox.alert(_("Error"),import_response.msg);
//            node.fireEvent('click',node);
        },
        failure: function(xhr){
            try{
                var import_response=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), import_response.msg);
            }catch(e){
                Ext.MessageBox.alert(_("错误"),_("失败: ") +xhr.statusText);
            }
        }
    });
}

function importVMConfiguration(node,paths){
    var action="import_vm";
    if (paths.split(",").length>1){
        action="import_vms";
    }
    var url="/node/import_configs?node_id="+node.attributes.id+"&paths="+paths+"&action="+action;
    var ajaxReq=ajaxRequest(url,0,"GET");
    closeWindow();
//    showScheduleWindow(node,_("Import VM"),url,action,"");
    ajaxReq.request({
        success: function(xhr) {
            var import_response=Ext.util.JSON.decode(xhr.responseText);
            if(import_response.success)
                Ext.MessageBox.alert(_("Success"),import_response.msg);
            else
                Ext.MessageBox.alert(_("Error"),import_response.msg);
            node=leftnav_treePanel.getNodeById(node.attributes.id);
//            node.fireEvent('click',node);
        },
        failure: function(xhr){
            try{
                var import_response=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), import_response.msg);
            }
            catch(e){
                Ext.MessageBox.alert(_("错误"),_("失败: ") +xhr.statusText);
            }
        }
    });
}

function addServerPool(node){
    Ext.MessageBox.prompt(_("新建服务器池"),_("输入服务器池名称"),function(btn, text){
        if (btn == 'ok'){
            if(text.length==0){
                Ext.MessageBox.alert(_("错误"),_("请输入服务器池的名称."));
                return;
            }
            var url="/node/add_group?group_name="+text+"&site_id="+node.attributes.id;

            var ajaxReq=ajaxRequest(url,0,"GET");
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
                        Ext.MessageBox.alert(_("Success"),response.msg);
                        node.fireEvent('click',node);
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



function manage_public_ip_pool(node){

    showWindow(_("管理公共IP池"),570,400,ManagePublicIPPool(node,"ADD"),null,false,false);
    
}

function removeServerPool(node){
    var msg=format(_("删除{0}，在服务器池添加的所有服务器也将被删除，是否继续?"),node.text);
    Ext.MessageBox.confirm(_("确认"),msg,function(id){
        if (id == 'yes'){
            var url="/node/remove_group?group_id="+node.attributes.id;

            var ajaxReq=ajaxRequest(url,0,"GET");
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
                        Ext.MessageBox.alert(_("Success"),response.msg);
                        node.parentNode.fireEvent('click',node.parentNode);
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

function restoreVM(node,directory,filenames){
    //alert(directory+"--"+filenames);
    var url="/node/restore_vm?node_id="+node.attributes.id+"&directory="+directory+"&filenames="+filenames;
    closeWindow();
//    showScheduleWindow(node,_("Restore VM"),url,"","");

    var ajaxReq=ajaxRequest(url,0,"GET");
    closeWindow();
    ajaxReq.request({
        success: function(xhr) {
            var import_response=Ext.util.JSON.decode(xhr.responseText);
            if(import_response.success)
                Ext.MessageBox.alert(_("Success"),import_response.msg);
            else
                Ext.MessageBox.alert(_("Error"),import_response.msg);
//            node.fireEvent('click',node);
        },
        failure: function(xhr){
            try{
                var import_response=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), import_response.msg);
            }catch(e){
                Ext.MessageBox.alert(_("错误"),_("失败: ") +xhr.statusText);
            }
        }
    });
}

function snapshotVM(node,directory,filenames){
    //alert(directory+"--"+filenames);
    var url="/node/save_vm?dom_id="+node.attributes.id+"&node_id="+node.parentNode.attributes.id+"&directory="+directory+"&filenames="+filenames;
    closeWindow();
//    showScheduleWindow(node,_("Save Snapshot"),url,"","");
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    closeWindow();
    ajaxReq.request({
        success: function(xhr) {
            var import_response=Ext.util.JSON.decode(xhr.responseText);
//            alert(import_response.msg);
            if(import_response.success)
                Ext.MessageBox.alert(_("Success"),import_response.msg);
            else
                Ext.MessageBox.alert(_("Error"),import_response.msg);
//            node.fireEvent('click',node);
        },
        failure: function(xhr){
            try{
                var import_response=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), import_response.msg);
            }catch(e){
                Ext.MessageBox.alert(_("错误"),_("失败: ") +xhr.statusText);
            }
        }
    });
}

function getTargetNodes(vm,node,action,objData){
//     alert("getTargetNodes is called");

    var url="/node/get_migrate_target_nodes?node_id="+node.attributes.id;
    if(action=='provision_image' || action == 'create_network'){
        url="/template/get_image_target_nodes?image_id="+node.attributes.nodeid;
    } else if(action == 'restore_from_backup') {
        url="/template/get_target_doms";
    }
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var res=Ext.util.JSON.decode(xhr.responseText);
            if(eval(res.success)){
                show_dialog(node,res,action,vm,objData);
            }else{
                Ext.MessageBox.alert(_("Error"),res.msg);
            }
        },
        failure: function(xhr){
            try{
                var res=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), res.msg);
            }catch(e){
                Ext.MessageBox.alert(_("错误"),_("失败: ") +xhr.statusText);
            }
        }
    });
}

function migrateVM(vm,node,dest_node,live,force){
    var url="",msg="";
    if(vm=='all'){
        url="/node/migrate_vm?dom_name=None&dom_id=None&source_node_id="+node.attributes.id+
        "&dest_node_id="+dest_node.attributes.id+"&live="+live+"&all=true";
        msg=format(_("迁移所有虚拟机从 {0} 到 {1}?"),node.text,dest_node.text);
    }else{
        url="/node/migrate_vm?dom_name="+vm.attributes.text+"&dom_id="+vm.attributes.id+"&source_node_id="+node.attributes.id+
        "&dest_node_id="+dest_node.attributes.id+"&live="+live+"&all=false";
        msg=format(_("迁移 {0} 从 {1} 到 {2}?"),vm.text,node.text,dest_node.text);
    }

    var args=Ext.util.JSON.encode({
        "force":force,
        "live":live
    });
    args.dest_node=dest_node;
    args.vm=vm;
    args.node=node;
    args.src_node=node;

    //closeWindow();

//    var ajaxReq=ajaxRequest(url,0,"GET",true);
    if(force!='true'){
            Ext.MessageBox.confirm(_("确认"), msg , function(id){
                if(id=='yes'){
                    runMigration(url,force,node,dest_node,vm,node,live);
                }
            });
    }else{
        runMigration(url,force,node,dest_node,vm,node,live);
    }
}

function runMigration(url,force,src_node,dest_node,vm,node,live){
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var res=Ext.util.JSON.decode(xhr.responseText);
            if(res.success){
                if(force!='true' && res.rows){
                    showWindow(_("迁移检查结果"),515,325,MigrationChecksDialog(vm,node,dest_node,live,res.rows, url));
                }else{
//                    src_node.fireEvent('click',src_node);
//                    dest_node.fireEvent('click',dest_node);
                    Ext.MessageBox.alert(_("Success"),res.msg);
//                    task_panel_do();
                }
            }else{
                Ext.MessageBox.alert(_("Error"),res.msg);
//                task_panel_do();
            }
        },
        failure: function(xhr){
            try{
                var res=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), res.msg);
            }catch(e){
                Ext.MessageBox.alert(_("错误"),_("失败: ") +xhr.statusText);
            }
        }
    });
}

function connectAll(srvrpool,statusList,start){
    if(statusList==null && start){
        statusList=new Array();
        var ch=srvrpool.childNodes;
        for(var i=0;i<ch.length;i++){
            statusList[i]=new Array();
            statusList[i][0]=ch[i].attributes.nodeid;
            statusList[i][1]=false;
            statusList[i][2]='';
            statusList[i][3]=ch[i];
        }
    }
    //alert(statusList);

    var node;
    for(var i=0;i<statusList.length;i++){
        if(!statusList[i][1]){
            break;
        }
    }
    if(i<statusList.length){
        node=statusList[i][3];
        var url="/node/connect_node?node_id="+node.attributes.id;
        var ajaxReq = ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {
                var res=Ext.util.JSON.decode(xhr.responseText);
                if(res.success){
                    //Ext.MessageBox.alert("---",res.msg);
                    statusList[i][1]=true;
                    statusList[i][2]=_('Success');
                    connectAll(srvrpool,statusList,false);
                }else{
                    //Ext.MessageBox.alert("Error",res.error);
                    if(res.error!=_('没有验证')){
                        statusList[i][1]=true;
                        statusList[i][2]=""+node.text+":- "+res.msg;
                        connectAll(srvrpool,statusList,false);
                        return
                    }
                    var form=credentialsForm();
                    form.addButton(_("确定"),function(){
                        if (form.getForm().isValid()) {
                            var uname=form.find('name','user_name')[0].getValue();
                            var pwd=form.find('name','pwd')[0].getValue();
                            closeWindow();
                            form.getForm().submit({
                                url:url,
                                params: {
                                    username:uname,
                                    password:pwd
                                },
                                success: function(form,action) {
                                    statusList[i][1]=true;
                                    statusList[i][2]=_('Success');
                                    connectAll(srvrpool,statusList,false);
                                },
                                failure: function(form, action) {
                                    if(action.result.error!=_('没有验证')){
                                        statusList[i][1]=true;
                                        statusList[i][2]=""+node.text+":- "+action.result.msg;
                                    }
                                    connectAll(srvrpool,statusList,false);
                                }
                            });
                        }else{
                            Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
                        }
                    });
                    form.addButton(_("取消"),function(){
                        closeWindow();
                        statusList[i][1]=true;
                        statusList[i][2]=node.text+":"+_('服务器没有验证');
                        connectAll(srvrpool,statusList,false);
                    });
                    showWindow(_("凭据")+node.text,280,150,form);
                }
            },
            failure: function(xhr){
                try{
                    var res=Ext.util.JSON.decode(xhr.responseText);
                    Ext.MessageBox.alert(_("Error"), res.msg);
                }catch(e){
                    Ext.MessageBox.alert(_("错误"),_("失败: ") +xhr.statusText);
                }
            }
        });
    }else if(i==statusList.length){
        srvrpool.fireEvent('click',srvrpool);
        var msg='';
        for(var i=0;i<statusList.length;i++){
            if(statusList[i][2]!=_('Success')){
                msg+=statusList[i][2]+"<br/>";
            }
        }
        if(msg!=''){
            Ext.MessageBox.alert(_("Status"),msg);
        }
    }
}

function getVMConfigFile(vm,action){
    var url="/node/get_vm_config_file?dom_id="+vm.attributes.id+
        "&node_id="+vm.parentNode.attributes.id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(!response.success){
                Ext.MessageBox.alert(_("Failure"),response.msg);
                return;
            }
//            var content=xhr.responseText.substring(xhr.responseText.indexOf('data="')+6,xhr.responseText.lastIndexOf('"/>'));
//            content=formatHTML(content);
            showWindow(_("编辑配置文件:-")+vm.text,510,500,FileViewEditDialog(response.content,"",'edit','text',vm,action));
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}
/*
function removeVMConfigFile(vm,action){
    var url="/node/remove_vm_config_file?dom_id="+vm.attributes.id+
        "&node_id="+vm.parentNode.attributes.id;

    Ext.MessageBox.confirm(_("Confirm"), format(_("Remove {0} from list under {1}?"),vm.text,vm.parentNode.text), function(id){
            confirmAction(vm,url,id,null,true);
    });
}
*/
function removeVMConfigFile(vm,action){
    var url="/node/get_node_status";
    url+="?dom_id="+vm.attributes.id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var url="/node/remove_vm_config_file?dom_id="+vm.attributes.id+
                    "&node_id="+vm.parentNode.attributes.id;
                var msg=format(_("确定从{1}移除 {0} 吗?"),vm.text,vm.parentNode.text);
                    
                if(response.result.part_of_vdc === true){
                    msg+="<br>"+_("警告: 这是 VDC 的一部分.不建议此操作.");
                }
                
                Ext.MessageBox.confirm(_("确认"), msg, function(id){
                        confirmAction(vm,url,id,action,true);
                });
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}
function removeVM(vm,action){
    var url="/node/get_node_status";
    url+="?dom_id="+vm.attributes.id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var url="/node/remove_vm?dom_id="+vm.attributes.id+
                    "&node_id="+vm.parentNode.attributes.id;
                //alert(response.node_up);
                if(response.result.is_up === false){
                    url+="&force=True";
                }
                var msg=" 在 "+vm.parentNode.text+"删除 "+ vm.text+"?";
                if(response.result.is_up === false && response.result.part_of_vdc === true){
                    msg=("警告: 相关VBDs/卷将不会被删除 "+
                                    "因为服务器关闭.");
                    msg+="<br>"+_("警告: 这是 VDC 的一部分.不建议此操作.确定要继续吗?");
                }
                else if(response.result.is_up === false && response.result.part_of_vdc === false)
                    {
                        msg=("警告: 相关VBDs/卷将不会被删除 "+
                                    "因为服务器关闭.");
                    }
                else if(response.result.is_up === true && response.result.part_of_vdc === true)
                    {
                        msg+="<br>"+_("警告: 这些VM是 VDC的一部分 .不建议此操作.确定要继续吗?");
                    }
                //showScheduleWindow(vm,msg,url,"delete","");
                Ext.MessageBox.confirm(_("确认"), msg, function(id){
                        confirmAction(vm,url,id,action,false);
                });
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function getBootDevice(vm,action){
    var url="/node/get_boot_device?dom_id="+vm.attributes.id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                showWindow(_("设置引导设备:-")+vm.text,315,120,BootImageSelection(vm,response.boot));
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}
function changeVmSettings(node,action){

        var node_id=node.parentNode.attributes.id;
        var group_id=node.parentNode.parentNode.attributes.id;
        var dom_id=node.attributes.text;
        var vm_id = node.attributes.id

        var url="/node/get_vm_config?domId="+node.attributes.text+"&nodeId="+node_id;
        var ajaxReq=ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {//alert(xhr.responseText);
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                      showWindow(_("虚拟机的配置设置 ")+dom_id,640,470,VMConfigSettings(action,node_id,group_id,null,node.attributes.state,response.vm_config,dom_id,node.parentNode, vm_id));
                  }else{
                    Ext.MessageBox.alert(_("Failure"),response.msg);
                }
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
            }
        });

}
function editImageSettings(node,action){

        var url="/node/get_initial_vmconfig?image_id="+node.attributes.nodeid+"&mode="+action;
        var ajaxReq=ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {//alert(xhr.responseText);
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                    var vm_config=response.vm_config;
                    showWindow(_("模板设置"),640,430,VMConfigSettings(action,null,null,node,null,vm_config,null, null));
                    }
                    else
                        Ext.MessageBox.alert(_("Failure"),response.msg);
                },
                failure: function(xhr){
                    Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                }
            });
}
function processDrop(e){
    var node=e.dropNode;
    var dest_node=e.target;
    var src_node=e.dropNode.parentNode;
    //alert(node+"--"+dest_node+"--"+src_node+"--"+e.data+"--"+e.point);
    if(dest_node.attributes.nodetype!=src_node.attributes.nodetype){
        Ext.Msg.alert(_("错误"),_("无效的放置位置."));
        return ;
    }

    if(node.attributes.nodetype=="DOMAIN"){
        migrateVM(node,src_node,dest_node,true,false);
        return;
    }

    Ext.Msg.confirm(_("确认"),format(_("确定要移动 {0} 从 {1} 到 {2}?"),node.text,src_node.text,dest_node.text),function(id){
        if(id=='yes'){
            if(node.attributes.nodetype=="IMAGE"){
                transferImage(node,src_node,dest_node);
            }else if(node.attributes.nodetype=="MANAGED_NODE"){
                transferNode(node,src_node,dest_node,false);
            }
        }
    });
}

function transferNode(node,src_grp,dest_grp,forcefully){
    var url="/node/transfer_node?node_id="+node.attributes.id+
        "&source_group_id="+src_grp.attributes.id+
        "&dest_group_id="+dest_grp.attributes.id+
        "&forcefully="+forcefully;

    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                src_grp.fireEvent('click',src_grp);
                dest_grp.fireEvent('click',dest_grp);
            }else{
                if(response.msg == "VM_RUNNING") {
                    // Prompt for user data:
                    Ext.Msg.confirm('警告', '从该服务器池移动服务器，将断开与它相关联的所有存储，这将导致运行的虚拟机无法使用该存储，确定要继续吗?', function(btn){
                        if (btn == 'yes'){
                            // process node transfer here...
                            transferNode(node,src_grp,dest_grp,true);
                        }
                    });
                }else{
                    Ext.MessageBox.alert(_("Failure"),response.msg);
                }
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}
function configueHighAvailability(node,action){
       HighAvailbility(node,action);
}

function select_view(node,dom,cloud){
    
        var cookie;
        var remember_cookie;
        if(cloud){
            cookie=getCookie(stackone.constants.CONNECT);
            remember_cookie=getCookie(stackone.constants.CONNECT_REMEMBER);
        }else{
            cookie=getCookie(stackone.constants.VM_CONSOLE);
            remember_cookie=getCookie(stackone.constants.VM_CONSOLE_REMEMBER);

        }

	if (cookie!=null && cookie!="" && remember_cookie=="true"){
		if (eval(cookie)==true){
			getVNCInfo(node,dom,cloud);
		}else{
                    var lcmd_cookie;
                 if(cloud){
                    lcmd_cookie=getCookie(stackone.constants.CONNECT_LOCAL_CMD);
                 }else{
                    lcmd_cookie=getCookie(stackone.constants.VM_CONSOLE_LOCAL_CMD);
                 }
	        if (lcmd_cookie!=""){
                        if(cloud){
                            cloud_select_view(node.attributes.vdcid,node);
                        }else{
                            get_command(lcmd_cookie,node,dom)
                        }	        		                            
	     	}
	    }
        
	}else{
        var url="/node/get_platform?"
        if(node.id!=null)
            url+="node_id="+node.id+"&type="+stackone.constants.MANAGED_NODE;

        var ajaxReq=ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {//alert(xhr.responseText);
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                    platform=response.platform;
                    showWindow(_("查看控制台"),300,200, select_type(platform, node, dom, cloud));
                }
                else
                    Ext.MessageBox.alert(_("Failure"),response.msg);
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
            }
        });

	}
	
}

function getSshTerminal(nod){
    getSshWindow(nod);
}

function select_type(platform, node,dom,cloud){
    
    var plt_ui_hlpr = new stackone.PlatformUIHelper(platform, "VIEW_CONSOLE");
    var components=plt_ui_hlpr.getComponentsToDisable();

    var description=new Ext.form.Label({
        html:_('您可以选择连接到虚拟机的查看器.')+
            '<br/><br/>'
    });
    var remember=new Ext.form.Checkbox({
        name: "remember",
        id: 'remember',
        hideLabel:true,
        boxLabel:_("记住我的选择"),
        checked:false,
        listeners:{
            check:function(box,checked){
               //var check=(checked)?"Y":"";
            }
        }
    });

    var use_applet=new Ext.form.Radio({
        boxLabel: _('使用VNC插件'),
        id:'use_applet',
        name:'radio',
        hideLabel:true,
        checked:true,
        listeners:{
            check:function(field,checked){
                if(checked){
                    command_combo.disable();
                }
            }
            }
    });


    var use_localcommand=new Ext.form.Radio({
        boxLabel: _('使用本地查看器:&nbsp;'),
        id:'use_localcommand',
        name:'radio',
        hideLabel:true,
        listeners:{
            check:function(field,checked){
               if(checked){
                    command_combo.enable();
               }
            }
            }
    });

    var command_store = new Ext.data.JsonStore({
        //get all 'local viewers' (vncviewer or tightvnc or vmware-vmrc, etc--) based on Server type.
        url: '/node/get_command_list',
        root: 'commands',
        fields: ['id','value'],
        sortInfo:{
            field:'value',
            direction:'DESC'
        },
        successProperty:'success',
        listeners:{
            load:function(obj,resc,f){

                command_combo.setValue(command_combo.getStore().getAt(0).get('id'));
                
                var cookie;
                if(cloud){
                    cookie=getCookie(stackone.constants.CONNECT);
                }else{
                    cookie=getCookie(stackone.constants.VM_CONSOLE);
                }

                if (cookie!=null && cookie!=""){
                    if (eval(cookie)==true){
                        use_applet.setValue(true);
                    }else{
                        use_localcommand.setValue(true);
                        use_applet.setValue(false);
                        var lcmd_cookie;
                        if(cloud){
                            lcmd_cookie=getCookie(stackone.constants.CONNECT_LOCAL_CMD);
                        }else{
                            lcmd_cookie=getCookie(stackone.constants.VM_CONSOLE_LOCAL_CMD);
                        }
                        
                        if (lcmd_cookie!=""){
                            command_combo.setValue(lcmd_cookie);
                        }

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

    command_store.load({
                params:{
                    node_id:node.attributes.id
                }
            })
            
    var command_combo=new Ext.form.ComboBox({
                id:"command_combo",
                width: 100,
                fieldLabel: _('命令'),
                allowBlank:false,
                triggerAction:'all',
                store:command_store,
                disabled:true,
                hideLabel:true,
                displayField:'id',
                valueField:'value',
                forceSelection: true,
                mode:'local'
      });

     var combo_panel=new Ext.Panel({
        border:false,
        width:"100%",
        id:"combo_panel",
        layout:'column',
        items:[use_localcommand,command_combo]
        });

     var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('确定'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(cloud){
                    setCookie(stackone.constants.CONNECT_REMEMBER,remember.getValue());
                    setCookie(stackone.constants.CONNECT,use_applet.getValue());
                }else{
                    setCookie(stackone.constants.VM_CONSOLE_REMEMBER,remember.getValue());
                    setCookie(stackone.constants.VM_CONSOLE,use_applet.getValue());
                    
                }
                if(use_applet.getValue()){
                   getVNCInfo(node,dom,cloud);
                }else{
                    if(command_combo.getValue()==""){
                        Ext.MessageBox.alert( _("失败") , "请从列表选择一个指");
                        return;
                    }
                    if(cloud){
                        setCookie(stackone.constants.CONNECT_LOCAL_CMD,command_combo.getValue());
                        cloud_select_view(node.attributes.vdcid,node);
                    }else{
                        setCookie(stackone.constants.VM_CONSOLE_LOCAL_CMD,command_combo.getValue());
                        get_command(command_combo.getValue(),node,dom,cloud)
                    }
                    
                }
               closeWindow();

            }
        }});

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


    var select_panel=new Ext.Panel({
        id:"select_panel",
        width:286,
        layout:"form",
        height:170,
        frame:true,
        labelWidth:60,
        bbar:[
        {
            xtype: 'tbfill'
        },button_ok,button_cancel],
        items:[description,use_applet,combo_panel,remember]
    });


    if (platform == stackone.constants.VMW){
        use_localcommand.setValue(true);
        use_applet.setValue(false);
    }

    //Disable panels based on platform
    var flag = true;
    for(var z=0;z<components.length;z++){
        Ext.getCmp(components[z]).setDisabled(flag);
    }

    return select_panel;
}

function get_command(command,node,dom,cloud){
    //get 'local viewer command' (vncviewer or tightvnc or vmware-vmrc, etc--) based on type of viewer selected from UI.
    var    url="/node/get_command?node_id="+node.attributes.id+"&dom_id="+dom.attributes.id+"&cmd="+command;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                getCMDInfo(dom,response.cmd,response);
            }else{
                Ext.MessageBox.alert( _("Failure") , response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function setCookie(c_name,value,expiredays)
{
    var exdate=new Date();
    exdate.setDate(exdate.getDate()+expiredays);
    document.cookie=c_name+ "=" +escape(value)+
    ((expiredays==null) ? "" : ";expires="+exdate.toUTCString());
}


function getCookie(c_name)
{
    if (document.cookie.length>0)
      {
      c_start=document.cookie.indexOf(c_name + "=");
      if (c_start!=-1)
        {
            c_start=c_start + c_name.length+1;
            c_end=document.cookie.indexOf(";",c_start);
            if (c_end==-1) c_end=document.cookie.length;
            var cookie_value=unescape(document.cookie.substring(c_start,c_end));
            return cookie_value;
        }
      }
    return "";
}
function del_cookie(name) {
    document.cookie = name +
    '=; expires=Thu, 01-Jan-70 00:00:01 GMT;';
}

function cloud_vm_action(vm,btn){
    var url="/cloud/vm_action";
    var vdc_id = vm.parentNode.parentNode.id ;
    url+="?dom_id="+vm.attributes.id+"&vdc_id="+vdc_id+"&action="+btn.id;

//    showScheduleWindow(vm,format(_("{0} {1} on {2}? "),btn.tooltip,vm.text,vm.parentNode.text),url,btn.id,btn);
        Ext.MessageBox.confirm(_("确认"),format(_("{0} {1} ? "),btn.tooltip,vm.text), function (id){

             confirm_cloud_vmaction(id,url);

              });      
}


function confirm_cloud_vmaction(id,url){


     if (id == 'yes'){
         var ajaxReq=ajaxRequest(url,0,"GET",true);
                ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                               var response=Ext.util.JSON.decode(xhr.responseText);
                               if(response.success){

                                }
                            },
                            failure: function(xhr){
                                Ext.MessageBox.alert( _("Failure"), xhr.statusText);
                            }
                    });
    }else if (id == 'no'){        
        return
    }



}


function Create_AMI(node,action,provider_id,account_id,region_id,vdc_id){
   
   

   var volume_store =new Ext.data.JsonStore({
        url: "/cloud/get_all_volumes?account_id="+account_id+"&provider_id="+provider_id+"&region_id="+region_id,
        root: 'info',
        fields: ['name'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    volume_store.load();
   
   
    var volume_combo = new Ext.form.ComboBox({
        id: 'volume',
        fieldLabel: _('卷'),
        allowBlank:true,
        triggerAction:'all',
        emptyText :_("选择卷"),
        store:volume_store,
        width:240,
        displayField:'name',
        editable:false,
        valueField:'name',
        typeAhead: true,
        minListWidth:50,
        labelSeparator:" ",
        mode:'local',
        forceSelection: true,
        selectOnFocus:true ,
        listeners: {

                select: function(combo, record, index){
                    
            }

        }

    });

   
    var name_textbox = new Ext.form.TextField({
        fieldLabel: '名称',
        name: 'temp_name',
        id: 'temp_name',
        width:240,
        labelSeparator:" ",
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {

            }
        }
    });

    var simple = new Ext.FormPanel({
        labelWidth:120,
        frame:true,
        border:0,
        labelAlign:"right" ,
        width:430,
        height:140,
        labelSeparator: ' ',
        items:[name_textbox,volume_combo]
    });

    simple.addButton(_("确定"),function(){
        var name=name_textbox.getValue()
        if (name != null) {
          if (name ){
             var url="/cloud/create_AMI";
                url+="?image_id="+node.attributes.id+"&name="+name+"&provider_id="+provider_id+"&account_id="+account_id+"&region_id="+region_id+
                     "&volume_id="+volume_combo.getValue();
                var ajaxReq=ajaxRequest(url,0,"GET",true);
                    ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                               var response=Ext.util.JSON.decode(xhr.responseText);
                               if(response.success){

                                }
                            },
                            failure: function(xhr){
                                Ext.MessageBox.alert( _("Failure"), xhr.statusText);
                            }
                        });
                win.close();

          }
          else{
              Ext.MessageBox.alert(_('错误'), _('请输入一个名称并选择卷组.'));

          }          

        }
    });
    simple.addButton(_("取消"),function(){
        win.close();
    });


    var win=new Ext.Window({
        title:"创建一个新的模板",
        width: 445,
//        layout:'fit',
        height: 160,
        modal: true,
        resizable: false,
        closable:true
    });

    win.add(simple);
    win.show();
   

}

function create_image_from_vm(node, action){
    
    var url="/node/is_vm_running?node_id="+node.attributes.id
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var res=Ext.util.JSON.decode(xhr.responseText);
            if(res.success){
                
                var main_wnd_height = 560;//540
                if(res.has_image){
                    main_wnd_height = 333;
                }

               if(res.running){
                    var msg=format("建议将虚拟机关闭之后进行此操作，确定要继续吗?");
                    Ext.MessageBox.confirm(_("确认"),msg,function(id){
                        if (id == 'yes'){
                             
                            image_from_vm_window(main_wnd_height,res,node, action)
                        }

                     });

                 }else{
                  
                      image_from_vm_window(main_wnd_height,res,node, action)
                 }
                 
            }else{
                Ext.MessageBox.alert(_("Error"),res.msg);
            }
        },
        failure: function(xhr){
            try{
                var res=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), res.msg);
            }catch(e){
                Ext.MessageBox.alert(_("错误"),_("失败e: ") +xhr.statusText);
            }
        }
    });
    
}

function image_from_vm_window(main_wnd_height,res,node, action){
  var w=new Ext.Window({
        title :_('转换模板'),
        width :480,
        height:main_wnd_height,
        modal : true,
        resizable : false,
        listeners: {
        show : function(w) {


        },
        render :function(c,v) {
        }


        }


    });
    
    w.add(ImageFromVM(w,node, action, res));
    w.show();
   
}














