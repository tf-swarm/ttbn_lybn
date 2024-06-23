/**
 * 生产时间url
 */
function makeDateUrl(opts) {
	opts = opts || {};
	
	var param 		= [],
		startDayId 	= opts.startDayId || "#start-day", 
		endDayId 	= opts.endDayId || "#end-day",
		from  		= $(startDayId).datebox("getValue") || '',
		to	  		= ($(endDayId).length && $(endDayId).datebox("getValue")) || '',
		fromAry		= from.split('/'),
		toAry		= to.split('/');
				
		if ( from.indexOf('-')>-1 ) {
			param.push( 'from='+from );
		}
		if ( to.indexOf('-')>-1 ) {
			param.push( 'to='+to );
		}
		if ( fromAry.length==3 ) {
			param.push( 'from='+[fromAry[2], fromAry[0], fromAry[1]].join('-') );
		}
		if ( toAry.length==3 ) {
			param.push( 'to='+[toAry[2], toAry[0], toAry[1]].join('-') );
		}
		return param.join('&');
}



//弹出信息窗口 title:标题 msgString:提示信息 msgType:信息类型 [error,info,question,warning]
function msgShow(title, msgString, msgType) {
    $.messager.alert(title, msgString, msgType);
}


var dateFormatter = function( date ) {
    var y = date.getFullYear();
    var m = date.getMonth()+1;
    var d = date.getDate();
    return y+'-'+(m<10?('0'+m):m)+'-'+(d<10?('0'+d):d);
}


var dateParse = function( s ) {
    if (!s) return new Date();
    var ss = (s.split('-'));
    var y = parseInt(ss[0],10);
    var m = parseInt(ss[1],10);
    var d = parseInt(ss[2],10);
    if (!isNaN(y) && !isNaN(m) && !isNaN(d)){
        return new Date(y,m-1,d);
    } else {
        return new Date();
    }
}


/**
 * 过滤特殊字符
 */
var escapeHtml = function(s) {
    var pattern = new RegExp("[`~!@#$^&*()=|{}':;',\\[\\].<>/?~！@#￥……&*（）——|{}【】‘；：”“'。，、？]");
    var rs = "";
    for (var i = 0; i < s.length; i++) {
        rs = rs+s.substr(i, 1).replace(pattern, '');
    }
    return rs.replace(/"/g, '');
}