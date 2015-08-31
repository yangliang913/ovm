/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function vmcloud_summary_page(mainpanel,node_id,node){
//    alert("hai hello welcome to vmpage");
    if(mainpanel.items)
        mainpanel.removeAll(true);

    var label1_1=new Ext.form.Label({
        html:getChartHdrMsg(node.text,"Hourly","CPU")
    });

    var avg_fdate="",avg_tdate="";
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
                text: _('OK'),
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
                            redrawChart(stackone.constants.CLOUD_VM,type_combo.getValue(),node_id,node.text,
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
                text: _('OK'),
                listeners: {
                    click: function(btn) {
                        if(cust.validate()){
                            cust_window.hide();
                            fdate=cust.fromTime();
                            tdate=cust.toTime();
                            redrawChart(stackone.constants.CLOUD_VM,type_combo.getValue(),node_id,node.text,
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
            redrawChart(stackone.constants.CLOUD_VM,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'vm_cpu_chart'+node_id,true,panel1_1,null,avg_fdate,avg_tdate);
            label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
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
		        redrawChart(stackone.constants.CLOUD_VM,type_combo.getValue(),node_id,node.text,
                            period_combo.getValue(),fdate,tdate,'vm_chart'+node_id,true,panel1_1,null,avg_fdate,avg_tdate);
        label1_1.setText(getChartHdrMsg(node.text,period_combo.getRawValue(),type_combo.getRawValue()),false);
    });


    var vm_grid=cloudvm_info_grid(node_id);

    var panel1 = new Ext.Panel({
        height:500,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column'
    });
    var panel1_0 = new Ext.Panel({
        height:500,
        width:'33%',
        border:false,
        bodyBorder:false
        ,layout:'fit'
    });
    var panel1_1 = new Ext.Panel({
        height:250,
       // width:'69%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        ,tbar:[' ',label1_1,{xtype:'tbfill'},avg_button,'-',period_combo,'-',type_combo]
    });

    var panel2_1 = new Ext.Panel({
        height:500,
        width:'66%',
        border:false,
        bodyBorder:false
        //,layout:'fit'
    });

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

    var task_grid=display_tasks_cloudvm(node_id,node);
   
     var panel1_2 = new Ext.Panel({
        height:250,
       // width:'69%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false        
    });
    panel1_2.add(task_grid)
    
    panel1_0.add(vm_grid);
    panel1.add(panel1_0);
    panel1.add(dummy_panel1);

    panel2_1.add(panel1_1);
    panel2_1.add(dummy_panel2);
    panel2_1.add(panel1_2)
    
    panel1.add(panel2_1);


    redrawChart(stackone.constants.CLOUD_VM,stackone.constants.CPU,node_id,node.text,
                    stackone.constants.HRS12,fdate,tdate,'vm_cpu_chart'+node_id,true,panel1_1,null,avg_fdate,avg_tdate);


    var topPanel = new Ext.Panel({
        collapsible:false,
        height:'100%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false
        ,bodyStyle:'padding-right:5px;',
        items:[panel1]
    });

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

function mvUIMakeUP(value, meta, rec) {
    var dict = {'Name':'名称',
	            'Virtual Data Center':'虚拟数据中心',
				'Template':'模板',
				'Status':'状态',
				'Memory (MB)':'内存',
				'Storage (GB)':'存储',
				'Virtualization':'虚拟化平台',
				'Instance Id':'实例Id',
				'Public DNS':'公共DNS'
	 };
	if (dict[rec.get('name').trim()]) {
		return dict[rec.get('name').trim()];
	} else {
		return rec.get('name');
	}
};	

function zmUIMakeUP (value, meta, rec) {
    var dict = { 'Name':'名称',
	             'Vcpu':'虚拟机CPU',
				 'Memory (MB)':'内存',
				 'Storage (GB)':'存储',
				 'Instance Id':'实例Id',
				 'Name':'名称',
				 'IaaS Type':'IaaS类型'
	 };
	 return dict[rec.get('name')];

};

function cloudvm_info_grid(node_id){
    var vm_info_store =new Ext.data.JsonStore({
        url: "/cloud/cloudvm_info?type=VM_INFO",
        root: 'info',
        fields: ['name','value','type','action','chart_type'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
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
            {header: "", width: 140, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'name', renderer:mvUIMakeUP},
            {header: "", width: 200, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_info_store
        ,tbar:[label_strge]
    });

    return vm_grid;
}


function cloudvm_availability_chart(node_id,node){
    var vm_avail_store = new Ext.data.Store({
        url: "/cloud/cloudvm_availability?node_id="+node_id,
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


function cloudvm_info_gridext(node_id){
    var vm_info_store =new Ext.data.JsonStore({
        url: "/cloud/cloudvm_info?type=VM_INFO_EXT",
        root: 'info',
        fields: ['name','value','type','action','chart_type'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
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

function vmcloud_config_page(configPanel,node_id,node){
    if(configPanel.items)
        configPanel.removeAll(true);
	
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

    var template_info=get_cloudtemplateinfo(node_id);
    var general_info=get_cloudgeneralinfo(node_id);
    
    var panel1_1=new Ext.Panel({
        width:'49.5%',
        height: 250,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel1_2=new Ext.Panel({
        width:'49.5%',
        height: 250,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });

    panel1_1.add(general_info);
    panel1_2.add(template_info);
    panel1.add(panel1_1);
    panel1.add(dummy_panel1);
    panel1.add(panel1_2);

    var storage_info=get_cloudstorageinfo(node_id,node);
  
    var panel2_1=new Ext.Panel({
        width:'49.5%',
        height: 250,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
    var panel2_2=new Ext.Panel({
        width:'49.5%',
        height: 250,
        border:false,
        bodyBorder:false,
        //bodyStyle:'padding-left:5px;padding-right:3px;padding-top:10px;',
        layout:'fit'
    });
      panel2_1.add(storage_info);
     var bottomPanel = new Ext.Panel({
//        collapsible:true,
        height:'100%',
        width:'100%',
        border:false,
//        cls:'headercolor',
        bodyBorder:false,
        bodyStyle:'padding-left:10px;padding-right:5px;',
        items:[panel1,panel2]
    });  

     vdcid=node.parentNode.parentNode.id;
     var url = "/cloud/get_cp_feature_set?vdc_id="+vdcid;
     var ajaxReq=ajaxRequest(url,0,"POST",true);
     ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success)
            {
                
                var nws_info=get_cloudnwsinfo(node_id,response.info)
               
                panel2_2.add(nws_info);
                panel2.add(panel2_1);
                panel2.add(dummy_panel2);
                panel2.add(panel2_2);


   
                 configPanel.add(bottomPanel);
                 bottomPanel.doLayout();
                configPanel.doLayout();


            }else{
                Ext.MessageBox.alert(_("失败"),_("无法加载供应商."));
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });


    
}

function get_cloudgeneralinfo(node_id){

    var vm_general_store =new Ext.data.JsonStore({
//        url: "vm_general_info",
        url: "/cloud/cloudvm_info?type=GENERAL_INFO",
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
    vm_general_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_general=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("常规信息")+'</div>',
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
        height: 250,
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
            {header: "", width: 150, sortable: false, css:'font-weight:bold;color:#414141;',dataIndex: 'name',renderer:zmUIMakeUP},
            {header: "", width: 350, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_general_store
        ,tbar:[label_general]
    });

    return general_grid;

}
function get_cloudstorageinfo(node_id,node){
    var hide=false;
    var autoexpand_column=2;
    if(node.attributes.cp_type == stackone.constants.CMS){
         hide=true;
         autoexpand_column=3
    }




   var vmstorage_columnmodel = new Ext.grid.ColumnModel([
     {
          header: _("设备"),
          width: 100,
          dataIndex: 'device',
          hidden:hide,
          sortable:true         
     },
     {
          header: _("挂载点"),
          width: 150,
          dataIndex: 'device',
          hidden:!hide,
          sortable:true
     },
    {
        header: _("类型"),
        width: 90,
        dataIndex: 'type',
        hidden:hide,
        sortable:true
    },
    {
        header: _("大小(GB)"),
        width: 100,
        sortable: true,
        dataIndex: 'size'
    },
    {
        header: _("模式"),
        width: 90,
        dataIndex: 'mode',
        hidden:!hide,
        sortable:true
    }
   ]);

    var vm_storage_store =new Ext.data.JsonStore({
//        url: "vm_general_info",
        url: "/cloud/cloudvm_info?type=STORAGE_INFO",
        root: 'info',
        fields: ['device','type','size','mode'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    vm_storage_store.load({
        params:{
            node_id:node_id
        }
    });
    var label_general=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("存储信息")+'</div>',
        id:'label_general'
    });

    var storage_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        //title:_("General"),
//        cls:'hideheader  ',
        disableSelection:true,
        colModel:vmstorage_columnmodel,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        width: '100%',
        height: 250,
        enableHdMenu:false,
         autoExpandColumn:autoexpand_column,
        enableColumnMove:false,
        //plugins:[action],
        autoScroll:true,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },       
        store:vm_storage_store
        ,tbar:[label_general]
    });

    return storage_grid;

}
function get_cloudnwsinfo(node_id,cp_feature){
    var store="";
    var colmodel="";
        
    
    var vm_nws_store =new Ext.data.JsonStore({
//        url: "vm_general_info",
        url: "/cloud/cloudvm_info?type=NWS_INFO",
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

    var vm_network_cms_columnmodel = new Ext.grid.ColumnModel([
     {
          header: _("名称"),
          width: 100,
          dataIndex: 'name',
          sortable:true         
     },
    {
        header: _("私有IP"),
        width: 90,
        dataIndex: 'private_ip',
        sortable:true
    },
    {
        header: _("公共IP"),
        width: 100,
        sortable: true,
        dataIndex: 'public_ip'
    }
   ]);    
    var vm_nws_store_cms =new Ext.data.JsonStore({
//        url: "vm_general_info",
        url: "/cloud/cloudvm_info?type=NWS_INFO_CMS",
        root: 'info',
        fields: ['name','private_ip','public_ip'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    var vm_network_columnmodel = new Ext.grid.ColumnModel([
     {
          header: _(""),
          width: 180,
          sortable:false,
          css:'font-weight:bold;color:#414141;',         
          dataIndex: 'name'
        
     },
    {
            header: "",
            width: 300,
            sortable: false,
            dataIndex: 'value',
            renderer:UIMakeUP
    }
   ]);    

   var label_general=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("网络信息")+'</div>',
        id:'label_general'
    });


     if (!is_feature_enabled(cp_feature,stackone.constants.CF_ACCOUNT))	
        {   
            store= vm_nws_store_cms;
            colmodel=vm_network_cms_columnmodel;
        }else{
              store=vm_nws_store;
              colmodel=vm_network_columnmodel;  
            }

    store.load({
        params:{
            node_id:node_id
        }
    });
    
    var network_grid = new Ext.grid.GridPanel({
        disableSelection:true,        
        //cls:'hideheader  ',
        stripeRows: true,
        border:true,
        width: '100%',
        height: 250,
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
        colModel: colmodel,
        store:store
        ,tbar:[label_general]
    });

    return network_grid;

}


function get_cloudtemplateinfo(node_id){
    
    var vm_template_store =new Ext.data.JsonStore({
        url: "/cloud/cloudvm_info?type=TEMPLATE_INFO",
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
        height: 250,
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
            {header: "", width: 150, sortable: false,  css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:zmUIMakeUP},
            {header: "", width: 350, sortable: false, dataIndex: 'value',renderer:UIMakeUP}
        ],
        store:vm_template_store
        ,tbar:[label_template]
    });

    return template_grid;
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

function display_tasks_cloudvm(node_id,node){
     var vmtask_grid=drawtask_grid(node_id,node,"虚拟机任务",248);
     return vmtask_grid;
}

function drawtask_grid(node_id,node,grd_lbl,grd_height){

      var node_type=node.attributes.nodetype;
     
      var task_columnModel = new Ext.grid.ColumnModel([
     {
         header: "",
         dataIndex: 'task_id',
         menuDisabled: false,
         hidden:true

     },
     {
         header: "名称",
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
                        Ext.MessageBox.confirm(_("确认"),_("确定要删除任务 "+task_name), function(id){
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

     if (node_type==stackone.constants.CLOUD_VM){
        task_columnModel.setHidden(3,true);
        task_columnModel.setColumnWidth(1,100);
        task_columnModel.setColumnWidth(2,80);
        task_columnModel.setColumnWidth(4,130);
        task_columnModel.setColumnWidth(5,130);
        task_columnModel.setColumnWidth(6,90);
     }else{
        task_columnModel.setHidden(3,false);
        task_columnModel.setColumnWidth(1,125);
        task_columnModel.setColumnWidth(2,125);
        task_columnModel.setColumnWidth(3,135);
        task_columnModel.setColumnWidth(4,150);
        task_columnModel.setColumnWidth(5,150);
        task_columnModel.setColumnWidth(6,120);
     }


     return task_grid;

}

function create_template(vm){
    var vm_name=new Ext.form.TextField({
        fieldLabel: _('云-虚拟机名称'),
        name: 'vm_name',
        width: 150,
        id: 'vm_name',
        value:vm.text,
        disabled:true,
        allowBlank:false
    });
    var image_name=new Ext.form.TextField({
        fieldLabel: _('模板名称'),
        name: 'image_name',
        width: 150,
        id: 'image_name',
        allowBlank:false
    });
    var description=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'description',
        width: 150,
        id: 'description',
        allowBlank:false
    });

    var tlabel_msg=new Ext.form.Label({
//        html:"<br/>The instance you're using as a template for a new image has the following volumes:<br/>"+
//            "* /dev/sda1, vol-f4483c9c (15 GiB), will delete on termination<br/>"+
//            "Total size of EBS volumes: 15 GiB.<br/>"+
//            "When you create an EBS image an EBS snapshot will also be created for each of the above volumes."
        html:"<br/>The instance you're using as a template for a new image has volumes.<br/>"+
                   "These volumes will be deleted on instance termination<br/>"+
                    "When you create an image a snapshot will also be created for each of the volumes."

    });

    var save_button=new Ext.Button({
        name: 'save',
        id: 'save',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(image_name.getValue()==""){
                    Ext.MessageBox.alert( _("失败") , "请为模板输入一个名称");
                    return;
                }else if(description.getValue()==""){
                    Ext.MessageBox.alert( _("失败") , "请输入模板的说明");
                    return;
                }

                var url="/cloud/create_template_vm?vm_id="+vm.attributes.id+"&vdc_id="+vm.parentNode.parentNode.id+
                    "&image_name="+image_name.getValue()+"&description="+description.getValue();
                var ajaxReq=ajaxRequest(url,0,"GET",true);
                ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success)
                            Ext.MessageBox.alert(_("成功"),response.msg);
                        else
                            Ext.MessageBox.alert(_("失败"),response.msg);
                    },
                    failure: function(xhr){
                        Ext.MessageBox.alert( _("失败") , xhr.statusText);
                    }
                });

                closeWindow();
            }
        }
 });
    var cancel_button= new Ext.Button({
        id: 'cancel',
        text: _('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow();
            }
        }
    });

    var template_panel=new Ext.Panel({
        border:true,
        width:"100%",
        id:"template_panel",
        layout:'form',
        frame:true,
        items:[image_name,description,tlabel_msg]
     });


    var template_outer_panel=new Ext.Panel({
        border:true,
        width:"100%",
        id:"template_outer_panel",
        layout:'form',
        bbar:[{
            xtype: 'tbfill'
        },  save_button,cancel_button],
        items:[template_panel]
     });

     return template_outer_panel;

    
}
