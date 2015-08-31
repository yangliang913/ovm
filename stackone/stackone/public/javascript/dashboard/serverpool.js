/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
//var search_bkp_textbox;
var task_store_b;
var backuptask_info_grid_b;
var task_store_r;
var backuptask_info_grid_r;

function server_pool_summary_page(mainpanel,node_id,node){
    //node_id='d9a3bd4a-062a-5017-22af-94222763e8b9';
    if(mainpanel.items)
        mainpanel.removeAll(true);

    var label0_1=new Ext.form.Label({
        html:'<div class="toolbar_hdg" >'+_("Daily")+'<br/></div>'
    });
    var label1_1=new Ext.form.Label({
        //html:getChartHdrMsg(node.text,"Hourly","CPU")
        html:'<div class="toolbar_hdg">'+_("负载最高服务器")+'</div>'
    });

    var period_combo=getPeriodCombo();
    var fdate="",tdate="",selperiod=stackone.constants.HRS12;
    period_combo.on('select',function(field,rec,index){
        if(field.getValue() ==stackone.constants.CUSTOM){
            var cust=new CustomPeriodUI(_("Select Period for Metric Utilization"),fdate,tdate,selperiod);
            var cust_window = cust.getWindow();
            var custom_btn= new Ext.Button({
                text: _('确定'),
                listeners: {
                    click: function(btn) {
                        if(cust.validate()){
                            cust_window.hide();
                            fdate=cust.fromTime();
                            tdate=cust.toTime();
                            redrawChart(stackone.constants.SERVER_POOL,type_combo.getValue(),node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'sp_chart'+node_id,true,panel1_1,stackone.constants.TOP5SERVERS);

                            //label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
                        }
                    }
                }
            });
            cust_window.addButton(custom_btn);
            cust_window.show();
        }else{
            selperiod=period_combo.getValue();
            fdate="",tdate="";
            redrawChart(stackone.constants.SERVER_POOL,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'sp_chart'+node_id,true,panel1_1,stackone.constants.TOP5SERVERS);
            //label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
        }
    });

    var type_combo=getMetricCombo();
    type_combo.on('select',function(field,rec,index){
        redrawChart(stackone.constants.SERVER_POOL,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'sp_chart'+node_id,true,panel1_1,stackone.constants.TOP5SERVERS);
        //label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
    });

//    var srvr_pool_info_grid=server_pool_info_grid(node_id);
//    var srvr_pool_sec_info_grid=server_pool_sec_info_grid(node_id);
    var srvr_pool_vm_grid=server_pool_vm_grid(node_id);
//    var srvr_pool_storage_grid=server_pool_storage_grid(node_id,node);
//    var srvr_pool_nw_grid=server_pool_nw_grid(node_id,node);

    //var sp_provisionsetg_grid=serverpool_provisionsetg_grid(node_id,node);

    var panel1 = new Ext.Panel({
        height:260,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column',
        bodyStyle:'padding-top:10px;padding-right:5px;'
    });
    var panel1_0 = new Ext.Panel({
        height:255,
        width:'30%',
        border:false,
        bodyBorder:false
        ,layout:'fit'
    });
    var panel1_1 = new Ext.Panel({
        height:255,
        width:'69%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false        
        //,bodyStyle:'padding-left:15px;'
        ,tbar:[getTop5Info(),label1_1,{xtype:'tbfill'},period_combo,'-',type_combo]
    });  
//    var panel2 = new Ext.Panel({
//        height:250,
//        width:'100%',
//        layout: 'fit',
//        bodyStyle:'padding-left:15px;padding-right:30px;padding-bottom:12px;padding-top:10px;',
//        border:false,
//        bodyBorder:false
//    });
//    var summary_grid=drawsummaryGrid(rows,node.attributes.nodetype,node.attributes.id,true,panel2);
   var panel3 = new Ext.Panel({
        width:'100%',
        height:185,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });

    var panel4 = new Ext.Panel({
        width:'100%',
        height: 185,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });

    var dummy_panel1 = new Ext.Panel({
        width:'1%',
        border:true,
        html:'&nbsp;&nbsp;',
        bodyBorder:false
    });
    var dummy_panel2 = new Ext.Panel({
        width:20,
        border:false,
        bodyBorder:false
    });
    var dummy_panel3 = new Ext.Panel({
        width:'1%',
        border:false,
        html:'&nbsp;',
        bodyBorder:false
    });
    var dummy_panel4 = new Ext.Panel({
        width:'1%',
        border:false,
        html:'&nbsp;',
        bodyBorder:false
    });
//    var dummy_panel5 = new Ext.Panel({
//        width:10,
//        border:false,
//        bodyBorder:false
//    });
    var top_cpu_grid=topN_spvms(node_id, node, "CPU");
    var top_mem_grid=topN_spvms(node_id, node, "Memory");


     var cpu_panel=new Ext.Panel({
        width:'49.5%',
        height: 180,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var mem_panel=new Ext.Panel({
        width:'49.5%',
        height: 180,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:5px;padding-right:3px;padding-top:5px;',
        layout:'fit'
    });

    
    
//    var storage_panel=new Ext.Panel({
//        width:'48%',
//        height: 220,
//        border:false,
//        bodyBorder:false,
//        bodyStyle:'padding-left:15px;padding-right:3px;padding-top:10px;',
//        layout:'fit'
//    });
//    var nw_panel=new Ext.Panel({
//        width:'48%',
//        height: 220,
//        border:false,
//        bodyBorder:false,
//        bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
//        layout:'fit'
//    });

    //panel1_1.add(get_sp_cpu_chart());
    redrawChart(stackone.constants.SERVER_POOL,stackone.constants.CPU,node_id,node.text,
                    stackone.constants.HRS12,fdate,tdate,'sp_chart'+node_id,true,panel1_1,stackone.constants.TOP5SERVERS);

    panel1_0.add(srvr_pool_vm_grid);
    panel1.add(panel1_0);
    panel1.add(dummy_panel1);
    panel1.add(panel1_1);
    //panel1_1.add(label1_1);

//    panel1.add(dummy_panel2);
//    panel1.add(chpanel2);

//    panel2.add(summary_grid);

//    panel3.add(srvr_pool_info_grid);
//    panel3.add(dummy_panel3);
//    panel3.add(srvr_pool_sec_info_grid);

    //storage_panel.add(label3);
   var server_cpu_panel=new Ext.Panel({
        width:'49.5%',
        height: 180,
        border:false,
        bodyBorder:false,
        layout:'fit'
//        bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;'
    });
    var server_mem_panel=new Ext.Panel({
        width:'49.5%',
        height: 180,
        border:false,
        bodyBorder:false,
        layout:'fit'
//        bodyStyle:'padding-left:5px;padding-right:3px;padding-top:5px;'
    });

    var top_servercpu_grid=topN_spservers(node_id, node, "CPU");
    var top_servermem_grid=topN_spservers(node_id, node, "Memory");
    server_cpu_panel.add(top_servercpu_grid);
    //nw_panel.add(label4);
    server_mem_panel.add(top_servermem_grid);

    cpu_panel.add(top_cpu_grid);
    //nw_panel.add(label4);
    mem_panel.add(top_mem_grid);

    panel3.add(server_cpu_panel);
    panel3.add(dummy_panel3);
    panel3.add(cpu_panel);

    panel4.add(server_mem_panel);
    panel4.add(dummy_panel4);
    panel4.add(mem_panel);

//    storage_panel.add(srvr_pool_storage_grid);
//    //nw_panel.add(label4);
//    nw_panel.add(srvr_pool_nw_grid);
//
//    panel5.add(storage_panel);
//    panel5.add(dummy_panel5);
//    panel5.add(nw_panel);
    //panel4.add(label2);



    var topPanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Server Pool Information for {0}"),node.text),
        height:'50%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false,
        items:[panel1,panel3,panel4]
    });

    var label_provstg=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("部署设置")+'</div>',
        id:'Provision_Settings'
    });
    var provision_setting_panel = new Ext.Panel({
        width:'50%',
        autoHeight: true,
        bodyBorder:false,
        layout:'column'
//        ,items:[label_provstg,sp_provisionsetg_grid]
    });

//    var bottomPanel = new Ext.Panel({
//        //layout  : 'fit',
//        collapsible:true,
//        title:"Shared Information",
//        height:'50%',
//        width:'100%',
//        border:false,
//        cls:'headercolor',
//        bodyBorder:false,
//        items:[panel5]
//    });

    var server_pool_homepanel=new Ext.Panel({
        width:"100%",
        height:"100%"
        ,items:[topPanel]
        ,bodyStyle:'padding-left:10px;padding-right:5px;'
    });
    //server_pool_homepanel.add(topPanel);
    //server_pool_homepanel.add(bottomPanel);
    mainpanel.add(server_pool_homepanel);
    server_pool_homepanel.doLayout();
    mainpanel.doLayout();
	centerPanel.setActiveTab(mainpanel);
}
function server_pool_task_details_page(mainpanel,node_id,node){
     if(mainpanel.items)
        mainpanel.removeAll(true);
     var task_grid=draw_grid(node_id,node,"服务器池任务",500);
     var taskformpanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Server Pool Information for {0}"),node.text),
        height:'80%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false,
        bodyStyle:'padding-left:15px;padding-right:5px;padding-top:10px;',
        resizable:true,
        items:[task_grid]
    });

    mainpanel.add(taskformpanel);
    taskformpanel.doLayout();
    mainpanel.doLayout();
}

/**
 * 服务器池-入门面板
 * 
 * @param {}
 *            mainpanel
 * @param {}
 *            node_id
 * @param {}
 *            node
 */
