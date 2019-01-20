
"use strict";

var numResults = 5;
var seqs;
var map;
var markers = [];
var alignments = [];

// jquery extend function
$.extend(
{
    redirectPost: function(location, args)
    {
        var form = '';
        $.each( args, function( key, value ) {
            value = value.split('"').join('\"');
            form += '<input type="hidden" name="'+key+'" value="'+value+'">';
        });
        $('<form action="' + location + '" method="POST">' + form + '</form>').appendTo($(document.body)).submit();
    }
});



$().ready(function() {
    getAlignments(querySeq,0) //querySeq set by template as a global variable
});
//Somewhat recursively call getAlignments
//So that we don't get into timeout trouble with Amazon Lambda

function getAlignments(sequence,startIndex){
    $.post( "../align/", { seq: sequence, seqName: seqName})
    .done(
        function( data ) {
        alignments = data["alignments"];
        var redirect = '../results/';
        $.redirectPost(redirect, {"alignments":encodeURIComponent(JSON.stringify(alignments))});
    })
}

