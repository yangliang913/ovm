/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var elements=new Array('share','mount_point','mount_options','username','password',
                            'portal','server','target','lun','options','interface','volume_group','windows_share',
                            'windows_username','windows_password','domain','device','host_adapter','bus_channel', 'lun');

var type_elements_map=new Array();
type_elements_map['nfs']='server,share,mount_point';//,mount_options
type_elements_map['iscsi']='portal,target,username,password';//,username,password,options
type_elements_map['aoe']='interface';
type_elements_map['lvm']='volume_group';
type_elements_map['cifs']='server,windows_share,mount_point,windows_username,windows_password,domain';
type_elements_map['gfs']='device,mount_point';
type_elements_map['ocfs']='device,mount_point';
type_elements_map['fc']='host_adapter,bus_channel,target,lun';

var type_props_map=new Array();
type_props_map['nfs']='server,share,mount_point,mount_options';
type_props_map['iscsi']='server,target,username,password,options';
type_props_map['aoe']='interface';
type_props_map['lvm']='volume_group';
type_props_map['cifs']='server,windows_share,mount_point,windows_username,windows_password,domain';
type_props_map['gfs']='device,mount_point';
type_props_map['ocfs']='device,mount_point';
type_props_map['fc']='host_adapter,bus_channel,target,lun';

var type_reqd_elements_map=new Array();
type_reqd_elements_map['nfs']='share,mount_point';
type_reqd_elements_map['iscsi']='portal,target';
type_reqd_elements_map['aoe']='';
type_reqd_elements_map['lvm']='volume_group';
type_reqd_elements_map['cifs']='server,windows_share,mount_point,windows_username,windows_password,domain';
type_reqd_elements_map['gfs']='device,mount_point';
type_reqd_elements_map['ocfs']='device,mount_point';
type_reqd_elements_map['fc']='host_adapter';

var total_cap=null,storage_def_form;

var storage_dc_grid, nw_def_title;
var show_available_storages;
var hideShowAllCheckbox;
var hideManagedServerText = false;
var unique_path=null;
var vmConfigAction;
var diskOption=null;
var sVolumeGroup=null;

