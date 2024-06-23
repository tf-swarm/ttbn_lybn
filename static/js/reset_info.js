$(function() {
	var user_id = false;
	var pwd = false;
	var phone = false;
	var code = false;

	$(".pwdBtnShow").click(function() {
		if($(".pwdBtnShow").attr("isshow") == "false") {
			$(".pwdBtnShow i").css("background-position", "-60px -93px");
			$(".password").hide();
			$(".password1").val($(".password").val());
			$(".password1").show();
			$(".pwdBtnShow").attr("isshow", "true");
		} else {
			$(".pwdBtnShow i").css("background-position", "-30px -93px");
			$(".password1").hide();
			$(".password").val($(".password1").val());
			$(".password").show();
			$(".pwdBtnShow").attr("isshow", "false");
		}
	});

	$(".confirm_Show").click(function() {
		if($(".confirm_Show").attr("isshow") == "false") {
			$(".confirm_Show i").css("background-position", "-60px -93px");
			$(".confirm_password").hide();
			$(".hide_password").val($(".confirm_password").val());
			$(".hide_password").show();
			$(".confirm_Show").attr("isshow", "true");
		} else {
			$(".confirm_Show i").css("background-position", "-30px -93px");
			$(".hide_password").hide();
			$(".confirm_password").val($(".hide_password").val());
			$(".confirm_password").show();
			$(".confirm_Show").attr("isshow", "false");
		}
	});

	$(".phone").blur(function() {
		reg = /^1[3|4|5|7|8][0-9]\d{4,8}$/i;
		if($(".phone").val() == "") {
			$(".phone").parent().addClass("errorC");
			$(".error1").html("请输入手机号");
			$(".error1").css("display", "block");
		} else if($(".phone").val().length < 11) {
			$(".phone").parent().addClass("errorC");
			$(".error1").html("手机号长度有误！");
			$(".error1").css("display", "block");
		} else if(!reg.test($(".phone").val())) {
			$(".phone").parent().addClass("errorC");
			$(".error1").html("逗我呢吧，你确定这是你的手机号!!");
			$(".error1").css("display", "block");
		} else {
			$(".phone").parent().addClass("checkedN");
			phone = true;
		}
	});
	$(".kapkey").blur(function() {
		reg = /^.*[\u4e00-\u9fa5]+.*$/;
		if($(".kapkey").val() == "") {
			$(".kapkey").parent().addClass("errorC");
			$(".error2").html("请输入验证码");
			$(".error2").css("display", "block");
		} else if($(".kapkey").val().length < 6) {
			$(".kapkey").parent().addClass("errorC");
			$(".error2").html("验证码长度有误！");
			$(".error2").css("display", "block");
		} else if(reg.test($(".kapkey").val())) {
			$(".kapkey").parent().addClass("errorC");
			$(".error2").html("验证码里无中文！");
			$(".error2").css("display", "block");
		} else {
			$(".kapkey").parent().addClass("checkedN");
			code = true;
		}
	});
	$(".password,.password1").blur(function() {
		reg1 = /^.*[\d]+.*$/;
		reg2 = /^.*[A-Za-z]+.*$/;
		reg3 = /^.*[_@#%&^+-/*\/\\]+.*$/;
		if($(".pwdBtnShow").attr("isshow") == "false") {
			var Pval = $(".password").val();
		} else {
			var Pval = $(".password1").val();
		}
		if(Pval == "") {
			$(".password").parent().addClass("errorC");
			$(".error3").html("请输入密码");
			$(".error3").css("display", "block");
		} else if(Pval.length > 16 || Pval.length < 6) {
			$(".password").parent().addClass("errorC");
			$(".error3").html("密码应为8-16个字符，区分大小写");
			$(".error3").css("display", "block");
		} else if(!((reg1.test(Pval) && reg2.test(Pval)) || (reg1.test(Pval) && reg3.test(Pval)) || (reg2.test(Pval) && reg3.test(Pval)))) {
			$(".password").parent().addClass("errorC");
			$(".error3").html("需至少包含数字、字母和符号中的两种类型");
			$(".error3").css("display", "block");
		} else {
			$(".password").parent().addClass("checkedN");
			pwd = true;
		}
	});

	$(".confirm_password,.hide_password").blur(function() {
		reg1 = /^.*[\d]+.*$/;
		reg2 = /^.*[A-Za-z]+.*$/;
		reg3 = /^.*[_@#%&^+-/*\/\\]+.*$/;
		if($(".confirm_Show").attr("isshow") == "false") {
			var Pval = $(".confirm_password").val();
		} else {
			var Pval = $(".hide_password").val();
		}
		var pwd = $(".password").val();
		if(Pval == "" || Pval != pwd) {
			$(".confirm_password").parent().addClass("errorC");
			$(".error5").html("两次输入不一致或密码格式不正确");
			$(".error5").css("display", "block");
		} else if(Pval.length > 16 || Pval.length < 6) {
			$(".confirm_password").parent().addClass("errorC");
			$(".error5").html("密码应为8-16个字符，区分大小写");
			$(".error5").css("display", "block");
		} else if(!((reg1.test(Pval) && reg2.test(Pval)) || (reg1.test(Pval) && reg3.test(Pval)) || (reg2.test(Pval) && reg3.test(Pval)))) {
			$(".confirm_password").parent().addClass("errorC");
			$(".error5").html("需至少包含数字、字母和符号中的两种类型");
			$(".error5").css("display", "block");
		} else {
			$(".confirm_password").parent().addClass("checkedN");
			pwd = true;
		}
	});

	$(".phone").focus(function() {
		$(".phone").parent().removeClass("errorC");
		$(".phone").parent().removeClass("checkedN");
		$(".error1").hide();
	});
	$(".kapkey").focus(function() {
		$(".kapkey").parent().removeClass("errorC");
		$(".kapkey").parent().removeClass("checkedN");
		$(".error2").hide();
	});

	$(".password,.password1").focus(function() {
		$(".password").parent().removeClass("errorC");
		$(this).parent().removeClass("checkedN");
		$(".error3").hide();
	});

	$(".confirm_password,.hide_password").focus(function() {
		$(".confirm_password").parent().removeClass("errorC");
		$(this).parent().removeClass("checkedN");
		$(".error5").hide();
	});


	$(".username").focus(function() {
		$(".username").parent().removeClass("errorC");
		$(".username").parent().removeClass("checkedN");
		$(".error4").hide();
	});

	$(".username").blur(function() {
		reg = /^[0-9]*[1-9][0-9]*$/;
		if($(".username").val() == "") {
			$(".username").parent().addClass("errorC");
			$(".error4").html("请输入用户ID");
			$(".error4").css("display", "block");
		} else if($(".username").val().length > 32 || $(".username").val().length < 7) {
			$(".username").parent().addClass("errorC");
			$(".error4").html("用户ID长度有误！");
			$(".error4").css("display", "block");
		} else if(!reg.test($(".username").val())) {
			$(".username").parent().addClass("errorC");
			$(".error4").html("用户ID格式有误!!");
			$(".error4").css("display", "block");
		} else {
			$(".username").parent().addClass("checkedN");
			user_id = true;
		}
	});

	$('#alter_password').click(function() {
		if(user_id == true && pwd == true && phone == true && code == true)
		{
			var params = $('#form_data').serialize();
			$.post('/run_manage/reset_pwd/', params, function(data) {
				if ( data.status) {
					alert(data.msg)
                    var URL= "/run_manage/reset_pwd/";
                    location.href=URL;
				}
				else {
					alert(data.msg);
				}

			});
		}
		else
		{
			if($(".username").val() == "") {
				$(".username").parent().addClass("errorC");
				$(".error4").html("请输入用户ID");
				$(".error4").css("display", "block");
			}
			if($(".password").val() == ""){
				$(".password").parent().addClass("errorC");
				$(".error3").html("请输入密码");
				$(".error3").css("display", "block");
			}
			if($(".confirm_password").val() == ""){
				$(".confirm_password").parent().addClass("errorC");
				$(".error5").html("请输入确认密码");
				$(".error5").css("display", "block");
			}
			if($(".phone").val() == "") {
				$(".phone").parent().addClass("errorC");
				$(".error1").html("请输入手机号");
				$(".error1").css("display", "block");
			}
			if($(".kapkey").val() == "") {
				$(".kapkey").parent().addClass("errorC");
				$(".error2").html("请输入验证码");
				$(".error2").css("display", "block");
			}
			else {
				user_id = true;
				pwd = true;
				phone = true;
				code = true;
			}

		}
	});
});