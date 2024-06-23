var pool;
function barrel_data(grade) {
    pool = grade;
    var pool_data = parseInt($("#pool_chip"+grade).val());
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

	$('#give_cancel').click(function(){
		$('#dialogmag_nine').fadeOut(300,function(){
			$('#dialohg_nine').addClass('bounceOutUp').fadeOut();
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
        $("#pool_chip"+pool).val(num);
	});

    $('#add_give').click(function(){
		$('#dialogmag_nine').fadeOut(300,function(){
			$('#dialohg_nine').addClass('bounceOutUp').fadeOut();
		});
		var day_triggle = parseInt($("#day_triggle").val());
		var give_triggle = parseInt($("#give_triggle").val());
        $("#triggle").val(day_triggle);
        $("#g_count").val(give_triggle);
	});
});


function add_give() {
    var triggle = parseInt($("#triggle").val());
    var g_count = parseInt($("#g_count").val());
	$("#day_triggle").val(triggle);
	$("#give_triggle").val(g_count);

    //列表 i 为索引，item为遍历值
    className = $(this).attr('class');
    $('#dialogmag_nine').fadeIn(300);
    $('#dialohg_nine').removeAttr('class').addClass('by_value '+className+'').fadeIn();
}