function server_pool_serverpoolStarter_page(mainpanel, node_id, node) {
	if (mainpanel.items)
		mainpanel.removeAll(true);
	var url = "/dashboard/server_pool_info?type=SERVER_POOL_VM_INFO&node_id="
			+ node_id;
	var ajaxReq = ajaxRequest(url, 0, "GET", true);
	ajaxReq.request({
		success : function(xhr) {
			var response = Ext.util.JSON.decode(xhr.responseText);
			if (response.success) {
				serverpool_list = response.info[4].list;
			}
		},
		failure : function(xhr) {
		}
	});
	/*var topHtml = '';
	topHtml += '<div class="toolbar_hdg" >';
	topHtml += '</div>';*/
	var topHtml = '';
	topHtml += '<div class="server-pool-starter-top">';
	topHtml += '	<div class="server-pool-starter-top-text">';
	topHtml += _("什么是服务器池？");
	topHtml += '<br/>';
	topHtml += '<br/>';
	topHtml += _("服务器池是主机和虚拟机的主要容器，通常要把主机（即物理服务器）添加到服务器池。");
	topHtml += '<br/>';
	topHtml += '<br/>';
	topHtml += _("SmartDataCenter可包含多个服务器池，一般全国性的集团公司或跨国公司会使用多个服务器池来表示企业内的组织结构。");
	topHtml += '<br/>';
	topHtml += _("服务器池的对象可以交互，但不同服务器池的交互则会受到限制。例如：您可以使用StackoneHA技术在一个服务器池内的主机之间迁移虚拟机，但不可以将虚拟机迁移到另一个服务器池的主机上。");
	topHtml += '	</div>';
	topHtml += '	<div class="server-pool-starter-top-img">';
	topHtml += '	</div>';
	topHtml += '</div>';
	
	var leftHtml = '';
	leftHtml += '<div class="server-pool-starter-left-text">';
	leftHtml += '<div>基本任务</div>';
	leftHtml += '<a href="#" onclick=javascript:server_pool_serverpoolStarter_page_insertServer();>';
	leftHtml += '添加服务器';
	leftHtml += '</a>';
	leftHtml += '<br/>';
	leftHtml += '</div>';
	var rightHtml = '';
	rightHtml += '<div class="server-pool-starter-right-text" >';
	rightHtml += _("了解主机");
	rightHtml += '<br/><br/>';
	rightHtml += _("主机是使用虚拟化管理软件运行不同虚拟机的服务器。一般，主机是运行SmartServer的计算节点。");
	rightHtml += '<br/>';
	rightHtml += '<br/>';
	rightHtml += _("主机为虚拟机提供存储和网络，并使虚拟机有访问的权限。同一台主机上可以运行多台不同的虚拟机。");
	rightHtml += '<br/>';
	rightHtml += '<br/>';
	rightHtml += _("将主机添加到SmartDataCenter后，您便能轻松的管理主机，以及运行在主机上面的虚拟机。");
	rightHtml += '</div>'
	var topPanel = new Ext.Panel({
		height : 300,
		width : '100%',
		region : 'north',
		border: false,
		frame: true,
		//bodyStyle : 'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
		html : topHtml
	});
	var leftPanel = new Ext.Panel({
		height : '60%',
		width : '40%',
		region : 'west',
		border: false,
		frame: true,
		bodyStyle : 'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
		html : leftHtml
	});
	var rightPanel = new Ext.Panel({
		height : '60%',
		width : '60%',
		region : 'center',
		border: false,
		frame: true,
		bodyStyle : 'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
		html : rightHtml
	});

	var serverpoolStarterPanel = new Ext.Panel({
		width : "100%",
		height : "100%",
		layout : 'border',
		border: false,
		items : [topPanel, leftPanel, rightPanel]
	});
	mainpanel.add(serverpoolStarterPanel);
	serverpoolStarterPanel.doLayout();
	mainpanel.doLayout();
}

function server_pool_serverpoolStarter_page_insertServer() {
	showWindow(_("选择平台"), 315, 120, select_platform(leftnav_treePanel.getSelectionModel().getSelectedNode()));
}


function server_pool_info_grid(node_id){
    var server_pool_info_store =new Ext.data.JsonStore({
        url: "/dashboard/server_pool_info?type=SERVER_POOL_INFO",
        root: 'info',
        fields: ['name','value','type','action','chart_type'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_pool_info_store.load({
        params:{
            node_id:node_id
        }
    });

    var server_pool_info_grid = new Ext.grid.GridPanel({
        //title:'Physical Resources',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        cls:'hideheader padded',
        width: 450,
        //height: 200,
        enableHdMenu:false,
        enableColumnMove:false,
        //plugins:[action],
        autoScroll:true,
         autoExpandColumn:1,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 100, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 300, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:server_pool_info_store
    });

    return server_pool_info_grid
}

function server_pool_sec_info_grid(node_id){
    var server_pool_sec_info_store =new Ext.data.JsonStore({
        url: "/dashboard/server_pool_info?type=SERVER_POOL_SEC_INFO",
        root: 'info',
        fields: ['name','value','type','action','chart_type'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_pool_sec_info_store.load({
        params:{
            node_id:node_id
        }
    });

    var server_pool_sec_info_grid = new Ext.grid.GridPanel({
        //title:'Physical Resources',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        cls:'hideheader padded',
        width: 450,
        //height: 200,
        enableHdMenu:false,
        enableColumnMove:false,
        //plugins:[action],
        autoScroll:true,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 100, sortable: false, css:'font-weight:bold;',dataIndex: 'name'},
            {header: "", width: 300, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:server_pool_sec_info_store
    });

    return server_pool_sec_info_grid
}

function server_pool_vm_grid(node_id){
    var vm_info_store =new Ext.data.JsonStore({
        url: "/dashboard/server_pool_info?type=SERVER_POOL_VM_INFO",
        root: 'info',
        fields: ['name','value','type','action','chart_type','list'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    vm_info_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_task'
    });

    var server_pool_vm_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 210,
        enableHdMenu:false,
         autoExpandColumn:1,
        enableColumnMove:false,
        //plugins:[action],
        autoScroll:true,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 135, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:NewUIMakeUP},
            {header: "", width: 120, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_info_store
        ,tbar:[label_strge]
    });

    return server_pool_vm_grid
}

function server_pool_storage_grid(node_id,node){

    var server_pool_storage_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width: 90,
        dataIndex: 'name',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("类型"),
        width: 60,
        sortable:true,
        dataIndex: 'type'
    },
    {
        header: _("大小(GB)"),
        width: 80,
        dataIndex: 'size',
        sortable:true,
        align: 'right'
    },
    {
        header: _("使用率(%)"),
        width: 120,
        dataIndex: 'usage',
        sortable:true,
        renderer:showBar
    },
    {
        header: _("状态"),
        width: 100,
        dataIndex: 'status',
        sortable:true,
        renderer: showSyncStatus
    },
    {
        header: _("说明"),
        width: 150,
        dataIndex: 'description',
        sortable:true
    }]);

    var server_pool_storage_store = new Ext.data.JsonStore({
        url: "/dashboard/server_pool_info?type=STORAGE_INFO&op=SP",
        root: 'info',
        fields: ['name','type','size','description','usage','status'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_pool_storage_store.load({
        params:{
            node_id:node_id
        }
    });

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("存储资源")+'</div>',
        id:'label_strge'
    });
    var settings_btn=new Ext.Button({
        tooltip:'管理存储池',
        tooltipType : "title",
        icon:'icons/settings.png',
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                showWindow(_("存储池")+":- "+node.text,444,495,StorageDefList(node));

            }
        }
    });
	var server_pool_storage_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: server_pool_storage_store,
        colModel:server_pool_storage_columnModel,
        stripeRows: true,
        frame:false,
        //autoExpandColumn:3,
        //autoExpandMax:300,
        border:true,
        enableHdMenu:true,
        autoScroll:true,
        id:'server_pool_storage_summary_grid',
        //cls:'padded',
//        viewConfig: {
//            getRowClass: function(record, index) {
//                return 'row-border';
//            }
//        },
        width:'100%',
        //autoExpandColumn:1,
        height:220
        ,tbar:[label_strge]
    });

	return server_pool_storage_grid;

}

function server_pool_nw_grid(node_id,node){

    var server_pool_nw_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width: 90,
        dataIndex: 'name',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("类型"),
        width: 80,
        sortable:true,
        dataIndex: 'type'
    },
    {
        header: _("服务器"),
        width: 100,
        sortable:true,
        dataIndex: 'server'
    },
    {
        header: _("详情"),
        width: 80,
        sortable:true,
        dataIndex: 'definition'
    },
    {
        header: _("说明"),
        width: 150,
        sortable:true,
        dataIndex: 'description'
    }]);

    var server_pool_nw_store = new Ext.data.JsonStore({
        url: "/dashboard/server_pool_info?type=VIRT_NW_INFO",
        root: 'info',
        fields: ['name','definition','type','description','server'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_pool_nw_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_nw=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("虚拟网络")+'</div>',
        id:'label_nw'
    });
    var settings_btn=new Ext.Button({
        tooltip:'管理虚拟网络',
        tooltipType : "title",
        icon:'icons/settings.png',
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
           showWindow(_("管理虚拟网络")+":- "+node.text,466,450,VirtualNetwork(node));
            }
        }
    });
	var server_pool_nw_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: server_pool_nw_store,
        colModel:server_pool_nw_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:4,
        autoExpandMax:300,
        autoExpandMin:150,
        border:true,
        enableHdMenu:true,
        autoScroll:true,
        id:'server_pool_nw_summary_grid',
        //cls:'padded',
