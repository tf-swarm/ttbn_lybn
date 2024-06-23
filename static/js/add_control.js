


var addstrVar = "";
addstrVar += "<div  class=\"aui_state_box\"><div class=\"aui_state_box_bg\"></div>";
addstrVar += "<div class=\"aui_outer aui_alert\" id=\"drag_con\">";
addstrVar += "<table class=\"aui_border aui_hybox\" style=\"border:2px solid #8a9499;\">";
addstrVar += "<tbody>";
addstrVar += "<form action=\"\" method=\"post\" id=\"form_search\">";
addstrVar += "<tr>";
addstrVar += "	<td class=\"aui_w\">";
addstrVar += "	</td>";
addstrVar += "	<td class=\"aui_c\">";
addstrVar += "		<div class=\"aui_inner\">";
addstrVar += "			<table class=\"aui_dialog\">";
addstrVar += "			<tbody>";
addstrVar += "			<tr>";
addstrVar += "				<td class=\"aui_header\" colspan=\"2\">";
addstrVar += "					<div class=\"aui_titleBar\">";
addstrVar += "						<div class=\"aui_title\" style=\"cursor: move;\">";
addstrVar += "							选择权限分类";
addstrVar += "						</div>";
addstrVar += "						<div class=\"aui_middle\" style=\"cursor: move;\">";
addstrVar += "							<div class=\"aui_user\" style=\"cursor: move;\">";
addstrVar += "								<label>用户名</label>";
addstrVar += "								<input type=\"text\" name=\"user_name\" class=\"add_user_name\" value=\"\">";
addstrVar += "								<input type=\"text\" name=\"user_id\" class=\"add_user_id\" style=\"display: none\" value=\"\">";
addstrVar += "							</div>";
addstrVar += "							<div class=\"aui_user\" style=\"cursor: move;\">";
addstrVar += "								<label>手机号</label>";
addstrVar += "								<input type=\"text\" name=\"phone\" class=\"add_phone\" value=\"\">";
addstrVar += "							</div>";
addstrVar += "							<div class=\"aui_user\" style=\"cursor: move;\">";
addstrVar += "								<label>部门归属</label>";
addstrVar += "								<select name=\"department\" class=\"add_department\">";
addstrVar += "									<option value=\"开发\">开发</option>";
addstrVar += "									<option value=\"老板\">老板</option>";
addstrVar += "									<option value=\"产品\">产品</option>";
addstrVar += "									<option value=\"运营\">运营</option>";
addstrVar += "								</select>";
addstrVar += "							</div>";
addstrVar += "						</div>";
addstrVar += "					</div>";
addstrVar += "				</td>";
addstrVar += "			</tr>";
addstrVar += "			<tr>";
addstrVar += "				<td class=\"aui_icon\" style=\"display: none;\">";
addstrVar += "					<div class=\"aui_iconBg\" style=\"background: transparent none repeat scroll 0% 0%;\">";
addstrVar += "					</div>";
addstrVar += "				</td>";
addstrVar += "				<td class=\"aui_main\" style=\"width: auto; height: auto;\">";
addstrVar += "					<div class=\"aui_content\" style=\"padding: 10px 25px;\">";
addstrVar += "						<div class=\"items jquery-localdata\">";
addstrVar += "							<div style=\"height:400px\" class=\"item-table\">";
addstrVar += "								<table style=\"width:700px;\" class=\"options-table\">";
addstrVar += "								<tbody class=\"item-list\" >";
var maxhy = znhycode;
for (var i in znhycode) {
    var node = "";
    for (var j in znhycode[i].maxhycode) {
        if (j != znhycode[i].maxhycode.length - 1) {
            if (j % 2 == 0) {
                node += "		<tr>";
                node += "			<td>";
                node += "				<label>";
                node += "				<input type=\"checkbox\"  name=\"item-list\" class=\"input-checkbox\" data-value=\"" + znhycode[i].maxhycode[j].CodeValue + "\" data-name=\"" + znhycode[i].maxhycode[j].CodeName + "\"  onclick=\"addhyitem(this)\">";
                node += znhycode[i].maxhycode[j].CodeName;
                node += "				</label>";
                node += "			</td>";
            } else {
                node += "			<td>";
                node += "				<label>";
                node += "				<input type=\"checkbox\"  name=\"item-list\" class=\"input-checkbox\" data-value=\"" + znhycode[i].maxhycode[j].CodeValue + "\" data-name=\"" + znhycode[i].maxhycode[j].CodeName + "\" onclick=\"addhyitem(this)\">";
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
                node += "				<input type=\"checkbox\"  name=\"item-list\" class=\"input-checkbox\" data-value=\"" + znhycode[i].maxhycode[j].CodeValue + "\" data-name=\"" + znhycode[i].maxhycode[j].CodeName + "\" onclick=\"addhyitem(this)\">";
                node += znhycode[i].maxhycode[j].CodeName;
                node += "				</label>";
                node += "			</td>";
                node += "		</tr>";
            } else {
                node += "			<td>";
                node += "				<label>";
                node += "				<input type=\"checkbox\"  name=\"item-list\" class=\"input-checkbox\" data-value=\"" + znhycode[i].maxhycode[j].CodeValue + "\" data-name=\"" + znhycode[i].maxhycode[j].CodeName + "\" onclick=\"addhyitem(this)\">";
                node += znhycode[i].maxhycode[j].CodeName;
                node += "				</label>";
                node += "			</td>";
                node += "		</tr>";
            }
        }
    }
    addstrVar += "<tr>";
    addstrVar += "	<th width=\"150\">";
    addstrVar += znhycode[i].CodeName;
    addstrVar += "	</th>";
    addstrVar += "	<td>";
    addstrVar += "		<table>";
    addstrVar += "		<tbody>";
    addstrVar += node;
    addstrVar += "		</tbody>";
    addstrVar += "		</table>";
    addstrVar += "	</td>";
    addstrVar += "</tr>";
}
addstrVar += "								</tbody>";
addstrVar += "								</table>";
addstrVar += "							</div>";
addstrVar += "						</div>";
addstrVar += "					</div>";
addstrVar += "				</td>";
addstrVar += "			</tr>";
addstrVar += "			<tr>";
addstrVar += "				<td class=\"aui_footer\" colspan=\"2\">";
addstrVar += "					<div class=\"aui_buttons\">";
addstrVar += "						<button class=\"aui-btn aui-btn-primary\" type=\"button\" onclick=\"add_manage()\">确定</button>";
addstrVar += "						<button class=\"aui-btn aui-btn-light\" type=\"button\" onclick=\"add_Close()\">取消</button>";
addstrVar += "					</div>";
addstrVar += "				</td>";
addstrVar += "			</tr>";
addstrVar += "			</tbody>";
addstrVar += "			</table>";
addstrVar += "		</div>";
addstrVar += "	</td>";
addstrVar += "	<td class=\"aui_e\">";
addstrVar += "	</td>";
addstrVar += "</tr>";
addstrVar += "<tr>";
addstrVar += "	<td class=\"aui_sw\">";
addstrVar += "	</td>";
addstrVar += "	<td class=\"aui_s\">";
addstrVar += "	</td>";
addstrVar += "	<td class=\"aui_se\" style=\"cursor: se-resize;\">";
addstrVar += "	</td>";
addstrVar += "</tr>";
addstrVar += "</form>";
addstrVar += "</tbody> </table></div></div>";

