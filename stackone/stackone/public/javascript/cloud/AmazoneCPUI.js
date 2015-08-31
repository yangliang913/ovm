

function GetCloudProvider(node, mode, result, cp_type){
    var append_url = "";
    if(mode == "EDIT") {
        append_url = "cp_id="+node.attributes.id;
    } else {
        append_url = "cp_type="+cp_type;
    }
    var url = "/cloud/get_cp_feature_set?"+append_url;
    var ajaxReq=ajaxRequest(url,0,"POST",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var display_label=eval("stackone.constants.IAAS_NAMES."+cp_type);
                showWindow(_("添加"+display_label+" "+stackone.constants.IAAS),670,470,CloudProviderUI(node, mode, result, cp_type, response.info), null, false, false);
            }else{
                Ext.MessageBox.alert(_("失败"),_("无法加载数据."));
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}





var status=false;
var conn_status = false;

function CloudProviderUI(node, action, result, type, cp_feature)
{

    conn_status=false;

if(!is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT))
    {
        status=true;
        conn_status=true;
    }

    var treePanel= new Ext.tree.TreePanel({
        region:'west',
        width:180,
        rootVisible:false,
        border: false,
        lines : false,
        id:'treePanel',
        cls:'leftnav_treePanel',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        listeners: {
           beforeclick: function(item)
           {
               if(status==false){
                   if(action=='ADD'){                                                    
                       Ext.MessageBox.alert(_("错误"),"Please connect to the "+stackone.constants.IAAS+" to fetch initial data by providing details on the General tab");
                       return status;
                   }
                   if(action=='EDIT'){
//                       if((item.id.substr(4,item.id.length))==3||(item.id.substr(4,item.id.length))==0){
                            if(conn_status==true){
                               return conn_status;
                            }

                            else {
                                Ext.MessageBox.alert(_("错误"),"请连接到"+stackone.constants.IAAS);
                                return status;
                            }
//                       }
                      
//                      else return status;
                   }
                   
               }


           },
           click: function(item) {                                                                        
                var id=item.id;                                                                 
                process_card_panel(card_panel,treePanel,id.substr(4,id.length),"treepanel");

            }
        }
    });

    // root node of tree view
    var rootNode = new Ext.tree.TreeNode({
        text	: 'Root Node',
        draggable: false,
        id		: 'rootnode',
        listeners: {
            expand : function(btn) {
                treePanel.getNodeById("node0").select();
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
    
//    Service Offerings
    var serviceNode = new Ext.tree.TreeNode({
        text: _('实例类型'),
        draggable: false,
        id: "node2",
        icon:'icons/vm-boot-param.png',
        nodeid: "bootparams",
        leaf:false,
        allowDrop : false
    });

    var accountNode = new Ext.tree.TreeNode({
        text: _('账户'),
        draggable: false,
        id: "node3",
        nodeid: "disk",
        icon:'icons/vm-storage.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });


    var serverPoolNode = new Ext.tree.TreeNode({
        text: _('服务器池'),
        draggable: false,
        id: "node4",
        nodeid: "cms_cp_server_pool",
        icon:'icons/vm-storage.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

    var storageNode = new Ext.tree.TreeNode({
        text: _('存储'),
        draggable: false,
        id: "node5",
        nodeid: "cms_cp_storage",
        icon:'icons/vm-storage.png',
        leaf:false,
        allowDrop : false,
        listeners: {
            click: function(item) {
                var id=item.id;

                var server_pool_grid = server_pool_panel.items.get("cms_cp_server_pool_panel").items.get("cms_cp_server_pool_grid");
                var server_pool_store = server_pool_grid.getStore();
                var sp_selections = server_pool_grid.getSelections();
                var sp_ids = new Array();
                for(var j=0; j<sp_selections.length; j++){
                        sp_ids.push(sp_selections[j].get('id'))
                    }
                var storage_grid = storage_panel.items.get("cms_cp_storage_panel").items.get("cms_cp_storage_grid");
                var storage_store = storage_grid.getStore();
                storage_store.load({
                                    params:{
                                            sp_id: Ext.util.JSON.encode(sp_ids)
                                           }
                                   });
            }
        }
    });


    var networkNode = new Ext.tree.TreeNode({
        text: _('网络'),
        draggable: false,
        id: "node6",
        nodeid: "cms_cp_network",
        icon:'icons/vm-storage.png',
        leaf:false,
        allowDrop : false,
        listeners: {
            click: function(item) {
                var id=item.id;

                var server_pool_grid = server_pool_panel.items.get("cms_cp_server_pool_panel").items.get("cms_cp_server_pool_grid");
                var server_pool_store = server_pool_grid.getStore();
                var sp_selections = server_pool_grid.getSelections();
                var sp_ids = new Array();
                for(var j=0; j<sp_selections.length; j++){
                        sp_ids.push(sp_selections[j].get('id'))
                    }
                var network_defined_grid = network_panel.items.get("cms_cp_defined_network_panel").items.get("cms_cp_defined_network_grid");
                var network_defined_store = network_defined_grid.getStore();
                network_defined_store.load({
                                            params:{
                                                    action : action,
                                                    sp_ids: Ext.util.JSON.encode(sp_ids),
                                                    provider_id : node.attributes.id
                                                   }
                                        });

                var network_vlan_grid = network_panel.items.get("cms_cp_vlan_network_panel").items.get("cms_cp_vlan_network_grid");
                var network_vlan_store = network_vlan_grid.getStore();
                network_vlan_store.load({
                                        params:{
                                                action : action,
                                                sp_ids: Ext.util.JSON.encode(sp_ids),
                                                provider_id : node.attributes.id
                                               }
                                     });


            }
        }
    });


    var templateNode = new Ext.tree.TreeNode({
        text: _('模板'),
        draggable: false,
        id: "node7",
        nodeid: "cms_cp_template",
        icon:'icons/vm-storage.png',
        leaf:false,
        allowDrop : false
        //cls:"labelcolor"
    });

    var NetworkingServiceNode = new Ext.tree.TreeNode({
        text: _('网络服务'),
        draggable: false,
        id: "node8",
        nodeid: "cms_cp_networking_service",
        icon:'icons/vm-storage.png',
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
        items:[treeheading,treePanel]

    });


    rootNode.appendChild(generalNode);
    
    if(action=='EDIT'){
        
        if(is_feature_enabled(cp_feature, stackone.constants.CF_REGION))
            {
                rootNode.appendChild(regionNode);
            }

        if(is_feature_enabled(cp_feature, stackone.constants.CF_SERVICE_OFFERING))
            {
                rootNode.appendChild(serviceNode);
            }
        if(is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT))
            {
                rootNode.appendChild(accountNode);
            }
        if(is_feature_enabled(cp_feature, stackone.constants.CF_SERVER_POOL))
            {
                rootNode.appendChild(serverPoolNode);
            }
        if(is_feature_enabled(cp_feature, stackone.constants.CF_STORAGE))
            {
                rootNode.appendChild(storageNode);
            }
        if(is_feature_enabled(cp_feature, stackone.constants.CF_NETWORK))
            {
                rootNode.appendChild(networkNode);
            }
        if(is_feature_enabled(cp_feature, stackone.constants.CF_TEMPLATE_GROUP))
            {
                rootNode.appendChild(templateNode);
            }
        if(is_feature_enabled(cp_feature, stackone.constants.CF_NETWORKING_SERVICE))
            {
                rootNode.appendChild(NetworkingServiceNode);
            }

//        rootNode.appendChild(serverPoolNode);
//        rootNode.appendChild(storageNode);
//        rootNode.appendChild(networkNode);
//        rootNode.appendChild(templateNode);

    }
    if(action=='ADD'){

//                alert("-----r-----"+is_feature_enabled(cp_feature, stackone.constants.CP_REGION_LEFT_NODE))

                if(is_feature_enabled(cp_feature, stackone.constants.CF_REGION))
                    {
                        rootNode.appendChild(regionNode);
                    }

                if(is_feature_enabled(cp_feature, stackone.constants.CF_SERVICE_OFFERING))
                    {
                        rootNode.appendChild(serviceNode);
                    }
                
                if(is_feature_enabled(cp_feature, stackone.constants.CF_SERVER_POOL))
                    {
                        rootNode.appendChild(serverPoolNode);
                    }

                if(is_feature_enabled(cp_feature, stackone.constants.CF_STORAGE))
                    {
                        rootNode.appendChild(storageNode);
                    }

                if(is_feature_enabled(cp_feature, stackone.constants.CF_NETWORK))
                    {
                        rootNode.appendChild(networkNode);
                    }

                if(is_feature_enabled(cp_feature, stackone.constants.CF_TEMPLATE_GROUP))
                    {
                       
                        rootNode.appendChild(templateNode);
                    }
                if(is_feature_enabled(cp_feature, stackone.constants.CF_NETWORKING_SERVICE))
                    { 

                        rootNode.appendChild(NetworkingServiceNode);
                    }
    }
   

    treePanel.setRootNode(rootNode);
//    if(action=='EDIT'){
//        regionNode.disable();
//        serviceNode.disable();
//    }




    var button_prev=new Ext.Button({
        id: 'move-prev',
        //text: _('Prev'),
        disabled: true,
        icon:'icons/2left.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                 if(status==true||conn_status==true){

                    process_card_panel(card_panel,treePanel,-1);
                }
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
                if(status==true||conn_status==true){
                    process_card_panel(card_panel,treePanel,1);
                }
                
            }
        }
    });

    

    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {

            click: function(btn) {
               if(action=='EDIT'){
                    if(conn_status==false){
                        Ext.MessageBox.alert(_("错误"),"请检查连接");
                    }
                    else{
                        status = false;
                        var cp_name=general_details_panel.items.get('general_panel').items.get("name").getValue();
                        if(!cp_name){
                            Ext.MessageBox.alert(_("错误"),"请指定IaaS的名称.");
                            return;
                        }
                        if(!checkSpecialCharacters(cp_name, "IaaS Name")){
                            return;
                        }
                       var acc_ids=Ext.getCmp("acc_id").getValue();
                       
                       var acci=account_grid.getStore();
                       var acclist=[]
                       for(var i=0;i<acci.getCount();i++){
                           var accnt_info=new Object();
                           
//                           accnt_info['account_details']=acci.getAt(i).get('account_details');
                           acclist.push(acci.getAt(i).get('account_details'));
                           
                       }
                   
                       var account_info_edit_json= Ext.util.JSON.encode({
                            "AccountInfo":acclist
                        });
                        
                        


                         Ext.MessageBox.show({
                            title:_('请稍候...'),
                            msg: _('请稍候...'),
                            width:300,
                            wait:true,
                            waitConfig: {
                                interval:200
                            }
                        });

                        var egitems=general_details_panel.items.get('general_panel').items;
                        var access_infos_edit=new Object();
                            
                        if(is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT))
                            {
                                access_infos_edit['endpoint']=egitems.get('endpoint').getValue();
                                access_infos_edit['port']=egitems.get('port').getValue();
                                access_infos_edit['access_key']=egitems.get('access_key_id').getValue();
                                access_infos_edit['secret_access_key']=egitems.get('secret_access_key').getValue();
                                access_infos_edit['path']=egitems.get('path').getValue();
                                var data_edit = collect_region_instance_type_info(region_details_panel, service_details_panel)
                                if (data_edit == null){return;}
                                // Region and Instance Type, Region has templates and Zones.
                                access_infos_edit['region_instance_type_info'] = data_edit
                            }


                        /////////////// SERVER_POOL //////////////////
                        if(is_feature_enabled(cp_feature, stackone.constants.CF_SERVER_POOL))
                            {
                                var sp_info = new Object()
                                var sp_panel_items = server_pool_panel.items.get('cms_cp_server_pool_panel').items;
                                var sp_grid = sp_panel_items.get("cms_cp_server_pool_grid");
                                var sp_store = sp_grid.getStore();
                                var add_sps = new Array();
                                var remove_sps = new Array();
                                for(var k=0;k<sp_store.getCount();k++)
                                {
//                                    alert("-----cc-------"+sp_grid.getSelectionModel().isSelected(k))
                                    if (sp_grid.getSelectionModel().isSelected(k))
                                    {
                                        if (sp_store.getAt(k).get('selected')==false)
                                            {
                                                add_sps.push(sp_store.getAt(k).get('id'))
                                            }
                                    }
                                    else{
                                          if (sp_store.getAt(k).get('selected')==true)
                                                {
                                                    remove_sps.push(sp_store.getAt(k).get('id'))
                                                }
                                    }
                                }

                               sp_info['add_sps'] = add_sps;
                               sp_info['remove_sps'] = remove_sps;
                               access_infos_edit['server_pools'] = sp_info;
                            }


                        /////////////// TEMPLATE_GROUP //////////////////
                        if(is_feature_enabled(cp_feature, stackone.constants.CF_TEMPLATE_GROUP))
                           {
                                var temp_info = new Object()
                                var temp_panel_items = template_panel.items.get('cms_cp_template_panel').items;
                                var temp_grid = temp_panel_items.get("cms_cp_template_grid");
                                var temp_store = temp_grid.getStore();
                                var add_temp = new Array();
                                var remove_temp = new Array();
                                for(var k=0;k<temp_store.getCount();k++)
                                {
//                                    alert("-----cc-------"+sp_grid.getSelectionModel().isSelected(k))
                                    if (temp_grid.getSelectionModel().isSelected(k))
                                    {
                                        if (temp_store.getAt(k).get('selected')==false)
                                            {
                                                add_temp.push(temp_store.getAt(k).get('id'))
                                            }
                                    }
                                    else{
                                          if (temp_store.getAt(k).get('selected')==true)
                                                {
                                                    remove_temp.push(temp_store.getAt(k).get('id'))
                                                }
                                    }
                                }

                               temp_info['add_temp'] = add_temp;
                               temp_info['remove_temp'] = remove_temp;
                               access_infos_edit['templates'] = temp_info;
                          }

                        /////////////// NETWORK //////////////////
                        if(is_feature_enabled(cp_feature, stackone.constants.CF_NETWORK))
                            {
                                /////////////// DEFINED NETWORK //////////////////
                                var defined_nw_info = new Object()
                                var defined_nw_panel_items = network_panel.items.get('cms_cp_defined_network_panel').items;
                                var defined_nw_grid = defined_nw_panel_items.get("cms_cp_defined_network_grid");
                                var defined_nw_store = defined_nw_grid.getStore();
                                var add_nw = new Array();
                                var remove_nw = new Array();
                                for(var k=0;k<defined_nw_store.getCount();k++)
                                {
//                                    alert("-----cc-------"+sp_grid.getSelectionModel().isSelected(k))
                                    if (defined_nw_grid.getSelectionModel().isSelected(k))
                                    {
                                        if (defined_nw_store.getAt(k).get('selected')==false)
                                            {
                                                add_nw.push(defined_nw_store.getAt(k).get('id'))
                                            }
                                    }
                                    else{
                                          if (defined_nw_store.getAt(k).get('selected')==true)
                                                {
                                                    remove_nw.push(defined_nw_store.getAt(k).get('id'))
                                                }
                                    }
                                }

                               defined_nw_info['add_nw'] = add_nw;
                               defined_nw_info['remove_nw'] = remove_nw;
                               access_infos_edit['defined_networks'] = defined_nw_info;



                                /////////////// VLAN ID POOL //////////////////
                                var vlan_id_pool_info = new Object()
                                var vlan_id_pool_panel_items = network_panel.items.get('cms_cp_vlan_network_panel').items;
                                var vlan_id_pool_grid = vlan_id_pool_panel_items.get("cms_cp_vlan_network_grid");
                                var vlan_id_pool_store = vlan_id_pool_grid.getStore();
                                var add_vlan_id_pool = new Array();
                                var remove_vlan_id_pool = new Array();
                                for(var k=0;k<vlan_id_pool_store.getCount();k++)
                                {
                                //                                    alert("-----cc-------"+sp_grid.getSelectionModel().isSelected(k))
                                    if (vlan_id_pool_grid.getSelectionModel().isSelected(k))
                                    {
                                        if (vlan_id_pool_store.getAt(k).get('selected')==false)
                                            {
                                                add_vlan_id_pool.push(vlan_id_pool_store.getAt(k).get('id'))
                                            }
                                    }
                                    else{
                                          if (vlan_id_pool_store.getAt(k).get('selected')==true)
                                                {
                                                    remove_vlan_id_pool.push(vlan_id_pool_store.getAt(k).get('id'))
                                                }
                                    }
                                }

                                vlan_id_pool_info['add_vlan_id_pool'] = add_vlan_id_pool;
                                vlan_id_pool_info['remove_vlan_id_pool'] = remove_vlan_id_pool;
                                access_infos_edit['vlan_id_pools'] = vlan_id_pool_info;

                                ////// Public IP Pool //////
                                var pub_ip_pool_panel_items = network_panel.items.get('cms_cp_pub_ip_pool_panel').items;
                                var pub_ip_pool_combo = pub_ip_pool_panel_items.get("cms_cp_pub_ip_pool_combo");
                                access_infos_edit['public_ip_pool'] = pub_ip_pool_combo.getValue();


                           }

                           if (is_feature_enabled(cp_feature, stackone.constants.CF_NETWORKING_SERVICE)){
                                     var inner_panel_items=networking_service_panel.items.get('networking_service_inner_panel').items;
                                     //upper pannel
                                     var networking_service_upper_panel_items =inner_panel_items.get('networking_service_upper_panel').items;

                                     var primary_panel_items= networking_service_upper_panel_items.get('primary_panel').items;
                                     var standby_panel_items= networking_service_upper_panel_items.get('standby_panel').items;

                                     var primary_serverpool_panel_items=primary_panel_items.get('primary_serverpool_panel').items;
                                     var primary_server_panel_items=primary_panel_items.get('primary_server_panel').items;

                                     var standby_serverpool_panel_items=standby_panel_items.get('standby_serverpool_panel').items;
                                     var standby_server_panel_items=standby_panel_items.get('standby_server_panel').items;

                                     var primary_serverpool_combo=primary_serverpool_panel_items.get('primary_serverpool_combo');
                                     //values------
                                     var primary_sp=primary_serverpool_combo.getRawValue();
                                     var primary_sp_id=primary_serverpool_combo.getValue();
//                                     alert("---primary_sp_id------"+primary_sp_id);
                                     //------

                                     var primary_server_combo=primary_server_panel_items.get('primary_server_combo');
                                     //values------
                                     var primary_s=primary_server_combo.getRawValue();
                                     var primary_s_id=primary_server_combo.getValue();
                                     var primary_public_Interface=primary_panel_items.get('primary_public_interface').getValue();
                                     //------
                                     var standby_serverpool_combo=standby_serverpool_panel_items.get('standby_serverpool_combo');
                                     //values------
                                     var standby_sp=standby_serverpool_combo.getRawValue();
                                     var standby_sp_id=standby_serverpool_combo.getValue();
//                                     alert("---standby_sp_id------"+standby_sp_id);
                                     //------
                                     var standby_server_combo=standby_server_panel_items.get('standby_server_combo');
                                     //values------
                                     var standby_s=standby_server_combo.getRawValue();
                                     var standby_s_id=standby_server_combo.getValue();
                                     var standby_public_Interface=standby_panel_items.get('standby_public_interface').getValue();
                                     //------
                                     //end--upper pannel
                                     //////////////////
                                    var networking_service_lower_panel_items =inner_panel_items.get('networking_service_lower_panel').items;
                                    var server=networking_service_lower_panel_items.get('server').getValue();
                                   
                                    var user=networking_service_lower_panel_items.get('user').getValue();
                                    var pass=networking_service_lower_panel_items.get('password').getValue();
                                    var sshport=networking_service_lower_panel_items.get('sshport').getValue();
                                    var pub_interface=networking_service_lower_panel_items.get('publicinterface').getValue();

                                    //////////////
//                                  
                                    var external_radio =inner_panel_items.get('external_server').getValue();
                                    var internal_radio= inner_panel_items.get('server_pool').getValue();

           //Validation check for Internal serverpool
                                    var i_nw_items=new Object();
                                    var prmer_items=new Object();
                                    var standby_items=new Object();
                                    var netwokservice=new Object();
                                    var e_nw_items=new Object();
                                    if(internal_radio==true){

                                        if(primary_sp==null || primary_sp==""){
                                            
                                            Ext.MessageBox.alert(_("错误"),"请选择网络服务的首选服务器池.");
                                            return;

                                        }else if(primary_s==null || primary_s=="" ){
                                             Ext.MessageBox.alert(_("错误"),"请选择网络服务的首选主机.");
                                             return;
                                        }else if(primary_public_Interface==null || primary_public_Interface =="" ){
                                             Ext.MessageBox.alert(_("错误"),"请输入网络服务的首选公共接口.");
                                             return;
                                        }
                                        if(standby_sp!="" ||standby_s!="" ||standby_public_Interface!=""){
                                            if(standby_sp==null || standby_sp==""){
                                                Ext.MessageBox.alert(_("错误"),"请选择网络服务的备用服务器池.");
                                                return;
                                            }else if(standby_s==null || standby_s=="" ){
                                                Ext.MessageBox.alert(_("错误"),"请选择网络服务的备用主机.");
                                                return;
                                            }else if(standby_public_Interface==null || standby_public_Interface =="" ){
                                                Ext.MessageBox.alert(_("错误"),"请输入网络服务的备用公共接口.");
                                                return;
                                            }
                                        }

                                        prmer_items['sp_id']=primary_sp_id;
                                        prmer_items['server_name']=primary_s;
                                        prmer_items['server_id']=primary_s_id;
                                        prmer_items['interface']=primary_public_Interface;

                                        if(!primary_sp_id){
                                            prmer_items = "";
                                        }

                                        i_nw_items['primary']=prmer_items;

                                        standby_items['sp_id']=standby_sp_id;
                                        standby_items['server_name']=standby_s;
                                        standby_items['server_id']=standby_s_id;
                                        standby_items['interface']=standby_public_Interface;

                                        if(!standby_sp_id||standby_sp_id=="none"){
                                            standby_items = "";
                                        } else {
                                            //stand by is defined
                                            if (standby_s_id == primary_s_id){
                                                Ext.MessageBox.alert(_("错误"),"网络服务的首选和备用主机不能为同一个.");
                                                return;
                                            }
                                        }

                                        i_nw_items['standby']=standby_items;
                                        netwokservice['internal_nw']=i_nw_items;
                                        netwokservice['external_nw']="";


                                    }else{

                                        if(server==""||user=="" ||pass==null||sshport==null||pub_interface==""){
                                            //alert(server+user+pass+sshport+pub_interface);
                                            Ext.MessageBox.alert(_("错误"),"您输入网络服务的外部服务器信息不完整，"+
                                                " 请重新检查输入信息.");
                                            return;
                                        }
                                        e_nw_items['server']=server;
                                        e_nw_items['user']=user;
                                        e_nw_items['password']=pass;
                                        e_nw_items['sshport']=sshport;
                                        e_nw_items['publicinterface'] =pub_interface;//cms(csep) region id
                                        netwokservice['external_nw']=e_nw_items;
                                        netwokservice['internal_nw']="";
                                    }

                                    access_infos_edit["network_service_info"]=netwokservice
                             }

                            var access_info_edit_json= Ext.util.JSON.encode({
                                "AccessInfo":access_infos_edit
                            });


                        var url1='/cloud_provider/update_provider?type='+type+'&provider_id='+node.attributes.id+
                            '&name='+egitems.get('name').getValue()+'&access_info='+access_info_edit_json+'&account_info='+account_info_edit_json+"&acc_ids="+acc_ids;
                        var ajaxReq1=ajaxRequest(url1,0,"POST",true);
                        ajaxReq1.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    Ext.MessageBox.alert( _("状态") , response.msg);
                                    closeWindow();

                                 }
                                 else {
                                    Ext.MessageBox.alert( _("失败") , response.msg);
                                }
                            },
                            failure: function(xhr){
                                Ext.MessageBox.alert( _("失败") , xhr.statusText);
                            }
                        });
                    }
                   

                }
                else{////////////  ADD  //////////////
                    var cp_name=general_details_panel.items.get('general_panel').items.get("name").getValue();
                    if(status==false){
                        Ext.MessageBox.alert(_("错误"),"请填写相应的字段与正确的值");
                    }
                    else if(!cp_name){
                        Ext.MessageBox.alert(_("错误"),"请指定Iaas的名称.");
                    }
                    else if(!checkSpecialCharacters(cp_name, "IaaS Name")){
                        return;
                    }
                     else{

                        Ext.MessageBox.show({
                            title:_('请稍候...'),
                            msg: _('请稍候...'),
                            width:300,
                            wait:true,
                            waitConfig: {
                                interval:200
                            }
                        });

                        if (is_feature_enabled(cp_feature, stackone.constants.CF_REGION) && is_feature_enabled(cp_feature, stackone.constants.CF_SERVICE_OFFERING))
                            {
                                var data_add = collect_region_instance_type_info(region_details_panel, service_details_panel)
                                if (data_add == null){return;}
                                var jsondata = Ext.util.JSON.encode(data_add)

                                var gitems=general_details_panel.items.get('general_panel').items;
                                if(gitems.get('name').getValue().trim()===""){
                                    Ext.MessageBox.alert(_("错误"),"请输入一个名称");
                                    return;
                                }
                                var name=gitems.get('name').getValue();
        //                        var access_key=gitems.get('access_key_id').getValue();
        //                        var secret_access_key=gitems.get('secret_access_key').getValue();

                                var access_infos=new Object();
                                access_infos['access_key']=gitems.get('access_key_id').getValue();
                                access_infos['secret_access_key']=gitems.get('secret_access_key').getValue();
        //                        access_infos['region']=gitems.get('region').getValue();
                                if(is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT))
                                    {
                                        access_infos['endpoint']=gitems.get('endpoint').getValue();
                                        access_infos['port']=gitems.get('port').getValue();
                                        access_infos['path']=gitems.get('path').getValue();
                                    }

                                var jsondata1= Ext.util.JSON.encode({
                                    "Name":name,
                                    "AccessInfo":access_infos
                                });

            //                    alert("roooooooooo"+node.attributes.id)
        //                        alert("---type------"+type);
                                var url='/cloud_provider/create_provider?type='+type+'&provider_node_id='+node.attributes.id+'&provider_details='+jsondata+
                                '&general='+jsondata1;
                          }//////// CMS CP ///////////
                          else if(is_feature_enabled(cp_feature, stackone.constants.CF_SERVER_POOL) && is_feature_enabled(cp_feature, stackone.constants.CF_TEMPLATE_GROUP)){
                                var gitems=general_details_panel.items.get('general_panel').items;
                                var name=gitems.get('name').getValue();
                                var access_infos=new Object();
//                                access_infos['endpoint']=gitems.get('endpoint').getValue();
//                                access_infos['port']=gitems.get('port').getValue();

                                var csep_info = new Object();

                                ///////////// SERVER POOL //////////
                                var sp_panel_items = server_pool_panel.items.get('cms_cp_server_pool_panel').items;
                                var sp_grid = sp_panel_items.get("cms_cp_server_pool_grid");
                                var selected_sps = sp_grid.getSelections();

                                //Validation
                                if (selected_sps.length == 0)
                                    {
                                        Ext.MessageBox.alert(_("错误"),"请选择一个服务器池");
                                        return;
                                    }

                                var sel_sp_ids = new Array();
                                for(var j=0; j<selected_sps.length; j++){
                                        sel_sp_ids.push(selected_sps[j].get('id'));
                                    }
                                csep_info["server_pools"] = sel_sp_ids;

                                ///////////// TEMPLATE GROUP //////////
                                var temp_panel_items = template_panel.items.get('cms_cp_template_panel').items;
                                var temp_grid = temp_panel_items.get("cms_cp_template_grid");
                                var selected_temps = temp_grid.getSelections();

                                //Validation
                                if (selected_temps.length == 0)
                                    {
                                        Ext.MessageBox.alert(_("错误"),"请选择一个模板");
                                        return;
                                    }

                                var sel_temps_ids = new Array();
                                for(var j=0; j<selected_temps.length; j++){
                                        sel_temps_ids.push(selected_temps[j].get('id'));
                                    }
                                csep_info["template_groups"] = sel_temps_ids;


                                ///////////// DEFINED NETWORK //////////
                                var defined_nw_panel_items = network_panel.items.get('cms_cp_defined_network_panel').items;
                                var defined_nw_grid = defined_nw_panel_items.get("cms_cp_defined_network_grid");
                                var selected_nws = defined_nw_grid.getSelections();

                                ///// Validation //////
//                                if (selected_nws.length == 0)
//                                    {
//                                        Ext.MessageBox.alert(_("Error"),"Please select a VLAN Network");
//                                        return;
//                                    }

                                var sel_nws_ids = new Array();
                                for(var j=0; j<selected_nws.length; j++){
                                        sel_nws_ids.push(selected_nws[j].get('id'));
                                    }
                                csep_info["defined_networks"] = sel_nws_ids;


                                ///////////// VLAN ID POOL //////////
                                var vlan_id_pool_panel_items = network_panel.items.get('cms_cp_vlan_network_panel').items;
                                var vlan_id_pool_grid = vlan_id_pool_panel_items.get("cms_cp_vlan_network_grid");
                                var selected_vlan_id_pools = vlan_id_pool_grid.getSelections();

                                ////// Validation ////////
//                                if (selected_vlan_id_pools.length == 0)
//                                    {
//                                        Ext.MessageBox.alert(_("Error"),"Please select a VLAN ID Pool");
//                                        return;
//                                    }

                                var sel_vlan_id_pools_ids = new Array();
                                for(var j=0; j<selected_vlan_id_pools.length; j++){
                                        sel_vlan_id_pools_ids.push(selected_vlan_id_pools[j].get('id'));
                                    }
                                csep_info["vlan_id_pools"] = sel_vlan_id_pools_ids;


                                ////// Public IP Pool //////
                                var pub_ip_pool_panel_items = network_panel.items.get('cms_cp_pub_ip_pool_panel').items;
                                var pub_ip_pool_combo = pub_ip_pool_panel_items.get("cms_cp_pub_ip_pool_combo");
                                csep_info["public_ip_pool"] = pub_ip_pool_combo.getValue();

                                ////// Validation ////////
//                                if (pub_ip_pool_combo.getValue() == "")
//                                    {
//                                        Ext.MessageBox.alert(_("Error"),"Please select a Public IP Pool");
//                                        return;
//                                    }

                                 if (is_feature_enabled(cp_feature, stackone.constants.CF_NETWORKING_SERVICE)){
                                     var inner_panel_items=networking_service_panel.items.get('networking_service_inner_panel').items;
                                     //upper pannel
                                     var networking_service_upper_panel_items =inner_panel_items.get('networking_service_upper_panel').items;

                                     var primary_panel_items= networking_service_upper_panel_items.get('primary_panel').items;
                                     var standby_panel_items= networking_service_upper_panel_items.get('standby_panel').items;

                                     var primary_serverpool_panel_items=primary_panel_items.get('primary_serverpool_panel').items;
                                     var primary_server_panel_items=primary_panel_items.get('primary_server_panel').items;

                                     var standby_serverpool_panel_items=standby_panel_items.get('standby_serverpool_panel').items;
                                     var standby_server_panel_items=standby_panel_items.get('standby_server_panel').items;

                                     var primary_serverpool_combo=primary_serverpool_panel_items.get('primary_serverpool_combo');
                                     //values------
                                     var primary_sp=primary_serverpool_combo.getRawValue();
                                     var primary_sp_id=primary_serverpool_combo.getValue();
//                                     alert("---primary_sp_id------"+primary_sp_id);
                                     //------

                                     var primary_server_combo=primary_server_panel_items.get('primary_server_combo');
                                     //values------
                                     var primary_s=primary_server_combo.getRawValue();
                                     var primary_s_id=primary_server_combo.getValue();
                                     var primary_public_Interface=primary_panel_items.get('primary_public_interface').getValue();
                                     //------
                                     var standby_serverpool_combo=standby_serverpool_panel_items.get('standby_serverpool_combo');
                                     //values------
                                     var standby_sp=standby_serverpool_combo.getRawValue();
                                     var standby_sp_id=standby_serverpool_combo.getValue();
//                                     alert("---standby_sp_id------"+standby_sp_id);
                                     //------
                                     var standby_server_combo=standby_server_panel_items.get('standby_server_combo');
                                     //values------
                                     var standby_s=standby_server_combo.getRawValue();
                                     var standby_s_id=standby_server_combo.getValue();
                                     var standby_public_Interface=standby_panel_items.get('standby_public_interface').getValue();
                                     //------
                                     //end--upper pannel
                                     //////////////////
                                    var networking_service_lower_panel_items =inner_panel_items.get('networking_service_lower_panel').items;
                                    var server=networking_service_lower_panel_items.get('server').getValue();
                                    var user=networking_service_lower_panel_items.get('user').getValue();
                                    var pass=networking_service_lower_panel_items.get('password').getValue();
                                    var sshport=networking_service_lower_panel_items.get('sshport').getValue();
                                    var pub_interface=networking_service_lower_panel_items.get('publicinterface').getValue();

                                    //////////////
//
                                    var external_radio =inner_panel_items.get('external_server').getValue();
                                    var internal_radio= inner_panel_items.get('server_pool').getValue();
                                    var i_nw_items=new Object();
                                    var prmer_items=new Object();
                                    var standby_items=new Object();
                                    var netwokservice=new Object();
                                    var e_nw_items=new Object();
                                    if(internal_radio==true){

                                        if(primary_sp==null || primary_sp==""){                                            
                                            Ext.MessageBox.alert(_("错误"),"请为网络服务选项选择一个服务器池");
                                            return;

                                        }else if(primary_s==null || primary_s=="" ){
                                             Ext.MessageBox.alert(_("错误"),"请选择一个主机");
                                             return;
                                        }else if(primary_public_Interface==null || primary_public_Interface =="" ){
                                             Ext.MessageBox.alert(_("错误"),"请选择一个公共接口");
                                             return;
                                        }
                                        if(standby_sp!="" ||standby_s!="" ||standby_public_Interface!=""){
                                            if(standby_sp==null || standby_sp==""){
                                                Ext.MessageBox.alert(_("错误"),"请选择备用服务器池");
                                                return;
                                            }else if(standby_s==null || standby_s=="" ){
                                                Ext.MessageBox.alert(_("错误"),"请选择备用主机");
                                                return;
                                            }else if(standby_public_Interface==null || standby_public_Interface =="" ){
                                                Ext.MessageBox.alert(_("错误"),"请选择备用公共接口");
                                                return;
                                            }
                                        }
                                        
                                        prmer_items['sp_id']=primary_sp_id;
                                        prmer_items['server_name']=primary_s;
                                        prmer_items['server_id']=primary_s_id;
                                        prmer_items['interface']=primary_public_Interface;
                                        i_nw_items['primary']=prmer_items;
                                        
                                        standby_items['sp_id']=standby_sp_id;
                                        standby_items['server_name']=standby_s;
                                        standby_items['server_id']=standby_s_id;
                                        standby_items['interface']=standby_public_Interface;
                                        if(!standby_sp_id||standby_sp_id=="none"){
                                            standby_items = "";
                                        }
                                        i_nw_items['standby']=standby_items;
                                        netwokservice['internal_nw']=i_nw_items;
                                        netwokservice['external_nw']="";
                                        
                                        
                                    }else{

                                        if(server==""||user=="" ||pass==""||sshport==""||pub_interface==""){
                                            Ext.MessageBox.alert(_("错误"),"您输入的信息不完整，请重新检查输入信息");
                                            return;
                                        }
                                        e_nw_items['server']=server;
                                        e_nw_items['user']=user;
                                        e_nw_items['password']=pass;
                                        e_nw_items['sshport']=sshport;
                                        e_nw_items['publicinterface'] =pub_interface;
                                        netwokservice['external_nw']=e_nw_items;
                                        netwokservice['internal_nw']="";
                                       
                                    }
                                                                     
                                   csep_info["network_service_info"]=netwokservice
                             }

                                var jsondata1= Ext.util.JSON.encode({
                                    "Name" : name,
                                    "AccessInfo" : access_infos,
                                    "csep_info" : csep_info
                                    
                                });
                                
                                var url='/cloud_provider/create_provider?type='+type+'&provider_node_id='+node.attributes.id+'&provider_details='+null+
                                                                '&general='+jsondata1;
                            }

                    
                          var ajaxReq=ajaxRequest(url,0,"POST",true);
                        ajaxReq.request({
                            success: function(xhr) {
                                var response=Ext.util.JSON.decode(xhr.responseText);
                                if(response.success){
                                    Ext.MessageBox.alert( _("状态") , response.msg);
                                    closeWindow();
                                    status=false;
                                 }
                                 else {
                                    Ext.MessageBox.alert( _("失败") , response.msg);
                                }
                            },
                            failure: function(xhr){
                                Ext.MessageBox.alert( _("失败") , xhr.statusText);
                            }
                        });
                    }
                   
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
            status=false;
            closeWindow();
        }
    }
    });

    var card_panel=new Ext.Panel({
    width:468,
    height:432,
    layout:"card",
    id:"card_panel",
    //        activeItem:0,
    cls: 'whitebackground',
    border:false,
    bbar:[
    {
        xtype: 'tbfill'
    },button_prev,button_next,button_ok,button_cancel]
    });


    var general_details_panel=create_cp_general_panel(node, card_panel, treePanel, action, type, cp_feature);

    if(action=='EDIT'){
        general_details_panel.items.get('general_panel').items.get('name').setValue(result.name);

        var account_record=result.account_details;
        var account_grid=create_editaccount_panel(type, node, cp_feature);//List Accounts grid

        ////// Enable/Disable Acoount panel based on development.ini setting  /////
        if(result.edit_account == false)
        {
            account_grid.disable();
        }

        var acc_rec = Ext.data.Record.create([
                                    {
                                        name: 'name',
                                        type: 'string'
                                    },
                                    {
                                        name: 'accesskey',//Account ID
                                        type: 'string'
                                    },
                                    {
                                        name: 'Description',
                                        type: 'string'
                                    },
                                    {
                                        name: 'account_details'//accesskey and secret_accesskey
                                    }
                                    ]);

                                for (var i=0;i<=account_record.length-1;i++){
                                   var acc_details= account_record[i].account_details;


                                    
                                    var param_obj_str="{";
                                        param_obj_str+="\"name\":\""+acc_details.account_name+"\",";
                                        param_obj_str+="\"account_id\":\""+acc_details.account_id+"\",";
                                        param_obj_str+="\"desc\":\""+acc_details.desc+"\",";
                                        param_obj_str+="\"provider_id\":\""+acc_details.provider_id+"\",";
                                        param_obj_str+="\"accesskey\":\""+acc_details.accesskey+"\",";
                                        param_obj_str+="\"secret_access_key\":\""+acc_details.secret_access_key+"\"";
                                        param_obj_str+="}";

                                     var r=new acc_rec({
                                        name:acc_details.account_name,
                                        accesskey:acc_details.accesskey,//Show Account ID instead of Account Name.
                                        Description:acc_details.desc,
                                        account_details:param_obj_str
                                    });

                                    account_grid.getStore().insert(0, r);
                                   

                                    }

//        general_details_panel.items.get('general_panel').items.get('region').setValue(result.region);
        if(is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT))
            {
                general_details_panel.items.get('general_panel').items.get('access_key_id').setValue(result.access_key);
                general_details_panel.items.get('general_panel').items.get('secret_access_key').setValue(result.secret_access_key);
                general_details_panel.items.get('general_panel').items.get('path').setValue(result.path);
                general_details_panel.items.get('general_panel').items.get('endpoint').setValue(result.endpoint);
                general_details_panel.items.get('general_panel').items.get('port').setValue(result.port);
            }



            card_panel.add(account_grid);
    }

    if(is_feature_enabled(cp_feature, stackone.constants.CF_REGION))
    {
        var region_details_panel=create_region_panel(type, action);
    }
    if(is_feature_enabled(cp_feature, stackone.constants.CF_SERVICE_OFFERING))
    {
        var service_details_panel=create_service_panel(type);
    }
    if(is_feature_enabled(cp_feature, stackone.constants.CF_SERVER_POOL))
    {
        var server_pool_panel = create_cms_cp_server_pool_panel(type, action, node, result)
    }
    if(is_feature_enabled(cp_feature, stackone.constants.CF_TEMPLATE_GROUP))
    {
        var template_panel = create_cms_cp_template_panel(type, action, node)
    }
    if(is_feature_enabled(cp_feature, stackone.constants.CF_STORAGE))
    {
        var storage_panel = create_cms_cp_storage_panel(type, server_pool_panel)
    }
    if(is_feature_enabled(cp_feature, stackone.constants.CF_NETWORK))
    {
        var network_panel = create_cms_cp_network_panel(type,  action, node)
    }
    if(is_feature_enabled(cp_feature, stackone.constants.CF_NETWORKING_SERVICE)){
        
        var networking_service_panel = create_cms_cp_networking_service_panel(type, action, node, result)
    }
        
    var right_panel=new Ext.Panel({
    id:"right_panel",
    width:475,
    height:440,
    //frame:true,
    cls: 'whitebackground',
    border:false,
    bodyStyle:'padding:5px 5px 5px 5px'
    ,listeners: {
        afterlayout: function() {//alert("afterlayout"+card_panel.activeItem);
            card_panel.getLayout().setActiveItem("panel0");
        }
     }
    });


   var outerpanel=new Ext.FormPanel({
       height: 490,
       width: 670,
       autoEl: {},
       layout: 'column',
       items: [side_panel,right_panel]
   });

   card_panel.add(general_details_panel);

   if(is_feature_enabled(cp_feature, stackone.constants.CF_REGION))
    {
        card_panel.add(region_details_panel);
    }
   if(is_feature_enabled(cp_feature, stackone.constants.CF_SERVICE_OFFERING))
    {
        card_panel.add(service_details_panel);
    }
   if(is_feature_enabled(cp_feature, stackone.constants.CF_SERVER_POOL))
    {
        card_panel.add(server_pool_panel);
    }
   if(is_feature_enabled(cp_feature, stackone.constants.CF_TEMPLATE_GROUP))
    {
        card_panel.add(template_panel);
    }
   if(is_feature_enabled(cp_feature, stackone.constants.CF_STORAGE))
    {
        card_panel.add(storage_panel);
    }
   if(is_feature_enabled(cp_feature, stackone.constants.CF_NETWORK))
    {
        card_panel.add(network_panel);
    }
   if(is_feature_enabled(cp_feature, stackone.constants.CF_NETWORKING_SERVICE)){
        card_panel.add(networking_service_panel);
   }
   right_panel.add(card_panel);
