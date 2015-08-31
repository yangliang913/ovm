/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function server_summary_page(mainpanel,node_id,node){
    //node_id='d9a3bd4a-062a-5017-22af-94222763e8b9';
    if(mainpanel.items)
        mainpanel.removeAll(true);

//    var label0_1=new Ext.form.Label({
//        html:'<div class="toolbar_hdg" >'+_("Daily")+'<br/></div>'
//    });
    var label2=new Ext.form.Label({
        html:getChartHdrMsg(node.text,"Hourly","CPU")
    });

    var avg_fdate="",avg_tdate="",selperiod=stackone.constants.HRS12;
    var avg_button=new Ext.Button({
        icon: '/icons/date.png', // icons can also be specified inline
        cls: 'x-btn-icon',
        tooltip: {
            text:'<b>显示平均值</b><br/>'
        },
        handler:function(){
            var avg=new CustomPeriodUI(_("显示平均值"),fdate,tdate,selperiod);
            var avg_window = avg.getWindow();
            var btn= new Ext.Button({
                id:'avg_button',
                text: _('确定'),
                listeners: {
                    click: function(btn) {
                        if(avg.validate()){
                            avg_window.hide();
                            avg_fdate=avg.fromTime();
                            avg_tdate=avg.toTime();
                            var label=formatDate(new Date(avg_fdate))+" - "+formatDate(new Date(avg_tdate));
                            var btnEl = avg_button.getEl().child(avg_button.buttonSelector);
                            var tgt = Ext.QuickTips.getQuickTip().targets[btnEl.id];
                            tgt.text = '<b>显示平均值</b><br/>'+label;
                            redrawChart(stackone.constants.MANAGED_NODE,type_combo.getValue(),node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'s_chart'+node_id,true,panel2,null,avg_fdate,avg_tdate);
                        }
                    }
                }
            });
            avg_window.addButton(btn);
            avg_window.show();

        }
    });

    var period_combo=getPeriodCombo();
    var fdate="",tdate="";
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
                            redrawChart(stackone.constants.MANAGED_NODE,type_combo.getValue(),node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'s_chart'+node_id,true,panel2,null,avg_fdate,avg_tdate);

                            label2.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
                        }
                    }
                }
            });
            cust_window.addButton(custom_btn);
            cust_window.show();
        }else{
            selperiod=period_combo.getValue();
            fdate="",tdate="";
            redrawChart(stackone.constants.MANAGED_NODE,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'s_chart'+node_id,true,panel2,null,avg_fdate,avg_tdate);
            label2.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
        }
    });

    var type_combo=getMetricCombo();
    type_combo.on('select',function(field,rec,index){
        redrawChart(stackone.constants.MANAGED_NODE,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'s_chart'+node_id,true,panel2,null,avg_fdate,avg_tdate);
        label2.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
    });

//    var srvr_info_grid=server_info_grid(node_id);
//    var srvr_sec_info_grid=server_sec_info_grid(node_id);
    var srvr_vm_grid=server_vm_grid(node_id);
//    var srvr_storage_grid=server_storage_grid(node_id,node);
//    var srvr_nw_grid=server_nw_grid(node_id,node);
    var top_cpu_grid=topNvms(node_id, node, "CPU");
    var top_mem_grid=topNvms(node_id, node, "Memory");

    var panel1 = new Ext.Panel({
        height:260,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column',
        bodyStyle:'padding-top:5px;padding-right:5px;'
    });
    var panel1_0 = new Ext.Panel({
        height:255,
        width:'30%',
        border:false,
        bodyBorder:false
        //,bodyStyle:'padding-right:15px;'
        ,layout:'fit'
    });
    var label1_1=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("CPU利用率")+'<br/></div>'
    });
    var label1_2=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("内存利用率")+'<br/></div>'
    });
    var panel1_1 = new Ext.Panel({
        height:230,
        width:'49.5%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        //,bodyStyle:';padding-right:15px;'
        ,tbar:[label1_1]
    });
    var panel1_2 = new Ext.Panel({
        height:230,
        width:'49.5%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        //,bodyStyle :'padding-left:15px;padding-right:15px;'
        ,tbar:[label1_2]
    });
