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
                  $(objId).prop("checked",isChecked);
                  $("#placemark_"+elephant["id"]).show();
                  $("#placemarkSmall_"+elephant["id"]).hide()
               }else{
                  $("#placemark_"+elephant["id"]).hide();
                  $("#placemarkSmall_"+elephant["id"]).show()
               }
            }
        }

    }
    update()

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


function placeMarker(locationPin,zIndex) {

  let lhp_ids = locationPin["lhp_ids"]
  let numChecked = 0
  for (let i=0;i<lhp_ids.length;i++){
    let lhp_id = lhp_ids[i]
    var objId = "#subjectChk_" + lhp_id;
    if($(objId).length > 0){ //not using true/false bit, in case of an error here
      if($(objId).is(':checked')){
        numChecked++;
      }
    }
  }
  if(numChecked>0){ //should have at least one checked
    var icon = locationPin["image"]
  }else if($("#chkShowAll").prop('checked')) {
    var icon = locationPin["smallimage"]
  }else{
    return // don't show icon at all
  }

var marker = new google.maps.Marker({
  map: map,
  icon: icon,
  optimized: true,
  zIndex: (zIndex),
  position: {
    lat: locationPin["lat"],
    lng: locationPin["lon"]
  }
});

markers.push(marker);
let locationHeader = "";
if (locationPin['letter'] !== undefined && locationPin['letter'] !== null){
  locationHeader = '<h2>'+locationPin['letter']+'</h2>'
}
var description = '<div>'+
  locationHeader+
  '<span class="mapDesc">Location Name:&nbsp;</span>' + locationPin["locationName"]+ '<br/>'+

  '<span class="mapDesc">Location Type:&nbsp;</span>' + locationPin["locationType"] + '<br/>'+
  '<span class="mapDesc">Country:&nbsp;</span>' + locationPin["locality"] + '<br/><br/>'+
  '<span style="font-weight:bold;font-style:italic">Closest match at location:</span><br/>'+
  '<span class="mapDesc">Haplotype:&nbsp;</span>' + locationPin["subjectID"] + '<br/>'+
  '<span class="mapDesc">Matches:&nbsp;</span>' + locationPin["score"] + '<br/>'+
  '<span class="mapDesc">Mismatches:&nbsp;</span>' + locationPin["mismatch"] + '<br/>'+
  '<span class="mapDesc">Author(s):&nbsp;</span>' + locationPin["authors"].join(", ") + '<br/>'+
'</div>';
attachDescription(marker, description); //allow users to click for description for lesser hits
}


function update(){
  deleteMarkers();
  var zIndex=10000;
  for (let locationPin in locationPinsDict){
    placeMarker(locationPinsDict[locationPin],zIndex);
    zIndex--;

  }
}