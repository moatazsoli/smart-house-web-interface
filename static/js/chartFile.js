"use strict";

var ajaxDataRenderer;
var plot;
var plot2;
var plot3;
var plot4;

function capitaliseFirstLetter(string)
{
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function chartLast10(e){
    var currentPlot,
        string = e.target.getAttribute('data-id');

    if(string === "temperature") {
        currentPlot = plot;
    }
    if(string === "proximity") {
        currentPlot = plot2;
    }
    if(string === "ambient") {
        currentPlot = plot3;
    }
    if(string === "humidity") {
        currentPlot = plot4;
    }

    var url = "/chart?type=" + string + "&range=Last10";

    currentPlot.destroy();

    currentPlot = $.jqplot(currentPlot.targetId.slice(1), url,{
        title: capitaliseFirstLetter(string),
        animate: true,
        // Will animate plot on calls to plot1.replot({resetAxes:true})
        animateReplot: true,
        dataRenderer: ajaxDataRenderer,
        dataRendererOptions: {
            unusedOptionalUrl: url
        },
        highlighter: {
            show: true,
            sizeAdjust: 7.5
        }
    });
}

function chartLast7(e){
    var currentPlot,
        string = e.target.getAttribute('data-id');

    if(string === "temperature") {
        currentPlot = plot;
    }
    if(string === "proximity") {
        currentPlot = plot2;
    }
    if(string === "ambient") {
        currentPlot = plot3;
    }
    if(string === "humidity") {
        currentPlot = plot4;
    }

    var url = "/chart?type=" + string + "&range=Last7Days";

    currentPlot.destroy();

    currentPlot = $.jqplot(currentPlot.targetId.slice(1), url,{
        title: capitaliseFirstLetter(string),
        animate: true,
        // Will animate plot on calls to plot1.replot({resetAxes:true})
        animateReplot: true,
        dataRenderer: ajaxDataRenderer,
        dataRendererOptions: {
            unusedOptionalUrl: url
        },
        highlighter: {
            show: true,
            sizeAdjust: 7.5
        },
        axes:{
            xaxis:
            {
                renderer:$.jqplot.DateAxisRenderer,
                tickOptions:{
                    formatString:'%b&nbsp;%#d'
                }
            }
        }
    });
}

function chartLast12(e){
    var currentPlot,
        string = e.target.getAttribute('data-id');

    if(string === "temperature") {
        currentPlot = plot;
    }
    if(string === "proximity") {
        currentPlot = plot2;
    }
    if(string === "ambient") {
        currentPlot = plot3;
    }
    if(string === "humidity") {
        currentPlot = plot4;
    }

    var url = "/chart?type=" + string + "&range=Last12Months";

    currentPlot.destroy();

    currentPlot = $.jqplot(currentPlot.targetId.slice(1), url,{
        title: capitaliseFirstLetter(string),
        animate: true,
        // Will animate plot on calls to plot1.replot({resetAxes:true})
        animateReplot: true,
        dataRenderer: ajaxDataRenderer,
        dataRendererOptions: {
            unusedOptionalUrl: url
        },
        highlighter: {
            show: true,
            sizeAdjust: 7.5
        },
        axes:{
            xaxis:
            {
                renderer:$.jqplot.DateAxisRenderer
            }
        }
    });
}

$(document).ready(function(){
    var ret;
    $.ajax({
        // have to use synchronous here, else the function
        // will return before the data is fetched
        async: false,
        url: "/data",
        dataType:"json",
        success: function(data) {
            ret = data;
        }
    });

    $("#tempVal").text(ret[0].temperature);
    $("#proxVal").text(ret[0].proximity);
    $("#ambVal").text(ret[0].ambient);
    $("#humVal").text(ret[0].humidity);

    // Our ajax data renderer which here retrieves a text file.
    // it could contact any source and pull data, however.
    // The options argument isn't used in this renderer.
    ajaxDataRenderer = function(url, plot, options) {
        var ret = null;
        $.ajax({
            // have to use synchronous here, else the function
            // will return before the data is fetched
            async: false,
            url: url,
            dataType:"json",
            success: function(data) {
                ret = data;
            }
        });
        return ret;
    };

    // The url for our json data
    var jsonurl = "/chart?type=temperature&range=Last10",
        jsonurl2 = "/chart?type=proximity&range=Last10",
        jsonurl3 = "/chart?type=ambient&range=Last10",
        jsonurl4 = "/chart?type=humidity&range=Last10";

    // passing in the url string as the jqPlot data argument is a handy
    // shortcut for our renderer.  You could also have used the
    // "dataRendererOptions" option to pass in the url.
    plot = $.jqplot('chartdiv', jsonurl,{
        title: "Temprature",
        animate: true,
        // Will animate plot on calls to plot1.replot({resetAxes:true})
        animateReplot: true,
        dataRenderer: ajaxDataRenderer,
        dataRendererOptions: {
            unusedOptionalUrl: jsonurl
        },
        highlighter: {
            show: true,
            sizeAdjust: 7.5
        }
    });

    plot2 = $.jqplot('chartdiv2', jsonurl2,{
        title: "Proximity",
        animate: true,
        animateReplot: true,
        dataRenderer: ajaxDataRenderer,
        dataRendererOptions: {
            unusedOptionalUrl: jsonurl2
        },
        highlighter: {
            show: true,
            sizeAdjust: 7.5
        }
    });

    plot3 = $.jqplot('chartdiv3', jsonurl3,{
        title: "Ambient Light",
        animate: true,
        animateReplot: true,
        dataRenderer: ajaxDataRenderer,
        dataRendererOptions: {
            unusedOptionalUrl: jsonurl3
        },
        highlighter: {
            show: true,
            sizeAdjust: 7.5
        }
    });

    plot4 = $.jqplot('chartdiv4', jsonurl4,{
        title: "Humidity",
        animate: true,
        animateReplot: true,
        dataRenderer: ajaxDataRenderer,
        dataRendererOptions: {
            unusedOptionalUrl: jsonurl4
        },
        highlighter: {
            show: true,
            sizeAdjust: 7.5
        }
    });

    //Binding Event Handlers for Last 10 readings chart
    var last10Temp= document.getElementById('tempLast10'),
        last10Prox = document.getElementById('proxLast10'),
        last10Amb = document.getElementById('ambLast10'),
        last10Hum = document.getElementById('humLast10'),

    //Binding Event Handlers for Last 10 readings chart
        last7Temp= document.getElementById('tempLast7'),
        last7Prox = document.getElementById('proxLast7'),
        last7Amb = document.getElementById('ambLast7'),
        last7Hum = document.getElementById('humLast7'),

    //Binding Event Handlers for Last 10 readings chart
        last12Temp= document.getElementById('tempLast12'),
        last12Prox = document.getElementById('proxLast12'),
        last12Amb = document.getElementById('ambLast12'),
        last12Hum = document.getElementById('humLast12');

    last10Temp.onclick = chartLast10;
    last10Prox.onclick = chartLast10;
    last10Amb.onclick = chartLast10;
    last10Hum.onclick = chartLast10;

    last7Temp.onclick = chartLast7;
    last7Prox.onclick = chartLast7;
    last7Amb.onclick = chartLast7;
    last7Hum.onclick = chartLast7;

    last12Temp.onclick = chartLast12;
    last12Prox.onclick = chartLast12;
    last12Amb.onclick = chartLast12;
    last12Hum.onclick = chartLast12;

});