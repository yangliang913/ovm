/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function Create_Account(grid,mode,win,vdc_id){


       var vdcaccount_treePanel= new Ext.tree.TreePanel({
        region:'west',
        width:180,
        rootVisible:false,
        border: false,
        lines : false,
        id:'vdc_treePanel',
        cls:'leftnav_treePanel',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        listeners: {
            click: function(item) {
                var id=item.id;
                process_panel(vdcaccount_card_panel,vdcaccount_treePanel,id.substr(4,id.length),"treepanel");
            }
        }
    });

    // root node of tree view
    var rootNode = new Ext.tree.TreeNode({
        text	: 'Root节点',
        draggable: false,
        id		: 'rootnode',
        listeners: {
            expand : function(btn) {
                vdcaccount_treePanel.getNodeById("node0").select();
            }
        }
    });
    var generalNode = new Ext.tree.TreeNode({
        text: _('常规'),
        draggable: false,
        id: "node0",
        icon:'icons/vm-general.png',
        nodeid: "general",
        leaf:false,
        allowDrop : false
       // cls:"labelcolor"
    });

    var regionNode = new Ext.tree.TreeNode({
        text: _('区域'),
        draggable: false,
        id: "node1",
        nodeid: "disk",
        icon:'icons/vm-storage.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

//    var Sevice_Custom = new Ext.tree.TreeNode({
//        text: _('Network'),
//        draggable: false,
//        id: "node2",
//        nodeid: "network",
//        icon:'icons/vm-network.png',
//        leaf:false,
//        allowDrop : false
//        //cls:"labelcolor"
//    });

    var serviceNode = new Ext.tree.TreeNode({
        text: _('实例类型'),
        draggable: false,
        id: "node2",
        icon:'icons/vm-boot-param.png',
        nodeid: "bootparams",
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
    var quotaNode = new Ext.tree.TreeNode({
        text: _('配额'),
        draggable: false,
        id: "node3",
        icon:'icons/vm-storage.png',
        nodeid: "quota",
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });
     var treeheading=new Ext.form.Label({
        html:'<br/><center><font size="2"></font></center><br/>'
    });

    var side_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        width:180,
        height:437,
        id:'side_panel',
        cls:'westPanel',
        items:[treeheading,vdcaccount_treePanel]

    // card panel for all panels
    });


     rootNode.appendChild(generalNode);
     rootNode.appendChild(regionNode);
     rootNode.appendChild(serviceNode);
     rootNode.appendChild(quotaNode);

    vdcaccount_treePanel.setRootNode(rootNode);


    var button_prev=new Ext.Button({
        id: 'move-prev',
        //text: _('Prev'),
        disabled: true,
        icon:'icons/2left.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
//                closeWindow();
                process_panel(vdcaccount_card_panel,vdcaccount_treePanel,-1);
//                cloud_card_panel.activeItem =0;
            }
        }
    });
    var button_next=new Ext.Button({
        id: 'move-next',
        //text: _('Next'),
        icon:'icons/2right.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
//                closeWindow();
                process_panel(vdcaccount_card_panel,vdcaccount_treePanel,1);
//                cloud_card_panel.activeItem =0
            }
        }
    });

    var url =""


    var acc_rec = Ext.data.Record.create([
        {
            name: 'name',
            type: 'string'
        },
        {
            name: 'cloud_provider',
            type: 'string'
        },
        {
            name: 'account_details'
        }
    ]);



    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                    
//                     param_obj_str+="username:'"+Ext.getCmp("username").getValue()+"',";
                    var param_obj_str="{";
//                        param_obj_str+="\"name\":\""+Ext.getCmp("acc_name").getValue()+"\",";
//                        param_obj_str+="\"desc\":\""+Ext.getCmp("acc_desc").getValue()+"\",";
//                        param_obj_str+="\"provider_id\":\""+Ext.getCmp("cloud_provider").getValue()+"\",";
//                        param_obj_str+="\"accesskey\":\""+Ext.getCmp("accesskey").getValue()+"\",";
//                        param_obj_str+="\"secret_access_key\":\""+Ext.getCmp("accesssecretkey").getValue()+"\"";
//                        param_obj_str+="}";

