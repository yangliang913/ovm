/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function VDCConfig(node_id,node_name,node_type,mode,type,cp_id){
    var url = "/cloud/get_cp_feature_set?cp_type="+type;
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                
                VDCConfigSettings(node_id,node_name,node_type,mode, response.info,type,cp_id);

            }else{
                Ext.MessageBox.alert(_("失败"),_("无法加载供应商."));
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });

}

function VDCConfigSettings(node_id,node_name,node_type,mode, cp_feature,cp_type,cp_id){
       var vdc_treePanel= new Ext.tree.TreePanel({
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
                process_panel(vdc_card_panel,vdc_treePanel,id.substr(4,id.length),"treepanel");
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
                vdc_treePanel.getNodeById("node5").select();
            }
        }
    });
    var generalNode = new Ext.tree.TreeNode({
        text: _('常规'),
        draggable: false,
        id: "node5",
        icon:'icons/vm-general.png',
        nodeid: "general",
        leaf:false,
        allowDrop : false
       // cls:"labelcolor"
    });
    var userNode = new Ext.tree.TreeNode({
        text: _('用户'),
        draggable: false,
        id: "node6",
        nodeid: "user",
        icon:'icons/vm-storage.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

    var regionNode = new Ext.tree.TreeNode({
        text: _('区域'),
        draggable: false,
        id: "node8",
        nodeid: "disk",
        icon:'icons/vm-storage.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
    var serviceNode = new Ext.tree.TreeNode({
        text: _('实例类型'),
        draggable: false,
        id: "node9",
        icon:'icons/vm-boot-param.png',
        nodeid: "bootparams",
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
    var quotaNode = new Ext.tree.TreeNode({
        text: _('配额'),
        draggable: false,
        id: "node10",
        icon:'icons/vm-storage.png',
        nodeid: "quota",
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

     var templateNode = new Ext.tree.TreeNode({
        text: _('模板'),
        draggable: false,
        id: "node11",
        nodeid: "cms_cp_template",
        icon:'icons/vm-storage.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

    var networkNode = new Ext.tree.TreeNode({
        text: _('网络'),
        draggable: false,
        id: "node12",
        icon:'icons/vm-storage.png',
        nodeid: "network",
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });


     var label_treepanel=new Ext.form.Label({
        html:'<div>'+'<br/></div><br/>'
    })
    var side_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:180,
        height:437,
        id:'side_panel',
        cls:'westPanel',
        items:[label_treepanel,vdc_treePanel]

    // card panel for all panels
    });
    rootNode.appendChild(generalNode);
    if(is_feature_enabled(cp_feature,stackone.constants.CF_REGION)){
        rootNode.appendChild(regionNode);
    } else {
        rootNode.appendChild(templateNode);
    }
    if(is_feature_enabled(cp_feature,stackone.constants.CF_SERVICE_OFFERING)){
        rootNode.appendChild(serviceNode);
    }
    if(is_feature_enabled(cp_feature,stackone.constants.CF_NETWORK)){
        rootNode.appendChild(networkNode);
    }
    rootNode.appendChild(quotaNode);
    rootNode.appendChild(userNode);
    vdc_treePanel.setRootNode(rootNode);
    
     var button_prev=new Ext.Button({
        id: 'move-prev',
        //text: _('Prev'),
        disabled: true,
        icon:'icons/2left.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
//                closeWindow();
                process_panel(vdc_card_panel,vdc_treePanel,-1);
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
                process_panel(vdc_card_panel,vdc_treePanel,1);
//                cloud_card_panel.activeItem =0
            }
        }
    });

   var general_panel=create_vdcgeneral_panel(node_id,node_name,node_type,mode,cp_feature,cp_type,cp_id);
   if(is_feature_enabled(cp_feature,stackone.constants.CF_NETWORK)){
        var network_panel = create_vdc_network_panel(node_id, mode)
   }
   var user_panel=create_user_details(mode,node_id);
   var region_details_panel=create_accountregion_panel(mode,cp_feature);
   var service_details_panel=create_instancetype_foraccount_panel();
   var quota_details_panel=create_quota_panel('','',node_id);
   var template_panel = create_template_panel(mode,node_id);
   var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('确定'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {                
                    submit_vdc_details(user_panel,node_id,node_type,mode,win,cp_feature);
//                win.close();
            }
        }
    });

    var button_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                win.close();
            }
        }
     });


    var vdc_card_panel=new Ext.Panel({
        width:"100%",
        height:435,
        layout:"card",
        id:"vdc_card_panel",
        activeItem:0,
        cls: 'whitebackground',
        border:false,
        bbar:[
        {
            xtype: 'tbfill'
        },button_prev,button_next,button_ok,button_cancel]
//        ,items:[general_panel]
    //
    });

//    rootNode.appendChild(general_Node);

    var right_panel=new Ext.Panel({
        id:"right_panel",
        width:500,
//         width:448,
        height:600,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        bodyStyle:'padding:5px 5px 5px 5px'
//        items:[change_settings]
        ,listeners: {
            afterlayout: function() {//alert("afterlayout"+card_panel.activeItem);
                vdc_card_panel.getLayout().setActiveItem("panel5");
            }
         }
    });


//     Side panel is removed now to get the genral tab only.....

    var outerpanel=new Ext.FormPanel({
//        width:498,
        width:900,
        height:490,
        autoEl: {},
        layout: 'column',
//         items:[side_panel,right_panel]
        items:[side_panel,right_panel]

    });
   
    vdc_card_panel.add(general_panel);
    if(is_feature_enabled(cp_feature,stackone.constants.CF_NETWORK)){
        vdc_card_panel.add(network_panel);
    }
    vdc_card_panel.add(user_panel);
    vdc_card_panel.add(region_details_panel);
    vdc_card_panel.add(service_details_panel);
    vdc_card_panel.add(quota_details_panel);
    vdc_card_panel.add(template_panel);
    
    right_panel.add(vdc_card_panel);

     if(mode=="EDIT"){
         var win=new Ext.Window({
        title:"编辑虚拟数据中心",
        width: 700,
//         width: 645,
//        layout:'fit',
        height: 475,
        modal: true,
        resizable: false,
        closable:true
    });
     }
     else{
          var win=new Ext.Window({
        title:"新建虚拟数据中心",
        width:700, //515,
//         width: 645,
//        layout:'fit',
        height:475, 
        modal: true,
        resizable: false,
        closable:true
    });
     }
    

    win.add(outerpanel);
    win.show();

}


