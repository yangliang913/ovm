


function fnValidateIPAddress(ipaddr) {
        //Remember, this function will validate only Class C IP.
        //change to other IP Classes as you need
        ipaddr = ipaddr.replace( /\s/g, "") //remove spaces for checking
        var re = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/; //regex. check for digits and in
                                              //all 4 quadrants of the IP
        if (re.test(ipaddr)) {
            //split into units with dots "."
            var parts = ipaddr.split(".");
            //if the first unit/quadrant of the IP is zero
            if (parseInt(parseFloat(parts[0])) == 0) {
                return false;
            }
            //if the fourth unit/quadrant of the IP is zero
            if (parseInt(parseFloat(parts[3])) == 0) {
                return false;
            }
            //if any part is greater than 255
            for (var i=0; i<parts.length; i++) {
                if (parseInt(parseFloat(parts[i])) > 255){
                    return false;
                }
            }
            return true;
        } else {
            return false;
        }
    }


function fnValidateCIDR(cidr) {
        var cidr_parts = cidr.split("/");
        if (cidr_parts.length != 2){
            return false
        }

        var ipaddr = cidr_parts[0];
        var mask = cidr_parts[1];

        if (parseInt(mask) < 1 || parseInt(mask) > 32){
            return false
        }

        ipaddr = ipaddr.replace( /\s/g, "") //remove spaces for checking
        var re = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/; //regex. check for digits and in
                                              //all 4 quadrants of the IP
        if (re.test(ipaddr)) {
            //split into units with dots "."
            var parts = ipaddr.split(".");
            //if the first unit/quadrant of the IP is zero
            if (parseInt(parseFloat(parts[0])) == 0) {
                return false;
            }
            //if the fourth unit/quadrant of the IP is zero
            if (parseInt(parseFloat(parts[3])) == 0) {
                return false;
            }
            //if any part is greater than 255
            for (var i=0; i<parts.length; i++) {
                if (parseInt(parseFloat(parts[i])) > 255){
                    return false;
                }
            }
            return true;
        } else {
            return false;
        }
    }

function validate_ip_address(address){
        var ip_parts = address.split("/");
        if (ip_parts.length == 2){
            return fnValidateCIDR(address);
        }
        else if(ip_parts.length == 1){
            return fnValidateIPAddress(address);
        }
        return false;
}

function validate_vlan_range(range){
        var re = /^\d+-\d+$/;

        if (re.test(range)){
            var range_parts = range.split("-");

            if (range_parts[0] > 4094 || range_parts[1] > 4094){
                return false
            }
        }
        else{
            return false;
        }

        return true;
    }


function is_special_char_exist(data, allow){
    var re = /^[a-zA-Z0-9+(),-_]+$/
    if (re.test(data))
        return false //special char doesnot exist
    return true//special char exist
}


function special_char_test(data){
  var iChars = "!@#$%^&*()+=-[]\\\';,./{}|\":<>?~_";
  for ( var i = 0; i < data.length; i++) {
    if (iChars.indexOf(data.charAt(i)) != -1) {
      return true;
    }
  }
  return false
}