//                    param_obj_str+="";

                    //                The adding to the main grid and the saving part.
                        var finitems=new Object();
                        var regsel=Ext.getCmp("regacc_grid").getSelectionModel().getSelections();
                        
                        if(regsel.length<1){
                            Ext.MessageBox.alert(_("错误"),"请选择区域");
                            return;
                        }
                        var frecord="";
                        var rname="";
                        var rid="";
                        var rend="";
                   
                    
                        for(var i=0;i<regsel.length;i++)
                        {
                            frecord=Ext.getCmp("regacc_grid").getStore().getAt(i);
                            rname=regsel[i].get('region');
                            rid=regsel[i].get('id');
                            rend=regsel[i].get('end_point');
                            if(!regsel[i].get('zone_name')){
                                Ext.MessageBox.alert(_("错误"),"请选择zones");
                                return;
                            }
                            else{
                                var zone_name=regsel[i].get('zone_name');
                                
                                var zn=[];
                                zn=zone_name.split(",");
                                var zonelist=[];
                                for(var j=0;j<zn.length;j++){
                                    var zlist=regsel[i].get('zone_list');
                                    for(var k=0;k<zlist.length;k++){
                                        if(zn[j]==zlist[k].name){
                                            zonelist.push(zlist[k]);
                                        }
                                    }
                                }
                            }
                            if(!regsel[i].get('temp_id')){
                                Ext.MessageBox.alert(_("错误"),"请选择模板");
                                return;
                            }
                            else{
                                var temp_id=regsel[i].get('temp_id');
                                var tid=[];
                                tid=temp_id.split(",");
                                var templist=[];
                                for(var j=0;j<tid.length;j++){
                                    var tlist=regsel[i].get('temp_list');
                                    for(var k=0;k<tlist.length;k++){
                                        if(tid[j]==tlist[k].id){
                                            templist.push(tlist[k]);
                                        }
                                    }
                                }
                            }

                            var items=new Object();
                            items['region_id']=rid;
                            items['templates']=templist;
                            items['zones']=zonelist;                         
                            items['region']=rname;
                            items['end_point']=rend;
                            finitems[rname]=items;

                        }
                        var serlist=new Array();
                        var sselections=Ext.getCmp("seroff_grid").getSelectionModel().getSelections()
                        if(sselections.length>0){
                            for(var i=0;i<sselections.length;i++){
                                frecord=Ext.getCmp("seroff_grid").getStore().getAt(i);
                                var serdic=new Object();
                                serdic['name']=sselections[i].get('name');
                                serdic['description']=sselections[i].get('description');
                                serdic['platform']=sselections[i].get('platform');
                                serdic['cpu']=sselections[i].get('cpu');
                                serdic['memory']=sselections[i].get('memory');
                                serdic['storage']=sselections[i].get('storage');
                                serdic['cname']=sselections[i].get('cname');
                                serdic['cid']=sselections[i].get('cid');
                                serdic['service_offering_id']=sselections[i].get('id');
                                serlist.push(serdic);
                            }
                        }

                         var quota_store=Ext.getCmp("quota_grid").getStore();
                         for(var e=0;e<quota_store.getCount();e++){
                             var q_rec=quota_store.getAt(e);
                             if (parseInt(q_rec.get("limit"))<parseInt(q_rec.get("used"))){
                                 Ext.MessageBox.alert( _("失败") ,_("Quota's ")+ q_rec.get("type")+_(" limit cannot be less than ")+_(q_rec.get("used")));
                                 return;
                             }
                         }

                         var quota_deta="[";
                         for(var d=0;d<quota_store.getCount();d++){
                             var q_rec=quota_store.getAt(d);
                             var limit = null;
                             quota_deta+="{category:'"+q_rec.get("category")+"',";
                             quota_deta+="type:'"+q_rec.get("type")+"',";
                             if((Ext.util.Format.lowercase(q_rec.get("limit"))== 'unlimited' || Ext.util.Format.trim(q_rec.get("limit")) == '')
                            		 && typeof(q_rec.get("limit")== 'string')){
                            	 limit = -1
                             }
                             else{
                            	 limit = q_rec.get("limit")
                             }
                             quota_deta+="limit: "+limit+",";
                             quota_deta+="used: "+q_rec.get("used")+"}";
                             
                             if (d!=quota_store.getCount()-1)
                                quota_deta+=",";
                         }
                         quota_deta+="]";
                         var quota_details=eval(quota_deta);

                         var jsondata= Ext.util.JSON.encode({
                            "Regions":finitems,
                            "ServiceOfferings":serlist,
                            "quota_details":quota_details
                        });

                        if(mode=="EDIT"){
                            grid.getStore().remove(grid.getSelectionModel().getSelected());
                        }
                        if (!Ext.getCmp("cloud_provider").getRawValue() && !Ext.getCmp("account_name").getRawValue()){
                            Ext.MessageBox.alert( _("警告") , "请验证您选择的 "+ stackone.constants.IAAS +" 和账户名称");
                            return
                        }

                        else{
                            var r=new acc_rec({
                            name:Ext.getCmp("account_name").getValue(),
//                            cloud_provider:Ext.getCmp("cloud_provider").getValue()
//                                account_details_str: param_det,
//                            account_details:param_obj_str
                            name:Ext.getCmp("account_name").getStore().getAt(0).get('name'),
                            cloud_provider:Ext.getCmp("cloud_provider").getRawValue(),
                            jsondata:jsondata


                        });
                        grid.getStore().insert(0, r);
                        }


                    win.close();
                }

        }
    });



    var button_cancel=new Ext.Button({
       name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                 win.close();
            }
        }
     });


    var vdcaccount_card_panel=new Ext.Panel({
        width:448,
        height:425,
        layout:"card",
        id:"vdc_card_panel",
//        activeItem:0,
        cls: 'whitebackground',
        border:false,
        bbar:[
        {
            xtype: 'tbfill'
        },button_prev,button_next,button_ok,button_cancel]
//        ,items:[account_panel]
    //
    });

//    rootNode.appendChild(Account_Node);
//    rootNode.appendChild(Quota_node);
//    rootNode.appendChild(Sevice_Custom);

    var general_details_panel=create_account_panel(grid,mode,vdc_id);
    var region_details_panel=create_accountregion_panel(mode);
    var service_details_panel=create_instancetype_foraccount_panel();
    var quota_details_panel=create_quota_panel(grid,mode,vdc_id);
    
//    var treeheading=new Ext.form.Label({
//        html:'<br/><br/>'
//    });
//
//    var labeltreehead=new Ext.form.Label({
//        html:'<div class="toolbar_hdg">'+_("Account Management")+'</div>',
//        id:'label_vm'
//    });
//
//
//    var side_panel = new Ext.Panel({
//        bodyStyle:'padding:0px 0px 0px 0px',
//        width:150,
//        height:508,
//        id:'side_panel',
//        cls:'westPanel',
////        tbar:[labeltreehead,{
////            xtype: 'tbfill'
////        }],
//        items:[vdcaccount_treePanel]
//
//    });

    var right_panel=new Ext.Panel({
        id:"right_panel",
        width:455,
        height:437,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        bodyStyle:'padding:5px 5px 5px 5px'
//        items:[change_settings]
        ,listeners: {
            afterlayout: function() {//alert("afterlayout"+card_panel.activeItem);
                vdcaccount_card_panel.getLayout().setActiveItem("panel0");
            }
         }
    });

   var outerpanel=new Ext.FormPanel({
       height: 440,
       width: 830,
       autoEl: {},
       layout: 'column',
       items: [side_panel,right_panel]
   });
   

    vdcaccount_card_panel.add(general_details_panel);
    vdcaccount_card_panel.add(region_details_panel);
    vdcaccount_card_panel.add(service_details_panel);
    vdcaccount_card_panel.add(quota_details_panel);

    right_panel.add(vdcaccount_card_panel);
    return outerpanel;

}

function create_account_panel(grid,mode,vdc_id){

    var width=250;
    var labelWidth=80;

    var name_textbox=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'acc_name',
        id: 'acc_name',
        labelWidth:labelWidth,
        allowBlank:false,
//        labelStyle: 'font-weight:bold;',
        width:width,
        labelSeparator:" ",
        listeners:{

        }
    });

    var desc_textbox=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'acc_desc',
        id: 'acc_desc',
        allowBlank:false,
        labelWidth:labelWidth,
//        labelStyle: 'font-weight:bold;',
        width:width,
        labelSeparator:" ",
        listeners:{

        }
    });

    var username_textbox=new Ext.form.TextField({
        fieldLabel: _('用户名'),
        name: 'username',
        id: 'username',
        allowBlank:false,
        labelWidth:labelWidth,
//        labelStyle: 'font-weight:bold;',
        width:width,
        labelSeparator:" ",
        listeners:{

        }
    });

//    var password_textbox=new Ext.form.TextField({
//        fieldLabel: _('User Name'),
//        name: 'username',
//        id: 'username',
//        allowBlank:false,
//        labelWidth:labelWidth,
////        labelStyle: 'font-weight:bold;',
//        width:width,
//        labelSeparator:" ",
//        listeners:{
//
//        }
//    });


    var accesskey_textbox=new Ext.form.TextField({
        fieldLabel: _('Access Key'),
        name: 'accesskey',
        id: 'accesskey',
        allowBlank:false,
        labelWidth:labelWidth,
//        labelStyle: 'font-weight:bold;',
        width:width,
        labelSeparator:" ",
        listeners:{

        }
    });


    var accesssecretkey_textbox=new Ext.form.TextField({
        fieldLabel: _('Access Secret Key'),
        name: 'accesssecretkey',
        id: 'accesssecretkey',
        inputType:'password',
        allowBlank:false,
        labelWidth:labelWidth,
//        labelStyle: 'font-weight:bold;',
        width:width,
        labelSeparator:" ",
        listeners:{

        }
    });

    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:80px"/>')
    });

    var newdummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:80px"/>')
    });


