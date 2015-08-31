/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */


function CloudTemplateLibrary_summary_page(mainpanel,templibrary_id,node){
  
   if(mainpanel.items){
        mainpanel.removeAll(true);
    }
    
    var cloudtemplatelibrary_homepanel=new Ext.Panel({
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
        items:[cloudtemplatelibrary_homepanel]
    });
    var summary_panel = new Ext.Panel({
        collapsible:false,
        //height:100,
        width:'100%',
        border:false,
        bodyBorder:false,
        layout:'fit'
    });
     var cloudtemplatelibrary_summary_panel = new Ext.Panel({
        collapsible:false,
        height:'100%',
        width:250,
        border:false,
//        bodyStyle:'padding-top:10px;',
        bodyBorder:false,
        layout:'fit'
    });
    var vdcid=node.parentNode.id;
    var url = "/cloud/get_cp_feature_set?vdc_id="+vdcid;
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
    
               var summary_grid=createprovider_summary_grid(templibrary_id,node,response.info)
               summary_panel.add(summary_grid);
               //imagehomepanel.add(dummyPanel);    
                cloudtemplatelibrary_homepanel.add(summary_panel);
                cloudtemplatelibrary_homepanel.add(cloudtemplatelibrary_summary_panel);
                mainpanel.add(topPanel);
                mainpanel.doLayout();

            }else{
                Ext.MessageBox.alert(_("失败"),_("无法加载供应商."));
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });


    
}

function createprovider_summary_grid(templibrary_id,node,cp_feature){

   if(is_feature_enabled(cp_feature,stackone.constants.CF_ACCOUNT))
         accounthide=false
    else
        accounthide=true
    
  
    var label_summary=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("概览")+'</div>',
        id:'label_task'
    });

    var templateprovider_columnModel = new Ext.grid.ColumnModel([
     {
        header: _("IaaS名称"),
        width:120,
        sortable: true,
        hidden:true,
        dataIndex: 'providername'
     },
     {
        header: _("IaaS类型"),
        width:90,
        sortable: true,
        hidden:true,
        dataIndex: 'type'
     },
      {
        header: _("账户名称"),
        dataIndex: 'account_name',
         width:90,
        sortable:true,
        hidden:accounthide
     },
     {
        header: _("模板组名称"),
        width:90,
        sortable: true,
        dataIndex: 'name'
     },
     {
        header: _("模板"),
        width: 90,
        sortable: true,
        align:'right',
        dataIndex: 'number'
     },
     {
        header: _("模板组编号"),
        dataIndex: 'tmpgroupid_id',
        sortable:false,
        hidden: true
    }]);

  var summary_store =new Ext.data.JsonStore({
        url:"/cloud_template/get_cloudtemplatelibrary_summary_info?templibrary_id="+templibrary_id+"&vdc_id="+node.parentNode.attributes.id,
        root: 'info',
        fields: ['name','type','number','tmpgroupid_id','providername','account_name'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    summary_store.load();


    var summary_grid = new Ext.grid.GridPanel({       
        disableSelection:true,
        colModel:templateprovider_columnModel,
        stripeRows: true,
//        autoHeight:true,
        border:true,        
        width: '100%',
        height:570,
        enableHdMenu:false,
        enableColumnMove:false,
        autoScroll:true,
        autoExpandColumn:3,
        frame:false,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },       
        store:summary_store,
        tbar:[label_summary]
    });

    return summary_grid;

}

 function CloudTemplateGroup_summary_page(mainpanel,templategroup_id,node)
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
        height:570,
        width:'100%',
        border:false,
//        bodyStyle:'padding-top:10px;',
        bodyBorder:false,
        layout:'fit'
    });
    vdcid=node.parentNode.parentNode.id;
     var url = "/cloud/get_cp_feature_set?vdc_id="+vdcid;
     var ajaxReq=ajaxRequest(url,0,"POST",true);
     ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success)
            {
                var CloudTemplateGroup_summary_grid =create_CloudTemplateGroup_grid(templategroup_id,node,response.info);
                imagegrp_summary_panel.add(CloudTemplateGroup_summary_grid);
                imagehomepanel.add(summary_panel);
                imagehomepanel.add(imagegrp_summary_panel);
                mainpanel.add(topPanel);
                mainpanel.doLayout();
            }else{
                Ext.MessageBox.alert(_("失败"),_("无法加载供应商."));
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });

    

}

