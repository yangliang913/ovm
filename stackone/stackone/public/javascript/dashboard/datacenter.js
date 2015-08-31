/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function data_center_summary_page(mainpanel,node_id,node){
    //node_id='d9a3bd4a-062a-5017-22af-94222763e8b9';
    if(mainpanel.items)
        mainpanel.removeAll(true);

    var label0_1=new Ext.form.Label({
        html:'<div class="toolbar_hdg" >'+_("天")+'<br/></div>'
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
                            redrawChart(stackone.constants.DATA_CENTER,type_combo.getValue(),node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'dc_chart'+node_id,true,panel1_1,stackone.constants.TOP5SERVERS);

                            //label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false,stackone.constants.TOP5SERVERS);
                        }
                    }
                }
            });
            cust_window.addButton(custom_btn);
            cust_window.show();
        }else{
            selperiod=period_combo.getValue();
            fdate="",tdate="";
            redrawChart(stackone.constants.DATA_CENTER,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'dc_chart'+node_id,true,panel1_1,stackone.constants.TOP5SERVERS);
            //label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false,stackone.constants.TOP5SERVERS);
        }
    });

    var type_combo=getMetricCombo();
    type_combo.on('select',function(field,rec,index){
        redrawChart(stackone.constants.DATA_CENTER,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'dc_chart'+node_id,true,panel1_1,stackone.constants.TOP5SERVERS);
        //label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false,stackone.constants.TOP5SERVERS);
    });

    var dt_cntr_vm_grid=data_center_vm_grid(node_id);

    var panel1 = new Ext.Panel({
        height:250,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column',
        bodyStyle:'padding-top:10px;padding-right:5px;'
    });
    var panel1_0 = new Ext.Panel({
        height:245,
        width:'30%',
        border:false,
        bodyBorder:false
        ,layout:'fit'
    });    
    var panel1_1 = new Ext.Panel({
        height:245,
        width:'69%',
        cls: 'whitebackground',
        border:true,
        bodyBorder:true
        //,bodyStyle:'padding-left:15px;'
        ,tbar:[getTop5Info(),label1_1,{xtype:'tbfill'},period_combo,'-',type_combo]
    });      

    var panel3 = new Ext.Panel({
        width:'100%',
        height: 185,
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

    var cpu_panel=new Ext.Panel({
        width:'49.5%',
        height: 180,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:5px;padding-top:10px;',
        layout:'fit'
    });
    var mem_panel=new Ext.Panel({
        width:'49.5%',
        height: 180,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:5px;padding-top:10px;',
        layout:'fit'
    });
     var srvr_cpu_panel=new Ext.Panel({
        width:'49.5%',
        height: 180,
        border:false,
        bodyBorder:false,
        layout:'fit'
        //bodyStyle:'padding-right:5px;padding-top:10px;'
    });
    var srvr_mem_panel=new Ext.Panel({
        width:'49.5%',
        height: 180,
        border:false,
        bodyBorder:false,
        layout:'fit'
        //bodyStyle:'padding-right:5px;padding-top:10px;'
    });

    var top_cpu_vms_grid=topN_dcvms(node_id, node, "CPU");
    var top_mem_vms_grid=topN_dcvms(node_id, node, "Memory");
    var top_cpu_srvr_grid=topN_dcservers(node_id, node, "CPU");
    var top_mem_srvr_grid=topN_dcservers(node_id, node, "Memory");
    //var error_console_grid=err_console_grid();

    redrawChart(stackone.constants.DATA_CENTER,stackone.constants.CPU,node_id,node.text,
                stackone.constants.HRS12,fdate,tdate,'dc_chart'+node_id,true,panel1_1,stackone.constants.TOP5SERVERS);

    panel1_0.add(dt_cntr_vm_grid);
    panel1.add(panel1_0);
    panel1.add(dummy_panel1);
    panel1.add(panel1_1);

    srvr_cpu_panel.add(top_cpu_srvr_grid);
    srvr_mem_panel.add(top_cpu_vms_grid);
    //err_panel.add(error_console_grid);
    
    panel3.add(srvr_cpu_panel);
    panel3.add(dummy_panel3);
    panel3.add(srvr_mem_panel);

    cpu_panel.add(top_mem_srvr_grid);
    mem_panel.add(top_mem_vms_grid);

    panel4.add(cpu_panel);
    panel4.add(dummy_panel4);
    panel4.add(mem_panel);

    //panel5.add(err_panel);
    
    var topPanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Information for {0}"),node.text),
        height:'50%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false,
        items:[panel1,panel3,panel4]
    });