//        viewConfig: {
//            getRowClass: function(record, index) {
//                return 'row-border';
//            }
//        },
        width:'100%',
        //autoExpandColumn:1,
        height:220
        ,tbar:[label_nw]
    });

	return server_pool_nw_grid;

}
function serverpool_provisionsetg_grid(node_id,node){
    var serverpool_provisionsetg_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Id"),
        width: 50,
        hidden: true,
        dataIndex: 'id'
    },
    {
        header: _("变量"),
        width: 150,
        dataIndex: 'variable'
    },
    {
        header: _("值"),
        width: 100,
        dataIndex: 'value'
    }]);

    var provisionsetg_store = new Ext.data.JsonStore({
        url: '/node/get_group_vars?group_id='+node_id,
        root: 'rows',
        fields: ['id', 'variable', 'value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert("Error",store_response.msg);
            }
        }
    });
   provisionsetg_store.load();
   var serverpool_provisionsetg_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: provisionsetg_store,
        colModel: serverpool_provisionsetg_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
        autoExpandMax:300,
        enableHdMenu:false,
        autoScroll:true,
        id:'serverpool_provisionsetg_grid',
        width:'100%',
        height:220
     });

	return serverpool_provisionsetg_grid;
  

}
function topN_spvms(node_id,node,metric){
    var top_cm = new Ext.grid.ColumnModel([
        {
            header: _("VMid"),
            width: 110,
            dataIndex: 'vmid',
            hidden:true,
            sortable:true
        },
        {
            header: _("名称"),
            width: 150,
            dataIndex: 'vm',
            //css:'font-weight:bold;',
            sortable:true
        },
        {
            header: format(_("主机{0}(%)"),metric),
            width: 180,
            sortable:true,
            dataIndex: 'usage',
            renderer:showBar
        }
    ]);

    var top_store = new Ext.data.JsonStore({
        url: "/dashboard/topNvms?node_id="+node_id+"&metric="+metric+"&node_type="+node.attributes.nodetype,
        root: 'info',
        fields: ['vmid','vm','usage','node_id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    top_store.load();

    var label=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+format(_("负载最高虚拟机{0}利用率"),metric)+'</div>',
        id:'label_task'
    });

	var top_grid = new Ext.grid.GridPanel({
//        disableSelection:true,
        store: top_store,
        colModel:top_cm,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
        autoExpandMax:300,
        autoExpandMin:80,
//        border:true,
        enableHdMenu:false,
        autoScroll:true,
        width:'100%',
        //autoExpandColumn:1,
        height:170
        ,tbar:[label]
        ,listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            rowdblclick:function(grid,rowIndex,e){
                handle_rowclick(grid,rowIndex,"click",e);
            }
        }
    });

	return top_grid;
}
function topN_spservers(node_id,node,metric){
    var top_cm = new Ext.grid.ColumnModel([
        {
            header: _("Serverid"),
            width: 110,
            dataIndex: 'serverid',
            hidden:true,
            sortable:true
        },
        {
            header: _("名称"),
            width: 150,
            dataIndex: 'server',
            //css:'font-weight:bold;',
            sortable:true
        },
        {
            header: format(_("{0}利用率(%)"),metric),
            width: 180,
            sortable:true,
            dataIndex: 'usage',
            renderer:showBar
        }
    ]);

    var top_store = new Ext.data.JsonStore({
        url: "/dashboard/topNservers?node_id="+node_id+"&metric="+metric+"&node_type="+node.attributes.nodetype,
        root: 'info',
        fields: ['serverid','server','usage','node_id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    top_store.load();

    var label=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+format(_("负载最高服务器{0}利用率"),metric)+'</div>',
        id:'label_task'
    });

	var top_grid = new Ext.grid.GridPanel({
//        disableSelection:true,
        store: top_store,
        colModel:top_cm,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
        autoExpandMax:300,
        autoExpandMin:80,
//        border:true,
        enableHdMenu:false,
        autoScroll:true,
        width:'100%',
        //autoExpandColumn:1,
        height:170
        ,tbar:[label]
        ,listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            rowdblclick:function(grid,rowIndex,e){
                handle_rowclick(grid,rowIndex,"click",e);
            }
        }
    });

	return top_grid;
}
function server_pool_config_page(configPanel,node_id,node){
   if(configPanel.items)
        configPanel.removeAll(true);
   var panel1 = new Ext.Panel({
        width:'100%',
        height:250,
        border:false,
        bodyBorder:false,
        layout:'column',
        bodyStyle:'padding-top:5px;padding-right:5px;'
    });
    var panel5 = new Ext.Panel({
        width:'100%',
        height: 300,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });
     var dummy_panel1 = new Ext.Panel({
        width:'1%',
        html:'&nbsp;',
        border:false,
        bodyBorder:false
    });
    var dummy_panel3 = new Ext.Panel({
        width:'0.5%',
        border:false,
        html:'&nbsp;&nbsp;',
        bodyBorder:false
    });
    var dummy_panel2 = new Ext.Panel({
        width:'0.5%',
        border:false,
        html:'&nbsp;&nbsp;',
        bodyBorder:false
    });
    var storage_panel=new Ext.Panel({
        width:'49.5%',
        height: 220,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var nw_panel=new Ext.Panel({
        width:'49.5%',
        height: 220,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var label1_1=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("主机操作系统")+'<br/></div>'
    });
    var label1_2=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("客户机操作系统")+'<br/></div>'
    });
    var panel1_1 = new Ext.Panel({
        height:245,
        width:'29%',
        border:false,
        bodyBorder:false
        ,layout:'fit'
    });
    var panel1_2 = new Ext.Panel({
        height:245,
        width:'35%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        ,tbar:[label1_1]
        ,layout:'fit'
    });

    var panel1_3 = new Ext.Panel({
        height:245,
        width:'35%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        ,tbar:[label1_2]
        ,layout:'fit'
    });

    
    panel1_2.add(os_dist_chart(node_id, node, stackone.constants.MANAGED_NODE));
    panel1_3.add(os_dist_chart(node_id, node, stackone.constants.DOMAIN));
    var srvr_pool_summarygrid=srvr_pool_summary_grid(node_id,node);
    panel1_1.add(srvr_pool_summarygrid);
    panel1.add(panel1_1);
    panel1.add(dummy_panel2);
    panel1.add(panel1_2);
    panel1.add(dummy_panel3);
    panel1.add(panel1_3);

    var srvr_pool_storage_grid=server_pool_storage_grid(node_id,node);
    var srvr_pool_nw_grid=server_pool_nw_grid(node_id,node);
    
    storage_panel.add(srvr_pool_storage_grid);
    //nw_panel.add(label4);
    nw_panel.add(srvr_pool_nw_grid);

    panel5.add(storage_panel);
    panel5.add(dummy_panel1);
    panel5.add(nw_panel);


//     var panel6 = new Ext.Panel({
//         width:'100%',
//         height: 300,
//         border:false,
//         bodyBorder:false,
//         bodyStyle:'padding-top:0px;padding-right:5px;',
//         layout:'column'
//     });
//    
//   panel6.add(SPBackupTaskGrid(node));

//     var panel7 = new Ext.Panel({
//         width:'100%',
//         height: 300,
//         border:false,
//         bodyBorder:false,
//         bodyStyle:'padding-top:00px;padding-right:5px;',
//         layout:'column'
//     });
//     //panel7.add(dummy_panel4);  
//     panel7.add(SPBackupResultGrid(node_id));


    var bottomPanel = new Ext.Panel({
      //layout  : 'fit',
//        collapsible:true,
        height:'50%',
        width:'100%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-left:10px;padding-right:5px;padding-top:5px;',
        items:[panel1,panel5]
    });
    configPanel.add(bottomPanel);
	bottomPanel.doLayout();
    configPanel.doLayout();
}

function search_backup(node_id, node, search_text) {
    //alert("searching backup...." + search_text);
    url_text="";
    //if(isNaN(search_text) == false) {
        //alert("It is number.")
        url_text = 'backup/get_sp_vm_backup_history?node_id='+node_id+ '&node_type='+ node_type+ '&search_text='+ search_text;
        //alert("url is " + url_text)

        var s = new Ext.data.JsonStore({
            url: url_text,
            root: 'rows',
            sortInfo: {
                field: 'starttime',
                direction: 'DESC' 
            },
            fields: ['taskid','vm_id','name','vm', 'server','location', 'backup_size','starttime', 'endtime','status', 'restore', 'errmsg', 'backup_type', 'backup_content', 'selective_content', 'lvm_present', 'vm_exists', 'result_id'],
            successProperty:'success',
            listeners:{
                loadexception:function(obj,opts,res,e){
                    var store_response=Ext.util.JSON.decode(res.responseText);
                    Ext.MessageBox.alert(_("Error"),store_response.msg);
                },
                load:function(my_store, records, options){
                    //alert("Loading data...");
                    //alert(my_store.getCount());
                    
                    backuptask_info_grid_b.store = my_store;
                    backuptask_info_grid_b.getView().refresh();
                }
            }
        });
        s.reload();
    /*
    } else {
        //alert("It is not a number.");
        //alert("search_text is " + search_text);
        my_store = backuptask_info_grid_b.getStore();
        //alert(my_store.getCount());
        my_store.filter('vm', search_text, false, false);
        //alert(my_store.getCount());
        backuptask_info_grid_b.store = my_store;
        backuptask_info_grid_b.getView().refresh();
    }
    */
}

