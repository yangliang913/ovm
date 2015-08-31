function DWM_fence_ui(node){
        var node_type=node.attributes.nodetype;
        var url="/ha/get_sp_fencing_data?node_id="+node.id+"&node_type="+node_type;
        var ajaxReq=ajaxRequest(url,0,"POST",true);
        ajaxReq.request({
            success: function(xhr) {//alert(xhr.responseText);
                var response=Ext.util.JSON.decode(xhr.responseText);
                if (response.success){
                     var fence_rec=response.fencing_data;
                     showWindow(_("电源管理-"+fence_rec[0].server),460,350,fencing_dialog(null, null,fence_rec,stackone.constants.DWM),windowid);
                }else{
                    Ext.MessageBox.alert( _("失败") , response.msg);
                }
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
        });

}
function HighAvailbility(node,action){
       var node_type=node.attributes.nodetype;
       var ha_data;
       var url="/ha/get_ha_details?node_type="+node_type+"&node_id="+node.attributes.id;
       var ajaxReq=ajaxRequest(url,0,"POST",true);
         ajaxReq.request({
            success: function(xhr) {//alert(xhr.responseText);
                var response=Ext.util.JSON.decode(xhr.responseText);
                ha_data=response.ha_data;

                if(node_type==stackone.constants.SERVER_POOL){
                   windowid=Ext.id();
                   showWindow(_("配置高可用"),640,470,server_pool_ha(node,action,windowid,ha_data),windowid, false, true);

               }else if(node_type==stackone.constants.DATA_CENTER)
                   // showWindow(_("Define Fencing Devices"),640,430,data_center_ha(node,action));
                    showWindow(_("设置Fencing以启动高可用"),640,430,data_center_ha(node,action));
          },
            failure: function(xhr){
                Ext.MessageBox.alert( _("失败") , xhr.statusText);
            }
        });

}
function server_pool_ha(node,action,win_id,ha_data){

  var treePanel= new Ext.tree.TreePanel({
        region:'west',
        width:180,
        rootVisible:false,
        border: false,
        lines : false,
        id:'treePanel',
        cls:'leftnav_treePanel',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        listeners: {
            click: function(item) {
                var id=item.id;
                process_card_panel(card_panel,treePanel,id.substr(4,id.length),"treepanel");
            }
        }
    });

    // root node of tree view
    var rootNode = new Ext.tree.TreeNode({
        text	: '根节点',
        draggable: false,
        id		: 'rootnode',
        listeners: {
            expand : function(btn) {
                treePanel.getNodeById("node0").select();
            }
        }
    });
    var generalNode = new Ext.tree.TreeNode({
        text: _('常规'),
        draggable: false,
        id: "node0",
        icon:'icons/vm-general.png',
        nodeid: "general",
        leaf:false,
        allowDrop : false
       // cls:"labelcolor"
    });
    var fencingNode = new Ext.tree.TreeNode({
        text: _('Fencing 配置'),
        draggable: false,
        id: "node1",
        nodeid: "fencing",
        icon:'icons/vm-network.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

    //var fencingNode = new Ext.tree.TreeNode({
        //text: _('Fencing'),
      //  text: _('Fencing Configuration'),

    var vm_priorNode = new Ext.tree.TreeNode({
        text: _('虚拟机的优先级'),
        draggable: false,
        id: "node2",
        nodeid: "vm_prior",
        icon:'icons/vm-storage.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
     var advancedNode = new Ext.tree.TreeNode({
        text: _('高级选项'),
        draggable: false,
        id: "node3",
        nodeid: "advanced",
        icon:'icons/templates-parameters.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
     var clusterNode = new Ext.tree.TreeNode({
        text: _('集群详情'),
        draggable: false,
        id: "node4",
        nodeid: "advanced",
        icon:'icons/vm-misc.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

    var general_details_panel=create_general_panel(node,ha_data);
    var vm_priority_panel=create_vm_prior_panel(node);
    var fencing_panel=create_fencing_panel(node,ha_data);
    var advanced_panel=create_advanced_panel(node);
    var cluster_panel=create_cluster_panel(node);

    var button_prev=new Ext.Button({
        id: 'move-prev',
        text: _('上一步'),
        //disabled: true,
        icon:'icons/prev.gif',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                //process_card_panel(card_panel,treePanel,-1);
				 //process_panel(card_panel,treePanel,-1);
				var t = card_panel.items.get(card_panel.items.indexOf(card_panel.getActiveTab())-1);
				if (t) {
					card_panel.setActiveTab(t);
				}
            }
        }
    });
    var button_next=new Ext.Button({
        id: 'move-next',
        text: _('下一步'),
        icon:'icons/next.gif',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                //process_card_panel(card_panel,treePanel,1);
				var t = card_panel.items.get(card_panel.items.indexOf(card_panel.getActiveTab())+1);
				//alert(t);
				if (t) {
					t.setDisabled(false);
					card_panel.setActiveTab(t);
					if (card_panel.items.indexOf(t) == card_panel.items.length-1) {
						button_ok.setDisabled(false);
					}
				}
            }
        }
    });
	var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('确定'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
		disabled: true,
        listeners: {
            click: function(btn) {
                submit_sp_hadetails(general_details_panel.items.get("general_panel"),
                vm_priority_panel,fencing_panel,
                advanced_panel.items.get("adv_panel"),cluster_panel.items.get("cluster_panel"),node.attributes.id,
                node.attributes.nodetype,win_id);
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
                closeWindow(win_id);
            }
        }
     });
    // card panel for all panels
    var card_panel=new Ext.TabPanel({
        width:"100%",
        height:425,
        //layout:"card",
        id:"card_panel",
        //        activeItem:0,
        cls: 'whitebackground',
		layoutOnTabChange: true,
        border:false,
        /*bbar:[
        {
            xtype: 'tbfill'
        },button_prev,button_next,button_ok,button_cancel],*/
        items:[general_details_panel,vm_priority_panel,fencing_panel,advanced_panel]
    //
    });
    rootNode.appendChild(generalNode);
    rootNode.appendChild(fencingNode);
    rootNode.appendChild(vm_priorNode);
    rootNode.appendChild(advancedNode);
//    rootNode.appendChild(clusterNode);
    var treeheading=new Ext.form.Label({
        html:'<br/><br/>'
    });

    var side_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:180,
        height:588,
        id:'side_panel',
        cls:'westPanel',
        items:[treeheading,treePanel]

    });
    var right_panel=new Ext.Panel({
        id:"right_panel",
        width:"100%",
        height:440,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        //bodyStyle:'padding:5px 5px 5px 5px',
		bbar:[
        {
            xtype: 'tbfill'
        },button_prev,button_next,button_ok]//,button_cancel]
//        items:[change_settings]
    });
    var outerpanel=new Ext.FormPanel({
        width:900,
        height:490,
        autoEl: {},
        layout: 'column',
        items:[side_panel,right_panel]

    });
    right_panel.add(card_panel);
    card_panel.activeItem = 0;
	//李必忠card_panel.items.getRange(1, 20).forEach(function(item){item.setDisabled(true)});
   // treePanel.setRootNode(rootNode);
		var card_panel_item = card_panel.items.getRange(1,20);
        for(var t=0 ;t<3;t ++){
	        //alert(t);
        	card_panel_item[t].setDisabled(true);
        	//var temp = card_panel_item[t];
        	//alert(temp);
        	}
    //return outerpanel;
    return right_panel;

}

function process_card_panel(panel,treePanel,value,type)
{
    var root_node=treePanel.getNodeById("rootnode");
    var children=root_node.childNodes;
    var selected_node_id;
    var node_ids=new Array();
        for(var i=0;i<children.length;i++){
            node_ids[i]=children[i].attributes.id;
            if(type=="treepanel"){
                if(node_ids[i].substr(4,node_ids[i].length)==value)
                    selected_node_id=node_ids[i];
            }
            else{
                var current_selected_nodeid=treePanel.getSelectionModel().getSelectedNode().attributes.id;
                if(node_ids[i]==current_selected_nodeid){
                    selected_node_id=children[parseInt(i)+parseInt(value)].attributes.id;
                }
            }
        }

    if(selected_node_id==children[0].attributes.id){
         panel.getBottomToolbar().items.get('move-prev').disable();
     }else{
         panel.getBottomToolbar().items.get('move-prev').enable();
     }
    if (selected_node_id==children[children.length-1].attributes.id){
         panel.getBottomToolbar().items.get('move-next').disable();
     }else{
         panel.getBottomToolbar().items.get('move-next').enable();
     }

    panel.getLayout().setActiveItem("panel"+selected_node_id.replace("node",""));
    treePanel.getNodeById(selected_node_id).select(); 

}
function create_general_panel(node,ha_data){

    // General Panel declaration
    var label_general=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("常规")+'<br/></div>'
    });

    var tlabel_general=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("常规")+'</div>'
    });
     var en_des=_("监视虚拟机和服务器的高可用性功能。当虚拟机出现故障，stackone会启动它。当一个服务器宕机时，stackone将启动备用服务器上所有正在运行的虚拟机.");

     var tooltip_enableha=new Ext.form.Label({
        html:'<img src=icons/information.png onClick=show_desc("'+escape(en_des)+'") />'
     })
     var same_des=_('每当一个虚拟机出现故障，stackone将在同一服务器上重新启动.');
     var tooltip_same=new Ext.form.Label({
        html:'<img src=icons/information.png onClick=show_desc("'+escape(same_des)+'") />'
     })
     var server_des=_('StackoneHA步骤： '+
        '<br/><br/>一，每当虚拟机出现故障，Stackone将首先在同一服务器重新启动它. '+
        ' '+
        '<br/><br/>'+
        '二，当物理服务器宕机，stackone将所有虚拟机迁移到备用服务器.若没有指定备用服务器，服务器池内的其他服务器将根据策略转移虚拟机. '+
        ' '+
        ' <br/><br/>三，建议配置fencing（也可省略）使故障服务器从存储中断开，使其上面的虚拟机在另一台正常服务器上运行，以消除两台物理服务器运行相同虚拟机的风险.'+
        ' '+
        ' '+
        '<br/><br/> 四，设置虚拟机优先级，以保证核心业务可持续运行. '+
        '<br/><br/> '+
        '五，最后，你也可设置故障服务器正常后可回迁已转移虚拟机.'
        );
     var tooltip_server=new Ext.form.Label({
        html:'<img src=icons/information.png onClick=show_desc("'+escape(server_des)+'",500,300) />'
     })

     var enable_ha_label=new Ext.form.Label({
        html: _('<b>启动高可用</b>')
     })
    var enable_ha= new Ext.form.Checkbox({
//        fieldLabel: _('<div style="width:10px"/>'),
        name: 'enable_ha',
        id: 'enable_ha',
        width:20,
        listeners:{
            check:function(field,checked){
                
            }
        }
    });
    var dummy_space=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:6px"/>')
    });
    var dummy_space2=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space3=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
     var dummy_space8=new Ext.form.Label({
        html:_('&nbsp;<div style="width:6px"/>')
    });
    var dummy_space9=new Ext.form.Label({
        html:_('&nbsp;<div style="width:6px"/>')
    });
     var dummy_space10=new Ext.form.Label({
        html:_('&nbsp;<div style="width:6px"/>')
    });
    var dummy_space14=new Ext.form.Label({
       html:_('&nbsp;<div style="width:6px"/>')
    });
    var dummy_space15=new Ext.form.Label({
        html:_('&nbsp;<div style="width:6px"/>')
    });


    var enable_ha_panel=new Ext.Panel({
        id:"enable_ha_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:33,
        bodyStyle:'padding-left:8px',
        items:[enable_ha,dummy_space,enable_ha_label,dummy_space2]
    });

   var migrate_heading=new Ext.form.Label({
        html: _('<br/>在服务器发生故障时 :')
   });
   var migrate_radio_other=new Ext.form.Label({
        html: _('虚拟机迁移到其它服务器.')
   });
   var migrate_radio_standy=new Ext.form.Label({
        html: _('虚拟机迁移到下列备用服务器.')
   });
   var migrate_back_label=new Ext.form.Label({
        html: _('当服务器启动时虚拟机迁回.')
   });
   var vm_fail_label=new Ext.form.Label({
        html: _('同一台机器上的虚拟机故障转移.')
   });
   var vm_server_fail_label=new Ext.form.Label({
        html: _('虚拟机和服务器故障转移.')
   });
   var use_table=new Ext.form.Label({
        html: _(' 请从下面列表选择备用服务器.')
   });
   var migrate_back= new Ext.form.Checkbox({
        name: 'migrate_back',
        id: 'migrate_back',
        width:20,
        listeners:{
            check:function(field,checked){
                if(checked && !migrate_other.getValue()){
                     migrate_back.setValue(false);
                }
            }
        }
    });
