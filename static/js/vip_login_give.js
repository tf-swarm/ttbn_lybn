var pool;
function vip_login_data(grade) {
    pool = grade;
    var pool_data = parseInt($("#login_chip"+grade).val());
	$("#pool_data").val(pool_data);
	$("#alter_data").val(pool_data);

    //列表 i 为索引，item为遍历值
    className = $(this).attr('class');
    $('#dialogmag').fadeIn(300);
    $('#dialohg').removeAttr('class').addClass('by_value '+className+'').fadeIn();
}

$(function () {
    //关闭弹窗
	$('.claseDialogBtn').click(function(){
		$('#dialogmag').fadeOut(300,function(){
			$('#dialohg').addClass('bounceOutUp').fadeOut();
		});
	});

    //数量+
    $('.add_data').click(function () {
        var num= parseInt($(this).next().val());
        num=num+1;
        $(this).next().val(num).blur();
    });

    $('#add_submit').click(function(){
		$('#dialogmag').fadeOut(300,function(){
			$('#dialohg').addClass('bounceOutUp').fadeOut();
		});
		var pool_data = parseInt($("#pool_data").val());
		var alter_data = parseInt($("#alter_data").val())
        var num = pool_data + alter_data
        $("#login_chip"+pool).val(num);
	});

});
