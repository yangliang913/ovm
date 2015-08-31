/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
function CloudNetworkDefinition(vdc_id, mode, network_rec, windowid_csd)
{
    var cloud_network_def_form;
	
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

    node_id="node_id="+"";
    var nat_forward_store= new Ext.data.JsonStore({
        url: '/network/get_nw_nat_fwding_map?'+node_id,
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
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    nat_forward_store.load();
    var nat_forward=new Ext.form.ComboBox({
        store:nat_forward_store,
        fieldLabel: _('NAT转发'),
        hideLabel: true,
        triggerAction:'all',
        emptyText :"",
        displayField:'name',
        valueField:'value',
        width: 150,
        allowBlank: false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'forward',
        id:'nat_forward',
        mode:'local'
    });
   var nat_forward_lbl=new Ext.form.Label({
         html:'<div style>NAT Forwarding</div>'
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
                Ext.MessageBox.alert(_("错误"),store_response.msg);
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
        allowBlank: true,
        typeAhead: true,
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
                    addressspace_ajax(value1,dhcprange);
                },
                 select:function(combo,record,index){
                    var value2="";
                    value2=record.get('value');
                    addressspace_ajax(value2,dhcprange);
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
function addressspace_ajax(value,dhcprange){
    var url="/network/nw_address_changed?ip_value="+value;
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                dhcprange.setValue(response.range.range);
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });}


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
                    //if(isolation_fldset.findById('nat_forward')){
                        //nat_forward_lbl.show();
                        //nat_forward.show();
//                        nat_forward.getEl().up('.x-form-item').setDisplayed(true);
                    //}
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
        fieldLabel: _('隔离或转发'),
        labelWidth: 80,
        width: 300,
        bodyStyle: 'padding:0 10px 0;',
        name:'radio',
        items: [hostonly_radio,nat_radio]

    });


if(mode=="EDIT"){
        if (cloud_network_grid.getSelectionModel().getSelected() != undefined) {
            if(nat_radio.validate()){
                nat_forward.hide();
                nat_forward_lbl.hide();
            }
            network_name.value = network_rec.get('name');
	    network_description.value = network_rec.get('description');
            address_space.value = network_rec.get('address');
            dhcprange.value = network_rec.get('range');
            nat_forward.value = network_rec.get('nat');

            
        }
	network_name.disable();
	address_space.disable();
	dhcprange.disable();
        nat_forward.disable();
	dhcp_checkBox.disable();
	nw_type.disable();
    } 






    var save_button=new Ext.Button({
            name: 'ok',
            id: 'ok',
             text:_("保存"),
            icon:'icons/accept.png',
            cls:'x-btn-text-icon',
            listeners: {
                    click: function(btn) {
                      
                       
                        if(!network_name.getValue()){
                             Ext.MessageBox.alert( _("错误") ,_("网络名称必须输入"));
                             return;
                        }
                        if(!network_description.getValue()){
                             Ext.MessageBox.alert( _("错误") ,_("网络说明必须输入"));
                             return;
                        }
                        if(mode=="NEW"){
				
                                var params="";
                                var url="";
				vdc_id="vdc_id="+vdc_id;
                                params= vdc_id+ "&nw_name="+network_name.getValue()+"&nw_desc="+network_description.getValue()+"&nw_address_space="+address_space.getRawValue()+
                                    "&nw_dhcp_range="+dhcprange.getRawValue()+"&nw_nat_fwding="+nat_radio.getValue();
				
                                url="/cloud_network/create_network?"+params;
				wait_msg=_('正在创建网络...')
                   
                        }else{
                            if (cloud_network_grid.getSelectionModel().getSelected() != undefined) {
                               	    net_rec = cloud_network_grid.getSelectionModel().getSelected();
	                            nw_id = net_rec.get('id');
				    network_name=network_name.getValue();	
				    nw_def_id=net_rec.get('nw_def_id');	
	                            network_desc = network_description.getValue();
	                            acc_id = net_rec.get("account_id");
	                            
    
                            url='/cloud_network/edit_network?vdc_id=' + vdc_id + '&acc_id=' + acc_id +  '&nw_id=' + nw_id + '&nw_def_id=' + nw_def_id + '&nw_name=' + network_name + '&desc=' + network_desc;
                            wait_msg = _('正在更新网络...');
                            success_msg = _("网络" + network_name + " 更新成功.");
                        	}
                        }
			
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
			
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
					
                                    var task_id = response.task_id;
                                    var wait_time = 3000;
                                    wait_for_nw_create_task(task_id,wait_time, mode,wait_msg, vdc_id,network_name, windowid_csd);
                                }else{                                    
                                    Ext.MessageBox.alert(_("失败"),response.msg);
                                }
                            },
                            failure: function(xhr){                                    
                                Ext.MessageBox.alert( _("失败") , xhr.statusText);
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
                        closeWindow( windowid_csd);
                      
                }
                }
            });
    
   var  Address_Specification_fldset=new Ext.form.FieldSet({
        title:_('地址规范'),
        collapsible: false,
        autoHeight:true,
        width:395,
        labelSeparator: ' ',
        labelWidth:100,
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
                layout:'form',
                bodyStyle: 'padding:0px 0px 0px 8px;',
                items:[dhcp_checkBox]
            },
               {
                width: 420,
                layout:'form',
                 bodyStyle: 'padding:0px 0px 0px 20px;',
                labelWidth:80,
                items:[dhcprange]
            }

        ]
                

    });

    if(mode == 'NEW'){
        Address_Specification_fldset.hide();
    }else{
        //Address_Specification_fldset.show();
        //Address_Specification_fldset.disable();
    }

   var isolation_fldset = new Ext.form.FieldSet({
        title:_('隔离'),
        collapsible: false,
        autoHeight:true,
        width:360,
        labelSeparator: ' ',
        labelWidth:100,
	layout:'column',
        items:[
            {
                width: 110,
                layout:'form',
                bodyStyle: 'padding:0px 0px 0px 8px;',
                items:[hostonly_radio]
            },{
                width: 160,
                layout:'form',
                bodyStyle: 'padding:0px 0px 0px 8px;',
                items:[nat_radio]
            },
            {
                width: 120,
                layout:'form',
                bodyStyle: 'padding:0px 0px 0px 10px;',
                items:[nat_forward_lbl]
                
               
            }
            ,{
                width: 210,
                layout:'form',
                bodyStyle: 'padding:0px 0px 0px 0px;',
                items:[nat_forward]
//                labelWidth:84
               
            }
        ]


    });
   if(mode=='EDIT'){
       Address_Specification_fldset.hide();
       nat_radio.disable();
       hostonly_radio.disable();
       if(nat_forward.value){
            nat_radio.setValue(true);         
       }
       else{
            hostonly_radio.setValue(true);
       }
   }
   var  cloud_nw_det_fldset=new Ext.form.FieldSet({
        title: _('指定虚拟网络详情'),
        collapsible: false,
        autoHeight:true,
        width:380,
        bodyStyle: 'padding:0px 0px 8px 0px;',
        labelSeparator: ' ',
        labelWidth:100,
        layout:'column',
        items: [
            {
                width: 360,
                layout:'form',
                items:[network_name]
            },{
                width: 360,
                layout:'form',
                bodyStyle: 'padding:0px 0px 4px 0px;',
                items:[network_description]
            },isolation_fldset,Address_Specification_fldset
        ]
    });