//    var none_des=_("When none is selected, the virtual machines would be distributed on other running servers.");
//
//    var tooltip_dedicate=new Ext.form.Label({
//        html:'<img src=icons/information.png onClick=show_desc("'+escape(none_des)+'") />'
//    });

//    var migrate_panel=new Ext.Panel({
//        id:"migrate_panel",
//        layout:"column",
//        frame:false,
//        width:'100%',
//        autoScroll:true,
//        border:false,
//        bodyBorder:false,
//        height:35,
//        items:[dummy_space1,migrate_ha_label,dummy_space3,migrate_back,dummy_space4]
//    });

    var migrate_other=new Ext.form.Radio({
        boxLabel: _(''),
        hideLabel:true,
        id:'migrate_other',
        name:'migrate_radio',
        listeners:{
            check:function(field,checked){
                if(!checked){
                     migrate_back.setValue(false);
                }else{
//                    servers_grid.setDisabled(true);
                }
            }
        }
    });
     var migrate_standby=new Ext.form.Radio({
        boxLabel: _(''),
        hideLabel:true,
        id:'migrate_standby',
        name:'migrate_radio',
        listeners:{
            check:function(field,checked){
//                if(checked){
//                    servers_grid.setDisabled(false);
//                }
            }
        }
    });
    var vm_failover_radio=new Ext.form.Radio({
        boxLabel: _(''),
        hideLabel:true,
        id:'vm_failover_radio',
        name:'vm_radio',
        listeners:{
            check:function(field,checked){
                if(checked){
                    Ext.getCmp("panel1").disable();
                    Ext.getCmp("use_table_panel").disable();
                    Ext.getCmp("standby_panel").disable();
                    Ext.getCmp("migrate_panel1").disable();
                    Ext.getCmp("migrate_panel2").disable();
                    Ext.getCmp("migrate_panel3").disable();
                    Ext.getCmp("migrate_panel4").disable();
                }else{
                    Ext.getCmp("panel1").enable();
                    Ext.getCmp("use_table_panel").enable();
                    Ext.getCmp("standby_panel").enable();
                    Ext.getCmp("migrate_panel1").enable();
                    Ext.getCmp("migrate_panel2").enable();
                    Ext.getCmp("migrate_panel3").enable();
                    Ext.getCmp("migrate_panel4").enable();
                }

            }
        }
    });
    var vm_server_failover_radio=new Ext.form.Radio({
        boxLabel: _(''),
        hideLabel:true,
        id:'vm_server_failover_radio',
        name:'vm_radio',
        listeners:{
            check:function(field,checked){
               if(checked){
                }
            }
        }
    });
     var vm_failover_panel1=new Ext.Panel({
        id:"vm_failover_panel1",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:30,
        bodyStyle:'padding-left:8px',
        items:[vm_failover_radio,dummy_space9,vm_fail_label,dummy_space14,tooltip_same]
    });
     var vm_failover_panel2=new Ext.Panel({
        id:"vm_failover_panel2",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:30,
        bodyStyle:'padding-left:8px',
        items:[vm_server_failover_radio,dummy_space10,vm_server_fail_label,dummy_space15,tooltip_server]
    });

     var migrate_panel1=new Ext.Panel({
        id:"migrate_panel1",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:40,
        items:[dummy_space3,migrate_heading]
    });

     var migrate_panel2=new Ext.Panel({
        id:"migrate_panel2",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:20,
        bodyStyle:'padding-left:18px',
        items:[migrate_other,dummy_space1,migrate_radio_other]
    });
     var migrate_panel3=new Ext.Panel({
        id:"migrate_panel3",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:28,
        bodyStyle:'padding-left:40px',
        items:[migrate_back,migrate_back_label]
    });

     var migrate_panel4=new Ext.Panel({
        id:"migrate_panel4",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:20,
        bodyStyle:'padding-left:18px',
        items:[migrate_standby,dummy_space8,migrate_radio_standy]
    });
     var use_table_panel=new Ext.Panel({
        id:"use_table_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:15,
        bodyStyle:'padding-left:38px',
        items:[use_table]
    });
    var stand_by=new Ext.form.Label({
        html:'<b>'+ _('&nbsp;&nbsp;&nbsp;备用服务器 :')+'</b>'
    });
    var stand_by_des=new Ext.form.Label({
        html:'<br><p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'+
            _('In the event of server failing, all virtual machines would be <br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;transferred to a these servers.')+
            '</p><br/>'
    });


//   var dedicate_ha_label=new Ext.form.Label({
//        html: _('Number of Dedicated Servers :')
//   })
//   var dedicate=new Ext.form.NumberField({
////        fieldLabel: _("<img src=icons/information.png onMouseOver=show_desc('"+escape(none_des)+"'); /> &nbsp;&nbsp;<b>Number of dedicated servers</b>"),
//        name: 'dedicate',
//        width: 35,
//        value:0,
//        id: 'dedicate'
////        allowBlank:false
//    });
//
//
//    var dedicated_server_panel=new Ext.Panel({
//        id:"dedicated_server_panel",
//        layout:"column",
//        frame:false,
//        width:'100%',
//        autoScroll:true,
//        border:false,
//        bodyBorder:false,
//        items:[dummy_space1,dedicate_ha_label,dummy_space3,dedicate,dummy_space4,tooltip_dedicate]
//    });


    var srvrs_colModel = new Ext.grid.ColumnModel([
        {header: _("节点ID"), dataIndex: 'node_id', hidden:true},
        {header: _("名称"), width: 50, sortable: true, dataIndex: 'name'},
        {header: _("平台"), width: 60, sortable: true, dataIndex: 'platform'},
        {header: _("CPUs"), width: 50, sortable: true, dataIndex: 'cpu'},
        {header: _("内存(MB)"), width: 75, sortable: true, dataIndex: 'memory'},
        {header:_("备用"),width: 55, sortable: true, dataIndex: 'is_standby',renderer:show_server_checkbox}
    ]);
    var srvrs_store = new Ext.data.JsonStore({
        url:"/ha/get_servers?node_id="+node.attributes.id,
        root: 'servers',
        successProperty:'success',
        fields:['node_id','name','platform','cpu','memory','is_standby'],
        listeners:{
//            load:function(obj,recs,opts){
//               insert_dummyrecs(obj);
//               prntPanel.getEl().unmask();
//            },
            loadexception:function(obj,opts,res,e){
//                prntPanel.getEl().unmask();
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
        ,sortInfo:{
            dir:'ASC',
            field:'name'
        }
    });
    srvrs_store.load();

   var select_des= _('从服务器池中选择特定的服务器，如果不指定，stackone将选择最轻微加载的服务器.');
   var tooltip_server=new Ext.form.Label({
        html:'<img src=icons/information.png onClick=show_desc("'+escape(select_des)+'") />'
     })

   var label_ser=new Ext.form.Label({
        html:'<div class="toolbar_hdg" style="height:18px" >'+_('服务器')+'</div>',
        id:'label_vm'
    });


     var servers_grid = new Ext.grid.GridPanel({
        id:"servers_grid",
        store: srvrs_store,
        colModel:srvrs_colModel,
        stripeRows: true,
        frame:false,
        width:"100%",
        autoExpandColumn:1,
        autoExpandMax:250,
        autoExpandMin:150,
        height:150,
        enableHdMenu:false,
//        tbar:[label_ser],
        listeners:{

        },
        tbar:[label_ser,

           {
                xtype:'tbfill'
            },_('搜索: '),new Ext.form.TextField({
            fieldLabel: _('搜索'),
            name: 'search',
            id: 'search_server',
            allowBlank:true,
            enableKeyEvents:true,
            width:100,
            listeners: {
                keyup: function(field) {
                    servers_grid.getStore().filter('name', field.getValue(), false, false);
                }
            }
        })


        ]
    });

    var standby_panel=new Ext.Panel({
        id:'standby_panel',
        height:175,
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-left:18px',
        items:[servers_grid]
    });

    var general_panel=new Ext.Panel({
        height:"100%",
        id:"general_panel",
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        //items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],
        //tbar:[tlabel_general],
        items:[enable_ha_panel,vm_failover_panel1,vm_failover_panel2,
            migrate_panel1,migrate_panel2,migrate_panel3,migrate_panel4,use_table_panel,standby_panel]
    });

   var general_details_panel=new Ext.Panel({
		title: '常规',
        id:"panel0",
        layout:"form",
        width:"100%",
        //cls: 'whitebackground paneltopborder',
        height:"100%",
        frame:false,
        //labelWidth:220,
       // bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[general_panel]
    });
    if (ha_data!=null){
        enable_ha.setValue(ha_data.enable_ha);
        if (ha_data.failover==stackone.constants.VM_SERVER_FAILOVER){
            vm_server_failover_radio.setValue(true);
        }
        if (ha_data.use_standby){
            migrate_standby.setValue(true);
        }else{
            migrate_other.setValue(true);
            migrate_back.setValue(ha_data.migrate_back);
        }
//        dedicate.setValue(ha_data.standby_count);
    }

    return general_details_panel;
}
function create_vm_prior_panel(node){

    var prior_des=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<p>'+ _('在故障转移阶段，根据虚拟机设置优先顺序迁移.')+'</p>'
    });

        var vmp_store = new Ext.data.JsonStore({
        url: '/ha/get_vm_priority',
        root: 'vm_priority',
        fields: ['id','value'],
        sortInfo:{
            field:'id',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
//            load:function(obj,resc,f){
//                alert(obj.getCount());
//            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    }
    );
    vmp_store.load();
    var vms_colModel = new Ext.grid.ColumnModel([
        {header: _("Id"), width: 22, sortable: true, hidden: true, dataIndex: 'id'},
        {header: _("名称"), width: 120, sortable: true, dataIndex: 'name'},
        {header: _("服务器"), width: 120, sortable: true, dataIndex: 'server'},
        {header: _("优先级"), width: 140, sortable: true,dataIndex: 'ha_priority',
            editor: new Ext.form.ComboBox({
                    typeAhead: true,
                    store:vmp_store,
                    triggerAction: 'all'
                    ,valueField:'value'
                    ,displayField:'value'
                    ,mode:'local'
                })

        }
    ]);

    var vms_store = new Ext.data.JsonStore({
        url:"/dashboard/dashboard_vm_info?node_id="+node.attributes.id+"&type="+node.attributes.nodetype,
        root: 'info',
        successProperty:'success',
        fields:['id','name','server','state','cpu','mem','storage','network','template','os','io','node_id','template_version','template_updates','ha_priority'],
        listeners:{
//            load:function(obj,recs,opts){
//                   insert_dummyrecs(obj);
//                   prntPanel.getEl().unmask();
//            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
        ,sortInfo:{
            dir:'ASC',
            field:'name'
        }
    });
    vms_store.load();
    var label_vm=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("虚拟机")+'</div>',
        id:'label_vm'
    });
      var vm_grid = new Ext.grid.EditorGridPanel({
//        title:'Performance Details',
        id:"vm_grid",
        store: vms_store,
        colModel:vms_colModel,
        stripeRows: true,
        frame:false,
        width:"100%",
        autoExpandColumn:1,
//        autoHeight:true,
//        autoExpandMax:300,
//        autoExpandMin:150,
        clicksToEdit:1,
        height:280,
//        maxHeight:100,
//        tbar:[label_vm],
        enableHdMenu:false,
        tbar:[label_vm,
            {
                xtype:'tbfill'
            },_('搜索: '),new Ext.form.TextField({
            fieldLabel: _('搜索'),
            name: 'search',
            id: 'search_vm',
            allowBlank:true,
            enableKeyEvents:true,
            width:100,
            listeners: {
                keyup: function(field) {
                    vm_grid.getStore().filter('name', field.getValue(), false, false);
                }
            }
        })
        ]

    });

    // General Panel declaration
    var label_vm_prior=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("虚拟机的优先级")+'<br/></div>'
    });

    var tlabel_vm_prior=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("虚拟机优先级")+'</div>'
    });
    var vm_prior_panel=new Ext.Panel({
		title: '虚拟机优先级',
        height:"100%",
        id:"panel2",
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding:5px 5px 5px 5px',
        //tbar:[tlabel_vm_prior],
        items:/*[prior_des,*/[vm_grid]
        ,listeners:{
            show:function(p){
                if(vms_store.getCount()>0){
                    vms_store.sort('name','ASC');
                }
            }
        }
    });
        var vm_priorities_panel=new Ext.Panel({
        id:"panel2",
        layout:"form",
        width:100,
        //cls: 'whitebackground paneltopborder',
        height:120,
        frame:false,
        labelWidth:130,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[vm_prior_panel]
    });
    return vm_prior_panel;
}