function StorageDefinition(node, mode, storage, storage_scope, host, vm_config_action, disk_mode, change_seting_mode, windowid, disks_option) {
    var storage_id="",storage_type="",storage_name="";
    vmConfigAction = vm_config_action;
    diskOption = disks_option;
    test_button_caption = 'Test';

    //We are checking whether the node passed is server or servergroup.
    if(node.attributes.nodetype == 'DATA_CENTER'){
        //When menu is invoked at data center level
        //Consider the node is a data center
        //node and group would be null
        sSiteId = "site_id=" + node.attributes.id;
        op_level = "&op_level=DC";
        sGroupId = "";
        sNodeId = "";
    }
    else if(node.attributes.nodetype == 'SERVER_POOL'){
        //When menu is invoked at server pool level
        //Consider the node is a group (server pool)
        //node would be null
        sSiteId = "site_id=" + node.parentNode.attributes.id;
        op_level = "&op_level=SP";
        sGroupId = "&group_id=" + node.attributes.id;
        sNodeId = "";
    }
    else if(node.attributes.nodetype == 'MANAGED_NODE'){
        //When menu is invoked at server level
        //Consider the node is a server
        sSiteId = "site_id=" + node.parentNode.parentNode.attributes.id;
        op_level = "&op_level=S";
        sGroupId = "&group_id=" + node.parentNode.attributes.id;
        sNodeId = "&node_id=" + node.attributes.id;
    }
    else if(node.attributes.nodetype == 'DOMAIN'){
        //When menu is invoked at vm level
        //Consider the node is a vm
        sSiteId = "site_id=" + node.parentNode.parentNode.parentNode.attributes.id;
        op_level = "&op_level=D";
        sGroupId = "&group_id=" + node.parentNode.parentNode.attributes.id;
        sNodeId = "&node_id=" + node.parentNode.attributes.id;
    }
    else{
        //When menu is invoked at server level
        //Consider the node is a server
        sSiteId = "site_id=" + node.parentNode.parentNode.attributes.id;
        op_level = "&op_level=S";
        sGroupId = "&group_id=" + node.parentNode.attributes.id;
        sNodeId = "&node_id=" + node.attributes.id;
    }
    
    if (menu_context.context_type=="grid"){
        var nodes=menu_context.nodes;
        if (nodes[0][2]=='MANAGED_NODE'){
            sSiteId = "site_id=" + nodes[2][0];
            op_level = "&op_level=S";
            sGroupId = "&group_id=" + nodes[1][0];
            sNodeId = "&node_id=" + nodes[0][0];
        }else if(nodes[0][2]=='DOMAIN'){
            sSiteId = "site_id=" +leftnav_treePanel.getNodeById(nodes[2][0]).parentNode.attributes.id;
            op_level = "&op_level=S";
            sGroupId = "&group_id=" + nodes[2][0];
            sNodeId = "&node_id=" + nodes[1][0];
        }
    }

    if(mode == "NEW") {
        nw_def_title = "定义";
        sSelectedDefId = "";
        hideShowAllCheckbox=true;
        hideManagedServerText=false;
        manageServerTitle = '验证/选择存储';
        test_button_caption = '扫描';
    } else if (mode == "EDIT") {
        nw_def_title = "定义";
        sSelectedDefId = "&def_id=" + storage.get('id');
        hideShowAllCheckbox=true;
        hideManagedServerText=false;
        manageServerTitle = '验证/选择存储';
        test_button_caption = '扫描';
    } else if (mode == "TEST") {
        nw_def_title = "";
        sSelectedDefId = "";
        hideShowAllCheckbox=true;
        show_available_storages=false;
        hideManagedServerText=false;
        manageServerTitle = '验证 / 选择存储';
        test_button_caption = 'Test';
    } else if (mode == "SELECT") {
        nw_def_title = "";
        sSelectedDefId = "";
        hideShowAllCheckbox=false;
        show_available_storages=true;
        hideManagedServerText=true;
        manageServerTitle = '选择存储';
    } else {
        nw_def_title = "";
        sSelectedDefId = "";
        hideShowAllCheckbox=false;
        show_available_storages=false;
        hideManagedServerText=false;
        manageServerTitle = '验证 / 选择存储';
    }

    var type_store = new Ext.data.JsonStore({
        url: '/storage/get_storage_types',
        root: 'rows',
        fields: ['name', 'value'],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load:function(store,recs,opts){
                if(mode=="NEW"){
                    types.setValue(recs[0].get('value'));
                    types.fireEvent('select',types,recs[0],0);

                }else if(mode=="TEST"||mode=="EDIT"){
                    types.setValue(storage.get('type'));
                }
            }
        }
    });

    type_store.load();

    var types=new Ext.form.ComboBox({
        fieldLabel: _('类型'),
        triggerAction:'all',
        store: type_store,
        emptyText :_("类型"),
        displayField:'name',
        valueField:'value',
        width: 220,
        allowBlank: false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'types',
        id:'types',
        mode:'local',
        listeners:{
            select:function(combo,rec,index){
                showStorageFields(rec.get('value'),storage_def_form);
            }
        }
    });

    var storage_store=new Ext.data.JsonStore({
        url: '/storage/get_storage_def_list?' + sSiteId + op_level + sGroupId,
        root: 'rows',
        fields: ['id', 'name', 'type','size', 'definition', 'description','stats','connection_props','scope'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load:function(store,recs,opts){
                 if(recs.length>0){
                    names.setValue(recs[0].get('id'));
                    names.fireEvent('select',names,recs[0],0);
                    storage_id=recs[0].get('id');
                    storage_name=recs[0].get('name');
                    storage_type=recs[0].get('type');
                    types.getEl().allowBlank=true;
                    name.getEl().allowBlank=true;
                    names.selectedIndex=0;
                 }

            }
        }
    });

    //While testing storage, we are showing this show all checkbox. This is only while selecting storage for VM 
    //when mode is SELECT.
    var chkShowAvailable = new Ext.form.Checkbox({
        boxLabel:_('仅显示可用的磁盘'),
        width:200,
        height:30,
        checked:true,
        hidden: hideShowAllCheckbox,
        listeners:{
            check:function(field,checked){
                if(checked==true){
                    show_available_storages=true;
                }else{
                    show_available_storages=false;
                }
                test_button_click();
            }
        }
    });

    var pnlShowAvailable=new Ext.Panel({
        layout:'table',
        labelWidth:80,
        header:false,
        layoutConfig: {
            columns: 1
        },
        items :[chkShowAvailable]
    });

    if(mode=="SELECT")
        storage_store.load();
    var names=new Ext.form.ComboBox({
        fieldLabel: _('名称'),
        triggerAction:'all',
        store: storage_store,
        displayField:'name',
        valueField:'id',
        width: 200,
        allowBlank: false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        id:'names',
        mode:'local',
        listeners:{
            select:function(combo,rec,index){
                //hide the grid and label on selection of storage.
                resultGrid.setVisible(false);
                storage_def_form.findById("resultLbl").setVisible(false);

                showStorageFields(rec.get('type'),storage_def_form);
                storage_id=rec.get('id');
                storage_name=rec.get('name');
                storage_type=rec.get('type');

                description.setValue(rec.get('description'));

                var elements=type_elements_map[storage_type].split(',');
                var props=type_props_map[storage_type].split(',');
                for(var i=0;i<elements.length;i++){
                    var element=storage_def_form.findById(elements[i]);
                    element.setValue(eval('rec.get("connection_props").'+props[i]));
                    if(type_reqd_elements_map[storage_type].split(',').indexOf(elements[i])>-1)
                        element.allowBlank=false;
//                        element.setDisabled(mode=='TEST');
                }
                test_button_click();
            }
        }
    });

    var name=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'name',
        id: 'name',
        width: 200,
        allowBlank:false
    });
    var description=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'description',
        width: 200,
        id: 'description'
    });
    var portal=new Ext.form.TextField({
        fieldLabel: _('ISCSI服务器IP'),
        name: 'portal',
        width: 200,
        id: 'portal'
    });
    var target=new Ext.form.TextField({
        fieldLabel: _('唯一标识符'),
        name: 'target',
        id: 'target',
        width: 200
    });
    var server=new Ext.form.TextField({
        fieldLabel: _('服务器'),
        name: 'server',
        width: 200,
        id: 'server'
    });
    var share=new Ext.form.TextField({
        fieldLabel: _('共享'),
        name: 'share',
        width: 200,
        id: 'share'
    });
    var username=new Ext.form.TextField({
        fieldLabel: _('用户名'),
        name: 'username',
        width: 200,
        id: 'username'
    });
    var password=new Ext.form.TextField({
        fieldLabel: _('密码'),
        name: 'password',
        id: 'password',
        width: 200,
        inputType : 'password'
    });
    var options=new Ext.form.TextField({
        fieldLabel: _('选项'),
        name: 'options',
        width: 200,
        id: 'options'
    });
    var nw_interface=new Ext.form.TextField({
        fieldLabel: _('网络接口'),
        name: 'interface',
        width: 200,
        id: 'interface'
    });
    var mnt_point=new Ext.form.TextField({
        fieldLabel: _('挂载点'),
        name: 'mount_point',
        width: 200,
        id: 'mount_point'
    });
    var mnt_options=new Ext.form.TextField({
        fieldLabel: _('挂载选项'),
        name: 'mount_options',
        width: 200,
        id: 'mount_options'
    });
    var volume_group=new Ext.form.TextField({
        fieldLabel: _('卷组'),
        name: 'volume_group',
        width: 200,
        id: 'volume_group'
    });
    var windows_share=new Ext.form.TextField({
        fieldLabel: _('Windows共享 (WS)'),
        name: 'windows_share',
        width: 200,
        id: 'windows_share'
    });
    var windows_username=new Ext.form.TextField({
        fieldLabel: _('WS用户名'),
        name: 'windows_username',
        width: 200,
        id: 'windows_username'
    });
    var windows_password=new Ext.form.TextField({
        fieldLabel: _('WS密码'),
        name: 'windows_password',
        id: 'windows_password',
        width: 200,
        inputType : 'password'
    });
    var domain=new Ext.form.TextField({
        fieldLabel: _('域名'),
        name: 'domain',
        width: 200,
        id: 'domain'
    });
    var device=new Ext.form.TextField({
        fieldLabel: _('设备'),
        name: 'device',
        width: 200,
        id: 'device'
    });
    var host_adapter=new Ext.form.TextField({
        fieldLabel: _('Host Adapter'),
        name: 'host_adapter',
        width: 200,
        id: 'host_adapter'
    });
    var bus_channel=new Ext.form.TextField({
        fieldLabel: _('Bus/ Channel'),
        name: 'bus_channel',
        width: 200,
        id: 'bus_channel'
    });
    var lun=new Ext.form.TextField({
        //fieldLabel: _('Lun'),
        name: 'lun',
        width: 200,
        id: 'lun',
        hidden: true
    });

    var node_store = new Ext.data.JsonStore({
        url: '/node/get_managed_nodes?' + sSiteId + sGroupId,
        root: 'rows',
        fields: ['hostname', 'id', 'group'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load:function(store,recs,opts){
                if(recs.length>0 && mode!="SELECT")
                    mgd_nodes.setValue(recs[0].get('id'));
                else
                    mgd_nodes.setValue(host);
            }
        }
    });

    node_store.load();

    var mgd_nodes=new Ext.form.ComboBox({
        fieldLabel: _('管理服务器'),
        triggerAction:'all',
        store: node_store,
        displayField:'hostname',
        valueField:'id',
        width: 200,
        allowBlank: true,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'mgd_nodes',
        id:'mgd_nodes',
        mode:'local'
    });

    var lbl=new Ext.form.Label({
        text:_('管理服务器'),
        hidden: hideManagedServerText
    });
    var test_button=new Ext.Button({
        name: 'test',
        id: 'test',
        text:_(test_button_caption),
        listeners: {
            click: function(btn) {
                test_button_click();
            }
        }
    });

    function test_button_click() {
        if(mgd_nodes.getValue() != "" && mgd_nodes.getValue() != null){
            var type;
            if(mode=="SELECT"){
                type=storage_type;
            }else{
                type=types.getValue();
            }
            if(mode == "NEW") {
                // process test functionality here...
                var url="/storage/storage_def_test?" + sSiteId + op_level + sGroupId + "&storage_id="+storage_id+
                    "&type="+type+"&node_id="+mgd_nodes.getValue()+"&mode="+mode+"&total_cap="+total_cap;

                testStorageDef(url,mode,mgd_nodes.getValue(),mgd_nodes.getRawValue(),type,result_fldset,resultGrid);
            }else{
                // process test functionality here...
                var url="/storage/storage_def_test?" + sSiteId + sGroupId + "&storage_id="+storage_id+
                    "&type="+type+"&node_id="+mgd_nodes.getValue()+"&mode="+mode+"&total_cap="+total_cap +"&show_available=" + show_available_storages + "&vm_config_action=" + vm_config_action + "&disk_option=" + diskOption;

                testStorageDef(url,mode,mgd_nodes.getValue(),mgd_nodes.getRawValue(),type,result_fldset,resultGrid);
            }
        }else{
            Ext.Msg.alert(_("警告"),_("请选择一个管理服务器."));
        }
    }

    var pnl=new Ext.Panel({
        layout:'table',
        labelWidth:80,
        header:false,
//        style: 'margin: -2px 0px -0px 0px',
        layoutConfig: {
            columns: 3
        },
        items :[lbl,mgd_nodes,test_button]
    });

