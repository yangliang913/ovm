/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var tmpl_id=""
var rule_deleted_record_list="";
var rule_record_list="";
var cloud_strg_grid_vm_level; //we are accessing this variable on CloudStorageAttachAtVMLevel.js
var cloud_account_id="";
var cloud_region_id="";
var cloud_zone_id="";
var cloud_instance_id="";
var storage_panel=null;
var vm_id, vm_name;
var sec_group_name = "";
var sec_group_desc = "";
var key_pair_name = "";
var public_ip_panel="";
var nws_panel3="";
var panel3="";
function CloudVMConfig(node, mode, vmfolder_node){
    var vdcid = "";
    if(mode == "PROVISION") {
        //node will be vdc node
        vdcid = node.attributes.id;
    } else {
        //node will be vm node
        vdcid = node.parentNode.parentNode.id
    }
    var url = "/cloud/get_cp_feature_set?vdc_id="+vdcid;
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                CloudVMConfigSettings(node, mode, vmfolder_node, response.info)
            }else{
                Ext.MessageBox.alert(_("失败"),_("无法加载供应商."));
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}

function CloudVMConfigSettings(node, mode, vmfolder_node, cp_feature){

    var vdcid;
    var vm_info;
    var vmfolderid;
    if(mode == "PROVISION") {
        vdcid = node.attributes.id;
        vmfolderid=vmfolder_node.attributes.id;
        vm_id = "";
        vm_name = "";
        win_title = "新建VM";
    } else {
        vm_id = node.attributes.id;
        vm_name = node.attributes.text;
        vdcid = node.parentNode.parentNode.id
        vmfolderid=node.attributes.vmfolderid;
        win_title = "编辑VM";
        //get data from database to display on wizard for this VM.
        vm_info = new Ext.data.JsonStore({
            url: "/cloud/cloudvm_info?node_id=" + vm_id + "&type=EDIT_VM_INFO",
            root: 'info',
            fields: ['id', 'name', 'template_id', 'template', 'region_id', 'region', 'account_id', 'account', 'zone_id', 'zone', 'category', 'service_type', 'instance_id', 'kernel_id', 'ramdisk_id', 'key_pair_name', 'sec_group_name', 'sec_group_desc', 'ip_name'],
            successProperty:'success',
            listeners:{
                load:function(my_store, records, options){
                    var rec=my_store.getAt(0);
                    cloud_account_id = rec.get("account_id");
                    cloud_region_id = rec.get("region_id");
                    cloud_zone_id = rec.get("zone_id");
                    cloud_instance_id = rec.get("instance_id");
                    tmpl_id = rec.get("template_id");
                    //vm_id = rec.get("id");
                    //vm_name = rec.get("name");

                    //set values in fields
                    Ext.getCmp("name_textbox").setValue(rec.get("name"));
                    Ext.getCmp("account").setValue(rec.get("account"));
                    
                    Ext.getCmp("region_general").setValue(rec.get("region"));
                    Ext.getCmp("zones_type").setValue(rec.get("zone"));
                    Ext.getCmp("cpu_textbox").setValue(rec.json.cpu);
                    Ext.getCmp("mem_textbox").setValue(rec.json.memory);
                    
                    //alert(rec.get("category"));
                    //Ext.getCmp("category_type").setValue(rec.get("category"));
                    //alert(rec.get("service_type"));
                    Ext.getCmp("serviceoffering").setValue(rec.get("service_type"));
                    //alert(rec.get("template"));
                    Ext.getCmp("lbl").text = rec.get("template");
                    //Ext.getCmp("lbl").setValue(rec.get("template"));
                    Ext.getCmp("lbl").show()
                    set_template_name(rec.get("template"));
                    
                    Ext.getCmp("kernel_type").setValue(rec.get("kernel_id"));
                    Ext.getCmp("ramdisk_type").setValue(rec.get("ramdisk_id"));

                    sec_group_name = rec.get("sec_group_name");
                    sec_group_desc = rec.get("sec_group_desc");
                    key_pair_name = rec.get("key_pair_name");
                    ip_name = rec.get("ip_name");
                    Ext.getCmp("key_pair").setValue(key_pair_name);
                    var sec_group = Ext.getCmp("security_group_grid");
                    if(ip_name) {
                        Ext.getCmp("publicIP_pair").setValue(ip_name);
                        Ext.getCmp("none").setValue(false);
                        Ext.getCmp("unassigned").setValue(true);
                    }
                    

                    var sg_store = new Ext.data.JsonStore({
                        root: 'rows',
                        fields: ['id', 'name', 'description', 'region', 'region_id', 'account_name', 'account_id', 'record_new', 'record_modified', 'rules_store', 'is_attached'],
                        autoLoad: true,
                        data: {rows: [{'id':'', 'name':sec_group_name, 'description':sec_group_desc, 'region':'', 'region_id':'', 'account_name':'', 'account_id':'', 'record_new':'', 'record_modified':'', 'rules_store':'', 'is_attached':''}]}
                    });

                    sec_group.store = sg_store;
                }
            }
        });
        vm_info.load();
    }

    var cloud_provision_treePanel= new Ext.tree.TreePanel({
        region:'west',
        width:180,
        rootVisible:false,
        border: false,
        lines : false,
        id:'vdc_treePanel',
        cls:'leftnav_treePanel',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        listeners: {
            click: function(item) {
                var id=item.id;
                process_cloud_panel(cloud_card_panel,cloud_provision_treePanel,id.substr(4,id.length),"treepanel");
            }
        }
    });

    // root node of tree view
    var rootNode = new Ext.tree.TreeNode({
        text	: 'Root节点',
        draggable: false,
        id		: 'rootnode',
        listeners: {
            expand : function(btn) {
                cloud_provision_treePanel.getNodeById("node0").select();
            }
        }
    });
    var general_Node = new Ext.tree.TreeNode({
        text: _('常规'),
        draggable: false,
        id: "node0",
        icon:'icons/vm-general.png',
        nodeid: "general",
        leaf:false,
        allowDrop : false
       // cls:"labelcolor"
    });

    var Storage_Node = new Ext.tree.TreeNode({
        text: _('存储'),
        draggable: false,
        id: "node1",
        nodeid: "storage",
        icon:'icons/vm-storage.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });


    var Rootdevice_Node = new Ext.tree.TreeNode({
        text: _('Root设备'),
        draggable: false,
        id: "node2",
        nodeid: "storage",
        icon:'icons/vm-boot-param.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

    var Network_Node = new Ext.tree.TreeNode({
        text: _('网络'),
        draggable: false,
        id: "node3",
        nodeid: "network",
        icon:'icons/vm-network.png',
        leaf:false,
        allowDrop : false,
        listeners: {
            click: function(item) {
            }
        }
    });

    var Template_Node = new Ext.tree.TreeNode({
        text: _('模板'),
        draggable: false,
        id: "node4",
        nodeid: "template",
        icon:'icons/templates-parameters.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });


    var general_panel=create_generalcloud_panel(vdcid, cp_feature, mode);
    var network_panel=create_networkcloud_panel(vdcid, mode, cp_feature, general_panel, node);
    var storage_panel=create_storagecloud_panel(vdcid, vm_info, mode, cp_feature);
    var rootdevice_panel=create_rootdevicecloud_panel(vdcid);



    // card panel for all panels


    var button_prev=new Ext.Button({
        id: 'move-prev',
        //text: _('Prev'),
        disabled: true,
        icon:'icons/2left.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
//                closeWindow();
                process_cloud_panel(cloud_card_panel,cloud_provision_treePanel,-1);
//                cloud_card_panel.activeItem =0;
            }
        }
    });
    var button_next=new Ext.Button({
        id: 'move-next',
        //text: _('Next'),
        icon:'icons/2right.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
//                closeWindow();
                process_cloud_panel(cloud_card_panel,cloud_provision_treePanel,1);
//                cloud_card_panel.activeItem =0
            }
        }
    });

    var url =""

    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        hidden:false, //((mode=="PROVISION")? false:true)
        listeners: {
            click: function(btn) {
            var vdc_private_nw_id = '';
            var vdc_predef_nw_ids = '';
            var private_nw_ids_for_vm='';
            if(is_feature_enabled(cp_feature,stackone.constants.CF_VDC_PRE_DEFINED_NW)){
                    var selected_temps = Ext.getCmp('predef_grid').getSelections();
                    var vdc_predef_nw_ids = new Array();
                    for(var j=0; j<selected_temps.length; j++){
                          vdc_predef_nw_ids.push((selected_temps[j].json.id));
                    }
                    vdc_predef_nw_ids = Ext.util.JSON.encode(vdc_predef_nw_ids);
            }

            if(is_feature_enabled(cp_feature,stackone.constants.CF_VDC_PRIVATE_NW_POOL)){
                    var ip_pool_combo_count = Ext.getCmp('ip_pool_combo').store.data.length;
                    if( ip_pool_combo_count> 1){
                        if(Ext.getCmp('ip_pool_combo').getValue() == '' && Ext.getCmp('unassigned').getValue()=="true"){
                            Ext.MessageBox.alert('提示','请选择一个私有网络');
                            return false;
                        }
                        else{
                        
                            vdc_private_nw_id = Ext.getCmp('ip_pool_combo').getValue();                          
                        }
                    }else if (ip_pool_combo_count== 1  && Ext.getCmp('unassigned').getValue()=="true"){
                              vdc_private_nw_id = Ext.getCmp('ip_pool_combo').store.getAt(0).data.id ;  

                         }
                var selected_private_nw = Ext.getCmp('vdc_private_grid').getSelections();
                    var private_nw_ids_for_vm = new Array();
                    for(var j=0; j<selected_private_nw.length; j++){
                          private_nw_ids_for_vm.push((selected_private_nw[j].json.id));
                    }
                    private_nw_ids_for_vm = Ext.util.JSON.encode(private_nw_ids_for_vm);
                    
             }

                var vm_name=Ext.getCmp("name_textbox").getValue();
                if(!vm_name){
                    Ext.MessageBox.alert(_("失败"),"请输入一个虚拟机的名称");
                    return;
                }
                if(!checkSpecialCharacters(vm_name, "虚拟机名称")){
                    return;
                }

                var serviceoffer=Ext.getCmp("serviceoffering").getValue();

                var zone_id=Ext.getCmp("zones_type").getValue();

                var ramdisktype=Ext.getCmp("ramdisk_type").getValue();

                if (ramdisktype==''){

                    ramdisktype='0'
                }

                var kerneltype=Ext.getCmp("kernel_type").getValue()

                if (kerneltype==''){

                    kerneltype='0'
                }

//                alert(ramdisktype+kerneltype);


                var accountid=Ext.getCmp("account").getValue();
                var regionid=Ext.getCmp("region_general").getValue();
                var vmname=Ext.getCmp("name_textbox").getValue();
                var tmplid=tmpl_id;

                var keypair;

                if (Ext.getCmp("key_pair").getValue()!=""){
                    keypair={}
                    keypair.id=Ext.getCmp("key_pair").getValue();
                    keypair.name=Ext.getCmp("key_pair").getRawValue();
                }

                var sec_grps="[";
                var sec_store=Ext.getCmp("security_group_grid").getStore();
                var rec_count=sec_store.getCount();
                for(var i=0;i<rec_count;i++){
                    var rec=sec_store.getAt(i);
                    if(rec.get('is_attached')){
                        var sec_grp="{";
                        sec_grp+="id:'"+rec.get('id')+"',";
                        sec_grp+="name:'"+rec.get('name')+"',";
                        sec_grp+="}";
                        if (i!=sec_store.getCount()-1)
                            sec_grp+=","

                        sec_grps+=sec_grp;
                    }
                }
                sec_grps+="]";
                var sec_g=eval("("+sec_grps+")");

                var public_ip;

                if(Ext.getCmp("unassigned").getValue()){
                    if(Ext.getCmp("publicIP_pair").getValue()==""){
                        Ext.MessageBox.alert(_("失败"),"请选择一个IP");
                        return;
                    }
                    public_ip={}
                    public_ip.id=Ext.getCmp("publicIP_pair").getValue();
                    public_ip.name=Ext.getCmp("publicIP_pair").getRawValue();
                }

                var json_data=Ext.util.JSON.encode({
                    "sec_grps":sec_g,
                    "key_pair":keypair,
                    "public_ip":public_ip,
                    "vdc_predef_nw_ids":vdc_predef_nw_ids,
                    "vdc_private_nw_id":vdc_private_nw_id,
                    "private_nw_ids_for_vm":private_nw_ids_for_vm
                });

                
                	


//                alert("accountid====="+accountid+"regionid====="+regionid+"vmname==="+vmname+"tmplid"+tmplid+"\n\nzone_id=0"+zone_id
//                        +"ramdisktype======="+ramdisktype+"kerneltype============"+kerneltype)

                if (tmplid){
                            if(mode == "PROVISION") {
                                url="/cloud/savevmdetails_info?vdc_id="+vdcid+"&vmfolder_id="+vmfolderid+"&acc_id="+accountid+"&region_id="
                                            +regionid+"&tmpl_id="+tmplid+"&instance_type_id="+serviceoffer+"&name="+vmname+
                                            "&zone_id="+zone_id+"&ramdisk_id="+ramdisktype+"&kernel_id="+kerneltype+
                                            "&mode=" + mode + "&data="+json_data;
                                        
                            } else {
                                url="/cloud/savevmdetails_info?vdc_id="+vdcid+"&vmfolder_id="+vmfolderid+"&vm_id="+vm_id+"&acc_id="+accountid+"&region_id="
                                            +cloud_region_id+"&tmpl_id="+tmplid+"&instance_type_id="+serviceoffer+"&name="+vmname+
                                            "&zone_id="+cloud_zone_id+"&ramdisk_id="+ramdisktype+"&kernel_id="+kerneltype+ "&mode=" + mode + "&data="+json_data;
                            }

//                            url = url+tinyurl;

                            var mem_value = '';
                            var cpu_value = '';

                            if(Ext.getCmp('cpu_textbox').getValue()!= '')
                                cpu_value = Ext.getCmp('cpu_textbox').getValue();

                            url+='&cpu_value='+cpu_value;

                            if(Ext.getCmp('mem_textbox').getValue()!= '')
                                mem_value = Ext.getCmp('mem_textbox').getValue();

                            url+='&memory_value='+mem_value;
                          if(is_feature_enabled(cp_feature,stackone.constants.CF_MEM_VCPU)){
                                if (mem_value == '' || mem_value == undefined){
                                    Ext.MessageBox.alert('警告','内存不可以为空');
                                    return false;
                                }
                                if (cpu_value == '' || cpu_value == undefined){
                                    Ext.MessageBox.alert('警告','VCPUs不可以为空');
                                    return false;
                                }
                          }
                            var ajaxReq=ajaxRequest(url,0,"POST",true);
                            ajaxReq.request({
                                success: function(xhr) {
                                    var response=Ext.util.JSON.decode(xhr.responseText);
                                    if(response.success){
                                        Ext.MessageBox.alert(_("成功"),_("新建VM任务提交"));
                                        win.close()

                                    }else{
                                        Ext.MessageBox.alert(_("失败"),response.msg);
                                        }
                                },
                                failure: function(xhr){
                                    Ext.MessageBox.alert( _("失败") , xhr.statusText);
                                    }
                            });
                       }

                    else{
                        Ext.MessageBox.alert( _("失败") , "请选择一个模板");
                    }
                }

         }
    });


    var button_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:"取消", //((mode=="PROVISION")? _("Cancel"):_("Close"))
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                win.close()
            }
        }
     });

    var cloud_card_panel=new Ext.Panel({
        width:"100%",
        height:475,
        layout:"card",
        id:"cloud_card_panel",
        activeItem:0,
        cls: 'whitebackground',
        border:false,
        bbar:[
        {
            xtype: 'tbfill'
        },button_ok,button_cancel]
        ,items:[general_panel,network_panel, storage_panel]
    //
    });

    if(mode != "PROVISION") {
        general_panel.disable();
        network_panel.disable();
        storage_panel.disable();
    }
    
    /*if(mode == "PROVISION") {
        storage_panel.disable();
        network_panel.disable();
    }*/

    rootdevice_panel.disable();

    rootNode.appendChild(general_Node);
    rootNode.appendChild(Network_Node);
    if(is_feature_enabled(cp_feature,stackone.constants.CMS_VM_STORAGE) || mode != "PROVISION"){
        rootNode.appendChild(Storage_Node);
    }
