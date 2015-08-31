

function ManagePublicIPPool(node, action)
{

    var tlabel_public_ip_pool=new Ext.form.Label({
        html:'<div>'+_("定义公共IP池")+'<br/></div>'
    });

    var label_public_ip_pool=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("公共IP池")+'<br/></div>'
    });

    var public_ip_pool_remove_list = new Array();

//    var button_ok=new Ext.Button({
//        name: 'ok',
//        id: 'ok',
//        text:_('Save'),
//        icon:'icons/accept.png',
//        cls:'x-btn-text-icon',
//        listeners: {
//
//                    click: function(btn)
//                        {
//                                ////////// ADD Public Pools //////////
//                                Ext.MessageBox.show({
//                                    title:_('Please wait...'),
//                                    msg: _('Please wait...'),
//                                    width:300,
//                                    wait:true,
//                                    waitConfig: {
//                                        interval:200
//                                    }
//                                });
//
//
//                        var public_ip_pool_details= Ext.util.JSON.encode({
//                            "remove_public_ip_pools":public_ip_pool_remove_list,
//                        });
//
//                        var url='/network/create_public_ip_pool?pool_infos='+public_ip_pool_details
//                        var ajaxReq=ajaxRequest(url,0,"POST",true);
//                        ajaxReq.request({
//                            success: function(xhr) {
//                                var response=Ext.util.JSON.decode(xhr.responseText);
//                                if(response.success){
//                                    Ext.MessageBox.alert( _("Status") , "Successfully Saved.");
//                                    closeWindow();
////                                    status=false;
//                                 }
//                                 else {
//                                    Ext.MessageBox.alert( _("Failure") , response.msg);
//                                }
//                            },
//                            failure: function(xhr){
//                                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
//                            }
//                        });
//
//                        }
//                    }
//    });
    

    var button_cancel=new Ext.Button({
    name: 'cancel',
    id: 'cancel',
    text:_('关闭'),
    icon:'icons/cancel.png',
    cls:'x-btn-text-icon',
    listeners: {
        click: function(btn) {
            status=false;
            closeWindow();
        }
    }
    });
    

    var add_button= new Ext.Button({
        id: 'add',
        text: _('添加'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn)
            {
                var w=new Ext.Window({
                        title :_('公共IP池'),
                        width :440,
                        height:400,
                        modal : true,
                        resizable : false
                    });
                    var p = Add_Public_IP_Pool(w, public_ip_pool_panel, null, 'ADD');
                    w.add(p);
                    w.show();
            }

        }
    });

    var substract_button= new Ext.Button({
        id: 'substract',
        text: _('移除'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                
                if(!public_ip_pool_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从列表中选择一行."));
                    return;
                }
                //Select for Remove
                if (public_ip_pool_grid.getSelectionModel().getSelected()){
                    var public_ip_pool_record = public_ip_pool_grid.getSelectionModel().getSelected()

//                    alert("---------------"+public_ip_pool_record.get("can_remove"));
                    if (public_ip_pool_record.get("can_remove") == false){
                            Ext.MessageBox.alert(_("错误"),_("不可以删除公共IP池"+public_ip_pool_record.get('name')+",保留的IP地址还存在."));
                            return;
                        }

                    if (public_ip_pool_record.get("id") != ""){

                        ////////// Delete Public Pools //////////
                        public_ip_pool_remove_list.push(public_ip_pool_record.get("id"));

                        var message_text = "确定要删除公共IP池"+ public_ip_pool_record.get("name");
                        Ext.MessageBox.confirm(_("Confirm"),message_text,function(id){
                                if(id=='yes')
                                {
                                        Ext.MessageBox.show({
                                            title:_('请稍候...'),
                                            msg: _('请稍候...'),
                                            width:300,
                                            wait:true,
                                            waitConfig: {
                                                interval:200
                                            }
                                        });

                                        var public_ip_pool_details= Ext.util.JSON.encode({
                                            "remove_public_ip_pools":public_ip_pool_remove_list
                                        });

                                        var url='/network/create_public_ip_pool?pool_infos='+public_ip_pool_details
                                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                                        ajaxReq.request({
                                            success: function(xhr) {
                                                var response=Ext.util.JSON.decode(xhr.responseText);
                                                if(response.success){
                                                    public_ip_pool_grid.getStore().remove(public_ip_pool_record);
                                                    Ext.MessageBox.alert( _("状态") , "已经成功删除.");
                                                 }
                                                 else {
                                                    Ext.MessageBox.alert( _("Failure") , response.msg);
                                                }
                                            },
                                            failure: function(xhr){
                                                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                                            }
                                        });
                                    }
                                });
                            }
                        }
                    }
                }
            });
        
    

    var edit_button= new Ext.Button({
        id: 'edit',
        text: _('编辑'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn)
            {
                if(!public_ip_pool_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从列表选择一行."));
                    return ;
                }
                var rrecord=public_ip_pool_grid.getSelectionModel().getSelected();

                var w=new Ext.Window({
                        title :_('编辑公共IP池'),
                        width :450,
                        height:400,
                        modal : true,
                        resizable : false
                    });
                    var p = Add_Public_IP_Pool(w, public_ip_pool_panel, rrecord, 'EDIT');
                    w.add(p);
                    w.show();
            }
        }
    });


    var public_ip_pool_store = new Ext.data.JsonStore({
        url: '/network/get_all_public_ip_pool',
        root: 'rows',
        fields: ['id', 'name', 'total_ips', 'available_ips', 'cidr', 'iplist', 'ip_info', 'all_ip_info', 'can_remove'],
        successProperty:'success'
//        listeners:{
//            loadexception:function(obj,opts,res,e){
//                var store_response=Ext.util.JSON.decode(res.responseText);
//                Ext.MessageBox.alert(_("Error"),store_response.msg);
//            }
//        }
    });

     public_ip_pool_store.load();


     var public_ip_pool_grid = new Ext.grid.GridPanel({
        store: public_ip_pool_store,
        enableHdMenu:false,
//        selModel:selmodel1,
        id:'public_ip_pool_grid',
        columns: [
            {
                id       :'id',
                header   : '编号',
                width    : 140,
                sortable : true,
                dataIndex: 'id',
                hidden : true
            },
            {
                header   : '名称',
                width    : 220,
                sortable : true,
                dataIndex: 'name',
                hidden : false
            },
            {
                header   : 'IP总量',
                width     : 150,
                sortable : false,
                dataIndex: 'total_ips',
                 hidden : false
            },
            {
                header : '可用IP',
                width  : 150,
                dataindex :'available_ips',
                hidden : false
            },
            {
                header   : 'cidr',
                width     : 100,
                sortable : false,
                dataIndex: 'cidr',
                 hidden : true
            },
            {
                header : 'iplist',
                width  : 100,
                dataindex :'iplist',
                hidden : true
            },
            {
                header : 'ip_info',
                width  : 100,
                dataindex :'ip_info',
                hidden : true
            },
            {
                header : 'all_ip_info',
                width  : 100,
                dataindex :'all_ip_info',
                hidden : true
            }

  ],

        stripeRows: true,

        height: 310,
        width:545,
        tbar:[label_public_ip_pool,{
            xtype: 'tbfill'
             },add_button,substract_button,edit_button],
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                edit_button.fireEvent('click',edit_button);
            }
         }
    });


    var public_ip_pool_panel=new Ext.Panel({
        id:"public_ip_pool_panel",
        width:555,
        height:367,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        bbar:[{
            xtype: 'tbfill'
        },button_cancel],
        items:[tlabel_public_ip_pool, public_ip_pool_grid]
    });

   var outerpanel=new Ext.FormPanel({
       height: 440,
       width: 670,
       autoEl: {},
       layout: 'column',
       items: [public_ip_pool_panel]
   });

   return outerpanel
}