//    var lbl1=new Ext.form.Label({
//        text:'Select a Server to validate the Storage Connectivity.'
//    });

    var resultLbl=new Ext.form.Label({
        html:'<img src="../icons/accept.png" /> &nbsp;Result',
        hidden:true,
        id:"resultLbl"
    });

    var test_fldset=new Ext.form.FieldSet({
        title: _(manageServerTitle),    //'Validate / Select Storage'
        collapsible: false,
        labelAlign:"left" ,
        autoHeight:true,
//        width: 400,
//        height:80,
        items:[pnlShowAvailable,pnl,resultLbl]
    });

    var resultGrid = new Ext.grid.GridPanel({
        store: new Ext.data.SimpleStore({
            fields:iscsi_fields
        }),
        colModel:iscsi_colModel,
        stripeRows: true,
        frame:false,
        title: _('发现存储'),
        border:false,
        width:400,
        height:136,//185
        hidden:true,
        autoScroll:true
        //autoExpandColumn:1,
    });

    var result_fldset=new Ext.form.FieldSet({
        title: _('发现存储'),
        collapsible: false,
        autoHeight:true,
        border:false,
        width: 410,
        hidden:true,
        items:[resultGrid]

    });

    //Start-Added for getting from existing definitions
    var from_dc_radio=new Ext.form.Label({
        html: "<div><font style: size='2'>从存储资源中选择</font></div>",
        id:'from_dc'
    });

    var dc_radio_panel=new Ext.Panel({
        id:"dc_radio_panel_id",
        width:408,
        height:35,
        frame:true,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[from_dc_radio]
    });

    var dc_columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), hidden: true, dataIndex: 'id'},
        {header: _("名称"), width: 80, sortable: false, dataIndex: 'name'},
        {header: _("类型"), width: 60, sortable: false, dataIndex: 'type'},
        {header: _("大小(GB)"), width: 60, sortable: false, dataIndex: 'size'},
        {header: _("定义"), hidden: true, sortable: false, dataIndex: 'definition'},
        {header: _("说明"), width: 200, sortable: false, dataIndex: 'description'},
        {header: _("状态"), hidden: true, sortable: false, dataIndex: 'status'},
        {header: _("范围"), hidden: true, sortable: false, dataIndex: 'scope'}
        ]);

    var dc_store = new Ext.data.JsonStore({
        url: '/storage/get_dc_storage_def_list?' + sSiteId + sGroupId,
        root: 'rows',
        fields: ['id', 'name', 'type','size', 'definition', 'description','stats','connection_props','status', 'scope'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });

    dc_store.load();

    var dc_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:false
    });

    storage_dc_grid = new Ext.grid.GridPanel({
        store: dc_store,
        colModel:dc_columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:dc_selmodel,
        width:408,
        autoExpandColumn:2,
        height:400,
        enableHdMenu:false,
        tbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'btnAssociate',
                id: 'btnAssociate',
                text:"附加",    //Associate
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        //var storageId = storage_dc_grid.getSelectionModel().getSelected().get('id');
                        var def_ids = "";
                        var sm = storage_dc_grid.getSelectionModel();
                        var rows = sm.getSelections();
                        for(i=0; i<rows.length; i++) {
                            if(i == rows.length-1) {
                                def_ids += rows[i].get('id');
                            } else {
                                def_ids += rows[i].get('id') + ',';
                            }
                        }
                        associate_defns("STORAGE",def_ids);
                    }
                }
            }),
            '-',
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('关闭'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        if(mode!="SELECT"){
                            storage_grid.enable();
                            closeWindow(windowid);
                        }else{
                            closeStorageDefinition();
                        }
                    }
                }
            })
        ]
    });

    existing_def_form = new Ext.FormPanel({
        labelWidth:120,
        frame:true,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        labelAlign:"left" ,
        width:421,
        height:450,
        labelSeparator: ' ',

        items:[dc_radio_panel,storage_dc_grid]
        });
    //End-Added for getting from existing definitions

    var nw_def_save_button = new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:((mode=='SELECT')?_("确定"):_("保存")),
        hidden:(mode=='TEST'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(mode=="TEST"){
                    closeWindow(windowid);
                    return;
                }

                if (storage_def_form.getForm().isValid()) {
                    if(mode=="SELECT"){
                        if (vm_config_action != "provision_vm" && vm_config_action != "provision_image" && vm_config_action != "change_vm_settings") {
                            if(resultGrid.isVisible()==false) {
                                Ext.Msg.alert(_("失败"), _("请选择存储设备."));
                                return;
                            }
                        }
                    //alert(storage_store.getAt(names.selectedIndex).get('connection_props').mount_point);
                    //alert(storage_store.getAt(names.selectedIndex).get(''));
                    var storage_disk_id=null, storage_allocated=false, vm_name=null, state=null;
                    var interface=null, disk=null, size=0, name=null;
                    var disk_context=new Object();
                    if(resultGrid.isVisible()==true) {
                        var sel_result_rec = resultGrid.getSelectionModel().getSelected();
                        if (sel_result_rec != null) {
                            storage_disk_id = sel_result_rec.get('storage_disk_id');
                            storage_allocated = sel_result_rec.get('storage_allocated');
                            unique_path = sel_result_rec.get('uniquepath');
                            if (storage_allocated == "Yes") {
                                storage_allocated = true;
                            } else {
                                storage_allocated = false;
                            }
                            vm_name = sel_result_rec.get('vm_name');
                        }
                    }
                    if (storage_type == "nfs" || storage_type == "cifs" || storage_type == "gfs" || storage_type == "ocfs"){
                        // special processing for NFS
                        disk_context.storage_name = storage_name;
                        disk_context.storage_id = storage_id;
                        disk_context.vm_name = vm_name;
                        disk_context.storage_allocated = storage_allocated;
                        disk_context.id = storage_disk_id;
                        disk_context.type = storage_type;
                        disk_context.name = storage_store.getAt(names.selectedIndex).get('connection_props').mount_point;
                        if(unique_path == null || unique_path == "") {
                            disk_context.disk = disk_context.name;
                        } else {
                            disk_context.disk = unique_path;
                        }
                        disk_context.size = "";
                        disk_context.interface = "";
                        disk_context.status = "";
                        disk_context.volume_group = null;
                    }else {
                            if(resultGrid.isVisible()==true) {
                                var selected_rec = resultGrid.getSelectionModel().getSelected();
                                unique_path = selected_rec.get('uniquepath');
                                state = selected_rec.get('state');
                                interface = selected_rec.get('interface');
                                disk = selected_rec.get('disk');
                                size = selected_rec.get('size(gb)');
                                name = selected_rec.get('name');
                            }
                                disk_context.storage_name = storage_name;
                                disk_context.storage_id = storage_id;
                                disk_context.vm_name = vm_name;
                                disk_context.storage_allocated = storage_allocated;
                                disk_context.id = storage_disk_id;
                                disk_context.type = storage_type;
                                disk_context.name = name;
                                disk_context.size = size;
                                disk_context.volume_group = sVolumeGroup;

                                if(disk == undefined) {
                                    if(unique_path == null || unique_path == "") {
                                        disk_context.disk = disk_context.name;
                                    } else {
                                        disk_context.disk = unique_path;
                                    }
                                } else {
                                    disk_context.disk =  disk;
                                }
                                
                                if (storage_type == "iscsi" || storage_type == "fc")
                                    disk_context.interface =  unique_path;
                                else if(storage_type == "aoe")
                                    disk_context.interface =  interface
                                disk_context.status =  state;
                        }
                        var result = set_disklocation(storage_type,disk_context,vm_config_action,disk_mode,change_seting_mode);
                        if(result==true) {
                            unique_path=null;
                            closeStorageDefinition();
                        }
                    }else{
                        //server pool
                        if(sGroupId != "" && sNodeId == "") {
                            if(storage_scope == 'DC') {
                                Ext.MessageBox.alert("信息", "这里不能编辑数据中心级存储");
                                return
                            }
                        }
                        var sp_ids = get_selected_sp_list();

                        var url='/storage/add_storage_def?' + sSiteId + op_level + sGroupId + sNodeId +
                            '&type='+types.getValue()+'&total_cap='+total_cap + '&sp_ids=' + sp_ids;
                        var msg=_('正在添加存储...');
                        var msg1 = _("任务已经提交.");
                        if(mode=='EDIT'){
                            url='/storage/edit_storage_def?' + sSiteId + op_level + sGroupId +
                                '&type='+types.getValue()+'&storage_id='+storage_id+'&total_cap='+total_cap + '&sp_ids=' + sp_ids;
                            msg=_('正在更新存储...');
                            msg1 = _("存储更新成功.");
                        }
                        storage_def_form.getForm().submit({
                            url:url,
                            success: function(form,action) {
                                //closeStorageDefinition();
                                DelayReloadStorageDefList();
                                Ext.MessageBox.alert("成功", msg1);
                                //reloadStorageDefList();
                                closeWindow(windowid);
                                storage_grid.enable();
                                //Ext.MessageBox.alert("Success",action.result.msg);
                            },
                            failure: function(form, action) {
                                Ext.Msg.alert(_("Failure"),action.result.msg );
                            },

                            waitMsg:msg
                        });
                    }
                }else{
                    Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
                }

            }
        }
    });

    var nw_def_cancel_button = new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:((mode=='TEST')?_("关闭"):_("取消")),  //_('Cancel'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(mode != "SELECT") {
                    storage_grid.enable();
                    closeWindow(windowid);
                }else{
                    closeStorageDefinition();
                }
            }
        }
    });

    function RemoveScanResult(){
        var url="/storage/RemoveScanResult"; 
        var ajaxReq=ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                    //Ext.MessageBox.alert("Success",response.msg);
                }else{
                    Ext.MessageBox.alert("Failure",response.msg);
                }
            },
            failure: function(xhr){
                Ext.MessageBox.alert( "Failure " , xhr.statusText);
            }
        });
    }

    function SaveScanResult(){
        var url="/storage/SaveScanResult?storage_id=" + storage_id; 
        var ajaxReq=ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                    //Ext.MessageBox.alert("Success",response.msg);
                }else{
                    Ext.MessageBox.alert("Failure",response.msg);
                }
            },
            failure: function(xhr){
                Ext.MessageBox.alert( "Failure " , xhr.statusText);
            }
        });
    }

    function get_selected_sp_list() {
        var def_ids = "";
        var row_count = sp_list_store.getCount();
        for(i=0; i<row_count; i++) {
            var rec = sp_list_store.getAt(i);
            if(rec.get('associated') == true) {
                if(i == row_count-1) {
                    def_ids += rec.get('id');
                } else {
                    def_ids += rec.get('id') + ',';
                }
            }
        }
        //remove last "," if there is.
        if(def_ids.substring(def_ids.length-1) == ",") {
            def_ids = def_ids.substring(0, def_ids.length-1);
        }
        return def_ids;
    }

    if(node.attributes.nodetype == 'DATA_CENTER'){
        if(mode == "NEW" || mode == "EDIT") {
            get_storage_def_form_for_new_edit();
        } else {
            get_main_storage_def_form();
        }
    } else {
        get_main_storage_def_form();
    }

    function get_storage_def_form_for_new_edit() {
        storage_def_form = new Ext.FormPanel({
            title: _(nw_def_title),
            labelWidth:120,
            frame:true,
            border:0,
            bodyStyle:'padding:0px 0px 0px 0px',
            labelAlign:"left" ,
            width:418,
            height:470,
            labelSeparator: ' ',
            items:[types,name,names,description,portal,host_adapter,bus_channel,target,lun,username,password,options,
                    nw_interface,server,share,windows_share,device,mnt_point,mnt_options,volume_group,
                    windows_username,windows_password,domain,test_fldset,resultGrid]
        });
        return storage_def_form;
    }

    function get_main_storage_def_form() {
        storage_def_form = new Ext.FormPanel({
            title: _(nw_def_title),
            labelWidth:120,
            frame:true,
            border:0,
            bodyStyle:'padding:0px 0px 0px 0px',
            labelAlign:"left" ,
            width:418,
            height:470,
            labelSeparator: ' ',
    
            items:[types,name,names,description,portal,host_adapter,bus_channel,target,lun,username,password,options,
                    nw_interface,server,share,windows_share,device,mnt_point,mnt_options,volume_group,
                    windows_username,windows_password,domain,test_fldset,resultGrid],
            bbar:[{xtype: 'tbfill'},
                nw_def_save_button,
                '-',
                nw_def_cancel_button
            ]
        });
        return storage_def_form;
    }

    //Start - Associate definition from DC level
    function showSPCheckBox(value,params,record){
        var id = Ext.id();
        (function(){
            new Ext.form.Checkbox({
                renderTo: id,
                checked:value,
                width:100,
                height:16,
                id:"chkSP",
                listeners:{
                    check:function(field,checked){
                        if(checked==true){
                            record.set('associated',true);
                        }else{
                            record.set('associated',false);
                        }
                    }
                }
            });
        }).defer(20)
        return '<span id="' + id + '"></span>';
    }

    var sp_list_columnModel = new Ext.grid.ColumnModel([
        {header: "Id", hidden: true, dataIndex: 'id'},
        {header: "", width: 25, sortable: false, renderer: showSPCheckBox, dataIndex: 'associated'},
        {header: "服务器池", width: 300, sortable:true, defaultSortable:true, dataIndex: 'serverpool'}
    ]);
    var sp_list_store = new Ext.data.JsonStore({
        url: '/storage/get_sp_list?' + sSiteId + sSelectedDefId,
        root: 'rows',
        fields: ['id', {name: 'associated', type: 'boolean'}, 'serverpool'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e) {
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    sp_list_store.setDefaultSort('serverpool');
    sp_list_store.load();

    var sp_list_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:false
    });

    sp_list_grid = new Ext.grid.GridPanel({
        store: sp_list_store,
        colModel:sp_list_columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:sp_list_selmodel,
        width:408,
        height:400,
        autoExpandColumn:2,
        enableHdMenu:false
    });

    var tabs = new Ext.TabPanel({
        width:418,
        height:470,
        activeTab: 0,
        frame:true,
        bbar:[{xtype: 'tbfill'},
            nw_def_save_button,
            '-',
            nw_def_cancel_button
        ]
    });

    var serverpoolPanel=new Ext.Panel({
        title   : _('服务器池'),
        closable: false,
        layout  : 'fit',
        id:'server_pool',
        autoScroll:true,
        defaults: {
            autoScroll:true
        },
        items:[sp_list_grid],
        listeners:{
            activate:function(panel){
                if(panel.rendered){
                    panel.doLayout();
                }
            }
        }
    });
    //End - Associate definition from DC level

    if(mode=="TEST"){
        names.setVisible(false);

        storage_id=storage.get('id');

        var type=storage.get('type');
        types.setValue(type);
        types.setDisabled(true);

        name.setValue(storage.get('name'));
        description.setValue(storage.get('description'));
        name.setDisabled(mode=='TEST');
        description.setDisabled(mode=='TEST');

        var elements=type_elements_map[type].split(',');
        var props=type_props_map[type].split(',');
        for(var i=0;i<elements.length;i++){
            var element=storage_def_form.findById(elements[i]);
            element.setValue(eval('storage.get("connection_props").'+props[i]));
            if(type_reqd_elements_map[type].split(',').indexOf(elements[i])>-1)
                element.allowBlank=false;
                element.setDisabled(mode=='TEST');
        }

    }else if(mode=="EDIT"){
        names.setVisible(false);

        storage_id=storage.get('id');

        var type=storage.get('type');
        types.setValue(type);
        types.setDisabled(true);

        name.setValue(storage.get('name'));
        description.setValue(storage.get('description'));

        var elements=type_elements_map[type].split(',');
        var props=type_props_map[type].split(',');
        for(var i=0;i<elements.length;i++){
            var element=storage_def_form.findById(elements[i]);
            element.setValue(eval('storage.get("connection_props").'+props[i]));
            if(type_reqd_elements_map[type].split(',').indexOf(elements[i])>-1)
                element.allowBlank=false;
                element.setDisabled(true);
        }

        //server pool level
        if(sGroupId != "" && sNodeId == "") {
            if(storage_scope == "DC") {
                name.disable();
                description.disable();
            } else {
                name.enable();
                description.enable();
            }
        }

    }else if(mode=="NEW"){
        names.setVisible(false);
    }else if(mode=="SELECT"){
        mgd_nodes.setValue(host);
        mgd_nodes.disable();
        names.selectedIndex=0;
        test_button.setText("SELECT");
        description.disable();
        server.disable();
        portal.disable();
        target.disable();
        username.disable();
        password.disable();
        share.disable();
        mnt_point.disable();
        mnt_options.disable();
        server.disable();
        nw_interface.disable();
        windows_share.disable();
        windows_username.disable();
        windows_password.disable();
        domain.disable();
        
        mgd_nodes.hidden=true;
        test_button.hidden=true;
    }

    var return_form;
    if(node.attributes.nodetype == 'DATA_CENTER'){
        return_form = storage_def_form;
        if(mode == "NEW" || mode == "EDIT") {
            addDefTabs(tabs,[storage_def_form, serverpoolPanel]);
            return_form = tabs;
        }
    }
    else if(node.attributes.nodetype == 'SERVER_POOL'){
        return_form = existing_def_form;
        if(mode=="TEST") {
            return_form = storage_def_form;
        }
    }
    else if(node.attributes.nodetype == 'MANAGED_NODE'){
        return_form = storage_def_form;
    }
    else if(node.attributes.nodetype == 'DOMAIN'){
        return_form = storage_def_form;
    }

    return return_form;
}

