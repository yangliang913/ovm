/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
function image_summary_page(mainpanel,image_id,node){
    
    if(mainpanel.items)
        mainpanel.removeAll(true);


    var template_info_grid=create_template_info_grid(image_id);
    var image_storage_grid=create_image_storage_grid(image_id);
    var image_nw_grid=create_image_nw_grid(image_id);
    //var vm_info_grid = create_vm_info_grid(image_id);
    var provision_settings_grid = create_prov_set(image_id);
    var bootparam_grid = create_boot_grid(image_id);
    var misc_grid = create_misc_grid(image_id);

    var panel1 = new Ext.Panel({
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'column',
        bodyStyle:'padding-top:5px;padding-right:5px'
    });
    
    var panel2 = new Ext.Panel({
        width:'100%',
       // height: 300,
        border:false,
        bodyBorder:false,
        layout:'column'
        //,bodyStyle:'padding-left:5px;'
        ,bodyStyle:'padding-top:10px;padding-right:5px'
    });
    

    var panel3 = new Ext.Panel({
        width:'100%',
        height: 160,
        border:false,
        bodyBorder:false,
        layout:'column'
        ,bodyStyle:'padding-top:10px;padding-right:5px'
    });

    var dummy_panel1 = new Ext.Panel({
        width:'1%',
        html:'&nbsp',
        height: 200,
        border:false,     
        bodyBorder:false
    });
    var dummy_panel2 = new Ext.Panel({
        width:'1%',
        html:'&nbsp',
        height: 250,
        border:false,      
        bodyBorder:false
    });
    var dummy_panel3 = new Ext.Panel({
        width:'1%',
        html:'&nbsp',
        height: 150,
        border:false,         
        bodyBorder:false
    });   

    var template_info_panel=new Ext.Panel({
        width:'49.5%',
        height: 200,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:5px;',
        layout:'fit'
    });

    var prov_details_panel=new Ext.Panel({
        width:'49.5%',
        height: 200,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:5px;',
        layout:'fit'
    });

    var storage_panel=new Ext.Panel({
        width:'49.5%',
        height: 150,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:5px;padding-top:10px;',
        layout:'fit'
    });
    
    var nw_panel=new Ext.Panel({
        width:'49.5%',
        height: 150,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:5px;padding-top:10px;',
        layout:'fit'
    });  
    
    var boot_info_panel=new Ext.Panel({
        width:'49.5%',
        height: 250,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:5px;padding-top:10px;',
        layout:'fit'
    });    

    var misc_details_panel=new Ext.Panel({
        width:'49.5%',
        height: 250,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:5px;padding-top:10px;',
        layout:'fit'
    });


    template_info_panel.add(template_info_grid);  
    panel1.add(template_info_panel);
    panel1.add(dummy_panel1);
    prov_details_panel.add(provision_settings_grid)
    panel1.add(prov_details_panel);

    boot_info_panel.add(bootparam_grid);
    panel2.add(boot_info_panel);
    panel2.add(dummy_panel2);
    misc_details_panel.add(misc_grid);
    panel2.add(misc_details_panel);

    storage_panel.add(image_storage_grid);
    
    nw_panel.add(image_nw_grid);

    panel3.add(storage_panel);
    panel3.add(dummy_panel3);
    panel3.add(nw_panel);

    var topPanel = new Ext.Panel({        
        collapsible:false,
        height:'100%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false,
        items:[panel1, panel2,panel3]
    });

//    var bottomPanel = new Ext.Panel({
//        collapsible:true,
//        title:"",
//        height:'100%',
//        width:'100%',
//        border:false,
//        cls:'headercolor',
//        bodyBorder:false,
//        items:[panel4]
//    });

    var image_homepanel=new Ext.Panel({
        height:"100%"
        ,items:[topPanel]
        ,bodyStyle:'padding:5px;'
    });
    
    mainpanel.add(image_homepanel);
    image_homepanel.doLayout();
    mainpanel.doLayout();
    centerPanel.setActiveTab(mainpanel);
}