//    rootNode.appendChild(Rootdevice_Node);

    var treeheading=new Ext.form.Label({
        html:'<br/><br/>'
    });

    var side_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:180,
        height:588,
        id:'side_panel',
        cls:'westPanel',
        items:[treeheading,cloud_provision_treePanel]

    });

    var right_panel=new Ext.Panel({
        id:"right_panel",
        width:448,
        height:600,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        bodyStyle:'padding:5px 5px 5px 5px'
//        items:[change_settings]
    });


    right_panel.add(cloud_card_panel);
    cloud_provision_treePanel.setRootNode(rootNode);


    var outerpanel=new Ext.FormPanel({
        width:900,
        height:480,
        autoEl: {},
        layout: 'column',
        items:[side_panel,right_panel]

    });


//    return outerpanel;


    var win=new Ext.Window({
        title:win_title,
        width: 645,
//        layout:'fit',
        height: 515,
        modal: true,
        resizable: false,
        closable:true
    });

    win.add(outerpanel);
    win.show();

}


function create_generalcloud_panel(vdc_id, cp_feature, mode){

    var name_textbox = new Ext.form.TextField({
        fieldLabel: '名称',
        name: 'name_textbox',
        id: 'name_textbox',
        width:300,
        labelSeparator:" ",
        allowBlank:true,
        enableKeyEvents:true,
        labelAlign:'left',
        listeners: {
            keyup: function(field) {

            }
        }
    });

    var accountcombo=create_account_dropdown(vdc_id,"provision");
    var account_id=accountcombo.getValue()



    var template_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="120"><b>模板</b><hr></div>'
    });

    var dummy_space=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    
    var mem_and_cpu_info_label = new Ext.form.Label({
    	html:'<div class="backgroundcolor" width="120"><b>内存和VCPU信息</b><hr></div>'
    });
    var mem_and_cpu_info_desc = new Ext.form.Label({
    	html:'<div class="backgroundcolor" width="120"><b>请选择模板</b><hr></div>'
    });
   
    
    var mem_textbox = new Ext.form.NumberField({
        fieldLabel: '内存(MB):',
        name: 'mem_textbox',
        id: 'mem_textbox',
        width:110,
        labelSeparator:" ",
        allowBlank:false,
        enableKeyEvents:true,
        labelAlign:'left',
        listeners: {
            keyup: function(field) {

            }
        }
    });
    var cpu_textbox = new Ext.form.NumberField({
        fieldLabel: 'VCPUs:',
        name: 'cpu_textbox',
        id: 'cpu_textbox',
        width:110,
        labelSeparator:" ",
        allowBlank:false,
        enableKeyEvents:true,
        labelAlign:'left',
        listeners: {
            keyup: function(field) {

            }
        }
    });
 

    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:80px"/>')
    });

    var dummy_space_panel2=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });

    var dummy_space_panel3=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });


    var dummy_space_panel4=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });

    var dummy_space_template=new Ext.form.Label({
        html:_('&nbsp;<div style="width:5px"/>')
    });

    var dummy_space_instance=new Ext.form.Label({
        html:_('&nbsp;<div style="width:5px"/>')
    });

    var dummy_space_advance=new Ext.form.Label({
        html:_('&nbsp;<div style="width:5px"/>')
    });
    var dummy_space7=new Ext.form.Label({
        html:_('&nbsp;<div style="width:5px"/>')
    });


    var select_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="120">请输入虚拟机详情</div>'
    });

    var selection_space=new Ext.form.Label({
        html:_('&nbsp;<div style="width:40px"/>')
    });

      var region_general_store =new Ext.data.JsonStore({
        url: "/cloud/get_regionforvdc?",
        root: 'info',
        fields: ['name','value'],
        successProperty:'success',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        listeners:{
            load:function(obj,opts,res,e){
                if(Region.getStore().getCount() != 0){
                    Region.setValue(Region.getStore().getAt(0).get('value'));
                    Region.fireEvent('select',Region,Region.getStore().getAt(i),0);
                }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });


    region_general_store.load({
        params:{
            vdcid : vdc_id
             }
    });


    var Region = new Ext.form.ComboBox({
        id: 'region_general',
        fieldLabel: _('区域'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择"),
        store:region_general_store,
        width:90,
        displayField:'name',
        labelAlign:'left',
        editable:false,
        valueField:'value',
        typeAhead: true,
//        minListWidth:50,
//        listWidth:100,
        labelSeparator:" ",
        mode:'local',
        forceSelection: true,
        selectOnFocus:true,
        listeners: {

                select: function(combo, record, index){

                     if(mode != "PROVISION") {
                        Ext.getCmp("panel3").disable();}else{Ext.getCmp("panel3").enable();} //network panel
//                   Ext.getCmp("panel2").enable();  //general panel
                    //Do not enable storage panel. It is only enabled in edit vm mode. Because while provisioning, we do not add/attach storage.
                   //Ext.getCmp("panel1").enable(); //storage panel

//                   if (zones_type.getValue () != null){
//                    zones_type.setValue("");
//                   }

                   zone_store.load({
                    params:{
                    region_id:combo.getValue(),
                    acc_id:accountcombo.getValue(),
                    vdc_id:vdc_id



                    }
                });

            	if (is_feature_enabled(cp_feature,stackone.constants.CF_KEY_PAIR))
                {
                    Ext.getCmp("key_pair").getStore().load({
                         params:{
                             vdc_id:vdc_id,
                             acc_id:accountcombo.getValue(),
                             region_id:combo.getValue(),
                             kp_type:"provision"
                            }
                        });
                }


            	if (is_feature_enabled(cp_feature,stackone.constants.CF_SEC_GRP))
                {
                    Ext.getCmp("security_group_grid").getStore().load({
                         params:{
                             vdc_id:vdc_id,
                             acc_id:accountcombo.getValue(),
                             region_id:combo.getValue(),
                             sec_type:"provision"
                            }
                        });
                }


            	if (is_feature_enabled(cp_feature,stackone.constants.CF_PUBLIC_IP))
                {
                     Ext.getCmp("publicIP_pair").getStore().load({
                         params:{
                             vdc_id:vdc_id,
                             acc_id:accountcombo.getValue(),
                             region_id:combo.getValue(),
                             pi_type:"provision"
                            }
                        });
                }

        }
      }
    });


    var zone_store =new Ext.data.JsonStore({
        url: "/cloud/get_all_zones?",
        root: 'rows',
        fields: ['name','id'],
        successProperty:'success',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
        }
        }
    });
         
    var zones_type = new Ext.form.ComboBox({
        id: 'zones_type',
        fieldLabel: _('可用Zone'),
        allowBlank:true,
        triggerAction:'all',
        emptyText :_("选择"),
        store:zone_store,
        width:100,
        displayField:'name',
        editable:false,
        valueField:'id',
        typeAhead: true,
//        minListWidth:50,
//        listWidth:100,
        labelSeparator:" ",
        mode:'local',
        labelAlign:'left',
        forceSelection: true,
        selectOnFocus:true,
        listeners: {
            select: function(combo, record, index){
                  
            }

             }

    });

    var category_store =new Ext.data.JsonStore({
        url: "/cloud/get_all_service_offering_categories?",
        root: 'rows',
        fields: ['name','value','default'],
        successProperty:'success',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        listeners:{
            load:function(obj,opts,res,e){
                for (var i=0;i<=category_type.getStore().getCount()-1;i++){
                    if(category_type.getStore().getAt(i).get('default')){
                        category_type.setValue(category_type.getStore().getAt(i).get('value'));
                    }
                    category_type.fireEvent('select',category_type,category_type.getStore().getAt(i),0);
            }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    var category_type = new Ext.form.ComboBox({
        id: 'category_type',
        fieldLabel: _('分类'),
        allowBlank:true,
        triggerAction:'all',
        emptyText :_("选择"),
        store:category_store,
        labelAlign:'left',
        width:100,
        displayField:'name',
        editable:false,
        valueField:'value',
        typeAhead: true,
//        minListWidth:50,
//        listWidth:100,
        labelSeparator:" ",
        mode:'local',
        forceSelection: true,
        selectOnFocus:true,
        listeners: {

                select: function(combo, record, index){
                    var category_id=combo.getValue();

                    //if (Ext.getCmp("serviceoffering").getValue()!= null){
                        //Ext.getCmp("serviceoffering").setValue("");
                    //}

                    Ext.getCmp("serviceoffering").getStore().load({
                        params:{
                            account_id:accountcombo.getValue(),
                            category_id:category_id,
                            vdc_id:vdc_id
                        }
                    });

             }

        }

    });

    var serviceofferings_store =new Ext.data.JsonStore({
        url: "/cloud/get_all_service_offerings?",
        root: 'rows',
        fields: ['name','value'],
        successProperty:'success',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

//    serviceofferings_store.load();

    var serviceoffering_type = new Ext.form.ComboBox({
        id: 'serviceoffering',
        fieldLabel: _('服务类型'),
        allowBlank:true,
        triggerAction:'all',
        emptyText :_("选择"),
        store:serviceofferings_store,
        width:100,
        displayField:'name',
        editable:false,
        valueField:'value',
        typeAhead: true,
        labelAlign:"left",
//        minListWidth:50,
//        listWidth:100,
        labelSeparator:" ",
        mode:'local',
        forceSelection: true,
        selectOnFocus:true,
        listeners: {

                select: function(combo, record, index){

                kernel_type_store.load({
                    params:{
                         regionid:Region.getValue(),
                         accountid:accountcombo.getValue(),
                         vdcid:vdc_id,
                         instance_type:combo.getValue(),
                         template_type:'kernel'
                    }
                });

                ramdisk_type_store.load({
                    params:{
                        regionid:Region.getValue(),
                         accountid:accountcombo.getValue(),
                         vdcid:vdc_id,
                         instance_type:combo.getValue(),
                         template_type:'ramdisk'
                    }
                });

                var sec_store=Ext.getCmp("security_group_grid").getStore();
                var rec_count=sec_store.getCount();
                if (rec_count > 0){
                Ext.getCmp("panel3").fireEvent('show',Ext.getCmp("panel3"));
                }
             }
        }

    });


    var template_selectbtn=new Ext.Button({
        tooltip:'Select Template',
        tooltipType : "title",
        icon:'icons/accept.png',
        labelAlign:'left',
        id: 'template_select',
        height:40,
        width:60,
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
            	
            	if (is_feature_enabled(cp_feature,stackone.constants.CF_REGION))	
                {   
	                if (Region.getValue() && accountcombo.getValue() && serviceoffering_type.getValue()){
	                    showWindow(_("选择模板"),700,460,show_templates(Region.getValue(),accountcombo.getValue(),serviceoffering_type.getValue(),vdc_id, cp_feature),null,false,true);
	                    Ext.MessageBox.show({
	                    title:_('请稍候...'),
	                    msg: _('请稍候...'),
	                    width:300,
	                    wait:true,
	                    waitConfig: {
	                        interval:200
	                    }
	                    });
	                }
	                else{
	                    Ext.MessageBox.alert( _("警告"),"请选择适当的帐户，区域和服务类型");
	                }
            	}else{
            		//For CMS IaaS
            		showWindow(_("选择模板"),600,460,show_templates('',accountcombo.getValue(),'',vdc_id, cp_feature),null,false,true);
                    Ext.MessageBox.show({
                    title:_('请稍候...'),
                    msg: _('请稍候...'),
                    width:300,
                    wait:true,
                    waitConfig: {
                        interval:200
                    }
                    });
            		
            	}   

            }
        }
    });

    var select_template=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="120">选择模板:&nbsp;</div>'
    });

    var panel_temp=new Ext.Panel({
        height:40,
        border:false,
        width: 380,
        labelAlign:"left" ,
        layout:'table',
        labelSeparator:' ',
        layoutConfig: {columns:4},
        id:"panel_temp",
        items: [
        {
            labelWidth: 220,
            layout:'form',
            border:false,
            items:[select_template]
        },
        {
            width: 10,
            layout:'form',
            border:false,
            items:[dummy_space]
        },
        {
            labelWidth: 120,
            layout:'form',
            border:false,
            items:[template_selectbtn]
        },
        {
            labelWidth: 10,
            layout:'form',
            border:false,
            items:[dummy_space_template]
        }]
    });


    var panel2=new Ext.Panel({
        height:90,
        border:false,
        width: 420,
        labelAlign:"left" ,
        layout:'form',
        labelSeparator:' ',
        id:"template_panel",
        items: [template_label,panel_temp]
    });

    var lbl=new Ext.form.Label({
        id:"lbl",
        html:'<div style="" class="labelheading"></div>'

    });
    var mem_and_cpu_panel=new Ext.Panel({
    	height:105,
        border:false,
        width: 420,
        labelAlign:"left" ,
        layout:'form',
        labelSeparator:' ',
        id:"mem_and_cpu_panel",
        layoutConfig: {columns:2},
//        tbar:[mem_and_cpu_info_label,{
//            xtype: 'tbfill'
//        }],
        items: [dummy_space7,mem_and_cpu_info_label,mem_textbox,cpu_textbox,dummy_space_template]
    	
    });
    
    panel2.add(lbl);
    panel2.doLayout();

    lbl.hide();

    var location_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="120"><b>Location</b><hr></div>'
    });


    var label1=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="120"><b>区域</b></div>'
    });


     var location_fieldset=new Ext.Panel({
        height:40,
        border:false,
        width: 410,
        labelAlign:"left" ,
        layout:'table',
        labelSeparator:' ',
        layoutConfig: {columns:3},
        id:"location_fieldset",
        items: [
        {
            id:"location_fieldset_region",
            labelWidth: 60,
            layout:'form',
            border:false,
            items:[Region]
        },
        {
            width: 10,
            layout:'form',
            border:false,
            items:[dummy_space_panel2]
        },
        {
            labelWidth:100,
            layout:'form',
            border:false,
            items:[zones_type]
        }
      ]
    });

     var instance_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="120"><b>实例类型</b><hr></div>'
    });

     var instance_fieldset=new Ext.Panel({
        height:40,
        border:false,
        width: 420,
        labelAlign:"left" ,
        layout:'table',
        labelSeparator:' ',
        layoutConfig: {columns:3},
        id:"instance_fieldset",
        items: [
        {
            labelWidth: 65,
            layout:'form',
            border:false,
            items:[category_type]
        },
        {
            width: 10,
            layout:'form',
            border:false,
            items:[dummy_space_panel3]
        },
        {
            labelWidth:85,
            layout:'form',
            border:false,
            items:[serviceoffering_type]
        }
      ]
    });

    var kernel_type_store =new Ext.data.JsonStore({
        url: "/cloud/get_kernel_ramdiskforaccount?",
        root: 'info',
        fields: ['image_id','id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    var kernel_type = new Ext.form.ComboBox({
        id: 'kernel_type',
        fieldLabel: _('内核'),
        allowBlank:true,
        triggerAction:'all',
        emptyText :_("选择"),
        store:kernel_type_store,
        width:120,
//        listWidth:100,
        displayField:'image_id',
        editable:false,
        valueField:'id',
        typeAhead: true,
//        minListWidth:0,
        labelSeparator:" ",
        labelAlign:'left',
        mode:'local',
        forceSelection: true,
        selectOnFocus:true,
        listeners: {

                select: function(combo, record, index){

                 if (ramdisk_type.getValue()!= null){
                    ramdisk_type.setValue("");
                }



             }

        }

    });

    var ramdisk_type_store =new Ext.data.JsonStore({
        url: "/cloud/get_kernel_ramdiskforaccount?",
        root: 'info',
        fields: ['image_id','id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });


    var ramdisk_type = new Ext.form.ComboBox({
        id: 'ramdisk_type',
        fieldLabel: _('Ramdisk'),
        triggerAction:'all',
        emptyText :_("选择"),
        store:ramdisk_type_store,
        width:120,
//        listWidth:100,
        displayField:'image_id',
        valueField:'id',
        typeAhead: true,
//        minListWidth:50,
        labelSeparator:"",
        labelAlign:'left',
        mode:'local',
        forceSelection: true,
        listeners: {

                select: function(combo, record, index){

             }

        }

    });

    var advance_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="120"><b>高级参数</b><hr></div>'
    });


     var advance_fieldset=new Ext.Panel({
        height:30,
        border:false,
        width: 420,
        labelAlign:"left" ,
        layout:'table',
        labelSeparator:' ',
        layoutConfig: {columns:3},
        id:"advance_fieldset",
        items: [
        {
            labelWidth: 52,
            layout:'form',
            border:false,
            items:[kernel_type]
        },
        {
            width: 10,
            layout:'form',
            border:false,
            items:[dummy_space_panel4]
        },
        {
            labelWidth:55,
            layout:'form',
            border:false,
            items:[ramdisk_type]
        }
      ]
    });

    var servicetype_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="120"><b>从这里选择你的服务类型.</b></div>'
    });

    var servicetype_selectbtn=new Ext.Button({
        tooltip:'选择服务',
        tooltipType : "title",
        icon:'icons/accept.png',
        id: 'service_select',
        height:40,
        width:50,
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                 showWindow(_("选择服务类型"),350,130,Select_servicetype(vdc_id,account_id));
            }
        }
    });


    var panel3=new Ext.Panel({
        height:40,
        border:false,
        width: 420,
        labelAlign:"right" ,
        layout:'table',
        labelSeparator:' ',
        layoutConfig: {columns:3},
        id:"service_panel",
        items: [
        {
            labelWidth: 220,
            layout:'form',
            border:false,
            items:[servicetype_label]
        },
        {
            width: 60,
            layout:'form',
            border:false,
            items:[dummy_space1]
        },
        {
            labelWidth: 120,
            layout:'form',
            border:false,
            items:[servicetype_selectbtn]
        }]
    });




    var label_general=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("常规")+'</div>',
        id:'label_vm'
    });


    var label_create_vm=new Ext.form.Label({
        html:'<div>'+_("新建VM.")+'<br/></div><br/>'
    });

    var location_space=new Ext.form.Label({
        html:_('&nbsp;<div style="width:40px"/>')
    });
    var instance_space=new Ext.form.Label({
        html:_('&nbsp;<div style="width:40px"/>')
    });
    var advanced_space=new Ext.form.Label({
        html:_('&nbsp;<div style="width:40px"/>')
    });

    var account_panel=new Ext.Panel({
        height:50,
        id:"account_panelxx",
        layout:"form",
        frame:false,
        width:'100%',
        cls: 'whitebackground',
        autoScroll:true,
        border:false,
        labelAlign:"left" ,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 0px',
        items:[accountcombo]
    });

    var name_panel=new Ext.Panel({
        height:120,
        id:"name_panel",
        layout:"form",
        labelAlign:"left" ,
        frame:false,
        width:'100%',
        cls: 'whitebackground',
//        autoScroll:true,
        labelWidth:75,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:1px 1px 1px 1px',
        tbar:[label_general],
        items:[select_label,selection_space,name_textbox,account_panel]
    });

     var general_panel=new Ext.Panel({
        height:460,
        id:"panel0",
        layout:"form",
        frame:false,
        width:'100%',
        cls: 'whitebackground',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
//        tbar:[label_general],
        items:[name_panel,location_label,location_fieldset,
            instance_label,instance_fieldset,panel2,mem_and_cpu_panel,advance_label,advance_fieldset]
    });
    
    advance_label.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_KERNEL_RAM));
    advance_fieldset.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_KERNEL_RAM));
    location_label.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_REGION));	
    location_fieldset.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_REGION));	
    instance_fieldset.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_SERVICE_OFFERING));
    instance_label.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_SERVICE_OFFERING));
    account_panel.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_ACCOUNT));
    mem_and_cpu_panel.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_MEM_VCPU));

    return general_panel;

}


