/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

 
function updateImageStorePanel(mainpanel,imagestore_id, imagestore_count)
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

    var imagestore_summary_grid = create_imagestore_grid(imagestore_id);    
   
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
    var summary_panel = new Ext.Panel({
        collapsible:false,
        //height:100,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'fit'
    });
     var imagestore_summary_panel = new Ext.Panel({
        collapsible:false,
        height:'100%',
        width:'100%',
        border:false,
        bodyStyle:'padding-top:10px;',
        bodyBorder:false,
        layout:'fit'
    });
    var summary_grid=create_summary_grid(imagestore_id)

    summary_panel.add(summary_grid);
//    imagehomepanel.add(dummyPanel);
    imagestore_summary_panel.add(imagestore_summary_grid);
    imagehomepanel.add(summary_panel);
    imagehomepanel.add(imagestore_summary_panel);
    mainpanel.add(topPanel);    
    
    mainpanel.doLayout();    
    
}

function create_summary_grid(imagestore_id){

     var label_summary=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_task'
    });

    var summary_store =new Ext.data.JsonStore({
        url:"/template/get_imagestore_summary_info?imagestore_id="+imagestore_id,
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

    summary_store.load();


    var summary_grid = new Ext.grid.GridPanel({
        //title:'Template Details',
        disableSelection:true,
        stripeRows: true,
        autoHeight:true,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 100,
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
            {header: "", width: 150, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'name',renderer:NewUIMakeUP},
            {header: "", width: 320, sortable: false,dataIndex:'value'}
        ],
        store:summary_store,
        tbar:[label_summary]
    });

    return summary_grid;

}

function image_store_summary_page(mainpanel,imagestore_id,node){

    var url="/template/get_imagestore_count?imagestore_id="+imagestore_id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(!response.success){
                Ext.MessageBox.alert(_("Failure"),response.msg);
                return;
            }           
            updateImageStorePanel(mainpanel,imagestore_id, response.count); 
        },
        failure: function(xhr){
            Ext.MessageBox.alert(_("Failure"),xhr.statusText);
        }
    });
}
 