//    var panel1_5 = new Ext.Panel({
//        height:'100%',
//        width:'60%',
//        border:false,
//        bodyBorder:false
//        //,bodyStyle:'padding-left:15px;padding-right:30px;padding-bottom:12px;padding-top:10px;'
//        ,layout:'fit'
//    });
    var panel2 = new Ext.Panel({
        height:255,
        width:'69%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        //,bodyStyle:'padding-left:15px;padding-right:30px;padding-bottom:12px;padding-top:10px;'
        ,tbar:[' ',label2,{xtype:'tbfill'},avg_button,'-',period_combo,'-',type_combo]
    });  
    //var summary_grid=drawsummaryGrid(rows,node.attributes.nodetype,node.attributes.id,true,panel2);

    var panel3 = new Ext.Panel({
        height:'100%',
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column'
        , bodyStyle:'padding-top:10px;padding-right:5px;'
    });

    var panel4 = new Ext.Panel({
        height:'100%',
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column'
        , bodyStyle:'padding-top:10px;padding-right:5px;'
    });

    var dummy_panel1 = new Ext.Panel({
        width:'1%',
        border:true,
        html:'&nbsp;&nbsp;',
        bodyBorder:false
    });
    
    var dummy_panel3 = new Ext.Panel({
        width:'1%',
        border:true,
        html:'&nbsp;',
        bodyBorder:false
    });
    var dummy_panel4 = new Ext.Panel({
        width:'1%',
        border:true,
        html:'&nbsp;',
        bodyBorder:false
    });

//    var info_panel=new Ext.Panel({
//        width:'48%',
//        height: 140,
//        border:false,
//        bodyBorder:false,
//        bodyStyle:'padding-left:15px;padding-right:3px;padding-top:10px;',
//        layout:'fit'
//    });
//    var sec_info_panel=new Ext.Panel({
//        width:'48%',
//        height: 140,
//        border:false,
//        bodyBorder:false,
//        bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
//        layout:'fit'
//    });

    var cpu_panel=new Ext.Panel({
        width:'49.5%',
        height: 230,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:15px;padding-right:3px;padding-top:2px;',
        layout:'fit'
    });
    var mem_panel=new Ext.Panel({
        width:'49.5%',
        height: 230,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:15px;padding-right:3px;',
        layout:'fit'
    });

    //panel1_1.add(get_cpu_chart());
    redrawChart(stackone.constants.MANAGED_NODE,stackone.constants.CPU,node_id,node.text,
                        stackone.constants.HRS12,fdate,tdate,'s_chart'+node_id,true,panel2,null,avg_fdate,avg_tdate);
    panel1_0.add(srvr_vm_grid);
    //panel1_5.add(panel2)
    panel1.add(panel1_0);
    panel1.add(dummy_panel1);
    panel1.add(panel2);
//    panel1.add(panel1_0);
//    panel1.add(dummy_panel1);
//
    panel1_1.add(server_usage_chart(node_id, node, "CPU"));
    panel1_2.add(server_usage_chart(node_id, node, "Memory"));
//    panel1.add(panel1_1);
//    panel1.add(dummy_panel2);
//    panel1.add(panel1_2);
    //panel1_1.add(label1_1);

//    panel1.add(dummy_panel2);
//    panel1.add(chpanel2);

    //panel2.add(summary_grid);

//    info_panel.add(srvr_info_grid);
//    sec_info_panel.add(srvr_sec_info_grid);

//    panel3.add(info_panel);
//    panel3.add(dummy_panel3);
//    panel3.add(sec_info_panel);

    //storage_panel.add(label3);
    cpu_panel.add(top_cpu_grid);
    //nw_panel.add(label4);
    mem_panel.add(top_mem_grid);

    panel3.add( panel1_1);
    panel3.add(dummy_panel3);
    panel3.add(cpu_panel);
    panel4.add(panel1_2);
    panel4.add(dummy_panel4);
    panel4.add(mem_panel);
    
    //panel4.add(label2);


    var topPanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Server Information for {0}"),node.text),
        height:'100%',
        width:'100%',
        border:false,
        cls:'headercolor',
        layout:'column',
        bodyBorder:false,
