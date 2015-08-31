/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
var menu_context=new Object();
function getDocumentDimensions() {    
  var myWidth = 0, myHeight = 0;
  if( typeof( window.innerWidth ) == 'number' ) {
    //Non-IE
    myWidth = window.innerWidth;
    myHeight = window.innerHeight;
  } else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
    //IE 6+ in 'standards compliant mode'
    myWidth = document.documentElement.clientWidth;
    myHeight = document.documentElement.clientHeight;
  } else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
    //IE 4 compatible
    myWidth = document.body.clientWidth;
    myHeight = document.body.clientHeight;
  }
//  window.alert( 'Width = ' + myWidth );
//  window.alert( 'Height = ' + myHeight );
    if(document.all){//alert('IE');
        myHeight = myHeight-5;
    }
  var dims=new Array();
  dims.push(myWidth);
  dims.push(myHeight);
  return dims;
}

var centerPanel,leftnav_treePanel;
var tasks_grid;
function dashboardUI(){
    update_ui_manager();    
    var method_map=new Array();
    method_map[stackone.constants.TMP_LIB]='CloudTemplateLibrary';
    method_map[stackone.constants.CLOUD_TMPGRP]='CloudTemplateGroup';
    method_map[stackone.constants.CLOUD_TEMP]='CloudTemplate';
    method_map[stackone.constants.VDC]='vdc';
    method_map[stackone.constants.CLOUD_VM]='vmcloud'
    method_map[stackone.constants.VDC_VM_FOLDER]="vdc_vm_folder";
    
    var dims=getDocumentDimensions();
   
    myHeight = dims[1];   

    var westPanel=new Ext.Panel({
        region:'west',
        width:180,
        height:'100%',
        autoScroll:true,
        split:true,
        layout:"fit",
        defaults: {
            autoScroll:true
        },
        minSize: 50,
        maxSize: 300,
        border:false,
        id:'westPanel',
        cls:'westPanel'
    });

    var V = new Ext.ux.plugin.VisibilityMode({ bubble : false }) ;
    centerPanel=new Ext.TabPanel({
        minTabWidth: 115,
        tabWidth:135,
        activeTab:0,
        border:false,
        id:'centerPanel'
        ,defaults: {
          plugins: V,
          hideMode : 'nosize'
        }
        ,listeners:{
            resize:function(){
                if(centerPanel.rendered){
                    centerPanel.doLayout();
                }
            }
            ,tabchange:function(tabpanel,tab){//alert(tabpanel.isRemoving);
                if(tabpanel.isRemoving==true){
                    return;
                }
                var node=leftnav_treePanel.getSelectionModel().getSelectedNode();
                var nodetype=node.attributes.nodetype;                
                var tabid=tab.getId();
                //vnc console tabs will have id=(console+nodeid)
                 if(tabid.indexOf('console')!=0){
                    //alert(tabid+"===="+nodetype+"===="+node.attributes.id);
                    var method=method_map[nodetype]+"_"+tabid+"_page";//alert(method)
                    eval(method+"(tab,node.attributes.id,node)")
                 }

            }
            ,remove:function(container,component){
            	if (Ext.isIE) {
            	component.rendered =true;
            	container.render(component);
            	}
            	
            }
            ,beforeremove :function(container,component){
            	if (Ext.isIE) {
            	component.rendered =false;
            	}
            }
        }

    });

    var label_entity=new Ext.form.Label({
        html:getHdrMsg('')
    });
    
    var menu_store = new Ext.data.JsonStore({
        //url: '/get_context_menu_items?menu_combo=True',
        root: 'rows',
        fields: ['text', 'value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_( "错误"),store_response.msg);
                }
            }
    });

   
    /*var menu_combo=new Ext.form.ComboBox({
        triggerAction:'all',
        store: menu_store,
        emptyText :_("选择操作"),
        displayField:'text',
        valueField:'value',
        width: 200,
        editable:false,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'menu_group',
        id:'menu_group',
        mode:'local',
        listeners:{
            select:function(combo){
                var menu=new Ext.menu.Item({
                    id:menu_combo.getValue(),
                    tooltip:menu_combo.getRawValue()
                });
                var node=leftnav_treePanel.getSelectionModel().getSelectedNode();

                if(node){
                    handleEvents(node,menu_combo.getValue(),menu);
                }
            }
        }
    });*/

    var northPanel=new Ext.Panel({
        region:'north',
        title: 'North Panel',
        collapsible:false,
        layout:'anchor',
        header:false,
        split:false,
        border:false,
        height: 22,
        id:'northPanel'
    });

    northPanel.add(toolbarPanel());  



   tasks_grid=TasksGrid();
   var southPanel=new Ext.Panel({
        region:'south',
        title: _('任务'),
        collapsible:true,
        layout:'fit',
        header:true,
        split:true,
        border:false,
        defaults: {
            autoScroll:true
        },
        collapsed:false,
        height: 120,
        minSize: 75,
        maxSize: 350,
        id:'southPanel'
        ,tools:[{
            id:'refresh',
            //qtip: 'Refresh form Data',
            // hidden:true,
            handler: function(event, toolEl, panel){
                tasks_grid.getStore().load();
            }
        }]
        ,plugins: new Ext.ux.collapsedPanelTitlePlugin()
    });
    southPanel.add(tasks_grid);