//   card_panel.activeItem = 0;


   return outerpanel;
      
}


function statuscheck(x)
{
    if(status==true)
    {
        x;
    }
}



function collect_region_instance_type_info(region_details_panel, service_details_panel)
{
    var finitems=new Object();
    var rgrid=region_details_panel.items.get('region_panel').items.get('reg_grid');
     var regsel=rgrid.getSelections();
    if(regsel.length<1){
        Ext.MessageBox.alert(_("错误"),"请至少选择一个Region");
        return null;
    }
    var frecord="";
    var rname="";
    var rend="";
    var region_id = "";
    for(var i=0;i<regsel.length;i++)
    {
        frecord=rgrid.getStore().getAt(i);
        rname=regsel[i].get('region');
        rend=regsel[i].get('end_point');
        region_id = regsel[i].get('region_id');//cms(csep) region id
        if(!regsel[i].get('zone_name')){
            Ext.MessageBox.alert(_("错误"),"请至少选择一个zones");
            return null;
        }
        else{
            var zone_name=regsel[i].get('zone_name');
            var zlist=regsel[i].get('zone_list');
            var zn=[];
            zn=zone_name.split(",");
            var zonelist=[];
            for(var j=0;j<zn.length;j++){
                for(var k=0;k<zlist.length;k++){
                    if(zn[j]==zlist[k].name){
                        zonelist.push(zlist[k]);
                    }
                }
            }
        }

        var sel_nonsel_templates = {};
        if(!regsel[i].get('temp_id')['selected_temp_ids']){
            Ext.MessageBox.alert(_("错误"),"请至少选择一个模板");
            return null;
        }
        else{
            var nonsel_temp_ids = regsel[i].get('temp_id')['non_selected_temp_ids'];
            var temp_id=regsel[i].get('temp_id')['selected_temp_ids'];
            var tlist=regsel[i].get('temp_list');
            // 'tlist' contain templates(machine, kernel and ramdisk) with details as list of dicts(object), taken from Cloud via Boto call.
            var tid=[];
            tid=temp_id.split(",");
            var templist=[];
            for(var j=0;j<tid.length;j++){
                for(var k=0;k<tlist.length;k++){
                    if(tid[j]==tlist[k].id){
                        //get object(dict) of selected templates from 'tlist'.
                        templist.push(tlist[k]);

                    }
                }
            }
        }
        //Region details
        sel_nonsel_templates["sel_templates"] = templist;
        sel_nonsel_templates["nonsel_templates"] = nonsel_temp_ids;
        var items=new Object();
        items['templates']=sel_nonsel_templates; // Selected templates with details for send to backend.
        items['zones']=zonelist;
        items['region']=rname;
        items['end_point']=rend;
        items['region_id'] = region_id;//cms(csep) region id

        finitems[rname]=items;
    }

    var serlist=new Array();
    var sgrid=service_details_panel.items.get('service_panel').items.get('ser_grid');
    var sselections=sgrid.getSelections();
    if(sselections.length>0){
        for(var i=0;i<sselections.length;i++){
            var frecord=sgrid.getStore().getAt(i);
            var serdic=new Object();
            serdic['name']=sselections[i].get('name');
            serdic['description']=sselections[i].get('description');
            serdic['platform']=sselections[i].get('platform');
            serdic['cpu']=sselections[i].get('cpu');
            serdic['memory']=sselections[i].get('memory');
            serdic['storage']=sselections[i].get('storage');
            serdic['cname']=sselections[i].get('cname');
            serdic['cid']=sselections[i].get('cid');
            serdic['service_offering_id']=sselections[i].get('service_offering_id');//cms(csep) service_offering_id
            serlist.push(serdic);
        }
    }

    else{
            Ext.MessageBox.alert(_("错误"),"请选择服务产品 ");
            return null;
    }
    
//                    finitems["name"]=gitems.get('name');
//                    finitems["access_key"]=gitems.get('access_key_id');
//                    finitems["secret_key"]=gitems.get('secret_access_key');

    var data= {
                "Regions":finitems,
                "ServceOfferings":serlist
             };
    
    return data
}






