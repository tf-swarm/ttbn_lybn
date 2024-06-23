// 有 FORM 表单全选操作
function checkAll(form, name){
	for(var i = 0; i < form.elements.length; i++){
		var e = form.elements[i];
		if(e.name.match(name)){
			e.checked = form.elements['chkall'].checked;
		}
	}
}

// 无 FORM 表单全选操作
$(function(){
	$("#chkall").click(function(){
		if(this.checked){
			$("input[type='checkbox']").each(function(){this.checked=true;});
		}else{
			$("input[type='checkbox']").each(function(){this.checked=false;});
		}
	});
});

// 双击是扩大textarea
function textareasize(obj, op) {
    if(!op) {
        if(obj.scrollHeight > 70) {
            obj.style.height = (obj.scrollHeight < 300 ? obj.scrollHeight : 300) + 'px';
            if(obj.style.position == 'absolute') {
                obj.parentNode.style.height = obj.style.height;
            }
        }
    } else {
        if(obj.style.position == 'absolute') {
            obj.style.position = '';
            obj.style.width = '';
            obj.parentNode.style.height = '';
        } else {
            obj.parentNode.style.height = obj.parentNode.offsetHeight + 'px';
            obj.style.width = BROWSER.ie > 6 || !BROWSER.ie ? '90%' : '600px';
            obj.style.position = 'absolute';
        }
    }
}

function copyCode(s){
	if(window.clipboardData){
		window.clipboardData.setData('text',s.val());
		alert('复制成功！\t\r请将已复制的代码粘贴到要加入微博秀功能的页面。');
	}else{
		alert('你的浏览器不支持脚本复制或你拒绝了浏览器安全确认。请尝试[Ctrl+C]复制代码并粘贴到要加入功能的页面。');
	}
}