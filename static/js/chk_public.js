// JavaScript Document
var chkInputInfo = function(me){
	return me = {
		changeGroupNum : function(){
			//alert(sid);
			var group_num = $("input#group_num").val();
			if(group_num == ""){
				$("input#group_num").next("span").html("@请输入数值！");
				$("input#group_num").focus();
				return false;
			}else{
				$("input#group_num").next("span").html("");
			}
			
			if(isNaN(group_num)){
				$("input#group_num").next("span").html("@必须是数字！");
				$("input#group_num").focus();
				return false;
			}else{
				$("input#group_num").next("span").html("");
			}
		},// END changeGroupNum
		
		changeMouseNum1 : function(){// 打地鼠锤子
			//alert(sid);
			var num500   = $("input#num500").val();
			var num1000  = $("input#num1000").val();
			var num5000  = $("input#num5000").val();
			var num10000 = $("input#num10000").val();
			var num50000 = $("input#num50000").val();
			
			if(num500 == ""){
				$("input#num500").next("span").html("请输入数值！");
				$("input#num500").focus();
				return false;
			}else{
				$("input#num500").next("span").html("");
			}
			
			if(isNaN(num500)){
				$("input#num500").next("span").html("必须是数字！");
				$("input#num500").focus();
				return false;
			}else{
				$("input#num500").next("span").html("");
			}
			
			if(num1000 == ""){
				$("input#num1000").next("span").html("请输入数值！");
				$("input#num1000").focus();
				return false;
			}else{
				$("input#num1000").next("span").html("");
			}
			
			if(isNaN(num1000)){
				$("input#num1000").next("span").html("必须是数字！");
				$("input#num1000").focus();
				return false;
			}else{
				$("input#num1000").next("span").html("");
			}
			
			if(num5000 == ""){
				$("input#num5000").next("span").html("请输入数值！");
				$("input#num5000").focus();
				return false;
			}else{
				$("input#num5000").next("span").html("");
			}
			
			if(isNaN(num5000)){
				$("input#num5000").next("span").html("必须是数字！");
				$("input#num5000").focus();
				return false;
			}else{
				$("input#num5000").next("span").html("");
			}
			
			if(num10000 == ""){
				$("input#num10000").next("span").html("请输入数值！");
				$("input#num10000").focus();
				return false;
			}else{
				$("input#num10000").next("span").html("");
			}
			
			if(isNaN(num10000)){
				$("input#num10000").next("span").html("必须是数字！");
				$("input#num10000").focus();
				return false;
			}else{
				$("input#num10000").next("span").html("");
			}
			
			if(num50000 == ""){
				$("input#num50000").next("span").html("请输入数值！");
				$("input#num50000").focus();
				return false;
			}else{
				$("input#num50000").next("span").html("");
			}
			
			if(isNaN(num50000)){
				$("input#num50000").next("span").html("必须是数字！");
				$("input#num50000").focus();
				return false;
			}else{
				$("input#num50000").next("span").html("");
			}
		},// END changeMouseNum1
		
		req_mouse_pond_data : function(whichOne){// 打地鼠奖池统计
			var startTime      = $.trim($('#start_time' + whichOne).val()).substr(0, 10);
			var stopTime       = $.trim($('#stop_time' + whichOne).val()).substr(0, 10);
			var pond_num_all   = $('#pond_num_all');
			var pond_num       = $('#pond_num');
			var gold_num_all   = $('#gold_num_all');
			var gold_num       = $('#gold_num');
			var blue_num_all   = $('#blue_num_all');
			var blue_num       = $('#blue_num');
			var getTimestamp   = new Date().getTime();// 取当前时间毫秒时间戳
			var getUnixNowTime = getTimestamp.toString().substr(0, 10);// 取当前时间十位时间戳
			// alert(startTime);
			// alert(getUnixNowTime);
			// alert(this.get_unix_time(startTime));
			
			// 验证时间选择是否正确
			if(this.chk_date(startTime, stopTime, getUnixNowTime)){
			
				$.ajax({
					url      : '/buniao_manage/mouse/pond_data/v/' + getTimestamp,
					async    : true,
					type     : 'post',
					dataType : 'json',
					data : {
						"which_one" : whichOne,
						"start"     : startTime,
						"end"       : stopTime,
					},
					success  : function(data){
						if(whichOne == 1){
							pond_num_all.html(data.now_all);
							pond_num.html(data.t_all);
							$('#days' + whichOne).html(data.days);
							$('#start_time' + whichOne).val(data.m_start_time);
							$('#stop_time' + whichOne).val(data.m_end_time);
							$('#mtr' + whichOne).css({'display':''});
						}else if(whichOne == 2){
							gold_num_all.html(data.now_chip);
							gold_num.html(data.t_chip);
							$('#days' + whichOne).html(data.days);
							$('#start_time' + whichOne).val(data.m_start_time);
							$('#stop_time' + whichOne).val(data.m_end_time);
							$('#mtr' + whichOne).css({'display':''});
						}else if(whichOne == 3){
							blue_num_all.html(data.now_hammer);
							blue_num.html(data.t_hammer);
							$('#days' + whichOne).html(data.days);
							$('#start_time' + whichOne).val(data.m_start_time);
							$('#stop_time' + whichOne).val(data.m_end_time);
							$('#mtr' + whichOne).css({'display':''});
						}
					},
					error    : function(){
						alert('很抱歉，操作失败，请稍后再试！');
					}
				});// END AJAX
				
			}// END IF
		},// END req_mouse_pond_data
		
		get_unix_time : function(dateStr){// 日期转换为时间戳
			var newstr   = dateStr.replace(/-/g, '/');
			var date     = new Date(newstr);
			var time_str = date.getTime().toString();
			return time_str.substr(0, 10);
		},// END get_unix_time
		
		chk_date : function(startTime, stopTime, getUnixNowTime){// 判断日期选择是否正确
			var u_startTime = this.get_unix_time(startTime);
			var u_stopTime  = this.get_unix_time(stopTime);
			
			if(u_startTime > getUnixNowTime){
				alert('开始时间不能大于当前时间！');
				return false;
			}else if(u_startTime > u_stopTime){
				alert('开始时间不能大于结束时间！');
				return false;
			}else if(u_stopTime > getUnixNowTime){
				alert('结束时间不能大于当前时间！');
				return false;
			}else{
				return true;
			}
		},// END chk_date
		
		changeBlackNum : function(){// 小黑屋
			//alert(sid);
			var user_id   = $("input#user_id").val();
			var user_id_r = $("input#user_id_r").val();
			var odds      = $("input#odds").val();
			
			if(user_id == ""){
				$("input#user_id").next("span").html("请输入用户ID！");
				$("input#user_id").focus();
				return false;
			}else{
				$("input#user_id").next("span").html("");
			}
			
			if(user_id_r == ""){
				$("input#user_id_r").next("span").html("请再输入一次！");
				$("input#user_id_r").focus();
				return false;
			}else{
				$("input#user_id_r").next("span").html("");
			}
			
			if(user_id != user_id_r){
				$("input#user_id_r").next("span").html("两次输入不一致，请重试！");
				$("input#user_id_r").focus();
				return false;
			}else{
				$("input#user_id_r").next("span").html("");
			}
			
			/*if(odds == ""){
				$("input#odds").next("span").html("请输入数值！！");
				$("input#odds").focus();
				return false;
			}else{
				$("input#odds").next("span").html("");
			}*/
			
			if(odds != ""){
				if(isNaN(odds)){
					$("input#odds").next("span").html("必须是数字！！");
					$("input#odds").focus();
					return false;
				}else{
					$("input#odds").next("span").html("");
				}
			}
		},// END changeBlackNum
		
		sgame_switch_button : function(thisHostName, buttonFlag, whichGame){// 小游戏开关（主机，按钮状态，哪个小游戏）
			
			var urlPath = '/buniao_manage/' + whichGame + '/switch_button/';
			
			$.ajax({
				url      : thisHostName + urlPath,
				async    : true,
				type     : 'post',
				dataType : 'json',
				data : {
					buttonFlag : buttonFlag,
					whichGame  : whichGame,
				},
				success  : function(data){
					alert(data.msg + '\n\n' + data.changeButtonInfo);
				},
				error    : function(){
					alert('操作失败，请稍后再试！');
				}
			});// END AJAX
			
		},// END sgame_switch_button
		
		
	};// END me
}();// END chkInputInfo