function create_networkcloud_panel(vdcid, mode, cp_feature, general_panel, node){

    var accountid=Ext.getCmp("account").getValue();

//    var region_id=Ext.getCmp("region").getValue();

    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space2=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space3=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space4=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space5=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });

    var sgroup_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="50">选择安全组或新建一个.</div>'
     });

    var keypair_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="50">选择密钥对或新建一个.</div>'
     });

    var publicip_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="50">选择一个未分配的公共IP或请求一个新的.</div>'
     });
     var predefined_nw_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="50">公共网络</div>'
     });
      var vdc_private_nw_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="50"> 私有网络</div>'
     });

    var securitygroup_store =new Ext.data.JsonStore({
        url: "/cloud_network/get_sec_group_list?",
        id:'securitygroup_store',
        root: 'rows',
        fields: ['id', 'name', 'description', 'region', 'region_id', 'account_name', 'account_id', 'record_new', 'record_modified', 'rules_store'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
//    securitygroup_store.load();
    var sec_grpcolumnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), hidden: true, dataIndex: 'id'},
        {header: _("名称"), width: 110, sortable: true, dataIndex: 'name'},
        {header: _("说明"), width: 200, sortable: true, dataIndex: 'description'},
        {header: _("区域"), width: 100, hidden: true, sortable: true, dataIndex: 'region'},
        {header: _("区域编号"), hidden: true, sortable: true, dataIndex: 'region_id'},
        {header: _("账户"), width: 100, hidden: true, sortable: true, dataIndex: 'account_name'},
        {header: _("账户编号"), hidden: true, sortable: true, dataIndex: 'account_id'},
        {header: _("新的记录"), width: 100, hidden: true, sortable: true, dataIndex: 'record_new'},
        {header: _("修改记录"), width: 100, hidden: true, sortable: true, dataIndex: 'record_modified'},
        {header: _("Rules Store"), width: 100, hidden: true, sortable: true, dataIndex: 'rules_store'},
        {header: _(""), width: 20, sortable: false, dataIndex: 'is_attached', renderer:show_sec_checkbox}
    ]);


    var sec_grpselmodel=new Ext.grid.RowSelectionModel({
        singleSelect:false
    })

    var new_button=new Ext.Button({
        name: 'add_secgrp',
        id: 'add_secgrp',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                security_group_grid.getSelectionModel().clearSelections();
                var windowid_sgd = Ext.id();
//                showWindow(_("Create Security Group"), 500, 390, SecGroupDetails(vdc_id, "NEW", null, windowid_sgd), windowid_sgd); //380, 365
                  showWindow(_("创建安全组"), 500, 390, SecGroupDetails(vdcid,"PROVISION", null, windowid_sgd), windowid_sgd); //380, 365
            }
        }
     });

     var edit_button=new Ext.Button({
        name: 'edit_secgrp',
        id: 'edit_secgrp',
        text:_("编辑"),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                     if(!security_group_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从列表中选择一个安全组"));
                    return;
                    }
                    var rec=security_group_grid.getSelectionModel().getSelected();
                    var windowid_sgd=Ext.id();
                    showWindow(_("编辑安全组"), 500, 390, SecGroupDetails(vdcid, "PROV_EDIT", rec, windowid_sgd), windowid_sgd);
            }
        }
     });


    var security_group_grid=new Ext.grid.GridPanel({
        id:'security_group_grid',
        store: securitygroup_store,
        stripeRows: true,
        colModel:sec_grpcolumnModel,
        frame:false,
        border:true,
        selModel:sec_grpselmodel,
        //autoExpandColumn:1,
//        autoScroll:true,
//        height:'100%',
        height:130,
        width:'100%',
        forceSelection: true,
        enableHdMenu:false,
        tbar:[_("<b>安全组</b>"),{
            xtype: 'tbfill'
        },new_button,edit_button],
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                edit_button.fireEvent('click',edit_button);
            }
         }

    });




     var nws_panel1=new Ext.Panel({
        height:180,
        border:false,
        width: 420,
        labelAlign:'left',
        layout:'column',
        autoScroll:true,
        labelSeparator:' ',
        id:"service_panel",
        items: [security_group_grid]

    });




    var key_selectbtn=new Ext.Button({
        tooltip:'选择',
        tooltipType : "title",
        icon:'icons/add.png',
        id: 'add',
        height:40,
        width:30,
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                var windowid=Ext.id();
                showWindow(_("创建密钥对"),380,190,KeyPairDefinition(vdcid,"PROVISION",null,windowid),windowid);//435

            }
        }
    });


    var keupair_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="120">Key Pair</div>'
     });



    var keypair_store =new Ext.data.JsonStore({
        url: "/cloud_network/get_key_pair_list?",
        root: 'rows',
        fields: ['id','name'],
        successProperty:'success',
        listeners:{

            load:function(obj,opts,res,e){if(keypair_group.getStore().getCount()>0){
                  keypair_group.setValue(keypair_group.getStore().getAt(keypair_group.getStore().getCount()-1).get('id'));
            }

            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
//    keypair_store.load();



    var keypair_group = new Ext.form.ComboBox({
        id: 'key_pair',
        fieldLabel: _('密钥对'),
        allowBlank:false,
        hideLabel:true,
        triggerAction:'all',
        emptyText :_("选择密钥对."),
        store:keypair_store,
        width:100,
        displayField:'name',
        editable:false,
        valueField:'id',
        typeAhead: true,
        minListWidth:114,
        labelSeparator:" ",
        mode:'local',
        selectOnFocus:true
    });
    
 var dummy_space5=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });

    var download_keypair=new Ext.Button({
        tooltip:'下载密钥对',
        tooltipType : "title",
        text:_("下载"),
        icon:'icons/storage_test.png',
        id: 'download_keypair',
        height:40,
        width:110,
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                       if(keypair_group.getValue()==""){
                        Ext.MessageBox.alert( _("警告"),"请选择一个密钥对下载");
                        return ;
                       }
                        Ext.MessageBox.confirm(_("确认"),"下载密钥对",function(id){
                            if(id=='yes'){
                                 downloadKeyPair(vdcid, Ext.getCmp("account").getValue(), Ext.getCmp("region_general").getValue(), keypair_group.getRawValue());
                            }
                        });

            } 
        }
    });
    var klbl=new Ext.form.Label({
         html: _("密钥对: &nbsp;")
     });

    var panel2=new Ext.Panel({
        autoHeight:true,
        border:false,
        width:'50%',
        labelAlign:'left',
        layout:'column',
        labelSeparator:' ',
        id:"keypair_panel1",
        items: [klbl,
            {
                width: 120,
//                layout:'form',
                border:false,
                items:[keypair_group]
            }
        ]
    });


     var nws_panel2=new Ext.Panel({
        height:40,
        border:false,
        width: 430,
        labelAlign:'left',
        layout:'column',
        labelSeparator:' ',
        id:"keypair_panel",
        items: [panel2,
            {
                width: 128,
                layout:'form',
                border:false,
                items:[download_keypair]
            }
            ,
            {
                width: 30,
                layout:'form',
                border:false,
                items:[key_selectbtn]
            }

            ]
    });

