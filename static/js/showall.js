"use strict";
   var map; var markers = [];
   var eleRange;
   var protectedArea;
$().ready(function() {
    $("i[name=detailExpander]").click(function(){
        $(this).toggleClass('fa-plus-square-o fa-minus-square-o');
        
         var thisID = this.id.split("_")[1];
         $("#detailsDiv_"+thisID).slideToggle('500')
        
        //$(this).parent().parent().next('tr[name=detailsTr]').find('td[name=detailsTd]').find('div[name=detailsDiv]').slideToggle('500');
    });
    
     $("#expand_protectedArea").click(function(){
        $(this).toggleClass('fa-plus-square-o fa-minus-square-o');
         $("#protectedAreaAdditionalInfo").slideToggle('500')
    });
    
   $("input[name=elephantCheckbox]").click(function(){
        update()
    });
    
    $("input[name=subjectCheckbox]").click(function(){
        subjectToggled(this)
    });
    $("input[name=alignmentCheckbox]").click(function(){
        alignmentToggled(this)
    });

    $("#chkEleRange").click(function(){
        eleRangeLayer(this)
    });

    $("#chkProtectedArea").click(function(){
        protectedRange(this)
    });

google.maps.event.addDomListener(window, 'load', initialize);
});

function eleRangeLayer(){
	if ($("#chkEleRange").is(':checked')){
	  eleRange.setMap(map);
      $("#elephantRangeMemo").show()
	}else{
	  eleRange.setMap(null);
      $("#elephantRangeMemo").hide()
	}
}

function protectedRange(){
	if ($("#chkProtectedArea").is(':checked')){
	  protectedArea.setMap(map);
      $("#protectedAreaMemo").show()
	}else{
	  protectedArea.setMap(null);
      $("#protectedAreaMemo").hide()
	}
}

function initialize() {
  var mapOptions = {
    center: {
      lat: -5,
      lng: 17
    },
    zoom: 4,
    draggable: true,
    zoomControl: true,
    scrollwheel: false,
    disableDoubleClickZoom: true,
    mapTypeId: google.maps.MapTypeId.TERRAIN
  };
  
  eleRange = new google.maps.FusionTablesLayer({
          query: {
            select: 'geometry_name',
            from: '1aOr66XXbwFiTbaBexZ6uaqruB90NoH9oq6KpI92U'
          }, templateId: 2,
   			 styleId: 2,
   			  options: {"suppressInfoWindows": true}
        });
        
        
  protectedArea = new google.maps.FusionTablesLayer({
       query: {
            select: 'geometry',
            from: '1uJKa5WgXFfxn30S95AaveJ5cCM1IbefhKR5efso'
          }
        });
        
  map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
  eleRangeLayer();
  protectedRange();
  update()
}

function subjectToggled(toggleSwitch){
    var isChecked = $("#"+toggleSwitch.id).prop('checked');
    var thisID = toggleSwitch.id.split("_")[1];

    
    for (var i=0;i<alignments.length;i++){
        var alignment = alignments[i];
    
        if( alignment.subjectID == thisID){
            for (var j=0;j<alignment["elephants"].length;j++){
               var elephant = alignment["elephants"][j];
               var objId = "#subjectChk_" + elephant["id"];
               if($(objId).length > 0){
                  $(objId).prop("checked",isChecked)
               }
            }
        }

    }
    update();
    if(isChecked){
        $("#placemark_"+thisID).show()
    }else{
        $("#placemark_"+thisID).hide()
    }
}

function alignmentToggled(toggleSwitch){
    var isChecked = $("#"+toggleSwitch.id).prop('checked');
    
    var thisID = toggleSwitch.id.split("_")[1];
    if(isChecked){
        $("#alignmentDiv_"+thisID).show('2000')
    }else{
        $("#alignmentDiv_"+thisID).hide('2000')
    }
    
}



function attachDescription(marker, description) {
  var infowindow = new google.maps.InfoWindow({
    content: description
  });
  marker.addListener('click', function() {
    infowindow.open(marker.get('map'), marker);
  });
}

function deleteMarkers() {
  clearMarkers();
  markers = [];
}

function clearMarkers() {
  setAllMap(null);
}


function setAllMap(map) {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}


function placeMarker(elephant,alignment,i) {
  //TODO fill in z-index
    //lat, lng, title, score, zindex

 var icon = alignment["image"];

  var marker = new google.maps.Marker({
    map: map,
    title: elephant["locationName"],
    icon: icon,
    label: alignment["mismatch"],
    optimized: true,
    zIndex: (1000-i),
    position: {
      lat: elephant["lat"],
      lng: elephant["lon"]
    }
  });
  markers.push(marker);
  
  //TODO: Show infowindow somehow
  /*if (score == bestScore) { //always show description for best hits
    var infowindow = new google.maps.InfoWindow({
      content: title
    });
    infowindow.open(map, marker);
    attachDescription(marker, title);
  } else {*/
    attachDescription(marker, elephant["locationName"]); //allow users to click for description for lesser hits
  //}
}

function update(){
    deleteMarkers();
    for (var i=0;i<alignments.length;i++){
        var alignment = alignments[i];
        for (var j=0;j<alignment["elephants"].length;j++){
            var elephant = alignment["elephants"][j];
            var objId = "#subjectChk_" + elephant["id"];
            if($(objId).length > 0){
                if ($(objId).is(':checked')){
                    placeMarker(elephant,alignment,i);
                    
                    //placeMarker(elephant["lat"],elephant["lon"],"#"+elephant["id"]+"  "+elephant["accession"],alignment["score"])
                }
            }
        }
    }
}