var add_type = "";
function add_control(type) {
    add_type = type;
    $('body').append(addstrVar);
    if (add_type == "show") {
        var inputarry = []; //["1","2","3","4"]
        $('.options-table .input-checkbox').each(function(index) {
            for (var i in inputarry) {
                if ($(this).data("value") == inputarry[i]) {
                    $(this).click();
                }
            }
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

function addhyitem(con) {
    if (add_type == "show") {
        if ($(con).prop("checked") == true) {
            if ($(".sltnode-checkbox[data-value=" + $(con).data("value") + "]").prop("checked"))
                return false;
            if ($('.options-table .input-checkbox:checked').length > 999) {
                $(con).prop("checked", false);
                alert('最多只能选择999项！');
                return false;
            } else {
                var selectnode = "<label id=\"sltnode-" + $(con).data("value") + "\"><input type=\"checkbox\" checked=\"checked\"  name=\"item-list\" class=\"sltnode-checkbox\" data-value=\"" + $(con).data("value") + "\"  data-name=\"" + $(con).data("name") + "\" onchange=\"add_hyitem(this)\">" + $(con).data("name") + "</label>";
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

function add_hyitem(con) {
    $(con).parent('label').remove();
    $('.options-table .input-checkbox[data-value="' + $(con).data('value') + '"]').prop("checked", false);
}

function add_Close() {
    $('.aui_state_box').remove();
}