function create_imagestore_grid(imagestore_id){

    var imagestore_columnModel = new Ext.grid.ColumnModel([       
     {
        header: _(""),
        width:50,
        sortable: false,
        dataIndex: 'desc',
        renderer: showTemplateDetailLink
    },
   
    {
        header: _("模板"),
        width: 100,
        sortable: true,
        dataIndex: 'template'
    },
     {
        header: _("版本"),
        width: 60,
        sortable: true,
        dataIndex: 'version'
     },
     {
        header: _("模板组"),
        width: 200,
        dataIndex: 'tg',
        sortable:true
    },
    {
        header: _("虚拟机"),
        width: 120,
        dataIndex: 'vm_num',
        sortable:false,
        renderer: showVMStatusLink,
        align:'right'

    },
    {
        header: _("镜像编号"),        
        dataIndex: 'image_id',
        sortable:false,
        hidden: true
    }]);


    var imagestore_store = new Ext.data.JsonStore({
        url: '/template/get_imagestore_details?imagestore_id='+imagestore_id,
        root: 'content',
        fields: ['template','version','tg','vm_num', 'desc', 'image_id','node_id'],
        successProperty:'success',
        listeners:{

            loadexception:function(obj,opts,res,e){                
                var store_response=Ext.util.JSON.decode(res.responseText);               
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }

        }
    });

    imagestore_store.load()
    var lbl_msg='模板信息';
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
                imagestore_summary_grid.getStore().filter('template', field.getValue(), false, false);
            }
        }
    }));
    var toolbar = new Ext.Toolbar({
        items: items
    });

    var imagestore_summary_grid = new Ext.grid.GridPanel({
//        disableSelection:true,
        store: imagestore_store,
        colModel:imagestore_columnModel,
        id:'imagestore_summary_grid',
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

    
    return imagestore_summary_grid;

}


function display_desc(image_desc) {    
    var display_string;
    if (image_desc == "_template_")
    {
        display_string = "A partially complete template intended for use as a template for expressing centralised provisioning schemes. A central provisioning scheme must have the following attributes: 1.  Shared storage for all GuestOS disks 2.  Identical storage mountpoints on all hosts (e.g. /mnt/guest_storage) 3.  Centrally accessable installation media (if appropriate) ";

    }
    else if(image_desc == "Fedora_PV_Install"){
        display_string ="This template creates a 5G virtual disk (vbd) and kicks off an interactive, anaconda installation for CentOS 5. The kernel_src and ramdisk_src point to the location from where the initial kernel and ramdisk are to be downloaded.";
     }    
    else if(image_desc == "CentOS_PV_Install"){
        display_string = " This template creates a 5G virtual disk (vbd) and kicks off an interactive, anaconda installation for CentOS 5. The kernel_src and ramdisk_src point to the location from where the initial kernel and ramdisk are to be downloaded.";
    }
    else if(image_desc == "Linux_CD_Install"){
         display_string = " 此模板创建一个10G虚拟磁盘 (vbd) 作为主硬盘驱动器。并设置从VM可启动的Linux的CD /DVD，同时，它提供各种具体的配置参数以便于部署操作系统在主硬盘驱动器上.";
    }
    else if(image_desc == "Windows_CD_Install"){
         display_string = " 此模板创建一个10G虚拟磁盘 (vbd) 作为主硬盘驱动器。并设置从VM可启动的Linux的CD /DVD，同时，它提供各种具体的配置参数以便于部署操作系统在主硬盘驱动器上.";
    }
    else {
        display_string = "No Information available for template added"+ image_desc;
    }

    Ext.MessageBox.alert("说明", display_string);  


}


function showImageDescription(data,params,record,row,col,store) {
    
    params.attr='ext:qtip="显示镜像说明"';
   
    if(data != "") {      
        var image_desc= record.get("template");    
        var nodeid = record.get("image_id");
        var fn1 = "display_help('" + nodeid + "')";

        //var returnVal = '<table><tr>'+data+'<td align="right"><a href="#" onClick= ' + fn1 + '><img src=" icons/file_edit.png "/></a> <a href="#" onClick= ' + fn2 + '><img src=" icons/information.png "/> </a></td> </tr></table>' ;

        var returnVal = '<a href="#" onClick= ' + fn1 + '><img src=" icons/information.png "/> </a>';
//        params.attr='ext:qtip="Show Image Description"' +
//                    '!important; background-position: right;'+
//                    'background-repeat: no-repeat;cursor: pointer;"';

        return returnVal;
    }
    else {
        
        return data;
    }
}

function image_group_summary_page(mainpanel,imagegroup_id,node){
    var url="/template/get_imagegroup_count?imagegroup_id="+imagegroup_id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(!response.success){
                Ext.MessageBox.alert(_("Failure"),response.msg);
                return;
            }
                   
            updateImageGroupPanel(mainpanel,imagegroup_id, response.info.group_name, response.info.num_templates);            
        },
        failure: function(xhr){
            Ext.MessageBox.alert(_("Failure"),xhr.statusText);
        }
    });
    centerPanel.setActiveTab(mainpanel);
}


function updateImageGroupPanel(mainpanel,imagegroup_id, group_name, imagegroup_count)
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

    var summary_panel = new Ext.Panel({
        collapsible:false,
        //height:100,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'fit'
    });
     var imagegrp_summary_panel = new Ext.Panel({
        collapsible:false,
        height:'100%',
        width:'100%',
        border:false,
        bodyStyle:'padding-top:10px;',
        bodyBorder:false,
        layout:'fit'
    });


    var imagegroups_summary_grid = create_imagegroup_grid(imagegroup_id);
    var summary_store_grid=create_summary_store_grid(imagegroup_id)
    summary_panel.add(summary_store_grid);
    imagegrp_summary_panel.add(imagegroups_summary_grid);
    imagehomepanel.add(summary_panel);
    imagehomepanel.add(imagegrp_summary_panel);
    mainpanel.add(topPanel);  
    mainpanel.doLayout();  
    
}