function create_vdcgeneral_panel(node_id,node_name,node_type,mode,cp_feature,cp_type,cp_id){


    var name_textbox = new Ext.form.TextField({
        fieldLabel: '名称',
        name: 'vdc_name',
        id: 'vdc_name',
        width:270,
        disabled:(mode=="EDIT"),
        labelSeparator:" ",
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {

            }
        }
    });


    var account_id="";

    var desc_textbox = new Ext.form.TextField({
        fieldLabel: '说明',
        name: 'vdc_desc',
        id: 'vdc_desc',
        width:270,
        labelSeparator:" ",
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {

            }
        }
    });
     if(!is_feature_enabled(cp_feature,stackone.constants.CF_REGION)){

        var label_vdc=new Ext.form.Label({
            html:'<div>'+_("指定这个虚拟数据中心的名称和说明.")+'<br/></div><br/>'
        });
     }
     else{
        var label_vdc=new Ext.form.Label({
            html:'<div>'+_("指定虚拟数据中心名称、说明和账户名称.")+'<br/></div><br/>'
        });
     }

    var label_general=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("常规 ")+'</div>',
        id:'label_vm'
    });


    var acc_textbox = new Ext.form.TextField({
        name: 'vdc_desc',
        id: 'acc_id',
        hidden :true,
        width:270,
        labelSeparator:" ",
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {

            }
        }
    });
    
     var cpid_new = cp_id;
        var get_cp_url =  "/cloud/get_cloud_providers?cp_type="+cp_type;
        if (mode == 'EDIT')
            get_cp_url = get_cp_url+'&vdc_id='+node_id;
    	var cloudprovider_store =new Ext.data.JsonStore({
            url:get_cp_url,
            root: 'info',
            id:"cloudprovider_store",
            fields: ['name','value'],
            successProperty:'success',
            sortInfo:{
                field:'name',
                direction:'ASC'
            },
            listeners:{
                load:function(obj,opts,res,e){
                    if (mode=="EDIT"){
                    	var cp_id = cloudprovider_store.getAt(0).get('value');
                    	cloud_provider.setValue(cp_id);
                    	cloud_provider.fireEvent('select',cloud_provider,cloudprovider_store.getAt(0),0);
                    }
                    else{
                        cloud_provider. setValue(cpid_new);
                        for (var i =0 ; i < cloudprovider_store.getCount();i++){
                            var rec = cloudprovider_store.getAt(i);
                            if (rec.get('value')==cpid_new){
                                cloud_provider.fireEvent('select',cloud_provider,rec,i);
                                break;
                            }                            
                        }
                    }
                    
                },
                loadexception:function(obj,opts,res,e){
                    var store_response=Ext.util.JSON.decode(res.responseText);
                    Ext.MessageBox.alert(_("错误"),store_response.msg);
                }
            }
        });
        cloudprovider_store.load();
        var width=250;
        var labelWidth=80;
        var cloud_provider = new Ext.form.ComboBox({
            id: 'cloud_provider_name',
            fieldLabel: _(stackone.constants.IAAS),
            allowBlank:false,
            triggerAction:'all',
            emptyText :_("选择"+stackone.constants.IAAS),
            store:cloudprovider_store,
            width:width,
            displayField:'name',
            editable:false,
            valueField:'value',
            labelWidth:labelWidth,
//            labelStyle: 'font-weight:bold;',
            typeAhead: true,
            minListWidth:50,
            labelSeparator:" ",
            mode:'local',
            forceSelection: true,
            selectOnFocus:true,
            listeners: {
                select: function(combo, record, index){
                    if(mode=="EDIT"){
                        accountname_store.load({

                            params:{
                                cp_id:cloud_provider.getValue(),
                                vdc_id:node_id
                            }
                        });
                    }
                    else{
                         accountname_store.load({

                            params:{
                                cp_id:cloud_provider.getValue()

                            }
                        });
                    }

                    if(is_feature_enabled(cp_feature,stackone.constants.CF_NETWORK)){
                        //// Defined Networks ////
                        var defined_network_store = Ext.getCmp("vdc_defined_network_grid").getStore();
                        var attr = new Object();
                        attr['cp_id'] = cloud_provider.getValue();
                        if (mode == 'EDIT')
                            {
                                attr['vdc_id'] = node_id;
                            }
                        defined_network_store.load({
                                                    params : attr
                                                   });
                    }


                    if(!is_feature_enabled(cp_feature,stackone.constants.CF_ACCOUNT)){
                        account_id   = acc_textbox.getValue();
                        var cp_id = cloud_provider.getValue();
                        if (mode=="EDIT"){

                            Ext.getCmp("quota_grid").getStore().load({
                                params:{
                                    cp_id:cp_id,
                                    vdc_id:node_id,
                                    account_id:account_id
                                }
                            });
                            Ext.getCmp("template_grid").getStore().load({
                                params:{
                                    cp_id:cp_id,
                                    vdc_id:node_id

                                }
                            });
                            Ext.getCmp("regacc_grid").getStore().load({
                                params:{
                                    cp_id:cp_id,
                                    vdc_id:node_id,
                                    account_id:account_id
                                }

                            });
                            Ext.getCmp("seroff_grid").getStore().load({
                                params:{
                                    cp_id:cp_id,
                                    vdc_id:node_id,
                                    account_id:account_id
                                }
                            });

                        }else{

                            Ext.getCmp("quota_grid").getStore().load({
                                params:{
                                    cp_id:cp_id
                                }
                            });

                            Ext.getCmp("regacc_grid").getStore().load({
                                params:{
                                    cp_id:cp_id,
                                    vdc_id:'',
                                    account_id:account_id
                                }
                            });

                            Ext.getCmp("template_grid").getStore().load({
                                params:{
                                    cp_id:cp_id,
                                    vdc_id:''

                                }
                            });

                            Ext.getCmp("seroff_grid").getStore().load({
                                params:{
                                    cp_id:cp_id
                                }
                            });
                        }
                    }

                }
        }
                        
        });

        var accountname_store =new Ext.data.JsonStore({
        	url: "/cloud/get_account_forcombo",
            root: 'info',
            fields: ['name','value'],
            id:'acc_store',
            successProperty:'success',
            sortInfo:{
                field:'name',
                direction:'ASC'
            },
            listeners:{
                load:function(obj,opts,res,e){
                    if((account_name.getStore().getCount()==1) && (mode!="EDIT")){
                        account_name.setValue(account_name.getStore().getAt(0).get('value'));
                        account_name.fireEvent('select',account_name,account_name.getStore().getAt(0),0);
                        account_panel.hide();

                    }
                	var record = '';
                    if (mode=="EDIT"){
                    	var acc_name = accountname_store.getAt(0).get('name');
                    	var acc_id = accountname_store.getAt(0).get('value');
                    	account_name.setValue(acc_id);
                    	account_name.fireEvent('select',account_name,accountname_store.getAt(0),0);
                    }
                },
                loadexception:function(obj,opts,res,e){
                    var store_response=Ext.util.JSON.decode(res.responseText);
                    Ext.MessageBox.alert(_("错误"),store_response.msg);
                }
            }
        });
       cloud_provider.hide();
       cloud_provider.hideLabel=true;
        
        var account_name = new Ext.form.ComboBox({
            id: 'cloud_account_name',
            fieldLabel: _('账户名称'),
            allowBlank:false,
            triggerAction:'all',
            emptyText :_("选择账户"),
            store:accountname_store,
            width:width,
            displayField:'name',
            editable:false,
            valueField:'value',
            labelWidth:40,
//            labelStyle: 'font-weight:bold;',
            typeAhead: true,
            minListWidth:50,
            labelSeparator:" ",
            mode:'local',
            forceSelection: true,
            selectOnFocus:true,
            listeners: {
            	    
                    select: function(combo, record, index){
                    	account_name = record['data']['name'];
                    	account_id   = combo.getValue();
                    	var cp_id = cloud_provider.getValue();
                    	Ext.getCmp("cloud_account_name").setValue(account_id);
                        if (mode=="EDIT"){
                              Ext.getCmp("quota_grid").getStore().load(
                              {
                                    params:{
                                        cp_id:cp_id,
                                        vdc_id:node_id,
                                        account_id:account_id
                                    }
                                }
                              );
                             Ext.getCmp("regacc_grid").getStore().load(
                                 {
                                    params:{
                                        cp_id:cp_id,
                                        vdc_id:node_id,
                                        account_id:account_id
                                    }

                                 }
                             );
                              Ext.getCmp("seroff_grid").getStore().load({
                                     params:{
                                        cp_id:cp_id,
                                        vdc_id:node_id,
                                        account_id:account_id
                                     }
                              });

                        }else{
                        	   
                                Ext.getCmp("quota_grid").getStore().load({
                                    params:{
                                    	cp_id:cp_id
                                    }
                                });

                                 Ext.getCmp("regacc_grid").getStore().load({
                                     params:{
                                        cp_id:cp_id,
                                        vdc_id:'',
                                        account_id:account_id
                                     }
                                });

                                Ext.getCmp("seroff_grid").getStore().load({
                                     params:{
                                        cp_id:cp_id
                                     }
                                });
                        }

                    }

            }
        })

        var account_panel=new Ext.Panel({
            height:50,
            id:"account_panel",
            layout:"form",
            frame:false,
            width:'90%',
            cls: 'whitebackground',
            border:false,
            bodyBorder:false,
//            bodyStyle:'padding:5px 5px 5px 5px',
            items:[account_name]
        });
//        if(!is_feature_enabled(cp_feature,stackone.constants.CF_REGION)){
//            var label_acc=new Ext.form.Label({
//                html:'<div>'+_("Select an "+stackone.constants.IAAS+".")+'<br/></div><br/>'
//            });
//        }
//        else{
//            var label_acc=new Ext.form.Label({
//                html:'<div>'+_("Select an "+stackone.constants.IAAS+" and specify account details to be used.")+'<br/></div><br/>'
//            });
//
//        }
//        var inform_label=new Ext.form.Label({
//            html:'<div class="backgroundcolor" width="150"><b>Account Information</b></div>'
//         });

//        var label_account=new Ext.form.Label({
//            html:'<div><b>'+_(stackone.constants.IAAS)+'</b><br></div>'
//        });
        var newdummy_space1=new Ext.form.Label({
            html:_('&nbsp;&nbsp;<div style="width:80px"/>')
        });
        var dummy_space1 = new Ext.form.Label({
        	html:_('&nbsp;<div style="width:80px;></div>')
        });
        var dummy_space2 = new Ext.form.Label({
        	html:_('&nbsp;<div style="width:80px;></div>')
        });

        var general_panel=new Ext.Panel({
            height:450,
            id:"panel5",
            layout:"form",
            frame:false,
            width:'70%',
            cls: 'whitebackground',
            autoScroll:true,
            border:false,
            bodyBorder:false,
            bodyStyle:'padding:5px 5px 5px 5px',
            tbar:[label_general],
            items:[label_vdc, name_textbox,desc_textbox,acc_textbox,cloud_provider,
                   account_panel]//,account_name
        });
//        inform_label.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_ACCOUNT));
        account_panel.setVisible(is_feature_enabled(cp_feature,stackone.constants.CF_ACCOUNT));
        if(account_name.getStore().getCount()==0){
            account_panel.hide();

        }
//        general_panel.add(account_panel);
        if (mode == "EDIT"){
        
            var url="/cloud/get_vdcdetails_foredit?vdc_id="+node_id;
            var ajaxReq=ajaxRequest(url,0,"POST",true);
                    ajaxReq.request({
                        success: function(xhr) {//alert(xhr.responseText);
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                name_textbox.setValue(response.vdc_detail.vdc_name);
                                desc_textbox.setValue(response.vdc_detail.vdc_desc);
                                acc_textbox.setValue(response.vdc_detail.account_id);
                                if(is_feature_enabled(cp_feature,stackone.constants.CF_VDC_PRIVATE_NW)){
                                //// create_default_network ////
                                var create_default_network = Ext.getCmp("create_default_network_checkbox");
                                var create_private_network = Ext.getCmp("create_private_network_checkbox");
                                create_default_network.setValue(response.vdc_detail.create_default_network);
                                create_private_network.setValue(response.vdc_detail.create_private_network);
                                if (create_default_network.getValue()){
                                    create_default_network.disable();
                                }
                                }
                               }else{
                                Ext.MessageBox.alert(_("失败"),response.msg);
                            }
                        },
                        failure: function(xhr){
                            Ext.MessageBox.alert( _("失败") , xhr.statusText);
                        }
            });

        //var account_grid=get_account_detailsgrid(node_id,account_id)
//        general_panel.add(account_grid);

    }
        
    if (mode=="EDIT"){
        cloud_provider.setDisabled(true);
        account_name.setDisabled(true);
    }
    return general_panel;

}