function create_prov_set(image_id){

    var prov_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });

    var provisioning_label=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("模板参数")+'</div>'
    });


    var provisioning_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("属性"),
        width:150,
        dataIndex: 'attribute',
        css:'font-weight:bold; color:#414141;',
        sortable:true
    },

    {
        header: _("值"),
        dataIndex: 'value',
        sortable:true,
        width:200
    }
    ]);


    var provisioning_store = new Ext.data.JsonStore({
        url: '/node/get_provisioning_configs',
        root: 'rows',
        fields: ['attribute','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }

    });

    provisioning_store.load({
        params:{
            image_id:image_id
        }
    });


   var provisioning_grid = new Ext.grid.GridPanel({
        store: provisioning_store,
        colModel:provisioning_columnModel,
        disableSelection:true,
        stripeRows: true,
        frame:false,
        border:true,
        cls:'hideheader',
        enableHdMenu:false,
        id:'provision_settings_grid',
        width:'100%',
        autoExpandColumn:1,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        tbar:[provisioning_label,{xtype:'tbfill'}
        ]

    });
   
    return provisioning_grid;

}

 function create_boot_grid(image_id){

     var boot_label=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("引导参数")+'</div>'
    });

    var boot_info_store =new Ext.data.JsonStore({
        url: "/template/get_boot_info?image_id="+image_id,
        root: 'rows',
        fields: ['name','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });

    boot_info_store.load();

    var boot_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        stripeRows: true,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 250,
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
            {header: "", width: 150, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:NewUIMakeUP},
            {header: "", width: 200, sortable: false, dataIndex: 'value'}
        ],
        store:boot_info_store,
        tbar:[boot_label,{xtype:'tbfill'}]
    });

    return boot_grid;

 }

 function create_misc_grid(image_id){

    var misc_label=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("其它选项")+'</div>'
    });

    var misc_info_store =new Ext.data.JsonStore({
        url: "/template/get_template_grid_info?image_id="+image_id+"&type=Misc",
        root: 'rows',
        fields: ['attribute','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });

    misc_info_store.load();

    var misc_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        stripeRows: true,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 250,
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
            {header: "", width: 150, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'attribute'},
            {header: "", width: 200, sortable: false, dataIndex: 'value'}
        ],
        store:misc_info_store,
        tbar:[misc_label]
    });

    return misc_grid;


}


function create_vm_info_grid(image_id){

//     var label_strge=new Ext.form.Label({
//         html:'<div class="toolbar_hdg">'+_("VM Information")+'</div>',
//         id:'label_task'
//     });

    var vm_info_store =new Ext.data.JsonStore({
        url: "/template/get_vm_status?image_id="+image_id,
        root: 'rows',
        fields: ['name','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });

    vm_info_store.load();

    var vm_info_grid = new Ext.grid.GridPanel({        
        disableSelection:true,
        stripeRows: true,        
        border:false,
        cls:'hideheader',       
        width: '100%',
        height: 100,
        enableHdMenu:false,
        enableColumnMove:false,       
        autoScroll:true,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [
            {header: "", width: 100, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 130, sortable: false, dataIndex: 'value'}
        ],
        store:vm_info_store
        //tbar:[label_strge]
    });

    return vm_info_grid;

}

function create_template_info_grid(image_id){

    var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_task'
    });

    var template_info_store =new Ext.data.JsonStore({
        url: "/template/get_template_details?image_id="+image_id,
        root: 'rows',
        fields: ['name','value','imageid'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });

    template_info_store.load();

    var template_info_grid = new Ext.grid.GridPanel({
        //title:'Template Details',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 200,
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
            {header: "", width: 150, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex: 'name',renderer:NewUIMakeUP},
            {header: "", width: 200, sortable: false, dataIndex: 'value'},
            {header: "", width: 130, sortable: false, dataIndex: 'imageid',hidden:true}
        ],
        store:template_info_store,
        tbar:[label_strge]
    });

    return template_info_grid;
}

//function showSet(data,params,record,row,col,store){
//
//    if(row==0){
//        if(data != "") {
//            var desc= record.get("value");
//            var node_id = record.get("imageid");
//            var fn1 = "display_edit_image_settings('" + node_id + "')";
//            var fn2 = "display_help('" + node_id + "')";
//            var returnVal =  '<table ><tr> <td>' + desc+ '</td> <td align="right"><a href="#" onClick= ' + fn1 + '><img src=" icons/file_edit.png "/></a> <a href="#" onClick= ' + fn2 + '><img src=" icons/information.png "/></a></td> </tr></table>';
//            return returnVal;
//        }
//    }
//    else {
//        return data;
//    }
//}

function create_image_storage_grid(image_id){

    var image_storage_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("类型"),
        width: 40,
        dataIndex: 'type',
        sortable:false
    },
    {
        header: _("位置"),
        width: 100,
        sortable: false,
        dataIndex: 'filename'
    },
    {
        header: _("设备"),
        width: 70,
        dataIndex: 'device',
        sortable:false
    },
    {
        header: _("模式"),
        width: 70,
        sortable: false,
        dataIndex: 'mode'
    },
    {
        header: _("共享"),
        width: 70,
        sortable: false,
        dataIndex: 'shared'
    }]);


 var image_storage_store = new Ext.data.JsonStore({
        url: '/node/get_disks?image_id='+image_id,
        root: 'disks',
        fields: ['type','filename','device', 'mode', 'shared'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){                
                var store_response=Ext.util.JSON.decode(res.responseText);               
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }

        }
    });

    image_storage_store.load()

     var label_strge=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("存储信息")+'</div>',
        id:'label_task'
    });

    var image_storage_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: image_storage_store,
        colModel:image_storage_columnModel,
        stripeRows: true,
        frame:false,       
        enableHdMenu:false,
        autoScroll:true,
        id:'image_storage_summary_grid',       
        width:'100%',
        autoExpandColumn:1,
        height: 220,
        tbar:[label_strge]
    });

    return image_storage_grid;

}