function create_summary_store_grid(grp_id){

     var label_summary=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_task'
    });

    var summary_st_store =new Ext.data.JsonStore({
        url:"/template/get_imagegrp_summary_info?grp_id="+grp_id,
        root: 'row',
        fields: ['name','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });

    summary_st_store.load();


    var summary_store_grid = new Ext.grid.GridPanel({
        //title:'Template Details',
        disableSelection:true,
        stripeRows: true,
        autoHeight:true,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 100,
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
            {header: "", width: 150, sortable: false, css:'font-weight:bold; color:#414141;',dataIndex:'name',renderer:NewUIMakeUP},
            {header: "", width: 320, sortable: false,dataIndex:'value'}
        ],
        store:summary_st_store,
        tbar:[label_summary]
    });

    return summary_store_grid;

}


function create_vminfo_grid(image_id, template_name){
    
    var vminfo_columnModel = new Ext.grid.ColumnModel([
     {
        header: _("虚拟机"),
        dataIndex: 'vm',
        hidden:true
    },
    {
        header: _("虚拟机"),        
        dataIndex: 'vm',

        sortable:true
    },
    {
        header: _("服务器"),       
        sortable: true,
        dataIndex: 'server'
    },
    {
        header: _("CPU"),        
        dataIndex: 'cpu',
        sortable:true
    },
    {
        header: _("内存"),       
        sortable: true,
        dataIndex: 'memory',
        align:'right'
    }]);
    
    var vminfo_store =new Ext.data.JsonStore({
        url: "/template/get_image_vm_info?image_id="+image_id,
        root: 'rows',
        fields: ['icon','vmid','vm','server','cpu','memory','node_id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    vminfo_store.load();
   
    var lbl_hdg=new Ext.form.Label({
        html:'<div class="labelheading" >'+_("虚拟机部署正在使用"+ template_name)+'<br/></div>'
    });

    var vminfo_grid = new Ext.grid.GridPanel({        
        store: vminfo_store,
        colModel:vminfo_columnModel,
        stripeRows: true,
        frame:true,
        id:'vminfo_grid',
//        cls:'grid_bg',
        forceFit :true,
        height : 245,
        autoWidth:true,
        autoExpandColumn:1,
        tbar:[ _('搜索: '),new Ext.form.TextField({
                fieldLabel: _('搜索'),
                name: 'search',                
                allowBlank:true,
                enableKeyEvents:true,
                listeners: {
                    keyup: function(field) {
                        vminfo_grid.getStore().filter('vm', field.getValue(), false, false);
                    }
                }
            }),{xtype:'tbfill'}
        ]
        ,listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            }
       }
    });    
    return vminfo_grid;
}

function display_VM_settings(image_id, template_name, vm_number) {   
    if(vm_number != 0)
    {
    var vminfo_grid = create_vminfo_grid(image_id, template_name);
   
    var vminfo_panel = new Ext.Panel({        
        cls:'westPanel',
        width:505,        
        height:275,        
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'close',
                id: 'close',
                text:_('关闭'),
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

    vminfo_panel.add(vminfo_grid);        
    showWindow(_("Information of Virtual Machines provisioned using "+ template_name),520,300,vminfo_panel);
}

}

function showVMStatusLink(data,cellmd,record,row,col,store) {
    if(data != "" & data != 0 ) {
        var image_id = record.get("image_id");
        var template_name = record.get("template");        
        var fn = "display_VM_settings('" + image_id + "','" + template_name + "','" + data + "')";
       
        var returnVal = '<a href="#" onClick=' + fn + '>' + data + '</a>';
        return returnVal;
    }
    else {
        
        return data;
    }
}



function display_edit_image_settings(node_id,template_name) {
    
    var node=leftnav_treePanel.getNodeById(node_id);
    if (node == null){
        node=new Ext.tree.TreeNode({
           text:  template_name,
           nodeid:node_id,
           id:node_id
        });

    }
    editImageSettings(node,'edit_image_settings');
    

}


function display_help(node_id) {
    
    var node=leftnav_treePanel.getNodeById(node_id);    
    getImageHelpInfo(node_id);
    

}


function showTemplateDetailLink(data,cellmd,record,row,col,store) {

        var node_id = record.get("image_id");  
        var template_name = record.get("template");
        var desc = record.get("desc");
        var fn1 = "display_edit_image_settings('" + node_id + "','" +  template_name + "')";
        var fn2 = "display_help('" + node_id + "')";         

        //var returnVal = '<table><tr>'+data+'<td align="right"><a href="#" onClick= ' + fn1 + '><img src=" icons/file_edit.png "/></a> <a href="#" onClick= ' + fn2 + '><img src=" icons/information.png "/> </a></td> </tr></table>' ;

        var returnVal = '<a href="#" onClick= ' + fn1 + '><img title="编辑模板设置" src="icons/file_edit.png "/></a><a href="#" onClick= ' + fn2 + '><img title="镜像说明" src=" icons/information.png "/> </a>';
//        cellmd.attr='ext:qtip="Show Image Description"' +
//                    '!important; background-position: right;'+
//                    'background-repeat: no-repeat;cursor: pointer;"';
        return returnVal;
       
}


function create_imagegroup_grid(imagegroup_id){

    
    var imagegroup_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("Image_ID"),
        dataIndex: 'image_id',
        sortable:false,
        hidden: true

    },
    {
        header: _(""),
        width: 50,
        dataIndex: 'details',
        sortable:false,
        renderer: showTemplateDetailLink
    },
    {
        header: _("模板"),
        width: 130,
        dataIndex: 'template',
        sortable:true       
 
    },
    {
        header: _("版本"),
        width: 60,
        dataIndex: 'version',
        sortable:true

    },
    {
        header: _("虚拟机"),
        width: 120,
        dataIndex: 'vm_num',
        sortable:false,
        renderer: showVMStatusLink,
        align:'right'
    },
    {
        header: _("CPUs"),
        sortable: false,
        width: 60,
        dataIndex: 'cpu',
        align:'right'
    },
    {
        header: _("内存(MB)"),
        sortable: false,
        width: 90,
        dataIndex: 'memory',
        align:'right'
    },
    {
        header: _("HVM"),       
        sortable: false,
        width: 50,
        dataIndex: 'hvm'
    },
    {
        header: _("修改者"),        
        dataIndex: 'modifier',
        sortable:false,
        hidden:true
    },
    {
        header: _("修改日期"),        
        dataIndex: 'modified_date',
        sortable:false,
        xtype: 'datecolumn', // use xtype instead of renderer
        format: 'M/d/Y',
        hidden:true
    }
    ]);

    var imagegroup_info_store =new Ext.data.JsonStore({
        url: '/template/get_imagegroup_details?imagegroup_id='+imagegroup_id,        
        root: 'info',
        fields: ['template','version','vm_num','cpu','memory', 'hvm', 'modifier', 'modified_date', 'image_id','node_id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    imagegroup_info_store.load();

    var lbl_msg='模板信息';
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
                imagegroup_info_grid.getStore().filter('template', field.getValue(), false, false);
            }
        }
    }));
    var toolbar = new Ext.Toolbar({
        items: items
    });

    var imagegroup_info_grid = new Ext.grid.GridPanel({        
        id:'imagegroup_summary_grid',         
        stripeRows: true,
        frame:false,        
        width:'100%',
        autoExpandColumn:2,
        height:400,
        autoScroll: true,
        tbar:toolbar,       
        colModel: imagegroup_columnModel,
        store:imagegroup_info_store
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

    return imagegroup_info_grid
}

function getImageHelpInfo(node_id){
    var url="/template/get_image_info?node_id="+node_id+"&level="+stackone.constants.IMAGE;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(!response.success){
                Ext.MessageBox.alert(_("Failure"),response.msg);
                return;
            }
            showImageInfoDilog(response.content);           
            
        },
        failure: function(xhr){
            Ext.MessageBox.alert(_("Failure"),xhr.statusText);
        }
    });
}
function showImageInfoDilog(content){
 var panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:587,
        height:525,
        autoScroll:true,        
        html    : "<span style='font-size:3; font-family: Verdana; color:#0000FF;text-align:left;'>"+content+"</span>",
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'close',
                id: 'close',
                text:_('关闭'),
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


    showWindow(_("显示模板说明"),600,550,panel);
}