//    var servicetype_selectbtn=new Ext.Button({
//        tooltip:'Select Service',
//        tooltipType : "title",
//        icon:'icons/accept.png',
//        id: 'service_select',
//        height:40,
//        width:50,
//        cls:'x-btn-icon',
//        listeners: {
//            click: function(btn) {
//                 showWindow(_("Select Servicetype"),350,130,Select_servicetype());
//            }
//        }
//    });
//
//
//    var getallregions_store=new Ext.data.JsonStore({
//        url: "/cloud/get_allregions",
//        root: 'info',
//        fields: ['value'],
//        successProperty:'success',
//        listeners:{
//            loadexception:function(obj,opts,res,e){
//                var store_response=Ext.util.JSON.decode(res.responseText);
//                Ext.MessageBox.alert(_("Error"),store_response.msg);
//            }
//        }
//    });
//    getallregions_store.load();
    

    var cloudprovider_store =new Ext.data.JsonStore({
        url: "/cloud/get_cloud_providers",
        root: 'info',
        id:"cloudprovider_store",
        fields: ['name','value'],
        successProperty:'success',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        listeners:{
            load:function(obj,opts,res,e){
                if (mode=="EDIT"){

                     var cp_name=grid.getSelectionModel().getSelected().get("cloud_provider");
                     var record;
                     for(var j=0;j<cloudprovider_store.getCount(); j++){
                        if (cloudprovider_store.getAt(j).get('name') == cp_name){
                            record=cloudprovider_store.getAt(j);
                            break;
                        }
                    }

                  cloud_provider.setValue(record.get("value"));
                  cloud_provider.fireEvent('select',cloud_provider,record,0);
                }

            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    cloudprovider_store.load();

    var cloud_provider = new Ext.form.ComboBox({
        id: 'cloud_provider',
        fieldLabel: _(stackone.constants.IAAS),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择 "+stackone.constants.IAAS),
        store:cloudprovider_store,
        width:width,
        displayField:'name',
        editable:false,
        valueField:'value',
        labelWidth:labelWidth,
//        labelStyle: 'font-weight:bold;',
        typeAhead: true,
        minListWidth:50,
        labelSeparator:" ",
        mode:'local',
        forceSelection: true,
        selectOnFocus:true,
        listeners: {
                select: function(combo, record, index){
                     accountname_store.load({
                         params:{
                            cp_id:cloud_provider.getValue()
                         }
                    });
                }

        }
    })


    var accountname_store =new Ext.data.JsonStore({
        url: "/cloud/get_account_forcombo",
        root: 'info',
        fields: ['name','value'],
        successProperty:'success',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        listeners:{
            load:function(obj,opts,res,e){
                if (mode=="EDIT"){
                     var acc_name=grid.getSelectionModel().getSelected().get("name");
                     var record;
                     for(var j=0;j<accountname_store.getCount(); j++){
                        if (accountname_store.getAt(j).get('name') == acc_name){
                            record=accountname_store.getAt(j);
                            break;
                        }
                    }

                  account_name.setValue(record.get("value"));
                  account_name.fireEvent('select',account_name,record,0);

                }

            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    

    var account_name = new Ext.form.ComboBox({
        id: 'account_name',
        fieldLabel: _('账户名称'),
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择账户"),
        store:accountname_store,
        width:width,
        displayField:'name',
        editable:false,
        valueField:'value',
        labelWidth:labelWidth,
//        labelStyle: 'font-weight:bold;',
        typeAhead: true,
        minListWidth:50,
        labelSeparator:" ",
        mode:'local',
        forceSelection: true,
        selectOnFocus:true,
        listeners: {
                select: function(combo, record, index){

                    if (mode=="EDIT"){
                          Ext.getCmp("quota_grid").getStore().load(
                          {
                                params:{
                                    cp_id:Ext.getCmp("cloud_provider").getValue(),
                                    vdc_id:vdc_id,
                                    account_id:Ext.getCmp("account_name").getValue()

                                }

                            }
                          );
                         Ext.getCmp("regacc_grid").getStore().load(
                             {
                                params:{
                                    cp_id:Ext.getCmp("cloud_provider").getValue(),
                                    vdc_id:vdc_id,
                                    account_id:Ext.getCmp("account_name").getValue()

                                }

                             }
                         );
                          Ext.getCmp("seroff_grid").getStore().load({
                                 params:{
                                    cp_id:cloud_provider.getValue(),
                                    vdc_id:vdc_id,
                                    account_id:Ext.getCmp("account_name").getValue()
                                 }
                          });

                    }else{
                            Ext.getCmp("quota_grid").getStore().load({
                                params:{
                                    cp_id:Ext.getCmp("cloud_provider").getValue()
                                }
                            });

                             Ext.getCmp("regacc_grid").getStore().load({
                                 params:{
                                    cp_id:cloud_provider.getValue(),
                                    vdc_id:vdc_id,
                                    account_id:Ext.getCmp("account_name").getValue()
                                 }
                            });

                            Ext.getCmp("seroff_grid").getStore().load({
                                 params:{
                                    cp_id:cloud_provider.getValue()
                                 }
                            });
                    }

                }

        }
    })

    var label_region=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("区域")+'</div>',
        id:'label_vm'
    });
   
    var label_acc=new Ext.form.Label({
        html:'<div>'+_("选择"+stackone.constants.IAAS+" ,并指定帐户要使用的详细信息.")+'<br/></div><br/>'
    });

    var inform_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="150"><b>账户信息</b></div>'
     });

    var label_account=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("提供")+'</div>',
        id:'label_vm'
    });

     var account_panel=new Ext.Panel({
        height:275,
        id:"panel7",
        layout:"form",
        frame:false,
        width:'100%',
        cls: 'whitebackground',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        tbar:[label_account],
        items:[label_acc,cloud_provider,newdummy_space1,inform_label,dummy_space1,account_name
            ]
    });

    if (mode=="EDIT"){
        cloud_provider.setDisabled(true);
        account_name.setDisabled(true);
    }
    return account_panel;

}

function create_accountregion_panel(mode,cp_feature){
    
    var selmodel1=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });

    var tlabel_region=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("区域管理")+'<br/></div>'
    });

     var label_region=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("")+'<br/></div>'
    });

    var tlabel_regionnws=new Ext.form.Label({
        html:'<div>'+_("选择可用于虚拟数据中心的区域、可用性区和模板.")+'<br/></div>'
    });

    var refresh_button= new Ext.Button({
        id: 'refresh',
        text: _('刷新'),
        icon:'icons/refresh.png',
        cls:'x-btn-text-icon',
        listeners: {
        }
    });

    var add_button= new Ext.Button({
        id: 'add',
        text: _('新建'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn)
            {
                var w=new Ext.Window({
                        title :_('区域'),
                        width :350,
                        height:270,
                        modal : true,
                        resizable : false
                   });
                   var p = NewRegionPanel(w,accreg_grid);
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
               if(!accreg_grid.getSelectionModel().getSelected()){
                   Ext.MessageBox.alert(_("错误"),_("请从列表中选择一列."));
                   return;
                }//alert(reg_grid.getSelectionModel().getSelected().get('id'));alert(reg_grid.getSelectionModel().getSelections());
               while (accreg_grid.getSelectionModel().getSelected()){
                   accreg_grid.getStore().remove(accreg_grid.getSelectionModel().getSelected());
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

        }
    });

    var regionstore = new Ext.data.JsonStore({
        url: "/cloud/get_regions_forprovisionvdc",
        root: 'rows',
        fields: ['id','region','end_point','add','addt','zone_list','temp_list',
            'zone_name','temp_id','region_selected','cp_id','account_id','vm_ids'],
        successProperty:'success',
        listeners: {
            load:function(obj,opts,res,e){
                  var size=regionstore.getCount();
                  for (var i=0;i<size;i++){
                        if (regionstore.getAt(i).get("region_selected")){
                             accreg_grid.getSelectionModel().selectRow(i,true);
                        }
                  }
                
            }
        }

    });
    var hide=false;
    if(!is_feature_enabled(cp_feature,stackone.constants.CF_IMPORT_VM)){
        hide=true;
    }

    var accreg_grid = new Ext.grid.GridPanel({
        store: regionstore,
        enableHdMenu:false,
        selModel:selmodel1,
        id:'regacc_grid',
        columns: [
            {
               id       :'id',
                header   : '编辑',
                width    : 140,
                sortable : true,
               dataIndex: 'id',
               hidden : true
            },
            {
                header   : '区域',
//                width    : 120,
                width    : 95,
                sortable : true,
                dataIndex: 'region'
//                hidden : true
            },
            {
                header   : 'End Point',
//                width    : 265,
                width     : 190,
                sortable : true,
                hidden : true,
                dataIndex: 'end_point'
            },

            {
                header   : '可用区',
                width    : 75,
                sortable : false,
                //renderer : change,
                dataIndex: 'add'
                ,renderer:function(value,params){
                    params.attr='ext:qtip="添加区"' +
                        'style="background-image:url(icons/add.png) '+
                        '!important; background-position: center;'+
                        'background-repeat: no-repeat;cursor: pointer;"';
                }
            },
            {
                header   : '模板',
                width    : 70,
                sortable : false,
                //renderer : change,
                dataIndex: 'addt'
                ,renderer:function(value,params){
                    params.attr='ext:qtip="添加模板"' +
                        'style="background-image:url(icons/add.png) '+
                        '!important; background-position: center;'+
                        'background-repeat: no-repeat;cursor: pointer;"';
                }
            },
            {
                header   : '虚拟机',
                width    : 120,
                sortable : false,
                //renderer : change,
                hidden:hide,
                dataIndex: 'add'
                ,renderer:function(value,params){
                    params.attr='ext:qtip="添加虚拟机"' +
                        'style="background-image:url(icons/add.png) '+
                        '!important; background-position: center;'+
                        'background-repeat: no-repeat;cursor: pointer;"';
                }
            },
            {
                header : 'Zone_list',
                width  : 200,
                hidden : true,
                dataindex :'zone_list'
            },
            {
                header : 'Temp_list',
                width  : 200,
                hidden : true,
                dataindex :'temp_list'

            },
           {
                header : 'Zone_name',
                width  : 200,
                hidden : true,
                dataindex :'zone_name'
            },
            {
                header : 'Temp_id',
                width  : 200,
                hidden : true,
                dataindex :'temp_id'

            },
            selmodel1

        ],


        stripeRows: true,

        height: 300,
        width:500,
        tbar:[label_region,{
            xtype: 'tbfill'
        }]
        ,listeners: {
            cellclick: function(reg_grid, rowIndex, columnIndex, e) {
                if (columnIndex==3){

                    var rrecord = reg_grid.getStore().getAt(rowIndex);

                    var nw=new Ext.Window({
                        title :_('可用区'),
                        width :355,
                        height:400,
                        modal : true,
                        resizable : false
                    });

                    var np = AddRegionZones_forvdc(nw,rrecord.get('region'),rrecord.get('zone_name'),rrecord.get('zone_list'),rrecord);
                    nw.add(np);
                    nw.show();
                } else if(columnIndex==4) {
                    var trecord = reg_grid.getStore().getAt(rowIndex);
                    var tw=new Ext.Window({
                        title :_('模板'),
                        width :800,
                        height:400,
                        modal : true,
                        resizable : false
                    });

                    var tselections=reg_grid.getSelections();
                    var tp=AddTemplates_forvdc(tw,trecord.get('region'),trecord.get('temp_id'),trecord.get('temp_list'),trecord,mode);

                    tw.add(tp);
                    tw.show();
                } else if (columnIndex==5){
                    var wait_win = Ext.MessageBox.show({
                        title:_('请稍候...'),
                        msg: _('请稍候...'),
                        width:400,
                        wait:true,
                        waitConfig: {
                            interval:200
                        }
                    }).hide();
                    var vrecord = reg_grid.getStore().getAt(rowIndex);
                    var w=new Ext.Window({
                        title :_('虚拟机'),
                        width :800,
                        height:400,
                        modal : true,
                        resizable : false
                    });

                    w.add(showVMsForVDC(w,vrecord,mode, wait_win));
                    w.show();
                    wait_win.show({
                        title:_('请稍候...'),
                        msg: _('请稍候...'),
                        width:400,
                        wait:true,
                        waitConfig: {
                            interval:200
                        }
                    });
                } else {
                    return;
                }
            }
        }


    });

    var region_panel = new Ext.Panel({
        height:415,
        id:"region_panel",
        layout:"form",
        frame:false,
        width:495,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        buttonAlign : 'center',
        tbar:[tlabel_region],
        items:[tlabel_regionnws,accreg_grid]
    });

    var region_details_panel=new Ext.Panel({
         border:false,
        id:"panel8",
        layout:"form",
        width:495,
        height:420,
            frame:false,
        labelWidth:250,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[region_panel]
    });

   return region_details_panel;

}