//    var bottomPanel = new Ext.Panel({
//        //layout  : 'fit',
//        collapsible:true,
////        title:"Shared Information",
//        height:'50%',
//        width:'100%',
//        border:false,
//        bodyBorder:false,
//        items:[]
//    });

    var data_center_homepanel=new Ext.Panel({
        width:"100%",
        height:"100%"
        ,items:[topPanel]
        ,bodyStyle:'padding-left:10px;padding-right:5px;'
    });
    //data_center_homepanel.add(topPanel);
    //data_center_homepanel.add(bottomPanel);
    mainpanel.add(data_center_homepanel);
    data_center_homepanel.doLayout();
    mainpanel.doLayout();
    centerPanel.setActiveTab(mainpanel);
}

/*
 * 服务器池-入门面板
 * 
 * @param {}
 *            mainpanel
 * @param {}
 *            node_id
 * @param {}
 *            node
 */
function data_center_datacenterStarter_page(mainpanel, node_id, node) {
	if (mainpanel.items)
		mainpanel.removeAll(true);
	var url = "/dashboard/data_center_info?type=DATA_CENTER_VM_INFO&node_id="
			+ node_id;
	var ajaxReq = ajaxRequest(url, 0, "GET", true);
	ajaxReq.request({
		success : function(xhr) {
			var response = Ext.util.JSON.decode(xhr.responseText);
			if (response.success) {
				datacenter_list = response.info[5].list;
			}
		},
		failure : function(xhr) {
		}
	});
	/*var topHtml = '';
	topHtml += '<div class="toolbar_hdg" >';
	topHtml += '</div>';*/
	var topHtml = '';
	topHtml += '<div class="data-center-starter-top">';
	topHtml += '	<div class="data-center-starter-top-text">';
	topHtml += _("欢迎使用Smart Data Center");
	topHtml += '<br/>';
	topHtml += '<br/>';
	topHtml += _("SmartDataCenter是一款服务器虚拟化软件，管理运行在基于x86系统的服务器池,它为用户提供了一个单站式控制台来创建、克隆、共享、配置、引导和迁移VM，从而简化大规模虚拟化管理，更进一步，提供24*7监控、实时迁移，全面掌握你的服务器池，以应付突发故障;最后，通过HA、负载均衡以及备份等功能自动化服务器池，使你心平气和面临IT运维。");	
	topHtml += '	</div>';
	topHtml += '	<div class="data-center-starter-top-img">';
	topHtml += '	</div>';
	topHtml += '</div>';

	var leftHtml = '';
	leftHtml += '<div class="data-center-starter-left-text">';
	leftHtml += '<div>基本任务</div>';
	leftHtml += '<a href="#" onclick=javascript:data_center_datacenterStarter_page_addServerPool();>';
	leftHtml += '新建服务器池';
	leftHtml += '</a>';
	leftHtml += '<br/>';
	leftHtml += '</div>';
	var rightHtml = '';
	rightHtml += '<div class="data-center-starter-right-text" >';
	rightHtml += _("什么是虚拟化");
	rightHtml += '<br/><br/>';
	rightHtml += _("虚拟化是指计算元件在虚拟的基础上而不是真实的基础上运行，是一个为了简化管理，优化资源的解决方案。它将物理硬件与操作系统分开，从而提供更高的资源利用率和灵活性。");
	rightHtml += '<br/>';
	rightHtml += '<br/>';
	rightHtml += _("虚拟化技术可以扩大硬件的容量，简化软件的重新配置过程。CPU的虚拟化技术可以单CPU模拟多CPU并行，允许一个平台同时运行多个操作系统，并且应用程序都可以在相互独立的空间内运行而互不影响，从而显著提高计算机的工作效率。");
	rightHtml += '</div>'
	var topPanel = new Ext.Panel({
		height : 300,
		width : '100%',
		region : 'north',
		border: false,
		frame: true,
		//bodyStyle : 'margin: 10px 10px 10px 10px;',
		html : topHtml
	});
	var leftPanel = new Ext.Panel({
		height : '60%',
		width : '40%',
		region : 'west',
		border: false,
		frame: true,
		bodyStyle : 'margin-right:5px;padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
		html : leftHtml
	});
	var rightPanel = new Ext.Panel({
		height : '60%',
		width : '60%',
		region : 'center',
		frame: true,
		border: false,
		//bodyStyle : 'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
		html : rightHtml
	});

	var datacenterStarterPanel = new Ext.Panel({
		width : "100%",
		height : "100%",
		layout : 'border',
		border: false,
		items : [topPanel, leftPanel, rightPanel]
	});
	mainpanel.add(datacenterStarterPanel);
	datacenterStarterPanel.doLayout();
	mainpanel.doLayout();
	centerPanel.setActiveTab(mainpanel);
}