function Sp_vm_backup_historyGrid(node_id,node){
    var label_task=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("备份")+'</div>',
        id:'label_task1'
    });
    var task_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("任务编号"),
        width: 50,
        dataIndex: 'taskid',
        hidden:true        
    },
    {
        header: _("虚拟机编号"),
        width: 50,
        dataIndex: 'vm_id',
        hidden:true        
    },    
    {
        header: _("虚拟机"),
        width: 100,
        dataIndex: 'vm',
        sortable:true        
    },  
    {
        header: _("服务器"),
        width: 100,
        dataIndex: 'server',
        sortable:true        
    },    
    {
        header: _("策略"),
        width: 100,
        dataIndex: 'name',
        sortable:true        
    },   

    {
        header: _("开始时间"),
        width: 140,
        dataIndex: 'starttime',
        sortable:true,
        renderer:function(value,params,record,row){
            value = format_date(value,params,record);
            return value;
        }
    },
    {
        header: _("结束时间"),
        width: 140,
        dataIndex: 'endtime',
        sortable:true,
        renderer:function(value,params,record,row){
            value = format_date(value,params,record);
            return value;
        }
    },
    {
        header: _("大小(GB)"),
        width: 70,
        dataIndex: 'backup_size',
        sortable:true,
        align: 'right'
    },
    {
        header: _("状态"),
        width: 100,
        dataIndex: 'status',        
        renderer:function(value,params,record,row){            
              if(value =='Failed' || value =='Success'){
                params.attr='ext:qtip="Show Message"' +
                    'style="background-image:url(icons/information.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            }
            return value;
        }
   },
    {
        header: _("还原"),
        width: 50,
        dataIndex: 'restore',
        align: 'center',
        renderer: showBackupResultDetailLink_pool
//          renderer:function(value,params,record,row){            
//                if( value =='Success'){
//                 params.attr='ext:qtip="Show Message"' +
//                     'style="background-image:url(icons/file_edit.png) '+
//                     '!important; background-position: right;'+
//                     'background-repeat: no-repeat;cursor: pointer;"';
//             }
//              return value;
//          }
    },
    {
        header: _("备份位置"),
        width: 200,
        dataIndex: 'location',
        sortable:true
    },
    {
        header: _("备份类型"),
        width: 250,
        dataIndex: 'backup_type',
        sortable:true,
        hidden: true   //hide this later
    },
    {
        header: _("备份内容"),
        width: 250,
        dataIndex: 'backup_content',
        sortable:true,
        hidden: true   //hide this later
    },
    {
        header: _("选择内容"),
        width: 250,
        dataIndex: 'selective_content',
        sortable:true,
        hidden: true   //hide this later
    },
    {
        header: _("LVM Present"),
        width: 250,
        dataIndex: 'lvm_present',
        sortable:true,
        hidden: true   //hide this later
    },
    {
        header: _("VM Exists"),
        width: 250,
        dataIndex: 'vm_exists',
        sortable:true,
        hidden: true   //hide this later
    },
    {
        header: _("Result Id"),
        width: 250,
        dataIndex: 'result_id',
        sortable:true,
        hidden: true   //hide this later
    }
   ]);

    node_id = node.attributes.id;
    node_type = node.attributes.nodetype;

    var task_store = new Ext.data.JsonStore({
        url: 'backup/get_sp_vm_backup_history?node_id='+node_id+ '&node_type='+ node_type,
        root: 'rows',
        sortInfo: {
            field: 'starttime',
            direction: 'DESC' 
        },
        fields: ['taskid','vm_id','name','vm', 'server','location', 'backup_size','starttime', 'endtime','status', 'restore', 'errmsg', 'backup_type', 'backup_content', 'selective_content', 'lvm_present', 'vm_exists', 'result_id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    task_store.load();
    task_store_b=task_store;

    //Do not use this function here. It gives problem to Restore table on dashboard UI.
    //search_backup(node_id, node, search_text);

    var backup_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:false
    });
    
    var search_bkp_textbox = new Ext.form.TextField({
        fieldLabel: '搜索',
        name: 'search_bkp_textbox',
        id: 'search_bkp_textbox',
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {
                //backuptask_info_grid.getStore().filter('vm', field.getValue(), false, false);
            }
        }
    });

    var search_bkp_button = new Ext.Button({
        tooltip:'搜索',
        tooltipType : "title",
        icon:'icons/search.png',
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                //alert(search_bkp_textbox.getValue());
                var search_text = search_bkp_textbox.getValue();
                search_backup(node_id, node, search_text);
            }
        }
    });

     //Seearch for Data Center, Serverpool-Backup tab- Backup table
     backuptask_info_grid_b = new Ext.grid.GridPanel({
        //disableSelection:true,
        store: task_store_b,
        colModel:task_columnModel,
        stripeRows: true,
        frame:false,
        //autoExpandColumn:3,
        //autoExpandMax:300,
        border:true,
        enableHdMenu:true,
        autoScroll:true,
        selModel:backup_selmodel,
        id:'backuptask_info_grid_b',
        
        width:'100%',
        //autoExpandColumn:1,
        height:220,        
        tbar:[label_task, { xtype: 'tbfill'},
        'Search: ',search_bkp_textbox,
        search_bkp_button],
        listeners: {
            rowcontextmenu :function(grid,rowIndex,e) {
                var record = grid.getStore().getAt(rowIndex);
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            cellclick: function(grid ,rowIndex,columnIndex,e,b) {
                var record = grid.getStore().getAt(rowIndex);
                if (columnIndex == 8)
                {
                    if(record.get('status') =='Failed'||record.get('status') =='Success'){
                        var err=record.get('errmsg');
                        showTaskMessage('Message',err);
                    }
                }
               
                if (columnIndex == 9) {
                    if(record.get('status') =='Success') {
                        Ext.MessageBox.confirm(_("确认"),"确定要还原备份吗?",function(id){
                            if(id=='yes'){
                                if(record.get('vm_exists')==false) {
//                                     alert("vm does not exist");

                                    var objData = new Object();
                                    objData.backup_type = record.get('backup_type')
                                    objData.lvm_present = record.get('lvm_present')
                                    objData.backup_content = record.get('backup_content')
                                    objData.selective_content = record.get('selective_content')
                                    objData.vm_id = record.get('vm_id')
                                    objData.result_id = record.get('result_id')
                                    handleEvents(node,'restore_from_backup',null,objData);   //node/action.js
                                } else {
//                                     alert("vm exists");
                                    //from node/RestoreBackup.js
                                    RestoreBackup("", record.get('vm_id'), "", record.get('result_id'), false); 
                                }
                            }
                        });
                    }
                }

//                 else
//                 {
//                     handle_rowclick(grid,rowIndex,"click",e);
//                     
//                 }
            }

// //             rowcontextmenu :function(grid,rowIndex,e) {
// //                 e.preventDefault();
// //                 handle_rowclick(grid,rowIndex,"contextmenu",e);
// //             },
//             rowdblclick:function(grid,rowIndex,e){
//                 handle_rowclick(grid,rowIndex,"click",e);
//             }
         }

    });
    
    return backuptask_info_grid_b; 
}

function search_restore(node_id, node, search_text) {
    //alert("searching restore...." + search_text);
    url_text="";
    //if(isNaN(search_text) == false) {
        //alert("It is number.")
        url_text = 'restore/get_sp_vm_restore_history?node_id='+node_id+ '&node_type='+ node_type+ '&search_text='+ search_text;
        //alert("url is " + url_text)

        var task_store = new Ext.data.JsonStore({
            url: 'restore/get_sp_vm_restore_history?node_id='+node_id+ '&node_type='+ node_type+ '&search_text='+ search_text,
            root: 'rows',
            sortInfo: {
                field: 'starttime',
                direction: 'DESC' 
            },
            fields: ['taskid','vm_id','name','vm', 'server','location', 'backup_size','starttime', 'endtime','status', 'restore', 'errmsg', 'backup_type', 'backup_content', 'selective_content', 'lvm_present', 'vm_exists', 'result_id'],
            successProperty:'success',
            listeners:{
                loadexception:function(obj,opts,res,e){
                    var store_response=Ext.util.JSON.decode(res.responseText);
                    Ext.MessageBox.alert(_("Error"),store_response.msg);
                },
                load:function(my_store, records, options){
                    //alert("Loading data...");
                    //alert(my_store.getCount());
                    
                    backuptask_info_grid_r.store = my_store;
                    backuptask_info_grid_r.getView().refresh();
                }
            }
        });
        task_store.reload();
    /*
    } else {
        //alert("It is not a number.");
        //alert("search_text is " + search_text);
        my_store = backuptask_info_grid_r.getStore();
        //alert(my_store.getCount());
        my_store.filter('vm', search_text, false, false);
        //alert(my_store.getCount());
        backuptask_info_grid_r.store = my_store;
        backuptask_info_grid_r.getView().refresh();
    }
    */
}

function sp_vm_restore_history_grid(node_id, node, search_text){
    var label_task=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("还原")+'</div>',
        id:'label_task1'
    });
    var task_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("任务编号"),
        width: 50,
        dataIndex: 'taskid',
        hidden:true        
    },
    {
        header: _("虚拟机编号"),
        width: 50,
        dataIndex: 'vm_id',
        hidden:true        
    },    
    {
        header: _("虚拟机"),
        width: 100,
        dataIndex: 'vm',
        sortable:true        
    },  
    {
        header: _("服务器"),
        width: 100,
        dataIndex: 'server',
        sortable:true        
    },    
    {
        header: _("策略"),
        width: 100,
        dataIndex: 'name',
        sortable:true        
    },   

    {
        header: _("开始时间"),
        width: 140,
        dataIndex: 'starttime',
        sortable:true,
        renderer:function(value,params,record,row){
            value = format_date(value,params,record);
            return value;
        }
    },
    {
        header: _("结束时间"),
        width: 140,
        dataIndex: 'endtime',
        sortable:true,
        renderer:function(value,params,record,row){
            value = format_date(value,params,record);
            return value;
        }
    },
    {
        header: _("大小(GB)"),
        width: 70,
        dataIndex: 'backup_size',
        sortable:true,
        align: 'right',
        hidden: true
    },
    {
        header: _("状态"),
        width: 100,
        dataIndex: 'status',        
        renderer:function(value,params,record,row){            
              if(value =='Failed' || value =='Success'){
                params.attr='ext:qtip="Show Message"' +
                    'style="background-image:url(icons/information.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            }
            return value;
        }
   },
    {
        header: _("还原"),
        width: 50,
        dataIndex: 'restore',
        align: 'center',
        renderer: showBackupResultDetailLink_pool,
        hidden:true
//          renderer:function(value,params,record,row){            
//                if( value =='Success'){
//                 params.attr='ext:qtip="Show Message"' +
//                     'style="background-image:url(icons/file_edit.png) '+
//                     '!important; background-position: right;'+
//                     'background-repeat: no-repeat;cursor: pointer;"';
//             }
//              return value;
//          }
    },
    {
        header: _("备份位置"),
        width: 200,
        dataIndex: 'location',
        sortable:true
    },
    {
        header: _("备份类型"),
        width: 250,
        dataIndex: 'backup_type',
        sortable:true,
        hidden: true   //hide this later
    },
    {
        header: _("备份内容"),
        width: 250,
        dataIndex: 'backup_content',
        sortable:true,
        hidden: true   //hide this later
    },
    {
        header: _("选择内容"),
        width: 250,
        dataIndex: 'selective_content',
        sortable:true,
        hidden: true   //hide this later
    },
    {
        header: _("LVM Present"),
        width: 250,
        dataIndex: 'lvm_present',
        sortable:true,
        hidden: true   //hide this later
    },
    {
        header: _("VM Exists"),
        width: 250,
        dataIndex: 'vm_exists',
        sortable:true,
        hidden: true   //hide this later
    },
    {
        header: _("Result Id"),
        width: 250,
        dataIndex: 'result_id',
        sortable:true,
        hidden: true   //hide this later
    }
   ]);

    node_id = node.attributes.id;
    node_type = node.attributes.nodetype;

    var task_store = new Ext.data.JsonStore({
        url: 'restore/get_sp_vm_restore_history?node_id='+node_id+ '&node_type='+ node_type,
        root: 'rows',
        sortInfo: {
            field: 'starttime',
            direction: 'DESC' 
        },
        fields: ['taskid','vm_id','name','vm', 'server','location', 'backup_size','starttime', 'endtime','status', 'restore', 'errmsg', 'backup_type', 'backup_content', 'selective_content', 'lvm_present', 'vm_exists', 'result_id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });  

    task_store.load();      
    task_store_r = task_store;

    var search_restore_textbox = new Ext.form.TextField({
        fieldLabel: '搜索',
        name: 'search_restore_textbox',
        id: 'search_restore_textbox',
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {
                //backuptask_info_grid.getStore().filter('vm', field.getValue(), false, false);
            }
        }

    });

    var search_restore_button = new Ext.Button({
        tooltip:'搜索',
        tooltipType : "title",
        icon:'icons/search.png',
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                //alert(search_restore_textbox.getValue());
                search_text = search_restore_textbox.getValue();
                search_restore(node_id, node, search_text);
            }
        }
    });

    var backup_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:false
    });
    
     //Search for Serverpool-Backup tab- Restore table
     backuptask_info_grid_r = new Ext.grid.GridPanel({
        //disableSelection:true,
        store: task_store_r,
        colModel:task_columnModel,
        stripeRows: true,
        frame:false,
        //autoExpandColumn:3,
        //autoExpandMax:300,
        border:true,
        enableHdMenu:true,
        autoScroll:true,
        selModel:backup_selmodel,
        id:'backuptask_info_grid_r',
        
        width:'100%',
        //autoExpandColumn:1,
        height:220,        
        tbar:[label_task, { xtype: 'tbfill'}, 
            'Search: ', search_restore_textbox, search_restore_button],
        listeners: {
            rowcontextmenu :function(grid,rowIndex,e) {
                var record = grid.getStore().getAt(rowIndex);
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            cellclick: function(grid ,rowIndex,columnIndex,e,b) {
                var record = grid.getStore().getAt(rowIndex);
                if (columnIndex == 8)
                {
                    if(record.get('status') =='Failed'||record.get('status') =='Success'){
                        var err=record.get('errmsg');
                        showTaskMessage('Message',err);
                    }
                }
               
                if (columnIndex == 9) {
                    if(record.get('status') =='Success') {
                        Ext.MessageBox.confirm(_("确认"),"确定要还原备份吗?",function(id){
                            if(id=='yes'){
                                if(record.get('vm_exists')==false) {
//                                     alert("vm does not exist");

                                    var objData = new Object();
                                    objData.backup_type = record.get('backup_type')
                                    objData.lvm_present = record.get('lvm_present')
                                    objData.backup_content = record.get('backup_content')
                                    objData.selective_content = record.get('selective_content')
                                    objData.vm_id = record.get('vm_id')
                                    objData.result_id = record.get('result_id')
                                    handleEvents(node,'restore_from_backup',null,objData);   //node/action.js
                                } else {
//                                     alert("vm exists");
                                    //from node/RestoreBackup.js
                                    RestoreBackup("", record.get('vm_id'), "", record.get('result_id'), false); 
                                }
                            }
                        });
                    }
                }

//                 else
//                 {
//                     handle_rowclick(grid,rowIndex,"click",e);
//                     
//                 }
            }

// //             rowcontextmenu :function(grid,rowIndex,e) {
// //                 e.preventDefault();
// //                 handle_rowclick(grid,rowIndex,"contextmenu",e);
// //             },
//             rowdblclick:function(grid,rowIndex,e){
//                 handle_rowclick(grid,rowIndex,"click",e);
//             }
         }

    });

    return backuptask_info_grid_r;
     
}

