/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function vm_summary_page(mainpanel,node_id,node){
    if(mainpanel.items)
        mainpanel.removeAll(true);

    var label0_1=new Ext.form.Label({
        html:'<div class="toolbar_hdg" >'+_("常规")+'<br/></div>'
    });
    var label1_1=new Ext.form.Label({
        html:getChartHdrMsg(node.text,"小时","CPU")
    });
     var label1_2=new Ext.form.Label({
        html:getChartHdrMsg(node.text,"小时","内存")
    });

    var avg_fdate="",avg_tdate="";
    var avg_button=new Ext.Button({
        icon: '/icons/date.png', // icons can also be specified inline
        cls: 'x-btn-icon',
        tooltip: {
            text:'<b>Show Average</b><br/>'
        },
        handler:function(){
            var avg=new CustomPeriodUI(_("显示平均值"),fdate,tdate,selperiod);
            var avg_window = avg.getWindow();
            var btn= new Ext.Button({
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
                            redrawChart(stackone.constants.DOMAIN,type_combo.getValue(),node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'vm_cpu_chart'+node_id,true,panel1_1,null,avg_fdate,avg_tdate);
                        }
                    }
                }
            });
            avg_window.addButton(btn);
            avg_window.show();

        }
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
                            redrawChart(stackone.constants.DOMAIN,type_combo.getValue(),node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'vm_cpu_chart'+node_id,true,panel1_1,null,avg_fdate,avg_tdate);

                            label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
                        }
                    }
                }
            });
            cust_window.addButton(custom_btn);
            cust_window.show();
        }else{
            selperiod=period_combo.getValue();
            fdate="",tdate="";
            redrawChart(stackone.constants.DOMAIN,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'vm_cpu_chart'+node_id,true,panel1_1,null,avg_fdate,avg_tdate);
            label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
        }
    });

    var storelst = [[stackone.constants.CPU,_(stackone.constants.CPU)],
                [stackone.constants.VMCPU,_(stackone.constants.VMCPU)],
                [stackone.constants.MEM,_(stackone.constants.MEM)]
               ];
    var type_combo=getMetricCombo(null,null,null,null,null,storelst); 
    type_combo.on('select',function(field,rec,index){
        redrawChart(stackone.constants.DOMAIN,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'vm_chart'+node_id,true,panel1_1,null,avg_fdate,avg_tdate);
        label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
    });

//    var avg_fdate1="",avg_tdate1="";
//    var avg_button1=new Ext.Button({
//        icon: '/icons/date.png', // icons can also be specified inline
//        cls: 'x-btn-icon',
//        tooltip: {
//            text:'<b>Show Average</b><br/>'
//        },
//        handler:function(){
//            var avg1=new CustomPeriodUI(_("Show Average"),fdate1,tdate1,selperiod1);
//            var avg_window1 = avg1.getWindow();
//            var btn= new Ext.Button({
//                text: _('OK'),
//                listeners: {
//                    click: function(btn) {
//                        if(avg1.validate()){
//                            avg_window1.hide();
//                            avg_fdate1=avg1.fromTime();
//                            avg_tdate1=avg1.toTime();
//                            var label=formatDate(new Date(avg_fdate1))+" - "+formatDate(new Date(avg_tdate1));
//                            var btnEl = avg_button1.getEl().child(avg_button1.buttonSelector);
//                            var tgt = Ext.QuickTips.getQuickTip().targets[btnEl.id];
//                            tgt.text = '<b>Show Average</b><br/>'+label;
//                            redrawChart(stackone.constants.DOMAIN,stackone.constants.MEM,node_id,node.text,
//                                period_combo.getValue(),fdate,tdate,'vm_memory_chart'+node_id,true,panel1_11,null,avg_fdate1,avg_tdate1);
//                        }
//                    }
//                }
//            });
//            avg_window1.addButton(btn);
//            avg_window1.show();
//
//        }
//    });
//
//    var period_combo1=getPeriodCombo();
//    var fdate1="",tdate1="",selperiod1=stackone.constants.HRS12;
//    period_combo1.on('select',function(field,rec,index){
//        if(field.getValue() ==stackone.constants.CUSTOM){
//            var cust1=new CustomPeriodUI(_("Select Period for Metric Utilization"),fdate1,tdate1,selperiod1);
//            var cust_window1 = cust1.getWindow();
//            var custom_btn1= new Ext.Button({
//                text: _('OK'),
//                listeners: {
//                    click: function(btn) {
//                        if(cust1.validate()){
//                            cust_window1.hide();
//                            fdate1=cust1.fromTime();
//                            tdate1=cust1.toTime();
//                            redrawChart(stackone.constants.DOMAIN,stackone.constants.MEM,node_id,node.text,
//                                period_combo1.getValue(),fdate1,tdate1,'vm_memory_chart'+node_id,true,panel1_11,null,avg_fdate,avg_tdate);
//
//                            label1_2.setText(getChartHdrMsg(node.text,period_combo1.getRawValue(),'Memory'),false);
//                        }
//                    }
//                }
//            });
//            cust_window1.addButton(custom_btn1);
//            cust_window1.show();
//        }else{
//            selperiod1=period_combo1.getValue();
//            fdate1="",tdate1="";
//            redrawChart(stackone.constants.DOMAIN,stackone.constants.MEM,node_id,node.text,
//                            period_combo1.getValue(),fdate1,tdate1,'vm_memory_chart'+node_id,true,panel1_11,null,avg_fdate,avg_tdate);
//            label1_2.setText(getChartHdrMsg(node.text,period_combo1.getRawValue(),'Memory'),false);
//        }
//    });

	
    var vm_grid=vm_info_grid(node_id);
