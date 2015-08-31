/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var form_height = 446;//200
var vlan_id_pool_def_form;
var nw_def_title;

function VLANIDPoolDef(node, mode, pool_rec, p_windowid) {
    var vlan_id_pool_id="";
    if(node.attributes.nodetype == 'DATA_CENTER'){
        sSiteId = "site_id=" + node.attributes.id;
    }
    
    if(mode == "NEW") {
        nw_def_title = "定义";
        sSelectedDefId = "";
    } else if (mode == "EDIT") {
        nw_def_title = "定义";
        sSelectedDefId = "&pool_id=" + pool_rec.get('id');
    }

    var tf_name=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'tf_namename',
        id: 'tf_name',
        width: 200,
        allowBlank:false
    });
    var tf_description=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'tf_description',
        width: 200,
        id: 'tf_description'
    });
    var tf_range=new Ext.form.TextField({
        fieldLabel: _('VLAN ID范围'),
        name: 'vlanid_range',
        width: 200,
        id: 'vlanid_range'
    });
    var lbl_range_ex = new Ext.form.Label({
        html:'<table><tr><td width="100"></td><td width="100" align="left">e.g., 100-200</td></tr></table>'
    });

    var lbl_interface_tip = new Ext.form.Label({
        html:'<table><tr><td width="100"></td><td width="230" align="left">提示：指定物理接口上将创建的VLAN.</td></tr></table>'
    });


    var lbl_cidr = new Ext.form.Label({
        html:'<table><tr><td width="102"></td><td width="100"></td></tr></table>'
    });

    var lbl_hosts = new Ext.form.Label({
        html:'<table><tr><td width="102"></td><td width="100"></td></tr></table>'
    });

    var header_text = "这代表VLAN ID池的详细信息。在创建VLAN ID池前，建议你详细规划业务模型.";
    var lbl_header = new Ext.form.Label({
        html:'<div style="" class="labelheading">' + _(header_text) + '</div><br/>'
    });

    var IP_network_detail_text="指定IP网络的详细信息。每个VLAN ID将用于指定的CIDR子网.";  

    var lbl_IP_network_detail_header = new Ext.form.Label({
        html:'<div style="" class="labelheading">' + _(IP_network_detail_text) + '</div><br/>'
    });

 
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

    var cmb_interface=new Ext.form.ComboBox({
        store:default_interfaces_store,
        fieldLabel: _('物理接口'),
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
        name:'cmb_interface',
        id:'cmb_interface',
        mode:'local',
        listeners:{
                blur:function(combo) {
                }
         }
    });


    var cidr_store = new Ext.data.JsonStore({
        url: '/network/get_default_cidr',
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

    cidr_store.load();

    var cmb_cidr=new Ext.form.ComboBox({
        store:cidr_store,
        fieldLabel: _('CIDR'),
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
        name:'cmb_cidr',
        id:'cmb_cidr',
        mode:'local',
        listeners:{
                blur:function(combo) {
                }
         }
    });


    var num_host_store = new Ext.data.JsonStore({
        url: '/network/get_num_hosts',
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
                Ext.MessageBox.alert(_("Error: Interface"),store_response.msg);
            }
        }
    });

    num_host_store.load();

    var cmb_num_hosts=new Ext.form.ComboBox({
        store:num_host_store,
        fieldLabel: _('每个网络的主机'),
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
        name:'cmb_num_hosts',
        id:'cmb_num_hosts',
        mode:'local',
        listeners:{
                blur:function(combo) {
                }
         }
    });


   var  ip_network_details_fldset=new Ext.form.FieldSet({
        title:_('IP网络详情'),
        collapsible: false,
        autoHeight:true,
        width:406,
        labelSeparator: '',
//        labelWidth:100,
        layout:'column',
        items:[
               {
                    width:416,
                    items:[lbl_IP_network_detail_header]
                },
                {
                	width: 416,
	                layout:'form',
                    //bodyStyle: 'padding:0px 0px 0px 0px;',
                    labelWidth:86,
        	        items:[cmb_cidr, lbl_cidr]
            },{
                width: 416,
                layout:'form',
                //bodyStyle: 'padding:0px 18px 0px 0px;',
                labelWidth:86,
                items:[cmb_num_hosts, lbl_hosts]
            }
        ]
    })


    var save_button = new Ext.Button({
        name: 'save',
        id: 'save',
        text:("保存"),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var pool_name = tf_name.getValue();
                var desc = tf_description.getValue();
                var range = tf_range.getValue();
                var interface = cmb_interface.getValue();
                var sp_ids = get_selected_sp_list();
                var cidr = cmb_cidr.getRawValue();
                var num_hosts = cmb_num_hosts.getRawValue();

                if (!pool_name || !interface || !cidr || !num_hosts){
                    Ext.MessageBox.alert(_('错误'), _('请用适当的值填充.'));
                    return;
                }

                if (!validate_vlan_range(range)){
                    Ext.MessageBox.alert(_('错误'), _('请输入一个有效的的范围, e.g.100-200, 范围的参数不能超过4094.'));
                    return;
                }


                var query_string = sSiteId + '&name=' + pool_name + '&desc=' + desc + '&range=' + range + '&interface=' + interface + '&sp_ids=' + sp_ids + '&cidr=' + cidr + '&num_hosts=' + num_hosts;

                var url='/network/add_vlan_id_pool?' + query_string;
                var msg=_('正在添加VLAN ID池...');
                if(mode=='EDIT'){
                    vlan_id_pool_id = pool_rec.get('id');
                    query_string = sSiteId + '&vlan_id_pool_id=' + vlan_id_pool_id + '&desc=' + desc + '&range=' + range + '&sp_ids=' + sp_ids + '&cidr=' + cidr + '&num_hosts=' + num_hosts + '&name=' + pool_name;
                    var url='/network/edit_vlan_id_pool?' + query_string;
                    var msg=_('正在更新VLAN ID 池...');
                }
                vlan_id_pool_def_form.getForm().submit({
                    url:url,
                    success: function(form, action) {
                        DelayLoadingVLANIDPoolList(vlanidpool_grid);
                        Ext.MessageBox.alert("Success", action.result.msg);
                        closeWindow(p_windowid);
                    },
                    failure: function(form, action) {
                        Ext.Msg.alert(_("Failure"), action.result.msg );
                    },

                    waitMsg:msg
                });
            }//end of function
        } //end of listeners
    });

    var cancel_button = new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:("取消"),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow(p_windowid);
            }
        }
    });

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
            get_def_form();
        }
    }

    function get_def_form() {
        vlan_id_pool_def_form = new Ext.FormPanel({
            title: _(nw_def_title),
            labelWidth:100,//120
            frame:true,
            border:0,
            bodyStyle:'padding:0px 0px 0px 0px',
            labelAlign:"left" ,
            width:418,
            height:form_height,//470
            labelSeparator: ' ',
            items:[tf_name, tf_description, tf_range, lbl_range_ex, cmb_interface, lbl_interface_tip, ip_network_details_fldset]
        });
        return vlan_id_pool_def_form;
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
    var url_sp_list = '/network/get_sp_list?' + sSiteId + sSelectedDefId + "&pool_tag=VLAN_ID_POOL";
    var sp_list_store = new Ext.data.JsonStore({
        url: url_sp_list,
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
        height:220,
        autoExpandColumn:2,
        enableHdMenu:false
    });

    var tabs = new Ext.TabPanel({
        width:421,//418
        height:form_height, //470
        activeTab: 0
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

    if(mode=="EDIT"){
        vlan_id_pool_id=pool_rec.get('id');
        tf_name.setValue(pool_rec.get('name'));
        tf_description.setValue(pool_rec.get('description'));
        tf_range.setValue(pool_rec.get('range'));
        cmb_interface.setValue(pool_rec.get('interface'));
        cmb_cidr.setValue(pool_rec.get('cidr'));
        cmb_num_hosts.setValue(pool_rec.get('num_hosts'));
//        alert("-----"+pool_rec.get('cidr') +"====="+pool_rec.get('num_hosts'));
//        tf_name.disable();
        cmb_interface.disable();
        cmb_cidr.disable();
        cmb_num_hosts.disable();

    }

    var return_form;
    if(node.attributes.nodetype == 'DATA_CENTER'){
        return_form = vlan_id_pool_def_form;
        if(mode == "NEW" || mode == "EDIT") {
            addDefTabs(tabs,[vlan_id_pool_def_form, serverpoolPanel]);
            return_form = tabs;
        }
    }

    var main_form = new Ext.Panel({
        frame:true,
        bodyStyle:'padding:0px 0px 0px 0px',
        cls: 'whitebackground',
        width:434,
        height:form_height,
        items:[lbl_header, tabs],
        bbar:[{xtype: 'tbfill'},
            save_button,
            '-',
            cancel_button
        ]
    });
    return_form = main_form;
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

        Ext.get('names').setVisible(false);
        Ext.get('names').up('.x-form-item').setDisplayed(false);
        vlan_id_pool_def_form.findById('names').allowBlank=true;
}
