/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */


function vCenterlist(node){
    
    var header_text = "发现和管理已经部署的VCenter.";
    var lbl=new Ext.form.Label({
        html:'<div style="" class="labelheading">'+ _(header_text) +'</div></br>'
    });

     var new_vCenter_button=new Ext.Button({
        name: 'new_vCenter',
        id: 'new_vCenter',
        text: "添加",
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var w=new Ext.Window({
                        title :_('添加vCenter'),
                        width :350,
                        height:298,
                        modal : true,
                        resizable : false
                    });
                    var p = vCenter(w,panel,null,'ADD');
                    w.add(p);
                    w.show();

            }
        }

    });

    var vCenter_remove_button=new Ext.Button({
        name: 'vCenter_remover',
        id: 'vCenter_remove',
        text: "移除",
        icon:'icons/delete.png',
        cls:'x-btn-text-icon' ,
        listeners: {
            click: function(btn) {
                if(!vCenter_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从列表选择一行."));
                    return ;
                }
                var vCenter_grid_record = vCenter_grid.getSelectionModel().getSelected()
                 var message_text = "确定要移除"+ vCenter_grid_record.get("host") + "吗? 所有被Stackone管理的VCenter实体将删除.";
                        Ext.MessageBox.confirm(_("确认"),message_text,function(id){
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

                                        var url='/vcenter/remove_vCenter?id='+vCenter_grid_record.get("id");
                                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                                        ajaxReq.request({
                                            success: function(xhr) {
                                                var response=Ext.util.JSON.decode(xhr.responseText);
                                                if(response.success){
                                                    vCenter_grid.getStore().remove(vCenter_grid_record);
                                                    Ext.MessageBox.alert( _("状态") , "已经成功删除.");
                                                    getNavNodes();
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

    });

     var vCenter_edit_button=new Ext.Button({
        name: 'vCenter_edit',
        id: 'vCenter_edit',
        text: "编辑",
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                 if(!vCenter_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从列表选择一行."));
                    return ;
                }
                var rrecord=vCenter_grid.getSelectionModel().getSelected();

                var w=new Ext.Window({
                        title :_('编辑已经部署的vCenter'),
                        width :350,
                        height:312,
                        modal : true,
                        resizable : false
                    });
                    var p = vCenter(w,panel,rrecord,'EDIT');
                    w.add(p);
                    w.show();
            }
        }

    });

     var import_button= new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('导入'),
        icon:'icons/appliance_import.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var selected=vCenter_grid.getSelectionModel().getSelected()
                if(!selected){
                    Ext.MessageBox.alert(_("错误"),_("请从列表选择一行."));
                    return ;
                }else{
                    var url = "/vcenter/test_vcenter_connection?"
                    Ext.MessageBox.show({
                                        title:_('请稍候...'),
                                        msg: _('请稍候...'),
                                        width:200,
                                        wait:true,
                                        waitConfig: {
                                            interval:200
                                            }
                                        });
                    var ajaxReq=ajaxRequest(url,0,"POST",true);
                    ajaxReq.request({
                             params: {   
                                         hostname:selected.get('host'),
                                         username:selected.get('username'),
                                         password:selected.get('password'),
                                      },
                             success: function(xhr){
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                     var w=new Ext.Window({
                                        title :_('导入vCenter'),
                                        width :670,
                                        height:485,
                                        modal : true,
                                        resizable : false,
                                         listeners: {
                                              show : function(w) {
                                                  Ext.MessageBox.show({
                                                    title:_('请稍候...'),
                                                    msg: _('请稍候...'),
                                                    width:200,
                                                    wait:true,
                                                    waitConfig: {
                                                        interval:200
                                                        }
                                                    });

                                              },
                                                render :function(c,v) {
                                              }


                                          }
                                     });
                                     
                                     w.add(vCenter_import(w, vCenter_grid, node));
                                     w.show();

                                }else{
                                    Ext.MessageBox.alert( _("Failure") , response.msg);
                                 }
                             },
                             failure: function(xhr){
                                 Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                             }
                    });

                 }

            }
        }
     });

     var columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), width: 150,hidden:true, sortable: false, dataIndex: 'id'},
        {header: _("主机"), width: 225, sortable: false, dataIndex: 'host'},
        {header: _("端口"), width: 0, sortable: false,hidden:true, dataIndex: 'port'},
        {header: _("协议"), width: 200, sortable: false, dataIndex: 'protocol'},
        {header: _("用户名"), width: 150,hidden:true, sortable: false, dataIndex: 'username'},
        {header: _("密码"), width: 0,hidden:true, sortable: false, dataIndex: 'password'},


    ]);

    var vCenter_list_store = new Ext.data.JsonStore({
        url: '/vcenter/get_vCenters',
        root: 'rows',
        fields: [ 'id', 'host', 'port', 'protocol','username','password'],
        successProperty:'success',
        listeners:{
            load:function(my_store, records, options){

            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
   vCenter_list_store.load();

     var vCenter_grid = new Ext.grid.GridPanel({
        store: vCenter_list_store,
        colModel:columnModel,
        id: 'vCenter_grid',
        stripeRows: true,
        frame:false,
//        selModel:virtual_nw_selmodel,
        width:'100%',
        //autoExpandColumn:2,
        height:350,
        autoScroll:true,
        enableHdMenu:false,
        autoExpandColumn:2,
        tbar:[{
                xtype: 'tbfill'
            },
            new_vCenter_button,
            '-',
            vCenter_edit_button,
            '-',
            vCenter_remove_button,
            '-',
            import_button

        ],
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                vCenter_edit_button.fireEvent('click',vCenter_edit_button);
            }
         }
    });


    var panel = new Ext.Panel({
        bodyStyle:'padding:5px 5px 5px 5px',
        width:450,
        height:420,
        //frame:true,
        cls: 'whitebackground',
        items:[lbl,vCenter_grid]
        ,bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('关闭'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {closeWindow();}
                    }
            })
        ]
    });
    return panel;

}


