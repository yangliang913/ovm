
function cloud_provider_store_summary_page(mainpanel,cloudproviderstore_id)
{
    if(mainpanel.items){
        mainpanel.removeAll(true);
    }
    
     var homepanel=new Ext.Panel({
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
        items:[homepanel]
    });

     var panel1 = new Ext.Panel({
         width:'100%',
        height: '100%',
         border:false,
         bodyBorder:false,
//        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });
    var summary_panel = new Ext.Panel({
        collapsible:false,
//        height:240,
        height:'100%',
        width:'32%',
        border:false,
        bodyBorder:false
       
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
    var label1_1=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("虚拟数据中心")+'<br/></div>'
    });

    var pychart_panel = new Ext.Panel({
        height:250,
        width:'33%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        //,bodyStyle:';padding-right:15px;'
        ,tbar:[label1_1]
    });
     pychart_panel.add(vdcs_per_cp_pychart(cloudproviderstore_id));

     var label1_2=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("虚拟机")+'<br/></div>'
    });

    var pychart_panel1 = new Ext.Panel({
        height:250,
        width:'33%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        //,bodyStyle:';padding-right:15px;'
        ,tbar:[label1_2]
    });

     pychart_panel1.add(vms_per_cp_pychart(cloudproviderstore_id));

     var cpstore_summary_panel = new Ext.Panel({
        collapsible:false,
//        height:330,
        width:'100%',
        border:false,
        bodyStyle:'padding-top:10px;',
        bodyBorder:false,
        layout:'fit'
    });

    var summary_grid=create_cloud_cpstoresummary_grid(cloudproviderstore_id);

    var cpstore_summary_grid=create_cloud_cpstoredetails_grid(cloudproviderstore_id);
    
    summary_panel.add(summary_grid);
    cpstore_summary_panel.add(cpstore_summary_grid);
    panel1.add(summary_panel);
    panel1.add(dummy_panel1);
    panel1.add(pychart_panel);
    panel1.add(dummy_panel2);
    panel1.add(pychart_panel1);
    homepanel.add(panel1);
    homepanel.add(cpstore_summary_panel);
    
//    homepanel.add(cpstore_summary_panel);
//    topPanel.add(cpstore_summary_panel);
    mainpanel.add(topPanel);    

    mainpanel.doLayout();

}



