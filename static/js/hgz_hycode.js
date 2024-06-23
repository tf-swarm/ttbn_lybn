var hystrVar = "";
hystrVar += "<div  class=\"aui_state_box\"><div class=\"aui_state_box_bg\"></div>";
hystrVar += "<div class=\"aui_outer aui_alert\" id=\"drag_con\">";
hystrVar += "<table class=\"aui_border aui_hybox\" style=\"border:2px solid #8a9499;\">";
hystrVar += "<tbody>";
hystrVar += "<form action=\"\" method=\"post\" id=\"form_search\">";
hystrVar += "<tr>";
hystrVar += "	<td class=\"aui_w\">";
hystrVar += "	</td>";
hystrVar += "	<td class=\"aui_c\">";
hystrVar += "		<div class=\"aui_inner\">";
hystrVar += "			<table class=\"aui_dialog\">";
hystrVar += "			<tbody>";
hystrVar += "			<tr>";
hystrVar += "				<td class=\"aui_header\" colspan=\"2\">";
hystrVar += "					<div class=\"aui_titleBar\">";
hystrVar += "						<div class=\"aui_title\" style=\"cursor: move;\">";
hystrVar += "							选择权限分类";
hystrVar += "						</div>";
hystrVar += "						<div class=\"aui_middle\" style=\"cursor: move;\">";
hystrVar += "							<div class=\"aui_user\" style=\"cursor: move;\">";
hystrVar += "								<label>用户名</label>";
hystrVar += "								<input type=\"text\" name=\"user_name\" class=\"user_name\" value=\"\">";
hystrVar += "								<input type=\"text\" name=\"user_id\" class=\"user_id\" style=\"display: none\" value=\"\">";
hystrVar += "							</div>";
hystrVar += "							<div class=\"aui_user\" style=\"cursor: move;\">";
hystrVar += "								<label>手机号</label>";
hystrVar += "								<input type=\"text\" name=\"phone\" class=\"phone\" value=\"\">";
hystrVar += "							</div>";
hystrVar += "							<div class=\"aui_user\" style=\"cursor: move;\">";
hystrVar += "								<label>部门归属</label>";
hystrVar += "								<select name=\"department\" class=\"department\">";
hystrVar += "									<option value=\"开发\">开发</option>";
hystrVar += "									<option value=\"老板\">老板</option>";
hystrVar += "									<option value=\"产品\">产品</option>";
hystrVar += "									<option value=\"运营\">运营</option>";
hystrVar += "								</select>";
hystrVar += "							</div>";
hystrVar += "						</div>";
hystrVar += "					</div>";
hystrVar += "				</td>";
hystrVar += "			</tr>";
hystrVar += "			<tr>";
hystrVar += "				<td class=\"aui_icon\" style=\"display: none;\">";
hystrVar += "					<div class=\"aui_iconBg\" style=\"background: transparent none repeat scroll 0% 0%;\">";
hystrVar += "					</div>";
hystrVar += "				</td>";
hystrVar += "				<td class=\"aui_main\" style=\"width: auto; height: auto;\">";
hystrVar += "					<div class=\"aui_content\" style=\"padding: 10px 25px;\">";
hystrVar += "						<div class=\"items jquery-localdata\">";
hystrVar += "							<div style=\"height:400px\" class=\"item-table\">";
hystrVar += "								<table style=\"width:700px;\" class=\"options-table\">";
hystrVar += "								<tbody class=\"item-list\" >";
var maxhy = znhycode;
for (var i in znhycode) {
    var node = "";
    for (var j in znhycode[i].maxhycode) {
        if (j != znhycode[i].maxhycode.length - 1) {
            if (j % 2 == 0) {
                node += "		<tr>";
                node += "			<td>";
                node += "				<label>";
                node += "				<input type=\"checkbox\"  name=\"item-list\" class=\"input-checkbox\" data-value=\"" + znhycode[i].maxhycode[j].CodeValue + "\" data-name=\"" + znhycode[i].maxhycode[j].CodeName + "\"  onclick=\"showhyitem(this)\">";
                node += znhycode[i].maxhycode[j].CodeName;
                node += "				</label>";
                node += "			</td>";
            } else {
                node += "			<td>";
                node += "				<label>";
                node += "				<input type=\"checkbox\"  name=\"item-list\" class=\"input-checkbox\" data-value=\"" + znhycode[i].maxhycode[j].CodeValue + "\" data-name=\"" + znhycode[i].maxhycode[j].CodeName + "\" onclick=\"showhyitem(this)\">";
                node += znhycode[i].maxhycode[j].CodeName;
                node += "				</label>";
                node += "			</td>";
                node += "		</tr>";
            }
        } else {
            if (j / 2 == 0) {
                node += "		<tr>";
                node += "			<td>";
                node += "				<label>";
                node += "				<input type=\"checkbox\"  name=\"item-list\" class=\"input-checkbox\" data-value=\"" + znhycode[i].maxhycode[j].CodeValue + "\" data-name=\"" + znhycode[i].maxhycode[j].CodeName + "\" onclick=\"showhyitem(this)\">";
                node += znhycode[i].maxhycode[j].CodeName;
                node += "				</label>";
                node += "			</td>";
                node += "		</tr>";
            } else {
                node += "			<td>";
                node += "				<label>";
                node += "				<input type=\"checkbox\"  name=\"item-list\" class=\"input-checkbox\" data-value=\"" + znhycode[i].maxhycode[j].CodeValue + "\" data-name=\"" + znhycode[i].maxhycode[j].CodeName + "\" onclick=\"showhyitem(this)\">";
                node += znhycode[i].maxhycode[j].CodeName;
                node += "				</label>";
                node += "			</td>";
                node += "		</tr>";
            }
        }
    }
    hystrVar += "<tr>";
    hystrVar += "	<th width=\"150\">";
    hystrVar += znhycode[i].CodeName;
    hystrVar += "	</th>";
    hystrVar += "	<td>";
    hystrVar += "		<table>";
    hystrVar += "		<tbody>";
    hystrVar += node;
    hystrVar += "		</tbody>";
    hystrVar += "		</table>";
    hystrVar += "	</td>";
    hystrVar += "</tr>";
}
hystrVar += "								</tbody>";
hystrVar += "								</table>";
hystrVar += "							</div>";
hystrVar += "						</div>";
hystrVar += "					</div>";
hystrVar += "				</td>";
hystrVar += "			</tr>";
hystrVar += "			<tr>";
hystrVar += "				<td class=\"aui_footer\" colspan=\"2\">";
hystrVar += "					<div class=\"aui_buttons\">";
hystrVar += "						<button class=\"aui-btn aui-btn-primary\" type=\"button\" onclick=\"update_control()\">确定</button>";
hystrVar += "						<button class=\"aui-btn aui-btn-light\" type=\"button\" onclick=\"Close()\">取消</button>";
hystrVar += "					</div>";
hystrVar += "				</td>";
hystrVar += "			</tr>";
hystrVar += "			</tbody>";
hystrVar += "			</table>";
hystrVar += "		</div>";
hystrVar += "	</td>";
hystrVar += "	<td class=\"aui_e\">";
hystrVar += "	</td>";
hystrVar += "</tr>";
hystrVar += "<tr>";
hystrVar += "	<td class=\"aui_sw\">";
hystrVar += "	</td>";
hystrVar += "	<td class=\"aui_s\">";
hystrVar += "	</td>";
hystrVar += "	<td class=\"aui_se\" style=\"cursor: se-resize;\">";
hystrVar += "	</td>";
hystrVar += "</tr>";
hystrVar += "</form>";
hystrVar += "</tbody> </table></div></div>";