function showBackupResultDetailLink_pool(data,cellmd,record,row,col,store) {
        var returnVal;
        var status= record.get("status");
        if(status == 'Success')
        
        {
            
            returnVal = '<a href="#"><img title="Restore Virtual Machines" src="icons/small_snapshot.png "/></a>';
        }

        return returnVal;       
}

function SPBackupResultGrid(node_id){
    var label_task=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("历史备份")+'</div>',
        id:'label_task1'
    });
    var task_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("任务编号"),
        width: 80,
        dataIndex: 'taskid',
        hidden:true        
    },
    {
        header: _("虚拟机编号"),
        width: 80,
        dataIndex: 'node_id',
        hidden:true        
    },
    {
        header: _("策略"),
        width: 200,
        dataIndex: 'name',
        sortable:true        
    },       

    {
        header: _("开始时间"),
        width: 160,
        dataIndex: 'starttime',
        sortable:true,
        renderer:function(value,params,record,row){
            value = format_date(value,params,record);
            return value;
        }
    },
    {
        header: _("结束时间"),
        width: 160,
        dataIndex: 'endtime',
        sortable:true,
        renderer:function(value,params,record,row){
            value = format_date(value,params,record);
            return value;
        }
    },
    {
        header: _("大小"),
        width: 70,
        dataIndex: 'backup_size',
        sortable:true,
        align: 'right'
    },
    {
        header: _("状态"),
        width: 100,
        dataIndex: 'status',        
        renderer:function(value,params,record,row){            
              if(value =='Failed' || value =='Success'){
                params.attr='ext:qtip="Show Message"' +
                    'style="background-image:url(icons/information.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            }
            return value;
        }
   },
    {
        header: _("备份位置"),
        width: 250,
        dataIndex: 'location',
        sortable:true
    }
   ]);



    var task_store = new Ext.data.JsonStore({
        url: 'backup/get_sp_backup_task_result?node_id='+node_id,
        root: 'rows',
        fields: ['taskid','node_id','name','location', 'backup_size','starttime', 'endtime','status', 'errmsg'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });  

    task_store.load();      

    
    
     var backuptask_info_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: task_store,
        colModel:task_columnModel,
        stripeRows: true,
        frame:false,
        //autoExpandColumn:3,
        //autoExpandMax:300,
        border:true,
        enableHdMenu:true,
        autoScroll:true,
        id:'backuptask_info_grid',
        
        width:'100%',
        //autoExpandColumn:1,
        height:220,
        tbar:[label_task],
        listeners: {
            cellclick: function(grid ,rowIndex,columnIndex,e,b) {
                if (columnIndex == 6)
                {
                    var record = grid.getStore().getAt(rowIndex);
                    if(record.get('status') =='Failed'||record.get('status') =='Success'){
                        var err=record.get('errmsg');
                        showTaskMessage('Message',err);

                    }
                }
//                 else
//                 {
//                     handle_rowclick(grid,rowIndex,"click",e);
//                     
//                 }
            }

// //             rowcontextmenu :function(grid,rowIndex,e) {
// //                 e.preventDefault();
// //                 handle_rowclick(grid,rowIndex,"contextmenu",e);
// //             },
//             rowdblclick:function(grid,rowIndex,e){
//                 handle_rowclick(grid,rowIndex,"click",e);
//             }
         }

    });
    
    return backuptask_info_grid; 
}

function srvr_pool_summary_grid(node_id,node){
      var summary_store =new Ext.data.JsonStore({
        url: "/dashboard/server_pool_info?type=SUMMARY",
        root: 'info',
        fields: ['name','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    summary_store.load({
        params:{
            node_id:node_id
        }
    });
    

    var label_summary=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_task'
    });

    var sp_summary_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        //title:_("Summary"),
        cls:'hideheader',
        width: '100%',
        height: 250,
         autoExpandColumn:1,
        enableHdMenu:false,
        enableColumnMove:false,
        //plugins:[action],
        autoScroll:true,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 120, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:NewUIMakeUP},
            {header: "", width: 100, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:summary_store
        ,tbar:[label_summary]
    });

    return sp_summary_grid;
}

function server_pool_vminfo_page(mainpanel,node_id,node){

    if(mainpanel.items)
        mainpanel.removeAll(true);
    var p2_expand=1;
    var p3_expand=1;
    var panel2 = new Ext.Panel({
        height:250,
        width:'100%',
        layout: 'fit',
        bodyStyle:'padding-bottom:12px;padding-top:10px;',
        border:false,
        bodyBorder:false,
        title:_('服务器信息'),
        collapsible:true,
        //cls:'headercolor1',
        listeners:({
            collapse:function(p2){
                p2_expand=0;
                panel3.setHeight(520);
                p3_expand=1;
            },
            expand:function(p2){
               if (p3_expand==1){
                   p2.setHeight(250);
                   panel3.setHeight(250);
                   p2.doLayout();
                   panel3.doLayout();
               }
            }

        })
    });
     var panel3 = new Ext.Panel({
        height:250,
        width:'100%',
        title:_('虚拟机信息'),
        layout: 'fit',
        bodyStyle:'padding-bottom:12px;padding-top:10px;',
        border:false,
        bodyBorder:false,
        collapsible:true,
        //cls:'headercolor1',
        listeners:({
            collapse:function(p3){
                 p3_expand=0;
                 panel2.setHeight(520);
                 p2_expand=1;

            },
             expand:function(p3){
                 if (p2_expand==1){
                   p3.setHeight(250);
                   panel2.setHeight(250);
                   panel2.doLayout();
                   p3.doLayout();
               }
             }
        })
    });
    var summary_grid=showServerList(node_id,stackone.constants.SERVER_POOL,panel2);
    //drawsummaryGrid(rows,node.attributes.nodetype,node.attributes.id,true,panel2);

    panel2.add(summary_grid);

    var vm_grid=showVMList(node_id,stackone.constants.SERVER_POOL,panel3);
    panel3.add(vm_grid);
    var vminformpanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Server Pool Information for {0}"),node.text),
        height:'50%',
        width:'100%',
        border:false,
//        cls:'headercolor',
        bodyStyle:'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
        bodyBorder:false,
        resizable:true,
        items:[panel2,panel3]
    });

    mainpanel.add(vminformpanel);
    vminformpanel.doLayout();
    mainpanel.doLayout();
}