//    var req_pub_ip_win_height = 125;
//    if(!is_feature_enabled(cp_feature, stackone.constants.CF_REGION)){
//        req_pub_ip_win_height = 100;
//    }

    var public_selectbtn=new Ext.Button({
        tooltip:'选择',
        tooltipType : "title",
        icon:'icons/add.png',
        id: 'add',
        height:40,
        width:50,
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                var windowid=Ext.id();
                if(is_feature_enabled(cp_feature, stackone.constants.CF_REGION)){
                    showWindow(_("请求公共IP"),380,140,PublicIPDefinition(vdcid,mode,null,windowid, cp_feature),windowid);//435
                }
                else{
                        var message_text = "确定要请求新的公共IP吗?";
                        Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                            if(id=='yes'){
                                request_public_ip(vdcid, "", "", "PROVISION", null)
                            }
                        });
                }
            }
        }
    });


    var publicIP_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="120">Public IP</div>'
     });


    var publicIP_store =new Ext.data.JsonStore({
        url: "/cloud_network/get_public_ip_list?",
        root: 'rows',
        fields: ['id','name'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            },
            load:function(obj,opts,res,e){
                if(publicIP_group.getStore().getCount()!=0){
                   publicIP_group.setValue(publicIP_store.getAt(0).get('id'));
                }
                
                
            }
        }
    });