var datainput = null;
var zytype = "";

function show_control(user_id,name,phone, department,control_list,type) {
    zytype = type;
    $('body').append(hystrVar);
    if (zytype == "show") {
        var inputarry = control_list; //["1","2","3","4"]
        $('.options-table .input-checkbox').each(function(index) {
            for (var i in inputarry) {
                if ($(this).data("value") == inputarry[i]) {
                    $(this).click();
                }
            }
            $('.aui_middle .user_id').val(user_id);
            $('.aui_middle .user_name').val(name);
            $('.aui_middle .phone').val(phone);
            $('.aui_middle .department').val(department);
        });
    } else {
        $('.aui_state_box .aui_buttons').remove();
        $('.aui-titlespan').remove();
    }
    var minwid = document.documentElement.clientWidth;
    $('.aui_outer').on("mousedown", function(e) {
        $(this)[0].oncontextmenu = function(e) {
            return false;
        }
        var getStartX = e.pageX
          , getStartY = e.pageY;
        var getPositionX = (minwid / 2) - $(this).offset().left
          , getPositionY = $(this).offset().top;
        $(document).on("mousemove", function(e) {
            var getEndX = e.pageX
              , getEndY = e.pageY;
            $('.aui_outer').css({
                left: getEndX - getStartX - getPositionX,
                top: getEndY - getStartY + getPositionY
            });
        });
        $(document).on("mouseup", function() {
            $(document).unbind("mousemove");
        })
    });
}

function showhyitem(con) {
    if (zytype == "show") {
        if ($(con).prop("checked") == true) {
            if ($(".sltnode-checkbox[data-value=" + $(con).data("value") + "]").prop("checked"))
                return false;
            if ($('.options-table .input-checkbox:checked').length > 999) {
                $(con).prop("checked", false);
                alert('最多只能选择999项！');
                return false;
            } else {
                var selectnode = "<label id=\"sltnode-" + $(con).data("value") + "\"><input type=\"checkbox\" checked=\"checked\"  name=\"item-list\" class=\"sltnode-checkbox\" data-value=\"" + $(con).data("value") + "\"  data-name=\"" + $(con).data("name") + "\" onchange=\"removehyitem(this)\">" + $(con).data("name") + "</label>";
                $('.aui-selecteditem').append(selectnode);
            }
        } else {
            $(".sltnode-checkbox[data-value=" + $(con).data("value") + "]").prop("checked", false);
            $(".sltnode-checkbox[data-value=" + $(con).data("value") + "]").parent('label').remove();
        }
    } else {
        // $(datainput).data("value", $(con).data("value"));
        // $(datainput).val($(con).data("name"));
        $('.aui_state_box').remove();
    }
}

function removehyitem(con) {
    $(con).parent('label').remove();
    $('.options-table .input-checkbox[data-value="' + $(con).data('value') + '"]').prop("checked", false);
}

function Close() {
    $('.aui_state_box').remove();
}