function create_fencing_panel(node,ha_data){

    var fd_tip=_("一台服务器至少配置一个Fencing设备.\n\
                <br>那些没有用Fencing设备配置的服务器不会被认为是实现高可用性.");

    var dummy_space=new Ext.form.Label({
        html:'<p>'+ _('&nbsp;<div style="width:8px"/>')+'</p>'
    });
    var fence_des=new Ext.form.Label({
        html:'<p>'+ _('作用：配置fencing使故障服务器从存储中断开，使其上面的虚拟机在另一台正常服务器上运行，以消除两台物理服务器运行相同虚拟机的风险 '+
            ' '+
            ' '+
            ''+
            '.<br/><br/>'+
            '注意：前提是你需要在datacenter中设置fencing '+
            ' '+
            ' '+
            ' <br/><br/>')+'</p>'
    });

    var tooltip_fd=new Ext.form.Label({
        html:'<img src=icons/information.png onClick=show_desc("'+escape(fd_tip)+'") /><br/>'
     })


   var label_panel=new Ext.Panel({
        id:"label_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        items:[fence_des]
    });
   var fence_colModel = new Ext.grid.ColumnModel([
            {header: _("服务器"), width: 200, sortable: true,dataIndex: 'server'},
        {header: _("Fencing 设备"), width: 40, sortable: true, dataIndex: 'fencing_devices'},
        {header: _("编辑"), width: 40, sortable: true, dataIndex: 'fence_details',renderer:edit_fencedetails}
    ]);

    var fence_store = new Ext.data.JsonStore({
        url:"/ha/get_sp_fencing_data",
        root: 'fencing_data',
        fields:['id','server','fencing_devices',"fence_details"],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
        }
    );

    fence_store.load(
        {
            params:{
                node_id:node.attributes.id,
                node_type:node.attributes.nodetype                
            }
         }
     );

    var label_vm=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("服务器和 Fencing 配置")+'</div>',
        id:'label_vm'
    });
      var fencing_grid = new Ext.grid.GridPanel({
        store: fence_store,
        id:"fencing_grid",
        colModel:fence_colModel,
        stripeRows: true,
        frame:false,
        width:"100%",
        autoExpandColumn:1,
//        autoExpandMax:300,
//        autoExpandMin:150,
        height:140,
//        maxHeight:100,
        enableHdMenu:false,
        tbar:[label_vm,
             {
                xtype:'tbfill'
            },_('搜索: '),new Ext.form.TextField({
            fieldLabel: _('搜索'),
            name: 'search',
            id: 'search_info',
            allowBlank:true,
            enableKeyEvents:true,
            width:100,
            listeners: {
                keyup: function(field) {
                    fencing_grid.getStore().filter('server', field.getValue(), false, false);
                }
            }
        })],


        listeners:{
            cellclick:function(grid, rowIndex, columnIndex, e) {
                windowid=Ext.id();
                if(columnIndex==2){
                    showWindow(_("Fencing 设备和参数"),460,350,fencing_dialog(fencing_grid, rowIndex,fence_store),windowid);
                }
            }
        }
    });

    // General Panel declaration
    var label_fencing=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("Fencing 配置")+'<br/></div>'
    });

    var tlabel_fencing=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("Fencing 配置")+'</div>'
    });
    var fence_panel=new Ext.Panel({
		title: '服务器/Fencing 配置',
        height:420,
        id:"panel1",
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding:5px 5px 5px 5px',
        //tbar:[tlabel_fencing,dummy_space],
        items:/*[label_panel*/[fencing_grid]
        ,listeners:{
            show:function(p){
                if(fence_store.getCount()>0){
                    fence_store.sort('server','ASC');
                }
            }
        }

    });
    var fencing_panel=new Ext.Panel({
        id:"panel1",
        layout:"form",
        width:"100%",
        //cls: 'whitebackground paneltopborder',
        height:"100%",
        frame:false,
        //labelWidth:130,
       // bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[fence_panel]
    });
    if(ha_data!=null){
        if(ha_data.failover==stackone.constants.VM_FAILOVER){
            Ext.getCmp("vm_failover_radio").setValue(true);
        }
    }
    return fence_panel;

}
function create_advanced_panel(node){

    var adv_des=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<p>'+ _('高级配置.')+'</p>'
    });
    var label_des=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("高级配置")+'</div>',
        id:'label_vm'
    });
   var adv_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("属性"),
        width:150,
        dataIndex: 'attribute',
        css:'font-weight:bold; color:#414141;',
        editor: new Ext.form.TextField({
            allowBlank: false
        }),
        sortable:true
    },

    {
        header: _("值"),
        dataIndex: 'value',
        editor: new Ext.form.TextField({
            allowBlank: false
        }),
//        sortable:true,
        width:180

    },
     {
        header: _("信息"),
        dataIndex: 'information',
        width:80
    }
    ]);
    var adv_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var adv_store = new Ext.data.JsonStore({
        url: '/ha/get_advanced_params?node_id='+node.attributes.id,
        root: 'adv_params',
        fields: ['attribute','value','information'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }

        }
    }
    );

//    adv_store.load();
    var adv_rec = Ext.data.Record.create([
    {
        name: 'attribute',
        type: 'string'
    },

    {
        name: 'value',
        type: 'string'
    }
    ]);
    var adv_add=new Ext.Button({
        name: 'adv_add',
        id: 'adv_add',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var r=new adv_rec({
                    attribute: '',
                    value: ' '
                });

                adv_grid.stopEditing();
                adv_store.insert(0, r);
                adv_grid.startEditing(0, 0);
            }
        }
    });
    var adv_remove=new Ext.Button({
        name: 'adv_remove',
        id: 'adv_remove',
        text:_("移除"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                adv_store.remove(adv_grid.getSelectionModel().getSelected());
            }
        }
    });

     var adv_grid = new Ext.grid.EditorGridPanel({
        store: adv_store,
        id:'adv_grid',
        stripeRows: true,
        colModel:adv_columnModel,
        frame:false,
//        border: false,
        selModel:adv_selmodel,
        autoExpandColumn:1,
        autoExpandMin:180,
        autoExpandMax:180,
        autoscroll:true,
        //autoHeight:true,
        height:300,
        //height: '100%',
        width: "100%",
        clicksToEdit:2,
        enableHdMenu:false,
        tbar:[label_des
//            {
//            xtype:'tbfill'
//        },
//        adv_add,adv_remove
    ]

    });
    var url='/ha/get_advanced_params?node_id='+node.attributes.id;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                for (var j=0;j<response.adv_params.length;j++){
                      var res=response.adv_params[j];
                      var tooltip=new Ext.form.Label({
                            html:res.information
                      });
                      if (res.attribute=="wait_interval"){
                          wait_interval.setValue(res.value);
                          wait_panel.add(tooltip);
                          wait_panel.doLayout();
                      }
                      else if (res.attribute=="retry_count"){
                          retry_count.setValue(res.value);
                          retry_panel.add(tooltip);
                          retry_panel.doLayout();
                      }
                }
            }
            else
                Ext.MessageBox.alert(_("失败"),response.msg);
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
    // General Panel declaration
    var label_adv=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("高级选项")+'<br/></div>'
    });

    var tlabel_fencing=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("高级选项")+'</div>'
    });

    var wait_label=new Ext.form.Label({
        html:_('等待间隔:')
    });
    var retry_label=new Ext.form.Label({
        html:_('重试计数:')
    });
    var dummy_space=new Ext.form.Label({
        html:_('&nbsp;<div style="width:6px"/>')
    });
    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space3=new Ext.form.Label({
        html:_('&nbsp;<div style="width:7px"/>')
    });
    var dummy_space4=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space5=new Ext.form.Label({
        html:_('&nbsp;<div style="height:4px"/>')
    });
    var dummy_space6=new Ext.form.Label({
        html:_('&nbsp;<div style="height:4px"/>')
    });

    var wait_interval=new Ext.form.TextField({
        fieldLabel: _('等待间隔'),
        name: 'wait_interval',
        width: 80,
        id: 'wait_interval',
        allowBlank:false
    });
   var wait_panel=new Ext.Panel({
        id:"wait_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:30,
        bodyStyle:'padding-left:8px',
        items:[wait_label,dummy_space,wait_interval,dummy_space1]
    });
    var retry_count=new Ext.form.TextField({
        fieldLabel: _('重试计数'),
        name: 'retry_count',
        id: 'retry_count',
        width: 80,
        allowBlank:false
    });
    var retry_panel=new Ext.Panel({
        id:"retry_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:30,
        bodyStyle:'padding-left:8px',
        items:[retry_label,dummy_space3,retry_count,dummy_space4]
    });


    var adv_panel=new Ext.Panel({
        height:440,
        id:'adv_panel',
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        //tbar:[tlabel_fencing],
        items:[adv_des,dummy_space6,wait_panel,dummy_space5,retry_panel]
    });
        var adv_detailpanel=new Ext.Panel({
		title: '高级选项',
        id:"panel3",
        layout:"form",
        width:"100%",
        //cls: 'whitebackground paneltopborder',
        height:"100%",
        frame:false,
        //labelWidth:130,
        //bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[adv_panel]
    });

    return adv_detailpanel;

}
function create_cluster_panel(node){

    var cluster_des=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<br/><p>'+ _('如果在池中的服务器配置了集群，请在这里指定它.')+'</p><br/>'
    });

    // General Panel declaration
    var label_cluster=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("集群详情")+'<br/></div>'
    });

    var tlabel_vm_prior=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("集群详情")+'</div>'
    });
    var cluster_store = new Ext.data.JsonStore({
        url: '/ha/get_cluster_adapters',
        root: 'clusters',
        fields: ['id','value'],
        sortInfo:{
            field:'value',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            load:function(obj,recs,f){
                    cluster_adapter.setValue(recs[0].get('id'));
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    }
    );
    cluster_store.load();
    var cluster_adapter=new Ext.form.ComboBox({
            width: 175,
            id:"cluster_adapter",
            fieldLabel: _('集群适配器'),
            allowBlank:false,
            triggerAction:'all',
            store:cluster_store,
            displayField:'value',
            valueField:'id',
            forceSelection: true,
            mode:'local',
            listWidth:175
        });
    var cluster_panel=new Ext.Panel({
        height:400,
        id:"cluster_panel",
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        tbar:[tlabel_vm_prior],
        items:[cluster_des,cluster_adapter]
    });
        var cluster_details_panel=new Ext.Panel({
        id:"panel4",
        layout:"form",
        width:100,
        //cls: 'whitebackground paneltopborder',
        height:120,
        frame:false,
        labelWidth:130,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[cluster_panel]
    });
    return cluster_details_panel;
}

function show_server_checkbox (value,params,record){
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
                        record.set('is_standby',true);
//                        field.setValue(true);
                    }else{
                        record.set('is_standby',false);
//                        field.setValue(false);
                    }
                }
            }
        });
    }).defer(5);
    return '<span id="' + id + '"></span>';
}