//    var vm_gridext=vm_info_gridext(node_id);
//    var vm_strge_grid=vm_storage_grid(node_id);
//    var vm_ntw_grid=vm_nw_grid(node_id);

    var panel1 = new Ext.Panel({
        height:500,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column'
//        bodyStyle:'padding-top:5px;padding-left:5px;'
    });
    var panel2 = new Ext.Panel({
        height:250,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column',
        bodyStyle:'padding-top:7px;padding-left:5px;'
    });

    var label_summ=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_task'
    });
    var panel1_0 = new Ext.Panel({
        height:500,
        width:'30%',
        border:false,
        bodyBorder:false
        ,layout:'fit'
    });
    var panel1_1 = new Ext.Panel({
        height:240,
       // width:'69%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        ,tbar:[' ',label1_1,{xtype:'tbfill'},avg_button,'-',period_combo,'-',type_combo]
    });  
    var label2_0=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("可用性")+'<br/></div>'
    });
    var panel2_0 = new Ext.Panel({
        height:'100%',
        width:'30%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        ,layout:'fit'

    });
    var panel2_1 = new Ext.Panel({
        height:500,
        width:'69%',
        border:false,
        bodyBorder:false
        //,layout:'fit'
    });
//     var panel1_11 = new Ext.Panel({
//        height:245,
//        //width:'35%',
//        border:false,
//        cls: 'whitebackground',
//        bodyStyle:'padding-top:10px;',
//        bodyBorder:false
//        ,tbar:[' ',label1_2,{xtype:'tbfill'}]
//    });

    var panel1_11=display_tasks(node_id,node);

    var dummy_panel1 = new Ext.Panel({
        width:'1%',
        border:true,
        html:'&nbsp;',
        bodyBorder:false
    });
    var dummy_panel2 = new Ext.Panel({
        height:10,
        border:true,
        html:'&nbsp;',
        bodyBorder:false
    });
    
    panel1_0.add(vm_grid);
    //panel1_1.add(chart_panel);

    panel1.add(panel1_0);
    panel1.add(dummy_panel1);
    panel2_1.add(panel1_1);
//    panel1_11.add(vm_life_cycle)dummy_panel2
    panel2_1.add(dummy_panel2)
    panel2_1.add(panel1_11)
    panel1.add(panel2_1)
  //panel1.add(panel1_1);

//    panel1.add(vm_avail_pie);
    redrawChart(stackone.constants.DOMAIN,stackone.constants.CPU,node_id,node.text,
                    stackone.constants.HRS12,fdate,tdate,'vm_cpu_chart'+node_id,true,panel1_1,null,avg_fdate,avg_tdate);

//    redrawChart(stackone.constants.DOMAIN,stackone.constants.MEM,node_id,node.text,
//                    stackone.constants.HRS12,fdate1,tdate1,'vm_memory_chart'+node_id,true,panel1_11,null,avg_fdate1,avg_tdate1);
//    storage_panel.add(vm_strge_grid);
//    nw_panel.add(vm_ntw_grid);
//
//    panel4.add(storage_panel);
//    panel4.add(dummy_panel4);
//    panel4.add(nw_panel);
    var topPanel = new Ext.Panel({
        //title:format(_("Information for {0}"),node.text),
        collapsible:false,
        height:'100%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false
        ,bodyStyle:'padding-right:5px;',
        items:[panel1]
    });

//    var bottomPanel = new Ext.Panel({
//        title:"Shared Information",
//        collapsible:true,
//        height:'50%',
//        width:'100%',
//        border:false,
//        cls:'headercolor',
//        bodyBorder:false,
//        items:[panel4]
//    });

    var vm_homepanel = new Ext.Panel({
        height:'100%',
        items:[topPanel]
        ,bodyStyle:'padding-left:10px;padding-right:5px;padding-top:10px;'
    });

    mainpanel.add(vm_homepanel);
    vm_homepanel.doLayout();
    mainpanel.doLayout();
    centerPanel.setActiveTab(mainpanel);

}

function vm_info_grid(node_id){
    var vm_info_store =new Ext.data.JsonStore({
        url: "/dashboard/vm_info?type=VM_INFO",
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
    vm_info_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_task'
    });

    var vm_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: false,
        //autoHeight:true,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 230,
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
            {header: "", width: 130, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:NewUIMakeUP},
            {header: "", width: 120, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_info_store
        ,tbar:[label_strge]
    });

    return vm_grid;
}

/**
 * 虚拟机-入门面板
 * 
 * @param {}
 *            mainpanel
 * @param {}
 *            node_id
 * @param {}
 *            node
 */
