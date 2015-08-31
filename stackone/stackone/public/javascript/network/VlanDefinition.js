/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
* phy_nw_name that allows for performing the standard set of VM operations
* (start, stop, pause, kill, shutdown, reboot, snapshot, etc...). It
* also attempts to simplify various aspects of VM lifecycle management.


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
var nw_new_win_popup;
var virtual_nw_def_form;
var g_bridge_prefix;
function VlanDefinition(node,mode,response,parentPanel,network_scope,windowid){
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
        //Consider the node is a servergroup
        //node would be null
        sSiteId = "site_id=" + node.parentNode.attributes.id;
        op_level = "&op_level=SP";
        sGroupId = "&group_id=" + node.attributes.id;
        sNodeId = "";
    }
    else{
        //When menu is invoked at server level
        //Consider the node is a server
        sSiteId = "site_id=" + node.parentNode.parentNode.attributes.id;
        op_level = "&op_level=S";
        sGroupId = "&group_id=" + node.parentNode.attributes.id;
        sNodeId = "&node_id=" + node.attributes.id;
    }

    var nw_type_str="VLAN_NW"
    var network_name=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'network_name',
        id: 'network_name',
        width: 200,
        allowBlank:false
    });
    var network_description=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'network_description',
        width: 200,
        id: 'network_description'
    });


    var nat_forward_store= new Ext.data.JsonStore({
        url: '/network/get_nw_nat_fwding_map?node_id='+node.attributes.id,
        root: 'nw_nat',
        fields: [ 'name', 'value'],
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
                //if(mode=="EDIT")
                  //nat_forward.setValue(network.nw_nat_info_interface);
            }
        }
    });
    nat_forward_store.load();
    var nat_forward=new Ext.form.ComboBox({
        store:nat_forward_store,
        fieldLabel: _('NAT转发'),
        hideLabel:true,
        triggerAction:'all',
        emptyText :"",
        displayField:'name',
        valueField:'value',
        width: 150,
        editable:true,
        allowBlank: false,
        typeAhead: true,
        //forceSelection: true,
        selectOnFocus:true,
        enableKeyEvents:true,
        name:'forward',
        id:'nat_forward',
        mode:'local'
    });
    var nat_forward_lbl=new Ext.form.Label({
         html:'<div style>NAT Forwarding</div>'
    });


// var interface_store= new Ext.data.JsonStore({
//         url: '/network/get_interface?node_id='+node.attributes.id,
//         root: 'rows',
//         fields: [ 'name', 'value'],
//         sortInfo:{
//             field:'name',
//             direction:'ASC'
//         },
//         successProperty:'success',
//         listeners:{
//             loadexception:function(obj,opts,res,e){
//                 var store_response=Ext.util.JSON.decode(res.responseText);
//                 Ext.MessageBox.alert(_("Error"),store_response.msg);
//             },
//             load:function(store,recs,opts){
//                 if(mode=="EDIT")
//                 {                    
//                     interface.setValue(network.interface);
//                 }
//             }
//         }
//     });
//     interface_store.load();