function show_desc(des,width,height,title){
    var id=Ext.id();
    if (width==null)
        width=300;
    if (height==null)
        height=150;
    if (title==null)
        title=_("信息");
    showWindow(title,width,height+33,show_panel(des,height),id,false,true);
}

function show_panel(des,height){

    var tooltip_des=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<br/><p>'+ unescape(des)+'</p><br/>'
    });
    var tooltip_panel=new Ext.Panel({
        height:height,
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[tooltip_des]
    });
    return tooltip_panel;
}
function fencing_dialog(grid, rowIndex,fence_store,dwm){

  var fence_colModel = new Ext.grid.ColumnModel([
        {header: _("Fencing设备"), width: 150, sortable: true,dataIndex: 'fencing_device'},
        {header: _("参数"), width: 80, sortable: true, dataIndex: 'parameters'}
    ]);

    var fenc_rec = Ext.data.Record.create([
    {
        name: 'fencing_device_id',
        type: 'string'
    },
    {
        name: 'fencing_device',
        type: 'string'
    },
    ,
    {
        name: 'device_type',
        type: 'string'
    },

    {
        name: 'parameters',
        type: 'string'
    },
    {
        name: 'parameters_obj'
    }
    ]);

    var fencep_store = new Ext.data.JsonStore({
//        url:"/ha/get_fencing_param",
//        root: 'fencing_param',
//        fields:['fencing_device','parameters'],
//        successProperty:'success',
//        listeners:{
//            loadexception:function(obj,opts,res,e){
//                var store_response=Ext.util.JSON.decode(res.responseText);
//                Ext.MessageBox.alert(_("Error"),store_response.msg);
//            }
//
//        }
    }
    );

    var fence_record="";
    var fens_rec="";
    if (dwm == stackone.constants.DWM){
        fence_record=fence_store[0].fence_details;        
    }
    else{
        fens_rec=fence_store.getAt(rowIndex);
        fence_record=fens_rec.get("fence_details");
        fence_record=Ext.util.JSON.decode(fence_record);
    }

    for (var i=0;i<fence_record.length;i++){
        var parms=fence_record[i].params;
        var par_str="";
        for (var j=0;j<parms.length;j++){
                par_str+=parms[j].attribute;
                par_str+="=";
                par_str+=parms[j].value;
                if(j!=parms.length-1)
                    par_str+=",";
            }
            par_str+="";
        var r=new fenc_rec({
            fencing_device_id: fence_record[i].id,
            fencing_device: fence_record[i].name,
            device_type: fence_record[i].device_type,
            parameters: par_str,
            parameters_obj:parms
        });
        fencep_store.insert(0, r);
    }


    var server_name=""
    if (dwm==stackone.constants.DWM){
        server_name=fence_store[0].server;
        var node_id=fence_store[0].id;
    }
    else{
        server_name=grid.getSelectionModel().getSelected().get('server');       

    }
    var server=new Ext.form.Label({
             html:_("<b>服务器</b>: "+server_name+"<br/><br/>")
        });
    var win_id=Ext.id();
    var fence_new_button=new Ext.Button({
        id: 'new',
        text: _('新建'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
          click: function(btn) {
                showWindow(_("配置 Fencing 设备 & 参数"),400,320,param_dialog(fencing_grid,btn.id,win_id,fenc_rec),win_id);
          }
        }
    });
    var fence_remove_button= new Ext.Button({
        id: 'remove',
        text: _('移除'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
            click: function(btn) {
                var rec=fencing_grid.getSelectionModel().getSelected();
                Ext.MessageBox.confirm(_("确认"),_("确定要删除 fencing 设备")+rec.get("fencing_device")+"?", function (id){
                if(id=='yes'){
                    fencep_store.remove(rec);
                }
                });
            }
        }});
    var fence_edit_button= new Ext.Button({
        id: 'edit',
        text: _('编辑'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        //                enableToggle:true,
        listeners: {
          click: function(btn) {
                 if(!fencing_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从列表中选择一个项目"));
                    return;
                }
                showWindow(_("配置Fencing 设备 & 参数"),400,320,param_dialog(fencing_grid,btn.id,win_id),win_id);
          }
        }
    });


        var label_fe=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Fencing 设备")+'</div>',
        id:'label_vm'
    });
      var fencing_grid = new Ext.grid.GridPanel({
//        title:'Performance Details',
        store: fencep_store,
        colModel:fence_colModel,
        stripeRows: true,
        frame:false,
        region:'center',
        //id:'summary_grid',
        width:430,
        autoExpandColumn:1,
//        autoHeight:true,
        autoExpandMax:300,
        autoExpandMin:150,
        height:250,
        maxHeight:100,
        tbar:[label_fe,
            {
            xtype: 'tbfill'
        },
        fence_new_button,fence_edit_button,fence_remove_button],
        enableHdMenu:true,
        listeners:{
             rowdblclick:function(grid, rowIndex, e){
                showWindow(_("配置 Fencing 设备 & 参数"),400,320,param_dialog(fencing_grid,"edit",win_id),win_id);
            }
        }
    });
        var fence_ok=new Ext.Button({
        name: 'fence_ok',
        id: 'fence_ok',
        text:_("确定"),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                    var fc=fencep_store.getCount();
                    var fence_det="[";
                    for(var i=0;i<fc;i++){
                        var fc_rec=fencep_store.getAt(i);
                        fence_det+="{name:'"+fc_rec.get("fencing_device")+"',";
                        fence_det+="id: '"+fc_rec.get("fencing_device_id")+"',";
                        fence_det+="device_type: '"+fc_rec.get("device_type")+"',";
                        fence_det+="params: "+Ext.util.JSON.encode(fc_rec.get("parameters_obj"))+"}";
                        if (i!=fc-1)
                            fence_det+=",";
                    }
                    fence_det+="]";
                    if (dwm==stackone.constants.DWM){
                        var jsondata="[";
                        for(var j=0;j<fc;j++){
                            var dwm_fc_rec=fencep_store.getAt(j);
                            jsondata+="{";
                            jsondata+="'name':'"+dwm_fc_rec.get("fencing_device")+"',";
                            jsondata+="'id': '"+dwm_fc_rec.get("fencing_device_id")+"',";
                            jsondata+="'device_type': '"+dwm_fc_rec.get("device_type")+"',";
                            jsondata+="'params': "+Ext.util.JSON.encode(dwm_fc_rec.get("parameters_obj"))+"}";
                            if (j!=fc-1)
                                jsondata+=",";
                        }
                        jsondata+="]";
                        
                        var json_fenc_data=Ext.util.JSON.encode({
                            "fence_details":jsondata
                        });
                        
                        var url="/ha/save_fencing_details_fordwm?node_id="+node_id+"&fence_det="+json_fenc_data;
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                            ajaxReq.request({
                                success: function(xhr) {//alert(xhr.responseText);
                                    var response=Ext.util.JSON.decode(xhr.responseText);
                                    if (response.success){
                                        Ext.MessageBox.alert( _("成功") , "电源管理值保存成功.");
                                        closeWindow(windowid);
                                    }else{
                                        Ext.MessageBox.alert( _("失败") , response.msg);
                                    }
                                },
                                failure: function(xhr){
                                    Ext.MessageBox.alert( _("失败") , xhr.statusText);
                            }

                        })
                    }else{                    
                        fens_rec.set("fence_details",fence_det);
                        if (fc==1){
                            fc=fencep_store.getAt(0).get("fencing_device");
                        }
                        fens_rec.set("fencing_devices",fc);
                        closeWindow(windowid);
                    }
                    
            }
        }
    });
    
    var fence_cancel=new Ext.Button({
        name: 'fence_cancel',
        id: 'fence_cancel',
        text:_("取消"),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow(windowid);
            }
        }
    });
    var fenc_panel = new Ext.Panel({
		height : 320,
		layout : 'border',
		frame : false,
		width : '100%',
		autoScroll : true,
		border : false,
		bodyBorder : false,
		bodyStyle : 'padding:5px 5px 5px 5px',
		bbar : [{
			xtype : 'tbfill'
		}, fence_ok, fence_cancel]
	});
	fenc_panel.add(fencing_grid);
	return fenc_panel;
}