function create_cp_general_panel(node, card_panel, treePanel, action, type, cp_feature)
{

     var tlabel_general=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("常规信息")+'<br/></div>'
    });

    var access_key_field_label = 'Access Key';
    var secret_access_key_field_label = 'Secret Key';
    var path_field_label = 'Path';
    
    var name=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'url',
        id: 'name',
        width: 320,
        allowBlank:false
    });


    var access_key_id=new Ext.form.TextField({
        fieldLabel: _(access_key_field_label),
        name: 'provider_name1',
        id: 'access_key_id',
        width: 320,
        allowBlank:false
    });

    var secret_access_key=new Ext.form.TextField({
        fieldLabel: _(secret_access_key_field_label),
        inputType:'password',
        name: 'secret_key',
        id: 'secret_access_key',
        width: 300,
        allowBlank:false
    });

//    var region=new Ext.form.TextField({
//        fieldLabel: _('Region'),
//        name: 'region',
//        id: 'region',
//        width: 200,
//        allowBlank:false
//    });

    var endpoint=new Ext.form.TextField({
        fieldLabel: _('服务器'),
        name: 'endpoint',
        id: 'endpoint',
        width: 200,
        allowBlank:false
    });

    var port=new Ext.form.NumberField({
        fieldLabel: _('端口'),
        name: 'port',
        id: 'port',
        width: 200,
        allowBlank:true
    });

    var path=new Ext.form.TextField({
        fieldLabel: _(path_field_label),
		fieldLabel: _('路径'),
        name: 'path',
        id: 'path',
        width: 200,
        allowBlank:false
    });
    if(!is_feature_enabled(cp_feature, stackone.constants.CF_PORT)){

        port.hide();
        port.hideLabel=true;

    }
    if(!is_feature_enabled(cp_feature, stackone.constants.CF_PATH)){

        path.hide();
        path.hideLabel=true;

    }
    if(!is_feature_enabled(cp_feature, stackone.constants.CF_END_POINT)){

        endpoint.hide();
        endpoint.hideLabel=true;

    }

    if (action=='ADD'){
            var url='/cloud_provider/get_initial_data?type='+type
            var ajaxReq=ajaxRequest(url,0,"POST",true);
            ajaxReq.request({
                success: function(xhr) {
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(response.success){
        //                alert("----result-----"+response.result.region);
//                        region.setValue(response.result.region);

                        endpoint.setValue(response.result.endpoint);
                        port.setValue(response.result.port);
                        path.setValue(response.result.path);
//                   Only for CMS Iaas
                       if (is_feature_enabled(cp_feature,stackone.constants.CF_NETWORKING_SERVICE))
                            Ext.getCmp("primary_public_interface").setValue(response.result.public_interface);
//                        Ext.MessageBox.alert( _("Status") , response.msg);
        //                closeWindow();
        //                status=false;
                     }
                     else {
                        Ext.MessageBox.alert( _("失败") , response.msg);
                    }
                },
                failure: function(xhr){
                    Ext.MessageBox.alert( _("失败") , xhr.statusText);
                }
            });

    }

     var tlabel_dummi=new Ext.form.Label({
        html:'<div class="toolbar_hdg"><br/></div>'
    });
     var intrmediate_msg = '.';
     if (type !== stackone.constants.CMS   )
         intrmediate_msg = " 名称，stackone将据此获取openstack的实例、模板等相关信息."
     var tlabel_generalmsg=new Ext.form.Label({
        html:'<div >'+_("<br/>请指定 "+stackone.constants.IAAS+intrmediate_msg )+'<br/></div>'
    });


    var tlabel_success=new Ext.form.Label({
        html:'<div ><b>'+_("连接成功")+'</b></div>'
    });

    var tlabel_wait=new Ext.form.Label({
        html:'<div ><b>'+_("正在连接，请稍候...........")+'</b></div>'
    });
    tlabel_success.hide();

    tlabel_wait.hide();
    var connect_button= new Ext.Button({
        id: 'connect',
        text: _('连接'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                tlabel_success.hide();
                connect_button.disable();
                if (!name.getValue() || !access_key_id.getValue() || !secret_access_key.getValue())
                {
                    Ext.MessageBox.alert(_('错误'), _('请确保你输入的名称和keys是正确的.'));
                    connect_button.enable();
                }
                else
                    {
                        tlabel_wait.show();

                        var access_infos=new Object();
                        access_infos['name']=name.getValue();
                        access_infos['access_key']=access_key_id.getValue();
                        access_infos['secret_access_key']=secret_access_key.getValue();
    //                    access_infos['region']=region.getValue();

                        if(is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT))
                        {
                                if(is_feature_enabled(cp_feature, stackone.constants.CF_PORT)){
                                     if (!port.getValue()){
                                        Ext.MessageBox.alert(_('错误'), _('请确保你输入的端口是正确的.'));
                                        connect_button.enable();
                                        return;
                                     }
                                  }

                                 if (!path.getValue() || !endpoint.getValue()){
                                    Ext.MessageBox.alert(_('错误'), _('请确保你输入的服务器和路径是正确的.'));
                                    connect_button.enable();
                                    return;
                                 }

                                access_infos['endpoint']=endpoint.getValue();
                                access_infos['port']=port.getValue();
                                access_infos['path']=path.getValue();
                         }

                        var access_info_json= Ext.util.JSON.encode({
                            "AccessInfo":access_infos
                        });

                        cp_id = "";
                        if (action == 'EDIT'){
                            cp_id = node.attributes.id;
                        }
                        var url='/cloud_provider/connect_to_provider?type='+type+'&access_info='+access_info_json+'&cp_id='+cp_id;

                        Ext.MessageBox.show({
                            title:_('请稍候...'),
                            msg: _('请稍候..'),
                            width:300,
                            wait:true,
                            waitConfig: {
                                interval:200
                            }
                        });

                          var ajaxReq=ajaxRequest(url,0,"POST",true);
                          ajaxReq.request({
                                    success: function(xhr) {
                                        var response=Ext.util.JSON.decode(xhr.responseText);
                                        if(response.success)
                                            {
                                               Ext.MessageBox.hide();
            //                                    tlabel_wait.hide();
            //                                   Ext.MessageBox.alert(_('Success'), _('Connection is successful'));
                                               tlabel_success.show();
                                               status=true;
                                               var result=response.rows;
            //                                   alert(result.Region.("eu-west-1").name);
                                               var region=result.Region;
                                              //var getKeys = function(region){
                                               var keys = [];
                                               for(var key in region){
                                                  keys.push(key);
                                               }
                                              // return keys;
                                            //}
                                               var reg_rec = Ext.data.Record.create([
                                                    {
                                                        name: 'id',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'region',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'name',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'description',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'end_point',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'cloud_provider_type',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'zone_name',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'zone_list',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'temp_id',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'temp_list',
                                                        type: 'string'
                                                    },
                                                    {//cms(csep) region id
                                                        name: 'region_id',
                                                        type: 'string'
                                                    }
                                                ]);
                                                var region_grid=card_panel.items.get("panel1").items.get('region_panel').items.get('reg_grid');
                                                region_grid.getStore().removeAll();

                                                for(var i=0;i<keys.length;i++){
                                                    var zlist=region[keys[i]].zones
                                                    var tlist=region[keys[i]].templates
                                                    var zname="";
                                                    var tname="";

                                                      //Zone
                                                      for(var j=0;j<zlist.length;j++){
                                                          if (action=='ADD'){
                                                           //Mark all zones as selected by default
                                                           zname+=((j==0)?"":",")+zlist[j].name
                                                          }
                                                          else if (action=='EDIT'){
                                                           if(zlist[j].selected==true){
                                                               //Mark only already selected zones as selected.
                                                               zname+=((j==0)?"":",")+zlist[j].name
                                                           }
                                                          }

                                                      }

                                                      //Template
                                                      for(var j=0;j<tlist.length;j++){
                                                          if (action=='ADD'){
                                                           //Mark all templates as selected by default
                                                           tname+=((j==0)?"":",")+tlist[j].id
                                                          }
                                                          else if (action=='EDIT'){
                                                           if(tlist[j].selected==true){
                                                               //Mark only already selected templates as selected.
                                                               tname+=((j==0)?"":",")+tlist[j].id
                                                           }
                                                          }
                                                      }

                                                        var temp_ids_dict = {};
                                                        temp_ids_dict['non_selected_temp_ids'] = [];
                                                        temp_ids_dict['selected_temp_ids'] = tname;

                                                       var new_entry=new reg_rec({
                                                           id:i+"",
                                                           region:region[keys[i]].name,
                                                           name:"",
                                                           description:"",
                                                           end_point:region[keys[i]].endpoint,
                                                           cloud_provider_type_id:"",
                                                           zone_name:zname,
                                                           zone_list:zlist,
                                                           temp_id:temp_ids_dict,
                                                           temp_list:tlist,
                                                           region_id:region[keys[i]].region_id//cms(csep) region id
                                                       });
            //                                            process_card_panel(card_panel,treePanel,'1',"treepanel");  zrec+=((i==0)?"":",")+selections[i].get('id');
                                                       region_grid.getStore().insert(0,new_entry);

                                                       if (action == 'EDIT'){
                                                           if (region[keys[i]].selected == true){
                                                                //mark last inserted row as selected
                                                                region_grid.getSelectionModel().selectRow(0,true);
                                                           }
                                                       }

                                                }

                                                //Mark all as selected by default.
                                                if (action=='ADD'){
                                                    region_grid.getSelectionModel().selectAll();
                                                }


            //                                           for(var k=0;k<region_grid.getStore().getCount();k++){
            //                                               region_grid.getSelectionModel().selectRow(k,true);
            //
            //                                           }
            //                                           region_grid.getSelectionModel().selectRow(0,true);
                                                      // w.close();
            //                                          alert("---------"+zname);

                                                var so=result.ServiceOfferings;
                                                var skeys = [];
                                                for(var key in so){
                                                    skeys.push(key);
                                               }
                                                var ser_rec = Ext.data.Record.create([
                                                    {
                                                        name: 'id',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'name',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'description',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'platform',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'cpu',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'memory',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'storage',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'cname',
                                                        type: 'string'
                                                    },
                                                    {
                                                        name: 'cid',
                                                        type: 'string'
                                                    },
                                                    {//cms(csep) service_offering_id
                                                        name: 'service_offering_id',
                                                        type: 'string'
                                                    }
                                                ]);
                                                var service_grid=card_panel.items.get("panel2").items.get('service_panel').items.get('ser_grid');
                                                service_grid.getStore().removeAll();
                                                for(var i=0;i<skeys.length;i++){
                                                        var slist=[];
                                                        slist=so[skeys[i]].instance_types;


                                                        for(var j=0;j<slist.length;j++)
                                                            {
                                                               var new_entry=new ser_rec({
                                                                   id:slist[j].id,
                                                                   name:slist[j].name,
                                                                   description:slist[j].description,
                                                                   platform:slist[j].platform,
                                                                   cpu:slist[j].cpu,
                                                                   memory:slist[j].memory,
                                                                   storage:slist[j].storage,
                                                                   cname:so[skeys[i]].category_name,
                                                                   cid:slist[j].cid,
                                                                   service_offering_id:slist[j].service_offering_id//cms(csep) service_offering_id
                                                               });

                                                               service_grid.getStore().insert(0,new_entry);

                                                               if (action == 'EDIT'){
            //                                                       alert("---------"+slist[j].selected);
                                                                   if (slist[j].selected == true){
                                                                        //mark last inserted row as selected
                                                                        service_grid.getSelectionModel().selectRow(0,true);
                                                                   }
                                                               }
                                                            }
                                                    }

                                                    //Mark all as selected by default.
                                                    if (action=='ADD'){
                                                        service_grid.getSelectionModel().selectAll();
                                                    }

                                             conn_status = true;
                                            }
                                            else
                                                {
                                                    conn_status = false;
                                                    tlabel_wait.hide();
                                                    status=false;
                                                    Ext.MessageBox.alert(_("失败") ,response.msg);
                                                }

            //                           card_panel.items.get("panel1").items.get("region_panel").items.get("reg_grid").getStore().load();

            //                           process_card_panel(card_panel,treePanel,1);
                                    },
                                    failure: function(xhr){
                                        status=false;
                                        tlabel_wait.hide();
                                        Ext.MessageBox.alert( _("失败") , xhr.statusText);
                                    }
                                    });
                        connect_button.enable();
                        }
                }
            }
    });

    var tconnect_button= new Ext.Button({
        id: 'test_connect',
        text: _('测试'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if (!name.getValue() || !access_key_id.getValue() || !secret_access_key.getValue()){
                    Ext.MessageBox.alert(_('错误'), _('请确保你输入的名称和keys.'));
                    connect_button.enable();
                }
                else{
                    var gitems=general_details_panel.items.get('general_panel').items;
                    var access_infos_test_conn=new Object();
                    access_infos_test_conn['access_key']=gitems.get('access_key_id').getValue();
                    access_infos_test_conn['secret_access_key']=gitems.get('secret_access_key').getValue();
//                    access_infos_test_conn['region']=gitems.get('region').getValue();
                    if(is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT))
                        {
                            access_infos_test_conn['endpoint']=gitems.get('endpoint').getValue();
                            access_infos_test_conn['port']=gitems.get('port').getValue();
                            access_infos_test_conn['path']=gitems.get('path').getValue();
                        }
                    var access_info_test_conn_json= Ext.util.JSON.encode({
                        "AccessInfo":access_infos_test_conn
                    });

                    var url='/cloud_provider/test_connect?type='+type+'&access_info='+access_info_test_conn_json;
                    Ext.MessageBox.show({
                    title:_('请稍候...'),
                    msg: _('请稍候...'),
                    width:300,
                    wait:true,
                    waitConfig: {
                        interval:200
                    }
                });

                var ajaxReq=ajaxRequest(url,0,"POST",true);
                ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success)
                                {
                                    Ext.MessageBox.hide();
                                    conn_status=true;
                                    tlabel_success.show();
                                }
                                else{
                                    tlabel_wait.hide();
                                    conn_status=false;
                                    tlabel_success.hide();
                                    Ext.MessageBox.alert(_("失败") ,response.msg);
                                }
                        },
                        failure: function(xhr){
                            tlabel_wait.hide();
                            Ext.MessageBox.alert( _("失败") , xhr.statusText);
                        }
                    });

                }
                
            }
        }
    });