//Add_Public_IP_Pool
function Add_Public_IP_Pool(w, public_ip_pool_panel, record, action)
{
    
    var public_ip_pool_grid = public_ip_pool_panel.items.get("public_ip_pool_grid");

    var tlabel_add_public_ip_pool=new Ext.form.Label({
        html:'<div>'+_("公共IP池可以被指定为整个网络/公共IP范围或私有的IP地址.你可通过CIDR来选择公共IP池和IPS.")+'<br/></div>'
    });

    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });

    var name_label=new Ext.form.Label({
        html: _('名称 :')
    });

    var name=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'name',
        id: 'name',
        width: 230,
        allowBlank:true
    });

     var pub_ip_name_label_panel=new Ext.Panel({
        id:"pub_ip_name_label_panel",
//        layout:"form",
        frame:false,
        width:100,
//        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:30,
//        bodyStyle:'padding-left:8px',
        items:[name_label]
    });

     var pub_ip_name_field_panel=new Ext.Panel({
        id:"pub_ip_name_field_panel",
//        layout:"form",
        frame:false,
        width:270,
//        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:30,
        bodyStyle:'padding-left:8px',
        items:[name]
    });

     var pub_ip_pool_name_panel=new Ext.Panel({
        id:"pub_ip_pool_name_panel",
        layout:"form",
        frame:false,
        width:380,
//        autoScroll:true,
        labelWidth:50,
        border:false,
        bodyBorder:false,
        height:30,
        bodyStyle:'padding-left:20px',
        items:[name]
    });

    var panels = Add_Public_IPs();
    var cidr_panel= panels.cidr_panel;
    var iplist_panel= panels.iplist_panel;
    var cidr = cidr_panel.items.get("cidr_grp_panel").items.get("cidr");
    var iplist = iplist_panel.items.get("iplist_grp_panel").items.get("iplist");
    var cidr_radio = cidr_panel.items.get("cidr_radio_label_panel").items.get("cidr_radio");
    var iplist_radio = iplist_panel.items.get("iplist_radio_label_panel").items.get("iplist_radio");

    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                  ///// Validation //////
                  if(name.getValue() == "")
                      {
                        Ext.MessageBox.alert(_("错误"),_("请输入池的名称."));
                        return ;
                      }
                  var pub_pool_store = public_ip_pool_grid.getStore();
                  for(var i=0; i<pub_pool_store.getCount(); i++)
                      {
                        if(pub_pool_store.getAt(i).get('name').toLowerCase() == name.getValue().toLowerCase()){

                            if (action == 'EDIT'){
                                if(pub_pool_store.getAt(i) != record){
                                    Ext.MessageBox.alert(_("错误"),_("池名称"+name.getValue().toLowerCase()+"已经存在."));
                                    return ;
                                }
                            }
                            else{
                                    Ext.MessageBox.alert(_("错误"),_("池名称"+name.getValue().toLowerCase()+"已经存在."));
                                    return ;
                                }
                        }
                      }


                if(cidr.getValue() == "" && iplist.getValue() == "")
                {
                    Ext.MessageBox.alert(_('错误'), _('请用适当的值填充.'));
                    return;
                }
        
                if(cidr_radio.getValue()) {
                    iplist.setValue("");
                }else if(iplist_radio.getValue()) {
                    cidr.setValue("");
                }

                ///// If cidr radio selected/////
                if (cidr_radio.getValue() || iplist_radio.getValue())
                    {
                       /////////  CIDR Validation /////////
                       if (cidr_radio.getValue()) {

                           var cidr_str = cidr.getValue();
                           var cidr_parts = cidr_str.split("-");
                           ///// cidr validation //////
                           if(cidr_parts.length == 1)
                               {
                                    var sts = fnValidateCIDR(cidr.getValue())
                                    if (!sts){
                                            Ext.MessageBox.alert(_('错误'), _('请输入有效的网络. 例如:138.33.88.0/23'));
                                            return;
                                    }
                               }
                            ///// cidr range validation //////
                            else if(cidr_parts.length == 2){
                                    for(var i=0; i<cidr_parts.length; i++){
                                        var sts = fnValidateIPAddress(cidr_parts[i])
                                        if (!sts){
                                                Ext.MessageBox.alert(_('错误'), _('请输入有效的IP范围. 例如:138.33.88.10-138.33.88.60'));
                                                return;
                                        }
                                    }
                                }
                            else{
                                    Ext.MessageBox.alert(_('错误'), _('请输入有效的网络/ IP范围. 例如:138.33.88.1/23 或者 138.33.88.10-138.33.88.60'));
                                    return;
                                }
                       }

                       /////////  IP list Validation /////////
                       if (iplist_radio.getValue()) {
                            var iplt = iplist.getValue().split(",");                            
                            for(var i=0; i<iplt.length; i++){
//                                alert("----------"+iplt[i]);
                                if (iplt[i] != "")
                                    {
                                        var sts = validate_ip_address(iplt[i])
                                         if (!sts){
                                                Ext.MessageBox.alert(_('错误'), _('请输入有效的IP地址. 例如:138.33.88.22, 138.33.88.24'));
                                                return;
                                            }
                                    }
                                }
                            }


                        var pool_info = new Object();
                        pool_info.name = name.getValue();
                        pool_info.cidr = cidr.getValue();
                        pool_info.cidr_radio = cidr_radio.getValue();
                        pool_info.iplist = iplist.getValue();
                        pool_info.iplist_radio = iplist_radio.getValue();
//                        alert("-----------"+record);
                        if(record != undefined){
                            pool_info.pool_id = record.get('id');
                        }

                        var pool_info_json= Ext.util.JSON.encode({
                            "pool_info":pool_info
                        });
                        var url='/network/create_public_ip_pool?pool_infos='+pool_info_json
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr){
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                  var result=response.rows;
                                   var pub_ip_pool_rec = Ext.data.Record.create([
                                            {
                                                name: 'id',
                                                type: 'string'
                                            },
                                            {
                                                name: 'name',
                                                type: 'string'
                                            },
                                            {
                                                name: 'total_ips',
                                                type: 'string'
                                            },
                                            {
                                                name: 'available_ips',
                                                type: 'string'
                                            },
                                            {
                                                name: 'cidr',
                                                type: 'string'
                                            },
                                            {
                                                name: 'iplist',
                                                type: 'string'
                                            },
                                            {
                                                name: 'ip_info',
                                                type: 'string'
                                            },
                                            {
                                                name: 'all_ip_info',
                                                type: 'string'
                                            }


                                    ]);

                                    if (action == 'ADD')
                                        {
                                            var pub_ip_pool_entry=new pub_ip_pool_rec({
                                                id : result.id,
                                                name : result.name,
                                                total_ips : result.total_ips,
                                                available_ips : result.available_ips,
                                                cidr : result.cidr,
                                                iplist : "",
                                                ip_info : result.iplist,
                                                all_ip_info : ""
                                            });

                                            public_ip_pool_grid.getStore().insert(0, pub_ip_pool_entry);
                                        }


                                    if (action == 'EDIT')
                                        {                                            
                                            record.set('name' , result.name);
                                            record.set('total_ips' , result.total_ips);
                                            record.set('available_ips' , result.available_ips);
                                            record.set('cidr' , result.cidr);
//                                            alert("===="+result.iplist);
                                            record.set('iplist' , "");
                                            record.set('ip_info' , result.iplist);
                                            record.set('all_ip_info' , "");
                                            record.set('all_ip_info' , "");
                                        }

                                      w.close();

                            }
                            else{
                                Ext.MessageBox.alert(_("Failure") ,response.msg);
                            }
                        },
                        failure: function(xhr){
                            Ext.MessageBox.alert( _("Failure"), xhr.statusText);
                        }

                    })


            }
          }
        }

     });


     var button_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('关闭'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn){
                w.close()
            }
        }
     });


     ////////////////  EDIT /////////////////
     if( action == "EDIT"){
         name.setValue(record.get("name"));
         cidr_radio.setValue(record.get("cidr")!=""?true:false);
         cidr.setValue(record.get("cidr"));
         iplist_radio.setValue(record.get("cidr")!=""?false:true);

         if (record.get("cidr") == "")
             {
//                 alert("------cc----"+record.get("ip_info"));
                 var ip_info = record.get("ip_info");
                 var ips = ""
                 for(var i=0; i<ip_info.length; i++){
                     ips = ips + ip_info[i].ip + ",";
                 }
                 iplist.setValue(ips);
             }

     }


    var pub_ip_fldset=new Ext.form.FieldSet({
        id:'pub_ip_fldset',
        title: _('公共IPs'),
        collapsible: false,
        autoHeight:true,
        labelSeparator:' ',
        width: 415,
//        labelWidth:labelWidth,
        collapsed: false,
        border: true,
        items :[panels.cidr_panel, panels.iplist_panel]
    });


   var public_ips_list_panel = new Ext.Panel({
        height:370,
        id:"public_ips_list_panel",
        layout:"form",
        frame:false,
        width:'90%',
//        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        bbar:[{
            xtype: 'tbfill'
        },button_ok, button_cancel],
        items:[tlabel_add_public_ip_pool, dummy_space1, pub_ip_pool_name_panel, pub_ip_fldset]
    });

    var parent_public_ips_list_panel=new Ext.Panel({
        id:"parent_public_ips_list_panel",
        layout:"form",
        width:475,
        //cls: 'whitebackground paneltopborder',
        height:395,
        frame:false,
        border:false,
        labelWidth:220,
        cls: 'whitebackground',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[public_ips_list_panel]
    });

    return parent_public_ips_list_panel;
}