/////////// Network ////////////
function create_vdc_network_panel(node, mode)
{

    var defined_network_selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });

    var tlabel_private_network=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("私有网络")+'<br/></div>'
    });

     var label_defined_network=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("定义的网络")+'<br/></div>'
    });

    var tlabel_desc_network=new Ext.form.Label({
        html:'<div>'+_( "请从下面列表选择可用网,以赋予虚拟数据中心使用.")+'<br/></div>'
    });

    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space2=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });


   var create_default_network_checkbox_label=new Ext.form.Label({
        html: _('创建默认的虚拟数据中心网络')
    });

   var create_private_network_checkbox_label=new Ext.form.Label({
        html: _('允许创建更多的私有网络')
    });


   var create_default_network_checkbox= new Ext.form.Checkbox({
        name: 'create_default_network_checkbox',
        id: 'create_default_network_checkbox',
        checked:true,
        width:20,
        listeners:{
            check:function(field,checked){
//                if(checked){
//                }
            }
        }
    });



   var create_private_network_checkbox= new Ext.form.Checkbox({
        name: 'create_private_network_checkbox',
        id: 'create_private_network_checkbox',
        checked:false,
        width:20,
        listeners:{
            check:function(field,checked){
//                if(checked){
//                }
            }
        }
    });


    var defined_network_store = new Ext.data.JsonStore({
        url: '/cloud_network/get_vdc_defined_networks',
        root: 'rows',
        fields: ['id', 'name', 'vlan_id', 'ip_range', 'selected'],
        successProperty:'success',
        listeners:{
                load:function(store)
                 {
                    if (mode=='EDIT')
                        {
                            for (var i=0;i<store.getCount();i++){
                                if(store.getAt(i).get('selected') == true)
                                    {
                                        defined_network_grid.getSelectionModel().selectRow(i,true);
                                    }
                            }
                        }
                        else{
                            defined_network_grid.getSelectionModel().selectAll();
                        }
                    }
            }
        });


    var defined_network_grid = new Ext.grid.GridPanel({
        store: defined_network_store,
        enableHdMenu:false,
        selModel:defined_network_selmodel,
        id:'vdc_defined_network_grid',
        columns: [
                    defined_network_selmodel,
                    {
                        id       :'id',
                        header   : '编号',
                        width    : 140,
                        sortable : true,
                        dataIndex: 'id',
                        hidden : true
                    },
                    {
                        header   : '名称',
                        width    : 150,
                        sortable : true,
                        dataIndex: 'name',
                        hidden : false
                    },
                    {
                        header   : 'VLAN ID',
                        width    : 120,
                        sortable : true,
                        dataIndex: 'vlan_id',
                        hidden : false
                    },
                    {
                        header   : 'IP范围',
                        width    : 180,
                        sortable : true,
                        dataIndex: 'ip_range',
                        hidden : false
                    }
                ],

        stripeRows: true,
        height: 215,
        width:485,
        tbar:[label_defined_network,{
            xtype: 'tbfill'
             }]
           ,listeners: {
                            ///
                        }
    });


     var create_default_network_panel=new Ext.Panel({
        id:"create_default_network_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:false,
        border:false,
        bodyBorder:false,
        autoHeight:true,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[create_default_network_checkbox, dummy_space1, create_default_network_checkbox_label]
    });


     var create_private_network_panel=new Ext.Panel({
        id:"create_private_network_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:false,
        border:false,
        bodyBorder:false,
        autoHeight:true,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[create_private_network_checkbox, dummy_space2, create_private_network_checkbox_label]
    });


    var private_network_panel = new Ext.Panel({
        height:70,
        id:"vdc_private_network_panel",
        layout:"column",
        frame:false,
        width:490,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        autoHeight:true,
        //        bodyStyle:'padding:5px 5px 5px 5px',
        buttonAlign : 'center',
        tbar:[tlabel_private_network],
        items:[create_default_network_panel,
                create_private_network_panel
            ]
    });


    var defined_network_panel = new Ext.Panel({
        height:290,
        id:"vdc_defined_network_panel",
        layout:"form",
        frame:false,
        width:490,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        buttonAlign : 'center',
//        tbar:[tlabel_network],
        items:[tlabel_desc_network, defined_network_grid]
    });


    var network_details_panel=new Ext.Panel({
        border:false,
        id:"panel12",
//        layout:"form",
        width:465,
        height:420,
        frame:false,
        labelWidth:220,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[private_network_panel, defined_network_panel]
    });

    return network_details_panel;
}


function create_user_details(mode,vdc_id){
	var remove_uidstr="";
        var delete_uidstr="";
    
    var group_hidden=true;
    if(mode=="EDIT"){        
        group_hidden=false;
    }
    var user_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("用户编号"),
        width: 0,
        dataIndex: 'userid',
        menuDisabled: false,
        hidden:true
    },
    {
        header: _("用户名"),
        width: 155,
        dataIndex: 'username',
        sortable:false
    },
    {
        header: _("名称"),
        width: 155,
        dataIndex: 'fnandln',
        sortable:false,
        hidden:false
    },
    {
        header: _("姓"),
        width: 0,
        sortable: true,
        dataIndex: 'fname',
        hidden:true
    },
     {
        header: _("名"),
        width: 0,
        sortable: true,
        dataIndex: 'lname',
        hidden:true
    },
    {
        header: _("昵称"),
        width: 0,
        sortable: true,
        dataIndex: 'nname',
        hidden:true
    },
    {
        header: _("密码"),
        width: 0,
        sortable: true,
        dataIndex: 'password',
        hidden:true
    },
    {
        header: _("重新输入一次密码"),
        width: 0,
        sortable: true,
        dataIndex: 'retypepassword',
        hidden:true
    },
     {
        header: _("邮箱"),
        width: 0,
        sortable: true,
        dataIndex: 'email',
        hidden:true
    },
     {
        header: _("电话 "),
        width: 0,
        sortable: true,
        dataIndex: 'phone',
        hidden:true
    },
    {
        header: _("状态"),
        width: 0,
        sortable: true,
        dataIndex: 'status',
        hidden:true
    },
     {
        header: _("角色"),
        width: 152,
        sortable: true,
        dataIndex: 'type1',
        hidden:!group_hidden
    },
    {
        header: _("角色"),
        width: 152,
        sortable: false,
        dataIndex: 'group',
        hidden:group_hidden
    },
    {
        header: _("hrole"),
        width: 165,
        sortable: false,
        dataIndex: 'hiddenrole',
        hidden:true
    },
    {
        header: _("hides"),
        width:160,
        sortable: false,
        dataIndex: 'hideselection',
        hidden:true
    },
    {
        header: _("edited"),
        width:160,
        sortable: false,
        dataIndex: 'edited',
        hidden:true
    },
    {
        header: _("Canremove"),
        width:0,
        sortable: false,
        dataIndex: 'canremove',
        hidden:true
    }
    ]);
    var userid_textbox = new Ext.form.TextField({
        
        name: 'vdc_name',
        id: 'uid',
        width:0,
        labelSeparator:" ",
        allowBlank:true,
        hidden:true


    });
    var delete_userid_textbox = new Ext.form.TextField({

        name: 'deleteuser',
        id: 'delete',
        width:0,
        labelSeparator:" ",
        allowBlank:true,
        hidden:true


    });

     var user_store =new Ext.data.JsonStore({
        url: "/cloud/get_vdc_users",
        root: 'rows',
        fields:['userid','username','fnandln','fname','lname','nname','email','phone','status','group','hiddenrole','canremove'], //['userid','username', 'name', 'group'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    if(mode=="EDIT"){
        user_store.load({
            params:{
                vdc_id:vdc_id
            }
        });
    }


    var prov_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });


    var user_add_button=new Ext.Button({
        id: 'user_add',
        text: _('添加'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
             click: function(btn) {
                var w=new Ext.Window({
                    title :'用户列表 ',
                    width :695,
                    height:435,
                    modal : true,
                    resizable : false
                });
               w.add(creat_user_selection(mode,vdc_id,user_grid,w));
               w.show();
             }
        }
    });


    var user_new_button=new Ext.Button({
        id: 'user_new',
        text: _('新建'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var w=new Ext.Window({
                    title :'新建用户',
                    width :370,
                    height:440,
                    modal : true,
                    resizable : false
                });
                w.add(VDCUserDetailsPanel(user_grid,'NEW',null,w));
                w.show();
            }
        }
    }) ;
     var user_remove_button=new Ext.Button({
        id: 'user_remove',
        text: _('移除'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(!user_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从用户列表选择一条记录"));
                    return false;
                }
                var edit_rec=user_grid.getSelectionModel().getSelected();
                var remove_uid=edit_rec.get("userid");
                var username=edit_rec.get("username");
                var canremove=edit_rec.get("canremove");
                if(canremove==true){
                    Ext.MessageBox.confirm(_("确认"),_("确定要从stackone数据库删除用户:")+username+"吗?", function (id){
                    if(id=='yes'){
                        user_grid.getStore().remove(edit_rec);
                        if(delete_uidstr!=""){
                           delete_uidstr+= ",";
                       }
                       remove_uidstr+= "{"+"'user_id':"+'\''+remove_uid+'\''+"},";
                    delete_userid_textbox.setValue(remove_uidstr);
                    }
                });
                
                }
                else{
                    Ext.MessageBox.confirm(_("确认"),_("确定要从虚拟数据中心移除用户:")+username+"吗?", function (id){
                    if(id=='yes'){
                        user_grid.getStore().remove(edit_rec);
                        if(remove_uidstr!=""){
                           remove_uidstr+= ",";
                       }
                       remove_uidstr+= "{"+"'user_id':"+'\''+remove_uid+'\''+"}";
                    userid_textbox.setValue(remove_uidstr);
                    }
                });

                }
                
                
            }
        }
    });
    var type="cloud";
     var user_edit_button= new Ext.Button({
       id: 'user_edit',
        text: _('编辑'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                
                if(!user_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从用户列表选择一条记录"));
                    return false;
                }
                var edit_rec=user_grid.getSelectionModel().getSelected();
                
                var w=new Ext.Window({
                    title :_('编辑用户'),
                    width :370,
                    height:440,
                    modal : true,
                    resizable : false
                });
                w.add(VDCEdituserDetailsPanel(user_grid,mode,edit_rec,w,type));
                w.show();


            }
        }
    });

    var lableuser=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("用户")+'</div>',
        id:'label_user'
    });

   var user_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });
    
    var user_grid = new Ext.grid.EditorGridPanel({
        store: user_store,
        id: 'user_grid',
        stripeRows: true,
        colModel:user_columnModel,
        frame:false,
        border: false,
        selModel:user_selmodel,
        //autoExpandColumn:1,
        autoscroll:true,
        height:320,
        width:'100%',
        clicksToEdit:2,
        enableHdMenu:false,
         tbar:[lableuser,
            _
        ,{
            xtype: 'tbfill'},user_add_button,'-',user_new_button,'-',user_edit_button,'-',user_remove_button,'-'],
    listeners:{
            rowdblclick:function(grid, rowIndex, e){
                user_edit_button.fireEvent('click',user_edit_button);
            }
        }
    });