// javascript:showWindow('"+_('Administration')+"',705,470,adminconfig());
     var header_html_link= "<div class='header-container'>";
        header_html_link+= "    <div class='header-left'>";
        header_html_link+= "        <img src='images/stackone_logo.gif' alt='stackone Logo'/>";
        header_html_link+= "    </div>";
        header_html_link+="<div class=header-co>";
    	header_html_link+= "<div class='header-right-bottom'>";
    	//header_html_link+="<p>"+_(edition_string+' '+version)+"</p>";
    	header_html_link+="</div>";
    	
    	if(sub_edition_string){
			header_html_link+= "<div class='header-right-bottom-bottom'>";
			//header_html_link+="<p><font size='1' color='silver'>"+sub_edition_string+"</font></p>";
			header_html_link+="</div>";
    	}
    	header_html_link+="</div>";
    	
        header_html_link+= "    <div class='header-right'>";
        header_html_link+= "        <div class='header-right-left'>";
        //header_html_link+= "           <p>"+_('User')+" : </p><p>"+user_firstname+"</p>";
        header_html_link+= "        </div>";
        header_html_link+= "        <div class='header-right-right'>";
        header_html_link+= "            <ul class='admin-nav-menu'>";
		header_html_link += "           <li class='username'><a href='#' >"
			+ user_firstname + "&nbsp;&nbsp;|&nbsp;&nbsp;</a></li>";

        if (is_cloud_admin=='True')
            header_html_link+= "           <li class='admin'><a href='#' onclick=javascript:showWindow('"+_('选择用户类型')+"',315,130,select_ui_type(is_cloud_admin));>（权限）</a></li>";

        header_html_link+= "         <li class='task'><a href='#' onclick=javascript:showWindow('"+_('审计')+"',740,370,Tasks());>（审计）</a></li>";

        header_html_link+= "         <li class='password'><a href='#' onclick=javascript:showWindow('"+_('密码')+"',400,200,changepass(user_name));>（密码）</a></li>";

       // header_html_link+= "         <li class='license'><a href='#' onclick=javascript:showWindow('"+_('License')+"',500,400,LicenseDialog());></a></li>";
        header_html_link+= "         <li class='logout'><a href='#' onclick=javascript:window.location='/user_logout'>（注销）</a></li>";

        header_html_link+= "         </ul>";
        header_html_link+= "        </div>";
        header_html_link+= "    </div>";

        if(rem_days!="")
        {
         header_html_link+="<div class='header-right-end'>"+_('评估许可剩余'+rem_days+'天！')+"</p></div>";
        }
        header_html_link+= "</div>";

    var headerPanel=new Ext.Panel({
        height:63-30,
        border:false,
        width:"100%",
        id:'headerPanel',
        cls:'headerPanel',
        layout:'column',
        html: header_html_link
    });



    var label_action=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<div class="toolbar_hdg">'+_("操作")+'</div>'
    });

    var titlePanel=new Ext.Panel({
        layout:'fit',
        region:'center',
        split:true,
        margins: '2 2 2 0',
        width:'100%',
        //tbar:[label_entity,{xtype:'tbfill'},label_action,"&nbsp;&nbsp;",menu_combo]
    });

    titlePanel.add(centerPanel);

    var borderPanel = new Ext.Panel({
        width:"100%",
        height:myHeight-60+30,
        layout:'border',
        id:'borderPanel',
        items: [westPanel,titlePanel,southPanel]
        ,monitorResize:true
    });

    var outerPanel = new Ext.Panel({
        border:false,
        width:"100%",
        height:"100%",
        id:'outerPanel',
        items: [headerPanel,borderPanel]
        ,monitorResize:true
        ,listeners:{
            resize:function(){
                var dims=getDocumentDimensions();
                //alert(dims[0]+"---"+dims[1])
                var myWidth = dims[0], myHeight = dims[1];
                if(borderPanel.rendered){
                    borderPanel.setHeight(myHeight-30);
                    borderPanel.doLayout();
                }
            }
        }
    });

    var summaryPanel=new Ext.Panel({
        title   : _('概览'),
        closable: false,
        //autoScroll:true,
        defaults: {
            autoScroll:true
        },
        layout:'fit',
        width:400,
        id:'summary'
        ,listeners:{
            activate:function(panel){
                if(panel.rendered){
                    panel.doLayout();
                }
            }
        }
    });

    var infoPanel=new Ext.Panel({
        title   : _('信息'),
        closable: false,      
        id:'info',
        height:600,
        autoScroll:true,
        defaults: {
            autoScroll:true
        },
        layout:'fit',    
        cls:'westPanel'
        ,listeners:{
            activate:function(panel){
                if(panel.rendered){
                    panel.doLayout();
                }
            }
        }
    });
    
    var configPanel=new Ext.Panel({
        title   : _('配置'),
        closable: false,
        layout  : 'fit',
        id:'config',
        autoScroll:true,
        defaults: {
            autoScroll:true
        }
        ,listeners:{
            activate:function(panel){
                if(panel.rendered){
                    panel.doLayout();
                }
            }
        }
    });

    var backup_history_Panel=new Ext.Panel({
        title   : _('备份'),
        closable: false,
        layout  : 'fit',
        id:'backup_history',
        autoScroll:true,
        defaults: {
            autoScroll:true
        }
        ,listeners:{
            activate:function(panel){
                if(panel.rendered){
                    panel.doLayout();
                }
            }
        }
    });

    var task_Panel=new Ext.Panel({
        title   : _('任务'),
        closable: false,
        layout  : 'fit',
        id:'task_details',
        autoScroll:true,
        defaults: {
            autoScroll:true
        }
        ,listeners:{
            activate:function(panel){
                if(panel.rendered){
                    panel.doLayout();
                }
            }
        }
    });

    var vminfoPanel=new Ext.Panel({
        title   : _('虚拟机'),
        closable: false,
        layout  : 'fit',
        id:'vminfo',
        autoScroll:true,
        defaults: {
            autoScroll:true
        }
        ,listeners:{
            activate:function(panel){
                if(panel.rendered){
                    panel.doLayout();
                }
            }
        }
    });
    var networkingPanel=new Ext.Panel({
        title   : _('网络'),
        closable: false,
        layout  : 'fit',
        id:'networking',
        autoScroll:true,
        defaults: {
            autoScroll:true
        }
        ,listeners:{
            activate:function(panel){
                if(panel.rendered){
                    panel.doLayout();
                }
            }
        }
    });


    var templatesPanel=new Ext.Panel({
        title   : _('模板'),
        closable: false,
        layout  : 'fit',
        id:'templateinfo',
        autoScroll:true,
        defaults: {
            autoScroll:true
        }
        ,listeners:{
            activate:function(panel){
                if(panel.rendered){
                    panel.doLayout();
                }
            }
        }
    });


    leftnav_treePanel = new Ext.tree.TreePanel({
        rootVisible : false,
        useArrows: true,
        autoScroll: true,
        animate: true,
        enableDD: true,
        containerScroll: true,
        border: false,
        el: westPanel.getEl(),
        layout: 'fit',
        cls:'leftnav_treePanel',
        listeners: {
            beforenodedrop: function(e){
                processDrop(e);
                return false;
            }
            ,contextmenu: function(node, e) {
                if (node.attributes.nodetype == stackone.constants.SPECIAL_NODE){

                    return;

                }
                if (node.attributes.nodetype == stackone.constants.CLOUD_TEMP){

                    return;

                }   
                showContextMenu(node, e);
            },beforeexpandnode:function(node){
                if(node.attributes.id!="0" && node.childNodes.length==1){//checking root node node.attributes.id!="0"
                        if(node.childNodes[0].attributes.id=="dummy_node"){
                            node.childNodes[0].getUI().hide();
                            node.fireEvent('click',node);

                        }
                 }
             }
        }
    });

    new Ext.tree.TreeSorter(leftnav_treePanel,{
        folderSort:true,
        dir:'ASC',
        property:"sorttext"
    });