function vm_domainStarter_page(mainpanel, node_id, node) {
	if (mainpanel.items)
		mainpanel.removeAll(true);
	/*var topHtml = '';
	topHtml += '<div class="toolbar_hdg" >';
	topHtml += '</div>';*/
	var topHtml = '';
	topHtml += '<div class="vm-starter-top">';
	topHtml += '	<div class="vm-starter-top-text">';
	topHtml += _("什么是虚拟机？");
	topHtml += '<br/>';
	topHtml += '<br/>';
	topHtml += _("虚拟机（VM）是支持多操作系统，并行运行在单个物理服务器上的一种系统，能够提供更加有效的底层硬件使用。与物理机一样，虚拟机上可以运行不同的操作系统和应用程序。虚拟机上安装的操作系统被称为客户机操作系统。");
	topHtml += '<br/>';
	topHtml += '<br/>';
	topHtml += _("因为每台虚拟机都是一个隔离的计算环境，所以您可以利用虚拟机做为测试环境或桌面环境，也可以用来整合物理服务器的应用程序。");
	topHtml += '	</div>';
	topHtml += '	<div class="vm-starter-top-img">';
	topHtml += '	</div>';
	topHtml += '</div>';
	
	var leftHtml = "";
	leftHtml += "<div class='vm-starter-left-text'>";
	leftHtml += '<div>基本任务</div>';
	leftHtml += "<a href='#' onclick=javascript:vm_domainStarter_page_startVm();>开机</a><br/>";
	leftHtml += "<a href='#' onclick=javascript:vm_domainStarter_page_shutdownVm();>关机</a><br/>";
	leftHtml += "<a href='#' onclick=javascript:vm_domainStarter_page_rebootVm();>重启</a><br/>";
	leftHtml += "</div>";
	
	var rightHtml = '';
	rightHtml += '<div class="vm-starter-right-text" >';
	rightHtml += _("了解如何在虚拟机上安装操作系统？");
	rightHtml += '<br/><br/>';
	rightHtml += _("新虚拟机就像刚从市场上采购回来的裸机。在使用之前，需要先安装操作系统，虚拟机上的操作系统被称为客户机操作系统。");
	rightHtml += '<br/>';
	rightHtml += '<br/>';
	rightHtml += _("在虚拟机上安装操作系统与在物理机上安装操作系统的方法基本相同。您可以选择用CD-ROM或ISO映像安装客户机操作系统，安装完成后，您就可以像使用物理机一样来操作虚拟机了。");
	rightHtml += '</div>'
	
	var topPanel = new Ext.Panel({
		height : 300,
		width : '100%',
		region : 'north',
		border: false,
		//frame: true,
		bodyStyle : 'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
		html : topHtml
	});
	var leftPanel = new Ext.Panel({
		border: false,
		frame: true,
		height : '60%',
		width : '40%',
		region : 'west',
		bodyStyle : 'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
		html : leftHtml
	});
	var rightPanel = new Ext.Panel({
		border: false,
		frame: true,
		height : '60%',
		width : '60%',
		region : 'center',
		bodyStyle : 'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
		html : rightHtml
	});

	var vmStarterPanel = new Ext.Panel({
		border: false,
		frame: true,
		width : "100%",
		height : "100%",
		layout : 'border',
		border:false,//lbz更改：加一句
		items : [topPanel, leftPanel, rightPanel]
		
	});
	mainpanel.add(vmStarterPanel);
	vmStarterPanel.doLayout();
	mainpanel.doLayout();
}

function vm_domainStarter_page_startVm(){
	var item = {};
	item.id = 'start';
	item.text = '开机';
	item.tooltip = '开机';
	vm_action(leftnav_treePanel.getSelectionModel().getSelectedNode(),item);	
}

function vm_domainStarter_page_shutdownVm() {
	var item = {};
	item.id = 'shutdown';
	item.text = '关机';
	item.tooltip = '关机';
	vm_action(leftnav_treePanel.getSelectionModel().getSelectedNode(), item);
}

function vm_domainStarter_page_rebootVm() {
	var item = {};
	item.id = 'reboot';
	item.text = '重启';
	item.tooltip = '重启';
	vm_action(leftnav_treePanel.getSelectionModel().getSelectedNode(), item);
}

function vm_storage_grid(node_id){

    var vm_storage_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("类型"),
        width:50,
        dataIndex: 'type',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("位置"),
        width: 150,
        sortable:true,
        dataIndex: 'filename'
    },
    {
        header: _("大小"),
        width: 50,
        sortable:true,
        dataIndex: 'size',
        align: 'right'
    },
    {
        header: _("设备"),
        width: 50,
        dataIndex: 'device'
    },
    {
        header: _("模式"),
        width: 35,
        dataIndex: 'mode'
    },
    {
        header: _("共享"),
        width: 45,
        dataIndex: 'shared'
    }]);

    var vm_storage_store = new Ext.data.JsonStore({
        url: "/dashboard/vm_info?type=STORAGE_INFO",
        root: 'info',
        fields: ['type','filename','device','mode','shared','size'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    vm_storage_store.load({
        params:{
            node_id:node_id
        }
    });

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("存储信息")+'</div>'
    });
	var vm_storage_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: vm_storage_store,
        colModel:vm_storage_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
        autoExpandMax:300,
        autoExpandMin:150,
        border:true,
        enableHdMenu:false,
        autoScroll:true,
        id:'vm_storage_summary_grid',
        width:'100%',
        //autoExpandColumn:1,
        height:220
        ,tbar:[label_strge]
    });

	return vm_storage_grid;

}

function vm_nw_grid(node_id){

    var vm_nw_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width: 150,
        dataIndex: 'name',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("详情"),
        width: 110,
        sortable:true,
        dataIndex: 'description'
    },
    {
        header: _("MAC"),
        width: 170,
        dataIndex: 'mac'
    } ]);


    var vm_nw_store = new Ext.data.JsonStore({
        url: "/dashboard/vm_info?type=NW_INFO",
        root: 'info',
        fields: ['name','description','mac'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    vm_nw_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_nw=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("网络信息")+'</div>'
    });
	var vm_nw_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: vm_nw_store,
        colModel:vm_nw_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
        autoExpandMax:300,
        border:true,
        enableHdMenu:false,
        autoScroll:true,
        id:'vm_nw_summary_grid',
        width:'100%',
        //autoExpandColumn:1,
        height:220
        ,tbar:[label_nw]
    });

	return vm_nw_grid;

}

function vm_availability_chart(node_id,node){
    var vm_avail_store = new Ext.data.Store({
        url: "/dashboard/vm_availability?node_id="+node_id,
        reader: new Ext.data.JsonReader({
            root: 'info',
            fields: ['label', 'value']
        })
    });

    var vm_avail_pie = new Ext.ux.PieFlot({
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
            position: "ne",
            margin: [0,0],
            backgroundOpacity: 0
        },
        series: []
    });

    vm_avail_store.on('load',
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
        vm_avail_pie
    );

    vm_avail_store.load();

    return vm_avail_pie;
}