function addDefTabs(prntPanel,childpanels){
    if(prntPanel.items){
        prntPanel.isRemoving=true;
        prntPanel.removeAll(true);
    }
    prntPanel.isRemoving=false;
    for(var i=0;i<childpanels.length;i++){
        prntPanel.add(childpanels[i]);
    }
    if(childpanels.length>0){
        prntPanel.setActiveTab(childpanels[0]);
    }
}

function hidefields(mode)
{

    if (mode=="SELECT"){
        Ext.get('types').setVisible(false);
        Ext.get('types').up('.x-form-item').setDisplayed(false);
        Ext.get('name').setVisible(false);
        Ext.get('name').up('.x-form-item').setDisplayed(false);
        storage_def_form.findById('types').allowBlank=true;
        storage_def_form.findById('name').allowBlank=true;
    }else{
        Ext.get('names').setVisible(false);
        Ext.get('names').up('.x-form-item').setDisplayed(false);
        storage_def_form.findById('names').allowBlank=true;

    }
//    types.getEl().allowBlank=true;
//    name.getEl().allowBlank=true;
}

function showStorageFields(type){

    for(var i=0;i<elements.length;i++){
        Ext.get(elements[i]).setVisible(false);
        Ext.get(elements[i]).up('.x-form-item').setDisplayed(false);
        storage_def_form.findById(elements[i]).allowBlank=true;
    }

    var new_elements=type_elements_map[type].split(',');
    for(i=0;i<new_elements.length;i++){
        Ext.get(new_elements[i]).setVisible(true);
        Ext.get(new_elements[i]).up('.x-form-item').setDisplayed(true);

        if(type_reqd_elements_map[type].split(',').indexOf(new_elements[i])>-1)
            storage_def_form.findById(new_elements[i]).allowBlank=false;
    }

}

