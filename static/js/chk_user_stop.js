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
	});
});