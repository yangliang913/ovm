/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var vlanidpool_grid;
var sSiteId;

var load_counter=0;
var def_timeout;
var curr_def_count=0;
var initial_def_count=0;
var is_timer=false; 
var def_name_adding="";
var adding_def=false;
var removing_def=false;

function VLANIDPool(node, p_windowid){
    var new_button_text = "新建";
    var remove_button_text = "移除"
    var hideEditButton = false;
    var header_text = "VLAN ID是用于创建虚拟网络.VLAN ID池即所有VLAN ID的集合.";
    //We are checking whether the node passed is server or servergroup.
    if(node.attributes.nodetype == 'DATA_CENTER'){
        sSiteId = "site_id=" + node.attributes.id;
        new_button_text = "新建";
        remove_button_text = "移除";
        hideEditButton = false;
    }

    var columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), width: 80, hidden:true, sortable: true, dataIndex: 'id'},
        {header: _("名称"), width: 80, sortable: true, dataIndex: 'name'},
        {header: _("说明"), width: 80, hidden:true,sortable: true, dataIndex: 'description'},
        {header: _("VLAN ID范围"), width: 150, sortable: true, dataIndex: 'range'},
        {header: _("接口"), width: 80, sortable: true, dataIndex: 'interface'},
        {header: _("所用"), width: 140, sortable: true, dataIndex: 'used_by'},
        {header: _("CIDR"), width: 80, sortable: true, dataIndex: 'cidr', hidden:true},
        {header: _("num_hosts"), width: 80, sortable: true, dataIndex: 'num_hosts', hidden:true}
    ]);
     var network_list_store = new Ext.data.JsonStore({
        url: '/network/get_vlan_id_pools',
        root: 'rows',
        fields: [ 'id','name','description','range','interface','used_by', 'cidr', 'num_hosts' ],
        successProperty:'success',
        listeners:{
            load:function(my_store, records, options){
                //alert("Loading...");
                load_counter++;
                //alert("Load counter=" + load_counter);
                if(load_counter>10) {
                    //alert("load counter is 10.");
                    clearTimeout(def_timeout);
                    is_timer=false;
                    //refresh the grid
                    return;
                }
                curr_def_count = my_store.getCount();
                if(is_timer == true) {
                    if(initial_def_count != curr_def_count) {
                        //alert("Breaking...");
                        if(adding_def==true){
                            for(i=0;i<=curr_def_count;i++) {
                                rec = my_store.getAt(i);
                                if(def_name_adding == rec.get('name') || def_name_adding == "") {
                                    //alert("Breaking for add...");
                                    clearTimeout(def_timeout);
                                    is_timer = false;
                                    adding_def = false;
                                    //refresh the grid
                                    reloadVLANIDPoolList();
                                    break;
                                } else {
                                    //alert("Breaking for add II...");
                                    clearTimeout(def_timeout);
                                    is_timer = false;
                                    adding_def = false;
                                    //refresh the grid
                                    reloadVLANIDPoolList();
                                    break;
                                }
                            }
                        } else {
                            //alert("Breaking for remove...");
                            clearTimeout(def_timeout);
                            is_timer = false;
                            removing_def = false;
                            //refresh the grid
                            reloadVLANIDPoolList();
                        }
                    } else {
                        //alert("Continue loading...");
                        def_timeout = setTimeout("reloadVLANIDPoolList()", 1000);
                    }
                }
            },
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
    network_list_store.load();
    var  virtual_nw_selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var tf_search = new Ext.form.TextField({
        fieldLabel: '搜索',
        name: 'tf_search',
        id: 'tf_search',
        width: 85,
        allowBlank:true,
        enableKeyEvents:true,
        listeners: {
            keyup: function(field) {
            }
        }
    });

    var search_button = new Ext.Button({
        id: 'search_button',
        name: 'search_button',
        tooltip:'搜索',
        tooltipType : "title",
        icon:'icons/search.png',
        cls:'x-btn-icon',
        listeners: {
            click: function(btn) {
                var search_text = tf_search.getValue();
                network_list_store.filter('name', search_text);
            }
        }
    });

    var virtual_new_button=new Ext.Button({
        name: 'add_network',
        id: 'add_network',
        text:new_button_text,
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                adding_def=true;
                removing_def=false;

                if(node.attributes.nodetype == 'DATA_CENTER' ) {
                    windowid=Ext.id();
                    nw_new_win_popup = showWindow(_("VLAN ID池详情"),448,476,VLANIDPoolDef(node, "NEW", null, windowid),windowid); //435,500,232
                }
            }
        }

    });

    var virtual_remove_button=new Ext.Button({
        name: 'remove_network',
        id: 'remove_network',
        text:remove_button_text,
        icon:'icons/delete.png',
        cls:'x-btn-text-icon' ,
        listeners: {
            click: function(btn) {
                adding_def=false;
                removing_def=true;

                if(vlanidpool_grid.getSelectionModel().getCount()>0){
                    var net_rec=vlanidpool_grid.getSelectionModel().getSelected();
                    var message_text = "";
                    if (node.attributes.nodetype == 'DATA_CENTER') {
                        message_text = "确定要删除VLAN ID池 " + net_rec.get('name') + "吗?";
                    }

                    Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                        if(id=='yes'){

                            var vlan_id_pool_id = net_rec.get('id');
                            var url="/network/remove_vlan_id_pool?" + sSiteId + "&vlan_id_pool_id=" + vlan_id_pool_id;
                            var ajaxReq=ajaxRequest(url,0,"POST",true);
                            ajaxReq.request({
                                success: function(xhr) {//alert(xhr.responseText);
                                    var response=Ext.util.JSON.decode(xhr.responseText);
                                    if(response.success){
                                          DelayLoadingVLANIDPoolList(vlanidpool_grid);
                                          Ext.MessageBox.alert("成功","任务已经成功提交.");
                                    }else{
                                        Ext.MessageBox.alert(_("Failure"),response.msg);
                                    }
                                },
                                failure: function(xhr){
                                    Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                                }
                            });
                        }
                     });

                }else{
                    Ext.MessageBox.alert(_("失败"),_("请选择一个要删除的VLAN ID池."));
                }
            }
        }

    });
    