//    publicIP_store.load();

    var publicIP_group = new Ext.form.ComboBox({
        id: 'publicIP_pair',
        hideLabel:true,
        fieldLabel: _('公共IP'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择公共IP."),
        store:publicIP_store,
        width:100,
        displayField:'name',
        editable:false,
        valueField:'id',
        typeAhead: true,
        minListWidth:114,
        labelSeparator:" ",
        mode:'local',
        forceSelection: true,
        selectOnFocus:true
    });


    var none=new Ext.form.Radio({
        boxLabel: _('None'),
        width:60,
        id:'none',
        checked:true,
        name:'radio',
        listeners:{
            check:function(field,checked){
                if(checked==true){
                    cloud_region_id = general_panel.items.get("location_fieldset").items.get("location_fieldset_region").items.get("region_general").getValue();
                    if (!is_feature_enabled(cp_feature,stackone.constants.CF_ACCOUNT)){
                     Ext.getCmp('cms_cp_pub_ip_pool_panel').disable(); }
				}

            }
            }
    });


    var unassigned=new Ext.form.Radio({
        boxLabel: _('未分配'),
        id:'unassigned',
        width:90,
        name:'radio',
        listeners:{
            check:function(field,checked){
                if(checked==true){
                    cloud_region_id = general_panel.items.get("location_fieldset").items.get("location_fieldset_region").items.get("region_general").getValue();
                    cloud_account_id = general_panel.items.get("name_panel").items.get("account_panelxx").items.get("account").getValue();
//                    alert("-------"+cloud_region_id+"===="+cloud_account_id);
                    publicIP_group.enable();
                    public_selectbtn.enable();
                    if(!is_feature_enabled(cp_feature,stackone.constants.CF_ACCOUNT)){
                    Ext.getCmp('cms_cp_pub_ip_pool_panel').enable(); }
					publicIP_store.load({
                        params:{
                            vdc_id:vdcid,
                            acc_id:cloud_account_id,
                            region_id:cloud_region_id,
                            pi_type:"provision"
                        }
                    });

                }else{
					publicIP_group.disable();
                    public_selectbtn.disable();
                }
            }
            }
    });
    var lbl=new Ext.form.Label({
         html: _("公共IP: &nbsp;")
     });


    panel3=new Ext.Panel({
//        height:100,
        border:false,
        width:'80%',
        labelAlign:'left',
        layout:'column',
        labelSeparator:' ',
        autoHeight:true,
//        bodyStyle:'padding: 5px 5px 5px 5px',
        id:"publicip_panel1",
        items: [lbl,none,unassigned,
            {
                width: 126,
//                layout:'form',
                border:false,
                items:[publicIP_group]
            }]
    });

    nws_panel3=new Ext.Panel({
        height:30,
        border:false,
        width: 430,
        labelAlign:'left',
        layout:'column',
        labelSeparator:' ',
        id:"publicip_panel",
        items: [panel3,
            {
                width: 30,
                layout:'form',
                border:false,
                items:[public_selectbtn]
            }
          ]
    });

    var predefined_nw_panel=new Ext.Panel({
        height:'20%',
        border:false,
        width: 430,
        labelSeparator:' ',
        id:"public_ip_comp_panel"
    });

    var vdc_private_nw_panel=new Ext.Panel({
        height:'20%',
        border:false,
        width: 430,
        labelSeparator:' ',
        id:"vdc_private_nw_panel"
    });


    var private_pool_panel=new Ext.Panel({
        height:'30%',
        border:false,
        width: 430,
        labelSeparator:' ',
        id:"private_pool_panel"
    });

    if(is_feature_enabled(cp_feature,stackone.constants.CF_VDC_PRE_DEFINED_NW)){
            var pdf_n_grid = get_vm_predefined_network_grid(vdcid, mode, node);
            predefined_nw_panel.add(pdf_n_grid);
        }

    if(is_feature_enabled(cp_feature,stackone.constants.CF_VDC_PRIVATE_NW)){
            var vdc_priv_grid = get_vm_vdc_private_network_grid(vdcid, mode, node);
            var selected =vdc_priv_grid.getSelections();
            if(selected == 0)
                     {		
                          unassigned.disable();
                          none.disable();  
                    }else if (selected == 1)
                    {	
                         unassigned.enable();
                         none.enable();  
                    }
                                  
            vdc_private_nw_panel.add(vdc_priv_grid);
        }
    
    if(is_feature_enabled(cp_feature,stackone.constants.CF_VDC_PRIVATE_NW)){
            var private_nw_combo = get_private_nw_combo();
            var selected =Ext.getCmp('vdc_private_grid').getSelections();
            private_pool_panel.add(private_nw_combo);
            if(selected <= 1)
            {
                Ext.getCmp('cms_cp_pub_ip_pool_panel').hide();            
            }
        }

      if(!is_feature_enabled(cp_feature,stackone.constants.CF_ACCOUNT)){
    Ext.getCmp('cms_cp_pub_ip_pool_panel').disable(); }
    
    var dummy_space6=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });

     var dummy_space7=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });




   var sec_grp_panel=new Ext.Panel({
        height:200,
        border:false,
        width: 430,
        labelSeparator:' ',
        id:"sec_grp_comp_panel",
        items: [sgroup_label,nws_panel1]
    });

    var key_pair_panel=new Ext.Panel({
        height:60,
        border:false,
        width: 430,
        labelSeparator:' ',
        id:"key_pair_comp_panel",
        items: [keypair_label,dummy_space2,nws_panel2]
    });

    public_ip_panel=new Ext.Panel({
        height:'100%',
        border:false,
        width: 430,
        labelSeparator:' ',
        id:"public_ip_comp_panel",
        items: [predefined_nw_panel,dummy_space6,vdc_private_nw_panel,dummy_space7,publicip_label,dummy_space3,nws_panel3,private_pool_panel]
    });

    var label_network=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("网络")+'</div>',
        id:'label_vm'
    });
    
    var label_network_details=new Ext.form.Label({
        html:'<div class="backgroundcolor" height="60" width="60">为虚拟机指定网络详情.</div>'
    });

    var network_panel=new Ext.Panel({
        height:"100%",
        id:"panel3",
        layout:"form",
        cls: 'whitebackground',
        frame:false,
        width:'100%',
        autoScroll:false,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        tbar:[label_network],
        items:[label_network_details,sec_grp_panel,key_pair_panel,public_ip_panel]
        ,listeners: {
            show:function(p){
//                alert("network_panel returns");
                securitygroup_store.sort('name','ASC');

            }
         }
});
    publicIP_group.disable();
    public_selectbtn.disable();
    if(mode == "EDIT_VM") {
        security_group_grid.disable();
        keypair_group.disable();
        key_selectbtn.disable();
        download_keypair.disable();
    }
    sec_grp_panel.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_SEC_GRP));
    key_pair_panel.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_KEY_PAIR));
    public_ip_panel.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_PUBLIC_IP));
    predefined_nw_panel.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_VDC_PRE_DEFINED_NW));
    private_pool_panel.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_VDC_PRIVATE_NW));
    vdc_private_nw_panel.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_VDC_PRIVATE_NW_POOL));

    return network_panel;

}