cloud_network_def_form = new Ext.Panel({
        frame:true,
        id:'virtual_nw_def_form',
        width:'100%',
	items:[cloud_nw_det_fldset]
    });

var nw_def_form = new Ext.FormPanel({
        frame:false,
        width:'100%',
        height:196,
        items:[cloud_network_def_form],
        bbar:[{xtype: 'tbfill'},save_button,'-',virt_cancel_button]
    });
return nw_def_form;
}
function wait_for_nw_create_task(task_id, wait_time, mode, msg, vdc_id, nw_name, windowid){
    var url = '/cloud_network/wait_for_task?task_id=' + task_id + '&wait_time=' + wait_time;
    Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: msg,
        width:300,
        wait:true,
        waitConfig: {
            interval:3000
        }
    });

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
               reloadCloudNetworkDefList();
		if(mode=="NEW")
		{
                	Ext.MessageBox.alert("成功", "网络" + nw_name.getValue() + "创建成功.");
			closeWindow(windowid);
		}
		else
		{
			Ext.MessageBox.alert("成功", "网络" + nw_name + "更新成功.");
			closeWindow(windowid);
		}
            }else{
                Ext.MessageBox.alert(_("失败"), response.msg);
		closeWindow(windowid);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
	    closeWindow(windowid);
        }
    });
}
