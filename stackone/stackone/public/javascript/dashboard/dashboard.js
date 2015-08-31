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
    method_map[stackone.constants.DATA_CENTER]='data_center';
    method_map[stackone.constants.SERVER_POOL]='server_pool';
    method_map[stackone.constants.MANAGED_NODE]='server';
    method_map[stackone.constants.DOMAIN]='vm';
    method_map[stackone.constants.IMAGE_STORE]='image_store';
    method_map[stackone.constants.IMAGE_GROUP]='image_group';
    method_map[stackone.constants.IMAGE]='image';
    method_map[stackone.constants.VDC_FOLDER]='vdc_folder';
    method_map[stackone.constants.VDC_VM_FOLDER]='vdc_vm_folder';
    method_map[stackone.constants.VDC]='vdc';
    method_map[stackone.constants.CLOUD_PROVIDER_FOLDER]='cloud_provider_store';
    method_map[stackone.constants.CLOUD_PROVIDER]='cloud_provider';
    method_map[stackone.constants.TMP_LIB]='CloudTemplateLibrary';
    method_map[stackone.constants.CLOUD_TMPGRP]='CloudTemplateGroup';
    method_map[stackone.constants.CLOUD_TEMP]='CloudTemplate';
    method_map[stackone.constants.CLOUD_VM]='vmcloud'


    var dims=getDocumentDimensions();
    //alert(dims[0]+"---"+dims[1])
    var myWidth = dims[0], myHeight = dims[1];
    
    var lbl_header=new Ext.form.Label({
        html:'<div align="center"><font size=4 face="Verdana" ><b>stackone Cloud</b></font></div>',
        id:'lbl_header'
    });
    
    var lbl_user=new Ext.form.Label({
        html:'<div align="left"><font size=2 face="Verdana" ><b>' + _('User') + ': ' + user_name + '</b></font></div>',
        id:'lbl_user'
    });

    var links="<div align='right'>";
    if(is_admin =='True'){        
        links+="<img style='cursor:pointer' title='Administration' src='/icons/admin.png' onclick=javascript:showWindow('"+_('Administration')+"',705,470,adminconfig()); ></img>&nbsp;";
       }
    links+="<img style='cursor:pointer' title='Change Password' src='/icons/chpass.png' onclick=javascript:showWindow('"+_("Password")+"',400,200,changepass(user_name)); ></img>&nbsp;";
    links+="<img style='cursor:pointer' title='Tasks' src='/icons/tasks.png' onclick=javascript:showWindow('"+_('Tasks')+"',740,370,Tasks());></img>&nbsp;"+
        "<img style='cursor:pointer' title='Logout' onclick=javascript:window.location='/user_logout' src='/icons/logout.png'></img>"+
        "</div>";

    var lbl_links=new Ext.form.Label({
        html:links,
        id:'lbl_links'
    });
        
    var westPanel=new Ext.Panel({
        region:'west',
        width:200,
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
//                    alert(tabid+"===="+nodetype+"===="+node.attributes.id);
                    var method=method_map[nodetype]+"_"+tabid+"_page";//alert(method)
                    var callback = function(context){eval(method+"(tab,node.attributes.id,node)")}
                    ///Fetch list of enabled components from backend. ///
                    stackone.UIHelper.GetUIHelper(node, nodetype, stackone.constants.DB_DASHBOARD, callback);
//                    eval(method+"(tab,node.attributes.id,node)")
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
       // url: '/get_context_menu_items?menu_combo=True',
        root: 'rows',
        fields: ['text', 'value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_( "Error"),store_response.msg);
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
        
//    var menu_btn=new Ext.Button({
//        tooltip:'Show Context Menu',
//        tooltipType : "title",
//        icon:'icons/settings.png',
//        cls:'x-btn-icon',
//        listeners: {
//            click: function(btn,e){
//                var node=leftnav_treePanel.getSelectionModel().getSelectedNode();
//                if(node)
//                    node.fireEvent('contextmenu',node,e);
//            }
//        }
//    });
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
	    header_html_link+= "  <div class='header-left'>";
	    header_html_link+= "  <img src='images/stackone_logo.gif' alt='stackone Logo'/>";
	    header_html_link+= "  </div>";
	    
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
        //header_html_link+= "           <p>"" : </p><p>""</p>";
        header_html_link+= "        </div>";
        header_html_link+= "        <div class='header-right-right'>";
        header_html_link+= "            <ul class='admin-nav-menu'>";
		header_html_link += "           <li class='username'><a href='#' >"
			+ user_firstname + "&nbsp;&nbsp;|&nbsp;&nbsp;</a></li>";

        if(is_admin=='True'){
            header_html_link+= "           <li class='admin'><a href='#' onclick=javascript:showWindow('"+_('选择用户类型')+"',315,130,select_ui_type());>(权限)</a></li>";
            header_html_link+= "         <li class='mangevcenter'><a href='#' onclick=javascript:showWindow('"+_('管理vCenters')+"',466,450,vCenterlist(null));>(vCenter)</a></li>";
    }
       
        header_html_link+= "         <li class='task'><a href='#' onclick=javascript:showWindow('"+_('审计')+"',740,370,Tasks());>(审计)</a></li>";
        header_html_link+= "         <li class='password'><a href='#' onclick=javascript:showWindow('"+_('密码')+"',400,200,changepass(user_name));>(密码)</a></li>";
        //header_html_link+= "         <li class='license'><a href='#' onclick=javascript:showWindow('"+_('License')+"',500,400,LicenseDialog());></a></li>";
        header_html_link+= "         <li class='logout'><a href='#' onclick=javascript:window.location='/user_logout'>(注销)</a></li>";
		
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
        //margins: '2 2 2 0',
        width:'100%',
       // tbar:[label_entity,{xtype:'tbfill'},label_action,"&nbsp;&nbsp;",menu_combo]
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
        //renderTo:'content',
//        width:myWidth-5,
        //height:myHeight-5,
        border:false,
        width:"100%",
        height:"100%",
        id:'outerPanel',
        items: [ headerPanel,borderPanel]
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
	
	// 数据中心-入门面板
	var datacenterStarterPanel = new Ext.Panel({
		title : _('入门'),
		closable : false,
		// autoScroll:true,
		defaults : {
			autoScroll : true
		},
		layout : 'fit',
		border:false,//lbz更改，添加一句
		width : 400,
		id : 'datacenterStarter',
		listeners : {
			activate : function(panel) {
				if (panel.rendered) {
					panel.doLayout();
				}
			}
		}
	});
	
	// 服务器池-入门面板
	var serverpoolStarterPanel = new Ext.Panel({
		title : _('入门'),
		closable : false,
		// autoScroll:true,
		defaults : {
			autoScroll : true
		},
		layout : 'fit',
		width : 400,
		id : 'serverpoolStarter',
		listeners : {
			activate : function(panel) {
				if (panel.rendered) {
					panel.doLayout();
				}
			}
		}
	});
    
	// 节点-入门面板
	var managernodeStarterPanel = new Ext.Panel({
		title : _('入门'),
		closable : false,
		// autoScroll:true,
		defaults : {
			autoScroll : true
		},
		layout : 'fit',
		width : 400,
		id : 'managernodeStarter',
		listeners : {
			activate : function(panel) {
				if (panel.rendered) {
					panel.doLayout();
				}
			}
		}
	});
	
	// 虚拟机-入门面板
	var domainStarterPanel = new Ext.Panel({
		title : _('入门'),
		closable : false,
		// autoScroll:true,
		defaults : {
			autoScroll : true
		},
		layout : 'fit',
		width : 400,
		id : 'domainStarter',
		listeners : {
			activate : function(panel) {
				if (panel.rendered) {
					panel.doLayout();
				}
			}
		}
	});
	
	// 模版库-入门面板
	var imageStoreStarterPanel = new Ext.Panel({
		title : _('入门'),
		closable : false,
		// autoScroll:true,
		defaults : {
			autoScroll : true
		},
		layout : 'fit',
		width : 400,
		id : 'imageStroeStarter',
		listeners : {
			activate : function(panel) {
				if (panel.rendered) {
					panel.doLayout();
				}
			}
		}
	});
	
	// 模版组-入门面板
	var imageGroupStarterPanel = new Ext.Panel({
		title : _('入门'),
		closable : false,
		// autoScroll:true,
		defaults : {
			autoScroll : true
		},
		layout : 'fit',
		width : 400,
		id : 'imageGroupStarter',
		listeners : {
			activate : function(panel) {
				if (panel.rendered) {
					panel.doLayout();
				}
			}
		}
	});
	// 模版-入门面板
	var imageStarterPanel = new Ext.Panel({
		title : _('入门'),
		closable : false,
		// autoScroll:true,
		defaults : {
			autoScroll : true
		},
		layout : 'fit',
		width : 400,
		id : 'imageStarter',
		listeners : {
			activate : function(panel) {
				if (panel.rendered) {
					panel.doLayout();
				}
			}
		}
	});
	
	// 虚拟机-控制台面板
	var domainConsolePanel = new Ext.Panel({
		title : _('控制台'),
		closable : false,
		// autoScroll:true,
		defaults : {
			autoScroll : true
		},
		layout : 'fit',
		width : 400,
		id : 'domainConsole',
		listeners : {
			activate : function(panel) {
				if (panel.rendered) {
					panel.doLayout();
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
        title   : _('信息 '),
        closable: false,
        //layout  : 'anchor',
        id:'info',
        height:600,
        autoScroll:true,
        defaults: {
            autoScroll:true
        },
        layout:'fit',
        //frame:true,
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

// var backupinformpanel = new Ext.Panel({
//         //layout  : 'fit',
//         //anchor:'100% 50%',
//         collapsible:false,
//         //title:format(_("Server Pool Information for {0}"),node.text),
//         height:'50%',
//         width:'100%',
//         border:false,
// //        cls:'headercolor',
//         bodyStyle:'padding-left:15px;padding-right:15px;padding-bottom:12px;padding-top:10px;',
//         bodyBorder:false,
//         resizable:true,
//         items:[SPBackupTasksGrid(node_id)]
//     });
// backup_history_Panel.add(backupinformpanel);
//     
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
                if (node.attributes.nodetype == stackone.constants.SPECIAL_NODE &&
                 node.attributes.id==1 && node.attributes.id==2){
                    return;
                }
                
                showContextMenu(node, e);
            }
            ,beforeexpandnode:function(node){
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
        
    leftnav_treePanel.on('restore',function(node,e){

        var iconClass=node.getUI().getIconEl().className;
        node.getUI().getIconEl().className="x-tree-node-icon loading_icon";
        var ajaxReq = ajaxRequest(node.attributes.url,0,"GET",true);
        //checkToolbar(node);
        
        if(node.attributes.nodetype==stackone.constants.SERVER_POOL){            
           // menu_combo.reset();
            menu_store.load({
                params:{
                    node_id:node.attributes.id,
                    node_type:node.attributes.nodetype,
                    cp_type:node.attributes.cp_type
                }
            });
            (function(){
                addTabs(centerPanel,[summaryPanel,configPanel,vminfoPanel, backup_history_Panel]);
                centerPanel.setActiveTab(backup_history_Panel)
            }).defer(25);         
            
            //getVNCInfo(node.parentNode,node,centerPanel);
            //updateInfoTab(InfoGrid(node),true);
            node.getUI().getIconEl().className=iconClass;
            label_entity.setText(getHdrMsg(node.text),false);            
            return;
            }
        });

    leftnav_treePanel.on('beforeclick',function(node,e){

        if (node.attributes.nodetype == stackone.constants.SPECIAL_NODE){
            Ext.MessageBox.alert(_("信息"),"假使服务器池中有太多的服务器显示在导航栏.<br/>\
                                    请使用服务器选项卡，确定你寻找的服务器.");           
            return false;

        }
    });

    leftnav_treePanel.on('click',function(node,e){
        
        if(node.attributes.clickable==stackone.constants.OUTSIDE_DOMAIN){
            return;
        }

       // Fix of bug:1364 (folder icon keeps spinning)
       if (node.text == 'Infrastructure' || node.text == 'Cloud')
           {
//               node.purgeListeners();
               return;
           }

//        check_license_expire('EXPIRED');
        var iconClass=node.getUI().getIconEl().className;
        node.getUI().getIconEl().className="x-tree-node-icon loading_icon";
//        alert(node.attributes.url);
        var ajaxReq = ajaxRequest(node.attributes.url,0,"GET",true);
        //checkToolbar(node);
    
        if(node.attributes.nodetype==stackone.constants.DOMAIN){
            //menu_combo.reset();
            menu_store.load({
                params:{
                    node_id:node.attributes.id,
                    node_type:node.attributes.nodetype
                }
            });
            (function(){
                addTabs(centerPanel,[domainStarterPanel,summaryPanel,configPanel,domainConsolePanel,backup_history_Panel]);
            }).defer(25);            

            //getVNCInfo(node.parentNode,node,centerPanel);
            //updateInfoTab(InfoGrid(node),true);
            node.getUI().getIconEl().className=iconClass;
            label_entity.setText(getHdrMsg(node.text),false);
            
            return;
        }else if(node.attributes.nodetype==stackone.constants.IMAGE){
            //menu_combo.reset();
            menu_store.load({
                params:{
                    node_id:node.attributes.id,
                    node_type:node.attributes.nodetype
                }
            });
            (function(){
                addTabs(centerPanel,[imageStarterPanel,summaryPanel/*,infoPanel*/,vminfoPanel]);
            }).defer(25);

            node.getUI().getIconEl().className=iconClass;
            label_entity.setText(getHdrMsg(node.text),false);
            
            infoPanel.setTitle(_('说明'));
            vminfoPanel.setTitle( _('虚拟机'));
            return;       
        }

        //showChart(node.attributes.nodetype ,"CPU",node.attributes.id,"DDDD","DTD",null,null,"DDD");
        ajaxReq.request({
            success: function(xhr) {

                node.getUI().getIconEl().className=iconClass;
                //alert(xhr.responseText+"-------------"+xhr.responseXML);
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(!check_lic(response)){return;}
                if(!response.success){
                    if(node.attributes.nodetype==stackone.constants.MANAGED_NODE &&
                            response.msg==_('服务器没有验证.')){
                        showWindow(_("认证 ")+node.text,280,150,credentialsform(node));
                        return;
                    }
                    Ext.MessageBox.alert(_("Failure"),response.msg);
                    return;
                }  
                
                label_entity.setText(getHdrMsg(node.text),false);
                //menu_combo.reset();
                menu_store.load({
                    params:{
                        node_id:node.attributes.id,
                        node_type:node.attributes.nodetype,
                        cp_type:node.attributes.cp_type
                    }
                });
                
                if(node.attributes.nodetype==stackone.constants.MANAGED_NODE){

                    addTabs(centerPanel,[managernodeStarterPanel,summaryPanel,configPanel,vminfoPanel,task_Panel]);
                    vminfoPanel.setTitle( _('虚拟机'));                    
                }else if(node.attributes.nodetype==stackone.constants.IMAGE_STORE ){

                    addTabs(centerPanel,[imageStoreStarterPanel,summaryPanel]);
                }else if(node.attributes.nodetype==stackone.constants.IMAGE_GROUP){

                    addTabs(centerPanel,[imageGroupStarterPanel,summaryPanel]);
                }else if(node.attributes.nodetype==stackone.constants.SERVER_POOL){

                    addTabs(centerPanel,[serverpoolStarterPanel,summaryPanel,configPanel,vminfoPanel, backup_history_Panel,task_Panel]);
                    vminfoPanel.setTitle(_('服务器'));
                }else if(node.attributes.nodetype==stackone.constants.DATA_CENTER) {

                    addTabs(centerPanel,[datacenterStarterPanel,summaryPanel,configPanel,vminfoPanel,backup_history_Panel]);
                    vminfoPanel.setTitle(_('服务器'));
                }
                
                else if(node.attributes.nodetype==stackone.constants.VDC_FOLDER) {

                    addTabs(centerPanel,[summaryPanel]);
                    
                }
                else if(node.attributes.nodetype==stackone.constants.VDC_VM_FOLDER) {

                    addTabs(centerPanel,[vminfoPanel]);
                    vminfoPanel.setTitle(_('虚拟机'));
                }
                else if(node.attributes.nodetype==stackone.constants.VDC) {
                    if(node.attributes.cp_type==stackone.constants.CMS){
                       addTabs(centerPanel,[summaryPanel, vminfoPanel,networkingPanel]);
                    }else{
                       addTabs(centerPanel,[summaryPanel, configPanel, vminfoPanel]);
                    }
                    vminfoPanel.setTitle(_('虚拟机'));
                }
                  else if(node.attributes.nodetype==stackone.constants.CLOUD_PROVIDER_FOLDER) {  
                    addTabs(centerPanel,[summaryPanel]);

                }
                else if(node.attributes.nodetype==stackone.constants.CLOUD_PROVIDER) {
                    
                    if (node.attributes.cp_type == stackone.constants.CMS){
                        addTabs(centerPanel,[summaryPanel,configPanel]);
                    }else{
                        addTabs(centerPanel,[summaryPanel]);}

                }
                else if(node.attributes.nodetype==stackone.constants.CLOUD_VM) {

                    addTabs(centerPanel,[summaryPanel,configPanel]);

                }else if(node.attributes.nodetype==stackone.constants.TMP_LIB ){

                    addTabs(centerPanel,[summaryPanel]);
                }else if(node.attributes.nodetype==stackone.constants.CLOUD_TMPGRP){

                    addTabs(centerPanel,[summaryPanel]);
                }
                  

                
                var r_children=response.nodes;
//                alert(response.nodes.toSource())
                var n_children=node.childNodes;
                var new_nodes=get_new_nodes(r_children,node);
                var del_nodes=get_del_nodes(r_children,n_children);
                //alert(node.attributes.text+"===dash==new=="+new_nodes+"del=="+del_nodes);
                if(new_nodes.length!=0)
                    appendChildNodes(new_nodes,node);
                if(del_nodes.length!=0)
                    removeNodes(node,del_nodes);
//                removeChildNodes(del_nodes);
//                appendChildNodes(response.nodes,node);
                node.expand();
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                node.getUI().getIconEl().className=iconClass;
            }
        });

    }); 

    // SET the root node.
    var rootNode = new Ext.tree.TreeNode({
        text		: 'rootnode',
        draggable       : false,
        nodetype : "rootnode",
        url : "/dashboard/dashboardservice?node_id=0&type=rootnode",
        id		: '0'
    });

    var Infrastructure = new Ext.tree.TreeNode({
        text		: 'Infrastructure',
        draggable   : false,
        sorttext    : "Infrastructure",
        id          : '1'
    });

    getNavNodes(rootNode, true);

  var cloud_Node = new Ext.tree.TreeNode({
//        text		: 'Cloud',
        draggable   : false,
        sorttext    :"zCloud",
        id          : '2'
    });

//    ajaxReq=ajaxRequest("get_cloudnav_nodes",0,"GET",true);
//    ajaxReq.request({
//        success: function(xhr) {//alert(xhr.responseText);
//            var response=Ext.util.JSON.decode(xhr.responseText);
//            if(response.success){
//                appendChildNodes(response.nodes,rootNode);
//                rootNode.expand();
//                get_app_updates();
//                check_license_expire();
////                cloud_Node.firstChild.fireEvent('click',cloud_Node.firstChild);
//                }else{
//                Ext.MessageBox.alert(_("Failure"),response.msg);
//            }
//        },
//        failure: function(xhr){
//            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
//        }
//    });

 
    westPanel.add(leftnav_treePanel);

//    leftnav_treePanel.add (leftnav_treePanel,cloud_Node,2);
//    leftnav_treePanel.add (leftnav_treePanel,Infrastructure,1);

//    rootNode.appendChild(Infrastructure);
//    rootNode.appendChild(cloud_Node);
    leftnav_treePanel.setRootNode(rootNode);


    //leftnav_treePanel.render();

    return outerPanel; 
}

function getNavNodes(rootNode, first){
    
    if (rootNode == null){
        rootNode = leftnav_treePanel.getNodeById('0');
    }
    var ajaxReq=ajaxRequest("get_nav_nodes",0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                if (first!=true){
                    removeChildNodes(rootNode);
                }
                appendChildNodes(response.nodes,rootNode);
                rootNode.expand();
                if (first==true){
                    get_app_updates();
                    check_license_expire();
                    rootNode.firstChild.fireEvent('click',rootNode.firstChild);
                }
            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
    
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

function getSshWindow(node){
        var response  = null;
        var platform = '';
        if(Ext.isLinux){
        	platform = 'linux'
        }else if(Ext.isWindows){
        	platform = 'windows'
        }
        var url='get_ssh_info?node_id='+node.id+'&client_platform='+platform
        var ajaxReq = ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {//alert(xhr.responseText);
                response=Ext.util.JSON.decode(xhr.responseText);
                showWindow(_('SSH终端'),450,260,show_ssh_window(node,response));
//                if(response){ 
//                    response = response.vnc;
//                 }else{
//                    Ext.MessageBox.alert(_("Failure"),response.msg);
//                }
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
            }
        });
}

function getCMDInfo(dom,cmd,response,cloud){
    var consolePanel=centerPanel.getItem('console'+dom.attributes.id);
    if (consolePanel != null ){
        centerPanel.remove(consolePanel);
    }

    if(response.vnc.port=='00'){
        Ext.MessageBox.alert(_("信息"),_("虚拟机没有运行."))
        return;
    }

//    alert("----cmd--"+cmd);
    var applet='<applet code="AppletRunner.class" archive="/jar/SAppletRunner.jar"'+
    ' width="1" height="1">'+
    '<param name="command" value="'+cmd+'">'+
    '</applet>';
    create_applet_tab(dom,applet,response);
}

function create_applet_tab(dom,applet,response,cloud){
    var myData = [
        ['VNC主机',response.vnc.hostname],
        ['VNC端口',response.vnc.port],
        ['VNC 转发端口',response.vnc.server+" : "+response.vnc.vnc_display],
        ['日志文件',response.vnc.temp_file]
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



function addTabs(prntPanel,childpanels){
	
	
    if(prntPanel.items){
        prntPanel.isRemoving=true;
//       	prntPanel.removeAll(true);
        
        
        prntPanel.items.each(function(tab){
            //vnc console tabs will have id=(console+nodeid)
            if(tab.getId().indexOf('console')!=0){
             		prntPanel.remove(tab,true);
            }
        })
        
        
        
   }
    prntPanel.isRemoving=false;
    for(var i=0;i<childpanels.length;i++){
    	
        prntPanel.insert(i,childpanels[i]);
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
                        Ext.MessageBox.alert(_("Failure"),response.msg);
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
                    Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                }
            });
        },
        interval :time
    };
    //var task_runner = new Ext.util.TaskRunner();
    task_runner.start(update_task);
}

/*function get_app_updates(){
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
           // var l = updates.length;
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
}*/


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
                    Ext.MessageBox.alert(_("stackone License Warning"),response.msg+
                                "<br>请联系Stackone技术支持.");
                }
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function check_lic(response){
    if(response.success){
        if(response.mode=='VIOLATION'){
            var mes_box = Ext.MessageBox;
            var config={'closable':false,
                    'msg':response.msg+
                        "<br>请联系Stackone技术支持.",
                    '标题':'已达到 stackone License限额.'
            }
            mes_box.show(config);
            var task = new Ext.util.DelayedTask(function(){
                config={'closable':true,
                        'buttons':Ext.MessageBox.OK,
                        'msg':response.msg+
                        "<br>请联系Stackone技术支持.",
                        '标题':'已达到 stackone License限额.'
                }
                mes_box.show(config);
            });
            task.delay(10000);return false;
        }
    }
    return true;
}

function show_ssh_window(node,response){
//    var vm_platform=response.vm_platform;
    if(!response.success){
        Ext.MessageBox.alert( _("Failure") , response.msg);
    }
    
    cmd  = Ext.util.Format.trim(response.vnc.command);
    var applet='<applet code="AppletRunner.class" archive="/jar/SAppletRunner.jar"'+
    ' width="1" height="1">'+
    '<param name="command" value="'+cmd+'">'+
    '</applet>';

    var consolePanel=centerPanel.getItem('console'+node.id);
    if (consolePanel != null ){
        centerPanel.remove(consolePanel);
    }
    var help= ''
    var heading='SSH连接信息';

    var label_summary=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_(heading)+'</div>'
    });

    var warn_tip=_('<font size="1" face="verdana" >\n\
                        <b> 提示 :</b> 为了使用VNC，您的浏览器需要启用Java Applet支持.</font>');

    var ssh_data = [
                ['SSH Forwarding', response.vnc.forwarding]
            ];
    if (response.vnc.forwarding == 'Enabled'){
            ssh_data.push(['SSH Host', response.vnc.hostname]);
            ssh_data.push(['SSH Port', response.vnc.port]);
        }
    ssh_data.push(['Server', response.vnc.server]);

    var console_grid = get_console_grid(ssh_data, label_summary);

//    var consolePanel_heading=new Ext.Panel({
//        autoHeight:true,
//        border:true,
//        cls:'hideheader',
//        width:'75%',
//        height: 150,
//        frame:false,
//        tbar:[label_summary]
//    });

    consolePanel=new Ext.Panel({
        title   : node.text+"&nbsp;&nbsp;&nbsp;",
        closable: true,
        layout  : 'fit',
        id      :'console'+node.id,
        html    : "<br/>"+warn_tip+"<br/>"+applet,
        bodyStyle:'padding-top:10px;padding-left:10px;padding-right:10px',
        bodyBorder:false
        ,cls:'westPanel'
    });

//    consolePanel.add(consolePanel_heading);
    consolePanel.add(console_grid);
    centerPanel.add(consolePanel);
    centerPanel.setActiveTab(consolePanel);
    return ' ';
}



function get_console_grid(data, label_summary)
{
    var summary_store = new Ext.data.SimpleStore({
        fields: [
            {name: 'name'},
            {name: 'value'}
        ]
    });
    
    summary_store.loadData(data);

    var summary_grid = new Ext.grid.GridPanel({
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
        store:summary_store,
        tbar:[label_summary]
    });

   return summary_grid
}



/*function show_log(file){

    var url="/node/get_vnc_log_content?file="+file;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    Ext.MessageBox.show({
        title:_('Please wait...'),
        msg: _('Please wait...'),
        width:300,
        wait:true,
        waitConfig: {
            interval:200
        }
    });
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                Ext.MessageBox.hide();
                showWindow(_("View Console log:")+" "+file,444,480,view_content(response.content));
            }
        },
        failure: function(xhr){
            Ext.MessageBox.hide();
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}

function view_content(content){

     var klbl=new Ext.form.Label({
         html: _(content)
     });

    var content_panel1=new Ext.Panel({
        closable: true,
        height:'100%',
        border:false,
        width:'100%',
        labelAlign:'left',
        layout:'form',
        frame:true,
        autoScroll:true,
        labelSeparator:' ',
        id:"content_panel1",
        items: [klbl]
    });

      var content_panel2=new Ext.Panel({
        height:450,
        border:true,
        width:'100%',
        labelAlign:'left',
        layout:'form',
        autoScroll:true,
        labelSeparator:' ',
        id:"content_panel2",
        items:[content_panel1],
        bbar:[{xtype: 'tbfill'},
                new Ext.Button({
                name: 'close',
                id: 'close',
                text:_('Close'),
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

    return content_panel2;


}*/
