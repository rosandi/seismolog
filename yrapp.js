/* 
  Instrumentation apps
  YRAPP
*/

const ww= window.innerWidth;
const wh= window.innerHeight;

var runid;
var running=false;
var msrlen=100;
var avg=10;
var dt=1;
var chn=1;

var pline = [{x: [0],y: [0],type: 'scatter',name: 'V1'}, 
             {x: [0],y: [0],type: 'scatter',name: 'V2'},
             {x: [0],y: [0],type: 'scatter',name: 'V3'},
             {x: [0],y: [0],type: 'scatter',name: 'V4'},
             {x: [0],y: [0],type: 'scatter',name: 'V5'},
             {x: [0],y: [0],type: 'scatter',name: 'V6'}];

plotwidth=0.72*ww;
plotheight=0.8*wh;

var layout = {
  width: plotwidth,
  height: plotheight,
  autosize: false,
  margin: {
    l: 50,
    r: 50,
    b: 50,
    t: 40,
    pad: 4
  },
  yaxis: {range: [-0.1, 0.1],title: 'volt'},
  xaxis: {title: 'time'}
};

var plotdata=[pline[0]];
Plotly.newPlot('plotarea',plotdata,layout);

function getval(elid) {
    return document.getElementById(elid).value;
}

function setval(elid,val) {
    document.getElementById(elid).value=val;
}

function getstatus() {
    $.getJSON('status', function(stat) {
        if(stat.status) {
            $('#statustext').html('Logging daemon is running<br>');
        } else {
            $('#statustext').html('Logging daemon is not running<br>');
        }
    });
}

function shutdown() {
    $("#statustext").append("system shutdown<br><H1>GOODBYE...</H1>");
    $.getJSON("shutdown",function(st){});
}

function togglerun() {
    $.getJSON('status',
    function(stat){
        console.log('stat: '+stat.status)
        if(stat.status) {
            $.getJSON('stop',function(s){
                console.log('stopping');
                $('#runbtn').css({'background-color':'green'});
                $('#runbtn').html('START');
                var d=new Date();
                sdate='stop: '+d.getDate()+'/'+d.getMonth()+'/'+d.getFullYear();
                sdate+=' '+d.getHours()+':'+d.getMinutes()+':'+d.getSeconds()+'<br>';
                $('#statustext').append(sdate)
            });
        } else {
            $.getJSON('start',function(s){
                console.log('starting');
                $('#runbtn').css({'background-color':'red'});
                $('#runbtn').html('STOP');
                var d=new Date();
                sdate='start logging at: '+d.getDate()+'/'+d.getMonth()+'/'+d.getFullYear();
                sdate+=' '+d.getHours()+':'+d.getMinutes()+':'+d.getSeconds()+'<br>';
                $('#statustext').append(sdate)
            });
        }
    });
}


function sendcmd() {
    cmd=getval('cmdtext').replace(/ /g,'/');
    console.log(cmd);
    $.get(cmd,function(data){
        $('#longresponse').html(data.replace(/,/g,',<br>'));
    });
}

function apply() {
    msrlen=getval('len');
    avg=getval('avg');
    dt=getval('dt');
    chn=0;
    if(document.getElementById('ch1').checked) chn+=1;
    if(document.getElementById('ch2').checked) chn+=2;
    if(document.getElementById('ch3').checked) chn+=4;
    if(document.getElementById('ch4').checked) chn+=8;
    if(document.getElementById('ch5').checked) chn+=16;
    if(document.getElementById('ch6').checked) chn+=32;
    if(chn==0) {
        chn=1; // avoids nonsense
        document.getElementById('ch1').checked=true;
    }
    
    /*
     * $.getJSON('avg/'+avg,function(resp){
        s='data length/block: '+msrlen+'<br>';
        s+=resp.msg+'<br>';
        console.log(resp.msg);
    });
    $.getJSON('dt/'+dt,function(resp){
        s+=resp.msg+'<br>';
        console.log(resp.msg);
    });
    $.getJSON('chn/'+chn,function(resp){
        s+=resp.msg;
        console.log(resp.msg);
        $('#longresponse').html(s);
    });
    */
}

//measure()