//    var dummy_space1=new Ext.form.Label({
//        html:_('&nbsp;&nbsp;&nbsp;<div style="width:10px"/>')
//    });


//    var dummy_space2=new Ext.form.Label({
//        html:_('&nbsp;<div style="width:10px"/>')
//    });

    var dummy_spacex=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });

//    var dummy_spacey=new Ext.form.Label({
//        html:_('&nbsp;<div style="width:10px"/>')
//    });

//    var dummy_space3=new Ext.form.Label({
//        html:_('&nbsp;&nbsp;&nbsp;<div style="width:10px"/>')
//    });

    if(action=='EDIT'){
//        connect_button.hide();
          tconnect_button.hide();
    }
    if(action=='ADD'){
        tconnect_button.hide();
    }

    var connection_items = [];

    if(is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT))
        {
             connection_items = [ {
                        width: 100,
                        layout:'form',
                        border:false,
                        items:[connect_button,tconnect_button]
                    },
                    {
                        labelWidth: 50,
            //            width: 100,
            //            width: 100,
                        layout:'form',
                        border:false,
                        items:[tlabel_success]
                    }]
        }


     var newgeneral_panel = new Ext.Panel({
        height:40,
        id:"newgeneral_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        labelWidth:100,
        buttonAlign :'center',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        //items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],
//        tbar:[tlabel_general,{
//            xtype: 'tbfill'
//        },connect_button],
        items:connection_items
    });

    var generallate_panel = new Ext.Panel({
        height:90,
        id:"generallate_panel",
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        labelWidth:150,
        buttonAlign :'center',
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding:5px 5px 5px 5px',
        //items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],

        items:[newgeneral_panel]
    });

    var label_width=50;
    if(is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT)){
        label_width=100;
    }

    var general_panel = new Ext.Panel({
        height:400,
        id:"general_panel",
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        labelWidth:label_width,
        bodyStyle:'padding:2px 2px 2px 2px',
        buttonAlign :'center',
        border:0,
        bodyBorder:false,
        tbar:[tlabel_general,{
            xtype: 'tbfill'
        }],
        items:[tlabel_generalmsg,dummy_spacex,name]
    });


    if(is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT))
        {
            general_panel.add(access_key_id);
            general_panel.add(secret_access_key);
            general_panel.add(endpoint);
            general_panel.add(port);
            general_panel.add(path);
    }
//    else
//        {
//            general_panel.add(endpoint);
//            general_panel.add(port);
//        }

    general_panel.add(tlabel_dummi);


//    general_panel.add(tlabel_generalmsg);
//    general_panel.add(dummy_space2);
    general_panel.add(generallate_panel);

    var general_details_panel=new Ext.Panel({
        border:false,
        id:"panel0",
        layout:"form",
        width:'100%',
        //cls: 'whitebackground paneltopborder',
        height:300,
        frame:false,
        labelWidth:220,
        bodyStyle:'padding:0px 0px 0px 0px',
        items:[general_panel]
    });

    return general_details_panel;

}

function create_region_panel(type, action)
{

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
        html:'<div>'+_("请选择你需要的数据，以导入stackone "+stackone.constants.IAAS+".")+'<br/></div>'
    });

    var store = new Ext.data.JsonStore({
        url: '/cloud_provider/get_all_lookup_regions?provider_type='+type,
        root: 'rows',
        fields: ['id','region','name','description', 'end_point','cloud_provider_type_id','temp_id','zone_name','add','addt','zone_list','temp_list','region_id'],
        successProperty:'success'
//        listeners:{
//            loadexception:function(obj,opts,res,e){
//                var store_response=Ext.util.JSON.decode(res.responseText);
//                Ext.MessageBox.alert(_("Error"),store_response.msg);
//            }
//        }
    });


     var reg_grid = new Ext.grid.GridPanel({
        store: store,
        enableHdMenu:false,
        selModel:selmodel1,
        id:'reg_grid',
        columns: [
            {
                id       :'id',
                header   : 'Id',
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
                header   : '名称',
//                width    : 120,
                width    : 75,
                sortable : true,
                dataIndex: 'name',
                 hidden : true
            },
            {
                header   : '说明',
//                width    : 265,
                width     : 70,
                sortable : true,
                //renderer : change,
                dataIndex: 'description',
                 hidden : true
            },
            {
                header   : 'End Point',
//                width    : 265,
                width     : 190,
                sortable : true,
                //renderer : change,
                dataIndex: 'end_point'
            },
            {
                header   : 'Type_ID',
                width    : 60,
                sortable : true,
                //renderer : change,
                dataIndex: 'cloud_provider_type_id',
                hidden : true
            },
            {   //contain ami/emi id of templates selected from 'add_tmp_grid' in comma seperated string form.
                header : 'Temp_ID',
                width  : 200,
                hidden : true,
                dataindex :'temp_id'
            },
            {
                header : 'Zone_ID',
                width  : 200,
                hidden : true,
                dataindex :'zone_name'
            },
            {
                header   : '可用区',
                width    : 75,
                sortable : false,
                //renderer : change,
                dataIndex: 'add'
                ,renderer:function(value,params){
                params.attr='ext:qtip="Add Zone"' +
                    'style="background-image:url(icons/add.png) '+
                    '!important; background-position: center;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            }     },
        {
                header   : '模板',
                width    : 70,
                sortable : false,
                //renderer : change,
                dataIndex: 'addt'
                ,renderer:function(value,params){
                params.attr='ext:qtip="Add Template"' +
                    'style="background-image:url(icons/add.png) '+
                    '!important; background-position: center;'+
                    'background-repeat: no-repeat;cursor: pointer;"';
            }     },
            {
                header : 'Zone_list',
                width  : 200,
                hidden : true,
                dataindex :'zone_list'
            },
            {   //contain templates(machine, kernel and ramdisk) with details as list of dicts, taken from Cloud via Boto call'.
                header : 'Temp_list',
                width  : 200,
                hidden : true,
                dataindex :'temp_list'
            } ,
            {//cms(csep) region id
                header : 'region_id',
                width  : 200,
                hidden : true,
                dataindex :'region_id'
            },
            selmodel1

  ],
        stripeRows: true,

        height: 300,
        width:460,
        tbar:[label_region,{
            xtype: 'tbfill'
             }]
           ,listeners: {
           cellclick: function(reg_grid, rowIndex, columnIndex, e) {
               if (columnIndex==8){


                var rrecord = reg_grid.getStore().getAt(rowIndex);

                        var nw=new Ext.Window({
                        title :_('可用区'),
                        width :350,
                        height:400,
                        modal : true,
                        resizable : false
                    });

//                    var selections=reg_grid.getSelections();

                    var np = AddRegionZones(nw,rrecord.get('region'),rrecord.get('zone_name'),rrecord.get('zone_list'),rrecord);


                    nw.add(np);
                    nw.show();
           }
           else if(columnIndex==9)
               {
                   var trecord = reg_grid.getStore().getAt(rowIndex);
                   var tw=new Ext.Window({
                        title :_('模板'),
                        width :800,
                        height:400,
                        modal : true,
                        resizable : false
                    });

                    var tselections=reg_grid.getSelections();
                    var tp=AddTemplates(tw,trecord.get('region'),trecord.get('temp_id')['selected_temp_ids'],trecord.get('temp_list'),trecord, action);

                    tw.add(tp);
                    tw.show();
               }

               else
                   {
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
        width:465,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        buttonAlign : 'center',
        //items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],
        tbar:[tlabel_region],
        items:[tlabel_regionnws,reg_grid]
    });

    var region_details_panel=new Ext.Panel({
         border:false,
        id:"panel1",
        layout:"form",
        width:465,
        //cls: 'whitebackground paneltopborder',
        height:420,
        frame:false,
        labelWidth:220,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[region_panel]
    });

    return region_details_panel;

}

/////////// Server Pools ////////////

function create_cms_cp_server_pool_panel(type, action, node, result)
{
    var server_pool_selection = Ext.data.Record.create([

        {
            name: 'id',
            type: 'string'
        },
        {
            name: 'serverpool',
            type: 'string'
        }
    ]);

    var sp_selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false,
            listeners:{

            }
        });

    var tlabel_server_pool=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("服务器池")+'<br/></div>'
    });

     var label_server_pool=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("")+'<br/></div>'
    });

    var tlabel_desc_server_pool=new Ext.form.Label({
        html:'<div>'+_("请为Iaas选择能提供计算能力的服务器池.")+'<br/></div><br>'
    });

    var server_pool_store = new Ext.data.JsonStore({
        url: '/csep/get_all_server_pool',
        root: 'rows',
        fields: ['id','name','host', 'cpu', 'memory', 'action', 'selected', 'can_remove'],
        successProperty:'success',
        listeners: {
            load:function(store,opts,res,e){
                          store.sort('name','ASC');
                          
                          if (action == 'EDIT'){
                                var size=store.getCount();
                                for (var i=0;i<size;i++){
                                    if (store.getAt(i).get('selected') == true){
                                        server_pool_grid.getSelectionModel().selectRow(i,true);
                                    }
                                }
//                                var network_service = result.additional_details.network_service;
//                                var internal_nw_ser = network_service.internal_nw_ser;
//                                if (internal_nw_ser){
//                                    var primary_ser_det = internal_nw_ser.PRIMARY;
//                                    size=store.getCount();
//                                    for (i=0;i<size;i++){
//                                        if (store.getAt(i).get('id') == primary_ser_det.sp_id){
//                                            var primary_serverpool_combo=Ext.getCmp('primary_serverpool_combo');
//                                            primary_serverpool_combo.setValue(primary_ser_det.sp_id);
//                                            var primary_server_combo=Ext.getCmp('primary_server_combo');
//                                            primary_server_combo.getStore().load({
//                                                params:{
//                                                    serverpoolid:primary_ser_det.sp_id
//                                                }
//                                            });
//                                            break;
//                                        }
//                                    }
//                                }
//
//                                if (internal_nw_ser != undefined)
//                                    if (internal_nw_ser.SECONDARY != undefined){
//                                        var secondary_ser_det = internal_nw_ser.SECONDARY;
//                                        for (var i=0;i<size;i++){
//                                            if (store.getAt(i).get('id') == secondary_ser_det.sp_id){
//                                                var standby_serverpool_combo=Ext.getCmp('standby_serverpool_combo');
//                                                standby_serverpool_combo.setValue(secondary_ser_det.sp_id);
//                                                var standby_server_combo=Ext.getCmp('standby_server_combo');
//
//                                                standby_server_combo.getStore().load({
//                                                    params:{
//                                                        serverpoolid:secondary_ser_det.sp_id
//                                                    }
//                                                })
//                                                break;
//
//                                            }
//                                        }
//                                    }

                          }
                          else{//ADD,  select all rows by default
                                server_pool_grid.getSelectionModel().selectAll();
//                                for(i=0;i<store.getCount();i++){
//                                    if (store.getAt(i).get('selected') == true){
//                                        var new_entry=new server_pool_selection({
//                                            id:store.getAt(i).get('id'),
//                                            serverpool:store.getAt(i).get('name')
//                                        });
////                                        var primary_serverpool_combo=Ext.getCmp('primary_serverpool_combo');
////                                        primary_serverpool_combo.getStore().insert(0,new_entry);
////                                        primary_serverpool_combo.getStore().sort('serverpool','ASC');
////                                        var standby_serverpool_combo=Ext.getCmp('standby_serverpool_combo');
////                                        standby_serverpool_combo.getStore().insert(0,new_entry);
////                                        standby_serverpool_combo.getStore().sort('serverpool','ASC');
//                                    }
//                                }

                          }
//                          var new_entry=new server_pool_selection({
//                            id:'none',
//                            serverpool:'None'
//                          });
//                          var standby_serverpool_combo=Ext.getCmp('standby_serverpool_combo');
//                          standby_serverpool_combo.getStore().insert(0,new_entry);

                  }

            }
    });

    server_pool_store.load({
                            params:{
                                    action : action,
                                    provider_id : node.attributes.id
                                   }
                            });

     var server_pool_grid = new Ext.grid.GridPanel({
        store: server_pool_store,
        enableHdMenu:false,
        selModel:sp_selmodel,
        id:'cms_cp_server_pool_grid',
        columns: [
                    sp_selmodel,
                    {
                        id       :'id',
                        header   : 'Id',
                        width    : 140,
                        sortable : true,
                        dataIndex: 'id',
                        hidden : true
                    },
                    {
                        header   : '名称',
                        width    : 108,
                        sortable : true,
                        dataIndex: 'name',
                        hidden : false
                    },
                    {
                        header   : '主机',
                        width    : 108,
                        sortable : true,
                        dataIndex: 'host',
                        hidden : false,
                        align:'right'
                    },
                    {
                        header   : 'CPUs',
                        width    : 108,
                        sortable : true,
                        dataIndex: 'cpu',
                        hidden : false,
                        align:'right'
                    },
                    {
                        header   : '内存(MB)',
                        width    : 108,
                        sortable : true,
                        dataIndex: 'memory',
                        hidden : false,
                        align:'right'
                    }
                ],

        stripeRows: true,
        height: 300,
        width:460
   
    });


    var server_pool_panel = new Ext.Panel({
        height:415,
        id:"cms_cp_server_pool_panel",
        layout:"form",
        frame:false,
        width:465,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        buttonAlign : 'center',
        tbar:[tlabel_server_pool],
        items:[tlabel_desc_server_pool, server_pool_grid]
    });

    var server_pool_details_panel=new Ext.Panel({
        border:false,
        id:"panel4",
        layout:"form",
        width:465,
        height:420,
        frame:false,
        labelWidth:220,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[server_pool_panel]
    });

    return server_pool_details_panel;
}


/////////// Storage ////////////

function create_cms_cp_storage_panel(type, server_pool_panel)
{

    var storage_selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });

    var tlabel_storage=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("存储")+'<br/></div>'
    });

     var label_storage=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("")+'<br/></div>'
    });

    var tlabel_desc_storage=new Ext.form.Label({
        html:'<div>'+_("请选择虚拟机使用的存储.")+'<br/></div>'
    });

    var storage_ids = new Array();
    var storage_store = new Ext.data.JsonStore({
        url: '/csep/get_all_storage',
        root: 'rows',
        fields: ['id','name','type', 'size', 'sp_id'],
        successProperty:'success',
        listeners:{
            beforeload:function(store)
            {
                storage_ids = [];
                var selections = storage_grid.getSelections();
                for(var j=0; j<selections.length; j++){
                        storage_ids.push(selections[j].get('id'));
                    }
            },
            load:function(store)
             {

                for(var i=0; i<store.getCount(); i++){
                    for(var j=0; j<storage_ids.length; j++){
                        if(store.getAt(i).get('id') == storage_ids[i])
                            {
                                storage_grid.getSelectionModel().selectRow(i,true);
                            }
                }
//                alert("----"+storage_ids);
                }
          }
        }
    });


    var storage_grid = new Ext.grid.GridPanel({
        store: storage_store,
        enableHdMenu:false,
        selModel:storage_selmodel,
        id:'cms_cp_storage_grid',
        columns: [
                    storage_selmodel,
                    {
                        id       :'id',
                        header   : 'Id',
                        width    : 140,
                        sortable : true,
                        dataIndex: 'id',
                        hidden : true
                    },
                    {
                        header   : '名称',
                        width    : 120,
                        sortable : true,
                        dataIndex: 'name',
                        hidden : false
                    },
                    {
                        header   : '类型',
                        width    : 120,
                        sortable : true,
                        dataIndex: 'type',
                        hidden : false
                    },
                    {
                        header   : '大小(GB)',
                        width    : 120,
                        sortable : true,
                        dataIndex: 'size',
                        hidden : false
                    },
                    {
                        header   : 'sp',
                        width    : 50,
                        sortable : true,
                        dataIndex: 'sp_id',
                        hidden : true
                    }
                ],

        stripeRows: true,
        height: 300,
        width:460,
        tbar:[label_storage,{
            xtype: 'tbfill'
             }]
           ,listeners: {
                            ///
                        }
    });


    var storage_panel = new Ext.Panel({
        height:415,
        id:"cms_cp_storage_panel",
        layout:"form",
        frame:false,
        width:465,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        buttonAlign : 'center',
        tbar:[tlabel_storage],
        items:[tlabel_desc_storage, storage_grid]
    });

    var storage_details_panel=new Ext.Panel({
        border:false,
        id:"panel5",
        layout:"form",
        width:465,
        height:420,
        frame:false,
        labelWidth:220,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[storage_panel]
    });

    return storage_details_panel;
}


/////////// Network ////////////

