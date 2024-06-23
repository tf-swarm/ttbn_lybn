var pool;
var give;
function chip_data(grade) {
    pool = grade;
    var pool_data = parseInt($("#current_chip"+grade).val());
	$("#pool_data").val(pool_data);
	$("#alter_data").val(pool_data);

    //列表 i 为索引，item为遍历值
    className = $(this).attr('class');
    $('#dialogmag').fadeIn(300);
    $('#dialohg').removeAttr('class').addClass('by_value '+className+'').fadeIn();
}

function add_give_more(inf) {
	give = inf;
    var triggle = parseInt($("#triggle"+inf).val());
    var g_count = parseInt($("#g_count"+inf).val());
	$("#day_triggle").val(triggle);
	$("#give_triggle").val(g_count);

    //列表 i 为索引，item为遍历值
    className = $(this).attr('class');
    $('#dialogmag_nine').fadeIn(300);
    $('#dialohg_nine').removeAttr('class').addClass('by_value '+className+'').fadeIn();
}

//收分池弹窗
function income_pool(){
	var present_all = parseInt($("#present_all").val());
	$("#extract_chip").val(present_all);

	//列表 i 为索引，item为遍历值
    className = $(this).attr('class');
    $('#dialogmag_income').fadeIn(300);
    $('#dialohg_income').removeAttr('class').addClass('by_value '+className+'').fadeIn();
}

$(function () {
    //关闭弹窗
	$('.claseDialogBtn').click(function(){
		$('#dialogmag').fadeOut(300,function(){
			$('#dialohg').addClass('bounceOutUp').fadeOut();
		});
	});
	//金猪池关闭弹窗
	$('#give_cancel').click(function(){
		$('#dialogmag_nine').fadeOut(300,function(){
			$('#dialohg_nine').addClass('bounceOutUp').fadeOut();
		});
	});

	//龙舟怪池关闭弹窗
	$('#dragon_cancel').click(function(){
		$('#dialogmag_ten').fadeOut(300,function(){
			$('#dialohg_ten').addClass('bounceOutUp').fadeOut();
		});
	});

	//收分池关闭弹窗
	$('.income_cancel').click(function(){
		$('#dialogmag_income').fadeOut(300,function(){
			$('#dialohg_income').addClass('bounceOutUp').fadeOut();
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

    $('#add_give_info').click(function(){
		$('#dialogmag_nine').fadeOut(300,function(){
			$('#dialohg_nine').addClass('bounceOutUp').fadeOut();
		});
		var day_triggle = parseInt($("#day_triggle").val());
		var give_triggle = parseInt($("#give_triggle").val());
        $("#triggle"+give).val(day_triggle);
        $("#g_count"+give).val(give_triggle);
	});

    $('#income_chip').click(function(){
		$('#dialogmag_income').fadeOut(300,function(){
			$('#dialohg_income').addClass('bounceOutUp').fadeOut();
		});
		var extract_chip = parseInt($("#extract_chip").val());

        $("#present_all").val(extract_chip);
	});

    $('#add_nian').click(function(){
		$('#dialogmag_nine').fadeOut(300,function(){
			$('#dialohg_nine').addClass('bounceOutUp').fadeOut();
		});
		var nian_data = parseInt($("#nian_data").val());
		var alter_nian = parseInt($("#alter_nian").val());
		var num = nian_data + alter_nian
        $("#nian_count").val(num);
	});

    $('#add_dragon_boat').click(function(){
		$('#dialogmag_ten').fadeOut(300,function(){
			$('#dialohg_ten').addClass('bounceOutUp').fadeOut();
		});
		var dragon_data = parseInt($("#dragon_boat_data").val());
		var alter_dragon = parseInt($("#alter_dragon_boat").val());
		var num = dragon_data + alter_dragon
        $("#dragon_boat").val(num);
	});
});


function add_nian() {
    var g_count = parseInt($("#nian_count").val());
	$("#nian_data").val(g_count);
	$("#alter_nian").val(g_count);

    //列表 i 为索引，item为遍历值
    className = $(this).attr('class');
    $('#dialogmag_nine').fadeIn(300);
    $('#dialohg_nine').removeAttr('class').addClass('by_value '+className+'').fadeIn();
}

function add_dragon_boat() {
    var g_count = parseInt($("#dragon_boat").val());
	$("#dragon_boat_data").val(g_count);
	$("#alter_dragon_boat").val(g_count);

    //列表 i 为索引，item为遍历值
    className = $(this).attr('class');
    $('#dialogmag_ten').fadeIn(300);
    $('#dialohg_ten').removeAttr('class').addClass('by_value '+className+'').fadeIn();
}