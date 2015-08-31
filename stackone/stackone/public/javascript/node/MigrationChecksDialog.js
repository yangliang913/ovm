/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function MigrationChecksDialog(vm,node,dest_node,live,rows, url){
    var columnModel = new Ext.grid.ColumnModel([
        {header: _("类型"), width: 40, sortable: false, dataIndex: 'type',renderer:function(value,params,record){
                if(value=='error'){
                    return '<img src="icons/cancel.png" />';
                }else if(value=='warning'){
                    return '<img src="icons/warning.png" />';
                }
        }},
        {header: _("分类"), width: 80, sortable: true, dataIndex: 'category'},
        {header: _("消息"), width: 150, sortable: true, dataIndex: 'message'}
    ]);

    var store = new Ext.data.SimpleStore({
        fields:[{name: 'type'},
                {name: 'category'},
                {name:'message'}]
    });
    store.loadData(getData(rows));
    var grid = new Ext.grid.GridPanel({
        store: store,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        border:true,
        width:495,
        autoExpandColumn:2,
        height:240
    });

    var lbl=new Ext.form.Label({
        text:_("虚拟机迁移检测已经完毕.")
    });
    var panel = new Ext.Panel({
        layout:'form',
        bodyStyle:'padding:15px 0px 0px 0px',
        labelWidth:60,
        labelSeparator:' ',
        width:500,
        height:300,
        autoScroll:true,
        enableColumnHide:false,
        items:[lbl,grid],
        bbar:[
            {xtype: 'tbfill'},
            new Ext.Button({
                name: 'continue',
                id: 'continue',
                text:_('继续'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        closeWindow();
                        //migrateVM(vm,node,dest_node,live,'true');
                        url+="&force=true"
                        runMigration(url,'true',node,dest_node,vm,node,live)
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
                    click: function(btn) {closeWindow();}
                }
            })
        ]
    });

    return panel;
}

function getData(rows){
    var data=new Array();
    for(var i=0;i<rows.length;i++){
        data[i]=new Array();
        data[i][0]=rows[i].type;
        data[i][1]=rows[i].category;
        data[i][2]=rows[i].message;
    }
    return data;
}