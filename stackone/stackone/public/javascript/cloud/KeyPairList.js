/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var key_pair_grid, key_panel;
function KeyPairList(vdc_id, windowid_kp,refresh_btn){
    var columnModel = new Ext.grid.ColumnModel([
        {header: _("编号"), hidden: true, dataIndex: 'id'},
        {header: _("名称"), width: 100, sortable: true, dataIndex: 'name'},
        {header: _("说明"), width: 200, sortable: true, dataIndex: 'description'},
        {header: _("指纹"), width: 200, hidden: true, sortable: true, dataIndex: 'fingerprint'},
        {header: _("区域"), width: 100, hidden: false, sortable: true, dataIndex: 'region'},
        {header: _("区域编号"), hidden: true, sortable: true, dataIndex: 'region_id'},
        {header: _("账户"), width: 100, hidden: false, sortable: true, dataIndex: 'account_name'},
        {header: _("账户编号"), hidden: true, sortable: true, dataIndex: 'account_id'},
        {header: _("下载"), hidden: true, sortable: true, dataIndex: 'download'}
        ]);

    var acc_id, region_id;
    var store = new Ext.data.JsonStore({
        url: '/cloud_network/get_key_pair_list?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id,
        root: 'rows',
        fields: ['id', 'name', 'description', 'fingerprint', 'region', 'region_id', 'account_id', 'account_name', 'download'],
        successProperty:'success'
    });
    store.load();

    var selmodel=new Ext.grid.RowSelectionModel({
         singleSelect:true
    });

    var new_button=new Ext.Button({
        name: 'add_key',
        id: 'add_key',
        text:_("新建"),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                key_pair_grid.getSelectionModel().clearSelections();
                var windowid=Ext.id();
                showWindow(_("创建密钥对"),380,190,KeyPairDefinition(vdc_id,  "NEW",null,windowid),windowid);//435
            }
        }
    });

    var remove_button=new Ext.Button({
        name: 'remove_key',
        id: 'remove_key',
        text:_("移除"),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedKey(key_pair_grid)){
                    if(key_pair_grid.getSelectionModel().getCount()>0){
                        var key_name, acc_id, region_id;
                        if (key_pair_grid.getSelectionModel().getSelected() != undefined) {
                            var rec=key_pair_grid.getSelectionModel().getSelected();
                            key_name=rec.get('name');
                            acc_id=rec.get('account_id');
                            region_id=rec.get('region_id');
                            var message_text = "确定要移除密钥对(" + key_name + ")吗?";
                            Ext.MessageBox.alert(_("信息"),_(message_text));
                            Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                                if(id=='yes'){
                                    removeKeyPair(vdc_id, acc_id, region_id, key_name);
                                }
                            });
                        }
                    }
                }
            }
        }
    });
    var edit_button=new Ext.Button({
        name: 'edit_key',
        id: 'edit_key',
        text:_("编辑"),
        icon:'icons/storage_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedKey(key_pair_grid)){
                    var rec=key_pair_grid.getSelectionModel().getSelected();
                    var windowid=Ext.id();
                    showWindow(_("编辑密钥对"),380,190,KeyPairDefinition(vdc_id, "EDIT",rec,windowid),windowid);
                }
            }
        }
    });
    var download_button=new Ext.Button({
        name: 'download_key',
        id: 'download_key',
        text:_("下载"),
        icon:'icons/storage_test.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                if(checkSelectedKey(key_pair_grid)){
                    if (key_pair_grid.getSelectionModel().getSelected() != undefined) {
                        var rec = key_pair_grid.getSelectionModel().getSelected();
                        var key_name = rec.get('name');
                        var acc_id = rec.get('account_id');
                        var region_id = rec.get('region_id');
                        var download = rec.get('download');

                        if(!download) {
                            Ext.MessageBox.alert("信息", "用户仅可以下载通过stackone平台创建的key.");
                            return;
                        }

                        var message_text = "确定要下载key吗?";
                        Ext.MessageBox.confirm(_("确认"),message_text,function(id){
                            if(id=='yes'){
                                 downloadKeyPair(vdc_id, acc_id, region_id, key_name);
                            }
                        });
                    }

                }
            }
        }
    });

    var refresh_button=new Ext.Button({
        name: 'refresh_button',
        id: 'refresh_button',
        text:_("导入"),
        icon:'icons/refresh.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {

                 var wait_win = Ext.MessageBox.show({
                            title:_('请稍候...'),
                            msg: '请稍候...',
                            width:300,
                            wait:true,
                            waitConfig: {
                                interval:200
                            }
                        }).hide();//hide

                 var nw=new Ext.Window({
                        title :_('导入密钥对'),
                        width :500,
                        height:400,
                        modal : true,
                        resizable : false
                    });

                var module = "KEY_PAIR";
                var panal=Import_Key_Pair(nw, wait_win, vdc_id, module);
                nw.add(panal);
                nw.show();
                        
                //this has to be call only after nw.show();
                //reinitializes an existing message box wait_win.
                wait_win.show({
                            title:_('请稍候...'),
                            msg: '请稍候...',
                            width:300,
                            wait:true,
                            waitConfig: {
                                interval:200
                            }
                        });//show


            }
        }
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
                store.filter('name', search_text);
            }
        }
    });
    var cut_tbar = new Array();
    cut_tbar.push({xtype: 'tbfill'});
    cut_tbar.push('搜索: ',tf_search);
    cut_tbar.push(search_button);
    cut_tbar.push('-');
    cut_tbar.push(new_button);
    cut_tbar.push('-');
    cut_tbar.push(edit_button);
    cut_tbar.push('-');
    cut_tbar.push(remove_button);
    cut_tbar.push('-');
    cut_tbar.push(download_button);
    cut_tbar.push('-');
    if(refresh_btn==true){
        cut_tbar.push(refresh_button);
        cut_tbar.push('-');

    }    

    key_pair_grid = new Ext.grid.GridPanel({
        store: store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        autoScroll:true,
        selModel:selmodel,
        width:548, //485
        height:385, //405
        enableHdMenu:false,
        tbar:cut_tbar,
        listeners: {
            rowdblclick:function(grid, rowIndex, e){
                edit_button.fireEvent('click',edit_button);
            }
         }
    });

    var lbl=new Ext.form.Label({
         html:'<div style="" class="labelheading">实例运行后，stackone允许你用公共/私有密钥安全的连接到它. 下面的列表代表了所有账户和区域的密钥.</div>'
    });
    key_panel = new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
        //width:485,//430
        height:468,
        frame:true,
        items:[lbl, key_pair_grid]
        ,bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'cancel',
                id: 'cancel',
                text:_('关闭'),
                icon:'icons/cancel.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {closeWindow(windowid_kp);}
                }
            })
        ]
    });

    return key_panel;
}