//        ,bodyStyle:'padding-left:10px;padding-right:5px;padding-top:5px;',
        items:[panel1,panel3,panel4]
    });

//    var bottomPanel = new Ext.Panel({
//        //layout  : 'fit',
////        collapsible:true,
////        title:"Top VMs",
//        height:'35%',
//        width:'100%',
//        border:false,
//        cls:'headercolor',
//        bodyBorder:false,
//        bodyStyle:'padding-top:15px;',
//        items:[]
//    });

    var server_homepanel=new Ext.Panel({
         height:'50%',
         width:'100%',
         border:false,
         bodyBorder:false
        ,collapsible:false
        ,items:[topPanel]
        ,bodyStyle:'padding-left:10px;padding-right:5px;padding-top:5px;'
    });
    //server_homepanel.add(topPanel);
    //server_homepanel.add(bottomPanel);
    mainpanel.add(server_homepanel);
    server_homepanel.doLayout();
    mainpanel.doLayout();
    centerPanel.setActiveTab(mainpanel);
}

/**
 * 节点-入门面板
 * 
 * @param {}
 *            mainpanel
 * @param {}
 *            node_id
 * @param {}
 *            node
 */
function server_managernodeStarter_page(mainpanel, node_id, node) {
	if (mainpanel.items)
		mainpanel.removeAll(true);
	var url = "/dashboard/server_info?type=VM_INFO&node_id="
			+ node_id;
	var ajaxReq = ajaxRequest(url, 0, "GET", true);
	ajaxReq.request({
		success : function(xhr) {
			var response = Ext.util.JSON.decode(xhr.responseText);
			if (response.success) {
				server_list = response.info[8].list;
			}
		},
		failure : function(xhr) {
		}
	});
	/*var topHtml = '';
	topHtml += '<div class="toolbar_hdg" >';
	topHtml += '</div>';*/
	var topHtml = '';
	topHtml += '<div class="managed-node-starter-top">';
	topHtml += '	<div class="managed-node-starter-top-text">';
	topHtml += _("什么是主机？");
	topHtml += '<br/>';
	topHtml += '<br/>';
	topHtml += _("主机是使用虚拟化管理软件运行不同虚拟机的服务器，主机提供虚拟机使用的CPU、内存、网络和存储资源，并使虚拟机有访问的权限。");
	topHtml += '	</div>';
	topHtml += '	<div class="managed-node-starter-top-img">';
	topHtml += '	</div>';
	topHtml += '</div>';

	var leftHtml = '';
	leftHtml += '<div class="managed-node-starter-left-text">';
	leftHtml += '<div>基本任务</div>';
	leftHtml += '<a href="#" onclick=javascript:server_managernodeStarter_page_insertVm();>';
	leftHtml += '新建虚拟机';
	leftHtml += '</a>';
	leftHtml += '<br/>';
	leftHtml += '</div>';
	
	var rightHtml = '';
	rightHtml += '<div class="managed-node-starter-right-text" >';
	rightHtml += _("了解如何新建虚拟机？");
	rightHtml += '<br/><br/>';
	rightHtml += _("您可以使用多种方法新建虚拟机。例如：您新建一个空白虚拟机、克隆现有的虚拟机、或从模板部署虚拟机，以及把物理机转换成虚拟机。");
	rightHtml += '<br/>';
	rightHtml += '<br/>';
	rightHtml += _("创建虚拟机时，它将创建在您选择的某台主机上面，虚拟机在这台主机上运行并使用该主机的资源。您也可以迁移虚拟机从该主机到另外一台主机上面（同一数据中心内，且虚拟机的存放位置是在共享存储上面）。");
	rightHtml += '</div>'
	var topPanel = new Ext.Panel({
		height : 300,
		width : '100%',
		region : 'north',
		border: false,
		frame: true,
		// border:false,//lbz更改，添加一句
		bodyStyle : 'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
		html : topHtml
	});
	var leftPanel = new Ext.Panel({
		height : '60%',
		width : '40%',
		border: false,
		frame: true,
		region : 'west',
		// border:false,//lbz更改，添加一句
		bodyStyle : 'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
		html : leftHtml
	});
	var rightPanel = new Ext.Panel({
		height : '60%',
		width : '60%',
		border: false,
		frame: true,
		region : 'center',
		// border:false,//lbz更改，添加一句
		bodyStyle : 'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
		html : rightHtml
	});

	var serverStarterPanel = new Ext.Panel({
		width : "100%",
		height : "100%",
		layout : 'border',
		border:false,//lbz更改：添加一句
		items : [topPanel, leftPanel, rightPanel]
	});
	mainpanel.add(serverStarterPanel);
	serverStarterPanel.doLayout();
	mainpanel.doLayout();
}