function create_cms_cp_network_panel(type, action, node)
{

    var defined_network_selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });

    var vlan_network_selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });

    var tlabel_network=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("网络")+'<br/></div>'
    });

     var label_defined_network=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("定义的网络")+'<br/></div>'
    });

     var label_vlan_network=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("VLAN ID池")+'<br/></div>'
    });

    var tlabel_desc_network=new Ext.form.Label({
        html:'<div>'+_("请为Iass选择现有的可用网络.")+'<br/></div>'
    });
    var tlabel_desc_vlanidpool =new Ext.form.Label({
        html:'<div>'+_("请为Iass选择现有可用的Vlan ID池.")+'<br/></div>'
    });
    var tlabel_desc_publicippool =new Ext.form.Label({
        html:'<div>'+_("请为Iass选择现有可用的公共IP池.")+'<br/></div>'
    });

    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:80px"/>')
    });

    defined_nw_ids = []
    var defined_network_store = new Ext.data.JsonStore({
        url: '/csep/get_defined_network_details',
        root: 'rows',
        fields: ['id', 'name', 'vlan_id', 'ip_range', 'selected'],
        successProperty:'success',
        listeners:{
            beforeload:function(store)
            {
//                alert("--b---"+store.getCount());
                defined_nw_ids = [];
                var selections = defined_network_grid.getSelections();
                for(var j=0; j<selections.length; j++){
                        defined_nw_ids.push(selections[j].get('id'));
                    }
            },
            load:function(store)
             {
//                alert("--a----"+store.getCount());
                for(var i=0; i<store.getCount(); i++){
                    for(var j=0; j<defined_nw_ids.length; j++){
                        if(store.getAt(i).get('id') == defined_nw_ids[i])
                            {
                                defined_network_grid.getSelectionModel().selectRow(i,true);
                            }                    
                        }
                if(store.getAt(i).get('selected') == true)
                    {
                        defined_network_grid.getSelectionModel().selectRow(i,true);
                    }
//                alert("----"+storage_ids);
                }
          }
        }
    });


    var vlan_id_pools_ids = []
    var vlan_network_store = new Ext.data.JsonStore({
        url: '/csep/get_vlan_id_pools_by_sp',
        root: 'rows',
        fields: ['id', 'name', 'range', 'available_ids', 'selected'],
        successProperty:'success',
        listeners:{
            beforeload:function(store)
            {
//                alert("--b---"+store.getCount());
                vlan_id_pools_ids = [];
                var selections = vlan_network_grid.getSelections();
                for(var j=0; j<selections.length; j++){
                        vlan_id_pools_ids.push(selections[j].get('id'));
                    }
            },
            load:function(store)
             {
//                alert("--a----"+store.getCount());
                for(var i=0; i<store.getCount(); i++){
                    for(var j=0; j<vlan_id_pools_ids.length; j++){
                        if(store.getAt(i).get('id') == vlan_id_pools_ids[i])
                            {
                                vlan_network_grid.getSelectionModel().selectRow(i,true);
                            }
                        }
                if(store.getAt(i).get('selected') == true)
                    {
                        vlan_network_grid.getSelectionModel().selectRow(i,true);
                    }
//                alert("----"+storage_ids);
                }
          }
        }
    });


    var defined_network_grid = new Ext.grid.GridPanel({
        store: defined_network_store,
        enableHdMenu:false,
        selModel:defined_network_selmodel,
        id:'cms_cp_defined_network_grid',
        columns: [
                    defined_network_selmodel,
                    {
                        id       :'id',
                        header   : 'Id',
                        width    : 140,
                        sortable : true,
                        dataIndex: 'id',
                        hidden : true
                    },
                    {
                        header   : '名称',
                        width    : 145,
                        sortable : true,
                        dataIndex: 'name',
                        hidden : false
                    },
                    {
                        header   : 'VLAN ID',
                        width    : 145,
                        sortable : true,
                        dataIndex: 'vlan_id',
                        hidden : false
                    },
                    {
                        header   : 'IP范围',
                        width    : 145,
                        sortable : true,
                        dataIndex: 'ip_range',
                        hidden : false
                    }
                ],

        stripeRows: true,
        height: 80,
        width:460,
        tbar:[label_defined_network,{
            xtype: 'tbfill'
             }]
           ,listeners: {
                            ///
                        }
    });



    var vlan_network_grid = new Ext.grid.GridPanel({
        store: vlan_network_store,
        enableHdMenu:false,
        selModel:vlan_network_selmodel,
        id:'cms_cp_vlan_network_grid',
        columns: [
                    vlan_network_selmodel,
                    {
                        id       :'id',
                        header   : 'Id',
                        width    : 140,
                        sortable : true,
                        dataIndex: 'id',
                        hidden : true
                    },
                    {
                        header   : '名称',
                        width    : 145,
                        sortable : true,
                        dataIndex: 'name',
                        hidden : false
                    },
                    {
                        header   : '范围',
                        width    : 145,
                        sortable : true,
                        dataIndex: 'range',
                        hidden : false
                    },
                    {
                        header   : '可用IDs',
                        width    : 146,
                        sortable : true,
                        dataIndex: 'available_ids',
                        hidden : false
                    }
                ],

        stripeRows: true,
        height: 64 ,
        width:460,
        tbar:[label_vlan_network,{
            xtype: 'tbfill'
             }]
           ,listeners: {
                            ///
                        }
    });



    var defined_network_panel = new Ext.Panel({
        height:138,
        id:"cms_cp_defined_network_panel",
        layout:"form",
        frame:false,
        width:465,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:2px 2px 2px 2px',
        buttonAlign : 'center',
        tbar:[tlabel_network],
        items:[tlabel_desc_network, defined_network_grid]
    });


    var vlan_network_panel = new Ext.Panel({
        height:138,
        id:"cms_cp_vlan_network_panel",
        layout:"form",
        frame:false,
        width:465,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        buttonAlign : 'center',
//        tbar:[tlabel_network],
        items:[tlabel_desc_vlanidpool,vlan_network_grid]
    });



    var label_pub_ip_pool=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("公共IP池")+'<br/></div>'
    });

    var label_available_ips=new Ext.form.Label({
        html:''
    });

    var pub_ip_pool_store = new Ext.data.JsonStore({
        url: '/csep/get_all_public_ip_pools',
        root: 'rows',
        fields: ['id','name', 'selected'],
        successProperty:'success',
        sortInfo:{
            field:'name',
            direction:'ASC'
        },
        listeners:{
            load:function(obj,opts,res,e){
                var cnt = pub_ip_pool_combo.getStore().getCount()
                if (action == "ADD"){
                        if(cnt==1){
                            pub_ip_pool_combo.setValue(pub_ip_pool_combo.getStore().getAt(0).get('id'));
                        }
                    }
                 if (action == "EDIT"){
                      for(var i=0; i<cnt; i++){
                          if(pub_ip_pool_combo.getStore().getAt(i).get("selected") == true){
                              pub_ip_pool_combo.setValue(pub_ip_pool_combo.getStore().getAt(i).get('id'));
                          }
                      }

                 //On Edit mode , disable pub_ip_pool_combo if pool already selected.
                 if (pub_ip_pool_combo.getValue()){
                        pub_ip_pool_combo.disable();
                    }

                 }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    var options=new Object()
    var params=new Object();
    params["provider_id"] = "";
    if (action === 'EDIT')
        {
            params["provider_id"] = node.attributes.id;
        }
    options['params']=params;
   
    pub_ip_pool_store.load(options);


    var pub_ip_pool_combo=new Ext.form.ComboBox({
        fieldLabel: _('公共IP池'),
        allowBlank:false,
        width: 250,
        store:pub_ip_pool_store,
        id:'cms_cp_pub_ip_pool_combo',
        forceSelection: true,
        triggerAction:'all',
        emptyText :_("选择公共IP池"),
        minListWidth:250,
        resizable:true,
        displayField:'name',
        valueField:'id',
//        value: rgrecord.get('region'),
        mode:'local'

    });

//    if (action == 'EDIT'){
//        pub_ip_pool_combo.disable();
//    }

    var pub_ip_pool_panel = new Ext.Panel({
        height:90,
        labelWidth:150,
        id:"cms_cp_pub_ip_pool_panel",
        layout:"form",
        frame:false,
        width:465,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        tbar:[label_pub_ip_pool],
        items:[tlabel_desc_publicippool,pub_ip_pool_combo, label_available_ips]
    });


    var network_details_panel=new Ext.Panel({
        border:false,
        id:"panel6",
//        layout:"form",
        width:465,
        height:420,
        frame:false,
        labelWidth:220,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[defined_network_panel, vlan_network_panel, pub_ip_pool_panel]
    });

    return network_details_panel;
}


/////////// Template Groups ////////////

function create_cms_cp_template_panel(type, action, node)
{

    var template_selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false,
            listeners:{
                rowdeselect:function(sel_model, index, record){
                    if(record.get('can_remove') == false){
                        sel_model.selectRow(index, true);
                        Ext.MessageBox.alert(_("错误"),"不可以移除模板组:"+record.get('name')+ ", 虚拟数据中心正在使用它.");
                    }
                }
            }
        });
    var tlabel_template=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("模板组")+'<br/></div>'
    });



    var tlabel_desc_template=new Ext.form.Label({
        html:'<div>'+_("请为Iass选择可用的模板组.")+'<br/></div>'
    });

    var template_store = new Ext.data.JsonStore({
        url: '/csep/get_all_template_groups',
        root: 'rows',
        fields: ['id','name','template', 'description', 'action', 'selected', 'can_remove'],
        successProperty:'success',
        listeners: {
            load:function(store,opts,res,e){
                          store.sort('name','ASC');
                          if (action == 'EDIT'){
                                  var size=store.getCount();
                                   for (var i=0;i<size;i++){
                                        if (store.getAt(i).get('selected') == true){
                                        template_grid.getSelectionModel().selectRow(i,true);
                                  }
                                }
                          }
                          else{//ADD,  select all rows by default
                                    template_grid.getSelectionModel().selectAll();
                          }
                  }

            }
    });


    template_store.load({
                            params:{
                                    action : action,
                                    provider_id : node.attributes.id
                                   }
                            });


    var template_grid = new Ext.grid.GridPanel({
        store: template_store,
        enableHdMenu:false,
        selModel:template_selmodel,
        id:'cms_cp_template_grid',
        columns: [
                    template_selmodel,

                    {
                        id       :'id',
                        header   : 'Id',
                        width    : 140,
                        sortable : true,
                        dataIndex: 'id',
                        hidden : true
                    },
                    {
                        header   : '名称',
                        width    : 150,
                        sortable : true,
                        dataIndex: 'name',
                        hidden : false
                    },
                    {
                        header   : '模板计数',
                        width    : 100,
                        align:'right',
                        sortable : true,
                        dataIndex: 'template',
                        hidden : false
                    },
                    {
                        header   : '说明',
                        width    : 170,
                        sortable : true,
                        dataIndex: 'description',
                        hidden : false
                    }
                ],

        stripeRows: true,
        height: 350,
        autoScroll:true,
        width:460,
        listeners: {
                            ///
                        }
    });

    /// Select All Tempaltes by default
    for(var k=0;k<template_grid.getStore().getCount();k++){
       template_grid.getSelectionModel().selectRow(k,true);
    }

    var template_panel = new Ext.Panel({
        height:415,
        id:"cms_cp_template_panel",
        layout:"form",
        frame:false,
        width:465,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        buttonAlign : 'center',
        tbar:[tlabel_template],
        items:[tlabel_desc_template, template_grid]
    });

    var template_details_panel=new Ext.Panel({
        border:false,
        id:"panel7",
        layout:"form",
        width:465,
        height:420,
        frame:false,
        labelWidth:220,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[template_panel]
        ,listeners:{
            show:function(p){
                if(template_store.getCount()>0){
                    template_store.sort('name','ASC');
                }
            }
        }
    });

    return template_details_panel;
}
function create_cms_cp_networking_service_panel(type, action, node, result){

    var networking_service_selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false,
            listeners:{
                rowdeselect:function(sel_model, index, record){
//                    if(record.get('can_remove') == false){
//                        sel_model.selectRow(index, true);
//                        Ext.MessageBox.alert(_("Error"),"Can not remove template group:"+record.get('name')+ ", Virtual Machines exist");
//                    }
                }
            }
        });

    
    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:5px"/>')
    });

    var dummy_space2=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space3=new Ext.form.Label({
        html:_('&nbsp;<div style="width:5px"/>')
    });
    var dummy_space4=new Ext.form.Label({
        html:_('&nbsp;<div style="width:5px"/>')
    });
    var dummy_space5=new Ext.form.Label({
        html:_('&nbsp;<div style="height:10px"/>')
    })
     var dummy_space6=new Ext.form.Label({
        html:_('&nbsp;<div style="height:5px"/>')
    })
     var dummy_space12=new Ext.form.Label({
        html:_('&nbsp;<div style="width:6px"/>')
    });
     
     var dummy_space8=new Ext.form.Label({
        html:_('&nbsp;<div style="width:7px"/>')
    });
    var dummy_space9=new Ext.form.Label({
        html:_('&nbsp;<div style="width:6px"/>')
    });
    var dummy_space10=new Ext.form.Label({
        html:_('&nbsp;<div style="width:6px"/>')
    });
    var dummy_space11=new Ext.form.Label({
        html:_('&nbsp;<div style="width:6px"/>')
    });
    var dummy_space12=new Ext.form.Label({
        html:_('&nbsp;<div style="width:7px"/>')
    });

    var networking_service_desc=new Ext.form.Label({
        html:'<div>'+_("请为网络服务选择主机.")+'<br/></div>'
    });
    var primary_label=new Ext.form.Label({
        html:'<div>'+_("首选")+'<br/></div>'
    });
    var standby_label=new Ext.form.Label({
        html:'<div>'+_("备用")+'<br/></div>'
    });


    var primary_checkbox= new Ext.form.Checkbox({
        name: 'primary_checkbox',
        id: 'primary_checkbox',
        checked:true,
        width:20,
        listeners:{
            check:function(field,checked){
//                if(checked){
//                }
            }
        }
    });
     var standby_checkbox= new Ext.form.Checkbox({
        name: 'standby_checkbox',
        id: 'standby_checkbox',
        checked:true,
        width:20,
        listeners:{
            check:function(field,checked){
//                if(checked){
//                }
            }
        }
    });
    var from_server_pool_radio=new Ext.form.Radio({
        boxLabel:_('从服务器池指定主机.'),
        name:"server_radio",
        hideLabel: true,
        id:'server_pool',
        value:'server_pool',
        checked: false,
        width:250,
        listeners: {
           check: function(r, checked) {

              
                
                if(checked) {
                    
                    networking_service_upper_panel.enable();
                    networking_service_lower_panel.disable();


                }else{
                    networking_service_upper_panel.disable();
                    networking_service_lower_panel.enable();

                }

           }
//           beforeshow  :function(c) {
//
//                 if(action=='ADD'){
//                 external_server_radio.setValue(false);}
//                 }
        }
    });

     var external_server_radio=new Ext.form.Radio({
        boxLabel:_('指定外部主机.'),
        name:"server_radio",
        hideLabel: true,
        id:'external_server',
        value:'external_server',
        
        width:250,
        listeners: {

           check: function(r, checked) {
                if(checked) {

 
                }

           }
//           beforeshow  :function(c) {
//
//                 if(action=='ADD'){
//                 from_server_pool_radio.setValue(true);}
//           }
        }


          
        
    });


     var button_test_interface=new Ext.Button({
        name: 'test_interface',
        id: 'test_interface',
        text:_('测试接口'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(server.getValue()==""||user.getValue()==""||password.getValue()==""||sshport.getValue()==null||sshport.getValue()==""){
                    Ext.MessageBox.alert(_("错误"),"您输入的信息不完整，请重新检查输入信息");
                      return;
                }
                Ext.MessageBox.show({
                            title:_('请稍候...'),
                            msg: _('请稍候...'),
                            width:300,
                            wait:true,
                            waitConfig: {
                                interval:200
                            }
                        });
               if(publicinterface.getValue()!=""){
                    var url='/csep/test_interface?server='+server.getValue()+"&user="+user.getValue()+"&password="+password.getValue()+"&sshport="+sshport.getValue();
                    var ajaxReq=ajaxRequest(url,0,"POST",true);
                  ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            
                            Ext.MessageBox.alert( _("状态") , response.msg);
                         }
                         else {
                            Ext.MessageBox.alert( _("失败") , response.msg);
                        }
                    },
                    failure: function(xhr){
                        Ext.MessageBox.alert( _("失败") , xhr.statusText);
                    }
                });
            }


            
        }
        }
     });

      var primary_serverpool_store = new Ext.data.JsonStore({
        url: '/csep/get_serverpools',
        root: 'rows',
        fields: ['id','serverpool'],
        successProperty:'success',
        sortInfo:{
            field:'serverpool',
            direction:'ASC'
        },
        listeners:{
            
            load:function(store,opts,res,e){
                if (action == 'EDIT'){
                    var network_service = result.additional_details.network_service;
                    var internal_nw_ser = network_service.internal_nw_ser;
                    if (internal_nw_ser){
                        var primary_ser_det = internal_nw_ser.PRIMARY;
                        var size=store.getCount();
                        for (i=0;i<size;i++){
                            if (store.getAt(i).get('id') == primary_ser_det.sp_id){
                                var primary_serverpool_combo=Ext.getCmp('primary_serverpool_combo');
                                primary_serverpool_combo.setValue(primary_ser_det.sp_id);
                                var primary_server_combo=Ext.getCmp('primary_server_combo');
                                primary_server_combo.getStore().load({
                                    params:{
                                        serverpoolid:primary_ser_det.sp_id
                                    }
                                });
                                break;
                            }
                        }
                    }
                }

            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    primary_serverpool_store.load({
                            params:{
                                    action : action,
                                    provider_id : node.attributes.id
                                   }
                            });

    var primary_serverpool_combo=new Ext.form.ComboBox({
        id: 'primary_serverpool_combo',
//        fieldLabel: _('Server Pool'),
        hideLabel: true,
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择服务器池"),
        store: primary_serverpool_store,
        width:110,
        displayField:'serverpool',
        valueField:'id',
        typeAhead: true,
        minListWidth:110,
        mode:'local',
        forceSelection: true,
        selectOnFocus:true,
        listeners:{
            select:function(combo,record,index){
                
                    var serverpool_id=record.get('id');
                    primary_server_store.load({
                         params:{
                            serverpoolid:serverpool_id
                        }

                })
            }
        }
    });
     var standby_serverpool_store = new Ext.data.JsonStore({
        url: '/csep/get_standby_serverpools',
        root: 'rows',
        fields: ['id','serverpool'],
        successProperty:'success',
        sortInfo:{
            field:'serverpool',
            direction:'ASC'
        },
        listeners:{

            load:function(store,opts,res,e){
                if (action == 'EDIT'){
                    var internal_nw_ser = network_service.internal_nw_ser;
                    if (internal_nw_ser != undefined){
                        if (internal_nw_ser.SECONDARY != undefined){
                            var secondary_ser_det = internal_nw_ser.SECONDARY;
                            for (var i=0;i<size;i++){
                                if (store.getAt(i).get('id') == secondary_ser_det.sp_id){
                                    var standby_serverpool_combo=Ext.getCmp('standby_serverpool_combo');
                                    standby_serverpool_combo.setValue(secondary_ser_det.sp_id);
                                    var standby_server_combo=Ext.getCmp('standby_server_combo');

                                    standby_server_combo.getStore().load({
                                        params:{
                                            serverpoolid:secondary_ser_det.sp_id
                                        }
                                    })
                                    break;

                                }
                            }
                        }
                    }
                }

            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

    standby_serverpool_store.load({
                            params:{
                                    action : action,
                                    provider_id : node.attributes.id
                                   }
                            });
     var standby_serverpool_combo=new Ext.form.ComboBox({
        id: 'standby_serverpool_combo',
//        fieldLabel: _('Server Pool'),
        hideLabel: true,
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择服务器池"),
        store: standby_serverpool_store,
        width:110,
        displayField:'serverpool',
        valueField:'id',
        typeAhead: true,
        minListWidth:110,
        mode:'local',
        forceSelection: true,
        selectOnFocus:true,
        listeners:{
            select:function(combo,record,index){
                var serverpool_id=record.get('id');
                standby_server_store.load({
                     params:{
                        serverpoolid:serverpool_id
                    }

                })
                if(record.get('id')=="none"){
                    standby_public_Interface.setValue("None");
                    standby_server_combo.setValue("None");
                }
                else{
                    standby_public_Interface.setValue("");
                    standby_server_combo.setValue("");

                }
                
//                var etype=record.get('name');
//                type_combo_raw_value = combo.getRawValue();
//                type_combo_value = combo.getValue();
//                entity_store.load({
//                    params:{
//                        type:etype
//                    }
//                });
//                setREPColumnHeaders(etype, columnModel);
            }
        }
    });

    var primary_server_store = new Ext.data.JsonStore({
        url: '/csep/get_servers',
        root: 'rows',
        fields: ['id','servers'],
        successProperty:'success',
        sortInfo:{
            field:'servers',
            direction:'ASC'
        },
        listeners:{
            load:function(store,opts,res,e){
                primary_server_combo.setValue("");
                if (action == 'EDIT'){
                    var network_service = result.additional_details.network_service;
                    var internal_nw_ser = network_service.internal_nw_ser;
                    if (internal_nw_ser){
                        var primary_ser_det = internal_nw_ser.PRIMARY;
                          var size=store.getCount();
                           for (var i=0;i<size;i++){
                                if (store.getAt(i).get('id') == primary_ser_det.server_id){
                                primary_server_combo.setValue(primary_ser_det.server_id);
                              }
                            }
                    }
                }

            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

//    primary_server_store.load();
     var primary_server_combo=new Ext.form.ComboBox({
        id: 'primary_server_combo',
//        fieldLabel: _('Server'),
        hideLabel: true,
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择主机"),
        store: primary_server_store,
        width:110,
        displayField:'servers',
        valueField:'id',
        typeAhead: true,
        minListWidth:110,
        mode:'local',
        forceSelection: true,
        selectOnFocus:true,
        listeners:{
            select:function(combo,record,index){
//                var etype=record.get('name');
//                type_combo_raw_value = combo.getRawValue();
//                type_combo_value = combo.getValue();
//                entity_store.load({
//                    params:{
//                        type:etype
//                    }
//                });
//                setREPColumnHeaders(etype, columnModel);
            }
        }
    });
    var standby_server_store = new Ext.data.JsonStore({
        url: '/csep/get_standby_servers',
        root: 'rows',
        fields: ['id','servers'],
        successProperty:'success',
        sortInfo:{
            field:'servers',
            direction:'ASC'
        },
        listeners:{
            load:function(store,opts,res,e){
                if (action == 'EDIT'){
                    var network_service = result.additional_details.network_service;
                    var internal_nw_ser = network_service.internal_nw_ser;
                    if (internal_nw_ser){
                       if( internal_nw_ser.SECONDARY != undefined){
                          var secondary_ser_det = internal_nw_ser.SECONDARY;
                          var size=store.getCount();
                           for (var i=0;i<size;i++){
                                if (store.getAt(i).get('id') == secondary_ser_det.server_id){
                                standby_server_combo.setValue(secondary_ser_det.server_id);
                              }
                            }
                       }
                    }
                }


            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });

     var standby_server_combo=new Ext.form.ComboBox({
        id: 'standby_server_combo',
//        fieldLabel: _('Server'),
        hideLabel: true,
        allowBlank:false,
        triggerAction:'all',
        emptyText :_("选择主机"),
        store: standby_server_store,
        width:110,
        displayField:'servers',
        valueField:'id',
        typeAhead: true,
        minListWidth:110,
        mode:'local',
        forceSelection: true,
        selectOnFocus:true,
        listeners:{
            select:function(combo,record,index){
//                var etype=record.get('name');
//                type_combo_raw_value = combo.getRawValue();
//                type_combo_value = combo.getValue();
//                entity_store.load({
//                    params:{
//                        type:etype
//                    }
//                });
//                setREPColumnHeaders(etype, columnModel);
            }
        }
    });



    var primary_public_Interface=new Ext.form.TextField({
        fieldLabel: _('公共接口'),
//        name: 'url',
        id: 'primary_public_interface',
        emptyText :_("公共接口"),
        width: 100,
        allowBlank:false,
        listeners:{
            beforerender :function(f){
//                var etype=record.get('name');
//                type_combo_raw_value = combo.getRawValue();
//                type_combo_value = combo.getValue();
//                entity_store.load({
//                    params:{
//                        type:etype
//                    }
//                });
//                setREPColumnHeaders(etype, columnModel);
            }
        }
    });
    var standby_public_Interface=new Ext.form.TextField({
        fieldLabel: _('公共接口'),
//        name: 'url',
        emptyText :_("公共接口"),
        id: 'standby_public_interface',
        width: 100,
        allowBlank:false
    });

//     var server_pool_store = new Ext.data.JsonStore({
//        url: '/csep/get_all_template_groups',
//        root: 'rows',
//        fields: ['id','name','template', 'description', 'action', 'selected', 'can_remove'],
//        successProperty:'success',
//        listeners: {
//            load:function(store,opts,res,e){
//
//                  }
//
//            }
//    });
//
//    server_pool_store.load({
//                            params:{
//                                    action : action,
//                                    provider_id : node.attributes.id
//                                   }
//                            });

  var server=new Ext.form.TextField({
        fieldLabel: _('主机'),
//        name: 'url',
        id: 'server',
        width: 200,
        allowBlank:false
    });
     var user=new Ext.form.TextField({
        fieldLabel: _('用户名'),
//        name: 'url',
        id: 'user',
        width: 200,
        allowBlank:false
    });
     var password=new Ext.form.TextField({
        fieldLabel: _('密码'),
        inputType: 'password',
//        name: 'url',
        id: 'password',
        width: 200,
        allowBlank:false
    });
    var sshport=new Ext.form.NumberField({
        fieldLabel: _('SSH端口'),
        name: 'numbers',
        width: 200,
        id: 'sshport',
        allowBlank:false
    });

     var publicinterface=new Ext.form.TextField({
        fieldLabel: _('公共接口'),
       // name: 'url',
        id: 'publicinterface',
        width: 200,
        allowBlank:false
    });

  var networking_service_lower_panel = new Ext.Panel({
        height:'40%',
        id:"networking_service_lower_panel",
        layout:"form",
        frame:false,
        width:'100%',
//        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding-left:20px',
        buttonAlign : 'center',
//        tbar:[tlabel_template],
        items:[server,user,password,sshport,publicinterface,dummy_space3,button_test_interface]
    });


    var primary_panel=new Ext.Panel({
        id:"primary_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        items:[primary_label,dummy_space2, {//primary_checkbox,
                width: 130,
                id:"primary_serverpool_panel",
                layout:'form',
                border:false,
                items:[primary_serverpool_combo]
            },dummy_space12,{
                width: 130,
                id:"primary_server_panel",
                layout:'form',
                border:false,
                items:[primary_server_combo]
            },dummy_space11,primary_public_Interface]
        
    });

     var standby_panel=new Ext.Panel({
        id:"standby_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        items:[standby_label,dummy_space8,{//standby_checkbox,
                width: 130,
                layout:'form',
                id:"standby_serverpool_panel",
                border:false,
                items:[standby_serverpool_combo]
            },dummy_space9, {
                width: 130,
                layout:'form',
                id:"standby_server_panel",
                border:false,
                items:[standby_server_combo]
            },dummy_space10,standby_public_Interface]
    });
    


  var networking_service_upper_panel = new Ext.Panel({
        height:100,
        id:"networking_service_upper_panel",
        layout:"form",
//        frame:true,
        width:'100%',
//        autoScroll:true,
        border:false,
        bodyBorder:false,
        autoExpandColumn:2,
//        autoExpandMin:150,

        bodyStyle:'padding-left:20px',
        buttonAlign : 'center',
//        tbar:[tlabel_template],
        items:[primary_panel,dummy_space5,standby_panel]
    });
    if(action =='EDIT'){

        var network_service = result.additional_details.network_service;
        var internal_nw_ser = network_service.internal_nw_ser;
        var external_nw_ser = network_service.external_nw_ser;
       
        if (internal_nw_ser){
            networking_service_lower_panel.disable();
            networking_service_upper_panel.enable();
            from_server_pool_radio.setValue(true);
            external_server_radio.setValue(false);
            var primary_ser_det = internal_nw_ser.PRIMARY;
            var secondary_ser_det = internal_nw_ser.SECONDARY;
            if (primary_ser_det)
                primary_public_Interface.setValue(primary_ser_det.interface);
            if (secondary_ser_det)
                standby_public_Interface.setValue(secondary_ser_det.interface);
        }
        else if (external_nw_ser){
           networking_service_lower_panel.enable();
           networking_service_upper_panel.disable();
           from_server_pool_radio.setValue(false);
           external_server_radio.setValue(true);
            server.setValue(external_nw_ser.server);
            user.setValue(external_nw_ser.username);
            password.setValue(external_nw_ser.password);
            sshport.setValue(external_nw_ser.ssh_port);
            publicinterface.setValue(external_nw_ser.interface);
        }
        


    }

    var networking_service_inner_panel = new Ext.Panel({
        height:'100%',
        id:"networking_service_inner_panel",
//        layout:"form",
        frame:false,
        width:'100%',
//        autoScroll:true,
        border:false,
        bodyBorder:false,
//        bodyStyle:'padding:5px 5px 5px 5px',
//        buttonAlign : 'center',
//        tbar:[tlabel_template],
        items:[networking_service_desc,dummy_space1,from_server_pool_radio,dummy_space6,networking_service_upper_panel,external_server_radio,dummy_space4,networking_service_lower_panel],
        listeners: {
            beforerender : function(cmp) {
                if(action=='ADD'){
                from_server_pool_radio.setValue(true);
//                primary_public_Interface.setValue(primary_ser_det.interface);
            }

            }
        }
    });


    var networking_service_outer_panel = new Ext.Panel({
        border:false,
        id:"panel8",
        layout:"form",
        width:'100%',
        height:'100%',
        frame:false,
//        labelWidth:220,
//        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[networking_service_inner_panel]
    });
    
    return networking_service_outer_panel;
}

function EditRegionPanel(ew,reg_grid,rgrecord)
{
    var type='';
    var label_nreg=new Ext.form.Label({
        html:'<div>'+_("select the region and enter appropriate values to the other fields")+'<br/></div><br/>'
    });
    var nreg_store = new Ext.data.JsonStore({
        url: '/cloud_provider/get_all_lookup_regions?provider_type='+type,
        root: 'rows',
        fields: ['id','region', 'end_point','cloud_provider_type_id'],
        successProperty:'success'

    });
    nreg_store.load();

    var ur;
    var nreg_combo=new Ext.form.ComboBox({
        fieldLabel: _('区域'),
        allowBlank:false,
        width: 190,
        store:nreg_store,
        id:'nreg_combo',
        forceSelection: true,
        triggerAction:'all',
        emptyText :_("选择"),
        minListWidth:50,
        displayField:'region',
        valueField:'id',
        value: rgrecord.get('region'),
        mode:'local'
        ,listeners:{
            select :function(){
                for(var i=0;i<nreg_combo.getStore().getCount();i++){
                    if(nreg_combo.getValue()==nreg_combo.getStore().getAt(i).get('id')){
                        ur=nreg_combo.getStore().getAt(i).get('end_point');
                        region_url.setValue(ur);
                    }
                }

            }

        }
    });


    var regionname=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'region_name',
        id: 'region_name',
        width: 150,
        value:rgrecord.get('name'),
        allowBlank:false
    });
    var reg_description=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'region_description',
        id: 'region_description',
        value:rgrecord.get('description'),
        width: 150,
        allowBlank:false
    });
    var region_url=new Ext.form.TextField({
        fieldLabel: _('End Point'),
        name: 'region_url',
        id: 'region_url',
        value:rgrecord.get('end_point'),
        width: 200,
        editable:false,
        allowBlank:false
    });


    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                var selections=nreg_combo.getValue();

            if(selections.length==0||regionname.getValue()==""||reg_description.getValue()==""||region_url.getValue()==""){
                Ext.MessageBox.alert(_('错误'), _('请至少选择一列.'));
                return;
            }
            else{
                    for(var i=0;i<nreg_store.getCount();i++){
                        if(selections==nreg_store.getAt(i).get('id')){
                            rgrecord.set('id',nreg_store.getAt(i).get('id'));
                            rgrecord.set('region',nreg_store.getAt(i).get('region'));
                            rgrecord.set('name',regionname.getValue());
                            rgrecord.set('description',reg_description.getValue());
                            rgrecord.set('end_point',region_url.getValue());
                            rgrecord.set('cloud_provider_type_id',nreg_store.getAt(i).get('cloud_provider_type_id'));
                            rgrecord.commit();
                            ew.close();


                        }
                        else
                            {
                                ew.close();
                            }
                    }
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
                ew.close()
            }
        }
     });


    var region_panel = new Ext.Panel({
        height:240,
        id:"new_region_panel",
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
        items:[label_nreg,nreg_combo,regionname,reg_description,region_url]
    });
    var region_details_panel=new Ext.Panel({
        id:"nrppanel1",
        layout:"form",
        width:340,
        cls: 'whitebackground',
        //cls: 'whitebackground paneltopborder',
        height:250,
        frame:false,
        labelWidth:220,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[region_panel]
    });

    return region_details_panel;
}

function NewRegionPanel(w,reg_grid )
{
    var type='';
    var label_nreg=new Ext.form.Label({
        html:'<div>'+_("select the region and enter appropriate values to the other fields")+'<br/></div><br/>'
    });
    var nreg_store = new Ext.data.JsonStore({
        url: '/cloud_provider/get_all_lookup_regions?provider_type='+type,
        root: 'rows',
        fields: ['id','region', 'end_point','cloud_provider_type_id'],
        successProperty:'success'

    });
    nreg_store.load();

    var ur;
    var nreg_combo=new Ext.form.ComboBox({
        fieldLabel: _('区域'),
        allowBlank:false,
        width: 190,
        store:nreg_store,
        id:'nreg_combo',
        forceSelection: true,
        triggerAction:'all',
        emptyText :_("选择"),
        minListWidth:50,
        displayField:'region',
        valueField:'id',
        mode:'local'
        ,listeners:{
            select :function(){
                for(var i=0;i<nreg_combo.getStore().getCount();i++){
                    if(nreg_combo.getValue()==nreg_combo.getStore().getAt(i).get('id')){
                        ur=nreg_combo.getStore().getAt(i).get('end_point');
                        region_url.setValue(ur);
                    }
                }

            }

        }
    });

    var region=new Ext.form.TextField({
        fieldLabel: _('区域'),
        name: 'region',
        id: 'region',
        width: 150,
        allowBlank:false
    });


    var regionname=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'region_name',
        id: 'region_name',
        width: 150,
        allowBlank:false
    });
    var reg_description=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'region_description',
        id: 'region_description',
        width: 150,
        allowBlank:false
    });
    var region_url=new Ext.form.TextField({
        fieldLabel: _('End Point'),
        name: 'region_url',
        id: 'region_url',
//        value:ur,
        width: 200,
        editable:false,
        allowBlank:false
    });


    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                var selections=nreg_combo.getValue();

            if(regionname.getValue()==""||regionname.getValue()==""||reg_description.getValue()==""||region_url.getValue()==""){
                Ext.MessageBox.alert(_('错误'), _('请用适当的值填充.'));
                return;
            }
            else
                {


                     var rep_rec = Ext.data.Record.create([
                    {
                        name: 'id',
                        type: 'string'
                    },
                    {
                        name: 'region',
                        type: 'string'
                    },
                    {
                        name: 'name',
                        type: 'string'
                    },
                    {
                        name: 'description',
                        type: 'string'
                    },
                    {
                        name: 'end_point',
                        type: 'string'
                    },
                    {
                        name: 'cloud_provider_type_id',
                        type: 'string'
                    },
                    {
                        name: 'template_id',
                        type: 'string'
                    },
                    {
                        name: 'zone_name',
                        type: 'string'
                    },
                    {
                        name: 'zone_list',
                        type: 'string'
                    }
                    ]);
                    for(var i=0;i<nreg_store.getCount();i++)
                    {

                        if(selections==nreg_store.getAt(i).get('id')){

                           var new_entry=new rep_rec({
                               id:"",
                               region:region.getValue(),
                               name:regionname.getValue(),
                               description:reg_description.getValue(),
                               end_point:region_url.getValue(),
                               cloud_provider_type_id:"",
                               template_id:"",
                               zone_name:"",
                               zone_list:""
                           });

                           reg_grid.getStore().insert(0,new_entry);
                           w.close();
                        }
                    }
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
                w.close()
            }
        }
     });


    var region_panel = new Ext.Panel({
        height:240,
        id:"new_region_panel",
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
        items:[label_nreg,region,regionname,reg_description,region_url]
    });
    var region_details_panel=new Ext.Panel({
        id:"nrppanel1",
        layout:"form",
        width:340,
        cls: 'whitebackground',
        //cls: 'whitebackground paneltopborder',
        height:250,
        frame:false,
        labelWidth:220,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[region_panel]
    });

    return region_details_panel;





}