function testStorageDef(url,mode,node,nodename,type,result_fldset,resultGrid){
//    alert(storage_def_form.getForm().get
    if (storage_def_form.getForm().isValid()) {
        var msg="";
        if(mode=="SELECT"){
            msg=_('正在加载存储...');
        } else {
            msg=_('正在测试存储...');
        }

        storage_def_form.getForm().submit({
            url:url,
            success: function(form,action) {
                processOutput(action.result,type,result_fldset,resultGrid);
                reloadStorageDefList();
            },
            failure: function(form, action) {
                if(action.result.error=='没有验证'){
                        var cred_form=credentialsForm();
                        cred_form.addButton(_("确定"),function(){
                            if (cred_form.getForm().isValid()) {
                                var uname=cred_form.find('name','user_name')[0].getValue();
                                var pwd=cred_form.find('name','pwd')[0].getValue();
                                if(mode=="TEST"){
                                    url+="&username="+uname;
                                    url+="&password="+pwd;
                                }else{
                                    storage_def_form.findById('username').setValue(uname);
                                    storage_def_form.findById('password').setValue(pwd);
                                }
                                cred_window.close();
                                testStorageDef(url,mode,node,nodename,type,result_fldset,resultGrid);
                            }else{
                                Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
                            }
                        });
                        cred_form.addButton(_("取消"),function(){
                            cred_window.close();
                            Ext.MessageBox.alert(_('E错误'), format(_('服务器 {0}未验证.'),nodename));
                        });

                        var cred_window=new Ext.Window({
                            title:_("认证 ")+nodename,width : 280,height: 150,modal : true,resizable : false
                            ,items:cred_form
                        });

                        cred_window.show();
                }else{
                    //Ext.MessageBox.alert('Error', action.result.msg);
                    storage_def_form.findById("resultLbl").setVisible(true);
                    var text="<img src='../icons/cancel.png'/> &nbsp;<b>Failure:</b>&nbsp;&nbsp;"+action.result.msg;
                    storage_def_form.findById("resultLbl").setText(text,false);
                    resultGrid.setVisible(false);
                }
            },

            waitMsg:msg
        });
    }else{
        Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
    }
}

