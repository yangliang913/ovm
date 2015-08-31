

function ImageFromVM(w,node, action, res)
{
    var MY_MODE = 'VM_TO_TEMPLATE';
                
   
    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });

    var dummy_space2=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });

    var dummy_space_height_10px = new Ext.form.Label({
        html:_('&nbsp;<div style="height:10px"/>')
    });

    var common_desc=new Ext.form.Label({
        html: _('指定模板详情')
    });

    var ref_template_desc=new Ext.form.Label({
        html: _("选择的虚拟机没有相关联的模板. 请从列表选择一个合适的模板.")
    });

    var temp_group_tip = new Ext.form.Label({
        html: _('&nbsp;模板组名称')
    });


    var temp_group_tip_icon = new Ext.form.Label({
        html:'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\n\
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\n\
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;提示:'
     })

    var image_store_tip_icon = new Ext.form.Label({
        html:'提示:&nbsp;'
     })

    var shared_loc_tip_icon = new Ext.form.Label({
        html:'提示:&nbsp;'
     })

    var image_store_label=new Ext.form.Label({
        html: _('镜像池')
    });

    var image_store_desc=new Ext.form.Label({
        html: _('磁盘将复制到Stackone管理主机.')
    });

    var shared_loc_label=new Ext.form.Label({
        html: _('共享磁盘')
    });

    var shared_loc_desc=new Ext.form.Label({
        html: _('在管理服务器指定共享磁盘的完整路径.')
    });
    
    



    var image_name_txtf = new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'image_name',
        id: 'image_name',
        allowBlank:false,
//        labelWidth:100,
//        labelStyle: 'font-weight:bold;',
        width:320,
        labelSeparator:"",
        listeners:{}
    });


    var shared_loc_txtf = new Ext.form.TextField({
//        fieldLabel: _('Path'),
        name: 'shared_loc',
        id: 'shared_loc',
        labelSeparator:"",
        allowBlank:false,
        labelWidth:100,
//        labelStyle: 'font-weight:bold;',
        width:400,
        emptyText :_("共享磁盘"),
//        labelSeparator:" ",
        listeners:{}
    });


    var image_group_store = new Ext.data.JsonStore({
        url: "/template/get_all_image_groups?imagestore_id="+node.attributes.id,
        root: 'rows',
        fields: ['name', 'id'],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        id:'id',
        successProperty:'success',
        listeners:{}
    });

    image_group_store.load();

    var image_group_combo=new Ext.form.ComboBox({
        fieldLabel: _('模板组'),
        allowBlank:false,
        width: 320,
        store:image_group_store,
        id:'image_group_store',
        forceSelection: true,
        triggerAction:'all',
        emptyText :_("选择"),
        minListWidth:50,
        displayField:'name',
        valueField:'id',
        mode:'local',
        labelSeparator:"",
        listeners:{}
    });


    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                    var image_name = image_name_txtf.getValue();
                    var image_group_id = image_group_combo.getValue();
                    var disk_copy_mode = 'IMAGE_STORE';
                    var shared_loc = "";