function AddRegionZones(nw,rname,zone_name,zone_list,record)
{
    var selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });

    var zlabel_addzone=new Ext.form.Label({
        html:'<div>'+_("区域  :"+rname)+'<br/></div><br/>'
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
                        var selections=add_reg_grid .getSelections();
                        if(selections.length==0)
                        {
                            Ext.MessageBox.alert(_('错误'), _('请用适当的值填充.'));
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
        //url: '/cloud_provider/get_all_lookup_zones?region_id='+id+'&provider_type='+type,
        root: 'rows',
        fields: ['id','name','details','state','region'],
        successProperty:'success'
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
        },
        {//cms(csep) zone_id
            name: 'zone_id',
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
            {//cms(csep) zone id
                header   : 'zone_id',
                width    : 150,
                sortable : true,
                dataIndex: 'zone_id',
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
               region:zone_list[i].regionName,
               zone_id:zone_list[i].zone_id//cms(csep) zone_id
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

function create_template_panel()
{
    var tlabel_template=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("模板类别")+'<br/></div>'
    });

//     var refresh_button= new Ext.Button({
//        id: 'refresh',
//        text: _('Refresh'),
//        icon:'icons/refresh.png',
//        cls:'x-btn-text-icon',
//        listeners: {
//        }
//    });

    var add_button= new Ext.Button({
        id: 'add',
        text: _('新建'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn)
            {
                var w=new Ext.Window({
                        title :_('模板'),
                        width :350,
                        height:270,
                        modal : true,
                        resizable : false
                    });
                    var p = NewTemplatePanel(w);
                    w.add(p);
                    w.show();
            }
//              click: function(btn)
//            {
//                var nw=new Ext.Window({
//                        title :_('Avail Region Zones'),
//                        width :400,
//                        height:400,
//                        modal : true,
//                        resizable : false
//                    });
//                    var np = AddRegionZones(nw);
//                    nw.add(np);
//                    nw.show();
//            }

        }
    });

    var substract_button= new Ext.Button({
        id: 'substract',
        text: _('移除'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
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



    var store = new Ext.data.JsonStore({
        url: '/cloud_provider/get_all_regions?',
        root: 'rows',
        fields: ['id','region', 'end_point'],
        successProperty:'success'
//        listeners:{
//            loadexception:function(obj,opts,res,e){
//                var store_response=Ext.util.JSON.decode(res.responseText);
//                Ext.MessageBox.alert(_("Error"),store_response.msg);
//            }
//        }
    });

     var temp_grid = new Ext.grid.GridPanel({
        store: store,
        columns: [
            {
                id       :'Name',
                header   : 'ID',
                width    : 120,
                sortable : true,
                dataIndex: 'id'
            },
            {
                header   : '模板',
                width    : 200,
                sortable : true,
                dataIndex: 'region'
            },
            {
                header   : '可用',
                width    : 140,
                sortable : true,
                //renderer : change,
                dataIndex: 'end_point'
            }
//
            ],


        stripeRows: true,

        height: 350,
        width: 460,
tbar:[{
            xtype: 'tbfill'
             },add_button,substract_button,edit_button]
    });
    var template_panel = new Ext.Panel({
        height:415,
        id:"template_panel",
        layout:"form",
        frame:false,
        width:465,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        //items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],
        tbar:[tlabel_template],
        items:[temp_grid]
    });

    var template_details_panel=new Ext.Panel({
         border:false,
        id:"panel2",
        layout:"form",
        width:465,
        //cls: 'whitebackground paneltopborder',
        height:420,
        frame:false,
        labelWidth:220,
        cls: 'whitebackground',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[template_panel]
    });

    return template_details_panel;
}


function NewTemplatePanel(w)
{



    var tlabel_cmnttemplate=new Ext.form.Label({
        html:'<div>'+_("请选择适当的模板")+'<br/></div><br/>'
    });


    var tlabel_addtemplate=new Ext.form.Label({
        html:'<div>'+_("区域  :"+rnme)+'<br/></div><br/>'
    });


    var templatename=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'template_name',
        id: 'template_name',
        width: 150,
        allowBlank:false
    });
    var tmp_description=new Ext.form.TextField({
        fieldLabel: _('说明'),
        name: 'template_description',
        id: 'template_description',
        width: 150,
        allowBlank:false
    });
    var tmp_url=new Ext.form.TextField({
        fieldLabel: _('URL'),
        name: 'template_url',
        id: 'template_url',
        width: 200,
        allowBlank:false
    });


    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(tmp_url.getValue()==tmp_description.getValue()){

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
                w.close()
            }
        }
     });


 var template_panel = new Ext.Panel({
        height:240,
        id:"template_panel",
        layout:"form",
        frame:false,
        width:340,
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        buttonAlign : 'center',
        //items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],
        bbar:[{
            xtype: 'tbfill'
        },button_ok,button_cancel],
        items:[templatename,tmp_description,tmp_url]
    });
    var template_details_panel=new Ext.Panel({
        id:"tdpanel1",
        layout:"form",
        width:345,
        cls: 'whitebackground',
        //cls: 'whitebackground paneltopborder',
        height:250,
        frame:false,
        labelWidth:220,
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[template_panel]
    });


    return template_details_panel;





}