function render_select_checkbox(value,params,record){
    var id = Ext.id();
    var disabled = false;
    var used_by = record.get("used_by");
    if(used_by!=null && used_by!=''){
        disabled = true;
        value=true;
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

function create_instancetype_foraccount_panel()
    {

    var selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });

    var tlabel_service=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("实例类型")+'<br/></div>'
    });

    var tlabel_servicenws=new Ext.form.Label({
        html:'<div>'+_("选择实例类型 ,应该是 "+stackone.constants.IAAS+"的一部分.")+'<br/></div>'
    });

    var refresh_button= new Ext.Button({
        id: 'refresh',
        text: _('刷新'),
        icon:'icons/refresh.png',
        cls:'x-btn-text-icon',
        listeners: {
        }
    });

    var add_button= new Ext.Button({
        id: 'add',
        text: _('新建'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
             click: function(btn)
            {
                var sw=new Ext.Window({
                        title :_('分类'),
                        width :520,
                        height:370,
                        modal : true,
                        resizable : false
                   });
                    var p = NewServicePanel(sw,ser_grid);
                   sw.add(p);
                    sw.show();
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
                if(!ser_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从列表选择一列."));
                    return;
                }
                while (ser_grid.getSelectionModel().getSelected()){
                    ser_grid.getStore().remove(ser_grid.getSelectionModel().getSelected());
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


        }
    });


     var ser_store = new Ext.data.JsonStore({
       url:"/cloud/get_instancetypes_forprovisionvdc",
        root: 'rows',
       fields: ['id','name','platform', 'cpu','memory','storage','cname','cid','instancetype_selected'],
        successProperty:'success',
        listeners:{
            load:function(obj,opts,res,e){
            (function(){
                    for(var k=0;k<ser_grid.getStore().getCount();k++){
                        if(ser_store.getAt(k).get('instancetype_selected'))
                            ser_grid.getSelectionModel().selectRow(k,true);
                    }
            }).defer(25);
        }

        }

    });

    var ser_grid = new Ext.grid.GridPanel({
        store: ser_store,
        enableHdMenu:false,
        selModel:selmodel,
        id:'seroff_grid',
        columns: [
            {
                id       :'Id',
                header   : '编号',
                width    : 100,
                sortable : true,
                hidden:true,
                dataIndex: 'id'
            },
            {
                id       :'Name',
                header   : '名称',
                width    : 70,
                sortable : true,
                dataIndex: 'name'
            },
            {
                header   : '平台',
                width    : 55,
                sortable : true,
                dataIndex: 'platform',
                align : 'right'

           },
            {
//                    <br/>(EC2 units)
                header   : 'CPU',
                width    : 40,
                sortable : true,
                dataIndex: 'cpu',
                align:'right'
            },
            {
                header   : '内存(MB)',
                width    : 80,
                sortable : true,
                dataIndex: 'memory',
                align : 'right'

            },
            {
                header   : '存储(GB)',
                width    : 80,
                sortable : true,
                dataIndex: 'storage',
                align : 'right'

            },
           {
                header   : '分类',
                width    : 90,
                sortable : true,
                dataIndex: 'cname'
            },
           {
                header   : '分类编号',
              width    : 100,
                sortable : true,
                dataIndex: 'cid',
                hidden:'true'
            },
            selmodel
            ],

        autoExpandColumn:2,
        stripeRows: true,
        frame:false,
        height: 290,
        width: 500,
        tbar:['',new Ext.form.Label({}),{
            xtype: 'tbfill'
             }]
     });

     var advance_option_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading"><br/></div>'
    });

    var notshown=true;
    var service_panel = new Ext.Panel({
        height:415,
        id:"service_panel",
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        //items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],
        tbar:[tlabel_service],
        items:[tlabel_servicenws,ser_grid,advance_option_label]

    });

    var service_details_panel=new Ext.Panel({
        border:false,
        id:"panel9",
        layout:"form",
        width:470,
        height:420,
        frame:false,
        labelWidth:220,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[service_panel],
        listeners:{
           show:function(p){
                if(ser_store.getCount()>0 && notshown){
                    ser_store.sort('cname','ASC');
                    notshown=false;
                }
            }
        }
     });

    return service_details_panel;
}