//                    alert(image_name+"---"+image_group);

                    if(image_name == "")
                        {
                        Ext.MessageBox.alert(_("错误"),_("请输入模板名称"));
                        return ;
                        }

                    if(image_group_id == "")
                        {
                        Ext.MessageBox.alert(_("错误"),_("请选择模板组"));
                        return ;
                        }

                    var plt_ui_hlpr = new stackone.PlatformUIHelper(platform,MY_MODE);
                    var xtrCmpnts = plt_ui_hlpr.getXtraComponents();
                    if(xtrCmpnts.indexOf("ref_image_fldset")>=0 ){
                        var ref_image_id = ""
                        if (!res.has_image){
                            ref_image_id = ref_image_combo.getValue();
                            if(ref_image_id == "") {
                                Ext.MessageBox.alert(_("错误"),_("请选择一个参考模板"));
                                return ;
                            }
                        }
                    }

                    if(shared_loc_radio.getValue()){
                        disk_copy_mode = 'SHARED_LOCATION';
                        shared_loc = shared_loc_txtf.getValue();
                        if(shared_loc == "")
                            {
                            Ext.MessageBox.alert(_("错误"),_("请输入共享磁盘位置"));
                            return ;
                            }
                    }

                    var context = {}
                    context['disk_copy_mode'] = disk_copy_mode;
                    context['shared_loc'] = shared_loc
                    context['ref_image_id'] = ref_image_id;
                    
                    if(xtrCmpnts.indexOf("host_id")>=0 ){
                         if( Ext.getCmp('host_id').getValue()==''|| Ext.getCmp('host_id').getValue()==null){
                          Ext.MessageBox.alert(_("错误"),_("请选择一个主机"));
                          return
                         }
                         if(Ext.getCmp('data_store').getValue()==''|| Ext.getCmp('data_store').getValue()==null){
                           Ext.MessageBox.alert(_("错误"),_("请选择一个存储库"));
                            return
                         }
                    }

                   
                    context['node_id'] = Ext.getCmp('host_id').getValue();
                    context['datastore_name'] = Ext.getCmp('data_store').getValue();

                    var context_json= Ext.util.JSON.encode(context);
                    var task_url="/template/create_image_from_vm?node_id="+node.attributes.id+"&image_name="+image_name+"&image_group_id="+image_group_id+"&context="+context_json
                    SubmitImageFromVMTask(task_url);
                    w.close();
                }
            }
      });


    var button_cancel=new Ext.Button({
        name: 'cancel',
        id: 'm_cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                w.close();
            }
        }
    });



    var image_name_fldset=new Ext.form.FieldSet({
        id:'image_name_fldset',
        title: _(''),
        collapsible: false,
        autoHeight:true,
        labelSeparator:'',
        width: 450,
//        labelWidth:labelWidth,
        collapsed: false,
        border: false,
        items :[image_name_txtf, image_group_combo, temp_group_tip_icon, temp_group_tip]
    });

    var ref_image_group_store = new Ext.data.JsonStore({
        url: "/template/get_all_image_groups?imagestore_id="+node.attributes.id,
        root: 'rows',
        fields: ['name', 'id'],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        id:'id',
        successProperty:'success',
        listeners:{}
    });

    ref_image_group_store.load();

    var ref_image_group_combo=new Ext.form.ComboBox({
        fieldLabel: _('模板组'),
        allowBlank:false,
        width: 320,
        store:ref_image_group_store,
        id:'ref_image_group_combo',
        forceSelection: true,
        triggerAction:'all',
        emptyText :_("选择"),
        minListWidth:50,
        displayField:'name',
        valueField:'id',
        mode:'local',
        labelSeparator:"",
        listeners:{
            select:function(combo,record,index){
                    var group_id = record.get('id');
                    ref_image_store.load({
                         params:{
                            group_id:group_id
                        }
                })
            }
        }
    });

    var ref_image_store = new Ext.data.JsonStore({
        url: "/template/get_all_images",
        root: 'rows',
        fields: ['name', 'id'],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        id:'id',
        successProperty:'success',
        listeners:{}
    });

    var ref_image_combo=new Ext.form.ComboBox({
        fieldLabel: _('模板'),
        allowBlank:false,
        width: 320,
        store:ref_image_store,
        id:'ref_image_combo',
        forceSelection: true,
        triggerAction:'all',
        emptyText :_("选择"),
        minListWidth:50,
        displayField:'name',
        valueField:'id',
        mode:'local',
        labelSeparator:"",
        listeners:{}
    });

    var ref_image_fldset=new Ext.form.FieldSet({
        id:'ref_image_fldset',
        title: _('参考模板'),
        collapsible: false,
        autoHeight:true,
        labelSeparator:'',
        width: 450,
//        labelWidth:labelWidth,
        collapsed: false,
        border: false,
        items :[ref_template_desc, dummy_space_height_10px, ref_image_group_combo, ref_image_combo]
    });

    var image_store_radio = new Ext.form.Radio({
        boxLabel: _(''),
        hideLabel:true,
        checked:false,
        id:'image_store_radio',
        name:'disk_path_radio',//Name should be same for all radio button
        listeners:{
            check:function(field,checked){
                if(checked){
                    shared_loc_txtf.setDisabled(true);
                }else{

                }
            }
        }
    });

    //Default selection
    image_store_radio.setValue(true);


    var shared_loc_radio = new Ext.form.Radio({
        boxLabel: _(''),
        hideLabel:true,
        checked:false,
        id:'shared_loc_radio',
        name:'disk_path_radio',//Name should be same for all radio button
        listeners:{
            check:function(field,checked){
                if(checked){
                    shared_loc_txtf.setDisabled(false);
                }else{

                }
            }
        }
    });


     var shared_loc_txt_panel=new Ext.Panel({
        id:"shared_loc_txt_panel",
        layout:"column",
        frame:false,
        width:430,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:30,
        bodyStyle:'padding-left:30px',
        items:[shared_loc_txtf]
    });


     var image_store_radio_label_panel=new Ext.Panel({
        id:"image_store_radio_label_panel",
        layout:"column",
        frame:false,
        width:400,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:20,
        bodyStyle:'padding-left:8px',
        items:[image_store_radio, dummy_space1, image_store_label]
    });



     var image_store_desc_panel=new Ext.Panel({
        id:"image_store_desc",
        layout:"column",
        frame:false,
        width:430,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:20,
        bodyStyle:'padding-left:30px',
        items:[image_store_tip_icon, image_store_desc]
    });


     var shared_loc_desc_panel=new Ext.Panel({
        id:"shared_loc_desc_panel",
        layout:"column",
        frame:false,
        width:430,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:20,
        bodyStyle:'padding-left:30px',
        items:[shared_loc_tip_icon, shared_loc_desc]
    });


     var shared_loc_radio_label_panel=new Ext.Panel({
        id:"shared_loc_radio_label_panel",
        layout:"column",
        frame:false,
        width:400,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:20,
        bodyStyle:'padding-left:8px; margin-top:8px',
        items:[shared_loc_radio, dummy_space2, shared_loc_label]
    });


    var radio_button_fldset=new Ext.form.FieldSet({
        id:'radio_button_fldset',
        title: _('模板磁盘位置'),
        collapsible: false,
        autoHeight:true,
        labelSeparator:'',
        width: 450,
//        labelWidth:labelWidth,
        collapsed: false,
        border: false,
        items :[image_store_radio_label_panel,
                image_store_desc_panel,
                shared_loc_radio_label_panel,
                shared_loc_desc_panel,
                shared_loc_txt_panel]
    });

    var host=new Ext.Button({
        tooltip:'选择主机',
//        icon:'icons/accept.png',
        name: 'host',
//        height:40,
        width:30,
        id: 'host',
        
//        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {


                 var url="/node/get_vcenter_nodes";
                url+="?vm_id="+node.id;
                var ajaxReq=ajaxRequest(url,0,"GET");
                ajaxReq.request({
                    success: function(xhr) {//alert(xhr.responseText);
                        var json=Ext.util.JSON.decode(xhr.responseText);
                        showWindow(_("选择一个目标节点"),315,325,NodeSelectionDialog(node,null,json,action, null));
                        
                       
               },
                    failure: function(xhr){
                        Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                    }
                });


                
                 
               
            },
            beforeshow : function( Component  ) {
                 
            }
        }
    });
    var store=new Ext.Button({
        tooltip:'选择存储库',
//        icon:'icons/accept.png',
        name: 'host',
//        height:40,
        width:30,
        id: 'store',

//        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if( Ext.getCmp('host_id').getValue()==''|| Ext.getCmp('host_id').getValue()==null){
                          Ext.MessageBox.alert(_("错误"),_("请选择一个主机"));
                          return
                         }
                showWindow(_("选择存储库"),700,400,dataStoreDialog(node.id));
                 Ext.MessageBox.show({
                            title:_('请稍候...'),
                            msg: _('请稍候...'),
                            width:300,
                            wait:true,
                            waitConfig: {
                                interval:200
                            }
                        });


            }
        }
    });

    var select_template=new Ext.form.Label({
        html:'选择主机:'
    });
    var host_name = new Ext.form.TextField({
        fieldLabel: _('主机'),
        name: 'host_name',
        id: 'host_name',
        allowBlank:false,
        disabled : true,
//        labelWidth:100,
//        labelStyle: 'font-weight:bold;',
        width:150
//        labelSeparator:"",
//        listeners:{}
    });
    var host_id = new Ext.form.TextField({
        name: 'host_id',
        id: 'host_id',
        hidden: true,
//        labelWidth:100,
//        labelStyle: 'font-weight:bold;',
        width:0
    });
   
    var data_store = new Ext.data.JsonStore({
        url:"/template/get_all_image_groups?imagestore_id="+node.attributes.id,
        root: 'rows',
        fields: ['name', 'id'],
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        id:'id',
        successProperty:'success'
//        listeners:{}
    });

    image_group_store.load();

    var datastore_name = new Ext.form.TextField({
        fieldLabel: _('存储库'),
        name: 'data_store',
        id: 'data_store',
        allowBlank:false,
        disabled : true,
//        labelWidth:100,
//        labelStyle: 'font-weight:bold;',
        width:150
//        labelSeparator:"",
//        listeners:{}
    });

     var host_panel=new Ext.Panel({
        id:"host_panel",
        layout:"column",
        frame:false,
        height:'50%',
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:30px',
        items:[
            {
            width: '57%',
            layout:'form',
            border:false,
            items:[host_name]
        },
        {
            width: '15%',
            layout:'form',
            border:false,
            items:[host]
        }
        ,{
            width: 0,
            layout:'form',
            border:false,
            items:[host_id]
        }]

    });
    var storag_panel=new Ext.Panel({
        id:"storag_panel",
        layout:"column",
        frame:false,
        height:'50%',
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding-left:30px',
         items:[
            {
            width: '57%',
            layout:'form',
            border:false,
            items:[datastore_name]
        },
        {
            width: '15%',
            layout:'form',
            border:false,
            items:[store]
        }
      ]
        
    });


    var host_storag_fldset=new Ext.form.FieldSet({
        id:'host_storag_fldset',
        title: _('数据存储'),
        collapsible: false,
        layout:"form",
        autoHeight:true,
        labelSeparator:'',
        width:'100%',
//        labelWidth:labelWidth,
        collapsed: false,
        border: false,
        items :[host_panel,storag_panel]
    });
   
    
    var vm_to_image_inner_panel_height = 525;//430
    var vm_to_image_outer_panel_height = 555;//440
    if(res.has_image){
        vm_to_image_inner_panel_height = 298;
        vm_to_image_outer_panel_height = 310;//310
    }

   var vm_to_image_inner_panel = new Ext.Panel({
        height:vm_to_image_inner_panel_height,
        id:"vm_to_image_inner_panel",
        layout:"form",
        frame:false,
        width:'100%',
//        autoScroll:true,
        border:false,
        bodyBorder:true,
//        bodyStyle:'padding:5px 5px 5px 5px',
        bbar:[{
            xtype: 'tbfill'
        },button_ok, button_cancel],
        items:[common_desc, image_name_fldset, radio_button_fldset]
    });


    vm_to_image_inner_panel.add(common_desc)
    vm_to_image_inner_panel.add(image_name_fldset)
    if (!res.has_image){
        vm_to_image_inner_panel.add(ref_image_fldset)
    }
    vm_to_image_inner_panel.add(radio_button_fldset);

    vm_to_image_inner_panel.add(host_storag_fldset);

