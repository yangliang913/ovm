

//////// override: For get store of combobox selection ////////
if ((typeof Range !== "undefined") && !Range.prototype.createContextualFragment)
{
	Range.prototype.createContextualFragment = function(html)
	{
		var frag = document.createDocumentFragment(),
		div = document.createElement("div");
		frag.appendChild(div);
		div.outerHTML = html;
		return frag;
	};
}

Ext.override(Ext.form.ComboBox, {
    getSelectedRecord: function() {
        return this.findRecord(this.valueField || this.displayField, this.getValue());
    },
    getSelectedIndex: function() {
        return this.store.indexOf(this.getSelectedRecord());
    }
});


function checkSpecialCharacters(value, text){
    var invalid_chars=new Array(' ','!','@','#','$','%','^','&','(',')','|','?','>','<','[',']','{','}','*','"',',','"',';',':','?','/','\'');
    for(var i=0;i<value.length;i++){
        for(var j=0;j<=invalid_chars.length;j++){
            if(value.charAt(i) == invalid_chars[j]){
                Ext.MessageBox.alert(_("错误"),_(text+" 不能包含下面特殊字符.<br>")+
                "space,comma,single quote,double quotes,'!','@','#',<br>'$','%','^','&','(',')','|','?','>','<','[',']','{','}','*',';',':','?','/'");
                return false;
            }
        }
    }
    return true;
}


function get_non_selected_records_from_grid(grid, attribute){
    // Get unselected rows from given grid
//    alert("---attribute----"+attribute);
    var non_selected_records = [];
    var sel_attr = [];
    var return_dict = {};
    var grid_store = grid.getStore();
    for(var i=0; i<grid_store.getCount(); i++)
        {
            var rec = grid_store.getAt(i);
            if (!grid.getSelectionModel().isSelected(rec)){
                if(attribute){
                    sel_attr.push(rec.get(attribute));
                }
                non_selected_records.push(rec);
            }
        }
     return_dict['records'] = non_selected_records;
     return_dict['attributes'] = sel_attr;
     return return_dict;
}


//###################//

var Cvt = {};

//#### CustColumnNodeUI ####//
Cvt.CustColumnNodeUI = Ext.extend(Ext.tree.TreeNodeUI, {
    focus: Ext.emptyFn, // prevent odd scrolling behavior
    renderElements : function(n, a, targetNode, bulkRender){
        this.indentMarkup = n.parentNode ? n.parentNode.ui.getChildIndent() : '';

        var t = n.getOwnerTree();
        var cols = t.columns;
        var bw = t.borderWidth;
        var c = cols[0];
	//alert("--1----"+a);
	//alert("----2--"+a.checked);
	var showcheckbox = a.showcheckbox;
        if (showcheckbox == undefined){
            showcheckbox = false;
        }
//        alert("---showcheckbox----"+showcheckbox);
        var enablecheckbox = a.enablecheckbox
//        alert("---enablecheckbox----"+enablecheckbox);
        if (enablecheckbox == undefined){
            enablecheckbox = true;
        }
        
	//alert("--enableCheckbox----"+enableCheckbox);

        var buf = [
             '<li class="x-tree-node"><div ext:tree-node-id="',n.id,'" class="x-tree-node-el x-tree-node-leaf ', a.cls,'">',
                '<div class="x-tree-col" style="width:',c.width-bw,'px;">',
                    '<span class="x-tree-node-indent">',this.indentMarkup,"</span>",
                    '<img src="', this.emptyIcon, '" class="x-tree-ec-icon x-tree-elbow">',
                    '<img src="', a.icon || this.emptyIcon, '" class="x-tree-node-icon',(a.icon ? " x-tree-node-inline-icon" : ""),(a.iconCls ? " "+a.iconCls : ""),'" unselectable="on">',
                    showcheckbox ? ('<input class="x-tree-node-cb" type="checkbox" ' + (enablecheckbox ? "" : "disabled") + (a.checked ? ' checked="checked" />' : '/>')) : '',
                    '<a hidefocus="on" class="x-tree-node-anchor" href="',a.href ? a.href : "#",'" tabIndex="1" ',
                    a.hrefTarget ? ' target="'+a.hrefTarget+'"' : "", '>',
                    '<span unselectable="on">', n.text || (c.renderer ? c.renderer(a[c.dataIndex], n, a) : a[c.dataIndex]),"</span></a>",
                "</div>"];
         for(var i = 1, len = cols.length; i < len; i++){
             c = cols[i];

             buf.push('<div class="x-tree-col ',(c.cls?c.cls:''),'" style="width:',c.width-bw,'px;">',
                        '<div class="x-tree-col-text">',(c.renderer ? c.renderer(a[c.dataIndex], n, a) : a[c.dataIndex]),"</div>",
                      "</div>");
         }
         buf.push(
            '<div class="x-clear"></div></div>',
            '<ul class="x-tree-node-ct" style="display:none;"></ul>',
            "</li>");

        if(bulkRender !== true && n.nextSibling && n.nextSibling.ui.getEl()){
            this.wrap = Ext.DomHelper.insertHtml("beforeBegin",
                                n.nextSibling.ui.getEl(), buf.join(""));
        }else{
            this.wrap = Ext.DomHelper.insertHtml("beforeEnd", targetNode, buf.join(""));
        }

        this.elNode = this.wrap.childNodes[0];
        this.ctNode = this.wrap.childNodes[1];
        var cs = this.elNode.firstChild.childNodes;
        this.indentNode = cs[0];
        this.ecNode = cs[1];
        this.iconNode = cs[2];
	   var index = 3;
	    if (showcheckbox) {
		this.checkbox = cs[3];
		// fix for IE6
		this.checkbox.defaultChecked = this.checkbox.checked;
		index++;
	    }
        this.anchor = cs[index];
        this.textNode = cs[index].firstChild;
    }
});