function image_store_imageStroeStarter_page(mainpanel,imagestore_id, imagestore_count){
	if (mainpanel.items)
		mainpanel.removeAll(true);
	/*var topHtml = '';
	topHtml += '<div class="toolbar_hdg" >';
	topHtml += '</div>';*/
	var topHtml = '';
	topHtml += '<div class="image-store-starter-top">';
	topHtml += '	<div class="image-store-starter-top-text">';
	topHtml += _("什么是模板库？");
	topHtml += '<br/>';
	topHtml += '<br/>';
	topHtml += _("模板库是模板组的一个集合，您可以定义不同的模板组分配给每个数据中心，使每个数据中心的管理员只可以看到和使用自己的模板组，避免多个数据中心使用同一个模板组造成的误造作。");
	topHtml += '	</div>';
	topHtml += '	<div class="image-store-starter-top-img">';
	topHtml += '	</div>';
	topHtml += '</div>';
	
	var leftHtml = "";
	leftHtml += "<div class='image-store-starter-left-text'>";
	leftHtml += '<div>基本任务</div>';
	leftHtml += "<a href='#' onclick=javascript:data_center_datacenterStarter_page_addImageGroup();>新建模板组</a><br/>";
	leftHtml += "</div>";
	
	var rightHtml = '';
	rightHtml += '<div class="image-store-starter-right-text" >';
	rightHtml += _("模板常识");
	rightHtml += '<br/>';
	rightHtml += '<br/>';
	rightHtml += _("模板是一个配置策略的集合，从中可以创建一个或多个虚拟机的设置。Stackone虚拟化平台默认创建linux和windows模板，它通常包含了虚拟CPU，内存，存储和网络配置的默认值。");
	rightHtml += '</div>'
	
	var topPanel = new Ext.Panel({
		border: false,
		frame: true,
		height : 300,
		width : '100%',
		region : 'north',
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
		width : "100%",
		height : "100%",
		layout : 'border',
		border:false,//lbz更改：添加一句
		items : [topPanel, leftPanel, rightPanel]
	});
	mainpanel.add(vmStarterPanel);
	vmStarterPanel.doLayout();
	mainpanel.doLayout();
}

