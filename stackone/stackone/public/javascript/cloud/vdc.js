/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */


/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function vdc_summary_page(mainpanel,node_id,node){
    //node_id='d9a3bd4a-062a-5017-22af-94222763e8b9';
    if(mainpanel.items)
        mainpanel.removeAll(true);

//    var label0_1=new Ext.form.Label({
//        html:'<div class="toolbar_hdg" >'+_("Daily")+'<br/></div>'
//    });
    var label2=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("负载最高的虚拟机")+'</div>'
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
                            redrawChart(stackone.constants.VDC,type_combo.getValue(),node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'s_chart'+node_id,true,panel2,stackone.constants.TOP5VMS,avg_fdate,avg_tdate);
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
                            fdate=cust.fromTime()
                            tdate=cust.toTime();
                            redrawChart(stackone.constants.VDC,type_combo.getValue(),node_id,node.text,
                                period_combo.getValue(),fdate,tdate,'s_chart'+node_id,true,panel2,stackone.constants.TOP5VMS,avg_fdate,avg_tdate);

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
            redrawChart(stackone.constants.VDC,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'s_chart'+node_id,true,panel2,stackone.constants.TOP5VMS,avg_fdate,avg_tdate);
            label2.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
        }
    });

    var storelst = [];
    if(node.attributes.cp_type == stackone.constants.CMS){
        storelst = [[stackone.constants.CPU,_(stackone.constants.CPU)],
                [stackone.constants.MEM,_(stackone.constants.MEM)]
               ];
    } else {
        storelst = [[stackone.constants.CPU,_('CPU')],
                [stackone.constants.METRIC_NETWORKIN,_('Network In (Bytes)')],
                [stackone.constants.METRIC_NETWORKOUT,_('Network Out (Bytes)')]
               ];
    }
    var type_combo=getMetricCombo(null, 135, null, null, null, storelst);
    type_combo.on('select',function(field,rec,index){
        redrawChart(stackone.constants.VDC,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'s_chart'+node_id,true,panel2,stackone.constants.TOP5VMS,avg_fdate,avg_tdate);
        label2.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
    });



//    var srvr_info_grid=server_info_grid(node_id);
//    var srvr_sec_info_grid=server_sec_info_grid(node_id);
    var vdc_summary_grid_var = vdc_overview_summary_grid_fun(node_id);
   
//    var srvr_storage_grid=server_storage_grid(node_id,node);
//    var srvr_nw_grid=server_nw_grid(node_id,node);
//    var top_cpu_grid=topNCloudvms(node_id, node, "CPU",top5vmmetric_combo);


    var top_cpu_grid=topNCloudvms(node_id, node, "CPU");//,enttype_combo1,top5vmmetric_combo
//    var top_network_grid=topNCloudvms(node_id, node, "Networkout");

    var panel1 = new Ext.Panel({
        height:540,
        width:'30%',
        border:false,
        bodyBorder:false,
        layout:'column',
        bodyStyle:'padding-top:5px;padding-right:5px;'
        
    });
    var panel1_0 = new Ext.Panel({
        height:535,
        width:'100%',
        border:false,
        bodyBorder:false
        ,bodyStyle:'padding-right:5px;'
        ,layout:'fit'
        
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
        height:'100%',
        width:'100%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        //,bodyStyle:'padding-left:15px;padding-right:30px;padding-bottom:12px;padding-top:10px;'
        ,tbar:[' ',label2,{xtype:'tbfill'},avg_button,'-',period_combo,'-',type_combo]
    });
    //var summary_grid=drawsummaryGrid(rows,node.attributes.nodetype,node.attributes.id,true,panel2);

    var panel3 = new Ext.Panel({
        height:'100%',
        width:'70%',
        border:false,
        bodyBorder:false,
        layout:'column'
        , bodyStyle:'padding-top:5px;padding-right:5px;'
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
        bodyStyle:'padding-top:10px;padding-right:5px;',
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
        width:'100%',
        height: 287,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:15px;padding-right:3px;padding-top:2px;',
        layout:'fit'
         
    });
    var network_panel=new Ext.Panel({
        width:'49.5%',
        height: 270,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:15px;padding-right:3px;',
        layout:'fit'
    });

    //panel1_1.add(get_cpu_chart());
    redrawChart(stackone.constants.VDC,stackone.constants.CPU,node_id,node.text,
                        stackone.constants.HRS12,fdate,tdate,'s_chart'+node_id,true,panel2,stackone.constants.TOP5VMS,avg_fdate,avg_tdate);
    panel1_0.add(vdc_summary_grid_var);
    //panel1_5.add(panel2)
    panel1.add(panel1_0);
    cpu_panel.add(top_cpu_grid);
    panel3.add(panel2);
    panel3.add(dummy_panel3);
    panel3.add(cpu_panel);


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
        items:[panel1,panel3]
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


function vdc_overview_summary_grid_fun(node_id){

    var vdc_info_store =new Ext.data.JsonStore({
        url: "/cloud_dashboard/vdc_info?vdc_id="+node_id+"&type=VDC_OVERVIEW_SUMMARY",
        root: 'info',
        fields: ['name','value','available','unit'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    vdc_info_store.load();



    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_task'
    });

    var vdc_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        autoExpandColumn:1,
        border:true,
//        cls:'hideheader',
        width: '100%',
        height: 425,
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
            {header: "", width: 145, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:testUIMakeUP},
            {header: "已用", width: 120, sortable: false, dataIndex: 'value',renderer:UIMakeUP,align:'right'},
            {header: _("分配"),width: 96,dataIndex: 'available',sortable:true,renderer:sageUIMakeUP,align:'right'},
            {header: _("单元"),width: 0,dataIndex: 'unit',hidden:true,sortable:true}

        ],
        store:vdc_info_store
        ,tbar:[label_strge]
    });

    return vdc_grid
}


function sageUIMakeUP(value, meta, rec) {
    var dict = {'unlimited':'无限'
				
	} 
	if (dict[rec.get('available').trim().replace(/&nbsp;/g, '')]) {
		return dict[rec.get('available').trim().replace(/&nbsp;/g, '')];
	} else {
	        return rec.get('available');
	}
	
}

function testUIMakeUP(value, meta, rec) {
    var dict = {'Virtual Machines':'虚拟机',
	            'Running':'可运行',
	            'Provisioned':'部署',
	            'Compute Resources':'计算资源',
	            'Memory (MB)':'内存',
				'Instance Type':'实例类型',
	            'vCPUs':'vCPUs',
				'Storage':'存储',
				'Size (GB)':'存储容量',
				'Networking':'网络',
				'Public IPs':'公共IP',
				'Private Networks':'私有网络'
				
	} 
	if (dict[rec.get('name').trim().replace(/&nbsp;/g, '')]) {
		return dict[rec.get('name').trim().replace(/&nbsp;/g, '')];
	} else {
	        return rec.get('name');
	}
	
}

function cloudUIMakeUP(value, meta, rec) {
    var dict = {'Providers':'供应商',
	            'Regions':'区域',
	            'Public IPs':'公共IP',
	            'Security Groups':'安全组',
	            'Key Pairs':'密钥对',
				
	} 
	if (dict[rec.get('name').trim().replace(/&nbsp;/g, '')]) {
		return dict[rec.get('name').trim().replace(/&nbsp;/g, '')];
	} else {
	        return rec.get('name');
	}
	
}