function server_pool_backup_history_page(backup_history_Panel,node_id,node){


    if(backup_history_Panel.items)
        backup_history_Panel.removeAll(true);

    node_id = node.attributes.id;
    node_type = node.attributes.nodetype;

    var panel1 = new Ext.Panel({
        width:'100%',
        height: 193, //200
        border:false,
        bodyBorder:false,
       // bodyStyle:'padding-top:0px;padding-right:5px;',
        layout:'column'
    });
   
    var panel2 = new Ext.Panel({
        width:'100%', //60
        height: 164, //200
        border:false,
        bodyBorder:false,
       // bodyStyle:'padding-top:0px;padding-right:5px;',
        layout:'column'
    });
    var panel1_1 = new Ext.Panel({
        height:180,
        width:'29%',
        border:false,
        bodyBorder:false
        ,layout:'fit'
    });
    var panel1_2 = new Ext.Panel({
        height:180,
        width:'70%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false,        
        //,tbar:[label1_1]
        layout:'fit'
    });
    var dummy_panel1 = new Ext.Panel({
        width:'1%',
        border:true,
        html:'&nbsp;&nbsp;',
        bodyBorder:false
    });

    panel1_1.add(SP_backup_summary_grid(node_id, node_type));
    panel1_2.add(SP_backup_failure_grid(node_id, node_type));
    panel1.add(panel1_1);
    panel1.add(dummy_panel1);
    panel1.add(panel1_2);
    panel2.add(SPBackupTaskGrid(node));



//     var panel6 = new Ext.Panel({
//         width:'100%',
//         height: 270,
//         border:false,
//         bodyBorder:false,
//        // bodyStyle:'padding-top:0px;padding-right:5px;',
//         layout:'column'
//     });
//    
//   panel6.add(SPBackupTaskGrid(node));

    var panel7 = new Ext.Panel({
        width:'100%',
        height: 235,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-top:00px;padding-right:5px;',
        layout:'column'
    });   
    var panel8 = new Ext.Panel({
        width:'100%',
        height: 300,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-top:00px;padding-right:5px;',
        layout:'column'
    });   
//     panel7.add(SPBackupResultGrid(node_id));
    panel7.add(Sp_vm_backup_historyGrid(node_id,node));
    panel8.add(sp_vm_restore_history_grid(node_id,node));
    
    var backupinformpanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Server Pool Information for {0}"),node.text),
        height:'50%',
        width:'100%',
        border:true,
//        cls:'headercolor',
        bodyStyle:'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
        bodyBorder:false,
        resizable:true,
        items:[panel1, panel2, panel7, panel8]
    });

    //backup_history_Panel.add(vminformpanel);
    var label_backup_task=new Ext.form.Label({
        //html:getChartHdrMsg(node.text,"Hourly","CPU")
        html:'<div class="toolbar_hdg">'+_("历史备份任务")+'</div>'
    });

    backup_history_Panel.add(backupinformpanel);

    backupinformpanel.doLayout();
    backup_history_Panel.doLayout();
}


function remove_backuppolicy(selected_grid,node,sp_id  ) {

    var edit_rec=selected_grid.getSelectionModel().getSelected();

    var backupsetup_id= edit_rec.get('backupsetup_id');
    var taskname=edit_rec.get('taskname');
    var url='backup/delete_backuprecord?backupsetup_id='+backupsetup_id;//alert(url);
    Ext.MessageBox.confirm("确认","确定要删除备份记录"+taskname+"吗?", function (id){
        if(id=='yes'){
            var ajaxReq=ajaxRequest(url,0,"POST",true);
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
                        backup_grid.getStore().load();
                    }else{
                        Ext.MessageBox.alert("Failure",response.msg);
                    }
                },
                failure: function(xhr){
                    Ext.MessageBox.alert( "Failure " , xhr.statusText);
                }
            });
        }
    });
 
}

function edit_backuppolicy(selected_grid,node,sp_id  ) {
   
    var sp_backup_grid= SP_Backup_Grid(node)
    var edit_rec=selected_grid.getSelectionModel().getSelected();
    var backupsetup_id=edit_rec.get('backupsetup_id');  
    
    var url="/backup/get_backupsetup_details?backupsetup_id="+backupsetup_id;
    var ajaxReq=ajaxRequest(url,0,"POST",true);

    
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);

            if(response.success){                            
                var backup_details = response.backupsetup_details[0];
                backupPanel = SPBackupConfigSettings(sp_backup_grid, node,sp_id, 'EDIT',backup_details)
                showWindow(_("Edit Backup Task "), 640, 506,backupPanel );

                var scheduleType_combo =backupPanel.findById('scheduleType_combo'); 
                
                var hourCombo =backupPanel.findById('hourCombo');
                var week_checkBoxgroup =backupPanel.findById('week_checkBoxgroup');                
                var month_checkBoxgroup =backupPanel.findById('month_checkBoxgroup'); 
                
                
                switch (scheduleType_combo.getValue()) {
                    case "Hourly":
                        hideField(hourCombo);
                        hideField(week_checkBoxgroup);
                        hideField(month_checkBoxgroup);
    
                        break;
                    case "Daily":
                        showField(hourCombo);
                        hideField(week_checkBoxgroup);
                        hideField(month_checkBoxgroup);
                        break;
                    case "Weekly":
                        showField(hourCombo);
                        showField(week_checkBoxgroup);
                        hideField(month_checkBoxgroup);
                        break;
                    case "Monthly":
                        showField(hourCombo);
                        hideField(week_checkBoxgroup);
                        showField(month_checkBoxgroup);
                        break;
                }

            

            }else{
                Ext.MessageBox.alert("Failure",response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( "Failure " , xhr.statusText);
        }
    });
    selected_grid.getStore().load();
}

function BackupMenuHandler(item, e) {
    var node = item.parentMenu.contextNode;
    var sp_id = item.parentMenu.sp_id;
    var selected_grid = item.parentMenu.selected_grid;
    if (item.getId() == "backup_edit")
    {
        
        edit_backuppolicy(selected_grid,node,sp_id );
    }
    
    if (item.getId() == "backup_remove")
    {
        remove_backuppolicy(selected_grid,node,sp_id  );
    }
    
    //alert(item.getItemId())
    //alert('Clicked on the menu item: ' + sp_id);
}


function Individual_SPBackup_HistoryGrid( backup_id){
    var label_task=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("历史备份")+'</div>',
        id:'label_task1'
    });
    var task_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("备份编号"),
        width: 80,
        dataIndex: 'backup_id',
        hidden:true        
    },
    {
        header: _("虚拟机编号"),
        width: 80,
        dataIndex: 'node_id',
        hidden:true        
    },
    {
        header: _("策略"),
        width: 100,
        dataIndex: 'name',
        sortable:true        
    },       

    {
        header: _("开始时间"),
        width: 130,
        dataIndex: 'starttime',
        sortable:true,
        renderer:function(value,params,record,row){
            value = format_date(value,params,record);
            return value;
        }
    },
    {
        header: _("结束时间"),
        width: 130,
        dataIndex: 'endtime',
        sortable:true,
        renderer:function(value,params,record,row){
            value = format_date(value,params,record);
            return value;
        }
    },
    {
        header: _("大小"),
        width: 70,
        dataIndex: 'backup_size',
        sortable:true,
        align: 'right'
    },
    {
        header: _("状态"),
        width: 80,
        dataIndex: 'status',        
        renderer:function(value,params,record,row){            
              if(value =='Failed' || value =='Success'){
                params.attr='ext:qtip="Show Message"' +
                    'style="background-image:url(icons/information.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            }
            return value;
        }
   },
    {
        header: _("备份位置"),
        width: 150,
        dataIndex: 'location',
        sortable:true
    }
   ]);



    var task_store = new Ext.data.JsonStore({
        url: 'backup/get_individual_sp_backup_task_history?backup_id='+backup_id,
        root: 'rows',
        fields: ['backup_id','node_id','name','location', 'backup_size','starttime', 'endtime','status', 'errmsg'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });  

    task_store.load();      

    
    
     var backuptask_info_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: task_store,
        colModel:task_columnModel,
        stripeRows: true,
        frame:false,
        //autoExpandColumn:3,
        //autoExpandMax:300,
        border:true,
        enableHdMenu:true,
        autoScroll:true,
        id:'backuptask_info_grid',
        
        width:'100%',
        //autoExpandColumn:1,
        height:220,
        //tbar:[label_task],
        listeners: {
            cellclick: function(grid ,rowIndex,columnIndex,e,b) {                
                if (columnIndex == 6)
                {
                    var record = grid.getStore().getAt(rowIndex);
                    if(record.get('status') =='Failed'||record.get('status') =='Success'){
                        var err=record.get('errmsg');
                        showTaskMessage('Message',err);
                    }
                }
//                 else
//                 {
//                     handle_rowclick(grid,rowIndex,"click",e);
//                     
//                 }
            }

// //             rowcontextmenu :function(grid,rowIndex,e) {
// //                 e.preventDefault();
// //                 handle_rowclick(grid,rowIndex,"contextmenu",e);
// //             },
//             rowdblclick:function(grid,rowIndex,e){
//                 handle_rowclick(grid,rowIndex,"click",e);
//             }
         }

    });
    
    return backuptask_info_grid; 
}

function SPBackupTask_History( backup_id){
    var history_panel = new Ext.Panel({
        width:'100%',
        height: 250,
        border:false,
        bodyBorder:false,
    // bodyStyle:'padding-top:0px;padding-right:5px;',
        layout:'column'
    });
   
    history_panel.add(Individual_SPBackup_HistoryGrid(backup_id));
    var history_window=new Ext.Window({
                    title :'历史备份',
                    width :700,
                    height:250,
                    modal : true,
                    resizable : true
                });
    history_window.add(history_panel);
    history_window.show();

}

