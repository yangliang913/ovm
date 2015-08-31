/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

function LicenseDialog() {

    
    var label_lse=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("License详情")+'</div>',
        id:'label_lse'
    });
    var info_store =new Ext.data.JsonStore({
        url: "lisence_info",
        root: 'info',
        fields: ['name','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
       
    info_store.load();

    var info_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        autoExpandColumn:1,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 340,
        enableHdMenu:false,
        enableColumnMove:false,
        //plugins:[action],
        autoScroll:true,
        frame:false,
        loadMask:true,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 160, sortable: true, css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 120, sortable: true, dataIndex: 'value'}
        ],
        store:info_store
        ,tbar:[label_lse]
    });
    
/*
    var label_dep=new Ext.form.Label({
        html:'<div class="toolbar_hdg">'+_("Deployment Details")+'</div>',
        id:'label_about'
    });
    var dep_store =new Ext.data.JsonStore({
        url: "deployment_info",
        root: 'info',
        fields: ['name','value'],
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("Error"),store_response.msg);
            }
        }
    });
        
    dep_store.load();

    var dep_grid = new Ext.grid.GridPanel({
       // title:'Virtual Machines',
        disableSelection:true,
        stripeRows: true,
        //autoHeight:true,
        autoExpandColumn:1,
        border:true,
        cls:'hideheader',
        width: '100%',
        height: 155,
        enableHdMenu:false,
        enableColumnMove:false,
        //plugins:[action],
        autoScroll:true,
        frame:false,
        loadMask:true,
        viewConfig: {
            getRowClass: function(record, index) {
                return 'row-border';
            }
        },
        columns: [//action,
            {header: "", width: 240, sortable: true, css:'font-weight:bold; color:#414141;',dataIndex: 'name'},
            {header: "", width: 120, sortable: true, dataIndex: 'value'}
        ],
        store:dep_store
        ,tbar:[label_dep]
    });
*/

    var close_button= new Ext.Button({
        id: 'close',
        text: '关闭',
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow();
            }
        }
    });
    
    var outerpanel=new Ext.Panel({
        id:"outerpanel",        
        width:490,
        layout:"column",
        height:370,
        cls: 'whitebackground',
        items:[info_grid],        
        bbar:[{
            xtype: 'tbfill'
        },close_button]    
    });

    return outerpanel;

}