function create_image_nw_grid(image_id){


    var image_nw_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("名称"),
        width: 150,
        dataIndex: 'name',
        sortable:false
    },
    {
        header: _("详情"),
        width: 170,
        sortable: false,
        dataIndex: 'description'
    },
    {
        header: _("MAC地址"),
        width: 100,
        dataIndex: 'mac',
        sortable:false
    }]);

    var image_nw_store = new Ext.data.JsonStore({
        url: '/network/get_nws?image_id='+image_id,
        root: 'rows',
        fields: ['name','description','mac'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){                
                var store_response=Ext.util.JSON.decode(res.responseText);                
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }

        }
    });
    image_nw_store.load();

    var label_nw=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("网络信息")+'</div>',
        id:'label_task'
    });

    var image_nw_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        store: image_nw_store,
        colModel:image_nw_columnModel,
        stripeRows: true,
        frame:false,        
        enableHdMenu:false,
        id:'image_nw_summary_grid',       
        autoScroll:true,
        width:'100%',
        autoExpandColumn:1,
        height: 220,
        tbar:[label_nw]
    });

    return image_nw_grid;

}

function image_vminfo_page(mainpanel,image_id,node){

     if(mainpanel.items)
        mainpanel.removeAll(true);

    var vm_details_grid=create_vm_details(image_id);

    var panel1 = new Ext.Panel({
        width:'75%',
        height: 350,
        border:false,
        bodyBorder:false,
        layout:'fit',
        bodyStyle:'padding-top:10px;padding-left:5px;'
    });

    panel1.add(vm_details_grid);

    var topPanel = new Ext.Panel({
        collapsible:false,
        height:'50%',
        width:'100%',
        border:false,
        cls:'headercolor',
        bodyBorder:false,
        items:[panel1]
    });

    var vm_main=new Ext.Panel({
        height:"100%"
        ,items:[topPanel]
        ,bodyStyle:'padding:5px;'
    });

    mainpanel.add(vm_main);
    vm_main.doLayout();
    mainpanel.doLayout();


  }

function create_vm_details(image_id){


    var vm_details_columnModel = new Ext.grid.ColumnModel([
//     {
//          header: _("VM"),
//          width: 100,
//          dataIndex: 'vm',
//          sortable:true,
//          hidden:true
//     },
    {
        header: _("名称"),
        width: 90,
        dataIndex: 'vm',
        sortable:true
    },
    {
        header: _("服务器"),
        width: 100,
        sortable: true,
        dataIndex: 'server'
    },
    {
        header: _("CPU"),
        width: 60,
        dataIndex: 'cpu',
        sortable:true
    },
    {
        header: _("内存(MB)"),
        width: 100,
        sortable: true,
        dataIndex: 'memory'
    },
    {
        header: _("模板版本"),
        width: 110,
        sortable: true,
        dataIndex: 'template_version'
    },
    {
        header: _("评论"),
        width: 150,
        sortable: true,
        dataIndex: 'vm_comment'
    }]);

    var vm_details_store =new Ext.data.JsonStore({
        url: "/template/get_image_vm_info?image_id="+image_id,
        root: 'rows',
        fields: ['icon','vmid','vm','server','cpu','memory','template_version','vm_comment','node_id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    vm_details_store.load();

    var lbl_hdg=new Ext.form.Label({
        html:'<div class="toolbar_hdg" >'+_("部署虚拟机正在使用模板")+'<br/></div>'
    });

    var vm_details_grid = new Ext.grid.GridPanel({
        store: vm_details_store,
        colModel:vm_details_columnModel,

        disableSelection:true,
        stripeRows: true,
        frame:false,
        border:true,
        enableHdMenu:false,
        id:'vm_details_grid',
        width:'100%',
        height:300,
        autoExpandColumn:1,
        autoExpandMin:150,
        tbar:[lbl_hdg,{xtype:'tbfill'},
            _('搜索: '),new Ext.form.TextField({
                fieldLabel: _('搜索'),
                name: 'search',
                allowBlank:true,
                enableKeyEvents:true,
                listeners: {
                    keyup: function(field) {
                        vm_details_grid.getStore().filter('vm', field.getValue(), false, false);
                    }
                }
            })
        ]
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

    return vm_details_grid;
}

    
function image_info_page(mainpanel,node_id,node){
    if(mainpanel.items)
        mainpanel.removeAll(true);

    var ajaxReq = ajaxRequest(node.attributes.url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(!response.success){
                Ext.MessageBox.alert(_("Failure"),response.msg);
                return;
            }

            var info_panel=new Ext.Panel({
                border:false,
                frame:true,
                closable: false,
                layout  : 'fit',
                html    : "<span style='font-size:3; font-family: Verdana; color:#0000FF;text-align:left;'>"+
                            response.content+"</span>"
            });

            mainpanel.add(info_panel);
            mainpanel.doLayout();
        }
        ,failure:function(xhr) {
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}


