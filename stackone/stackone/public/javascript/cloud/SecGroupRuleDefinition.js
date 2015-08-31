/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var sec_group_rule_def_form;
var rule_id="";
var rule_connection="";
var rule_protocol="";
var rule_from_port="";
var rule_to_port="";
var rule_source_ip="";
function SecGroupRuleDefinition(vdc_id, acc_id, region_id, mode, rule_rec, windowid_rule) {
    /*
    mode: this would be "NEW" or "EDIT".
    rule_rec: security group rule record (selected record in security grid rule store).
    windowid_rule: window id (e.g., windowid_rule=Ext.id();)
    */

    var rule_rec_template = Ext.data.Record.create([
    {
        name: 'id',
        type: 'string'
    },
    {
        name: 'connection',
        type: 'string'
    },
    {
        name: 'protocol',
        type: 'string'
    },
    {
        name: 'from_port',
        type: 'string'
    },
    {
        name: 'to_port',
        type: 'string'
    },
    {
        name: 'source_ip',
        type: 'string'
    },
    {
        name: 'record_new',
        type: 'string'
    },
    {
        name: 'record_modified',
        type: 'string'
    }
    ]);

    var connection_store=new Ext.data.JsonStore({
        url: '/cloud_network/get_connection_methods?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id,
        root: 'rows',
        fields: ['name', 'port'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    connection_store.load();

    var protocol_store=new Ext.data.JsonStore({
        url: '/cloud_network/get_protocols?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id,
        root: 'rows',
        fields: ['name', 'value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    protocol_store.load();

    var tf_id=new Ext.form.TextField({
        //fieldLabel: _('Id'),
        name: 'id',
        id: 'id',
        width: 200,
        allowBlank:true,
        hidden: true
    });
    var tf_from_port=new Ext.form.TextField({
        fieldLabel: _('From Port'),
        name: 'from_port',
        id: 'from_port',
        width: 200,
        allowBlank:false,
        hidden: false
    });
    var tf_to_port=new Ext.form.TextField({
        fieldLabel: _('To Port'),
        name: 'to_port',
        id: 'to_port',
        width: 200,
        allowBlank:false,
        hidden: false
    });
    var tf_source_ip=new Ext.form.TextField({
        fieldLabel: _('资源 (IP/安全组)'),
        name: 'source_ip',
        id: 'source_ip',
        width: 200,
        allowBlank:false,
        hidden: false
    });

    var cmb_connection=new Ext.form.ComboBox({
        fieldLabel: _('连接方法'),
        triggerAction:'all',
        root:'rows',
        store: connection_store,
        emptyText :_("选择连接方法"),
        //editable:false,
        displayField:'name',
        valueField:'port',
        width: 200,
        allowBlank: false,
        typeAhead: true,
        //forceSelection: true,
        selectOnFocus:true,
        name:'cmb_connection',
        id:'cmb_connection',
        mode:'local',
        listeners: {
            select: function(combo, record, index) {
                tf_from_port.setValue(combo.getValue());
                tf_to_port.setValue(combo.getValue());
                cmb_protocol.setValue("tcp");
            }
        }
    });
    var cmb_protocol=new Ext.form.ComboBox({
        fieldLabel: _('协议'),
        triggerAction:'all',
        root:'rows',
        store: protocol_store,
        emptyText :_("选择协议"),
        editable:false,
        displayField:'name',
        valueField:'value',
        width: 200,
        allowBlank: false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'cmb_protocol',
        id:'cmb_protocol',
        mode:'local'
    });

    var save_button = new Ext.Button({
        name: 'save',
        id: 'save',
        text:_("确定"),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(sec_group_rule_def_form.getForm().isValid()) {
                    var new_rule_rec = new rule_rec_template({
                        id: null,
                        connection: cmb_connection.getRawValue(),
                        protocol: cmb_protocol.getValue(),
                        from_port: tf_from_port.getValue(),
                        to_port: tf_to_port.getValue(),
                        source_ip: tf_source_ip.getValue(),
                        record_new: false,
                        record_modified: false
                    });
                    if(mode == "EDIT") {
                        new_rule_rec.set('id', tf_id.getValue());
                        new_rule_rec.set('record_modified', true);
                        rule_grid.getStore().remove(rule_rec);
                        new_rec_index = rule_grid.getStore().getCount();
                    } else {
                        new_rule_rec.set('record_new', true);
                        new_rec_index = rule_grid.getStore().getCount();
                    }
                    rule_grid.getStore().insert(new_rec_index, new_rule_rec);
                    
                    //reloadSecGroupRuleList();
                    closeWindow(windowid_rule);
                }
            }
        }
    });

    var cancel_button = new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_("取消"),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow(windowid_rule);
            }
        }
    });

    if(mode=="EDIT"){
        if (rule_grid.getSelectionModel().getSelected() != undefined) {
            tf_id.value = rule_rec.get('id');
            cmb_connection.value = rule_rec.get('connection');
            cmb_protocol.value = rule_rec.get('protocol');
            tf_from_port.value = rule_rec.get('from_port');
            tf_to_port.value = rule_rec.get('to_port');
            tf_source_ip.value = rule_rec.get('source_ip');
        }
        cmb_connection.disable();
        tf_from_port.disable();
        tf_to_port.disable();
    } else if(mode == "NEW") {
        tf_source_ip.value = '0.0.0.0/0';
    };

    function get_rule_def_form() {
        sec_group_rule_def_form = new Ext.FormPanel({
            //title: _("Create Key Pair"),
            labelWidth:120,
            frame:true,
            border:0,
            bodyStyle:'padding:0px 0px 0px 0px',
            labelAlign:"left" ,
            height: 190,
            labelSeparator: ' ',
            items:[tf_id, cmb_connection, cmb_protocol, tf_from_port, tf_to_port, tf_source_ip],
            bbar:[{xtype: 'tbfill'},
                save_button,
                '-',
                cancel_button
            ]
        });
        return sec_group_rule_def_form;
    };

    var return_form = get_rule_def_form();
    return return_form;
}