function showVMsForVDC(w,record,mode, wait_win){
    var reg_name = record.get("region");
    var reg_id = record.get("id");
    var cp_id = record.get("cp_id");
    var account_id = record.get("account_id");
    var vm_ids = record.get("vm_ids");
//    var tselmodel=new Ext.grid.CheckboxSelectionModel({
//        singleSelect:false
//    });

    var tlabel_tmpnws=new Ext.form.Label({
        html:'<div>'+_("在这些区域的可用虚拟机.")+'<br/></div>'
    });

    var tlabel_add_vm=new Ext.form.Label({
        html:'<div>'+_("区域 :"+reg_name)+'<br/></div><br/>'
    });

    var tbutton_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('确定'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var l = vm_store.getTotalCount();
                var trec="";
                for (var i=0; i < l;i++){
                    var r = vm_store.getAt(i);
                    if(r.get("is_selected")){
                        trec+=((trec=="")?"":",")+r.get('id');
                    }
                }
                record.set('vm_ids',trec);
                record.commit();
                w.close();
            }
        }
    });

    var tbutton_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                w.close();
            }
        }
    });

    var vm_search_by_name = new Ext.form.TextField({
        fieldLabel: _('搜索'),
        name: 'search',
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {
                 vm_grid.getStore().filter('name', field.getValue(), false, false);
            }
        }
    });

    var url = "/cloud/get_vms_for_provision_vdc?region_id="+reg_id+
        "&account_id="+account_id+"&cp_id="+cp_id+"&sel_vm_ids="+vm_ids;
    var vm_store = new Ext.data.JsonStore({
        url: url,
        root: 'rows',
        fields: ['id','instance_id','name','image_id','zone','instance_type', 'state', 'used_by','is_selected'],
        successProperty:'success',
        listeners: {
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            },
            load:function(obj,opts,res,e){
                wait_win.hide();
            }
        }
    });
    vm_store.load();

    var vm_grid = new Ext.grid.GridPanel({
        store: vm_store,
        id:'vdc_vm_grid',
        //selModel:tselmodel,
        autoExpandColumn:1,
        autoExpandMax:350,
        autoExpandMin:280,
        enableHdMenu:false,
        columns: [
        {
            header   : '编号',
            width    : 100,
            sortable : true,
            dataIndex: 'id',
            hidden:true
        },
        {
            header   : '名称',
            width    : 110,
            sortable : true,
            dataIndex: 'name'
        },
        {
            header   : '实例编号',
            width    : 80,
            sortable : true,
            dataIndex: 'instance_id'
        },
        {
            header   : '状态',
            width    : 65,
            dataIndex: 'state'
        },
        {
            header   : 'Zone',
            width    : 90,
            sortable : true,
            dataIndex: 'zone'
        },
        {
            header   : '实例类型',
            width    : 90,
            sortable : true,
            dataIndex: 'instance_type'
        },
        {
            header   : '所用',
            width    : 110,
            dataIndex: 'used_by'
        },
        {header:_("选择"),width: 55, sortable: true, dataIndex: 'is_selected', renderer:render_select_checkbox}
        ],
        stripeRows: true,
        height: 285,
        width: 775,
        tbar:[{
            xtype: 'tbfill'
        }, '搜索(按名称): ',vm_search_by_name]
    });

    var tmp_panel = new Ext.Panel({
        height:370,
        id:"add_region_vm_panel",
        layout:"form",
        frame:false,
        width:785,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        buttonAlign : 'center',
        bbar:[{
            xtype: 'tbfill'
        },tbutton_ok,tbutton_cancel],
        items:[tlabel_add_vm,tlabel_tmpnws,vm_grid]
    });

    var tmp_details_panel=new Ext.Panel({
        layout:"form",
        width:790,
        height:380,
        frame:false,
        labelWidth:220,
        cls: 'whitebackground',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[tmp_panel]
    });

    return tmp_details_panel;
}

