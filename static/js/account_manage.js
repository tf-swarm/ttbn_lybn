var w,h,className;
	function getSrceenWH(){
		w = $(window).width();
		h = $(window).height();
		$('#dialogBg').width(w).height(h);
	}

	window.onresize = function(){  
		getSrceenWH();
	}  
	$(window).resize();  
	
	$(function(){
		getSrceenWH();
	
	//关闭弹窗
	$('.claseDialogBtn').click(function(){
		$('#dialogBg').fadeOut(300,function(){
			$('#dialog').addClass('bounceOutUp').fadeOut();
			$('#edit_show').empty();
		});
	});
});

function redact(nid,account_name,phone,department) {
	$.post('/control_manage/edit_account/',{'user_id':nid,'user_name':account_name,'phone':phone,'department':department},function (data) {
		if(data.islogin){
			$("#user_id").val(data.user_id);
			$("#edit_user_name").val(data.user_name);
			$("#edit_phone").val(data.phone);
			$("#edit_department option[value='"+data.department+"']").attr("selected","selected");

			var str_html = '';
			var options = '';
			//列表 i 为索引，item为遍历值
			$.each(data.info, function(i,item){
				str_html = '<div class="label_end">';
				str_html += '<select name="account_info" class="ui dropdown" id="edit_option">';
				if (item.name == "data_collect"){
					data_collect = '<option value="data_collect" selected>数据总汇</option>';
					str_html += data_collect
                }
                else {
					data_collect = '<option value="data_collect">数据总汇</option>';
					str_html +=data_collect
				}

				if (item.name == "order_query"){
					order_query = '<option value="order_query" selected>订单查询</option>';
					str_html += order_query
                }
                else {
					order_query = '<option value="order_query">订单查询</option>';
					str_html += order_query
				}

				if (item.name == "mail_general"){
					mail_general = '<option value="mail_general" selected>邮件总览</option>';
					str_html += mail_general
                }
                else {
					mail_general = '<option value="mail_general">邮件总览</option>';
					str_html += mail_general
				}

				if (item.name == "chip_fill_point"){
					chip_fill_point = '<option value="chip_fill_point" selected>鸟蛋填分设置</option>';
					str_html += chip_fill_point
                }
                else {
					chip_fill_point = '<option value="chip_fill_point">鸟蛋填分设置</option>';
					str_html += chip_fill_point
				}
				if (item.name == "barrel_fill_point"){
					barrel_fill_point = '<option value="barrel_fill_point" selected>炮倍填分设置</option>';
					str_html += barrel_fill_point
                }
                else {
					barrel_fill_point = '<option value="barrel_fill_point">炮倍填分设置</option>';
					str_html += barrel_fill_point
				}

				if (item.name == "nian_pool_point"){
					nian_pool_point = '<option value="nian_pool_point" selected>年兽填分设置</option>';
					str_html += nian_pool_point
                }
                else {
					nian_pool_point = '<option value="nian_pool_point">年兽填分设置</option>';
					str_html += nian_pool_point
				}

				if (item.name == "broadcast_set"){
					broadcast_set = '<option value="broadcast_set" selected>公告设置</option>';
					str_html += broadcast_set
                }
                else {
					broadcast_set = '<option value="broadcast_set">公告设置</option>';
					str_html += broadcast_set
				}

				if (item.name == "pay_add_gift"){
					pay_add_gift = '<option value="pay_add_gift" selected>充值加赠</option>';
					str_html += pay_add_gift
                }
                else {
					pay_add_gift = '<option value="pay_add_gift">充值加赠</option>';
					str_html += pay_add_gift
				}

				if (item.name == "sum_count"){
					sum_count = '<option value="sum_count" selected>渠道数据统计</option>';
					str_html += sum_count
                }
                else {
					sum_count = '<option value="sum_count">渠道数据统计</option>';
					str_html += sum_count
				}

				if (item.name == "coupon_count"){
					coupon_count = '<option value="coupon_count" selected>玩家期间数据统计</option>';
					str_html += coupon_count
                }
                else {
					coupon_count = '<option value="coupon_count">玩家期间数据统计</option>';
					str_html += coupon_count
				}

				if (item.name == "super_weapon_count"){
					super_weapon_count = '<option value="super_weapon_count" selected>超级武器统计</option>';
					str_html += super_weapon_count
                }
                else {
					super_weapon_count = '<option value="super_weapon_count">超级武器统计</option>';
					str_html += super_weapon_count
				}

				if (item.name == "player_general"){
					player_general = '<option value="player_general" selected>玩家总览</option>';
					str_html += player_general
                }
                else {
					player_general = '<option value="player_general">玩家总览</option>';
					str_html += player_general
				}

				if (item.name == "give_gift"){
					give_gift = '<option value="give_gift" selected>赠送礼包</option>';
					str_html += give_gift
                }

                if (item.name == "arena_general"){
					arena_general = '<option value="arena_general" selected>竞技场总览</option>';
					str_html += arena_general
                }
                else {
					arena_general = '<option value="arena_general">竞技场总览</option>';
					str_html += arena_general
				}

				if (item.name == "arena_particulars"){
					arena_particulars = '<option value="arena_particulars" selected>竞技场详情</option>';
					str_html += arena_particulars
                }
                else {
					arena_particulars = '<option value="arena_particulars">竞技场详情</option>';
					str_html += arena_particulars
				}

				if (item.name == "mini_general"){
					mini_general = '<option value="mini_general" selected>小游戏总览</option>';
					str_html += mini_general
                }
                else {
					mini_general = '<option value="mini_general">小游戏总览</option>';
					str_html += mini_general
				}

				if (item.name == "mini_particulars"){
					mini_particulars = '<option value="mini_particulars" selected>小游戏详情</option>';
					str_html += mini_particulars
                }
                else {
					mini_particulars = '<option value="mini_particulars">小游戏详情</option>';
					str_html += mini_particulars
				}


				if (item.name == "limit_time_shop"){
					limit_time_shop = '<option value="limit_time_shop" selected>限时商城</option>';
					str_html += limit_time_shop
                }
                else {
					limit_time_shop = '<option value="limit_time_shop">限时商城</option>';
					str_html += limit_time_shop
				}

				if (item.name == "shop_for_record"){
					shop_for_record = '<option value="shop_for_record" selected>商城兑换记录</option>';
					str_html += shop_for_record
                }
                else {
					shop_for_record = '<option value="shop_for_record">商城兑换记录</option>';
					str_html += shop_for_record
				}
				if (item.name == "card_secret_set"){
					card_secret_set = '<option value="card_secret_set" selected>卡密设置</option>';
					str_html += card_secret_set
                }
                else {
					card_secret_set = '<option value="card_secret_set">卡密设置</option>';
					str_html += card_secret_set
				}

				if (item.name == "exchange_code_general"){
					exchange_code_general = '<option value="exchange_code_general" selected>兑换码总览</option>';
					str_html += exchange_code_general
                }
                else {
					exchange_code_general = '<option value="exchange_code_general">兑换码总览</option>';
					str_html += exchange_code_general
				}

				if (item.name == "exchange_code_query"){
					exchange_code_query = '<option value="exchange_code_query" selected>兑换查询</option>';
					str_html += exchange_code_query
                }
                else {
					exchange_code_query = '<option value="exchange_code_query">兑换查询</option>';
					str_html += exchange_code_query
				}

				if (item.name == "red_packet_general"){
					red_packet_general = '<option value="red_packet_general" selected>红包总览</option>';
					str_html += red_packet_general
                }
                else {
					red_packet_general = '<option value="red_packet_general">红包总览</option>';
					str_html += red_packet_general
				}

				if (item.name == "player_pay_double"){
					player_pay_double = '<option value="player_pay_double" selected>充值翻倍</option>';
					str_html += player_pay_double
                }
                else {
					player_pay_double = '<option value="player_pay_double">充值翻倍</option>';
					str_html += player_pay_double
				}

				if (item.name == "vip_login_give"){
					vip_login_give = '<option value="vip_login_give" selected>vip登录赠送</option>';
					str_html += vip_login_give
                }
                else {
					vip_login_give = '<option value="vip_login_give">vip登录赠送</option>';
					str_html += vip_login_give
				}

				if (item.name == "saving_pot"){
					saving_pot = '<option value="saving_pot" selected>存钱窝</option>';
					str_html += saving_pot
                }
                else {
					saving_pot = '<option value="saving_pot">存钱窝</option>';
					str_html += saving_pot
				}

                if (item.name == "account_set"){
					account_set = '<option value="account_set" selected>账号管理</option>';
					str_html += account_set
                }

				str_html += '</select>';
				str_html += '<a onclick="$(this).parent().remove();">' + '<img src="/static/images/cross-circle.png" style="vertical-align: baseline;;">' + '</a>';
	           	str_html += '</div>';
				// $("#edit_option option[value='"+item.name+"']").attr("selected","selected");

				$("#edit_show").append(str_html);
			});
			className = $(this).attr('class');
			$('#dialogBg').fadeIn(300);
			$('#dialog').removeAttr('class').addClass('animated '+className+'').fadeIn();
		}
	});
}