//     alert(Ext.getCmp('host_storag_fldset').isVisible())
//   if(Ext.getCmp('host_storag_fldset').isVisible()){
//        host_name.setValue(node.parentNode.text)
//        host_id.setValue(node.parentNode.id)
//    }

    var platform="";
    var url="/node/get_platform?"

    if(node.id!=null)
        url+="node_id="+node.id+"&type="+stackone.constants.DOMAIN;

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                platform=response.platform;
                template_platform_UI_helper(node,platform,MY_MODE,true,true);
                
            }
            else
                Ext.MessageBox.alert(_("Failure"),response.msg);
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
    
    




   
    var vm_to_image_outer_panel = new Ext.Panel({
        id:"vm_to_image_outer_panel",
        layout:"form",
        width:460,
        height:vm_to_image_outer_panel_height,
        frame:false,
        border:false,
//        labelWidth:220,
        cls: 'whitebackground',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[vm_to_image_inner_panel]
    });
    return vm_to_image_outer_panel;
}


function template_platform_UI_helper(vm_node,platform,change_seting_mode,flag,hide){
    var plt_ui_hlpr = new stackone.PlatformUIHelper(platform,change_seting_mode);
    var components=plt_ui_hlpr.getComponentsToDisable();

    //alert(components.length+"--"+components);
//    if(hide){
//        for(var x=0;x<components.length;x++){
//            Ext.getCmp(components[x]).hide();
//        }
//    }
    for(var z=0;z<components.length;z++){
        Ext.getCmp(components[z]).setDisabled(flag);
    }
    
    if(plt_ui_hlpr.isDataStoreSupported()){
            Ext.getCmp('host_name').setValue(vm_node.parentNode.text)
            Ext.getCmp('host_id').setValue(vm_node.parentNode.id)
            var url="/node/get_data_store";
                url+="?host_id="+vm_node.parentNode.id;

           var ajaxReq=ajaxRequest(url,0,"GET",true);
            ajaxReq.request({
                success: function(xhr) {//alert(xhr.responseText);
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    
                    if(response.success){
                        var length=response.info.length;
                        for(var i=0;i<length;i++){
                            if(response.info[i].name==vm_node.text){
                               Ext.getCmp('data_store').setValue(response.info[i].name)
                            }
                        }


                    }
                    else
                        Ext.MessageBox.alert(_("Failure"),response.msg);
                },
                failure: function(xhr){
                    Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                }
            });
        }

}