////////////////////// vdc_config_page ////////////////////////////

function vdc_config_page(mainpanel,node_id,node){

    if(mainpanel.items)
        mainpanel.removeAll(true);

    var panel1 = new Ext.Panel({
        width:'100%',
        height: '70%',
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

    var label1_1=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("各区域虚拟机")+'<br/></div>'
    });

    var vms_pichart_panel = new Ext.Panel({
        height:225,
        width:'49.5%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        //,bodyStyle:';padding-right:15px;'
        ,tbar:[label1_1]
    });


    var label1_2=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("各区域存储")+'<br/></div>'
    });

    var storage_pichart_panel = new Ext.Panel({
        height:220,
        width:'49.5%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        //,bodyStyle:';padding-right:15px;'
        ,tbar:[label1_2]
    });

//    var srvr_interface_grid= vdc_overview_network_grid_fun(node_id,node);
//    var srvr_dvce_grid=vdc_overview_disk_grid_fun(node_id,node);

//    var vdc_storage_grid=vdc_overview_snapshot_grid_fun(node_id, node);
//    var vdc_nw_grid=vdc_overview_storage_grid_fun(node_id, node);

    panel1_1.add(vdc_config_summary_grid_fun(node_id));
    vms_pichart_panel.add(vms_per_regions_pichart_fun(node_id));
    panel1_2.add(vms_pichart_panel);
//    panel1_2.add(vdc_config_keypair_grid_fun(node_id, node));
//    panel2_1.add(vdc_config_providers_grid_fun(node_id, node));
    panel2_2.add(vdc_config_security_group_grid_fun(node_id, node));

//    panel2_1.add(vdc_config_public_ip_grid_fun(node_id, node));
    panel3_1.add(vdc_config_keypair_grid_fun(node_id, node));
    panel3_2.add(vdc_config_public_ip_grid_fun(node_id, node));

//    panel4_1.add(vdc_config_storage_grid_fun(node_id, node));
//    storage_pichart_panel.add(storage_per_regions_pichart_fun(node_id));
//    panel4_2.add(storage_pichart_panel);

    panel1.add(panel1_1);
    panel1.add(dummy_panel1);
    panel1.add(panel1_2)

    panel2.add(panel3_1);
    panel2.add(dummy_panel2);
    panel2.add(panel2_2)

//    panel3.add(panel3_1);
//    panel3.add(dummy_panel3);
    panel3.add(panel3_2);

//    panel4.add(panel4_1);
//    panel4.add(dummy_panel4);
//    panel4.add(panel4_2);

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
function vdc_vm_folder_vminfo_page(mainpanel,node_id,node)
{

     if(mainpanel.items)
        mainpanel.removeAll(true);
    node_id=node.parentNode.attributes.id; 
    var panel2 = new Ext.Panel({
        height:'190%',
        width:'190%',
        layout: 'fit',
//        bodyStyle:'padding-bottom:12px;padding-top:10px;',
        border:false,
        bodyBorder:false
    });
    var summary_grid=showCloudVMList(node,node_id,stackone.constants.MANAGED_NODE,panel2);
//    drawsummaryGrid(rows,node.attributes.nodetype,node.attributes.id,true,panel2);

    panel2.add(summary_grid);

    var vminformpanel = new Ext.Panel({
        layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Server Pool Information for {0}"),node.text),
        height:'140%',
        width:'140%',
        border:false,
        cls:'headercolor',
        bodyBorder:false,
        bodyStyle:'padding-left:5px;padding-right:1px;padding-bottom:5px;padding-top:3px;',
        resizable:true,
        items:[panel2]
    });

    mainpanel.add(vminformpanel);
    vminformpanel.doLayout();
    mainpanel.doLayout();

}


function vdc_config_summary_grid_fun(node_id){

    var vdc_info_store =new Ext.data.JsonStore({
        url: "/cloud_dashboard/vdc_info?vdc_id="+node_id+"&type=VDC_CONFIG_SUMMARY",
        root: 'info',
        fields: ['name','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });



    vdc_info_store.load();



    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_task'
    });

    var vdc_grid = new Ext.grid.GridPanel({
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
            {header: "", width: 120, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:cloudUIMakeUP},
            {header: "", width: 120, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vdc_info_store
        ,tbar:[label_strge]
    });

    return vdc_grid
}


function vms_per_regions_pichart_fun(vdc_id){

    var vms_per_region_store = new Ext.data.Store({
        url:"/cloud_dashboard/vdc_info?vdc_id="+vdc_id+"&type=VDC_CONFIG_VMS_BY_REGION_PICHART",
        reader: new Ext.data.JsonReader({
            root: 'info',
            fields: ['label', 'value']
        })
    });

    var vms_per_region_pie1 = new Ext.ux.PieFlot({
        pies: {
            show: true,
            autoScale: true,
            fillOpacity: 1,
            labelFormatter: function(label, value, percent, textValue, pie, serie, options) {
                if(value == 0)
                {
                    return '';
                }
                return textValue + '% ('+value+')';
//                return value;
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

    vms_per_region_store.on('load',
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
        vms_per_region_pie1
    );

    vms_per_region_store.load();

    return vms_per_region_pie1;
}


function vdc_config_providers_grid_fun(node_id, node){

    var vdc_providers_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width: 200,
        dataIndex: 'name',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("账户名称"),
        width: 170,
        sortable:true,
        dataIndex: 'account'
    },
    {
        header: _("虚拟机"),
        width: 141,
        sortable:true,
        dataIndex: 'vms'
    }]);

    var vdc_providers_store = new Ext.data.JsonStore({
        url:"/cloud_dashboard/vdc_info?vdc_id="+node_id+"&type=VDC_CONFIG_PROVIDERS",
        root: 'info',
        fields: ['name', 'account', 'vms'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    vdc_providers_store.load();

//    var settings_btn=new Ext.Button({
//        tooltip:'Manage Storage Pool',
//        tooltipType : "title",
//        icon:'icons/settings.png',
//        cls:'x-btn-icon',
//        listeners: {
//            click: function(btn) {
//                showWindow(_("Storage Pool")+":- "+node.text,444,495,StorageDefList(node));
//            }
//        }
//    });

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("提供")+'</div>'
    });

    var vdc_providers_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: vdc_providers_store,
        colModel:vdc_providers_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:0,
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

	return vdc_providers_grid;

}


function vdc_config_security_group_grid_fun(node_id,node){

    var vdc_security_group_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width: 150,
        dataIndex: 'name',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("账户名称"),
        width: 120,
        sortable:true,
        dataIndex: 'account'
    },
    {
        header: _("区域"),
        width: 120,
        sortable:true,
        dataIndex: 'region'
    },
    {
        header: _("虚拟机"),
        width: 111,
        sortable:true,
        dataIndex: 'vms'
    }]);

    var vdc_security_group_store = new Ext.data.JsonStore({
        url:"/cloud_dashboard/vdc_info?vdc_id="+node_id+"&type=VDC_CONFIG_SECURITY_GROUP",
        root: 'info',
        fields: ['name', 'account', 'region', 'vms'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    vdc_security_group_store.load();

//    var settings_btn=new Ext.Button({
//        tooltip:'Manage Storage Pool',
//        tooltipType : "title",
//        icon:'icons/settings.png',
//        cls:'x-btn-icon',
//        listeners: {
//            click: function(btn) {
//                showWindow(_("Storage Pool")+":- "+node.text,444,495,StorageDefList(node));
//            }
//        }
//    });

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("安全组")+'</div>'
    });

    var vdc_security_group_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: vdc_security_group_store,
        colModel:vdc_security_group_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:0,
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

	return vdc_security_group_grid;

}



function vdc_config_keypair_grid_fun(node_id,node){

    var vdc_keypair_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width: 150,
        dataIndex: 'name',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("账户名称"),
        width: 120,
        sortable:true,
        dataIndex: 'account'
    },
    {
        header: _("区域"),
        width: 120,
        sortable:true,
        dataIndex: 'region'
    },
    {
        header: _("虚拟机"),
        width: 120,
        sortable:true,
        dataIndex: 'vms'
    }]);

    var vdc_keypair_store = new Ext.data.JsonStore({
        url:"/cloud_dashboard/vdc_info?vdc_id="+node_id+"&type=VDC_CONFIG_KEYPAIR",
        root: 'info',
        fields: ['name', 'account', 'region', 'vms'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

      vdc_keypair_store.load();

//    vdc_storage_store.load({
//        params:{
//            node_id:node_id
//        }
//    });

//    var settings_btn=new Ext.Button({
//        tooltip:'Manage Storage Pool',
//        tooltipType : "title",
//        icon:'icons/settings.png',
//        cls:'x-btn-icon',
//        listeners: {
//            click: function(btn) {
//                showWindow(_("Storage Pool")+":- "+node.text,444,495,StorageDefList(node));
//            }
//        }
//    });

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("密钥对")+'</div>'
    });

    var vdc_keypair_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: vdc_keypair_store,
        colModel:vdc_keypair_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:0,
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

	return vdc_keypair_grid;

}



