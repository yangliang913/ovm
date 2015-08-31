/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
var nw_name;
var nw_new_win_popup;
var virtual_nw_def_form;
function VirtualNetworkDefinition(node,mode,response,parentPanel,network_scope,windowid){
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

    var network_name=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'network_name',
        id: 'network_name',
        width: 200,
        allowBlank:false
    });
    nw_name = network_name;

    var network_description=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'network_description',
        width: 200,
        id: 'network_description'
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
    var dhcprange=new Ext.form.TextField({
        fieldLabel: _('DHCP范围'),
        name: 'dhcpname',
        id: 'dhcpname',
        width: 200,
        allowBlank:true
    });
    var bridgename=new Ext.form.TextField({
        fieldLabel: _('网桥名称'),
        name: 'bridgename',
        width: 200,
        id: 'bridgename'
    });


    var lb2=new Ext.form.Label({
        text:_("指定虚拟网络详情.")
    });

    var lb3=new Ext.form.Label({
        html:'<table><tr><td width="100"></td><td width="275"><i>提示: 使用NAT创建隔离N / W或转发到物理N / W.</i></td></tr></table>'
    });
    var lb4=new Ext.form.Label({
        html:'<table><tr><td width="100"></td><td width="275"><i>提示: 为每个定义的虚拟网络创建网桥.</i></td></tr></table>'
    });

    
var interface_store= new Ext.data.JsonStore({
        url: '/network/get_interface?node_id='+node.attributes.id,
        root: 'rows',
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
                {                    
                    interface.setValue(network.interface);
                }
            }
        }
    });
    interface_store.load();

    var interface=new Ext.form.ComboBox({
        store:interface_store,
        fieldLabel: _('接口'),
        triggerAction:'all',
        emptyText :"",
        displayField:'name',
        valueField:'value',
        width: 200,
        allowBlank: false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'forward',
        id:'interface',
        mode:'local'
    });

    var id_label=new Ext.form.Label({
        //text: "ID: ",
        html:'<div style="">'+_("ID: ")+'&nbsp;</div>'
    })

    var vlan_id=new Ext.form.TextField({
        fieldLabel: _('ID'),
        boxLabel: _('ID'),
        hideLabel: true,
        name: 'vlan_id',
        id: 'vlan_id',
        width: 50,
        allowBlank:false,
        disabled: true,
        vtype: 'portnum'
    });

    var vlan_checkBox=  new Ext.form.Checkbox({
        id: 'vlan_checkBox',
        name: 'vlan_checkBox',
        checked: false,
        hideLabel: true,
        boxLabel: 'V LAN', 
        width:70,       
        listeners: {
            check: function(this_checkbox, checked) {
                if(checked)
                {
                    vlan_id.enable();
                }
                else
                {
                   vlan_id.disable();
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
        boxLabel: 'Bond Details', 
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
        allowBlank: false,
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
                    var value1="";
                    value1=address_space.getRawValue();
//                    alert(value1);
                    if(dhcp_checkBox.checked){
                        addressspace_ajax(value1,dhcprange);
                    }
                },
                 select:function(combo,record,index){
                    var value2="";
                    value2=record.get('value');
                    if(dhcp_checkBox.checked){
                        addressspace_ajax(value2,dhcprange);
                    }
            }
        }

    });


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
        fieldLabel: _('NAT转发'),
        triggerAction:'all',
        emptyText :"",
        displayField:'name',
        valueField:'value',
        width: 200,
        allowBlank: false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'forward',
        id:'nat_forward',
        mode:'local'
    });