//function vm_storage_chart(node_id,node){
//    var vm_storage_store = new Ext.data.Store({
//        url: "/dashboard/vm_storage?node_id="+node_id,
//        reader: new Ext.data.JsonReader({
//            root: 'info',
//            fields: ['label', 'value']
//        })
//    });
//
//    var vm_storage_pie = new Ext.ux.PieFlot({
//        pies: {
//            show: true,
//            autoScale: true,
//            fillOpacity: 1,
//            labelFormatter: function(label, value, percent, textValue, pie, serie, options) {
//                if(value == 0)
//                {
//                    return '';
//                }
//                return textValue + '% ('+value+"GB)";
//            },
//            labelStyle: 'font-size:11px; '
//
//        },
//        width:'100%',
//        height:'100%',
//        legend: {
//            show: true,
//            position: "ne",
//            margin: [0,0],
//            backgroundOpacity: 0
//        },
//        series: []
//    });
//
//    vm_storage_store.on('load',
//        function(store, records, options) {
//            try{
//                var series = this.createSeries(store, 'label', 'value');
//                this.plot(series);
//                this.baseRanges = this.getRanges();
//            }catch(e)
//            {
//                Ext.MessageBox.alert(_("Error"),e);
//            }
//
//        },
//        vm_storage_pie
//    );
//
//    vm_storage_store.load();
//
//    return vm_storage_pie;
//}

function vm_info_gridext(node_id){
    var vm_info_store =new Ext.data.JsonStore({
        url: "/dashboard/vm_info?type=VM_INFO_EXT",
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
    vm_info_store.load({
        params:{
            node_id:node_id
        }
    });

    var vm_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        cls:'hideheader padded',
        width: '100%',
        height: 210,
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
            {header: "", width: 110, sortable: false, css:'font-weight:bold;',dataIndex: 'name'},
            {header: "", width: 160, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_info_store
//        ,tbar:[label_strge]
    });

    return vm_grid;
}

function vm_config_page(configPanel,node_id,node){
    
    var UIContext = {"context":stackone.constants.DB_DASHBOARD, "path":stackone.constants.DB_TABS_CONFIG}

    if(configPanel.items)
        configPanel.removeAll(true);
    var vm_strge_grid=vm_storage_grid(node_id);
    var vm_ntw_grid=vm_nw_grid(node_id);

    var row_panels = [];
    var row_dummy_panels = [];
    var row_inner_panels = [];
    var panel_grids = []

    var panel1 = new Ext.Panel({
        width:'100%',
        height: '100%',
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

    row_panels.push(panel1)
    row_panels.push(panel2)
    row_panels.push(panel3)
    row_panels.push(panel4)

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

    row_dummy_panels.push(dummy_panel1);
    row_dummy_panels.push(dummy_panel2);
    row_dummy_panels.push(dummy_panel3);
    row_dummy_panels.push(dummy_panel4);

    var template_info=get_templateinfo(node_id);
    var general_info=get_generalinfo(node_id);
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

    var row_inner_panels_1 = [panel1_1, panel1_2];

    panel_grids.push([general_info, stackone.constants.DB_GENERAL]);
    panel_grids.push([template_info, stackone.constants.DB_TEMPLATE]);

    var bootparam_info=get_bootparaminfo(node_id);
    var advanced_info=get_advancedinfo(node_id);

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

    var row_inner_panels_2 = [panel2_1, panel2_2];

    var usb_info=get_usbdeviceinfo(node_id);
    var display_info=get_displayinfo(node_id)
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

    var row_inner_panels_3 = [panel3_1, panel3_2];

    panel_grids.push([display_info, stackone.constants.DB_DISPLAY]);
    panel_grids.push([usb_info, stackone.constants.DB_USB]);
    panel_grids.push([bootparam_info, stackone.constants.DB_BOOT]);
    panel_grids.push([advanced_info, stackone.constants.DB_ADVANCED]);

    var storage_panel=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var nw_panel=new Ext.Panel({
        width:'49.5%',
        height: '100%',
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });

    var row_inner_panels_4 = [storage_panel, nw_panel];

    panel_grids.push([vm_strge_grid, stackone.constants.DB_STORAGE]);
    panel_grids.push([vm_ntw_grid, stackone.constants.DB_NETWORK]);

    row_inner_panels.push(row_inner_panels_1);
    row_inner_panels.push(row_inner_panels_2);
    row_inner_panels.push(row_inner_panels_3);
    row_inner_panels.push(row_inner_panels_4);

    /// Add Grids to Panels after checking whether it is enabled ////
    var final_row_panels = [];
    var processed_grid_panel_cnt = 0;
    var processed_row_inner_panel_cnt = 0;
    for(var i=0; i < row_panels.length; i++){
        var row_panel = row_panels[i];
        for(var j=processed_row_inner_panel_cnt; j < row_inner_panels.length; j++){
//            alert("--j---");
            var row_inner_sub_panels = row_inner_panels[j];//2 items
            processed_row_inner_panel_cnt += 1;
            for(var k=0; k < row_inner_sub_panels.length; k++){
                var inner_panel = row_inner_sub_panels[k]
                for(var p=processed_grid_panel_cnt; p < panel_grids.length; p++){
//                    alert("--p---");
                    var panel_grid = panel_grids[p][0];
                    var panel_grid_type = panel_grids[p][1];
                    processed_grid_panel_cnt += 1;
                    /// Check whether Grid is enabled for Virtual Machine///
                    if (stackone.UIHelper.IsEnabled(panel_grid_type, UIContext))
                        {
                            inner_panel.add(panel_grid);
                            break
                        }
                }
            }

            for(var r=0; r < row_inner_sub_panels.length; r++){
                row_panel.add(row_inner_sub_panels[r]);                
                if (r == 0){
                        row_panel.add(row_dummy_panels[i]);
                    }
                }
            break;
            }
       
       final_row_panels.push(row_panel);
    }


    var bottomPanel = new Ext.Panel({
//        collapsible:true,
        height:'100%',
        width:'100%',
        border:false,
//        cls:'headercolor',
        bodyBorder:false,
        bodyStyle:'padding-left:10px;padding-right:5px;',
//        items:[panel1,panel3,panel2,panel4]
    });

//    alert("--final_row_panels---"+final_row_panels);
    for(var i=0; i < final_row_panels.length; i++){
        bottomPanel.add(final_row_panels[i]);
    }

    configPanel.add(bottomPanel);
    bottomPanel.doLayout();
    configPanel.doLayout();
}

function get_generalinfo(node_id){

    var vm_general_store =new Ext.data.JsonStore({
//        url: "vm_general_info",
        url: "/dashboard/vm_info?type=GENERAL_INFO",
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
    vm_general_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_general=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("常规")+'</div>', 
        id:'label_general'
    });

    var general_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        //title:_("General"),
        cls:'hideheader  ',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        width: '100%',
        height: 150,
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
            {header: "", width: 150, sortable: false, css:'font-weight:bold;color:#414141;',dataIndex: 'name',renderer:NewUIMakeUP},
            {header: "", width: 350, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_general_store
        ,tbar:[label_general]
    });

    return general_grid;

}
function get_templateinfo(node_id){
    var vm_template_store =new Ext.data.JsonStore({
        url: "/dashboard/vm_info?type=TEMPLATE_INFO",
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
    vm_template_store.load({
        params:{
            node_id:node_id
        }
    });

   var label_template=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("模板")+'</div>',
       id:'label_template'
   });

    var template_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        //title:_("Template"),
        cls:'hideheader ',
        width: '100%',
        height: 150,
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
            {header: "", width: 150, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:NewUIMakeUP},
            {header: "", width: 350, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_template_store
        ,tbar:[label_template]
    });

    return template_grid;
}
function get_bootparaminfo(node_id){

    var vm_bootparam_store =new Ext.data.JsonStore({
//        url: "vm_bootparam_info",
        url: "/dashboard/vm_info?type=BOOT_PARAM",
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
    vm_bootparam_store.load({
        params:{
            node_id:node_id
        }
    });

   var label_bp=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("启动参数")+'</div>',
       id:'label_bp'
   });

    var bootparams_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        //title:_("Boot Parameters"),
        cls:'hideheader',
        width: '100%',
        height: 260,
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
            {header: "", width: 150, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:NewUIMakeUP},
            {header: "", width: 350, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_bootparam_store
        ,tbar:[label_bp]
    });

    return bootparams_grid;

}
function get_displayinfo(node_id){

    var vm_display_store =new Ext.data.JsonStore({
//        url: "vm_bootparam_info",
        url: "/dashboard/vm_info?type=DISPLAY",
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
    vm_display_store.load({
        params:{
            node_id:node_id
        }
    });
   var label_display=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("显示配置")+'</div>',
       id:'label_general'
   });

    var display_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        //title:_("Display Configuration"),
        cls:'hideheader',
        width: '100%',
        height: 130,
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
            {header: "", width: 150, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:NewUIMakeUP},
            {header: "", width: 350, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_display_store
        ,tbar:[label_display]
    });

    return display_grid;

}
function get_usbdeviceinfo(node_id){

    var vm_usbdevice_store =new Ext.data.JsonStore({
//        url: "vm_bootparam_info",
        url: "/dashboard/vm_info?type=USB_DEVICE",
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
    vm_usbdevice_store.load({
        params:{
            node_id:node_id
        }
    });
   
    var label_usb=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("USB配置")+'</div>',
       id:'label_usb'
    });

    var display_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        //title:_("USB Configuration"),
        cls:'hideheader ',
        width: '100%',
        height: 130,
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
            {header: "", width: 150, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 350, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_usbdevice_store
        ,tbar:[label_usb]
    });

    return display_grid;

}
function get_advancedinfo(node_id){
       var adv_store =new Ext.data.JsonStore({
//        url: "vm_bootparam_info",
        url: "/dashboard/vm_info?type=ADVANCED",
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
    adv_store.load({
        params:{
            node_id:node_id
        }
    });

   var label_adv=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("高级选项")+'</div>',
       id:'label_adv'
   });

    var adv_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        //title:_("Advanced"),
        cls:'hideheader',
        width: '100%',
        height: 260,
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
            {header: "", width: 150, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:NewUIMakeUP},
            {header: "", width: 350, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:adv_store
        ,tbar:[label_adv]
    });

    return adv_grid;

}

