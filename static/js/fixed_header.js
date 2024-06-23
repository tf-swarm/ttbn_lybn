"use strict";
window.onload = function(){
	  var tableCont = document.querySelector('#table-cont')

	  function scrollHandle (e){
		var scrollTop = this.scrollTop;
		this.querySelector('thead').style.transform = 'translateY(' + scrollTop + 'px)';
	  }

	  tableCont.addEventListener('scroll',scrollHandle)
};