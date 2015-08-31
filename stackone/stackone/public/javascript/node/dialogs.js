/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function show_dialog(node,responseData,action,vm,objData){
//     alert("show_dialog is called");

    if(objData == undefined || objData == null || objData == "") {
        objData = null;
    }

    if(action=='import'){
        var p = ImportVMConfigDialog(node,responseData,action);
        if (p==null){
            return;
        }
        showWindow(_("选择虚拟机配置文件"),550,425,p,null,false,true);
    }else if(action=='restore')
        showWindow(_("从快照还原"),515,425,FileDialog(node,responseData,action));
    else if(action=='hibernate')
        showWindow(_("保存快照"),515,425,FileDialog(node,responseData,action,vm));
    else if(action=='migrate' || action=='migrate_all' || action=='provision_image' || action=='create_network' || action=='restore_from_backup')
        showWindow(_("选择目标节点"),315,325,NodeSelectionDialog(vm,node,responseData,action,objData));
}

function show_dialog_SP(node,responseData,action,vm,sp,objData){
    if(objData == undefined || objData == null || objData == "") {
        objData = null;
    }

        showWindow(_("选择一个目标服务器池"),315,325,SPSelectionDialog(node,responseData,action,vm,sp,objData));
}