function SPBackupTaskGrid(node){
    var vm_id;
    var sp_id;
    var url_str;
    var hide_location = true;
    var hide_server_pool_col = true;
    if(node.attributes.nodetype==stackone.constants.DATA_CENTER)
    {
        hide_server_pool_col = false;
    }

    if((node.attributes.nodetype==stackone.constants.SERVER_POOL) || (node.attributes.nodetype==stackone.constants.DATA_CENTER ))
    {
        node_id = node.attributes.id;
        node_type = node.attributes.nodetype;
        url_str= 'backup/get_backupsetupinfo?node_id=' +node_id+ '&node_type='+ node_type;
        hide_location = true;
    }
    if(node.attributes.nodetype==stackone.constants.DOMAIN)
    { 
        vm_id = node.attributes.id;    
        var s_node = node.parentNode;
        var sp_node = s_node.parentNode;
        sp_id = sp_node.attributes.id;
        url_str= 'backup/get_vm_backupsetupinfo?sp_id=' +sp_id + '&vm_id='+vm_id;
        hide_location = false;
    
    }
   
    
    var label_task=new Ext.form.Label({
            html:'<div class="toolbar_hdg">'+_("备份策略")+'</div>',
            id:'label_task1'
        });
    
    var backup_selmodel=new Ext.grid.RowSelectionModel({
            singleSelect:true
        });
    
    var title_edit = new Ext.form.TextField();
    
    var backup_columnModel = new Ext.grid.ColumnModel([
        {
            header: "Site ID",
            width: 50,
            dataIndex: 'backupsetup_id',
            menuDisabled: false,
            hidden:true,
            editor: title_edit
            
        },
        {
            header: "策略",
            width: 120,
            dataIndex: 'taskname',
            sortable:true,
            editor: title_edit,
            id:'taskname'
    
        },
        {
            header: "服务器池",
            width: 100,
            dataIndex: 'serverpool',
            sortable:true,
            editor: title_edit,
            id:'serverpool',
            hidden:hide_server_pool_col
        },
        {
            header: "备份类型",
            width: 120,
            dataIndex: 'backup_type',
            sortable:true,
            editor: title_edit,
            id:'backup_type'
    
        },
        {
            header: "频率",
            width: 100,
            dataIndex: 'frequency',
            sortable:true,
            editor: title_edit,
            id:'frequency'
    
        },
        {
            header: "保留",
            width: 75,
            dataIndex: 'retention',
            sortable:true,
            editor: title_edit,
            id:'retention',
            align: 'right',
            hidden:true
        },
        {
            header: "位置",
            width: 200,
            dataIndex: 'location',
            sortable:true,
            editor: title_edit,
            id:'location',
            hidden:true
        },
        {
            header: "失败",
            width: 80,
            dataIndex: 'failures',
            sortable:true,
            editor: title_edit,
            //hidden: true,
            id:'failures',
            align: 'right'
    
        },
        {
            header: "开始时间",
            width: 140,
            dataIndex: 'start_time',
            sortable:true,
            editor: title_edit,
            id:'start_time',
            renderer:function(value,params,record,row){
                value = format_date(value,params,record);
                return value;
            }
        },
        {
            header: "状态",
            width: 100,
            dataIndex: 'status',
            sortable:true,
            editor: title_edit,            
            id:'status',
            renderer:function(value,params,record,row){            
               if(value =='Failed' || value =='Success'){
                params.attr='ext:qtip="Show Message"' +
                    'style="background-image:url(icons/information.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
             }
                return value;
            }
    
        },
        {
            header: "详细信息",
            width: 250,
            dataIndex: 'detail_msg',
            menuDisabled: false,
            hidden:true,
            editor: title_edit
            
        },
        {
            header: "Num Run",
            width: 50,
            dataIndex: 'num_runs',
            menuDisabled: false,
            hidden:true,
            editor: title_edit,
            align: 'right'
        }
//         {
//             header: "Backup Location",
//             width: 250,
//             dataIndex: 'location',
//             menuDisabled: false,
//             hidden:hide_location,
//             editor: title_edit,
//             
//         },
        
    ]);

     var backup_store =new Ext.data.JsonStore({
            //url: "get_backupsetupinfo",
            url: url_str,
            root: 'rows',
//             fields: [ 'backupsetup_id','taskname','backup_type', 'location', 'num_runs', 'next_schedule', 'last_backup_status', 'last_backup_detail' ],
            fields: [ 'backupsetup_id','taskname','backup_type', 'frequency', 'failures', 'start_time', 'status','detail_msg', 'num_runs', 'location', 'retention', 'serverpool'],
            successProperty:'success',
            listeners:{
                loadexception:function(obj,opts,res,e){
                    var store_response=Ext.util.JSON.decode(res.responseText);
                    Ext.MessageBox.alert("Error2",store_response.msg);
                }

            }
        });

    backup_store.load();

    var backup_grid=new Ext.grid.GridPanel({
        store: backup_store,
        stripeRows: true,
        colModel:backup_columnModel,
        frame:false,
        border: false,
        selModel:backup_selmodel,
        height:150,
        width:'100%',
        //autoExpandColumn:4,
        enableHdMenu:false,
        loadMask:true,
        id:'backup_grid',
        layout:'fit',
        tbar:[label_task],     
        listeners:{

            cellclick: function(grid ,rowIndex,columnIndex,e,b) {   
                if(node.attributes.nodetype==stackone.constants.SERVER_POOL || node.attributes.nodetype==stackone.constants.DATA_CENTER){
                    if (columnIndex == 9)
                    {
                        var record = grid.getStore().getAt(rowIndex);
                        var backup_id =record.get('backupsetup_id');
                        var num_runs =record.get('num_runs');
                        //showTaskMessage('Message',msg);
                        var result_window=new Ext.Window({
                            title :'备份结果',
                            width :500,
                            height:400,
                            modal : true,
                            resizable : false
                        });
                        result_window.add(Backup_report_grid(backup_id, num_runs, result_window));
                        result_window.show();
                        
                    }
                }
                if(node.attributes.nodetype==stackone.constants.DOMAIN){
                    var record = grid.getStore().getAt(rowIndex);
                    //var backup_id =record.get('backupsetup_id');
                    var msg =record.get('detail_msg');
                    showTaskMessage('Message',msg);
                }     

            },

            rowcontextmenu :function(grid,rowIndex,e) {                
                e.preventDefault();
                grid.getSelectionModel().selectRow(rowIndex);
                //handle_rowclick(grid,rowIndex,"contextmenu",e);
                var c=new Ext.menu.Menu({
                            items: [{
                                        text: '编辑备份策略',
                                        id: 'backup_edit',
                                        icon:'icons/file_edit.png',
                                        handler: BackupMenuHandler
                                    },
                                    new Ext.menu.Item({
                                        text: '移除备份策略',
                                        id: 'backup_remove',
                                        icon:'icons/delete.png',
                                        handler: BackupMenuHandler
                                    }),
                                    '-'
                            ]
//                             listeners: {
//                                 itemclick: function(item) {
//                                     alert(item)
//                                 }
//                             }
                        });
                c.contextNode = node;
                c.sp_id = sp_id;
                c.selected_grid = backup_grid;
                c.showAt(e.getXY()); 

                },

            rowdblclick:function(grid, rowIndex, e){
                
                edit_backuppolicy(grid,node,sp_id );
                /*sp_backup_grid= SP_Backup_Grid(node)

                var edit_rec=grid.getSelectionModel().getSelected();
                var backupsetup_id=edit_rec.get('backupsetup_id');
                
                var url="/backup/get_backupsetup_details?backupsetup_id="+backupsetup_id;
                var ajaxReq=ajaxRequest(url,0,"POST",true);


                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);

                        if(response.success){                            
                            var backup_details = response.backupsetup_details[0];
                            backupPanel = SPBackupConfigSettings(sp_backup_grid, node,sp_id, 'EDIT',backup_details)
                            showWindow(_("Edit Backup Task "), 640, 600,backupPanel );

                            var scheduleType_combo =backupPanel.findById('scheduleType_combo'); 
                            
                            var hourCombo =backupPanel.findById('hourCombo');
                            var week_checkBoxgroup =backupPanel.findById('week_checkBoxgroup');                
                            var month_checkBoxgroup =backupPanel.findById('month_checkBoxgroup'); 
                            
                            
                            switch (scheduleType_combo.getValue()) {
                                case "Hourly":
//                                     HourCombo.disable();
//                                     Week_checkBoxgroup.disable();
//                                     Month_checkBoxgroup.disable();
                                    hideField(hourCombo);
                                    hideField(week_checkBoxgroup);
                                    hideField(month_checkBoxgroup);
                
                                    break;
                                case "Daily":
                                    showField(hourCombo);
                                    hideField(week_checkBoxgroup);
                                    hideField(month_checkBoxgroup);
                                    break;
                                case "Weekly":
                                    showField(hourCombo);
                                    showField(week_checkBoxgroup);
                                    hideField(month_checkBoxgroup);
                                    break;
                                case "Monthly":
                                    showField(hourCombo);
                                    hideField(week_checkBoxgroup);
                                    showField(month_checkBoxgroup);
                                    break;
                            }

                        grid.getStore().load();

                        }else{
                            Ext.MessageBox.alert("Failure",response.msg);
                        }
                    },
                    failure: function(xhr){
                        Ext.MessageBox.alert( "Failure " , xhr.statusText);
                    }
               });*/
            }
        }  
    });

    return backup_grid; 
}

function shown_nonbackup_vm_window(node_id, node_type){

   var nonbackup_vm_window=new Ext.Window({
                        title :'没有备份策略的虚拟机',
                        width :420,
                        height:400,
                        modal : true,
                        resizable : false
                    });
                   
    nonbackup_vm_window.add(Non_backupVM_grid(node_id, node_type));
    nonbackup_vm_window.show();
}

function SP_backup_summary_grid(node_id, node_type){
    var sp_backup_summary_store =new Ext.data.JsonStore({
        url: "/backup/sp_backup_summary?node_id="+ node_id+"&node_type=" + node_type,
        root: 'info',
        fields: ['name','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    sp_backup_summary_store.load();

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_strge'
    });

    var sp_backup_summary_grid = new Ext.grid.GridPanel({       
        disableSelection:true,
        stripeRows: true,        
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 150,
        enableHdMenu:false,
         autoExpandColumn:1,
        enableColumnMove:false,        
        autoScroll:true,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 180, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:NewUIMakeUP},
            {header: "", width: 120, sortable: false, dataIndex: 'value',renderer:function(value,params,record,row){   
                var returnVal = value;
                if (row == 2)   
                { 
                    
                     var num_nonbackup_vm =record.get('value');  
                     if (num_nonbackup_vm != "0"){                    
                        var fn = "shown_nonbackup_vm_window('" + node_id + "','" +  node_type + "')";                   
                        returnVal = '<a href="#" onClick=' + fn + '>' + value + '</a>';
                    }
                }
            
                return returnVal;
            }
        }    
        ],
        store:sp_backup_summary_store,
        tbar:[label_strge]
    });

    return sp_backup_summary_grid
}


function SP_backup_failure_grid(node_id, node_type){
    var sp_backup_failure_store =new Ext.data.JsonStore({
        url: "/backup/sp_backup_failure?node_id="+ node_id+"&node_type=" + node_type,
        root: 'info',
        fields: ['node_id','vm','policy','last_success','num_fail'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    sp_backup_failure_store.load();

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("失败的备份")+'</div>',
        id:'label_strge'
    });

var sp_backup_failure_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("虚拟机编号"),
        width: 110,
        dataIndex: 'node_id',
        hidden:true,
        sortable:true
    },
    {
        header: _("虚拟机"),
        width: 100,
        dataIndex: 'vm',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("策略"),
        width: 100,
        sortable:true,
        dataIndex: 'policy'
    },
    {
        header: _("最近成功的备份"),
        width: 150,
        dataIndex: 'last_success',
        sortable:true,
        renderer:function(value,params,record,row){
            value = format_date(value,params,record);
            return value;
        }
    },
    {
        header: _("连续失败"),
        width: 150,
        dataIndex: 'num_fail',
        sortable:true,
        align: 'right'
        
    }]);
      
        
      
    var sp_backup_failure_grid = new Ext.grid.GridPanel({
        id:'sp_backup_failure_grid',
        forceSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:false,        
        width: '100%',
        height: 180,
        enableHdMenu:true,
        autoExpandColumn:1,        
        autoScroll:true,
        frame:false,
        colModel:sp_backup_failure_columnModel,
        store:sp_backup_failure_store,
        tbar:[label_strge],
        listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            rowdblclick:function(grid,rowIndex,e){
                handle_rowclick(grid,rowIndex,"click",e);
            }
        }
    });

    return sp_backup_failure_grid
}