//    leftnav_treePanel.on('restore',function(node,e){
//
//        var iconClass=node.getUI().getIconEl().className;
//        node.getUI().getIconEl().className="x-tree-node-icon loading_icon";
//        var ajaxReq = ajaxRequest(node.attributes.url,0,"GET",true);
//        //checkToolbar(node);
//
//        if(node.attributes.nodetype==stackone.constants.VDC){
//            menu_combo.reset();
//            menu_store.load({
//                params:{
//                    node_id:node.attributes.id,
//                    node_type:node.attributes.nodetype
//                }
//            });
//            (function(){
//                addTabs(centerPanel,[summaryPanel,configPanel,vminfoPanel]);
//                centerPanel.setActiveTab(backup_history_Panel)
//            }).defer(25);
//
//            //getVNCInfo(node.parentNode,node,centerPanel);
//            //updateInfoTab(InfoGrid(node),true);
//            node.getUI().getIconEl().className=iconClass;
//            label_entity.setText(getHdrMsg(node.text),false);
//            return;
//            }
//        });
//
    leftnav_treePanel.on('click',function(node,e){


        var iconClass=node.getUI().getIconEl().className;
        node.getUI().getIconEl().className="x-tree-node-icon loading_icon";
        var ajaxReq = ajaxRequest(node.attributes.url,0,"GET",true);
        //checkToolbar(node);

        if(node.attributes.nodetype==stackone.constants.VDC){
                //menu_combo.reset();
                menu_store.load({
                    params:{
                        node_id:node.attributes.id,
                        node_type:node.attributes.nodetype,
                        cp_type:node.attributes.cp_type
                    }
                });
         }
        else if(node.attributes.nodetype==stackone.constants.CLOUD_VM){
            //menu_combo.reset();
            menu_store.load({
                params:{
                    node_id:node.attributes.id,
                    node_type:node.attributes.nodetype,
                    cp_type:node.attributes.cp_type
                }
            });
        }
        else{
            menu_store.removeAll()
        }
//            (function(){
//                addTabs(centerPanel,[summaryPanel,configPanel]);
//            }).defer(25);
//
//            //getVNCInfo(node.parentNode,node,centerPanel);
//            //updateInfoTab(InfoGrid(node),true);
//            node.getUI().getIconEl().className=iconClass;
//            label_entity.setText(getHdrMsg(node.text),false);

//            return;
//        }
        
    ajaxReq.request({
            success: function(xhr) {
                node.getUI().getIconEl().className=iconClass;              


                var response=Ext.util.JSON.decode(xhr.responseText);
                if(!check_lic(response)){return;}
                if(!response.success){
//                    if(node.attributes.nodetype==stackone.constants.MANAGED_NODE &&
//                            response.msg==_('Server not authenticated.')){
//                        showWindow(_("Credentials for ")+node.text,280,150,credentialsform(node));
//                        return;
//                    }
                    Ext.MessageBox.alert(_("失败"),response.msg);
                    return;
                }
                
//                if(node.attributes.nodetype==stackone.constants.DOMAIN){
//
//                    menu_combo.reset();
//                    menu_store.load({
//                        params:{
//                            node_id:node.attributes.id,
//                            node_type:node.attributes.nodetype
//                        }
//                    });
//
//
//                    addTabs(centerPanel,[summaryPanel,configPanel]);
//                    vminfoPanel.setTitle( _('Configuration'));
//                    node.getUI().getIconEl().className=iconClass;
//                    label_entity.setText(getHdrMsg(node.text),false);
//                }else

                if(node.attributes.nodetype==stackone.constants.TMP_LIB ){

                    addTabs(centerPanel,[summaryPanel]);
                }else if(node.attributes.nodetype==stackone.constants.CLOUD_TMPGRP){

                    addTabs(centerPanel,[summaryPanel]);
                }                                  
                else if(node.attributes.nodetype==stackone.constants.VDC){
                    if(node.attributes.cp_type==stackone.constants.CMS){
                        addTabs(centerPanel,[summaryPanel, vminfoPanel,networkingPanel]);
                    }else{
                       addTabs(centerPanel,[summaryPanel, configPanel, vminfoPanel]);
                    }
                    vminfoPanel.setTitle(_('虚拟机'));
                }
                else if(node.attributes.nodetype==stackone.constants.VDC_VM_FOLDER) {
                   
                    addTabs(centerPanel,[vminfoPanel]);
                    vminfoPanel.setTitle(_('虚拟机'));
                }
                else if(node.attributes.nodetype==stackone.constants.CLOUD_VM) {

                    addTabs(centerPanel,[summaryPanel,configPanel]);

                }

                var r_children=response.nodes;
                var n_children=node.childNodes;
                var new_nodes=get_new_nodes(r_children,node);
                var del_nodes=get_del_nodes(r_children,n_children);
                if(new_nodes.length!=0)
                    appendChildNodes(new_nodes,node);
                if(del_nodes.length!=0)
                    removeNodes(node,del_nodes);
                node.expand();
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("失败") , xhr.statusText);
                node.getUI().getIconEl().className=iconClass;
            }
        });

    });

    var rootNode = new Ext.tree.TreeNode({
        text		: 'Root Node',
        draggable: false,
        id		: '0'
    });

    var ajaxReq=ajaxRequest("/cloud/get_nav_nodes_for_cloud",0,"GET",true);    
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                appendChildNodes(response.nodes,rootNode);
                rootNode.expand();
                get_app_updates();
                check_license_expire();
                if (rootNode.firstChild != null)
                   rootNode.firstChild.fireEvent('click',rootNode.firstChild);
                }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });

    westPanel.add(leftnav_treePanel);

    leftnav_treePanel.setRootNode(rootNode);
    //leftnav_treePanel.render();

    return outerPanel;
}