function AddTemplates_forvdc(tw,rnme,temp_id,temp_list,trecord,mode){

    var tselmodel=new Ext.grid.CheckboxSelectionModel({
        singleSelect:false
    });

    var tlabel_tmpnws=new Ext.form.Label({
        html:'<div>'+_("在这些区域的可用模板.")+'<br/></div>'
    });

    var tlabel_addtemplate=new Ext.form.Label({
        html:'<div>'+_("区域 :"+rnme)+'<br/></div><br/>'
    });

    var tbutton_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
             click: function(btn) {
                var tmpselections=add_tmp_grid .getSelections();
                if(tmpselections.length==0)
                {
                    Ext.MessageBox.alert(_('错误'), _('请至少选择一列.'));
                    return;
                }
             var trec=""
        for (var i=0;i<=tmpselections.length-1;i++)
        {
              trec+=((i==0)?"":",")+tmpselections[i].get('id');
        }
             for(var m=temp_list.length-1;m>=0;m--){
                 if(temp_list[m].state==false){
                     trec+=((m==0)?"":",")+temp_list[m].id;
                 }

        }
        trecord.set('temp_id',trec);
        trecord.commit();
       tw.close()

           }
        }
    });

   var tbutton_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                tw.close();
            }
        }
     });

    var refresh_button= new Ext.Button({
        id: 'refresh',
        text: _('刷新'),
        icon:'icons/refresh.png',
        cls:'x-btn-text-icon',
        listeners: {
        }
    });

    var temp_rec = Ext.data.Record.create([
        {
            name: 'name',
            type: 'string'
        },
        {
            name: 'description',
            type: 'string'
        },
        {
            name: 'root_device_name',
            type: 'string'
        },
        {
            name: 'root_device_type',
            type: 'string'
        },
        {
            name: 'owner_alias',
            type: 'string'
        },
        {
            name: 'kernel_id',
            type: 'string'
        },
        {
            name: 'ramdisk_id',
            type: 'string'
        },
       {
           name: 'platform',
           type: 'string'
       },
       {
            name: 'state',
            type: 'string'
        },
        {
            name: 'location',
            type: 'string'
        },
       {
           name: 'item',
           type: 'string'
        },
        {
            name: 'is_public',
            type: 'string'
        },
        {
            name: 'ownerId',
            type: 'string'
       },
        {
            name: 'type',
           type: 'string'
       },
        {
            name: 'id',
            type: 'string'
        },
        {
            name: 'architecture',
            type: 'string'
        },
        {
              name: 'state',
            type: 'string'
        }
    ]);


    var temp_store = new Ext.data.SimpleStore({
        fields: ['name','description','root_device_name','root_device_type','owner_alias',
            'kernel_id','ramdisk_id','platform','state','location','item','is_public','ownerId',
            'type','id','architecture','state', 'visibility']

     });


    var vdc_temp_search_by_name = new Ext.form.TextField({
                fieldLabel: _('搜索'),
                name: 'search',
                id: 'search',
                allowBlank:true,
                enableKeyEvents:true,
                listeners: {
                    keyup: function(field) {
                         add_tmp_grid.getStore().filter('name', field.getValue(), false, false);
                    }
                }

            })


    var vdc_select_template_type = new Ext.form.ComboBox({
        id: 'select_template',
        fieldLabel: _('选择模板'),
        triggerAction:'all',
        //emptyText :_("Select Template"),
        store:[['All','All'], ['DEFAULT_TEMPLATE', 'Shared Templates'], ['MY_TEMPLATE', 'Custom Templates']],
        width:140,
        listWidth:120,
        displayField:'name',
        valueField:'value',
//        minListWidth:0,
        labelSeparator:" ",
        mode:'local',
        forceSelection:true,
        listeners: {
                    select: function(combo, record, index){
//                        alert("----"+combo.getValue());
                            if(combo.getValue()=="All")
                            {
                                add_tmp_grid.getStore().loadData(main_array);
                            }else{
                                add_tmp_grid.getStore().filter('visibility', combo.getValue(), false, false);
                            }

                            ///mark selected templates//
                            (function(){
                                      mark_selected_templates();
                             }).defer(25);
        	    }
             }

    });

    vdc_select_template_type.setValue('All');


     var vdc_dummy_space_temp=new Ext.form.Label({
         html:_('&nbsp;<div style="width:25px"/>')
    });


    var add_tmp_grid = new Ext.grid.GridPanel({
        store: temp_store,
        id:'add_temp_grid',
        selModel:tselmodel,
        autoExpandColumn:1,
        autoExpandMax:400,
        autoExpandMin:280,
        enableHdMenu:false,
        columns: [
             {
                header   : '编号',
                width    : 230,
                sortable : true,
                dataIndex: 'id',
                hidden:true

            },
            {

                header   : '名称',
                width    : 270,
                sortable : true,
                dataIndex: 'name'
            },
            {
                header   : '说明',
                width    : 300,
                sortable : true,
                dataIndex: 'description',
                hidden:true

            },
            {
                header   : 'Root_Device_Name',
                width    : 230,
                sortable : true,
                dataIndex: 'root_device_name',
                hidden:true

            },
            {
                header   : 'Root_Device_Type',
                width    : 230,
                sortable : true,
                dataIndex: 'root_device_type',
                hidden:true

            },
            {
                header   : 'Owner_Alias',
                width    : 120,
                sortable : true,
                dataIndex: 'owner_alias',
                hidden:true

            },
            {
                header   : 'Kernel_id',
                width    : 230,
                sortable : true,
                dataIndex: 'kernel_id',
                hidden:true

            },
            {
                header   : 'Ramdisk_id',
                width    : 230,
                sortable : true,
                dataIndex: 'ramdisk_id',
                hidden:true

            },
            {
                header   : '平台',
                width    : 90,
                sortable : true,
                dataIndex: 'platform'

            },
            {
                header   : '资源',
                width    : 150,
                sortable : true,
                dataIndex: 'location'

            },
            {
                header   : 'Item',
                width    : 230,
                sortable : true,
                dataIndex: 'item',
                hidden:true

            },
            {
                header   : 'is_Public',
                width    : 230,
                sortable : true,
                dataIndex: 'is_public',
                hidden:true

            },
            {
                header   : 'ownerId',
                width    : 230,
                sortable : true,
                dataIndex: 'ownerId',
               hidden:true

           },
            {
                header   : '类型',
                width    : 230,
                sortable : true,
                dataIndex: 'type',
                hidden:true

            },
           {
               header   : '架构',
                width    : 85,
                sortable : true,
                dataIndex: 'architecture'
           },
           {
                header   : '状态',
               width    : 90,
               sortable : true,
               dataIndex: 'state',
                hidden :true
           },{
                header   : 'visibility',
               width    : 90,
               sortable : true,
               dataIndex: 'visibility',
                hidden :true
           },
            tselmodel
            ],

       stripeRows: true,
       height: 285,
       width: 775,
       tbar:[{xtype: 'tbfill'}, '搜索(按名称): ',vdc_temp_search_by_name, vdc_dummy_space_temp, vdc_select_template_type]
     });


    var mark_selected_templates = function mark_sel_templates(){
                 var tn=temp_id.split(",");
                 for(var j=0;j<tn.length;j++){
                    for(var k=0;k<add_tmp_grid.getStore().getCount();k++){
                        if(tn[j]==add_tmp_grid.getStore().getAt(k).get('id')){//mark all machine images as selected by default.
                            add_tmp_grid.getSelectionModel().selectRow(k,true);
                            break;
                        }
                    }
                 }
            }


    var main_array =  new Array();
    ///// anonymous function /////
     (function(){
        for(var i=temp_list.length-1;i>=0;i--){
            var ch_array = new Array();

            if(temp_list[i].state==true){ //state=True for machine images. show only machine images in grid.
             ch_array.push(temp_list[i].name);
             ch_array.push(temp_list[i].description);
             ch_array.push(temp_list[i].root_device_name);
             ch_array.push(temp_list[i].root_device_type);
             ch_array.push(temp_list[i].owner_alias);
             ch_array.push(temp_list[i].kernel_id);
             ch_array.push(temp_list[i].ramdisk_id);
             ch_array.push(temp_list[i].platform);
             ch_array.push(temp_list[i].state);
             ch_array.push(temp_list[i].location);
             ch_array.push(temp_list[i].item);
             ch_array.push(temp_list[i].is_public);
             ch_array.push(temp_list[i].ownerId);
             ch_array.push(temp_list[i].type);
             ch_array.push(temp_list[i].id);
             ch_array.push(temp_list[i].architecture);
             ch_array.push(temp_list[i].visibility);
             main_array.push(ch_array);
           }

        }

        temp_store.loadData(main_array);

        ///mark selected templates//
        (function(){
                mark_selected_templates();
        }).defer(25);

    }).defer(25);



      var tmp_panel = new Ext.Panel({
        height:370,
        id:"add_region_panel",
        layout:"form",
        frame:false,
        width:785,
        autoScroll:true,
        border:false,
        bodyBorder:false,
       bodyStyle:'padding:5px 5px 5px 5px',
        buttonAlign : 'center',
        //items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],
        bbar:[{
            xtype: 'tbfill'
             },tbutton_ok,tbutton_cancel],
        items:[tlabel_addtemplate,tlabel_tmpnws,add_tmp_grid]
    });

    var tmp_details_panel=new Ext.Panel({
        id:"atppanel1",
        layout:"form",
        width:790,
        //cls: 'whitebackground paneltopborder',
        height:380,
        frame:false,
        labelWidth:220,
        cls: 'whitebackground',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[tmp_panel]
    });


    return tmp_details_panel;

}
function AddRegionZones_forvdc(nw,rname,zone_name,zone_list,record){

    var selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });

    var type='EC2';
    var zlabel_addzone=new Ext.form.Label({
        html:'<div>'+_("区域 :"+rname)+'<br/></div><br/>'
    });


     var tlabel_regionnws=new Ext.form.Label({
        html:'<div>'+_("在这些区域的可用区.")+'<br/></div>'
    });



    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var selections=add_reg_grid.getSelections(); //Zone grid
                if(selections.length==0)
                {
                    Ext.MessageBox.alert(_('错误'), _('请选择一个区.'));
                    return;
                }
                else
                    {
              var zrec="";
        for (var i=0;i<=selections.length-1;i++){
            zrec+=((i==0)?"":",")+selections[i].get('name');
        }
        record.set('zone_name',zrec);
        record.commit();
        nw.close()
                    }
            }
        }
     });
     var button_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                nw.close()
            }
        }
     });

    var refresh_button= new Ext.Button({
        id: 'refresh',
        text: _('刷新'),
        icon:'icons/refresh.png',
        cls:'x-btn-text-icon',
        listeners: {
        }
    });

    var zone_store = new Ext.data.JsonStore({
        url: '/cloud_provider/get_all_lookup_zones?region_id='+"id"+'&provider_type='+type,
        root: 'rows',
        fields: ['id','name','details','state','region'],
        successProperty:'success',
        listeners:{
//            load:function()
//             {
//                 if(zoneid!=null){
//                     var zid=zoneid.split(",");
//                     for(var i=0;i<zid.length;i++){
//                         for(var j=0;j<add_reg_grid.getStore().getCount();j++){
//                             if(zid[i]==add_reg_grid.getStore().getAt(j).get('id')){
//                                 add_reg_grid.getSelectionModel().selectRow(j,true);
//                                 break;
//                             }
//                         }
//                     }
//                 }
//             }
        }
    });
