


function catalogClick(e){
	//console.log(e);
	window.open("/audio/catalog/" + $("#auctionId").val() + "/" + e.target.id);

}

function endAuction(e){
	



	$( "#dialog-confirm1" ).dialog({
		resizable: false,
		height:140,
		modal: true,
		buttons: {
			"Are you sure you want to end this auction?": function() {
				
				var csrftoken = getCookie('csrftoken');
					ajaxSetup(csrftoken);


					$.ajax({
						type: "POST",
						url: "/audio/auction/endAuction",
						data: "",
						success: function(data) {

						},
						error: function (xhr, ajaxOptions, thrownError) {
				        	//alert(xhr.status);
				        	//alert(thrownError);
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

		},
		error: function (xhr, ajaxOptions, thrownError) {
        	//alert(xhr.status);
        	//alert(thrownError);
        	return false;
      	}
	});
	
}


$( document ).ready(function() {

	$('.catalogItem').click(catalogClick);

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

	
	$( "#opener" ).click(function() {
    	$( "#dialog-confirm" ).dialog( "open" );
    });



});
