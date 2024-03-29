

function catalogClick(e){
	//console.log(e);
	window.open("/audio/catalog/" + $("#auctionId").val() + "/" + e.target.id);

}



function ajaxSetup(csrftoken){
		$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	        }
	    }
	});
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}



function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function sendEmail (template, auctionId, consignorId) {
		console.log("sending email")
		
		var csrftoken = getCookie('csrftoken');
		ajaxSetup(csrftoken);

		$.ajax({
		type: "POST",
		url: "/admin/sendEmail/",
		data: {"template":template, "auctionId":auctionId, "consignorId":consignorId},
		success: function(data) {
			$('#consignorIdEmailMsg').css("color","green")
			$('#consignorIdEmailMsg').text("Email was successfully sent.")
		},
		error: function (xhr, ajaxOptions, thrownError) {
			$('#consignorIdEmailMsg').css("color","red")
			$('#consignorIdEmailMsg').text("Something went wrong - email was not sent.")
        	return false;
      	}
	});
	
}

function endMyAuction (auctionId, userId) {
		
		var csrftoken = getCookie('csrftoken');
		ajaxSetup(csrftoken);

		$.ajax({
		type: "POST",
		url: "/admin/endFlatAuction/"+auctionId+"/" + userId + "/",
		data: {"email" : true},
		success: function(data) {
			$('#endAuctionMsg').css("color","green")
			window.location.reload()
		},
		error: function (xhr, ajaxOptions, thrownError) {
			$('#endAuctionMsg').css("color","red")
			$('#endAuctionMsg').text("Something went wrong. Please contact us.")
        	return false;
      	}
	});
	
}

$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return results[1] || 0;
    }
}




function submitBid(itemId){

	var csrftoken = getCookie('csrftoken');
	ajaxSetup(csrftoken);

	$.ajax({
		type: "POST",
		url: "/audio/catalog/submitBid/",
		data: {"bidAmount": $("#bidAmount_" + itemId).val(), "itemId":itemId},
		success: function(data) {
			if(data.success){
				result = $.urlParam('success')
				

				if(result)
					window.location.reload()			 
				else{
					split = window.location.href.split("?")
					
					if (split.length>1)
						window.location+="&success=true";
					else
						window.location+="?success=true";
				}
					
				
			}else{
				$('.successMsg').hide()
				$("#msg").html("<div>Something went wrong, we could not save your bid:<br> "  + data.msg + "</div>")
        	
			}
		},
		error: function (xhr, ajaxOptions, thrownError) {
        	$("#msg").text("Something went wrong, we could not save your bid.")
        	return false;
      	}
	});
}

function openDialog(elem){
	$( "#" + elem ).dialog( "open" );

}

$( document ).ready(function() {

	//$('.catalogItem').click(catalogClick);

	$('#bidSubmit').click(function () {
		$("#bidSubmitForm").submit();
	});

	$("#btnLeft").click(function () {
	    var selectedItem = $("#id_bcItemsSelected option:selected");
	    $("#id_bcItemsAvailable").append(selectedItem);
	});

	$("#btnRight").click(function () {
	    var selectedItem = $("#id_bcItemsAvailable option:selected");
	    $("#id_bcItemsSelected").append(selectedItem);
	});


	$( "#dialog-confirm" ).dialog({
		resizable: false,
		height:140,
		modal: true,
		autoOpen: false, 
		buttons: {
			"Mark Winners": function() {
				$("#markWinnersForm").submit()
				$( this ).dialog( "close" );
			},
		Cancel: function() {
				$( this ).dialog( "close" );
			}
		}
	});

	$( "#emailInvoices-confirm" ).dialog({
		resizable: false,
		height:140,
		modal: true,
		autoOpen: false, 
		buttons: {
			"Email Invoices": function() {
				$("#markWinnersForm").submit()
				sendInvoices()
				$( this ).dialog( "close" );
			},
		Cancel: function() {
				$( this ).dialog( "close" );
			}
		}
	});

	$( "#lockFlat-confirm" ).dialog({
		resizable: false,
		height:140,
		modal: true,
		autoOpen: false, 
		buttons: {
			"Lock this flat auction": function() {
				var csrftoken = getCookie('csrftoken');
				ajaxSetup(csrftoken);

				$.ajax({
					type: "POST",
					url: "/admin/endFlatAuction/"+ $("#auctionId").val() + "/",
					success: function(data) {
						if(data.success){

							$("#msg").css("color","green")
							$("#msg").text("You've successfully locked this flat auction")
						}else{
							$("#msg").text("Something went wrong, this flat auction wasn't locked: "  + data.msg)
			        	
						}


					},
					error: function (xhr, ajaxOptions, thrownError) {
			        	$("#msg").text("Something went wrong, this flat auction wasn't locked")
			        	return false;
			      	}
				});
				$( this ).dialog( "close" );
			},
		Cancel: function() {
				$( this ).dialog( "close" );
			}
		}
	});

	$( "#lockBlind-confirm" ).dialog({
		resizable: false,
		height:140,
		modal: true,
		autoOpen: false, 
		buttons: {
			"Lock this blind auction": function() {
				var csrftoken = getCookie('csrftoken');
				ajaxSetup(csrftoken);

				$.ajax({
					type: "POST",
					url: "/admin/endBlindAuction/"+ $("#auctionId").val() + "/",
					success: function(data) {

						if(data.success){

							$("#msg").css("color","green")
							$("#msg").text("You've successfully locked this blind auction")
						}else{
							$("#msg").text("Something went wrong, this blind auction wasn't locked: "  + data.msg)
			        	
						}

					},
					error: function (xhr, ajaxOptions, thrownError) {
			        	$("#msg").text("Something went wrong, this blind auction wasn't locked")
			        	return false;
			      	}
				});
				$( this ).dialog( "close" );
			},
		Cancel: function() {
				$( this ).dialog( "close" );
			}
		}
	});


	
	$( "#emailInvoices" ).click(function() {
    	$( "#emailInvoices-confirm" ).dialog( "open" );
    });

	$( "#opener" ).click(function() {
    	$( "#dialog-confirm" ).dialog( "open" );
    });

    $( "#lockFlat" ).click(function() {
    	$( "#lockFlat-confirm" ).dialog( "open" );
    });

    $( "#lockBlind" ).click(function() {
    	$( "#lockBlind-confirm" ).dialog( "open" );
    });

    $(".quickLook").click(function(){
			var csrftoken = getCookie('csrftoken');
			ajaxSetup(csrftoken);
			item = $(this).attr("id").substring(10)
			

			$.ajax({
				type: "POST",
				url: "/audio/catalog/itemInfo/"+ item + "/",
				success: function(data) {
					$("#itemPopup").removeClass("successError")
					
					if(data.success){
						$("#itemPopup").html(data)
					}else{
						$("#itemPopup").html(data)
		        	
					}
					$( "#itemPopup" ).dialog("open", "position", "center");

				},
				error: function (xhr, ajaxOptions, thrownError) {
		        	$("#itemPopup").html("That is not a valid item.")
		        	$("#itemPopup").addClass("successError")
		        	$( "#itemPopup" ).dialog("open", "position", "center");
		        	return false;
				}
			});
			
			

			return false;
		})




});