//    user_grid.add(userid_textbox);
    
     var user_desc=new Ext.form.Label({
        html:'<div>'+_("请添加用户并赋予此虚拟数据中心访问或控制权限.")+'<br/></div>'
    });
    var user_panel=new Ext.Panel({
        height:'100%',
        id:"panel6",
        layout:"form",
        frame:false,
        width:'100%',
        cls: 'whitebackground',
//        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[user_desc,userid_textbox,delete_userid_textbox,user_grid]
        ,listeners:{
            show:function(p){
                if(user_store.getCount()>0){
                    user_store.sort('username','ASC');
                }
            }
        }

    });

    return user_panel;

}
function creat_user_selection(mode,vdc_id,user_grid,w){

var add_store=new Ext.data.JsonStore({
        url: "/model/get_cloud_users_list?vdc_id="+vdc_id,
        root: 'rows',
        fields: ['userid','username','name','fname','lname','nname','email','phone','status','rol','vdc','sts'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }

       


        }
    });
     var user_role_store = new Ext.data.JsonStore({
        url: '/model/get_user_role_map',
        root: 'user_role',
        fields: ['id','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    user_role_store.load();

        //add_store.load();
        //if(mode=="EDIT"){
        add_store.load();

   // }
   
      var add_columnModel = new Ext.grid.ColumnModel([
      {
        header: _(""),
        width: 0,
        dataIndex: 'sts',
        menuDisabled: false,
        hidden:true
    },

    {
        header: _("用户编号"),
        width: 0,
        dataIndex: 'userid',
        menuDisabled: false,
        hidden:true
    },
    {
        header: _("用户名"),
        width: 150,
        dataIndex: 'username',
        sortable:true
    },
    {
        header: _("名称"),
        width: 150,
        sortable: true,
        dataIndex: 'name'
    },
    {
        header: _("姓"),
        width: 0,
        sortable: true,
        dataIndex: 'fname',
        hidden:true
    },
     {
        header: _("名"),
        width: 0,
        sortable: true,
        dataIndex: 'lname',
        hidden:true
    },
    {
        header: _("昵称"),
        width: 0,
        sortable: true,
        dataIndex: 'nname',
        hidden:false
    },
    {
        header: _("密码"),
        width: 0,
        sortable: true,
        dataIndex: 'password',
        hidden:true
    },

     {
        header: _("邮箱"),
        width: 0,
        sortable: true,
        dataIndex: 'email',
        hidden:true
    },
     {
        header: _("电话"),
        width: 0,
        sortable: true,
        dataIndex: 'phone',
        hidden:true
    },
    {
        header: _("状态"),
        width: 0,
        sortable: true,
        dataIndex: 'status',
        hidden:true
    },

    {
        header: _("角色"),
        width: 165,
        sortable: false,
        dataIndex: 'rol',
        hidden:true
    },
   
    {
        header: _("现有用户"),
        width: 150,
        sortable: true,
//        hidden:true,
        dataIndex: 'vdc'
    },
     {
        header: _("选择角色"),
        width: 85,
        sortable: false,
        dataIndex: 'role',

        editor:new Ext.form.ComboBox({

            typeAhead: true,
            store:user_role_store,
            emptyText :_("选择角色"),
            triggerAction: 'all',
            displayField:'value',
            valueField:'id'

            
            ,mode:'local',
            listeners:{
            	beforerender :function(field){
                    //field.disable();

                }
            }
            

     })

    },{header:_("选择"),width: 55, sortable: true, dataIndex: 'is_selected', renderer:select_user_checkbox}

    ]);

    var labuserlist=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("用户列表 ")+'</div>',
        id:'label_user'
    });
     var btn_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('确定'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                         
                          var rep_rec1 = Ext.data.Record.create([

                           {
                            name: 'userid',
                            type: 'string'
                          },
                          {
                            name: 'username',
                            type: 'string'
                          }
                          ,{
                            name: 'fnandln',
                            type: 'string'
                          },
                          {
                            name: 'fname',
                            type: 'string'
                          },
                          {
                            name: 'lname',
                            type: 'string'
                          },
                          {
                            name: 'nname',
                            type: 'string'
                          },

                          {
                            name: 'email',
                            type: 'string'
                          },
                          {
                            name: 'phone',
                            type: 'string'
                          },
                          {
                            name: 'status',
                            type: 'string'
                         //   hidden: true
                          },

                          {
                            name: 'rol',
                            type: 'string'
                           // hidden: true
                          }
                          ,{
                            name: 'group',
                            type: 'string'
                          }
                         
                          ,{
                              name: 'type1',
                              type: 'string'

                          }
                           ,{
                            name: 'hideselection',
                            type: 'string'
                          }


                          ]);
                        


                        var store=user_add_grid.getStore();
                        var user_grid1=user_grid.getStore();
                        var user_count=user_grid.getStore().getCount();
                     

                        var user_stor=user_add_grid.getStore();

                        var rec_count=user_add_grid.getStore().getCount();

                      if(mode=='EDIT'){
                      for(var i=0;i<rec_count;i++){
                      if(user_stor.getAt(i).get('sts')=='False'&&user_stor.getAt(i).get('is_selected')==true&&(user_stor.getAt(i).get('role')==""||user_stor.getAt(i).get('role')==null)){
                          Ext.MessageBox.alert(_("警告"),"请选择你要添加用户的角色.");return;
                      }
                      }
                      }

                      if(mode=='NEW'){
                         for(var i=0;i<rec_count;i++){
                      if(user_stor.getAt(i).get('is_selected')==true&&(user_stor.getAt(i).get('role')==""||user_stor.getAt(i).get('role')==null)){
                          Ext.MessageBox.alert(_("警告"),"请选择你要添加用户的角色.");return;
                      }
                      }
                      }
                     
                      if(mode=='EDIT'){

                        for(var i=0;i<user_count;i++)
                                   {
                                       for(var j=0;j<rec_count;j++)
                                           { 
                                               
                                               
                                               if(user_stor.getAt(j).get('is_selected')==true&&user_stor.getAt(j).get('userid')==user_grid1.getAt(i).get('userid')&&user_stor.getAt(j).get('role')==user_grid1.getAt(i).get('group'))
                                                   {
                                                       
                                                       Ext.MessageBox.alert(_("Warning"),"Role already selected for :"+ user_stor.getAt(j).get('username'));return;
                                                   }
                                           }
                                   }

                                   
                      }
                      if(mode=='NEW'){
                          
                        for(var i=0;i<user_count;i++)
                                   {
                                       for(var j=0;j<rec_count;j++)
                                           { 


                                               if(user_stor.getAt(j).get('is_selected')==true&&user_stor.getAt(j).get('userid')==user_grid1.getAt(i).get('userid')&&user_stor.getAt(j).get('role')==user_grid1.getAt(i).get('type1'))
                                                   {

                                                       Ext.MessageBox.alert(_("警告"),"角色已经选定:"+ user_stor.getAt(j).get('username'));return;
                                                   }
                                           }
                                   }

                      }
                          
                    for(var i=0;i<rec_count;i++){                            
                            
                        if(mode=='EDIT'){
                            
                            if(user_stor.getAt(i).get('is_selected')==true&&user_stor.getAt(i).get('role')!=null){ //user_stor.getAt(i).get('sts')=='False'
                               
                                var new_entry=new rep_rec1({
                                        userid:user_stor.getAt(i).get('userid'),
                                        username:user_stor.getAt(i).get('username'),
                                        fnandln:user_stor.getAt(i).get('name'),
                                        fname:user_stor.getAt(i).get('fname'),
                                        lname:user_stor.getAt(i).get('lname'),
                                        nname:user_stor.getAt(i).get('nname'),
                                        email:user_stor.getAt(i).get('email'),
                                        phone:user_stor.getAt(i).get('phone'),
                                        status:user_stor.getAt(i).get('status'),
                                        rol:user_stor.getAt(i).get('rol'),
                                        group:user_stor.getAt(i).get('role'),
                                        hideselection:'true'
                                      });
                              remove_existing_user_row(user_grid, user_stor.getAt(i).get('userid'));
                              user_grid.getStore().insert(0,new_entry);
                            }
                        }
                        if(mode=='NEW'){
                            if(user_stor.getAt(i).get('is_selected')==true){
                            
                                var new_entry1=new rep_rec1({
                                        userid:user_stor.getAt(i).get('userid'),
                                        username:user_stor.getAt(i).get('username'),
                                        fnandln:user_stor.getAt(i).get('name'),
                                        fname:user_stor.getAt(i).get('fname'),
                                        lname:user_stor.getAt(i).get('lname'),
                                        nname:user_stor.getAt(i).get('nname'),
                                        email:user_stor.getAt(i).get('email'),
                                        phone:user_stor.getAt(i).get('phone'),
                                        status:user_stor.getAt(i).get('status'),
                                        rol:user_stor.getAt(i).get('rol'),
                                        type1:user_stor.getAt(i).get('role'),
                                        hideselection:'true'
                                      });
                                remove_existing_user_row(user_grid, user_stor.getAt(i).get('userid'));
                                user_grid.getStore().insert(0,new_entry1);
                            }

                        }

                    }
                       
                    w.close();
                }
        }
        
    });

    var btn_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
             w.close();
            }
        }
    });
    var user_add_grid = new Ext.grid.EditorGridPanel({
        store: add_store,
        id: 'add_grid',
        stripeRows: true,
        colModel:add_columnModel,
        frame:false,
        border: false,
//        selModel:selmodel,
        clicksToEdit:1,
        //autoExpandColumn:1,
        autoscroll:true,
        height:400,//125,
        width:675,             //'100%',

        enableHdMenu:false,
        
         bbar:[labuserlist,
        {
            xtype: 'tbfill'
        },btn_ok,btn_cancel],
         tbar:[labuserlist,_,

                 {
            xtype: 'tbfill'
        }]

    });


    var user_selection_panel=new Ext.Panel({
        height:600,
        id:"selection",
        layout:"form",
        frame:false,
        width:685,
        cls: 'whitebackground',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px'

    });

    user_selection_panel.add(user_add_grid);
    return user_selection_panel;

}
 

function remove_existing_user_row(user_grid, userid){
    var user_store = user_grid.getStore();
    for (var i= 0; i< user_store.getCount();i++){
        var rec = user_store.getAt(i);
        if (rec.get("userid") == userid){
            user_store.removeAt(i);
            return;
        }
    }
}

 function select_user_checkbox (value,params,record){
    var id = Ext.id();
    var cuserid;
    
    (function(){
        var cb = new Ext.form.Checkbox({
            renderTo: id,
            width:100,
            height:16,
            checked:value,
            value:false,
            listeners:{
                	beforerender:function(field){
 
                        if(record.get("sts")=='True'){
                        record.set("is_selected", true);
                        field.disable();
                        
                        }

                    },
                check:function(field,checked){
                  record.set("is_selected", checked);
                  
                }
            }
        });

//    cb.setDisabled(true);

    }).defer(5);
    return '<span id="' + id + '"></span>';
}