function vdc_config_public_ip_grid_fun(node_id,node){

    var vdc_public_ip_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width: 100,
        dataIndex: 'name',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("账户名称"),
        width: 100,
        sortable:true,
        dataIndex: 'account'
    },
    {
        header: _("区域"),
        width: 100,
        sortable:true,
        dataIndex: 'region'
    },
    {
        header: _("公共IP"),
        width: 100,
        sortable:true,
        dataIndex: 'ip'
    },
    {
        header: _("虚拟机"),
        width: 101,
        sortable:true,
        dataIndex: 'vm'
    }]);

    var vdc_public_ip_store = new Ext.data.JsonStore({
        url:"/cloud_dashboard/vdc_info?vdc_id="+node_id+"&type=VDC_CONFIG_PUBLIC_IPS",
        root: 'info',
        fields: ['name', 'account', 'region', 'ip', 'vm'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    vdc_public_ip_store.load();

//    var settings_btn=new Ext.Button({
//        tooltip:'Manage Storage Pool',
//        tooltipType : "title",
//        icon:'icons/settings.png',
//        cls:'x-btn-icon',
//        listeners: {
//            click: function(btn) {
//                showWindow(_("Storage Pool")+":- "+node.text,444,495,StorageDefList(node));
//            }
//        }
//    });

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("公共IPs")+'</div>'
    });

    var vdc_public_ip_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: vdc_public_ip_store,
        colModel:vdc_public_ip_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:0,
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

	return vdc_public_ip_grid;

}


function vdc_config_storage_grid_fun(node_id, node){

    var vdc_storage_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("区域"),
        width: 250,
        dataIndex: 'region',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("块存储(GB)"),
        width: 120,
        sortable:true,
        dataIndex: 'block_storage'
    },
    {
        header: _("快照(GB)"),
        width: 120,
        sortable:true,
        dataIndex: 'snapshot'
    }]);

    var vdc_storage_store = new Ext.data.JsonStore({
        url:"/cloud_dashboard/vdc_info?vdc_id="+node_id+"&type=VDC_CONFIG_STORAGE",
        root: 'info',
        fields: ['name', 'account', 'vms'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    vdc_storage_store.load();

//    var settings_btn=new Ext.Button({
//        tooltip:'Manage Storage Pool',
//        tooltipType : "title",
//        icon:'icons/settings.png',
//        cls:'x-btn-icon',
//        listeners: {
//            click: function(btn) {
//                showWindow(_("Storage Pool")+":- "+node.text,444,495,StorageDefList(node));
//            }
//        }
//    });

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("存储")+'</div>'
    });

    var vdc_storage_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: vdc_storage_store,
        colModel:vdc_storage_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:0,
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

	return vdc_storage_grid;

}


