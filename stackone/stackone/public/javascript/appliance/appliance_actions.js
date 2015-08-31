/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function handleApplianceEvents(node,action,item){
    getApplianceInfo(node,action);
}

function showApplianceList(node,action){
    var url="/appliance/get_appliance_list";
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    Ext.MessageBox.show({
        title:_('请稍候..'),
        msg: _('正在配置应用列表,请稍候...'),
        width:300,
        wait:true,
        waitConfig: {interval:200}
    });

    ajaxReq.request({
        success: function(xhr) {
           
            Ext.MessageBox.hide();
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                showWindow(_("应用分类"),715,425,ApplianceList(node,action));
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }

        },
        failure: function(xhr){
            Ext.MessageBox.hide();
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
    
}

function getApplianceInfo(node,action){
    var dom_id=node.attributes.text;
    var node_id=node.parentNode.attributes.id;
    var params="dom_id="+dom_id+"&node_id="+node_id;
    var url="/appliance/get_appliance_info?"+params;
    
    if(action.substring(0,4)=="NAV_")
        url+="&action="+action;
    var ajaxReq=ajaxRequest(url,0,"GET",true);
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                if(action=="SPECIFY_DETAILS" || !response.appliance.is_valid)
                    showWindow(_("应用详情"),315,325,ApplianceDetails(node,action,response.appliance,dom_id,node_id));
                else
                    doApplianceAction(action,response.appliance)
            }else{
                Ext.MessageBox.alert(_("失败"),response.msg);
            }

        },
        failure: function(xhr){
            Ext.MessageBox.alert( _("失败") , xhr.statusText);
        }
    });
}

function doApplianceAction(action,appliance){
    if(action=="VISIT_APPLICATION")
        window.open(appliance.web_url)
    else if(action=="SPECIFY_DETAILS")
        return
    else
        window.open(appliance.mgmt_web_url)
}