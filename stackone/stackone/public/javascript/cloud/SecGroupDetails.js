/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
var sec_group_details_form=null;
var rule_grid=null;
var rule_record_list="";
var rule_deleted_record_list="";
function SecGroupDetails(vdc_id, mode, sec_group, windowid_sgd){
    /*
    mode: this would be "NEW" or "EDIT".
    sec_group: security group record (selected record in security grid store).
    windowid_sgd: window id (e.g., windowid_sgd=Ext.id();)
    */
    var tf_sec_group_id=new Ext.form.TextField({
        //fieldLabel: _('Id'),
        name: 'sec_group_id',
        id: 'sec_group_id',
        width: 200,
        allowBlank:true,
        hidden: true
    });
    var tf_sec_group_name=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'sec_group_name',
        id: 'sec_group_name',
        width: 200,
        allowBlank:false,
        hidden: false
    });
    var tf_sec_group_desc=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'sec_group_desc',
        id: 'sec_group_desc',
        width: 200,
        allowBlank:false,
        hidden: false
    });

    var cmb_region = create_region_dropdown(vdc_id);
    cmb_region.width = 200;

    var cmb_account=null;
    if (mode=="PROVISION"||mode=="PROV_EDIT"){
        cmb_account = create_account_dropdown(vdc_id,null,"sec_grp");
        cmb_account.setValue(Ext.getCmp("account").getRawValue());
        cmb_account.disable();
        cmb_region.setValue(Ext.getCmp("region_general").getRawValue());
        cmb_region.disable();
    }
    else
        cmb_account = create_account_dropdown(vdc_id, "provision");
    cmb_account.width = 200;

    if(mode=="EDIT"){
        if (sec_group_grid.getSelectionModel().getSelected() != undefined) {
            tf_sec_group_id.value = sec_group.get('id');
            tf_sec_group_name.value = sec_group.get('name');
            tf_sec_group_desc.value = sec_group.get('description');
            cmb_account.setValue(sec_group.get('account_name'));
            cmb_region.setValue(sec_group.get('region'));
        }
        tf_sec_group_name.disable();
        cmb_region.disable();
        cmb_account.disable();
    }
    if(mode=="PROV_EDIT"){
        tf_sec_group_id.value = sec_group.get('id');
        tf_sec_group_name.value = sec_group.get('name');
        tf_sec_group_desc.value = sec_group.get('description');
        tf_sec_group_name.disable();
    }

    var ruleColumnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), hidden: true, dataIndex: 'id'},
        {header: _("连接方法"), width: 120, sortable: true, dataIndex: 'connection'},
        {header: _("协议"), width: 65, sortable: true, dataIndex: 'protocol'},
        {header: _("From Port"), width: 70, hidden: false, sortable: true, dataIndex: 'from_port'},
        {header: _("To Port"), width: 55, hidden: false, sortable: true, dataIndex: 'to_port'},
        {header: _("资源(IP/安全组)"), width: 140, hidden: false, sortable: true, dataIndex: 'source_ip'},
        {header: _("新的记录"), width: 55, hidden: true, sortable: true, dataIndex: 'record_new'},
        {header: _("修改记录"), width: 55, hidden: true, sortable: true, dataIndex: 'record_modified'}
    ]);

    var rule_store;

    if (mode=="PROV_EDIT"){
        rule_store = sec_group.get("rules_store");
        var acc_id = sec_group.get("account_id");
        var region_id = sec_group.get("region_id");
        rule_store = new Ext.data.JsonStore({
            url: '/cloud_network/get_rule_list?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&security_group_id=' + sec_group.get('id') + '&security_group_name=' + sec_group.get('name'),
            root: 'rows',
            fields: ['id', 'connection', 'protocol', 'from_port', 'to_port', 'source_ip', 'record_new', 'record_modified'],
            successProperty:'success'
        });
        rule_store.load();


    }

    if(mode == "EDIT") {
        var acc_id = sec_group.get("account_id");
        var region_id = sec_group.get("region_id");

        rule_store = new Ext.data.JsonStore({
            url: '/cloud_network/get_rule_list?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&security_group_id=' + sec_group.get('id') + '&security_group_name=' + sec_group.get('name'),
            root: 'rows',
            fields: ['id', 'connection', 'protocol', 'from_port', 'to_port', 'source_ip', 'record_new', 'record_modified'],
            successProperty:'success'
        });
        rule_store.load();
    } else if(mode=="NEW"|| mode=="PROVISION") {
        rule_store = new Ext.data.JsonStore({
            root: 'rows',
            fields: ['id', 'connection', 'protocol', 'from_port', 'to_port', 'source_ip', 'record_new', 'record_modified'],
            autoLoad: true
            //data: {rows: [{'id':'', 'connection':'', 'protocol':'', 'from_port':'', 'to_port':'', 'source_ip':'', 'record_new':false, 'record_modified':false}]}
        });
    }

    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var new_button=new Ext.Button({
        name: 'add_key',
        id: 'add_key',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                rule_grid.getSelectionModel().clearSelections();
                var acc_id = cmb_account.getValue("id");
                var region_id = cmb_region.getValue("id");
                if(!acc_id) {
                    Ext.MessageBox.alert("信息", "请选择账户.");
                    return;
                } else if(!region_id) {
                    Ext.MessageBox.alert("信息", "请选择区域.");
                    return;
                }
                windowid_rule=Ext.id();
                showWindow(_("创建规则"),380,220,SecGroupRuleDefinition(vdc_id, acc_id, region_id, "NEW",null,windowid_rule),windowid_rule);//435
            }
        }
    });

    var remove_button=new Ext.Button({
        name: 'remove_key',
        id: 'remove_key',
        text:_("移除"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedRule(rule_grid)){
                    if(rule_grid.getSelectionModel().getCount()>0){
                        if (rule_grid.getSelectionModel().getSelected() != undefined) {
                            var rec=rule_grid.getSelectionModel().getSelected();
                            var rule_id = rec.get('id');
                            var rule_connection = rec.get('connection');
                            var rule_protocol = rec.get('protocol');
                            var rule_from_port = rec.get('from_port');
                            var rule_to_port = rec.get('to_port');
                            var rule_source_ip = rec.get('source_ip');
                            var rule_security_group_id = tf_sec_group_id.getValue();
                            var rule_security_group_name = tf_sec_group_name.getValue();

                            if(rule_deleted_record_list.length >= 2) {  //e.g., []
                                rule_deleted_record_list = String(rule_deleted_record_list).replace("]", ",");
                            } else if(rule_deleted_record_list.length == 0) {
                                rule_deleted_record_list = "["
                            }
                            var record_dic = "{";
                            if(rule_id != "" &&  rule_id != undefined) {
                                record_dic += 'id:"' + rule_id + '"';
                                record_dic += ',connection:"' + rule_connection + '"';
                                record_dic += ',protocol:"' + rule_protocol + '"';
                                record_dic += ',from_port:"' + rule_from_port + '"';
                                record_dic += ',to_port:"' + rule_to_port + '"';
                                record_dic += ',source_ip:"' + rule_source_ip + '"';
                                record_dic += ',security_group_id:"' + rule_security_group_id + '"';
                                record_dic += ',security_group_name:"' + rule_security_group_name + '"';
                            }
                            record_dic += "}";
                            rule_deleted_record_list += record_dic;
                            rule_deleted_record_list += "]";
            
//                             alert("rule_deleted_record_list=" + rule_deleted_record_list);
                            rule_grid.getStore().remove(rec);
                        }
                    }
                }
            }
        }
    });
    
    var edit_button=new Ext.Button({
        name: 'edit_key',
        id: 'edit_key',
        text:_("编辑"),
        icon:'icons/storage_edit.png',
        cls:'x-btn-text-icon',
        hidden:true,
        listeners: {
            click: function(btn) {
                if(checkSelectedRule(rule_grid)){
                    var rec = rule_grid.getSelectionModel().getSelected();
                    var acc_id = sec_group.get("account_id");
                    var region_id = sec_group.get("region_id");
                    if(!acc_id) {
                        Ext.MessageBox.alert("信息", "请选择账户.");
                        return;
                    } else if(!region_id) {
                        Ext.MessageBox.alert("信息", "请选择区域.");
                        return;
                    }
                    windowid_rule=Ext.id();
                    showWindow(_("编辑规则"),380,220,SecGroupRuleDefinition(vdc_id, acc_id, region_id, "EDIT",rec,windowid_rule),windowid_rule);
                }
            }
        }
    });

    var cancel_button = new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {closeWindow(windowid_sgd);}
        }
    });

    var save_button = new Ext.Button({
        name: 'save',
        id: 'save',
        text:((mode=="EDIT")? _("保存"):_("创建")),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(sec_group_details_form.getForm().isValid()){
                    var wait_msg, success_msg, acc_id, region_id, sg_id, sg_record_new, sg_record_modified;
                    var sg_name = tf_sec_group_name.getValue();

                    if(mode == "NEW") {
                        sg_id = null;
                        sg_record_new = true;
                        sg_record_modified = false;
                        acc_id = cmb_account.getValue();
                        region_id = cmb_region.getValue();
                        wait_msg = _('正在创建安全组...');
                        success_msg = ("安全组 " + sg_name + " 创建成功.");
                    }
                    else if(mode=="EDIT"){
                        sg_id = tf_sec_group_id.getValue();
                        sg_record_new = false;
                        sg_record_modified = true;
                        acc_id = sec_group.get("account_id");
                        region_id = sec_group.get("region_id");
                        wait_msg = _('正在更新安全组...');
                        success_msg = ("安全组 " + sg_name + "更新成功.");
                    }else if(mode == "PROVISION") {
                        sg_id = null;
                        sg_record_new = true;
                        sg_record_modified = false;
                        acc_id = Ext.getCmp("account").getValue();
                        region_id = Ext.getCmp("region_general").getValue();
                        wait_msg = _('正在创建安全组...');
                        success_msg = ("安全组 " + sg_name + "创建成功.");
                    }
                    if(mode == "NEW" || mode == "EDIT" || mode == "PROVISION") {

                       var sg_record_list = "["

                                var sec_record_dic = "{";
                                if(sg_id == null) {
                                    sec_record_dic += 'id:' + null;
                                }else {
                                    sec_record_dic += 'id:"' + sg_id + '"';
                                }
                                sec_record_dic += ',name:"' + tf_sec_group_name.getValue() + '"';
                                sec_record_dic += ',description:"' + tf_sec_group_desc.getValue() + '"';
                                sec_record_dic += ',region_id:"' + region_id + '"';
                                sec_record_dic += ',account_id:"' + acc_id + '"';
                                sec_record_dic += ',record_new:' + sg_record_new;
                                sec_record_dic += ',record_modified:' + sg_record_modified;
                                sec_record_dic += "}";

                                sg_record_list = sg_record_list + sec_record_dic;
                        sg_record_list += "]";

                        var obj_SG = new Object();
                        sg_record_list = eval(sg_record_list);
                        obj_SG.records = sg_record_list;
                        sg_data = Ext.util.JSON.encode(obj_SG);

                        var rule_record_lists;
                        var rule_r_list="[";
                        for(var i=0; i<rule_grid.getStore().getCount(); i++){
                            var rec = rule_grid.getStore().getAt(i);
                            if(rec.get("record_new") == true || rec.get("record_modified") == true) {
                                var record_dic = "{";
                                if(rec.get('id') == "") {
                                    record_dic += 'id:' + null;
                                }else {
                                    record_dic += 'id:"' + rec.get('id') + '"';
                                }
                                record_dic += ',connection:"' + rec.get('connection') + '"';
                                record_dic += ',protocol:"' + rec.get('protocol') + '"';
                                record_dic += ',from_port:"' + rec.get('from_port') + '"';
                                record_dic += ',to_port:"' + rec.get('to_port') + '"';
                                record_dic += ',source_ip:"' + rec.get('source_ip') + '"';
                                record_dic += ',security_group_id:"' + tf_sec_group_id.getValue() + '"';
                                record_dic += ',security_group_name:"' + tf_sec_group_name.getValue() + '"';

                                if(rec.get('record_new') == undefined) {
                                    record_dic += ',record_new:' + true;
                                }else{
                                    record_dic += ',record_new:' + rec.get('record_new');
                                }

                                if(rec.get('record_modified') == undefined) {
                                    record_dic += ',record_modified:' + false;
                                }else {
                                    record_dic += ',record_modified:' + rec.get('record_modified');
                                }

                                if(i==(rule_grid.getStore().getCount()-1) || (rule_grid.getStore().getCount())==1){
                                    record_dic += "}";
                                }else{
                                    record_dic += "},";
                                }

                                rule_r_list = rule_r_list + record_dic;
                            }
                        }
                        rule_r_list += "]";

                        var obj_Rule = new Object();
                        rule_record_lists = eval(rule_r_list);
                        obj_Rule.records = rule_record_lists;
                        rule_data = Ext.util.JSON.encode(obj_Rule);

                        var rule_deleted_data;
                        if(rule_deleted_record_list.length <= 4) {  //e.g., [{}]
                            rule_deleted_data="NONE";
                        } else if(rule_deleted_record_list.length > 4) {    //e.g., [{}]
                            var obj_Rule = new Object();
                            rule_deleted_record_list = eval(rule_deleted_record_list);
                            obj_Rule.records = rule_deleted_record_list;
                            rule_deleted_data = Ext.util.JSON.encode(obj_Rule);
                            rule_deleted_record_list = "";
                        }



                        var url='/cloud_network/manage_security_group?vdc_id=' + vdc_id + '&acc_id=' + acc_id +
                            '&region_id=' + region_id + '&sg_data=' + sg_data + '&sg_deleted_data=NONE' +
                              '&rule_data=' + rule_data + '&rule_deleted_data=' + rule_deleted_data + '&mode=' + mode;
                        // alert("url=" + url);

                        var ajaxReq=ajaxRequest(url,0,"GET",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                        var task_id = response.task_id;
                                        var wait_time = 3000;
                                        wait_for_sg_task(task_id, wait_time, wait_msg, success_msg, windowid_sgd,mode,vdc_id);
                                }else{
                                    Ext.MessageBox.alert("失败",response.msg);
                                }
                            },
                            failure: function(xhr){
                                Ext.MessageBox.alert( "失败" , xhr.statusText);
                            }
                        });


                    }else if(mode == "PROV_EDIT") {

//                            alert(rule_deleted_record_list);
                            var rule_deleted_data;
                            if(rule_deleted_record_list.length>0){
                                var obj_Rule = new Object();
                                rule_deleted_record_list = eval(rule_deleted_record_list);
                                obj_Rule.records = rule_deleted_record_list;
                                rule_deleted_data = Ext.util.JSON.encode(obj_Rule);
                            }else{
                                rule_deleted_data="NONE"
                           }
                           rule_deleted_record_list="";


                            var rule_records = "["
                            for(var i=0; i<rule_grid.getStore().getCount(); i++){
                                var rec = rule_grid.getStore().getAt(i);
                                if(rec.get("record_new") == true || rec.get("record_modified") == true) {
                                    var record_dic = "{";
                                    if(rec.get('id') == "") {
                                        record_dic += 'id:' + null;
                                    }else {
                                        record_dic += 'id:"' + rec.get('id') + '"';
                                    }
                                    record_dic += ',connection:"' + rec.get('connection') + '"';
                                    record_dic += ',protocol:"' + rec.get('protocol') + '"';
                                    record_dic += ',from_port:"' + rec.get('from_port') + '"';
                                    record_dic += ',to_port:"' + rec.get('to_port') + '"';
                                    record_dic += ',source_ip:"' + rec.get('source_ip') + '"';
                                    record_dic += ',security_group_id:"' + tf_sec_group_id.getValue() + '"';
                                    record_dic += ',security_group_name:"' + tf_sec_group_name.getValue() + '"';

                                    if(rec.get('record_new') == undefined) {
                                        record_dic += ',record_new:' + false;
                                    }else{
                                        record_dic += ',record_new:' + rec.get('record_new');
                                    }

                                    if(rec.get('record_modified') == undefined) {
                                        record_dic += ',record_modified:' + false;
                                    }else {
                                        record_dic += ',record_modified:' + rec.get('record_modified');
                                    }

                                    if(i==(rule_grid.getStore().getCount()-1) || (rule_grid.getStore().getCount())==1){
                                        record_dic += "}";
                                    }else{
                                        record_dic += "},";
                                    }

                                    rule_records = rule_records + record_dic;
                                }
                            }
                            rule_records += "]";
        //                     alert("rule_record_list=" + rule_record_list);
                            rule_records = rule_records;

                            var rule_data;

                            if(rule_records.length>0){
                                var obj_Rule = new Object();
                                rule_records = eval(rule_records);
                                obj_Rule.records = rule_records;
                                rule_data = Ext.util.JSON.encode(obj_Rule);
                            }else{
                                rule_data="NONE";
                            }

                        
                            var url='/cloud_network/manage_security_group?vdc_id=' + vdc_id + '&acc_id=' + Ext.getCmp("account").getValue() +
                                '&region_id=' + Ext.getCmp("region_general").getValue() + '&sg_data=NONE' +  '&sg_deleted_data=NONE' +
                                  '&rule_data=' + rule_data + '&rule_deleted_data='+rule_deleted_data + '&mode=' + mode;
                            // alert("url=" + url);
                            var msg=_('正在更新安全组...');

                            var ajaxReq=ajaxRequest(url,0,"GET",true);
                            ajaxReq.request({
                                success: function(xhr) {
                                    var response=Ext.util.JSON.decode(xhr.responseText);
                                    if(response.success){
                                        closeWindow(windowid_sgd);
                                    }else{
                                        Ext.MessageBox.alert("失败",response.msg);
                                    }
                                },
                                failure: function(xhr){
                                    Ext.MessageBox.alert( "失败 " , xhr.statusText);
                                }
                            });

                    }
                }else{
                    Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
                }
            }
        }
    });

    rule_grid = new Ext.grid.GridPanel({
        store: rule_store,
        colModel:ruleColumnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:selmodel,
        width:474, //415
        height:170, //365 //180
        enableHdMenu:false,
        style:'padding:10px 0px 0px 0px',   //top, right, bottom, left
        tbar:[{xtype: 'tbfill'},
            new_button,
            '-',
            edit_button,
            '-',
            remove_button,
            '-'
        ],
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                edit_button.fireEvent('click',edit_button);
            }
         }
    });

    var lbl_border1=new Ext.form.Label({
         html:'<div style=""><br></div>'
    });
    var lbl_rule_heading=new Ext.form.Label({
         html:'<div style="font-weight:bold; padding:5px 0px 0px 0px"><font>安全组规则:</font></div>'
    });
    var lbl_rule=new Ext.form.Label({
         html:'<div style="" class="labelheading">这代表选定的安全组规则</div>'
    });

    sec_group_details_form = new Ext.FormPanel({
        //title: _(""),
        labelWidth:80, //150
        frame:true,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',    //top, right, bottom, left
        labelAlign:"left" ,
        autoHeight:true,
        labelSeparator: ' ',
        items:[tf_sec_group_id, tf_sec_group_name, tf_sec_group_desc, cmb_account, cmb_region, lbl_border1, lbl_rule_heading, rule_grid],
        bbar:[{xtype: 'tbfill'},
            save_button,
            '-',
            cancel_button
        ]
    });
     if(cmb_account.getStore().getCount()==0){
            cmb_account.hide();
            cmb_account.hideLabel = true;
            rule_grid.height=190;

     }
    return sec_group_details_form;
}

function checkSelectedRule(grid){
    if(grid.getSelections().length==0){
        Ext.MessageBox.alert(_("警告"),_("请选择一条规则"));
        return false;
    }
    return true;
}

function reloadSecGroupRuleList(){
    rule_grid.getStore().load();
}