function storage_per_regions_pichart_fun(vdc_id){

    var storage_per_region_store = new Ext.data.Store({
        url:"/cloud_dashboard/vdc_info?vdc_id="+vdc_id+"&type=VDC_CONFIG_STORAGE_BY_REGION_PICHART",
        reader: new Ext.data.JsonReader({
            root: 'info',
            fields: ['label', 'value']
        })
    });

    var storage_per_region_pie1 = new Ext.ux.PieFlot({
        pies: {
            show: true,
            autoScale: true,
            fillOpacity: 1,
            labelFormatter: function(label, value, percent, textValue, pie, serie, options) {
                if(value == 0)
                {
                    return '';
                }
                return textValue + '% ('+value+')';
//                return value;
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

    storage_per_region_store.on('load',
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
        storage_per_region_pie1
    );

    storage_per_region_store.load();

    return storage_per_region_pie1;
}



////////////////////// vdc_vminfo_page ////////////////////////////

function vdc_vminfo_page(mainpanel,node_id,node){

     if(mainpanel.items)
        mainpanel.removeAll(true);
        
    var panel2 = new Ext.Panel({
        height:'190%',
        width:'190%',
        layout: 'fit',
//        bodyStyle:'padding-bottom:12px;padding-top:10px;',
        border:false,
        bodyBorder:false
    });
    var summary_grid=showCloudVMList(node,node_id,stackone.constants.MANAGED_NODE,panel2);
//    drawsummaryGrid(rows,node.attributes.nodetype,node.attributes.id,true,panel2);

    panel2.add(summary_grid);

    var vminformpanel = new Ext.Panel({
        layout  : 'fit',
        //anchor:'100% 50%',
        collapsible:false,
        //title:format(_("Server Pool Information for {0}"),node.text),
        height:'140%',
        width:'140%',
        border:false,
        cls:'headercolor',
        bodyBorder:false,
        bodyStyle:'padding-left:10px;padding-right:10px;padding-bottom:5px;padding-top:10px;',
        resizable:true,
        items:[panel2]
    });

    mainpanel.add(vminformpanel);
    vminformpanel.doLayout();
    mainpanel.doLayout();
}



function showCloudVMList(node,node_id,type,prntPanel){
    var iscms=false;
    var template_width=140;
    var s_hidden=(type===stackone.constants.MANAGED_NODE);
    if(node.attributes.cp_type==stackone.constants.CMS){
        iscms=true;
        template_width=240;
    }else{
        iscms=false;

    }
     var showBarFun = "";
     showBarFun = showBar;
     var node_type=node.attributes.nodetype;
     

    var vms_colModel = new Ext.grid.ColumnModel([
        {header: _("编号"), width: 22, sortable: true, hidden: true, dataIndex: 'vm_id'},
        {header: _("名称"), width: 90, sortable: true, dataIndex: 'name'},
        {header: _("状态"), width: 80, sortable: true, dataIndex: 'state'},
        {header: _("CPU (%)"), width: 110, sortable: true, dataIndex: 'cpuussage',renderer:showBarFun},
        {header: _("vCPUs"), width: 80, sortable: true, dataIndex: 'cpu',align:'right'},
        {header: _("内存(MB)"), width: 85, sortable: true, dataIndex: 'mem',align:'right'},
        {header: _("存储(GB)"), width: 85, sortable: true, dataIndex: 'storage',align:'right'},
//        {header: _("Root Device Type"), width: 100, sortable: true, dataIndex: 'root_device_type',renderer:formatValue,tooltip:'Local/Pool Used'},
//        {header: _("Root Device"), width: 80, sortable: true, hidden: true, dataIndex: 'root_device',tooltip:'Total/Rx/Tx'},
        {header: _("区域"), width: 100, sortable: true,hidden: iscms, dataIndex: 'region'},//
        {header: _("实例类型"), width: 110,hidden: iscms ,sortable: true, dataIndex: 'instance_type'},//
        {header: _("私有IP"), width: 100, sortable: true, dataIndex: 'private_ip',align:'right'},
        {header: _("公共IP"), width: 100, sortable: true, dataIndex: 'public_ip',align:'right'},
        {header: _("模板"), width: template_width , sortable: true, dataIndex: 'template'},
//        {header: _("Platform"), width: 100, sortable: true, dataIndex: 'os'},
        {header: _("节点编号"), dataIndex: 'vdc_id',hidden:true}
    ]);


    var items=new Array();

    var vm_query_store = new Ext.data.JsonStore({
//        url:"/dashboard/get_canned_custom_list?node_level="+type+"&lists_level="+stackone.constants.VMS,
        url: "/cloud_dashboard/vdc_info?vdc_id="+node_id+"&type=TESTING",
        root: 'info',
        successProperty:'success',
        fields:['value'],
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    vm_query_store.load();

     var tb_lbl=new Ext.form.Label({
        html:getHdrMsg("负载最高的50台虚拟机CPU利用率")
    });


    var vmquery_combo=new Ext.form.ComboBox({
        id: 'vm_id',
        fieldLabel: _('查询名称'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择类型"),
        store: vm_query_store,
        width:220,
        displayField:'value',
        valueField:'value',
        editable:false,
        typeAhead: true,
        minListWidth:50,
        mode:'local',
        tpl: '<tpl for="."><div class="x-combo-list-item">{value}</div><tpl if="xindex == 4"><hr /></tpl></tpl>',
        forceSelection: true,
        selectOnFocus:true,
        listeners:{
            select:function(combo,record,index){
                if (combo.getValue()==stackone.constants.TOP50BYCPUVM){
                    tb_lbl.setText(getHdrMsg(""),false);
                }
//                else if(combo.getValue()==stackone.constants.TOP50BYMEMVM){
//
//                    tb_lbl.setText(getHdrMsg("The table shows top 50 Virtual Machines by current Memory Utilization(%)."),false);
//                }
//                else if(combo.getValue()==stackone.constants.DOWNVM){
//
//                    tb_lbl.setText(getHdrMsg("The table shows top 50 Down Virtual Machines"),false);
//
//                }
//                else if(combo.getValue()==stackone.constants.RUNNINGVM){
//
//                    tb_lbl.setText(getHdrMsg("The table shows top 50 Running Virtual Machines"),false);
//
//                }
                else{

                    var url="/dashboard/get_custom_search?name="+combo.getValue()+"&lists_level="+stackone.constants.VMS;
                    var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    var info=response.info;
                                    tb_lbl.setText(getHdrMsg("List of Top "+info.max_count+" Virtual Machines with condition : "+combo.getValue()),false);
                                }else{
//                                    Ext.MessageBox.alert(_("Failure"),response.msg);
                                }
                            },
                            failure: function(xhr){
//                                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                            }
                        });
                }

                vms_list_store.load({
                    params:{
                        canne:combo.getValue()
                    }
                });
            }
        }

    });


    var custom_btn=new Ext.Button({
        tooltip:'自定义搜索',
        tooltipType : "title",
        icon:'icons/add_search.png',
        id: 'add',
        height:120,
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                CustomSearchDefList(type,node_id,stackone.constants.VMS,vm_query_store);
//                showWindow(_("Custom Search")+":- ",530,450,CustomSearchDefList(type,node_id,stackone.constants.VMS,vm_query_store),null,false,false);
            }
        }
    });



    items.push(tb_lbl);
    items.push({xtype:'tbfill'});
    items.push(_('搜索: '));
    items.push(new Ext.form.TextField({
        //fieldLabel: _('Search'),
        name: 'search',
        //id: 'search_summary',
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {
                grid.getStore().filter('name', field.getValue(), false, false);
            }
        }
    }));

//    items.push(vmquery_combo);
//    items.push(custom_btn);

    var toolbar = new Ext.Toolbar({
        items: items
    });


    var vms_list_store = new Ext.data.JsonStore({
//        url:"/dashboard/dashboard_vm_info?node_id="+node_id+"&type="+type,
        url: "/cloud_dashboard/vdc_info?vdc_id="+node_id+"&type=VDC_VM_VM_LIST",
        root: 'info',
        successProperty:'success',
        fields:['node_id','name','state','cpuussage','cpu','mem','storage','private_ip','public_ip','region','instance_type', 'template', 'vdc_id', 'cp_type'],
        listeners:{
            beforeload:function(obj,recs,opts){
                if(prntPanel.getEl()){
                    prntPanel.getEl().mask();
                }
            },
            load:function(obj,recs,opts){
               //insert_dummyrecs(obj);
               prntPanel.getEl().unmask();
            },
            loadexception:function(obj,opts,res,e){
                prntPanel.getEl().unmask();
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    vms_list_store.load();

    var grid = new Ext.grid.GridPanel({
//        title:'Performance Details',
        store: vms_list_store,
        colModel:vms_colModel,
        stripeRows: true,
        frame:false,
        //id:'summary_grid',
        width:820,
        autoExpandColumn:0,
//        autoHeight:true,
        autoExpandMax:300,
        autoExpandMin:150,
        height:150,
        maxHeight:100,
        enableHdMenu:false,
        tbar:toolbar
       ,listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            rowdblclick :function(grid,rowIndex,e) {
                handle_rowclick(grid,rowIndex,"click",e);
            }
        }
    });

//    var window = new Ext.Window({
//        //title:'VM Information',
//        width: 820,
//        height:250,
//        modal:true,
//        layout: 'fit',
//        plain:true,
//        items:[grid]
//    });
//    window.show();

    return grid;
}

function vdc_networking_page(mainpanel,node_id,node){
    if(mainpanel.items)
        mainpanel.removeAll(true);

    var panel1 = new Ext.Panel({
        width:'100%',
        height: '30%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:3px',//;padding-right:5px;
        layout:'column'
    });
    var panel2 = new Ext.Panel({
        width:'100%',
        height: '30%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:3px',//;padding-right:5px;
        layout:'column'
    });
    var panel3 = new Ext.Panel({
        width:'100%',
        height: '30%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:3px',//;padding-right:5px;
        layout:'column'
    });
     var panel1_1=new Ext.Panel({
        width:'100%',
        height: '100%',
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:10px;padding-right:10px;padding-bottom:5px;padding-top:10px;',
        bodyStyle:'padding-top:7px;',
        layout:'fit'
    });
   
    var panel2_1=new Ext.Panel({
        width:'100%',
        height: '100%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:7px;',
        layout:'fit'
    });
    var panel3_1=new Ext.Panel({
        width:'100%',
        height: '100%',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-top:7px;',
        layout:'fit'
    });
     var label1_1=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("定义的网络")+'<br/></div>'
    });
    panel1_1.add(vdc_networking_definedNW(node_id,node));
    panel2_1.add(vdc_networking_privateNW(node_id, node));
    panel3_1.add(vdc_networking_publicIPs(node_id, node));


    panel1.add(panel1_1);
    panel2.add(panel2_1);
    panel3.add(panel3_1);


    var networkingpanel = new Ext.Panel({
        height:"100%",
        width:"100%",
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-left:10px;padding-right:10px',
        items:[panel1,panel2,panel3]
    });
    mainpanel.add(networkingpanel);
    networkingpanel.doLayout();
    mainpanel.doLayout();

    


}


////////////////////// draw_grid  (GRAPH) ////////////////////////////


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
         header: "提供者类型",
         width: 135,
         dataIndex: 'provider_type',
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
             fields: [ 'task_id','taskname','username','provider_type','entity_name','start_time',
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
                        Ext.MessageBox.confirm(_("确认"),_("确定要删除任务"+task_name), function(id){
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


function vdc_overview_disk_grid_fun(node_id,node){

    var server_dvce_columnModel = new Ext.grid.ColumnModel([
//    {
//        header: _("Device"),
//        width: 150,
//        dataIndex: 'file_system',
//        //css:'font-weight:bold;',
//        sortable:true
//    },
//    {
//        header: _("Mounted On"),
//        width: 150,
//        sortable:true,
//        dataIndex: 'mounted_on'
//    },
//    {
//        header: _("Size"),
//        width: 100,
//        dataIndex: 'size',
//        sortable:true
//    }
]);

    var server_dvce_store = new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=DISK_INFO",
        root: 'info',
        fields: ['file_system','mounted_on','size'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    server_dvce_store.load({
        params:{
            node_id:node_id
        }
    });

   var label_dvce=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("磁盘")+'</div>'
   });
	var vdc_dvce_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: server_dvce_store,
        colModel:server_dvce_columnModel,
        stripeRows: true,
        frame:false,
        //title:_("Mounted Devices"),
        autoExpandColumn:0,
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

	return vdc_dvce_grid;

}

function vdc_overview_network_grid_fun(node_id,node){

    var vdc_interface_columnModel = new Ext.grid.ColumnModel([
//    {
//        header: _("Name"),
//        width: 110,
//        dataIndex: 'interface_name',
//        //css:'font-weight:bold;',
//        sortable:true
//    },
//    {
//        header: _("IP Address"),
//        width: 300,
//        sortable:true,
//        dataIndex: 'ip_address'
//    }
]);

    var vdc_interface_store = new Ext.data.JsonStore({
        url: "/dashboard/server_info?type=INTERFACE_INFO",
        root: 'info',
        fields: ['interface_name','ip_address'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    vdc_interface_store.load({
        params:{
            node_id:node_id
        }
    });
   var label_interface=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("网络")+'</div>'
   });

	var vdc_interface_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: vdc_interface_store,
        colModel:vdc_interface_columnModel,
        stripeRows: true,
        //title:_("Available Interfaces"),
        frame:false,
        autoExpandColumn:0,
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

	return vdc_interface_grid;

}



function svdc_config_grid(node_id,node,config){

    var vdc_config_store = new Ext.data.JsonStore({
        url: "/dashboard/server_info?type="+config+"_INFO",
        root: 'info',
        fields: ['label','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    vdc_config_store.load({
        params:{
            node_id:node_id
        }
    });

   var label_config=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+format(_("{0}信息"),config)+'</div>'
   });

    var vdc_config_grid = new Ext.grid.GridPanel({
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
            {header: "", width: 150, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'label'},
            {header: "", width: 280, sortable: false, dataIndex: 'value',renderer:UIMakeUP,css: 'white-space: normal !important;'}
        ],
        store:vdc_config_store
        ,tbar:[label_config]
    });

    return vdc_config_grid

}

function vdc_usage_chart(node_id,node,metric){
    
    var vdc_usage_store = new Ext.data.Store({
        url: "/dashboard/server_usage?node_id="+node_id+"&metric="+metric,
        reader: new Ext.data.JsonReader({
            root: 'info',
            fields: ['label', 'value']
        })
    });

    var vdc_usage_pie = new Ext.ux.PieFlot({
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

    vdc_usage_store.on('load',
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
        vdc_usage_pie
    );

    vdc_usage_store.load();

    return vdc_usage_pie;
}



function topNCloudvms(node_id,node,metric){//,top5vmmetric_combo

//   alert(metric);
var label=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+format(_("负载最高的虚拟机 {0}利用率"),metric)+'</div>'
    });
 var enttype_store1 = new Ext.data.JsonStore({
        url: '/cloud/get_top5vm_matric?cp_type='+node.attributes.cp_type,
        root: 'nodes',
        fields: ['name','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_( "错误"),store_response.msg);
            }
            ,load:function(store,recs,options){

            }
        }
    });
    enttype_store1.load();
    var enttype_combo1=new Ext.form.ComboBox({
        triggerAction:'all',
        store: enttype_store1,
        emptyText :_("选择"),
        fieldLabel:'Type',
        displayField:'name',
        valueField:'value',
        width: 130,
        labelStyle: 'width:50px;',
        ctCls:"combo_ct",
        forceSelection: true,
        mode:'local',
        value:'CPU',
        listeners:{
            select:function(combo){
                
                top_grid.getStore().load({
                                  params:{
                                    node_id:node_id,
                                    metric:combo.getValue(),
                                    node_type:node.attributes.nodetype
                                }

//                                url: "/cloud_dashboard/topNCloudvms?node_id="+node_id+"&metric="+combo.getValue()+"&node_type="+node.attributes.nodetype
                            });
//                            label.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
                            label.setText(gettopNCloudvmsMsg(combo.getValue()),false);

//             loadtopNvmstore(node_id,node,combo.getValue())
//             topNCloudvms(node_id, node, combo.getValue(),combo)
            }
        }
    });
var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;&nbsp;&nbsp;&nbsp;<div style="width:320px"/>')
    });
    var str = "";
    var showBarFun = "";
    
       
        str = "利用率(%)";
        showBarFun = showBar;
  
    

    var top_cm = new Ext.grid.ColumnModel([
        {
            header: _(""),
            width: 110,
            dataIndex: 'vm_id',
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
//         {
//            header: _("Region"),
//            width: 150,
//            dataIndex: 'region',
//            //css:'font-weight:bold;',
//            sortable:true
//        },

        {
            header: format(_("{0}"),str),
            width: 330,
            sortable:true,
            dataIndex: 'usage',
            renderer:showBarFun
        }
    ]);
    

    var top_store = new Ext.data.JsonStore({
        url: "/cloud_dashboard/topNCloudvms?",
        root: 'info',
        fields: ['vm_id','vm','usage','node_id','cp_type'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            },
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            rowdblclick :function(grid,rowIndex,e) {
                handle_rowclick(grid,rowIndex,"click",e);
            }
        }
    });
   top_store.load( {params:{
                                    node_id:node_id,
                                    metric:metric,
                                    node_type:node.attributes.nodetype
   }});

	var top_grid = new Ext.grid.GridPanel({
//        disableSelection:true,
        store: top_store,
        id:'top_grid',
        colModel:top_cm,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
//        autoExpandMax:300,
//        autoExpandMin:80,
        //border:false,
        enableHdMenu:false,
        autoScroll:true,
        width:'100%',
        //autoExpandColumn:1,
        height:340
        ,tbar:[label,{xtype:"tbfill"},enttype_combo1]//top5vmmetric_combo
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
function gettopNCloudvmsMsg(metric){

    return '<div class="toolbar_hdg">'+format(_("负载最高虚拟机 {0}利用率"),metric)+'</div>';
}


//////////////////////// vdc_templateinfo_page ///////////////////////////



function vdc_templateinfo_page(mainpanel,vdc_id, vdc_count)
{

    if(mainpanel.items){
        mainpanel.removeAll(true);
    }

    var imagehomepanel=new Ext.Panel({
        height:"100%",
        width:"100%",
        layout: 'fit',
        bodyStyle:'padding-left:10px;padding-right:10px',
        border:false,
        bodyBorder:false
    });



    var topPanel = new Ext.Panel({
        collapsible:false,
        //title:format(_("Available Template Groups Details")),
        height:'100%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false,
        layout:'fit',
        items:[imagehomepanel]
    });
    
//    var summary_panel = new Ext.Panel({
//        collapsible:false,
//        //height:100,
//        width:'100%',
//        border:false,
//        bodyBorder:false,
//        layout:'fit'
//    });

    var template_list_panel = new Ext.Panel({
        collapsible:false,
        height:'100%',
        bodyStyle:'padding-top:10px;',
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'fit'
    });

//     var imagestore_summary_panel = new Ext.Panel({
//        collapsible:false,
//        height:'100%',
//        width:'100%',
//        border:false,
//        bodyStyle:'padding-top:10px;',
//        bodyBorder:false,
//        layout:'fit'
//    });
//    var summary_grid = vdc_folder_overview_summary_grid_fun(vdc_folder_id);

    var template_list_grid = vdc_template_list_grid_fun(vdc_id);

//    summary_panel.add(summary_grid);
    template_list_panel.add(template_list_grid);
//    imagehomepanel.add(dummyPanel);


//    imagehomepanel.add(summary_panel);
    imagehomepanel.add(template_list_panel);
//    imagehomepanel.add(imagestore_summary_panel);
    mainpanel.add(topPanel);

    mainpanel.doLayout();

}




function vdc_template_list_grid_fun(vdc_id){

    var template_list_store_columnModel = new Ext.grid.ColumnModel([
//     {
//        header: _(""),
//        width:50,
//        sortable: false,
//        dataIndex: 'desc',
//        renderer: show_vdc_list_detail_link
//    },

    {
        header: _("名称"),
        width: 200,
        sortable: true,
        dataIndex: 'name'
    },
     {
        header: _("Root设备类型"),
        width: 70,
        sortable: true,
        dataIndex: 'root_device_type'
     },
     {
        header: _("Root设备"),
        width: 150,
        dataIndex: 'root_device_name',
        sortable:true
    },
     {
        header: _("内核"),
        width: 100,
        dataIndex: 'kernel_id',
        sortable:true
    },
    {
        header: _("Ramdisk"),
        width: 100,
        dataIndex: 'ramdisk_id',
        sortable:true
//        align:'right'

    },
     {
        header: _("Platform"),
        width: 150,
        dataIndex: 'platform',
        sortable:true
    },
     {
        header: _("架构"),
        width: 150,
        dataIndex: 'architecture',
        sortable:true
    },
    {
        dataIndex: 'vdc_id',
        sortable:false,
        hidden: true
    },
    {
        header: _(""),
        dataIndex: 'id',
        sortable:false,
        hidden: true
    }
    ]);


    var template_list_store = new Ext.data.JsonStore({
        url: "/cloud_dashboard/vdc_info?vdc_id="+vdc_id+"&type=VDC_TEMPLATE_TEMP_LIST",
        root: 'info',
        fields: ['id', 'name', 'root_device_type', 'root_device_name', 'kernel_id', 'ramdisk_id', 'platform', 'architecture'],
        successProperty:'success',
        listeners:{

            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }

        }
    });

    template_list_store.load()
    var lbl_msg='虚拟数据中心信息';
    var tb_lbl=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+lbl_msg+'</div>'
    });

    var items=new Array();
    items.push(tb_lbl);
    items.push({xtype:'tbfill'});
    items.push(_('搜索: '));
    items.push(new Ext.form.TextField({
        name: 'search',
        id: 'search_summary',
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {
                template_list_summary_grid.getStore().filter('name', field.getValue(), false, false);
            }
        }
    }));
    var toolbar = new Ext.Toolbar({
        items: items
    });

    var template_list_summary_grid = new Ext.grid.GridPanel({
//        disableSelection:true,
        store: template_list_store,
        colModel:template_list_store_columnModel,
        id:'template_list_summary_grid_id',
        stripeRows: true,
        frame:false,
        width:"100%",
        autoExpandColumn:1,
        autoExpandMin:150,
        height:400,
        enableHdMenu:false,
        tbar:toolbar
        ,listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            rowdblclick :function(grid,rowIndex,e) {
                handle_rowclick(grid,rowIndex,"click",e);
            }
        }
    });


    return template_list_summary_grid;

}