//      zone_store.load();
    var zone_rec = Ext.data.Record.create([
        {
            name: 'id',
            type: 'string'
        },
        {
            name: 'name',
            type: 'string'
        },
        {
            name: 'details',
            type: 'string'
        },
        {
            name: 'state',
            type: 'string'
        },
        {
            name: 'region',
            type: 'string'
        }
    ]);


//     zone_store.load();
     var add_reg_grid = new Ext.grid.GridPanel({
        store: zone_store,
        selModel:selmodel,
        enableHdMenu:false,
        columns: [
            {
                header   : '编号',
                width    : 150,
               sortable : true,
                dataIndex: 'id',
                hidden   : true

            },
            {
                id       :'name',
                header   : '名称',
                width    : 150,
               sortable : true,
               dataIndex: 'name'
            },
            {
                header   : '详情',
                width    : 150,
                sortable : true,
                dataIndex: 'details',
                hidden   : true

            },
            {

                header   : '状态',
                width    : 150,
                sortable : true,
                dataIndex: 'state'
            },
            {
                header   : '区域',
                width    : 150,
                sortable : true,
               dataIndex: 'region',
                hidden   : true

            },

            selmodel
//            {
//                header   : 'End Point',
//                width    : 100,
//                sortable : true,
//                //renderer : change,
//                dataIndex: 'end_point'
//            }
//
            ],


        stripeRows: true,

        height: 280,
        width: 330,
        tbar:[{
            xtype: 'tbfill'
             }]
     });


    (function(){
        for(var i=zone_list.length-1;i>=0;i--){

            var new_entry=new zone_rec({
               id:i+"",
               name:zone_list[i].name,
               details:"kk",
               state:zone_list[i].state,
               region:zone_list[i].regionName
           });

           add_reg_grid.getStore().insert(0,new_entry);

        }
        (function(){
             var zn=zone_name.split(",");
             for(var j=0;j<zn.length;j++){
                for(var k=0;k<add_reg_grid.getStore().getCount();k++){
                   if(zn[j]==add_reg_grid.getStore().getAt(k).get('name')){
                        add_reg_grid.getSelectionModel().selectRow(k,true);
                        break;
                    }
                }
             }
        }).defer(25);
    }).defer(25);


      var region_panel = new Ext.Panel({
        height:370,
        id:"add_region_panel",
        layout:"form",
        frame:false,
        width:335,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        buttonAlign : 'center',
        //items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],
        bbar:[{
            xtype: 'tbfill'
             },button_ok,button_cancel],
        items:[zlabel_addzone,tlabel_regionnws,add_reg_grid]
    });

    var region_details_panel=new Ext.Panel({
        id:"arppanel1",
        layout:"form",
        width:340,
        //cls: 'whitebackground paneltopborder',
        height:395,
        frame:false,
        border:false,
        labelWidth:220,
        cls: 'whitebackground',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[region_panel]
    });


    return region_details_panel;



}