//     var interface=new Ext.form.ComboBox({
//         store:interface_store,
//         fieldLabel: _('Interface'),
//         triggerAction:'all',
//         emptyText :"",
//         displayField:'name',
//         valueField:'value',
//         width: 200,
//         allowBlank: false,
//         typeAhead: true,
//         forceSelection: true,
//         selectOnFocus:true,
//         name:'forward',
//         id:'interface',
//         mode:'local'
//     });
    /*
    var interface=new Ext.form.TextField({
        fieldLabel: _('Interface'),
        name: 'interface',
        id: 'interface',
        width: 200,
        value: 'bond0',
        allowBlank:false,
        listeners:{
                blur : function(textbox) {
                    
                    var interface_name=textbox.getRawValue();
                    var vid = vlan_id.getValue();
                    var bridge_name= "";
                    if (vlan_checkBox.getValue())  
                    {                  
                        bridge_name = interface_name +"."+ vid;
                    }
                    else
                    {
                        bridge_name = interface_name;
                    }
                    bridgename.setValue(bridge_name);
                    
                }
        }
    });
    */

   var bridge_prefix_store = new Ext.data.JsonStore({
        url: '/network/get_bridge_prefix',
        root: 'rows',
        fields: ['name'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误: 网桥前缀不正确"),store_response.msg);
            },
            load:function(my_store, records, options){
                rec = my_store.getAt(0);
                g_bridge_prefix = rec.get("name");
                //alert(g_bridge_prefix);
            }
        }
    });
    bridge_prefix_store.load();

   var default_interfaces_store = new Ext.data.JsonStore({
        url: '/network/get_default_interfaces',
        root: 'rows',
        fields: [ 'name', 'value' ],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误: 接口"),store_response.msg);
            }
        }
    });
    default_interfaces_store.load();

    var interface=new Ext.form.ComboBox({
        store:default_interfaces_store,
        fieldLabel: _('接口'),
        triggerAction:'all',
        emptyText :"",
        displayField:'name',
        valueField:'value',
        width: 200,
        allowBlank: false,
        typeAhead: true,
//        forceSelection: true,
        selectOnFocus:true,
        editable:true,
        disabled:true,
        enableKeyEvents:true,
        name:'interface',
        id:'interface',
        mode:'local',
        listeners:{
                blur:function(combo) {
                    set_bridge_name(combo);
                }
         }
    });
    
    var no_vlan_interface=new Ext.form.ComboBox({
        store:default_interfaces_store,
        fieldLabel: _('接口'),
        triggerAction:'all',
        emptyText :"",
        displayField:'name',
        valueField:'value',
        width: 200,
        allowBlank: false,
        typeAhead: true,
//        forceSelection: true,
        selectOnFocus:true,
        editable:true,
        disabled:true,
        enableKeyEvents:true,
        name:'no_vlan_interface',
        id:'no_vlan_interface',
        mode:'local',
        listeners:{
                blur:function(combo) {
                    set_bridge_name(combo);
                }
         }
    });

    var from_pool_radio=new Ext.form.Radio({
        boxLabel:_('从VLAN ID池获取'),
        hideLabel: true,
        checked: false,
        name:'get_from_pool',
        id:'get_from_pool',
        value:'from_pool',
        width:150,
        listeners: {
            check: function(r, checked) {
                if(checked) {
                    specify_id_radio.setValue(false);
                    vlan_id_pool_combo.enable();
                    interface.disable();
                    vlan_id.disable();
                    no_vlan_id_radio.setValue(false);
                    isolation_fldset.enable();
                    Address_Specification_fldset.disable();
                }
            } 
        }
    });

    var specify_id_radio=new Ext.form.Radio({
        boxLabel:_('指定VLAN ID'),
        hideLabel: true,
        checked: true,
        name:'specify_id',
        id:'specify_id',
        value:'specify_id',
        width:120,
        listeners: {
            check: function(r, checked) {
                if(checked) {
                    from_pool_radio.setValue(false);
                    vlan_id_pool_combo.disable();
                    interface.enable();
                    vlan_id.enable();
                    no_vlan_id_radio.setValue(false);
                    isolation_fldset.enable();
                    Address_Specification_fldset.enable();
                    dhcp_checkBox.enable();
                    dhcprange.enable();
                }
            } 
        }
    });

    var no_vlan_id_radio=new Ext.form.Radio({
        boxLabel:_('没有VLAN ID'),
        hideLabel: true,
        checked: false,
        name:'no_vlan_id',
        id:'no_vlan_id',
        value:'no_vlan_id',
        width:120,
        listeners: {
            check: function(r, checked) {
                if(checked) {
                    from_pool_radio.setValue(false);
                    vlan_id_pool_combo.disable();
                    specify_id_radio.setValue(false);
                    no_vlan_interface.enable();
                    interface.disable();
                    vlan_id.disable();
                    Address_Specification_fldset.enable();
                    isolation_fldset.disable();
                    dhcp_checkBox.disable();
                    dhcprange.disable();
                }
            } 
        }
    });


    //VLAN ID Pool-Start
   var vlan_id_pool_store = new Ext.data.JsonStore({
        url: '/network/get_vlan_id_pools',
        root: 'rows',
        fields: [ 'id', 'name' ],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误:接口"),store_response.msg);
            }
        }
    });
    vlan_id_pool_store.load();

    var vlan_id_pool_combo=new Ext.form.ComboBox({
        store:vlan_id_pool_store,
        fieldLabel: _('VLAN ID池'),
        triggerAction:'all',
        emptyText :"",
        displayField:'name',
        valueField:'id',
        width: 200,
        allowBlank: false,
        typeAhead: true,
//        forceSelection: true,
        selectOnFocus:true,
        editable:true,
        enableKeyEvents:true,
        name:'vlan_id_pool',
        id:'vlan_id_pool',
        mode:'local',
        listeners:{
            select: function(obj){
                Address_Specification_fldset.disable();
            }
         }
    });
    //VLAN ID Pool-End

    function set_bridge_name(combo) {
        var interface_name=combo.getRawValue();
        //extract numeric part of the interface with following statement.
//        console.log(interface_name);
        var r = interface_name.match(/[\d\.]+/g);
//        console.log(r);
        if(r){
            int_num = r[0];
            var vid = vlan_id.getValue();
            var bridge_name="";
            if(parseInt(vid)>=0) {
                bridge_name = g_bridge_prefix + int_num + "." + vid;
            }
            else {
                bridge_name = g_bridge_prefix + int_num;
            }
            bridgename.setValue(bridge_name);
        }
    }

    var id_label=new Ext.form.Label({
        //text: "ID: ",
        html:'<div style="">'+_("(指定VLAN ID)")+'&nbsp;</div>',
        hidden: true
    });

    var vlan_id=new Ext.form.TextField({
        fieldLabel: _('VLAN ID'),
        //boxLabel: _('ID'),
        hideLabel: false,
        name: 'vlan_id',
        id: 'vlan_id',
        width: 70,
        allowBlank:false,
        disabled: true,
        vtype: 'portnum',
        value:'',
        listeners:{
                blur : function(textbox) {
                    var value1="";
                    vid=textbox.getRawValue();
                    if(parseInt(vid)<0 || parseInt(vid)>4094) {
                        Ext.MessageBox.alert(_("警告"), _("请输入0到4094之间的VLAN ID."));
                        textbox.setValue("");
                        return;
                    }
                    set_bridge_name(textbox);
                }
        }
    });
    var dhcp_checkBox=  new Ext.form.Checkbox({
        id: 'dhcp_checkBox',
        name: 'dhcp_checkBox',
        checked: true,
        hideLabel: true,
        boxLabel: 'DHCP', 
        width:70,       
        listeners: {
            check: function(this_checkbox, checked) {
                //alert("check");
                if(checked)
                {
                    dhcprange.enable();
                }
                else
                {
                   dhcprange.setValue("");
                   dhcprange.disable();
                }
            },
            click: function(obj) {
                //alert("click");
            }

        }
    });
    var vlan_checkBox=  new Ext.form.Checkbox({
        id: 'vlan_checkBox',
        name: 'vlan_checkBox',
        checked: false,
        hideLabel: true,
        boxLabel: 'VLAN', 
        width:70,       
        listeners: {
            check: function(this_checkbox, checked) {
                if(checked)
                {
                    vlan_id.enable();
                    vid=vlan_id.getValue();
                    interface_name = interface.getValue();
                    bridge_name = interface_name +"."+ vid;
                    bridgename.setValue(bridge_name);
                    //id_label.setVisible(true);
                }
                else
                {
                    vlan_id.disable(); 
                    interface_name = interface.getValue();                    
                    bridgename.setValue(interface_name);
                    //id_label.setVisible(false);
                }
            }

        }
    });

    

    var vlan_id_group=new Ext.Panel({
        id:"vlan_id_group",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        items:[vlan_checkBox,id_label, vlan_id]
    });


    
