/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function select_platform(prntNode){

    var store = new Ext.data.JsonStore({
        url: '/get_platforms?',
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
    var platform = new Ext.form.ComboBox({
        fieldLabel: _('选择平台'),
        allowBlank:false,
        store: store,
        emptyText :"选择平台",
        mode: 'local',
        displayField:'name',
        valueField:'value',
        width: 140,
        triggerAction :'all',
        forceSelection: true,
        name:'plat_form'        
    });

    var simple = new Ext.FormPanel({
        labelWidth:120,
        frame:true,
        border:0,
        labelAlign:"right" ,
        width:300,
        height:100,
        labelSeparator: ' ',
        items:[platform]
    });

    simple.addButton(_("确定"),function(){
        if (simple.getForm().isValid()) {
            closeWindow();
            if(platform.getValue()=='xen')
                showWindow(_("添加主机"),330,340,XenUI(null,prntNode,'add'));
            else if(platform.getValue()=='kvm')
                showWindow(_("添加主机"),330,265,KVMUI(null,prntNode,'add',null,platform.getValue()));
            else if(platform.getValue() == "vmw")
                showWindow(_("添加主机"),330,165,ESXiUI(null,prntNode,'add',null,platform.getValue()));
        }else{
            Ext.MessageBox.alert(_('错误'), _('请选择一个平台.'));
        }
    });
    simple.addButton(_("取消"),function(){
        closeWindow();
    });

    return simple;
}

function show_platform(node,nodeinfo){
    var platform=nodeinfo.platform;
    if(platform=='xen')
        showWindow(_("编辑主机")+node.text,330,340,XenUI(node,node.parentNode,'edit',nodeinfo));
    else if(platform=='kvm')
        showWindow(_("编辑主机")+node.text,330,265,KVMUI(node,node.parentNode,'edit',nodeinfo,platform));
    else if(platform=='vmw')
        showWindow(_("编辑主机")+node.text,330,165,ESXiUI(node,node.parentNode,'edit',nodeinfo,platform));
}