function AddTemplates(tw,rnme,temp_id,temp_list,trecord, action)
{
    var tselmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });

     var tlabel_tmpnws=new Ext.form.Label({
        html:'<div>'+_("在此区域的可用模板.")+'<br/></div>'
    });

    var tlabel_addtemplate=new Ext.form.Label({
        html:'<div>'+_("区域  :"+rnme)+'<br/></div><br/>'
    });



    var tbutton_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
                     click: function(btn) {

                                //get selected records
                                var tmpselections=add_tmp_grid.getSelections();
                                if(tmpselections.length==0)
                                {
                                    Ext.MessageBox.alert(_('错误'), _('请至少选择一列.'));
                                    return;
                                }

                                //get all non selected records
                                var non_selected_records = get_non_selected_records_from_grid(add_tmp_grid, 'id')
                                var non_selected_temp_ids = non_selected_records['attributes'];
//                                alert("----non_selected_temp_ids------"+non_selected_temp_ids.join(","));


                                // In 'add_tmp_grid' showing templates getting from Cloud (Templates available in Cloud).
                                // Get ami/emi id of all selected templates and make a comma seperated string.
                                var trec=""
                                for (var i=0;i<=tmpselections.length-1;i++)
                                {
                                      trec+=((i==0)?"":",")+tmpselections[i].get('id');
                                }

                                // get id(image_id) of kernel and ramdisk, we want to save it even if do not displaying.
                                for(var m=temp_list.length-1;m>=0;m--){
                                    //Select all available Kernel(aki) and Ramdisk images (ari) for save in DB, 'false' means it is not a machine image.
                                     if(temp_list[m].state==false){ 
                                         trec+=((m==0)?"":",")+temp_list[m].id;
                                     }
                                }

//                                alert("----trec----"+trec);
                                // 'trec' contain image_id of templates selected from 'add_tmp_grid' plus image_id of all kernal and ramdisk under this region.
                                var temp_ids_dict = {};
                                temp_ids_dict['non_selected_temp_ids'] = non_selected_temp_ids;
                                temp_ids_dict['selected_temp_ids'] = trec;
                                trecord.set('temp_id', "");
                                trecord.set('temp_id', temp_ids_dict);
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

     var tbutton_template=new Ext.Button({
        name: 'template',
        id: 'template',
        text:_('公共模板'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var ctw=new Ext.Window({
                    title :_('选择公共模板'),
                    width :800,
                    height:400,
                    modal : true,
                    resizable : false
                });
               var custom_template =customTemplate(ctw,add_tmp_grid,rnme);
               ctw.add(custom_template);
               ctw.show();
                
            }
        }
    });

//    var refresh_button= new Ext.Button({
//        id: 'refresh',
//        text: _('Refresh'),
//        icon:'icons/refresh.png',
//        cls:'x-btn-text-icon',
//        listeners: {
//        }
//    });

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
            'type','id','architecture', 'visibility', 'state']
//        data:main_array

     });


//    var temp_store = new Ext.data.JsonStore({
//        url: '/cloud_provider/get_all_lookup_templates?region_id='+id+'&provider_type='+type,
//        root: 'rows',
//        fields: ['name','description','root_device_name','root_device_type','owner_alias',
//            'kernel_id','ramdisk_id','platform','state','location','item','is_public','ownerId',
//            'type','id','architecture','state'],
//        successProperty:'success',
//        listeners:{
////            load:function()
////             {
////                 if(template_ids!=null){
////                     var tid=template_ids.split(",");
////                     for(var i=0;i<tid.length;i++){
////                         for(var j=0;j<add_tmp_grid.getStore().getCount();j++){
////                             if(tid[i]==add_tmp_grid.getStore().getAt(j).get('id')){
////                                 add_tmp_grid.getSelectionModel().selectRow(j,true);
////                                 break;
////                             }
////
////                         }
////                     }
////                 }
////             }
//         }
//     });




//    temp_store.load();


    var temp_search_by_name = new Ext.form.TextField({
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


    var select_template_type = new Ext.form.ComboBox({
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
    
    select_template_type.setValue('All');


     var dummy_space_temp=new Ext.form.Label({
         html:_('&nbsp;<div style="width:25px"/>')
    });

     //'add_tmp_grid' contain all templates available in cloud(loading directly from Cloud)
     var add_tmp_grid = new Ext.grid.GridPanel({
        store: temp_store,
        selModel:tselmodel,
        autoExpandColumn:11,
        autoExpandMax:400,
        autoExpandMin:300,
        enableHdMenu:false,
        columns: [

            {

                header   : '名称',
                width    : 170,
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
                width    : 100,
                sortable : true,
                dataIndex: 'platform'               

            },
            {
                header   : '状态',
                width    : 100,
                sortable : true,
                dataIndex: 'state',
                hidden:true

            },
            {
                header   : '资源',
                width    : 370,
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
                header   : '编号',
                width    : 230,
                sortable : true,
                dataIndex: 'id',
                hidden:true

            },
            {
                header   : '架构',
                width    : 90,
                sortable : true,
                dataIndex: 'architecture'


            },{

                header   : 'visibility',
                width    : 90,
                sortable : true,
                dataIndex: 'visibility',
                hidden :true
           },
            {

                header   : '状态',
                width    : 90,
                sortable : true,
                dataIndex: 'state',
                hidden :true
           },
            tselmodel
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

        height: 285,
        width: 775,
        tbar:[{xtype: 'tbfill'}, '搜索(按名称): ',temp_search_by_name, dummy_space_temp, select_template_type, tbutton_template]
     });


    var mark_selected_templates = function mark_sel_templates(){
                 var tn=temp_id.split(",");
//                 alert("----mmm-------"+tn);
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

//               var new_tentry=new temp_rec({
//               name:temp_list[i].name,
//               description:temp_list[i].description,
//               root_device_name:temp_list[i].root_device_name,
//               root_device_type:temp_list[i].root_device_type,
//               owner_alias:temp_list[i].owner_alias,
//               kernel_id:temp_list[i].kernel_id,
//               ramdisk_id:temp_list[i].ramdisk_id,
//               platform:temp_list[i].platform,
//               state:temp_list[i].state,
//               location:temp_list[i].location,
//               item:temp_list[i].item,
//               is_public:temp_list[i].is_public,
//               ownerId:temp_list[i].ownerId,
//               type:temp_list[i].type,
//               id:temp_list[i].id,
//               architecture:temp_list[i].architecture,
//               state:temp_list[i].state
//           });


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
             ch_array.push(temp_list[i].state);             
//           add_tmp_grid.getStore().insert(0,new_tentry);
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

function customTemplate(ctw,add_tmp_grid,rnme)
{
    var tlabel_addtemplate=new Ext.form.Label({
        html:'<div>'+"允许你添加公共模板在Amazon使用."+'<br/></div><br/>'
    });

    var temp_store1 = new Ext.data.SimpleStore({
        fields: ['name','description','root_device_name','root_device_type','owner_alias',
        'kernel_id','ramdisk_id','platform','state','location','item','is_public','ownerId',
        'type','id','architecture','state']
    //        data:main_array

    });
        
    var ctbutton_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                var custom_tmp_stor=custom_tmp_grid.getStore();
                var customtemp_rec_count=custom_tmp_grid.getStore().getCount();


                var custom_tmp_selections=custom_tmp_grid.getSelections();
                if(custom_tmp_selections.length==0){
                    Ext.MessageBox.alert(_('错误'), _('请至少选择一列.'));
                    return;
                }
                else
                {
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

                   for (var i=0;i<=custom_tmp_selections.length-1;i++){
                        var temp_new_entry=new temp_rec({
                            name:custom_tmp_selections[i].get('name'),
                            description:custom_tmp_selections[i].get('description'),
                            root_device_name:custom_tmp_selections[i].get('root_device_name'),
                            root_device_type:custom_tmp_selections[i].get('root_device_type'),
                            owner_alias:custom_tmp_selections[i].get('owner_alias'),
                            kernel_id:custom_tmp_selections[i].get('kernel_id'),
                            ramdisk_id:custom_tmp_selections[i].get('ramdisk_id'),
                            platform:custom_tmp_selections[i].get('platform'),
                            state:custom_tmp_selections[i].get('state'),
                            location:custom_tmp_selections[i].get('location'),
                            item:custom_tmp_selections[i].get('item'),
                            is_public:custom_tmp_selections[i].get('is_public'),
                            ownerId:custom_tmp_selections[i].get('ownerId'),
                            type:custom_tmp_selections[i].get('type'),
                            id:custom_tmp_selections[i].get('id'),
                            architecture:custom_tmp_selections[i].get('architecture'),
                            state:custom_tmp_selections[i].get('state')

                        });
                        add_tmp_grid.getStore().insert(0,temp_new_entry);
                        add_tmp_grid.getSelectionModel().selectRow(0, true);
                        
                    }
                    ctw.close();
               }
                
            }
        }
    });
    var ctbutton_cancel=new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                ctw.close();

            }
        }
    });

     var ctbutton_search=new Ext.Button({
        name: 'search',
        id: 'ctsearch',
        text:_('搜索'),
        icon:'icons/search.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var egitems=Ext.getCmp('panel0').items.get('general_panel').items;
                var access_infos=new Object();
                access_infos['endpoint']=egitems.get('endpoint').getValue();
                access_infos['port']=egitems.get('port').getValue();
                access_infos['access_key']=egitems.get('access_key_id').getValue();
                access_infos['secret_access_key']=egitems.get('secret_access_key').getValue();
                access_infos['path']=egitems.get('path').getValue();
                access_infos['region']=rnme;

                var desc = temp_search_by_desc.getValue();

                
                Ext.MessageBox.show({
                    title:_('请稍候...'),
                    msg: _('请稍候...'),
                    width:300,
                    wait:true,
                    waitConfig: {
                        interval:200
                    }
                });

                var access_info_json= Ext.util.JSON.encode({
                    "AccessInfo":access_infos
                });
                var url='/cloud_provider/search_template?description='+desc+'&access_info='+access_info_json;

                var ajaxReq=ajaxRequest(url,0,"POST",true);
                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            Ext.MessageBox.hide();
                            var temp_list = response.templates;

                            var main_array =  new Array();
                            ///// anonymous function /////
                            (function(){
                                for(var i=temp_list.length-1;i>=0;i--){

                                    var ch_array = new Array();

                                    //               var new_tentry=new temp_rec({
                                    //               name:temp_list[i].name,
                                    //               description:temp_list[i].description,
                                    //               root_device_name:temp_list[i].root_device_name,
                                    //               root_device_type:temp_list[i].root_device_type,
                                    //               owner_alias:temp_list[i].owner_alias,
                                    //               kernel_id:temp_list[i].kernel_id,
                                    //               ramdisk_id:temp_list[i].ramdisk_id,
                                    //               platform:temp_list[i].platform,
                                    //               state:temp_list[i].state,
                                    //               location:temp_list[i].location,
                                    //               item:temp_list[i].item,
                                    //               is_public:temp_list[i].is_public,
                                    //               ownerId:temp_list[i].ownerId,
                                    //               type:temp_list[i].type,
                                    //               id:temp_list[i].id,
                                    //               architecture:temp_list[i].architecture,
                                    //               state:temp_list[i].state
                                    //           });


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
                                        ch_array.push(temp_list[i].state);
                                        //           add_tmp_grid.getStore().insert(0,new_tentry);
                                        main_array.push(ch_array);
                                    }

                                }

                                temp_store1.loadData(main_array);

//                                ///mark selected templates//
//                                (function(){
//                                    mark_selected_templates();
//                                }).defer(25);

                            }).defer(25);

                        } else{
                            Ext.MessageBox.alert(_("失败") ,response.msg);
                        }
                    },
                    failure: function(xhr){
                        tlabel_wait.hide();
                        Ext.MessageBox.alert( _("失败") , xhr.statusText);
                    }
                });

            }
        }
    });
    var tselmodel1=new Ext.grid.CheckboxSelectionModel({
        singleSelect:false
    });

    var temp_search_by_desc = new Ext.form.TextField({
        fieldLabel: _('说明: '),
        name: 'Description',
        id: 'Description',
        allowBlank:true
    });

    var custom_tmp_grid = new Ext.grid.GridPanel({
        store: temp_store1,
        selModel:tselmodel1,
        autoExpandColumn:11,
        autoExpandMax:400,
        autoExpandMin:300,
        enableHdMenu:false,
        columns: [

        {

            header   : '名称',
            width    : 170,
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
            width    : 100,
            sortable : true,
            dataIndex: 'platform'

        },
        {
            header   : '状态',
            width    : 100,
            sortable : true,
            dataIndex: 'state',
            hidden:true

        },
        {
            header   : '资源',
            width    : 370,
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
            header   : '编号',
            width    : 230,
            sortable : true,
            dataIndex: 'id',
            hidden:true

        },
        {
            header   : '架构',
            width    : 90,
            sortable : true,
            dataIndex: 'architecture'


        },{

            header   : '状态',
            width    : 90,
            sortable : true,
            dataIndex: 'state',
            hidden :true


        },
        tselmodel1
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

        height: 290,
        width: 775,
        tbar:["Description : ",temp_search_by_desc,{
            xtype: 'tbfill'
        },ctbutton_search]
    });

    var customtmp_panel = new Ext.Panel({
        height:370,
        id:"customtmp_panel",
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
        },ctbutton_ok,ctbutton_cancel],
        items:[tlabel_addtemplate, custom_tmp_grid]
    });

    var customtmp_details_panel=new Ext.Panel({
        id:"customtmp_details_panel",
        layout:"form",
        width:790,
        //cls: 'whitebackground paneltopborder',
        height:380,
        frame:false,
        labelWidth:220,
        cls: 'whitebackground',
        bodyStyle:'border-top:1px solid #AEB2BA;',
        items:[customtmp_panel]
    });


    return customtmp_details_panel;

}

function create_service_panel(type)
{

     var selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });

    var tlabel_service=new Ext.form.Label({
       html:'<div class="toolbar_hdg">'+_("实例类型")+'<br/></div>'
    });

     var tlabel_servicenws=new Ext.form.Label({
        html:'<div>'+_("请选择实例，将做为stackone "+stackone.constants.IAAS+"的一部分.")+'<br/></div>'
    });

     var ser_store = new Ext.data.JsonStore({
        url: '/cloud_provider/get_all_lookup_service_offerings?provider_type='+type,
        root: 'rows',
        fields: ['id','name','description','platform', 'cpu','memory','storage','cname','cid'],
        successProperty:'success'
//        listeners:{
//            loadexception:function(obj,opts,res,e){
//                var store_response=Ext.util.JSON.decode(res.responseText);
//                Ext.MessageBox.alert(_("Error"),store_response.msg);
//            }
//        }
    });

     var ser_grid = new Ext.grid.GridPanel({
        store: ser_store,
        enableHdMenu:false,
        selModel:selmodel,
        id:'ser_grid',
        columns: [
            {
                id       :'Id',
                header   : 'Id',
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
                header   : '说明',
                width    : 105,
                sortable : true,
                dataIndex: 'description',
                hidden:'true'
            },
            {
                header   : '平台',
                width    : 55,
                sortable : true,
                dataIndex: 'platform',
                align : 'right'

            },
            {
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
//            {
//                header   : 'End Point',
//                width    : 100,
//                sortable : true,
//                //renderer : change,
//                dataIndex: 'end_point'
//            }
//
            ],

        autoExpandColumn:2,
        stripeRows: true,
        frame:false,
        height: 290,
        width: 462,
        tbar:['',new Ext.form.Label({}),{
            xtype: 'tbfill'
             }]
     });

      var advance_option_label=new Ext.form.Label({
        html:'<div style="" class="boldlabelheading"><br/></div>'
    })


//      var ser_store1 = new Ext.data.JsonStore({
//        url: '/cloud_provider/get_all_regions?',
//        root: 'rows',
//        fields: ['id','region', 'end_point'],
//        successProperty:'success'
////        listeners:{
////            loadexception:function(obj,opts,res,e){
////                var store_response=Ext.util.JSON.decode(res.responseText);
////                Ext.MessageBox.alert(_("Error"),store_response.msg);
////            }
////        }
//    });

//     var ser_grid1 = new Ext.grid.GridPanel({
////        text: "hghgh",
//        store:ser_store1,
//        enableHdMenu:false,
////        title :"Storage Type",
//        header:true,
//        columns: [
//            {
//                id       :'id',
//                header   : 'Name',
//                width    : 175,
//                sortable : true,
//                dataIndex: 'id'
//            },
//            {
//                header   : 'Details',
//                width    : 175,
//                sortable : true,
//                dataIndex: 'region'
//            },
////            {
////                header   : 'End Point',
////                width    : 100,
////                sortable : true,
////                //renderer : change,
////                dataIndex: 'end_point'
////            }
////
//            ],
//
//
//        stripeRows: true,
//
//        height: 110,
//        width: 350,
//        tbar:['Storage Type']
//     });

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
        id:"panel2",
        layout:"form",
        width:470,
        //cls: 'whitebackground paneltopborder',
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


function NewServicePanel(sw,ser_grid)
{
   var type='';
    var label_nser=new Ext.form.Label({
        html:'<div>'+_("Select the appropriate category type for instance type")+'<br/></div><br/>'
    });
    var nser_store = new Ext.data.JsonStore({
        url: '/cloud_provider/get_all_lookup_service_offering_categories?provider_type='+type,
        root: 'rows',
        fields: ['id','name'],
        successProperty:'success'
//        ,listeners:{
//
////            loadexception:function(obj,opts,res,e){//alert(res.responseText);
////                var store_response=Ext.util.JSON.decode(res.responseText);
////                Ext.MessageBox.alert(_("Error"),store_response.msg);
////            }
//        }
    });
    nser_store.load();

    var category_id='category_id';
    var nser_combo=new Ext.form.ComboBox({
        fieldLabel: _('分类'),
        allowBlank:false,
        width: 190,
        store:nser_store,
        id:'nser_combo',
        forceSelection: true,
        triggerAction:'all',
        emptyText :_("选择"),
        minListWidth:50,
        displayField:'name',
        valueField:'id',
        mode:'local',
        listeners:{
            select:function(cmb,rec,indx)
            {
                var cselections=nser_combo.getValue();

                if(cselections.length>0)
                    {
                        var options=new Object();
                        var params=new Object();
                        params[category_id]=cselections;
                        options['params']=params;
                        ngser_store.load(options);
                    }

            }
        }
    });
    var selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });


     var ngser_store = new Ext.data.JsonStore({
        url: '/cloud_provider/get_all_lookup_service_offerings?provider_type='+type,
        root: 'rows',
        fields: ['id','name','description','platform', 'cpu','memory','storage','cname','cid'],
        successProperty:'success'
//        listeners:{
//            loadexception:function(obj,opts,res,e){
//                var store_response=Ext.util.JSON.decode(res.responseText);
//                Ext.MessageBox.alert(_("Error"),store_response.msg);
//            }
//        }
    });

     var nser_grid = new Ext.grid.GridPanel({
        store: ngser_store,
        enableHdMenu:false,
        selModel:selmodel,
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
                width    : 75,
                sortable : true,
                dataIndex: 'name'
            },
            {
                header   : '说明',
                width    : 115,
                sortable : true,
                dataIndex: 'description'
            },
            {
                header   : '平台',
                width    : 80,
                sortable : true,
                dataIndex: 'platform'
            },
            {
                header   : 'CPU',
                width    : 50,
                sortable : true,
                dataIndex: 'cpu'
            },
            {
                header   : '内存',
                width    : 75,
                sortable : true,
                dataIndex: 'memory'
            },
            {
                header   : '存储',
                width    : 70,
                sortable : true,
                dataIndex: 'storage'
            },
            {
                header   : '分类名称',
                width    : 110,
                sortable : true,
                dataIndex: 'cname',
                hidden:'true'
            },
            {
                header   : '分类编号',
                width    : 110,
                sortable : true,
                dataIndex: 'cid',
                hidden:'true'
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

        height: 260,
        width: 495,
        tbar:['Instance Type',new Ext.form.Label({}),{
            xtype: 'tbfill'
             }]
     });



    var save_button= new Ext.Button({
        id: 'save',
        text: _('确定'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
            var nserselections=nser_grid.getSelections();

            if(nserselections.length==0){
                Ext.MessageBox.alert(_('错误'), _('请至少选择一列.'));
                return;
            }
             else
                {





                 var nser_rec = Ext.data.Record.create([
                    {
                        name: 'id',
                        type: 'string'
                    },
                    {
                        name: 'name',
                        type: 'string'
                    },
                    {
                        name: 'description',
                        type: 'string'
                    },
                    {
                        name: 'platform',
                        type: 'string'
                    },
                    {
                        name: 'cpu',
                        type: 'string'
                    },
                    {
                        name: 'memory',
                        type: 'string'
                    },
                    {
                        name: 'storage',
                        type: 'string'
                    },
                    {
                        name: 'cname',
                        type: 'string'
                    },
                    {
                        name: 'cid',
                        type: 'string'
                    }
                    ]);
            for (var i=0;i<=nserselections.length-1;i++){
                var nsernew_entry=new nser_rec({
                    id:nserselections[i].get('id'),
                    name:nserselections[i].get('name'),
                    description:nserselections[i].get('description'),
                    platform:nserselections[i].get('platform'),
                    cpu:nserselections[i].get('cpu'),
                    memory:nserselections[i].get('memory'),
                    storage:nserselections[i].get('storage'),
                    cname:nserselections[i].get('cname'),
                    cid:nserselections[i].get('cid')
                });






                       ser_grid.getStore().insert(0,nsernew_entry);
                       sw.close();
                                }
                }



            }
        }
    });

    var cancel_button= new Ext.Button({
        id: 'cancel',
        text: _('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click:function(btn){
                sw.close();
            }
        }
    });


    var nservice_panel = new Ext.Panel({
        height:340,
        id:"nservice_panel",
        layout:"form",
        frame:false,
        cls: 'whitebackground',
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        //items:[boot_check,kernel, ramdisk,root_device,kernel_args,on_shutdown,on_reboot,on_crash],
        bbar:[{
            xtype: 'tbfill'
        },save_button,cancel_button],
        items:[label_nser,nser_combo,nser_grid]
    });