/////////////////////////////////////////////////////////////////////////////
//////////////////////////////// VDC Folder ////////////////////////////////
/////////////////////////////////////////////////////////////////////////////



function vdc_folder_summary_page(mainpanel,vdc_folder_id, vdc_folder_count)
{

    if(mainpanel.items){
        mainpanel.removeAll(true);
    }

    var imagehomepanel=new Ext.Panel({
        height:"100%",
        width:"100%",
        //layout: 'fit',
        bodyStyle:'padding-left:10px;padding-top:10px;padding-right:10px',
        border:false,
        bodyBorder:false
    });



    var topPanel = new Ext.Panel({
        collapsible:false,
        //title:format(_("Available Template Groups Details")),
        height:'75%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false,
        items:[imagehomepanel]
    });

    var panel1 = new Ext.Panel({
         width:'100%',
        height: '100%',
         border:false,
         bodyBorder:false,
//        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });

    var dummy_panel1 = new Ext.Panel({
        width:'1%',
        html:'&nbsp;',
        border:false,
        bodyBorder:false
    });


    var summary_panel = new Ext.Panel({
        collapsible:false,
        height:'100%',
        width:'49.5%',
        border:false,
        bodyBorder:false,
        layout:'fit'
    });

    var vdc_list_panel = new Ext.Panel({
        collapsible:false,
        //height:100,
        bodyStyle:'padding-top:10px;',
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'fit'
    });

    var label1_1=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("虚拟数据中心提供者")+'<br/></div>'
    });

    var pichart_panel = new Ext.Panel({
        height:230,
        width:'48%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        //,bodyStyle:';padding-right:15px;'
        ,tbar:[label1_1]
    });

    pichart_panel.add(vms_per_cp_pichart_fun(vdc_folder_id));

//     var imagestore_summary_panel = new Ext.Panel({
//        collapsible:false,
//        height:'100%',
//        width:'100%',
//        border:false,
//        bodyStyle:'padding-top:10px;',
//        bodyBorder:false,
//        layout:'fit'
//    });

    var summary_grid = vdc_folder_overview_summary_grid_fun(vdc_folder_id);
    var vm_list_summary_grid = vdc_folder_overview_list_grid_fun(vdc_folder_id);

    summary_panel.add(summary_grid);
    vdc_list_panel.add(vm_list_summary_grid);
//    imagehomepanel.add(dummyPanel);

    panel1.add(summary_panel);
    panel1.add(dummy_panel1);
    panel1.add(pichart_panel);

    imagehomepanel.add(panel1);
//    imagehomepanel.add(summary_panel);
//    imagehomepanel.add(pichart_panel);
    imagehomepanel.add(vdc_list_panel);
//    imagehomepanel.add(imagestore_summary_panel);
    mainpanel.add(topPanel);

    mainpanel.doLayout();

}

