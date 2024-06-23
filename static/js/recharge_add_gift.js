var value;
$(function(){

    //支付宝关闭弹窗
    $('.claseDialogBtn').click(function(){
        $('#dialogmag').fadeOut(300,function(){
            $('#dialohg').addClass('bounceOutUp').fadeOut();
        });
    });

    //微信关闭弹窗
    $('.claseDialogBtn').click(function(){
        $('#popout').fadeOut(300,function(){
            $('#capacity').addClass('bounceOutUp').fadeOut();
        });
    });
});

//微信显示弹框
function weixin(data) {
	value = data;
    var info = parseInt($("#weixin"+value).val());
	$("#wechat").val(info);

    //列表 i 为索引，item为遍历值
    className = $(this).attr('class');
    $('#popout').fadeIn(300);
    $('#capacity').removeAttr('class').addClass('by_value '+className+'').fadeIn();
}

//支付宝显示弹框
function alipay(data) {
	value = data;
    var info = parseInt($("#alipay"+value).val());
	$("#alipay").val(info);

    //列表 i 为索引，item为遍历值
    className = $(this).attr('class');
    $('#dialogmag').fadeIn(300);
    $('#dialohg').removeAttr('class').addClass('by_value '+className+'').fadeIn();
}

$(function () {
    $('#alert_alipay').click(function(){
        $('#dialogmag').fadeOut(300,function(){
            $('#dialohg').addClass('bounceOutUp').fadeOut();
        });
        var alipay = parseInt($("#alipay").val());
        $("#alipay"+value).val(alipay);
    });

    $('#alert_wechat').click(function(){
        $('#popout').fadeOut(300,function(){
            $('#capacity').addClass('bounceOutUp').fadeOut();
        });
        var wechat = parseInt($("#wechat").val());
        $("#weixin"+value).val(wechat);
    });
});