function vdcs_per_cp_pychart(cloudproviderstore_id){



    var vms_per_cp_store = new Ext.data.Store({
        url:"/cloud_dashboard/vdc_details?cloud_provider_storeid="+cloudproviderstore_id,
        reader: new Ext.data.JsonReader({
            root: 'rows',
            fields: ['label', 'value']
        })
    });

    var vms_per_cp_pie1 = new Ext.ux.PieFlot({
        pies: {
            show: true,
            autoScale: true,
            fillOpacity: 1,
            labelFormatter: function(label, value, percent, textValue, pie, serie, options) {
//                alert(label+"==value=="+value+"===percent==="+percent+"==textValue==="+textValue+"pie==="+pie);
                if(value == 0)
                {
                    return '';
                }
//                return textValue + '% ';
                return textValue+"%("+value+")";
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



function vms_per_cp_pychart(cloudproviderstore_id){


    var vms_per_cp_store = new Ext.data.Store({
        url:"/cloud_dashboard/vms_details_for_cps?cloud_provider_storeid="+cloudproviderstore_id,
        reader: new Ext.data.JsonReader({
            root: 'rows',
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
//                return textValue + '% ';
                return textValue+"%("+value+")";
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




function create_cloud_cpstoresummary_grid(cloudproviderstore_id){

     var label_summary=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_task'
    });

    var summarycloud_store =new Ext.data.JsonStore({
        url:"/cloud_dashboard/get_cloudproviderstore_summary_info?cloudproviderstore_id="+cloudproviderstore_id,
        root: 'rows',
        fields: ['name','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    summarycloud_store.load();


    var summarycloud_grid = new Ext.grid.GridPanel({
        //title:'Template Details',
        disableSelection:true,
        stripeRows: true,
//        autoHeight:true,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 250,

        enableHdMenu:false,
        enableColumnMove:false,
        autoExpandColumn:1,
        autoScroll:true,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [
            {header: "H1", width: 180, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'name',renderer:serveUIMakeUP},
            {header: "H2", width: 70, sortable: false,dataIndex:'value',renderer:UIMakeUP}
        ],
        store:summarycloud_store,
        tbar:[label_summary]
    });

    return summarycloud_grid;

}


function create_cloud_cpstoredetails_grid(cloudproviderstore_id){   
 

    var detailcloud_store =new Ext.data.JsonStore({
        url:"/cloud_dashboard/get_cloudproviderstore_details_info?cloudproviderstore_id="+cloudproviderstore_id,
        root: 'rows',
        fields: ['id','name','type','vdc','regions','vms','cpu','memory','storage'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });


    detailcloud_store.load()


    var cloudprovider_columnModel = new Ext.grid.ColumnModel([
        {
        header: _("编号"),
        width: 10,
        hidden: true,
        dataIndex: 'id'
     },
     {
        header: _("名称"),
        width: 170,
        sortable: true,
        dataIndex: 'name'
    },
     {
        header: _("类型"),
        width: 150,
        sortable: true,
        dataIndex: 'type'
     },
      {
        header: _("虚拟数据中心"),
        width: 160,
        dataIndex: 'vdc',
        sortable:true,
        align:'right'
     },
     
    {
        header: _("区域"),
        width: 80,
        dataIndex: 'regions',
        sortable:false,
        align:'right'


    },
    {
        header: _("虚拟机"),
        dataIndex: 'vms',
        sortable:false,
        width: 105,
        align:'right'
      
    },
    {
        header: _("CPU"),
        dataIndex: 'cpu',
        sortable:false,
        width: 90,
        align:'right'

    },
    {
        header: _("内存(MB)"),
        dataIndex: 'memory',
        sortable:false,
        width: 100,
        align:'right'

    },
    {
        header: _("存储(GB)"),
        dataIndex: 'storage',
        sortable:false,
        width: 100,
        align:'right'

    }
    ]);
    
    var lbl_msg=stackone.constants.IAAS;
    var tb_lbl=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+lbl_msg+'</div>'
    });

    var items=new Array();
    items.push(tb_lbl);
    items.push({xtype:'tbfill'});
    items.push(_('搜索: '));
    items.push(new Ext.form.TextField({
        name: '搜索',
        id: 'search_summary',
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {
                cp_details_grid.getStore().filter('name', field.getValue(), false, false);
            }
        }
    }));
    var toolbar = new Ext.Toolbar({
        items: items
    });

    var cp_details_grid = new Ext.grid.GridPanel({
//        disableSelection:true,
        store: detailcloud_store,
        colModel:cloudprovider_columnModel,
        id:'cpstore_summary_grid',
        stripeRows: true,
        frame:false,
        width:"100%",
        autoExpandColumn:1,
        autoExpandMin:150,
        height:330,
        enableHdMenu:false,
        tbar:toolbar,
          viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        }
//        ,listeners:{
//            rowcontextmenu :function(grid,rowIndex,e) {
//                e.preventDefault();
//                handle_rowclick(grid,rowIndex,"contextmenu",e);
//            },
//            rowdblclick :function(grid,rowIndex,e) {
//                handle_rowclick(grid,rowIndex,"click",e);
//            }
//        }
    });


    return cp_details_grid;
    
    
}

function cloud_provider_summary_page(mainpanel,cloudprovider_id, node){
	
    
    if (node.attributes.cp_type==stackone.constants.CMS){
        return cms_cloud_provider_summary_page(mainpanel,cloudprovider_id, node);
    }

    if(mainpanel.items){
        mainpanel.removeAll(true);
    }

    
     var homepanel=new Ext.Panel({
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
        items:[homepanel]
    });

     var panel1 = new Ext.Panel({
         width:'100%',
        height: '100%',
         border:false,
         bodyBorder:false,
//        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });

    var panel2 = new Ext.Panel({
         width:'100%',
        height: '100%',
         border:false,
         bodyBorder:false,
//        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });

    var panel2_1 = new Ext.Panel({
        collapsible:false,
//        height:330,
        width:'100%',
        border:false,
        bodyStyle:'padding-top:10px;',
        bodyBorder:false,
        layout:'fit'
    });


    var summary_panel = new Ext.Panel({
        collapsible:false,
//        height:240,
        height:'100%',
        width:'32%',
        border:false,
        bodyBorder:false

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
    var label1_1=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("各区域的虚拟机")+'<br/></div>'
    });

    var pychart_panel = new Ext.Panel({
        height:325,
        width:'33%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        //,bodyStyle:';padding-right:15px;'
        ,tbar:[label1_1]
    });
     pychart_panel.add(vms_per_cldpvdrr_pychart(cloudprovider_id));

     var label1_2=new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("各实例类型的虚拟机")+'<br/></div>'
    });

    var pychart_panel1 = new Ext.Panel({
        height:325,
        width:'33%',
        cls: 'whitebackground',
        border:false,
        bodyBorder:false
        //,bodyStyle:';padding-right:15px;'
        ,tbar:[label1_2]
    });

     pychart_panel1.add(vms_per_cldpvdrs_pychart(cloudprovider_id));


     var dummy_panel3 = new Ext.Panel({
        width:'1%',
        html:'&nbsp;',
        border:false,
        bodyBorder:false
    });



     var region_panel = new Ext.Panel({
        collapsible:false,
//        height:330,
        width:'49.4%',
        border:false,
//        bodyStyle:'padding-top:10px;',
        bodyBorder:false,
        layout:'fit'
    });
    var service_panel = new Ext.Panel({
        collapsible:false,
//        height:330,
        width:'49.4%',
        border:false,
//        bodyStyle:'padding-top:10px;',
        bodyBorder:false,
        layout:'fit'
    });



    var summary_grid=create_cloudprovider_summary_grid(cloudprovider_id);
    var region_grid=create_cloudprovider_region_grid(cloudprovider_id);
    var service_grid=create_cloudprovider_service_grid(cloudprovider_id);

    summary_panel.add(summary_grid);
    region_panel.add(region_grid);
    service_panel.add(service_grid);

    panel1.add(summary_panel);
    panel1.add(dummy_panel1);
    panel1.add(pychart_panel);
    panel1.add(dummy_panel2);
    panel1.add(pychart_panel1);
    panel2.add(region_panel);
    panel2.add(dummy_panel3);
    panel2.add(service_panel);
    
    
    
    
    homepanel.add(panel1);
    panel2_1.add(panel2);
//    homepanel.add(dummy_panel4);
    homepanel.add(panel2_1);

//    homepanel.add(cpstore_summary_panel);
//    topPanel.add(cpstore_summary_panel);
    mainpanel.add(topPanel);

    mainpanel.doLayout();

    

}

function create_cloudprovider_summary_grid(cloudprovider_id){
     var label_summary=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_task'
    });
    var summarycloud_store =new Ext.data.JsonStore({
        url:"/cloud_dashboard/get_cloudprovider_summary_info?cloudprovider_id="+cloudprovider_id,
        root: 'rows',
        fields: ['name','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    summarycloud_store.load();
     var summarycloud_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        stripeRows: true,
//        autoHeight:true,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 325,
        enableHdMenu:false,
        enableColumnMove:false,
        autoExpandColumn:1,
        autoScroll:true,
        layout:'fit',
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
            ,forceFit:false
        },
        columns: [
            {header: "", width: 180, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'name',renderer:meUIMakeUP},
            {header: "", width: 340, sortable: false,dataIndex:'value'}
        ],
        store:summarycloud_store,
        tbar:[label_summary]
    });

    return summarycloud_grid;
}


function vms_per_cldpvdrr_pychart(cloudprovider_id){
    


    var vms_per_cpr_store = new Ext.data.Store({
        url:"/cloud_dashboard/vms_details_for_cloudprovider?cloudprovider_id="+cloudprovider_id,
        reader: new Ext.data.JsonReader({
            root: 'rows',
            fields: ['label', 'value']
        })
    });

    var vms_per_cpr_pie1 = new Ext.ux.PieFlot({
        pies: {
            show: true,
            autoScale: true,
            fillOpacity: 1,
            labelFormatter: function(label, value, percent, textValue, pie, serie, options) {
                if(value == 0)
                {
                    return '';
                }
//                return textValue + '% ';
                return textValue+"%("+value+")";
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

    vms_per_cpr_store.on('load',
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
        vms_per_cpr_pie1
    );

    vms_per_cpr_store.load();

    return vms_per_cpr_pie1;

}



function vms_per_cldpvdrs_pychart(cloudprovider_id){

    var vms_per_cps_store = new Ext.data.Store({
        url:"/cloud_dashboard/vms_details_per_cpservice?cloudprovider_id="+cloudprovider_id,
        reader: new Ext.data.JsonReader({
            root: 'rows',
            fields: ['label', 'value']
        })
    });

    var vms_per_cps_pie1 = new Ext.ux.PieFlot({
        pies: {
            show: true,
            autoScale: true,
            fillOpacity: 1,
            labelFormatter: function(label, value, percent, textValue, pie, serie, options) {
                if(value == 0)
                {
                    return '';
                }
//                return textValue + '% ';
                return textValue+"%("+value+")";
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

    vms_per_cps_store.on('load',
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
        vms_per_cps_pie1
    );

    vms_per_cps_store.load();

    return vms_per_cps_pie1;

}


function create_cloudprovider_region_grid(cloudprovider_id){

      var label_region=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("区域")+'</div>',
        id:'label_task'
    });


    var detailcloud_store =new Ext.data.JsonStore({
        url:"/cloud_dashboard/get_cloudprovider_region_info?cloudprovider_id="+cloudprovider_id,
        root: 'rows',
        fields: ['id','name','end_point','Virtual Machines'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });


    detailcloud_store.load()


    var cloudprovider_columnModel = new Ext.grid.ColumnModel([
        {
        header: _("编号"),
        width: 10,
        hidden: true,
        dataIndex: 'id'
     },
     {
        header: _("名称"),
        width: 80,
        sortable: true,
        dataIndex: 'name'
    },
     {
        header: _("Endpoint"),
        width: 230,
        sortable: true,
        dataIndex: 'end_point'
     },
      {
        header: _("虚拟机"),
        width: 110,
        dataIndex: 'Virtual Machines',
        sortable:true,
        align:'right'
     }

    ]);

    var cpregion_details_grid = new Ext.grid.GridPanel({
//        disableSelection:true,
        store: detailcloud_store,
        colModel:cloudprovider_columnModel,
        id:'cpstore_summary_grid',
        stripeRows: true,
        frame:false,
        width:"100%",
        autoExpandColumn:1,
        autoExpandMin:150,
        height:250,
        enableHdMenu:false,
        tbar:[label_region]
    });

   

 


    return cpregion_details_grid;

}


function create_cloudprovider_service_grid(cloudprovider_id){

    var label_service=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("实例类型")+'</div>',
        id:'label_task'
    });

    var servicecloud_store =new Ext.data.JsonStore({
        url:"/cloud_dashboard/get_cloudprovider_service_info?cloudprovider_id="+cloudprovider_id,
        root: 'rows',
        fields: ['id','name','category','vms','cpu','memory','storage'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    servicecloud_store.load();

    var cloudprovider_columnModel = new Ext.grid.ColumnModel([
        {
        header: _("编号"),
        width: 10,
        hidden: true,
        dataIndex: 'id'
     },
     {
        header: _("名称"),
        width: 75,
        sortable: true,
        dataIndex: 'name'
    },
     {
        header: _("分类"),
        width: 100,
        sortable: true,
        dataIndex: 'category'
     },
      {
        header: _("虚拟机"),
        width: 105,
        dataIndex: 'vms',
        sortable:true,
        align:'right'
     },
     {
        header: _("CPU"),
        width: 50,
        dataIndex: 'cpu',
        sortable:true,
        align:'right'
     },
     {
        header: _("内存(MB)"),
        width: 80,
        dataIndex: 'memory',
        sortable:true,
        align:'right'
     },
     {
        header: _("存储(GB)"),
        width: 80,
        dataIndex: 'storage',
        sortable:true,
        align:'right'
     }

    ]);

    var cpservice_details_grid = new Ext.grid.GridPanel({
//        disableSelection:true,
        store: servicecloud_store,
        colModel:cloudprovider_columnModel,
        id:'cpstore_service_grid',
        stripeRows: true,
        frame:false,
        width:"100%",
        autoExpandColumn:1,
        autoExpandMin:65,
        height:250,
        enableHdMenu:false,
        tbar:[label_service]
    });

    return cpservice_details_grid;

}

function cms_cloud_provider_summary_page(mainpanel,cloudprovider_id, node){


    if(mainpanel.items){
        mainpanel.removeAll(true);
    }

    
     var homepanel=new Ext.Panel({
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
        items:[homepanel]
    });

     var panel1 = new Ext.Panel({
         width:'100%',
        height: '100%',
         border:false,
         bodyBorder:false,
//        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });

    var panel2 = new Ext.Panel({
         width:'100%',
        height: '100%',
         border:false,
         bodyBorder:false,
//        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });

    var panel2_1 = new Ext.Panel({
        collapsible:false,
//        height:330,
        width:'100%',
        border:false,
        bodyStyle:'padding-top:10px;',
        bodyBorder:false,
        layout:'fit'
    });


    var summary_panel = new Ext.Panel({
        collapsible:false,
//        height:240,
        height:'100%',
        width:'32%',
        border:false,
        bodyBorder:false

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

     var vdc_panel = new Ext.Panel({
        collapsible:false,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'fit'
    });
    var usage_panel = new Ext.Panel({
        collapsible:false,
        width:'66%',
        border:false,
//        bodyStyle:'padding-top:10px;',
        bodyBorder:false,
        layout:'fit'
    });



    var summary_grid=create_cloudprovider_summary_grid(cloudprovider_id);
    var virtualdatacenter_grid=iaasVdcPanel(cloudprovider_id);
    var usage_grid=iaasUsagePanel(cloudprovider_id);


    summary_panel.add(summary_grid);
    vdc_panel.add(virtualdatacenter_grid);
    usage_panel.add(usage_grid);

    panel1.add(summary_panel);
    panel1.add(dummy_panel2);
    panel2.add(vdc_panel);
    panel2.add(dummy_panel3);
    panel1.add(usage_panel);
    homepanel.add(panel1);
    panel2_1.add(panel2);
    homepanel.add(panel2_1);
    mainpanel.add(topPanel);
    mainpanel.doLayout();

}

function iaasUsagePanel(cloudprovider_id){
    
    var iaas_usage_label = new Ext.form.Label({
        html:'<div class="toolbar_hdg" >'+_("IaaS利用率")+'<br/></div>'
    });
    var usage_store =new Ext.data.JsonStore({
        url:"/cloud_dashboard/get_cloudprovider_usage_details_info?cp_id="+cloudprovider_id,
        root: 'rows',
        fields: ['name','usage','limit','total'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    usage_store.load();

    var iaas_details_grid = new Ext.grid.GridPanel({
        store: usage_store,
        id:'iaas_details_grid',
        stripeRows: true,
        frame:false,
        width:"100%",
//        autoExpandMin:100,
        height:325,
        enableHdMenu:false,
        autoExpandColumn:1,
        layout:'fit',
        tbar:[iaas_usage_label],
         viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
            ,forceFit:false
//            ,scrollOffset: 0
        },
        columns: [
            {header: " ", width:280,sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'name',renderer:samUIMakeUP},
            {header: "已用", width:130, sortable: false, align:'right',css:'font-weight:bold; color:#414141;',dataIndex:'usage'},
            {header: "分配", width:140, sortable: false,align:'right', css:'font-weight:bold; color:#414141;',dataIndex:'limit',renderer:limitUIMakeUP},
            {header: "共有", width:130, sortable: false,align:'right', css:'font-weight:bold; color:#414141;',dataIndex:'total'}
        ]

    });
    return iaas_details_grid ;
}

function limitUIMakeUP(value, meta, rec) {
    var dict = {'Unlimited':'无限'
				
	} 
	if (dict[rec.get('limit')]) {
		return dict[rec.get('limit')];
	} else {
	        return rec.get('limit');
	}
	
}

function serveUIMakeUP(value, meta, rec) {
    var dict = {'IaaS':'IaaS',
	            'Virtual Data Centers':'虚拟数据中心',
	            'Virtual Machines':'虚拟机',
	            'CPU\'s':'CPU数量',
	            'Memory(GB)':'内存',
	            'Storage(GB)':'存储'
	} 
    return dict[rec.get('name')];
}

function meUIMakeUP(value, meta, rec) {
    var dict = {'Name':'名称',
	            'Type':'类型',
	            'Virtual Data Centers':'虚拟数据中心',
	            'Virtual Machines':'虚拟机',
	            'Server Pools':'资源池',
	            'Public Templates':'公共模板',
				'Regions':'区域'
	} 
    return dict[rec.get('name')];
}

function samUIMakeUP(value, meta, rec) {
    var dict = {'Virtual Machines':'虚拟机',
	            'Running':'可运行',
	            'Provisioned':'部署',
	            'Compute Resources':'计算资源',
	            'Memory (MB)':'内存',
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

function iaasVdcPanel(cloudprovider_id){
    var vdc_label = new Ext.form.Label({
         html:'<div class="toolbar_hdg" >'+_("虚拟数据中心")+'<br/></div>'
     });
    var combo_val='Allocated';
    var data_store =new Ext.data.JsonStore({
        url:"/cloud_dashboard/get_cloudprovider_usage_vdc_info",
        root: 'rows',
        fields: ['Name','vCPUs','Memory','Size','Public IPs','Private Networks'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    data_store.load({
        params:{
            cp_id:cloudprovider_id,
            comboval:combo_val
        }
    });
    var select_options = new Ext.form.ComboBox({
        id: 'select_template',
        fieldLabel: _('选择'),
        triggerAction:'all',
        emptyText :_("选择"),
        store:[['Used','Used'],
              ['Allocated','Allocated'],
              ['Available','Available']
             ],
        width:150,
        listWidth:150,
        displayField:'name',
        valueField:'name',
//        minListWidth:0,
        labelSeparator:" ",
        align:'right',
        mode:'local',
        forceSelection: true,
        listeners: {
                select: function(combo, record, index){
                   data_store.load({
                        params:{
                            cp_id:cloudprovider_id,
                            comboval:combo.getValue()
                        }
                   });
            }
         }
    });    

    var items = new Array();
    items.push(vdc_label);
    items.push({xtype:'tbfill'});
//
    select_options.setValue('Allocated');
    items.push(select_options);
//    items.push(custom_btn);
    var toolbar = new Ext.Toolbar({
        items: items
    });
    var vdc_grid = new Ext.grid.GridPanel({
        id:'vdc_details11_grid',
        stripeRows: true,
        frame:false,
        width:"100%",
        autoExpandMin:150,
        height:310,
        enableHdMenu:false,
        tbar:toolbar,
        layout:'fit',
        autoScroll:true,
        autoExpandColumn:1,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
            ,forceFit:false
//            ,scrollOffset: 0

        },
        store: data_store,
        columns: [
            {header: "", hidden: true, dataIndex:'Name'},
            {header: "名称", width: 175, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'Name'},
            {header: "vCPU", width: 80, sortable: false, align:'right',css:'font-weight:bold; color:#414141;',dataIndex:'vCPUs'},
            {header: "内存(MB)", width: 80, sortable: false,align:'right', css:'font-weight:bold; color:#414141;',dataIndex:'Memory'},
            {header: "存储(GB)", width: 100, sortable: false,align:'right', css:'font-weight:bold; color:#414141;',dataIndex:'Size'},
            {header: "公共IP", width: 175, sortable: false,align:'right', css:'font-weight:bold; color:#414141;',dataIndex:'Public IPs'},
            {header: "私有网络", width: 177, sortable: false, align:'right',css:'font-weight:bold; color:#414141;',dataIndex:'Private Networks'}
        ]
    });
    return vdc_grid;
}


function cloud_provider_config_page(mainpanel,cloudprovider_id, node){

    if(mainpanel.items){
        mainpanel.removeAll(true);
    }

    
    var network_label = new  Ext.form.Label({
       html:'<div class="toolbar_hdg" >'+_("网络")+'<br/></div>'
    });

     var homepanel=new Ext.Panel({
        height:"100%",
        width:"100%",
        //layout: 'fit',
        bodyStyle:'padding-left:10px;padding-top:10px;padding-right:2px;',
        border:false,
        bodyBorder:false
    });

    var panel1 = new Ext.Panel({
         width:'100%',
        height: '100%',
         border:false,
         bodyBorder:false,
//        bodyStyle:'padding-top:10px;padding-right:5px;',
        layout:'column'
    });

    var topPanel = new Ext.Panel({
        collapsible:false,
        //title:format(_("Available Template Groups Details")),
        height:'75%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false,
        items:[homepanel]
    });

    var server_pool_panel = new Ext.Panel({
        collapsible:false,
        width:'49%',
        border:false,
        bodyBorder:false,
        layout:'fit'
    });
    
    var storage_panel = new Ext.Panel({
        width:'49%',
        border:false,
        bodyBorder:false,
        collapsible:false,
        layout:'fit'
    });
    var vlanidpoolpanel = new Ext.Panel({
        width:'49%',
        border:false,
        bodyBorder:false,
        collapsible:false,
        layout:'fit'
    });
     var dummy_panel1 = new Ext.Panel({
        width:'1%',
        html:'&nbsp;',
        border:false,
        bodyBorder:false
    });
     var network_panel = new Ext.Panel({
        width:'100%',
        html:'&nbsp;',
        border:false,
        bodyBorder:false,
        layout: 'fit',
        tbar:[network_label]
    });
     var publicippoolpanel =  new Ext.Panel({
         width:'49%',
         border:false,
         bodyBorder:false,
         collapsible:false,
         layout:'fit'
     });
    var  defined_nw_panel = new Ext.Panel({
         width:'49%',
         border:false,
         bodyBorder:false,
         collapsible:false,
         layout:'fit'
     });
    var private_nw_panel = new Ext.Panel({
        width:'49%',
        border:false,
        bodyBorder:false,
        collapsible:false,
        layout:'fit'
    });
    var dummy_panel3 = new Ext.Panel({
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
    var panel2 = new Ext.Panel({
        width:'100%',
       height: '100%',
        border:false,
        bodyBorder:false,
//       bodyStyle:'padding-top:10px;padding-right:5px;',
       layout:'column'
   });
    var panel3 = new Ext.Panel({
        width:'100%',
       height: '100%',
        border:false,
        bodyBorder:false,
//       bodyStyle:'padding-top:10px;padding-right:5px;',
       layout:'column'
   });
 
    var panel1_1 = new Ext.Panel({
        collapsible:false,
//        height:330,
        width:'100%',
        border:false,
//        bodyStyle:'padding-top:1px;',
        bodyBorder:false,
        layout:'fit'
    });
    var panel1_2 = new Ext.Panel({
        collapsible:false,
//        height:330,
        width:'100%',
        border:false,
        bodyStyle:'padding-top:10px;',
        bodyBorder:false,
        layout:'fit'
    });
    var panel2_1 = new Ext.Panel({
        collapsible:false,
//        height:330,
        width:'100%',
        border:false,
        bodyStyle:'padding-top:10px;',
        bodyBorder:false,
        layout:'fit'
    });
    var panel3_1 = new Ext.Panel({
        collapsible:false,
//        height:330,
        width:'100%',
        border:false,
        bodyStyle:'padding-top:10px;',
        bodyBorder:false,
        layout:'fit'
    });

    var server_pool_grid = iaasConfigServerPoolGrid(cloudprovider_id);
    var storage_panel_grid = iaasConfigStoragePanelGrid(cloudprovider_id);
    var vlanidpool_grid = iaasConfigVlanIdPoolPanelGrid(cloudprovider_id)
    
    var publicippool = iaasConfigPublicIpPool(cloudprovider_id);
    storage_panel.add(storage_panel_grid);
    server_pool_panel.add(server_pool_grid);
    var defined_nw_grid = iaasConfigDefinedNetwork(cloudprovider_id);
    var private_nw_grid = iaasConfigPrivateNetwork(cloudprovider_id)
    private_nw_panel.add(private_nw_grid);
    defined_nw_panel.add(defined_nw_grid);
    vlanidpoolpanel.add(vlanidpool_grid);
    publicippoolpanel.add(publicippool);
   
    panel1.add(server_pool_panel);
    panel1.add(dummy_panel2);
    panel1.add(storage_panel);
    panel1_1.add(panel1);
    homepanel.add(panel1_1);
//    panel1_2.add(network_panel)
//    homepanel.add(panel1_2);
    
    panel2.add(vlanidpoolpanel);
    panel2.add(dummy_panel1);
    panel2.add(defined_nw_panel);
    panel2_1.add(panel2);
    homepanel.add(panel2_1);
    
    panel3.add(private_nw_panel);
    panel3.add(dummy_panel3);
    panel3.add(publicippoolpanel);
    panel3_1.add(panel3);
    homepanel.add(panel3_1);
    
    mainpanel.add(topPanel);
    mainpanel.doLayout();

}
function iaasConfigServerPoolGrid(cloudprovider_id){
    var server_pool_label = new  Ext.form.Label({
        html:'<div class="toolbar_hdg" >'+_("服务器池")+'<br/></div>'
    });
    var serverpool_json_store = new Ext.data.JsonStore({
        url:'cloud_dashboard/get_cloudprovider_serverpool_info?&cp_id='+cloudprovider_id,
        root:'rows',
        fields: ['name','cpu_used','cpu_total','memory_used','memory_total','high_availability'],
        successProperty:'success',
        listeners:{
            loadException:function(obj,opts,res,e){
                 var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }

    });
    serverpool_json_store.load();
    var server_pool_grid = new Ext.grid.GridPanel({
        id :'server_pool_grid',
        stripeRows:true,
        frame:false,
        width:'100%',
        autoExpandMin:150,
        layout:'fit',
        height:173,
        autoExpanColumn:1,
        enableHdMenu:false,
        tbar:[server_pool_label],
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
            ,forceFit:false
            ,scrollOffset: 0
        },
        store:serverpool_json_store,
          columns: [
            {header: "名称", width: 127, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'name'},
            {header: "已经使用的CPU", hidden:true,width: 100, sortable: false, align:'right',css:'font-weight:bold; color:#414141;',dataIndex:'cpu_used'},
            {header: "CPUs", width: 122, sortable: false,align:'right', css:'font-weight:bold; color:#414141;',dataIndex:'cpu_total'},
            {header: "已经使用的内存",hidden:true, width: 100, sortable: false,align:'right', css:'font-weight:bold; color:#414141;',dataIndex:'memory_used'},
            {header: "内存(MB)", width: 127, sortable: false,align:'right', css:'font-weight:bold; color:#414141;',dataIndex:'memory_total'},
            {header: "高可用", width:133, sortable: false, align:'right',css:'font-weight:bold; color:#414141;',dataIndex:'high_availability'}
        ]
    });
    return server_pool_grid;

}

function iaasConfigStoragePanelGrid(cloudprovider_id){
     var storage_pool_label = new  Ext.form.Label({
        html:'<div class="toolbar_hdg" >'+_("存储")+'<br/></div>'
    });
    var storage_json_store = new Ext.data.JsonStore({
        url:'cloud_dashboard/get_cloudprovider_storage_info?&cp_id='+cloudprovider_id,
        root:'rows',
        fields: ['name','type','used','total','available'],
        successProperty:'success',
        listeners:{
            loadException:function(obj,opts,res,e){
                 var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }

    });
    storage_json_store.load();
    var storage_grid = new Ext.grid.GridPanel({
        id :'server_pool_grid',
        stripeRows:true,
        frame:false,
        width:'100%',
        autoExpandMin:150,
        height:173,
        autoExpandColumn:1,
        layout:'fit',
        enableHdMenu:false,
        tbar:[storage_pool_label],
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
            ,forceFit:true
            ,scrollOffset: 0
        },
        store:storage_json_store,
          columns: [
            {header: "名称", width: 123, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'name'},
            {header: "类型", width: 116, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'type'},
            {header: "已经使用(GB)", width: 116, sortable: false,align:'right', css:'font-weight:bold; color:#414141;',dataIndex:'used'},
            {header: "可用(GB)", width: 116, sortable: false, align:'right',css:'font-weight:bold; color:#414141;',dataIndex:'available'},
            {header: "总共(GB)", width: 116, sortable: false, align:'right',css:'font-weight:bold; color:#414141;',dataIndex:'total'}
        ]
    });
    return storage_grid;
}

function iaasConfigVlanIdPoolPanelGrid(cp_id){
	
	var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("VLAN ID池")+'</div>'
    });


    var vdc_vlan_store = new Ext.data.JsonStore({
        url:"/cloud_dashboard/get_cloudprovider_vlanidpoolinfo?&cp_id="+cp_id,
        root: 'rows',
        fields: ['total', 'range', 'used','allocated','name'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
//                console.log(store_response);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    vdc_vlan_store.load();
    var vdc_vlanidpools_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: vdc_vlan_store,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
        autoExpandMax:300,
        enableHdMenu:true,
        autoScroll:true,
        width:'100%',
        height:173,
        layout:'fit',
        tbar:[label_strge],
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
            ,forceFit:'true'
            ,scrollOffset: 0
        },
        columns: [
                  {header: "名称", width: 122, sortable: false,align:'left', css:'font-weight:bold; color:#414141;',dataIndex:'name'},
                  {header: "范围", width: 127, sortable: false, align:'left',css:'font-weight:bold; color:#414141;',dataIndex:'range'},
                  {header: "已经使用", width: 113, sortable: false,align:'right', css:'font-weight:bold; color:#414141;',dataIndex:'used'},
                  {header: "分配", width: 113, sortable: false, align:'right',css:'font-weight:bold; color:#414141;',dataIndex:'allocated'},
                  {header: "总共", width: 113, sortable: false, align:'right',css:'font-weight:bold; color:#414141;',dataIndex:'total'}
                  
              ]
    });
    return vdc_vlanidpools_grid;

}


function iaasConfigPublicIpPool(cp_id){
	
    var ippoollabel=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("公共IP池")+'</div>'
    });
    var pool_store = new Ext.data.JsonStore({
        url:"/cloud_dashboard/get_cloudprovider_publicip_pool_info?&cp_id="+cp_id,
        root: 'rows',
        fields: ['total', 'range', 'used','allocated','name'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    pool_store.load();
    var vdc_publicippool_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: pool_store,
        stripeRows: true,
        frame:false,
        autoExpandColumn:1,
        autoExpandMax:300,
        enableHdMenu:true,
        autoScroll:true,
        width:'100%',
        height:173,
        layout:'fit',
        tbar:[ippoollabel],
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
            ,forceFit:true
            ,scrollOffset: 0
        },
        columns: [
                  {header: "名称", width: 120, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'name'},
                  {header: "范围", width: 120, sortable: false,hidden:true, align:'left',css:'font-weight:bold; color:#414141;',dataIndex:'range'},
                  {header: "已经使用", width: 115, sortable: false,align:'right', css:'font-weight:bold; color:#414141;',dataIndex:'used'},
                  {header: "分配", width: 115, sortable: false, align:'right',css:'font-weight:bold; color:#414141;',dataIndex:'allocated'},
                  {header: "总共", width: 115, sortable: false, align:'right',css:'font-weight:bold; color:#414141;',dataIndex:'total'}
                  
              ]
    });
    return vdc_publicippool_grid;

}

function iaasConfigDefinedNetwork(cp_id){
	
	var networklabel=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("定义的网络")+'</div>'
    });
    var nw_store = new Ext.data.JsonStore({
        url:"/cloud_dashboard/get_cloudprovider_definednw_info?&cp_id="+cp_id,
        root: 'rows',
        fields: ['details', 'interface','name'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    nw_store.load();
    var vdc_nw_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: nw_store,
        stripeRows: true,
        frame:false,
        autoExpandColumn:0,
        enableHdMenu:true,
        autoScroll:true,
        width:'100%',
        height:173,
        layout:'fit',
        tbar:[networklabel],
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
            ,forceFit:true
            ,scrollOffset: 0
        },
        columns: [
                  {header: "名称", width: 168, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'name'},
                  {header: "详情", width: 168, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'details'},
                  {header: "接口", width: 168, sortable: false,css:'font-weight:bold; color:#414141;',dataIndex:'interface'}
                  
              ]
    });
    return vdc_nw_grid;
}



function iaasConfigPrivateNetwork(cp_id){
	
	var pri_networklabel=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("私有网络")+'</div>'
    });
    var nw_store = new Ext.data.JsonStore({
        url:"/cloud_dashboard/get_cloudprovider_privatenw_info?&cp_id="+cp_id,
        root: 'rows',
        fields: ['details', 'vdc','name','vlanid','privateip_used','dhcp'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    nw_store.load();
    var vdc_nw_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: nw_store,
        stripeRows: true,
        frame:false,
        //autoExpandColumn:0,
        //autoExpandMax:300,
        enableHdMenu:true,
        autoScroll:false,
        width:'100%',
        height:173,
        layout:'fit',
        tbar:[pri_networklabel],
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
            ,forceFit:true
            ,scrollOffset: 0
           
        },
        columns: [
                  {header: "VDC", width: 80, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'vdc'},
                  {header: "名称", width: 80, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'name'},
                  {header: "Nated", width:40, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'details'},
                  {header: "VLAN ID", width: 51, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'vlanid'},
                  {header: "私有IP 已经使用/总共",hidden:true, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'privateip_used'},
                  {header: "DHCP", width: 130, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'dhcp'}
                  
              ]
    });
    return vdc_nw_grid;
}