function processOutput(details,type,result_fldset,resultGrid){
    if(details.STORAGE_DETAILS != null) {
        sVolumeGroup = details.STORAGE_DETAILS[0].VOLUME_GROUP;
    }
    if (details.DETAILS == null) {
        resultGrid.setVisible(false);
        storage_def_form.findById("resultLbl").setVisible(false);
        return;
    }
    var text="<img src='../icons/accept.png'/> &nbsp;<b>成功:</b>&nbsp;&nbsp;"+_("总共大小")+":&nbsp;"+details.SUMMARY.TOTAL+" GB";

    var dataObj=new Array(),fields=new Array(),columnModel=new Array();
    if (type=='iscsi'){
        fields=iscsi_fields;
        columnModel=iscsi_colModel;
        dataObj=process_iscsi_output(details);
    }else if (type=='fc'){
        fields=fc_fields;
        columnModel=fc_colModel;
        dataObj=process_fc_output(details);
    }else if(type=='nfs' || type=='cifs' || type=='gfs' || type=='ocfs'){
        var available=details.STORAGE_DETAILS[0].AVAILABLE;
        unique_path=details.STORAGE_DETAILS[0].uuid;

        text+=",&nbsp;"+_("可用大小")+":&nbsp;"+available+" GB";
        fields=nfs_fields;
        columnModel=nfs_colModel;
        dataObj=process_nfs_output(details);
    }else if(type=='aoe'){
        fields=aoe_fields;
        columnModel=aoe_colModel;
        dataObj=process_aoe_output(details);
    }else if(type=='lvm'){
        fields=lvm_fields;
        columnModel=lvm_colModel;
        dataObj=process_lvm_output(details);
    }

    var store = new Ext.data.SimpleStore({
        fields:fields
    });
    if (type=='iscsi' || type=='fc'){
        store.setDefaultSort('lun');
    }
    store.loadData(dataObj);

    storage_def_form.findById("resultLbl").setVisible(true);
    storage_def_form.findById("resultLbl").setText(text,false);

    if (vmConfigAction=="provision_vm" || vmConfigAction=="provision_image" || vmConfigAction=="change_vm_settings" ) {
        if(diskOption == "CREATE_DISK") {
            resultGrid.setVisible(false);
        } else {
            resultGrid.setVisible(true);
        }
    } else {
        resultGrid.setVisible(true);
    }
    resultGrid.reconfigure(store,columnModel);

    if(details.SUMMARY!=null && details.SUMMARY.TOTAL!=null)
        total_cap=details.SUMMARY.TOTAL;
}