function VMBackupResultGrid(node_id){
    var label_task=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("备份")+'</div>',
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
        dataIndex: 'vm_id',
        hidden:true
    },
    {
        header: _("任务编号"),
        width: 80,
        dataIndex: 'result_id',
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
            //  if(value =='Failed' || value =='Succeeded')
            //{
                params.attr='ext:qtip="Show Message"' +
                    'style="background-image:url(icons/information.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            //}
            return value;
        }
    },
    {
        header: _("还原"),
        width: 50,
        dataIndex: 'restore',
        align: 'center',
        renderer: showBackupResultDetailLink
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
        width: 250,
        dataIndex: 'location',
        sortable:true
    }
   
   ]);

/*
function is_vm_deleted(def_type, def_ids){
    if(def_ids == ""){
        Ext.MessageBox.alert("Warning","Please select storage");
        return;
    }

    var url="/restore/is_vm_deleted?" + sSiteId + op_level + sGroupId + "&def_type=" + def_type + "&def_ids=" + def_ids; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
//                 closeWindow(windowid);
//                 reloadStorageDefList();
//                 Ext.MessageBox.alert("Success","Virtual Machine is deleted");
            }else{
                Ext.MessageBox.alert("Failure",response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( "Failure " , xhr.statusText);
        }
    });
}
*/

    function showBackupResultDetailLink(data,cellmd,record,row,col,store) {
            var returnVal;
            var status= record.get("status");
            if(status == 'Success')
            
            {
                
                returnVal = '<a href="#"><img title="Restore Virtual Machines" src="icons/small_snapshot.png "/></a>';
            }
    
            return returnVal;       
    }