function appendGrid(summaryPanel,grid){
    if(summaryPanel.items)
        summaryPanel.removeAll(true);
    summaryPanel.add(grid);
    grid.render('summaryPanel');

    summaryPanel.doLayout();
}

function updateInfoTab(child,keepActive){
    var actTab=centerPanel.getActiveTab();
    var infopanel=centerPanel.getItem('infoPanel');
    centerPanel.setActiveTab(infopanel);
    if (infopanel!=null){
        infopanel.removeAll();
        infopanel.add(child);
        infopanel.doLayout();
        if(!keepActive)
            centerPanel.setActiveTab(actTab);
    }
}

function download(node_id,dom_id){
    Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: _('请稍候...'),
        width:300,
        wait:true,
        waitConfig: {
            interval:200
        }
    });
//
    var url="/cloud/download_keypair?vdc_id="+node_id+"&dom_id="+dom_id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                Ext.MessageBox.hide();
                var web_url = response.path + '/cloud_network/get_private_key?vdc_id=' + response.vdc_id + '&acc_id=' + response.acc_id + '&region_id=' + response.region_id + '&key_name=' + response.key_name;
                window.open(web_url, "_parent");
            }else{
                Ext.MessageBox.hide();
                Ext.MessageBox.alert( _("失败") , response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });

}