function vCenter(w,panel,record,action){
    var connect_status=false;
    var vCenter_grid=panel.items.get("vCenter_grid");
    var vCenter_grid_record = vCenter_grid.getSelectionModel().getSelected()

    var prior_des=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:('Credential software resent host.')
    });

    var prior_des0=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:('   ')
    });

    var dummy_space5=new Ext.form.Label({
        html:_('&nbsp;&nbsp;&nbsp;&nbsp;<div style="height:4px"/>')
    });

     var dummy_space6=new Ext.form.Label({
        html:_('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<div style="width:90px"/>')
    });

    var dummy_space7=new Ext.form.Label({
        html:_('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<div style="height:4px"/>')
    });

    var dummy_space8=new Ext.form.Label({
        html:_('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<div style="height:4px"/>')
    });

    var dummy_space9=new Ext.form.Label({
        html:_('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<div style="height:4px"/>')
    });

    var dummy_space10=new Ext.form.Label({
        html:_('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<div style="height:4px"/>')
    });

    var dummy_space11=new Ext.form.Label({
        html:_('&nbsp;&nbsp;<div style="height:4px"/>')
    });

    var dummy_space12=new Ext.form.Label({
        html:_('&nbsp;&nbsp;<div style="height:4px"/>')
    });

    var vCenterHost_label=new Ext.form.Label({
        html:_('&nbsp;&nbsp;vCenter主机')
    });

    var port_label=new Ext.form.Label({
        html:_('&nbsp;&nbsp;端口')
    });

    var ssl_label=new Ext.form.Label({
        html:_('&nbsp;&nbsp;协议')
    });

    var username_label=new Ext.form.Label({
        html:_('&nbsp;&nbsp;用户名')
    });

    var password_label=new Ext.form.Label({
        html:_('&nbsp;&nbsp;密码')
    });
    var testlable_success=new Ext.form.Label({
        html:'<b>'+_('成功连接')+'</b>'
    });
    var testlable_failure=new Ext.form.Label({
        html:'<b>'+_('失败')+'</b>'
    });
    var testlable_wait=new Ext.form.Label({
        html:'<div ><b>'+_("正在连接，请稍候...........")+'</b></div>'
    });
    var dummy_space_lable=new Ext.form.Label({
        html:_('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<div style="height:9px"/>')
    });

    var prior_des1=new Ext.form.Label({
         width :280,
         height:30,
        //html:"<b>Actions</b>"
        html:"请输入已经部署VCenter的详细信息. </br> </b>"
    });

    var prior_header=new Ext.form.Label({
         width :310,
         height:20,
        //html:"<b>Actions</b>"
        html:"<b>连接详情:</br> </br> </b>"
    });

    var cred_header=new Ext.form.Label({
         width :310,
         height:20,
        //html:"<b>Actions</b>"
        html:"<b>认证: </br> </b>"
    });

    var cred_des1=new Ext.form.Label({
         width :250,
         height:20,
        //html:"<b>Actions</b>"
        html:"Credential software resent host.</br> </br> "
    });
    var vCenter_host=new Ext.form.TextField({
        fieldLabel: _('vCenter主机'),
        name: 'vCenter_host',
//        value: "192.168.0.145",
        id: 'vCenter_host',
        width: 150,
        allowBlank:false
    });
    var port=new Ext.form.TextField({
        fieldLabel: _('端口'),
        name: 'port',
        value: 22,
        id: 'port',
        width: 150,
        allowBlank:false
   });

   var ssl_store = new Ext.data.SimpleStore({
    fields: ['id','ssl'],
    data : [['1','http'],['2','https']]
   });


    var ssl=new Ext.form.ComboBox({
        fieldLabel: _('ssl '),
        triggerAction:'all',
        store: ssl_store,
        value : 2,
        displayField:'ssl',
        valueField:'id',
        width: 145,
        allowBlank: true,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'ssl',
        id:'ssl',
        mode:'local'
    });


    var username=new Ext.form.TextField({
        fieldLabel: _('用户名'),
        name: 'user_name',
        id: 'username',
        value:'root',
        width: 150,
        allowBlank:false
    });

    var password=new Ext.form.TextField({
        fieldLabel: _('密码'),
        name: 'pwd',
//        value:"vmware",
        id: 'pwd',
        width: 150,
        inputType : 'password'
    });

    var dummy_Panel1=new Ext.Panel({
        id:"dummy_Panel1",
        frame:false,
        width:'100%',
        height:3,
        autoScroll:false,
        border:false,
        bodyBorder:false
//      ,bodyStyle:'padding-left:8px'
    });

    var dummy_Panel2=new Ext.Panel({
        id:"dummy_Panel2",
        frame:false,
        width:'100%',
        height:3,
        autoScroll:false,
        border:false,
        bodyBorder:false
//        ,bodyStyle:'padding-left:8px'
    });

     var dummy_Panel3=new Ext.Panel({
        id:"dummy_Panel3",
        frame:false,
        width:'100%',
        height:10,
        autoScroll:false,
        border:false,
        bodyBorder:false
//       , bodyStyle:'padding-left:8px'
    });

    var dummy_Panel4=new Ext.Panel({
        id:"dummy_Panel4",
        frame:false,
        width:'100%',
        height:3,
        autoScroll:false,
        border:false,
        bodyBorder:false
//       ,bodyStyle:'padding-left:8px'
    });

    var dummy_Panel5=new Ext.Panel({
        id:"dummy_Panel5",
        frame:false,
        width:'30%',
        height:30,
        autoScroll:false,
        border:false,
        bodyBorder:false
//      ,bodyStyle:'padding-left:8px'
    });

     var connection=new Ext.Panel({
        id:"connection",
        layout:"column",
        frame:false,
        width:'90%',
        autoScroll:false,
        border:false,
        bodyBorder:false,
        autoHeight:true,
//        bodyStyle:'padding-left:8px',dummy_space11,
        items:[prior_des1,prior_header,vCenterHost_label,dummy_space5,vCenter_host,dummy_Panel1,dummy_Panel2,ssl_label,dummy_space8,ssl]
    });

    var credential=new Ext.Panel({
        id:"credential",
        layout:"column",
        frame:false,
        width:'90%',
        autoScroll:false,
        border:false,
        bodyBorder:false,
        autoHeight:true,
//        bodyStyle:'padding-left:8px',,dummy_space12
        items:[cred_header,username_label,dummy_space9,username,dummy_Panel4,password_label,dummy_space10,password]
    });
    testlable_success.hide()
    testlable_failure.hide()
    var test=new Ext.Button({
        name: 'test',
        id: 'test',
        text:_('连接'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                testlable_success.hide()
                testlable_failure.hide()
                var url = "/vcenter/test_vcenter_connection?"
                Ext.MessageBox.show({
                                    title:_('请稍候...'),
                                    msg: _('请稍候...'),
                                    width:200,
                                    wait:true,
                                    waitConfig: {
                                        interval:200
                                        }
                                    });
                var ajaxReq=ajaxRequest(url,0,"POST",true);
                ajaxReq.request({
                     params: {
                                 hostname:vCenter_host.getValue(),
                                 username:username.getValue(),
                                 password:password.getValue(),
                                },
                    success: function(xhr){
                                    var response=Ext.util.JSON.decode(xhr.responseText);
                                    if(response.success){
                                        connect_status=true
                                        Ext.MessageBox.hide()
                                        testlable_failure.hide()
                                        testlable_success.show();
                                            Ext.MessageBox.alert( _("状态") , "连接成功.");
                                         }
                                     else {
                                         connect_status=false;
                                         testlable_success.hide()
                                         testlable_failure.show()
                                        Ext.MessageBox.alert( _("Failure") , response.msg);
                                    }},
                    failure: function(xhr){
                        connect_status=false;
                        testlable_success.hide()
                        testlable_failure.show()
                        Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                    }
              });
            }
        }
    });

     var test_panel=new Ext.Panel({
        id:"test_panel",
        frame:false,
//        layout:"column",
        width:'30%',
        autoScroll:false,
        border:false,
        bodyBorder:false,
        autoHeight:true,
//        bodyStyle:'padding-left:8px',
        items:[dummy_space6,test]
    });
     
    var lable_panel=new Ext.Panel({
        id:"lable_panel",
        frame:false,
//        layout:"column",
        width:'50%',
        autoScroll:false,
        border:false,
        bodyBorder:false,
        autoHeight:true,
//        bodyStyle:'padding-left:8px',
        items:[dummy_space_lable,testlable_failure,testlable_success]
    });
    var main_panel=new Ext.Panel({
        id:"main_panel",
        frame:false,
        layout:"column",
        width:'100%',
        autoScroll:false,
        border:false,
        bodyBorder:false,
        autoHeight:true,
//        bodyStyle:'padding-left:8px',
        items:[test_panel,lable_panel]
    });



    var simple = new Ext.Panel({
//        labelWidth:120,
        frame:true,
        border:0,
        bodyStyle:'padding:0px 0px 0px 0px',
        width:340,
        height:274,
        labelSeparator: ' ',
//        items:[prior_des1,vCenter_host,port,ssl,prior_des,username,password],
        items:[connection,dummy_Panel3,credential,main_panel],
        bbar:[{xtype: 'tbfill'}, new Ext.Button({
                name: 'ok',
                id: 'ok',
                text:_('确定'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon whitebackground',
                listeners: {
                    click: function(btn) {


                        if (username.isValid() && vCenter_host.isValid && port.isValid && ssl.isValid) {
                             if(connect_status==false){
                                    Ext.MessageBox.alert(_("错误"),"请测试连接");
                                    return
                                }

                            if (action == 'ADD'){

                                var url='/vcenter/add_vCenter?'
                            }
                            if (action == 'EDIT'){
                                var url='/vcenter/edit_vCenter?id='+vCenter_grid_record.get("id")
                             }

//                        var url='/network/create_public_ip_pool?pool_infos='+vCenter_info_json


                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({

                             params: {

                                 host:vCenter_host.getValue(),
                                 port:port.getValue(),
                                 ssl:ssl.getRawValue(),
                                 username:username.getValue(),
                                 password:password.getValue()

                             },
                            success: function(xhr){
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){

//                                  var result=response.rows;

                                     var vCenter_rec = Ext.data.Record.create([
                                                        {
                                                            name: 'id',
                                                            type: 'string'
                                                        },
                                                        {
                                                            name: 'host',
                                                            type: 'string'
                                                        },
                                                        {
                                                            name: 'port',
                                                            type: 'string'
                                                        },
                                                        {
                                                            name: 'protocol',
                                                            type: 'string'
                                                        },
                                                        {
                                                            name: 'username',
                                                            type: 'string'
                                                        },
                                                        {
                                                            name: 'password',
                                                            type: 'string'
                                                        }

                                                ]);
                                    if (action == 'ADD'){
                                           var vCenter_entry=new vCenter_rec({
                                                id   : response.id,
                                                host : response.host,
                                                port : response.port,
                                                protocol : response.ssl,
                                                username :response.username,
                                                password :response.password

                                            });

                                            vCenter_grid.getStore().insert(0, vCenter_entry);
                                     }
                                        if (action == 'EDIT'){
                                            record.set('id' , response.id);
                                            record.set('host' , response.host);
                                            record.set('port' , response.port);
                                            record.set('protocol' , response.ssl);
                                            record.set('username' , response.username);
                                            record.set('password' , response.password);

                                        }

                                 w.close();
                                }
                                else {
                                    Ext.MessageBox.alert(_("Failure") ,response.msg);
                                }
                            },
                            failure: function(xhr){
                                Ext.MessageBox.alert( _("Failure"), xhr.statusText);
                            }
                        })
                    }else{
                        Ext.MessageBox.alert(_('错误'), _('您输入的信息不完整，请重新检查输入信息.'));
                    }
                   }
                }
            }),
            '-',
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('取消'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {w.close();
                    }
                }
            })]
    });

 if (action == 'EDIT'){

   vCenter_host.disabled=true;
   vCenter_host.setValue(record.get("host"));
   port.setValue(record.get("port"));
   ssl.setValue(record.get("protocol"));
   username.setValue(record.get("username"));

 }

    return simple;
}
function render_select_checkbox(value,params,record){
    var id = Ext.id();
    var disabled = false;
    var used_by = record.get("used_by");
    if(used_by!=null && used_by!=''){
        disabled = true;
    }
    (function(){
        var cb = new Ext.form.Checkbox({
            renderTo: id,
            width:100,
            height:16,
            disabled:disabled,
            checked:value,
            value:false,
            listeners : {
                check:function(field,checked){
                    record.set("is_selected", checked);
                }
            }
        });
    }).defer(5);
    return '<span id="' + id + '"></span>';
}
function imported_nodes(selected_nodes){

    var selected_nodes_list=[];
    var selected_dcs = new Array();
    //var nodes = selected_nodes;

    for (var i=0; i < selected_nodes.length; i++) {

        if (selected_nodes[i].attributes.type != "HostSystem"){
            continue;
        }
            var selected_node = selected_nodes[i];
            var parent=selected_node.parentNode;
            var hosts=[];            
            var dc = get_datacenter(selected_node);
            if (selected_dcs.indexOf(dc['moid']) >=0 ){
                continue;
            }
            selected_dcs.push(dc['moid']);
            parent.eachChild(function(node) {
                if(selected_nodes.indexOf(node) != -1){
                   var host_dict = {};
                   host_dict["name"] = node.attributes.name;
                   host_dict["type"] = node.attributes.type;
                   host_dict["moid"] = node.attributes.moid;
                   host_dict["actual_name"] = node.attributes.actual_name;
                   hosts.push(host_dict);
                }
            });

            var parent_dict={};
            var item = {};
            parent_dict['name']=parent.attributes.name;
            parent_dict['type']=parent.attributes.type;
            parent_dict['moid']=parent.attributes.moid;
            parent_dict["actual_name"] = parent.attributes.actual_name;
            item['hosts']=hosts;
            item['parent']=parent_dict;
            item['dc']=dc;
            selected_nodes_list.push(item);


    }

    return selected_nodes_list;
}