function data_center_datacenterStarter_page_addImageGroup(){
	addImageGroup(leftnav_treePanel.getSelectionModel().getSelectedNode());
}


function image_group_imageGroupStarter_page(mainpanel,imagestore_id, imagestore_count){
	if (mainpanel.items)
		mainpanel.removeAll(true);
	/*var topHtml = '';
	topHtml += '<div class="toolbar_hdg" >';
	topHtml += '</div>';*/
	var topHtml = '';
	topHtml += '<div class="image-group-starter-top">';
	topHtml += '	<div class="image-group-starter-top-text">';
	topHtml += _("什么是模板组？");
	topHtml += '<br/>';
	topHtml += '<br/>';
	topHtml += _("模板组是模板的一个集合，您可以分配模板到不同的模板组，满足不同用户的需求。");
	topHtml += '	</div>';
	topHtml += '	<div class="image-group-starter-top-img">';
	topHtml += '	</div>';
	topHtml += '</div>';
	
	var leftHtml = "";
	leftHtml += "<div class='image-group-starter-left-text'>";
	leftHtml += '<div>基本任务</div>';
	leftHtml += "<a href='#' onclick=javascript:image_group_imageGroupStarter_page_renameImageGroup();>重命名模板组</a><br/>";
	leftHtml += "</div>";
	
	var rightHtml = '';
	rightHtml += '<div class="image-group-starter-right-text" >';
	rightHtml += _("如何基于模板部署新虚拟机？");
	rightHtml += '<br/><br/>';
	rightHtml += _("1、选择一个模板。");
	rightHtml += '<br/>';
	rightHtml += _("2、点击左边的”部署VM“。。");
	rightHtml += '<br/>';
	rightHtml += _("3、从数据中心选择一台主机。");
	rightHtml += '<br/>';
	rightHtml += _("4、输入虚拟机名称，点击确定，一个新的虚拟机即可创建成功。");
	rightHtml += '</div>'
	
	var topPanel = new Ext.Panel({
		height : 300,
		width : '100%',
		region : 'north',
		border: false,
		frame: true,
		//border:false,//lbz更改：添加一句
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
		border: false,
		frame: true,
		region : 'center',
		bodyStyle : 'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
		html : rightHtml
	});

	var vmStarterPanel = new Ext.Panel({
		width : "100%",
		height : "100%",
		layout : 'border',
		border:false,//lbz更改
		items : [topPanel, leftPanel, rightPanel]
	});
	mainpanel.add(vmStarterPanel);
	vmStarterPanel.doLayout();
	mainpanel.doLayout();
}