function param_dialog(grid,mode,win_id,fenc_rec){

        var fencing_device_store = new Ext.data.JsonStore({
        url: '/ha/get_sp_fencing_devices',
        root: 'fencing_devices',
        fields: ['id','value','fence_id','device_type','description'],
        sortInfo:{
            field:'value',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            load:function(obj,resc,f){
                if (mode=="edit"){
                    var fence_id;
                    for(var i=0;i<fencing_device_store.getCount(); i++){
                        if (fencing_device_store.getAt(i).get('value') == grid.getSelectionModel().getSelected().get("fencing_device")){
                            fence_id=fencing_device_store.getAt(i).get('fence_id');
                            break;
                        }

                    }
                    param_store.load({
                       params:{
                            fence_id:fence_id
                           }
                    }); 

                    var record="";
                    for(var j=0;j<fencing_device_store.getCount(); j++){
                        if (fencing_device_store.getAt(j).get('fence_id') == fence_id){
                            record=fencing_device_store.getAt(j);
                            break;
                        }
                    }
                    fence_combo.setValue(grid.getSelectionModel().getSelected().get("fencing_device"));
//                    fence_combo.fireEvent('select',fence_combo,record,null);
                    fence_combo.setDisabled(true);
                    if (Ext.getCmp("sp_desc_icon")!=null){
                       fentype_panel.remove("sp_desc_icon");
                    }
                    var desc_icon=new Ext.form.Label({
                        id: 'sp_desc_icon',
                        html:'<img src=icons/information.png onClick=show_desc("'+escape(record.get("description"))+'",300,200,"说明") />'
                     })
                    fentype_panel.add(desc_icon);
                    fentype_panel.doLayout();

                }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    }
    );


    fencing_device_store.load();
    var fence_combo=new Ext.form.ComboBox({
        fieldLabel: _('Fencing 设备'),
        allowBlank:false,
        width: 180,
        store:fencing_device_store,
        id:'fence_combo',
        forceSelection: true,
        triggerAction:'all',
        minListWidth:150,
        displayField:'value',
        valueField:'id',
        mode:'local',
        listeners:{
         select:function(combo,record,index){
             if(mode!="edit"){
                device_type.setValue(record.get("device_type"));
                param_store.load({
                    params:{
                        fence_id:record.get("fence_id")
                    }
                });

                if (Ext.getCmp("sp_desc_icon")!=null){
                   fentype_panel.remove("sp_desc_icon");
                }
                var desc_icon=new Ext.form.Label({
                    id: 'sp_desc_icon',
                    html:'<img src=icons/information.png onClick=show_desc("'+escape(record.get("description"))+'",300,200,"说明") />'
                 })
                fentype_panel.add(desc_icon);
                fentype_panel.doLayout();

             }
         }
     }
    });


   var device_type=new Ext.form.TextField({
        fieldLabel: _('设备类型'),
        name: 'device_type',
        width: 180,
        id: 'device_type',
        disabled:true,
        value:(mode=="edit")?grid.getSelectionModel().getSelected().get("device_type"):""
    });

   
   var param_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("属性"),
        width:150,
        dataIndex: 'attribute',
        css:'font-weight:bold; color:#414141;',
        editor: new Ext.form.TextField({
            allowBlank: false
        }),
        sortable:true
		
    },
    
    {
        header: _("值"),
        dataIndex: 'value',
//        editor: new Ext.form.TextField({
//            allowBlank: false
//        }),
//        sortable:true,
        renderer:createUI
    },

    {
        dataIndex: 'is_environ',
        hidden:true

    }
    ]);
    var param_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });



   var fenc_param = Ext.data.Record.create([
    {
        name: 'attribute',
        type: 'string'
    },

    {
        name: 'value',
        type: 'string'
    },
    {
        name: 'type',
        type: 'string'
    },
     {
        name: 'field',
        type: 'string'
    },
    ,
     {
        name: 'field_datatype',
        type: 'string'
    }
     ,
     {
        name: 'is_environ',
        type: 'string'
     }
     ,
     {
        name: 'sequence',
        type: 'integer'
    },
    {
        name: 'values',
        type: 'string'
    }
    ]);



//    alert(Ext.util.JSON.encode(param_rec));

    var param_store = new Ext.data.JsonStore({
        url: '/ha/get_sp_fencingdevice_params',
        root: 'rows',
        fields: ['attribute','value','type','field','field_datatype',
            'is_environ','sequence','values'],
        sortInfo:{
            field:'sequence',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            load:function(obj,resc,f){

                if(mode=="edit"){
                    var param_obj=grid.getSelectionModel().getSelected().get("parameters_obj");
                    for(var i=0;i<param_obj.length;i++){
                        param_store.getAt(i).set('attribute',param_obj[i].attribute);
                        param_store.getAt(i).set('value',param_obj[i].value);
                        param_store.getAt(i).set('type',param_obj[i].type);
                        param_store.getAt(i).set('field',param_obj[i].field);
                        param_store.getAt(i).set('field_datatype',param_obj[i].field_datatype);
                        param_store.getAt(i).set('is_environ',param_obj[i].is_environ);
                        param_store.getAt(i).set('sequence',param_obj[i].sequence);
    //                    param_store.getAt(i).set('values',param_obj[i].values);

                    }
                    param_store.sort('sequence','ASC');

                }

            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    }
    );



//    if(mode=="edit"){
//        var fence_id;
//        for(var i=0;i<fencing_device_store.getCount(); i++){
//            if (fencing_device_store.get('value') == grid.getSelectionModel().getSelected().get("fencing_device")){
//                fence_id=fencing_device_store.get('fence_id');
//                break;
//            }
//
//        }
//        param_store.load({
//           params:{
//                fence_id:fence_id
//               }
//        });

//        var param_obj=grid.getStore().getAt(rowIndex).get("parameters_obj");
//        var param_obj=grid.getSelectionModel().getSelected().get("parameters_obj");
//        for(var i=0;i<param_obj.length;i++){
//            var r=new fenc_param({
//                attribute: param_obj[i].attribute,
//                value: param_obj[i].value,
//                type: param_obj[i].type,
//                field: param_obj[i].field,
//                field_datatype: param_obj[i].field_datatype,
//                is_environ:param_obj[i].is_environ,
//                sequence:param_obj[i].sequence,
//                values:param_obj[i].values
//
//            });
//            param_store.insert(0, r);
//        }
//        param_store.sort('sequence','ASC');
////        fence_combo.setValue(grid.getStore().getAt(rowIndex).get("fencing_device"));
//        fence_combo.setValue(grid.getSelectionModel().getSelected().get("fencing_device"));
//        fence_combo. setDisabled(true);
//    }
    var param_add=new Ext.Button({
        name: 'param_add',
        id: 'param_add',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var r=new fenc_param({
                    attribute: '',
                    value: ' '
                });

                param_grid.stopEditing();
                param_store.insert(0, r);
                param_grid.startEditing(0, 0);
            }
        }
    });
    var param_remove=new Ext.Button({
        name: 'param_remove',
        id: 'param_remove',
        text:_("移除"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                param_store.remove(param_grid.getSelectionModel().getSelected());
            }
        }
    });


    var label_parm=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("参数")+'</div>',
        id:'label_vm'
    });
     var param_grid = new Ext.grid.EditorGridPanel({
        store: param_store,
        stripeRows: true,
        colModel:param_columnModel,
        frame:false,
        border: false,
        selModel:param_selmodel,
        autoExpandColumn:1,
        //autoExpandMin:325,
        //autoExpandMax:426,
        autoscroll:true,
        //autoHeight:true,
        height:190,
        //height: '100%',
        width: '100%',
        clicksToEdit:2,
        enableHdMenu:false,
        tbar:[label_parm,
            {
            xtype:'tbfill'
        }]

    });

     var fence_ok=new Ext.Button({
        name: 'fence_ok',
        id: 'fence_ok',
        text:_("确定"),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                    var pc=param_store.getCount();
                    var flag=0;
                    var param_det="";
                    var param_obj_str="[";
                    if(fence_combo.getValue()==""){
                        Ext.MessageBox.alert(_("错误"),_("请选择一个 fencing设备"));
                        return;
                    }
                    var parent_store=grid.getStore();
                    for(var i=0;i<pc;i++){
                        var p_rec=param_store.getAt(i);
                        for(var j=0;j<parent_store.getCount();j++){
                                var f_n=parent_store.getAt(j).get("fencing_device");
                                if (mode=="new" && f_n==fence_combo.getRawValue()){
                                     flag++;
                                     Ext.MessageBox.alert(_("错误"),_("名称已经存在: "+fence_combo.getRawValue()));
                                     break;
                                }
                        }


                        if(p_rec.get("field_datatype") && p_rec.get("value")=="" ){
                            flag++;
                            Ext.MessageBox.alert(_("错误"),_("请输入一个值"+p_rec.get("attribute")));
                            break;
                        }else if(p_rec.get("field_datatype") =="integer" && isNaN(p_rec.get("value")) ){
                            flag++;
                            Ext.MessageBox.alert(_("错误"),_("请输入number "+p_rec.get("attribute")));
                            break;
                        }else if(p_rec.get("field_datatype")=="ipaddr"){
                            var errorString=verifyIP(p_rec.get("value"));
                             if ( errorString!= ""){
                                    flag++;
                                    Ext.MessageBox.alert(_("错误"),_(errorString));
                                    break;
                              }
                        }

                        param_det+=p_rec.get("attribute")+"=";
                        param_det+=p_rec.get("value");
                        if (i!=pc-1)
                            param_det+=",";

                        param_obj_str+="{";
                        param_obj_str+="attribute:'"+p_rec.get("attribute")+"',";
                        param_obj_str+="value:'"+p_rec.get("value")+"',";
                        param_obj_str+="type:'"+p_rec.get("type")+"',";
                        param_obj_str+="field:'"+p_rec.get("field")+"',";
                        param_obj_str+="field_datatype:'"+p_rec.get("field_datatype")+"',";
                        param_obj_str+="is_environ:'"+p_rec.get("is_environ")+"',";
                        param_obj_str+="sequence:"+p_rec.get("sequence");
                        param_obj_str+="}";
                        if (i!=pc-1)
                            param_obj_str+=",";
                    }
                    param_det+="";
                    param_obj_str+="]";

                    if(flag==0){
                        if (mode=="edit"){
                            var rec=grid.getSelectionModel().getSelected();
                            rec.set("parameters",param_det);
                            rec.set("parameters_obj",null);
                            rec.set("parameters_obj",Ext.util.JSON.decode(param_obj_str));
                        }else{
                            var r=new fenc_rec({
                                fencing_device_id:fence_combo.getValue(),
                                fencing_device:fence_combo.getRawValue(),
                                device_type:device_type.getValue(),
                                parameters: param_det,
                                parameters_obj:Ext.util.JSON.decode(param_obj_str)
                            });
                            grid.getStore().insert(0, r);
                        }
                        closeWindow(win_id);
                    }
            }
        }
    });
    var fence_cancel=new Ext.Button({
        name: 'fence_cancel',
        id: 'fence_cancel',
        text:_("取消"),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow(win_id);

            }
        }
    });
    var fen_label=new Ext.form.Label({
        html:_('设备类型:')
    });
    var dummy_space=new Ext.form.Label({
        html:_('&nbsp;<div style="width:34px"/>')
    });
    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:6px"/>')
    });
    var dummy_space3=new Ext.form.Label({
        html:_('<div style="height:10px"/>')
    });
    var fentype_panel=new Ext.Panel({
        id:"fentype_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:27,
//        bodyStyle:'padding-left:8px',
        items:[fen_label,dummy_space,device_type,dummy_space1]
    });
   var fenc_panel=new Ext.Panel({
        height:290,
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        bbar:[{
            xtype:'tbfill'
        },fence_ok,fence_cancel],

        items:[fence_combo,fentype_panel,dummy_space3,param_grid]
    });
    return fenc_panel;

}

function edit_fencedetails(data,cellmd,record,row,col,store){
        var returnVal = '<img title="Edit Fencing Details" src="icons/file_edit.png "/>';
        return returnVal;
}