function server_managernodeStarter_page_insertVm() {
	maintenance_check(leftnav_treePanel.getSelectionModel().getSelectedNode(), "provision_vm", null, null);
}


function server_config_page(mainpanel,node_id,node){

    if(mainpanel.items)
        mainpanel.removeAll(true);

    var panel1 = new Ext.Panel({
        width:'100%',
        height: '30%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });
    var panel2 = new Ext.Panel({
        width:'100%',
        height: '100%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });
    var panel3 = new Ext.Panel({
        width:'100%',
        height: '100%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });
    var panel4 = new Ext.Panel({
        width:'100%',
        height: '100%',
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
    var dummy_panel2 = new Ext.Panel({
        width:'1%',
        html:'&nbsp;',
        border:false,
        bodyBorder:false
    });
    var dummy_panel3 = new Ext.Panel({
        width:'1%',
        html:'&nbsp;',
        border:false,
        bodyBorder:false
    });
    var dummy_panel4 = new Ext.Panel({
        width:'1%',
        html:'&nbsp;',
        border:false,
        bodyBorder:false
    });
    var panel1_1=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel1_2=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel2_1=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel2_2=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel3_1=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel3_2=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel4_1=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel4_2=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });

    var srvr_interface_grid= server_interface_grid(node_id,node);
    var srvr_dvce_grid=server_dvce_grid(node_id,node);

    var srvr_storage_grid=server_storage_grid(node_id, node);
    var srvr_nw_grid=server_nw_grid(node_id, node);

    panel1_1.add(server_config_grid(node_id, node, "Platform"));
    panel1_2.add(server_config_grid(node_id, node, "Memory"));

    panel2_1.add(server_config_grid(node_id, node, "OS"));
    panel2_2.add(server_config_grid(node_id, node, "CPU"));

    panel3_1.add(srvr_interface_grid);
    panel3_2.add(srvr_dvce_grid);

    panel4_1.add(srvr_storage_grid);
    panel4_2.add(srvr_nw_grid);

    panel1.add(panel1_1);
    panel1.add(dummy_panel1);
    panel1.add(panel1_2)

    panel2.add(panel2_1);
    panel2.add(dummy_panel2);
    panel2.add(panel2_2)

    panel3.add(panel3_1);
    panel3.add(dummy_panel3);
    panel3.add(panel3_2);   

    panel4.add(panel4_1);
    panel4.add(dummy_panel4);
    panel4.add(panel4_2);

    var configpanel = new Ext.Panel({
        height:"100%",
        width:"100%",
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-left:10px;padding-right:5px;',
        items:[panel1,panel2,panel3,panel4]
    });
    mainpanel.add(configpanel);
    configpanel.doLayout();
    mainpanel.doLayout();

}

function server_vminfo_page(mainpanel,node_id,node){

     if(mainpanel.items)
        mainpanel.removeAll(true);

    var panel2 = new Ext.Panel({
        height:350,
        width:'100%',
        layout: 'fit',
        bodyStyle:'padding-bottom:12px;padding-top:10px;',
        border:false,
        bodyBorder:false
    });
    var summary_grid=showVMList(node_id,stackone.constants.MANAGED_NODE,panel2);
    //drawsummaryGrid(rows,node.attributes.nodetype,node.attributes.id,true,panel2);

    panel2.add(summary_grid);

    var vminformpanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Server Pool Information for {0}"),node.text),
        height:'50%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false,
        bodyStyle:'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
        resizable:true,
        items:[panel2]
    });

    mainpanel.add(vminformpanel);
    vminformpanel.doLayout();
    mainpanel.doLayout();
}

function server_info_grid(node_id){
    var server_info_store =new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=SERVER_INFO",
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
    server_info_store.load({
        params:{
            node_id:node_id
        }
    });

    var server_info_grid = new Ext.grid.GridPanel({
        //title:'Physical Resources',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        cls:'hideheader',
        width:'100%',
        //height: 200,
        enableHdMenu:false,
        enableColumnMove:false,
         autoExpandColumn:1,
        //plugins:[action],
        autoScroll:true,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 100, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 200, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:server_info_store
    });

    return server_info_grid
}

function server_task_details_page(mainpanel,node_id,node){
     if(mainpanel.items)
        mainpanel.removeAll(true);
     var task_grid=draw_grid(node_id,node,"服务器任务",520);
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

function draw_grid(node_id,node,grd_lbl,grd_height){

      var node_type=node.attributes.nodetype;

      var task_columnModel = new Ext.grid.ColumnModel([
     {
         header: "",
         dataIndex: 'task_id',
         menuDisabled: false,
         hidden:true

     },
     {
         header: "任务名称",
         width: 135,
         dataIndex: 'taskname',
         sortable:true,
         renderer:customize_taskname

     },
     {
         header: "用户名",
         width: 125,
         dataIndex: 'username',
         sortable:true

     },
     {
         header: "实体名称",
         width: 125,
         dataIndex: 'entity_name',
         sortable:true

     },
     {
         header: "开始时间",
         width: 190,
         dataIndex: 'start_time',
         sortable:true,
         renderer:format_date

     },
     {
         header: "结束时间",
         width: 190,
         dataIndex: 'end_time',
         sortable:true,
         renderer:format_date

     },
     {
         header: "状态",
         width: 130,
         dataIndex: 'status',
         sortable:true,
         renderer:function(value,params,record,row){
              if(value =='Failed' || value =='Succeeded' || value =='Not Started'|| value =='Canceled'){
                params.attr='ext:qtip="Show Message"' +
                    'style="background-image:url(icons/information.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            }
            return value;
        }

     }
     ,
     {
         header: "",
         width: 25,
         dataIndex: 'edit_icon',
         sortable:true

     }
     ,
     {
         header: "",
         width: 25,
         dataIndex: 'delete_icon',
         sortable:true

     },
     {
        header: _(""),
        width: 25,
        dataIndex: 'status',
        sortable:true,
        renderer:function(value,params,record,row){
            if(value =='Started' && record.get('cancellable')==true){
                return "<img title='Cancel Task' alt='Cancel Task' align='right' width='13' height='13' "+
                    "src='icons/cancel.png' style='cursor:pointer'/>";
            }
            return "";
        }
     }
     ]);
     var task_selmodel=new Ext.grid.RowSelectionModel({
             singleSelect:true
         });


      var task_store =new Ext.data.JsonStore({
             //url: "get_backupsetupinfo",
             url: '/node/get_tasks?node_id='+node_id+'&node_type='+node_type,
             root: 'rows',
             fields: [ 'task_id','taskname','username','entity_name','start_time',
                        'end_time','status','edit_icon','delete_icon','error_msg','cancellable'],
             sortInfo: {
                field: 'start_time',
                direction: 'DESC'
             },
             successProperty:'success',
             listeners:{
                 loadexception:function(obj,opts,res,e){
                     var store_response=Ext.util.JSON.decode(res.responseText);
//                     Ext.MessageBox.alert("Error2",store_response.msg);
                 }

             }
         });

     task_store.load();

    var label_task=new Ext.form.Label({
         html:'<div class="toolbar_hdg">'+_(grd_lbl)+'</div>',
         id:'label_task1'
     });
      var task_dis_store =new Ext.data.JsonStore({
             //url: "get_backupsetupinfo",
             url: '/node/get_task_display',
             root: 'task_display',
             fields: [ 'id','value'],
             successProperty:'success',
             listeners:{
                load:function(obj,opts,res){
                    task_type.setValue(obj.getAt(0).get("value"));
                },
                 loadexception:function(obj,opts,res,e){
                     var store_response=Ext.util.JSON.decode(res.responseText);
                     Ext.MessageBox.alert("Error2",store_response.msg);
                 }

             }
         });

     task_dis_store.load();
     var task_type=new Ext.form.ComboBox({
        fieldLabel: _('显示'),
        allowBlank:false,
        triggerAction:'all',
        store: task_dis_store,
        displayField:'value',
        valueField:'id',
        width: 100,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'task_type',
        id:'task_type',
        mode:'local',
        listeners:{
            select:function(combo,record,index){
                    task_grid.getStore().load({
                        params:{
                            display_type:task_type.getValue()
                        }
                    });
            }
        }
     });
     var task_grid=new Ext.grid.GridPanel({
         store: task_store,
         stripeRows: true,
         colModel:task_columnModel,
         frame:false,
         selModel:task_selmodel,
         height:grd_height,
         width:'100%',
         enableHdMenu:false,
         loadMask:true,
         autoExpandColumn:1,
         id:'task_grid',
         layout:'fit',
         tbar:[label_task,{xtype:'tbfill'},_('显示: '),task_type],
         listeners:{
            cellclick:function(grid, rowIndex, columnIndex, e) {
                windowid=Ext.id();
                var record=task_grid.getStore().getAt(rowIndex);
                var task_name=record.get("taskname");
                var status=record.get("status");
                if(columnIndex==9 && status =='Started' && record.get('cancellable')==true){
                   canceltask(record.get('task_id'),task_name);
                   return;
                }
                if(columnIndex==7 && status=="Not Started"){
                        edit_schedule(task_grid, rowIndex,task_name,task_type.getValue());
                }else if(columnIndex==8 && status=="Not Started"){
                        Ext.MessageBox.confirm(_("确认"),_("确定删除任务吗？ "+task_name), function(id){
                                if(id=="yes"){
                                    delete_schedule(task_grid, rowIndex,task_type.getValue());
                                }
                        });
                }else if(columnIndex==6 && (status=="Succeeded"||status=="Failed"||
                        status=="Not Started" || status =='Canceled')){
                    var err=record.get('error_msg');
                    if (status=="Not Started")
                        err+="Task "+task_name+" is scheduled to run at "+format_date(record.get("start_time"));
                    showTaskMessage('Message',err);
                }

            }
         }
     });

     if (node_type==stackone.constants.DOMAIN){
        task_columnModel.setHidden(3,true);
        task_columnModel.setColumnWidth(1,100);
        task_columnModel.setColumnWidth(2,80);
        task_columnModel.setColumnWidth(4,130);
        task_columnModel.setColumnWidth(5,130);
        task_columnModel.setColumnWidth(6,90);
//        task_columnModel.setColumnWidth(7,30);
//        task_columnModel.setColumnWidth(8,55);
//        task_grid.setHeight(248);
     }else{
        task_columnModel.setHidden(3,false);
        task_columnModel.setColumnWidth(1,125);
        task_columnModel.setColumnWidth(2,125);
        task_columnModel.setColumnWidth(3,135);
        task_columnModel.setColumnWidth(4,150);
        task_columnModel.setColumnWidth(5,150);
        task_columnModel.setColumnWidth(6,120);
//        task_columnModel.setColumnWidth(7,40);
//        task_columnModel.setColumnWidth(8,55);
     }


     return task_grid;

}
function customize_taskname(value,params,record){
    var t_name=["Provision","start","pause","unpause","shutdown","kill","reboot","Migrate",
        "Remove","start_all","shutdown_all","kill_all","migrate_all","Snapshot",
        "Import Virtual Machine","Import Virtual Machines"];
    var t_label=["Provision","Start","Pause","Resume","Shutdown","Kill","Reboot","Migrate",
        "Remove","Start All","Shutdown All","Kill All","Migrate All","Snapshot","Import",
        "Import"];
    if (value==null || value==""){
            return value;
    }
    var idx=t_name.indexOf(value);
    if (idx==-1)
        return value;
    else{
        value=t_label[idx];
    }
    return value;
}
function server_sec_info_grid(node_id){
    var server_sec_info_store =new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=SERVER_SEC_INFO",
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
    server_sec_info_store.load({
        params:{
            node_id:node_id
        }
    });

    var server_sec_info_grid = new Ext.grid.GridPanel({
        //title:'Physical Resources',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        cls:'hideheader padded',
        width:'100%',
        //height: 200,
        enableHdMenu:false,
        enableColumnMove:false,
         autoExpandColumn:1,
        //plugins:[action],
        autoScroll:true,
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
        store:server_sec_info_store
    });

    return server_sec_info_grid
}

function server_vm_grid(node_id){
    var vm_info_store =new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=VM_INFO",
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

    var server_vm_grid = new Ext.grid.GridPanel({
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
            {header: "", width: 140, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:NewUIMakeUP},
            {header: "", width: 100, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_info_store
        ,tbar:[label_strge]
    });

    return server_vm_grid
}

function server_dvce_grid(node_id,node){

    var server_dvce_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("设备"),
        width: 150,
        dataIndex: 'file_system',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("挂载"),
        width: 150,
        sortable:true,
        dataIndex: 'mounted_on'
    },
    {
        header: _("大小"),
        width: 100,
        dataIndex: 'size',
        sortable:true
    }]);

    var server_dvce_store = new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=DISK_INFO",
        root: 'info',
        fields: ['file_system','mounted_on','size'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_dvce_store.load({
        params:{
            node_id:node_id
        }
    });
    
   var label_dvce=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("挂载设备")+'</div>'
   });
	var server_dvce_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: server_dvce_store,
        colModel:server_dvce_columnModel,
        stripeRows: true,
        frame:false,
        //title:_("Mounted Devices"),
        autoExpandColumn:1,
        autoExpandMax:300,
//        border:false,
        enableHdMenu:false,
        //cls:'headercolor1',
        autoScroll:true,
        //cls:'padded',
//        viewConfig: {
//            getRowClass: function(record, index) {
//                return 'row-border';
//            }
//        },
        width:'100%',
        //autoExpandColumn:1,
        height:220
        ,tbar:[label_dvce]
    });

	return server_dvce_grid;

}

function server_interface_grid(node_id,node){

    var server_interface_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width: 110,
        dataIndex: 'interface_name',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("IP地址"),
        width: 300,
        sortable:true,
        dataIndex: 'ip_address'
    }]);

    var server_interface_store = new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=INTERFACE_INFO",
        root: 'info',
        fields: ['interface_name','ip_address'],
        sortInfo: {
            field: 'interface_name',
            direction: 'ASC'
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_interface_store.load({
        params:{
            node_id:node_id
        }
    });
   var label_interface=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("可用接口")+'</div>'
   });
    
	var server_interface_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: server_interface_store,
        colModel:server_interface_columnModel,
        stripeRows: true,
        //title:_("Available Interfaces"),
        frame:false,
        autoExpandColumn:1,
        autoExpandMax:350,
        //cls:'headercolor1',
        //border:false,
        enableHdMenu:false,
        autoScroll:true,
        //cls:'padded',
