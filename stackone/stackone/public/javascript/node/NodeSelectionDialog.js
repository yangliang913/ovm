/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
var provision_node_tree;
function NodeSelectionDialog(vm,node,jsonData,action, objData){    
//     alert("NodeSelectionDialog is called");
    var root_visible = true;
    if(action=='create_image_from_vm'){
        root_visible = false;
    }
    var lbl=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("只有连接的服务器将会显示在这里.")+'</div><br>'
    });
    var node_tree=new Ext.tree.TreePanel({
        rootVisible      : root_visible,
        useArrows        : true,
        collapsible      : false,
        animCollapse     : false,
        border           : false,
        id               : "tree_nodelist",
        autoScroll       : true,
        animate          : false,
        enableDD         : false,
        containerScroll  : true,
        layout           : 'fit'
    });

    var panel = new Ext.Panel({
        layout:'form',
        bodyStyle:'padding:0px 0px 0px 3px',
        labelWidth:60,
        labelSeparator:' ',
        cls: 'whitebackground',
        width:300,
        height:300,
        autoScroll:true,
        bbar:[
            new Ext.form.Checkbox({
                name: 'live',
                id: 'live',
                boxLabel:_('实时迁移'),
                checked:true,
                hidden:(action=='provision_image' || action=='create_network' || action=='restore_from_backup'||action=='create_image_from_vm')
            }),
            {xtype: 'tbfill'},
            new Ext.Button({
                name: 'ok',
                id: 'ok',
                text:_('确定'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        if(action=='create_image_from_vm'){
                            var selected_node = node_tree.getSelectionModel().getSelectedNode()
                             Ext.getCmp('host_name').setValue(selected_node.text);
                             Ext.getCmp('host_id').setValue(selected_node.id);
                             closeWindow();

                        }else{
                           submitNodeSelection(node_tree,node,vm,panel,action,objData);
                        }
                        
                    }
                }
            }),
            '-',
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('取消'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {closeWindow();}
                }
            })
        ]
    });
    panel.add(lbl);
    panel.add(node_tree);
    
    var dataNode = new Ext.tree.TreeNode({
        text: _("数据中心"),
        draggable: false,
        iconCls: "small_pool",
        id: "data_center",
        leaf:false,
        expandable:true,
        expanded:true,
        nodetype:"DATA_CENTER"
    });
    node_tree.setRootNode(dataNode);

    new Ext.tree.TreeSorter(node_tree,{
        folderSort:true,
        dir:'ASC'
    });
    var nodes=jsonData.nodes;
    appendChildren(nodes,dataNode);
    dataNode.expand();
    provision_node_tree = node_tree;

    return panel;
}

function appendChildren(nodes,prntNode){
    
    for(var i=0;i<nodes.length;i++){
        var iconcls=nodes[i].type+"_icon";
        if(nodes[i].platform!=null){
            iconcls=nodes[i].platform+"_icon";
        }
        var node = new Ext.tree.TreeNode({
            text: nodes[i].name,
            id:nodes[i].id,
            draggable: false,
            iconCls: iconcls,
            leaf:false,
            nodetype:nodes[i].type,
            nodeid:nodes[i].name
        });
        appendChildren(nodes[i].children,node);
        prntNode.appendChild(node);
    }
}

function submitNodeSelection(node_tree,node,vm,panel,action,objData){
    var dest_node=node_tree.getSelectionModel().getSelectedNode();

    if(action=='provision_image'){
        closeWindow();
        var n=leftnav_treePanel.getNodeById(dest_node.attributes.id);
        dest_node=(n!=null?n:dest_node);
        Provision(dest_node,node,action);
    }else if(action=='create_network'){
        if(dest_node.attributes.nodetype!='MANAGED_NODE'){
            Ext.MessageBox.alert(_('警告g'),_('请选择一个管理节点.'));
            return;
        }
        closeWindow();
        //When menu is invoked at server level
        site_id = dest_node.parentNode.parentNode.attributes.id;
        strOpLevel = "S";
        group_id = dest_node.parentNode.attributes.id;
        node_id = dest_node.attributes.id;

        OpenNewNetworkDialog(dest_node, site_id, group_id, node_id, strOpLevel);
    }else if(action=='restore_from_backup'){
//         alert("After click in restore_vm");
        if(dest_node == null) {
            Ext.MessageBox.alert(_('警告'),_('请选择一个虚拟机.'));
            return;
        }
        if(dest_node.attributes.nodetype!='DOMAIN'){
            Ext.MessageBox.alert(_('警告'),_('请选择一个虚拟机.'));
            return;
        }
        closeWindow();
        //When menu is invoked at server level
        site_id = dest_node.parentNode.parentNode.parentNode.attributes.id;
        group_id = dest_node.parentNode.parentNode.attributes.id;
        node_id = dest_node.parentNode.attributes.id;
        vm_id = dest_node.attributes.id;
        call_RestoreRecentBackup(dest_node, vm_id, action) //from node/RestoreBackup.js

//         alert("objData.backup_type=" + objData.backup_type);
//         alert("objData.lvm_present=" + objData.lvm_present);
//         alert("objData.backup_content=" + objData.backup_content);
//         alert("objData.selective_content=" + objData.selective_content);
//         alert("objData.vm_id=" + objData.vm_id);
//         alert("objData.result_id=" + objData.result_id);

        //ask for reference vm disk (if it is HOT and LVM as well as CONTENT COPY and SELECTIVE CONTENT)
        /*
        if((objData.backup_type=="HOT" && objData.lvm_present==true) || (objData.backup_content=="CONTENT" && objData.selective_content==true)) {
            Restore(objData.vm_id, objData.result_id, node_id); //from node/RestoreBackup.js
        } else {
            RestoreBackup(node_id, objData.vm_id, "", objData.result_id, false);   //from node/RestoreBackup.js
        }
        */
    }else{
        if(dest_node.attributes.nodetype!='MANAGED_NODE'){
            Ext.MessageBox.alert(_('警告'),_('请选择一个管理节点.'));
            return;
        }
        closeWindow();
        migrateVM(vm,node,dest_node,panel.getBottomToolbar().items.get('live'). getValue(),'false');
    }
}
