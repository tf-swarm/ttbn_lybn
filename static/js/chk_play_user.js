$(function(){
	$(".button").click(function(){
		//alert(11);
		var user_id = $("input#user_id").val();
		if(user_id == ""){
			$("input#user_id").next("span").html("请输入用户ID！");
			$("input#user_id").focus();
			return false;
		}else{
			$("input#user_id").next("span").html("");
		}
		
		var user_id_r = $("input#user_id_r").val();
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
		
		var give_num = $("input#give_num").val();
		/*if(give_num == ""){
			$("input#give_num").next("span").html("请输入数值！");
			$("input#give_num").focus();
			return false;
		}else{
			$("input#give_num").next("span").html("");
		}*/
		
		/*if(give_num <= 0 || give_num > 1000){
			$("input#give_num").next("span").html("不在允许的范围内！");
			$("input#give_num").focus();
			return false;
		}else{
			$("input#give_num").next("span").html("");
		}*/
		if(give_num != ""){
			if(isNaN(give_num)){
				$("input#give_num").next("span").html("必须是数字！");
				$("input#give_num").focus();
				return false;
			}else{
				$("input#give_num").next("span").html("");
			}	
		}
		
	});
});