var nw_type_str="HOST_PRIVATE_NW"
var hostonly_radio=new Ext.form.Radio({
        boxLabel:_('仅主机（独立）'),
        hideLabel: true,

        checked: true,
        name:"nw_type",
        id:'hostonly_radio',
        value:'host_only',
        width:140,
        listeners: {
            check: function(r, checked) {
                if(checked) {
                    nw_type_str="HOST_PRIVATE_NW";
                    nw_vlan.setValue(false);
                    //nat_forward.hide();
                    //nat_forward.getEl().up('.x-form-item').setDisplayed(false);                    
                
                    showField2(dhcprange);

                    hideField2(interface);
                    hideField2(bond_details_checkBox); 
                    //hideField2(bond_details_grid);
                    bond_details_grid.hide();
                    hideField2(vlan_checkBox);
                    hideField2(vlan_id);                    
                    hideField2(gateway);
                    hideField2(ip_address);
                    hideField2(nat_forward);
                }
            } 
        }
    });

    var nat_radio=new Ext.form.Radio({
        boxLabel:_('NAT转发'),
        hideLabel: true,
        name:"nw_type",
        id:'nat_radio',
        value:'nat_forwarded',
        width:120,
        listeners: {
            check: function(r, checked) {
                if(checked) {
                    nw_type_str="HOST_PRIVATE_NW";
                    nw_vlan.setValue(false);

//                     if(virtual_nw_det_fldset.findById('nat_forward')){
//                         nat_forward.show();
//                         nat_forward.getEl().up('.x-form-item').setDisplayed(true);
//                     }else{
//                         
//                         virtual_nw_det_fldset.insert(6,{
//                             width: 420,
//                             layout:'form',
//                             items:[nat_forward]
//                         });
//                         virtual_nw_def_form.doLayout();
//                         //nat_forward.getEl().up('.x-form-item').setDisplayed(true);
//                     }
                    showField2(nat_forward);
                    showField2(dhcprange);

                    hideField2(interface);
                    hideField2(bond_details_checkBox); 
                    //hideField2(bond_details_grid);
                    bond_details_grid.hide();
                    hideField2(vlan_checkBox);
                    hideField2(vlan_id);                    
                    hideField2(gateway);
                    hideField2(ip_address);
                }
            }
        }
    });

    var nw_vlan=new Ext.form.Radio({
        boxLabel:_('VLAN'),
        name:"nw_type",
        hideLabel: true,
        id:'nw_vlan',
        value:'nw_vlan',
        checked: false,  
        width:80,
        listeners: {
            check: function(r, checked) {                    
                 if(checked) {
                    nw_type_str="VLAN_NW";
                    showField2(interface);
                    showField2(bond_details_checkBox); 
                    //showField2(bond_details_grid);
                    bond_details_grid.show();
                    showField2(vlan_checkBox);
                    showField2(vlan_id);
                    showField2(bridgename); 
                    showField2(gateway);
                    showField2(ip_address);
                    
                    hideField2(nat_forward);
                    hideField2(dhcprange);
                    
                    
                } 
                /*else
                {
                    hideField2(interface);
                    hideField2(bond_details_checkBox); 
                    hideField2(bond_details_grid);
                    hideField2(vlan_checkBox);
                    hideField2(vlan_id);
                    hideField2(bridgename); 
                }    */          
            }
        }
    });

    var dummy_radio=new Ext.form.Radio({
        boxLabel:_('dummy_radio'),
        name:"dummy_radio",
        hideLabel: true,
        id:'dummy_radio',
        value:'dummy_radio',
        checked: false,
        hidden: true,
        width: 0
    });

    var nw_type=new Ext.form.RadioGroup({
        frame: true,
        id:"nw_type",
        title:_('RadioGroups'),
        fieldLabel: _('隔离/NAT'), //Isolated or NAT or VLAN
        labelWidth: 80,
        width: 1,
        bodyStyle: 'padding:0 10px 0;',
        name:'radio',
        //items: [hostonly_radio,nat_radio, nw_vlan]
        items: [dummy_radio]


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
                                Ext.MessageBox.alert("信息", "数据中心和服务器池级别的网络不能在这里编辑");
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
                         if(!address_space.getRawValue()){
                             Ext.MessageBox.alert( _("错误") ,_("地址空间是必须要输入的"));
                             return;
                        }
                        if(nat_radio.getValue()){
                             if(!nat_forward.getValue()){
                                 Ext.MessageBox.alert( _("错误") ,_("NAT转发是必须要输入的"));
                                 return;
                            }
                        }
//                        alert(address_space.getRawValue()+"---"+dhcprange.getRawValue());

                        if(dhcp_checkBox.checked == false)
                        {
                            dhcprange.setValue("");
                        }

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
                                var params="";
                                var url="";
                                params= sSiteId + op_level_main + sGroupId + sNodeId + "&nw_name="+network_name.getValue()+"&nw_desc="+network_description.getValue()+ "&nw_type="+ nw_type_str+
                                    "&nw_bridge="+bridgename.getValue()+"&nw_address_space="+address_space.getRawValue()+
                                    "&nw_dhcp_range="+dhcprange.getRawValue()+"&nat_radio="+nat_radio.getValue()+"&nw_nat_fwding="+nat_forward.getValue()+"&nw_gateway="+ gateway.getValue()+ "&nw_ip_address="+ip_address.getValue()+  "&nw_use_vlan="+vlan_checkBox.getValue()+ "&nw_vlan_id="+vlan_id.getValue()+ "&nw_isbonded="+bond_details_checkBox.getValue()+ "&nw_slaves="+slave_jdata+ "&interface="+interface.getValue(); 
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
                                    if(response.msg != "") {
                                        //Ext.MessageBox.alert("Success",response.msg);
                                    }
                                    closeThisWindow(nw_new_win_popup);
                                    //reloadVirtualNetworkDefList();
                                    DelayLoadingDefList(virtual_nw_grid);
                                    Ext.MessageBox.alert("成功","任务已经成功提交.");

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

//             },{
//                 width: 420,
//                 layout:'form',
//                 items:[nw_type]
            },{
                width: 110,
                layout:'form',
                items:[nw_type]
            },{
                width: 125,
//                layout:'form',
                items:[hostonly_radio]
            },{
                width: 125,
//                layout:'form',
                items:[nat_radio]
//             },{
//                 width: 80,
//                 layout:'form',
//                 items:[nw_vlan]
            },{
                width: 420,
                layout:'form',
                items:[lb3]
            },{
                width: 420,
                layout:'form',
                items:[interface]
            },{               
                width: 105,
                layout:'form',
                items:[bond_details_checkBox]
            },{
                width: 190,
                layout:'form',
                border: true,
                items:[bond_details_grid]
            },{
                width: 105,
                layout:'form',
                items:[vlan_checkBox]
            },{
                width: 200,
                layout:'form',
                labelWidth:20,
                items:[vlan_id]
//             },{
//                width: 420,
//                layout:'form',
//                items:[bridgename]
           
           },{
                width: 420,
                layout:'form',
                items:[address_space]
            },{
                width: 420,
                layout:'form',
                items:[gateway]
            },{
                width: 400,
                layout:'form',
                items:[ip_address]
            },{
                width: 420,
//                layout:'form',
                items:[dhcp_checkBox]
            },{
                width: 420,
                layout:'form',
                bodyStyle: 'padding: 0px 0px 0px 20px',
                labelWidth:80,
                items:[dhcprange]
            },{
               width: 420,
               layout:'form',
               items:[nat_forward]
           }
            ,{
                width: 420,
                layout:'form',
                items:[bridgename]
            },
            {
                width: 400,
                layout:'form',
                items:[lb4]
            }
        ]
    });

    //Start - From existing definitions
    var new_def_radio=new Ext.form.Radio({
        boxLabel: _('定义新的网络'),
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
        {header: _("详情"), width: 225, sortable: false, dataIndex: 'definition'},
        {header: _("说明"), width: 100, sortable: false, dataIndex: 'description'},
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
        //height:530,
        items:[virtual_nw_det_fldset]
    });

    nw_def_form = new Ext.FormPanel({
        frame:false,
        width:'100%',
        height:335,
        items:[dc_radio_panel,existing_nw_def_form,virtual_nw_def_form],
        bbar:[{xtype: 'tbfill'},virt_save_button,'-',virt_cancel_button]
    });

    //nat_forward.getEl().up('.x-form-item').setDisplayed(true);
    if(mode=="NEW"){
        bridgename.setValue(response.bridge.bridge);       

        if(node.attributes.nodetype == 'SERVER_POOL'){
            dc_radio_panel.setVisible(true);
            existing_nw_def_form.setVisible(true);
            virtual_nw_def_form.setVisible(false);
        } else {
            dc_radio_panel.setVisible(false);
            existing_nw_def_form.setVisible(false);
            virtual_nw_def_form.setVisible(true);
            //nw_def_form.height = 530;
        }

    }
    if(mode=="EDIT"){
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
        network_name.setValue(network.name);
        network_description.setValue(network.description);
        address_space.setValue(network.nw_ipv4_info_ip_network);
        dhcprange.setValue(network.dhcp_range_value);
        if(network.dhcp_range_value) {
            dhcp_checkBox.checked = true;
        }else {
            dhcp_checkBox.checked = false;
        }
        bridgename.setValue(network.nw_bridge_info_name);

        vlan_checkBox.setValue(network.use_vlan);
        vlan_id.setValue(network.vlan_id);
        gateway.setValue(network.gateway);
        ip_address.setValue(network.ip_address);
        bond_details_checkBox.setValue(network.is_bonded);

        nw_type.disable();
        hostonly_radio.disable();
        nw_vlan.disable();
        nat_radio.disable();
        interface.disable();
        bond_details_checkBox.disable();
        bond_details_grid.disable();
        vlan_checkBox.disable();
        vlan_id.disable();
        gateway.disable();
        ip_address.disable();
        address_space.disable();
        nat_forward.disable();
        dhcprange.disable();
        bridgename.disable();
        lb3.disable();
        lb4.disable();
        
//         if (network.nw_type== "VLAN_NW")
//         {
//             nw_vlan.setValue(true);
//             nat_radio.setValue(false);
//             hostonly_radio.setValue(false);
//         }
//         else
//         {
// 
//             
//             if(network.nw_nat_forward){
//                 nw_vlan.setValue(false);
//                 nat_radio.setValue(true);
//                 hostonly_radio.setValue(false);
//     //            nat_forward.setValue(network.nw_nat_info_interface);
//             }
//             else
//             {
//                 nw_vlan.setValue(false);
//                 nat_radio.setValue(false);
//                 hostonly_radio.setValue(true);
// 
//             }
//         }

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


function hideField2(field)
{
//field.disable();// for validation
field.hide();
field.getEl().up('.x-form-item').setDisplayed(false); // hide label
}

function showField2(field)
{
//field.enable();
field.show();
field.getEl().up('.x-form-item').setDisplayed(true);// show label
}
