/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var file_browser,appl_panel;
function ImportApplianceDialog(image_group,appliance){
    var grpid = image_group.attributes.nodeid;
    var is_manual=(appliance==null);
    var description="",link="";

    var location=new Ext.form.TriggerField({
        fieldLabel: _('位置'),
        name: 'location',
        allowBlank:false,
        id: 'location',
        labelStyle: 'font-weight:bold;',
        width:420,
        disabled:!is_manual,
        triggerClass : "x-form-search-trigger"
    });
    location.onTriggerClick = function(){
        if(is_manual){
            file_browser=new Ext.Window({title:_("选择应用"),width : 515,height: 425,modal : true,resizable : false});
            file_browser.add(FileBrowser("/","","",true,false,location,file_browser));
            file_browser.show();
        }
    };

    var img_name=new Ext.form.TextField({
        fieldLabel: _('模板名称'),
        name: 'img_name',
        allowBlank:false,
        id: 'img_name',
        labelStyle: 'font-weight:bold;',
        width:250
    });

//    var img_grp=new Ext.form.TextField({
//        fieldLabel: _('Template Group'),
//        name: 'img_grp',
//        id: 'img_grp',
//        labelStyle: 'font-weight:bold;',
//        width:250
//        value:image_group.text,
//        disabled:true
//    });
  
    var grp_store = new Ext.data.JsonStore({
        url: '/template/get_image_groups',
        root: 'nodes',
        fields: ['NODE_NAME', 'NODE_ID','NODE_TYPE'],
        sortInfo:{
            field:'NODE_NAME',
            direction:'ASC'
        },
        id:'NODE_ID',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            },
            load:function(store,recs,opts){
                if(image_group.attributes.nodetype == stackone.constants.IMAGE_GROUP){
                    img_grp.setValue(image_group.text); 
                    img_grp.disable(true);
                }
                            
            }

        }
    });    
    grp_store.load();


    var img_grp=new Ext.form.ComboBox({
        fieldLabel: _('模板组'),
        allowBlank:false,        
        triggerAction:'all',
        store:grp_store,
        emptyText :_("选择模板组"),
        displayField:'NODE_NAME',
        valueField:'NODE_ID',
        labelStyle: 'font-weight:bold;',
        width: 250,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'img_grp',
        id:'img_grp',
        mode:'local',
        listeners:{
            select:function(combo,record,index){
                grpid=record.get('NODE_ID');
            }
        }
    });
   
    var prvdr_store = new Ext.data.JsonStore({
        url: '/appliance/get_appliance_providers',
        root: 'rows',
        fields: ['name', 'value'],
        id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    prvdr_store.load();
    var prvdrs=new Ext.form.ComboBox({
        fieldLabel: _('提供'),
        allowBlank:false,
        triggerAction:'all',
        store: prvdr_store,
        emptyText :_("提供"),
        displayField:'name',
        valueField:'value',
        width: 100,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'prvdr',
        id:'prvdr',
        mode:'local',
        disabled:!is_manual
    });

    var pltfrm_store = new Ext.data.JsonStore({
        url: '/get_platforms',
        root: 'rows',
        fields: ['name', 'value'],
        //id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    pltfrm_store.load();
    var pltfrms=new Ext.form.ComboBox({
        fieldLabel: _('平台'),
        allowBlank:false,
        triggerAction:'all',
        store: pltfrm_store,
        emptyText :_("平台"),
        displayField:'name',
        valueField:'value',
        width: 100,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'pltfrm',
        id:'pltfrm',
        mode:'local',
        disabled:!is_manual
    });

    var pkg_store = new Ext.data.JsonStore({
        url: '/appliance/get_appliance_packages',
        root: 'rows',
        fields: ['name', 'value'],
        id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    pkg_store.load();
    var pkgs=new Ext.form.ComboBox({
        fieldLabel: _('包'),
        allowBlank:false,
        triggerAction:'all',
        store: pkg_store,
        emptyText :_("包"),
        displayField:'name',
        valueField:'value',
        width: 100,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'pkg',
        id:'pkg',
        mode:'local',
        disabled:!is_manual
    });

    var arch_store = new Ext.data.JsonStore({
        url: '/appliance/get_appliance_archs',
        root: 'rows',
        fields: ['name', 'value'],
        id:'id',
        successProperty:'success',
        listeners:{
            loadexception:function(obj,opts,res,e){
                var store_response=Ext.util.JSON.decode(res.responseText);
                Ext.MessageBox.alert(_("错误"),store_response.msg);
            }
        }
    });
    arch_store.load();
    var archs=new Ext.form.ComboBox({
        fieldLabel: _('架构'),
        allowBlank:false,
        triggerAction:'all',
        store: arch_store,
        emptyText :_("架构"),
        displayField:'name',
        valueField:'value',
        width: 100,
        typeAhead: true,
        forceSelection: true,
        selectOnFocus:true,
        name:'arch',
        id:'arch',
        mode:'local',
        disabled:!is_manual
    });

    var pae=new Ext.form.Checkbox({
        name: 'pae',
        id: 'pae',
        boxLabel:_('PAE'),
        checked:false,
        disabled:!is_manual
    });

    var hvm=new Ext.form.Checkbox({
        name: 'hvm',
        id: 'hvm',
        boxLabel:_('Hvm'),
        checked:false,
        disabled:!is_manual
    });

    var size=new Ext.form.TextField({
        fieldLabel: _('大小'),
        name: 'size',
        id: 'size',
        labelStyle: 'font-weight:bold;',
        width:50,
        disabled:true
    });

    
    var addn_panel= new Ext.Panel({
        layout:'column',
        bodyStyle:'padding:15px 0px 0px 0px;',
        labelWidth:60,
        labelSeparator:' ',
        //title:"Specify Additional Information",
        width:550,
        height:100,
        items:[prvdrs,pltfrms,pkgs,archs,pae,hvm,size]
    });

    var lbl=new Ext.form.Label({
        //text:"Specify download url or file location of the appliance/reference disk to be imported."
        html:'<div class="backgroundcolor" align="center" width="250"><font size="2"><i>'+
            _("Specify download url or file location of the appliance/reference disk to be imported")+
            '</i></font><br/></div><br>'
    });
    appl_panel = new Ext.FormPanel({
        labelWidth:125,
        frame:true,
        border:0,
        bodyStyle:'padding:5px 0px 0px 0px',
        labelAlign:"left" ,
        width:566,
        height:210,
        labelSeparator: ' ',
        items:[lbl,location,img_name,img_grp,addn_panel],
        bbar:[{xtype: 'tbfill'},
            new Ext.Button({
                name: 'ok',
                id: 'ok',
                text:_('确定'),
                icon:'icons/accept.png',
                cls:'x-btn-text-icon',
                listeners: {
                    click: function(btn) {
                        
                        if(appl_panel.getForm().isValid()){

                            checkImage(location.getValue(),
                                pkgs.getValue(),
                                archs.getValue(),
                                pae.getValue(),
                                hvm.getValue(),
                                size.getValue(),
                                prvdrs.getValue(),
                                pltfrms.getValue(),
                                description,
                                link,
                                img_name.getValue(),
                                grpid,
                                is_manual,
                                image_group
                            );
                                
                        }else{
                            Ext.MessageBox.alert(_("警告"),_("您输入的信息不完整，请重新检查输入信息."));
                        }
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

    if(!is_manual){
        description=appliance.description;
        link=appliance.link;

        location.setValue(appliance.href);
        img_name.setValue(appliance.title);
        prvdrs.setValue(appliance.provider_id);
        pltfrms.setValue(appliance.platform);
        pkgs.setValue(appliance.type);
        archs.setValue(appliance.arch);
        pae.setValue((appliance.PAE=='True'));
        hvm.setValue((appliance.is_hvm=='True'));
        size.setValue(parseInt(appliance.size/ (1024 * 1024)));
    }

    return appl_panel;
}

function checkImage(href,type,arch,pae,hvm,size,provider_id,platform,description,link,image_name,group_id,is_manual,image_group){
    var url="/template/check_image_exists?image_name="+image_name;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    Ext.MessageBox.show({
        title:_("导入: ")+image_name,
        msg:_("正在检查..."),
        width:300,
        wait:true,
        waitConfig: {interval:500}
    });
    ajaxReq.request({
        success: function(xhr) {
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                if(response.exists){
                    Ext.MessageBox.confirm(_("警告"),_("同样名字的模板已经存在,要覆盖吗?"),function(id){
                        if(id=='yes'){
                            importAppliance(href,type,arch,pae,hvm,size,provider_id,platform,description,link,image_name,group_id,is_manual,image_group);
                        }
                    });
                }else{
                    Ext.MessageBox.hide();
                    importAppliance(href,type,arch,pae,hvm,size,provider_id,platform,description,link,image_name,group_id,is_manual,image_group);
                }
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }
        },
        failure: function(xhr){
            Ext.MessageBox.hide();
            Ext.MessageBox.alert(_("失败"),xhr.statusText);
        }
    });
}

function importAppliance(href,type,arch,pae,hvm,size,provider_id,platform,description,link,image_name,group_id,is_manual,image_group){
    var url="/appliance/import_appliance?d=d";

    


    var params=new Object();

        params.href=href;
        params.type=type;
        params.arch=arch;
        params.pae=pae;
        params.hvm=hvm;
        params.size=size;
        params.provider_id=provider_id;
        params.platform=platform;
        params.description=description;
        params.link=link;
        params.image_name=image_name;
        params.group_id=group_id;
        params.is_manual=is_manual;
    //alert('pppppaaaaa'+params.href);
    var args= new Object();
        args.image_name=image_name;
        args.params=params;
    
    //alert(args+'beforesch'+args.image_name+'image'+args.params);
    showScheduleWindow(image_group,format(_("导入{0}"),image_name),url,'import',args);
    closeWindow();
//    var ajaxReq=ajaxRequest(url,0,"GET",true);
}

function import_Appliance_sch(url,image_name,image_group,params){
    var msg=(params.href.substring(0,1)=="/")?"正在复制... ":"正在下载... ";
    Ext.MessageBox.show({
        title:"导入: "+image_name,
        msg:msg,
        width:300,
        wait:true,
        waitConfig: {interval:500}
    });
     var ajaxReq=ajaxRequest(url,0,"GET",true);
        ajaxReq.request({
        params: params,
        success: function(xhr) {
            Ext.MessageBox.hide();
            closeWindow();
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                Ext.MessageBox.alert(_("成功"),format(_("导入 {0}任务提交."),image_name));
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }
//            image_group.fireEvent('click',image_group);
//            task_panel_do();
        },
        failure: function(xhr){
            Ext.MessageBox.hide();
            Ext.MessageBox.alert(_("失败"),xhr.statusText);
//            image_group.fireEvent('click',image_group);
        }
    });
}

function setLocationValue(value){
    //Ext.get("location").setValue(value);
    //alert(value);
    appl_panel.findById("location").setValue(value);
    file_browser.close();
}

function closeFileBrowser(){
    file_browser.close();
}