function Backup_report_grid(backup_id, num_runs, parentwindow){

    var backup_report_store =new Ext.data.JsonStore({
        url: "/backup/backup_report?backup_id="+ backup_id+ "&num_runs="+ num_runs,
        root: 'info',
        fields: ['node_id','vm','status','message', 'detail_result'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    backup_report_store.load();

//     var label_strge=new Ext.form.Label({
//         html:'<div class="toolbar_hdg">'+_("Backup Failures")+'</div>',
//         id:'label_strge'
//     });

    var backup_report_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("虚拟机编号"),
        width: 110,
        dataIndex: 'node_id',
        hidden:true,
        sortable:true
    },
    {
        header: _("虚拟机"),
        width: 100,
        dataIndex: 'vm',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("状态"),
        width: 80,
        sortable:true,
        dataIndex: 'status'
    },
    {
        header: _("结果"),
        width: 200,
        sortable:true,
        dataIndex: 'message'
        
    },
    {
        header: _(""),
        width: 20,
        sortable:true,
        //hidden: true,
        dataIndex: 'detail_result',
        renderer:function(value,params,record,row){       
              
                params.attr='ext:qtip="Show Message"' +
                    'style="background-image:url(icons/information.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            
            //return value;
        }
    
        
    }]);
      
      
    var bkp_result_btnOk=new Ext.Button({
        name: 'bkp_rslt_ok',
        id: 'bkp_rslt_ok',
        text:_('OK'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                parentwindow.close();
            }
        }
    });

    var backup_report_grid = new Ext.grid.GridPanel({
        id:'backup_report_grid',
        forceSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:false,        
        width: '100%',
        height: 370,    //210
        enableHdMenu:true,
        autoExpandColumn:3,        
        autoScroll:true,
        frame:false,
        colModel:backup_report_columnModel,
        store:backup_report_store,
        //tbar:[label_strge],
        bbar:[{xtype: 'tbfill'}, bkp_result_btnOk],
        listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {                
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            rowdblclick:function(grid,rowIndex,e){                
                handle_rowclick(grid,rowIndex,"click",e);
                grid.parentwindow.close();
            },
            cellclick: function(grid ,rowIndex,columnIndex,e,b) {                
                if (columnIndex == 4)
                {
                    
                    var record = grid.getStore().getAt(rowIndex);                    
                    if(record.get('status') =='Failed'||record.get('status') =='Success'){
                        var detail_result=record.get('detail_result');
                        showTaskMessage('Message',detail_result);
                    }
                }

            }
        }
    });
    
    backup_report_grid.parentwindow = parentwindow;

    return backup_report_grid
}



function Backupconfig_list_grid(group_id){

    function showBackupCheckBox(value,params,record){
        var id = Ext.id();
        (function(){
            var disable = false;
            if( record.get('backup_all')== true)
            {
                disable = true;
            }

            new Ext.form.Checkbox({
                renderTo: id,
                checked:value,
                width:100,
                height:16,
                disabled :disable,
                id:"chkVM",
                listeners:{
                    check:function(field,checked){
                        if(checked==true){
                            record.set('allow_backup',true);
                        }else{
                            record.set('allow_backup',false);
                        }
                    }
                }
            });
        }).defer(20)
        return '<span id="' + id + '"></span>';
    }


    var backupconfig_list_columnModel = new Ext.grid.ColumnModel([
        {header: "Backup_id", hidden: true, dataIndex: 'backup_id'},
        {header: "备份策略", width: 100, sortable: true, dataIndex: 'name'},
        {
            header: "类型", width:80, sortable: true, 
            dataIndex: 'backup_type' 
            
        },
        {
            header: "频率", width:80, sortable: true, 
            dataIndex: 'frequency' 
            
        },   
        {
            header: "保留天数", width:100, sortable: true, 
            dataIndex: 'retention_days', 
            editor: new Ext.form.TextField({
                allowBlank: false
            })
        },
         {header: "选择", width: 80, sortable: true, renderer: showBackupCheckBox, dataIndex: 'allow_backup'},
        {header: "Backup_all", hidden: true, dataIndex: 'backup_all'}
        
    ]);

    url_vm_list_store= '/backup/get_backupConfig_of_sp?group_id=' +group_id;
    
    var backupconfig_list_store = new Ext.data.JsonStore({
//         url: '/storage/get_vm_list?group_id=' + "1",
        id: 'backupconfig_list_store',
        url: url_vm_list_store,
        root: 'rows',
        fields: ['backup_id', {name: 'allow_backup', type: 'boolean'}, 'name','backup_type','frequency', 'retention_days', 'backup_all' ],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e) {
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    backupconfig_list_store.load();

    var backupconfig_list_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var select_all_Button=new Ext.Button({
        name: 'select_all',
        id: 'select_all',
        text:_("选择全部"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                for(var i=0;i<backupconfig_list_store.getCount();i++){     
                    backupconfig_list_store.getAt(i).set('allow_backup',true);
               
                }
                
            }
        }
    });
   

    backupconfig_list_grid = new Ext.grid.EditorGridPanel({
        id: 'backupconfig_list_grid',
        store: backupconfig_list_store,
        colModel:backupconfig_list_columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:backupconfig_list_selmodel,
        width:'100%',
        height:320,
        //height:'100%',
        autoExpandColumn:1,
        autoExpandMin:120,
        enableHdMenu:false,
        clicksToEdit:2,
        tbar:[{
            xtype:'tbfill'
        }, select_all_Button]
    });
    return backupconfig_list_grid
}

function Backupconfig_list_window(group_id, vm_id){
    var backup_config_window=new Ext.Window({
                    title :'备份策略',
                    width :500,
                    height:400,
                    modal : true,
                    resizable : false
                });
   

    var button_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                backup_config_window.close();
                
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

            var backupconfig_list_store=backupconfig_list_grid.getStore();
            var backupconfig_stat = "[";
            for(var i=0;i<backupconfig_list_store.getCount();i++){
                if (backupconfig_list_store.getAt(i).get("allow_backup") == true)
                {
                    backupconfig_stat+="'"+backupconfig_list_store.getAt(i).get("backup_id")+"',";                    
                }
            }
            backupconfig_stat+="]";
            
            var backupconfig_jdata= eval("("+backupconfig_stat+")");

            params="vm_id="+vm_id+"&backup_id_list="+backupconfig_jdata;
            url="/backup/Add_vm_to_backuplist?"+params;      
            

            

            var ajaxReq=ajaxRequest(url,0,"GET",true);
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    
                    if(response.success){
                        //backup_grid.getStore().load();
                        backup_config_window.close();
                        //Ext.MessageBox.alert("Sucess",response.msg);
                    }else{
                        Ext.MessageBox.alert("Failure",response.msg);
                    }
                },
                failure: function(xhr){
                    Ext.MessageBox.alert( "Failure " , xhr.statusText);
                }
            });
    

                
               
            }
        }
    });

    var label_backup =new Ext.form.Label({
        html:'<div style="" class="boldlabelheading">'+_("备份策略")+'<br/></div>'
    });

    var backupconfig_list_grid = Backupconfig_list_grid(group_id);

    var backup_panel=new Ext.Panel({
        height:370,
        layout:"form",
        frame:false,       
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding:5px 5px 5px 5px',
        items:[label_backup, backupconfig_list_grid],
        bbar:[
        {
            xtype: 'tbfill'
        },button_ok,button_cancel]
        
       
        //tbar:[tlabel_backup, ]
    });
    backup_config_window.add(backup_panel);
    backup_config_window.show();

//return backup_panel;
}


function show_Backupconfig_list(data,cellmd,record,row,col,store) {

        var group_id = record.get("group_id"); 
        var vm_id = record.get("vm_id");  
//        alert(vm_id);
        
       
        //backup_config_window.show();

        var template_name = record.get("template");
        var desc = record.get("desc");
        
        var fn1 = "Backupconfig_list_window('" + group_id + "','" +  vm_id + "')";      
        var returnVal = '<a href="#" onClick=' + fn1 + ' ><img title="Backup Config" src="icons/file_edit.png "/></a>';
        
        return returnVal;
       
}


function Non_backupVM_grid(node_id, node_type){

    var non_backupVM_columnModel = new Ext.grid.ColumnModel([
        {header: "组编号", hidden: true, dataIndex: 'group_id'},
        {header: "虚拟机编号", hidden: true, dataIndex: 'vm_id'},
        {header: "虚拟机", width: 100, sortable: true, dataIndex: 'vm_name'},
        {header: "客户机操作系统", width: 80, sortable: true, dataIndex: 'os_name'},
        {header: "模板", width: 120, sortable: true, dataIndex: 'template'},
        {header: "相关策略", width: 110, sortable: true, dataIndex: 'details', renderer: show_Backupconfig_list}        
        
    ]);

    url_vm_list_store= '/backup/non_backupVM?node_id='+node_id+ '&node_type='+node_type;
 
    var non_backupVM_store = new Ext.data.JsonStore({
//         url: '/storage/get_vm_list?group_id=' + "1",
        id: 'non_backupVM_store',
        url: url_vm_list_store,
        root: 'info',
        fields: ['group_id','vm_id', 'vm_name', 'os_name', 'template'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e) {
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    non_backupVM_store.load();

    var non_backupVM_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    

    non_backupVM_grid = new Ext.grid.GridPanel({
        id: 'non_backupVM_grid',
        store: non_backupVM_store,
        colModel:non_backupVM_columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:non_backupVM_selmodel,
        width:'100%',
        //height:140,
        height:390,
        autoExpandColumn:2,
        autoExpandMin:100,
        enableHdMenu:false        
        
    });
    return non_backupVM_grid
}