//        viewConfig: {
//            getRowClass: function(record, index) {
//                return 'row-border';
//            }
//        },
        width:'100%',
        //autoExpandColumn:1,
        height:220
        ,tbar:[label_interface]
    });

	return server_interface_grid;

}

function server_config_grid(node_id,node,config){    

    var server_config_store = new Ext.data.JsonStore({
        url: "/dashboard/server_info?type="+config+"_INFO",
        root: 'info',
        fields: ['label','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_config_store.load({
        params:{
            node_id:node_id
        }
    });

   var label_config=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+format(_("{0}信息"),config)+'</div>'
   });
    
    var srvr_config_grid = new Ext.grid.GridPanel({
        //title:'Physical Resources',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        //title:format(_("{0} Information"),config),
        border:true,
        //cls:'hideheader padded headercolor1',
        cls:'hideheader',
        width:'100%',
//        autoHeight:true,
        height:150,
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
            {header: "", width: 150, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'label',renderer:NewUIMakeUP},
            {header: "", width: 280, sortable: false, dataIndex: 'value',renderer:UIMakeUP,css: 'white-space: normal !important;'}
        ],
        store:server_config_store
        ,tbar:[label_config]
    });

    return srvr_config_grid
}

function server_usage_chart(node_id,node,metric){
    var srvr_usage_store = new Ext.data.Store({
        url: "/dashboard/server_usage?node_id="+node_id+"&metric="+metric,
        reader: new Ext.data.JsonReader({
            root: 'info',
            fields: ['label', 'value']
        })
    });

    var srvr_usage_pie = new Ext.ux.PieFlot({
        pies: {
            show: true,
            autoScale: true,
            fillOpacity: 1,
            labelFormatter: function(label, value, percent, textValue, pie, serie, options) {
                if(value == 0)
                {
                    return '';
                }
                return textValue + '% ';
            },
            labelStyle: 'font-size:11px; '

        },
        width:'100%',
        height:'100%',
        legend: {
            show: true,
            position: "se",
            margin: [0,0],
            backgroundOpacity: 0
        },
        series: []
    });

    srvr_usage_store.on('load',
        function(store, records, options) {
            try{
                var series = this.createSeries(store, 'label', 'value');
                this.plot(series);
                this.baseRanges = this.getRanges();
            }catch(e)
            {
//                Ext.MessageBox.alert(_("Error"),e);
            }

        },
        srvr_usage_pie
    );

    srvr_usage_store.load();

    return srvr_usage_pie;
}

