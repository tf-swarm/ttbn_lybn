//*********获取验证码*********//

	var AddInterValObj; //timer变量，控制时间
	var adcount = 60; //间隔函数，1秒执行
	var addCount;//当前剩余秒数
	
	function sendAddmes() {
		var myreg = /^1[35678]\d{9}$/;
		if(!myreg.test($("#add_phone").val())) 
		{ 
			layertest('请输入有效的手机号码')
		    return false;
		}
		else
		{
			var phone = $("#add_phone").val();
		　　 //向后台发送处理数据
			$.ajax({
			 　	type: "POST", //用POST方式传输
			 　	dataType: "JSON", //数据格式:JSON
				headers:{"X-CSRFToken":$.cookie('csrftoken')},
			 　	url: '/check_phone/', //目标地址
				data: {phone:phone}, //{username:$("#username").val(), content:$("#content").val()},
				success: function (data){
					if ( data.result == 1) {
							addCount = adcount;
						　	//设置button效果，开始计时
							$("#addSendCode").attr("disabled", "true");
							$("#addSendCode").val("" + addCount + "秒重新发送").css({"background-color":"#b2b2b2"});
							AddInterValObj = window.setInterval(SetAddnTime, 1000); //启动计时器，1秒执行一次
							var phone = $("#add_phone").val();
						　　//向后台发送处理数据
							$.ajax({
							 　　type: "POST", //用POST方式传输
							 　　dataType: "JSON", //数据格式:JSON
							 　　url: '/get_verify/', //目标地址
								 data: {phone:phone}, //{username:$("#username").val(), content:$("#content").val()},
							　　 error: function (data) { },
							 　　success: function (msg){ }
							 });
						}else {
							layertest('用户名不存在或用户已禁用！')
							return false;
						}

				}
			});
		}
	}
	
	//timer处理函数
	function SetAddnTime() {
		if (addCount == 0) {                
			window.clearInterval(AddInterValObj);//停止计时器
			$("#addSendCode").removeAttr("disabled");//启用按钮
			$("#addSendCode").val("获取验证码").css({"background-color":"#009bfd"});
		}
		else {
			addCount--;
			$("#addSendCode").val("" + addCount + "秒重新发送").css({"background-color":"#b2b2b2"});
		}
	}

	// layer modal
	function layertest(content){
		layer.open({
		    content: content
		    ,btn: '确定'
		});
	}
	//layer loading
	function loading(content){
		layer.open({
		    type: 2
		    ,content: content
		});
	}
	
	// update btn click
	$(document).on('click','.updateBtn',function(){
		if($('.error').length >0){
			layertest('请您填写正确的资料')
		}else{
			loading('跳转中')
		}
	})
