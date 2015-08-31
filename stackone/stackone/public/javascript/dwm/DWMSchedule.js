/*
*   Stackone---领先的以虚拟化为基础的私有云提供商   -  Copyright (c) 2008 Stackone Corp.
*   ======

* http://www.stackone.com.cn
* author : Benf<yangbf@stackone.com.cn>
*/



function DVM_Policy(node){


    var dummy_space=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space1=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space2=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space3=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space4=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space5=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space6=new Ext.form.Label({
        html:_('&nbsp;<div style="width:80px"/>')
    });
    var dummy_space7=new Ext.form.Label({
        html:_('&nbsp;<div style="width:80px"/>')
    });
    var dummy_space8=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space9=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space10=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space11=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space12=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space13=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space14=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space15=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space16=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });
    var dummy_space17=new Ext.form.Label({
        html:_('&nbsp;<div style="width:20px"/>')
    });
    var dummy_space18=new Ext.form.Label({
        html:_('&nbsp;<div style="width:10px"/>')
    });

    var labelWidth=240;
    var fieldWidth=40;
    var width=490;

    var DWM_label=new Ext.form.Label({
        html:'<div class="backgroundcolor" width="250">通过启用动态工作负载管理,\
                          你可以自动负载平衡该服务器池的所有虚拟机.均匀分布策略将确保服务器池中的服务器不致利用过度.节电策略，将更保持虚拟机可持续性，不致意外崩溃，同时自动节省电力.实现绿色环保.\
                            \
                          <br/><br/></div>'
    });

    var policy_lbl=new Ext.form.Label({
        html: _('<b>选择动态工作负载管理策略</b>'),
        bodyStyle:'padding:10px 0px 0px 0px'
    });

    var policy_lbl_panel=new Ext.Panel({
        height:30,
        border:false,
        width:width,
        labelAlign:'left',
        layout:'table',
        labelSeparator:' ',
        layoutConfig: {columns:2},
        id:"policy_lbl_panel",
        items: [
        {
//            labelWidth: labelWidth,
            layout:'form',
            border:false,
            items:[dummy_space17]
        },
        {
//            width: 127,
            layout:'form',
            border:false,
            items:[policy_lbl]
        }
      ]
    });
    
    var lb_schedule_lbl=new Ext.form.Label({
        html: _('运行策略在以下期间')
    });

    var ps_schedule_lbl=new Ext.form.Label({
        html: _('运行策略在以下期间')
    });
    
    var enable_dwm_label=new Ext.form.Label({
        html: _('<b>启用动态工作负载管理</b>')
    })  ;


    var lb_json_object_field=new Ext.form.TextField({
        fieldLabel: _('Lbjson_object'),
        name: 'lb_json_object',
        labelSeparator:'',
        width: 150,
        id: 'lb_json_object',
        allowBlank:true       
    });

    var ps_json_object_field=new Ext.form.TextField({
        fieldLabel: _('Psjson_object'),
        name: 'ps_json_object',
        width: 150,
        labelSeparator:'',
        id: 'ps_json_object',
        allowBlank:true
    });



    var lb_policy_id=new Ext.form.TextField({
        fieldLabel: _('lb_policyid'),
        name: 'lb_policyid',
        labelSeparator:'',
        width: 150,
        id: 'lb_policyid',
        allowBlank:true
    });

    var ps_policy_id=new Ext.form.TextField({
        fieldLabel: _('ps_policyid'),
        name: 'ps_policyid',
        labelSeparator:'',
        width: 150,
        id: 'ps_policyid',
        allowBlank:true
    });

    var enable_dwm= new Ext.form.Checkbox({
        name: 'enable_dwm',
        id: 'enable_dwm',
        width:20,
        listeners:{
            check:function(field,checked){
                if (!checked){
                    field_panel.disable();
                }
                else{
                    field_panel.enable();
                }

            }
        }
    });  
   

    var enable_dwm_panel=new Ext.Panel({
        id:"enable_dwm_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:33,
        bodyStyle:'padding-left:8px',
        items:[dummy_space18,enable_dwm,dummy_space,enable_dwm_label,dummy_space1]
    });
    

    var enable_lb_label=new Ext.form.Label({
        html: _('<b>启用均匀分布策略</b>')
    });


  
    var lb_threshold_label1=new Ext.form.Label({
        html: _(' %')
    });

    var lb_threshold=new Ext.form.NumberField({
        fieldLabel: _('分发负载当服务器CPU大于'),
        name: 'threshold',
        width: fieldWidth,
        labelSeparator:'',
        id: 'threshold',
        allowBlank:true

    });

    var lb_dataperiod_label1=new Ext.form.Label({
        html: _('分钟')
    });

    var lb_dataperiod=new Ext.form.NumberField({
        fieldLabel: _('超过'),
        name: 'lb_data_period',
        labelSeparator:'',
        width: fieldWidth,
        id: 'lb_data_period',
        allowBlank:true
    });
   

    var LB_thereshold_panel=new Ext.Panel({
        height:30,
        border:false,
        width:650,
        labelAlign:'left',
        layout:'table',
        labelSeparator:' ',
//        labelWidth: labelWidth,
        layoutConfig: {columns:7},
        id:"lb_thereshold_panel",
        items: [
        {            
            labelWidth: labelWidth,
//            width: 300,
            layout:'form',
            border:false,
            items:[lb_threshold]
        },
        {            
//            labelWidth: labelWidth,
//            width: 300,
            layout:'form',
            border:false,
            items:[dummy_space8]
        },
        {
//            width: 80,
            layout:'form',
            border:false,
            items:[lb_threshold_label1]
        },
{
//            labelWidth: labelWidth,
//            width: 300,
            layout:'form',
            border:false,
            items:[dummy_space16]
        },
        {
            labelWidth: 90,
//            width: 220,
            layout:'form',
            border:false,
            items:[lb_dataperiod]
        },
        {
            labelWidth: labelWidth,
//            width: 300,
            layout:'form',
            border:false,
            items:[dummy_space9]
        },
        {
            width: 50,
            layout:'form',
            border:false,
            items:[lb_dataperiod_label1]
        }
        ]
    });

    var lb_frequency_label1=new Ext.form.Label({
        html: _(' 分钟')
    });
   
    var lb_frequency=new Ext.form.NumberField({
        fieldLabel: _('重新评估每'),
        name: 'lb_frequency',
        labelSeparator:'',
        width: fieldWidth,
        id: 'lb_frequency',
        allowBlank:true
//        bodyStyle:'margin-left:50px'
    });    

    var LB_frequency_panel=new Ext.Panel({
        height:30,
        border:false,
        width:width,
        labelAlign:'left',
        layout:'table',
        labelSeparator:' ',
        labelWidth: labelWidth,
        layoutConfig: {columns:3},
        id:"lb_frequency_panel",
        items: [        
        {
            labelWidth: labelWidth,
//            width: 220,
            layout:'form',
            border:false,
            items:[lb_frequency]
        },
        {
            labelWidth: labelWidth,
//            width: 300,
            layout:'form',
            border:false,
            items:[dummy_space10]
        },
        {
//            width: 80,
            layout:'form',
            border:false,
            items:[lb_frequency_label1]
        }
        ]
    });

    

    var ps_threshold_label1=new Ext.form.Label({
        html: _(' %')
    });

    var ps_threshold=new Ext.form.NumberField({
        fieldLabel: _('合并服务器当CPU低于'),
        name: 'ps_threshold',
        width: fieldWidth,
        labelSeparator:'',
        id: 'ps_threshold',
        allowBlank:true

    });

   var ps_dataperiod_label1=new Ext.form.Label({
        html: _(' 分钟')
    });


    var ps_dataperiod=new Ext.form.NumberField({
        fieldLabel: _('超过'),
        name: 'ps_data_period',
        width: fieldWidth,
        labelSeparator:'',
        id: 'ps_data_period',
        allowBlank:true
    });

    var PS_thereshold_panel=new Ext.Panel({
        height:30,
        border:false,
        width:620,
        labelAlign:'left',
        layout:'table',
        labelSeparator:' ',
//        labelWidth: 480,
        layoutConfig: {columns:7},
        id:"ps_thereshold_panel",
        items: [
        {
            labelWidth: labelWidth,
//            width: 220,
            layout:'form',
            border:false,
            items:[ps_threshold]
        },
        {
//            labelWidth: labelWidth,
//            width: 300,
            layout:'form',
            border:false,
            items:[dummy_space11]
        },
        {
//            width: 80,
            layout:'form',
            border:false,
            items:[ps_threshold_label1]
        },
        {
//            labelWidth: labelWidth,
//            width: 300,
            layout:'form',
            border:false,
            items:[dummy_space15]
        },
        {
            labelWidth: 90,
//            width: 220,
            layout:'form',
            border:false,
            items:[ps_dataperiod]
        },
        {
//            labelWidth: labelWidth,
//            width: 300,
            layout:'form',
            border:false,
            items:[dummy_space12]
        },
        {
            width: 50,
            layout:'form',
            border:false,
            items:[ps_dataperiod_label1]
        }
        ]
    });
  

    var ps_frequency_label1=new Ext.form.Label({
        html: _(' 分钟')
    });

    var ps_frequency=new Ext.form.NumberField({
        fieldLabel: _('重新评估每'),
        name: 'ps_frequency',
        width: fieldWidth,
        labelSeparator:'',
        id: 'ps_frequency',
        allowBlank:true
//        bodyStyle:'margin-left:50px'
    });



    var PS_frequency_panel=new Ext.Panel({
        height:30,
        border:false,
        width:width,
        labelAlign:'left',
        layout:'table',
        labelSeparator:' ',
        labelWidth: labelWidth,
        layoutConfig: {columns:3},
        id:"ps_frequency_panel",
        items: [       
        {
            labelWidth: labelWidth,
//            width: 220,
            layout:'form',
            border:false,
            items:[ps_frequency]
        },
        {
            labelWidth: labelWidth,
//            width: 300,
            layout:'form',
            border:false,
            items:[dummy_space13]
        },
        {
//            width: 80,
            layout:'form',
            border:false,
            items:[ps_frequency_label1]
        }
        ]
    });



     var ps_below_label1=new Ext.form.Label({
        html: _(' %')
    });

    var ps_low_freq=new Ext.form.NumberField({
        fieldLabel: _('保持服务器CPU低于'),
        name: 'ps_freq',
        width: fieldWidth,
        labelSeparator:'',
        id: 'ps_freq',
        allowBlank:true
//        bodyStyle:'margin-left:50px'
    });



    var PS_low_freq_panel=new Ext.Panel({
        height:30,
        border:false,
        width:width,
        labelAlign:'left',
        layout:'table',
        labelSeparator:' ',
        labelWidth: labelWidth,
        layoutConfig: {columns:3},
        id:"ps_freq_panel",
        items: [
        {
            labelWidth: labelWidth,
//            width: 220,
            layout:'form',
            border:false,
            items:[ps_low_freq]
        },
        {
            labelWidth: labelWidth,
//            width: 300,
            layout:'form',
            border:false,
            items:[dummy_space14]
        },
        {
//            width: 80,
            layout:'form',
            border:false,
            items:[ps_below_label1]
        }
        ]
    });


    var enable_ps_label=new Ext.form.Label({
        html: _('<b>启用节电策略</b>')
    });


    var enable_LB=new Ext.form.Radio({
//        boxLabel: _(''),
        hideLabel:true,
        id:'enable_lb',
        name:'enable',
        listeners:{
            check:function(field,checked){
                if(!checked){
                    lb_frequency.disable();
                    lb_threshold.disable();
                    lb_dataperiod.disable()
                    lb_schedule_btn.disable();
                }else{
                   lb_frequency.enable();
                   lb_frequency.setValue(stackone.constants.DWM_FREQUENCY);
                   lb_threshold.enable();
                   lb_threshold.setValue(stackone.constants.DWM_THRESHOLD);
                   lb_dataperiod.enable()
                   lb_dataperiod.setValue(stackone.constants.DWM_DATA_PERIOD);
                   lb_schedule_btn.enable();
                }
            }
        }
    });

    var lb_desc=_('均匀分布策略将确保服务器池中的服务器不致利用过度.');
    var tooltip_lb=new Ext.form.Label({
       html:'<img src=icons/information.png onClick=show_desc("'+escape(lb_desc)+'") />'
     })

    var enable_lb_panel=new Ext.Panel({
        id:"enable_lb_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        labelWidth:labelWidth,
        height:33,
        bodyStyle:'padding-left:10px',
        items:[enable_LB,dummy_space2,enable_lb_label,dummy_space3,tooltip_lb]
    });

   var enable_PS=new Ext.form.Radio({
//        boxLabel: _(''),
        hideLabel:true,
        id:'enable_ps',
        name:'enable',
        listeners:{
            check:function(field,checked){
                if(!checked){
                    ps_frequency.disable();
                    ps_threshold.disable();
                    ps_dataperiod.disable();
                    ps_low_freq.disable();
                    ps_schedule_btn.disable();
                }else{                   
                   ps_frequency.enable();
                   ps_frequency.setValue(stackone.constants.DWM_FREQUENCY);
                   ps_threshold.enable();
                   ps_threshold.setValue(stackone.constants.DWM_PS_THRESHOLD);
                   ps_dataperiod.enable();
                   ps_dataperiod.setValue(stackone.constants.DWM_DATA_PERIOD);
                   ps_low_freq.enable();
                   ps_low_freq.setValue(stackone.constants.DWM_THRESHOLD);
                   ps_schedule_btn.enable();
                }
            }
        }
    });

    var ps_desc=_('节电策略，将更保持虚拟机可持续性，不致意外崩溃，同时自动节省电力.实现绿色环保. ');
    var tooltip_ps=new Ext.form.Label({
        html:'<img src=icons/information.png onClick=show_desc("'+escape(ps_desc)+'") />'
     })


    var enable_ps_panel=new Ext.Panel({
        id:"enable_ps_panel",
        layout:"column",
        frame:false,
        width:'100%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        height:33,
        bodyStyle:'padding-left:10px',
        items:[enable_PS,dummy_space4,enable_ps_label,dummy_space5,tooltip_ps]
    });

    var url=""
    url="/dwm/get_dwm_details?group_id="+node.attributes.id;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
            success: function(xhr) {
                var response=Ext.util.JSON.decode(xhr.responseText);
                if(response.success){
                    var info=response.msg;
                    enable_dwm.setValue(false);
                    for (var i=0;i<=info.length-1;i++){
                        if (info[i].policy == stackone.constants.LOAD_BALANCING){                            

                            enable_dwm.setValue(info[i].dwm_enabled);
                            enable_LB.setValue(info[i].enabled);
                            lb_frequency.setValue(info[i].frequency);
                            lb_threshold.setValue(info[i].threshold);
                            lb_dataperiod.setValue(info[i].data_period);
                            lb_json_object_field.setValue(info[i].scobject);
                            lb_policy_id.setValue(info[i].policy_id);

                        }
                        else if(info[i].policy == stackone.constants.POWER_SAVING){

                            enable_dwm.setValue(info[i].dwm_enabled);
                            enable_PS.setValue(info[i].enabled);
                            ps_frequency.setValue(info[i].frequency);
                            ps_threshold.setValue(info[i].threshold);
                            ps_dataperiod.setValue(info[i].data_period);;
                            ps_json_object_field.setValue(info[i].scobject);
                            ps_policy_id.setValue(info[i].policy_id);                          
                            ps_low_freq.setValue(info[i].up_threshold);                            
                        }
                    }
                }else{
//                    Ext.MessageBox.alert("Failure",response.msg);
                    }
            },
            failure: function(xhr){
//                Ext.MessageBox.alert( "Failure " , xhr.statusText);
                }
    });


    var lb_schedule_btn=new Ext.Button({
        id: 'Schedule',
        text: _('时间表'),
//        icon:'icons/accept.png',
        cls:'x-btn-text',
        width:fieldWidth,
        listeners: {
            click: function(btn) {                
                    DWMSchedule_window(stackone.constants.LOAD_BALANCING,node.attributes.id,"EDIT",lb_policy_id.getValue(),lb_json_object_field.getValue());
               
            }
        }
    });


     var panel1=new Ext.Panel({
        height:30,
        border:false,
        width:width,
        labelAlign:'left',
        layout:'table',
        labelSeparator:' ',
        labelWidth: labelWidth,
        layoutConfig: {columns:3},
        id:"lb_panel",
        items: [
        {
            labelWidth: labelWidth,
            layout:'form',
            border:false,
            items:[lb_schedule_lbl]
        },
        {
            width: 127,
            layout:'form',
            border:false,
            items:[dummy_space6]
        },
        {
//            labelWidth: 50,
            layout:'form',
            border:false,
            items:[lb_schedule_btn]
        }]
    });

    var ps_schedule_btn=new Ext.Button({
       id: 'Schedule1',
        text: _('时间表'),
//        icon:'icons/accept.png',
        width:fieldWidth,
        cls:'x-btn-text',
        listeners: {
            click: function(btn) {
                DWMSchedule_window(stackone.constants.POWER_SAVING,node.attributes.id,"EDIT",ps_policy_id.getValue(),ps_json_object_field.getValue());
                
            }
        }
    });

    var panel2=new Ext.Panel({
        height:30,
        border:false,
        width:width,
        labelAlign:'left',
        layout:'table',
        labelSeparator:' ',
        layoutConfig: {columns:3},
        id:"ps_panel",
        items: [        
        {
            labelWidth: labelWidth,
            layout:'form',
            border:false,
            items:[ps_schedule_lbl]
        },
        {
            width: 127,
            layout:'form',
            border:false,
            items:[dummy_space7]
        },
        {
//            labelWidth: 50,
            layout:'form',
            border:false,
            items:[ps_schedule_btn]
        }]
    });   

    
    var cancel_button= new Ext.Button({
       id: 'cancel',
        text: _('关闭'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                closeWindow();
            }
        }
    });    
    
          
    var save= new Ext.Button({
       id: 'ok',
        text: _('保存'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var lbval=lb_json_object_field.getValue();
                var psval=ps_json_object_field.getValue();
                var policy_array = [];
                if (enable_dwm.getValue()){
                    var policy_selected=false;
                    if(enable_LB.getValue()){
                        if(lbval == null || lbval == "" || lbval==" "){
                            Ext.MessageBox.alert( "警告" ,"请选择均匀分布策略时间表 " );
                            return;
                        }
                        if(parseInt(lb_frequency.getValue())==0){
                            Ext.MessageBox.alert( "警告" ,"请选择一个非0时间（单位为分钟）" );
                            return;
                        }

                        var lb_policy=new Object();
                        lb_policy.schedule_object=lb_json_object_field.getValue();
                        lb_policy.frequency=lb_frequency.getValue();
                        lb_policy.threshold=lb_threshold.getValue();
                        lb_policy.data_period=lb_dataperiod.getValue();
                        lb_policy.policy_name=stackone.constants.LOAD_BALANCING;
                        lb_policy.upper_threshold=0;
                       
                        policy_array.push(lb_policy);
                        policy_selected=true;
                    }
                    if(enable_PS.getValue()){
                        if(psval == null || psval == "" || psval==" "){
                            Ext.MessageBox.alert( "警告" ,"请选择节电政策的时间表 " );
                            return;
                        }
                        if(parseInt(ps_frequency.getValue())==0){
                            Ext.MessageBox.alert( "警告" ,"请选择一个非0时间（单位为分钟" );
                            return;                           
                        }

                        var ps_policy=new Object();
                        ps_policy.schedule_object=ps_json_object_field.getValue();
                        ps_policy.frequency=ps_frequency.getValue();
                        ps_policy.threshold=ps_threshold.getValue();
                        ps_policy.data_period=ps_dataperiod.getValue();
                        ps_policy.policy_name=stackone.constants.POWER_SAVING;
                        ps_policy.upper_threshold=ps_low_freq.getValue();

                        policy_array.push(ps_policy);
                        policy_selected=true;
                    }
                    if (policy_selected == false){
                        Ext.MessageBox.alert( "警告" ,"请允许任何一个策略" );
                        return;

                    }

                }
                var policy_object=new Object();
                policy_object.policies=policy_array;
 
                var json_policy_object=Ext.util.JSON.encode({
                    "policy_object":policy_object
                });
             
                var offsetmillis=parseInt((new Date()).getTimezoneOffset())*60*1000;
                
                url="/dwm/save_dwm_details?group_id="+node.attributes.id+"&policy_object="+
                        json_policy_object+"&enabled="+enable_dwm.getValue()+"&offset="+offsetmillis;
                var ajaxReq=ajaxRequest(url,0,"GET",true);
                ajaxReq.request({
                    success: function(xhr) {
                        var response=Ext.util.JSON.decode(xhr.responseText);
                        if(response.success){
                            Ext.MessageBox.alert("成功","已经成功保存");
                            closeWindow();
                        }else{
                            Ext.MessageBox.alert("失败",response.msg);
                            }
                    },
                    failure: function(xhr){
                        Ext.MessageBox.alert( "失败 " , xhr.statusText);
                        }
                });

                
            }
        }
    });


     var lb_fields_and_but=new Ext.Panel({
        id:"lb_fields_and_but",
        layout:"form",
        labelWidth:labelWidth,
        width:'100%',
        bodyStyle:'padding-left:40px',
        items:[LB_thereshold_panel,LB_frequency_panel, panel1]
    });


     var ps_fields_and_but=new Ext.Panel({
        id:"ps_fields_and_but",
        layout:"form",
        labelWidth:labelWidth,
        width:'100%',
        bodyStyle:'padding-left:40px',
        items:[PS_thereshold_panel,PS_low_freq_panel,PS_frequency_panel, panel2]
    });

    var fldset=new Ext.form.FieldSet({
        id:'fldset',
        collapsible: false,
        autoHeight:true,
        labelSeparator:' ',
        width: 620,
        labelWidth:labelWidth,
        collapsed: false,
        border: false,
        items :[enable_lb_panel, lb_fields_and_but]
    });
    var fldset1=new Ext.form.FieldSet({
        id:'fldset1',
        collapsible: false,
        autoHeight:true,
        labelSeparator:' ',
        width: 620,
        labelWidth:labelWidth,
        collapsed: false,
        border: false,
        items :[enable_ps_panel, ps_fields_and_but]
    });

    var label1=new Ext.form.Label({
         html:'<div class="toolbar_hdg">'+_("选择动态工作负载管理策略")+'</div>'
    });

    var field_panel= new Ext.Panel({
        bodyStyle:'padding:0px 0px 0px 0px',
//        layout:"form",
        frame:false,
        width:'100%',
        height:'60%',
        items:[fldset,fldset1]
//        tbar:[label1,{xtype: 'tbfill'}]
    });

    lb_frequency.disable();
    lb_threshold.disable();
    lb_dataperiod.disable()
    lb_schedule_btn.disable();

    ps_frequency.disable();
    ps_threshold.disable();
    ps_dataperiod.disable();
    ps_low_freq.disable();
    ps_schedule_btn.disable();
    
    field_panel.disable();     

    var panel = new Ext.FormPanel({
        bodyStyle:'padding:0px 0px 0px 0px',
        layout:"form",
        frame:true,
        width:'100%',
        height:500,
        items:[enable_dwm_panel,policy_lbl_panel,field_panel],
        bbar:[{xtype: 'tbfill'},save,cancel_button]        
    });


  return panel
}