function show_slave_CheckBox(value,params,record){
        var id = Ext.id();
        (function(){
            new Ext.form.Checkbox({
                renderTo: id,
                checked:value,
                width:100,
                height:16,
                id:"show_slave_CheckBox",
                listeners:{
                    check:function(field,checked){
                        if(checked==true){
                            record.set('is_slave',true);
                        }else{
                            record.set('is_slave',false);
                        }
                    }
                }
            });
        }).defer(20)
        return '<span id="' + id + '"></span>';
}

   
 var bond_details_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width:100,
        dataIndex: 'phy_nw_name',        
        editor: new Ext.form.TextField({
            allowBlank: false
        }),
        sortable:true
    },    
    {
        header: _("从属"),
        dataIndex: 'is_slave',        
        sortable:true,
        renderer: show_slave_CheckBox
    }
    ]);


//     var bond_details_store = new Ext.data.JsonStore({
//         url: '/backup/get_copy_options?group_id='+group_id,
//         root: 'rows',
//         fields: ['attribute','value'],
//         successProperty:'success',
//         listeners:{
//             loadexception:function(obj,opts,res,e){
//                 var store_response=Ext.util.JSON.decode(res.responseText);
//                 Ext.MessageBox.alert(_("Error"),store_response.msg);
//             }
//         }
// 
//     });
//    bond_details_store.load();    
//     var bond_detail_store = new Ext.data.SimpleStore({
//         fields: ['phy_nw_name', 'is_slave'],
//         idIndex: 0 // id for each record will be the first element
//     });
// 
//     var myData = [
//         [ 'eth0', true],  // note that id for the record is the first element
//         [ 'eth1', false],
//         [ 'eth2', false],
//         [ 'eth3', false]
//     ];
// // 
// //     
//     bond_detail_store.loadData(myData);
    

    url_bond_detail_store= '/network/get_bond_details' 
    
     if(mode=="EDIT"){
         url_bond_detail_store= '/network/get_bond_details?nw_id='+response.network.nw_id;
 }

    
    var bond_detail_store = new Ext.data.JsonStore({
//         url: '/storage/get_vm_list?group_id=' + "1",
        id: 'bond_detail_store',
        url: url_bond_detail_store,
        root: 'rows',
        fields: ['phy_nw_name', {name: 'is_slave', type: 'boolean'} ],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e) {
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    bond_detail_store.load();
//     bond_detail_store.loadData(myData);

    var bond_details_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var bond_details_grid = new Ext.grid.EditorGridPanel({
        store: bond_detail_store,
        id: "bond_details_grid",
        stripeRows: true,
        colModel:bond_details_columnModel,
        frame:false,
        border: true,
        selModel:bond_details_selmodel,
        autoExpandColumn:1,        
        autoscroll:true,
        height:130,
        width:180,
        clicksToEdit:2,
        enableHdMenu:true, 
        disabled: false
    });

 
    var bond_details_checkBox=  new Ext.form.Checkbox({
        id: 'bond_details_checkBox',
        name: 'bond_details_checkBox',
        checked: true,
        boxLabel: 'Bond详情', 
        hideLabel: true,
        width:105,       
        listeners: {
            check: function(this_checkbox, checked) {
                if(checked)
                {
                    bond_details_grid.enable()
                }
                else
                {
                    bond_details_grid.disable()
                }
            }

        }
    });

   


   var address_space_store = new Ext.data.JsonStore({
        url: '/network/get_nw_address_space_map',
        root: 'nw_address_space',
        fields: [ 'name', 'value'],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    address_space_store.load();
    
    var address_space=new Ext.form.ComboBox({
        store:address_space_store,
        fieldLabel: _('地址空间'),
        triggerAction:'all',
        emptyText :"",
        displayField:'name',
        valueField:'value',
        width: 200,
        allowBlank: true, //false
        typeAhead: true,
//        forceSelection: true,
        selectOnFocus:true,
        editable:true,
        enableKeyEvents:true,
        name:'address_space',
        id:'address_space',
        mode:'local',
        listeners:{
                blur : function(combo) {
                     if(no_vlan_id_radio.getValue()==false)
                     {
                        var value1="";
                        value1=address_space.getRawValue();
                        addressspace_ajax(value1,dhcprange);
                      }  
                },
                 select:function(combo,record,index){
                    if(no_vlan_id_radio.getValue()==false){
                    var value2="";
                    value2=record.get('value');
                    addressspace_ajax(value2,dhcprange);}
            }
         }

    });

    var dhcprange=new Ext.form.TextField({
        fieldLabel: _('DHCP范围'),
        name: 'dhcpname',
        id: 'dhcpname',
        width: 200,
        allowBlank:true
    });

/*
    var nat_forward_store= new Ext.data.JsonStore({
        url: '/network/get_nw_nat_fwding_map?node_id='+node.attributes.id,
        root: 'nw_nat',
        fields: [ 'name', 'value'],
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
                if(mode=="EDIT")
                  nat_forward.setValue(network.nw_nat_info_interface);
            }
        }
    });
    nat_forward_store.load();

    var nat_forward=new Ext.form.ComboBox({
        store:nat_forward_store,
        fieldLabel: _('NAT Forwarding'),
        triggerAction:'all',
        emptyText :"",
        displayField:'name',
        valueField:'value',
        width: 200,
        allowBlank: true,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'forward',
        id:'nat_forward',
        mode:'local'
    });
*/
    Ext.form.VTypes.ipnumVal  = /^[0-9.\-]/;
    Ext.form.VTypes.ipnumMask = /[\d.]/;
    Ext.form.VTypes.ipnumText = 'In-valid IP .';
    Ext.form.VTypes.ipnum     = function(v){
        return Ext.form.VTypes.ipnumVal.test(v);
    };

    var gateway=new Ext.form.TextField({
        fieldLabel: _('网关'),
        name: 'gateway',
        id: 'gateway',
        width: 200,
        allowBlank:true,
        vtype: 'ipnum'
        
    });

    var ip_address=new Ext.form.TextField({
        fieldLabel: _('IP地址'),
        name: 'ip_address',
        id: 'ip_address',
        width: 200,
        allowBlank:true,
        vtype: 'ipnum'
    });
    var dhcprange=new Ext.form.TextField({
        fieldLabel: _('DHCP范围'),
        name: 'dhcpname',
        id: 'dhcpname',
        width: 200,
        allowBlank:true
    });

//     var dhcp_checkbox=  new Ext.form.Checkbox({
// 
//         name: 'dhcp_checkbox',
//         checked: true,
//         boxLabel: 'DHCP', 
//         hideLabel: true,
//         width:100,       
//         listeners: {
//             check: function(this_checkbox, checked) {
//                 if(checked)
//                 {
//                     dhcprange.enable()
//                 }
//                 else
//                 {
//                     dhcprange.disable()
//                 }
//             }
// 
//         }
//     });

    var bridgename=new Ext.form.TextField({
        fieldLabel: _('网桥名称'),
        name: 'bridgename',
        width: 200,
        id: 'bridgename'
        //value: interface.getRawValue(),
    });


    var lb2=new Ext.form.Label({
        text:_("指定VLAN详情.")
    });

    var lb3=new Ext.form.Label({
        html:'<table><tr><td width="100"></td><td width="275"><i>提示：使用NAT创建隔离N / W或转发到物理N / W.</i></td></tr></table>'
    });
    var lb4=new Ext.form.Label({
        html:'<table><tr><td width="100"></td><td width="275"><i>提示: 为每个定义的虚拟网络创建网桥.</i></td></tr></table>'
    });

    var hostonly_radio=new Ext.form.Radio({
        boxLabel:_('隔离'),
        hideLabel: true,
        checked: true,
        name:"hostonly_radio",
        id:'hostonly_radio',
        value:'host_only',
        width:100,
        listeners: {
            check: function(r, checked) {
                if(checked) {
                    nat_forward_lbl.hide();
                    nat_radio.setValue(false);
                    nat_forward.hide();
//                    nat_forward.getEl().up('.x-form-item').setDisplayed(false);
                }
            }
        }
    });

    var nat_radio=new Ext.form.Radio({
        boxLabel:_('NAT转发'),
        hideLabel: true,
        name:"nat_radio",
        value:'nat_forwarded',
        width:150,
        listeners: {
            check: function(r, checked) {
                if(checked) {
                    hostonly_radio.setValue(false);
                    if(isolation_fldset.findById('nat_forward')){
                        nat_forward_lbl.show();
                        nat_forward.show();
                        //nat_forward.getEl().up('.x-form-item').setDisplayed(true);
                    }/*else{
                        
                        virtual_nw_det_fldset.insert(13,{
                            width: 420,
                            layout:'form',
                            items:[nat_forward]
                        });
                        virtual_nw_def_form.doLayout();
                        //nat_forward.getEl().up('.x-form-item').setDisplayed(true);
                    }*/
                }
            }
        }
    });
 if(mode=='NEW'){
     nat_forward.hide();
     nat_forward_lbl.hide();
   }

    var nw_type=new Ext.form.RadioGroup({
        frame: true,
        title:_('RadioGroups'),
        fieldLabel: _('隔离或NAT'),
        labelWidth: 80,
        width: 300,
        bodyStyle: 'padding:0 10px 0;',
        name:'radio',
        items: [hostonly_radio,nat_radio]

    });

   
    
    var virt_save_button=new Ext.Button({
            name: 'ok',
            id: 'ok',
             text:_("保存"),
            icon:'icons/accept.png',
            cls:'x-btn-text-icon',
            listeners: {
                    click: function(btn) {
                        //server pool level
                        if(sGroupId != "" && sNodeId == "") {
                            //If the network is defined at data center level
                            if(network_scope == 'DC') {
                                Ext.MessageBox.alert("信息", "数据中心级网络不能在这里编辑");
                                return
                            }
                        } //server level
                        else if(sGroupId != "" && sNodeId != "") {
                            //If the network is defined at server pool level
                            if(network_scope == 'SP' || network_scope == 'DC') {
                                Ext.MessageBox.alert("信息", "这里不能编辑数据中心和服务器池级别的网络");
                                return
                            }
                        }

                        

                        if(!network_name.getValue()){
                             Ext.MessageBox.alert( _("错误") ,_("网络名称是必须要输入的"));
                             return;
                        }
                        if(!network_description.getValue()){
                             Ext.MessageBox.alert( _("错误") ,_("网络说明是必须要输入的"));
                             return;
                        }
//                          if(!address_space.getRawValue()){
//                              Ext.MessageBox.alert( _("Error") ,_("Address space is required"));
//                              return;
//                         }
//                         if(!dhcprange.getRawValue()){
//                              Ext.MessageBox.alert( _("Error") ,_("DHCP address range is required "));
//                              return;
//                         }

                        if(nat_radio.getValue()){
                            
                             if(!nat_forward.getRawValue()){
                                 Ext.MessageBox.alert( _("错误") ,_("NAT Forwarding 是必须要输入的"));
                                 return;
                            }
                        }
//                        alert(address_space.getRawValue()+"---"+dhcprange.getRawValue());
                     var slaves_stat="[";
                        for(var i=0;i<bond_detail_store.getCount();i++){
                            if  (bond_detail_store.getAt(i).get("is_slave") == true)
                            {
                                //slaves_stat+="'slave':";
                                //slaves_stat+="'"+bond_detail_store.getAt(i).get("phy_nw_name")+"',";
                                slaves_stat+= "'"+ bond_detail_store.getAt(i).get("phy_nw_name")+"',";
                                
                            }
                        }   
                        slaves_stat+="]";                                            

                        slave_jdata= eval("("+slaves_stat+")");

                        if(mode=="NEW"){
                                var vlan_interface="";
                                if(no_vlan_id_radio.getValue()==true)
                                {
                                    vlan_interface=no_vlan_interface.getRawValue();
                                }else{vlan_interface=interface.getRawValue();}        
                                var params="";
                                var url="";
                                params= sSiteId + op_level + sGroupId + sNodeId + "&nw_name="+network_name.getValue()+"&nw_desc="+network_description.getValue()+ "&nw_type="+ nw_type_str+
                                    "&nw_bridge="+bridgename.getValue()+"&nw_address_space="+address_space.getRawValue()+
                                    "&nw_dhcp_range="+dhcprange.getRawValue()+"&nat_radio="+nat_radio.getValue()+"&nw_nat_fwding="+nat_forward.getRawValue()+"&nw_gateway="+ gateway.getValue()+ "&nw_ip_address="+ip_address.getValue()+  "&nw_use_vlan="+vlan_checkBox.getValue()+ "&nw_vlan_id="+vlan_id.getValue()+ "&nw_isbonded="+bond_details_checkBox.getValue()+ "&nw_slaves="+slave_jdata+ "&interface="+vlan_interface+"&vlan_id_pool_id="+vlan_id_pool_combo.getValue();
                                url="/network/add_nw_defn?"+params;
                   
                        }else{
                            var id=response.network.nw_id;
                            params= params="nw_id="+id+"&nw_name="+network_name.getValue()+"&nw_desc="+network_description.getValue();
                            url="/network/edit_nw_defn?"+params;
                        }

                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {//alert(xhr.responseText);
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    //                                           closeVirtualNetworkDefinition();
                                    //                                           parentPanel.remove('virtual_nw_def_form');
                                    
                                    closeThisWindow(nw_new_win_popup);
                                    //reloadVirtualNetworkDefList();
                                    DelayLoadingDefList(virtual_nw_grid);

                                }else{                                    
                                    Ext.MessageBox.alert(_("Failure"),response.msg);
                                }
                            },
                            failure: function(xhr){                                    
                                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                            }
                        });

                    }
                }

     });
     var virt_cancel_button=new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('取消'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                       click: function(btn) {
                        closeThisWindow(nw_new_win_popup);
                        reloadVirtualNetworkDefList();
                }
                }
            });
    if(mode=='NEW'){
        //nat_forward.hide();
   }
   var  select_VLAN_ID_fldset=new Ext.form.FieldSet({
        title:_('VLAN信息'),
        collapsible: false,
        autoHeight:true,
        width:395,
        labelSeparator: ' ',
        labelWidth:100,
        layout:'column',
        items:[{
                width: 416,
//                layout:'form',
                bodyStyle: 'padding:0px 0px 0px 8px;',
                items:[no_vlan_id_radio]
            },{
                width: 416,
                layout:'form',
                bodyStyle: 'padding:0px 0px 0px 18px;',
                labelWidth:82,
                items:[no_vlan_interface]
            },
            {
                width: 416,
//                layout:'form',
                bodyStyle: 'padding:0px 0px 0px 8px;',
                items:[from_pool_radio]
            },{
             width: 416,
                layout:'form',
                bodyStyle: 'padding:0px 0px 0px 18px;',
                labelWidth:82,
                items:[vlan_id_pool_combo]
            },{
                width: 416,
//                layout:'form',
                bodyStyle: 'padding:0px 0px 0px 8px;',
                items:[specify_id_radio]
            },
            {               
                width: 105,
                layout:'form',
                items:[bond_details_checkBox],
                hidden:true
            },{
                width: 190,
                layout:'form',
                border: true,
                items:[bond_details_grid],
                hidden:true
            },/*{
                width: 105,
                layout:'form',
                items:[vlan_checkBox]
            },*/{
                width: 416,
                layout:'form',
                //labelWidth:20,
                bodyStyle: 'padding:0px 0px 0px 18px;',
                labelWidth:82,
                items:[vlan_id]
            },{
                width: 416,
                layout:'form',
                bodyStyle: 'padding:0px 0px 5px 18px;',
                labelWidth:82,
                items:[interface]
            }
        ] 


    })


   var  Address_Specification_fldset=new Ext.form.FieldSet({
        title:_('地址规范'),
        collapsible: false,
        autoHeight:true,
        width:395,
        labelSeparator: ' ',
        labelWidth:100,
        //bodyStyle: 'padding:0px 0px 0px 0px;',
        layout:'column',
        items:[
            {
               width: 420,
               layout:'form',
               items:[address_space],
               bodyStyle: 'padding:3px 0px 0px 8px;',
               hidden:false,
               labelWidth:92
            },{
                width:420,
//                layout:'form',
                bodyStyle: 'padding:0px 0px 0px 8px;',
                items:[dhcp_checkBox]
            },
               {
                width: 420,
                layout:'form',
                 bodyStyle: 'padding:0px 0px 0px 20px;',
                labelWidth:80,
                items:[dhcprange]
            },{
                width: 420,
                layout:'form',
                items:[gateway],
                hidden:true
            },{
                width: 400,
                layout:'form',
                items:[ip_address],
                hidden:true
            },{
               width: 420,
               layout:'form',
               items:[bridgename],
               bodyStyle: 'padding:0px 0px 3px 8px;',
               labelWidth:92
            }

        ]
                

            })


    

   var isolation_fldset = new Ext.form.FieldSet({
        title:_('隔离'),
        collapsible: false,
        autoHeight:true,
        width:395,
        labelSeparator: ' ',
        labelWidth:100,
        //bodyStyle: 'padding:0px 0px 0px 0px;',
        layout:'column',
        items:[
            {
                width: 110,
//                layout:'form',
                bodyStyle: 'padding:0px 0px 0px 8px;',
                //labelWidth:0,
                items:[hostonly_radio]
            },{
                width: 160,
//                layout:'form',
               bodyStyle: 'padding:0px 0px 0px 0px;',
                //labelWidth:0,
                items:[nat_radio]
            },
            {
                width: 120,
                layout:'form',
                bodyStyle: 'padding:0px 0px 0px 10px;',
                items:[nat_forward_lbl]


            },{
                width: 210,
                layout:'form',
                bodyStyle: 'padding:0px 0px 0px 0px;',
                items:[nat_forward],
                labelWidth:84
               
            }
        ]


    })
    if(mode == 'NEW')
    {
                    from_pool_radio.setValue(false);
                    vlan_id_pool_combo.disable();
                    interface.enable();
                    vlan_id.enable();
                    no_vlan_id_radio.setValue(false);
                    no_vlan_interface.disable();
                    Address_Specification_fldset.enable();
                    isolation_fldset.enable();
    }
     if(mode=='EDIT'){
       if(nat_forward.value){
            nat_radio.setValue(true);
       }
       else{
            hostonly_radio.setValue(true);
       }
   }
   var  virtual_nw_det_fldset=new Ext.form.FieldSet({
        title: _('指定虚拟网络详情'),
        collapsible: false,
        autoHeight:true,
        width:400,
        labelSeparator: ' ',
        labelWidth:100,
        layout:'column',
        items: [
            {
                width: 420,
                layout:'form',
                items:[network_name]
            },{
                width: 420,
                layout:'form',
                items:[network_description]
            }, select_VLAN_ID_fldset,isolation_fldset,/*{
                width: 200,
                layout:'form',
                items:[id_label]
            },*/Address_Specification_fldset
//             {
//                 width: 105,
//                 layout:'form',
//                 items:[dhcp_checkbox]
//             },
        ]
    });

    //Start - From existing definitions
    var new_def_radio=new Ext.form.Radio({
        boxLabel: _('Define new network'),
        id:'new_def',
        name:'radio',
        //icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners:{
            check:function(field,checked){
                if(checked==true){
                    existing_nw_def_form.setVisible(false);
                    virtual_nw_def_form.setVisible(true);
                    nw_def_form.getBottomToolbar().show();
                }
            }
        }
    });

    var from_dc_radio=new Ext.form.Radio({
        checked:true,
        boxLabel: _('从现有网络选择'),
        id:'from_dc',
        name:'radio',
        //icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners:{
            check:function(field,checked){
                if(checked==true){
                    existing_nw_def_form.setVisible(true);
                    virtual_nw_def_form.setVisible(false);
                    nw_def_form.getBottomToolbar().hide();
                }
            }
        }
    });

    var dc_radio_group= new  Ext.form.RadioGroup({
        columns: 1,
        //vertical: false,
        id:'dcradiogroup',
        items: [new_def_radio,from_dc_radio]
    });

    dc_radio_panel=new Ext.Panel({
        id:"dc_radio_panel_id",
        width:'100%',
        height:65,
        frame:true,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[dc_radio_group]
    });

    var dc_nw_columnModel = new Ext.grid.ColumnModel([

        {header: _("名称"), width: 100, sortable: false, dataIndex: 'name'},
        {header: _("详情"), width: 225, sortable: false, dataIndex: 'definition'},//225
        {header: _("说明"), width: 100, sortable: false, dataIndex: 'description'},//100
        {header: _("状态"), hidden: true, sortable: false, dataIndex: 'status'},
        {header: _("范围"), hidden: true, sortable: false, dataIndex: 'scope'}
    ]);

     var network_list_dc_store = new Ext.data.JsonStore({
        url: '/network/get_nw_dc_defns?' + sSiteId + op_level + sGroupId + sNodeId,
        root: 'rows',
        fields: [ 'name', 'definition', 'description','status','type','id', 'status', 'scope'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    network_list_dc_store.load();

    var  virtual_nw_dc_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:false
    });

    var virt_associate_button=new Ext.Button({
        name: 'btnNwAssociate',
        id: 'btnNwAssociate',
        text:"关联",
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                //var nwId = virtual_nw_dc_grid.getSelectionModel().getSelected().get('id');
                var def_ids = "";
                var sm = virtual_nw_dc_grid.getSelectionModel();
                var rows = sm.getSelections();
                for(i=0; i<rows.length; i++) {
                    if(i == rows.length-1) {
                        def_ids += rows[i].get('id');
                    } else {
                        def_ids += rows[i].get('id') + ',';
                    }
                }
                associate_nw_defns("NETWORK",def_ids);
            }
        }
    });

     var virt_associate_cancel_button=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('关闭'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow(windowid);
                reloadVirtualNetworkDefList();
            }
        }
    });

    virtual_nw_dc_grid = new Ext.grid.GridPanel({
        store: network_list_dc_store,
        colModel:dc_nw_columnModel,
        stripeRows: true,
        frame:false,
        selModel:virtual_nw_dc_selmodel,
        width:'100%',
        height:270,
        autoScroll:true,
        enableHdMenu:false
    });

    existing_nw_def_form = new Ext.Panel({
        frame:true,
        id:'existing_nw_def_form',
        width:'100%',
        items:[virtual_nw_dc_grid],
        tbar:[{xtype: 'tbfill'},virt_associate_button,'-',virt_associate_cancel_button]
    });
    //End - From existing definitions

    virtual_nw_def_form = new Ext.Panel({
        frame:true,
        id:'virtual_nw_def_form',
        width:'100%',
        items:[virtual_nw_det_fldset]
    });

    nw_def_form = new Ext.FormPanel({
        frame:true,
        width:'100%',
        height:506,//430 (261), 254, 324
        items:[dc_radio_panel,existing_nw_def_form,virtual_nw_def_form],
        bbar:[{xtype: 'tbfill'},virt_save_button,'-',virt_cancel_button]
    });

    //nat_forward.getEl().up('.x-form-item').setDisplayed(true);
    if(mode=="NEW"){
        //bridgename.setValue(response.bridge.bridge);

            dc_radio_panel.setVisible(false);
            existing_nw_def_form.setVisible(false);
            virtual_nw_def_form.setVisible(true);
            //nw_def_form.height = 430;
        //}

    }else{
        var network=response.network;
        network_name.enable();
        network_description.enable();

        //server pool level
        if(sGroupId != "" && sNodeId == "") {
            if(network_scope == "DC") {
                network_name.disable();
                network_description.disable();
            }
        }
        //server level
        else if(sGroupId != "" && sNodeId != "") {
            if(network_scope == "DC" || network_scope == "SP") {
                network_name.disable();
                network_description.disable();
            }
        }
        if(nat_radio.validate()){
                nat_forward.hide();
                nat_forward_lbl.hide();
            }
        network_name.setValue(network.name);
        network_description.setValue(network.description);
        address_space.setValue(network.nw_ipv4_info_ip_network);
        dhcprange.setValue(network.dhcp_range_value);
        vlan_id_pool_combo.setValue(network.vlan_id_pool_name);
        interface.setValue(network.interface);
        bridgename.setValue(network.nw_bridge_info_name);  
        vlan_id.setValue(network.vlan_id);      
        vlan_checkBox.setValue(network.use_vlan);        
        gateway.setValue(network.gateway);
        ip_address.setValue(network.ip_address);
        bond_details_checkBox.setValue(network.is_bonded);

    
        var slave_list = network.slave_list;
       
        network_name.disable();
        nw_type.disable();
        no_vlan_id_radio.disable();
        dhcp_checkBox.disable();
        address_space.disable();
        nat_forward.disable();
        dhcprange.disable();
        bridgename.disable();
        lb3.disable();
        lb4.disable();
        vlan_checkBox.disable();
        vlan_id.disable();
        gateway.disable();
        ip_address.disable();
        bond_details_checkBox.disable();
        bond_details_grid.disable();
        interface.disable();
        vlan_id_pool_combo.disable();
        from_pool_radio.disable();
        specify_id_radio.disable();
        nat_radio.disable();
        hostonly_radio.disable();
        if(network.nw_nat_forward==true){
            nat_radio.setValue(true);
            hostonly_radio.setValue(false);
            nat_forward.setValue(network.nw_nat_info_interface);
        }
        else if (network.nw_nat_forward==false){nat_radio.setValue(false);
            hostonly_radio.setValue(true);
            nat_radio.disable();
            hostonly_radio.disable();        
            }
        
        //show normal edit window
        dc_radio_panel.setVisible(false);
        existing_nw_def_form.setVisible(false);
        virtual_nw_def_form.setVisible(true);
    }

    return nw_def_form;
}


function addressspace_ajax(value,dhcprange){
    var url="/network/nw_address_changed?ip_value="+value;
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                dhcprange.setValue(response.range.range);
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