function dataStoreDialog(vm_id){
    var tlabel_datastoredialog=new Ext.form.Label({
        html:'<div>'+_("存储库")+'<br/></div>'
    });
    var label_datastoredialog=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("存储库")+'<br/></div>'
    });
//     var url="/node/get_datastore";

     var selected_host_id=Ext.getCmp('host_id').getValue();
     var url="/node/get_data_store";
         url+="?host_id="+selected_host_id;
     var datastore_store = new Ext.data.JsonStore({
        url: url,
        root: 'info',
        fields: ['id','name'],//, 'drivetype', 'capacity', 'provisioned', 'free', 'type', 'thinprovisioning', 'access'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            },
            load :function ( Store ,  records, Ooptions ) {
                Ext.MessageBox.hide();
            }
        }
    });

     datastore_store.load();

      var datastore_grid = new Ext.grid.GridPanel({
        store: datastore_store,
        enableHdMenu:false,
//        selModel:selmodel1,
        id:'datastore_grid',
        columns: [
            {
                id       :'编号',
                header   : 'Id',
                width    : 140,
                sortable : true,
                dataIndex: 'id',
                hidden : true
            },
            {
                header   : '名称',
                width    : 140,
                sortable : true,
                dataIndex: 'name',
                hidden : false
            }
//            {
//                header   : 'DriveType',
//                width     : 150,
//                sortable : false,
//                dataIndex: 'drivetype',
//                 hidden : false
//            },
//            {
//                header : 'Capacity',
//                width  : 150,
//                dataindex :'capacity',
//                hidden : false
//            },
//            {
//                header   : 'Provisioned',
//                width     : 100,
//                sortable : false,
//                dataIndex: 'provisioned',
//                 hidden : false
//            },
//            {
//                header : 'Free',
//                width  : 100,
//                dataindex :'free',
//                hidden : false
//            },
//            {
//                header : 'Type',
//                width  : 100,
//                dataindex :'type',
//                hidden : false
//            },
//            {
//                header : 'ThinProvisioning',
//                width  : 100,
//                dataindex :'thinprovisioning',
//                hidden : false
//            },
//            {
//                header : 'Access',
//                width  : 100,
//                dataindex :'access',
//                hidden : false
//            }


  ],

        stripeRows: true,

        height: 310,
        width:680,
        tbar:[label_datastoredialog],
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
//                edit_button.fireEvent('click',edit_button);
            },
            render:function(th){
//            Ext.MessageBox.hide();
            }
         }
    });

    var button_cancel=new Ext.Button({
        name: 'cancel',
        id: 'can',
        text:_('关闭'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow();
            }
        }
    });
     var store_ok=new Ext.Button({
                name: 'store_ok',
                id: 'store_ok',
                text:_('确定'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        var datastore_grid_record = datastore_grid.getSelectionModel().getSelected()
                        datastore_grid_record.get("name");
                        Ext.getCmp('data_store').setValue(datastore_grid_record.get("name"))
                        closeWindow();
                    }
                }
            })

     var datastor_panel=new Ext.Panel({
        id:"datastor_panel",
        width:690,
        height:367,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        bbar:[{
            xtype: 'tbfill'
        },store_ok,button_cancel],
        items:[tlabel_datastoredialog, datastore_grid]
    });

   var outerpanel=new Ext.FormPanel({
       height: 440,
       width: 695,
       autoEl: {},
       layout: 'column',
       items: [datastor_panel]
   });

   return outerpanel



}



function SubmitImageFromVMTask(url)
{
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var res=Ext.util.JSON.decode(xhr.responseText);
            if(res.success){
                closeWindow();
                Ext.MessageBox.alert(_("Success"),res.msg);
            }else{
                Ext.MessageBox.alert(_("Error"),res.msg);
            }
        },
        failure: function(xhr){
            //alert('Fail');
            try{
                var res=Ext.util.JSON.decode(xhr.responseText);
                Ext.MessageBox.alert(_("Error"), res.msg);
            }catch(e){
                Ext.MessageBox.alert(_("Error"),_("Failure: ") +xhr.statusText);
            }
        }
    });
}