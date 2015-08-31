/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
/*
 * MODES--EDIT_VM_INFO,EDIT_VM_CONFIG
 * panel1--Disks
 * panel2--Networks
 * panel3--BootParams
 * panel4--Miscellaneous
 * panel5--Provisioning
 */
//var stackone={};
stackone.PlatformUIHelper=function(platform,mode){
    this.mode=mode;
    this.platform=platform;
    var xen_in_memory=new Array('vmname','panel2','panel3','panel4'); 
    var xen_on_disk=new Array();
    var kvm_in_memory=new Array('memory','vcpu','boot_loader','boot_check','panel1','panel2','panel3','panel4');
    var kvm_on_disk=new Array('boot_loader','boot_check');
    var vmw_vmtotemplate = new Array('host_storag_fldset');
    var xenkvm_vmtotemplate = new Array('ref_image_fldset');
    var vmw_template_edit = new Array('panel0','panel1','panel2','panel3','panel4','panel5','panel6','panel8');
    
    var vmw_provision_vm = new Array('server_det_panel','vm_config_filename','memory','vcpu','auto_start_vm',
                                    'panel2','panel3','panel4',
                                    'panel5','panel6','panel9','prior_panel');

    var vmw_edit_vm = new Array('vmname','template_version','auto_start_vm','panel1','panel2','panel3','panel4',
                               'panel5','panel6','panel9','panel7');

    var kvm_view_console = new Array('use_applet', 'remember');

    this.getComponentsToDisable=function(){
        if(this.platform==='kvm'){
            if(this.mode==='EDIT_VM_INFO'){
                return kvm_in_memory;
            }else if(this.mode==='EDIT_VM_CONFIG'){
                return kvm_on_disk;
            }else if(this.mode==='VM_TO_TEMPLATE'){
                return vmw_vmtotemplate;
            }else if(this.mode==='PROVISION_VM'){
                return vmw_provision_vm;//Note: For re-enable items disabled in VMware Provision UI.
            }else if(this.mode==='VIEW_CONSOLE'){
                return [];
            }

        }else if(this.platform==='xen'){
            if(this.mode==='EDIT_VM_INFO'){
                return xen_in_memory;
            }else if(this.mode==='EDIT_VM_CONFIG'){
                return xen_on_disk;
            }else if(this.mode==='VM_TO_TEMPLATE'){
                return vmw_vmtotemplate;
            }else if(this.mode==='PROVISION_VM'){
                return vmw_provision_vm;//Note: For re-enable items disabled in VMware Provision UI.
            }else if(this.mode==='VIEW_CONSOLE'){
                return [];
            }
            
        }else if(this.platform==='vmw'||this.platform==='vcenter'){
            if(this.mode==='VM_TO_TEMPLATE'){
                return xenkvm_vmtotemplate;
            }else if(this.mode==='EDIT_TEMPLATE'){
                return vmw_template_edit;
            }else if(this.mode==='PROVISION_VM'){
                return vmw_provision_vm;
            }else if(this.mode==='EDIT_VM'){
                return vmw_edit_vm;
            }else if(this.mode==='VIEW_CONSOLE'){
                return kvm_view_console;
            }
        }
        return (new Array());
    }
    this.isDataStoreSupported=function(){
        if(this.platform==='vmw'){
            return true;
        }
        return false;
    }
    this.getXtraComponents=function(){
        if(this.platform==='vmw'){
            return new Array('host_id','data_store');
        } else if(this.platform==='xen'){
            return new Array('ref_image_fldset');
        } else if(this.platform==='kvm'){
            return new Array('ref_image_fldset');
        }
        return new Array();
    }
}

////////////// UIHelper //////////////

stackone.UIHelper = {}
stackone.UIHelper.attributes = {}

stackone.UIHelper.GetUIHelper = function(node, node_type, ui_type, callback){
//    alert("====node_type==="+node_type);
    var url="/dashboard/get_ui_helper?node_id="+node.attributes.id + "&node_type=" + node_type + "&ui_type=" + ui_type;
    var ajaxReq=ajaxRequest(url,0,"POST", true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                stackone.UIHelper.SetProperty(response.result, ui_type)
                callback();//function need to be customize based on helper items comming from backend.
             }
             else {
                Ext.MessageBox.alert( _("Failure") , response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

stackone.UIHelper.SetProperty = function(result, ui_type){
//    alert(Ext.util.JSON.encode(result));
    if (ui_type == stackone.constants.DB_DASHBOARD){
        stackone.UIHelper.attributes.dashboard = result
    }
}

stackone.UIHelper.GetProperty = function(context){
    if (context == stackone.constants.DB_DASHBOARD){
        return "stackone.UIHelper.attributes.dashboard"
    }
    return undefined
}

stackone.UIHelper.IsEnabled = function(table, context){
    //table ==> item(grid) to be enable or disable
    var cntxt = context.context
    var path = context.path
//    alert("-path----"+path + "---"+ table);
    var root = stackone.UIHelper.GetProperty(cntxt)
//    alert("-root----"+root);
    try{
        var sts = eval(root + "." + path + "." + table);
    }catch(e){
        return true;
    }
//    alert("---sts---"+sts);
    return sts    
}
    

