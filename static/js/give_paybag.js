$(function(){
	function submitForm(){
		var form = document.getElementById("form_search");
		form.submit();
	}

	$('#form_search').submit(function(){
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

function chip(){
document.getElementById("product_id0").style.display="block";
document.getElementById("product_id1").style.display="none";
document.getElementById("product_id2").style.display="none";

}
function dimao(){
document.getElementById("product_id0").style.display="none";
document.getElementById("product_id1").style.display="block";
document.getElementById("product_id2").style.display="none";

}
function gift_bag(){
document.getElementById("product_id0").style.display="none";
document.getElementById("product_id1").style.display="none";
document.getElementById("product_id2").style.display="block";
}