function DWMSchedule_window(dwm,node_id,mode,policy_id,scobject){

    var checkBoxSelMod = new Ext.grid.CheckboxSelectionModel({
        singleSelect:false
    });

    var columnModel = new Ext.grid.ColumnModel([
        checkBoxSelMod,
        {
            header: _("类型"),
//            width:110,
            dataIndex: 'type',
            sortable:true,
            hidden:true
        },
        {
            header: _("天"),
            width:220,
            dataIndex: 'day',
            sortable:true
        },
        {
            header: _("开始时间"),
//            width: 140,
            sortable:true,
            dataIndex: 'starttime'
        },
        {
            header: _("持续时间(Hrs)"),
//            width: 100,
            sortable:true,
            dataIndex: 'duration'
        },
        {
            header: _("Scobject"),
//            width: 100,
            sortable:true,
            dataIndex: 'scobject',
            hidden:true
        }
    ]);

//
//    if (mode=="EDIT"){
//        alert(policy_id);
//        var params="group_id="+node_id+"&policy_id="+policy_id;
//
//    }

//    var params="group_id="+node_id+"&policy_id="+policy_id;
//    var get_dwmstore =new Ext.data.JsonStore({
//        url:"/dwm/get_dwm_schedule_details?"+params,
//        root: 'info',
//        successProperty:'success',
//        fields:['type','day','starttime','duration','scobject'],
//        listeners:{
//
//            loadexception:function(obj,opts,res,e){
//                var store_response=Ext.util.JSON.decode(res.responseText);
//                Ext.MessageBox.alert(_("Error"),store_response.msg);
//            }
//        }
//
//    });
//
//    get_dwmstore.load();


    var get_dwmstore =new Ext.data.SimpleStore({
        fields:['type','day','starttime','duration','scobject']
    })
    
    var policy_rec = Ext.data.Record.create([
        {
            name: 'type',
            type: 'string'
        },
        {
            name: 'day',
            type: 'string'
        },
        {
            name: 'starttime',
            type: 'string'
        },
        {
            name: 'duration',
            type: 'string'
        },
        {
            name: 'scobject',
            type: 'string'
        }

    ]);


//    var scobject=lb_json_object_field.getValue();
    if (scobject){
        
        for(var i=0;i< scobject.length;i++){
            var sc_obj=scobject[i];
            var new_entry=new policy_rec({
                type:sc_obj.type,
                starttime:sc_obj.starttime,
                day:sc_obj.day,
                duration:sc_obj.duration,
                scobject:sc_obj
            });
            get_dwmstore.insert(0,new_entry);
        }
    }

    var edit_button=new Ext.Button({
        name: 'edit_var',
        id: 'edit_var',
        text:_("编辑"),
        icon:'icons/file_edit.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var rec=grid.getSelectionModel().getSelected();
                var index=grid.getStore().indexOf(rec);
//                grid.getStore().remove(rec);             
                if(rec){
                    var obj=rec.get('scobject');
                    DWMScheduleUI(grid,node_id,"EDIT",obj,index);
//                    grid.getStore().remove(rec);
                }else{
                    Ext.MessageBox.alert(_("警告"),_("请选择一个时间表"));
                    return;
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
            click: function(btn) {
                 win.close();
            }
        }
    });    

    var grid = new Ext.grid.EditorGridPanel({
        store: get_dwmstore,
        colModel:columnModel,
        stripeRows: true,
        frame:false,
        selModel:checkBoxSelMod,
        width:'100%',
        autoExpandColumn:1,
        height:320,
        id:"Json_grid",
        clicksToEdit:2,
        enableHdMenu:false,
        region: 'center',
		border : false,
		bodyBorder : false,
        tbar:[{xtype: 'tbfill'},
             new Ext.Button({
                name: 'add_var',
                id: 'add_var',
                text:_("添加"),
                icon:'icons/add.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        DWMScheduleUI(grid,node_id,"NEW",null,null);
                    }
                }
            }),
             '-',edit_button
            ,
            '-',
            new Ext.Button({
                name: 'remove_var',
                id: 'remove_var',
                text:_("移除"),
                icon:'icons/delete.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        grid.getStore().remove(grid.getSelectionModel().getSelected());
                    }
                }
            })
        ],
        listeners: {
            rowdblclick: function(grid ,rowIndex,columnIndex,e,b) {
                edit_button.fireEvent('click',edit_button);
            }
        }

    });   


    var save= new Ext.Button({
        id: 'ok',
        text: _('确定'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var jsonobject_list=new Array();
                var recs=grid.getStore().getRange(0,grid.getStore().getCount());                
                for(var i=0;i<recs.length;i++){
                    var object=recs[i]
                    var obj=object.get('scobject')
                    jsonobject_list[i]=obj;
                }    
                if (dwm == stackone.constants.POWER_SAVING){
                    Ext.getCmp("ps_json_object").setValue(jsonobject_list);                    
                }else if (dwm == stackone.constants.LOAD_BALANCING){
                    Ext.getCmp("lb_json_object").setValue(jsonobject_list);                    
                }
                win.close();
            }
        }
    });
   

    var panel = new Ext.Panel({
		height : 400,
		layout : "form",
		frame : false,
		width : '100%',
		autoScroll : true,
		border : false,
		bodyBorder : false,
//		bodyStyle : 'padding:5px 5px 5px 5px',
		items : [grid],
		cls : 'whitebackground',
		bbar : [{
			xtype : 'tbfill'
		}, save, cancel_button]
	});

	var title = "时间表详情 " + eval("stackone.constants.POLICY_NAMES." + dwm);

	var win = new Ext.Window({
		title : title,
		width : 470,
		layout : 'fit',
		height : 400,
		modal : true,
		resizable : false,
		closable : false
	});

    win.add(panel);
    win.show();
    
}

