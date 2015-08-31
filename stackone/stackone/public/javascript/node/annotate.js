
function annotateEntity(node,action){

    var url="/node/get_annotation?node_id="+node.attributes.id;
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var annotate=response.annotate;
                showWindow(_("注释")+" "+node.text,400,220,process_annotation(node,action,annotate.user,annotate.text));
            }else{
                Ext.MessageBox.alert( _("Failure") , response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
}
function process_annotation(node,action,username,text){


    var annotate_text=new Ext.form.Label({
         html: _("请输入下面的注释，别人也会通过电子邮件接到通知.")
    });

    var br=new Ext.form.Label({
         html: _("<div style='height:10px'/>")
    });
    var modified_by=(username==null)?"":username;
    var user_name=new Ext.form.Label({
         html: _("上次的修改者:&nbsp;&nbsp;"+modified_by)
     });
//    var user_name = new Ext.form.TextField({
//        fieldLabel: 'Last Modified by:',
//        name: 'user_name',
//        id: 'user_name',
//        width:180,
//        value:username,
//        disabled:true,
//        labelSeparator:" ",
//        allowBlank:true,
//        enableKeyEvents:true,
//        listeners: {
//            keyup: function(field) {
//
//            }
//        }
//    });

    var user_annotation = new Ext.form.TextArea({
        fieldLabel: '注释 ',
        name: 'user_annotation',
        id: 'user_annotation',
        width: 260,
        height: 100,
        value:text,
        enableKeyEvents:true,
        listeners: {
            keydown: function(field) {
                var annot_values=user_annotation.getValue();
                if(annot_values.length>=256){
                   user_annotation.setValue(annot_values.substring(0,255));
                }
            }
        }

    });
    var annotate_panel1=new Ext.form.FormPanel({
        closable: true,
        height:'100%',
        border:false,
        width:'100%',
        layout:'form',
        frame:true,
        labelAlign:"right" ,
        id:"annotate_panel1",
        items: [annotate_text,br,user_annotation,user_name]
    });


    var button_clear=new Ext.Button({
        name: 'clear',
        id: 'clear',
        text:_('清除'),
        icon:'icons/delete.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
//                if (user_annotation.getValue()!=""){
                     var msg=format(_("清除注释. 确定要继续吗?"),node.text);
                     Ext.MessageBox.confirm(_("确认"),msg,function(id){
                        if (id == 'yes'){
                            user_annotation.setValue("");
                            user_name.setText("上次修改者:");
                            modified_by="";
                            var url="/node/process_annotation?node_id="+node.attributes.id;
                            save_annotation(url);

                      }});
//                }
            }

        }
     });

     var button_save=new Ext.Button({
        name: 'save',
        id: 'save',
        text:_('保存'),
        icon:'icons/accept.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                    var url="/node/process_annotation?node_id="+node.attributes.id;
//                    if (user_annotation.getValue()!="")
                    url+="&text="+escape(user_annotation.getValue());
                    if (modified_by!="")
                        url+="&user="+modified_by;
                    save_annotation(url);
            }

        }
     });


      var annotate_panel2=new Ext.Panel({
        height:190,
        border:true,
        width:'100%',
        labelAlign:'left',
        layout:'form',
        frame:false,
        labelSeparator:' ',
        id:"annotate_panel2",
        items:[annotate_panel1],
        bbar:[{xtype: 'tbfill'},button_clear,button_save,
                new Ext.Button({
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
            })

    ]
    });

    return annotate_panel2;
}

function save_annotation(url){
        var ajaxReq = ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                    Ext.MessageBox.alert( _("Success") , response.msg);
                }else{
                    Ext.MessageBox.alert( _("Failure") , response.msg);
                }
            },
            failure: function(xhr){
                Ext.MessageBox.alert( _("Failure") , xhr.statusText);
            }
        });
        closeWindow();


}