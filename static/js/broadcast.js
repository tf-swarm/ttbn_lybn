$(function(){

	var error_led = false;
	var error_interval = false;
	var error_start = false;
	var error_end = false;

    $('#send_form').submit(function() {
		check_led();
		check_interval();
		check_start();
        check_end();

		if(error_led == true && error_interval == true && error_start == true && error_end == true)
		{
			return true;
		}
		else
		{
			return false;
		}

    });


	function check_led(){
        var len = $('#led').val().length;
		if(len==0||len>=100)
		{
			alert('公告60字中文以内或公告内容不能为空！')
			error_led = false;
		}
		else
		{
			error_led = true;
		}
	}

	function check_interval(){
        var len = $('#interval').val().length;
		if(len<=1)
		{
			alert('最少10秒或内容不能为空！')
			error_interval = false;
		}
		else
		{
			error_interval = true;
		}
	}

    function check_start(){
		var start_time = $('#start').val();
		if(start_time=="")
		{
			alert('请选择开始时间')
			error_start = false;
		}
		else
		{
			error_start = true;
		}
    }

    function check_end(){
		var start_end = $('#end').val();
		if(start_end=="")
		{
			alert('请选择开始结束')
			error_end = false;
		}
		else
		{
			error_end = true;
		}
    }

})