function DWMScheduleUI(schedule_summary_grid,node_id,mode,object,row_index){

    var date=new Date();
    var hrs=date.getHours();
    var mins=date.getMinutes();
    var mod=(mins+5)-(mins%5);
    var time=hrs+":"+((mod<10)?"0":"")+mod;


    var duration_time=new Ext.form.TimeField({
        fieldLabel: _('持续时间(Hrs)'),
        name: 'duration',
        disabled:false,
        format:'H',
        anchor:'60%',
        id: 'duration',
//        minValue:'01',
        value:time,
        increment:60
    });
    
    var start_time=new Ext.form.TimeField({
        fieldLabel: _('开始时间'),
        name: 'starttime',
        disabled:false,
        format:'H:i',
        anchor:'60%',
        id: 'starttime',
//        minValue:'12:00',
        value:time,
        increment:30
    });

    var label_str =""

    var week_array = [],week_label_array = [];

    for(var i=0; i<7; i++)
    {
        label_str = "";
    
        switch (i) {
        case 0:
           label_str = "周一";
            break;
        case 1:
           label_str = "周二";
            break;
        case 2:
            label_str = "周三";
            break;
        case 3:
            label_str = "周四";
            break;
        case 4:
            label_str = "周五";
            break;
        case 5:
            label_str = "周六";
            break;
        case 6:
            label_str = "周日";
            break;
        }

        var weekday_checkBox=  new Ext.form.Checkbox({
            name: 'WDay'+i,
            checked: false,
            boxLabel: label_str,
            width : 100
        });

        week_array[i]= weekday_checkBox;
        week_label_array[i]= label_str;

    }

    var Week_checkBoxgroup = new Ext.form.CheckboxGroup({
        id:'week_checkBoxgroup',
        xtype: 'checkboxgroup',
        fieldLabel: "星期",
        itemCls: 'x-check-group-alt',
        width:"100%",
        //disabled: true,
        // Put all controls in a single column with width 100%
        columns: 1,
        items:
        [
                week_array[0],
                week_array[1],
                week_array[2],
                week_array[3],
                week_array[4],
                week_array[5],
                week_array[6]



        ]
    });


//    var month_array = [],monthday_stat_label=[];
//
//    for(var i=1; i<=31; i++)
//    {
//        label_str = ""+ i;
//
//        var monthday_checkBox=  new Ext.form.Checkbox({
//            name: 'MDay'+i,
//            checked: false,
//            boxLabel: label_str,
//            width: 50
//        });
//        month_array[i]= monthday_checkBox;
//        monthday_stat_label[i]=i;
//
//    }
//
//    var Month_checkBoxgroup = new Ext.form.CheckboxGroup({
//        id:'month_checkBoxgroup',
//        xtype: 'checkboxgroup',
//        fieldLabel: "Day of the Month",
//        itemCls: 'x-check-group-alt',
//        disabled: true,
//        // Put all controls in a single column with width 100%
//        columns: 4,
//        items: [
//            month_array[1],
//            month_array[2],
//            month_array[3],
//            month_array[4],
//            month_array[5],
//            month_array[6],
//            month_array[7],
//            month_array[8],
//            month_array[9],
//            month_array[10],
//            month_array[11],
//            month_array[12],
//            month_array[13],
//            month_array[14],
//            month_array[15],
//            month_array[16],
//            month_array[17],
//            month_array[18],
//            month_array[19],
//            month_array[20],
//            month_array[21],
//            month_array[22],
//            month_array[23],
//            month_array[24],
//            month_array[25],
//            month_array[26],
//            month_array[27],
//            month_array[28],
//            month_array[29],
//            month_array[30],
//            month_array[31],
//
//
//        ]
//    });
//
//    var MonthDatestore = new Ext.data.SimpleStore({
//        fields: ['dataFieldName', 'displayFieldName'],
//        data: [['1', '1'], ['2', '2'], ['3', '3'], ['4', '4'],['5', '5'],['6', '6'],['7', '7'], ['8', '8'], ['9', '9'], ['10', '10'],['11', '11'], ['12', '12'], ['13', '13'], ['14', '14'],['15', '15'],['16', '16'],['17', '17'], ['18', '18'], ['19', '19'], ['20','20'], ['21', '21'], ['22', '22'], ['23', '23'], ['24', '24'], ['25', '25'], ['26', '26'], ['27', '27'], ['28', '28'], ['29', '29'], ['30', '30']]
//
//    });



    var scheduleType_combo=new Ext.form.ComboBox({
        //anchor:'90%',
        id: 'scheduleType_combo',
        width:100,
        minListWidth: 120,
        fieldLabel:"频率",

        allowBlank:false,
        triggerAction:'all',
        editable: false,
        store:[//['Hourly',_('Hourly')],
                ['Daily',_('Daily')],
                ['Weekly',_('Weekly')]
//                ['Monthly',_('Monthly')],
               ],
        forceSelection: true,
        mode:'local',
        value: 'Weekly',
        listeners: {

                select: function(combo, record, index){
                   
                    if (combo.getValue() == 'Daily')
                    {
                        Week_checkBoxgroup.disable();
//                        hideField(Week_checkBoxgroup);
//                        hideField(Month_checkBoxgroup);

                    }
                    else if (combo.getValue() == 'Weekly')
                    {
                        Week_checkBoxgroup.enable();
//                        showField(Week_checkBoxgroup);
//                        hideField(Month_checkBoxgroup);
                    }                   
//                    else if(combo.getValue() == 'Monthly')
//                    {
//
//                        hideField(Week_checkBoxgroup);
//                        showField(Month_checkBoxgroup);
//                    }
                }
        }

    });

    
    var scheduleType_combo_Group = {
        xtype: 'fieldset',
        border: false,
        id: 'scheduleType_combo_Group',
        autoHeight: true,
        labelWidth: 110,
        items: [
        {
            layout:'column',
            border:false,
            width: 320,
            //labelWidth: 100,
            items:[
            {
                columnWidth:1.0,
                border:false,
                width: 270,
                layout: 'form',
                labelWidth: 110,
                items: [scheduleType_combo]

            }]

        },        
        start_time,
        duration_time,
        Week_checkBoxgroup
//        Month_checkBoxgroup,

        ]
    }      
    
    var rec = Ext.data.Record.create([
        {
            name: 'type',
            type: 'string'
        },
        {
            name: 'day',
            type: 'string'
        },
        {
            name: 'starttime',
            type: 'string'
        },
        {
            name: 'duration',
            type: 'string'
        },
        {
            name: 'scobject',
            type: 'string'
        }

    ]);

    if (mode=="EDIT"){     
        duration_time.setValue(object.duration);
        start_time.setValue(object.starttime);
        scheduleType_combo.setValue(object.type);

        if (object.type == 'Weekly'){
            
            var weekdays=object.dows;
            for (var j=0;j<weekdays.length;j++){
                var index=weekdays[j];
                week_array[index].setValue(true);
            }

        }else if (object.type == 'Daily'){
//            hideField(Week_checkBoxgroup);
//            Ext.getCmp("week_checkBoxgroup").setVisible(false);
            Ext.getCmp("week_checkBoxgroup").disable();
//            scheduleType_combo.setValue(object.type)
        }
    }

    var save= new Ext.Button({
        id: 'ok',
        text: _('确定'),
        icon:'icons/add.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {
                var schedule_object=new Object();   
                schedule_object.type= scheduleType_combo.getValue();
                schedule_object.starttime= start_time.getValue();
                schedule_object.duration=duration_time.getValue();
                var dows="",weekdays_list="";
                for(var i=0;i<7;i++){
                    if (week_array[i].getValue())
                    {
                    //dows+="{";
                    //dows+="'id':";
                        if(dows != "")
                        {
                            dows+=",";
                            weekdays_list+=", ";
                        }

                        weekdays_list+=week_label_array[i];
                        dows+=i;
                    }
                }
                  
//                    var monthday_stat="", monthday_stat_text="";
//                    for(var j=1;j<=31;j++){
//                        if (month_array[j].getValue())
//                        {
//
//                            if(monthday_stat != "")
//                            {
//                                monthday_stat+=",";
//
//                                monthday_stat_text+=",";
//                            }
//
//                                monthday_stat_text+=j;
//                                monthday_stat+=j;
//                        }
//                    }
//
                var day="";
                if(scheduleType_combo.getValue() == "Weekly") {
                    day=weekdays_list;

                    var dow_list=new Array();
                    var dow=dows.split(',')
                    for (var i=0;i<dow.length;i++){
                        dow_list[i]=dow[i]

                    }
                     
                     

                    var weekdaylist=new Array();
                    var weekday_list=weekdays_list.split(',')
                    for (var i=0;i<weekday_list.length;i++){
                        weekdaylist[i]=weekday_list[i]

                    }
                     

                    schedule_object.dows = dow_list;
                    schedule_object.weekdays_list =weekdaylist ;
                    if(dows == "") {
                        Ext.MessageBox.alert(_("信息"),_("请选择周的一天"));
                        return;
                    }
                }
//                    else if(scheduleType_combo.getValue() == "Monthly") {
//                        day=monthday_stat_text
//                        if(monthday_stat == "") {
//                            Ext.MessageBox.alert(_("Info"),_("Please select day of the month"));
//                            return;
//                        }
//                    }
                else{
                    day='Daily';
                }

                schedule_object.day = day;                
//                    schedule_object.monthday_stat = monthday_stat;
//                    schedule_object.monthday_stat_text = monthday_stat_text;

                var new_entry=new rec({
                    type:scheduleType_combo.getValue(),
                    starttime:start_time.getValue(),
                    day:day,
                    duration:duration_time.getValue(),
                    scobject:schedule_object
                });
                if (mode =="EDIT"){                   
                    var del_record=schedule_summary_grid.getStore().getAt(row_index);                  
                    schedule_summary_grid.getStore().remove(del_record);
                    schedule_summary_grid.getStore().insert(row_index,new_entry);
                }else{
                    schedule_summary_grid.getStore().insert(0,new_entry);
                }
                win.close();
            }
        }
    });

    var cancel_button= new Ext.Button({
       id: 'cancel',
        text: _('取消'),
        icon:'icons/cancel.png',
        cls:'x-btn-text-icon',
        listeners: {
            click: function(btn) {                 
                win.close();
            }
        }
    });    
    var schedule_panel=new Ext.Panel({
        height:350,
        layout:"form",
        frame:false,
        width:'90%',
        autoScroll:true,
        border:false,
        bodyBorder:false,
        cls: 'whitebackground',
        bodyStyle:'padding:5px 5px 5px 5px',
        items:[scheduleType_combo_Group],
        bbar:[{xtype: 'tbfill'},save,cancel_button]
    });
//     Ext.getCmp("month_checkBoxgroup").setVisible(false);


    var win=new Ext.Window({
        title:"时间表",
        width: 400,
        layout:'fit',
        height: 410,
        modal: true,
        resizable: false,
        closable:false
    });

    win.add(schedule_panel);
    win.show();

}