function data_center_datacenterStarter_page_addServerPool(){
	addServerPool(leftnav_treePanel.getSelectionModel().getSelectedNode());
}

function data_center_config_page(mainpanel,node_id,node){

    if(mainpanel.items)
        mainpanel.removeAll(true);

    var dt_cntr_storage_grid=data_center_storage_grid(node_id,node);
    var dt_cntr_nw_grid=data_center_nw_grid(node_id,node);
    var dt_cntr_info_grid=data_center_info_grid(node_id);
    var panel1 = new Ext.Panel({
        height:250,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column',
        bodyStyle:'padding-top:5px;padding-right:5px;'
    });
    var label1_1=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("主机操作系统")+'<br/></div>'
    });
    var label1_2=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("客户机操作系统")+'<br/></div>'
    });
     var panel1_1 = new Ext.Panel({
        height:245,
        width:'35%',
        cls: 'whitebackground',
        border:true,
        bodyBorder:true
        //,bodyStyle:'padding-left:15px;'
        ,tbar:[label1_1]
    });
    var panel1_2 = new Ext.Panel({
        height:245,
        width:'35%',
        cls: 'whitebackground',
        border:true,
        bodyBorder:true
        //,bodyStyle:'padding-left:15px;'
        ,tbar:[label1_2]
    });
    var dummy_panel1 = new Ext.Panel({
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
    var panel1_0 = new Ext.Panel({
        height:245,
        width:'29%',
        border:false,
        bodyBorder:false
        ,layout:'fit'
    });
     var panel4 = new Ext.Panel({
         width:'100%',
        height: 300,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });

    var dummy_panel4 = new Ext.Panel({
        width:'1%',
        html:'&nbsp;',
        border:false,
        bodyBorder:false
    });

    var storage_panel=new Ext.Panel({
        width:'49.5%',
        height: 220,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var nw_panel=new Ext.Panel({
        width:'49.5%',
        height: 220,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
	
    panel1_0.add(dt_cntr_info_grid);   
    panel1_1.add(os_dist_chart(node_id, node,stackone.constants.MANAGED_NODE));
    panel1_2.add(os_dist_chart(node_id, node,stackone.constants.DOMAIN));
    panel1.add(panel1_0);
    panel1.add(dummy_panel1);
    panel1.add(panel1_1);
    panel1.add(dummy_panel2);
    panel1.add(panel1_2);


    storage_panel.add(dt_cntr_storage_grid);
    nw_panel.add(dt_cntr_nw_grid);

   
    panel4.add(storage_panel);
    panel4.add(dummy_panel4);
    panel4.add(nw_panel);
    var data_center_configpanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Information for {0}"),node.text),
        height:'50%',
        width:'100%',
        border:false,
        //cls:'headercolor',
        bodyBorder:false,
        items:[panel1,panel4]
        ,bodyStyle:'padding-left:10px;padding-right:5px;padding-top:5px;'
    });
//     var bottomPanel1 = new Ext.Panel({
//        //layout  : 'fit',
//        collapsible:true,
////        title:"Shared Information",
//        height:'50%',
//        width:'100%',
//        border:false,
////        cls:'headercolor',
//        bodyBorder:false,
//        items:[panel4]
//    });
//
//     var data_center_configpanel=new Ext.Panel({
//        width:"100%",
//        height:"100%"
//        ,items:[topPanel1,bottomPanel1]
//        ,bodyStyle:'padding:5px;'
//    });
    mainpanel.add(data_center_configpanel);
    data_center_configpanel.doLayout();
    mainpanel.doLayout();

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
//        alert("----value------"+value);
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

var changeMap = {
	// 服务器池summary panel
	'Server Pools' : '服务器池',
	'Servers' : '服务器',
	'Virtual Machines' : '虚拟机',
	'Virtual Machine Density' : '虚拟机密度',
	'Virtualization Platform' : '虚拟化平台',
	'Notifications' : '通知',
	'Storage Allocation (%)' : '存储使用率',
	'Fencing Configured' : 'Fencing 配置',
	'DWM Policy' : 'DWM策略',

	// 服务器池 config panel
	'Total CPU count' : '总CPU数',
	'Total Memory' : '总内存',
	'Storage Available' : '可用存储',
	'Networks' : '网络',

	// 服务器池 backup panel
	'Backup Policies' : '备份策略',
	'Backup Failures <br/>(Last 7 days)' : '备份失败（过去7天）',
	'Virtual Machines without backup policy' : '没有备份策略的虚拟机',
	'Total Backup Size (GB)' : '总备份体积（GB）',

	// 服务器池 summary panel
	'Storage Used' : '已使用存储',
	'High Availability' : '高可用',
	'Outstanding Failures' : '严重的失败操作',

	// 服务器 summary panel
	'Status' : '状态',
	'Platform' : '平台',
	'Host OS' : '宿主操作系统',
	'CPUs' : 'CPU数目',
	'Memory' : '内存',
	'Host CPU(%)' : '宿主CPU使用率（%）',
	'Host Memory(%)' : '宿主内存使用率（%）',

	// 虚拟机 summary panel
	'Name' : '名称',
	'Template' : '模板',
	'Network' : '网络',
	'Guest OS' : '客户操作系统',
	'Virtual CPUs' : '虚拟CPU个数',
	'Server' : '服务器',
	'Storage Allocation' : '存储加载数',
	'Host CPU Usage(%)' : '宿主CPU使用率（%）',
	'Memory Utilization(%)' : '内存使用率（%）',
	'Virtual Data Center' : '虚拟服务器池',
	'IaaS' : 'IaaS',
	'Account User' : '账号用户',
	'Cloud User' : '云用户',
	'Cloud VM Name' : '云虚拟机名称',

	// 模板库 summary panel
	'Template Groups' : '模板组',
	'Location' : '位置',

	// 模板组 summary panel
	'Group Name' : '组名',
	'Total Templates' : '总模板数',

	// 模板 summary panel
	'Version' : '版本',
	'Group' : '模板组',

	//
	'Version' : '版本',
	'Bootloader' : '启动加载器',
	'Ramdisk' : '内存盘',
	'Kernel Args' : '内核参数',
	'On Power off' : '关电源时',
	' Availble Memory (MB)' : '可用内存（MB）',
	'Total Memory (MB)' : '总内存（MB）',
	'Kernel' : '内核',
	'Distribution' : '发行版',
	'Architecture' : '架构',
	'Model' : '型号',
	'Vendor Id' : '厂商ID',
	'Processors' : '处理器',
	'Speed (MHz)' : '速度（MHz）',
	//
	'Name' : '名称',
	'Server' : '服务器',
	'Virtual CPUs' : '虚拟CPU个数',
	'Memory' : '内存',
	'Guest OS' : '客户机操作系统',

	//
	'VNC' : '虚拟网络控制',
	'Use Unused Display' : '是否使用显示',
	'SDL' : 'SDL',
	'Standard Vga' : '标准VGA',

	//
	'USB Enabled' : '启用USB',
	'USB Device' : 'USB设备',

	//
	'Boot Loader' : '启动加载器',
	'Kernel' : '内核',
	'RAMDisk' : '内存盘',
	'Root Device' : '根设备',
	'Kernel Arguments' : '内核参数',
	'On Power Off' : '关闭电源',
	'On Reboot' : '重新启动',
	'On Crash' : '注销',
	'Boot Device' : '启动设备',

	//
	'Architecture Lib directory' : '架构Lib目录',
	'Network Mode' : '网络适配器',
	'Shadow Memory' : 'Shadow内存',
	'Device Model' : '设备型号',
	'Builder' : '生产厂商'
	

};

var testarr = [];
function NewUIMakeUP(value, meta, rec) {
	if (rec.data.name) {
		var ret = rec.data.name;
		if (changeMap[ret]) {
			ret = changeMap[ret];
		}
		return ret;
	}
	if (rec.data.label) {
		var ret = rec.data.label;
		if (changeMap[ret]) {
			ret = changeMap[ret];
		}
		return ret;
	}
}
function NewUIMakeUP(value, meta, rec) {
	if (rec.data.name) {
		var ret = rec.data.name;
		if (changeMap[ret]) {
			ret = changeMap[ret];
		}
		return ret;
	}
	if (rec.data.label) {
		var ret = rec.data.label;
		if (changeMap[ret]) {
			ret = changeMap[ret];
		}
		return ret;
	}
}

function showHADialog(sp_id){
    var node=leftnav_treePanel.getNodeById(sp_id);
    HighAvailbility(node,"");
}
function showHASummary(value,meta,rec){
    var entities = rec.get('list');
    if(value > 0) {
        var fn = "showHADetails('" + entities + "')";
        var returnVal = '<a href="#" onClick=' + fn + '>' + value + '</a>';
        return returnVal;
    }
    else {
        return value;
    }
}

function showHADetails(vm_ids){

    var failed_vms_grid=draw_failed_vms_grid(vm_ids);

    var failed_vms_panel = new Ext.Panel({
        width:600,
        height:325,
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'close',
                id: 'close',
                text:_('Close'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        closeWindow();
                    }
                }
            })

        ]
    });

    failed_vms_panel.add(failed_vms_grid);
    showWindow(_("虚拟机"),615,350,failed_vms_panel);
}