function process_fc_output(details,test){

    var test_data =
    {
        'DETAILS': [{
            'CurrentPortal': ' 192.168.12.104:3260,1',
            'Lun': 'Test 1',
            'State': 'running',
            'Target': 'shared_104:store',
            'mount_point': '/dev/sde',
            'SIZE': ' 3142 MB',
            'uuid': 'df150e55-3e28-4e93-8d9a-e6acfa7fe52c',
            'STORAGE_DISK_ID': '',
            'STORAGE_ALLOCATED': '',
            'VM_NAME': ''
        },

        {
            'CurrentPortal': ' 192.168.12.104:3260,1',
            'Lun': 'Test 2',
            'State': 'running',
            'Target': 'shared_104:store',
            'mount_point': '/dev/sdf',
            'SIZE': ' 3142 MB',
            'uuid': '/dev/disk/by-uuid/b472fcb4-f4fe-44f8-837f-333ad9244171',
            'STORAGE_DISK_ID': '',
            'STORAGE_ALLOCATED': '',
            'VM_NAME': ''
        }],
        'id': '5b76f1d1-fb55-683b-e0e2-dd04b8d13212',
        'name': 't',
        'op': 'GET_DISKS',
        'type': 'iscsi'
    };

    if(test)
        details = test_data;

    var data_arr=new Array(),j=0;
    if (details.DETAILS!=null){
        for(var i=0;i<details.DETAILS.length;i++){
            var item=details.DETAILS[i];
            if (item.Lun == null)
                continue

            data_arr[j]=new Array();
            data_arr[j][0]="Lun " + item.Lun;
            if(item.USED > 0) {
                data_arr[j][1]=item.USED;
            } else if(item.SIZE > 0) {
                data_arr[j][1]=item.SIZE;
            } else {
                data_arr[j][1]=0;
            }
            if(item.MOUNT != null) {
                data_arr[j][2]=item.MOUNT;
            } else {
                data_arr[j][2]=item.mount_point;
            }
            data_arr[j][3]=item.State;
            data_arr[j][4]=item.uuid;
            data_arr[j][5]=item.STORAGE_DISK_ID;
            data_arr[j][6]=item.STORAGE_ALLOCATED;
            data_arr[j][7]=item.VM_NAME;
            data_arr[j][8]=parseInt(item.Lun);
            j++;
        }
    }
    return data_arr
}

function process_iscsi_output(details,test){

    var test_data =
    {
        'DETAILS': [{
            'CurrentPortal': ' 192.168.12.104:3260,1',
            'Lun': 'Test 1',
            'State': 'running',
            'Target': 'shared_104:store',
            'mount_point': '/dev/sde',
            'SIZE': ' 3142 MB',
            'uuid': 'df150e55-3e28-4e93-8d9a-e6acfa7fe52c',
            'STORAGE_DISK_ID': '',
            'STORAGE_ALLOCATED': '',
            'VM_NAME': ''
        },

        {
            'CurrentPortal': ' 192.168.12.104:3260,1',
            'Lun': 'Test 2',
            'State': 'running',
            'Target': 'shared_104:store',
            'mount_point': '/dev/sdf',
            'SIZE': ' 3142 MB',
            'uuid': '/dev/disk/by-uuid/b472fcb4-f4fe-44f8-837f-333ad9244171',
            'STORAGE_DISK_ID': '',
            'STORAGE_ALLOCATED': '',
            'VM_NAME': ''
        }],
        'id': '5b76f1d1-fb55-683b-e0e2-dd04b8d13212',
        'name': 't',
        'op': 'GET_DISKS',
        'type': 'iscsi'
    };

    if(test)
        details = test_data;

    var data_arr=new Array(),j=0;
    if (details.DETAILS!=null){
        for(var i=0;i<details.DETAILS.length;i++){
            var item=details.DETAILS[i];
            if (item.Lun == null)
                continue

            data_arr[j]=new Array();
            data_arr[j][0]="Lun " + item.Lun;
            if(item.USED > 0) {
                data_arr[j][1]=item.USED;
            } else if(item.SIZE > 0) {
                data_arr[j][1]=item.SIZE;
            } else {
                data_arr[j][1]=0;
            }
            /*
            if(item.MOUNT != null) {
                data_arr[j][2]=item.MOUNT;
            } else {
                data_arr[j][2]=item.mount_point
            }
            */
            data_arr[j][2]=item.DISKS;
            data_arr[j][3]=item.State;
            data_arr[j][4]=item.uuid;
            data_arr[j][5]=item.STORAGE_DISK_ID;
            data_arr[j][6]=item.STORAGE_ALLOCATED;
            data_arr[j][7]=item.VM_NAME;
            data_arr[j][8]=parseInt(item.Lun);
            j++;
        }
    }
    return data_arr
}

function process_nfs_output(details,test){
    var test_data =
    {
        'DETAILS': [{
            'AVAILABLE': '8.7G',
            'MOUNT': '/mnt/vm_data',
            'USED': '38G',
            'FILESYSTEM': '192.168.12.104:/mnt/Test',
            'uuid': '',
            'STORAGE_ALLOCATED': '',
            'STORAGE_DISK_ID': '',
            'VM_NAME': '',
            'DISKS': ''
        }]
    }

    if (test)
        details = test_data

    var data_arr=new Array();
    var mount_point, file_system;
    if (details.STORAGE_DETAILS!=null){
        mount_point=details.STORAGE_DETAILS[0].MOUNT;
        file_system=details.STORAGE_DETAILS[0].FILESYSTEM;
    }
    if (details.DETAILS!=null){
        for(var i=0;i<details.DETAILS.length;i++){
            var item=details.DETAILS[i];
            data_arr[i]=new Array();
            data_arr[i][0]=mount_point;
            data_arr[i][1]=item.SIZE;
            data_arr[i][2]=file_system;
            data_arr[i][3]=item.uuid;
            data_arr[i][4]=item.STORAGE_ALLOCATED;
            data_arr[i][5]=item.STORAGE_DISK_ID;
            data_arr[i][6]=item.VM_NAME;
            data_arr[i][7]=item.DISKS;
        }
    }
    return data_arr
}

function process_aoe_output(details,test){
    var test_data = {
        'DETAILS': [{
            'DEVICENAME': 'test5.0',
            'INTERFACENAME': 'eth0',
            'SIZE': '4.405GB',
            'STATUS': 'up',
            'STORAGE_DISK_ID': '',
            'STORAGE_ALLOCATED': '',
            'VM_NAME': ''
        },

        {
            'DEVICENAME': 'test5.0',
            'INTERFACENAME': 'eth0',
            'SIZE': '9.405GB',
            'STATUS': 'up',
            'STORAGE_DISK_ID': '',
            'STORAGE_ALLOCATED': '',
            'VM_NAME': ''
        }],
        'id': 'e5631f9d-47f3-f597-2f39-38d3ba605d84',
        'name': 'AOE Test',
        'op': 'GET_DISKS',
        'type': 'aoe'
    }

    if (test)
        details = test_data
    var data_arr=new Array();
    if (details.DETAILS!=null){
        for(var i=0;i<details.DETAILS.length;i++){
            var item=details.DETAILS[i];
            data_arr[i]=new Array();
            data_arr[i][0]=item.uuid;   //item.DEVICENAME;
            data_arr[i][1]=item.SIZE;
            data_arr[i][2]=item.uuid;  //"/dev/etherd/"+ item.DEVICENAME;
            data_arr[i][3]=item.State;  //item.STATUS;
            data_arr[i][4]=item.INTERFACENAME;
            data_arr[i][5]=item.STORAGE_DISK_ID;
            data_arr[i][6]=item.STORAGE_ALLOCATED;
            data_arr[i][7]=item.VM_NAME;
        }
    }
    return data_arr
}