function Add_Public_IPs()
{
    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });

    var dummy_space2=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });

    var cidr_label=new Ext.form.Label({
        html: _('网络/IP范围')
    });

    var cidr_eg_label=new Ext.form.Label({
        html: _('例如: 138.33.88.0/23 或者 138.33.88.10-138.33.88.60')
    });

    var iplist_eg_label=new Ext.form.Label({
        html: _('例如: 138.33.88.22, 138.33.88.24')
    });

    var iplist_label=new Ext.form.Label({
        html: _('私有IPs')
    });


    var cidr=new Ext.form.TextField({
//        fieldLabel: _('cidr'),
        name: 'cidr',
        id: 'cidr',
        width: 330,
        labelSeparator:"",
        allowBlank:true
    });

    var iplist=new Ext.form.TextArea({
//        fieldLabel: _('iplist'),
        name: 'iplist',
        id: 'iplist',
        width: 330,
        height: 90,
        labelSeparator:"",
        allowBlank:true
    });

    var cidr_radio=new Ext.form.Radio({
        boxLabel: _(''),
        hideLabel:true,
        checked:false,
        id:'cidr_radio',
        name:'range_radio',//Name should be same for all radio button
        listeners:{
            check:function(field,checked){
                if(checked){
                    iplist.setDisabled(true);
                    cidr.setDisabled(false);
                }else{

                }

            }
        }
    });

    //Default selection
    cidr_radio.setValue(true);

    var iplist_radio=new Ext.form.Radio({
        boxLabel: _(''),
        hideLabel:true,
        checked:false,
        id:'iplist_radio',
        name:'range_radio',//Name should be same for all radio button
        listeners:{
            check:function(field,checked){
                if(checked){
                    cidr.setDisabled(true);
                    iplist.setDisabled(false);
                }else{

                }

            }
        }
    });


     var cidr_radio_label_panel=new Ext.Panel({
        id:"cidr_radio_label_panel",
        layout:"column",
        frame:false,
        width:180,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:20,
        bodyStyle:'padding-left:8px',
        items:[cidr_radio, dummy_space1, cidr_label]
    });


     var cidr_eg_panel=new Ext.Panel({
        id:"cidr_eg_panel",
        layout:"column",
        frame:false,
        width:350,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:20,
//        bodyStyle:'padding-left:200px;padding-top:5px;',
        items:[cidr_eg_label]
    });


     var iplist_eg_panel=new Ext.Panel({
        id:"iplist_eg_panel",
        layout:"column",
        frame:false,
        width:200,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:50,
//        bodyStyle:'padding-left:200px;padding-top:5px;',
        items:[iplist_eg_label]
    });


     var iplist_radio_label_panel=new Ext.Panel({
        id:"iplist_radio_label_panel",
        layout:"column",
        frame:false,
        width:180,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:20,
        bodyStyle:'padding-left:8px',
        items:[iplist_radio, dummy_space2, iplist_label]
    });


     var cidr_grp_panel=new Ext.Panel({
        id:"cidr_grp_panel",
//        layout:"form",
        frame:false,
        width:380,
//        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:40,
        bodyStyle:'padding-left:30px',
        items:[cidr, cidr_eg_panel]
    });


     var cidr_panel=new Ext.Panel({
        id:"cidr_panel",
//        layout:"column",
        frame:false,
        width:430,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:65,
        bodyStyle:'padding-left:8px',
        items:[cidr_radio_label_panel, cidr_grp_panel]
    });

     var iplist_grp_panel=new Ext.Panel({
        id:"iplist_grp_panel",
//        layout:"form",
        frame:false,
        width:380,
//        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:120,
        bodyStyle:'padding-left:30px',
        items:[iplist, iplist_eg_panel]
    });


     var iplist_panel=new Ext.Panel({
        id:"iplist_panel",
//        layout:"column",
        frame:false,
        width:430,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:145,
        bodyStyle:'padding-left:8px',
        items:[iplist_radio_label_panel, iplist_grp_panel]
    });

    var panels = new Object();
    panels.cidr_panel = cidr_panel;
    panels.iplist_panel = iplist_panel;

    return panels;
}