/*
function restore_function(node_id) {
    
   alert(node_id);
    

}*/

    var task_store = new Ext.data.JsonStore({
        url: 'backup/get_vm_backup_task_result?node_id='+node_id,
        root: 'rows',
        fields: ['taskid','result_id','vm_id','name','location', 'backup_size','starttime', 'endtime','status', 'errmsg', 'restore'],
        sortInfo: {
            field: 'starttime',
            direction: 'DESC' 
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });  

    task_store.load();      

    
    
     var backupresult_info_grid = new Ext.grid.GridPanel({
//         disableSelection:true,
        store: task_store,
        colModel:task_columnModel,
        stripeRows: true,
        frame:false,
        //autoExpandColumn:3,
        //autoExpandMax:300,
        border:true,
        enableHdMenu:true,
        autoScroll:true,
        id:'backupresult_info_grid',
        
        width:'100%',
        //autoExpandColumn:1,
        height:350,
        tbar:[label_task],
        listeners: {
            rowcontextmenu :function(grid,rowIndex,e) {
                var record = grid.getStore().getAt(rowIndex);
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            cellclick: function(grid ,rowIndex,columnIndex,e,b) {
                //alert(rowIndex);
//alert(columnIndex);

                var record = grid.getStore().getAt(rowIndex);
                if (columnIndex == 5)
                {
                    //if(record.get('status') =='Failed'||record.get('status') =='Succeeded'){
                        var err=record.get('errmsg');
                        showTaskMessage('Message',err);
                    //}
                }
                if (columnIndex == 6)
                {
                    if(record.get('status') =='Success'){                        
                        var backup_result_id =record.get('restore');
                        //showTaskMessage('Message',err);

                        Ext.MessageBox.confirm(_("确认"),"确定要还原备份吗?",function(id){
                            if(id=='yes'){
                                RestoreBackup("", node_id, "", record.get('taskid'), false);
                            }
                        });
                    }
                }
                
            }
        }



    });
    
    return backupresult_info_grid; 
}

/**
 * 虚拟机-控制台面板
 * 
 * @param {}
 *            mainpanel
 * @param {}
 *            node_id
 * @param {}
 *            node
 */
function vm_domainConsole_page(mainpanel, node_id, node) {
	if (mainpanel.items) mainpanel.removeAll(true);
	var dom = node;
	node = node.parentNode;
	var url = 'get_vnc_info?node_id=' + node.attributes.id + '&dom_id=' + dom.attributes.id;
	var ajaxReq = ajaxRequest(url, 0, "GET", true);
	if (dom.getUI().getIconEl() != null) {
		var iconClass = dom.getUI().getIconEl().className;
		dom.getUI().getIconEl().className = "x-tree-node-icon loading_icon";
	}
	ajaxReq.request({
		success : function(xhr) {
			if (dom.getUI().getIconEl() != null) {
				dom.getUI().getIconEl().className = iconClass;
			}
			var response = Ext.util.JSON.decode(xhr.responseText);
			if (response.success) {

				var host = response.vnc.hostname;
				var port = response.vnc.port;
				var height = response.vnc.height;
				var width = response.vnc.height;
				var new_window = response.vnc.new_window;
				var show_control = response.vnc.show_control;
				var encoding = response.vnc.encoding;
				var restricted_colours = response.vnc.restricted_colours;
				var offer_relogin = response.vnc.offer_relogin;

				if (port == '00') {
					Ext.MessageBox.alert(_("消息"), _("虚拟机没有运行."))
					return;
				}

				var applet = '<applet id="vmconsolepanel" code="VncViewer.class" archive="/jar/SVncViewer.jar"'
						+ 'width="'
						+ "100%"
						+ '" height="'
						+ "100%"
						+ '">'
						+ '<param name="HOST" value="'
						+ host
						+ '">'
						+ '<param name="PORT" value="'
						+ port
						+ '">'
						+ '<param name="Open new window" value="'
						+ 'No'
						+ '">'
						+ '<param name="Show controls" value="'
						+ show_control
						+ '">'
						+ '<param name="Encoding" value="'
						+ encoding
						+ '">'
						+ '<param name="Restricted colors" value="'
						+ restricted_colours
						+ '">'
						+ '<param name="Offer relogin" value="'
						+ offer_relogin
						+ '">' + '</applet>';
					
					var consolePanel = new Ext.Panel({
						html: applet,
						width : "100%",
						height : "100%",
						border:false
					});
					mainpanel.add(consolePanel);
					consolePanel.doLayout();
					mainpanel.doLayout();
			} else {
				Ext.MessageBox.alert(_("失败"), response.msg);
			}
		},
		failure : function(xhr) {
			if (dom.getUI().getIconEl() != null) {
				dom.getUI().getIconEl().className = iconClass;
			}
			Ext.MessageBox.alert(_("失败"), xhr.statusText);
		}
	});
}


function VMRestoreResultGrid(node_id){
    var label_task=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("还原")+'</div>',
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
            //  if(value =='Failed' || value =='Succeeded')
            //{
                params.attr='ext:qtip="Show Message"' +
                    'style="background-image:url(icons/information.png) '+
                    '!important; background-position: right;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            //}
            return value;
        }
    },
    {
        header: _("还原"),
        width: 50,
        dataIndex: 'restore',
        align: 'center',
        renderer: showBackupResultDetailLink,
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
        width: 250,
        dataIndex: 'location',
        sortable:true
    }
   
   ]);
   


/*
function is_vm_deleted(def_type, def_ids){
    if(def_ids == ""){
        Ext.MessageBox.alert("Warning","Please select storage");
        return;
    }

    var url="/restore/is_vm_deleted?" + sSiteId + op_level + sGroupId + "&def_type=" + def_type + "&def_ids=" + def_ids; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
//                 closeWindow(windowid);
//                 reloadStorageDefList();
//                 Ext.MessageBox.alert("Success","Virtual Machine is deleted");
            }else{
                Ext.MessageBox.alert("Failure",response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( "Failure " , xhr.statusText);
        }
    });
}
*/

    function showBackupResultDetailLink(data,cellmd,record,row,col,store) {
            var returnVal;
            var status= record.get("status");
            if(status == 'Success')
            
            {
                
                returnVal = '<a href="#"><img title="Restore Virtual Machines" src="icons/small_snapshot.png "/></a>';
            }
    
            return returnVal;       
    }


