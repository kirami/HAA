


function catalogClick(e){
	//console.log(e);
	window.open("/audio/catalog/" + $("#auctionId").val() + "/" + e.target.id);

}

function endAuction(e){
	

	$( "#dialog-confirm" ).dialog({
		resizable: false,
		height:140,
		modal: true,
		buttons: {
			"Delete all items": function() {
				console.log("hit yes");
				$( this ).dialog( "close" );
			},
			Cancel: function() {
				$( this ).dialog( "close" );
			}
		}
	});

	$.ajax({
		type: "POST",
		url: "/audio/auction/endAuction",
		data: "",
		success: function(data) {
			//googleConversion();
			onSuccess(true);

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


});