function getVNCInfo(node,dom,cloud){
    //    if(!Java0Installed){
    //        Ext.MessageBox.alert( _("Warning") , _("Your Browser does not support java applets.")+"<br>"+
    //                            _("Please install the Java Runtime Environment Plugin."));
    //        return;
    //    }
    var consolePanel=centerPanel.getItem('console'+dom.attributes.id);
    if (consolePanel != null ){
        centerPanel.remove(consolePanel);
    }
    var url;

    //if (consolePanel == null ){
    if(cloud){
     url='/cloud/get_vnc_info_for_cloudcmsvm?node_id='+node.attributes.id+'&dom_id='+dom.attributes.id;
    }else{
     url='get_vnc_info?node_id='+node.attributes.id+'&dom_id='+dom.attributes.id;
    }
    
    var ajaxReq = ajaxRequest(url,0,"GET",true);
    if (dom.getUI().getIconEl()!=null){
        var iconClass=dom.getUI().getIconEl().className;
        dom.getUI().getIconEl().className="x-tree-node-icon loading_icon";
    }
    ajaxReq.request({
        success: function(xhr) {//alert(xhr.responseText);
            if (dom.getUI().getIconEl()!=null){
                dom.getUI().getIconEl().className=iconClass;
            }
            var response=Ext.util.JSON.decode(xhr.responseText);
            if(response.success){
                var host=response.vnc.hostname;
                var port=response.vnc.port;
                var height=response.vnc.height;
                var width=response.vnc.height;
                var new_window=response.vnc.new_window;
                var show_control=response.vnc.show_control;
                var encoding=response.vnc.encoding;
                var restricted_colours=response.vnc.restricted_colours;
                var offer_relogin=response.vnc.offer_relogin;

                if(port=='00'){
                    Ext.MessageBox.alert(_("消息"),_("虚拟机没有运行."))
                    return;
                }

                var applet='<applet code="VncViewer.class" archive="/jar/SVncViewer.jar"'+
                'width="'+width+'" height="'+height+'">'+
                '<param name="HOST" value="'+host+'">'+
                '<param name="PORT" value="'+port+'">'+
                '<param name="Open new window" value="'+new_window+'">'+
                '<param name="Show controls" value="'+show_control+'">'+
                '<param name="Encoding" value="'+encoding+'">'+
                '<param name="Restricted colors" value="'+restricted_colours+'">'+
                '<param name="Offer relogin" value="'+offer_relogin+'">'+
                '</applet>';
                //var msg=response.vnc.msg;
                create_applet_tab(dom,applet,response);

            }else{
                Ext.MessageBox.alert(_("Failure"),response.msg);
            }
        },
        failure: function(xhr){
            if (dom.getUI().getIconEl()!=null){
                dom.getUI().getIconEl().className=iconClass;
            }
            Ext.MessageBox.alert( _("Failure") , xhr.statusText);
        }
    });
//    }else{
//        centerPanel.setActiveTab(consolePanel);
//    }
}