function open_login(account_name,phone,department) {
    $.post('/control_manage/alter_login/', {"user_name":account_name,"phone":phone,"department":department}, function(msg) {
        if ( msg.state) {
            if(confirm(msg.info)){
                var pag = $('.pagination-num').val() ;
                var URL= "/control_manage/G_account_setting/?page=" + pag;
                location.href=URL;
            }else {
                var pag = $('.pagination-num').val() ;
                var URL= "/control_manage/G_account_setting/?page=" + pag;
                location.href=URL;
            }
        }
        else {
            alert(msg.info);
        }

    });
}

function delete_data(account_name,phone,department) {
    $.post('/control_manage/delete_data/', {"user_name":account_name,"phone":phone,"department":department}, function(msg) {
        if ( msg.state) {
            if(confirm(msg.info)){
                var pag = $('.pagination-num').val() ;
                var URL= "/control_manage/G_account_setting/?page=" + pag;
                location.href=URL;
            }else {
                var pag = $('.pagination-num').val() ;
                var URL= "/control_manage/G_account_setting/?page=" + pag;
                location.href=URL;
            }
        }
        else {
            alert(msg.info);
        }

    });
}

$(function(){
	getSrceenWH();
	//显示弹框
	$('#bn_btn_one').click(function(){
		className = $(this).attr('class');
		$('#dialogmag').fadeIn(300);
		$('#dialohg').removeAttr('class').addClass('by_value '+className+'').fadeIn();
	});
	
	//关闭弹窗
	$('.claseDialogBtn').click(function(){
		$('#dialogmag').fadeOut(300,function(){
			$('#dialohg').addClass('bounceOutUp').fadeOut();
		});
	});
});


$(function(){
	getSrceenWH();

	//显示弹框
	$('#red_packet').click(function(){
		className = $(this).attr('class');
		$('#dialogmag').fadeIn(300);
		$('#dialohg').removeAttr('class').addClass('by_value '+className+'').fadeIn();
	});

	//关闭弹窗
	$('.claseDialogBtn').click(function(){
		$('#dialogmag').fadeOut(300,function(){
			$('#dialohg').addClass('bounceOutUp').fadeOut();
		});
	});
});


$(function(){
	getSrceenWH();
	//显示弹框
	$('.up_cards_close').click(function(){
		className = $(this).attr('class');
		$('#dialogmag').fadeIn(300);
		$('#dialohg').removeAttr('class').addClass('by_value '+className+'').fadeIn();
	});

	//关闭弹窗
	$('.claseDialogBtn').click(function(){
		$('#dialogmag').fadeOut(300,function(){
			$('#dialohg').addClass('bounceOutUp').fadeOut();
		});
	});
});



 