function get_datacenter(node){
    var p = node.parentNode;
    while(true){
        if (p == undefined){
            return null
        }
        if(p.attributes.type == "Datacenter"){
            var res = {}
            res["name"] = p.attributes.name;
            res["type"] = p.attributes.type;
            res["moid"] = p.attributes.moid;
            res["actual_name"] = p.attributes.actual_name;
            return res
        }
        p = p.parentNode
    }
}




function vCenter_import(w, vCenter_grid, node){
    var import_header_text = "请选择通过Stackone来管理的集群、主机文件夹和主机.";
    var import_lbl=new Ext.form.Label({
        html:'<div style="" class="labelheading">'+ _(import_header_text) +'</div><br/>'
    });

   var vCenter_grid_record = vCenter_grid.getSelectionModel().getSelected()
    var check =[];
    var westPanel=new Ext.Panel({
        bodyStyle:'padding:5px 5px 5px 5px',
        region:'west',
        width:660,
        height:450,
//        autoScroll:true,
        split:true,
        layout:"fit",
        
//        items:[],
//        defaults: {
//            autoScroll:true
//        },

        minSize: 50,
        maxSize: 300,
        border:false,
        id:'westPanel',
        cls:'westPanel',
        bbar:[{xtype: 'tbfill'}, new Ext.Button({

                name: 'ok',
                id: 'ok',
                text:_('确定'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon whitebackground',
                listeners: {
                    click: function(btn) {

                        Ext.MessageBox.show({
                            title:_('请稍候...'),
                            msg: _('请稍候...'),
                            width:300,
                            wait:true,
                            waitConfig: {
                                interval:200
                            }
                        });

                        var checked_nodes = vcenter_columntree.getChecked();
                        if (checked_nodes.length == 0){
                            Ext.MessageBox.alert(_("错误"),_("请选择一个主机"));
                            return ;
                        }
                        var node_details = imported_nodes(checked_nodes);
                        var context = {};
                        context["selected_objects"] = node_details;
                        var deco_context = Ext.util.JSON.encode(context);
                        var url = "/vcenter/import_managed_objects_from_vcenter?vcenter_id=" + vCenter_grid_record.get("id") + "&context=" + deco_context
                        var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {//alert(xhr.responseText);

                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){

                                    w.close();
                                    Ext.MessageBox.alert( _("信息") , "导入vCenter任务已经提交");

                                    }else{
                                    Ext.MessageBox.alert(_("Failure"),response.msg);
                                }
                            },
                            failure: function(xhr){
                                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                            }
                        });

                    }

                }
        }),
            '-',
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('取消'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {w.close();
                    }
                }
            })]
    });
    var outerPanel = new Ext.Panel({
        //renderTo:'content',
//        width:myWidth-5,
        //height:myHeight-5,
        border:false,
        width:"100%",
        height:"100%",
        id:'outerPanel',
        items: [ ]
        ,monitorResize:true
        ,listeners:{
            resize:function(){


            }
        }
    });

  var vcenter_columntree = new Ext.tree.ColumnTree({
        width: 655,
        height: 420,
        rootVisible:false,
        autoScroll:true,
        title:'&nbsp;',
        renderTo: Ext.getBody(),

        columns:[
	{
//            xtype: 'vcenter_columntree',
            header:'名称',
            width:295,
            dataIndex:'name'
        }
         ,{
//            xtype: 'treecolumn',
            header:'类型',
            width:155,
            dataIndex:'xtype'
            
        }
        ,{
//            xtype: 'treecolumn',
            header:'CPU',
            width:55,
            css : "text-align:right;",
            dataIndex:'cpu'
        }
        ,{
//            xtype: 'treecolumn',
            header:'内存',
            width:55,
            
                            
            dataIndex:'memory'
        }
        ,{
//            xtype: 'treecolumn',
            header:'虚拟机',
            width:90,
            align: 'right',
            dataIndex:'vms'
        }
 ],

        loader: new Ext.tree.TreeLoader({
            dataUrl:"/vcenter/get_managed_objects_from_vcenter?vcenter_id="+vCenter_grid_record.get("id"),
            requestMethod:'GET',
            uiProviders:{
                'col': Cvt.CustColumnNodeUI
            },listeners: {
                'load' :  function(store,records,options) {
                    Ext.MessageBox.hide();
                }}

        }),

        root: new Ext.tree.AsyncTreeNode({
            text:'Tasks'
        }),
        listeners: {
            beforeappend:function( tree,  parent, node ){
              if(node.attributes.type=="Datacenter"){
                  node.attributes.icon='icons/vmw-datacenter.png'
                  
              }else if(node.attributes.type=="ClusterComputeResource"){
                  node.attributes.icon='icons/vmw-cluster-compute-resource.png'
              }else if(node.attributes.type=="HostSystem"){
                  node.attributes.icon='icons/vmw-host-system.png'
              }else if(node.attributes.type=="Folder"){
                  node.attributes.icon='icons/vmw-folder.png'
              }

            if(node.attributes.type != "Datacenter"){
                node.attributes.showcheckbox = true;
                if(node.attributes.selected == true){
                    
                     
                    node.attributes.checked = true;
                   node.attributes.enablecheckbox = false;
                    

//                    childnode.getUI().checkbox.disabled = true
                }else{
                    node.attributes.checked = false;
                }
            }

        },
        append:function( tree, parent,node, index ){
            parent.expand(true);

        } ,checkchange : function(node,checked){
            if (node.manualCheck){
                return;
            }
            node.eachChild(function (node) {
                node.cascade(function (node) {
                 if(!node.attributes.selected){
                    if (node.ui.rendered) {
                        node.ui.toggleCheck(checked);
                    } else {
                        node.attributes.checked = checked;
                    }
                 }
               });
            });
            var parent=node.parentNode;
//
            if(checked && !parent.attributes.checked){
                ////                alert(parent.attributes.checked+"--"+parent.attributes.name)
                 parent.manualCheck = true;
                 if (parent.ui.rendered) {
                     parent.ui.toggleCheck(checked);
                 } else {
                     parent.attributes.checked = checked;
                 }
                 parent.manualCheck = false;
             }
        
             var ch=vcenter_columntree.getChecked(null,parent)
             if(parent.attributes.checked && ch.length ==1){
                 parent.ui.toggleCheck(false);
             }


     }


     }

    });
   var te=new Ext.tree.TreeEditor(vcenter_columntree);
   te.on('beforestartedit', function(ed, boundEl, value) {

       var find=ed.editNode.findChild( 'type','HostSystem');
       var attribute_type = ed.editNode.attributes.type
       if(attribute_type!="Datacenter" && (attribute_type==="HostSystem" || find==null)){
           cancelEdit( true );
       }

    });
    te.on('complete', function(ed, value, startValue) {
//        ed.editNode.setText(value)
          ed.editNode.attributes.name=value;

    });
    westPanel.add(import_lbl);
    westPanel.add(vcenter_columntree);
    return westPanel;
}


