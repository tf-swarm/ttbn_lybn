$(function(){

	var error_name = false;
	var error_password = false;
	var error_verify = false;


	$('#userName').blur(function() {
		check_user_name();
	});

	$('#pwd').blur(function() {
		check_pwd();
	});

	// $('#verify').blur(function() {
	// 	check_verify();
	// });


	$('#reg_form').submit(function(){
		check_user_name();
		check_pwd();
		// check_verify();
		if(error_name == false && error_password == false && error_verify == false)
		{
		return true;
		}
		else
		{

		return false;
		}

	});

	function check_user_name(){
		var len = $('#userName').val().length;
		if(len<1||len>20)
		{

			$('.ht_show_error').show();
			$('.ht_show_error ul li:eq(0)').html('请输入用户名').show();
			error_name = true;
		}
		else
		{
			$('.ht_show_error').hide();
			$('.ht_show_error ul li:eq(0)').hide();
			error_name = false;
		}
	}

	function check_pwd(){
		var len = $('#pwd').val().length;
		if(len==0)
		{
			$('.ht_show_error').show();
			$('.ht_show_error ul li:eq(1)').html('请输入密码').show();
			error_password = true;
		}
		else
		{
			 $.post('/check_password/',{'phone':$('#add_phone').val(),'verify':$('#code').val()}, function (data) {
				if(data.ok==0)
				{
					$('.ht_show_error').show();
					$('.ht_show_error ul li:eq(1)').html('密码错误!').show();
					// $('#error_tip li:eq(2)').show();
					error_verify = true;
				}else {
					$('.ht_show_error').hide();
					$('.ht_show_error ul li:eq(1)').hide();
					error_verify = false;
				}
			});
		}		
	}

	function check_verify(){
		var len = $('#verify').val().length;
		if(len==0)
		{

			$('.ht_show_error').show();
			$('.ht_show_error ul li:eq(2)').html('请输入验证码').show();
			error_verify = true;
		}
		else
		{
            $.post('/verify_check/',{'verify':$('#verify').val()}, function (data) {
				if(data.ok==0)
				{
					$('.ht_show_error').show();
					$('.ht_show_error ul li:eq(2)').html('验证码错误!').show();
					// $('#error_tip li:eq(2)').show();
					error_verify = true;
				}else {//当前用户名不存在
					$('.ht_show_error').hide();
					$('.ht_show_error ul li:eq(2)').hide();
					error_verify = false;
				}
            });

		}
	}
});