function checkSelectedKey(grid){
    if(grid.getSelections().length==0){
        Ext.MessageBox.alert(_("警告"),_("请选择一个key"));
        return false;
    }
    return true;
}

function removeKeyPair(vdc_id, acc_id, region_id, key_name){
    var url='/cloud_network/delete_key?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&key_name=' + key_name; 
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var task_id = response.task_id;
                var wait_time = 3000;
                wait_for_kp_remove_task(task_id, wait_time, key_name);
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}

function downloadKeyPair(vdc_id, acc_id, region_id, key_name){
// alert("downloading key pair...");
    var url='/cloud_network/download_key?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&key_name=' + key_name;

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var web_url = response.path + '/cloud_network/get_private_key?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&key_name=' + key_name;
                window.open(web_url, "_parent");
            }else{
                Ext.MessageBox.alert(_("失败"), response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}

function deleteKeyFile(vdc_id, acc_id, region_id, key_name){
//     alert("deleting key file...");
    var url='/cloud_network/delete_key_file?vdc_id=' + vdc_id + '&acc_id=' + acc_id + '&region_id=' + region_id + '&key_name=' + key_name;

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
//                 Ext.MessageBox.alert("Success", response.msg);
            }else{
                Ext.MessageBox.alert(_("失败"), response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }

    });
}

function reloadKPList(){
    key_pair_grid.getStore().load();
}

