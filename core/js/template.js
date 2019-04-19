$(function(){
	     $('#tabs a').click(function(e) {
	          e.preventDefault();                
	          $('#tabs li').removeClass("current").removeClass("hoverItem");
	          $(this).parent().addClass("current");
	          $("#content div").removeClass("show");
	          $('#' + $(this).attr('title')).addClass('show');
	         // alert($(this).attr('title'));
	          if($(this).attr('title')=="tab1"){
	        		 
                    //这边是打开第一页时候可以添加一些操作
 
	          }
	          if($(this).attr('title')=="tab2"){
	        		
                  //这边是打开第二页时候可以添加一些操作
 
	          }
	          if($(this).attr('title')=="tab3"){
	        		
                  //这边是打开第三页时候可以添加一些操作
	          }
	      });
 
 
	     $('#tabs a').hover(function(){
	        if(!$(this).parent().hasClass("current")){
	          $(this).parent().addClass("hoverItem");
	        }
	     },function(){
	        $(this).parent().removeClass("hoverItem");
	     });
	  });