function create_quota_panel(grid,mode,vdc_id,data){
     var label_vdc=new Ext.form.Label({
         html:'<div>'+_("一个虚拟数据中心从多种 "+stackone.constants.IAAS+"使用资源. 请为每个"+stackone.constants.IAAS+"指定账户详情.")+'<br/></div><br/>'
     });

     var label_quota=new Ext.form.Label({
         html:'<div class="toolbar_hdg">'+_("配额")+'</div>',
         id:'label_vm'
     });

     var quota_grid=create_quota_grid();
     var quota_panel=new Ext.Panel({
         height:450,
         id:"panel10",
         layout:"form",
         frame:false,
         width:'100%',
         cls: 'whitebackground',
         autoScroll:true,
         border:false,
         bodyBorder:false,
//         bodyStyle:'padding:5px 5px 5px 5px',
         items:[quota_grid]
     });


     return quota_panel;
 }
 
 function mingUIMakeUP(value, meta, rec) {
    var dict = {'Virtual Machines':'虚拟机',
	            'Running':'可运行',
	            'Provisioned':'部署',
	            'Compute Resources':'计算资源',
	            'Memory (MB)':'内存(MB)',
	            'vCPUs':'vCPUs',
				'Storage':'存储',
				'Size (GB)':'存储容量(GB)',
				'Networking':'网络',
				'Public IPs':'公共IP',
				'Private Networks':'私有网络'
				
	}
	if (dict[rec.get('category').trim().replace(/&nbsp;/g, '')]) {
		return dict[rec.get('category').trim().replace(/&nbsp;/g, '')];
	} else {
	        return rec.get('category');
	}
	
}

function typeUIMakeUP(value, meta, rec) {
    var dict = {'Virtual Machines':'虚拟机',
	            'Running':'可运行',
	            'Provisioned':'部署',
	            'Compute Resources':'计算资源',
	            'Memory (MB)':'内存(MB)',
				'Instance Type':'实例类型',
	            'vCPUs':'vCPUs',
				'Storage':'存储',
				'Size (GB)':'存储容量(GB)',
				'Networking':'网络',
				'Public IPs':'公共IP',
				'Private Networks':'私有网络'
				
	} 
	if (dict[rec.get('type_unit').trim().replace(/&nbsp;/g, '')]) {
		return dict[rec.get('type_unit').trim().replace(/&nbsp;/g, '')];
	} else {
	        return rec.get('type_unit');
	}
	
}
 
 function eeUIMakeUP(value, meta, rec) {
    var dict = {'unlimited':'无限'
				
	} 
	if (dict[rec.get('limit')]) {
		return dict[rec.get('limit')];
	} else {
	        return rec.get('limit');
	}
	
}


 function create_quota_grid(is_editable){

      var json_record = Ext.data.Record.create([
         {name: 'category'},
         {name: 'type'},
         {name: 'type_unit'},
         {name: 'limit'},
         {name: 'used'},
         {name: 'unit'}
     ]);

     var json_reader = new Ext.data.JsonReader({
         totalProperty: "results",
         root: "quota_summary",
         successProperty:'success',
         id: "json_reader"
     },json_record);

     var quota_store = new Ext.data.GroupingStore({
         id:'quota_store',
         url: '/cloud/quota_summary',
         reader:json_reader,
         remoteSort :true,
         remoteGroup:true,
         groupField:'category',
         listeners:{
             loadexception:function(obj,opts,res,e){
                 var store_response=Ext.util.JSON.decode(res.responseText);
                 Ext.MessageBox.alert(_("Error"),store_response.msg);
             }
         }
     });

     var quota_columnModel = new Ext.grid.ColumnModel([
         {header: "", width: 100,hidden:true,  dataIndex: 'category',sortable: false,renderer:mingUIMakeUP},
         {header: "类型", width: 0,hidden:true ,dataIndex: 'type',sortable: false},
         {header: "类型", width: 250,  dataIndex: 'type_unit',sortable: false,renderer:typeUIMakeUP},
         {header: "限额", width:230 , dataIndex: 'limit',sortable: false,editor:(is_editable==false)?"":new Ext.form.NumberField(),renderer:eeUIMakeUP},
         {header: "已用", width: 0,hidden:true ,dataIndex: 'used',sortable: false},
         {header: "单元", width: 0,hidden:true ,dataIndex: 'unit',sortable: false}
     ]);

     var quota_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
     });

    var label_quota_summary=new Ext.form.Label({
         html:'<div class="toolbar_hdg">'+ _("配额") +'</div>',
         id:'label_vm'
     });
     var quota_grid = new Ext.grid.EditorGridPanel({
         store: quota_store,
         id: "quota_grid",
         stripeRows: true,

        view: new Ext.grid.GroupingView({
            forceFit:true,
            startCollapsed : false
            // custom grouping text template to display the number of items per group
//            groupTextTpl: '{text} ({[values.rs.length]} {[values.rs.length > 1 ? "Items" : "Item"]})'
        }),

         colModel:quota_columnModel,
         frame:false,
         border: false,
         selModel:quota_selmodel,
 //        autoExpandColumn:1,

         autoscroll:true,
         height:'100%',
         width:'100%',
         clicksToEdit:2,
         enableHdMenu:false,
         tbar:[label_quota_summary,
         {
            xtype: 'tbfill'
         }]
     });


     return quota_grid;


 }