function cloud_select_view(vdcid,dom){
    var url="/cloud/get_cloud_vm_platform?dom_id="+dom.attributes.id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: _('请稍候...'),
        width:300,
        wait:true,
        waitConfig: {
            interval:200
        }
    });
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                if (response.provider_type!=stackone.constants.CMS){
                    var title = "连接";
                    if (response.key_pair_name){
                        title += " (密钥对: "+response.key_pair_name+")";
                    }
                    showWindow(title,450,260,show_cloud(vdcid,dom,response));
                }
                else{
                    show_cms_cloud(dom);
                }
                Ext.MessageBox.hide();
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
                Ext.MessageBox.hide();
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });

}
function show_cloud(vdcid,dom,response){
    
    var vm_platform=response.vm_platform;
    var key_pair=response.key_pair;

    var OSName="Unknown OS";
    if (navigator.appVersion.indexOf("Win")!=-1) OSName="Windows";
    if (navigator.appVersion.indexOf("Mac")!=-1) OSName="MacOS";
    if (navigator.appVersion.indexOf("X11")!=-1) OSName="UNIX";
    if (navigator.appVersion.indexOf("Linux")!=-1) OSName="Linux";
    
     var klbl=new Ext.form.Label({
         html: _("如果你没有密钥对，请下载密钥对 \n\
             <a href='javascript:download(&quot;"+vdcid+"&quot;,&quot;"+dom.attributes.id+"&quot;)'>下载</a><br/><br/>")
     });

     var default_login=new Ext.form.Radio({
        boxLabel: _('默认用户(Administrator/root)'),
        id:'default_login',
        name:'radio',
        width:"50%",
        hideLabel:true,
        checked:true,
        listeners:{
            check:function(field,checked){
                if(checked){
                    user_login.setValue(false);
                    default_login.setValue(true);
                    user_name.disable();
                }
            }
            }
    });


    var user_login=new Ext.form.Radio({
        boxLabel: _('其他用户:&nbsp;'),
        id:'user_login',
        name:'radio',
        hideLabel:true,
        listeners:{
            check:function(field,checked){
               if(checked){
                    user_login.setValue(true);
                    default_login.setValue(false);
                    user_name.enable();
               }
            }
            }
    });

    var user_name = new Ext.form.TextField({
        hideLabel: true,
        name: 'user_name',
        id: 'user_name',
        width:110,
        labelSeparator:" ",
        allowBlank:true,
        disabled:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {

            }
        }
    });

    var en_des=_("Login to be used for connecting to Virtual Machine.");

    var userheading=new Ext.form.Label({
        html:_('<div class="backgroundcolor" width="120"><b>User</b>\n\
                <img src=icons/information.png onClick="show_desc(&quot;'+escape(en_des)+'&quot;)"/><br/><hr></div>')
    });

     var userpanel=new Ext.FormPanel({
        width:"100%",
        height:"50%",
        autoEl: {},
        layout: 'column',
        items:[default_login,user_login,user_name]

    });

    var loc_des=_("Key Location is directory where the Private key of the key pair is stored. Key FileName is the file name. Typically, on linux platform this will be .pem file and on windows\n\
        this will be .ppk file used by Putty");
    var location=new Ext.form.Label({
        html:_('<div class="backgroundcolor" width="120"><br/><b>Location</b>\n\
                <img src=icons/information.png onClick="show_desc(&quot;'+escape(loc_des)+'&quot;)"/><br/><hr></div>')
    });



     var key_location = new Ext.form.TextField({
        name: 'key_location',
        fieldLabel: _('密钥位置:&nbsp;'),
        id: 'key_location',
        width:200,
        labelSeparator:" ",
        allowBlank:true,
        value:(OSName=="Windows")?"C:\\putty\\cloudkeys\\":"/home/user/.ssh/",
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {

            }
        }
    });

    var key_filename = new Ext.form.TextField({
        name: 'key_filename',
        id: 'key_filename',
        fieldLabel: _('密钥文件名:&nbsp;'),
        width:200,
        labelSeparator:" ",
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {

            }
        }
    });

    var u_panel=new Ext.Panel({
        height:'40%',
        border:false,
        width:'100%',
        labelAlign:'left',
        layout:'form',
        frame:false,
        autoScroll:true,
        labelSeparator:' ',
        id:"u_panel",
        items: [userheading,userpanel]

    });

    var loc_panel=new Ext.Panel({
        height:'40%',
        border:false,
        width:'100%',
        labelAlign:'left',
        layout:'form',
        frame:false,
        autoScroll:true,
        labelSeparator:' ',
        id:"loc_panel",
        items: [location,key_location,key_filename]

    });
    var connect_panel1=new Ext.Panel({
        closable: true,
        height:'100%',
        border:false,
        width:'100%',
        labelAlign:'left',
        layout:'form',
        frame:true,
        autoScroll:true,
        labelSeparator:' ',
        id:"connect_panel1",
        items: [klbl,u_panel,loc_panel]

    });
    key_filename.setValue(key_pair);
    if (vm_platform!=null){
        
       loc_panel.disable();
    }


    var button_ok=new Ext.Button({
        name: 'ok',
        id: 'ok',
        text:_('继续'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var u_name=user_name.getValue();
                if(user_login.getValue()&&u_name==""){
                    Ext.MessageBox.alert( _("失败") , "请输入用户的名称");
                    return;
                }
                setCookie(stackone.constants.DEFAULT_LOGIN,default_login.getValue());
                setCookie(stackone.constants.USER_NAME,u_name);
                setCookie(stackone.constants.KEY_LOCATION,key_location.getValue());
                var key_file=key_filename.getValue();
                cloud_get_command(vdcid,dom,u_name,OSName,key_location.getValue(),key_file,vm_platform);
                closeWindow();
            }

        }
     });
     var cancel= new Ext.Button({
        name: 'cancel',
        id: 'cancel',
        text:_('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow();
            }
        }
    });
    var connect_panel2=new Ext.Panel({
        height:'100%',
        border:true,
        width:'100%',
        labelAlign:'left',
        layout:'form',
        autoScroll:true,
        labelSeparator:' ',
        id:"connect_panel2",
        items:[connect_panel1],
        bbar:[{xtype: 'tbfill'},button_ok,cancel]
    });

    var default_cookie=getCookie(stackone.constants.DEFAULT_LOGIN);
    if (default_cookie!=null && default_cookie!=""){
        if (eval(default_cookie)==true){
            default_login.setValue(true);
        }else{
            user_login.setValue(true);
            var user_name_cookie=getCookie(stackone.constants.USER_NAME);
            if (user_name_cookie!=""){
                user_name.setValue(user_name_cookie);
            }
        }
    }
    var key_loc_cookie=getCookie(stackone.constants.KEY_LOCATION);
    if (key_loc_cookie!=null && key_loc_cookie!="")
        key_location.setValue(key_loc_cookie);

    return connect_panel2;

}
function cloud_get_command(vdcid,dom,user_name,OSName,key_location,key_file,vm_platform){

    var url="/cloud/get_command?node_id="+vdcid+"&dom_id="+dom.attributes.id+"&os_name="+OSName+"&user_name="+user_name;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var cmd=response.cmd;
//                key_location=key_location.replace(/^\s+|\s+$/g,"");
//                key_file=key_file.replace(/^\s+|\s+$/g,"");
                var last_char=key_location.charAt(key_location.length-1);
                var key_pair=null;
                if(vm_platform==null){
                    if (OSName=="Windows"){
                        key_pair=key_location+"\\"+key_file;
                        if(last_char=="\\")
                            key_pair=key_location+key_file;
                    }else{
                        key_pair=key_location+"/"+key_file;
                        if(last_char=="/")
                            key_pair=key_location+key_file;
                    }
                }
                cloud_getCMDInfo(vdcid,dom,cmd,response,OSName,key_pair);
            }else{
                Ext.MessageBox.alert( _("失败") , response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}


function cloud_getCMDInfo(vdcid,dom,cmd,response,OSName,key_pair){

    var consolePanel=centerPanel.getItem('console'+dom.attributes.id);
    if (consolePanel != null ){
        centerPanel.remove(consolePanel);
    }

//    key_pair="'"+key_pair+"'";
//    alert(key_pair);
    cmd=cmd.replace("KEYPAIR",key_pair);
    var applet='<applet code="AppletRunner.class" archive="/jar/SAppletRunner.jar"'+
    ' width="1" height="1">'+
    '<param name="command" value="'+cmd+'">'+
    '</applet>';

//    alert(applet);


    var help=response.info.help;
    var heading=response.info.heading;
    var label_summary=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_(heading)+'</div>'
    });

    var consolePanel_heading=new Ext.Panel({
        autoHeight:true,
        border:true,
        cls:'hideheader',
        width:'75%',
        height: 150,
        frame:false,
        tbar:[label_summary]
    });

    consolePanel=new Ext.Panel({
        title   : dom.text+"&nbsp;&nbsp;&nbsp;",
        closable: true,
        layout  : 'fit',
        id      :'console'+dom.attributes.id,
        html    : "<br/>"+help+"<br/>"+applet,
        bodyStyle:'padding-top:10px;padding-left:10px;padding-right:10px',
        bodyBorder:false
        ,cls:'westPanel'
    });
    consolePanel.add(consolePanel_heading);
    centerPanel.add(consolePanel);
    centerPanel.setActiveTab(consolePanel);

}


