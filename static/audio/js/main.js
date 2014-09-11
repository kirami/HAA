


function catalogClick(e){
	//console.log(e);
	window.open("/audio/catalog/" + $("#auctionId").val() + "/" + e.target.id);

}




$( document ).ready(function() {

	$('.catalogItem').click(catalogClick);

	$('#bidSubmit').click(function () {
		$("#bidSubmitForm").submit();
	});


});
