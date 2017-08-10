/**
 * Created by Lawrence.Ouyang on 8/10/2016.
 */

//////////////////////////////////////////
/// CONVERSIONS
/////////////////////////////////////////

convertTime = function(timestamp, format) {
    var dateTime = moment(timestamp, format);
    return dateTime.format("MM/DD/YYYY - h:mm A");
};

intToHashid = function(target) {
    var hashid = new Hashids("TABS", 8);
    return hashid.encode(target);
};

//////////////////////////////////////////
/// FORMATTERS
/////////////////////////////////////////

toTitleCase = function(str){
    return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
};

//////////////////////////////////////////
/// BADGE ISSUANCE FUNCTIONS
/////////////////////////////////////////
function disableNext() {
    $('a[href="#next"]').css("pointer-events", "none").css("background", "#eee").css("color", "#aaa");
}

function enableNext() {
    $('a[href="#next"]').css("pointer-events", "auto").css("background", "#3C87A0").css("color", "#fff");
}