function submit_vdc_details(user_panel,node_id,node_type,mode,win,cp_feature){
    var user_object=new Object();
    var template_object=new Object();
    var infrastructure_object=new Object();
    var editeduser_object=new Object();
    var removed_user_object=new Object();
    var deleted_user_object=new Object();
//    user_object.

    var vdc_object=new Object();
    var account_object=new Object();

    var url="";

    vdc_object.name=Ext.getCmp("vdc_name").getValue();
    vdc_object.desc=Ext.getCmp("vdc_desc").getValue();
    var acc_ids=Ext.getCmp("acc_id").getValue();
    var user_grd=user_panel.items.get('user_grid');
    var user_store=user_grd.getStore();
    //alert(user_store.getAt(0).get("hiddenrole"));
    //alert(user_store.getAt(0).get("group"));
    var vdcname=Ext.getCmp('vdc_name').getValue()
    if(!vdcname){
    	Ext.MessageBox.alert(_('警告'),"请填写虚拟数据中心的名称 ");
    	return;
    }
    if(!checkSpecialCharacters(vdcname, "Virtual Data Center Name")){
       return;
     }
        if (!Ext.getCmp("cloud_provider_name").getRawValue() && !Ext.getCmp("cloud_account_name").getRawValue()){
            Ext.MessageBox.alert( _("警告") , "请验证你选择的 "+stackone.constants.IAAS+" 和账户名称");
            return;
        }
    
    //for user details
    var edited_user="[";
    var infrastructure_user="[";
    var userlist="[";
    
    for(var i=0;i<user_store.getCount();i++)
    {
        if(user_store.getAt(i).get("userid")!=null&&user_store.getAt(i).get("edited")=="True"){
            edited_user+="{'user_id':'"+user_store.getAt(i).get("userid")+"',";
            edited_user+=" 'user_name':'"+user_store.getAt(i).get("username")+"',";
            edited_user+=" 'user_fname':'"+user_store.getAt(i).get("fname")+"',";
            edited_user+=" 'user_lname':'"+user_store.getAt(i).get("lname")+"',";
            edited_user+=" 'user_nname':'"+user_store.getAt(i).get("nname")+"',";
            edited_user+=" 'user_password':'"+user_store.getAt(i).get("password")+"',";
            edited_user+=" 'user_email':'"+user_store.getAt(i).get("email")+"',";
            edited_user+=" 'user_phone':'"+user_store.getAt(i).get("phone")+"',";
            edited_user+=" 'user_status':'"+user_store.getAt(i).get("status")+"',";
            edited_user+=" 'user_hiddenrole':'"+user_store.getAt(i).get("hiddenrole")+"',";
            edited_user+=" 'user_group':'"+user_store.getAt(i).get("group")+"'}";
            if(i!=user_store.getCount()-1){
                edited_user+=","
            }

        }
        if(user_store.getAt(i).get("userid")==""||user_store.getAt(i).get("userid")==null){
            
          
            userlist+="{'user_id':'"+user_store.getAt(i).get("userid")+"',";
            userlist+=" 'user_name':'"+user_store.getAt(i).get("username")+"',";
            userlist+=" 'user_fname':'"+user_store.getAt(i).get("fname")+"',";
            userlist+=" 'user_lname':'"+user_store.getAt(i).get("lname")+"',";
            userlist+=" 'user_nname':'"+user_store.getAt(i).get("nname")+"',";
            userlist+=" 'user_password':'"+user_store.getAt(i).get("password")+"',";
            userlist+=" 'user_email':'"+user_store.getAt(i).get("email")+"',";
            userlist+=" 'user_phone':'"+user_store.getAt(i).get("phone")+"',";
            userlist+=" 'user_status':'"+user_store.getAt(i).get("status")+"',";
            userlist+=" 'user_type':'"+user_store.getAt(i).get("type1")+"'}";
            if(i!=user_store.getCount()-1){
                userlist+=","
            }
        }
        if(mode=='EDIT'){
            if(user_store.getAt(i).get("hideselection")=="true"&&user_store.getAt(i).get("edited")!="True"){
                infrastructure_user+="{'user_id':'"+user_store.getAt(i).get("userid")+"',";
                infrastructure_user+="'user_group':'"+user_store.getAt(i).get("group")+"'}";
                 if(i!=user_store.getCount()-1){
                    infrastructure_user+=","
                 }
            }

       }
        if(mode=='NEW'){
                
                if(user_store.getAt(i).get("hideselection")=="true"&&user_store.getAt(i).get("edited")!="True"){
                    infrastructure_user+="{'user_id':'"+user_store.getAt(i).get("userid")+"',";
                    infrastructure_user+="'user_group':'"+user_store.getAt(i).get("type1")+"'}";
                     if(i!=user_store.getCount()-1){
                        infrastructure_user+=","
                     }

                }
        }
       
    }
    userlist+="]";
    infrastructure_user+="]";
    edited_user+="]";

    if(mode=='EDIT'){               
        var removeduseridlist="["+Ext.getCmp("uid").getValue()+"]";
        var deleteduseridlist="["+Ext.getCmp("delete").getValue()+"]";
        
    }
    
    
    var finitems=new Object();
    var regsel=Ext.getCmp("regacc_grid").getSelectionModel().getSelections();
    if(is_feature_enabled(cp_feature,stackone.constants.CF_REGION)){
        if(regsel.length<1){
            Ext.MessageBox.alert(_("错误"),"请选择区域 ");
            return;
        }
    }
    var rname="";
    var rid="";
    var rend="";
    var jsondata='';

    for(var i=0;i<regsel.length;i++)
    {
        rname=regsel[i].get('region');
        rid=regsel[i].get('id');
        rend=regsel[i].get('end_point');
//        alert("---region---zone_name-------"+rname+"---------"+regsel[i].get('zone_name'));
        if(!regsel[i].get('zone_name')){
            Ext.MessageBox.alert(_("错误"),"请选择区为区域 "+rname);
            return;
        }
        else{
            var zone_name=regsel[i].get('zone_name');

            var zn=[];
            zn=zone_name.split(",");
            var zonelist=[];
            var zlist=regsel[i].get('zone_list');
//            alert("--zn-----"+zn.length);
//            alert("--zlist-----"+zlist.length);
            for(var j=0;j<zn.length;j++){                
                for(var k=0;k<zlist.length;k++){
                    if(zn[j]==zlist[k].name){
                        zonelist.push(zlist[k]);
                    }
                }
            }
        }

//        alert("---region---temp_id-------"+rname+"---------"+regsel[i].get('temp_id'));
        if(!regsel[i].get('temp_id')){
            if(is_feature_enabled(cp_feature,stackone.constants.CF_REGION)){
                Ext.MessageBox.alert(_("错误"),"请选择模板为区域 "+rname);
                return;
            }
        }
        else{
            var temp_id=regsel[i].get('temp_id');//selected templates id.
            var tid=[];
            tid=temp_id.split(",");//selected templates id list.
            var templist=[];
            var tlist=regsel[i].get('temp_list');//templates grid store of selected region
//            alert("--tid-----"+tid.length);
//            alert("--tlist-----"+tlist.length);
            for(var j=0;j<tid.length;j++){
                for(var k=0;k<tlist.length;k++){
                    if(tid[j]==tlist[k].id){
                        templist.push(tlist[k]);
                    }
                }
            }
        }

        var vm_ids=regsel[i].get('vm_ids');//selected vms id.
        var vm_id_list=vm_ids.split(",");

        var items=new Object();
        items['region_id']=rid;
        items['templates']=templist;
        items['vm_ids']=vm_id_list;
        items['zones']=zonelist;
        items['region']=rname;
        items['end_point']=rend;
        finitems[rname]=items;

    }
    var serlist=new Array();
    var sselections=Ext.getCmp("seroff_grid").getSelectionModel().getSelections()
    if(sselections.length>0){
        for(var i=0;i<sselections.length;i++){
            var serdic=new Object();
            serdic['name']=sselections[i].get('name');
            serdic['description']=sselections[i].get('description');
            serdic['platform']=sselections[i].get('platform');
            serdic['cpu']=sselections[i].get('cpu');
            serdic['memory']=sselections[i].get('memory');
            serdic['storage']=sselections[i].get('storage');
            serdic['cname']=sselections[i].get('cname');
            serdic['cid']=sselections[i].get('cid');
            serdic['service_offering_id']=sselections[i].get('id');
            serlist.push(serdic);
        }
    }

     var quota_store=Ext.getCmp("quota_grid").getStore();
     for(var e=0;e<quota_store.getCount();e++){
         var q_rec=quota_store.getAt(e);
         if (parseInt(q_rec.get("limit"))<parseInt(q_rec.get("used"))){
             Ext.MessageBox.alert( _("失败") ,_("Quota's ")+ q_rec.get("type")+_(" limit cannot be less than ")+_(q_rec.get("used")));
             return;
         }
     }

     var quota_deta="[";
     for(var d=0;d<quota_store.getCount();d++){
         var q_rec=quota_store.getAt(d);
         var limit = null;
         quota_deta+="{category:'"+q_rec.get("category")+"',";
         quota_deta+="type:'"+q_rec.get("type")+"',";
         if((Ext.util.Format.lowercase(q_rec.get("limit"))== 'unlimited' || Ext.util.Format.trim(q_rec.get("limit")) == '')
        		 && typeof(q_rec.get("limit")== 'string')){
        	 limit = -1
         }
         else{
        	 limit = q_rec.get("limit")
         }
         quota_deta+="limit: "+limit+",";
         quota_deta+="used: "+q_rec.get("used")+"}";
         
         if (d!=quota_store.getCount()-1)
            quota_deta+=",";
     }
     quota_deta+="]";
     var quota_details=eval(quota_deta);

     
     if(!is_feature_enabled(cp_feature,stackone.constants.CF_REGION)){
        var template_grid=Ext.getCmp("template_grid");        
        var net_rec=template_grid.getSelectionModel().getSelections();
        if(!net_rec.length){
            Ext.MessageBox.alert(_("错误"),"请选择一个模板");
            return;
        }
        var template_list="[";
        for(var d=0;d<net_rec.length;d++){//getCount()

            template_list+="{'id':'"+net_rec[d].get("id")+"'}";
//            template_list+="'name':'"+net_rec[d].get("name")+"',";
//            template_list+=" 'description':'"+net_rec[d].get("description")+"'}";
            if(d!=net_rec.length-1){
                template_list+=","
            }



        }
        template_list+="]";
        
     }

     var jsondata= Ext.util.JSON.encode({
        "Regions":finitems,
        "ServiceOfferings":serlist,
        "quota_details":quota_details
    });

    var template_details=Ext.util.JSON.decode(template_list);
    template_object.template_details=template_details;

    var user_details=Ext.util.JSON.decode(userlist);
    user_object.user_details=user_details;

    var infrastructure_user_details=Ext.util.JSON.decode(infrastructure_user);
    infrastructure_object.infrastructure_user_details=infrastructure_user_details;

    var edited_user_details=Ext.util.JSON.decode(edited_user);
    editeduser_object.edited_user_details=edited_user_details;

    var removed_user_details=Ext.util.JSON.decode(removeduseridlist);
    removed_user_object.removed_user_details=removed_user_details;

    var deleted_user_details=Ext.util.JSON.decode(deleteduseridlist);
    deleted_user_object.deleted_user_details=deleted_user_details;


    ////// Defined Networks  //////
    var vdc_network_dict = new Object();
    
    if(is_feature_enabled(cp_feature,stackone.constants.CF_NETWORK)){
        var vdc_defined_network_dict = new Object();
        var vdc_private_network_panel = Ext.getCmp("vdc_private_network_panel");
        var create_default_network_panel = vdc_private_network_panel.items.get("create_default_network_panel");
        var create_default_network_checkbox = create_default_network_panel.items.get("create_default_network_checkbox");
       
    var create_private_network_panel = vdc_private_network_panel.items.get("create_private_network_panel");
        var create_private_network_checkbox = create_private_network_panel.items.get("create_private_network_checkbox");
        
        var vdc_defined_network_panel = Ext.getCmp("vdc_defined_network_panel");
        var defined_networks_grid = vdc_defined_network_panel.items.get("vdc_defined_network_grid");

//        var defined_networks_grid = Ext.getCmp("vdc_defined_network_grid")
        var defined_networks_store = defined_networks_grid.getStore();
        var add_defined_networks = new Array();
        var remove_defined_networks = new Array();
        for(var k=0;k<defined_networks_store.getCount();k++)
        {
            if (defined_networks_grid.getSelectionModel().isSelected(k))
            {
                if (defined_networks_store.getAt(k).get('selected')==false)
                    {
                        add_defined_networks.push(defined_networks_store.getAt(k).get('id'))
                    }
            }
            else{
                  if (defined_networks_store.getAt(k).get('selected')==true)
                        {
                            remove_defined_networks.push(defined_networks_store.getAt(k).get('id'))
                        }
            }
        }

        vdc_defined_network_dict['add_defined_networks'] = add_defined_networks;
        vdc_defined_network_dict['remove_defined_networks'] = remove_defined_networks;

        vdc_network_dict["create_default_network"] = create_default_network_checkbox.getValue();
        vdc_network_dict["defined_networks"] = vdc_defined_network_dict;
        vdc_network_dict["create_private_network"]=create_private_network_checkbox.getValue();
    }

    if (mode == "EDIT" || mode == "NEW")
        {
            //Common for ADD and EDIT
            vdc_object.cpname=Ext.getCmp('cloud_provider_name').getRawValue();
            var account_list=[];
            var res_dictt = { 'account_name':Ext.getCmp('cloud_account_name').getRawValue(),
                                'cloud_provider':Ext.getCmp('cloud_provider_name').getRawValue(),
                                'jsondata':jsondata
                            };
            account_list.push(res_dictt);
//            var account_details=Ext.util.JSON.encode(account_list);
            account_object.account_details=account_list;
            var res_dict = {
                            "vdc_object":vdc_object,
                            "account_object":account_object,
                            "user_object":user_object,
                            "infrastructure_object":infrastructure_object,
                            "editeduser_object":editeduser_object,
                            "template_object"    :template_object,
                            "networks" : vdc_network_dict
                        };
        }

    ///////// VDC EDIT //////////
    if (mode == "EDIT"){
        res_dict["removed_user_object"] = removed_user_object;
        res_dict["deleted_user_object"] = deleted_user_object;
        var jsondata= Ext.util.JSON.encode(res_dict);
        url="/cloud/edit_vdc?vdc_id="+node_id+"&vdc_name="+vdc_object.name+"&vdc_desc="+vdc_object.desc+"&acc_data="+jsondata+"&acc_ids="+acc_ids;
    }
    ///////// VDC ADD //////////
    else{
        var jsondata= Ext.util.JSON.encode(res_dict);
        var params="&vdc_data="+jsondata;
        url="/cloud/save_provision_vdc?node_id="+node_id+"&node_type="+node_type+params;
    }
    
    Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: _('请稍候...'),
        width:400,
        wait:true,
        waitConfig: {
            interval:200
        }
    });