function draw_failed_vms_grid(vm_ids){
    var cm = new Ext.grid.ColumnModel([
        {
            header: _("vmid"),
            width: 110,
            dataIndex: 'vm_id',
            hidden:true
        },
        {
            header: _("名称"),
            width: 120,
            dataIndex: 'vmname',
            sortable:true
        },
        {
            header: _("服务器"),
            width: 100,
            dataIndex: 'servername',
            sortable:true
        },
        {
            header: _("serverid"),
            width: 100,
            hidden:true,
            dataIndex: 'serverid'
        },
        {
            header:  _("Down At"),
            width: 180,
            dataIndex: 'down_at'
        }
    ]);

    var failed_vms_store = new Ext.data.JsonStore({
        url: "/dashboard/failed_vms?vm_ids="+vm_ids,
        root: 'vm_info',
        fields: ['vm_id','vmname','serverid','servername','down_at'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){alert(res.responseText);
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    failed_vms_store.load();    

	var failed_vms_grid = new Ext.grid.GridPanel({
        store: failed_vms_store,
        colModel:cm,
        stripeRows: true,
        frame:true,
        forceFit :true,
        autoExpandColumn:1,
        autoExpandMin:80,
        enableHdMenu:false,
        autoScroll:true,
        autoWidth:true,
        height:290
        ,listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            }
//            ,rowdblclick:function(grid,rowIndex,e){
//                handle_rowclick(grid,rowIndex,"click",e);
//            }
        }
    });

	return failed_vms_grid;
}

function data_center_info_grid(node_id){
    var data_center_info_store =new Ext.data.JsonStore({
        url: "/dashboard/data_center_info?type=DATA_CENTER_INFO",
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
    data_center_info_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_task'
    });

    var data_center_info_grid = new Ext.grid.GridPanel({
        //title:'Physical Resources',
        disableSelection:true,
        stripeRows: true,
        //title:_("Summary"),
        //autoHeight:true,
        border:true,
        //cls:'hideheader padded headercolor1',
        cls:'hideheader ',
        //width: 450,
        width: '100%',
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
             {header: "", width: 120, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:NewUIMakeUP},
             {header: "", width: 100, sortable: true,dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:data_center_info_store
        ,tbar:[label_strge]
    });

    return data_center_info_grid
}

function data_center_sec_info_grid(node_id){
    var data_center_sec_info_store =new Ext.data.JsonStore({
        url: "/dashboard/data_center_info?type=DATA_CENTER_SEC_INFO",
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
    data_center_sec_info_store.load({
        params:{
            node_id:node_id
        }
    });

    var data_center_sec_info_grid = new Ext.grid.GridPanel({
        //title:'Physical Resources',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:false,
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
        store:data_center_sec_info_store
    });

    return data_center_sec_info_grid
}

function data_center_vm_grid(node_id){
    var vm_info_store =new Ext.data.JsonStore({
        url: "/dashboard/data_center_info?type=DATA_CENTER_VM_INFO",
        root: 'info',
        fields: ['name','value','type','action','chart_type','list','entType'], 
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
    
    var data_center_vm_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        autoExpandColumn:1,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 225,
        enableHdMenu:false,
        enableColumnMove:false,
        //plugins:[action],
        autoScroll:true,
        frame:false,
        loadMask:true,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 120, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:NewUIMakeUP},
            {header: "", width: 120, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_info_store
        ,tbar:[label_strge]
    });

    return data_center_vm_grid
}

function data_center_storage_grid(node_id,node){

    var data_center_storage_columnModel = new Ext.grid.ColumnModel([
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
        header: _("分配(%)"),
        width: 120,
        dataIndex: 'usage',
        sortable:true,
        renderer:showBar
    },
    {
        header: _("状态"),
        width: 150,
        dataIndex: 'status',
        sortable:true,
        renderer: showSyncStatus
    },
    {
        header: _("说明"),
        width: 150,
        dataIndex: 'description',
        sortable:true,
        hidden:true
    },
    {
        header: _("服务器池"),
        width: 150,
        dataIndex: 'serverpools',
        sortable:true
    }]);

    var data_center_storage_store = new Ext.data.JsonStore({
        url: "/dashboard/data_center_info?type=STORAGE_INFO&op=DC",
        root: 'info',
        fields: ['name','type','size','description','serverpools','usage','status'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    data_center_storage_store.load({
        params:{
            node_id:node_id
        }
    });

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("存储资源")+'</div>'
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
    var data_center_storage_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: data_center_storage_store,
        colModel:data_center_storage_columnModel,
        stripeRows: true,
        frame:false,
        //autoExpandColumn:1,
        //autoExpandMax:300,
        border:true,
        enableHdMenu:false,
        autoScroll:true,
        id:'data_center_storage_summary_grid',
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

	return data_center_storage_grid;

}

function data_center_nw_grid(node_id,node){

    var data_center_nw_columnModel = new Ext.grid.ColumnModel([
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
        width: 100,
        sortable:true,
        dataIndex: 'definition'
    },
    {
        header: _("说明"),
        width: 150,
        sortable:true,
        dataIndex: 'description'
    }]);

    var data_center_nw_store = new Ext.data.JsonStore({
        url: "/dashboard/data_center_info?type=VIRT_NW_INFO",
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
    data_center_nw_store.load({
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
	var data_center_nw_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: data_center_nw_store,
        colModel:data_center_nw_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:4,
        autoExpandMin:150,
        border:true,
        enableHdMenu:true,
        autoScroll:true,
        id:'data_center_nw_summary_grid',
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

	return data_center_nw_grid;

}

function topN_dcvms(node_id,node,metric){
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
            width: 100,
            dataIndex: 'vm',
            //css:'font-weight:bold;',
            sortable:true
        },
        {
            header: format(_("主机 {0}(%)"),metric),
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
        //autoExpandMax:300,
        autoExpandMin:80,
        //border:false,
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
function topN_dcservers(node_id,node,metric){
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
            width: 100,

            dataIndex: 'server',
            //css:'font-weight:bold;',
            sortable:true
        },
        {
            header: format(_("{0} 利用率(%)"),metric),
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
        html:'<div class="toolbar_hdg">'+format(_("负载最高服务器 {0} 利用率"),metric)+'</div>'
    });

	var top_grid = new Ext.grid.GridPanel({
//        disableSelection:true,
        store: top_store,
        colModel:top_cm,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
        //autoExpandMax:300,
        autoExpandMin:80,
        //border:false,
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

Ext.override(Ext.grid.GridPanel, {
     rowcontextmenu :function(grid,rowIndex,e) {
        e.preventDefault();
        handle_rowclick(grid,rowIndex,"contextmenu",e);
    },
    rowdblclick:function(grid,rowIndex,e){
        handle_rowclick(grid,rowIndex,"click",e);
    }
});

function os_dist_chart(node_id,node,metric){
    var srvr_distribution_store = new Ext.data.Store({
        url:"/dashboard/os_distribution_chart?node_id="+node_id+"&metric="+metric+"&node_type="+node.attributes.nodetype,
        reader: new Ext.data.JsonReader({
        root: 'info',
            fields: ['label', 'value']
        })
    });

    var srvr_distribution_pie = new Ext.ux.PieFlot({
        pies: {
            show: true,
            autoScale: true,
            fillOpacity: 1,
            labelFormatter: function(label, value,percent,textValue, pie, series, options) {
//                alert(label+"==value=="+value+"===percent==="+percent+"==textValue==="+textValue+"pie==="+pie);
                if(value==0){
                    return "";
                }
                return textValue+"%("+value+")";
            },  
            labelStyle: 'font-size:10px; '

        },
        height:'100%',
        width:'100%',
        legend: {
            show: true,
            position: "se",
            margin: [0,0],
            backgroundOpacity: 0
            ,labelFormatter: function(label, series) {                
                return '<div style="font-size:10px;">' + label + '</div>';
            }
        },
        series: []
    });

    srvr_distribution_store.on('load',
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
        srvr_distribution_pie
    );

    srvr_distribution_store.load();

    return srvr_distribution_pie;
}

function data_center_vminfo_page(mainpanel,node_id,node){

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
    
    var server_grid=showServerList(node_id,stackone.constants.DATA_CENTER,panel2);

    panel2.add(server_grid);

    var vm_grid=showVMList(node_id,stackone.constants.DATA_CENTER,panel3);
    panel3.add(vm_grid);
    var vminformpanel = new Ext.Panel({
        //layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Server Pool Information for {0}"),node.text),
        height:'50%',
        width:'100%',
        border:false,
        //cls:'headercolor1',
//        cls:'headercolor',
        bodyStyle:'padding-left:15px;padding-right:10px;padding-bottom:12px;padding-top:10px;',
        bodyBorder:false,
        resizable:true,
        items:[panel2,panel3]
    });

    mainpanel.add(vminformpanel);
    vminformpanel.doLayout();
    mainpanel.doLayout();
}


function data_center_backup_history_page(backup_history_Panel,node_id,node){
    if(backup_history_Panel.items)
        backup_history_Panel.removeAll(true);

    node_id = node.attributes.id;
    node_type = node.attributes.nodetype;


    var panel1 = new Ext.Panel({
        width:'100%',
        height: 192,
        border:false,
        bodyBorder:false,
       // bodyStyle:'padding-top:0px;padding-right:5px;',
        layout:'column'
    });
   
    var panel2 = new Ext.Panel({
        width:'100%',
        height: 162,
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


    var panel7 = new Ext.Panel({
        width:'100%',
        height: 300,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-top:00px;padding-right:5px;',
        layout:'column'
    });   
//     panel7.add(SPBackupResultGrid(node_id));
    panel7.add(Sp_vm_backup_historyGrid(node_id,node));
    
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
        items:[panel1, panel2, panel7]
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