function addTabs(prntPanel,childpanels){
    if(prntPanel.items){
        prntPanel.isRemoving=true;
        //prntPanel.removeAll(true);
        prntPanel.items.each(function(tab){
            //vnc console tabs will have id=(console+nodeid)
            if(tab.getId().indexOf('console')!=0){
                prntPanel.remove(tab);
            }
        })
    }
    prntPanel.isRemoving=false;
    for(var i=0;i<childpanels.length;i++){
        prntPanel.insert(i,childpanels[i]);
        //prntPanel.setActiveTab(childpanels[i]);
    }
    if(childpanels.length>0){
        prntPanel.setActiveTab(childpanels[0]);
    }
}

function getHdrMsg(node){
    return '<div class="toolbar_hdg" >'+node+'<div>';
}

function update_ui_manager(){
    var time=page_refresh_interval*1000
    var update_task = {
        run : function() {
            var url="/node/get_updated_entities?user_name="+user_name;
            var ajaxReq = ajaxRequest(url,0,"GET",true);
            ajaxReq.request({
                success: function(xhr) {
//                    alert(xhr.responseText);
                    var response=Ext.util.JSON.decode(xhr.responseText);
                    if(!response.success){
                        Ext.MessageBox.alert(_("失败"),response.msg);
                        return;
                    }
//                    alert(response.update_details.length);
                    var node_ids;
//                    if(eval("response.update_details."+user_name)){
                    if(response.node_ids.length>0){
                        node_ids=response.node_ids;
                        var selected_node=leftnav_treePanel.getSelectionModel().getSelectedNode();
                        for(var i=0;i<=node_ids.length;i++){
                            var node=leftnav_treePanel.getNodeById(node_ids[i]);
                            if(node!=null){
//                                if(node.isExpanded()){
                                    update_expanded_node(node);
//                                }

                                if(node.attributes.nodetype===stackone.constants.VDC){
                                    var children=node.childNodes;
                                    if (children != null){
                                        for(var j=0;j<children.length;j++){
                                            var child = children[j];
                                            if(child.attributes.nodetype===stackone.constants.VDC_VM_FOLDER){
                                                update_expanded_node(child);
                                            }
                                        }
                                    }
                                }
                                if(node.parentNode != null && node.parentNode != undefined
                                    && node_ids.indexOf(node.parentNode.attributes.id)<0){
                                    //will come here if the entity is deleted in the backend
                                    //as we will not be able to find the parent of deleted entity
                                    update_expanded_node(node.parentNode);
                                } else {
                                    //if it is a deleted entity , don't try to update the UI
                                    //as it will throw errors
                                    if(selected_node!=null && selected_node.attributes.id==node_ids[i]){
                                        //selected_node.fireEvent('click',selected_node);
                                        var tab=centerPanel.getActiveTab();
                                        //alert(tab.getId());
                                        centerPanel.fireEvent('tabchange',centerPanel,tab);
                                    }
                                }
                            }
                        }
                    }
                },
                failure: function(xhr){
                    Ext.MessageBox.alert( _("失败") , xhr.statusText);
                }
            });
        },
        interval :time
    };
    //var task_runner = new Ext.util.TaskRunner();
    task_runner.start(update_task);
}