var  virtual_edit_button= new Ext.Button({
        name: 'edit_network',
        id: 'edit_network',
        text:_("编辑"),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        hidden: hideEditButton,
        listeners: {
            click: function(btn) {
                adding_def=false;
                removing_def=false;

                if(vlanidpool_grid.getSelectionModel().getCount()>0){
                    var edit_rec=vlanidpool_grid.getSelectionModel().getSelected();
                    var vlan_id_pool_id=edit_rec.get('id');
                    var url="/network/get_vlan_id_pool_details?vlan_id_pool_id="+vlan_id_pool_id;
                    var ajaxReq=ajaxRequest(url,0,"POST",true);
                    ajaxReq.request({
                        success: function(xhr) {//alert(xhr.responseText);
                            var response=Ext.util.JSON.decode(xhr.responseText);
                            if(response.success){
                                windowid=Ext.id();

                                nw_new_win_popup = showWindow(_("VLAN ID池详情"),448,476,VLANIDPoolDef(node, "EDIT", edit_rec, windowid),windowid); //435,500,232
                            }else{
                                Ext.MessageBox.alert(_("Failure"),response.msg);
                            }
                        },
                        failure: function(xhr){
                            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
                        }
                    });
                }else{
                    Ext.MessageBox.alert(_("失败"),_("请选择一个要编辑的VLAN ID池"));
                }

            }
        }

    });

    vlanidpool_grid = new Ext.grid.GridPanel({
        store: network_list_store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        selModel:virtual_nw_selmodel,
        width:'100%',
        //autoExpandColumn:2,
        height:350,
        autoScroll:true,
        enableHdMenu:false,
        autoExpandColumn:2,
        tbar:[{
                xtype: 'tbfill'
            },
//            'Search: ', tf_search,
//            search_button,
//            '-',
            virtual_new_button,
            '-',
            virtual_edit_button,
            '-',
            virtual_remove_button,
            '-',
            new Ext.Button({
                name: 'btnRefreshNetwork',
                id: 'btnRefreshNetwork',
                text:"刷新",
                icon:'icons/refresh.png',
                cls:'x-btn-text-icon',
                hidden: false,
                listeners: {
                    click: function(btn) {
                        adding_def=false;
                        removing_def=false;

                        //alert("Refreshing network");
                        reloadVLANIDPoolList();
                    }
                }
            })

        ],
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                virtual_edit_button.fireEvent('click',virtual_edit_button);
            }
         }
    });

    var lbl=new Ext.form.Label({
        html:'<div style="" class="labelheading">' + _(header_text) +'</div><br/>'
    });

    var panel = new Ext.Panel({
        bodyStyle:'padding:5px 5px 5px 5px',
        width:482,//452
        height:420,
        //frame:true,
        cls: 'whitebackground',
        items:[lbl,vlanidpool_grid]
        ,bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('关闭'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {adding_def=false; removing_def=false;closeWindow(p_windowid);}
                    }
            })
        ]
    });
    return panel;

}

function reloadVLANIDPoolList(){
    vlanidpool_grid.enable();
    vlanidpool_grid.getStore().load();
}

function DelayLoadingVLANIDPoolList(grid) {
    is_timer = true;
    load_counter=0;
    initial_def_count = grid.getStore().getCount();
    def_name_adding = "";
    reloadVLANIDPoolList();
}
