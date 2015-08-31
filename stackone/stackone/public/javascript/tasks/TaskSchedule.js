/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
function showScheduleWindow(node,msg,url,action,params){
    
//    var date=new Date();
//    var hrs=date.getHours();
//    var mins=date.getMinutes();
//    var mod=(mins+5)-(mins%5);
//    var time=hrs+":"+((mod<10)?"0":"")+mod;
//    var schdate=new Ext.form.DateField({
//        fieldLabel: _('Date'),
//        name: 'schdate',
//        disabled:true,
//        anchor:'100%',
//        minValue:date,
//        id: 'schdate',
//        value:date
//    });
//
//    var schtime=new Ext.form.TimeField({
//        fieldLabel: _('Time'),
//        name: 'schtime',
//        disabled:true,
//        format:'H:i',
//        anchor:'100%',
//        id: 'schtime',
//        //minValue:'12:00',
//        value:time,
//        increment:5
//    });
//
//    var msg_lbl=new Ext.form.Label({
//         html:'<b>'+ _(msg) +'</b><br/><br/>'
//     });
//
//     var later=new Ext.form.Checkbox({
//         fieldLabel:_('Schedule?'),
//         //boxLabel: _('Later'),
//         id:'later',
//         name:'sch',
//         labelAlign:'left',
//         listeners:{
//             check:function(field,checked){
//                 if(checked){
//                     schdate.enable();
//                     schtime.enable();
//                 }
//                 else{
//                     schdate.disable();
//                     schtime.disable();
//                 }
//             }
//         }
//     });
//
//
//    var later_fldset=new Ext.form.FieldSet({
//        collapsible: false,
//        anchor:'100% 80%',
//        labelWidth:90,
//        layout:'form',
//        items: [later,schdate,schtime]
//    });
//
//    var count=new Ext.form.NumberField({
//        fieldLabel: _("After"),
//        name: 'count',
//        disabled:true,
//        width: 100,
//        id: 'count'
//    });
//
//    var interval=new Ext.form.ComboBox({
//        width:100 ,
//        fieldLabel:_("Interval"),
//        triggerAction:'all',
////        displayField:'value',
////        valueField:'id',
//        editable: false,
//        value:'minutes',
//        disabled:true,
//        store:[['minutes',_('Minutes')],['hours',_('Hours')],['days',_('Days')]],
//        mode:'local',
//        id:'interval'
//    });
//
//    var after_fldset=new Ext.form.FieldSet({
//        collapsible: false,
//        autoHeight:true,
//        anchor:'100%',
//        labelWidth:50,
//        layout:'column',
//        items: [{
//            width: 160,
//            layout:'form',
//            items:[count]
//        },{
//            width: 160,
//            layout:'form',
//            items:[interval]
//        }]
//    });
//
//    var now=new Ext.form.Radio({
//        boxLabel: _('Now'),
//        id:'now',
//        name:'sch',
//        checked:true,
//        listeners:{
//            check:function(field,checked){
//                if(checked){
//                    schdate.disable();
//                    schtime.disable();
//                    count.disable();
//                    interval.disable();
//                }
//            }
//        }
//    });

////    var later=new Ext.form.Radio({
////        boxLabel: _('Later'),
////        id:'later',
////        name:'sch',
////        listeners:{
////            check:function(field,checked){
////                if(checked){
////                    schdate.enable();
////                    schtime.enable();
////                    count.disable();
////                    interval.disable();
////                }
////            }
////        }
////    });
////
////    var after=new Ext.form.Radio({
////        boxLabel: _('After'),
////        id:'after',
////        name:'sch',
////        listeners:{
////            check:function(field,checked){
////                if(checked){
////                    schdate.disable();
////                    schtime.disable();
////                    count.enable();
////                    interval.enable();
////                }
////            }
////        }
////    });
////
////    var taskSch = new Ext.form.RadioGroup({
////        fieldLabel: _("Schedule"),
////        anchor:'100%',
////        columns: 2,
////        items: [now,later]
////    });
//
//    var task_sch = new Ext.FormPanel({
//        labelWidth:100,
//        frame:true,
//        border:0,
//        labelAlign:"left" ,
//        width:280,
//        height:180,
//        labelSeparator: ' ',
//        items:[later_fldset]
//    });
//
//    task_sch.addButton(_("OK"),function(){
//
//        if(later.getValue()){
//            url+="&date="+schdate.getValue()+"&time="+schtime.getValue();
//        }
//        window.close();
        if(action=='PROVISION_VM' || action=='EDIT_VM_INFO'){
            vm_config_settings(node,url,action);
        }else if(action=='migrate'){
            var destnode=params.dest_node;
            var live=params.live;
            var force=params.force;
            var vm=params.vm;
            runMigration(url,force,params.src_node,destnode,vm,params.node,live); 
        }else if(action=='import'){
            var image_name=params.image_name;
            var param=params.params;
            import_Appliance_sch(url,image_name,node,param)
        }else{
            confirmAction(node,url,'yes',action);
        }
//
//    });
//    task_sch.addButton(_("Cancel"),function(){
//        window.close();
//    });
//
//    //showWindow(_("Schedule Task:-")+msg,415,220,task_sch);
//
//    var window = new Ext.Window({
//        title:_("Confirm"),
//        width: 300,
//        autoHeight:true,
//        minWidth: 300,
//        minHeight: 200,
//        layout: 'fit',
//        plain:true,
//        resizable:false,
//        bodyStyle:'padding:5px;',
//        buttonAlign:'center',
//        items: [msg_lbl,task_sch]
//    });
//
//    window.show();

}