/*
function restore_function(node_id) {
    
   alert(node_id);
    

}*/

    var task_store = new Ext.data.JsonStore({
        url: 'restore/get_vm_restore_task_result?node_id='+node_id,
        root: 'rows',
        fields: ['taskid','name','location', 'backup_size','starttime', 'endtime','status', 'errmsg', 'restore'],
        sortInfo: {
            field: 'starttime',
            direction: 'DESC' 
        },
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });  

    task_store.load();      

    
    
     var backupresult_info_grid = new Ext.grid.GridPanel({
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
        id:'backupresult_info_grid',
        
        width:'100%',
        //autoExpandColumn:1,
        height:350,
        tbar:[label_task],
        listeners: {
            cellclick: function(grid ,rowIndex,columnIndex,e,b) {
                //alert(rowIndex);
//alert(columnIndex);

                var record = grid.getStore().getAt(rowIndex);
                if (columnIndex == 5)
                {
                    //if(record.get('status') =='Failed'||record.get('status') =='Succeeded'){
                        var err=record.get('errmsg');
                        showTaskMessage('Message',err);
                    //}
                }
                if (columnIndex == 6)
                {
                    if(record.get('status') =='Success'){                        
                        var backup_result_id =record.get('restore');
                        //showTaskMessage('Message',err);

                        Ext.MessageBox.confirm(_("确认"),"确定要还原备份吗?",function(id){
                            if(id=='yes'){
                                RestoreBackup("", node_id, "", record.get('taskid'), false);
                            }
                        });
                    }
                }
                
            }
        }



    });
    
    return backupresult_info_grid; 
}

function vm_backup_history_page(backup_history_Panel,node_id,node){

var panel1 = new Ext.Panel({
        width:'100%',
        height: 192,
        border:false,
        bodyBorder:false,
       // bodyStyle:'padding-top:0px;padding-right:5px;',
        layout:'column'
    });
   
    var panel2 = new Ext.Panel({
        width:'60%',
        height: 200,
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

    node_type = node.attributes.nodetype;

    panel1_1.add(VM_backup_summary_grid(node_id, node_type));
    panel1_2.add(SPBackupTaskGrid(node));
    panel1.add(panel1_1);
    panel1.add(dummy_panel1);
    panel1.add(panel1_2);
    //panel2.add(VMBackupResultGrid(node_id));



//      var panel6 = new Ext.Panel({
//         width:'100%',
//         height: 270,
//         border:false,
//         bodyBorder:false,
//        // bodyStyle:'padding-top:0px;padding-right:5px;',
//         layout:'column'
//     });
//    
//   panel6.add(SPBackupTaskGrid(node));
// 
    var panel7 = new Ext.Panel({
        width:'100%',
        height: 365,
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
    panel7.add(VMBackupResultGrid(node_id));
    panel8.add(VMRestoreResultGrid(node_id));

    if(backup_history_Panel.items)
        backup_history_Panel.removeAll(true);
    
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
        items:[panel1, panel7, panel8]
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

function VM_backup_summary_grid(node_id, node_type){
    var vm_backup_summary_store =new Ext.data.JsonStore({
        url: "/backup/vm_backup_summary?node_id="+ node_id,
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
    vm_backup_summary_store.load();

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_strge'
    });

    var vm_backup_summary_grid = new Ext.grid.GridPanel({       
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
                //if (row == 1)   
                //{ 
                    
                //     var num_nonbackup_vm =record.get('value');  
                //     if (num_nonbackup_vm != "0"){                    
                //        var fn = "shown_nonbackup_vm_window('" + node_id + "','" +  node_type + "')";                   
                //        returnVal = '<a href="#" onClick=' + fn + '>' + value + '</a>';
                //    }
                //}
            
                return returnVal;
            }}    
        ],
        store:vm_backup_summary_store,
        tbar:[label_strge]
    });

    return vm_backup_summary_grid
}

function display_tasks(node_id,node){
     var vmtask_grid=draw_grid(node_id,node," 虚拟机任务",248);
     return vmtask_grid;
}

function format_date(value,params,record){
        if (value==null || value==""){
            return value;
        }
        var date =new Date(value);

//        var myDate = String(new Date(value)).split("GMT");

        var str_date=date.getFullYear()+"-"+
            format_date_value(String(parseInt(date.getMonth()+1)))+"-"+
            format_date_value(String(date.getDate()))+
            " "+format_date_value(String(date.getHours()))+":"+
            format_date_value(String(date.getMinutes()))+":"+
            format_date_value(String(date.getSeconds()));
//        return myDate[0].substr(0,myDate[0].length-4);
        return str_date;

}

function delete_schedule(task_grid, rowIndex,task_type){

    var task_id=task_grid.getStore().getAt(rowIndex).get("task_id");
    var url="/node/delete_task?task_id="+task_id;
    var ajaxReq=ajaxRequest(url,0,"GET",true);

    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
                   var response=Ext.util.JSON.decode(xhr.responseText);
                   if(response.success){
                       task_grid.getStore().load({
                             params:{
                                display_type:task_type
                            }
                       })

                    }
                },
                failure: function(xhr){
                    Ext.MessageBox.alert( _("Failure"), xhr.statusText);
                }
            });


}