//    var nservice_details_panel=new Ext.Panel({
//         border:false,
//        id:"panel3",
//        layout:"form",
//        width:345,
//        cls: 'whitebackground',
//        //cls: 'whitebackground paneltopborder',
//        height:265,
//        frame:false,
//        labelWidth:220,
//        bodyStyle:'border-top:1px solid #AEB2BA;',
//        items:[nservice_panel]
//    });
//
//    return nservice_details_panel;

return  nservice_panel;




}

function create_editaccount_panel(type, node, cp_feature){
    //List Accounts
    
    var acc_textbox = new Ext.form.TextField({
        name: 'vdc_desc',
        id: 'acc_id',
        hidden :true,
        width:270,
        labelSeparator:" ",
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {

            }
        }
    });

   
   var newaccount_columnModel = new Ext.grid.ColumnModel([

    {
        header: _("账户"),
        dataIndex: 'name',
        width:100,
        hidden:true
    },
    {
        header: _("账户编号"),
        dataIndex: 'accesskey',
        width:100,
        sortable:true
    },    
    {
        header: _("说明"),
        dataIndex: 'Description',
        width:250,
//        editor: new Ext.form.TextField({
//            allowBlank: false
//        }),
        sortable:true
    },
     {
//        header: _("Account"),
        dataIndex: 'account_details',//accesskey and secret_accesskey
        hidden:true
    }

    ]);


    var prov_selmodel=new Ext.grid.RowSelectionModel({
        singleSelect:true
    });


    var newaccount_store =new Ext.data.SimpleStore({
        fields:['cloud_provider','name','account_details']

    });

    var provider_general=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("账户")+'</div>',
        id:'label_vm'
    });


    var new_button=new Ext.Button({
        id: 'new_accnt',
        text: _('添加'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                
                var w=new Ext.Window({
                    title :_('添加账户'),
                    width :455,
                    height:360,
                    modal : true,
                    resizable : false
                });
                w.add(Create_Accounts(newaccount_grid,"NEW",w,node,type, null, cp_feature));
                w.show();
            
          }
        }
    }) ;


    var remove_button=new Ext.Button({
        id: 'remove_accnt',
        text: _('移除'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                 if(!newaccount_grid.getSelectionModel().getSelected()){
                    Ext.MessageBox.alert(_("错误"),_("请从列表选择一列."));
                    return;
                }//alert(reg_grid.getSelectionModel().getSelected().get('id'));alert(reg_grid.getSelectionModel().getSelections());
                else{
                    var acc_ids="";
                    acc_ids=Ext.getCmp('acc_id').getValue();
                    var rec=newaccount_grid.getSelectionModel().getSelected().get('account_details');
                    rec=Ext.util.JSON.decode(rec);
                    acc_ids+=((acc_ids=="")?"":",")+rec.account_id
                    
                    newaccount_grid.getStore().remove(newaccount_grid.getSelectionModel().getSelected());
                    var acc_textbox=Ext.getCmp('acc_id');
                    acc_textbox.setValue(acc_ids);
//                    alert(Ext.getCmp('acc_id').getValue());
                }

            }
        }
    });

    var edit_button= new Ext.Button({
        id: 'edit_accnt',
        text: _('编辑'),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                var w=new Ext.Window({
                    title :_('编辑账户'),
                    width :455,
                    height:360,
                    modal : true,
                    resizable : false
                });
                var record = newaccount_grid.getSelectionModel().getSelected()
                w.add(Create_Accounts(newaccount_grid,"EDIT",w,node,type, record));
                w.show();
          }
        }
    });

    var newaccount_grid = new Ext.grid.EditorGridPanel({
        store: newaccount_store,
        id: "panel3",
        stripeRows: true,
        colModel:newaccount_columnModel,
        frame:false,
        border: false,
        selModel:prov_selmodel,
        autoExpandColumn:1,
        autoscroll:true,
        height:250,
        width:'100%',
        clicksToEdit:2,
        enableHdMenu:false,
        tbar:[provider_general,{
            xtype: 'tbfill'
        },new_button, edit_button, remove_button, acc_textbox]
    });

return  newaccount_grid;
    
}



function Create_Accounts(grid,mode,win,node,type, record, cp_feature){


    var account_treePanel= new Ext.tree.TreePanel({
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
                process_cloud_panel(vdc_card_panel,account_treePanel,id.substr(4,id.length),"treepanel");
            }
        }
    });

    // root node of tree view
    var rootNode = new Ext.tree.TreeNode({
        text	: 'Root Node',
        draggable: false,
        id		: 'rootnode',
        listeners: {
            expand : function(btn) {
                account_treePanel.getNodeById("node0").select();
            }
        }
    });
    var Account_Node = new Ext.tree.TreeNode({
        text: _('账户'),
        draggable: false,
        id: "nodex",
        icon:'icons/vm-general.png',
        nodeid: "general",
        leaf:false,
        allowDrop : false
       // cls:"labelcolor"
    });
    var acc_conn_status = new Object();
    acc_conn_status["conn_status"] = true;//testt status
    acc_conn_status["tested"] = false;//connection tested
    var account_panel=create_newaccount_panel(type, node, acc_conn_status, cp_feature);
    var acc_rec = Ext.data.Record.create([
    {
        name: 'name',
        type: 'string'
    },
    {
        name: 'accesskey',
        type: 'string'
    },
    {
        name: 'Description',
        type: 'string'
    },
    {
        name: 'account_details'
    }
    ]);

    //// EDIT ////
    if (mode == 'EDIT')
        {
            Ext.getCmp("acc_name").setValue(record.get('name'));
            Ext.getCmp("acc_desc").setValue(record.get('Description'));
            Ext.getCmp("accesskey").setValue(Ext.util.JSON.decode(record.get('account_details'))['accesskey']);
            Ext.getCmp("accesssecretkey").setValue(Ext.util.JSON.decode(record.get('account_details'))['secret_access_key']);
        }

    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('确定'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
//                      param_obj_str+="username:'"+Ext.getCmp("username").getValue()+"',";
                        if (acc_conn_status["tested"] == false){
                            Ext.MessageBox.alert(_("错误"),"提交任务前请先测试连接");
                            return;
                        }
                        else if (acc_conn_status["conn_status"] == false){
                            Ext.MessageBox.alert(_("错误"),"连接失败, 请重新测试连接");
                            return;
                        }

//                    param_obj_str+="";
                        if (mode == 'EDIT')
                            {
                                var accnt_details = Ext.util.JSON.decode(record.get('account_details'));
                                var param_obj_str_edit="{";
                                    param_obj_str_edit+="\"name\":\""+Ext.getCmp("acc_name").getValue()+"\",";
                                    param_obj_str_edit+="\"account_id\":\""+accnt_details['account_id']+"\",";
                                    param_obj_str_edit+="\"desc\":\""+Ext.getCmp("acc_desc").getValue()+"\",";
                                    param_obj_str_edit+="\"provider_id\":\""+node.attributes.id+"\",";
                                    param_obj_str_edit+="\"accesskey\":\""+Ext.getCmp("accesskey").getValue()+"\",";
                                    param_obj_str_edit+="\"secret_access_key\":\""+Ext.getCmp("accesssecretkey").getValue()+"\"";
                                    param_obj_str_edit+="}";

                                record.set('name', Ext.getCmp("acc_name").getValue());
                                record.set('accesskey', Ext.getCmp("accesskey").getValue());
                                record.set('Description', Ext.getCmp("acc_desc").getValue());
                                record.set('account_details', param_obj_str_edit);
                                record.commit();
                            }
                            else{//ADD
//                            if (!Ext.getCmp("cloud_provider").getValue() && !Ext.getCmp("acc_name").getValue()){
//                                Ext.MessageBox.alert( _("Warning") , "Please verify you selected a Cloud Provider and entered Name");
//                                return
//                            }
//                            else{
                                var param_obj_str="{";
                                    param_obj_str+="\"name\":\""+Ext.getCmp("acc_name").getValue()+"\",";
                                    param_obj_str+="\"account_id\":\"\",";
                                    param_obj_str+="\"desc\":\""+Ext.getCmp("acc_desc").getValue()+"\",";
                                    param_obj_str+="\"provider_id\":\""+node.attributes.id+"\",";
                                    param_obj_str+="\"accesskey\":\""+Ext.getCmp("accesskey").getValue()+"\",";
                                    param_obj_str+="\"secret_access_key\":\""+Ext.getCmp("accesssecretkey").getValue()+"\"";
                                    param_obj_str+="}";

                                var r=new acc_rec({
                                        name:Ext.getCmp("acc_name").getValue(),
                                        accesskey:Ext.getCmp("accesskey").getValue(),
                                        Description:Ext.getCmp("acc_desc").getValue(),
                                        account_details:param_obj_str
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


    var vdc_card_panel=new Ext.Panel({
        width:"100%",
        height:320,
        layout:"card",
        id:"vdc_card_panel",
        activeItem:0,
        cls: 'whitebackground',
        border:false,
        bbar:[
        {
            xtype: 'tbfill'
        },button_ok,button_cancel]
        ,items:[account_panel]
    //
    });

    rootNode.appendChild(Account_Node);
//    rootNode.appendChild(Quota_node);
//    rootNode.appendChild(Sevice_Custom);


//    var treeheading=new Ext.form.Label({
//        html:'<br/><br/>'
//    });
//
//    var labeltreehead=new Ext.form.Label({
//        html:'<div class="toolbar_hdg">'+_("Account Management")+'</div>',
//        id:'label_vm'
//    });


//    var side_panel = new Ext.Panel({
//        bodyStyle:'padding:0px 0px 0px 0px',
//        width:150,
//        height:508,
//        id:'side_panel',
//        cls:'westPanel',
////        tbar:[labeltreehead,{
////            xtype: 'tbfill'
////        }],
//        items:[account_treePanel]
//
//    });

    var right_panel=new Ext.Panel({
        id:"right_panel",
        width:448,
        height:520,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        bodyStyle:'padding:5px 5px 5px 5px'
//        items:[change_settings]
    });

    var outerpanel=new Ext.FormPanel({
        width:550,
//        width:750,
        height:430,
        autoEl: {},
        layout: 'column',
//         items:[side_panel,right_panel]
        items:[right_panel]

    });
    right_panel.add(vdc_card_panel);
    account_treePanel.setRootNode(rootNode);


    return outerpanel;

}

function create_newaccount_panel(type, node, acc_conn_status, cp_feature){

    var width=250;
    var labelWidth=80;
//    acc_conn_status = false;

    var access_key_field_label = 'Access Key';
    var secret_access_key_field_label = 'Secret Key';

if(!is_feature_enabled(cp_feature, stackone.constants.CF_ACCOUNT))
    {
        access_key_field_label = 'Account ID';
        secret_access_key_field_label = 'Password';
    }


    var name_textbox=new Ext.form.TextField({
        fieldLabel: _('名称'),
        name: 'acc_name',
        id: 'acc_name',
        labelWidth:labelWidth,
        allowBlank:false,
//        labelStyle: 'font-weight:bold;',
        width:width,
//        labelSeparator:" ",
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
//        labelSeparator:" ",
        listeners:{

        }
    });

//    var username_textbox=new Ext.form.TextField({
//        fieldLabel: _('User Name'),
//        name: 'username',
//        id: 'username',
//        allowBlank:false,
//        labelWidth:labelWidth,
////        labelStyle: 'font-weight:bold;',
//        width:width,
////        labelSeparator:" ",
//        listeners:{
//
//        }
//    });


    var accesskey_textbox=new Ext.form.TextField({
        fieldLabel: _(access_key_field_label),
        name: 'accesskey',
        id: 'accesskey',
        allowBlank:false,
        labelWidth:labelWidth,
//        labelStyle: 'font-weight:bold;',
        width:width,
//        labelSeparator:" ",
        listeners:{

        }
    });


    var accesssecretkey_textbox=new Ext.form.TextField({
        fieldLabel: _(secret_access_key_field_label),
        name: 'accesssecretkey',
        id: 'accesssecretkey',
        inputType:'password',
        allowBlank:false,
        labelWidth:labelWidth,
//        labelStyle: 'font-weight:bold;',
        width:width,
//        labelSeparator:" ",
        listeners:{

        }
    });

    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:80px"/>')
    });

    var dummy_space2=new Ext.form.Label({
        html:_('&nbsp;<div style="width:80px"/>')
    });

    var dummy_space3=new Ext.form.Label({
        html:_('&nbsp;<div style="width:80px"/>')
    });

    var newdummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:80px"/>')
    });


    var tlabel_success=new Ext.form.Label({
        html:'<div ><b>'+_("连接成功")+'</b></div>'
    });

    var tlabel_wait=new Ext.form.Label({
        html:'<div ><b>'+_("正在连接，请稍候...........")+'</b></div>'
    });
    
    tlabel_success.hide();
    tlabel_wait.hide();

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


//    var cloudprovider_store =new Ext.data.JsonStore({
//        url: "/cloud/get_cloud_providers",
//        root: 'info',
//        fields: ['name','value'],
//        successProperty:'success',
//        sortInfo:{
//            field:'name',
//            direction:'ASC'
//        },
//        listeners:{
//            loadexception:function(obj,opts,res,e){
//                var store_response=Ext.util.JSON.decode(res.responseText);
//                Ext.MessageBox.alert(_("Error"),store_response.msg);
//            }
//        }
//    });
//    cloudprovider_store.load();

//    var cloud_provider = new Ext.form.ComboBox({
//        id: 'cloud_provider',
//        fieldLabel: _('Cloud Provider'),
//        allowBlank:false,
//        triggerAction:'all',
//        emptyText :_("Select Cloud Provider"),
//        store:cloudprovider_store,
//        width:width,
//        displayField:'name',
//        editable:false,
//        valueField:'name',
//        labelWidth:labelWidth,
////        labelStyle: 'font-weight:bold;',
//        typeAhead: true,
//        minListWidth:50,
//        labelSeparator:" ",
//        mode:'local',
//        forceSelection: true,
//        selectOnFocus:true
//    });


//    var label_region=new Ext.form.Label({
//        html:'<div class="toolbar_hdg">'+_("Region")+'</div>',
//        id:'label_vm'
//    });
//
//     var region_checkBoxSelMod = new Ext.grid.CheckboxSelectionModel({
//        singleSelect:false
//    });

//    var columnModel = new Ext.grid.ColumnModel([
//        {header: _("Id"), hidden: true, sortable: true, dataIndex: 'id'},
//        {header: _("Name"), width: 120, sortable: true, dataIndex: 'name'},
//        region_checkBoxSelMod
//    ]);


//    var region_GRID =new Ext.grid.GridPanel({
//        store: getallregions_store,
//        colModel:columnModel,
//        id:"region_grid",
//        stripeRows: true,
//        frame:false,
//        border:false,
//        width:'100%',
//        autoExpandColumn:1,
//        height:100,
//        selModel:region_checkBoxSelMod,
//        enableColumnHide:false,
//        tbar:[label_region],
//        listeners: {
//            rowclick: function(g,index,evt){
//
//            }
//
//        }
//    });

    var label_acc=new Ext.form.Label({
        html:'<div>'+_("请输入账户详情.")+'<br/></div><br/>'
    });

    var inform_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="150"><b>账户信息</b></div>'
     });

    var label_account=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("账户")+'</div>',
        id:'label_vm'
    });


    var test_connection_button= new Ext.Button({
        id: 'test_connection_button',
        text: _('测试'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                
                if (!name_textbox.getValue() || !accesskey_textbox.getValue() || !accesssecretkey_textbox.getValue()){
                    Ext.MessageBox.alert(_('错误'), _('请确保你输入的名称和keys是正确的.'));
//                    connect_button.enable();
                }
                else{
                    var access_infos_test_conn=new Object();
                    access_infos_test_conn['provider_id'] = node.attributes.id;
                    access_infos_test_conn['access_key'] = accesskey_textbox.getValue();
                    access_infos_test_conn['secret_access_key'] = accesssecretkey_textbox.getValue();

                    var access_info_json= Ext.util.JSON.encode({
                        "AccessInfo":access_infos_test_conn
                    });
                    
                    var url='/cloud_provider/test_connect?type='+type+'&access_info='+access_info_json;
                    
                    Ext.MessageBox.show({
                    title:_('请稍候...'),
                    msg: _('请稍候...'),
                    width:300,
                    wait:true,
                    waitConfig: {
                        interval:200
                    }
                });

                acc_conn_status["tested"] = true;

                var ajaxReq=ajaxRequest(url,0,"POST",true);
                ajaxReq.request({
                        success: function(xhr) {
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success)
                                {
                                    Ext.MessageBox.hide();
                                    acc_conn_status["conn_status"] = true;
                                    tlabel_success.show();
                                }
                                else{
                                    tlabel_wait.hide();
                                    acc_conn_status["conn_status"] = false;
                                    tlabel_success.hide();
                                    Ext.MessageBox.alert(_("失败") ,response.msg);
                                }
                        },
                        failure: function(xhr){
                            tlabel_wait.hide();
                            Ext.MessageBox.alert( _("失败") , xhr.statusText);
                        }
                    });

                }

            }
        }
    });


     var test_button_panel = new Ext.Panel({
        height:40,
        id:"newgeneral_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        labelWidth:100,
        buttonAlign :'center',
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[ {
                        width: 100,
                        layout:'form',
                        border:false,
                        items:[test_connection_button]
                    },
                    {
                        labelWidth: 50,
                        layout:'form',
                        border:false,
                        items:[tlabel_success]
                    }]
          });


     var account_panel=new Ext.Panel({
        height:400,
        id:"panelx",
        layout:"form",
        frame:false,
        width:'100%',
        cls: 'whitebackground',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        tbar:[label_account],
        items:[label_acc,newdummy_space1,inform_label,dummy_space1,name_textbox,desc_textbox,
            accesskey_textbox,accesssecretkey_textbox,  dummy_space2, dummy_space3,test_button_panel]
    });

    return account_panel;


}