function get_app_updates(){
    var url="/get_app_updates";
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(!response.success){
//                Ext.MessageBox.alert(_("Failure"),response.msg);
                return;
            }
            var updates  = response.updates;
            //alert(updates);
            var value= "";
            var description="",nbsp="&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;";
            var l = 0;
            if (updates != null)
               l = updates.length;
            for(var i=0;i<l;i++){
                var update= updates[i];
                description=update.description;
                description=description.replace( /<li>/g, nbsp);
                description=description.replace( /<\/li>/g, "<br/>");
//                alert("-----"+description);
                value +="<CENTER>"+"<b>"+update.title+"</CENTER>"+"</b>"+"<br/>"+"<br/>"+"<b>Published Date:</b>"
                    +update.pubDate+"<br />"+"<br />"+description+"<br/>"+"<br/><hr><br/>";
            }
            if(l>0){
//                alert(value);
                var popup=new Ext.Window({
                    title : "更新",
                    width : 500,
                    height: 400,
                    modal : true,
                    resizable : true,
                    minWidth :250,
                    minHeight :250,
                    autoScroll:true,
                    html    : value
                });
                popup.show();
            }
        },
        failure: function(xhr){
//            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}


function check_license_expire(mode){
    var url="/check_license_expire";
    if(mode == "EXPIRED"){
        url+="?mode=EXPIRED";
    }

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                check_lic(response);
                if(response.mode=='WARNING'){
                    Ext.MessageBox.alert(_("stackone License警告"),response.msg+
                                "<br>请联系stackone技术支持.");
                }
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}

function check_lic(response){
    if(response.success){
        if(response.mode=='VIOLATION'){
            var mes_box = Ext.MessageBox;
            var config={'closable':false,
                    'msg':response.msg+
                        "<br>请联系stackone技术支持.",
                    '提示':'stackone License Violated.'
            }
            mes_box.show(config);
            var task = new Ext.util.DelayedTask(function(){
                config={'closable':true,
                        'buttons':Ext.MessageBox.OK,
                        'msg':response.msg+
                        "<br>请联系stackone技术支持.",
                        '提示':'stackone License Violated.'
                }
                mes_box.show(config);
            });
            task.delay(10000);return false;
        }
    }
    return true;
}

function showPassword(vm_id){
   var url="/cloud/get_windows_admin_password?vm_id="+vm_id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: _('请稍候...'),
        width:300,
        wait:true,
        waitConfig: {
            interval:200
        }
    });
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var password=response.password;
                Ext.MessageBox.hide();

                showWindow(_('密码'),400,155,show_password(password));
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
                Ext.MessageBox.hide();
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });





}
function show_password(password){

    var klbl=new Ext.form.Label({
         html: _(password)
     });

    var pass_panel1=new Ext.Panel({
        closable: true,
        height:'100%',
        border:false,
        width:'100%',
        labelAlign:'left',
        layout:'form',
        frame:true,
        autoScroll:true,
        labelSeparator:' ',
        id:"pass_panel1",
        items: [klbl]
    });

      var pass_panel2=new Ext.Panel({
        height:123,
        border:true,
        width:'100%',
        labelAlign:'left',
        layout:'form',
        autoScroll:true,
        labelSeparator:' ',
        id:"pass_panel2",
        items:[pass_panel1],
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

    return pass_panel2;

}

function show_desc(des,width,height,title){
    var id=Ext.id();
    if (width==null)
        width=300;
    if (height==null)
        height=150;
    if (title==null)
        title=_("信息");
    showWindow(title,width,height+33,show_panel(des,height),id,false,true);
}
function show_panel(des,height){

    var tooltip_des=new Ext.form.Label({
        //html:"<b>Actions</b>"
        html:'<br/><p>'+ unescape(des)+'</p><br/>'
    });
    var tooltip_panel=new Ext.Panel({
        height:height,
        layout:"form",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[tooltip_des]
    });
    return tooltip_panel;
}

function show_cms_cloud(dom,node){

    var url="/cloud/get_vnc_details?cloud_vm_id="+dom.attributes.id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: _('请稍候...'),
        width:300,
        wait:true,
        waitConfig: {
            interval:200
        }
    });
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                create_vnc(dom,response.vnc,node);
                Ext.MessageBox.hide();

            }else{
                Ext.MessageBox.hide();
                Ext.MessageBox.alert(_("失败"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.hide();
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
    
}

function create_vnc(dom,vnc){
    var applet='<applet code="VncViewer.class" archive="/jar/SVncViewer.jar"'+
        'width="'+vnc.width+'" height="'+vnc.height+'">'+
        '<param name="HOST" value="'+vnc.hostname+'">'+
        '<param name="PORT" value="'+vnc.port+'">'+
        '<param name="Open new window" value="'+vnc.new_window+'">'+
        '<param name="Show controls" value="'+vnc.show_control+'">'+
        '<param name="Encoding" value="'+vnc.encoding+'">'+
        '<param name="Restricted colors" value="'+vnc.restricted_colours+'">'+
        '<param name="Offer relogin" value="'+vnc.offer_relogin+'">'+
        '</applet>';

        var myData = [
        ['VNC主机',vnc.hostname],
        ['VNC端口',vnc.port]
//        ['VNC Forwarded Port',vnc.server+" : "+vnc.vnc_display],
//        ['Log File',vnc.temp_file]
    ];

    var summary_vnc_store = new Ext.data.SimpleStore({
        fields: [
            {name: 'name'},
            {name: 'value'}
        ]
    });

    // manually load local data
    summary_vnc_store.loadData(myData);
    var warn_tip=_('<font size="1" face="verdana" >\n\
                        <b> 提示 :</b> 为了使用VNC，您的浏览器需要启用Java Applet支持.</font>');

    var label_summary=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("VNC显示信息")+'&nbsp;&nbsp;</div>'
    });
    var summary_vnc_grid = new Ext.grid.GridPanel({
        disableSelection:true,
        stripeRows: true,
        autoHeight:true,
        border:true,
        cls:'hideheader',
        width:'75%',
        height: 150,
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
        {
            header: "",
            width: 200,
            sortable: false,
            css:'font-weight:bold; color:#414141;',
            dataIndex:'name'
        },{
            header: "",
            width: 220,
            sortable: false,
            dataIndex:'value'
        }
        ],
        store:summary_vnc_store,
        tbar:[label_summary]
    });

    consolePanel=new Ext.Panel({
        title   : dom.text+"&nbsp;&nbsp;&nbsp;",
        closable: true,
        layout  : 'fit',
        id      :'console'+dom.attributes.id,
        html    : "<br/>"+warn_tip+"<br/>"+applet,
        bodyStyle:'padding-top:10px;padding-left:10px;padding-right:10px',
        bodyBorder:false
        ,cls:'westPanel'
    });
    consolePanel.add(summary_vnc_grid)
    centerPanel.add(consolePanel);
    centerPanel.setActiveTab(consolePanel);



}
