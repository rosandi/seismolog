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
             ];

plotwidth=0.60*ww;
plotheight=0.3*wh;

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
  yaxis: {range: [-1, 1],title: 'a.u.'},
  xaxis: {title: 'time (s)'}
};

var plotdatax=[pline[0]];
var plotdatay=[pline[1]];
var plotdataz=[pline[2]];

Plotly.newPlot('plotareax',plotdatax,layout);
Plotly.newPlot('plotareay',plotdatay,layout);
Plotly.newPlot('plotareaz',plotdataz,layout);

function getval(elid) {
    return document.getElementById(elid).value;
}

function setval(elid,val) {
    document.getElementById(elid).value=val;
}

function getstatus() {
    $.getJSON('status', function(stat) {
        if(stat.status) {
            $('#statustext').append('Logging daemon is running<br>');
        } else {
            $('#statustext').append('Logging daemon is not running<br>');
        }
    });
}

function shutdown() {
    $("#statustext").html("<div style='text-align:center'>system shutdown...<br><H1>GOOD BYE...</H1></div>");
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
                $('#statustext').append(sdate);
                $('#statustext').append(s.program+'<br>');
            });
        }
    });
}

function listFiles(){
    $.getJSON('list/json',function(lst) {
        s='';
        for(i=0;i<lst.files.length;i++) {
            fl=lst.files[i].replace(/.json/,'')
            s+='<tr><td class="cell" onclick=plotfile($(this).html()+".json")>'+fl+'</td></tr>';
        }
        $('#filelist').html(s);
    });
}

function plotfile(fname) {
    if(fname=='--' || fname=='' || fname=='null') return;
    $.getJSON('load/'+fname, function(data){
        t=new Array(data.length);
        dt=data.tsample/data.length;
        for (i=0;i<data.length;i++) {
            t[i]=i*dt;
        }
        
        layout.xaxis={range: [0,data.tsample],title: 'time (s)'};
        layout.yaxis={range: [-200, 200],title: 'a.u.'};
        
        pline[0].x=t;
        pline[1].x=t;
        pline[2].x=t;
        
        pline[0].y=data.x;
        pline[1].y=data.y;
        pline[2].y=data.z;
        Plotly.redraw('plotareax');
        Plotly.redraw('plotareay');
        Plotly.redraw('plotareaz');
    });
}

function sendcmd() {
    cmd=getval('cmdtext').replace(/ /g,'/');
    console.log(cmd);
    $.get(cmd,function(data){
        $('#longresponse').append(data+'<br>');
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

    if(chn==0) {
        chn=1; // avoids nonsense
        document.getElementById('ch1').checked=true;
    }
    
    sconf='par/chanmask='+chn+':block='+msrlen+':avg='+avg+':delay='+dt+'/';
    $.get(sconf,function(resp){
        $('#longresponse').append(resp+'<br>');
    });
}