function process_lvm_output(details,test){
    var test_data =
    {
        'DETAILS': [{
            'LOGICAL_VOLUME': 'LogVol00',
            'SIZE': '38G',
            'uuid': '/dev/VolGroup00/LogVol00',
            'STORAGE_ALLOCATED': 'No',
            'STORAGE_DISK_ID': '',
            'VM_NAME': ''
        }]
    }

    if (test)
        details = test_data

    var data_arr=new Array();
    if (details.DETAILS!=null){
        for(var i=0;i<details.DETAILS.length;i++){
            var item=details.DETAILS[i];
            data_arr[i]=new Array();
            data_arr[i][0]=item.LOGICAL_VOLUME;
            data_arr[i][1]=item.SIZE;
            data_arr[i][2]=item.uuid;
            data_arr[i][3]=item.STORAGE_ALLOCATED;
            data_arr[i][4]=item.STORAGE_DISK_ID;
            data_arr[i][5]=item.VM_NAME;
        }
    }
    return data_arr
}

var iscsi_colModel = new Ext.grid.ColumnModel([
    {header: _("名称"), width: 100, sortable: true, dataIndex: 'name'},
    {header: _("大小(GB)"), width: 60, sortable: true, dataIndex: 'size(gb)'},
    {header: _("磁盘"), width: 100, sortable: true, dataIndex: 'disk'},
    {header: _("状态"), width: 80, sortable: true, dataIndex: 'state'},
    {header: _("唯一路径"), width: 300, sortable: true, dataIndex: 'uniquepath'},
    {header: _("存储磁盘编号"), width: 150, hidden: true, sortable: true, dataIndex: 'storage_disk_id'},
    {header: _("分配"), width: 150, hidden: true, sortable: true, dataIndex: 'storage_allocated'},
    {header: _("虚拟机"), width: 150, hidden: false, sortable: true, dataIndex: 'vm_name'},
    {header: _("Lun"), hidden: true, defaultSortable: true, sortable: true, dataIndex: 'lun'}
    
]);
var iscsi_fields = new Array(
    {name: 'name'},
    {name: 'size(gb)'},
    {name: 'disk'},
    {name: 'state'},
    {name: 'uniquepath'},
    {name: 'storage_disk_id'},
    {name: 'storage_allocated'},
    {name: 'vm_name'},
    {name: 'lun'}
    
    
);
var aoe_colModel = new Ext.grid.ColumnModel([
    {header: _("磁盘"), width: 100, defaultSortable: true, sortable: true, dataIndex: 'disk'},
    {header: _("名称"), width: 100, hidden: true, sortable: true, dataIndex: 'name'},
    {header: _("大小(GB)"), width: 60, sortable: true, dataIndex: 'size(gb)'},
    {header: _("状态"), width: 80, sortable: true, dataIndex: 'state'},
    {header: _("接口"), width: 250, hidden: true, sortable: true, dataIndex: 'interface'},
    {header: _("存储磁盘编号"), width: 150, hidden: true, sortable: true, dataIndex: 'storage_disk_id'},
    {header: _("分配"), width: 150, hidden: true, sortable: true, dataIndex: 'storage_allocated'},
    {header: _("虚拟机"), width: 150, hidden: false, sortable: true, dataIndex: 'vm_name'}
]);
var aoe_fields = new Array(
    {name: 'name'},
    {name: 'size(gb)'},
    {name: 'disk'},
    {name: 'state'},
    {name: 'interface'},
    {name: 'storage_disk_id'},
    {name: 'storage_allocated'},
    {name: 'vm_name'}
);
var nfs_colModel = new Ext.grid.ColumnModel([
    {header: _("名称"), width: 140, hidden: true, defaultSortable: true, sortable: true, dataIndex: 'name'},
    {header: _("磁盘"), width: 175, hidden: false, sortable: true, dataIndex: 'disks'},
    {header: _("大小(GB)"), width: 60, sortable: false, dataIndex: 'size(gb)'},
    {header: _("虚拟机"), width: 150, hidden: false, sortable: true, dataIndex: 'vm_name'},
    {header: _("属性"), width: 225, hidden: true, sortable: true, dataIndex: 'attributes'},
    {header: _("Unique Path"), width: 300, hidden: true, sortable: true, dataIndex: 'uniquepath'},
    {header: _("分配"), width: 150, hidden: true, sortable: true, dataIndex: 'storage_allocated'},
    {header: _("存储磁盘编号"), width: 150, hidden: true, sortable: true, dataIndex: 'storage_disk_id'}
]);
var nfs_fields = new Array(
    {name: 'name'},
    {name: 'size(gb)'},
    {name: 'attributes'},
    {name: 'uniquepath'},
    {name: 'storage_allocated'},
    {name: 'storage_disk_id'},
    {name: 'vm_name'},
    {name: 'disks'}
);
var lvm_colModel = new Ext.grid.ColumnModel([
    {header: _("Logical Volume"), width: 100, hidden: false, defaultSortable: true, sortable: true, dataIndex: 'name'},
    {header: _("大小(GB)"), width: 60, sortable: false, dataIndex: 'size(gb)'},
    {header: _("Unique Path"), width: 200, hidden: false, sortable: true, dataIndex: 'uniquepath'},
    {header: _("虚拟机"), width: 150, hidden: false, sortable: true, dataIndex: 'vm_name'},
    {header: _("分配"), width: 150, hidden: true, sortable: true, dataIndex: 'storage_allocated'},
    {header: _("存储磁盘编号"), width: 150, hidden: true, sortable: true, dataIndex: 'storage_disk_id'}
]);
var lvm_fields = new Array(
    {name: 'name'},
    {name: 'size(gb)'},
    {name: 'uniquepath'},
    {name: 'storage_allocated'},
    {name: 'storage_disk_id'},
    {name: 'vm_name'}
);
var fc_colModel = new Ext.grid.ColumnModel([
    {header: _("名称"), width: 60, sortable: true, dataIndex: 'name'},
    {header: _("大小(GB)"), width: 60, sortable: true, dataIndex: 'size(gb)'},
    {header: _("磁盘"), width: 70, sortable: true, dataIndex: 'disk'},
    {header: _("状态"), width: 60, sortable: true, dataIndex: 'state'},
    {header: _("唯一路径"), width: 300, sortable: true, dataIndex: 'uniquepath'},
    {header: _("存储磁盘编号"), hidden: true, sortable: true, dataIndex: 'storage_disk_id'},
    {header: _("分配"), hidden: true, sortable: true, dataIndex: 'storage_allocated'},
    {header: _("虚拟机"), width: 100, hidden: false, sortable: true, dataIndex: 'vm_name'},
    {header: _("Lun"), hidden: true, defaultSortable: true, sortable: true, dataIndex: 'lun'}
]);
var fc_fields = new Array(
    {name: 'name'},
    {name: 'size(gb)'},
    {name: 'disk'},
    {name: 'state'},
    {name: 'uniquepath'},
    {name: 'storage_disk_id'},
    {name: 'storage_allocated'},
    {name: 'vm_name'},
    {name: 'lun'}
);