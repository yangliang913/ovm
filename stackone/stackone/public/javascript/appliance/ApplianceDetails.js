/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function ApplianceDetails(node,action,appliance,dom_id,node_id){

    var app_protocol = new Ext.form.ComboBox({
        fieldLabel: _('协议'),
        store: [['http','http'],['https','https']],
        allowBlank:false,
        mode: 'local',
        width: 140,
        triggerAction:'all',
        typeAhead: true,
        forceSelection: true,
        value:'http',
        name:'app_protocol',
        id:'app_protocol'
    });
    var host=new Ext.form.TextField({
        fieldLabel: _('主机名'),
        name: 'host',
        id: 'host',
        allowBlank:false
    });    
    var app_port=new Ext.form.TextField({
        fieldLabel: _('端口'),
        name: 'app_port',
        id: 'app_port',
        allowBlank:false,
        value:80
    });
    var app_path=new Ext.form.TextField({
        fieldLabel: _('路径'),
        name: 'app_path',
        id: 'app_path',
        allowBlank:false,
        value:"/"
    });

    var app_mgmt_protocol = new Ext.form.ComboBox({
        fieldLabel: _('协议'),
        store: [['http','http'],['https','https']],
        allowBlank:false,
        mode: 'local',
        width: 140,
        forceSelection: true,
        value:'https',
        name:'app_mgmt_protocol',
        id:'app_mgmt_protocol'
    });
    var app_mgmt_port=new Ext.form.TextField({
        fieldLabel: _('端口'),
        name: 'app_mgmt_port',
        id: 'app_mgmt_port',
        allowBlank:false,
        value:8003
    });

    var app_fldset=new Ext.form.FieldSet({
        title: _('应用URL'),
        collapsible: false,
        autoHeight:true,
        width: 300,
        items :[ app_protocol,host,app_port,app_path ]
    });
    var mgmt_fldset=new Ext.form.FieldSet({
        title: _('管理URL'),
        collapsible: false,
        autoHeight:true,
        width: 300,
        items :[app_mgmt_protocol,app_mgmt_port ]
    });

    var simple = new Ext.FormPanel({
        labelWidth:70,
        frame:true,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        labelAlign:"right" ,
        width:300,
        height:300,
        labelSeparator: ' ',
        items:[app_fldset,mgmt_fldset]
    });
    //alert("++"+appliance.app_protocol+"==="+appliance.app_mgmt_protocol+"\\\\");
    app_protocol.setValue((appliance.app_protocol!=null)?appliance.app_protocol:"http");
    host.setValue(appliance.host);
    app_port.setValue((appliance.app_port!="")?appliance.app_port:80);
    app_path.setValue(appliance.app_path);
    app_mgmt_protocol.setValue((appliance.app_mgmt_protocol!=null)?appliance.app_mgmt_protocol:"https");
    app_mgmt_port.setValue((appliance.app_mgmt_port!="")?appliance.app_mgmt_port:"8003");

    var url="/appliance/save_appliance_info?dom_id="+dom_id+"&node_id="+node_id+"&action="+action;
    simple.addButton(_("确定"),function(){
        if (simple.getForm().isValid()) {
            if(isNaN(app_mgmt_port.getValue()) || isNaN(app_port.getValue())){
                Ext.Msg.alert(_("警告"), _("端口应该是数字."));
                return;
            }
            simple.getForm().submit({
                url:url,
                success: function(form,act) {
                    //Ext.Msg.alert("Success",action.result.msg );
                    closeWindow();
                    doApplianceAction(action,act.result.appliance)
                },
                failure: function(form, action) {
                    Ext.Msg.alert("失败",action.result.msg );
                }
            });
        }else{
            Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
        }
    });
    simple.addButton(_("取消"),function(){
        closeWindow();
    });

    return simple;
}