function topNvms(node_id,node,metric){
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
            width: 350,
            dataIndex: 'vm',
            //css:'font-weight:bold;',
            sortable:true
        },
        {
            header: format(_("主机{0}(%)"),metric),
            width: 230,
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
        html:'<div class="toolbar_hdg">'+format(_("负载最高虚拟机 {0} 利用率"),metric)+'</div>',
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
        //border:false,
        enableHdMenu:false,
        autoScroll:true,
        width:'100%',
        //autoExpandColumn:1,
        height:300
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

function server_storage_grid(node_id,node){

    var server_storage_columnModel = new Ext.grid.ColumnModel([
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
        width: 100,
        dataIndex: 'size',
        sortable:true
    },
    {
        header: _("说明"),
        width: 150,
        dataIndex: 'description',
        sortable:true
    },
    {
        header: _("状态"),
        width: 100,
        dataIndex: 'status',
        sortable:true,
        renderer: showSyncStatus
    }]);

    var server_storage_store = new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=STORAGE_INFO&op=S",
        root: 'info',
        fields: ['name','type','size','description','status'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_storage_store.load({
        params:{
            node_id:node_id
        }
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
    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("存储资源")+'</div>'
    });

    var server_storage_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: server_storage_store,
        colModel:server_storage_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:3,
        autoExpandMax:300,
//        border:false,
        enableHdMenu:true,
        autoScroll:true,
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

	return server_storage_grid;

}

function server_nw_grid(node_id,node){

    var server_nw_columnModel = new Ext.grid.ColumnModel([
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
        header: _("详情"),
        width: 100,
        sortable:true,
        dataIndex: 'definition'
    },
    {
        header: _("说明"),
        width: 80,
        sortable:true,
        dataIndex: 'description'
    },
    {
        header: _("范围"),
        width: 110,
        sortable:true,
        dataIndex: 'displayscope',
        hidden:true
    }]);

    var server_nw_store = new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=VIRT_NW_INFO",
        root: 'info',
        fields: ['name','definition','type','description','displayscope'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    server_nw_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_nw=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("虚拟网络")+'</div>'
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
	var server_nw_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: server_nw_store,
        colModel:server_nw_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:3,
        autoExpandMax:300,
        //border:false,
        enableHdMenu:true,
        autoScroll:true,
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

	return server_nw_grid;

}