function create_CloudTemplateGroup_grid(templategroup_id,node,cp_feature){

     /*if(is_feature_enabled(cp_feature,stackone.constants.CF_ACCOUNT))
    accounthide=false
    else
    accounthide=true*/
    var autoExpandColumn=6;
    var hide_CpuMenStor=true;
    if(is_feature_enabled(cp_feature,stackone.constants.CF_MEM_VCPU)){
        hide_CpuMenStor=false;
        autoExpandColumn=2;

    }
    
    if(is_feature_enabled(cp_feature,stackone.constants.CF_REGION))
    regionhide=false
    else
    regionhide=true
    var imagegroup_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("模板编号"),
        dataIndex: 'node_id',
        sortable:false,
        hidden: true

    },
    {
        header: _("VDC编号"),
        dataIndex: 'vdc_id',
        sortable:false,
        hidden: true

    },
//    {
//        header: _(""),
//        width: 40,
//        dataIndex: 'details',
//        sortable:true
//         ,renderer:function(value,params,record,row){
//            params.attr='ext:qtip="Template Details"' +
//                'style="background-image:url(icons/information.png) '+
//                '!important; background-position: right;'+
//                'background-repeat: no-repeat;cursor: pointer;"';
//
//        return value;
//        }
//    },
    {
        header: _('名称'),
        width: 170,
        dataIndex: 'name',
        sortable:true
    },
     
    {
        header: _("IaaS名称"),
        width: 90,
        hidden:true,
        dataIndex: 'cloud_provider',
        sortable:true      

    },
     {
        header: _("区域"),
        sortable: true,
        width: 70,
        dataIndex: 'region',
        hidden:regionhide        
    },  
    {
        header: _("平台"),
        sortable: true,
        width: 80,
        dataIndex: 'platform',
        hidden:regionhide
    },   
    {
        header: _("资源"),
        width: 150,
        dataIndex: 'location',
        sortable:true,
        hidden:regionhide
       
    },
    {
        header: _("架构"),
        width: 90,
        dataIndex: 'architecture',
        sortable:true       

    },
    {
            header: _("vCPU"),
            width: 90,
            dataIndex: 'cpu',
            sortable:true,
            align:'right',
            hidden:hide_CpuMenStor

   },
    {
            header: _("内存(MB)"),
            width: 110,
            dataIndex: 'memory',
            sortable:true,
            align:'right',
            hidden:hide_CpuMenStor

    },
    {
            header: _("存储(GB)"),
            width: 110,
            dataIndex: 'size',
            sortable:true,
            align:'right',
            hidden:hide_CpuMenStor

    },
    {
        header: _("供应商编号"),
        width: 100,
        dataIndex: 'provider_id',
        sortable:true
        ,hidden: true

    },
    {
        header: _("账户编号"),
        width: 100,
        dataIndex: 'account_id',
        sortable:true
        ,hidden: true

    },
    {
        header: _(""),
        width: 35,
        dataIndex: 'node_type',
        sortable:true
        ,hidden:true

    },
    {
        header: _(""),
        width: 35,
        dataIndex: 'region_id',
        sortable:true
        ,hidden:true

    },
    {
        header: _(""),
        width: 35,
        dataIndex: 'cp_type',
        sortable:true
        ,hidden:true

    }
    ]);

    var templategroup_info_store =new Ext.data.JsonStore({
        url: '/cloud_template/get_cloudtemplategroup_details?templategroup_id='+templategroup_id+"&templategroup_name="+node.attributes.text,
        root: 'info',
        fields: ['node_id','vdc_id','name','cloud_provider','platform', 'location',
                'architecture','provider_id','region','account_id','node_type','cp_type','region_id','memory','cpu','size'],
        successProperty:'success',
        listeners:{
            beforeload : function(){
                Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: _('请稍候...'),
        width:600,
        wait:true,
        waitConfig: {
            interval:200
        }
        });
            },
            load : function(){
                 Ext.MessageBox.hide();
       

            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    templategroup_info_store.load();

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
                cloudtemplategroup_info_grid.getStore().filter('name', field.getValue(), false, false);
            }
        }
    }));

    var toolbar = new Ext.Toolbar({
        items: items
    });

    var cloudtemplategroup_info_grid = new Ext.grid.GridPanel({
        id:'imagegroup_summary_grid',
        stripeRows: true,
        frame:false,
        width:'100%',
//        autoHeight:true,
        autoExpandColumn:autoExpandColumn,
        autoExpandMax:480,
        autoExpandMin:350,
        height:'100%',
        autoScroll: true,
        tbar:toolbar,
        colModel: imagegroup_columnModel,
        store:templategroup_info_store
        ,listeners:{
            rowcontextmenu :function(grid,rowIndex,e) {
                e.preventDefault();
                handle_rowclick(grid,rowIndex,"contextmenu",e);
            },
            rowdblclick :function(grid,rowIndex,e) {
                handle_rowclick(grid,rowIndex,"click",e);
            }
//           , rowclick :function(grid,rowIndex,e) {
//
//                show_templatedetails(grid,rowIndex);
//
//            }
        }
    });

    return cloudtemplategroup_info_grid
}




