/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function templateform(node){
      var empty_label=new Ext.form.Label({
        html:'<br/><center><font size="1"></center><br/>'
    });
     var template_label=new Ext.form.Label({
        html:'<div class="bluebackgroundcolor" align="center" width="250">'+
            _("使用下列方法创建一个新的模板")+
            '</font><br/></div>'
    });

    var cancel_button=new Ext.Button({
            name: 'close',
            id: 'close',
            text:_('关闭'),
            icon:'icons/cancel.png',
            cls:'x-btn-text-icon',
            listeners: {
                click: function(btn) {

                       closeWindow();
                }
            }
        });
   
    var appliance=new Ext.form.Radio({
        boxLabel: '<font size=2>'+
            _("导入应用")+
            ': </font><table><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>'+
            _("浏览集成的目录，并选择应用程序导入模板.")+
            '</td></table>',
        id:'appliance',
        name:'radio',
        checked:true,
        listeners:{
            check:function(field,checked){               
                 if(checked==true){                    
                 }              
            }}
        });
    var refdisk=new Ext.form.Radio({
        boxLabel: '<font size=2>'+
            _("使用参考磁盘")+
            ' :</font><table><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>'+
            _("将你已下载的参考磁盘或应用转换为模板.")+
            '</td></table>',
        id:'refdisk',
        name:'radio',
        listeners:{
            check:function(field,checked){
                 if(checked==true){                  
                 }
            }}
        });
     var virtualmachine=new Ext.form.Radio({
        boxLabel: '<font size=2>'+
            _("从已存在的虚拟机中")+
            ' :</font><table><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>'+
            _("选择一个现有的虚拟机，将其转换为模板.")+
            '</td></table>',
        id:'virtualmchine',
        name:'radio',
        disabled:true,
        listeners:{
            check:function(field,checked){
                 if(checked==true){                   
                 }               
            }}
        });
    var ok_button=new Ext.Button({
            name: 'ok',
            id: 'ok',
            text:_('确定'),
            icon:'icons/accept.png',
            cls:'x-btn-text-icon',
            listeners: {
                click: function(btn) {
                 if(appliance.getValue()){
                      showTemplateList(node);
                  }
                  else if(refdisk.getValue()){
                      showrefDialog(node);
                  }
                  else{
                  Ext.MessageBox.alert(_('错误'), _('请至少选择一个选项.'));
                  }

                }
            }
        });
    var outerpanel=new Ext.Panel({
         width:390,
         height:280,
         id:'outerpanel',
         frame:true,
         items:[template_label,empty_label,appliance,refdisk],
         bbar:[{
             xtype: 'tbfill'
          },ok_button,cancel_button]

    });

    return outerpanel;
}
 function showTemplateList(node){
    closeWindow();
    var url="/appliance/get_appliance_list";
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: _('获取设备列表中，请稍候...'),
        width:300,
        wait:true,
        waitConfig: {interval:200}
    });

    ajaxReq.request({
        success: function(xhr) {

            Ext.MessageBox.hide();
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                showWindow(_("应用目录"),715,425,ApplianceList(node));
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
function showrefDialog(node){
    closeWindow();
    showWindow(_("参考磁盘详细信息"),575,230,ImportApplianceDialog(node,null));
}

