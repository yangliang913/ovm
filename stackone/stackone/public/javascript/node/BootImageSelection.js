/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function BootImageSelection(vm,boot){
    var devices=new Ext.form.ComboBox({
        fieldLabel: _('引导设备'),
        triggerAction:'all',
        store: [['d',_('CD ROM')],['c',_('Disk')],['n',_('Network')]],
        width: 150,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'devices',
        id:'devices',
        mode:'local'
    });
    devices.setValue(boot);
    
    var simple = new Ext.FormPanel({
        labelWidth:70,
        frame:true,
        border:0,
        labelAlign:"right" ,
        width:300,
        height:100,
        labelSeparator: ' ',
        items:[devices]
    });

    simple.addButton(_("确定"),function(){
        if (simple.getForm().isValid()) {
            closeWindow();
            setBootDevice(vm,devices.getValue());
        }else{
            Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
        }
    });
    simple.addButton(_("取消"),function(){
        closeWindow();
    });

    return simple;
}

function setBootDevice(vm,value){
    var url="/node/set_boot_device?dom_id="+vm.attributes.id+"&boot="+value;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                if(eval(response.running))
                    Ext.MessageBox.alert(_("Success"),response.msg);
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert(_("Failure"), xhr.statusText);
        }
    });
}