function createUI(value, meta, rec){
     var type=rec.get('type');
     var id = Ext.id();
     if (type=="filebrowser"){
        (function(){
            var loc=new Ext.form.TriggerField({
                    renderTo: id,
                    allowBlank:false,
                    width:120,
                    triggerClass : "x-form-search-trigger",
                    onTriggerClick:function(){
                        file_browser=new Ext.Window({
                            title:_("选择文件"),
                            width : 515,
                            height: 425,
                            modal : true,
                            resizable : false
                        });
                        var url="";
                        file_browser.add(FileBrowser("/","",url,true,false,loc,file_browser));
                        file_browser.show();
                    },
                    listeners: {
                         change: function(obj) {
//                            alert('newval');
                        }
                    }


              });
        }).defer(25);

        return '<span id="' + id + '"></span>';
     }else if(type=="checkbox"){
        (function(){
            new Ext.form.Checkbox({
                renderTo: id,
                checked:value,
                width:100,
                height:16,
                listeners: {
                     check: function(obj) {
                        if(obj.checked)
                            rec.set('value',true);
                        else
                            rec.set('value',false);
                    }
                }
            });
        }).defer(25);
        return '<span id="' + id + '"></span>';
     }else if(type=="textfield" || type=="ipaddr"){
        (function(){
            new Ext.form.TextField({
                width: 160,
                renderTo: id,
                value:value,
                listeners: {
                      change: function(obj,newValue,oldValue) {
                          rec.set('value',newValue);
                    }
                }
            });
        }).defer(25);
        return '<span id="' + id + '"></span>';
     }else if(type=="passwordfield"){
        (function(){
            new Ext.form.TextField({
                width: 160,
                renderTo: id,
                inputType : 'password',
                value:value,
                listeners: {
                      change: function(obj,newValue,oldValue) {
                          rec.set('value',newValue);
                    }
                }
            });
        }).defer(25);
        return '<span id="' + id + '"></span>';
     }else if(type=="combobox"){
        (function(){
            var values=rec.get('values');
            //alert(values);
            if(values!=null && values!=""){
                values=eval('('+values+')');
            }
            var store = new Ext.data.SimpleStore({
                fields: ['value', 'name'],
                sortInfo:{
                    field:'name',
                    direction:'ASC'
                },
                data : values
            });
            
            if (value==''){
                value="off";                
            }
            new Ext.form.ComboBox({
                allowBlank:false,
                triggerAction:'all',
                store: store,
                renderTo: id,
                value:value,
                displayField:'name',
                valueField:'value',
                width: 160,
                forceSelection: true,
                mode:'local',
                listeners: {
                      select: function(obj,newrec,oldValue) {
                          rec.set('value',newrec.get('value'));
                    }
                }
             });
        }).defer(25);
        return '<span id="' + id + '"></span>';
     }else{
        return value; 
    }
}
 function create_fencing_dc_panel(node){

   var dc_des=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<p>作用：配置fencing使故障服务器从存储中断开，使其上面的虚拟机在另一台正常服务器上运行，以消除两台物理服务器运行相同虚拟机的风险. '+
            ' '+
            ' '+
            ' '+
            ' '+
            ' '+
            '<br/><br/>注意：当您选择动态工作负载管理器政策的电源策略,服务器可能需要断电.'+
            ' '+
            ''+
    '</p>'
    });
   var fencedc_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("设备名称"),
        width:180,
        dataIndex: 'fencing_name',
        css:'font-weight:bold; color:#414141;',
        sortable:true
    },

    {
        header: _("设备类型"),
        dataIndex: 'fencing_type',
        width:230,
        sortable:true
    }
    ]);
    var fence_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var fenc_rec = Ext.data.Record.create([
    {
        name: 'id',
        type: 'string'
    },
    {
        name: 'fencing_name',
        type: 'string'
    },
    {
        name: 'fencing_type',
        type: 'string'
    },

    {
        name: 'fencing_params',
        type: 'string'
    }
    ]);

    var fence_store = new Ext.data.JsonStore({
        url: '/ha/get_dc_fence_resources',
        root: 'fencing_details',
        fields: ['id','fencing_name','fencing_type','fencing_clasn','fencing_params'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }

        }
    }
    );
    windowid=Ext.id();
    fence_store.load();
    var fenc_add=new Ext.Button({
        name: 'new',
        id: 'new',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                    showWindow(_("设置 Fencing 设备"),460,320,dc_fencing_dialog(fenc_grid,windowid,btn.id,fenc_rec),windowid);
            }
        }
    });
    var fenc_remove=new Ext.Button({
        name: 'remove',
        id: 'remove',
        text:_("移除"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var rec=fenc_grid.getSelectionModel().getSelected();
                var res_id=rec.get("id");
                var f_name=rec.get("fencing_name");
//                fence_store.remove(fenc_grid.getSelectionModel().getSelected());
                remove_fencing_device(fence_store,res_id,f_name);

            }
        }
    });
    var fenc_edit=new Ext.Button({
        name: 'edit',
        id: 'edit',
        text:_("编辑"),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var rec=fenc_grid.getSelectionModel().getSelected();
                if(!rec){
                    Ext.MessageBox.alert(_("错误"),_("请从列表中选择一个项目"));
                    return;
                }
                var res_id=rec.get("id");
                showWindow(_("编辑 Fencing设备"),460,320,dc_fencing_dialog(fenc_grid,windowid,btn.id,fenc_rec,res_id),windowid);

            }
        }
    });
     var fenc_grid = new Ext.grid.GridPanel({
        store: fence_store,
        id:'fenc_grid',
        stripeRows: true,
        colModel:fencedc_columnModel,
        frame:false,
        border:false,//lbz更改：去掉边框
        selModel:fence_selmodel,
        //autoExpandColumn:1,
        //autoScroll:true,
        //height:'100%',
        height:350,
        width:'100%',
        forceSelection: true,
        enableHdMenu:false,
//        id:'fenc_grid',
        tbar:[
            _('搜索: '),new Ext.form.TextField({
            fieldLabel: _('搜索'),
            name: 'search',
            id: 'search_info',
            allowBlank:true,
            enableKeyEvents:true,
            width:100,
            listeners: {
                keyup: function(field) {
                    fenc_grid.getStore().filter('fencing_name', field.getValue(), false, false);
                }
            }
        })
            ,
            {
            xtype:'tbfill'
        },fenc_add,fenc_edit,fenc_remove],
         listeners:{
             rowdblclick:function(grid, rowIndex, e){
                var rec=fenc_grid.getSelectionModel().getSelected();
                var res_id=rec.get("id");
                showWindow(_("编辑Fencing设备"),460,320,dc_fencing_dialog(fenc_grid,windowid,"edit",fenc_rec,res_id),windowid);
            }
        }

    });

    // General Panel declaration
    var label_adv=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("配置Fencing 设备")+'<br/></div>'
    });

    var tlabel_fencing=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("设置Fencing以启动高可用")+'</div>'
    });
    var fence_panel=new Ext.Panel({
        height:375,//lbz更改：375--475
        id:"panel0",
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding:5px 5px 5px 5px',//lbz更改：注释掉
        //tbar:[tlabel_fencing],
        items:[fenc_grid],//lbz更改：dc_des,
        listeners:{
            show:function(p){
                if(fence_store.getCount()>0){
                    fence_store.sort('server','ASC');
                }
            }
        }
    });
        var fencing_panel=new Ext.Panel({
        id:"panel0",
        layout:"form",
        width:'100%',
        //cls: 'whitebackground paneltopborder',
        height:'100%',
        frame:false,
       // labelWidth:130,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[fence_panel]
    });




