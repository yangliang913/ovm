/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function Provision(dest_node,img_node,action){

    if(dest_node.attributes.nodetype=='MANAGED_NODE'){
       var node_id=dest_node.attributes.id; 
       var group_id=dest_node.parentNode.attributes.id;
       if (img_node!=null)
            get_initvmconfig(img_node,action,node_id,group_id,dest_node);
       else
             showWindow(_("新建VM"),640,470,VMConfigSettings(action,node_id,group_id,img_node,null,null,null,dest_node));

    }else if(dest_node.attributes.nodetype=='SERVER_POOL'){
        group_id=dest_node.attributes.id;
        var url="/node/get_alloc_node?group_id="+dest_node.attributes.id;
        if(action=='provision_image')
            url+="&image_id="+img_node.attributes.nodeid;
        var ajaxReq=ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                    var n=new Ext.tree.TreeNode({
                       text: response.node.name,
                       nodeid:response.node.name,
                       id:response.node.id
                    });
                    if (img_node!=null)
                        get_initvmconfig(img_node,action,response.node.id,group_id,n); 
                    else{                        
                        showWindow(_("新建VM "),640,470,VMConfigSettings(action,response.node.id,group_id,img_node,null,null,null,n));
                    }
                }else{
                    Ext.MessageBox.alert(_("Failure"),response.msg);
                }
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("Failure") , xhr.statusText); 
            }
        });
    }else{
        Ext.MessageBox.alert(_('警告'),_('无效的选择.'));
        return;
    }
}

function get_initvmconfig(img_node,action,node_id,group_id,dest_node){
    var url="/node/get_initial_vmconfig?image_id="+img_node.attributes.nodeid;
            var ajaxReq=ajaxRequest(url,0,"GET",true);
            ajaxReq.request({
                success: function(xhr) {//alert(xhr.responseText);
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
                        var vm_config=response.vm_config;
                        showWindow(_("新建VM"),640,470,VMConfigSettings(action,node_id,group_id,img_node,null,vm_config,null,dest_node));
                         }
                    else
                        Ext.MessageBox.alert(_("Failure"),response.msg);
                },
                failure: function(xhr){
                    Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                }
            });

}