//   alert(url);
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);

            Ext.MessageBox.hide();
            if(response.success){                               
                Ext.MessageBox.alert(_("状态"),response.msg);
                win.close();
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }
        },
        failure: function(xhr){
            
            Ext.MessageBox.hide();
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });

}


function user_window(response_msg){

//    var msg="Do you want to create a new user"
        Ext.MessageBox.confirm(_("确认"), response_msg, function(id){
             show_usercreate(id,response_msg);
    });
}

function show_usercreate(btn_id,response_msg){
    
    if (btn_id== 'yes'){
        var id = Ext.id();
        showWindow('Users',705,470,adminconfig(stackone.constants.CLOUD,id),id);
//        var msg=response_msg+" Create User"
//        Ext.MessageBox.alert(_("Status"),msg);
    }else if (btn_id == 'no'){
//        Ext.MessageBox.alert(_("Status"),response_msg);
        return
    }

}

function VDCUserDetailsPanel(grid,mode,user,w){
    var user_id=new Ext.form.TextField({
        fieldLabel: _('用户编号'),
        name: 'userid',
        width: 150,
        id: 'userid',
        allowBlank:false,
        disabled: true
    });
    var user_name=new Ext.form.TextField({
        fieldLabel: _('用户名'),
        name: 'username',
        width: 150,
        id: 'username',
        allowBlank:false
    });
    var user_fname=new Ext.form.TextField({
        fieldLabel: _('姓'),
        name: 'fname',
        width: 150,
        id: 'fname',
        allowBlank:false
    });
    var user_lname=new Ext.form.TextField({
        fieldLabel: _('名'),
        name: 'lname',
        width: 150,
        id: 'lname',
        allowBlank:false
    });
    var display_name=new Ext.form.TextField({
        fieldLabel: _('昵称'),
        name: 'nname',
        width: 150,
        id: 'nname',
        allowBlank:false
    });
    var user_password=new Ext.form.TextField({
        fieldLabel: _('密码'),
        name: 'password',
        width: 150,
        id: 'pass',
        inputType:'password',
        allowBlank:false
    });
    var user_repass=new Ext.form.TextField({
        fieldLabel: _('重新输入一次密码'),
        name: 'repassword',
        width: 150,
        id: 'repassword1',
        inputType:'password',
        initialPassField: 'pass',
        allowBlank:false
    });
    var user_email=new Ext.form.TextField({
        fieldLabel: _('邮箱'),
        name: 'email',
        width: 165,
        id: 'email',
        allowBlank:false
    });
    var user_phone=new Ext.form.NumberField({
        fieldLabel: _('电话'),
        name: 'phone',
        width: 150,
        id: 'phone',
        allowBlank:true
    });
    var createdby=new Ext.form.TextField({
        fieldLabel: _('创建者'),
        name: 'createdby',
        width: 150,
        id: 'createdby',
        allowBlank:false,
        disabled:true
    });
    var createddate=new Ext.form.TextField({
        fieldLabel: _('创建日期'),
        name: 'createddate',
        width: 150,
        id: 'createddate',
        allowBlank:false,
        disabled:true
    });
    var modifiedby=new Ext.form.TextField({
        fieldLabel: _('修改者'),
        name: 'modifiedby',
        width: 150,
        id: 'modifiedby',
        allowBlank:false,
        disabled:true
    });
    var modifieddate=new Ext.form.TextField({
        fieldLabel: _('修改日期'),
        name: 'modifieddate',
        width: 150,
        id: 'modifieddate',
        allowBlank:false,
        disabled:true
    });
    var newpasswrd=new Ext.form.TextField({
        fieldLabel: _('新密码'),
        name: 'newpass',
        width: 150,
        id: 'newpass',
        inputType:'password'
    });
    var confpasswrd=new Ext.form.TextField({
        fieldLabel: _('重新输入一次密码'),
        name: 'confpass',
        width: 150,
        id: 'confpass',
        inputType:'password'
    });
    var user_status_store = new Ext.data.JsonStore({
        url: '/model/get_user_status_map',
        root: 'user_status',
        fields: ['id','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    user_status_store.load();
    var user_role_store = new Ext.data.JsonStore({
        url: '/model/get_user_role_map',
        root: 'user_role',
        fields: ['id','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    user_role_store.load();
    var user_status=new Ext.form.ComboBox({
        width:80,
        minListWidth: 90,
        fieldLabel:_("状态"),
        allowBlank:false,
        triggerAction:'all',
        store:user_status_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'user_status'
    });
    var user_type=new Ext.form.ComboBox({
        width:80,
        minListWidth: 90,
        fieldLabel:_("角色"),
        allowBlank:false,
        triggerAction:'all',
        store:user_role_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'user_type'
    });
    var url="";
    if(mode=='NEW'){
        url="/model/get_groups_map";
    }
    else if(mode=='EDIT'){
        url="/model/get_groups_map?userid="+user.userid;
    }
    var user_cancel_button= new Ext.Button({
        id: 'cancel',
        text: _('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                w.close();
            }
        }
    });
    var user_save_button=new Ext.Button({
        id: 'save',
        text: _('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(user_rightpanel.getForm().isValid()) {
                    var url="",flag=false,errmsg="";
                    var uid="";
                    var repass= user_repass.getValue();
                    if(mode=="NEW" && user_password.getValue()!=repass){
                        errmsg+="<br>"+_("密码信息不匹配");
                        flag=true;
                    }
                    var email=user_email.getValue();
                    if(!EmailCheck(email)){
                        errmsg+="<br>"+_("请输入一个有效邮箱");
                        flag=true;
                    }
                    if(flag){
                        Ext.MessageBox.alert(_("警告"),errmsg);
                        return ;
                    }
                    uid=user_name.getValue();
                    var user_store=grid.getStore();
                    for(var i=0;i<user_store.getCount();i++){
                        if(user_store.getAt(i).get("username")==uid){
                            Ext.MessageBox.alert(_("警告"),"此用户名已经存在");
                            return ;
                        }
                        if(user_store.getAt(i).get("email")==email){
                            Ext.MessageBox.alert(_("警告"),"此邮箱已经存在");
                            return ;
                        }
                    }
//
                    if(mode=='NEW'){
                       // alert("Grgrgrg");
                          var rep_rec = Ext.data.Record.create([
                          {                            
                            name:'userid',
                            type:'string'                           
                          },
                          {
                            name: 'username',
                            type: 'string'
                          },
                           {
                            name: 'fnandln',
                            type: 'string'
                          },
                          {
                            name: 'fname',
                            type: 'string'
                          },
                          {
                            name: 'lname',
                            type: 'string'                           
                          },
                          {
                            name: 'nname',
                            type: 'string'                            
                          },
                          {
                            name: 'password',
                            type: 'string'                            
                          },
                          {
                            name: 'repassword1',
                            type: 'string'                            
                          },
                          {
                            name: 'email',
                            type: 'string'                          
                          },
                          {
                            name: 'phone',
                            type: 'string'                           
                          },{
                             name:'createdby',
                             type: 'string'                             
                          },
                          {   name:'createddate',
                              type: 'string'                            
                          },
                          {   name:'modifiedby',
                              type: 'string'                              
                          },
                          {   name:'modifieddate',
                              type: 'string'                              
                          },
                          {   name:'newpasswrd',
                              type: 'string'                              
                          },
                           {  name:'confpasswrd',
                              type: 'string'                             
                          },
                          {
                            name: 'status',
                            type: 'string'
                         //   hidden: true
                          },
                          {
                            name: 'type1',
                            type: 'string'
                           // hidden: true
                          },
                          {
                            name: 'group',
                            type: 'string'
                           // hidden: true
                          }
                          ]);
                    }
                    var new_entry=new rep_rec({
                        userid:user_id.getValue(),
                        username:user_name.getValue(),
                        fnandln:user_fname.getValue()+" "+user_lname.getValue(),
                        fname:user_fname.getValue(),
                        lname:user_lname.getValue(),
                        nname:display_name.getValue(),
                        password:user_password.getValue(),
                        email:user_email.getValue(),
                        phone:user_phone.getValue(),
                        status:user_status.getValue(),
                        type1:user_type.getValue(),
                        group:user_type.getValue()

                    });
                    //add new record.
                   grid.getStore().insert(0, new_entry);
                   w.close();
                 }else if(mode=='EDIT'){
                        var flag=false,errmsg="";
                        //var rec_count=groupitemselector.toStore.getCount();
                        var change_passwd=passwrd_fldset.getEl().child('legend').child('input').dom.checked;
                        if(change_passwd == true)
                        {
                            if(newpasswrd.getValue() == "")
                            {
                                errmsg+="<br>"+_("请输入新的密码");
                                flag=true;
                            }
                            if(newpasswrd.getValue() != "")
                            {
                                if(newpasswrd.getValue() != confpasswrd.getValue())
                                {
                                    errmsg+="<br>"+_("密码信息不匹配");
                                    flag=true;
                                }
                            }
                        }
                        if(flag){
                            Ext.MessageBox.alert(_("警告"),errmsg);
                            return ;
                        }       
                    }               
                else{
                    Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
                }
            }
        }
    });
    var tabPanel=new Ext.TabPanel({
        defaults: {
            autoScroll:true
        },
        margins: '2 2 2 0',
        minTabWidth: 115,
        tabWidth:135,
        activeTab:0,
        cls: 'whitebackground',
        border:false,
        id:'tabpanel',
        bbar:[{
            xtype: 'tbfill'
        },user_save_button,user_cancel_button]
    });
    var user_rightpanel=new Ext.FormPanel({
        id:"rightpanel",
        title:_('用户'),
        layout:"form",
        width:300,
        height:345,
        //frame:true,
        labelWidth:100,
        border:0,
        bodyStyle:'padding:10px 10px 10px 10px'
    //items:[user_name,user_fname,user_lname,user_password,user_repass,user_email,user_phone,user_status]
    });
    var passwrd_fldset=new Ext.form.FieldSet({
        checkboxToggle:true,
        collapsed: true,
        title: _('修改密码'),
        id: 'change_passwd',
        autoHeight:true,
        width:280,
        labelWidth:90,
        layout:'column',
        items: [{
            width: 300,
            layout:'form',
            items:[newpasswrd,confpasswrd]
        }]
    });
    user_rightpanel.add(user_name);
    user_rightpanel.add(user_fname);
    user_rightpanel.add(user_lname);
    user_rightpanel.add(display_name);
    if(mode=="NEW"){
        user_rightpanel.add(user_password);
        user_rightpanel.add(user_repass);
    }
    user_rightpanel.add(user_email);
    user_rightpanel.add(user_phone);
    user_rightpanel.add(user_status);
    user_rightpanel.add(user_type);
    var user_auditpanel=new Ext.Panel({
        id:"auditpanel",
        title:_('Audit'),
        width:300,
        height:345,
        layout:"form",
        frame:true,
        labelWidth:100,
        border:false,
        bodyBorder:false,
        items:[createdby,createddate,modifiedby,modifieddate ]
    });
    var user_group=new Ext.form.TextField({
        fieldLabel: _('Groups'),
        name: 'groups',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'user_group'
    });
    if(mode=="EDIT"){
        var userid=user.userid;
        user_id.setValue(user.userid);
        user_name.setValue(user.username);
        user_name.disabled=true;
        user_fname.setValue(user.fname);
        user_lname.setValue(user.lname);
        display_name.setValue(user.displayname);
        user_email.setValue(user.email);
        user_phone.setValue(user.phone);
        user_status.setValue(user.status);
        user_group.setValue(user.groupname);
        user_rightpanel.add(user_group);
        user_rightpanel.add(passwrd_fldset);
        tabPanel.add(user_rightpanel);
        tabPanel.add(user_auditpanel);
        tabPanel.setActiveTab(user_auditpanel);
        tabPanel.setActiveTab(user_rightpanel);
        createdby.setValue(user.createdby);
        modifiedby.setValue(user.modifiedby)
        createddate.setValue(user.createddate)
        modifieddate.setValue(user.modifieddate)
    }else if(mode=="NEW"){
        user_status.setValue("Active");
    }
    tabPanel.add(user_rightpanel);
    tabPanel.setActiveTab(user_rightpanel);
    var new_users_panel=new Ext.Panel({
        id:"new_user_panel",
        layout:"form",
        width:350,
        height:450,
        cls: 'whitebackground',
        frame:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[tabPanel]
    });
    return new_users_panel;
}


function VDCEdituserDetailsPanel(user_grid,mode,edit_rec,w,type){

    var user_id=new Ext.form.TextField({
        fieldLabel: _('用户编号'),
        name: 'userid',
        width: 150,
        id: 'userid',
        allowBlank:false,
        disabled: true
    });
    var user_name=new Ext.form.TextField({
        fieldLabel: _('用户名'),
        name: 'username',
        width: 150,
        id: 'username',
        allowBlank:false
    });
    var user_fname=new Ext.form.TextField({
        fieldLabel: _('姓'),
        name: 'fname',
        width: 150,
        id: 'fname',
        allowBlank:false
    });
    var user_lname=new Ext.form.TextField({
        fieldLabel: _('名'),
        name: 'lname',
        width: 150,
        id: 'lname',
        allowBlank:false
    });
    var display_name=new Ext.form.TextField({
        fieldLabel: _('昵称'),
        name: 'dispname',
        width: 150,
        id: 'dispname',
        allowBlank:false
    });
    var user_password=new Ext.form.TextField({
        fieldLabel: _('密码'),
        name: 'password',
        width: 150,
        id: 'pass',
        inputType:'password',
        allowBlank:false
    });
    var user_repass=new Ext.form.TextField({
        fieldLabel: _('重新输入一次密码'),
        name: 'repass',
        width: 150,
        id: 'repass',
        inputType:'password',
        initialPassField: 'pass',
        allowBlank:false
    });
    var user_email=new Ext.form.TextField({
        fieldLabel: _('邮箱'),
        name: 'email',
        width: 165,
        id: 'email',
        allowBlank:false
    });
    var user_phone=new Ext.form.NumberField({
        fieldLabel: _('电话'),
        name: 'phone',
        width: 150,
        id: 'phone',
        allowBlank:true
    });
     var hidden_role=new Ext.form.TextField({
//        fieldLabel: _('hidden role'),
        name: 'hiddenrole',
        width: 0,
        id: 'hiddenrole',
//        allowBlank:false,
        hidden:true
    });

    var newpasswrd=new Ext.form.TextField({
        fieldLabel: _('新密码'),
        name: 'newpass',
        width: 150,
        id: 'newpass',
        inputType:'password'
    });

    var confpasswrd=new Ext.form.TextField({
        fieldLabel: _('重新输入一次密码'),
        name: 'confpass',
        width: 150,
        id: 'confpass',
        inputType:'password'
    });


    var user_status_store = new Ext.data.JsonStore({
        url: '/model/get_user_status_map',
        root: 'user_status',
        fields: ['id','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    var user_role_store = new Ext.data.JsonStore({
        url: '/model/get_user_role_map',
        root: 'user_role',
        fields: ['id','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    user_role_store.load();
    user_status_store.load();
    var user_status=new Ext.form.ComboBox({
        width:80,
        minListWidth: 90,
        fieldLabel:_("状态"),
        allowBlank:false,
        triggerAction:'all',
        store:user_status_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'user_status'
    });
    var user_role=new Ext.form.ComboBox({
        width:80,
        minListWidth: 90,
        fieldLabel:_("角色"),
        allowBlank:false,
        triggerAction:'all',
        store:user_role_store,
        displayField:'value',
        valueField:'id',
        forceSelection: true,
        mode:'local',
        id:'user_role'
    });    

    var user_cancel_button= new Ext.Button({
        id: 'cancel',
        text: _('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                w.close();
            }
        }
    });

     var user_save_button=new Ext.Button({
        id: 'save',
        text: _('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
//                var index=user_grid.getStore().indexOf(edit_rec)
//                var user_store=user_grid.getStore();
//                user_store.getAt(index).set("edited")=true;

                if(user_rightpanel.getForm().isValid()) {
                    var url="",flag=false,errmsg="";
                    var uid="";
                    var repass= user_repass.getValue();
                    
                    var email=user_email.getValue();
                    if(!EmailCheck(email)){
                        errmsg+="<br>"+_("请输入一个有效的邮箱");
                        flag=true;
                    }
                    if(flag){
                        Ext.MessageBox.alert(_("警告"),errmsg);
                        return ;
                    }
//
                   // if(mode=='NEW'){
                       // alert("Grgrgrg");
                          var rep_rec = Ext.data.Record.create([
                          {
                            name:'userid',
                            type:'string'
                          },
                          {
                            name: 'username',
                            type: 'string'
                          },
                           {
                            name: 'fnandln',
                            type: 'string'
                          },
                          {
                            name: 'fname',
                            type: 'string'
                          },
                          {
                            name: 'lname',
                            type: 'string'
                          },
                          {
                            name: 'nname',
                            type: 'string'
                          },
                          {
                            name: 'password',
                            type: 'string'
                          },
                          {
                            name: 'repassword1',
                            type: 'string'
                          },
                          {
                            name: 'email',
                            type: 'string'
                          },
                          {
                            name: 'phone',
                            type: 'string'
                          },{
                             name:'createdby',
                             type: 'string'
                          },
                          {   name:'createddate',
                              type: 'string'
                          },
                          {   name:'modifiedby',
                              type: 'string'
                          },
                          {   name:'modifieddate',
                              type: 'string'
                          },
                          {   name:'newpasswrd',
                              type: 'string'
                          },
                           {  name:'confpasswrd',
                              type: 'string'
                          },
                          {
                            name: 'status',
                            type: 'string'
                         //   hidden: true
                          },
                          {
                            name: 'type1',
                            type: 'string'
                           // hidden: true
                          },
                          {
                            name: 'group',
                            type: 'string'
                           // hidden: true
                          },
                          {
                            name: 'edited',
                            type: 'string'
                           // hidden: true
                          },
                          {
                            name: 'edited',
                            type: 'string'
                           // hidden: true
                          }


                          ]);
                    }

                   if(mode=='EDIT'){
                        var new_entry=new rep_rec({
                            userid:user_id.getValue(),
                            username:user_name.getValue(),
                            fnandln:user_fname.getValue()+" "+user_lname.getValue(),
                            fname:user_fname.getValue(),
                            lname:user_lname.getValue(),
                            nname:display_name.getValue(),
                            password:newpasswrd.getValue(),
                            email:user_email.getValue(),
                            phone:user_phone.getValue(),
                            status:user_status.getValue(),
                            group:user_role.getValue(),
    //                        type1:user_role.getValue(),
                            hiddenrole:hidden_role.getValue(),
    //                        type1:user_type.getValue(),
                            //group:user_group.getValue(),
                            edited:"True"


                        });
                   }
                   if(mode=='NEW'){
                        var new_entry=new rep_rec({
                            userid:user_id.getValue(),
                            username:user_name.getValue(),
                            fnandln:user_fname.getValue()+" "+user_lname.getValue(),
                            fname:user_fname.getValue(),
                            lname:user_lname.getValue(),
                            nname:display_name.getValue(),
                            password:newpasswrd.getValue(),
                            email:user_email.getValue(),
                            phone:user_phone.getValue(),
                            status:user_status.getValue(),
                            type1:user_role.getValue(),
    //                        type1:user_role.getValue(),
                            hiddenrole:hidden_role.getValue(),
    //                        type1:user_type.getValue(),
                            //group:user_group.getValue(),
                            edited:"True"


                        });
                   }
                    //add new record.

                  var index=user_grid.getStore().indexOf(edit_rec);
                  var user_store=user_grid.getStore();
                  var previousrole=user_store.getAt(index).get("hiddenrole");
                  user_grid.getStore().remove(edit_rec);
                  user_grid.getStore().insert(index, new_entry);
                   w.close();
                // }else if(mode=='EDIT'){
                        var flag=false,errmsg="";
                        //var rec_count=groupitemselector.toStore.getCount();
                        var change_passwd=passwrd_fldset.getEl().child('legend').child('input').dom.checked;
                        if(change_passwd == true)
                        {
                            if(newpasswrd.getValue() == "")
                            {
                                errmsg+="<br>"+_("请输入新密码");
                                flag=true;
                            }
                            if(newpasswrd.getValue() != "")
                            {
                                if(newpasswrd.getValue() != confpasswrd.getValue())
                                {
                                    errmsg+="<br>"+_("密码信息不匹配");
                                    flag=true;
                                }
                            }
                        }
                        if(flag){
                            Ext.MessageBox.alert(_("警告"),errmsg);
                            return ;
                        }
                   // }
               // else{
                //    Ext.MessageBox.alert(_('Errors'), _('Some of the required information is missing.'));
               // }
            }
        }
    });


    var tabPanel=new Ext.TabPanel({
        defaults: {
            autoScroll:true
        },
        margins: '2 2 2 0',
        minTabWidth: 115,
        tabWidth:135,
        activeTab:0,
        cls: 'whitebackground',
        border:false,
        id:'tabpanel',
        bbar:[{
            xtype: 'tbfill'
        },user_save_button,user_cancel_button]
    });

    var user_rightpanel=new Ext.FormPanel({
        id:"rightpanel",
        title:_('用户'),
        layout:"form",
        width:300,
        height:345,
        //frame:true,
        labelWidth:100,
        border:0,
        bodyStyle:'padding:10px 10px 10px 10px'
    //items:[user_name,user_fname,user_lname,user_password,user_repass,user_email,user_phone,user_status]
    });

    var passwrd_fldset=new Ext.form.FieldSet({
        checkboxToggle:true,
        collapsed: true,
        title: _('修改密码'),
        id: 'change_passwd',
        autoHeight:true,
        width:280,
        labelWidth:90,
        layout:'column',
        items: [{
            width: 300,
            layout:'form',
            items:[newpasswrd,confpasswrd]
        }]
    });

    user_rightpanel.add(user_name);
    user_rightpanel.add(user_fname);
    user_rightpanel.add(user_lname);
    user_rightpanel.add(display_name);
    
    user_rightpanel.add(user_email);
    user_rightpanel.add(user_phone);
    user_rightpanel.add(user_status);
    user_rightpanel.add(user_role);
//    user_rightpanel.add(hidden_role);

    var user_group=new Ext.form.TextField({
//        fieldLabel:'',
        name: 'groups',
        valueField:'id',
//        forceSelection: true,
        mode:'local',
        id:'user_group',
        hidden:true
//
    });
        
    user_id.setValue(edit_rec.get('userid'));
    user_name.setValue(edit_rec.get('username'));
    user_name.disabled=true;
    user_fname.setValue(edit_rec.get('fname'));
    user_lname.setValue(edit_rec.get('lname'));
    display_name.setValue(edit_rec.get('nname'));
    user_email.setValue(edit_rec.get('email'));
    user_phone.setValue(edit_rec.get('phone'));
    user_status.setValue(edit_rec.get('status'));
    user_role.setValue(edit_rec.get('group'))
    user_group.setValue(edit_rec.get('group'));
    hidden_role.setValue(edit_rec.get('hiddenrole'));
    if (mode=='NEW'){
        user_role.setValue(edit_rec.get('type1'))
    }
    else{
        user_role.setValue(edit_rec.get('group'));
    }
//        user_rightpanel.add(user_group);
    user_rightpanel.add(passwrd_fldset);

    tabPanel.add(user_rightpanel);
    tabPanel.setActiveTab(user_rightpanel);



    tabPanel.add(user_rightpanel);
//        tabPanel.add(groupassign_details_panel);
//        tabPanel.setActiveTab(groupassign_details_panel);
    tabPanel.setActiveTab(user_rightpanel);

    var new_users_panel=new Ext.Panel({
        id:"new_user_panel",
        layout:"form",
        width:350,
        height:450,
        cls: 'whitebackground',
        frame:true,
        labelWidth:130,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[tabPanel]
    });

    return new_users_panel;

}

function create_template_panel(action, node_id){

    var template_selmodel=new Ext.grid.CheckboxSelectionModel({
        singleSelect:false,
        listeners:{
            rowdeselect:function(sel_model, index, record){
                if(record.get('can_remove') == false){
                    sel_model.selectRow(index, true);
                    Ext.MessageBox.alert(_("错误"),"不可以移除模板组:"+record.get('name')+ ",虚拟机正在使用模板");
                }
            }
        }
    });

    var tlabel_template=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("模板")+'<br/></div>'
    });

//    var label_template=new Ext.form.Label({
//        html:'<div class="toolbar_hdg">'+_("")+'<br/></div>'
//    });

    var tlabel_desc_template=new Ext.form.Label({
        html:'<div>'+_("请选择供虚拟数据中心使用的模板.")+'<br/></div>'
    });
     var newdummy_space_template=new Ext.form.Label({
            html:_('&nbsp;&nbsp;<div style="width:80px"/>')
        });
    
    var template_store = new Ext.data.JsonStore({
        url: '/cloud/get_all_templates_for_vdc',
        root: 'rows',
        fields: ['id','name', 'description', 'selected', 'can_remove'],
        successProperty:'success',
        listeners: {
            load:function(store,opts,res,e){
                var size=store.getCount();
                if (action == 'EDIT'){
                    for (var i=0;i<size;i++){
                        if (store.getAt(i).get('selected') == true){
                            template_grid.getSelectionModel().selectRow(i,true);
                        }
                    }
                }else{//ADD,  select all rows by default
                    template_grid.getSelectionModel().selectAll();
                }
            }
        }
    });

    var template_grid = new Ext.grid.GridPanel({
        store: template_store, //template_store,
        enableHdMenu:false,
        selModel:template_selmodel,
        id:'template_grid',
        //autoExpandColumn:3,
        columns: [
        template_selmodel,

        {
            id       :'id',
            header   : '编号',
            width    : 140,
            sortable : true,
            dataIndex: 'id',
            hidden : true
        },
        {
            header   : '名称',
            width    : 200,
            sortable : true,
            dataIndex: 'name',
            hidden : false
        },
        {
            header   : '说明',
            width    : 265,
            sortable : true,
            dataIndex: 'description',
            hidden : false
        }
        ],

        stripeRows: true,
        height: 350,
        width:500
//        tbar:[label_template,{
//            xtype: 'tbfill'
//        }]
    });
    

    var template_panel = new Ext.Panel({
        height:415,
        id:"template_panel",
        layout:"form",
        frame:false,
        width:495,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        tbar:[tlabel_template],
        items:[tlabel_desc_template, newdummy_space_template ,template_grid]
    });

    var template_details_panel=new Ext.Panel({
        border:false,
        id:"panel11",
        layout:"form",
        width:465,
        height:420,
        frame:false,
        labelWidth:220,
        bodyStyle:'border-top:1px solid #AEB2BA;',

        items:[template_panel]
    });

    return template_details_panel;


}