//        var fenc_detailpanel=new Ext.Panel({
//        id:"panel0",
//        layout:"form",
//        width:100,
//        //cls: 'whitebackground paneltopborder',
//        height:120,
//        frame:false,
//        labelWidth:130,
//        bodyStyle:'border-top:1px solid #AEB2BA;',
//        items:[label_adv, fenc_grid]
//    });

    return fence_panel;
 }

 //data center level ha uiwindowid
 function data_center_ha(node,action){
      var treePanel= new Ext.tree.TreePanel({
        region:'west',
        width:180,
        rootVisible:false,
        border: false,
        lines : false,
        id:'treePanel',
        cls:'leftnav_treePanel',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        listeners: {
            click: function(item) {
                var id=item.id;
                process_card_panel(card_panel,treePanel,id.substr(4,id.length),"treepanel");
            }
        }
    });

    // root node of tree view
    var rootNode = new Ext.tree.TreeNode({
        text	: '根节点',
        draggable: false,
        id		: 'rootnode',
        listeners: {
            expand : function(btn) {
                treePanel.getNodeById("node0").select();
            }
        }
    });
    var generalNode = new Ext.tree.TreeNode({
        text: _('Fencing 设备'),
        draggable: false,
        id: "node0",
        icon:'icons/vm-general.png',
        nodeid: "fencing",
        leaf:false,
        allowDrop : false
       // cls:"labelcolor"
    });


    var fencing_details_panel=create_fencing_dc_panel(node);

    var button_prev=new Ext.Button({
        id: 'move-prev',
        text: _('上一步'),
        disabled: true,
        icon:'icons/prev.gif',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                process_card_panel(card_panel,treePanel,-1);
            }
        }
    });
    var button_next=new Ext.Button({
        id: 'move-next',
        text: _('下一步'),
        icon:'icons/next.gif',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                process_card_panel(card_panel,treePanel,1);
            }
        }
    });
  var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('确定'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
//                submit_dc_hadetails(fencing_details_panel,node.attributes.id,node.attributes.nodetype);
                closeWindow();
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
                closeWindow();
            }
        }
     });
    // card panel for all panels
    var card_panel=new Ext.Panel({
        //width:620,//lbz更改435--880
        //height:390,//lbz更改：
        width:630,//lbz更改435--880
        height:400,//lbz更改：
        layout:"card",
        id:"card_panel",
        //        activeItem:0,
        cls: 'whitebackground',
        border:false,
        bbar:[
        {
            xtype: 'tbfill'
        },button_ok,button_cancel],//lbz更改：去除button_prev,button_next,
        items:[fencing_details_panel]
    //
    });
    rootNode.appendChild(generalNode);
    var treeheading=new Ext.form.Label({
        html:'<br/><br/>'
    });

    var side_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:180,
        height:588,
        id:'side_panel',
        cls:'westPanel',
        items:[treeheading,treePanel]

    });
    var right_panel=new Ext.Panel({
        id:"right_panel",
        width:900,//lbz更改：448--890
        height:490,//lbz更改：600--480
        //frame:true,
        cls: 'whitebackground',
        border:false
        //bodyStyle:'padding:5px 5px 5px 5px'
//        items:[change_settings]
    });
    var outerpanel=new Ext.FormPanel({
        width:900,
        height:490,
        autoEl: {},
        layout: 'column',
        border:false,
        items:[right_panel]//side_panel,]

    });
    right_panel.add(card_panel);
    card_panel.activeItem = 0;
    treePanel.setRootNode(rootNode);

    return outerpanel;

 }

 function dc_fencing_dialog(grid,win_id,mode,fenc_rec,res_id){

    var dev_name=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'dev_name',
        width: 190,
        id: 'dev_name'

    });

    var fen_classifica_combo = new Ext.data.JsonStore({
        url: '/ha/ha_fence_resource_types_classification',
        root: 'fence_resources',
        fields: ['classification'],
        successProperty:'success',
        listeners:{
            load:function(obj,resc,f){
 
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }

    });
    fen_classifica_combo.load();


    var fen_combo = new Ext.form.ComboBox({
        fieldLabel: _('分类'),
        typeAhead: true,
        triggerAction: 'all',
        lazyRender:true,
        mode: 'local',
        width: 190,
        minListWidth:190,
        store:fen_classifica_combo,
        listeners:{
            select:function(obj,resc,f){
             fence_combo.getStore().load({
                    params:{
                        category:fen_combo.getValue()
                    }
             })
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        },
        valueField: 'classification',
        displayField: 'classification'
    });

   var fencing_device_store = new Ext.data.JsonStore({
        url: '/ha/ha_fence_resource_types',
        root: 'fence_resources',
        fields: ['id','value','name','description'],
        sortInfo:{
            field:'value',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            load:function(obj,resc,f){
                 if(mode=="edit"){
                    var fence_id;
                    for(var i=0;i<fencing_device_store.getCount(); i++){
                        if (fencing_device_store.getAt(i).get('value') == grid.getSelectionModel().getSelected().get("fencing_type")){
                            fence_id=fencing_device_store.getAt(i).get('id');
                            break;
                        }

                    }
                    param_store.load({
                       params:{
                            fence_id:fence_id
                           }
                    });
                    var record="";
                    for(var j=0;j<fencing_device_store.getCount(); j++){
                        if (fencing_device_store.getAt(j).get('id') == fence_id){
                            record=fencing_device_store.getAt(j);
                            break;
                        }
                    }
                    fence_combo.setValue(grid.getSelectionModel().getSelected().get("fencing_type"));
                    fence_combo.fireEvent('select',fence_combo,record,null);
                 }else{
                     fence_combo.setValue("");
                     fen_panel.remove("desc_icon");
                 }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    }
    );
   var fence_combo=new Ext.form.ComboBox({
        fieldLabel: _('设备类型'),
        allowBlank:false,
        width: 190,
        store:fencing_device_store,
        id:'fence_combo',
        forceSelection: true,
        triggerAction:'all',
        minListWidth:190,
        displayField:'value',
        valueField:'id',
        mode:'local',
        listeners:{
         select:function(combo,record,index){
//             if(mode!="edit"){
                param_store.load({
                    params:{
                        fence_id:record.get("id")
                    }
                });
                if (Ext.getCmp("desc_icon")!=null){
                   fen_panel.remove("desc_icon");
                }
                var desc_icon=new Ext.form.Label({
                    id: 'desc_icon',
                    html:'<img src=icons/information.png onClick=show_desc("'+escape(record.get("description"))+'",300,200,"说明") />'
                 })
                fen_panel.add(desc_icon);
                fen_panel.doLayout();
//             }
         }
       }
    });


   var param_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("属性"),
        width:150,
        dataIndex: 'attribute',
        css:'font-weight:bold; color:#414141;',
        editor: new Ext.form.TextField({
            allowBlank: false
        }),
        sortable:true,
		renderer:function(value, meta, rec) {
			var m = {
				'IP Address':'IP地址',
				'Login':'登录名',
				'Password':'密码',
				'Hostname':'主机名',
				'device':'设备',
				'Port':'端口',
				'Node Name':'节点名称'
				};
			if (m[value] != undefined) { return m[value]};
			return value;
		}
    },

    {
        header: _("值"),
        dataIndex: 'value',
//        editor: new Ext.form.TextField({
//            allowBlank: false
//        }),
//        sortable:true,
        renderer:createUI
    }
    ]);
    var param_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var param_store = new Ext.data.JsonStore({
        url: '/ha/ha_fence_resource_type_meta',
        root: 'rows',
        fields: ['id','attribute','value','field','type','field_datatype','sequence','values'],

        sortInfo:{
            field:'sequence',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            load:function(obj,resc,f){
                if(mode=="edit"){
                    var param_obj=grid.getSelectionModel().getSelected().get("fencing_params");
                    param_obj=Ext.util.JSON.decode(param_obj);
                    for(var i=0;i<param_obj.length;i++){
                        param_store.getAt(i).set('id',param_obj[i].id);
                        param_store.getAt(i).set('attribute',param_obj[i].attribute);
                        param_store.getAt(i).set('value',param_obj[i].value);
                        param_store.getAt(i).set('field',param_obj[i].field);
                        param_store.getAt(i).set('type',param_obj[i].type);
                        param_store.getAt(i).set('field_datatype',param_obj[i].field_datatype);
                        param_store.getAt(i).set('sequence',param_obj[i].sequence);
//                        param_store.getAt(i).set('values',param_obj[i].values);

//                        param_store.insert(0, r);
                    }
                    param_store.sort('sequence','ASC');
            //        fence_combo.setValue(grid.getSelectionModel().getSelected().get("fencing_id"));

                }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }

        }
    }
    );

//    param_store.load();
    var param_rec = Ext.data.Record.create([
    {
        name: 'id',
        type: 'string'
    },
    {
        name: 'attribute',
        type: 'string'
    },

    {
        name: 'value',
        type: 'string'
    },
    {
        name: 'type',
        type: 'string'
    },
    {
        name: 'field',
        type: 'string'
    },
     {
        name: 'field_datatype',
        type: 'string'
    },
     {
        name: 'sequence',
        type: 'integer'
    },
     {
        name: 'values',
        type: 'string'
    }
    ]);

//
//    if(mode=="edit"){
//        var param_obj=grid.getStore().getAt(rowIndex).get("fencing_params");
//        for(var i=0;i<param_obj.length;i++){
//            var r=new fenc_param({
//                attribute: param_obj[i].attribute,
//                value: param_obj[i].value,
//                type: param_obj[i].type
//            });
//            param_store.insert(0, r);
//        }
//        fence_combo.setValue(grid.getStore().getAt(rowIndex).get("fencing_device"));
//        fence_combo. setDisabled(true);
//    }


//    if(mode=="edit"){
//        var param_obj=grid.getSelectionModel().getSelected().get("fencing_params");
//        param_obj=Ext.util.JSON.decode(param_obj);
//        for(var i=0;i<param_obj.length;i++){
//            var r=new param_rec({
//                id: param_obj[i].id,
//                attribute: param_obj[i].attribute,
//                value: param_obj[i].value,
//                field: param_obj[i].field,
//                type: param_obj[i].type,
//                field_datatype:param_obj[i].field_datatype,
//                sequence:param_obj[i].sequence,
//                values:param_obj[i].values
//            });
//            param_store.insert(0, r);
//        }
//        param_store.sort('sequence','ASC');
////        fence_combo.setValue(grid.getSelectionModel().getSelected().get("fencing_id"));
//        fence_combo.setValue(grid.getSelectionModel().getSelected().get("fencing_type"));
//        dev_name.setValue(grid.getSelectionModel().getSelected().get("fencing_name"));
////        dev_name.setDisabled(true);
//        fence_combo.setDisabled(true);
//    }


    var param_add=new Ext.Button({
        name: 'param_add',
        id: 'param_add',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var r=new param_rec({
                    attribute: '',
                    value: ' '
                });

                param_grid.stopEditing();
                param_store.insert(0, r);
                param_grid.startEditing(0, 0);
            }
        }
    });
    var param_remove=new Ext.Button({
        name: 'param_remove',
        id: 'param_remove',
        text:_("移除"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                param_store.remove(param_grid.getSelectionModel().getSelected());
            }
        }
    });

    var label_parm=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("参数")+'</div>',
        id:'label_vm'
    });
     var param_grid = new Ext.grid.EditorGridPanel({
        store: param_store,
        stripeRows: true,
        colModel:param_columnModel,
        frame:false,
        border: false,
        selModel:param_selmodel,
        autoExpandColumn:1,
        //autoExpandMin:325,
        //autoExpandMax:426,
        autoscroll:true,
        //autoHeight:true,
        height:150,
        //height: '100%',
        width: '100%',
        clicksToEdit:2,
        enableHdMenu:false,
        tbar:[label_parm,
            {
            xtype:'tbfill'
        }
//        param_add,param_remove
    ]

    });
     var fence_ok=new Ext.Button({
        name: 'fence_ok',
        id: 'fence_ok',
        text:_("确定"),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                    var pc=param_store.getCount();
                    var flag=0;
                    var param_obj_str="[";

                    var parent_store=grid.getStore();

                    for(var i=0;i<pc;i++){
                        var p_rec=param_store.getAt(i);

                        for(var j=0;j<parent_store.getCount();j++){
                                var f_n=parent_store.getAt(j).get("fencing_name");
                                if (mode=="new" && f_n==dev_name.getValue()){
                                     flag++;
                                     Ext.MessageBox.alert(_("错误"),_("名称已经存在: "+dev_name.getValue()));
                                     break;
                                }else if(mode=="edit"){
                                    var f_name=grid.getSelectionModel().getSelected().get("fencing_name");
                                    if(f_n!=f_name && f_n==dev_name.getValue()){
                                        flag++;
                                        Ext.MessageBox.alert(_("错误"),_("名称已经存在: "+dev_name.getValue()));
                                        break;
                                    }
                                }
                        }

                        if(p_rec.get("field_datatype") && p_rec.get("value")=="" ){
                            flag++;
                            Ext.MessageBox.alert(_("错误"),_("请输入一个值"+p_rec.get("attribute")));
                            break;

                        }else if(p_rec.get("field_datatype") =="integer" && isNaN(p_rec.get("value")) ){
                            flag++;
                            Ext.MessageBox.alert(_("错误"),_("请输入number "+p_rec.get("attribute")));
                            break;

                        }else if(p_rec.get("field_datatype")=="ipaddr"){
                            var errorString=verifyIP(p_rec.get("value"));
                             if ( errorString!= ""){
                                    flag++;
                                    Ext.MessageBox.alert(_("错误"),_(errorString));
                                    break;
                              }
                        }

                        param_obj_str+="{";
                        param_obj_str+="id:'"+p_rec.get("id")+"',";
                        param_obj_str+="attribute:'"+p_rec.get("attribute")+"',";
                        param_obj_str+="value:'"+p_rec.get("value")+"',";
                        param_obj_str+="field:'"+p_rec.get("field")+"',";
                        param_obj_str+="type:'"+p_rec.get("type")+"',";
                        param_obj_str+="field_datatype:'"+p_rec.get("field_datatype")+"',";
                        param_obj_str+="sequence:"+p_rec.get("sequence");
                        param_obj_str+="}";
                        if (i!=pc-1)
                            param_obj_str+=",";
                    }
                    param_obj_str+="]";

//                    if (mode=="edit"){
//                        var rec=grid.getSelectionModel().getSelected();
////                        alert(param_obj_str);
//                        rec.set("fencing_name",dev_name.getValue());
//                        rec.set("fencing_params",param_obj_str);
//                    }else{
//                        var r=new fenc_rec({
//                            id:fence_combo.getValue(),
//                            fencing_name:dev_name.getValue(),
//                            fencing_type:fence_combo.getRawValue(),
//                            fencing_params:param_obj_str
//                        });
//                        grid.getStore().insert(0, r);
//                    }



//                    var fpstore=grid.getStore();
//                    for(var j=0;j<fpstore.getCount();j++){
//                        if(dev_name.getValue()==fpstore.getAt(j).get("fencing_name")){
//                            flag++;
//                            Ext.MessageBox.alert(_("Error"),_("Name already existing"));
//                            break
//                        }
//                    }
                    if(dev_name.getValue()=="" || dev_name.getValue()==null){
                            flag++;
                            Ext.MessageBox.alert(_("错误"),_("请输入Name"));
                    }

                    if(flag==0){
                        var  param_obj=Ext.util.JSON.decode(param_obj_str);
                        var fence_params=new Object();
                        fence_params.fence_details=param_obj;

                        var jsondata= Ext.util.JSON.encode({
                        "param_obj":param_obj
                        });


                       if (mode=="edit"){
                            var url="/ha/update_dc_params?res_id="+res_id+"&fencing_name="+dev_name.getValue()+"&fencing_id="+fence_combo.getValue()+"&params="+jsondata;
                       }
                       else{
                           var url="/ha/save_dc_params?fencing_name="+dev_name.getValue()+"&fencing_id="+fence_combo.getValue()+"&params="+jsondata;
                       }

                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {//alert(xhr.responseText);
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                       closeWindow(win_id);
                                       grid.getStore().load();
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
        }
    });
    var fence_cancel=new Ext.Button({
        name: 'fence_cancel',
        id: 'fence_cancel',
        text:_("取消"),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow(win_id);

            }
        }
    });

    var fen_label=new Ext.form.Label({
        html:_('设备类型:')
    });
    var dummy_space=new Ext.form.Label({
    	//lbz更改：40--53
        html:_('&nbsp;<div style="width:53px"/>')
    });
    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:6px"/>')
    });
    var dummy_space3=new Ext.form.Label({
        html:_('&nbsp;<div style="height:4px"/>')
    });
     var fen_panel=new Ext.Panel({
        id:"fpanel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:30,//lbz更改：20--30
//        bodyStyle:'padding-left:8px',
        items:[fen_label,dummy_space,fence_combo,dummy_space1]
    });

   var fenc_panel=new Ext.Panel({
        height:290,
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        bbar:[{
            xtype:'tbfill'
        },fence_ok,fence_cancel],

        items:[dev_name,fen_combo,fen_panel,dummy_space3,param_grid]
        //items:[dev_name,fence_combo,fen_desc,param_grid]
    });

    if (mode=="edit"){
        fen_combo.setValue(grid.getSelectionModel().getSelected().get("fencing_clasn"))
        fen_combo.fireEvent('select',fen_combo,null,null);
        dev_name.setValue(grid.getSelectionModel().getSelected().get("fencing_name"));
        fen_combo.setDisabled(true);
        fence_combo.setDisabled(true);
    }
    return fenc_panel;

 }
 function submit_sp_hadetails(general_panel,vm_priority_panel,fencing_panel,advanced_panel,
                cluster_panel,node_id,node_type,win_id){

    var general_object=new Object();
    var vm_priority_object=new Object();
    var fence_object=new Object();
    var advance_object=new Object();
    var cluster_object=new Object();

    //general panel
    var enable_ha=general_panel.items.get("enable_ha_panel").items.get("enable_ha").getValue();
//    var no_standy_by=general_panel.items.get("dedicated_server_panel").items.get("dedicate").getValue();
//    var migrate_back=general_panel.items.get("migrate_panel").items.get("migrate_back").getValue();
    var servers_grid=general_panel.items.get("standby_panel").items.get("servers_grid");
    var server_store=servers_grid.getStore();

    var server_list="["
    for(var i=0;i<server_store.getCount();i++){
//            alert(server_store.getAt(i).get("is_standby"));

//        if(server_store.getAt(i).get("is_standby")){
            server_list+="{ server_id:'"+server_store.getAt(i).get("node_id")+"'";
            server_list+=","
            server_list+="server_name:'"+server_store.getAt(i).get("name")+"'";
            server_list+=","
            server_list+="is_standby:"+server_store.getAt(i).get("is_standby");
            server_list+=" }"
//            }
        if (i!=server_store.getCount()-1)
            server_list+=","
    }
    server_list+="]"
    //vif= eval("("+vif+")");
    server_list=Ext.util.JSON.decode(server_list);

    var flag=false;
    for(var i=0;i<server_store.getCount();i++){
        if(server_store.getAt(i).get("is_standby")){
            flag=true;
            break;
        }
    }
    if(!(Ext.getCmp("vm_failover_radio").getValue()) && Ext.getCmp("migrate_standby").getValue() && !flag){
        Ext.MessageBox.alert( _("失败") , "选择一个备用服务器");
        return;
    }
    var migrate_back=Ext.getCmp("migrate_back").getValue();
    if (Ext.getCmp("migrate_standby").getValue() && flag){
        migrate_back=Ext.getCmp("migrate_standby").getValue();
    }
    var use_standby=false;
    if(Ext.getCmp("migrate_standby").getValue()){
        use_standby=true;
    }
    var failover=0;
    if(Ext.getCmp("vm_failover_radio").getValue()){
       failover=stackone.constants.VM_FAILOVER;
    }
    if(Ext.getCmp("vm_server_failover_radio").getValue()){
       failover=stackone.constants.VM_SERVER_FAILOVER;
    }
    general_object.enable_ha=enable_ha;
    general_object.failover=failover;
//    general_object.no_standy_by=no_standy_by;
    general_object.migrate_back=migrate_back
    general_object.use_standby=use_standby
    general_object.preferred_servers_list=server_list;

    // vm priority panel
    var vm_grid=vm_priority_panel.items.get("vm_grid");
    var vm_store=vm_grid.getStore();

    var vm_list="["
    for(i=0;i<vm_store.getCount();i++){
            vm_list+="{ vm_id:'"+vm_store.getAt(i).get("node_id")+"'";
            vm_list+=","
            vm_list+="ha_priority:'"+vm_store.getAt(i).get("ha_priority")+"'";
            vm_list+=" }"
        if (i!=vm_store.getCount()-1)
            vm_list+=","
    }
    vm_list+="]"
    vm_list=Ext.util.JSON.decode(vm_list);

    vm_priority_object.vm_priority_list=vm_list;


    // fencing panel
    var fence_grid=fencing_panel.items.get("fencing_grid")
    var fence_store=fence_grid.getStore();

    var fence_details="[";
    for(i=0;i<fence_store.getCount();i++){
            fence_details+="{ 'server_id':'"+fence_store.getAt(i).get("id")+"', ";
            fence_details+="'fencing_data':"+fence_store.getAt(i).get("fence_details")+"}";
            if (i!=fence_store.getCount()-1)
                fence_details+=","
    }
    fence_details+="]";

//    alert(fence_details);
    fence_details=Ext.util.JSON.decode(fence_details);
    fence_object.fence_details=fence_details;

//    alert(fence_details);

    // advance panel
//    var adv_grid=advanced_panel.items.get("adv_grid")
//    var adv_store=adv_grid.getStore();
//
//    for(i=0;i<adv_store.getCount();i++){
//        var attribute=adv_store.getAt(i).get("attribute");
//        var adv_value="";
//
//        adv_value=process_value(adv_store.getAt(i).get("value"));
//        if(attribute!="" && adv_store.getAt(i).get("value")!="")
//            eval('advance_object.'+attribute+'='+adv_value);
//    }
    advance_object.wait_interval=Ext.getCmp("wait_interval").getValue();
    advance_object.retry_count=Ext.getCmp("retry_count").getValue();

    // cluster panel
    var cluster_adapter=cluster_panel.items.get("cluster_adapter").getValue()
    cluster_object.cluster_adapter=cluster_adapter;



    var jsondata= Ext.util.JSON.encode({
    "general_object":general_object,
    "vm_priority_object":vm_priority_object,
    "fence_object":fence_object,
    "advance_object":advance_object,
    "cluster_object":cluster_object
    });
    var params="&ha_data="+jsondata;
    var url="/ha/process_ha?node_id="+node_id+"&node_type="+node_type+params;
    Ext.MessageBox.show({
        title:_('请稍后...'),
        msg: _('请稍后...'),
        width:600,
        wait:true,
        waitConfig: {
            interval:200
        }
    });
//    alert(url);
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);

            Ext.MessageBox.hide();
            if(response.success){
                var msg="";
                msg=_("高可用修改任务成功提交");
                Ext.MessageBox.alert(_("状态"),msg);

            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }
            closeWindow(win_id);

        },
        failure: function(xhr){
            closeWindow(win_id);
            Ext.MessageBox.hide();
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });

 }