function vdc_folder_overview_summary_grid_fun(vdc_folder_id){

     var label_summary=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_task'
    });

    var vdc_folder_store =new Ext.data.JsonStore({
        url:"/cloud_dashboard/vdc_folder_info?vdc_folder_id="+vdc_folder_id+"&type=VDC_FOLDER_OVERVIEW_SUMMARY",
        root: 'result',
        fields: ['name','value', 'type'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    vdc_folder_store.load();


    var vdc_folder_grid = new Ext.grid.GridPanel({
        //title:'Template Details',
        disableSelection:true,
        stripeRows: true,
        autoHeight:false,
        border:true,
//        cls:'hideheader',
        width: '100%',
        height: 230,
        enableHdMenu:false,
        enableColumnMove:false,
        autoScroll:true,
        autoExpandColumn:1,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [
            {
                header   : '',
                width: 200,
                sortable: false,
                css:'font-weight:bold; color:#414141;',
                dataIndex:'name',
				renderer:nvUIMakeUP
            },
            {
                header: '',
                width: 300,
                sortable: false,
                dataIndex:'value',
                renderer:UIMakeUP
            }

        ],
        store:vdc_folder_store,
        tbar:[label_summary]
    });

    return vdc_folder_grid;

}


function vms_per_cp_pichart_fun(vdc_folder_id){

    var vms_per_cp_store = new Ext.data.Store({
        url:"/cloud_dashboard/vdc_folder_info?vdc_folder_id="+vdc_folder_id+"&type=VDC_FOLDER_OVERVIEW_PICHART",
        reader: new Ext.data.JsonReader({
            root: 'result',
            fields: ['label', 'value']
        })
    });

    var vms_per_cp_pie1 = new Ext.ux.PieFlot({
        pies: {
            show: true,
            autoScale: true,
            fillOpacity: 1,
            labelFormatter: function(label, value, percent, textValue, pie, serie, options) {
                if(value == 0)
                {
                    return '';
                }
                return textValue + '% ('+value+')';
//                return value;
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

    vms_per_cp_store.on('load',
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
        vms_per_cp_pie1
    );

    vms_per_cp_store.load();

    return vms_per_cp_pie1;
}



function vdc_folder_overview_list_grid_fun(vdc_folder_id){

    var vdc_list_store_columnModel = new Ext.grid.ColumnModel([
//     {
//        header: _(""),
//        width:50,
//        sortable: false,
//        dataIndex: 'desc',
//        renderer: show_vdc_list_detail_link
//    },

    {
        header: _("名称"),
        width: 200,
        sortable: true,
        dataIndex: 'vdc'
    },
     {
        header: _("虚拟机"),
        width: 100,
        sortable: true,
        dataIndex: 'vm_num'
     },
     {
        header: _("CPUs"),
        width: 150,
        dataIndex: 'cpus',
        align:'right',
        sortable:true
    },
     {
        header: _("内存(MB)"),
        width: 150,
        dataIndex: 'memory',
        align:'right',
        sortable:true
    },
    {
        header: _("存储(GB)"),
        width: 150,
        dataIndex: 'storage',
        align:'right',
        sortable:true
//        align:'right'

    },
    {
        dataIndex: 'vdc_id',
        sortable:false,
        hidden: true
    }
//    {
//        header: _(""),
//        dataIndex: 'vdc_search',
//        sortable:false,
//        hidden: true
//    },
    ]);


    var vdc_list_store = new Ext.data.JsonStore({
        url: "/cloud_dashboard/vdc_folder_info?vdc_folder_id="+vdc_folder_id+"&type=VDC_FOLDER_OVERVIEW_VDC_LIST",
        root: 'result',
        fields: ['vdc', 'vm_num', 'memory', 'storage', 'cpus', 'vdc_id', 'node_id', 'cp_type'],
        successProperty:'success',
        listeners:{

            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }

        }
    });

    vdc_list_store.load()
    var lbl_msg='虚拟数据中心';
    var tb_lbl=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+lbl_msg+'</div>'
    });

    var items=new Array();
    items.push(tb_lbl);
    items.push({xtype:'tbfill'});
    items.push(_('搜索: '));
    items.push(new Ext.form.TextField({
        name: 'search',
        id: 'search_summary',
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {
                vdc_list_summary_grid.getStore().filter('vdc', field.getValue(), false, false);
            }
        }
    }));
    var toolbar = new Ext.Toolbar({
        items: items
    });

    var vdc_list_summary_grid = new Ext.grid.GridPanel({
//        disableSelection:true,
        store: vdc_list_store,
        colModel:vdc_list_store_columnModel,
        id:'vdc_list_summary_grid_id',
        stripeRows: true,
        frame:false,
        width:"100%",
        autoExpandColumn:1,
        autoExpandMin:150,
        height:400,
        enableHdMenu:false,
        tbar:toolbar
        ,listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            rowdblclick :function(grid,rowIndex,e) {
                handle_rowclick(grid,rowIndex,"click",e);
            }
        }
    });


    return vdc_list_summary_grid;

}


function show_vdc_list_detail_link(data,cellmd,record,row,col,store) {
        var vdc_id = record.get("vdc_id");
//        var desc = record.get("desc");
//        var fn1 = "display_edit_image_settings('" + node_id + "','" +  template_name + "')";
        var fn1 = "display_vdc_details('" + vdc_id + "')";

        var returnVal = '<a href="#" onClick= ' + fn1 + '><img title="虚拟数据中心详情" src=" icons/information.png "/> </a>';

        return returnVal;
}


function format_date_value(value){
      var pad_zero="0";
      if (value.length<2)
          value=pad_zero+value;
      return value;
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

function nvUIMakeUP(value, meta, rec) {
    var dict = {'Virtual Data Centers':'虚拟数据中心',
	            'Providers':'提供者',
				'Virtual Machines':'虚拟机',
				'CPUs':'CPU数量',
				'Memory (MB)':'内存',
				'Storage (GB)':'存储'
	 };
    return dict[rec.get('name')];
}

function show_quota_summary(vdc_id){

    showWindow(_("配额概览"),550,450,quota_summary(vdc_id),null,true);
    
}
function quota_summary(vdc_id){
    var acc_store = new Ext.data.JsonStore({
        url: "/cloud/get_accountsforvdc?vdcid="+vdc_id,
        root: 'info',
        fields: ['name','value'],
        sortInfo:{
            field:'value',
            direction:'ASC'
        },
        successProperty:'success',
        listeners:{
            load:function(obj,recs,f){
                acc_combo.setValue(recs[0].get('value'));
                acc_combo.fireEvent('select',acc_combo,recs[0],0);
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    }
    );
    acc_store.load();
    var acc_combo=new Ext.form.ComboBox({
            width: 175,
            id:"acc_combo",
            fieldLabel: _('账户'),
            allowBlank:false,
            triggerAction:'all',
            store:acc_store,
            displayField:'name',
            valueField:'value',
            forceSelection: true,
            mode:'local',
            listWidth:175,
            listeners:{
                select:function(combo,record,index){
                      Ext.getCmp("quota_grid").getStore().load(
                      {
                            params:{
                                vdc_id:vdc_id,
                                account_id:acc_combo.getValue()

                            }

                        }
                      );
                }
            }
        });
    var quota_grid=create_quota_grid(false);
//     var q_ok=new Ext.Button({
//        name: 'q_ok',
//        id: 'q_ok',
//        text:_("OK"),
//        icon:'icons/accept.png',
//        cls:'x-btn-text-icon',
//        listeners: {
//            click: function(btn) {
//                        closeWindow();
//                    }
//
//        }
//    });

    var q_cancel=new Ext.Button({
        name: 'q_cancel',
        id: 'q_cancel',
        text:_("关闭"),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow();
            }
        }
    });
    var q_panel=new Ext.Panel({
        height:420,
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        bbar:[{
            xtype:'tbfill'
        },q_cancel],
        items:[acc_combo,quota_grid]
    });
    
    return q_panel;
}
function vdc_networking_definedNW(node_id,node){

    var vdc_definedNW_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width: 200,
        dataIndex: 'name',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("接口"),
        width: 260,
        sortable:true,
        dataIndex: 'interface',
        hidden:true
    },
    {
        header: _("VLAN ID"),
        width: 260,
        sortable:true,
        dataIndex: 'vlanid',
        align:'right',
        hidden:true
    },
    {
        header: _("IP范围"),
        width: 390,
        sortable:true,
        dataIndex: 'iprange'
    }]);


    var vdc_definedNW_store = new Ext.data.JsonStore({
        url:"/cloud_dashboard/vdc_info?vdc_id="+node_id+"&type=VDC_NETWORKING_DEFINEDNW",
        root: 'info',
        fields: ['name', 'interface', 'vlanid','iprange'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    vdc_definedNW_store.load();


    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("定义的网络")+'</div>'
    });

    var vdc_definedNW_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: vdc_definedNW_store,
        colModel:vdc_definedNW_columnModel,
        stripeRows: true,
        frame:false,
//        autoExpandColumn:3,
//        autoExpandMax:300,
//        border:false,
        enableHdMenu:true,
        autoScroll:true,
 
        width:'100%',
        //autoExpandColumn:1,
        height:180
        ,tbar:[label_strge]
    });

	return vdc_definedNW_grid;

}
function vdc_networking_privateNW(node_id, node){

    var vdc_privateNW_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width: 200,
        dataIndex: 'name',
        //css:'font-weight:bold;',
        sortable:true
    },