function select_ip_checkbox (value,params,record){
//    alert("------"+value+"------"+params+"-----"+record.get("is_selected"));
//    record.set("is_selected", true);
    var id = Ext.id();
    (function(){
        var cb = new Ext.form.Checkbox({
            renderTo: id,
            width:100,
            height:16,
            checked:value,
            value:false,
            listeners:{
                check:function(field,checked){
                    //For make single selection, when clicking on check box.
                    var pub_ip_list_grid = Ext.getCmp('public_ips_list_grid');
                    var ips_store = pub_ip_list_grid.getStore();

                    if (record.get("can_remove") == false){
                            Ext.MessageBox.alert(_("错误"),_("无法删除保留的公共IP"+record.get('ip')+"."));
                            record.set('is_selected',true);
                            field.setValue(true);
                            return;
                        }

                    if(checked){
                        record.set('is_selected',true);
//                        pub_ip_list_grid.getSelectionModel().selectRow(rec_index,true);
                        field.setValue(true);
                    }else{
                        record.set('is_selected',false);
//                        pub_ip_list_grid.getSelectionModel().deselectRow(rec_index,true);
//                        alert("-----"+rec_index);
//                        pub_ip_list_grid.getSelectionModel().clearSelections();
                        field.setValue(false);
                    }
                }
            }
        });

    }).defer(5);
    return '<span id="' + id + '"></span>';
}




/////////////////////////////////////////////



