$(document).ready(function() {
    var wbbOpt = {
        buttons: "fontsize,fontcolor,|," +
        "bold,italic,underline,strike,superscript, subscript,|," +
        "img,video,link,|," +
        "bullist,numlist,|," +
        "code,quote,|," +
        "smilebox"
    };
$("#editor").wysibb(wbbOpt);
});