//function image_group_imageGroupStarter_page_addImage(){
//	showWindow(_("创建模板")+":- "+leftnav_treePanel.getSelectionModel().getSelectedNode().text,400,300 ,templateform(leftnav_treePanel.getSelectionModel().getSelectedNode()));
//}
function image_group_imageGroupStarter_page_renameImageGroup() {
	renameImageGroup(leftnav_treePanel.getSelectionModel().getSelectedNode());
 }


function image_imageStarter_page(mainpanel,imagestore_id, imagestore_count){
	if (mainpanel.items)
		mainpanel.removeAll(true);
	/*var topHtml = '';
	topHtml += '<div class="toolbar_hdg" >';
	topHtml += '</div>';*/
	var topHtml = '';
	topHtml += '<div class="image-starter-top">';
	topHtml += '	<div class="image-starter-top-text">';
	topHtml += _("什么是模板？");
	topHtml += '<br/>';
	topHtml += '<br/>';
	topHtml += _("模板是Stackone的一组相关配置，包含了新建虚拟机相关的所有信息，例如：默认的虚拟机CPU、内存、网络、配置信息等参数（用户可根据不同需求修改默认的参数）。");
	topHtml += '<br/>';
	topHtml += '<br/>';
	topHtml += _("使用模板可以节省新建虚拟机和安装操作系统的时间，您可以克隆一个新的空白模板，也可以将现有虚拟机克隆为模板，然后通过模板来部署虚拟机。");
	topHtml += '	</div>';
	topHtml += '	<div class="image-starter-top-img">';
	topHtml += '	</div>';
	topHtml += '</div>';
	
	var leftHtml = "";
	leftHtml += "<div class='image-starter-left-text'>";
	leftHtml += '<div>基本任务</div>';
	leftHtml += "<a href='#' onclick=javascript:image_imageStarter_page_provisionImage();>部署VM</a><br/>";
	leftHtml += "<a href='#' onclick=javascript:image_imageStarter_page_editImageSettings();>编辑设置</a><br/>";
	leftHtml += "</div>";
	var rightHtml = '';
	rightHtml += '<div class="image-starter-right-text" >';
	rightHtml += _("如何克隆一个新的模板？");
	rightHtml += '<br/><br/>';
	rightHtml += _("1、选择一个默认的模板。");
	rightHtml += '<br/>';
	rightHtml += _("2、点击右键的“克隆模板”。");
	rightHtml += '<br/>';
	rightHtml += _("3、输入新模板的名称。");
	rightHtml += '<br/>';
	rightHtml += _("4、点击保存，一个新的模板将出现在你的模板组里面。");
	rightHtml += '</div>'
	var topPanel = new Ext.Panel({
		height : 300,
		width : '100%',
		region : 'north',
		border: false,
		frame: true,
		// border:false,//lbz更改：添加一句
		//bodyStyle : 'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
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
		width : "100%",
		height : "100%",
		layout : 'border',
		border:false,//lbz更改：添加一句
		items : [topPanel, leftPanel, rightPanel]
	});
	mainpanel.add(vmStarterPanel);
	vmStarterPanel.doLayout();
	mainpanel.doLayout();
}

function image_imageStarter_page_provisionImage() {
	getTargetNodes(null, leftnav_treePanel.getSelectionModel().getSelectedNode(), 'provision_image');
}

function image_imageStarter_page_editImageSettings() {
	editImageSettings(leftnav_treePanel.getSelectionModel().getSelectedNode(), 'edit_image_settings');
}