function edit_schedule(task_grid, rowIndex,task_name,task_type){

    var start_time=task_grid.getStore().getAt(rowIndex).get("start_time");
    var st_date=new Date(start_time);
    var month=format_date_value(String(st_date.getMonth()+1));
    var day=format_date_value(String(st_date.getDate()));

    var date_toset=month+"/"+day+"/"+st_date.getFullYear();

    var hours=format_date_value(String(st_date.getHours()));
    var minutes=format_date_value(String(st_date.getMinutes()));

    var time_toset=hours+":"+minutes;

    var curr_date_value=new Date();
    var month=format_date_value(String(curr_date_value.getMonth()+1));
    var day=format_date_value(String(curr_date_value.getDate()));

    var curr_date=month+"/"+day+"/"+curr_date_value.getFullYear();
//    var date=new Date();
//    var hrs=date.getHours();
//    var mins=date.getMinutes();
//       var mod=(mins+5)-(mins%5);
//    var time=hrs+":"+((mod<10)?"0":"")+mod;

    var date_lbl=new Ext.form.Label({
        html:_('日期:')
    });
    var time_lbl=new Ext.form.Label({
        html:_('时间:')
    });
    var date=new Ext.form.DateField({
        fieldLabel: _('日期'),
        hideLabel:true,
        name: 'schdate',
        anchor:'100%',
        minValue:curr_date,
        format:'m/d/Y',
        id: 'schdate',
        value:date_toset,
        width:110
    });

    var schdate=new Ext.Panel({
        height:30,
        border:false,
        width:200,
        labelAlign:'right',
        layout:'table',
        labelSeparator:' ',
        layoutConfig: {columns:2},
        items: [
         {
            width: 70,
            layout:'form',
            border:false,
            items:[date_lbl]
        },
        {
            width: 120,
            layout:'form',
            border:false,
            items:[date]
        }]
    });

    var time=new Ext.form.TimeField({
        fieldLabel: _('时间'),
        hideLabel:true,
        name: 'schtime',
        format:'H:i',
        anchor:'100%',
        id: 'schtime',
        //minValue:'12:00',
        value:time_toset,
        increment:5,
        maxHeight:80,
        width:110
    });

    var schtime=new Ext.Panel({
        height:30,
        border:false,
        width:200,
        labelAlign:'right',
        layout:'table',
        labelSeparator:' ',
        layoutConfig: {columns:2},
        items: [
         {
            width: 70,
            layout:'form',
            border:false,
            items:[time_lbl]
        },
        {
            width: 120,
            layout:'form',
            border:false,
            items:[time]
        }]
    });

    var msg_lbl=new Ext.form.Label({
         html:'<b>'+ _("Change "+task_name+" schedule time:") +'</b><br/><br/>'
     });
    var task_sch = new Ext.FormPanel({
        labelWidth:70,
        frame:true,
        border:0,
        labelAlign:"left" ,
        width:200,
        height:160,
        labelSeparator: ' ',
        items:[msg_lbl,schdate,schtime]
    });
    task_sch.addButton(_("确定"),function(){

        var task_id=task_grid.getStore().getAt(rowIndex).get("task_id");
        var url="/node/edit_task?task_id="+task_id+"&date="+date.getValue()+"&time="+time.getValue();
        var ajaxReq=ajaxRequest(url,0,"GET",true);
        window.close();
        ajaxReq.request({
            success: function(xhr) {//alert(xhr.responseText);
                       var response=Ext.util.JSON.decode(xhr.responseText);
                       if(response.success){
                           task_grid.getStore().load({
                                 params:{
                                    display_type:task_type
                                }
                           })

                        }
                    },
                    failure: function(xhr){
                        Ext.MessageBox.alert( _("Failure"), xhr.statusText);
                    }
                });
   });
    task_sch.addButton(_("取消"),function(){
         window.close();
    });

    var window = new Ext.Window({
        title:_("编辑计划时间"),
        width: 250,
        autoHeight:true,
        minWidth: 300,
        minHeight: 200,
        layout: 'fit',
        plain:true,
        resizable:false,
        modal: true,
        closable:true,
        bodyStyle:'padding:5px;',
        buttonAlign:'center',
        items: [task_sch]
    });
    window.show();
   
}
// function VMBackupTaskGrid(node){
// 
// var vm_id = node.attributes.id;
// alert(node.attributes.nodetype);
// var s_node = node.parentNode;
// var sp_node = s_node.parentNode;
// var sp_id = sp_node.attributes.id;
// 
// var label_task=new Ext.form.Label({
//         html:'<div class="toolbar_hdg">'+_("Backup Tasks")+'</div>',
//         id:'label_task1'
//     });
// 
// var backup_selmodel=new Ext.grid.RowSelectionModel({
//         singleSelect:true
//     });
// 
// var title_edit = new Ext.form.TextField();
// 
//  var backup_columnModel = new Ext.grid.ColumnModel([
//     {
//         header: "Site ID",
//         width: 50,
//         dataIndex: 'backupsetup_id',
//         menuDisabled: false,
//         hidden:true,
//         editor: title_edit,
//         
//     },
//     {
//         header: "Task Name",
//         width: 150,
//         dataIndex: 'taskname',
//         sortable:true,
//         editor: title_edit,
//         id:'taskname'
// 
//     },
//     {
//         header: "Backup Type",
//         width: 150,
//         dataIndex: 'backup_type',
//         sortable:true,
//         editor: title_edit,
//         id:'backup_type'
// 
//     },
//     {
//         header: "Location",
//         width: 150,
//         dataIndex: 'location',
//         sortable:true,
//         editor: title_edit,
//         id:'location'
// 
//     },
//     ]);
// 
//      var backup_store =new Ext.data.JsonStore({
//             //url: "get_backupsetupinfo",
//             url: 'get_vm_backupsetupinfo?sp_id=' +sp_id + '&vm_id='+vm_id,
//             root: 'rows',
//             fields: [ 'backupsetup_id','taskname','backup_type', 'location' ],
//             successProperty:'success',
//             listeners:{
//                 loadexception:function(obj,opts,res,e){
//                     var store_response=Ext.util.JSON.decode(res.responseText);
//                     Ext.MessageBox.alert("Error2",store_response.msg);
//                 }
// 
//             }
//         });
// 
//     backup_store.load();
// 
// 
//     var backup_grid=new Ext.grid.GridPanel({
//         store: backup_store,
//         stripeRows: true,
//         colModel:backup_columnModel,
//         frame:false,
//         selModel:backup_selmodel,
//         height:250,
//         width:'100%',
//         enableHdMenu:false,
//         loadMask:true,
//         id:'backup_grid',
//         layout:'fit',
//         tbar:[label_task],
//         listeners:{
//              rowdblclick:function(grid, rowIndex, e){
//                 backup_edit_button.fireEvent('click',backup_edit_button);
//             }
//         }
//     });
// 
//     return backup_grid; 
// }
