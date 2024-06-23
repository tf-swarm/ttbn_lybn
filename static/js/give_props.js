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

		var give_num = $("input#give_num").val();
		if (give_num ==""){
		    $("input#give_num").next("span").html("请输入用户ID！");
			$("input#give_num").focus();
			return false;
        }else {
		    $("input#give_num").next("span").html("");
        }

        // var give_day = $("input#give_day").val();
        // if (give_num ==""){
		 //    $("input#give_day").next("span").html("请输入用户ID！");
			// $("input#give_day").focus();
			// return false;
        // }else {
		 //    $("input#give_day").next("span").html("");
        // }

		}else{
			$("input#user_id_r").next("span").html("");
		}
	});

	$("#give_day").blur(function(){
		var d=$(this);
		if(d.val().length<1||d.val().length>3){
			 $(this).val('');
			 $("input#give_day").next("span").html("请输入长度为1-3位");
			 $("input#give_day").focus();
			 return false;
		}else{
			$("input#give_day").next("span").html("");
		}
	});
});