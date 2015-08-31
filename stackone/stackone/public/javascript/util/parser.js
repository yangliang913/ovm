/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

function loadXMLDoc(response,isFile)
{
    try //Internet Explorer
    {
        xmlDoc=new ActiveXObject("Microsoft.XMLDOM");
        xmlDoc.async=false;
        xmlDoc.loadXML(response);
        return xmlDoc;
    }
    catch(e)
    {
        try //Firefox, Mozilla, Opera, etc.
        {
            parser=new DOMParser();
            xmlDoc=parser.parseFromString(response,"text/xml");
            return xmlDoc;
        }
        catch(e) {
            alert("Your Browser is not capable of XML Dom parsing. "+e.message)
        }
    }
}