//    {
//        header: _("Interface"),
//        width: 180,
//        sortable:true,
//        dataIndex: 'interface'
//    },
//    {
//        header: _("VLANID"),
//        width: 180,
//        sortable:true,
//        dataIndex: 'vlanid'
//    },
    {
        header: _("IP详情"),
        width: 260,
        sortable:true,
        dataIndex: 'ipdetails'
    },
    {
        header: _("已用私有IP"),
        width: 150,
        sortable:true,
        dataIndex: 'privateipsused',
        align:'right'
    },
    {
        header: _("NATED"),
        width: 150,
        sortable:true,
        dataIndex: 'nated'
    }]);



    var vdc_privateNW_store = new Ext.data.JsonStore({
        url:"/cloud_dashboard/vdc_info?vdc_id="+node_id+"&type=VDC_NETWORKING_PRIVATENW",
        root: 'info',
        fields: ['name', 'interface', 'vlanid','ipdetails','privateipsused','nated'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    vdc_privateNW_store.load();


    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("私有网络")+'</div>'
    });

    var vdc_privateNW_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: vdc_privateNW_store,
        colModel:vdc_privateNW_columnModel,
        stripeRows: true,
        frame:false,
        //autoExpandColumn:0,
        //autoExpandMax:300,
//        border:false,
        enableHdMenu:true,
        //autoScroll:false,

        width:'100%',
        //autoExpandColumn:1,
        height:180
        ,tbar:[label_strge]
    });

	return vdc_privateNW_grid;

}
function vdc_networking_publicIPs(node_id, node){

    var vdc_publicIPs_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("IP地址"),
        width: 150,
        dataIndex: 'ipaddress',
        //css:'font-weight:bold;',
        sortable:true
    },
    {
        header: _("虚拟机"),
        width: 260,
        sortable:true,
        dataIndex: 'virtualmachine'
    },
    {
        header: _("私有IP"),
        width: 150,
        sortable:true,
        dataIndex: 'privateip'
    },
    {
        header: _("分配"),
        width: 200,
        sortable:true,
        dataIndex: 'assignedat'
    }]);



    var vdc_publicIPs_store = new Ext.data.JsonStore({
        url:"/cloud_dashboard/vdc_info?vdc_id="+node_id+"&type=VDC_NETWORKING_PUBLICIPS",
        root: 'info',
        fields: ['ipaddress', 'virtualmachine', 'privateip','assignedat'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    vdc_publicIPs_store.load();


    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("公共IPs")+'</div>'
    });

    var vdc_publicIPs_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: vdc_publicIPs_store,
        colModel:vdc_publicIPs_columnModel,
        stripeRows: true,
        frame:false,
        autoExpandColumn:0,
        autoExpandMax:300,
//        border:false,
        enableHdMenu:true,
        //autoScroll:true,

        width:'100%',
        //autoExpandColumn:1,
        height:180
        ,tbar:[label_strge]
    });

	return vdc_publicIPs_grid;

}