function wait_for_kp_remove_task(task_id, wait_time, key_name){
    //alert("waiting for task completion...");
    var url = '/cloud_network/wait_for_task?task_id=' + task_id + '&wait_time=' + wait_time;
    //alert("url is " + url);
    Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: _('正在移除密钥对...'),
        width:300,
        wait:true,
        waitConfig: {
            interval:3000
        }
    });

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                reloadKPList();
                Ext.MessageBox.alert("成功", "密钥对" + key_name + " 移除成功.");
            }else{
                Ext.MessageBox.alert(_("失败"), response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}


function refresh_list(w, sel_keys, vdc_id, module){
    //alert("refreshing list...");
    var url = '/cloud_network/save_imported_items_from_cloud?items=' + sel_keys + '&vdc_id=' + vdc_id + '&module=' + module;
    //alert("url is " + url);

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var task_id = response.task_id;
                var wait_time = 3000;
                wait_for_refresh_task(task_id, wait_time)
                w.close();
            }else{
                Ext.MessageBox.alert(_("失败"), response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}


function wait_for_refresh_task(task_id, wait_time){
    //alert("waiting for task completion...");
    var url = '/cloud_network/wait_for_task?task_id=' + task_id + '&wait_time=' + wait_time;
    //alert("url is " + url);
    var refresh_win = Ext.MessageBox.show({
        title:_('请稍候...'),
        msg: _('正在刷新列表...'),
        width:300,
        wait:true,
        waitConfig: {
            interval:200
        }
    });

    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                reloadKPList();
                refresh_win.hide();
//                Ext.MessageBox.alert("Info", response.status);
            }else{
                Ext.MessageBox.alert(_("失败"), response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}



function Import_Key_Pair(w, wait_win, vdc_id, module)
{

    var tlabel_key_pair=new Ext.form.Label({
        html:'<div>'+_("导入密钥对")+'<br/></div>'
    });

    var label_key_pair=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("密钥对")+'<br/></div>'
    });

    var button_cancel=new Ext.Button({
    name: 'cancel',
    id: 'cancel',
    text:_('关闭'),
    icon:'icons/cancel.png',
    cls:'x-btn-text-icon',
    listeners: {
        click: function(btn) {
            w.close();
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
                var l = key_pair_store.getTotalCount();
                var keypair_list = new Array();
                for (var i=0;i<l;i++){
                    var r = key_pair_store.getAt(i);
                    if(r.get("is_selected")){
                       var dt = {'name' :r.get('name'),
                            'region' : r.get('region')}
                        keypair_list.push(dt);
                    }
                }
                if(keypair_list.length == 0){
                     Ext.MessageBox.alert(_("错误"),_("请选择一个密钥对"));
                     return;
                }
                refresh_list(w, Ext.util.JSON.encode(keypair_list), vdc_id, module)
                
            }
        }
    });


    var key_pair_store = new Ext.data.JsonStore({
        url: '/cloud_network/refresh_list',
        root: 'rows',
        fields: ['id', 'name', 'region', 'used_by','is_selected'],
        successProperty:'success',
        listeners:{
            load:function(store){
                wait_win.hide();
            }
        }
    });


    var args = {params:{vdc_id:vdc_id,
                            module:module
                        }
                };
    key_pair_store.load(args);


    var selmodel=new Ext.grid.CheckboxSelectionModel({
            singleSelect:false
        });

     var key_pair_grid = new Ext.grid.GridPanel({
        store: key_pair_store,
        enableHdMenu:false,
        selModel:selmodel,
        id:'key_pair_grid',
        columns: [
            {
                id       :'id',
                header   : '编号',
                width    :  0,
                sortable : true,
                dataIndex: 'id',
                hidden : true
            },
            {
                header: _("名称"),
                width: 145,
                sortable: true,
                dataIndex: 'name'
            },
            {
                header   : '区域',
                width     : 150,
                sortable : true,
                dataIndex: 'region',
                 hidden : false
            },
            {
                header : '所用',
                width  : 95,
                sortable : true,
                dataindex :'used_by',
                hidden : false
            },
            {header:_("选择"),width: 50, sortable: true, dataIndex: 'is_selected', renderer:render_select_checkbox}
        ],

        stripeRows: true,
        height: 310,
        width:475,
        tbar:[label_key_pair,{
            xtype: 'tbfill'
             }],
        listeners: {

         }
    });


    var key_pair_panel=new Ext.Panel({
        id:"key_pair_panel",
        width:490,
        height:367,
        //frame:true,
        cls: 'whitebackground',
        border:false,
        bodyStyle:'padding:5px 5px 5px 5px',
        bbar:[{
            xtype: 'tbfill'
        },button_ok, button_cancel],
        items:[tlabel_key_pair, key_pair_grid]
    });

   var outerpanel=new Ext.FormPanel({
       height: 380,
       width: 495,
       autoEl: {},
       layout: 'column',
       items: [key_pair_panel]
   });

   return outerpanel
}


