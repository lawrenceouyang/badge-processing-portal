$.validator.addMethod ("date_format", function(value){
    // Must be in format MM/DD/YYYY and be a valid calendar date
    var dob = $('#dob_0').val();
    var momentDob = moment(dob, 'MM/DD/YYYY');
    var date_regex = /^\d{2}\/\d{2}\/\d{4}$/ ;
    return date_regex.test(dob) && momentDob.isValid() && moment().isAfter(momentDob) && momentDob.isAfter(moment().subtract(73000, "days"));
});

$.validator.addMethod ("csn_format_new", function(value){
    var csn_new = $('#new_badge').val();
    if(csn_new.length != 16) return false;
    else return true;
});

$.validator.addMethod ("csn_duplicate", function(value, element, param){
    return element.val() != param;
}, "You cannot enter the same CSN twice.");

$.validator.addMethod ("csn_format_escort", function(value){
    var csn_escort = $('#escort_badge').val();
    if(csn_escort.length != 16) {
        $("#escort_status").hide();
        return false;
    }
    else {
        return true;
    }
});

$.validator.addMethod( "pattern", function( value, element, param ) {
	if ( this.optional( element ) ) {
		return true;
	}
	if ( typeof param === "string" ) {
		param = new RegExp( "^(?:" + param + ")$" );
	}
	return param.test( value ) && value.length <= 50;
}, "Please manually enter a valid name under 50 characters." );

$.validator.addMethod( "timestampTo" , function(value) {
    return (moment(value, "MM/DD/YYYY") >= moment($('#from_date').val(), "MM/DD/YYYY"));
}, "Incorrect timestamp.");

// Validates whether input contains only white space
$.validator.addMethod( "whitespace", function(value){
    if(!value.replace(/\s/g, '').length)return false;
    else return true;
}, "Invalid.");

// Validates whether input contains any white space
$.validator.addMethod( "any_whitespace", function(value){
    return !(/\s/g.test(value));
}, "Incorrect CSN number format. Please click 'Clear Badges' and try again.");

// Validates whether input is a hex value
$.validator.addMethod( "is_hexadecimal", function(value){
    if(value.match(/^[A-F0-9]{16}$/i) !== null) return true;
    else return false;
}, "Incorrect CSN number format. Please click 'Clear Badges' and try again.");