function create_storagecloud_panel(vdc_id, vm_info, mode, cp_feature){
//     var accountid=Ext.getCmp("account").getValue();

    var disk_edit=is_feature_enabled(cp_feature, stackone.constants.CF_VM_STORAGE_EDIT);
    var columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), hidden: true, dataIndex: 'id'},
        {header: _("名称"), width: 140, sortable: true, dataIndex: 'name',hidden:!disk_edit},
        {header: _("说明"), width: 110, sortable: true, dataIndex: 'description',hidden:!disk_edit},
        {header: _("挂载点"), width: 140, sortable: true, dataIndex: 'mount_point',hidden:disk_edit},
        {header: _("卷编号"), width: 110, sortable: true, dataIndex: 'volume_id',hidden:!disk_edit},
        {header: _("大小"), width: 70, sortable: true, dataIndex: 'display_size'},
        {header: _("大小"), hidden: true, sortable: true, dataIndex: 'size'},
        {header: _("大小单元"), hidden: true, sortable: true, dataIndex: 'size_unit'},
        {header: _("模式"), width: 140, sortable: true, dataIndex: 'mode',hidden:disk_edit}
        ]);

    var volume_store = new Ext.data.JsonStore({
        url: '/cloud_storage/get_attached_volumes?vm_id=' + vm_id,
        root: 'rows',
        fields: ['id', 'name', 'description', 'volume_id', 'display_size', 'size', 'size_unit','mount_point','mode'],
        successProperty:'success'
    });
    volume_store.load();

    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("存储")+'</div>',
        id:'label_task'
    });

    var new_button=new Ext.Button({
        name: 'add_button',
        id: 'add_button',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                cloud_strg_grid_vm_level.getSelectionModel().clearSelections();
                var windowid_csd = Ext.id();
                showWindow(_("创建存储"), 380, 275, CloudStorageDefinition(vdc_id, "NEW", null, windowid_csd, vm_info,cp_feature), windowid_csd);
            }
        }
    });
    
    var remove_button=new Ext.Button({
        name: 'remove_button',
        id: 'remove_button',
        text:_("移除"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedStorage(cloud_strg_grid_vm_level)){
                    var storage_name, acc_id, region_id;
                    var rec=cloud_strg_grid_vm_level.getSelectionModel().getSelected();
                    storage_name=rec.get('name');
                    volume_id=rec.get('volume_id');
                    var message_text = "确定要移除 (" + storage_name + ")存储吗?";
                    Ext.MessageBox.alert(_("信息"),_(message_text));
                    Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                        if(id=='yes'){
                            var remove_object = new Object();
                            remove_object.vdc_id = vdc_id;
                            remove_object.account_id = cloud_account_id;
                            remove_object.region_id = cloud_region_id;
                            remove_object.volume_id = volume_id;
                            remove_object.storage_name = storage_name;
                            remove_object.grid = cloud_strg_grid_vm_level;

                            detachCloudStorage(vdc_id, cloud_account_id, cloud_region_id, volume_id, cloud_instance_id, null, null, storage_name, cloud_strg_grid_vm_level, remove_object);
                        }
                    });
                }
            }
        }
    });

    var attach_button=new Ext.Button({
        name: 'attach_button',
        id: 'attach_button',
        text:_("附加"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var windowid_strg= Ext.id();
                showWindow(_("附加存储"), 380, 210, CloudStorageAttachAtVMLevel(vdc_id, cloud_account_id, cloud_region_id, cloud_zone_id, vm_id, vm_name, null, cloud_instance_id, mode, windowid_strg), windowid_strg);
            }
        }
    });

    var detach_button=new Ext.Button({
        name: 'detach_button',
        id: 'detach_button',
        text:_("分离"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedStorage(cloud_strg_grid_vm_level)){
                    rec = cloud_strg_grid_vm_level.getSelectionModel().getSelected();
                    var storage_name = rec.get('name');
                    var volume_id = rec.get('volume_id');
                    
                    if(cloud_instance_id) {
                        var message_text = "确定要把(" + storage_name + ") 存储从 (" + vm_name + ")虚拟机分离吗?";
                        Ext.MessageBox.alert(_("信息"),_(message_text));
                        Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                            if(id=='yes'){
                                detachCloudStorage(vdc_id, cloud_account_id, cloud_region_id, volume_id, cloud_instance_id, null, null, storage_name, cloud_strg_grid_vm_level);
                            }
                        });
                    } else {
                        Ext.MessageBox.alert(_("信息"),_("存储未附加给虚拟机."));
                    }

                }
            }
        }
    });
    
    var tbar = new Array();
    tbar.push({xtype: 'tbfill'});

    //TODO : commenting out for now, need to implement
//    if(disk_edit){
//        tbar.push(new_button);
//        tbar.push('-');
//        tbar.push(remove_button);
//        tbar.push('-');
//        tbar.push(attach_button);
//        tbar.push('-');
//        tbar.push(detach_button);
//    }
    cloud_strg_grid_vm_level = new Ext.grid.GridPanel({
        store: volume_store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        id:'cloud_vm_strg_grid',
        autoScroll:true,
        autoExpandColumn:1,
        selModel:selmodel,
        width:'100%',
        height:360,
        enableHdMenu:false,
        root: 'rows',
        tbar:tbar,
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                edit_button.fireEvent('click',edit_button);
            }
         }
    });

    var label_vol_list_info=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="60">这显示了与虚拟机相关的卷的列表.</div>'
    });

    var storagetotal_panel=new Ext.Panel({
        id:"panel1",
        cls: 'whitebackground',
        layout:"form",
        frame:false,
        width:'100%',
        height:320,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding:5px 5px 5px 5px',
        tbar:[label_strge],
        items:[label_vol_list_info, cloud_strg_grid_vm_level]
    });

    return storagetotal_panel;
}

function create_rootdevicecloud_panel(vdcid){

    var accountid=Ext.getCmp("account").getValue();


    var template_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="120">The root device is ebs.</div>'
    });



    var rootdevice_detials=new Ext.Button({
        tooltip:'Root设备详情',
        tooltipType : "title",
        icon:'icons/accept.png',
        id: 'rootdevice_detials',
        height:40,
        width:50,
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                showWindow(_("Root设备详情"),250,250,Rootdevice_details(accountid));
            }
        }
    });


    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:80px"/>')
    });

    var panel=new Ext.Panel({
        height:40,
        border:false,
        width: 420,
        labelAlign:'left',
        layout:'table',
        labelSeparator:' ',
        layoutConfig: {columns:3},
        id:"panel",
        items: [
        {
            labelWidth: 220,
            layout:'form',
            border:false,
            items:[template_label]
        },
        {
            width: 60,
            layout:'form',
            border:false,
            items:[dummy_space1]
        },
        {
            labelWidth: 120,
            layout:'form',
            border:false,
            items:[rootdevice_detials]
        }]
    });



    var label_rootdevice=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Root设备")+'</div>',
        id:'label_vm'
    });

    var rootdevice_panel=new Ext.Panel({
        height:420,
        id:"panel2",
        cls: 'whitebackground',
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
//        labelWidth:130,
        tbar:[label_rootdevice],
        items:[panel]
    });

    return rootdevice_panel;

}

function Select_template(regionid,accountid,vdcid,cp_feature){


    if(is_feature_enabled(cp_feature,stackone.constants.CF_REGION))
    regionhide=false
    else
    regionhide=true

    if(!is_feature_enabled(cp_feature,stackone.constants.CF_ACCOUNT))
    hide=false
    else
    hide=true

    var templates_store =new Ext.data.JsonStore({
        url: "/cloud/get_templatesforaccount?",
        root: 'info',
        fields: ['id','name','platform','architecture','region','location','provider','source','cpu','memory','size'],
        successProperty:'success',
        listeners:{
            load: function(){
                templates_store.sort('name','ASC');
                Ext.MessageBox.hide();
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
//    templates_store.load();

    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

     var template_columnModel = new Ext.grid.ColumnModel([

    {
        header: _("编号"),
        width:70,
        dataIndex: 'id',
        hidden:true
    },
//    {
//        header: _(""),
//        width: 35,
//        dataIndex: 'details',
//        sortable:true
//         ,renderer:function(value,params,record,row){
//            params.attr='ext:qtip="Template Details"' +
//                'style="background-image:url(icons/information.png) '+
//                '!important; background-position: right;'+
//                'background-repeat: no-repeat;cursor: pointer;"';
//
//        return value;
//        }
//    },
    {
        header: _("名称"),
        width:170,
        dataIndex: 'name',
        sortable:true
    },
    {
        header: _("IaaS"),
        width:60,
        dataIndex: 'provider',
        sortable:true,
        hidden:true
        
    },
    {
        header: _("区域"),
        width:100,
        dataIndex: 'region',
        sortable:true,
        hidden:regionhide
    },
    {
        header: _("资源"),
        width:250,
        dataIndex: 'location',
        sortable:true,  
        hidden:regionhide
    },
    {
        header: _("平台"),
        width:100,
        dataIndex: 'platform',
        sortable:true,
        hidden:regionhide
    },
    {
        header: _("架构"),
        width:100,
        dataIndex: 'architecture',
        sortable:true,
        hidden:regionhide
    },
    {
        header: _("模板类型"),
        width:120,
        dataIndex: 'source',
        sortable:true,
        hidden:true
        
    },
    {
        header: _("VCPUs"),
        width:110,
        dataIndex: 'cpu',
        sortable:true,
        align:'right',
        hidden:hide
    },
    {
        header: _("内存(MB)"),
        width:110,
        dataIndex: 'memory',
        align:'right',
        sortable:true,
        hidden:hide
    },
    {
            header: _("存储GB)"),
            width:110,
            dataIndex: 'size',
            align:'right',
            sortable:true,
            hidden:hide
        }
    ]);


    var label_template=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("模板")+'</div>',
        id:'label_vm'
    });

    var search=new Ext.form.TextField({
        fieldLabel: _('搜索'),
        name: 'search',
        //id: 'search_summary',
        allowBlank:true,
        emptyText :_("搜索"),
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {
                template_grid.getStore().filter('name', field.getValue(), false, false);
            }
        }
    })

    var select_template = new Ext.form.ComboBox({
        id: 'select_template',
        fieldLabel: _('选择模板'),
        triggerAction:'all',
        //emptyText :_("Select Template"),
        store:[['All Templates','All Templates'],['DEFAULT_TEMPLATE','Shared Templates'],['MY_TEMPLATE','Custom Templates']],
        width:140,
        listWidth:120,
        displayField:'name',
        valueField:'name',
//        minListWidth:0,
        labelSeparator:" ",
        mode:'local',
        forceSelection:true,
        listeners: {
                    select: function(combo, record, index){
                            if(combo.getValue()=="All Templates")
                            {   
                                  template_grid.getStore().reload();                      
                            }else{
                            template_grid.getStore().filter('source', combo.getValue(), false, false);}
         
        	    }
             }

    });
      select_template.setValue('All Templates');
      
     var template_type_store =new Ext.data.JsonStore({
        url: "/cloud/get_templatetypeforprovision?",
        root: 'info',
        fields: ['name'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

//    template_type_store.load();

     var template_type = new Ext.form.ComboBox({
        id: 'template_type',
        fieldLabel: _('选择类型'),
        triggerAction:'all',
        emptyText :_("选择类型"),
        store:template_type_store,
        width:120,
        listWidth:100,
        displayField:'name',
        valueField:'name',
//        minListWidth:0,
        labelSeparator:" ",
        mode:'local',
        forceSelection: true,
        listeners: {

                select: function(combo, record, index){

                 var type=combo.getValue()
                 templates_store.load({
                    params:{

                         regionid:Ext.getCmp("region_general").getValue(),
                         accountid:Ext.getCmp("account").getValue(),
                         vdcid:vdcid,
                         instance_type:Ext.getCmp("serviceoffering").getValue(),
                         template_type:type
                    }
                });


             }

        }

    });
     var dummy_space1=new Ext.form.Label({
         html:_('&nbsp;<div style="width:25px"/>')
    });  
     
     
    var template_grid = new Ext.grid.GridPanel({
        store: templates_store,
        colModel:template_columnModel,
        stripeRows: true,
        selmodel:selmodel,
        frame:false,
        id:'template_summary_grid',
        width:'100%',
        autoExpandColumn:4,
        autoExpandMax:250,
        autoExpandMin:150,
        height:385,
        maxHeight:100,
        enableHdMenu:true,
        tbar:[label_template,{xtype: 'tbfill'},search,dummy_space1,select_template]
       ,listeners:{
        }
    });

    var template_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="60">模板.</div>'
    });


    return template_grid;

}

function Select_servicetype(vdcid,accountid){

    var servicetype_store =new Ext.data.JsonStore({
        url: "/cloud/get_servicetypeforvdc?accountid="+accountid,
        root: 'info',
        fields: ['name','value'],
        successProperty:'success',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    servicetype_store.load();


    var Service_types = new Ext.form.ComboBox({
        id: 'servicetypes_combo',
//        fieldLabel: _('Templates'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择服务类型."),
        store:servicetype_store,
        width:200,
        displayField:'value',
        editable:false,
        valueField:'value',
        typeAhead: true,
        minListWidth:50,
        labelSeparator:" ",
        mode:'local',
        forceSelection: true,
        selectOnFocus:true
    });

    var Servicetype_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="60">服务类型.</div>'
    });

//
    var label_template=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("服务类型")+'</div>',
        id:'label_vm'
    });

    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:25px"/>')
    });

    var servtype_panel=new Ext.Panel({
        id:"servtype_panel",
        cls: 'whitebackground',
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[Servicetype_label,dummy_space1,Service_types],
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'ok',
                id: 'ok',
                text:_('确定'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        closeWindow();
                    }
                }
            }),
            '-',
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('取消'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {closeWindow();}
                }
            })
        ]
    });



    var Sercietype_panel=new Ext.Panel({
        height:140,
        id:"template_panel",
        cls: 'whitebackground',
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        tbar:[label_template],
        items:[servtype_panel]
    });

    return Sercietype_panel;


}