// function submit_dc_hadetails(fencing_panel,node_id,node_type){
//
//    // dc fencing panel
//    var fence_object=new Object();
//    var fence_grid=fencing_panel.items.get("fenc_grid")
//    var fence_store=fence_grid.getStore();
//
//    var fence_details="[";
//    for(var i=0;i<fence_store.getCount();i++){
//            fence_details+="{ 'fencing_id':'"+fence_store.getAt(i).get("fencing_id")+"', ";
//            fence_details+=" 'fencing_name':'"+fence_store.getAt(i).get("fencing_name")+"', ";
//            fence_details+=" 'display_name':'"+fence_store.getAt(i).get("fencing_type")+"', ";
//            fence_details+="'fencing_data':"+fence_store.getAt(i).get("fencing_params")+"}";
//            if (i!=fence_store.getCount()-1)
//                fence_details+=","
//    }
//    fence_details+="]";
//
////    alert(fence_details);
//    fence_details=Ext.util.JSON.decode(fence_details);
//    fence_object.fence_details=fence_details;
//
//    var jsondata= Ext.util.JSON.encode({
//    "fence_object":fence_object
//    });
//
//    var params="&ha_data="+jsondata;
//    var url="ha/process_ha?node_id="+node_id+"&node_type="+node_type+params;
//    Ext.MessageBox.show({
//        title:_('Please wait...'),
//        msg: _('Please wait...'),
//        width:600,
//        wait:true,
//        waitConfig: {
//            interval:200
//        }
//    });
////    alert(url);
//    //alert('jsondata:'+jsondata.general_object.start_checked);
//    var ajaxReq=ajaxRequest(url,0,"POST",true);
//    ajaxReq.request({
//        success: function(xhr) {//alert(xhr.responseText);
//            var response=Ext.util.JSON.decode(xhr.responseText);
//
//            Ext.MessageBox.hide();
//            if(response.success){
//                var msg="";
//                msg=_("High Avaibility changes submitted successfully");
//                Ext.MessageBox.alert(_("Status"),msg);
////                if (action =="EDIT_VM_INFO" || action =="PROVISION_VM"){
////                    node.fireEvent('click',node);
////                }
//
//            }else{
//                Ext.MessageBox.alert(_("Failure"),response.msg);
//            }
//        },
//        failure: function(xhr){
//            Ext.MessageBox.hide();
//            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
//        }
//    });
//
// }

 function remove_fencing_device(fence_store,res_id,f_name){


    Ext.MessageBox.confirm(_("确认"),_("确定要删除fencing 设备")+f_name+"?", function (id){
       
       if(id=='yes'){
            var url="/ha/remove_fencing_device?res_id="+res_id;
            var ajaxReq=ajaxRequest(url,0,"POST",true);
            ajaxReq.request({
                success: function(xhr) {//alert(xhr.responseText);
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
                           fence_store.load();
                    }else{
                        Ext.MessageBox.alert(_("失败"),response.msg);
                    }
                },
                failure: function(xhr){
                    Ext.MessageBox.alert( _("失败") , xhr.statusText);
                }
            });
       }
    });
 }
function verifyIP (IPvalue) {
    var errorString = "";
   

    var ipPattern = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
    var ipArray = IPvalue.match(ipPattern);

    if (IPvalue == "0.0.0.0")
        errorString = errorString + IPvalue+' is not a valid IP address.';
    else if (IPvalue == "255.255.255.255")
        errorString = errorString + IPvalue+' is not a valid IP address.';
    if (ipArray == null)
        errorString = errorString + IPvalue+' is not a valid IP address.';
    else {
        for (var i = 0; i < 4; i++) {
                var thisSegment = ipArray[i];
                if (thisSegment > 255) {
                    errorString = errorString + IPvalue+' is not a valid IP address.';
                    i = 4;
                }
                if ((i == 0) && (thisSegment > 255)) {
                    errorString = errorString + IPvalue+' is not a valid IP address.';
                    i = 4;
                }
           }
    }
    return errorString;
}
