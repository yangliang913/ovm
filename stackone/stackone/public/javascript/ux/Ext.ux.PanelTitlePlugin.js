/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/
Ext.ux.collapsedPanelTitlePlugin = function ()
{
    this.init = function(p) {
        if (p.collapsible)
        {
            var r = p.region;
            if ((r == 'north') || (r == 'south'))
            {
                p.on ('render', function()
                    {
                        var ct = p.ownerCt;
                        ct.on ('afterlayout', function()
                            {
                                if (ct.layout[r].collapsedEl)
                                {
                                    p.collapsedTitleEl = ct.layout[r].collapsedEl.createChild ({
                                        tag: 'span',
                                        cls: 'x-panel-collapsed-text',
                                        html: "<div style='font-size:11px'>&nbsp;"+p.title+"</div>"
                                    });
                                    p.setTitle = Ext.Panel.prototype.setTitle.createSequence (function(t)
                                        {p.collapsedTitleEl.dom.innerHTML = t;});
                                }
                            }, false, {single:true});
                        p.on ('collapse', function()
                            {
                                if (ct.layout[r].collapsedEl && !p.collapsedTitleEl)
                                {
                                    p.collapsedTitleEl = ct.layout[r].collapsedEl.createChild ({
                                        tag: 'span',
                                        cls: 'x-panel-collapsed-text',
                                        html: "<div style='font-size:11px'>&nbsp;"+p.title+"</div>"
                                    });
                                    p.setTitle = Ext.Panel.prototype.setTitle.createSequence (function(t)
                                        {p.collapsedTitleEl.dom.innerHTML = t;});
                                }
                            }, false, {single:true});
                    });
            }
        }
    };
}