function Rootdevice_details(){

   var label_rootdevice=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("服务类型")+'</div>',
        id:'label_vm'
    });


    var rootdevice_store =new Ext.data.JsonStore({
        url: "/cloud/get_rootdeviceforcloud",
        root: 'info',
        fields: ['name','value'],
        successProperty:'success',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    rootdevice_store.load();

    var rootdevice= new Ext.form.ComboBox({
        id: 'rootdevice_combo',
//        fieldLabel: _('Templates'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择Root设备."),
        store:rootdevice_store,
        width:200,
        displayField:'value',
        editable:false,
        valueField:'value',
        typeAhead: true,
        minListWidth:50,
        labelSeparator:" ",
        mode:'local',
        forceSelection: true,
        selectOnFocus:true
    });




    var rootdevice_panel=new Ext.Panel({
        height:120,
        id:"rootdevice_panel",
        cls: 'whitebackground',
//        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
//        labelWidth:130,
        tbar:[label_rootdevice],
        items:[rootdevice]
    });

    return rootdevice_panel;


}

function process_cloud_panel(panel,treePanel,value,type)
{

    var count=value;
    panel.getLayout().setActiveItem("panel"+count);
    treePanel.getNodeById("node"+count).select();

}
function UIMakeUP(value, meta, rec){
    if(rec.get('type')==='bar'){
        var val=Ext.util.Format.substr(value,0,4);
        var id = Ext.id();
        (function(){
            new Ext.ProgressBar({
                renderTo: id,
                value: val/100,
                text:val,
                width:100,
                height:16
            });
        }).defer(25)
        return '<span id="' + id + '"></span>';
    }else if(rec.get('type')==='storage'){
        var val=Ext.util.Format.substr(value,0,4);
        var id = Ext.id();
        (function(){
            new Ext.ProgressBar({
                renderTo: id,
                value: val/100,
                text:val,
                width:75,
                height:16
            });
        }).defer(25)
        return '<span id="' + id + '"></span>';
    }else if(rec.get('type')==='vmsummary'){
        var summary=value;
        if(value.indexOf('/')>-1){
            var values=value.split('/');
            var tot=values[0];
            var run=values[1];
            var paus=values[2];
            var down=values[3];

            summary=tot;
            if(run!=0 || paus!=0 || down!=0){
                var str_down="";
                if(values[4]=="node_down"){
                    str_down="_down";
                }
                summary+=" [";
                var flag=false;
                if(run!=0){
                    flag=true;
                    summary+=run+" "+
                        "<img width='11px' title='"+run+"Running' height='11px' src='../icons/small_started_state"+str_down+".png'/>";
                }
                if(paus!=0){
                    summary+=((flag)?" , ":"")+paus+" "+
                        "<img width='11px' title='"+paus+"Paused' height='11px' src='../icons/small_pause"+str_down+".png'/>";
                    flag=true;
                }
                if(down!=0){
                    summary+=((flag)?" , ":"")+down+" "+
                        "<img width='11px' title='"+down+"Down' height='11px' src='../icons/small_shutdown"+str_down+".png'/>";
                }

                summary+="]";
            }

        }
        return summary;
    }else if(rec.get('type')==='serversummary'){
        var summary=value;
        if(value.indexOf('/')>-1){
            var values=value.split('/');
            var tot=values[0];
            var run=values[1];
            var down=values[2];

            summary=tot;
            if(run!=0 || down!=0){
                summary+=" [";
                var flag=false;
                if(run!=0){
                    flag=true;
                    summary+=run+" "+
                        "<img width='11px' title='"+run+"Connected' height='11px' src='../icons/small_connect.png'/>";
                }
                if(down!=0){
                    summary+=((flag)?" , ":"")+down+" "+
                        "<img width='11px' title='"+down+"Not Connected' height='11px' src='../icons/small_disconnect.png'/>";
                }

                summary+="]";
            }

        }
        return summary;
    }
    else if(rec.get('type') == 'Notifications'){

        var notificationValue = showNotifications(value,meta,rec);
        return notificationValue;
    }
    else if(rec.get('type') == 'hasummary'){
        return showHASummary(value,meta,rec);
    }
    else if(rec.get('type') == 'fenceconfig'){
        if(value == 0) {
            var sp_id = rec.get('list');
            var fn = "showHADialog('" + sp_id + "')";
            var returnVal = 'No<a style="text-decoration:none;" href="#" onClick=' + fn + '>'+
                    '&nbsp;<img title="Configure Fence" alt="Configure Fence" width="13"'+
                    ' height="13" src="../icons/information.png"/></a>';
            return returnVal;
        }
        else {
            return "Yes";
        }
    }
    else if(rec.get('type') == 'Systemtasks'){
        var sysTasks = showSysTasks(value,meta,rec);
        return sysTasks;
    }
    else{
        return value;
    }
}

function create_account_dropdown(vdc_id,type,id){


     var account_store =new Ext.data.JsonStore({
        url: "/cloud/get_accountsforvdc?vdcid="+vdc_id,
        root: 'info',
        fields: ['name','value'],
        successProperty:'success',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        listeners:{
            load:function(obj,opts,res,e){
                if(Account.getStore().getCount()==1){
                    Account.setValue(Account.getStore().getAt(0).get('value'));
                    Account.fireEvent('select',Account,Account.getStore().getAt(0),0);
                    var acc_panel = Ext.getCmp("account_panelxx");
                    if (acc_panel != undefined){
                        acc_panel.hide();
                    }
                    
                }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    account_store.load();

    var account_id="";
    var val=(id==null)?"":+'_'+id;
    var Account = new Ext.form.ComboBox({
        id: 'account'+val,
        fieldLabel: _('账户'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择"),
        store:account_store,
        width:300,
        displayField:'name',
        editable:false,
        valueField:'value',
        labelAlign:'left',
        typeAhead: true,
        minListWidth:50,
        labelSeparator:" ",
        mode:'local',
        forceSelection: true,
        selectOnFocus:true ,
        listeners: {
                    
                select: function(combo, record, index){
                    account_id=combo.getValue();
                    if (type == 'provision' || type == 'public_ip'){
                        if(Ext.getCmp("region_general")!=null){
                            Ext.getCmp("region_general").getStore().load({
                            params:{
                                vdcid:vdc_id
//                                accountid:account_id
                            }
                            });
                        }else{
                            Ext.getCmp("region").getStore().load({
                            params:{
                                vdcid:vdc_id
//                                accountid:account_id
                            }
                            });
                        }
                         if(Ext.getCmp("category_type")!= undefined  &&  Ext.getCmp("region_general") != undefined)
                            if (Ext.getCmp("category_type").getValue() && Ext.getCmp("region_general").getValue()){

                                Ext.getCmp("category_type").setValue(" ");
                                Ext.getCmp("region_general").setValue(" ");
                                Ext.getCmp("zones_type").setValue(" ");

                            }
                        if(Ext.getCmp("category_type")!= undefined )
                            Ext.getCmp("category_type").getStore().load({
                                params:{
                                    account_id:account_id,
                                    vdc_id:vdc_id
                                }
                            });
                    }
            }

        }

    });
    return Account;

}

function create_region_dropdown(vdcid){


      var region_store =new Ext.data.JsonStore({
        url: "/cloud/get_regionforvdc?",
        root: 'info',
        fields: ['name','value'],
        successProperty:'success',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        listeners:{
            load:function(obj,opts,res,e){
                if(Region.getStore().getCount()==1){
                    Region.setValue(Region.getStore().getAt(0).get('value'));
                }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    region_store.load({
        params:{
            vdcid:vdcid
             }
    });

    var Region = new Ext.form.ComboBox({
        id: 'region',
        fieldLabel: _('区域'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择"),
        store:region_store,
        width:270,
        displayField:'name',
        editable:false,
        valueField:'value',
        typeAhead: true,
        minListWidth:50,
        labelSeparator:" ",
        labelAlign:'elft',
        mode:'local',
        forceSelection: true,
        selectOnFocus:true,
        listeners: {

                select: function(combo, record, index){

        }

      }
    });
    return Region;

}

function reloadSecGroup(vdc_id){
       var acc_id=Ext.getCmp('account').getValue();
       var region_id=Ext.getCmp("region_general").getValue();

       Ext.getCmp("security_group_grid").getStore().load({
             params:{
                 vdc_id:vdc_id,
                 acc_id:acc_id,
                 region_id:region_id,
                 sec_type:"provision"
             }

            }
       );

}

function show_sec_checkbox (value,params,record){
    var id = Ext.id();
    (function(){
        new Ext.form.Checkbox({
            renderTo: id,
            width:100,
            height:16,
            checked:value,
            value:false,
            listeners:{
                check:function(field,checked){
                    if(checked){
                        record.set('is_attached',true);
//                        field.setValue(true);
                    }else{
                        record.set('is_attached',false);
//                        field.setValue(false);
                    }
                }
            }
        });
    }).defer(5);
    return '<span id="' + id + '"></span>';
}

function show_templates(region,account,serviceoffering_type,vdc_id, cp_feature){
    var  template_grid=Select_template(region,account,vdc_id,cp_feature)

   
   template_grid.getStore().load({
        params:{

             regionid:region,
             accountid:account,
             vdcid:vdc_id,
             instance_type:serviceoffering_type
        }
    });

    var temp_name=""

    var temp_panel=new Ext.Panel({
        id:"temp_panel",
        cls: 'whitebackground',
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[template_grid],
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'ok',
                id: 'ok',
                text:_('确定'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                    	
                        var selection=template_grid.getSelectionModel().getSelected();
                        if(selection== undefined){
                        	Ext.MessageBox.alert('错误','请选择一个模板');
                        	return false;
                        }
                        tmpl_id=selection.get('id');
                        temp_name=selection.get('name');
                       
                        if (temp_name == null){

                            temp_name=tmpl_id
                        }
//                        get cpu memeory info 
	                        var url = "/cloud/get_template_info?template_id="+tmpl_id;
	                        var ajaxReq=ajaxRequest(url,0,"POST",true);
	                        ajaxReq.request({
	                            success: function(xhr) {
	                                var response=Ext.util.JSON.decode(xhr.responseText);
	                                if(response.success){
	                                	var info  = response.nodes.info;
	                                	Ext.getCmp('cpu_textbox').setValue(info['cpu']);
	                                	Ext.getCmp('mem_textbox').setValue(info['memory']);
	                                }else{
	                                    Ext.MessageBox.alert(_("失败"),_("无法获取信息."));
	                                }
	                            },
	                            failure: function(xhr){
	                                Ext.MessageBox.alert( _("失败") , xhr.statusText);
	                            }
	                        });

                            var cloud_vm_strg_grid = Ext.getCmp('cloud_vm_strg_grid');
                            if (cloud_vm_strg_grid){
                                cloud_vm_strg_grid.getStore().load({
                                    params:{
                                        vdc_id : vdc_id,
                                        tmpl_id : tmpl_id
                                    }
                                });
                            }

//                            alert("------"+tmpl_id);
                            
                            if(is_feature_enabled(cp_feature,stackone.constants.CF_VDC_PRE_DEFINED_NW)){
                                    var predef_json_store = Ext.getCmp('predef_grid').getStore();
                                    predef_json_store.load({
                                        params:{
                                            vdcid : vdc_id,
                                            tmpl_id : tmpl_id
                                        }
                                    });
                            }

                        /*if (temp_name != " "){
                                Ext.getCmp("lbl").setText("  Selected Template :  "+temp_name);
//                                lbl.setText("  Selected Template :  "+temp_name);
                                Ext.getCmp("lbl").show();
//                                lbl.show();
                            }*/
                        set_template_name(temp_name);
                        closeWindow();
                    }
                }
            }),
            '-',
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('取消'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {closeWindow();}
                }
            })
        ]
    });

    return temp_panel;

}

function set_template_name(temp_name)
{
    if (temp_name && temp_name != " ")
    {
        Ext.getCmp("lbl").setText("  选择模板 :  "+temp_name);
        Ext.getCmp("lbl").show();
    }
}



function get_vm_predefined_network_grid(vdcid, mode, node){
    var url="";
    if(mode=="EDIT_VM")
    {
        vm_id=node.attributes.id;
        url="/cloud_network/get_predefined_network_list_for_vm_provision?mode="+mode+"&vm_id="+vm_id;
    }
    else
    {
        url="/cloud_network/get_predefined_network_list_for_vm_provision?mode="+mode;
    }

    var nw_label = new Ext.form.Label({
        html:'<div class="toolbar_hdg" >'+_("定义的网络")+'<br/></div>'
    });
    var nw_selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false,
            listeners:{
            }
     });

    var predef_json_store = new Ext.data.JsonStore({
        //url:'/cloud_network/get_predefined_network_list_for_vm_provision',
        url:url,
        root:'rows',
        fields: ['id', 'name', 'from_template', 'selected'],
        successProperty:'success',
        listeners:{
            loadException:function(obj,opts,res,e){
                 var store_response=Ext.util.JSON.decode(res.responseText);

                Ext.MessageBox.alert(_("错误"),store_response.msg);
            },
            load:function(store,opts,res,e){
                    var size=store.getCount();
                    if(mode != "PROVISION") {   
                        for (var i=0;i<size;i++){
                            //alert("selected----:"+store.getAt(i).get('selected'));
                            if(store.getAt(i).get('selected') == true)
                            {
                                predef_grid.getSelectionModel().selectRow(i,true);
                            }
                        }
                            
                    }
                    else {
                        for (var i=0;i<size;i++){
                            if (store.getAt(i).get('from_template') == true){
                                    predef_grid.getSelectionModel().selectRow(i,true);
                            }
                        }

                    }

                }
          }
    });

    predef_json_store.load({
        params:{
            vdcid : vdcid
        }
    });

    var predef_grid = new Ext.grid.GridPanel({
        id :'predef_grid',
        stripeRows:true,
        frame:false,
        width:'100%',
        autoScroll:true,
        autoExpandMin:100,
        height:95,
        enableHdMenu:false,
         autoExpandColumn:1,    
        selModel:nw_selmodel,
        tbar:[nw_label],
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        store:predef_json_store,
          columns: [
            nw_selmodel,
            {header: "id", width: 180, sortable: false,hidden:true, css:'font-weight:bold; color:#414141;',dataIndex:'id'},
            {header: "名称", width: 402, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'name'}
        ]
    });
    return predef_grid;
}




function get_vm_vdc_private_network_grid(vdcid, mode, node){
    var url="";
    if(mode=="EDIT_VM")
    {
        vm_id=node.attributes.id;
        url="/cloud_network/get_private_network_list_for_vm_provision?&vdcid="+vdcid+"&mode="+mode+"&vm_id="+vm_id;
    }
    else
    {
        url="/cloud_network/get_private_network_list_for_vm_provision?&vdcid="+vdcid+"&mode="+mode;    
    }

    var vdc_nw_label = new Ext.form.Label({
        html:'<div class="toolbar_hdg" >'+_("私有网络")+'<br/></div>'
    });
     
    
    var vdc_nw_selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false,
            listeners:{
                rowselect:function(sel_model, index, record){
                      
                      var ex_str = Ext.data.Record.create([
                       {
                            name: 'attribute',
                            type: 'string'
                        },
                        {
                            name: 'id',
                            type: 'string'
                        }
                    ]);
                     var selected =Ext.getCmp('vdc_private_grid').getSelections();
                     Ext.getCmp('unassigned').enable();
                     Ext.getCmp('none').enable();  
                     if(selected.length>1)
                     {
                        Ext.getCmp('cms_cp_pub_ip_pool_panel').show();
                    
                    }   
                     Ext.getCmp('ip_pool_combo').store.removeAll();
                     for (i=0;i< selected.length;i++){
                            var new_record=new ex_str({
                                name: selected[i].json.dflt,
                                id: selected[i].json.id
                            });
                            Ext.getCmp('ip_pool_combo').store.insert(i,new_record);
                     }
                    
                     
                },
               rowdeselect:function(sel_model, index, record){
                         var selected =Ext.getCmp('vdc_private_grid').getSelections();
                         //alert("Length"+selected.length);
                         if(selected.length == 0)
                         {
                             Ext.getCmp('unassigned').disable();
                             Ext.getCmp('none').disable();
                             //Ext.getCmp('ip_pool_combo').hide();              
                         }
                         else if(selected.length == 1)
                         {
                             Ext.getCmp('cms_cp_pub_ip_pool_panel').hide();
                             //lbl_combo=Ext.getCmp('ip_pool_combo').fieldLabel
                             //lbl_combo.hide();
                         }
                         Ext.getCmp('ip_pool_combo').store.remove(Ext.getCmp('ip_pool_combo').store.getAt(index));
                         Ext.getCmp('ip_pool_combo').setValue('');
                 }
           }

     });

    var vdc_private_json_store = new Ext.data.JsonStore({
        //url:'/cloud_network/get_private_network_list_for_vm_provision?&vdcid='+vdcid,
        url:url,
        root:'rows',
        fields: ['dflt','nated','IP Details', 'selected'],
        successProperty:'success',
        listeners:{
            loadException:function(obj,opts,res,e){
                 var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            },
            load:function(store,opts,res,e){
                if(mode != "PROVISION") {   
                                
                    for (var i=0;i<store.getCount();i++){
                        //alert("selected-private----:"+store.getAt(i).get('selected'));
                        if(store.getAt(i).get('selected') == true)
                        {
                            vdc_private_grid.getSelectionModel().selectRow(i,true);
                        }
                    }
                        
                }
                else if(store.getCount() == 1){
                      vdc_private_grid.getSelectionModel().selectAll();
                      var ex_str = Ext.data.Record.create([
                               {
                                    name: 'attribute',
                                    type: 'string'
                                },
                                {
                                    name: 'id',
                                    type: 'string'
                                }
                       ]);
                     var new_record=new ex_str({
                            name: opts[0].json.dflt,
                            id: opts[0].json.id
                     });
                     Ext.getCmp('ip_pool_combo').store.insert(0,new_record);
                     Ext.getCmp('ip_pool_combo').setValue(new_record.data.name);
                }
            }
        }
    });
    vdc_private_json_store.load();
    var vdc_private_grid = new Ext.grid.GridPanel({
        id :'vdc_private_grid',
        stripeRows:true,
        frame:false,
        width:'100%',
        //autoExpandMin:100,
        height:95,
        //autoExpandColumn:1,
        autoScroll:true,
        enableHdMenu:false,
        selModel:vdc_nw_selmodel,
        tbar:[vdc_nw_label],
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        store:vdc_private_json_store,
          columns: [
              vdc_nw_selmodel,
               {header: "默认", width: 120, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'dflt'},
               {header: "id", width: 180, sortable: false,hidden:true, css:'font-weight:bold; color:#414141;',dataIndex:'id'},
               {header: "IP详情", width: 200, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'IP Details'},
                {header: "Nated", width: 60, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'nated'}
        ]
    });
    
    return vdc_private_grid;
}

function get_private_nw_combo(){
        var label_combo = new Ext.form.Label({
            html:'<div class =toolbar_hdg'+_('池信息')+'</br></div>'
        })
        var dummyStore = new Ext.data.JsonStore({
            id:'temp_1',
            fields: [
                        {name:''}
                     ]
        });
        var vm_ip_pool_combo=new Ext.form.ComboBox({
            fieldLabel: _('私有网络'),
            allowBlank:false,
            width: 150,

            store:dummyStore,
            id:'ip_pool_combo',
            forceSelection: false,
            triggerAction:'all',
            emptyText :_("选择IP "),
            minListWidth:150,
            displayField:'name',
            valueField:'id',
            mode:'local',
            editable:false,
            listeners:{
                        select :function(){
                                }
                    }
        });
        var vm_ip_pool_panel = new Ext.Panel({
            height:60,
            labelWidth:120,
            id:"cms_cp_pub_ip_pool_panel",
            layout:"form",
            frame:false,
            width:420,
            autoScroll:true,
            border:false,
            bodyBorder:false,
            bodyStyle:'padding:3px 3px 3px 3px',
            items:[vm_ip_pool_combo]
       });

       return  vm_ip_pool_panel;
}