function CloudTemplate_summary_page(mainpanel,template_id,node)
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


    var CloudTemplateGroup_summary_grid = create_CloudTemplate_grid(template_id,node);

    imagegrp_summary_panel.add(CloudTemplateGroup_summary_grid);
    imagehomepanel.add(summary_panel);
    imagehomepanel.add(imagegrp_summary_panel);
    mainpanel.add(topPanel);
    mainpanel.doLayout();

}


function create_CloudTemplate_grid(template_id,node){

    var image_columnModel = new Ext.grid.ColumnModel([
    {
        header: _("模板编号"),
        dataIndex: 'node_id',
        sortable:true,
        hidden: true

    },
    {
        header: _('名称'),
        width: 200,
        dataIndex: 'name',
        sortable:true

    },
    {
        header: _("类型"),
        width: 35,
        dataIndex: 'cloud_type',
        sortable:true,
        hidden:true

    },
    {
        header: _("Owner"),
        sortable: true,
        width:100,
        dataIndex: 'owner'        
    },
    {
        header: _("平台"),
        sortable: true,
        width: 45,
        dataIndex: 'platform',
        hidden:true
    },
    {
        header: _("状态"),
        width: 100,
        dataIndex: 'state',
        sortable:true
    },
    {
        header: _("位置"),
        width: 340,
        dataIndex: 'location',
        sortable:true

    },
    {
        header: _("架构"),
        width: 100,
        dataIndex: 'architecture',
        sortable:true

    },
    {
        header: _("供应商编号"),
        width: 100,
        dataIndex: 'provider_id',
        sortable:true,
        hidden: true


    },
    {
        header: _("账户编号"),
        width: 100,
        dataIndex: 'account_id',
        sortable:true,
        hidden: true

    }
    
    ]);

    var templategroup_info_store =new Ext.data.JsonStore({
        url: '/cloud_template/get_cloudtemplate_details?template_id='+template_id+"&name="+node.attributes.text,
        root: 'info',
        fields: ['node_id','name','cloud_type','owner', 'platform', 'state', 'location','architecture','provider_id','account_id'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    templategroup_info_store.load();

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
                cloudtemplate_info_grid.getStore().filter('name', field.getValue(), false, false);
            }
        }
    }));
    var toolbar = new Ext.Toolbar({
        items: items
    });

    var cloudtemplate_info_grid = new Ext.grid.GridPanel({
        id:'image_summary_grid',
        stripeRows: true,
        frame:false,
        width:'100%',
        autoExpandColumn:6,
        autoExpandMax:480,
        autoExpandMin:350,
        height:500,
        autoScroll: true,
        tbar:toolbar,
        colModel: image_columnModel,
        store:templategroup_info_store
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

    return cloudtemplate_info_grid
}

function show_templatedetails(grid,rowIndex){

    var record=grid.getStore().getAt(rowIndex)


    var id=record.get('id')
    var name=record.get('name');
    var providername=record.get('cloud_provider');
    var region=record.get('region');
    var location=record.get('location');
    var architecture=record.get('architecture');
    var platform=record.get('platform');

    
    var url="/cloud_template/get_templatedetails?name="+name+
        "&provider="+providername+"&region="+region+"&location="+location+"&architecture="+architecture+
        "&platform="+platform;

//    var content=""
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            var content=response.content
            editor.setValue(content);
            if(!response.success){
                Ext.MessageBox.alert(_("失败"),response.msg);
                return;
            }
        }

     })

     
     var editor=new Ext.form.TextArea({
        width: 450,
        height: 205,
        bodyStyle:'padding:0px 0px 0px 0px',
        readOnly:true
    });
    
    var panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:455,
        height:205,
        items:[editor],
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'ok',
                id: 'ok',
                text:_('确定'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        closeWindow();                        
                    }
                }
            }),          
        ]
    });

   var win=new Ext.Window({
        title:"模板详情",
        width: 450,
//        layout:'fit',
        height: 200,
        modal: true,
        resizable: false,
        closable:true
    });

    win.add(panel);
    win.show();


}
